import os
import requests
from requests.auth import HTTPBasicAuth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")  # "sandbox" or "live"

# PayPal endpoints
BASE_URLS = {
    "sandbox": "https://api-m.sandbox.paypal.com",
    "live": "https://api-m.paypal.com"
}
BASE_URL = BASE_URLS.get(PAYPAL_MODE, BASE_URLS["sandbox"])


def get_access_token():
    """Get PayPal OAuth access token"""
    url = f"{BASE_URL}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}

    try:
        response = requests.post(url, headers=headers, data=data,
                                 auth=HTTPBasicAuth(PAYPAL_CLIENT_ID, PAYPAL_SECRET))
        response.raise_for_status()
        token = response.json()["access_token"]
        logger.info("PayPal access token retrieved successfully.")
        return token
    except requests.RequestException as e:
        logger.error(f"Error getting PayPal access token: {e}")
        raise


def create_order(amount, currency="USD"):
    """Create a PayPal order for a given amount"""
    access_token = get_access_token()
    url = f"{BASE_URL}/v2/checkout/orders"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": currency, "value": f"{amount:.2f}"}}]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"PayPal order created successfully: {response.json()['id']}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error creating PayPal order: {e}")
        raise


def capture_order(order_id):
    """Capture a PayPal order by order ID"""
    access_token = get_access_token()
    url = f"{BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        logger.info(f"PayPal payment captured successfully: {order_id}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error capturing PayPal order {order_id}: {e}")
        raise
