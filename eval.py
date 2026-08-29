import json
from collections import defaultdict
from models import PaymentFailureEvent
from agent import RecoveryAgent

def run_evaluation(data_file: str = "mock_failures.json"):
    with open(data_file, "r") as f:
        failures = json.load(f)

    agent = RecoveryAgent()
    
    total_events = len(failures)
    total_amount_at_risk = 0.0
    amount_recovered_projected = 0.0
    action_counts = defaultdict(int)
    guardrail_passes = 0
    guardrail_blocks = 0

    recovery_multipliers = {
        "smart_retry": 0.70,
        "upi_push_intent": 0.65,
        "hinglish_whatsapp": 0.45,
        "card_fallback_link": 0.50,
        "merchant_escalation": 0.15
    }

    for raw in failures:
        event = PaymentFailureEvent(**raw)
        total_amount_at_risk += event.amount
        plan = agent.diagnose_and_plan(event)
        
        action_counts[plan.action_type] += 1
        
        if plan.guardrail_passed:
            guardrail_passes += 1
            projected_recovery = event.amount * recovery_multipliers.get(plan.action_type, 0.0)
            amount_recovered_projected += projected_recovery
        else:
            guardrail_blocks += 1
            amount_recovered_projected += event.amount * recovery_multipliers["merchant_escalation"]

    recovery_rate = (amount_recovered_projected / total_amount_at_risk) * 100 if total_amount_at_risk > 0 else 0
    guardrail_pass_rate = (guardrail_passes / total_events) * 100 if total_events > 0 else 0

    print("=" * 60)
    print("RECOVERYSENTINEL — BATCH EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Transactions Evaluated : {total_events}")
    print(f"Total Gross Value at Risk    : ₹{total_amount_at_risk:,.2f}")
    print(f"Projected Recovery Value     : ₹{amount_recovered_projected:,.2f}")
    print(f"Projected Recovery Rate      : {recovery_rate:.2f}%\n")
    
    print("-" * 60)
    print("GUARDRAIL SAFETY TELEMETRY")
    print("-" * 60)
    print(f"Approved Actions (Passed)    : {guardrail_passes} ({guardrail_pass_rate:.1f}%)")
    print(f"Blocked / Escalated (Gated)  : {guardrail_blocks} ({100 - guardrail_pass_rate:.1f}%)\n")
    
    print("-" * 60)
    print("ACTION ROUTING BREAKDOWN")
    print("-" * 60)
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_events) * 100
        print(f"  • {action:<25}: {count:2d} ({percentage:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    run_evaluation()