#!/usr/bin/env python3
"""
Friday 4pm CT — Check approval state, post to LinkedIn if approved.
If no response received, skip and notify.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "output" / "carousel_state.json"


def main():
    if not STATE_FILE.exists():
        print("No carousel state found — nothing to post.")
        return

    with open(STATE_FILE) as f:
        state = json.load(f)

    status = state.get("status")
    pdf_path = state.get("pdf_path")

    if status == "approved":
        print(f"✅ Approved — posting to LinkedIn: {pdf_path}")
        # LinkedIn poster will be wired here once OAuth is live
        poster = BASE_DIR / "linkedin_poster.py"
        if poster.exists():
            import subprocess
            result = subprocess.run(
                [sys.executable, str(poster), "--document", pdf_path,
                 "--caption", "This week in revenue cycle — top RCM signals leaders are watching. 👇 Swipe through.\n\n#RCM #RevenueCycle #MedicalBilling #HealthcareFinance"],
                capture_output=True, text=True
            )
            print(result.stdout)
            if result.returncode == 0:
                state["status"] = "posted"
                state["posted_at"] = datetime.now().isoformat()
            else:
                print(f"LinkedIn post failed: {result.stderr}")
                state["status"] = "post_failed"
        else:
            print("LinkedIn poster not yet configured — approval recorded, post skipped until OAuth is live.")
            state["status"] = "approved_pending_oauth"
    elif status == "skipped":
        print("⏭ Skipped by user — no post this week.")
    elif status == "pending":
        print("⏳ No response received by 4pm — auto-skipping this week.")
        state["status"] = "timeout_skipped"
    else:
        print(f"Unknown state: {status}")

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


if __name__ == "__main__":
    main()
