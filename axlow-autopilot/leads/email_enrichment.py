#!/usr/bin/env python3
"""
Multi-source email lookup with fallback chain
Hunter.io → Skrapp.io → Apollo.io → Pattern matching
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict

CONFIG_FILE = Path(__file__).parent / "config.json"


def load_config() -> dict:
    """Load API keys from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save config.json"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def hunter_io_lookup(first_name: str, last_name: str, company_domain: str, api_key: str) -> Optional[Dict]:
    """
    Hunter.io email finder
    Free tier: 25 searches/month, 50 verifications/month
    """
    if not api_key:
        return None
    
    try:
        url = "https://api.hunter.io/v2/email-finder"
        params = {
            "domain": company_domain,
            "first_name": first_name,
            "last_name": last_name,
            "api_key": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("email"):
                return {
                    "email": data["data"]["email"],
                    "confidence": data["data"].get("score", 0),
                    "source": "hunter.io"
                }
        elif response.status_code == 429:
            print("  [Hunter.io] Rate limit reached")
        
    except Exception as e:
        print(f"  [Hunter.io] Error: {e}")
    
    return None


def apollo_io_lookup(first_name: str, last_name: str, company_name: str, company_domain: str, api_key: str) -> Optional[Dict]:
    """
    Apollo.io people search
    Free tier: 60 email credits/month
    """
    if not api_key:
        return None
    
    try:
        url = "https://api.apollo.io/v1/people/match"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": api_key
        }
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "organization_name": company_name,
            "domain": company_domain
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            person = data.get("person", {})
            email = person.get("email")
            
            if email:
                return {
                    "email": email,
                    "confidence": 85,  # Apollo doesn't provide confidence scores
                    "source": "apollo.io"
                }
        elif response.status_code == 429:
            print("  [Apollo.io] Rate limit reached")
        
    except Exception as e:
        print(f"  [Apollo.io] Error: {e}")
    
    return None


