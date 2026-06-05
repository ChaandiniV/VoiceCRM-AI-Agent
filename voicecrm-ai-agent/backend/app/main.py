from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from backend.app.config import get_settings
from backend.app.models.schemas import (
    BrowserVoiceLeadRequest,
    BrowserVoiceLeadResponse,
    CallSimulationRequest,
    CallSimulationResponse,
    GenericWebhookResponse,
    LeadScore,
    RoadmapResponse,
)
from backend.app.services.agent import LeadQualificationAgent
from backend.app.services.automation_client import AutomationClient
from backend.app.services.crm_client import CRMClient
from backend.app.services.database import (
    add_transcript,
    create_call,
    create_lead,
    fetch_all,
    fetch_lead,
    init_db,
    store_webhook_event,
    update_call_status,
)
from backend.app.services.roadmap import build_implementation_roadmap

settings = get_settings()
app = FastAPI(
    title="VoiceCRM AI Agent",
    description="Voice AI + CRM automation implementation project for AI Solutions Engineer roles.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = LeadQualificationAgent()
crm_client = CRMClient()
automation_client = AutomationClient()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "VoiceCRM AI Agent",
        "crm_provider": settings.crm_provider,
    }


@app.post("/api/demo/simulate-call", response_model=CallSimulationResponse)
def simulate_call(payload: CallSimulationRequest) -> CallSimulationResponse:
    init_db()
    payload_dict = payload.model_dump()
    call_id = create_call(
        call_sid="demo-call",
        caller_phone=payload.phone,
        customer_name=payload.customer_name,
        source="demo_api",
    )

    result = agent.qualify(payload_dict)
    for turn in result.transcript:
        add_transcript(call_id, turn["speaker"], turn["message"])

    crm_payload = {
        **payload_dict,
        "lead_score": result.score,
        "priority": result.priority,
        "next_action": result.next_action,
        "implementation_summary": result.implementation_summary,
    }
    crm_result = crm_client.create_or_update_lead(crm_payload)

    lead_id = create_lead(
        call_id=call_id,
        customer_name=payload.customer_name,
        phone=payload.phone,
        email=payload.email,
        company=payload.company,
        industry=payload.industry,
        requirement=payload.requirement,
        budget=payload.budget,
        timeline=payload.timeline,
        preferred_channel=payload.preferred_channel,
        lead_score=result.score,
        priority=result.priority,
        next_action=result.next_action,
        crm_status=crm_result.get("status", "unknown"),
        crm_record_id=crm_result.get("record_id"),
    )

    automation_payload = {
        "event_type": "qualified_voice_lead",
        "source": "voicecrm_ai_agent",
        "call_id": call_id,
        "lead_id": lead_id,
        "customer_name": payload.customer_name,
        "phone": payload.phone,
        "email": payload.email,
        "company": payload.company,
        "industry": payload.industry,
        "requirement": payload.requirement,
        "budget": payload.budget,
        "timeline": payload.timeline,
        "preferred_channel": payload.preferred_channel,
        "lead_score": result.score,
        "priority": result.priority,
        "next_action": result.next_action,
        "reasons": result.reasons,
        "implementation_summary": result.implementation_summary,
        "workflow": result.implementation_summary.get("workflow"),
        "integrations_needed": ", ".join(result.implementation_summary.get("integrations_needed", [])),
        "estimated_complexity": result.implementation_summary.get("estimated_complexity"),
        "recommended_poc": result.implementation_summary.get("recommended_poc"),
        "transcript": result.transcript,
        "crm_mode": crm_result.get("mode", "mock"),
        "crm_status": crm_result.get("status", "unknown"),
        "crm_record_id": crm_result.get("record_id"),
    }
    automation_result = automation_client.send_qualified_lead(automation_payload)
    store_webhook_event(
        "make",
        "outbound_qualified_lead",
        {"automation_result": automation_result, "payload": automation_payload},
    )

    update_call_status(call_id, "completed")

    return CallSimulationResponse(
        call_id=call_id,
        lead_id=lead_id,
        crm_mode=crm_result.get("mode", "mock"),
        automation_mode=automation_result.get("mode", "local_mock"),
        automation_status=automation_result.get("status", "unknown"),
        lead_score=LeadScore(
            score=result.score,
            priority=result.priority,
            reasons=result.reasons,
            next_action=result.next_action,
        ),
        transcript=result.transcript,
        implementation_summary=result.implementation_summary,
    )


