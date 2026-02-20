#!/usr/bin/env python3
"""Edge detection and market analysis for Kalshi trading."""
import math
from datetime import datetime, timezone
from typing import Optional


# Category classification by ticker/title keywords
CATEGORY_KEYWORDS = {
    'economics': ['FED', 'CPI', 'NFP', 'GDP', 'JOBS', 'INFLATION', 'RATE', 'FOMC',
                  'UNEMPLOYMENT', 'PAYROLL', 'DEFICIT', 'DEBT', 'BUDGET'],
    'politics': ['HOUSE', 'SENATE', 'CONGRESS', 'BILL', 'LAW', 'ELECTION', 'VOTE',
                 'SHUTDOWN', 'PRESIDENT', 'EXECUTIVE', 'CONFIRM', 'NOMINATE'],
    'weather': ['TEMP', 'WEATHER', 'RAIN', 'SNOW', 'STORM', 'HURRICANE', 'TORNADO',
                'HEAT', 'COLD', 'FLOOD', 'DROUGHT', 'NOAA'],
    'sports': ['NBA', 'NFL', 'MLB', 'NHL', 'SOCCER', 'TENNIS', 'GOLF', 'CHAMPIONSHIP',
               'SUPER', 'WORLD', 'SERIES'],
    'entertainment': ['OSCAR', 'GRAMMY', 'EMMY', 'AWARD', 'MOVIE', 'BOX', 'OFFICE',
                      'NETFLIX', 'STREAMING'],
    'crypto': ['BTC', 'ETH', 'BITCOIN', 'CRYPTO', 'ETHEREUM'],
    'tech': ['APPLE', 'GOOGLE', 'META', 'AMAZON', 'MSFT', 'AI', 'EARNINGS'],
}

# Tier weights for allocation strategy
TIER_WEIGHTS = {
    'economics': 1.0,
    'politics': 1.0,
    'weather': 0.75,
    'tech': 0.75,
    'sports': 0.5,
    'entertainment': 0.5,
    'crypto': 0.6,
    'other': 0.4,
}


def classify_market(ticker: str, title: str) -> str:
    combined = (ticker + ' ' + title).upper()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return category
    return 'other'


