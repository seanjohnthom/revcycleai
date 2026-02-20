#!/usr/bin/env python3
"""Find real tradeable markets via events endpoint."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from kalshi_client import KalshiClient

client = KalshiClient()

# Get events — these are cleaner
data = client._get('/events', params={'limit': 50, 'status': 'open'}, auth=False)
events = data.get('events', [])
print(f"Events (open): {len(events)}")
for e in events[:10]:
    print(f"  {e.get('event_ticker')} | {e.get('title','')[:60]}")
    
print()

# Also try getting markets with a category filter or series filter
# Try series_ticker for known market series
series_tickers = ['FED', 'CPI', 'INXU', 'KXUSD']  # common Kalshi series prefixes
for s in series_tickers:
    data2 = client._get('/markets', params={'limit': 10, 'series_ticker': s}, auth=False)
    markets = data2.get('markets', [])
    if markets:
        print(f"Series '{s}': {len(markets)} markets")
        for m in markets[:3]:
            print(f"  {m.get('ticker')} | bid:{m.get('yes_bid')} ask:{m.get('yes_ask')} vol:{m.get('volume')}")

# Try paginating further to find non-MVE markets
print("\nSearching deeper in pagination for non-MVE markets...")
cursor = None
non_mve_count = 0
pages = 0
for _ in range(30):  # Check up to 30 pages
    data3 = client.get_markets(limit=200, cursor=cursor, status='open')
    batch = data3.get('markets', [])
    non_mve = [m for m in batch if 'KXMVE' not in m.get('ticker','')]
    non_mve_count += len(non_mve)
    cursor = data3.get('cursor')
    pages += 1
    
    if non_mve:
        print(f"  Page {pages}: Found {len(non_mve)} non-MVE markets!")
        for m in non_mve[:3]:
            print(f"    {m.get('ticker')} | bid:{m.get('yes_bid')} vol:{m.get('volume')}")
        if non_mve_count >= 20:
            break
    
    if not cursor or not batch:
        break
    time.sleep(0.3)

print(f"\nTotal non-MVE markets found: {non_mve_count} (in {pages} pages)")
