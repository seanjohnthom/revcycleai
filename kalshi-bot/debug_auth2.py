#!/usr/bin/env python3
"""Try more auth variations - timestamp format + padding type"""
import os, time, base64, requests
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_KEY_ID = os.getenv('KALSHI_API_KEY_ID')
PRIVATE_KEY_PEM = os.getenv('KALSHI_PRIVATE_KEY')
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

private_key = serialization.load_pem_private_key(PRIVATE_KEY_PEM.encode(), password=None)

def sign_pkcs1(msg: str) -> str:
    sig = private_key.sign(msg.encode(), asym_padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(sig).decode()

def sign_pss(msg: str) -> str:
    sig = private_key.sign(msg.encode(), asym_padding.PSS(
        mgf=asym_padding.MGF1(hashes.SHA256()),
        salt_length=asym_padding.PSS.MAX_LENGTH
    ), hashes.SHA256())
    return base64.b64encode(sig).decode()

def try_auth(label, ts, path, method, sign_fn):
    msg = ts + method + path
    headers = {
        'KALSHI-ACCESS-KEY': API_KEY_ID,
        'KALSHI-ACCESS-TIMESTAMP': ts,
        'KALSHI-ACCESS-SIGNATURE': sign_fn(msg),
        'Content-Type': 'application/json',
    }
    resp = requests.get(f'{BASE_URL}/portfolio/balance', headers=headers)
    status = "✓ OK" if resp.ok else "✗"
    print(f"[{label}] {resp.status_code} {status}")
    if resp.ok:
        print(f"  {resp.text[:300]}")
    return resp.ok

path = '/trade-api/v2/portfolio/balance'
now_ms = str(int(time.time() * 1000))
now_s  = str(int(time.time()))

combos = [
    ("ms + PKCS1 + GET",   now_ms, path, "GET",    sign_pkcs1),
    ("ms + PSS  + GET",    now_ms, path, "GET",    sign_pss),
    ("s  + PKCS1 + GET",   now_s,  path, "GET",    sign_pkcs1),
    ("s  + PSS  + GET",    now_s,  path, "GET",    sign_pss),
    ("ms + PKCS1 + get",   now_ms, path, "get",    sign_pkcs1),
]

for args in combos:
    if try_auth(*args):
        print("FOUND WORKING COMBO!")
        break
