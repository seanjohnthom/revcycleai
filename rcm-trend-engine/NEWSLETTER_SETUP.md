# RevCycleAI Newsletter Setup Guide

## What's Built

✅ **Automated newsletter composer** (`newsletter_builder.py`)
- Pulls top 5 trends from past 7 days
- Generates clean HTML email with cover story + developing stories
- Includes free resources CTA and house ads (Axlow/PayorMap)
- Sends via MailerLite API

✅ **Tuesday 7am CT cron job** (ID: `4e65e54f-86c4-48cc-800c-eaf9e2a99171`)
- Runs every Tuesday at 7:00 AM Central
- Auto-generates and sends newsletter
- Next run: Check with `/status` or `cron list`

## Before First Send

### 1. Verify sender email in MailerLite

The newsletter sends from `newsletter@revcycleai.com`. You need to verify this in MailerLite:

1. Go to MailerLite dashboard → Settings → Domains & Emails
2. Add `newsletter@revcycleai.com` as a verified sender
3. Follow their verification steps (usually DNS TXT record)

**Alternative:** Change `FROM_EMAIL` in `newsletter_builder.py` to an already-verified email.

### 2. Test with preview mode

```bash
cd /Users/shackleton/.openclaw/workspace/rcm-trend-engine
python3 newsletter_builder.py --preview
```

This generates `newsletter_preview.html` — open it in your browser to review the design and content before sending.

### 3. Manual test send

Once `newsletter@revcycleai.com` is verified, do a test send:

```bash
python3 newsletter_builder.py
```

This will send immediately to your entire subscriber list (or the group specified in `MAILERLITE_GROUP_ID`).

**Pro tip:** Create a "Test" group in MailerLite with just your email, set `MAILERLITE_GROUP_ID` to that group's ID, and test there first.

## Environment Variables

The script needs these env vars (already set in your OpenClaw env):

- `MAILERLITE_API_KEY` — MailerLite API key
- `MAILERLITE_GROUP_ID` — (Optional) Target a specific group; leave unset to send to all subscribers

## How It Works

1. **Tuesday 7am CT**: Cron fires
2. Script loads `data/trends.json` (populated by daily RCM Trend Engine scan at 6am)
3. Picks top 5 trends by score from past 7 days
4. Generates HTML email:
   - Cover story (highest score trend)
   - 3 developing stories
   - Free resources CTA
   - Axlow + PayorMap house ads
5. Sends via MailerLite API
6. Confirms send in Telegram (if cron notify enabled)

## Customization

### Subject lines

Edit `SUBJECT_TEMPLATES` in `newsletter_builder.py`:

```python
SUBJECT_TEMPLATES = [
    "The 3 RCM signals you can't miss this week",
    "What changed in revenue cycle this week (and what to do)",
    # Add your own...
]
```

The script uses the first template by default. You can rotate or randomize if you want.

### HTML styling

All CSS is inline in `generate_html_newsletter()` function. Modify colors, fonts, spacing there.

### Content structure

Current structure:
1. Header (logo, date)
2. Cover story (urgent/high-priority)
3. Developing stories (3-4 items)
4. Free resources CTA
5. House ads (Axlow, PayorMap)
6. Footer (links, unsubscribe)

Change sections in the `generate_html_newsletter()` function.

## Monitoring

- Check MailerLite dashboard for open rates, click rates
- Cron will post to Telegram when newsletter sends (if `notify: true` in cron job)

## Troubleshooting

**"FROM_EMAIL not verified"**
→ Verify `newsletter@revcycleai.com` in MailerLite first

**"No trends found"**
→ Run the RCM Trend Engine daily scan: `python3 trend_monitor.py`

**"Campaign creation failed"**
→ Check MAILERLITE_API_KEY is set correctly

## Manual Override

If you want to skip the automated send one week:

```bash
# Disable the cron
cron update --jobId 4e65e54f-86c4-48cc-800c-eaf9e2a99171 --patch '{"enabled": false}'

# Re-enable when ready
cron update --jobId 4e65e54f-86c4-48cc-800c-eaf9e2a99171 --patch '{"enabled": true}'
```

Or just manually send whenever you want:

```bash
cd /Users/shackleton/.openclaw/workspace/rcm-trend-engine
python3 newsletter_builder.py
```

---

**Next step:** Verify `newsletter@revcycleai.com` in MailerLite, then run a `--preview` test.
