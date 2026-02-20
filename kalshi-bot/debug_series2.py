#!/usr/bin/env python3
"""Find active markets via series."""
import requests, time

BASE = 'https://api.elections.kalshi.com/trade-api/v2'

# Try known active series to find markets with volume
active_series = [
    'KXFED', 'KXCPI', 'KXFEDDECISION', 'FEDDECISION',
    'KXFRM', 'KXBTCPRICE', 'KXINX', 'KXSPY', 
    'KXTRUMP', 'KXDOGE', 'KXGOV',
]

for s in active_series:
    r = requests.get(f'{BASE}/series/{s}/markets', params={'limit': 5})
    if r.ok:
        data = r.json()
        markets = data.get('markets', [])
        if markets:
            print(f"Series {s}: {len(markets)} markets")
            for m in markets[:2]:
                print(f"  {m.get('ticker')[:50]} | bid:{m.get('yes_bid')} vol:{m.get('volume')}")
        else:
            print(f"Series {s}: 0 markets (series exists)")
    else:
        print(f"Series {s}: {r.status_code}")
    time.sleep(0.2)

# Try directly finding markets by event
print("\n--- Search for events with 'rate' in title ---")
r = requests.get(f'{BASE}/events', params={'limit': 200, 'status': 'open'})
events = r.json().get('events', [])
print(f"Events returned: {len(events)}")
rate_events = [e for e in events if 'rate' in e.get('title','').lower() or 'fed' in e.get('title','').lower() or 'cpi' in e.get('title','').lower()]
print(f"Rate/Fed/CPI related: {len(rate_events)}")
for e in rate_events[:5]:
    print(f"  {e.get('event_ticker')} | {e.get('title','')[:60]}")

# Try the markets endpoint with an event_ticker filter
print("\n--- Markets filtered by event_ticker ---")
r = requests.get(f'{BASE}/markets', params={'limit': 20, 'event_ticker': 'KXFED-26MAR'})
print(f"KXFED-26MAR markets: {r.status_code} | {len(r.json().get('markets',[]))} markets")
r = requests.get(f'{BASE}/markets', params={'limit': 20, 'series_ticker': 'KXFED'})
print(f"KXFED series markets: {r.status_code} | {len(r.json().get('markets',[]))} markets")

# Check what the current active events look like (no filter)
print("\n--- All events (no filter) first 20 ---")
r = requests.get(f'{BASE}/events', params={'limit': 20})
events = r.json().get('events', [])
for e in events[:10]:
    print(f"  {e.get('event_ticker')} | {e.get('title','')[:60]} | markets: {len(e.get('markets',[]))}")

# Try markets without ANY filter and check their actual event_tickers
print("\n--- Markets breakdown by event_ticker prefix ---")
r = requests.get(f'{BASE}/markets', params={'limit': 200})
markets = r.json().get('markets', [])
prefixes = {}
for m in markets:
    t = m.get('event_ticker','?').split('-')[0][:15]
    prefixes[t] = prefixes.get(t, 0) + 1
print("Event ticker prefixes:", dict(sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:10]))
