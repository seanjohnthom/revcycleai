#!/usr/bin/env python3
"""Position sizing and risk management."""
import math, os
from typing import Optional
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

MAX_POSITIONS  = int(os.getenv('MAX_POSITIONS', '8'))
MIN_POSITION   = float(os.getenv('MIN_POSITION', '1.00'))
MIN_EDGE       = float(os.getenv('MIN_EDGE', '0.05'))
MONTHLY_BUDGET = float(os.getenv('MONTHLY_BUDGET', '25.00'))
CASH_RESERVE   = 4.50  # Always keep this undeployed
KELLY_FRACTION = 0.25  # Fractional Kelly multiplier (25% = quarter-Kelly, conservative)
KELLY_MAX_PCT  = 0.15  # Never risk more than 15% of bankroll on a single position

# Dynamic scaling tiers — MAX_POSITION scales with bankroll
SCALING_TIERS = [
    (50, 2.50),    # Under $50: $2.50 max (10% of $25)
    (100, 5.00),   # $50-$99: $5 max (10% of $50)
    (250, 10.00),  # $100-$249: $10 max (10% of $100)
    (500, 20.00),  # $250-$499: $20 max (8% of $250)
    (float('inf'), 40.00)  # $500+: $40 max (8% of $500)
]


def get_max_position_for_balance(balance: float) -> float:
    """
    Returns dynamic MAX_POSITION based on current balance.
    Scales up as bankroll grows while maintaining risk discipline.
    """
    for threshold, max_pos in SCALING_TIERS:
        if balance < threshold:
            return max_pos
    return SCALING_TIERS[-1][1]  # Fallback to largest tier


def kelly_fraction(true_prob: float, market_price: float) -> float:
    """
    Full Kelly criterion for a binary prediction market contract.

    For a YES contract priced at p_market:
      - Win: profit = (1 - p_market) per dollar risked
      - Loss: lose p_market per dollar risked
      - Kelly fraction = (p_true - p_market) / (1 - p_market)

    Returns full Kelly fraction (0.0–1.0) of bankroll to wager.
    Edge must be positive or returns 0.
    """
    if market_price <= 0 or market_price >= 1:
        return 0.0
    edge = true_prob - market_price
    if edge <= 0:
        return 0.0
    f = edge / (1.0 - market_price)
    return max(0.0, min(f, 1.0))  # Clamp 0-100%


def calculate_position_size(edge: float, price_cents: int, balance_cents: int,
                             true_prob: float = None) -> float:
    """
    Returns dollar amount to deploy using Kelly Criterion sizing.

    Kelly formula for binary market:
        f* = (p_true - p_market) / (1 - p_market)

    We apply KELLY_FRACTION (quarter-Kelly by default) for conservatism,
    then cap at dynamic MAX_POSITION (scales with bankroll) and KELLY_MAX_PCT.
    Falls back to edge-table sizing if true_prob not provided.
    """
    balance = balance_cents / 100
    price   = price_cents / 100
    available = max(0, balance - CASH_RESERVE)
    
    # Dynamic max position based on current balance
    max_position = get_max_position_for_balance(balance)

    if true_prob is not None and 0 < price < 1:
        # Kelly-based sizing
        f_full     = kelly_fraction(true_prob, price)
        f_scaled   = f_full * KELLY_FRACTION           # Quarter-Kelly
        kelly_size = f_scaled * balance                 # Dollar amount
        max_kelly  = balance * KELLY_MAX_PCT            # Hard cap (15% of bankroll)
        base_size  = min(kelly_size, max_kelly)

        # Log the Kelly calculation for transparency
        print(f"    Kelly: f*={f_full:.3f} → x{KELLY_FRACTION} = {f_scaled:.3f} → "
              f"${kelly_size:.2f} (cap: ${max_kelly:.2f}, max_pos: ${max_position:.2f})")
    else:
        # Fallback edge-table sizing (used when true_prob unavailable)
        if edge >= 0.20:
            base_size = 2.00
        elif edge >= 0.10:
            base_size = 1.25
        elif edge >= 0.05:
            base_size = 0.625
        else:
            return 0

    # Hard caps: dynamic MAX_POSITION + available cash
    size = min(base_size, max_position, available)

    if size < MIN_POSITION and available >= MIN_POSITION:
        size = MIN_POSITION
    elif size < 0.50:
        return 0

    return round(size, 2)


