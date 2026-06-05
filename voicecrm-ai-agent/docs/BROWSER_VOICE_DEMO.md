# Browser Voice Demo

This project now includes a free voice demo that does not require Twilio, OpenAI paid audio, or any phone number.

## What it does

```text
Laptop microphone
    ↓
Browser SpeechRecognition API
    ↓
Captured transcript
    ↓
FastAPI `/api/voice/browser-lead`
    ↓
Lead qualification + transcript storage
    ↓
Make webhook
    ↓
Google Sheets / email / HubSpot-ready automation
    ↓
Browser text-to-speech agent reply
```

## How to run

Start FastAPI:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open this URL in Chrome or Edge:

```text
http://127.0.0.1:8000/voice-demo
```

Click:

1. **Speak agent prompt**
2. **Start listening**
3. Speak a requirement, for example:

```text
We need an AI voice assistant for appointment bookings, FAQs, and WhatsApp follow-up. We want to go live in three weeks and update our CRM automatically.
```

4. Click **Stop**
5. Click **Send to AI Qualification**

You should see:

- Lead score
- Priority
- Agent reply
- Raw API response
- New database records
- New Make/Google Sheets row if `MAKE_WEBHOOK_URL` is configured

## Important note

This is a real voice interaction at the browser level, but it is not a real phone call yet.

Use this wording in interviews:

> I implemented a free browser voice demo using speech-to-text and text-to-speech so the project demonstrates the full voice intake flow without requiring paid telephony. The transcript is sent to FastAPI, qualified by the AI agent logic, stored in SQLite, and pushed to Make for Google Sheets/CRM automation. The Twilio webhook endpoints are already included for replacing the browser voice demo with real inbound calls later.

## Browser support

Use Chrome or Edge. Speech recognition usually works on `localhost` / `127.0.0.1`.

If your browser blocks the microphone, allow microphone permission in the address bar.
