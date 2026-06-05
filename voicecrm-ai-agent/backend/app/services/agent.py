from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from backend.app.config import get_settings


@dataclass
class QualificationResult:
    score: int
    priority: str
    reasons: list[str]
    next_action: str
    transcript: list[dict[str, str]]
    implementation_summary: dict[str, Any]


class LeadQualificationAgent:
    """Mock-first AI agent.

    This class uses deterministic prompt-style logic so the project runs without API keys.
    In production, this module can be swapped for OpenAI Realtime, OpenAI Agents SDK,
    Vapi, Retell, or another conversational AI platform.
    """

    SYSTEM_PROMPT = """
    You are a Voice AI Solutions Engineer assistant.
    Your goal is to qualify inbound business leads, understand their workflow,
    identify CRM/API/telephony needs, and recommend the next implementation step.
    Keep the conversation professional, concise, and action-oriented.
    """.strip()

    DISCOVERY_QUESTIONS = [
        "What business process should the voice agent automate?",
        "Which CRM or internal system should receive the captured lead data?",
        "What are the expected call volumes and go-live timeline?",
        "Do you need WhatsApp, email, or human-agent handoff after the call?",
    ]

    def qualify(self, payload: dict[str, Any]) -> QualificationResult:
        settings = get_settings()
        if settings.ai_provider.lower() in {"hf", "huggingface"} and settings.hf_token:
            from backend.app.services.hf_ai import HuggingFaceQualificationClient

            hf_result = HuggingFaceQualificationClient(
                token=settings.hf_token,
                model=settings.hf_model,
                base_url=settings.hf_base_url,
            ).qualify(payload)
            if hf_result is not None:
                return hf_result

        requirement = payload.get("requirement", "") or ""
        budget = payload.get("budget", "") or ""
        timeline = payload.get("timeline", "") or ""
        industry = payload.get("industry", "General Services") or "General Services"
        preferred_channel = payload.get("preferred_channel", "Email") or "Email"

        reasons: list[str] = []
        score = 35

        if len(requirement) > 35:
            score += 15
            reasons.append("Clear business requirement captured")
        if any(word in requirement.lower() for word in ["booking", "appointment", "lead", "faq", "support", "sales", "customer"]):
            score += 15
            reasons.append("Use case is suitable for voice AI automation")
        if budget and re.search(r"\d", budget):
            score += 15
            reasons.append("Budget signal provided")
        if any(word in timeline.lower() for word in ["week", "urgent", "month", "go live", "immediate"]):
            score += 15
            reasons.append("Timeline suggests active buying intent")
        if any(word in preferred_channel.lower() for word in ["whatsapp", "crm", "email"]):
            score += 10
            reasons.append("Follow-up channel is defined")

        score = min(score, 100)
        if score >= 80:
            priority = "High"
            next_action = "Book technical discovery call and prepare vertical-specific POC."
        elif score >= 60:
            priority = "Medium"
            next_action = "Send demo workflow and confirm CRM/telephony integration details."
        else:
            priority = "Low"
            next_action = "Send educational material and capture missing qualification details."

        customer_name = payload.get("customer_name", "Customer")
        company = payload.get("company", "the client")
        transcript = [
            {"speaker": "agent", "message": f"Hello {customer_name}, thanks for calling. What would you like the AI voice assistant to help with?"},
            {"speaker": "customer", "message": requirement},
            {"speaker": "agent", "message": "Which CRM or business system should receive the captured information?"},
            {"speaker": "customer", "message": f"We want the details routed to our CRM and followed up through {preferred_channel}."},
            {"speaker": "agent", "message": "What is your expected go-live timeline and budget range?"},
            {"speaker": "customer", "message": f"Timeline: {timeline or 'Not confirmed yet'}. Budget: {budget or 'Not confirmed yet'}."},
            {"speaker": "agent", "message": f"Great. I will prepare a {industry} voice AI implementation plan for {company}."},
        ]

        summary = {
            "vertical": industry,
            "workflow": self._classify_workflow(requirement),
            "integrations_needed": self._infer_integrations(requirement, preferred_channel),
            "estimated_complexity": self._estimate_complexity(score, requirement),
            "recommended_poc": self._recommend_poc(industry, requirement),
        }

        return QualificationResult(score, priority, reasons, next_action, transcript, summary)

    @staticmethod
    def _classify_workflow(requirement: str) -> str:
        text = requirement.lower()
        if "appointment" in text or "booking" in text:
            return "Appointment booking and FAQ automation"
        if "lead" in text or "sales" in text:
            return "Inbound lead qualification"
        if "support" in text or "ticket" in text:
            return "Customer support triage"
        return "General voice assistant workflow"

    @staticmethod
    def _infer_integrations(requirement: str, preferred_channel: str) -> list[str]:
        integrations = ["Voice telephony webhook", "CRM contact/deal creation"]
        text = f"{requirement} {preferred_channel}".lower()
        if "whatsapp" in text:
            integrations.append("WhatsApp Business follow-up")
        if "email" in text:
            integrations.append("Email follow-up automation")
        if "booking" in text or "appointment" in text:
            integrations.append("Calendar or booking system API")
        return integrations

    @staticmethod
    def _estimate_complexity(score: int, requirement: str) -> str:
        text = requirement.lower()
        if any(word in text for word in ["multiple", "erp", "payment", "custom"]):
            return "High"
        if score >= 75:
            return "Medium"
        return "Low"

    @staticmethod
    def _recommend_poc(industry: str, requirement: str) -> str:
        return (
            f"Build a 5-minute {industry} demo where the caller asks questions, "
            "shares contact details, receives next-step confirmation, and the lead appears in CRM."
        )
