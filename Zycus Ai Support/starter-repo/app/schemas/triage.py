from pydantic import BaseModel, Field
from typing import List, Optional

class TriageRequest(BaseModel):
    subject: str
    body: str

class TriageResponse(BaseModel):
    product_area: str
    issue_category: str
    urgency: str = Field(pattern='^P[1-4]$')
    reasoning: str
    relevant_kb_docs: List[str]
    known_issue_patterns: List[str]
    recommended_team: str
    draft_response: str
