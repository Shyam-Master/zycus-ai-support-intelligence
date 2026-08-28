from pydantic import BaseModel
from typing import List, Optional

class RiskItem(BaseModel):
    risk: str
    severity: str
    evidence_quote: str
    ticket_id: str
    reason: str

class SignalItem(BaseModel):
    signal: str
    evidence_quote: str
    ticket_id: str

class TamBriefResponse(BaseModel):
    account_id: str
    account_name: str
    executive_summary: str
    open_risks: List[RiskItem]
    escalation_signals: List[SignalItem]
    churn_risk_signals: List[SignalItem]
    recommended_talking_points: List[str]
    recent_ticket_count: int
    overall_health: str
