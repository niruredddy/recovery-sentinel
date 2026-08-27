from models import PaymentFailureEvent, ActionPlan
from guardrails import GuardrailEngine

class RecoveryAgent:
    def __init__(self):
        self.guardrail = GuardrailEngine()

    def diagnose_and_plan(self, event: PaymentFailureEvent) -> ActionPlan:
        error_code = event.error_code.upper()
        
        if "DOWNTIME" in error_code or "NPCI" in error_code:
            delay = 30 if event.retry_count == 0 else 60
            raw_plan = ActionPlan(
                action_type="smart_retry",
                confidence=0.92,
                delay_minutes=delay,
                payload={"target_gateway": "backup_switch", "retry_attempt": event.retry_count + 1},
                rationale="Infrastructure switch error detected; scheduling backoff retry on backup route.",
                guardrail_passed=False
            )
        elif "INSUFFICIENT_FUNDS" in error_code:
            raw_plan = ActionPlan(
                action_type="hinglish_whatsapp",
                confidence=0.88,
                delay_minutes=10,
                payload={
                    "phone": event.customer_phone,
                    "template": "insufficient_balance_nudge",
                    "deep_link": f"https://rzp.io/i/{event.transaction_id}"
                },
                rationale="Soft decline due to balance; sending quick customer nudge with alternate payment link.",
                guardrail_passed=False
            )
        elif "AUTH" in error_code or "TIMEOUT" in error_code:
            raw_plan = ActionPlan(
                action_type="upi_push_intent",
                confidence=0.85,
                delay_minutes=2,
                payload={"intent_ttl_sec": 300, "customer_id": event.customer_id},
                rationale="Authentication drop; pushing real-time collect intent to customer UPI handle.",
                guardrail_passed=False
            )
        elif "MANDATE" in error_code:
            raw_plan = ActionPlan(
                action_type="card_fallback_link",
                confidence=0.81,
                delay_minutes=0,
                payload={"customer_id": event.customer_id, "amount": event.amount},
                rationale="Mandate acknowledgment failure; generating immediate manual authorization card link.",
                guardrail_passed=False
            )
        else:
            raw_plan = ActionPlan(
                action_type="merchant_escalation",
                confidence=0.50,
                delay_minutes=0,
                payload={"raw_error": event.error_description},
                rationale="Unclassified failure pattern; routing to merchant operations.",
                guardrail_passed=False
            )

        return self.guardrail.validate_plan(event, raw_plan)