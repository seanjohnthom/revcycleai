#!/usr/bin/env python3
"""
Kalshi Edge Finder — ClawdBot
Full autonomous trading bot. Scan → Analyze → Execute → Monitor → Report.

Usage:
  python3 kalshi_bot.py              # Full autonomous loop (daemon)
  python3 kalshi_bot.py --scan-only  # Scan & analyze, no trading
  python3 kalshi_bot.py --report     # Print weekly report
  python3 kalshi_bot.py --monitor    # Check open positions
  python3 kalshi_bot.py --balance    # Check account balance
  python3 kalshi_bot.py --starter    # Run starter batch (first 5 trades)
"""
import sys, os, time, json, argparse
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from kalshi_client import KalshiClient
from edge_finder import rank_opportunities, analyze_market
from position_manager import (
    calculate_position_size, contract_count,
    can_open_position, get_limit_price, should_exit
)
import trade_ledger as ledger
import reporter


def print_banner():
    print("=" * 50)
    print("  KALSHI EDGE FINDER — ClawdBot")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)


# ── STEP 1: SCAN ──────────────────────────────────────────────────────────────

def scan_markets(client: KalshiClient, verbose: bool = True) -> list:
    """Fetch all active markets from Kalshi."""
    if verbose:
        print("\n[SCAN] Fetching active markets...")
    markets = client.get_all_markets(status='open')
    if verbose:
        print(f"[SCAN] Found {len(markets)} open markets")
    return markets


# ── STEP 2: ANALYZE ───────────────────────────────────────────────────────────

def analyze_markets(markets: list, verbose: bool = True) -> list:
    """Run edge analysis on all markets, return ranked opportunities."""
    if verbose:
        print(f"\n[ANALYZE] Running edge analysis on {len(markets)} markets...")
    opportunities = rank_opportunities(markets)
    if verbose:
        print(f"[ANALYZE] Found {len(opportunities)} markets with edge ≥ 5%")
    return opportunities


def print_opportunities(opps: list, limit: int = 15):
    print(f"\n{'─'*50}")
    print(f"TOP OPPORTUNITIES ({min(limit, len(opps))} of {len(opps)})")
    print(f"{'─'*50}")
    for i, opp in enumerate(opps[:limit], 1):
        print(f"\n#{i} [{opp['category'].upper()}] {opp['ticker']}")
        print(f"    {opp['title'][:70]}")
        print(f"    Implied: {opp['implied_prob']:.0%} → Est: {opp['true_prob']:.0%} | Edge: {opp['edge']:.1%}")
        print(f"    Trade: BUY {opp['trade_side'].upper()} @ ${opp['limit_price_cents']/100:.2f}")
        pos_size = opp.get('position_size') or 0
        contracts = opp.get('contracts') or 0
        days_left = opp.get('days_to_resolution') or 0
        print(f"    Size: ${pos_size:.2f} ({contracts} contracts) | {days_left:.1f} days left")
        print(f"    Volume: ${opp['volume']:,.0f} | Closes: {opp['close_time'][:10]}")


# ── STEP 3+4: SIZE + EXECUTE ─────────────────────────────────────────────────

