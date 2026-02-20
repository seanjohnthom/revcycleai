#!/usr/bin/env python3
"""
Axlow RCM Lead Hunter — Weekly Prospecting Engine
Runs via cron every Monday 7 AM CT.
Produces 150-250 qualified, enriched RCM prospects per week.
"""

import os
import csv
import json
import time
import random
import requests
from datetime import datetime, date
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
WORKSPACE   = Path(__file__).parent
MASTER_CSV  = WORKSPACE / "master_leads.csv"
CONTACTED   = WORKSPACE / "contacted_log.csv"

# Load from config.json
_cfg = {}
_cfg_path = WORKSPACE / "config.json"
if _cfg_path.exists():
    _cfg = json.loads(_cfg_path.read_text())

HUNTER_KEY      = os.environ.get("HUNTER_API_KEY", _cfg.get("hunter_api_key", ""))
SHEET_ID        = os.environ.get("GOOGLE_SHEET_ID", _cfg.get("sheet_id", ""))
APPS_SCRIPT_URL = os.environ.get("APPS_SCRIPT_URL", _cfg.get("apps_script_url", ""))
SHEETS_CREDS    = os.environ.get("GOOGLE_SHEETS_CREDS", _cfg.get("service_account_json", ""))

TODAY       = date.today().isoformat()
WEEK_CSV    = WORKSPACE / f"weekly_{TODAY}.csv"

# ── CSV Schema ────────────────────────────────────────────────────────────────
FIELDNAMES = [
    "first_name", "last_name", "email", "company", "title",
    "linkedin_url", "location", "company_type", "company_size",
    "icp_tier", "priority_score", "priority_level", "sequence",
    "personalization_line", "hook_angle", "email_source",
    "pain_signals", "company_context", "date_added", "date_verified",
    "status", "notes"
]

# ── ICP Targets ───────────────────────────────────────────────────────────────
TIER1_TITLES = [
    "Revenue Cycle Manager", "RCM Director", "Revenue Cycle Director",
    "Billing Manager", "Denial Management Manager", "Denial Management Director",
    "VP Revenue Cycle", "VP of Revenue Cycle", "Director of Patient Financial Services",
    "Director Revenue Cycle"
]

TIER2_TITLES = [
    "Practice Manager", "Prior Authorization Manager", "Prior Auth Manager",
    "Credentialing Manager", "Coding Manager", "Coding Director",
    "AR Manager", "Accounts Receivable Manager", "CFO", "Controller"
]

TIER3_COMPANY_TYPES = [
    "medical billing company", "RCM company", "revenue cycle management company",
    "medical billing outsourcing", "healthcare billing services"
]

# ── Google X-ray Queries ──────────────────────────────────────────────────────
XRAY_QUERIES = [
    # Tier 1
    'site:linkedin.com/in "revenue cycle manager" "medical group"',
    'site:linkedin.com/in "revenue cycle manager" "health system"',
    'site:linkedin.com/in "RCM director" "hospital"',
    'site:linkedin.com/in "RCM director" "DSO"',
    'site:linkedin.com/in "billing manager" "dental"',
    'site:linkedin.com/in "billing manager" "medical group"',
    'site:linkedin.com/in "denial management" director',
    'site:linkedin.com/in "denial management manager"',
    'site:linkedin.com/in "VP revenue cycle"',
    'site:linkedin.com/in "director patient financial services"',
    # Tier 2
    'site:linkedin.com/in "practice manager" "dental group"',
    'site:linkedin.com/in "practice manager" "medical group"',
    'site:linkedin.com/in "prior authorization manager"',
    'site:linkedin.com/in "coding manager" "hospital"',
    'site:linkedin.com/in "AR manager" "healthcare"',
    # Tier 3
    'site:linkedin.com/in "revenue cycle" "billing company"',
    'site:linkedin.com/in "director" "medical billing" "outsourcing"',
    'site:linkedin.com/in "RCM" "billing services" director',
]

