#!/usr/bin/env python3
"""Quick targeted trade placer — bypasses full market scan."""
import sys
sys.path.insert(0, '.')
from kalshi_client import KalshiClient
from position_manager import calculate_position_size, contract_count, can_open_position

TARGETS = [
    # (ticker,          side,  limit_cents, true_prob, edge, description)
    ('KXGDP-26JAN30-T1.5',  'yes', 90, 0.96, 0.06, 'GDP Q4 >1.5% — settles tomorrow'),
    ('KXGDP-26JAN30-T1.75', 'yes', 85, 0.91, 0.06, 'GDP Q4 >1.75% — settles tomorrow'),
    ('KXCPI-26FEB-T0.1',    'yes', 89, 0.94, 0.06, 'CPI Feb >0.1% — 20 days'),
]

def main():
    client = KalshiClient()
    bal = client.get_balance()
    balance_cents = bal.get('balance', 0)
    portfolio = bal.get('portfolio_value', 0)
    print(f"\n💰 Balance: ${balance_cents/100:.2f} | Portfolio: ${portfolio/100:.2f}")

    open_positions = client.get_positions()
    open_tickers = {p.get('ticker', '') for p in open_positions if p.get('position', 0) != 0}
    print(f"📊 Open positions: {len(open_tickers)} — {', '.join(open_tickers) or 'none'}\n")

    placed = 0
    for ticker, side, limit_cents, true_prob, edge, desc in TARGETS:
        print(f"🎯 {ticker} — {desc}")

        # Skip if already have a position
        if ticker in open_tickers:
            print(f"   ⏭️  Already have a position — skipping\n")
            continue

        # Size it
        bal_now = client.get_balance()
        balance_cents = bal_now.get('balance', 0)
        position_size = calculate_position_size(edge, limit_cents, balance_cents, true_prob=true_prob)
        if position_size <= 0:
            print(f"   ⚠️  Position size too small (${position_size:.2f}) — skipping\n")
            continue

        contracts = contract_count(position_size, limit_cents)
        open_count = len(open_tickers)
        from position_manager import MAX_POSITIONS
        ok   = open_count < MAX_POSITIONS and balance_cents/100 >= 5.50
        reason = f"{open_count} positions open" if not ok else ""
        if not ok:
            print(f"   ⚠️  Cannot open: {reason}\n")
            continue

        print(f"   Size: ${position_size:.2f} | {contracts} contracts @ ${limit_cents/100:.2f}")

        # Place order
        try:
            result = client.place_order(
                ticker=ticker,
                action='buy',
                side=side,
                order_type='limit',
                count=contracts,
                price=limit_cents,
            )
            order_id = result.get('order', {}).get('order_id', 'unknown')
            status   = result.get('order', {}).get('status', 'unknown')
            print(f"   ✅ Order placed — ID: {order_id} | Status: {status}")
            open_tickers.add(ticker)
            placed += 1
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        print()

    bal_final = client.get_balance()
    print(f"\n📊 Done — {placed} orders placed")
    print(f"💰 Remaining balance: ${bal_final.get('balance',0)/100:.2f}")

if __name__ == '__main__':
    main()
