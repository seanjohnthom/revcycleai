#!/usr/bin/env python3
"""
Generate personalization_line for every lead using hook_angle + pain_signals.
Uses Claude API directly (or a simple rule-based approach from existing data).
Saves updated batch_parsed.json and pushes to Google Sheet.
"""
import json, re, sys
from pathlib import Path
import urllib.request, urllib.error

DATA   = Path(__file__).parent / 'batch_parsed.json'
OUTPUT = Path(__file__).parent / 'batch_parsed.json'

def clean_hook(hook: str) -> str:
    """Strip the 'OUTREACH:' trailer and clean up the hook angle into a 1-2 sentence personalization."""
    hook = re.sub(r'\s*OUTREACH:.*$', '', hook, flags=re.IGNORECASE|re.DOTALL).strip()
    hook = re.sub(r'\s+', ' ', hook)
    # Trim to ~200 chars naturally at sentence boundary
    if len(hook) <= 200:
        return hook
    # Find last sentence end within 220 chars
    truncated = hook[:220]
    last_period = max(truncated.rfind('. '), truncated.rfind('! '), truncated.rfind('? '))
    if last_period > 100:
        return truncated[:last_period+1]
    return truncated.rstrip(',.;:') + '.'


def build_personalization(lead: dict) -> str:
    """Build a natural 1-2 sentence personalization line from available data."""
    hook  = lead.get('hook_angle', '').strip()
    pain  = lead.get('pain_signals', '').strip()
    first = lead.get('first_name', '')
    title = lead.get('title', '')
    co    = lead.get('company', '')

    # If hook_angle has real content, clean and use it
    if hook and len(hook) > 30:
        return clean_hook(hook)

    # Fallback: build from pain_signals
    if pain and len(pain) > 30:
        pain_clean = pain[:180].rstrip(',.;:')
        return f"Saw that {co} is navigating {pain_clean.lower()}—thought Axlow might be worth 2 minutes of your time."

    # Last resort: title-based generic (still better than blank)
    return f"With a role like {title} at {co}, payor policy lookups are probably eating more of your team's day than they should."


def push_to_sheets(leads: list) -> bool:
    """Push updated personalization_lines to Google Sheet via Apps Script webhook."""
    WEBHOOK = "https://script.google.com/macros/s/AKfycbx7fO1oK2khO2s9cXQ5jjQmzafiHYw05f6nF3JPqJEeKFipkWWzm2kf7w_ghzKDnnvf/exec"
    rows = []
    for l in leads:
        rows.append({
            "email":                l.get("email",""),
            "personalization_line": l.get("personalization_line",""),
        })
    payload = json.dumps({"action": "update_personalization", "rows": rows}).encode()
    req = urllib.request.Request(WEBHOOK, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode()
            print(f"Sheet response: {body[:120]}")
            return True
    except Exception as e:
        print(f"Sheet push failed (non-fatal): {e}", file=sys.stderr)
        return False


def main():
    leads = json.loads(DATA.read_text())
    updated = 0
    for lead in leads:
        current = lead.get('personalization_line', '').strip()
        if not current:
            lead['personalization_line'] = build_personalization(lead)
            updated += 1

    OUTPUT.write_text(json.dumps(leads, indent=2))
    print(f"Generated personalization for {updated}/{len(leads)} leads.")
    print()

    # Print sample
    for l in leads[:5]:
        print(f"  {l['first_name']} {l['last_name']} @ {l['company']}")
        print(f"  → {l['personalization_line']}")
        print()

    # Push to sheets
    print("Pushing to Google Sheet...")
    push_to_sheets(leads)


if __name__ == '__main__':
    main()
