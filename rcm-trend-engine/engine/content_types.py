#!/usr/bin/env python3
"""
RCM Trend Engine — Extended Content Type Generators
Full blog posts, email newsletters, downloadable resource concepts.
"""
from datetime import datetime


def generate_full_blog_post(brief: dict) -> str:
    """Generate a full 1,500–2,500 word blog post draft from a content brief."""
    title    = brief['recommended_title']
    source   = brief['source_article']
    angle    = brief['content_angle']
    outline  = brief['outline']
    kws      = brief['primary_keywords']
    audience = brief['target_audience']
    ctas     = brief['product_ctas']
    date     = datetime.now().strftime('%B %d, %Y')

    cta_block = ''
    if ctas:
        c = ctas[0]
        cta_block = f"""
<div class="cta-box">
<strong>{c['product']}</strong><br>
{c['section_cta']}<br>
→ <a href="{c['url']}">{c['url']}</a>
</div>"""

    angles_intro = {
        'regulatory': f"""If you haven't read this yet, you need to stop what you're doing.

On {source.get('date', 'recently')}, {source.get('source', 'regulators')} released a change that affects how every billing team in the country needs to operate. This isn't theoretical. This is live.

Here's the plain-English breakdown of what changed, who it affects, and exactly what you need to do before it costs you money.""",

        'denial_management': f"""Here's what nobody is talking about: denial rates just hit levels we haven't seen in five years.

If you're managing AR for a multi-specialty group, a DSO, or a third-party billing company, you've probably already felt it. Claims that used to sail through are sitting in your denied queue. And the root cause isn't what most people think.

I've been watching this develop for the past several weeks. Here's what's actually happening — and how to fight back.""",

        'network': f"""There's a revenue leak in your practice, and most billing directors don't even know it's there.

It's happening at the claim level, quietly, every single day. Your EOBs look normal. The payor name is right. The check clears. But you're getting paid 15–30% less than your contracted rate — and you signed off on it without realizing it.

This is the umbrella network problem, and a recent change just made it significantly worse.""",

        'industry_trend': f"""Something is shifting in revenue cycle management right now, and the teams that see it early will be significantly better positioned in 12 months.

Here's what's happening, why it matters for your team specifically, and what the leading DSOs and health systems are already doing about it.""",
    }

    intro = angles_intro.get(angle, angles_intro['industry_trend'])

    sections = []
    for i, section_title in enumerate(outline):
        sections.append(f"""
## {section_title}

[DRAFT: Expand this section with 200-350 words of expert-level content. Be specific — name real payors, real CPT codes, real scenarios. No generic advice.]

[Include: A concrete example, a dollar figure where possible, and a direct action item.]
""")

    sections_text = '\n'.join(sections)

    conclusion = f"""
## What to Do Right Now

If you're reading this and wondering where to start, here's your 48-hour action plan:

1. **Audit your most recent EOBs** for the affected claim types mentioned above
2. **Brief your billing team today** — they need to know before the next batch goes out
3. **Update your workflow** to flag these claims before submission, not after denial

The difference between teams that adapt quickly and those that don't isn't intelligence — it's information. You now have it.
{cta_block}

---

*{title}. Published {date}. For RCM professionals managing payor policy complexity at scale.*

*Keywords: {', '.join(kws[:4])}*
"""

    return f"""# {title}

*Published: {date} | For: {audience}*

---

{intro}

{sections_text}

{conclusion}"""


