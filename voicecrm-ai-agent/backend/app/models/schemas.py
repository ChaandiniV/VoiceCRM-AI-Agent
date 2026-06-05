from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field


class CallSimulationRequest(BaseModel):
    customer_name: str = Field(..., examples=["Aisha Khan"])
    phone: str = Field(..., examples=["+971501112233"])
    email: Optional[EmailStr] = Field(default=None, examples=["aisha@example.com"])
    company: Optional[str] = Field(default=None, examples=["Palm Clinic"])
    industry: Optional[str] = Field(default="General Services", examples=["Healthcare"])
    requirement: str = Field(..., examples=["We need an AI voice assistant for bookings and FAQs"])
    budget: Optional[str] = Field(default=None, examples=["12000 AED monthly"])
    timeline: Optional[str] = Field(default=None, examples=["Go live in 3 weeks"])
    preferred_channel: Optional[str] = Field(default="Email", examples=["WhatsApp follow-up"])


class LeadScore(BaseModel):
    score: int
    priority: str
    reasons: list[str]
    next_action: str


class CallSimulationResponse(BaseModel):
    call_id: int
    lead_id: int
    crm_mode: str
    automation_mode: str
    automation_status: str
    lead_score: LeadScore
    transcript: list[dict[str, str]]
    implementation_summary: dict[str, Any]




class BrowserVoiceLeadRequest(BaseModel):
    customer_name: str = Field(default="Website Caller", examples=["Aisha Khan"])
    phone: str = Field(default="browser-demo", examples=["+971501112233"])
    email: Optional[EmailStr] = Field(default=None, examples=["aisha@example.com"])
    company: Optional[str] = Field(default=None, examples=["Palm Clinic"])
    industry: Optional[str] = Field(default="General Services", examples=["Healthcare"])
    spoken_transcript: str = Field(..., examples=["We need an AI voice assistant for bookings and FAQs"])
    budget: Optional[str] = Field(default=None, examples=["12000 AED monthly"])
    timeline: Optional[str] = Field(default=None, examples=["Go live in 3 weeks"])
    preferred_channel: Optional[str] = Field(default="Email", examples=["WhatsApp follow-up"])


class BrowserVoiceLeadResponse(CallSimulationResponse):
    agent_reply: str
    voice_demo_note: str


class RoadmapResponse(BaseModel):
    lead_id: int
    phases: list[dict[str, Any]]
    risks: list[str]
    recommended_demo_assets: list[str]


class GenericWebhookResponse(BaseModel):
    status: str
    stored_event_id: int
