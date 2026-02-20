#!/usr/bin/env python3
"""
Parse starter_batch_100.md → batch_parsed.json → push to Google Sheets
"""

import re
import json
import sys
import os

# Add leads dir to path so we can import prospect.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prospect import push_to_sheets, append_to_master

DATE_ADDED = "2026-02-18"
FIELDNAMES = [
    "first_name", "last_name", "email", "company", "title",
    "linkedin_url", "location", "company_type", "company_size",
    "icp_tier", "priority_score", "priority_level", "sequence",
    "personalization_line", "hook_angle", "email_source",
    "pain_signals", "company_context", "date_added", "date_verified",
    "status", "notes"
]

MD_PATH = os.path.join(os.path.dirname(__file__), "starter_batch_100.md")
OUT_PATH = os.path.join(os.path.dirname(__file__), "batch_parsed.json")


def clean(s):
    return (s or "").strip()


def parse_field(block, label):
    """Extract single-line field from a block."""
    pattern = rf"^{re.escape(label)}:\s*(.+)$"
    m = re.search(pattern, block, re.MULTILINE)
    return clean(m.group(1)) if m else ""


def parse_multiline_field(block, label):
    """Extract the text after '- Label:' (may span to next bullet)."""
    pattern = rf"- {re.escape(label)}:\s*(.+?)(?=\n- |\Z)"
    m = re.search(pattern, block, re.DOTALL)
    return clean(m.group(1).replace("\n", " ")) if m else ""


def split_name(full_name_raw):
    """Split 'First Last' into (first, last). Handle ⚠️ verification notes."""
    fn = clean(full_name_raw)
    
    # If it contains the verification warning, names are unknown
    if "⚠️" in fn or "NEEDS MANUAL" in fn:
        return "", ""
    
    # Handle credentials like "Larry Benz, DPT"
    fn = re.sub(r",\s*\w+$", "", fn)
    
    parts = fn.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    # Last word is last name
    return " ".join(parts[:-1]), parts[-1]


def parse_sequence_letter(seq_raw):
    """Extract just the letter from 'A (The Time Saver)'."""
    m = re.match(r"([A-E])", clean(seq_raw))
    return m.group(1) if m else clean(seq_raw)


def parse_email(email_raw):
    """If 'LinkedIn Only', return empty string. Otherwise extract email."""
    er = clean(email_raw)
    if "linkedin only" in er.lower():
        return ""
    # Extract email from 'email@domain.com (Pattern Match...)'
    m = re.match(r"([^\s(]+@[^\s(]+)", er)
    return m.group(1) if m else ""


def parse_email_source(source_raw):
    """Strip 'Pattern Match - Unverified' suffix, return (source, notes)."""
    sr = clean(source_raw)
    notes = ""
    if "Pattern Match - Unverified" in sr:
        notes = "Pattern Match - Unverified"
        sr = sr.replace("Pattern Match - Unverified", "").strip(" -").strip()
        if not sr:
            sr = "Pattern Match"
    if "LinkedIn Only" in sr:
        sr = "LinkedIn Only"
    return sr, notes


def parse_linkedin(ln_raw):
    """Return confirmed LinkedIn URL or empty string."""
    lr = clean(ln_raw)
    # If it's a confirmed URL
    m = re.search(r"(https?://[^\s\[]+)", lr)
    if m:
        return m.group(1)
    return ""


