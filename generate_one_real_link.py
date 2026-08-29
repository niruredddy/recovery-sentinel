import os
import httpx
from dotenv import load_dotenv

load_dotenv()

key_id = os.getenv("RAZORPAY_KEY_ID")
key_secret = os.getenv("RAZORPAY_KEY_SECRET")

print(f"Key ID loaded: {key_id}")

url = "https://api.razorpay.com/v1/payment_links"
payload = {
    "amount": 149900,
    "currency": "INR",
    "description": "RecoverySentinel Live Recovery Test",
    "customer": {
        "name": "Customer Test",
        "contact": "+919876543210"
    }
}

response = httpx.post(url, json=payload, auth=(key_id, key_secret))
print(f"HTTP Status: {response.status_code}")
print("Full Response Body:", response.json())