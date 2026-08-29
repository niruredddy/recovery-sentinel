import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

def create_recovery_payment_link(amount: float, transaction_id: str, customer_phone: Optional[str] = None) -> str:
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET or "yourKeyHere" in RAZORPAY_KEY_ID:
        return f"https://rzp.io/i/mock_{transaction_id}"

    url = "https://api.razorpay.com/v1/payment_links"
    payload = {
        "amount": int(amount * 100),
        "currency": "INR",
        "accept_partial": False,
        "description": f"Payment recovery for failure ref: {transaction_id}",
        "customer": {
            "contact": customer_phone or "+919876543210"
        },
        "notify": {"sms": False, "email": False},
        "reminder_enable": True
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
            timeout=5.0
        )
        if response.status_code in (200, 201):
            return response.json().get("short_url", f"https://rzp.io/i/{transaction_id}")
    except Exception:
        pass

    return f"https://rzp.io/i/{transaction_id}"