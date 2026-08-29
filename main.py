import uuid
import json
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def dashboard():
    logs = get_recent_audit_logs(limit=25)
    rows_html = ""
    for log in logs:
        badge_color = "#10b981" if log["guardrail_passed"] == 1 else "#ef4444"
        badge_text = "PASSED" if log["guardrail_passed"] == 1 else "GATED"
        payload_data = json.loads(log["decision_payload"])
        rationale = payload_data.get("rationale", "")
        
        rows_html += f"""
        <tr style="border-bottom: 1px solid #1f2937;">
            <td style="padding: 12px; font-family: monospace;">{log['transaction_id']}</td>
            <td style="padding: 12px;">{log['error_code']}</td>
            <td style="padding: 12px; text-transform: uppercase;">{log['payment_method']}</td>
            <td style="padding: 12px; font-weight: 600; color: #38bdf8;">{log['action_type']}</td>
            <td style="padding: 12px;">{log['confidence']:.2f}</td>
            <td style="padding: 12px;"><span style="background: {badge_color}22; color: {badge_color}; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{badge_text}</span></td>
            <td style="padding: 12px; color: #9ca3af; font-size: 13px;">{rationale}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RecoverySentinel Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #f3f4f6; margin: 0; padding: 40px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
            h1 {{ margin: 0; font-size: 24px; color: #ffffff; }}
            table {{ width: 100%; border-collapse: collapse; background: #111827; border-radius: 8px; overflow: hidden; }}
            th {{ background: #1f2937; padding: 14px 12px; text-align: left; font-size: 13px; text-transform: uppercase; color: #9ca3af; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>RecoverySentinel Live Audit Ledger</h1>
                    <p style="color: #9ca3af; margin-top: 4px;">Real-time agentic triage, deterministic guardrail verdicts, and recovery routing</p>
                </div>
                <div>
                    <a href="/docs" style="background: #2563eb; color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-size: 14px;">Interactive API Docs</a>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Transaction ID</th>
                        <th>Error Code</th>
                        <th>Method</th>
                        <th>Assigned Action</th>
                        <th>Confidence</th>
                        <th>Guardrail</th>
                        <th>Decision Rationale</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else '<tr><td colspan="7" style="padding: 24px; text-align: center; color: #6b7280;">No transactions processed yet. Trigger a webhook to view logs.</td></tr>'}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

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