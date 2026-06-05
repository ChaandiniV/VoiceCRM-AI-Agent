from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from backend.app.config import get_settings


class CRMClient:
    """CRM abstraction layer.

    The project runs in mock mode by default. When CRM_PROVIDER=hubspot and
    HUBSPOT_PRIVATE_APP_TOKEN is configured, it sends a HubSpot contact create
    request. For portfolio demos, mock mode is safer and easier to review.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def create_or_update_lead(self, lead_payload: dict[str, Any]) -> dict[str, Any]:
        provider = self.settings.crm_provider.lower().strip()
        if provider == "hubspot" and self.settings.hubspot_private_app_token:
            return self._create_hubspot_contact(lead_payload)
        return self._write_mock_payload(lead_payload)

    def _create_hubspot_contact(self, lead_payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.settings.hubspot_base_url.rstrip('/')}/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {self.settings.hubspot_private_app_token}",
            "Content-Type": "application/json",
        }
        body = {
            "properties": {
                "firstname": lead_payload.get("customer_name", "").split(" ")[0],
                "lastname": " ".join(lead_payload.get("customer_name", "").split(" ")[1:]) or "Unknown",
                "email": lead_payload.get("email") or "",
                "phone": lead_payload.get("phone") or "",
                "company": lead_payload.get("company") or "",
                "lifecyclestage": "lead",
                "notes_last_contacted": lead_payload.get("requirement") or "",
            }
        }
        response = requests.post(url, headers=headers, json=body, timeout=20)
        if response.status_code >= 400:
            return {
                "mode": "hubspot",
                "status": "failed",
                "record_id": None,
                "error": response.text,
                "request_payload": body,
            }
        data = response.json()
        return {
            "mode": "hubspot",
            "status": "created",
            "record_id": str(data.get("id")),
            "response": data,
        }

    @staticmethod
    def _write_mock_payload(lead_payload: dict[str, Any]) -> dict[str, Any]:
        outbox_path = Path("data/crm_mock_outbox.jsonl")
        outbox_path.parent.mkdir(parents=True, exist_ok=True)
        mock_record_id = f"mock-{abs(hash(json.dumps(lead_payload, sort_keys=True))) % 10_000_000}"
        record = {
            "mode": "mock",
            "status": "created",
            "record_id": mock_record_id,
            "payload": lead_payload,
        }
        with outbox_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return record
