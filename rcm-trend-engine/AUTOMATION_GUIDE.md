# RCM Trend Engine — Full Automation Guide

## Daily Automation (6am CT)

**Current Cron:** `18b77735`  
**Command:** `cd /Users/shackleton/.openclaw/workspace/rcm-trend-engine && PYTHONPATH=/Users/shackleton/.openclaw/workspace/rcm-trend-engine python3 -m engine.trend_monitor`

---

## How It Works

### 1. RSS Feed Scanning (Automated ✅)
- Scans 14 RSS feeds for RCM news
- Scores articles based on keywords
- Saves to `data/trending.json`
- **Fully automated** — runs every morning at 6am CT

### 2. Web Scraping (Manual for now ⏳)
When RSS feeds are quiet (< 3 new articles), the agent should:

**Sites to scrape:**
- https://www.healthcarefinancenews.com/
- https://www.beckershospitalreview.com/finance/
- https://www.modernhealthcare.com/revenue-cycle
- https://www.hfma.org/revenue-cycle

**Process:**
1. Use `web_fetch` to get each site
2. Extract 5 most recent RCM/revenue cycle headlines
3. Generate blog posts + LinkedIn posts
4. Update revcycleai.com homepage + blog index
5. Commit and push to GitHub

**Example workflow (what we did today Feb 21):**
```
1. Ran 6am cron → 0 new RSS articles (weekend)
2. Agent scanned HealthcareFinanceNews.com manually
3. Found 3 fresh stories (AI vendor spend, payer mix, MA growth)
4. Generated 1 blog post + 3 LinkedIn posts
5. Deployed to revcycleai.com
```

---

## 3. LinkedIn Auto-Posting (Blocked ❌ → Activates Monday)

**Status:** API permissions pending (403 error on `organizationAcls`)  
**Expected fix:** Monday Feb 23, 2026  
**Location:** `/workspace/rcm-trend-engine/linkedin_poster.py`

**Once activated:**
- Cron auto-posts to RevCycleAI company page
- No manual intervention needed
- Posts immediately after blog content is generated

---

## Making Web Scraping Fully Automated

**Option 1: Modify Cron to Call Agent**

Update cron command to:
```python
# After trend_monitor runs, check if < 3 articles
# If so, trigger agent to scrape fresh content
cd /workspace/rcm-trend-engine && python3 -c "
from engine import trend_monitor
import subprocess

results = trend_monitor.run_scan(verbose=True)
if results['total_new'] < 3:
    print('📰 RSS quiet. Triggering fresh content scraping...')
    subprocess.run(['openclaw', 'agent', 'run', 
        'Scan healthcare news sites for fresh RCM stories. Generate blog post and LinkedIn posts. Deploy to revcycleai.com.'])
"
```

**Option 2: Weekend-Specific Cron**

Create a second cron that runs **Saturdays only**:
- Scans healthcare news sites
- Generates fresh content
- Deploys automatically

**Option 3: Manual Trigger (Current)**

Keep daily RSS cron as-is. When I (agent) see the 6am cron fired with 0 articles, I proactively:
1. Scan healthcare news sites
2. Generate content
3. Deploy

This is what we did today and it worked perfectly.

---

## Recommendation

**Start with Option 3 (manual agent trigger)**

Pros:
- Works now (no code changes needed)
- Agent has full context and judgment
- Can handle edge cases (API down, site blocked, etc.)

Cons:
- Requires agent to notice and act
- Not 100% hands-off

**Once LinkedIn API works, upgrade to Option 1 or 2** for full autonomy.

---

## Current Status (Feb 21, 2026)

✅ **RSS scanning:** Fully automated  
✅ **Blog generation:** Automated (when RSS has content)  
✅ **Web scraping:** Manual trigger (agent-initiated)  
✅ **GitHub deployment:** Automated  
❌ **LinkedIn auto-posting:** Blocked until Monday  

**Next milestone:** LinkedIn API activation → 100% automation achieved.
