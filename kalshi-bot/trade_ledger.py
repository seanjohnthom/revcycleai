#!/usr/bin/env python3
"""Trade ledger — logs every entry, exit, settlement."""
import json, os
from datetime import datetime, timezone, timedelta
from typing import Optional

LEDGER_PATH = os.path.join(os.path.dirname(__file__), 'trades.json')


def _load() -> dict:
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH) as f:
            return json.load(f)
    return {'trades': [], 'watchlist': []}


def _save(data: dict):
    with open(LEDGER_PATH, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def log_entry(ticker: str, order_id: str, side: str, price_cents: int,
              count: int, thesis: str, edge: float, data_sources: list = None):
    data = _load()
    trade = {
        'id': order_id,
        'ticker': ticker,
        'side': side,
        'entry_price_cents': price_cents,
        'count': count,
        'capital_deployed': round(price_cents * count / 100, 2),
        'thesis': thesis,
        'edge_at_entry': edge,
        'data_sources': data_sources or [],
        'status': 'open',
        'entry_time': datetime.now(timezone.utc).isoformat(),
        'exit_price_cents': None,
        'pnl': None,
        'exit_time': None,
        'settlement': None,
    }
    data['trades'].append(trade)
    _save(data)
    return trade


def log_exit(order_id: str, exit_price_cents: int = None,
             settled: bool = False, pnl: float = None):
    data = _load()
    for trade in data['trades']:
        if trade['id'] == order_id:
            trade['status'] = 'settled' if settled else 'closed'
            trade['exit_price_cents'] = exit_price_cents
            trade['exit_time'] = datetime.now(timezone.utc).isoformat()
            if pnl is not None:
                trade['pnl'] = pnl
            elif exit_price_cents is not None:
                # Calculate P&L: (exit - entry) * count / 100
                trade['pnl'] = round(
                    (exit_price_cents - trade['entry_price_cents']) * trade['count'] / 100, 2
                )
            break
    _save(data)


def log_watchlist(ticker: str, title: str, edge: float, reason: str):
    data = _load()
    # Remove existing entry for same ticker
    data['watchlist'] = [w for w in data['watchlist'] if w['ticker'] != ticker]
    data['watchlist'].append({
        'ticker': ticker,
        'title': title,
        'edge': edge,
        'reason': reason,
        'added': datetime.now(timezone.utc).isoformat(),
    })
    _save(data)


def get_open_trades() -> list:
    data = _load()
    return [t for t in data['trades'] if t['status'] == 'open']


def get_all_trades() -> list:
    return _load()['trades']


def get_watchlist() -> list:
    return _load().get('watchlist', [])


def get_weekly_pnl() -> float:
    data = _load()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    closed = [
        t for t in data['trades']
        if t['status'] in ('closed', 'settled')
        and t.get('exit_time')
        and datetime.fromisoformat(t['exit_time']) >= week_ago
        and t.get('pnl') is not None
    ]
    return round(sum(t['pnl'] for t in closed), 2)


def get_monthly_pnl() -> float:
    data = _load()
    month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    closed = [
        t for t in data['trades']
        if t['status'] in ('closed', 'settled')
        and t.get('exit_time')
        and datetime.fromisoformat(t['exit_time']) >= month_ago
        and t.get('pnl') is not None
    ]
    return round(sum(t['pnl'] for t in closed), 2)


def get_win_rate(days: int = 30) -> Optional[float]:
    data = _load()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    closed = [
        t for t in data['trades']
        if t['status'] in ('closed', 'settled')
        and t.get('exit_time')
        and datetime.fromisoformat(t['exit_time']) >= cutoff
        and t.get('pnl') is not None
    ]
    if not closed:
        return None
    wins = [t for t in closed if t['pnl'] > 0]
    return round(len(wins) / len(closed) * 100, 1)


def get_deployed_capital() -> float:
    open_trades = get_open_trades()
    return round(sum(t['capital_deployed'] for t in open_trades), 2)
