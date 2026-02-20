# Email Enrichment Setup Guide

## Overview

Multi-source email lookup with fallback chain gives you **235 verified lookups/month for free**:

- **Hunter.io:** 25 searches + 50 verifications/month
- **Skrapp.io:** 150 emails/month (BEST free tier)
- **Apollo.io:** 60 credits/month
- **Pattern matching:** Unlimited (50% confidence)

## Setup Steps

### 1. Get API Keys

#### Hunter.io (25/mo)
1. Go to https://hunter.io
2. Sign up for free account (use `shackletonbot@gmail.com` / `Endurance123`)
3. Go to https://hunter.io/api-keys
4. Copy your API key

#### Skrapp.io (150/mo — BEST)
1. Go to https://www.skrapp.io
2. Sign up for free account
3. Go to https://www.skrapp.io/dashboard/api
4. Generate an API key
5. Copy the token

#### Apollo.io (60/mo)
1. Go to https://app.apollo.io
2. Sign up for free account
3. Go to https://app.apollo.io/#/settings/integrations/api
4. Click "Create New Key"
5. Copy the API key

### 2. Configure Keys

Run the setup script:

```bash
cd /Users/shackleton/.openclaw/workspace/axlow-autopilot/leads
python3 email_enrichment.py --setup
```

It will prompt you for each API key. Paste them when asked.

**OR** manually edit `config.json`:

```json
{
  "hunter_api_key": "YOUR_HUNTER_KEY",
  "skrapp_api_key": "YOUR_SKRAPP_KEY",
  "apollo_api_key": "YOUR_APOLLO_KEY",
  "google_sheet_id": "1D4yVYdu5iG--is_aAVfUXnJ9UnOmfimWc5fQKxtNFmI"
}
```

### 3. Test It

```bash
python3 email_enrichment.py
```

This runs a test lookup for "John Smith @ acmebilling.com" and shows which source found an email.

## How It Works

**Fallback chain:**

1. **Try Hunter.io first** (highest accuracy, limited credits)
2. If no result → **Try Skrapp.io** (best free tier)
3. If no result → **Try Apollo.io** (good B2B coverage)
4. If all fail → **Pattern matching** (firstname.lastname@domain.com)

**Example flow:**

```
Looking up: Sarah Johnson @ dentalrcm.com
  [Hunter.io] Rate limit reached
  ✓ Found via Skrapp.io: sarah.johnson@dentalrcm.com (confidence: 85%)
```

## Usage in Lead Hunter

The Monday lead hunter cron automatically uses this system:

```python
from email_enrichment import find_email

result = find_email(
    first_name="Sarah",
    last_name="Johnson",
    company_name="Dental RCM Solutions",
    company_domain="dentalrcm.com"
)

if result:
    email = result["email"]
    confidence = result["confidence"]
    source = result["source"]
```

## Monthly Limits

| Source | Free Tier | Resets |
|--------|-----------|--------|
| Hunter.io | 25 searches, 50 verifications | 1st of month |
| Skrapp.io | 150 emails | 1st of month |
| Apollo.io | 60 credits | 1st of month |
| Pattern matching | Unlimited | Never |

**Total verified:** 235/month  
**Total with pattern:** Unlimited

## Email Verification

Hunter.io also verifies emails (separate quota: 50/month):

```python
from email_enrichment import verify_email

result = verify_email("sarah.johnson@dentalrcm.com")
# Returns: {"valid": True, "result": "deliverable", "score": 95}
```

Use this to validate pattern-matched emails before sending cold emails.

## Confidence Levels

- **90-100%:** Hunter.io verified
- **75-89%:** Skrapp.io or Apollo.io found
- **50-74%:** Pattern matched (unverified)

**Best practice:**
- Confidence ≥75%: Safe to cold email immediately
- Confidence 50-74%: Verify with Hunter.io before emailing (if credits available)

## Troubleshooting

**"Rate limit reached"**
→ Monthly credits exhausted, fallback to next source

**"No email found"**
→ All sources failed, pattern matching returned an email (50% confidence)

**"API key invalid"**
→ Check config.json, re-run `--setup`

## Upgrading (Optional)

If you need more volume:

**Skrapp.io paid tiers:**
- Starter: $49/mo (1,500 emails)
- Pro: $99/mo (5,000 emails)

**Hunter.io paid tiers:**
- Starter: $49/mo (500 searches, 1,000 verifications)
- Growth: $99/mo (2,500 searches, 5,000 verifications)

**Apollo.io paid tiers:**
- Basic: $49/mo (unlimited searches, 12,000 export credits/year)
- Professional: $99/mo (unlimited + advanced filters)

For Axlow's scale (100-250 leads/week), the **free tiers are sufficient** for the first few months.

---

**Next:** Run `python3 email_enrichment.py --setup` to configure your API keys.
