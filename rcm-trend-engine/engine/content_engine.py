#!/usr/bin/env python3
"""
RCM Trend Engine — Content Brief Generator
Takes a trending article and produces a full SEO content brief.
"""
import json, re
from pathlib import Path
from datetime import datetime

from signal_sources import MONETIZATION_MAP, CONTENT_ANGLES

CONTENT_DIR = Path(__file__).parent.parent / 'content'
CONTENT_DIR.mkdir(exist_ok=True)


def detect_angle(article: dict) -> str:
    """Pick the best content angle based on article category and keywords."""
    kws   = [k.lower() for k in article.get('keywords', [])]
    title = article.get('title', '').lower()

    if any(k in kws for k in ['cms', 'rule', 'regulation', 'law', 'mandate', 'proposed rule', 'final rule']):
        return 'regulatory'
    if any(k in kws for k in ['denial', 'denied', 'rejection', 'appeal', 'audit']):
        return 'denial_management'
    if any(k in kws for k in ['network', 'ppo', 'umbrella', 'leased', 'careington', 'dentemax', 'zelis', 'silent ppo']):
        return 'network'
    return 'industry_trend'


def pick_products(article: dict) -> list:
    """Return list of products to promote in this article."""
    products = article.get('products', [])
    if not products:
        return ['axlow']  # Default
    return products[:2]   # Max 2 CTAs per article


def generate_seo_title(article: dict) -> list:
    """Generate 3 SEO title options."""
    angle = detect_angle(article)
    templates = CONTENT_ANGLES.get(angle, CONTENT_ANGLES['industry_trend'])
    title = article.get('title', '')

    # Extract key entities from title
    payor_names = ['UnitedHealthcare', 'Aetna', 'Cigna', 'Humana', 'BCBS', 'Anthem',
                   'MetLife', 'Delta Dental', 'Careington', 'DenteMax', 'Zelis', 'Beam']
    found_payor = next((p for p in payor_names if p.lower() in title.lower()), 'Major Payors')

    topics = {
        'regulatory': 'CMS Rule',
        'denial_management': 'Claim Denials',
        'network': 'PPO Network',
        'industry_trend': 'RCM Innovation',
    }
    topic = topics.get(angle, 'RCM Update')
    year = datetime.now().year

    return [
        t.replace('[PAYOR]', found_payor).replace('[TOPIC]', topic)
         .replace('[RULE]', 'New Rule').replace('[YEAR]', str(year))
         .replace('[DATE]', 'Q2 2026').replace('[NETWORK]', 'Umbrella Network')
         .replace('[POLICY]', 'Policy').replace('[CLAIM TYPE]', 'Claims')
         .replace('[PROCEDURE]', 'Procedure').replace('[NEWS]', title[:40])
        for t in templates[:3]
    ]


def generate_brief(article: dict) -> dict:
    """Generate a full content brief for an article."""
    angle    = detect_angle(article)
    products = pick_products(article)
    titles   = generate_seo_title(article)

    # Primary keywords for SEO
    primary_kws = [k for k in article.get('keywords', [])
                   if k in [kw for kws in [
                       ['prior authorization', 'denial management', 'revenue cycle', 'RCM',
                        'payor policy', 'fee schedule', 'network stacking', 'silent PPO',
                        'umbrella network', 'claim denied', 'CMS', 'Medicare', 'Medicaid']
                   ] for kw in kws]][:3]
    if not primary_kws:
        primary_kws = ['revenue cycle management', 'RCM', 'healthcare billing']

    # Build product CTAs
    ctas = []
    for pid in products:
        p = MONETIZATION_MAP.get(pid)
        if p:
            ctas.append({
                'product': p['name'],
                'url': p['url'],
                'inline_cta': p['cta_short'],
                'section_cta': p['cta'],
            })

    # Article outline
    outlines = {
        'regulatory': [
            "1. What changed: Plain-English summary of the rule",
            "2. Who is affected: Which provider types, payors, and claim categories",
            "3. Effective date and implementation timeline",
            "4. What you need to do RIGHT NOW: Specific action items",
            "5. How to check current policies with [product CTA]",
            "6. Key takeaways and summary checklist",
        ],
        'denial_management': [
            "1. The problem: Why this denial type is spiking right now",
            "2. Root cause analysis: What's driving the increase",
            "3. How to identify affected claims in your AR",
            "4. Appeal strategy: Step-by-step with script",
            "5. Prevention: How to avoid this denial in the future",
            "6. How [product] helps catch this before it hits your AR",
        ],
        'network': [
            "1. The network relationship explained (with diagram description)",
            "2. How to tell if your claims are being routed through this network",
            "3. The fee schedule difference: What you're losing per claim",
            "4. Dollar impact calculation for a typical practice",
            "5. How to audit your EOBs for this issue",
            "6. Carve-out strategy: How to negotiate a direct contract",
            "7. Use [product] to map your routing in 30 seconds",
        ],
        'industry_trend': [
            "1. What's happening: The trend explained",
            "2. Why it matters for revenue cycle teams",
            "3. Early movers: What leading DSOs/health systems are doing",
            "4. What happens if you ignore it",
            "5. Your 30-day action plan",
            "6. Tools that help: [product CTA]",
        ],
    }

    brief = {
        'source_article': {
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'source': article.get('source', ''),
            'score': article.get('score', 0),
            'urgency': article.get('urgency', ''),
            'published': article.get('date', ''),
        },
        'content_angle': angle,
        'urgency': article.get('urgency', '48h'),
        'title_options': titles,
        'recommended_title': titles[0],
        'primary_keywords': primary_kws,
        'secondary_keywords': article.get('keywords', [])[:8],
        'target_audience': _audience_for_angle(angle),
        'word_count_target': '1,200-1,800 words',
        'outline': outlines.get(angle, outlines['industry_trend']),
        'product_ctas': ctas,
        'distribution': _distribution_for_urgency(article.get('urgency', '48h')),
        'meta_description': f"Expert analysis: {article.get('title', '')[:100]}. What RCM teams need to know and what to do now.",
        'internal_links': _internal_links(products),
        'created_at': datetime.now().isoformat(),
        'status': 'draft',
    }
    return brief