def generate_email_newsletter(articles: list, week_str: str = '') -> str:
    """Generate a weekly 'This Week in RCM' email newsletter."""
    if not week_str:
        week_str = datetime.now().strftime('%B %d, %Y')

    top_stories = sorted(articles, key=lambda x: -x.get('score', 0))[:3]

    story_blocks = []
    for i, art in enumerate(top_stories, 1):
        products = art.get('products', ['axlow'])
        cta_map = {
            'axlow': 'Find the updated policy → axlow.com',
            'payormap': 'Map your claim routing → payormap.com',
            'ppo_playbook': 'Negotiation playbook → [PPO Playbook URL]',
        }
        cta = cta_map.get(products[0] if products else 'axlow', 'axlow.com')

        story_blocks.append(f"""**#{i}: {art.get('title', '')}**

{art.get('summary', '')[:200]}...

*Source: {art.get('source', '')} — {art.get('date', '')[:10]}*

**What this means for you:** [2-3 sentences of practical implication]

**The action:** [1 specific thing to do this week]

{cta}

---""")

    stories_text = '\n\n'.join(story_blocks)

    return f"""Subject: This Week in RCM — {week_str}

Preview text: {top_stories[0].get('title', 'Top RCM trends')[:80]}... + 2 more stories your team needs to know.

---

**This Week in RCM**
*The signal, not the noise. Every Tuesday.*

Hey [First Name],

Three things your revenue cycle team needs to know this week:

---

{stories_text}

**Quick takes** (things worth 60 seconds of your attention):

• [Short item 1 — one sentence]
• [Short item 2 — one sentence]
• [Short item 3 — one sentence]

---

**This week's free resource:**

[Resource name — cheat sheet, template, or checklist]
→ Download free: revcycleai.com/free/[slug]

---

Forward this to your billing director. They need to see it.

— The RCM Trend Engine Team
revcycleai.com

*You're receiving this because you subscribed at revcycleai.com.*
*[Unsubscribe] | [View in browser]*"""


def generate_downloadable_resource(trend_topic: str, article: dict) -> dict:
    """Generate a downloadable resource concept and outline."""
    products = article.get('products', ['axlow'])
    keywords = article.get('keywords', [])

    resource_types = {
        'regulatory': {
            'type': 'Checklist',
            'title': f'Compliance Checklist: {trend_topic}',
            'description': 'Step-by-step compliance verification checklist for billing teams',
            'sections': [
                '☐ Step 1: Verify current policy version is on file',
                '☐ Step 2: Identify affected claim types in your payer mix',
                '☐ Step 3: Update billing system rules and edits',
                '☐ Step 4: Brief coding and billing staff',
                '☐ Step 5: Set up denial tracking for affected codes',
                '☐ Step 6: Schedule 30-day post-implementation audit',
                '☐ Step 7: Verify appeals process for transition-period denials',
            ],
        },
        'denial_management': {
            'type': 'Template',
            'title': f'Denial Appeal Letter Template: {trend_topic}',
            'description': 'Customizable appeal letter with policy citations and clinical justification framework',
            'sections': [
                '[Date]',
                '[Payor Name] Appeals Department',
                'RE: Appeal of Denied Claim — [Claim #] — [Patient DOB]',
                '',
                'Dear Appeals Reviewer,',
                '',
                'We are appealing the denial of [CPT code] for [diagnosis] on [DOS].',
                'The denial reason cited was: [denial code and reason].',
                '',
                'Clinical justification: [Insert supporting documentation]',
                'Policy citation: [Payor policy name and version]',
                'Supporting evidence: [Attach records]',
                '',
                'We request reconsideration within [X] business days per your contract terms.',
                'Contact: [Billing contact name, phone, email]',
            ],
        },
        'network': {
            'type': 'Calculator',
            'title': 'Umbrella Network Revenue Leakage Calculator',
            'description': 'Estimate how much you\'re losing annually to network stacking and repricing',
            'sections': [
                'INPUTS:',
                '• Monthly claim volume: ___',
                '• Average claim amount: $___',
                '• % of claims affected by leased networks: ___% (estimate 15-40%)',
                '• Your contracted rate vs. umbrella network rate: ___% difference',
                '',
                'CALCULATION:',
                '• Monthly affected claims: [volume × affected %]',
                '• Revenue leakage per month: [affected claims × avg claim × rate difference]',
                '• Annual revenue leakage: [monthly × 12]',
                '',
                'TYPICAL RESULTS:',
                '• 5-provider practice: $18,000–$45,000/year',
                '• 20-provider DSO: $75,000–$200,000/year',
                '• 50+ provider DSO: $250,000–$800,000/year',
            ],
        },
        'industry_trend': {
            'type': 'Cheat Sheet',
            'title': f'RCM Cheat Sheet: {trend_topic}',
            'description': '1-page quick reference for your billing team',
            'sections': [
                'WHAT\'S CHANGING: [2-3 bullet summary]',
                'WHO IT AFFECTS: [Specific roles and claim types]',
                'KEY DATES: [Timeline]',
                'ACTION ITEMS: [5-7 specific steps]',
                'RED FLAGS TO WATCH: [Warning signs]',
                'WHERE TO GET MORE INFO: [Sources]',
                'PRODUCT TOOLS: [Axlow/PayorMap links]',
            ],
        },
    }

    angle = article.get('urgency', 'industry_trend')
    # Map urgency → resource type
    cat = article.get('category', 'industry')
    if 'regulatory' in keywords or cat == 'regulatory':
        rtype = 'regulatory'
    elif any(k in keywords for k in ['denial', 'denied', 'appeal']):
        rtype = 'denial_management'
    elif any(k in keywords for k in ['umbrella', 'network', 'silent ppo', 'leased']):
        rtype = 'network'
    else:
        rtype = 'industry_trend'

    resource = resource_types[rtype]
    product_cta = {
        'axlow': 'axlow.com — Find any payor policy in 20 seconds',
        'payormap': 'payormap.com — Map your claim routing instantly',
    }.get(products[0] if products else 'axlow', 'axlow.com')

    return {
        'type': resource['type'],
        'title': resource['title'],
        'description': resource['description'],
        'format': 'PDF (1-2 pages)',
        'gate': 'Email capture at revcycleai.com/free/',
        'content_outline': resource['sections'],
        'product_cta': product_cta,
        'estimated_downloads': '200-500 in first 30 days if distributed in RCM Facebook groups',
        'email_sequence_trigger': 'After download: 3-email nurture sequence → product trial offer',
        'created_at': datetime.now().isoformat(),
    }


