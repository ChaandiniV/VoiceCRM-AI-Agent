from __future__ import annotations

import json
import sys
from urllib import request, error

API_URL = "http://127.0.0.1:8000/api/demo/simulate-call"

payload = {
    "customer_name": "Aisha Khan",
    "phone": "+971501112233",
    "email": "aisha@example.com",
    "company": "Palm Clinic",
    "industry": "Healthcare",
    "requirement": "We need an AI voice assistant to handle appointment booking, FAQs, and lead capture for new patients.",
    "budget": "12000 AED monthly",
    "timeline": "Go live in 3 weeks",
    "preferred_channel": "WhatsApp follow-up",
}

try:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(API_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=20) as response:
        result = json.loads(response.read().decode("utf-8"))
        print(json.dumps(result, indent=2))
except error.URLError as exc:
    print("Could not reach FastAPI backend. Start it with:")
    print("uvicorn backend.app.main:app --reload --port 8000")
    print(f"Error: {exc}")
    sys.exit(1)
