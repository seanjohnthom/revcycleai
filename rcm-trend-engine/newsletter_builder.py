#!/usr/bin/env python3
"""
RevCycleAI Newsletter Builder
Generates and sends the weekly "This Week in RCM" newsletter via MailerLite
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
TRENDS_FILE = BASE_DIR / "data" / "trends.json"
MAILERLITE_API_KEY = os.getenv("MAILERLITE_API_KEY")
MAILERLITE_GROUP_ID = os.getenv("MAILERLITE_GROUP_ID")  # Optional: target specific group

# Newsletter config
NEWSLETTER_NAME = "This Week in RCM"
FROM_NAME = "RevCycleAI"
FROM_EMAIL = "newsletter@revcycleai.com"  # Must be verified in MailerLite
SUBJECT_TEMPLATES = [
    "The 3 RCM signals you can't miss this week",
    "What changed in revenue cycle this week (and what to do)",
    "This week's RCM intelligence — {date}",
    "3 RCM moves for your week ahead",
]


def load_recent_trends(days=7):
    """Load trends from the past N days"""
    if not TRENDS_FILE.exists():
        print("❌ No trends.json found. Run trend_monitor.py first.")
        sys.exit(1)
    
    with open(TRENDS_FILE) as f:
        all_trends = json.load(f)
    
    cutoff = datetime.now() - timedelta(days=days)
    recent = [
        t for t in all_trends 
        if datetime.fromisoformat(t.get("detected_at", "2020-01-01")) > cutoff
    ]
    
    # Sort by score (highest first)
    recent.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return recent[:5]  # Top 5 trends


def generate_html_newsletter(trends):
    """Generate HTML email from trends"""
    
    if not trends:
        print("❌ No trends found for newsletter generation")
        sys.exit(1)
    
    # Pick cover story (highest score)
    cover = trends[0]
    developing = trends[1:4] if len(trends) > 1 else []
    
    # Build HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #FAFAFA; }}
  .container {{ max-width: 600px; margin: 0 auto; background: #fff; }}
  .header {{ background: #09090B; color: #fff; padding: 32px 24px; text-align: center; }}
  .header .wordmark {{ display: inline-flex; align-items: center; gap: 0; margin-bottom: 8px; }}
  .header .wordmark-text {{ font-size: 24px; font-weight: 800; color: #fff; letter-spacing: -0.5px; }}
  .header .wordmark-text span {{ font-weight: 400; }}
  .header .wordmark-ai {{ display: inline-block; background: #1D4ED8; color: #fff; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 4px; margin-left: 6px; letter-spacing: 0.5px; vertical-align: middle; }}
  .header h1 {{ margin: 0; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }}
  .header p {{ margin: 8px 0 0; font-size: 13px; color: #A1A1AA; }}
  .content {{ padding: 32px 24px; }}
  .cover-story {{ margin-bottom: 32px; padding-bottom: 32px; border-bottom: 2px solid #E4E4E7; }}
  .cover-story .label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #DC2626; margin-bottom: 12px; }}
  .cover-story h2 {{ font-size: 22px; font-weight: 800; line-height: 1.3; margin: 0 0 12px; color: #09090B; }}
  .cover-story p {{ font-size: 15px; line-height: 1.6; color: #52525B; margin: 0 0 16px; }}
  .cover-story a {{ display: inline-block; background: #1D4ED8; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 14px; }}
  .developing {{ margin-bottom: 32px; }}
  .developing h3 {{ font-size: 16px; font-weight: 700; margin: 0 0 16px; color: #09090B; text-transform: uppercase; letter-spacing: 0.5px; }}
  .story {{ margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #E4E4E7; }}
  .story:last-child {{ border-bottom: none; }}
  .story .urgency {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
  .story .urgency.high {{ color: #DC2626; }}
  .story .urgency.medium {{ color: #F59E0B; }}
  .story .urgency.low {{ color: #16A34A; }}
  .story h4 {{ font-size: 15px; font-weight: 700; line-height: 1.4; margin: 0 0 6px; color: #09090B; }}
  .story p {{ font-size: 13px; line-height: 1.5; color: #52525B; margin: 0; }}
  .cta-block {{ background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border: 2px solid #1D4ED8; border-radius: 8px; padding: 24px; margin: 32px 0; text-align: center; }}
  .cta-block h4 {{ font-size: 18px; font-weight: 800; color: #1D4ED8; margin: 0 0 12px; }}
  .cta-block p {{ font-size: 14px; color: #52525B; margin: 0 0 16px; line-height: 1.5; }}
  .cta-block a {{ display: inline-block; background: #1D4ED8; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 14px; }}
  .pro-cta {{ background: #09090B; border-radius: 8px; padding: 28px 24px; margin: 32px 0; text-align: center; color: #fff; }}
  .pro-cta h4 {{ font-size: 20px; font-weight: 800; color: #fff; margin: 0 0 8px; }}
  .pro-cta .badge {{ display: inline-block; background: #1D4ED8; color: #fff; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 4px; margin-bottom: 16px; letter-spacing: 0.5px; text-transform: uppercase; }}
  .pro-cta p {{ font-size: 15px; color: #A1A1AA; margin: 0 0 20px; line-height: 1.6; }}
  .pro-cta ul {{ list-style: none; padding: 0; margin: 0 0 24px; text-align: left; max-width: 400px; margin-left: auto; margin-right: auto; }}
  .pro-cta ul li {{ font-size: 14px; color: #D4D4D8; padding: 8px 0; border-bottom: 1px solid #27272A; }}
  .pro-cta ul li:last-child {{ border-bottom: none; }}
  .pro-cta ul li::before {{ content: "✓"; color: #16A34A; font-weight: 700; margin-right: 10px; }}
  .pro-cta a {{ display: inline-block; background: #1D4ED8; color: #fff; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 15px; }}
  .pro-cta .price {{ font-size: 13px; color: #71717A; margin-top: 12px; }}
  .house-ads {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 32px 0; }}
  .ad {{ background: #fff; border: 2px solid #E4E4E7; border-radius: 8px; padding: 20px; text-align: center; }}
  .ad .sponsor-label {{ font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #A1A1AA; margin-bottom: 12px; }}
  .ad h5 {{ font-size: 16px; font-weight: 800; margin: 0 0 8px; color: #09090B; }}
  .ad p {{ font-size: 13px; color: #52525B; margin: 0 0 16px; line-height: 1.5; }}
  .ad a {{ display: inline-block; background: #1D4ED8; color: #fff; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 13px; }}
  .ad.axlow {{ border-color: #3B82F6; }}
  .ad.payormap {{ border-color: #10B981; }}
  .ad.axlow a {{ background: #3B82F6; }}
  .ad.payormap a {{ background: #10B981; }}
  .advertise-cta {{ text-align: center; margin: 20px 0 0; padding-top: 20px; border-top: 1px solid #E4E4E7; }}
  .advertise-cta p {{ font-size: 12px; color: #71717A; margin: 0 0 8px; }}
  .advertise-cta a {{ color: #1D4ED8; text-decoration: none; font-weight: 600; font-size: 13px; }}
  .advertise-cta a:hover {{ text-decoration: underline; }}
  .footer {{ background: #09090B; color: #71717A; padding: 24px; text-align: center; font-size: 12px; line-height: 1.6; }}
  .footer a {{ color: #A1A1AA; text-decoration: none; }}
  @media (max-width: 600px) {{
    .house-ads {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="container">
  <!-- Header -->
  <div class="header">
    <div class="wordmark">
      <span class="wordmark-text">Rev<span>Cycle</span></span>
      <span class="wordmark-ai">AI</span>
    </div>
    <h1>📧 This Week in RCM</h1>
    <p>{datetime.now().strftime("%B %d, %Y")}</p>
  </div>

  <!-- Content -->
  <div class="content">
    <!-- Cover Story -->
    <div class="cover-story">
      <div class="label">🔴 Cover Story</div>
      <h2>{cover.get('title', 'No title')}</h2>
      <p>{cover.get('summary', cover.get('description', 'No summary available'))}</p>
      <a href="https://revcycleai.com/blog">Read the full analysis →</a>
    </div>

    <!-- Developing Stories -->
    <div class="developing">
      <h3>Also Developing</h3>
"""

    # Add developing stories
    for story in developing:
        urgency = story.get('urgency', 'low')
        urgency_label = {
            'immediate': 'high',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }.get(urgency, 'low')
        
        urgency_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(urgency_label, '🟢')
        
        html += f"""
      <div class="story">
        <div class="urgency {urgency_label}">{urgency_emoji} {story.get('category', 'General').title()}</div>
        <h4>{story.get('title', 'No title')}</h4>
        <p>{story.get('summary', story.get('description', 'No summary available'))[:150]}...</p>
      </div>
"""

    # CTA block
    html += """
    </div>

    <!-- Pro CTA -->
    <div class="pro-cta">
      <div class="badge">RevCycleAI Pro</div>
      <h4>⭐ Go deeper with premium RCM tools</h4>
      <p>Advanced analytics, carve-out opportunity scanner, full resource library, and premium industry reports.</p>
      <ul>
        <li>Advanced denial benchmarking by payor</li>
        <li>Carve-out opportunity scanner (network stacking analysis)</li>
        <li>Full resource library (100+ templates, checklists, calculators)</li>
        <li>Premium weekly reports with actionable insights</li>
      </ul>
      <a href="https://revcycleai.com/pro">See pricing →</a>
      <p class="price">$29/mo · Founding member rate locked forever</p>
    </div>

    <!-- Free Resources CTA -->
    <div class="cta-block">
      <h4>📋 Get the Free Resources</h4>
      <p>Prior auth checklists, denial appeal templates, PPO network maps, and more — all free downloads.</p>
      <a href="https://revcycleai.com/free">Browse free resources →</a>
    </div>

    <!-- House Ads -->
    <div class="house-ads">
      <div class="ad axlow">
        <div class="sponsor-label">Sponsored</div>
        <h5>Axlow</h5>
        <p>Instant payor policy search. Find prior auth requirements in seconds, not hours.</p>
        <a href="https://axlow.com">Try Axlow →</a>
      </div>
      <div class="ad payormap">
        <div class="sponsor-label">Sponsored</div>
        <h5>PayorMap</h5>
        <p>DSO claim routing intelligence. Avoid umbrella network repricing leaks before they hit your AR.</p>
        <a href="https://payormap.com">See PayorMap →</a>
      </div>
    </div>
    
    <!-- Advertise CTA -->
    <div class="advertise-cta">
      <p>Reach RCM professionals and billing decision-makers</p>
      <a href="https://revcycleai.com/advertise">Advertise in this newsletter →</a>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <p><strong>RevCycleAI</strong><br>RCM intelligence for billing teams, directors, and DSO operators.</p>
    <p style="margin-top: 12px;">
      <a href="https://revcycleai.com">revcycleai.com</a> · 
      <a href="https://revcycleai.com/blog">Intelligence</a> · 
      <a href="https://revcycleai.com/tools">Tools</a>
    </p>
    <p style="margin-top: 12px; font-size: 11px;">
      You're receiving this because you subscribed at revcycleai.com<br>
      <a href="{$unsubscribe}">Unsubscribe</a>
    </p>
  </div>
</div>
</body>
</html>
"""
    
    return html


