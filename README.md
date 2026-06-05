# VoiceCRM AI Agent

A browser-based AI voice lead qualification and CRM automation project built for a **Solutions Engineer - Voice AI** use case.

The project captures spoken customer requirements, sends the transcript to a FastAPI backend, qualifies the lead, stores the data locally, and triggers a Make.com webhook that writes the lead into Google Sheets. The architecture is CRM-ready and can be extended to HubSpot, Zoho, Twilio Voice, WhatsApp Business API, or real telephony workflows.

---

## What We Built

```text
Browser voice input
    -> Speech-to-text transcript
    -> FastAPI backend
    -> Lead qualification logic / optional Hugging Face AI layer
    -> SQLite storage
    -> Make.com webhook
    -> Google Sheets lead logging
    -> Streamlit dashboard
```

This project was built to demonstrate practical implementation skills: APIs, webhooks, automation, CRM-ready payload design, dashboards, and voice-enabled customer intake.

---

## Current Status

| Component | Status |
|---|---|
| Browser voice input | Working |
| Browser speech-to-text | Working in supported browsers |
| Browser text-to-speech reply | Working |
| FastAPI backend | Working |
| Lead scoring and qualification | Working |
| Optional Hugging Face AI layer | Supported through environment variables |
| Rule-based fallback | Working |
| Make.com webhook | Working |
| Google Sheets logging | Working |
| SQLite local storage | Working |
| Streamlit dashboard | Working |
| Mock CRM mode | Working |
| Real HubSpot/Zoho writeback | Future scope |
| Real Twilio phone call integration | Future scope |

Important: the current voice demo uses the browser microphone, not a real phone number. CRM is in mock mode unless HubSpot/Zoho credentials are added.

---

## Screenshots

### Browser Voice Demo

![Browser Voice Demo](docs/images/voice-demo.png)

### AI Qualification Result

![AI Qualification Result](docs/images/ai-result.png)

### Google Sheets Output

![Google Sheets Output](docs/images/google-sheets-output.png)

### Make.com Scenario

![Make Scenario](docs/images/make-scenario.png)

### FastAPI Docs

![FastAPI Docs](docs/images/fastapi-docs.png)

### Streamlit Dashboard

![Streamlit Dashboard](docs/images/streamlit-dashboard.png)



---

## Features

- Browser-based voice input for free voice demo
- Browser speech-to-text and text-to-speech
- FastAPI backend with API routes
- Voice lead qualification endpoint
- Lead score, priority, next action, and agent reply
- Optional Hugging Face LLM qualification layer
- Rule-based fallback if AI API is not configured or fails
- Make.com webhook integration
- Google Sheets lead logging
- SQLite database for local storage
- Streamlit dashboard for reviewing leads
- CRM-ready payload for future HubSpot or Zoho integration
- Twilio-style structure for future real call integration

---

## Tech Stack

| Area | Technology |
|---|---|
| Backend | FastAPI |
| Voice demo | Browser Speech Recognition + Text-to-Speech |
| Automation | Make.com Webhooks |
| Lead storage | SQLite |
| Dashboard | Streamlit |
| AI layer | Hugging Face optional, rule-based fallback |
| CRM output | Google Sheets now, HubSpot/Zoho ready later |
| Language | Python |

---

## Folder Structure

```text
voicecrm-ai-agent/
├── backend/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── models/
│       └── services/
├── dashboard/
│   └── app.py
├── frontend/
│   └── voice_demo.html
├── data/
│   ├── google_sheet_headers.csv
│   └── make_sample_payload.json
├── docs/
│   ├── architecture.md
│   ├── MAKE_SETUP.md
│   ├── BROWSER_VOICE_DEMO.md
│   └── images/
├── scripts/
│   └── demo_call.py
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ChaandiniV/VoiceCRM-AI-Agent.git
cd VoiceCRM-AI-Agent/voicecrm-ai-agent
```

If your repo folder directly contains the project files, use:

```bash
cd VoiceCRM-AI-Agent
```

### 2. Create Virtual Environment

For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

For macOS/Linux/GitHub Codespaces:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy the example file:

```bash
cp .env.example .env
```

For Windows:

```bash
copy .env.example .env
```

Example `.env`:

```env
APP_NAME=VoiceCRM AI Agent
DATABASE_URL=sqlite:///./voicecrm.db

MAKE_WEBHOOK_URL=your_make_webhook_url_here
MAKE_WEBHOOK_SECRET=demo-secret-change-me

CRM_PROVIDER=mock
HUBSPOT_ACCESS_TOKEN=

MOCK_MODE=true

AI_PROVIDER=rules
HF_TOKEN=
HF_MODEL=openai/gpt-oss-120b:fastest
HF_BASE_URL=https://router.huggingface.co/v1
```

Do not push `.env` to GitHub.

---

## Run the Backend

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Browser voice demo:

```text
http://127.0.0.1:8000/voice-demo
```

