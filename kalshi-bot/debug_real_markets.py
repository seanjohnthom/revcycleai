#!/usr/bin/env python3
"""Explore the real tradeable markets."""
import requests, json, time

BASE = 'https://api.elections.kalshi.com/trade-api/v2'

# Get KXFED markets
print("=== KXFED-26MAR markets ===")
r = requests.get(f'{BASE}/markets', params={'limit': 20, 'event_ticker': 'KXFED-26MAR'})
markets = r.json().get('markets', [])
for m in markets:
    print(f"\n  ticker: {m.get('ticker')}")
    print(f"  title: {m.get('title','')[:70]}")
    print(f"  status: {m.get('status')} | yes_bid: {m.get('yes_bid')} | yes_ask: {m.get('yes_ask')}")
    print(f"  volume: {m.get('volume')} | volume_24h: {m.get('volume_24h')} | liquidity: {m.get('liquidity')}")
    print(f"  close_time: {m.get('close_time','')[:20]} | last_price: {m.get('last_price')}")

# Also check the series_ticker approach
print("\n\n=== Series-based market discovery ===")
# These are series we know exist
series_to_try = [
    ('KXFED', 'Federal Reserve'),
    ('KXCPI', 'CPI/Inflation'),
    ('KXECONSTAT', 'Economic Stats'),
    ('KXBTC', 'Bitcoin'),
    ('KXINX', 'S&P 500'),
    ('KXFRM', 'Mortgage Rate'),
    ('KXGOV', 'Government'),
    ('KXTARIFF', 'Tariffs'),
    ('KXTRUMP', 'Trump'),
    ('KXGDP', 'GDP'),
]

all_found = []
for ticker, name in series_to_try:
    r = requests.get(f'{BASE}/markets', params={'limit': 50, 'series_ticker': ticker})
    if r.ok:
        m = r.json().get('markets', [])
        tradeable = [x for x in m if (x.get('yes_bid') or 0) > 0 and (x.get('yes_ask') or 0) > 0]
        print(f"  {name} ({ticker}): {len(m)} total, {len(tradeable)} with bids")
        for t in tradeable[:3]:
            print(f"    {t.get('ticker')[:50]} | bid:{t.get('yes_bid')} ask:{t.get('yes_ask')} vol:{t.get('volume')}")
            all_found.append(t)
    time.sleep(0.3)

print(f"\nTotal tradeable markets found: {len(all_found)}")