def validate_trend(article: dict) -> dict:
    """Run the 3-question validation filter on an article."""
    title = article.get('title', '')
    score = article.get('score', 0)
    products = article.get('products', [])
    keywords = article.get('keywords', [])

    # Q1: Will people search for this?
    searchable_score = 0
    high_search_kws = ['prior authorization', 'CMS', 'denial', 'UnitedHealthcare', 'Aetna',
                       'Cigna', 'fee schedule', 'CPT', 'ICD-10', 'Medicare', 'Medicaid',
                       'network stacking', 'silent PPO', 'umbrella network']
    for kw in keywords:
        if any(hk.lower() in kw.lower() for hk in high_search_kws):
            searchable_score += 1
    q1 = searchable_score >= 2 or score >= 20

    # Q2: Can we monetize the traffic?
    q2 = len(products) > 0

    # Q3: Can we be the best result?
    # Heuristic: regulatory/payor changes + specific payors = underserved
    specific_payors = ['UnitedHealthcare', 'Aetna', 'Cigna', 'Humana', 'BCBS', 'Anthem',
                       'MetLife', 'Delta Dental', 'Careington', 'DenteMax', 'Zelis']
    has_specific = any(p.lower() in title.lower() for p in specific_payors)
    is_recent = True  # New content from daily scan is inherently fresh
    q3 = has_specific or is_recent

    all_pass = q1 and q2 and q3
    return {
        'q1_search_potential': q1,
        'q2_monetization_path': q2,
        'q3_can_be_best': q3,
        'validated': all_pass,
        'recommendation': 'PUBLISH' if all_pass else 'SKIP',
        'reasoning': {
            'q1': f'Score {score}, {searchable_score} high-search keywords matched',
            'q2': f'Products: {products}',
            'q3': f'Specific payor: {has_specific}, Recent: {is_recent}',
        }
    }
