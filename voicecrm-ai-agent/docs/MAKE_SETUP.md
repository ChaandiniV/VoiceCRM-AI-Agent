# Make.com Setup Guide — VoiceCRM AI Agent

This project is designed to run in two modes:

1. **Local mock mode** — no accounts, no API keys, no payment.
2. **Make integration mode** — FastAPI sends qualified lead data to a Make Custom Webhook, then Make updates Google Sheets, sends email alerts, and optionally creates HubSpot CRM contacts.

For your portfolio, the recommended free workflow is:

```text
FastAPI /api/demo/simulate-call
        ↓
Make Custom Webhook
        ↓
Google Sheets: Add a Row
        ↓
Router by priority
        ├── High priority → Email alert to sales/implementation team
        └── Medium/Low priority → normal follow-up email
        ↓
Optional HubSpot: Create/Update contact
```

---

## Part A — Create the Google Sheet

Create a new Google Sheet named:

```text
VoiceCRM Leads
```

Add these headers in row 1:

```csv
lead_id,call_id,created_at,customer_name,phone,email,company,industry,requirement,budget,timeline,preferred_channel,lead_score,priority,next_action,workflow,integrations_needed,estimated_complexity,recommended_poc,crm_status
```

The same header row is also available in:

```text
data/google_sheet_headers.csv
```

---

## Part B — Create the Make scenario

### 1. Add Custom Webhook trigger

In Make:

1. Create a new scenario.
2. Add module: **Webhooks → Custom webhook**.
3. Click **Add** and name it:

```text
voicecrm_lead_intake
```

4. Copy the webhook URL.
5. Open your repo `.env` file and paste it:

```env
MAKE_WEBHOOK_URL=https://hook.eu2.make.com/your-webhook-id
MAKE_WEBHOOK_SECRET=demo-secret-change-me
```

6. Click **Run once** in Make.
7. In your terminal, run:

```bash
python scripts/demo_call.py
```

Make should capture the sample payload and learn the fields.

---

### 2. Add Google Sheets module

Add module:

```text
Google Sheets → Add a Row
```

Connect your Google account and select:

```text
Spreadsheet: VoiceCRM Leads
Sheet: Sheet1
```

Map fields like this:

| Sheet column | Make field |
|---|---|
| lead_id | `lead_id` |
| call_id | `call_id` |
| created_at | `now` or Make execution time |
| customer_name | `customer_name` |
| phone | `phone` |
| email | `email` |
| company | `company` |
| industry | `industry` |
| requirement | `requirement` |
| budget | `budget` |
| timeline | `timeline` |
| preferred_channel | `preferred_channel` |
| lead_score | `lead_score` |
| priority | `priority` |
| next_action | `next_action` |
| workflow | `implementation_summary.workflow` |
| integrations_needed | `join(implementation_summary.integrations_needed; ", ")` |
| estimated_complexity | `implementation_summary.estimated_complexity` |
| recommended_poc | `implementation_summary.recommended_poc` |
| crm_status | `crm_status` |

---

### 3. Add email notification

Add module:

```text
Gmail → Send an email
```

Subject:

```text
New {{priority}} VoiceCRM lead: {{company}}
```

Body:

```text
New VoiceCRM lead captured.

Customer: {{customer_name}}
Company: {{company}}
Phone: {{phone}}
Email: {{email}}
Industry: {{industry}}
Priority: {{priority}}
Lead score: {{lead_score}}

Requirement:
{{requirement}}

Next action:
{{next_action}}

Recommended POC:
{{implementation_summary.recommended_poc}}
```

Send it to your own email for the demo.

---

### 4. Optional: Add Router for high-priority leads

Add a Make **Router** after the webhook or after Google Sheets.

Route 1 filter:

```text
priority Equal to High
```

Action:

```text
Send urgent email / create HubSpot contact / create follow-up task
```

Route 2 filter:

```text
priority Not equal to High
```

Action:

```text
Send normal follow-up email
```

---

### 5. Optional: Add HubSpot contact creation

Add module:

```text
HubSpot CRM → Create a Contact
```

Map:

| HubSpot field | Make field |
|---|---|
| Email | `email` |
| First name | first part of `customer_name` |
| Last name | remaining part of `customer_name` |
| Phone | `phone` |
| Company | `company` |
| Lifecycle stage | Lead |

If HubSpot setup takes time, skip it and use Google Sheets first. The project is still valid because the integration architecture is real.

---

## Part C — Run the full demo

Start FastAPI:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Start dashboard:

```bash
streamlit run dashboard/app.py
```

Run sample call:

```bash
python scripts/demo_call.py
```

Expected result:

1. FastAPI stores call, transcript, lead, CRM mock payload, and Make outbound event.
2. Make receives the payload.
3. Google Sheets gets a new row.
4. Email notification is sent.
5. Streamlit dashboard shows the lead.

---

## What to say in interview

> I used Make as the integration layer because many real solutions engineering projects combine code with low-code automation. FastAPI handles the AI-agent logic and webhook payload generation, while Make handles operational workflow automation such as Google Sheets logging, email alerts, and optional HubSpot CRM contact creation. This simulates how a Voice AI implementation would move from call intake to CRM update and go-live monitoring.

