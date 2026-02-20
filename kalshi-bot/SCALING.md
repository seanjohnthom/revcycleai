# Kalshi Bot Auto-Scaling Feature

## What It Does

The bot now **automatically scales position sizes** as your bankroll grows. This lets you capitalize on winning streaks while maintaining strict risk discipline.

## Scaling Tiers

| Bankroll | Max Position | % of Bankroll | Notes |
|----------|--------------|---------------|-------|
| < $50 | $2.50 | 10% | Starting tier (conservative) |
| $50-$99 | $5.00 | 10% | 2x position size |
| $100-$249 | $10.00 | 10% | 4x position size |
| $250-$499 | $20.00 | 8% | 8x position size (slightly lower %) |
| $500+ | $40.00 | 8% | 16x position size (max tier) |

## Risk Controls (Always Active)

Even with larger positions, these limits never change:

✅ **Quarter-Kelly sizing** (0.25x full Kelly) — Conservative bet sizing  
✅ **15% max bankroll cap** — Never risk more than 15% on one trade  
✅ **5% minimum edge** — No trades below 5% advantage  
✅ **Max 8 simultaneous positions** — Diversification enforced  
✅ **$4.50 cash reserve** — Always keep minimum available  

## How It Works

1. **Every trade**, bot checks current balance
2. **Calculates dynamic MAX_POSITION** based on tier
3. **Kelly formula** still runs (unchanged)
4. **Final size** = min(Kelly size, 15% cap, dynamic max, available cash)

### Example

**Scenario:** You grow from $25 → $100 bankroll

**Old system (static $2.50 max):**
- 6% edge trade @ $0.90
- Kelly says: $1.80
- Max cap: $2.50
- **Position: $1.80** ❌ (leaving money on table)

**New system (dynamic scaling):**
- Same 6% edge @ $0.90
- Kelly says: $3.60 (scaled with $100 bankroll)
- 15% cap: $15.00
- Dynamic max: $10.00 (new tier)
- **Position: $3.60** ✅ (scales with bankroll)

## Profit Milestones

If the model keeps winning, here's what to expect:

### Milestone 1: $50 bankroll (+100% gain)
- Max position doubles to $5
- Can take bigger bites of high-edge opportunities
- Still conservative (10% max)

### Milestone 2: $100 bankroll (+300% gain)
- Max position: $10
- Now in "serious trader" territory
- Kelly sizing really shines here

### Milestone 3: $250 bankroll (+900% gain)
- Max position: $20
- Operating at scale
- Model is proven, now maximizing edge

### Milestone 4: $500 bankroll (+1,900% gain)
- Max position: $40
- Top tier unlocked
- Generate real alpha

## When to Withdraw Profits

**Suggested strategy:**

1. **Let it run to $100** — Validate the model with real volume
2. **At $250** — Consider withdrawing 50% ($125), keep $125 deployed
3. **At $500** — Withdraw another 50%, keep $250 working
4. **Above $1,000** — You've beaten the market. Withdraw aggressively, keep $500 max deployed

This keeps risk bounded while letting wins compound.

## Testing

Current balance: **$18.75**  
Current tier: **< $50**  
Max position: **$2.50**

After tomorrow's GDP settlement:
- If all 3 GDP trades win (+$0.30 profit) → Still in $2.50 tier
- Need to reach $50 to unlock $5 max positions

## Monitoring

The bot logs dynamic max in every trade decision:

```
Kelly: f*=0.067 → x0.25 = 0.017 → $0.32 (cap: $2.81, max_pos: $2.50)
```

Watch for `max_pos` to increase as bankroll grows.

## Manual Override

If you want to lock position sizing at current level (pause scaling):

Edit `position_manager.py` and replace `get_max_position_for_balance(balance)` with a fixed value:

```python
max_position = 2.50  # Lock at $2.50 regardless of balance
```

Not recommended — scaling is the whole point!

---

**Bottom line:** The bot now grows with you. Start conservative, scale systematically, maintain discipline. Let the edge compound.