def _audience_for_angle(angle: str) -> str:
    mapping = {
        'regulatory': 'VP Revenue Cycle, RCM Managers, Billing Directors, Practice Managers',
        'denial_management': 'Denial Management Specialists, Billing Managers, AR Managers',
        'network': 'VP Payor Contracting, DSO Operations Leaders, Credentialing Managers',
        'industry_trend': 'RCM Leaders, VP Revenue Cycle, CFOs, Practice Managers',
    }
    return mapping.get(angle, 'RCM Professionals')


def _distribution_for_urgency(urgency: str) -> list:
    if urgency == 'immediate':
        return ['blog_post', 'linkedin_article', 'linkedin_post', 'x_thread', 'email_alert']
    if urgency == '24h':
        return ['blog_post', 'linkedin_article', 'linkedin_post', 'x_thread']
    if urgency == '48h':
        return ['blog_post', 'linkedin_post', 'x_post']
    return ['blog_post', 'linkedin_post']


def _internal_links(products: list) -> list:
    links = []
    if 'axlow' in products:
        links += [
            {'anchor': 'payor policy search', 'url': 'https://axlow.com'},
            {'anchor': 'find any payor policy in seconds', 'url': 'https://axlow.com'},
        ]
    if 'payormap' in products:
        links += [
            {'anchor': 'dental PPO routing intelligence', 'url': 'https://payormap.com'},
            {'anchor': 'map your claim routing', 'url': 'https://payormap.com'},
        ]
    return links


def save_brief(brief: dict) -> Path:
    """Save brief to content directory."""
    slug = re.sub(r'[^a-z0-9]+', '-', brief['recommended_title'].lower())[:60]
    date = datetime.now().strftime('%Y-%m-%d')
    filename = CONTENT_DIR / f"{date}-{slug}.json"
    filename.write_text(json.dumps(brief, indent=2))
    return filename


def generate_linkedin_post(brief: dict) -> str:
    """Generate a LinkedIn post from a content brief."""
    title    = brief['recommended_title']
    angle    = brief['content_angle']
    source   = brief['source_article']
    ctas     = brief['product_ctas']
    kws      = brief['primary_keywords'][:3]

    hooks = {
        'regulatory': f"⚠️ RCM Alert: {title}\n\nIf you haven't read this yet, you need to.",
        'denial_management': f"📉 Denial spike alert: {title}\n\nHere's what's actually driving this — and how to fight back.",
        'network': f"💰 Revenue leakage: {title}\n\nMost practices don't even know this is happening to their claims.",
        'industry_trend': f"📊 {title}\n\nHere's what this means for your revenue cycle team.",
    }

    cta_line = ''
    if ctas:
        cta = ctas[0]
        cta_line = f"\n\n🔗 {cta['inline_cta']}"

    hashtags = ' '.join([f"#{k.replace(' ', '').replace('-', '')}" for k in kws[:4]] +
                        ['#RevenueC ycle', '#RCM', '#HealthcareFinance'])

    return f"""{hooks.get(angle, hooks['industry_trend'])}

What's changing:
• [Key point 1 from article]
• [Key point 2 from article]
• [Key point 3 — the action item]

The bottom line: [1-2 sentence plain-English summary of impact]
{cta_line}

{hashtags}

Source: {source.get('source', '')} — link in comments"""


def generate_x_thread(brief: dict) -> str:
    """Generate an X/Twitter thread from a content brief."""
    title = brief['recommended_title']
    ctas  = brief['product_ctas']
    cta_line = f"\n\n🔗 {ctas[0]['inline_cta']}" if ctas else ''

    return f"""1/ {title}

A thread for RCM teams 🧵👇

2/ What happened: [Plain English summary of the news/change]

3/ Who it affects: [Specific provider types, specialties, or claim categories]

4/ The dollar impact: [Specific estimate — e.g., "$200-500 per affected claim" or "3-5% of applicable claims"]

5/ What to do RIGHT NOW:
→ [Action 1]
→ [Action 2]
→ [Action 3]
{cta_line}

6/ Bottom line: [One sentence. What do you do today?]

RT if this helps your team. Follow for daily RCM intelligence."""


if __name__ == '__main__':
    # Test with a sample article
    sample = {
        'title': 'CMS Proposes New Prior Authorization Requirements for Medicare Advantage Plans',
        'url': 'https://cms.gov/test',
        'source': 'CMS News',
        'score': 28,
        'urgency': 'immediate',
        'keywords': ['prior authorization', 'Medicare Advantage', 'CMS', 'revenue cycle'],
        'products': ['axlow'],
        'date': '2026-02-19',
    }
    brief = generate_brief(sample)
    path = save_brief(brief)
    print(f"Brief saved: {path}")
    print(f"\nTitle options:")
    for t in brief['title_options']:
        print(f"  - {t}")
    print(f"\nLinkedIn Post:")
    print(generate_linkedin_post(brief))
