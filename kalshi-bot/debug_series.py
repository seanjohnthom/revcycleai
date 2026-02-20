#!/usr/bin/env python3
import sys, os, json, time, requests
sys.path.insert(0, os.path.dirname(__file__))
from kalshi_client import KalshiClient

client = KalshiClient()
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

# Try markets without status filter
print("=== Markets (no status filter) ===")
r = requests.get(f'{BASE_URL}/markets', params={'limit': 5})
m = r.json().get('markets', [])
for x in m[:3]:
    print(f"  {x.get('ticker')[:40]} | status:{x.get('status')} | bid:{x.get('yes_bid')}")

# Try markets with status=active
print("\n=== Markets (status=active) ===")
r = requests.get(f'{BASE_URL}/markets', params={'limit': 5, 'status': 'active'})
m = r.json().get('markets', [])
for x in m[:3]:
    print(f"  {x.get('ticker')[:40]} | status:{x.get('status')} | bid:{x.get('yes_bid')}")

# Try series endpoint
print("\n=== Series list ===")
r = requests.get(f'{BASE_URL}/series', params={'limit': 20})
print(f"Status: {r.status_code}")
if r.ok:
    series = r.json().get('series', [])
    for s in series[:10]:
        print(f"  {s.get('ticker')} | {s.get('title','')[:50]}")

# Try events with status=open or no filter
print("\n=== Events (no status filter, limit=10) ===")
r = requests.get(f'{BASE_URL}/events', params={'limit': 10})
events = r.json().get('events', [])
for e in events[:5]:
    print(f"  {e.get('event_ticker')} | {e.get('title','')[:60]}")
    # Get markets for this event
    r2 = requests.get(f'{BASE_URL}/events/{e.get("event_ticker")}')
    if r2.ok:
        data = r2.json()
        event_data = data.get('event', data)
        markets = event_data.get('markets', [])
        print(f"    -> {len(markets)} markets")
        for m2 in markets[:2]:
            print(f"    {m2.get('ticker')[:50]} | bid:{m2.get('yes_bid')} ask:{m2.get('yes_ask')} vol:{m2.get('volume')}")
    time.sleep(0.2)

# Try to find markets by searching for known tickers
print("\n=== Direct market lookup (known Fed/CPI tickers) ===")
test_tickers = ['KXFED-25DEC', 'FED-25DEC', 'KXFED', 'KXCPI']
for t in test_tickers:
    r = requests.get(f'{BASE_URL}/markets/{t}')
    print(f"  {t}: {r.status_code}")
    if r.ok:
        m = r.json().get('market', r.json())
        print(f"    Found: {m.get('ticker')} | {m.get('title','')[:40]}")
