import uuid
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from models import PaymentFailureEvent, ActionPlan, AuditLogEntry
from agent import RecoveryAgent
from database import init_db, record_audit_entry, get_recent_audit_logs

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="RecoverySentinel Engine",
    description="Agentic Payment Failure Triage & Bounded Recovery API",
    version="1.0.0",
    lifespan=lifespan
)

agent = RecoveryAgent()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "RecoverySentinel"}

@app.post("/webhook/payment-failure", status_code=status.HTTP_200_OK)
def handle_payment_failure(event: PaymentFailureEvent):
    try:
        plan: ActionPlan = agent.diagnose_and_plan(event)
        
        entry_status = "dispatched" if plan.guardrail_passed else "blocked_by_guardrail"
        if plan.action_type == "merchant_escalation":
            entry_status = "queued"

        audit_entry = AuditLogEntry(
            audit_id=f"aud_{uuid.uuid4().hex[:10]}",
            transaction_id=event.transaction_id,
            input_event=event,
            decision=plan,
            status=entry_status
        )

        record_audit_entry(audit_entry)

        return {
            "success": True,
            "audit_id": audit_entry.audit_id,
            "decision": plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit/logs")
def fetch_audit_logs(limit: int = 50):
    logs = get_recent_audit_logs(limit=limit)
    return {"count": len(logs), "logs": logs}

@app.get("/")
def root():
    return {
        "service": "RecoverySentinel Engine",
        "status": "healthy",
        "docs_url": "/docs",
        "endpoints": {
            "webhook": "/webhook/payment-failure",
            "audit_logs": "/audit/logs"
        }
    }