@app.get("/voice-demo", response_class=HTMLResponse)
def browser_voice_demo():
    project_root = Path(__file__).resolve().parents[2]
    demo_path = project_root / "frontend" / "voice_demo.html"

    if not demo_path.exists():
        return HTMLResponse(
            content=f"""
            <h2>Voice demo file not found</h2>
            <p>Expected path: {demo_path}</p>
            """,
            status_code=404,
        )

    return FileResponse(str(demo_path), media_type="text/html")


@app.post("/api/voice/browser-lead", response_model=BrowserVoiceLeadResponse)
def browser_voice_lead(payload: BrowserVoiceLeadRequest) -> BrowserVoiceLeadResponse:
    """Convert browser speech transcript into a qualified VoiceCRM lead.

    This is the free voice layer for the portfolio demo:
    browser microphone -> transcript -> FastAPI -> AI qualification -> Make webhook.
    """
    init_db()
    requirement = payload.spoken_transcript.strip()
    payload_dict = {
        "customer_name": payload.customer_name,
        "phone": payload.phone,
        "email": payload.email,
        "company": payload.company,
        "industry": payload.industry,
        "requirement": requirement,
        "budget": payload.budget,
        "timeline": payload.timeline,
        "preferred_channel": payload.preferred_channel,
    }

    call_id = create_call(
        call_sid="browser-voice-demo",
        caller_phone=payload.phone,
        customer_name=payload.customer_name,
        source="browser_voice_demo",
    )

    add_transcript(call_id, "agent", "Hello, this is the VoiceCRM AI assistant. Please describe what you need help with.")
    add_transcript(call_id, "customer", requirement)

    result = agent.qualify(payload_dict)
    for turn in result.transcript:
        add_transcript(call_id, turn["speaker"], turn["message"])

    crm_payload = {
        **payload_dict,
        "lead_score": result.score,
        "priority": result.priority,
        "next_action": result.next_action,
        "implementation_summary": result.implementation_summary,
    }
    crm_result = crm_client.create_or_update_lead(crm_payload)

    lead_id = create_lead(
        call_id=call_id,
        customer_name=payload.customer_name,
        phone=payload.phone,
        email=payload.email,
        company=payload.company,
        industry=payload.industry,
        requirement=requirement,
        budget=payload.budget,
        timeline=payload.timeline,
        preferred_channel=payload.preferred_channel,
        lead_score=result.score,
        priority=result.priority,
        next_action=result.next_action,
        crm_status=crm_result.get("status", "unknown"),
        crm_record_id=crm_result.get("record_id"),
    )

    agent_reply = result.implementation_summary.get("agent_reply") or (
        f"Thanks {payload.customer_name}. I captured your request. "
        f"This is a {result.priority.lower()} priority lead with a score of {result.score}. "
        f"Next step: {result.next_action}"
    )
    add_transcript(call_id, "agent", agent_reply)

    automation_payload = {
        "event_type": "browser_voice_qualified_lead",
        "source": "voicecrm_browser_voice_demo",
        "call_id": call_id,
        "lead_id": lead_id,
        "customer_name": payload.customer_name,
        "phone": payload.phone,
        "email": payload.email,
        "company": payload.company,
        "industry": payload.industry,
        "requirement": requirement,
        "budget": payload.budget,
        "timeline": payload.timeline,
        "preferred_channel": payload.preferred_channel,
        "lead_score": result.score,
        "priority": result.priority,
        "next_action": result.next_action,
        "reasons": result.reasons,
        "implementation_summary": result.implementation_summary,
        "workflow": result.implementation_summary.get("workflow"),
        "integrations_needed": ", ".join(result.implementation_summary.get("integrations_needed", [])),
        "estimated_complexity": result.implementation_summary.get("estimated_complexity"),
        "recommended_poc": result.implementation_summary.get("recommended_poc"),
        "transcript": result.transcript + [{"speaker": "agent", "message": agent_reply}],
        "crm_mode": crm_result.get("mode", "mock"),
        "crm_status": crm_result.get("status", "unknown"),
        "crm_record_id": crm_result.get("record_id"),
    }
    automation_result = automation_client.send_qualified_lead(automation_payload)
    store_webhook_event(
        "make",
        "outbound_browser_voice_qualified_lead",
        {"automation_result": automation_result, "payload": automation_payload},
    )

    update_call_status(call_id, "completed")

    return BrowserVoiceLeadResponse(
        call_id=call_id,
        lead_id=lead_id,
        crm_mode=crm_result.get("mode", "mock"),
        automation_mode=automation_result.get("mode", "local_mock"),
        automation_status=automation_result.get("status", "unknown"),
        lead_score=LeadScore(
            score=result.score,
            priority=result.priority,
            reasons=result.reasons,
            next_action=result.next_action,
        ),
        transcript=result.transcript + [{"speaker": "agent", "message": agent_reply}],
        implementation_summary=result.implementation_summary,
        agent_reply=agent_reply,
        voice_demo_note="Real browser microphone speech-to-text and browser text-to-speech; Twilio/OpenAI voice can be added later for production calls.",
    )