def send_newsletter(html_content, subject=None):
    """Send newsletter via MailerLite API"""
    
    if not MAILERLITE_API_KEY:
        print("❌ MAILERLITE_API_KEY not set in environment")
        sys.exit(1)
    
    # Generate subject if not provided
    if not subject:
        subject = SUBJECT_TEMPLATES[0]  # Use first template
        subject = subject.replace("{date}", datetime.now().strftime("%b %d"))
    
    # Create campaign
    campaign_payload = {
        "name": f"{NEWSLETTER_NAME} — {datetime.now().strftime('%Y-%m-%d')}",
        "type": "regular",
        "emails": [
            {
                "subject": subject,
                "from_name": FROM_NAME,
                "from": FROM_EMAIL,
                "content": html_content
            }
        ]
    }
    
    # If group ID specified, target that group; otherwise send to all subscribers
    if MAILERLITE_GROUP_ID:
        campaign_payload["groups"] = [MAILERLITE_GROUP_ID]
    
    headers = {
        "Authorization": f"Bearer {MAILERLITE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Create campaign
    print("Creating campaign...")
    response = requests.post(
        "https://connect.mailerlite.com/api/campaigns",
        headers=headers,
        json=campaign_payload
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create campaign: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    campaign = response.json()
    campaign_id = campaign["data"]["id"]
    print(f"✅ Campaign created: {campaign_id}")
    
    # Schedule/send campaign
    print("Sending campaign...")
    send_response = requests.post(
        f"https://connect.mailerlite.com/api/campaigns/{campaign_id}/schedule",
        headers=headers,
        json={"delivery": "instant"}  # Send immediately
    )
    
    if send_response.status_code not in [200, 201]:
        print(f"❌ Failed to send campaign: {send_response.status_code}")
        print(send_response.text)
        sys.exit(1)
    
    print(f"✅ Newsletter sent!")
    print(f"   Subject: {subject}")
    print(f"   Campaign ID: {campaign_id}")
    
    return campaign_id


def main():
    print("=" * 60)
    print("RevCycleAI Newsletter Builder")
    print("=" * 60)
    
    # Load trends
    print("\n📊 Loading recent trends...")
    trends = load_recent_trends(days=7)
    print(f"   Found {len(trends)} trends from past 7 days")
    
    if len(trends) < 3:
        print("⚠️  Less than 3 trends found. Newsletter quality may be low.")
    
    # Generate HTML
    print("\n📧 Generating newsletter HTML...")
    html = generate_html_newsletter(trends)
    
    # Preview option
    if "--preview" in sys.argv:
        preview_file = BASE_DIR / "newsletter_preview.html"
        with open(preview_file, "w") as f:
            f.write(html)
        print(f"✅ Preview saved to: {preview_file}")
        print("   Open in browser to review before sending")
        return
    
    # Send newsletter
    print("\n📮 Sending newsletter via MailerLite...")
    campaign_id = send_newsletter(html)
    
    print("\n" + "=" * 60)
    print("✅ Newsletter sent successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
