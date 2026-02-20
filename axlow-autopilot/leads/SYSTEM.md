# Axlow Lead Hunter — Automated System

## Architecture

```
Every Monday 7:00 AM CT
        ↓
  Cron Job fires
        ↓
  Spawns research sub-agent
        ↓
  150-250 new prospects researched
  (Google X-ray + company mining + Hunter.io email lookup)
        ↓
  Deduplicated against master_leads.csv
        ↓
  New records appended to Google Sheet
        ↓
  Priority A leads → Immediate Telegram ping
        ↓
  Weekly summary report → Telegram (Monday ~9 AM)
```

## Files

- `master_leads.csv` — Master database, all leads ever found
- `weekly_YYYY-MM-DD.csv` — Each week's new batch
- `contacted_log.csv` — Leads already in active sequences (do not re-prospect)
- `SYSTEM.md` — This file

## Google Sheet

- Sheet Name: Axlow Leads Master
- Account: shackletonbot@gmail.com
- Sheet ID: [SET AFTER CREATION]
- Credentials: [SERVICE ACCOUNT JSON PATH]

## Hunter.io

- Account: shackletonbot@gmail.com
- API Key: [SET AFTER BROWSER LOGIN]
- Monthly budget: 25 lookups + 50 verifications
- Reset date: 1st of each month

## Cron Schedule

- **Weekly run:** Every Monday 7:00 AM CT
- **Target volume:** 150-250 new qualified prospects
- **Priority A ping:** Immediate on discovery
- **Summary report:** Delivered via Telegram same day

## Sequences

| Code | Name | Target |
|------|------|--------|
| A | The Time Saver | Tier 1 RCM Managers & Directors |
| B | The Denial Killer | Denial Management leaders |
| C | The Practice Efficiency Play | Tier 2 Practice Managers |
| D | The Multi-Client Multiplier | Tier 3 RCM companies |
| E | The Executive ROI | VPs and C-suite |