def execute_trade(client: KalshiClient, opp: dict, balance_cents: int,
                  open_positions: list, dry_run: bool = False) -> bool:
    """Attempt to place a trade for an opportunity. Returns True if placed."""
    ticker = opp['ticker']
    side = opp['trade_side']
    limit_price = opp['limit_price_cents']
    edge = opp['edge']

    # Refresh orderbook for best limit price
    try:
        ob = client.get_orderbook(ticker)
        better_price = get_limit_price(ob, side)
        if better_price and 1 <= better_price <= 99:
            limit_price = better_price
    except Exception:
        pass

    # Calculate size — Kelly Criterion with true_prob from edge analysis
    true_prob = opp.get('true_prob')
    position_size = calculate_position_size(edge, limit_price, balance_cents, true_prob=true_prob)
    if position_size <= 0:
        print(f"  [SKIP] {ticker}: position size too small (Kelly)")
        return False

    contracts = contract_count(position_size, limit_price)
    if contracts < 1:
        print(f"  [SKIP] {ticker}: 0 contracts at Kelly-sized position")
        return False

    # Risk checks
    ok, reason = can_open_position(open_positions, balance_cents, position_size)
    if not ok:
        print(f"  [SKIP] {ticker}: {reason}")
        return False

    print(f"\n  [EXECUTE] {ticker}")
    print(f"    Side: {side.upper()} | Price: ${limit_price/100:.2f} | Contracts: {contracts}")
    print(f"    Kelly size: ${position_size:.2f} | Edge: {edge:.0%} | p_true: {true_prob:.0%}")
    print(f"    Thesis: {opp['thesis'][:100]}")

    if dry_run:
        print("    [DRY RUN — not placing order]")
        return False

    try:
        result = client.place_order(
            ticker=ticker,
            action='buy',
            side=side,
            order_type='limit',
            count=contracts,
            price=limit_price
        )
        order = result.get('order', result)
        order_id = order.get('order_id', order.get('id', f'unknown-{int(time.time())}'))

        print(f"    [ORDER PLACED] ID: {order_id}")

        ledger.log_entry(
            ticker=ticker,
            order_id=order_id,
            side=side,
            price_cents=limit_price,
            count=contracts,
            thesis=opp['thesis'],
            edge=edge,
            data_sources=['kalshi_market_data', 'favorite_longshot_bias'],
        )
        return True

    except Exception as e:
        print(f"    [ERROR] Failed to place order: {e}")
        return False


# ── STEP 5: MONITOR ───────────────────────────────────────────────────────────

def monitor_positions(client: KalshiClient, verbose: bool = True):
    """Check all open positions. Uses LIVE Kalshi API as source of truth for position size."""
    # ── Source of truth: live API positions ──────────────────────────────────
    live_positions = client.get_positions()
    # Only consider LONG positions (positive count) — never act on shorts/negatives
    live_by_ticker = {
        p['ticker']: p for p in live_positions
        if p.get('position', 0) > 0  # Only long YES positions
    }

    if not live_by_ticker:
        if verbose:
            print("[MONITOR] No open long positions to monitor")
        return

    if verbose:
        print(f"\n[MONITOR] Checking {len(live_by_ticker)} live long positions...")

    # Cross-reference with ledger for entry price / thesis (but use API for count)
    open_trades = ledger.get_open_trades()
    trade_by_ticker = {t['ticker']: t for t in open_trades}

    for ticker, pos in live_by_ticker.items():
        live_count = pos['position']           # ALWAYS use live count, never ledger
        trade = trade_by_ticker.get(ticker)
        entry_price = trade['entry_price_cents'] if trade else pos.get('market_exposure', 0) // max(live_count, 1)

        # Validate: if ledger count wildly diverges from live, log and use live
        if trade and abs(trade.get('count', 0) - live_count) > 2:
            print(f"  [WARN] {ticker}: ledger count {trade.get('count')} vs live {live_count} — using live")

        # Get current market price
        try:
            market = client.get_market(ticker)
            current_price = market.get('yes_bid', 0) or market.get('last_price', 0)
        except Exception:
            current_price = entry_price

        exit_flag, exit_reason = should_exit(
            {**trade, 'entry_price_cents': entry_price, 'count': live_count} if trade else
            {'entry_price_cents': entry_price, 'count': live_count, 'side': 'yes'},
            current_price
        )
        unrealized = round((current_price - entry_price) * live_count / 100, 2)

        if verbose:
            sign = '+' if unrealized >= 0 else ''
            print(f"  {ticker}: entry ${entry_price/100:.2f} → current ${current_price/100:.2f} | {live_count} contracts | unrealized: {sign}${unrealized:.2f}")

        if exit_flag:
            print(f"  [EXIT TRIGGER] {ticker}: {exit_reason}")
            try:
                # Sell EXACTLY what the live API says we own
                client.place_order(ticker, 'sell', 'yes', 'market', live_count, current_price)
                if trade:
                    ledger.log_exit(trade['id'], exit_price_cents=current_price)
                print(f"  [SOLD] {ticker}")
            except Exception as e:
                print(f"  [ERROR] Failed to exit {ticker}: {e}")


