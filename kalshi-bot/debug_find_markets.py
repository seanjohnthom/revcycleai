#!/usr/bin/env python3
"""Find the real active markets with volume."""
import requests, json

BASE = 'https://api.elections.kalshi.com/trade-api/v2'

# Try market_type filters
for mt in ['binary', 'scalar']:
    r = requests.get(f'{BASE}/markets', params={'limit': 5, 'market_type': mt})
    m = r.json().get('markets', [])
    non_mve = [x for x in m if 'KXMVE' not in x.get('ticker','')]
    print(f"market_type={mt}: {len(m)} total, {len(non_mve)} non-MVE")
    for x in non_mve[:2]:
        print(f"  {x.get('ticker')} | bid:{x.get('yes_bid')} vol:{x.get('volume')}")

# Sort by volume  
print("\n--- Sort by volume ---")
r = requests.get(f'{BASE}/markets', params={'limit': 20, 'min_volume': 1000})
print(f"Status: {r.status_code}")
m = r.json().get('markets', [])
print(f"Markets with min_volume param: {len(m)}")
for x in m[:5]:
    print(f"  {x.get('ticker')[:50]} | bid:{x.get('yes_bid')} vol:{x.get('volume')}")

# Try known specific event tickers
print("\n--- Known event tickers ---")
known_events = [
    'KXFED-25MAR', 'KXFED-26MAR', 'KXFOMC-26MAR',
    'KXCPI-26FEB', 'KXCPI-26MAR', 'KXCPI-25MAR',
    'KXNFP-26FEB', 'KXNFP-26MAR',
    'KXBTC-26FEB', 'KXBTC-26MAR',
    'KXINX-26FEB', 'KXSPY-26FEB',
]
for et in known_events:
    r = requests.get(f'{BASE}/events/{et}')
    if r.status_code == 200:
        data = r.json()
        e = data.get('event', data)
        markets = e.get('markets', [])
        print(f"  ✓ {et}: {len(markets)} markets")
        for m in markets[:2]:
            print(f"    {m.get('ticker')[:50]} | bid:{m.get('yes_bid')} vol:{m.get('volume')}")
    else:
        print(f"  ✗ {et}: {r.status_code}")

# Try the portfolio to see what kinds of markets exist
print("\n--- Check series endpoint with more ---")
r = requests.get(f'{BASE}/series', params={'limit': 100})
series_list = r.json().get('series', [])
print(f"Total series: {len(series_list)}")
# Look for economic/financial series
for s in series_list:
    t = s.get('ticker','').upper()
    title = s.get('title','').upper()
    if any(k in t or k in title for k in ['FED','CPI','RATE','ECON','INFLATION','NFP','GDP']):
        print(f"  ECON: {s.get('ticker')} | {s.get('title','')[:60]}")
