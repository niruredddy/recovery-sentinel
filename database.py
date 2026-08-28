import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from models import PaymentFailureEvent, ActionPlan, AuditLogEntry

DB_FILE = "recovery_ledger.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            audit_id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            error_code TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            action_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            delay_minutes INTEGER NOT NULL,
            guardrail_passed INTEGER NOT NULL,
            raw_event TEXT NOT NULL,
            decision_payload TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def record_audit_entry(entry: AuditLogEntry):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (
            audit_id, transaction_id, timestamp, error_code, payment_method,
            action_type, confidence, delay_minutes, guardrail_passed,
            raw_event, decision_payload, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.audit_id,
        entry.transaction_id,
        entry.timestamp.isoformat(),
        entry.input_event.error_code,
        entry.input_event.payment_method,
        entry.decision.action_type,
        entry.decision.confidence,
        entry.decision.delay_minutes,
        1 if entry.decision.guardrail_passed else 0,
        entry.input_event.model_dump_json(),
        entry.decision.model_dump_json(),
        entry.status
    ))
    conn.commit()
    conn.close()

def get_recent_audit_logs(limit: int = 50) -> List[dict]:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]