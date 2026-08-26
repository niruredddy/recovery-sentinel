from datetime import datetime
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field

class PaymentFailureEvent(BaseModel):
    transaction_id: str
    merchant_id: str
    customer_id: str
    customer_phone: Optional[str] = None
    amount: float = Field(gt=0)
    currency: str = "INR"
    error_code: str
    error_description: str
    payment_method: Literal["upi", "card", "netbanking", "mandate"]
    issuer_bank: str
    retry_count: int = Field(default=0, ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ActionPlan(BaseModel):
    action_type: Literal[
        "smart_retry",
        "upi_push_intent",
        "hinglish_whatsapp",
        "card_fallback_link",
        "merchant_escalation"
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    delay_minutes: int = Field(ge=0)
    payload: Dict[str, Any]
    rationale: str
    guardrail_passed: bool

class AuditLogEntry(BaseModel):
    audit_id: str
    transaction_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_event: PaymentFailureEvent
    decision: ActionPlan
    status: Literal["queued", "blocked_by_guardrail", "dispatched", "failed"]