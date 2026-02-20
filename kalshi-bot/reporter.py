#!/usr/bin/env python3
"""Weekly and monthly report generator."""
from datetime import datetime, timezone
import trade_ledger as ledger


SEP = "━" * 45


def weekly_report(balance_cents: int, open_positions: list) -> str:
    balance = balance_cents / 100
    deployed = ledger.get_deployed_capital()
    cash = balance - deployed
    weekly_pnl = ledger.get_weekly_pnl()
    monthly_pnl = ledger.get_monthly_pnl()
    win_rate = ledger.get_win_rate(30)
    all_trades = ledger.get_all_trades()
    open_trades = ledger.get_open_trades()
    watchlist = ledger.get_watchlist()

    now = datetime.now(timezone.utc)
    week_str = now.strftime('%Y-%m-%d')

    # Trades executed this week
    from datetime import timedelta
    week_ago = now - timedelta(days=7)
    recent_closed = [
        t for t in all_trades
        if t.get('entry_time')
        and datetime.fromisoformat(t['entry_time']) >= week_ago
        and t['status'] != 'open'
    ]
    recent_open = [
        t for t in all_trades
        if t.get('entry_time')
        and datetime.fromisoformat(t['entry_time']) >= week_ago
        and t['status'] == 'open'
    ]

    lines = [
        SEP,
        f"KALSHI WEEKLY EXECUTION REPORT",
        f"Week of {week_str} | Monthly Budget: $25.00 | Balance: ${balance:.2f}",
        SEP,
        "",
        "PORTFOLIO SNAPSHOT:",
        f"  Account balance:          ${balance:.2f}",
        f"  Capital deployed:         ${deployed:.2f}",
        f"  Cash available:           ${cash:.2f}",
        f"  Open positions:           {len(open_trades)}",
        f"  Closed this week:         {len(recent_closed)} | P&L: {'+'if weekly_pnl>=0 else ''}${weekly_pnl:.2f}",
        f"  Running monthly P&L:      {'+'if monthly_pnl>=0 else ''}${monthly_pnl:.2f}",
        f"  Win rate (30d):           {win_rate:.1f}%" if win_rate else "  Win rate (30d):           N/A (no settled trades yet)",
        "",
        SEP,
        "TRADES EXECUTED THIS WEEK:",
    ]

    all_this_week = recent_open + recent_closed
    if not all_this_week:
        lines.append("  (none)")
    for t in all_this_week:
        status_str = t['status'].upper()
        if t['status'] == 'settled' and t.get('pnl') is not None:
            pnl_str = f" — {'WON' if t['pnl'] > 0 else 'LOST'} {'+'if t['pnl']>=0 else ''}${t['pnl']:.2f}"
        elif t['status'] == 'open':
            pnl_str = " — OPEN"
        else:
            pnl_str = ""

        lines.extend([
            "",
            f"  ▶ {t['ticker']}",
            f"    Side: {t['side'].upper()} | Entry: ${t['entry_price_cents']/100:.2f} | Contracts: {t['count']}",
            f"    Capital: ${t['capital_deployed']:.2f} | Edge at entry: {t['edge_at_entry']:.0%}",
            f"    Status: {status_str}{pnl_str}",
            f"    Thesis: {t['thesis'][:120]}",
        ])

    lines.extend(["", SEP, "POSITIONS MONITORED & HELD:"])

    if not open_positions:
        lines.append("  (none)")
    for pos in open_positions:
        ticker = pos.get('ticker', '?')
        contracts = pos.get('position', 0)
        current = pos.get('market_exposure', 0)
        lines.append(f"  {ticker} — {contracts} contracts | Market exposure: ${current/100:.2f}")

    lines.extend(["", SEP, "WATCHLIST (approaching threshold):"])
    wl = ledger.get_watchlist()
    if not wl:
        lines.append("  (none)")
    for w in wl:
        lines.append(f"  {w['ticker']}: edge {w['edge']:.0%} — {w['reason']}")

    lines.extend(["", SEP, ""])

    return "\n".join(lines)


def monthly_report() -> str:
    all_trades = ledger.get_all_trades()
    closed = [t for t in all_trades if t['status'] in ('closed', 'settled') and t.get('pnl') is not None]

    if not closed:
        return "No closed trades yet for monthly report."

    total_deployed = sum(t['capital_deployed'] for t in closed)
    total_returned = total_deployed + sum(t['pnl'] for t in closed)
    net_pnl = sum(t['pnl'] for t in closed)
    roi = (net_pnl / total_deployed * 100) if total_deployed > 0 else 0
    wins = [t for t in closed if t['pnl'] > 0]
    win_rate = len(wins) / len(closed) * 100

    # Category breakdown
    cat_pnl = {}
    for t in closed:
        cat = t.get('category', 'other')
        cat_pnl[cat] = cat_pnl.get(cat, 0) + t['pnl']

    # Top 3 winners and losers
    by_pnl = sorted(closed, key=lambda x: x['pnl'], reverse=True)
    top3 = by_pnl[:3]
    bot3 = by_pnl[-3:]

    lines = [
        SEP,
        "KALSHI MONTHLY PERFORMANCE REPORT",
        SEP,
        "",
        "P&L SUMMARY:",
        f"  Total deployed:  ${total_deployed:.2f}",
        f"  Total returned:  ${total_returned:.2f}",
        f"  Net profit/loss: {'+'if net_pnl>=0 else ''}${net_pnl:.2f}",
        f"  ROI:             {roi:.1f}%",
        f"  Win rate:        {win_rate:.1f}% ({len(wins)}/{len(closed)})",
        "",
        "P&L BY CATEGORY:",
    ]
    for cat, pnl in sorted(cat_pnl.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {cat.capitalize():15s}: {'+'if pnl>=0 else ''}${pnl:.2f}")

    lines.extend(["", "TOP WINNERS:"])
    for t in top3:
        if t['pnl'] > 0:
            lines.append(f"  +${t['pnl']:.2f}  {t['ticker']} — {t['thesis'][:80]}")

    lines.extend(["", "BIGGEST LOSERS:"])
    for t in bot3:
        if t['pnl'] < 0:
            lines.append(f"  -${abs(t['pnl']):.2f}  {t['ticker']} — {t['thesis'][:80]}")

    lines.extend(["", SEP, ""])
    return "\n".join(lines)