COMPANY_QUERIES = [
    # DSOs
    "largest dental service organizations United States 2024 list",
    "top DSO companies US revenue cycle leadership",
    # Health systems
    "largest health systems United States 2024 revenue cycle",
    # ASCs
    "largest ambulatory surgery center groups United States",
    "top ASC management companies revenue cycle",
    # PE-backed
    "PE backed healthcare platforms RCM revenue cycle",
    "private equity healthcare companies revenue cycle management",
    # RCM companies
    "top medical billing companies United States 2024",
    "largest RCM outsourcing companies healthcare US",
    # Multi-specialty
    "largest multi-specialty medical groups United States",
]


def load_existing_leads():
    """Load existing leads to deduplicate against."""
    existing_emails = set()
    existing_linkedin = set()
    if MASTER_CSV.exists():
        with open(MASTER_CSV) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("email"):
                    existing_emails.add(row["email"].lower())
                if row.get("linkedin_url"):
                    existing_linkedin.add(row["linkedin_url"].lower())
    return existing_emails, existing_linkedin


def is_duplicate(lead, existing_emails, existing_linkedin):
    email = (lead.get("email") or "").lower()
    linkedin = (lead.get("linkedin_url") or "").lower()
    if email and email in existing_emails:
        return True
    if linkedin and linkedin in existing_linkedin:
        return True
    return False


def calculate_priority(lead):
    score = 0
    title = (lead.get("title") or "").lower()
    company_type = (lead.get("company_type") or "").lower()
    pain_signals = (lead.get("pain_signals") or "").lower()

    if "revenue cycle" in title or "denial management" in title:
        score += 2
    if any(t in company_type for t in ["dso", "asc", "pe-backed"]):
        score += 1
    if "rcm company" in company_type or "billing company" in company_type:
        score += 2
    if "hiring" in pain_signals or "growing" in pain_signals:
        score += 1

    return min(score, 5)


def assign_sequence(lead):
    title = (lead.get("title") or "").lower()
    tier = lead.get("icp_tier", 1)
    company_type = (lead.get("company_type") or "").lower()

    if "denial" in title:
        return "B"
    if tier == 3 or "billing company" in company_type or "rcm company" in company_type:
        return "D"
    if "vp" in title or "cfo" in title or "controller" in title:
        return "E"
    if tier == 2:
        return "C"
    return "A"


def hunter_domain_search(domain):
    """Use Hunter.io API to find email pattern for a domain."""
    if not HUNTER_KEY:
        return None, None
    try:
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_KEY}&limit=5"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("data"):
            pattern = data["data"].get("pattern")
            emails = data["data"].get("emails", [])
            return pattern, emails
    except Exception as e:
        print(f"Hunter API error: {e}")
    return None, None


def hunter_email_finder(first_name, last_name, domain):
    """Use Hunter.io to find and verify a specific email."""
    if not HUNTER_KEY:
        return None, "no_api_key"
    try:
        url = (f"https://api.hunter.io/v2/email-finder"
               f"?domain={domain}&first_name={first_name}&last_name={last_name}"
               f"&api_key={HUNTER_KEY}")
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("data", {}).get("email"):
            email = data["data"]["email"]
            conf  = data["data"].get("confidence", 0)
            return email, f"Hunter.io ({conf}% confidence)"
    except Exception as e:
        print(f"Hunter finder error: {e}")
    return None, "Hunter lookup failed"


def construct_email(first, last, pattern, domain):
    """Construct email from known pattern."""
    if not pattern or not domain:
        return None
    first = first.lower().replace(" ", "")
    last  = last.lower().replace(" ", "")
    templates = {
        "{first}.{last}": f"{first}.{last}@{domain}",
        "{first}":        f"{first}@{domain}",
        "{f}{last}":      f"{first[0]}{last}@{domain}",
        "{first}{last}":  f"{first}{last}@{domain}",
        "{first}_{last}": f"{first}_{last}@{domain}",
    }
    return templates.get(pattern, f"{first}.{last}@{domain}")