def days_to_resolution(close_time_str: str) -> Optional[float]:
    """Return days until market closes. None if unparseable."""
    if not close_time_str:
        return None
    try:
        close_time = datetime.fromisoformat(close_time_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = close_time - now
        return delta.total_seconds() / 86400
    except Exception:
        return None


def implied_probability(yes_price_cents: int) -> float:
    """Convert cents price to 0-1 probability."""
    return yes_price_cents / 100.0


def kelly_criterion(edge: float, price: float) -> float:
    """Half-Kelly position size as fraction of bankroll."""
    if price <= 0 or price >= 1:
        return 0
    odds_against = (1.0 / price) - 1.0
    if odds_against <= 0:
        return 0
    full_kelly = edge / odds_against
    return max(0, full_kelly / 2)  # Half-Kelly


def compute_true_probability(market: dict, category: str) -> Optional[float]:
    """
    Estimate true probability using available signals.
    Returns None if we can't form a view.
    
    Core strategies:
    1. Favorite-longshot bias exploitation (main structural edge)
    2. Category-specific adjustments
    """
    yes_price = market.get('yes_bid', 0) or market.get('last_price', 0)
    if not yes_price:
        return None

    implied = implied_probability(yes_price)

    # STRATEGY: Favorite-Longshot Bias
    # High-probability contracts (80-97¢) are systematically underpriced
    # Low-probability contracts (5-15¢) are systematically overpriced

    if implied >= 0.80:
        # Strong favorite: true prob higher than market implies
        # Research suggests ~5-8% underpricing in this range
        # ADJUSTED: differentiate by category — economics markets are slightly more
        # efficient than sports; use 5% for economics, 7% for sports (NBA strong fav)
        if category == 'sports':
            bias_correction = 0.07  # Sports favorites are more underpriced on Kalshi
        elif category == 'economics':
            bias_correction = 0.05  # Slightly more efficient; was 0.06 (reduced)
        else:
            bias_correction = 0.06
        true_prob = min(0.97, implied + bias_correction)

    elif implied >= 0.70:
        # Moderate favorite: slight underpricing
        if category == 'sports':
            bias_correction = 0.05  # Sports 70-80% still has meaningful bias
        elif category == 'economics':
            bias_correction = 0.02  # Economics more efficient in this range
        else:
            bias_correction = 0.03
        true_prob = min(0.95, implied + bias_correction)

    elif implied >= 0.55 and category == 'sports':
        # NBA/NFL slight favorites still show longshot bias in markets
        true_prob = implied + 0.03
        true_prob = min(0.90, true_prob)

    elif implied <= 0.10:
        # Longshot trap: overpriced, skip (not a good buy)
        return None

    elif implied <= 0.20:
        # Low prob: slight overpricing, slight NO edge
        true_prob = implied * 0.85  # deflate by 15%

    else:
        # Middle range (20-70%): use market as baseline with minor adjustments
        # Apply category-specific nudges
        if category == 'economics':
            # Economic markets tend to be more efficient but slight favorite bias
            true_prob = implied + 0.01 if implied > 0.5 else implied - 0.01
        elif category == 'weather':
            # Weather models give us edge; assume slight correction toward high probs
            true_prob = implied + 0.02 if implied > 0.6 else implied
        elif category == 'sports':
            # Sports markets: even moderate favorites underpriced due to retail bias
            true_prob = implied + 0.02 if implied > 0.5 else implied
        else:
            true_prob = implied  # No systematic edge in middle range

    return max(0.01, min(0.99, true_prob))


def analyze_market(market: dict) -> Optional[dict]:
    """
    Run full 5-step edge analysis on a market.
    Returns analysis dict or None if no edge found.
    """
    ticker = market.get('ticker', '')
    title = market.get('title', ticker)
    yes_bid = market.get('yes_bid', 0) or 0
    yes_ask = market.get('yes_ask', 0) or 0
    volume = market.get('volume', 0) or 0
    volume_24h = market.get('volume_24h', 0) or 0
    liquidity = market.get('liquidity', 0) or 0
    close_time = market.get('close_time', '')
    status = market.get('status', '')
    last_price = market.get('last_price', 0) or 0
    market_type = market.get('market_type', '')

    # STEP 1: Market vitals
    # Skip multivariate (parlay) markets — low liquidity, too complex
    if 'MVE' in ticker.upper() or 'KXMVE' in ticker.upper():
        return None

    # Market must be active
    if status and status not in ('open', 'active'):
        return None

    # Need tradeable prices
    yes_price = yes_bid or last_price
    if not yes_price or yes_price <= 0:
        return None

    # Need at least a bid OR a last price; ask can be 0 for very high prob markets
    if yes_bid <= 0 and last_price <= 0:
        return None
    # If no ask, use bid+2 as estimate
    if yes_ask <= 0:
        yes_ask = min(99, yes_bid + 2)

    days_left = days_to_resolution(close_time)
    if days_left is None or days_left < 0.5 or days_left > 30:
        return None

    # Use 24h volume or total volume — accept markets with at least some activity
    effective_volume = max(volume, volume_24h, liquidity)
    if effective_volume < 200:
        return None

    # STEP 2: Classify and estimate true probability
    category = classify_market(ticker, title)
    # Use mid-price for implied probability
    yes_mid = (yes_bid + yes_ask) / 2
    true_prob = compute_true_probability({**market, 'yes_bid': int(yes_mid)}, category)
    if true_prob is None:
        return None

    implied = implied_probability(int(yes_mid))
    yes_price = int(yes_mid)

    # STEP 3: Calculate edge
    # Determine which side has the edge
    edge_yes = true_prob - implied        # positive = buy YES
    edge_no  = (1 - true_prob) - (1 - implied)  # positive = buy NO (same as -edge_yes)

    if abs(edge_yes) < 0.05:
        return None

    # Best side
    if edge_yes >= 0.05:
        trade_side = 'yes'
        trade_action = 'buy'
        edge = edge_yes
        entry_price_cents = yes_bid or yes_price
    elif edge_yes <= -0.05:
        trade_side = 'no'
        trade_action = 'buy'
        edge = -edge_yes  # magnitude
        no_price = 100 - (yes_ask or yes_price)
        entry_price_cents = no_price
    else:
        return None

    if entry_price_cents <= 0 or entry_price_cents >= 100:
        return None

    # STEP 4: Risk checks
    liquidity_ok = effective_volume >= 200
    time_ok = 0.5 <= days_left <= 30
    price_ok = 0.01 <= entry_price_cents / 100 <= 0.99

    if not (liquidity_ok and time_ok and price_ok):
        return None

    # STEP 5: Limit order price — 1-2 cents inside the spread
    if trade_side == 'yes' and yes_ask and yes_bid:
        spread = yes_ask - yes_bid
        limit_price = yes_bid + min(2, max(1, spread // 2))
    elif trade_side == 'no' and yes_ask and yes_bid:
        no_bid = 100 - yes_ask
        no_ask = 100 - yes_bid
        spread = no_ask - no_bid
        limit_price = no_bid + min(2, max(1, spread // 2))
    else:
        limit_price = entry_price_cents

    limit_price = max(1, min(99, int(limit_price)))

    # NOTE: Position size is NOT calculated here — the bot passes balance
    # and calls position_manager.calculate_position_size() with true_prob
    # for proper Kelly sizing. We pass true_prob in the result for that.
    entry_price = entry_price_cents / 100
    tier_weight = TIER_WEIGHTS.get(category, 0.4)
    estimated_contracts = max(1, math.floor(
        min(2.50 * tier_weight, 2.50) / entry_price
    ))

    return {
        'ticker': ticker,
        'title': title,
        'category': category,
        'tier_weight': tier_weight,
        'yes_price_cents': yes_price,
        'implied_prob': round(implied, 4),
        'true_prob': round(true_prob, 4),
        'edge': round(edge, 4),
        'trade_side': trade_side,
        'trade_action': trade_action,
        'limit_price_cents': limit_price,
        'contracts': estimated_contracts,         # Refined by Kelly in bot
        'position_size': None,                    # Set by bot after Kelly calc
        'days_to_resolution': round(days_left, 1),
        'volume': effective_volume,
        'close_time': close_time,
        'thesis': (
            f"{'Favorite-longshot' if trade_side == 'yes' and implied >= 0.70 else 'Edge'} bias: "
            f"market implies {implied:.0%}, estimate {true_prob:.0%} ({edge:.0%} edge). "
            f"Buy {trade_side.upper()} @ ${limit_price/100:.2f}. "
            f"Category: {category}. Days left: {days_left:.1f}."
        ),
    }


def rank_opportunities(markets: list) -> list:
    """Analyze all markets and return ranked list of opportunities."""
    results = []
    for market in markets:
        analysis = analyze_market(market)
        if analysis:
            results.append(analysis)
    # Sort by edge magnitude descending
    results.sort(key=lambda x: x['edge'], reverse=True)
    return results
