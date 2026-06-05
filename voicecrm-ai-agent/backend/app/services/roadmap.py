from __future__ import annotations

from typing import Any


def build_implementation_roadmap(lead: dict[str, Any]) -> dict[str, Any]:
    requirement = (lead.get("requirement") or "").lower()
    priority = lead.get("priority", "Medium")
    company = lead.get("company") or "Client"

    phases = [
        {
            "phase": "1. Discovery & workflow mapping",
            "duration": "1-2 days",
            "deliverables": [
                "Current call flow map",
                "CRM fields and data routing requirements",
                "Escalation and handoff rules",
            ],
        },
        {
            "phase": "2. Voice agent POC",
            "duration": "3-5 days",
            "deliverables": [
                "Prompt flow and sample conversation scripts",
                "Inbound call webhook prototype",
                "Transcript and lead capture pipeline",
            ],
        },
        {
            "phase": "3. CRM/API integration",
            "duration": "2-4 days",
            "deliverables": [
                "Contact/deal creation payloads",
                "Webhook logs and retry handling",
                "CRM field mapping document",
            ],
        },
        {
            "phase": "4. UAT & go-live",
            "duration": "2-3 days",
            "deliverables": [
                "Test call scenarios",
                "Go-live checklist",
                "Monitoring dashboard and handover notes",
            ],
        },
    ]

    if "booking" in requirement or "appointment" in requirement:
        phases[2]["deliverables"].append("Calendar or booking API handoff")

    risks = [
        "Missing CRM field ownership may delay integration sign-off.",
        "Telephony provider setup requires verified phone number and HTTPS webhook URL.",
        "Prompt flow needs UAT with real call scenarios before go-live.",
    ]
    if priority == "High":
        risks.append("Compressed timeline requires early agreement on MVP scope.")

    recommended_demo_assets = [
        f"{company} vertical demo script",
        "Architecture diagram showing voice webhook, AI agent, CRM, and dashboard",
        "Before/after workflow map",
        "Call transcript and lead creation screen recording",
    ]

    return {
        "lead_id": lead["id"],
        "phases": phases,
        "risks": risks,
        "recommended_demo_assets": recommended_demo_assets,
    }