def append_to_master(leads):
    """Append new leads to master CSV."""
    write_header = not MASTER_CSV.exists()
    with open(MASTER_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        for lead in leads:
            writer.writerow({k: lead.get(k, "") for k in FIELDNAMES})


def write_weekly_batch(leads):
    """Write this week's batch to its own CSV."""
    with open(WEEK_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for lead in leads:
            writer.writerow({k: lead.get(k, "") for k in FIELDNAMES})
    print(f"Weekly batch saved: {WEEK_CSV}")


def push_to_sheets(leads):
    """Push new leads to Google Sheet via Apps Script webhook (no credentials needed)."""
    if not APPS_SCRIPT_URL:
        print("⚠️  No Apps Script URL configured. Leads saved locally only.")
        return

    pushed = 0
    failed = 0
    for lead in leads:
        try:
            payload = {k: lead.get(k, "") for k in FIELDNAMES}
            r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=15)
            data = r.json()
            if data.get("ok"):
                pushed += 1
            else:
                print(f"  Sheet error for {lead.get('email','?')}: {data}")
                failed += 1
        except Exception as e:
            print(f"  Push failed for {lead.get('email','?')}: {e}")
            failed += 1
        time.sleep(0.3)  # be gentle with the webhook

    print(f"✅ Pushed {pushed} leads to Google Sheets. Failed: {failed}")


def test_sheet_connection():
    """Ping the Apps Script to confirm the webhook is live."""
    if not APPS_SCRIPT_URL:
        print("❌ No APPS_SCRIPT_URL in config.json")
        return False
    try:
        r = requests.get(APPS_SCRIPT_URL, timeout=10)
        data = r.json()
        if data.get("ok"):
            print(f"✅ Sheet webhook live: {data.get('status')}")
            return True
        else:
            print(f"❌ Unexpected response: {data}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def generate_weekly_report(new_leads, priority_a):
    tier_counts = {1: 0, 2: 0, 3: 0}
    email_count = 0
    states      = set()
    sequences   = {}

    for lead in new_leads:
        tier = lead.get("icp_tier", 1)
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        if lead.get("email") and lead["email"] != "LinkedIn Only":
            email_count += 1
        loc = lead.get("location", "")
        if "," in loc:
            states.add(loc.split(",")[-1].strip())
        seq = lead.get("sequence", "")
        sequences[seq] = sequences.get(seq, 0) + 1

    email_pct = round(email_count / len(new_leads) * 100) if new_leads else 0

    report = f"""
🎯 *Axlow Lead Hunter — Weekly Report*
📅 {TODAY}

*New Prospects Added:* {len(new_leads)}
├ Tier 1 (Primary): {tier_counts.get(1, 0)}
├ Tier 2 (Secondary): {tier_counts.get(2, 0)}
└ Tier 3 (RCM Companies): {tier_counts.get(3, 0)}

*Email Coverage:* {email_pct}% ({email_count}/{len(new_leads)} verified)

*States Covered:* {len(states)} ({', '.join(sorted(states)[:8])}{'...' if len(states) > 8 else ''})

*Sequence Assignments:*
{chr(10).join(f'├ Seq {k}: {v} prospects' for k,v in sorted(sequences.items()))}

*🔥 Priority A Hot Signals: {len(priority_a)}*
{chr(10).join(f'• {p.get("first_name")} {p.get("last_name")} @ {p.get("company")} — {p.get("hook_angle", "")}' for p in priority_a[:5])}

_Next run: Monday {TODAY}_
    """.strip()

    return report


if __name__ == "__main__":
    print(f"[{datetime.now()}] Axlow Lead Hunter starting weekly run...")

    existing_emails, existing_linkedin = load_existing_leads()
    print(f"Loaded {len(existing_emails)} existing leads for deduplication.")

    # NOTE: Actual web research is handled by the AI sub-agent.
    # This script handles: deduplication, email enrichment via Hunter.io,
    # CSV writing, Google Sheets push, and report generation.
    # The sub-agent calls this script's functions directly or passes lead data via JSON.

    print("Script ready. Sub-agent will call enrichment functions directly.")
    print(f"Hunter API: {'configured' if HUNTER_KEY else 'NOT SET - set HUNTER_API_KEY env var'}")
    print(f"Sheets: {'configured' if SHEET_ID else 'NOT SET - run setup_sheets.py first'}")