def monitor_unfilled_orders(client: KalshiClient):
    """Cancel limit orders that haven't filled in 4 hours."""
    try:
        orders = client.get_orders(status='resting')
    except Exception:
        return

    now = datetime.now(timezone.utc)
    for order in orders:
        created = order.get('created_time', '')
        if not created:
            continue
        try:
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            age_hours = (now - created_dt).total_seconds() / 3600
            if age_hours >= 4:
                order_id = order.get('order_id', order.get('id'))
                print(f"  [CANCEL] Order {order_id} unfilled after {age_hours:.1f}h")
                client.cancel_order(order_id)
        except Exception as e:
            print(f"  [ERROR] Checking order age: {e}")


# ── STEP 6: SETTLE ────────────────────────────────────────────────────────────

def check_settlements(client: KalshiClient):
    """Update ledger for any settled positions."""
    try:
        settlements = client.get_settlements()
    except Exception:
        return

    open_trades = ledger.get_open_trades()
    open_by_ticker = {t['ticker']: t for t in open_trades}

    for s in settlements:
        ticker = s.get('ticker', '')
        if ticker in open_by_ticker:
            trade = open_by_ticker[ticker]
            revenue = s.get('revenue', 0)  # in cents
            pnl = round(revenue / 100 - trade['capital_deployed'], 2)
            ledger.log_exit(trade['id'], exit_price_cents=revenue // trade['count'],
                           settled=True, pnl=pnl)
            print(f"  [SETTLED] {ticker}: P&L ${'+' if pnl >= 0 else ''}{pnl:.2f}")


# ── MAIN FLOWS ────────────────────────────────────────────────────────────────

def run_starter_batch(client: KalshiClient):
    """First run: scan, analyze top 30, trade top 5, watchlist next 3."""
    print_banner()
    print("\n╔══════════════════════════════════╗")
    print("║  STARTER BATCH — FIRST RUN       ║")
    print("╚══════════════════════════════════╝")

    # 1. Verify account
    bal = client.get_balance()
    balance_cents = bal.get('balance', 0)
    print(f"\n[ACCOUNT] Balance: ${balance_cents/100:.2f}")
    if balance_cents < 500:  # < $5
        print("[ABORT] Balance too low (< $5). Please deposit funds.")
        return

    # 2. Scan
    markets = scan_markets(client)

    # 3. Analyze top 30
    opps = analyze_markets(markets)
    top30 = opps[:30]

    print_opportunities(top30, limit=30)

    # 4. Execute top 5
    open_positions = client.get_positions()
    print("\n[EXECUTE] Placing orders for top 5 opportunities...")
    executed = 0
    for opp in opps[:10]:  # Try top 10, stop after 5 fill
        if executed >= 5:
            break
        # Refresh balance
        bal = client.get_balance()
        balance_cents = bal.get('balance', 0)
        if execute_trade(client, opp, balance_cents, open_positions, dry_run=False):
            executed += 1
            time.sleep(1)  # Rate limiting

    print(f"\n[EXECUTE] Placed {executed} orders")

    # 5. Watchlist next 3
    print("\n[WATCHLIST] Adding next 3 near-threshold markets...")
    watchlist_candidates = opps[5:15]  # Markets just below top 5
    added = 0
    for opp in watchlist_candidates:
        if added >= 3 or opp['edge'] < 0.03:
            break
        ledger.log_watchlist(opp['ticker'], opp['title'], opp['edge'],
                            f"Edge {opp['edge']:.0%} — monitoring for entry")
        print(f"  + Watchlist: {opp['ticker']} (edge {opp['edge']:.0%})")
        added += 1

    # 6. Log 2 passed markets
    print("\n[PASSED] Markets scanned but no edge found:")
    passed = [m for m in markets if not any(o['ticker'] == m.get('ticker') for o in opps)]
    for m in passed[:2]:
        ticker = m.get('ticker', '?')
        price = m.get('yes_bid', m.get('last_price', 0))
        print(f"  ✗ {ticker}: ${price/100:.2f} — Insufficient edge or volume")

    print("\n[DONE] Starter batch complete. Bot will now enter monitoring loop.")