In GitHub Codespaces, open the forwarded port 8000 URL from the **PORTS** tab and add:

```text
/voice-demo
```

---

## Run the Streamlit Dashboard

Open a second terminal:

```bash
streamlit run dashboard/app.py
```

---

## Make.com Integration

### Scenario Structure

```text
Custom Webhook -> Google Sheets: Add a Row
```

### Steps

1. Create a new Make.com scenario.
2. Add **Webhooks -> Custom Webhook**.
3. Copy the webhook URL.
4. Paste the URL into `.env`:

```env
MAKE_WEBHOOK_URL=https://hook.make.com/your-webhook-url
```

5. Add **Google Sheets -> Add a Row**.
6. Connect your Google account.
7. Select your spreadsheet: `VoiceCRM Leads`.
8. Map the webhook fields to the spreadsheet columns.
9. Click **Run once** and test from the browser voice demo.

---

## Google Sheets Columns

Create a Google Sheet named:

```text
VoiceCRM Leads
```

Use these headers:

```text
lead_id
call_id
created_at
customer_name
phone
email
company
industry
requirement
budget
timeline
preferred_channel
lead_score
priority
next_action
workflow
integrations_needed
estimated_complexity
recommended_poc
crm_status
```

---

## Test Voice Script

Use this in the browser voice demo:

```text
We are a real estate company and need an AI voice assistant to answer property inquiries, qualify buyers, book viewings, and update HubSpot CRM. We want to launch next month.
```

Expected result:

- Lead score generated
- Priority assigned
- Next action created
- Agent reply generated
- Make webhook status shown as sent
- New row added in Google Sheets

---

## Optional Hugging Face AI Layer

The project supports an optional Hugging Face AI layer for LLM-based lead analysis. If it is not configured, the app still works using the rule-based fallback.

Update `.env`:

```env
AI_PROVIDER=huggingface
HF_TOKEN=your_hugging_face_token_here
HF_MODEL=openai/gpt-oss-120b:fastest
HF_BASE_URL=https://router.huggingface.co/v1
```

If the Hugging Face call fails due to quota, model availability, or token issues, the system falls back to the rule-based qualification logic so the demo does not break.

---

## What Is Real vs Mock

| Part | Status |
|---|---|
| Browser voice input | Real |
| Speech-to-text | Real browser feature |
| FastAPI API | Real |
| Make webhook | Real |
| Google Sheets row creation | Real |
| SQLite storage | Real |
| Dashboard | Real |
| Lead qualification | Rule-based or optional Hugging Face AI |
| CRM integration | Mock mode now |
| Twilio phone calls | Not connected yet |

Honest project description:

> This is a browser-based voice CRM automation MVP. It demonstrates voice intake, backend processing, lead qualification, webhook automation, and CRM-ready logging. Real phone calls and direct HubSpot/Zoho writeback are future extensions.

---

## Future Improvements

- Add Twilio Voice for real inbound phone calls.
- Add HubSpot contact and deal creation.
- Add Zoho CRM integration.
- Add WhatsApp Business API follow-up.
- Add OpenAI Realtime or Twilio Media Streams for live phone-call voice agents.
- Deploy FastAPI backend to Render/Railway/Fly.io.
- Deploy Streamlit dashboard.
- Add authentication for dashboard users.
- Add call transcript history and analytics.

---

## Resume Bullet

Built **VoiceCRM AI Agent**, a browser-based AI voice lead qualification and CRM automation system using FastAPI, speech-to-text, SQLite, Streamlit, Make.com webhooks, and Google Sheets to capture spoken customer requirements and route qualified leads into CRM-ready workflows.

---

## Interview Explanation

> I built this project to simulate the implementation lifecycle of a Voice AI Solutions Engineer. The browser captures a customer requirement through voice input, converts it to text, sends it to a FastAPI backend, qualifies the lead, stores the record, and triggers a Make.com webhook. Make then logs the qualified lead into Google Sheets. The project is structured so it can later be connected to Twilio for phone calls and HubSpot or Zoho for CRM updates.

---

## Git Commands

First check status:

```bash
git status
```

Make sure `.env` is not being pushed. If it appears, run:

```bash
git rm --cached .env
```

Make sure `.gitignore` contains:

```gitignore
.env
.venv/
__pycache__/
voicecrm.db
*.pyc
.pytest_cache/
```

Add and commit:

```bash
git add .
git commit -m "Add VoiceCRM AI Agent documentation and screenshots"
git push
```

If this is the first push:

```bash
git init
git add .
git commit -m "Initial VoiceCRM AI Agent project"
git branch -M main
git remote add origin https://github.com/ChaandiniV/VoiceCRM-AI-Agent.git
git push -u origin main
```

If the remote already exists:

```bash
git remote set-url origin https://github.com/ChaandiniV/VoiceCRM-AI-Agent.git
git push -u origin main
```

---

## Author

Chaandini Viswanathan  
B.Tech Computer Science Engineering - Artificial Intelligence  
Sharjah, UAE
