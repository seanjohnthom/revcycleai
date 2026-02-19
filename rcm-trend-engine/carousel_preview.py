#!/usr/bin/env python3
"""
Friday 10am CT — Generate carousel, send Telegram preview with approve/skip buttons.
Saves approval state to output/carousel_state.json
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "output" / "carousel_state.json"

def main():
    # Generate the carousel
    sys.path.insert(0, str(BASE_DIR))
    from engine.weekly_carousel import build_weekly_carousel

    print("Generating weekly carousel...")
    pdf_path = build_weekly_carousel()
    print(f"PDF ready: {pdf_path}")

    # Save pending state
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "status": "pending",
        "pdf_path": pdf_path,
        "generated_at": datetime.now().isoformat(),
        "week": datetime.now().strftime("Week of %B %-d, %Y"),
        "approved_at": None
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"State saved: {STATE_FILE}")
    print(f"CAROUSEL_PDF={pdf_path}")
    print(f"CAROUSEL_STATE=pending")


if __name__ == "__main__":
    main()
