# RecoverySentinel

An agentic failure-triage engine designed to diagnose dropped transactions and trigger bounded, policy-compliant payment recovery workflows.

## Features
- **Event Ingestion:** Processes webhook payloads for failed checkout, UPI, card, and recurring mandate payments.
- **Agentic Diagnosis:** Classifies technical vs. customer-induced payment failures to determine optimal recovery routing.
- **Deterministic Guardrails:** Rejects ungrounded decisions and enforces strict retry caps.
- **Audit Ledger:** Structured logging of all decision trails and automated recovery actions.

## Quickstart

1. Clone the repository and enter the directory:
   ```bash
   git clone https://github.com/niruredddy/recovery-sentinel.git
   cd recovery-sentinel
   ```

2. Set up the virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Generate mock transaction data:
   ```cmd
   python generate_mock_data.py
   ```
