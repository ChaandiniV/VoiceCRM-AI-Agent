from __future__ import annotations

import json
import re
from typing import Any

import requests

from backend.app.services.agent import QualificationResult


class HuggingFaceQualificationClient:
    """LLM-based lead qualification through Hugging Face Inference Providers.

    If the HF API fails, the app falls back to the rule-based qualifier.
    """

    def __init__(self, token: str, model: str, base_url: str, timeout: int = 30) -> None:
        self.token = token
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def qualify(self, payload: dict[str, Any]) -> QualificationResult | None:
        if not self.token:
            return None

        system_prompt = (
            "You are an AI Solutions Engineer qualifying an inbound Voice AI/CRM automation lead. "
            "Analyze the customer requirement and return ONLY valid JSON. No markdown."
        )

        user_prompt = f"""
Customer payload:
{json.dumps(payload, indent=2)}

Return this exact JSON schema:
{{
  "score": 0,
  "priority": "High|Medium|Low",
  "reasons": ["reason 1", "reason 2"],
  "next_action": "specific next implementation step",
  "agent_reply": "short professional reply to the caller",
  "implementation_summary": {{
    "vertical": "industry/vertical",
    "workflow": "main workflow to automate",
    "integrations_needed": ["integration 1", "integration 2"],
    "estimated_complexity": "Low|Medium|High",
    "recommended_poc": "one sentence POC recommendation"
  }}
}}

Scoring guide:
- 80-100 High: clear use case, timeline, budget/integration intent.
- 60-79 Medium: useful use case but missing some details.
- 0-59 Low: vague requirement or weak buying intent.
""".strip()

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                    "max_tokens": 700,
                    "stream": False,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = self._parse_json(content)

            score = int(parsed.get("score", 50))
            score = max(0, min(100, score))

            priority = str(parsed.get("priority", "Medium")).title()
            if priority not in {"High", "Medium", "Low"}:
                priority = "Medium"

            reasons = parsed.get("reasons") or ["LLM-based qualification completed"]
            if not isinstance(reasons, list):
                reasons = [str(reasons)]

            summary = parsed.get("implementation_summary") or {}
            if not isinstance(summary, dict):
                summary = {}

            summary["agent_reply"] = parsed.get("agent_reply") or self._default_agent_reply(payload, priority, score)
            summary["ai_provider"] = "huggingface"
            summary["ai_model"] = self.model

            transcript = [
                {
                    "speaker": "agent",
                    "message": f"Hello {payload.get('customer_name', 'there')}, how can I help with your AI voice automation requirement?",
                },
                {"speaker": "customer", "message": payload.get("requirement", "")},
                {"speaker": "agent", "message": summary["agent_reply"]},
            ]

            return QualificationResult(
                score=score,
                priority=priority,
                reasons=[str(r) for r in reasons],
                next_action=str(parsed.get("next_action") or "Schedule a technical discovery call."),
                transcript=transcript,
                implementation_summary=summary,
            )

        except Exception as exc:
            print(f"[HF_AI] Falling back to rule-based qualification: {exc}")
            return None

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        text = text.strip()
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise

    @staticmethod
    def _default_agent_reply(payload: dict[str, Any], priority: str, score: int) -> str:
        return (
            f"Thanks {payload.get('customer_name', 'there')}. I captured your requirement. "
            f"This looks like a {priority.lower()} priority opportunity with a score of {score}. "
            "The next step is a short technical discovery call to confirm integrations and go-live scope."
        )
