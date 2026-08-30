# RecoverySentinel

An intelligent payment failure recovery engine that diagnoses failed transactions, enforces safety rules, generates Razorpay recovery links, and records all actions in an audit ledger.

Built for **Razorpay AI Buildathon — Track 3: AI Revenue Recovery**.

---

## What It Does

When payments fail (due to OTP timeouts, low balances, or bank downtime), blind retries cause card blocks and lost revenue. **RecoverySentinel** automates recovery:

* **Analyzes Root Cause:** Classifies errors like `AUTH_OTP_TIMEOUT`, `INSUFFICIENT_FUNDS_DECLINE`, and `BANK_DOWNTIME_NPCI`.
* **Safety Guardrails:** Enforces a maximum of 3 retries and blocks low-confidence actions (`< 0.70`).
* **Razorpay Links:** Generates payment recovery links via Razorpay API (with offline fallback).
* **Audit Dashboard:** Displays every transaction, decision rationale, and status in a real-time web UI.
* **Evaluation Metrics:** Includes a benchmark script (`eval.py`) to measure recovered revenue and safety rates.

---

## System Workflow

1. Payment failure webhook received by FastAPI.
2. Triage agent selects the best recovery strategy.
3. Guardrails check whether the action is safe (`PASSED` vs `GATED`).
4. Razorpay recovery link is generated.
5. Decision is saved to SQLite and displayed on the live dashboard.

---

## Tech Stack

* **Language & Framework:** Python 3.12, FastAPI, Uvicorn
* **Data Validation:** Pydantic
* **Database:** SQLite3
* **API Client:** HTTPX, Razorpay Test API
* **Frontend:** Built-in HTML Dashboard

---

## Project Structure

* `agent.py` — Triage agent and recovery decision logic
* `guardrails.py` — Deterministic safety checks and retry limits
* `models.py` — Pydantic schemas and data models
* `razorpay_client.py` — Razorpay payment link generator
* `db.py` — SQLite ledger database operations
* `main.py` — FastAPI webhook and audit dashboard UI
* `eval.py` — Evaluation harness and benchmark metrics
* `seed_ledger.py` — Batch test runner for 50 failure scenarios
* `mock_failures.json` — Test failure dataset

---

## How to Run

### 1. Set Up Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
## 2. Configure API Keys (Optional)
Create a .env file in the root directory: 
```
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```
(If no keys are provided, the system uses built-in fallback links.)

##3. Start the Server
```Bash
uvicorn main:app --reload --port 8000
```
Open
http://127.0.0.1:8000 in your browser to view the Live Audit Dashboard.

## 4. Ingest Test Data
In a second terminal:
```Bash
python seed_ledger.py
```
## 5. Run Evaluation Benchmark
```Bash
python eval.py
```
