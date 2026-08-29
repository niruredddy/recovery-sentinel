import os
import httpx
from dotenv import load_dotenv

load_dotenv()

key_id = os.getenv("RAZORPAY_KEY_ID")
key_secret = os.getenv("RAZORPAY_KEY_SECRET")

print(f"Testing Key ID: {key_id}")
print(f"Testing Secret: {'*' * len(key_secret) if key_secret else 'None'}")

url = "https://api.razorpay.com/v1/payment_links"
payload = {
    "amount": 50000,
    "currency": "INR",
    "description": "Direct Razorpay Test Link",
    "customer": {
        "name": "Niranjan Reddy",
        "contact": "+919876543210",
        "email": "test@example.com"
    }
}

response = httpx.post(url, json=payload, auth=(key_id, key_secret))
print(f"\nStatus Code: {response.status_code}")
print("Response JSON:")
print(response.json())