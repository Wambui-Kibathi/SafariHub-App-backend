import os
import requests

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = "https://api.paystack.co"

def initialize_transaction(email, amount, callback_url):
    """
    Initialize a Paystack transaction.
    amount in kobo (i.e., 1000 = 10.00 NGN)
    """
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    payload = {
        "email": email,
        "amount": int(amount * 100),  # convert Naira to kobo
        "callback_url": callback_url
    }
    response = requests.post(f"{BASE_URL}/transaction/initialize", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["data"]  # returns authorization_url and reference

def verify_transaction(reference):
    """
    Verify a Paystack transaction by reference.
    """
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    response = requests.get(f"{BASE_URL}/transaction/verify/{reference}", headers=headers)
    response.raise_for_status()
    return response.json()["data"]  # returns status, amount, customer info, etc.