def contract_count(position_size: float, price_cents: int) -> int:
    """How many contracts to buy for a given dollar size and price."""
    if price_cents <= 0:
        return 0
    price = price_cents / 100
    return max(1, math.floor(position_size / price))


def can_open_position(open_positions: list, balance_cents: int,
                      position_size: float) -> tuple[bool, str]:
    """
    Check all risk rules before opening a new position.
    Returns (ok, reason).
    """
    balance = balance_cents / 100
    # Only count positions with actual quantity (non-zero)
    active_positions = [p for p in open_positions if abs(p.get('position', 0)) > 0]
    
    # Dynamic max position based on current balance
    max_position = get_max_position_for_balance(balance)

    if len(active_positions) >= MAX_POSITIONS:
        return False, f"Max positions reached ({MAX_POSITIONS})"

    if balance < CASH_RESERVE + MIN_POSITION:
        return False, f"Insufficient balance (${balance:.2f}, need ${CASH_RESERVE + MIN_POSITION:.2f})"

    if position_size < MIN_POSITION:
        return False, f"Position too small (${position_size:.2f} < ${MIN_POSITION:.2f})"

    if position_size > max_position:
        return False, f"Position exceeds max (${position_size:.2f} > ${max_position:.2f})"

    # Category concentration: max 40% in any one category
    # (simplified check — full impl would check categories)

    return True, "OK"


def get_limit_price(orderbook: dict, side: str) -> Optional[int]:
    """
    Calculate limit order price 1-2 cents inside the spread.
    Kalshi orderbook: yes/no arrays are sorted LOWEST→HIGHEST price.
    Best YES bid = yes[-1][0]; Best NO bid = no[-1][0].
    YES ask implied = 100 - best NO bid.
    Returns price in cents.
    """
    try:
        yes_bids = orderbook.get('yes', [])  # [[price, qty], ...] low→high
        no_bids  = orderbook.get('no', [])   # [[price, qty], ...] low→high

        if side == 'yes':
            best_yes_bid = yes_bids[-1][0] if yes_bids else None
            best_yes_ask = (100 - no_bids[-1][0]) if no_bids else None

            if best_yes_bid and best_yes_ask:
                spread = best_yes_ask - best_yes_bid
                if spread <= 0:
                    # No spread — just use the best bid
                    return best_yes_bid
                offset = min(2, max(1, spread // 2))
                return min(99, best_yes_bid + offset)
            return best_yes_bid

        elif side == 'no':
            best_no_bid = no_bids[-1][0] if no_bids else None
            best_no_ask = (100 - yes_bids[-1][0]) if yes_bids else None

            if best_no_bid and best_no_ask:
                spread = best_no_ask - best_no_bid
                if spread <= 0:
                    return best_no_bid
                offset = min(2, max(1, spread // 2))
                return min(99, best_no_bid + offset)
            return best_no_bid

    except Exception:
        pass
    return None


def should_exit(position: dict, current_price_cents: int) -> tuple[bool, str]:
    """
    Check exit triggers for an open position.
    Returns (should_exit, reason).
    """
    entry_price = position.get('entry_price_cents', 0)
    if not entry_price:
        return False, ""

    # Loss cut: down 50%+ from entry
    if current_price_cents <= entry_price * 0.50:
        return True, f"Loss limit hit: entry ${entry_price/100:.2f}, current ${current_price_cents/100:.2f}"

    # Profit target: up 50%+ from entry (lock gains)
    if current_price_cents >= entry_price * 1.50:
        return True, f"Profit target hit: entry ${entry_price/100:.2f}, current ${current_price_cents/100:.2f}"

    # Near settlement (price close to $1): lock gains if ≥ 95¢ AND we're in profit
    # NOTE: Threshold raised from 90¢ to 95¢ to avoid premature exits on high-prob
    # contracts that were entered near 90¢ (e.g. GDP YES entered at 90¢ should
    # NOT exit immediately just because price is 90¢).
    if current_price_cents >= 95 and current_price_cents > entry_price:
        return True, f"Near settlement at ${current_price_cents/100:.2f}, locking gains"

    return False, ""
