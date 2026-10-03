from typing import Any
from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(min_length=1)


class NLIRequest(BaseModel):
    statement_a: str
    statement_b: str


class ClaimCreate(BaseModel):
    claim_id: str
    claim_text: str
    claim_type: str = 'GENERAL'


class FeedbackRequest(BaseModel):
    claim_id_fk: int
    reviewer: str
    ai_prediction: str
    ai_risk_score: float
    decision: str
    comments: str = ''


class GenericResponse(BaseModel):
    data: Any
    disclaimer: str = 'ClaimGuard AI provides AI-assisted claim analysis and investigation support. AI predictions are not definitive determinations of fraud, liability, or coverage.'
