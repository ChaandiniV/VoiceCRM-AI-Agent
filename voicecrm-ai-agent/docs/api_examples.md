# API Examples

## Health check

```bash
curl http://127.0.0.1:8000/
```

## Simulate full call

```bash
curl -X POST http://127.0.0.1:8000/api/demo/simulate-call \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Aisha Khan",
    "phone": "+971501112233",
    "email": "aisha@example.com",
    "company": "Palm Clinic",
    "industry": "Healthcare",
    "requirement": "We need an AI voice assistant to handle appointment booking and FAQs",
    "budget": "12000 AED monthly",
    "timeline": "Go live in 3 weeks",
    "preferred_channel": "WhatsApp follow-up"
  }'
```

## Get leads

```bash
curl http://127.0.0.1:8000/api/leads
```

## Get roadmap

```bash
curl http://127.0.0.1:8000/api/roadmap/1
```

## Test Twilio-style inbound webhook locally

```bash
curl -X POST http://127.0.0.1:8000/webhooks/twilio/voice \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+971501112233&CallSid=CA12345"
```
