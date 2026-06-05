from backend.app.services.agent import LeadQualificationAgent


def test_high_intent_lead_scores_high():
    agent = LeadQualificationAgent()
    result = agent.qualify(
        {
            "customer_name": "Aisha Khan",
            "company": "Palm Clinic",
            "industry": "Healthcare",
            "requirement": "We need appointment booking, FAQs, and customer support automation.",
            "budget": "12000 AED monthly",
            "timeline": "Go live in 3 weeks",
            "preferred_channel": "WhatsApp follow-up",
        }
    )
    assert result.score >= 80
    assert result.priority == "High"
    assert result.transcript
