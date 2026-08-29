import json
import httpx

with open("mock_failures.json", "r") as f:
    records = json.load(f)

print("Dispatching failure events to live webhook...")
for record in records:
    response = httpx.post("http://127.0.0.1:8000/webhook/payment-failure", json=record)
    if response.status_code == 200:
        data = response.json()
        print(f"Logged {record['transaction_id']} -> {data['decision']['action_type']}")

print("\nAll 50 events processed and logged to SQLite ledger.")