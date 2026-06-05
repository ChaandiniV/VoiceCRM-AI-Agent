# Demo Script

## Scenario

A healthcare clinic wants a voice AI assistant to answer inbound calls, qualify appointment requests, answer common FAQs, and send qualified leads to CRM.

## Demo flow

### Step 1 — Start backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### Step 2 — Start dashboard

```bash
streamlit run dashboard/app.py
```

### Step 3 — Run sample call

```bash
python scripts/demo_call.py
```

### Step 4 — Explain result

The backend generates:

- A call log
- A transcript
- A lead score
- A next action
- A CRM payload
- A suggested implementation summary

### Step 5 — Show dashboard

Open the Streamlit dashboard and point out:

- Lead created from AI call
- Priority score
- CRM sync status
- Transcript view
- Webhook event tracking

## Interview pitch

> This project simulates how I would implement a voice AI system for a client. I start from client workflow requirements, design the call flow, expose webhook endpoints, qualify the conversation through an AI-agent workflow, save transcripts, score the lead, and push CRM-ready data to a CRM abstraction layer. I also built a dashboard and delivery assets because solutions engineering is not only coding; it is also implementation planning, testing, go-live, and client communication.
