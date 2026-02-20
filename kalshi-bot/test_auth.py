#!/usr/bin/env python3
"""Quick auth test for Kalshi API"""
import os, time, base64, requests
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_KEY_ID = os.getenv('KALSHI_API_KEY_ID')
PRIVATE_KEY_PEM = os.getenv('KALSHI_PRIVATE_KEY')
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

# Load the private key
private_key = serialization.load_pem_private_key(PRIVATE_KEY_PEM.encode(), password=None)

def get_auth_headers(method: str, path: str) -> dict:
    timestamp_ms = str(int(time.time() * 1000))
    message = timestamp_ms + method.upper() + path
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return {
        'KALSHI-ACCESS-KEY': API_KEY_ID,
        'KALSHI-ACCESS-TIMESTAMP': timestamp_ms,
        'KALSHI-ACCESS-SIGNATURE': base64.b64encode(signature).decode('utf-8'),
        'Content-Type': 'application/json',
    }

# Test 1: Public endpoint (no auth)
print("=== Test 1: Public market data (no auth) ===")
resp = requests.get(f'{BASE_URL}/markets', params={'limit': 5})
print(f"Status: {resp.status_code}")
if resp.ok:
    data = resp.json()
    markets = data.get('markets', [])
    print(f"Got {len(markets)} markets. First: {markets[0].get('ticker') if markets else 'none'}")
else:
    print(f"Error: {resp.text[:300]}")

# Test 2: Authenticated endpoint
print("\n=== Test 2: GET /portfolio/balance (auth required) ===")
path = '/trade-api/v2/portfolio/balance'
headers = get_auth_headers('GET', path)
resp = requests.get(f'{BASE_URL}/portfolio/balance', headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")
