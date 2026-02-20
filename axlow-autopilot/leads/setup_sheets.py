#!/usr/bin/env python3
"""
One-time setup: Creates the Axlow Leads Master Google Sheet
and writes the Sheet ID to the config.
Run once after setting up Google service account credentials.
"""

import json
from pathlib import Path

WORKSPACE = Path(__file__).parent
CONFIG    = WORKSPACE / "config.json"

FIELDNAMES = [
    "first_name", "last_name", "email", "company", "title",
    "linkedin_url", "location", "company_type", "company_size",
    "icp_tier", "priority_score", "priority_level", "sequence",
    "personalization_line", "hook_angle", "email_source",
    "pain_signals", "company_context", "date_added", "date_verified",
    "status", "notes"
]

def setup(creds_path):
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds  = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)

    # Create spreadsheet
    sh = client.create("Axlow Leads Master")
    sh.share("shackletonbot@gmail.com", perm_type="user", role="writer")

    ws = sh.sheet1
    ws.update_title("All Leads")
    ws.append_row(FIELDNAMES)

    # Format header row
    ws.format("A1:V1", {
        "backgroundColor": {"red": 0.114, "green": 0.278, "blue": 0.251},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
    })
    ws.freeze(rows=1)

    # Save Sheet ID
    config = {}
    if CONFIG.exists():
        config = json.loads(CONFIG.read_text())
    config["sheet_id"] = sh.id
    config["sheet_url"] = sh.url
    CONFIG.write_text(json.dumps(config, indent=2))

    print(f"✅ Sheet created: {sh.url}")
    print(f"✅ Sheet ID saved to config.json: {sh.id}")
    return sh.id

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 setup_sheets.py /path/to/service_account.json")
        sys.exit(1)
    setup(sys.argv[1])
