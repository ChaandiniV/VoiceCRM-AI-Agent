from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from backend.app.config import get_settings


class AutomationClient:
    """Outbound automation connector.

    The recommended portfolio setup uses Make.com as the integration layer:
    FastAPI sends a qualified lead payload to a Make Custom Webhook, then Make
    can add a Google Sheets row, create/update a HubSpot contact, and send an
    email/WhatsApp follow-up.

    If MAKE_WEBHOOK_URL is empty, this client writes the payload to a local
    JSONL outbox so the repo stays runnable without any accounts or paid APIs.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def send_qualified_lead(self, lead_payload: dict[str, Any]) -> dict[str, Any]:
        if self.settings.make_webhook_url:
            return self._send_to_make(lead_payload)
        return self._write_local_outbox(lead_payload)

    def _send_to_make(self, lead_payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.settings.make_webhook_secret:
            headers["X-VoiceCRM-Secret"] = self.settings.make_webhook_secret

        response = requests.post(
            self.settings.make_webhook_url,
            json=lead_payload,
            headers=headers,
            timeout=20,
        )

        result = {
            "mode": "make",
            "status_code": response.status_code,
            "response_preview": response.text[:500],
        }

        if response.status_code >= 400:
            result["status"] = "failed"
            return result

        result["status"] = "sent"
        return result

    @staticmethod
    def _write_local_outbox(lead_payload: dict[str, Any]) -> dict[str, Any]:
        outbox_path = Path("data/make_mock_outbox.jsonl")
        outbox_path.parent.mkdir(parents=True, exist_ok=True)
        mock_event_id = f"make-mock-{abs(hash(json.dumps(lead_payload, sort_keys=True, default=str))) % 10_000_000}"
        record = {
            "mode": "local_mock",
            "status": "queued_locally",
            "event_id": mock_event_id,
            "payload": lead_payload,
        }
        with outbox_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return record
