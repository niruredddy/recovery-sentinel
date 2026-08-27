import os
from dotenv import load_dotenv
from models import PaymentFailureEvent, ActionPlan

load_dotenv()

MAX_AUTO_RETRY_ATTEMPTS = int(os.getenv("MAX_AUTO_RETRY_ATTEMPTS", 3))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.75))

class GuardrailEngine:
    @staticmethod
    def validate_plan(event: PaymentFailureEvent, plan: ActionPlan) -> ActionPlan:
        if plan.confidence < CONFIDENCE_THRESHOLD:
            plan.action_type = "merchant_escalation"
            plan.delay_minutes = 0
            plan.rationale = f"Confidence {plan.confidence:.2f} below minimum threshold {CONFIDENCE_THRESHOLD}"
            plan.guardrail_passed = False
            return plan

        if plan.action_type == "smart_retry" and event.retry_count >= MAX_AUTO_RETRY_ATTEMPTS:
            plan.action_type = "merchant_escalation"
            plan.delay_minutes = 0
            plan.rationale = f"Retry count {event.retry_count} reached maximum allowed limit ({MAX_AUTO_RETRY_ATTEMPTS})"
            plan.guardrail_passed = False
            return plan

        if plan.action_type == "smart_retry" and plan.delay_minutes <= 0:
            plan.delay_minutes = 15
            plan.rationale += " [Auto-adjusted delay to 15m default]"

        plan.guardrail_passed = True
        return plan