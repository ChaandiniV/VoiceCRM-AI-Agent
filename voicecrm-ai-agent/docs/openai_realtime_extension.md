# OpenAI Realtime Extension Plan

This MVP uses a deterministic mock agent so anyone can run it locally.

To convert it into a real voice AI agent:

## Option A — Browser voice demo

Use OpenAI Realtime with WebRTC for browser-based voice interaction.

Flow:

```text
Browser microphone
    -> WebRTC session
    -> OpenAI Realtime model
    -> tool call to FastAPI CRM endpoint
    -> dashboard update
```

## Option B — Phone-call voice demo

Use Twilio Voice or SIP provider for incoming phone calls.

Flow:

```text
Caller
    -> Twilio phone number
    -> Twilio webhook / media stream
    -> FastAPI voice bridge
    -> OpenAI Realtime model
    -> CRM tool call
```

## Tool functions to expose to the model

- `create_lead(customer_name, phone, email, company, requirement, priority)`
- `schedule_follow_up(lead_id, channel, timestamp)`
- `escalate_to_human(call_id, reason)`
- `lookup_faq(question)`

## Guardrails

- Never promise pricing unless it is in the approved knowledge base.
- Confirm customer contact details before CRM creation.
- Escalate urgent, medical, legal, or financial advice requests.
- Log every tool call for auditability.
