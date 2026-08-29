import json
import time
import httpx

with open("mock_failures.json", "r") as f:
    records = json.load(f)

print("Dispatching failure events to live webhook...")
with httpx.Client(timeout=30.0) as client:
    for record in records:
        try:
            response = client.post("http://127.0.0.1:8000/webhook/payment-failure", json=record)
            if response.status_code == 200:
                data = response.json()
                print(f"Logged {record['transaction_id']} -> {data['decision']['action_type']}")
            else:
                print(f"Failed {record['transaction_id']} -> Status {response.status_code}")
        except Exception as e:
            print(f"Skipping {record['transaction_id']} due to network delay: {e}")
        time.sleep(0.1)

print("\nSeeding complete. Check http://127.0.0.1:8000 for updated logs.")