def run_scan_only(client: KalshiClient):
    """Scan and print opportunities without trading."""
    print_banner()
    print("\n[MODE] Scan only — no trades will be placed\n")

    bal = client.get_balance()
    balance_cents = bal.get('balance', 0)
    print(f"[ACCOUNT] Balance: ${balance_cents/100:.2f} | Portfolio: ${bal.get('portfolio_value', 0)/100:.2f}")

    # Get tickers already held so we don't recommend adding more
    open_positions = client.get_positions()
    held_tickers = {p['ticker'] for p in open_positions if p.get('position', 0) != 0}
    open_trades = ledger.get_open_trades()
    held_tickers |= {t['ticker'] for t in open_trades}
    if held_tickers:
        print(f"[DEDUP] Skipping {len(held_tickers)} already-held tickers: {', '.join(sorted(held_tickers))}")

    markets = scan_markets(client)
    opps = analyze_markets(markets)
    # Filter out already-held positions
    opps = [o for o in opps if o['ticker'] not in held_tickers]
    print_opportunities(opps, limit=20)

    print(f"\n[SUMMARY] {len(opps)} new opportunities found across {len(markets)} markets")
    if opps:
        cats = {}
        for o in opps:
            cats[o['category']] = cats.get(o['category'], 0) + 1
        print("[CATEGORIES]", " | ".join(f"{k}: {v}" for k, v in sorted(cats.items(), key=lambda x: x[1], reverse=True)))


def run_monitor(client: KalshiClient):
    """Check positions and unfilled orders."""
    print_banner()
    check_settlements(client)
    monitor_positions(client)
    monitor_unfilled_orders(client)


def run_daemon(client: KalshiClient):
    """Full autonomous loop."""
    print_banner()
    print("\n[DAEMON] Starting autonomous loop...")

    # Check if first run (no trades in ledger)
    if not ledger.get_all_trades():
        run_starter_batch(client)

    # Schedule
    import schedule
    schedule.every().day.at("08:00").do(lambda: _daily_scan(client))
    schedule.every(6).hours.do(lambda: monitor_positions(client))
    schedule.every(2).hours.do(lambda: monitor_unfilled_orders(client))
    schedule.every().monday.at("06:00").do(lambda: _weekly_report(client))

    print("[DAEMON] Scheduler running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)


def _daily_scan(client: KalshiClient):
    print(f"\n[DAILY SCAN] {datetime.now(timezone.utc).isoformat()}")
    check_settlements(client)
    markets = scan_markets(client, verbose=False)
    opps = analyze_markets(markets, verbose=False)
    open_positions = client.get_positions()
    # Dedup: skip tickers already in open positions or open trades
    held_tickers = {p['ticker'] for p in open_positions if p.get('position', 0) != 0}
    held_tickers |= {t['ticker'] for t in ledger.get_open_trades()}
    opps = [o for o in opps if o['ticker'] not in held_tickers]
    bal = client.get_balance()
    balance_cents = bal.get('balance', 0)
    print(f"[BALANCE] ${balance_cents/100:.2f} | {len(opps)} new opportunities found (after dedup)")

    executed = 0
    for opp in opps[:10]:
        if executed >= 3:
            break  # Max 3 new trades per daily scan
        bal = client.get_balance()
        if execute_trade(client, opp, bal.get('balance', 0), open_positions):
            executed += 1
            time.sleep(1)

    if executed:
        print(f"[DAILY] Placed {executed} new orders")
    else:
        print("[DAILY] No new trades — no sufficient edges or limits reached")


def _weekly_report(client: KalshiClient):
    bal = client.get_balance()
    positions = client.get_positions()
    print(reporter.weekly_report(bal.get('balance', 0), positions))


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Kalshi Edge Finder — ClawdBot')
    parser.add_argument('--scan-only', action='store_true', help='Scan markets, no trading')
    parser.add_argument('--report', action='store_true', help='Print weekly report')
    parser.add_argument('--monitor', action='store_true', help='Check open positions')
    parser.add_argument('--balance', action='store_true', help='Check account balance')
    parser.add_argument('--starter', action='store_true', help='Run starter batch')
    args = parser.parse_args()

    client = KalshiClient()

    if args.balance:
        bal = client.get_balance()
        print(f"Balance:         ${bal.get('balance', 0)/100:.2f}")
        print(f"Portfolio value: ${bal.get('portfolio_value', 0)/100:.2f}")

    elif args.scan_only:
        run_scan_only(client)

    elif args.report:
        bal = client.get_balance()
        positions = client.get_positions()
        print(reporter.weekly_report(bal.get('balance', 0), positions))

    elif args.monitor:
        run_monitor(client)

    elif args.starter:
        run_starter_batch(client)

    else:
        run_daemon(client)