def skrapp_io_lookup(first_name: str, last_name: str, company_domain: str, api_key: str) -> Optional[Dict]:
    """
    Skrapp.io email finder
    Free tier: 150 emails/month
    """
    if not api_key:
        return None
    
    try:
        url = "https://api.skrapp.io/api/v2/find"
        headers = {
            "X-Access-Token": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "domain": company_domain
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("email"):
                return {
                    "email": data["email"],
                    "confidence": data.get("confidence", 75),
                    "source": "skrapp.io"
                }
        elif response.status_code == 429:
            print("  [Skrapp.io] Rate limit reached")
        
    except Exception as e:
        print(f"  [Skrapp.io] Error: {e}")
    
    return None


def pattern_match_email(first_name: str, last_name: str, company_domain: str) -> Optional[Dict]:
    """
    Pattern-based email guessing
    Common patterns: firstname@domain, firstnamelastname@domain, f.lastname@domain
    Returns most likely pattern (no verification)
    """
    if not company_domain or not first_name or not last_name:
        return None
    
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    domain = company_domain.lower().strip()
    
    # Common patterns (ordered by frequency in B2B)
    patterns = [
        f"{first}.{last}@{domain}",       # firstname.lastname@ (most common)
        f"{first}{last}@{domain}",        # firstnamelastname@
        f"{first[0]}{last}@{domain}",     # flastname@
        f"{first}@{domain}",              # firstname@
        f"{first[0]}.{last}@{domain}",    # f.lastname@
    ]
    
    # Return first pattern (most likely)
    return {
        "email": patterns[0],
        "confidence": 50,  # Pattern match = 50% confidence
        "source": "pattern_match",
        "alternatives": patterns[1:]  # Include other possibilities
    }


def find_email(first_name: str, last_name: str, company_name: str, company_domain: str, 
               verbose: bool = True) -> Optional[Dict]:
    """
    Multi-source email lookup with fallback chain
    
    Returns dict with:
        - email: str
        - confidence: int (0-100)
        - source: str (hunter.io, apollo.io, skrapp.io, pattern_match)
        - alternatives: list (optional, for pattern matching)
    """
    config = load_config()
    
    # Extract API keys
    hunter_key = config.get("hunter_api_key")
    apollo_key = config.get("apollo_api_key")
    skrapp_key = config.get("skrapp_api_key")
    
    if verbose:
        print(f"  Looking up: {first_name} {last_name} @ {company_domain}")
    
    # Fallback chain
    sources = [
        ("Hunter.io", lambda: hunter_io_lookup(first_name, last_name, company_domain, hunter_key)),
        ("Skrapp.io", lambda: skrapp_io_lookup(first_name, last_name, company_domain, skrapp_key)),
        ("Apollo.io", lambda: apollo_io_lookup(first_name, last_name, company_name, company_domain, apollo_key)),
        ("Pattern", lambda: pattern_match_email(first_name, last_name, company_domain)),
    ]
    
    for source_name, lookup_func in sources:
        try:
            result = lookup_func()
            if result and result.get("email"):
                if verbose:
                    print(f"  ✓ Found via {source_name}: {result['email']} (confidence: {result['confidence']}%)")
                return result
        except Exception as e:
            if verbose:
                print(f"  [WARN] {source_name} failed: {e}")
            continue
    
    if verbose:
        print(f"  ✗ No email found for {first_name} {last_name}")
    
    return None


def verify_email(email: str, api_key: str = None) -> Dict:
    """
    Verify email deliverability using Hunter.io
    Free tier: 50 verifications/month
    
    Returns:
        - valid: bool
        - result: str (deliverable, risky, undeliverable)
        - score: int (0-100)
    """
    config = load_config()
    hunter_key = api_key or config.get("hunter_api_key")
    
    if not hunter_key:
        return {"valid": None, "result": "unknown", "score": 0}
    
    try:
        url = "https://api.hunter.io/v2/email-verifier"
        params = {
            "email": email,
            "api_key": hunter_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            return {
                "valid": data.get("status") == "valid",
                "result": data.get("result", "unknown"),
                "score": data.get("score", 0)
            }
    except Exception as e:
        print(f"  [Email Verify] Error: {e}")
    
    return {"valid": None, "result": "unknown", "score": 0}


def setup_api_keys():
    """Interactive setup for API keys"""
    print("\n" + "=" * 60)
    print("Email Enrichment API Key Setup")
    print("=" * 60)
    
    config = load_config()
    
    print("\n📧 Hunter.io (25 searches/mo, 50 verifications/mo)")
    print("   Get key: https://hunter.io/api-keys")
    hunter = input("   Hunter.io API key (or press Enter to skip): ").strip()
    if hunter:
        config["hunter_api_key"] = hunter
    
    print("\n📧 Skrapp.io (150 emails/mo — BEST FREE TIER)")
    print("   Get key: https://www.skrapp.io/dashboard/api")
    skrapp = input("   Skrapp.io API key (or press Enter to skip): ").strip()
    if skrapp:
        config["skrapp_api_key"] = skrapp
    
    print("\n📧 Apollo.io (60 credits/mo)")
    print("   Get key: https://app.apollo.io/#/settings/integrations/api")
    apollo = input("   Apollo.io API key (or press Enter to skip): ").strip()
    if apollo:
        config["apollo_api_key"] = apollo
    
    save_config(config)
    
    print("\n✅ API keys saved to config.json")
    print("\nFallback chain: Hunter.io → Skrapp.io → Apollo.io → Pattern matching")
    print("Total free lookups: 235/month + unlimited pattern matching\n")


if __name__ == "__main__":
    import sys
    
    if "--setup" in sys.argv:
        setup_api_keys()
    else:
        # Test lookup
        result = find_email(
            first_name="John",
            last_name="Smith",
            company_name="Acme Billing",
            company_domain="acmebilling.com",
            verbose=True
        )
        
        if result:
            print(f"\n✅ Result: {result}")
        else:
            print("\n❌ No email found")
