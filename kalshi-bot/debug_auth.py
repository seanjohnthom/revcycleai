#!/usr/bin/env python3
"""Try multiple auth formats to find the correct Kalshi v2 signature"""
import os, time, base64, requests
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_KEY_ID = os.getenv('KALSHI_API_KEY_ID')
PRIVATE_KEY_PEM = os.getenv('KALSHI_PRIVATE_KEY')
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

private_key = serialization.load_pem_private_key(PRIVATE_KEY_PEM.encode(), password=None)

def sign(message: str) -> str:
    sig = private_key.sign(message.encode('utf-8'), padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(sig).decode('utf-8')

def try_auth(label, path_for_signing):
    ts = str(int(time.time() * 1000))
    msg = ts + 'GET' + path_for_signing
    headers = {
        'KALSHI-ACCESS-KEY': API_KEY_ID,
        'KALSHI-ACCESS-TIMESTAMP': ts,
        'KALSHI-ACCESS-SIGNATURE': sign(msg),
        'Content-Type': 'application/json',
    }
    resp = requests.get(f'{BASE_URL}/portfolio/balance', headers=headers)
    print(f"[{label}] {resp.status_code} — msg='{msg[:60]}...'")
    if resp.ok:
        print(f"  SUCCESS: {resp.text[:200]}")
    else:
        print(f"  {resp.text[:150]}")

# Try different path formats
try_auth("full path",         "/trade-api/v2/portfolio/balance")
try_auth("short path",        "/portfolio/balance")
try_auth("v2 prefix",         "v2/portfolio/balance")
try_auth("no leading slash",  "trade-api/v2/portfolio/balance")
