# Architecture Notes

## Goal

Design a deployable-style Voice AI implementation that converts phone conversations into qualified CRM leads.

## Main components

### 1. Voice entry point

In production, a telephony provider such as Twilio receives the phone call and sends an HTTPS webhook to the FastAPI backend.

Current MVP endpoints:

- `/webhooks/twilio/voice` — receives inbound call metadata and returns TwiML.
- `/webhooks/twilio/process` — receives speech recognition result from a Twilio-style `<Gather>` flow.
- `/webhooks/twilio/status` — stores call status callbacks.

### 2. Agent orchestration

The `LeadQualificationAgent` module contains the conversation configuration:

- System role
- Discovery questions
- Qualification criteria
- Lead score calculation
- Next action recommendation
- Implementation summary

The current implementation is deterministic and mock-first so the project is easy to run locally. In a production version, this module can be replaced by:

- OpenAI Realtime API
- OpenAI Agents SDK
- Vapi
- Retell AI
- Bland AI
- Custom WebSocket/SIP voice agent

### 3. CRM layer

The `CRMClient` is an abstraction layer.

- `CRM_PROVIDER=mock` stores CRM payloads in `data/crm_mock_outbox.jsonl`.
- `CRM_PROVIDER=hubspot` attempts to create a HubSpot contact using a private app token.

This separation shows implementation thinking: the agent should not directly depend on one CRM vendor.

### 4. Storage

SQLite tables:

- `calls`
- `transcripts`
- `leads`
- `webhook_events`

This supports auditability, debugging, dashboard monitoring, and go-live readiness.

### 5. Dashboard

The Streamlit dashboard shows:

- Total calls
- Qualified leads
- Average lead score
- High-priority leads
- Pipeline table
- Transcript review
- Webhook event logs

## Production considerations

Before a real deployment, add:

- HTTPS hosting
- Authentication and authorization
- Webhook signature validation
- Retry queue for failed CRM writes
- PII handling and retention policy
- Call recording consent flow
- Load testing for concurrent calls
- Monitoring and alerting
