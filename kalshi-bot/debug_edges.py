#!/usr/bin/env python3
"""Debug why edge finder returns 0 results."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from kalshi_client import KalshiClient

client = KalshiClient()

# Get a sample of markets
data = client.get_markets(limit=200, status='open')
markets = data.get('markets', [])

print(f"Total markets in first page: {len(markets)}")
print()

# Filter stats
stats = {
    'total': len(markets),
    'has_yes_bid': 0,
    'has_volume': 0,
    'not_mve': 0,
    'right_days': 0,
    'active_status': 0,
}

samples_with_bid = []

for m in markets:
    ticker = m.get('ticker', '')
    yes_bid = m.get('yes_bid', 0) or 0
    yes_ask = m.get('yes_ask', 0) or 0
    volume = m.get('volume', 0) or 0
    volume_24h = m.get('volume_24h', 0) or 0
    liquidity = m.get('liquidity', 0) or 0
    status = m.get('status', '')

    is_mve = 'KXMVE' in ticker or 'MVE' in ticker
    if not is_mve:
        stats['not_mve'] += 1

    if status in ('open', 'active'):
        stats['active_status'] += 1

    if yes_bid > 0:
        stats['has_yes_bid'] += 1
        if not is_mve:
            samples_with_bid.append(m)

    eff_vol = max(volume, volume_24h, liquidity)
    if eff_vol >= 200:
        stats['has_volume'] += 1

print("FILTER STATS:")
for k, v in stats.items():
    print(f"  {k}: {v}")

print(f"\nMarkets with yes_bid > 0 and not MVE: {len(samples_with_bid)}")

if samples_with_bid:
    print("\nSAMPLE markets with active bids:")
    for m in samples_with_bid[:5]:
        print(f"\n  ticker: {m.get('ticker')}")
        print(f"  title: {m.get('title', '')[:60]}")
        print(f"  status: {m.get('status')}")
        print(f"  yes_bid: {m.get('yes_bid')} | yes_ask: {m.get('yes_ask')}")
        print(f"  volume: {m.get('volume')} | volume_24h: {m.get('volume_24h')} | liquidity: {m.get('liquidity')}")
        print(f"  close_time: {m.get('close_time')}")
        print(f"  last_price: {m.get('last_price')}")
else:
    print("\nNO markets with active bids! Checking raw data...")
    print("\nSample statuses:", set(m.get('status') for m in markets[:20]))
    print("Sample tickers:", [m.get('ticker', '')[:30] for m in markets[:5]])
    # Print one full market with non-zero bid
    for m in markets:
        if (m.get('yes_bid') or 0) > 0:
            print("\nFirst market with yes_bid > 0:")
            print(json.dumps({k: v for k, v in m.items() 
                             if k in ['ticker','title','yes_bid','yes_ask','volume','volume_24h',
                                     'liquidity','status','close_time','last_price']}, indent=2))
            break
