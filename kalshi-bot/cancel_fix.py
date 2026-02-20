#!/usr/bin/env python3
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from kalshi_client import KalshiClient

client = KalshiClient()

# Cancel the bad orders
bad_orders = [
    '87e45e55-7182-4d3d-92ad-181de06cd37a',
    'ef9edef6-ddd2-4ea8-a17e-9edb442aec00',
]

for oid in bad_orders:
    try:
        result = client.cancel_order(oid)
        print(f"Cancelled {oid}: {result}")
    except Exception as e:
        print(f"Cancel {oid} error: {e}")

# Check open orders
print("\n--- Open orders ---")
try:
    orders = client.get_orders()
    print(f"Open orders: {len(orders)}")
    for o in orders:
        print(f"  {o.get('ticker')} | side:{o.get('side')} price:{o.get('yes_price') or o.get('no_price')} status:{o.get('status')}")
except Exception as e:
    print(f"Error: {e}")

# Debug actual orderbook format
print("\n--- Orderbook for KXCPI-26FEB-T0.1 ---")
try:
    ob = client.get_orderbook('KXCPI-26FEB-T0.1')
    print(json.dumps(ob, indent=2)[:2000])
except Exception as e:
    print(f"Error: {e}")