def parse_prospects(md_text):
    """Split markdown into prospect blocks and parse each."""
    # Split on the separator line that precedes each PROSPECT heading
    # Each prospect block starts with the separator ━━━... PROSPECT #N
    # We split by the separator pattern
    separator = "━" * 38
    
    # Find all prospect blocks
    pattern = re.compile(
        r"━{38}\s*\nPROSPECT #(\d+).*?\n━{38}\s*\n(.*?)(?=━{38}\s*\nPROSPECT #|\Z)",
        re.DOTALL
    )
    
    prospects = []
    
    for match in pattern.finditer(md_text):
        num = int(match.group(1))
        block = match.group(2)
        
        # ── Basic fields ──────────────────────────────────────────────────────
        full_name_raw = parse_field(block, "Full Name")
        first, last = split_name(full_name_raw)
        
        title        = parse_field(block, "Title")
        # Clean "[to verify]" and "[title to verify via LinkedIn]" etc
        title = re.sub(r"\s*\[.*?\]", "", title).strip()
        
        company      = parse_field(block, "Company")
        company_type = parse_field(block, "Company Type")
        company_size = parse_field(block, "Company Size")
        location     = parse_field(block, "Location")
        
        linkedin_raw = parse_field(block, "LinkedIn URL")
        linkedin_url = parse_linkedin(linkedin_raw)
        
        email_raw    = parse_field(block, "Email")
        email        = parse_email(email_raw)
        
        source_raw   = parse_field(block, "Email Source")
        email_source, notes = parse_email_source(source_raw)
        
        icp_tier_raw     = parse_field(block, "ICP Tier")
        priority_score_r = parse_field(block, "Priority Score")
        priority_level   = parse_field(block, "Priority Level")
        
        try:
            icp_tier = int(icp_tier_raw)
        except:
            icp_tier = 1
        try:
            priority_score = int(priority_score_r)
        except:
            priority_score = 0
        
        # ── Sequence ─────────────────────────────────────────────────────────
        seq_raw = parse_field(block, "Sequence")
        sequence = parse_sequence_letter(seq_raw)
        
        # ── Personalization intel ─────────────────────────────────────────────
        pain_signals   = parse_multiline_field(block, "Pain Signals")
        company_context= parse_multiline_field(block, "Company Context")
        hook_angle     = parse_multiline_field(block, "Hook Angle")
        
        # Suggested Connection Request → personalization_line (first 200 chars)
        conn_req_raw   = parse_field(block, "Suggested Connection Request")
        personalization_line = conn_req_raw[:200] if conn_req_raw else ""
        
        lead = {
            "first_name":          first,
            "last_name":           last,
            "email":               email,
            "company":             company,
            "title":               title,
            "linkedin_url":        linkedin_url,
            "location":            location,
            "company_type":        company_type,
            "company_size":        company_size,
            "icp_tier":            icp_tier,
            "priority_score":      priority_score,
            "priority_level":      priority_level,
            "sequence":            sequence,
            "personalization_line": personalization_line,
            "hook_angle":          hook_angle[:300] if hook_angle else "",
            "email_source":        email_source,
            "pain_signals":        pain_signals[:150] if pain_signals else "",
            "company_context":     company_context[:150] if company_context else "",
            "date_added":          DATE_ADDED,
            "date_verified":       "",
            "status":              "new",
            "notes":               notes,
        }
        
        prospects.append(lead)
        print(f"  Parsed #{num}: {first} {last} @ {company} [{priority_level}]")
    
    return prospects


def main():
    print("📂 Reading starter_batch_100.md …")
    with open(MD_PATH, "r") as f:
        md_text = f.read()
    
    print("🔍 Parsing prospects …")
    leads = parse_prospects(md_text)
    print(f"\n✅ Parsed {len(leads)} prospects total.\n")
    
    # Save JSON
    with open(OUT_PATH, "w") as f:
        json.dump(leads, f, indent=2)
    print(f"💾 Saved to batch_parsed.json\n")
    
    # Push to Google Sheets
    print("📊 Pushing to Google Sheets …")
    push_to_sheets(leads)
    
    # Append to master CSV
    print("\n📁 Appending to master_leads.csv …")
    append_to_master(leads)
    print("✅ Done — master_leads.csv updated.\n")
    
    # Summary
    named = sum(1 for l in leads if l["first_name"])
    with_email = sum(1 for l in leads if l["email"])
    tier_counts = {}
    for l in leads:
        t = l["icp_tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1
    
    print("=" * 50)
    print(f"SUMMARY")
    print(f"  Total parsed:        {len(leads)}")
    print(f"  Named prospects:     {named}")
    print(f"  With email:          {with_email}")
    print(f"  LinkedIn Only:       {len(leads) - with_email}")
    for t in sorted(tier_counts):
        print(f"  ICP Tier {t}:          {tier_counts[t]}")
    print("=" * 50)


if __name__ == "__main__":
    main()
