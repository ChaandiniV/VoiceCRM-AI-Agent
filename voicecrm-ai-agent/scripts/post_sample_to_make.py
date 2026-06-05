from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

make_url = os.getenv("MAKE_WEBHOOK_URL", "").strip()
make_secret = os.getenv("MAKE_WEBHOOK_SECRET", "").strip()

if not make_url:
    print("MAKE_WEBHOOK_URL is empty. Paste your Make Custom Webhook URL into .env first.")
    sys.exit(1)

payload_path = Path("data/make_sample_payload.json")
payload = json.loads(payload_path.read_text(encoding="utf-8"))
headers = {"Content-Type": "application/json"}
if make_secret:
    headers["X-VoiceCRM-Secret"] = make_secret

response = requests.post(make_url, json=payload, headers=headers, timeout=20)
print("Status:", response.status_code)
print("Response:", response.text[:1000])
response.raise_for_status()
