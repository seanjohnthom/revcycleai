# Trading Lessons Learned

## February 20, 2026 — The Minnesota Trade

### What Happened
- **8am automated scan:** Found OKC @ 89¢ (5% edge), placed trade
- **9:30am manual check:** User spotted NBA games on mobile app
- **9:45am deep scan:** Found Minnesota @ 87¢ (69% edge) — THE ONLY opportunity in 1,200 markets
- **User decision:** Chose Kelly sizing (4 contracts = $3.48) over conservative auto-scale (2 contracts = $1.74)

### Key Insights

#### ✅ What Worked Well

1. **User intuition beats automation**
   - Mobile app showed games that weren't in morning scan
   - Asking "are there other opportunities?" led to finding Minnesota
   - Human pattern recognition: "I see LA vs LA and several others"

2. **Kelly sizing on exceptional edges**
   - Edge formula: 69.2% (market 87% → true 96%)
   - Auto-scale would cap at $2.50 (2 contracts)
   - Kelly recommended $3.56 (4 contracts = $3.48)
   - When edge is >50%, trust Kelly over conservative caps

3. **Comprehensive verification**
   - Scanned 1,200 markets across all categories
   - Confirmed Minnesota was the ONLY ≥5% edge opportunity
   - No regrets about missing trades — we got the one that mattered

4. **Favorite-longshot bias model is selective**
   - Only triggers on 80-97¢ favorites
   - Market efficiency: 1,199 out of 1,200 markets fairly priced
   - Low false positive rate = good model discipline

#### ⚠️ What Needs Improvement

1. **Timing of scans**
   - 8am scan ran BEFORE NBA games opened with pricing
   - Minnesota market went live sometime between 8am-9:30am
   - **Solution:** Add midday scan (12pm CT) to catch newly opened markets

2. **API vs Mobile App lag**
   - Mobile app showed games with pricing
   - API `/markets` endpoint didn't return them initially
   - Needed direct ticker search to find them
   - **Solution:** Build a ticker generator based on known game schedules

3. **Auto-scale caps on exceptional edges**
   - $2.50 cap at <$50 bankroll is conservative
   - Made sense for 5-10% edges
   - On 69% edge (9 percentage point advantage), Kelly math is more accurate
   - **Solution:** Override auto-scale when edge >40% and bet Kelly (capped at 15% bankroll)

4. **Position tracking**
   - Had to manually calculate deployed capital
   - Needed live API call to verify positions
   - **Solution:** Add real-time portfolio dashboard to bot

### Lessons for Tomorrow

#### Immediate Changes

1. **Add midday scan cron (12pm CT)**
   - Catches markets that open after morning scan
   - NBA games often get pricing 2-6 hours before tip-off
   - Run same analysis as 8am scan

2. **Kelly override rule**
   ```python
   if edge >= 0.40:  # 40%+ edge
       use_kelly_sizing = True
       max_position = min(balance * 0.15, balance * edge * 0.25)
   else:
       use_kelly_sizing = False
       max_position = get_max_position_for_balance(balance)
   ```

3. **Build NBA ticker generator**
   - Parse known game schedules
   - Generate expected tickers: KXNBAGAME-{date}{away}{home}-{team}
   - Try direct lookups instead of relying on `/markets` endpoint

4. **Portfolio status command**
   - `python3 kalshi_bot.py --status` shows live portfolio
   - Balance, deployed capital, cash available, open positions
   - Unrealized P&L on open positions

#### Strategic Learnings

1. **Market efficiency varies by time of day**
   - Morning: Macro markets (CPI, GDP) often mispriced after overnight news
   - Midday: New markets open, brief mispricing window
   - Evening: Sports markets tighten as game time approaches

2. **When to override automation**
   - Exceptional edges (>40%) deserve Kelly sizing
   - User intuition about "other opportunities" worth checking
   - Mobile app can show markets API doesn't return yet

3. **Sample size matters**
   - Only 3 settled trades so far (2 wins, 1 loss)
   - Model needs 20-30 trades to validate edge assumptions
   - Be conservative until track record proves out

4. **Opportunity scarcity**
   - 1 tradeable opportunity out of 1,200 markets
   - When you find edge, bet it properly
   - Don't chase — if nothing meets threshold, sit out

### Metrics to Track

- **Scan efficiency:** How many opportunities per 100 markets scanned?
- **API lag:** Time between market opening and appearing in `/markets` endpoint
- **Edge realization:** Do 69% edge markets actually hit 96%? Or is model overconfident?
- **Kelly vs auto-scale:** Track P&L difference when overriding caps

### Tomorrow's Checklist

- [ ] Add 12pm CT midday scan cron
- [ ] Build Kelly override logic for edges >40%
- [ ] Create `--status` command for live portfolio
- [ ] Test NBA ticker generator
- [ ] Document OKC + Minnesota settlement results
- [ ] Update edge assumptions if both lose (model recalibration)

---

**Bottom line:** User instinct + bot automation = optimal. Trust Kelly math on exceptional edges. Scan more frequently to catch newly opened markets.
