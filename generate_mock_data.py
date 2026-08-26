import json
import random
from datetime import datetime, timezone

error_catalog = [
    {
        "code": "BANK_DOWNTIME_NPCI",
        "desc": "NPCI switch timeout during debit request",
        "method": "upi",
        "bank": "SBI"
    },
    {
        "code": "INSUFFICIENT_FUNDS_DECLINE",
        "desc": "Card declined by issuer due to insufficient balance",
        "method": "card",
        "bank": "HDFC"
    },
    {
        "code": "MANDATE_PRE_DEBIT_UNACKNOWLEDGED",
        "desc": "Mandate notification window not acknowledged",
        "method": "mandate",
        "bank": "ICICI"
    },
    {
        "code": "AUTH_OTP_TIMEOUT",
        "desc": "Customer failed to complete 2FA inside 180s",
        "method": "upi",
        "bank": "AXIS"
    },
    {
        "code": "NETBANKING_GATEWAY_RESET",
        "desc": "TCP connection reset by merchant netbanking portal",
        "method": "netbanking",
        "bank": "KOTAK"
    }
]

records = []
for index in range(1, 51):
    err = random.choice(error_catalog)
    records.append({
        "transaction_id": f"pay_mock_{index:04d}",
        "merchant_id": f"mer_{random.randint(101, 115)}",
        "customer_id": f"cust_{random.randint(500, 999)}",
        "customer_phone": f"+9198{random.randint(10000000, 99999999)}",
        "amount": round(random.uniform(299.0, 24999.0), 2),
        "currency": "INR",
        "error_code": err["code"],
        "error_description": err["desc"],
        "payment_method": err["method"],
        "issuer_bank": err["bank"],
        "retry_count": random.choice([0, 0, 1, 2, 3]),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

with open("mock_failures.json", "w") as fp:
    json.dump(records, fp, indent=2)