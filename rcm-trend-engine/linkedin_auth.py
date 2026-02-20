#!/usr/bin/env python3
"""
LinkedIn OAuth flow — one-time setup to get access token
Run this once, authorize in browser, paste the code, get the token
"""

import sys
import json
import requests
from pathlib import Path
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

CLIENT_ID = "86tgxjfrv6of5b"
CLIENT_SECRET = "WPL_AP1.r1I5xKhlEnSETrE0.F4jpaA=="
REDIRECT_URI = "https://www.linkedin.com/developers/tools/oauth/redirect"
SCOPES = "w_organization_social"  # Company page posting permission

BASE_DIR = Path(__file__).parent
TOKEN_FILE = BASE_DIR / ".linkedin_token.json"


def step1_get_auth_url():
    """Generate the OAuth URL for the user to visit"""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    print("=" * 60)
    print("STEP 1: Authorize the app")
    print("=" * 60)
    print(f"\n1. Visit this URL:\n\n{auth_url}\n")
    print("2. Sign in with the LinkedIn account that owns the RevCycleAI company page")
    print("3. Click 'Allow'")
    print("4. You'll be redirected to a page with a 'code' in the URL")
    print("5. Copy everything after '?code=' and before '&state'")
    print("\n" + "=" * 60)


def step2_exchange_code(auth_code):
    """Exchange the authorization code for an access token"""
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code not in [200, 201]:
            print(f"\n❌ Token exchange failed: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        token_data = response.json()
        
        # Save token
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
        
        print("\n✅ Access token saved to:", TOKEN_FILE)
        print("\nToken expires in:", token_data.get("expires_in", "unknown"), "seconds")
        print("\n⚠️  LinkedIn tokens expire after 60 days. You'll need to re-run this script to refresh.")
        return token_data
    
    except Exception as e:
        print(f"\n❌ Token exchange failed: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        step1_get_auth_url()
        print("\nOnce you have the code, run:")
        print(f"  python3 {sys.argv[0]} YOUR_CODE_HERE\n")
    else:
        auth_code = sys.argv[1]
        print(f"\nExchanging code for token...")
        step2_exchange_code(auth_code)


if __name__ == "__main__":
    main()
