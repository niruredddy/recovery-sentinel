import json
from models import PaymentFailureEvent
from agent import RecoveryAgent

agent = RecoveryAgent()

with open("mock_failures.json", "r") as f:
    failures = json.load(f)

for raw in failures[:5]:
    event = PaymentFailureEvent(**raw)
    plan = agent.diagnose_and_plan(event)
    print(f"TXN: {event.transaction_id} | Code: {event.error_code} (Retry #{event.retry_count})")
    print(f"  -> Decision: {plan.action_type} (Delay: {plan.delay_minutes}m, Passed: {plan.guardrail_passed})")
    print(f"  -> Rationale: {plan.rationale}\n")