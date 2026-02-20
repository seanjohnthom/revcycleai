#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kalshi_client import KalshiClient

client = KalshiClient()
data = client.get_markets(limit=5, status='open')
markets = data.get('markets', [])

print(f"Got {len(markets)} markets\n")
for m in markets[:3]:
    print(json.dumps(m, indent=2))
    print("---")
