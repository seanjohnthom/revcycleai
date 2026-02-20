# Proposed Improvements for Tomorrow

## Priority 1: Midday Scan (High Impact, Easy)

**Problem:** Minnesota market opened between 8am-9:30am, after morning scan  
**Solution:** Add 12pm CT scan to catch newly opened markets

```bash
# Add cron job
python3 kalshi_bot.py --scan --trade
# Schedule: Daily 12:00 PM CT
```

**Expected impact:** Catch 2-5 additional opportunities per week

---

## Priority 2: Kelly Override on Exceptional Edges (High Impact, Medium)

**Problem:** Auto-scale cap ($2.50) leaves money on table for 69% edges  
**Solution:** Override auto-scale when edge ≥40%, use Kelly (capped at 15% bankroll)

**Code change in `position_manager.py`:**
```python
def calculate_position_size(balance, edge, price, open_positions):
    kelly_fraction = 0.25
    kelly_max = 0.15
    
    # Kelly override for exceptional edges
    if edge >= 0.40:
        kelly_raw = edge * kelly_fraction
        kelly_capped = min(kelly_raw, kelly_max)
        max_position = balance * kelly_capped
        use_kelly = True
    else:
        max_position = get_max_position_for_balance(balance)
        use_kelly = False
    
    # Rest of sizing logic...
```

**Expected impact:** +20-40% profit on exceptional edges (1-2 per month)

---

## Priority 3: Portfolio Status Command (Medium Impact, Easy)

**Problem:** Had to manually calculate deployed capital and positions  
**Solution:** `python3 kalshi_bot.py --status` shows live portfolio

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KALSHI PORTFOLIO STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balance:           $23.75
Deployed:          $8.11
Cash available:    $15.64
Open positions:    3/8
Realized P&L:      +$2.32

OPEN POSITIONS:
1. KXCPI-26FEB-T0.1 (NO -32) — $3.84 deployed
2. KXNBAGAME-26FEB20BKNOKC-OKC (YES 1) — $0.89 deployed | +$0.02 unrealized
3. KXNBAGAME-26FEB20DALMIN-MIN (YES 4) — $3.48 deployed | TBD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Expected impact:** Better decision making, faster portfolio visibility

---

## Priority 4: NBA Ticker Generator (Medium Impact, Medium)

**Problem:** API `/markets` lags behind mobile app; games open before appearing  
**Solution:** Generate expected tickers and try direct lookups

**Logic:**
1. Get today's NBA schedule (from ESPN API or hardcoded)
2. Generate tickers: `KXNBAGAME-{date}{away}{home}-{team}`
3. Try `get_market(ticker)` for each team
4. If 404, skip; if 200, analyze for edge

**Expected impact:** Find opportunities 1-3 hours earlier

---

## Priority 5: Edge Realization Tracking (Low Impact, High Value)

**Problem:** Don't know if 69% edge formula actually reflects reality  
**Solution:** Track predicted vs actual win rates

**After each settlement:**
```python
{
  "ticker": "KXNBAGAME-26FEB20DALMIN-MIN",
  "edge_predicted": 0.692,
  "market_prob": 0.87,
  "model_prob": 0.96,
  "actual_result": "win" or "loss",
  "settled_date": "2026-02-20"
}
```

**After 20-30 trades:**
- If 96% model_prob markets win 96% → model is accurate
- If 96% model_prob markets win 87% → model is overconfident, recalibrate
- If 96% model_prob markets win 100% → model is underconfident, bet more

**Expected impact:** Model refinement, better sizing over time

---

## Implementation Priority

**Today (before 7pm games):**
1. ✅ Document lessons (DONE)
2. Add `--status` command (15 min)

**Tomorrow morning:**
3. Add midday scan cron (5 min)
4. Update Kelly override logic (30 min)

**This weekend:**
5. Build NBA ticker generator (1-2 hours)
6. Add edge realization tracking (1 hour)

---

## Testing Plan

1. **Status command:** Run now, verify output matches manual calculation
2. **Midday scan:** Run manually at 12pm tomorrow, check for new opportunities
3. **Kelly override:** Backtest on Minnesota trade (should recommend 4 contracts)
4. **NBA ticker generator:** Test with tonight's games, verify it finds them
5. **Edge tracking:** Add to ledger after OKC/Minnesota settle

---

## Success Metrics (30 days)

- Opportunities found: 8am scan vs 12pm scan (expect 60/40 split)
- Kelly override profitability: Track P&L when edge >40%
- Model accuracy: Win rate on 80-97¢ favorites (target: 90-96%)
- Missed opportunities: Zero (comprehensive scans catch everything)