@app.get("/api/calls")
def list_calls() -> list[dict[str, Any]]:
    init_db()
    return fetch_all("calls")


@app.get("/api/leads")
def list_leads() -> list[dict[str, Any]]:
    init_db()
    return fetch_all("leads")


@app.get("/api/transcripts")
def list_transcripts() -> list[dict[str, Any]]:
    init_db()
    return fetch_all("transcripts")


@app.get("/api/webhook-events")
def list_webhook_events() -> list[dict[str, Any]]:
    init_db()
    return fetch_all("webhook_events")


@app.get("/api/roadmap/{lead_id}", response_model=RoadmapResponse)
def roadmap(lead_id: int) -> RoadmapResponse:
    init_db()
    lead = fetch_lead(lead_id)
    if not lead:
        return RoadmapResponse(lead_id=lead_id, phases=[], risks=["Lead not found"], recommended_demo_assets=[])
    return RoadmapResponse(**build_implementation_roadmap(lead))


@app.get("/api/export/leads.csv")
def export_leads_csv() -> StreamingResponse:
    init_db()
    leads = fetch_all("leads")
    output = io.StringIO()
    fieldnames = [
        "id",
        "customer_name",
        "phone",
        "email",
        "company",
        "industry",
        "lead_score",
        "priority",
        "next_action",
        "crm_status",
        "crm_record_id",
        "created_at",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for lead in leads:
        writer.writerow({key: lead.get(key) for key in fieldnames})
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=voicecrm_leads.csv"},
    )


@app.post("/webhooks/twilio/voice")
async def twilio_inbound_voice(request: Request) -> Response:
    """Twilio-style inbound call webhook.

    In a live Twilio setup, configure your Twilio phone number's Voice webhook
    to point to this endpoint through an HTTPS URL, for example with ngrok.
    """
    form = await request.form()
    payload = dict(form)
    event_id = store_webhook_event("twilio", "inbound_voice", payload)
    caller = payload.get("From", "unknown")
    call_sid = payload.get("CallSid", f"webhook-{event_id}")
    create_call(call_sid=call_sid, caller_phone=caller, customer_name="Unknown Caller", source="twilio_webhook")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="{settings.public_base_url}/webhooks/twilio/process" method="POST" speechTimeout="auto">
    <Say voice="alice">Hello. This is {settings.business_name}'s AI assistant. Please tell me what you need help with today.</Say>
  </Gather>
  <Say voice="alice">Sorry, I did not receive a response. Our team will follow up shortly.</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.post("/webhooks/twilio/process")
async def twilio_process_speech(
    SpeechResult: str = Form(default=""),
    From: str = Form(default="unknown"),
    CallSid: str = Form(default="unknown"),
) -> Response:
    payload = {"SpeechResult": SpeechResult, "From": From, "CallSid": CallSid}
    store_webhook_event("twilio", "speech_result", payload)

    # For demo purposes, we store a lightweight transcript turn.
    # Full lead creation is handled by /api/demo/simulate-call.
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">Thank you. I captured your request. A solutions engineer will review your details and follow up with a demo plan.</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.post("/webhooks/twilio/status", response_model=GenericWebhookResponse)
async def twilio_status_callback(request: Request) -> GenericWebhookResponse:
    form = await request.form()
    event_id = store_webhook_event("twilio", "status_callback", dict(form))
    return GenericWebhookResponse(status="stored", stored_event_id=event_id)


@app.post("/webhooks/crm/hubspot", response_model=GenericWebhookResponse)
async def hubspot_crm_webhook(request: Request) -> GenericWebhookResponse:
    payload = await request.json()
    event_id = store_webhook_event("hubspot", "crm_event", payload)
    return GenericWebhookResponse(status="stored", stored_event_id=event_id)
