#!/usr/bin/env python3
"""
RCM Trend Engine — Signal Sources
Defines all monitored RSS feeds, keywords, and payor bulletin sources.
"""

# ── RSS FEEDS ────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    # Government / Regulatory (HIGHEST VALUE — publish within 24-48h)
    {
        "name": "CMS News",
        "url": "https://www.cms.gov/newsroom/rss",
        "category": "regulatory",
        "priority": 10,
        "monetize": ["axlow", "payormap"],
        "urgency": "immediate",
    },
    {
        "name": "CMS Fact Sheets",
        "url": "https://www.cms.gov/newsroom/fact-sheets/rss",
        "category": "regulatory",
        "priority": 10,
        "monetize": ["axlow"],
        "urgency": "immediate",
    },
    {
        "name": "OIG HHS",
        "url": "https://oig.hhs.gov/newsroom/rss/newsreleases.rss",
        "category": "regulatory",
        "priority": 9,
        "monetize": ["axlow"],
        "urgency": "immediate",
    },
    {
        "name": "Federal Register (Health)",
        "url": "https://www.federalregister.gov/documents/search.rss?conditions%5Bagencies%5D%5B%5D=centers-for-medicare-medicaid-services",
        "category": "regulatory",
        "priority": 9,
        "monetize": ["axlow", "payormap"],
        "urgency": "immediate",
    },
    # Industry Publications (High intent, professional audience)
    {
        "name": "RevCycle Intelligence",
        "url": "https://revcycleintelligence.com/rss/all",
        "category": "industry",
        "priority": 8,
        "monetize": ["axlow", "payormap"],
        "urgency": "24h",
    },
    {
        "name": "Becker's Hospital Review - RCM",
        "url": "https://www.beckershospitalreview.com/rss/healthcare-information-technology.rss",
        "category": "industry",
        "priority": 7,
        "monetize": ["axlow", "payormap"],
        "urgency": "24h",
    },
    {
        "name": "Healthcare Finance News",
        "url": "https://www.healthcarefinancenews.com/rss.xml",
        "category": "industry",
        "priority": 7,
        "monetize": ["axlow"],
        "urgency": "48h",
    },
    {
        "name": "Modern Healthcare",
        "url": "https://www.modernhealthcare.com/rss/news.rss",
        "category": "industry",
        "priority": 7,
        "monetize": ["axlow"],
        "urgency": "48h",
    },
    {
        "name": "HFMA News",
        "url": "https://www.hfma.org/rss/news.rss",
        "category": "industry",
        "priority": 8,
        "monetize": ["axlow"],
        "urgency": "48h",
    },
    {
        "name": "ADA News",
        "url": "https://www.ada.org/publications/ada-news/rss",
        "category": "dental",
        "priority": 8,
        "monetize": ["payormap"],
        "urgency": "48h",
    },
    {
        "name": "Becker's Dental Review",
        "url": "https://www.beckershospitalreview.com/rss/dental.rss",
        "category": "dental",
        "priority": 8,
        "monetize": ["payormap"],
        "urgency": "48h",
    },
    {
        "name": "MGMA Insights",
        "url": "https://www.mgma.com/rss/all",
        "category": "industry",
        "priority": 6,
        "monetize": ["axlow"],
        "urgency": "72h",
    },
    {
        "name": "Dental Economics",
        "url": "https://www.dentaleconomics.com/rss",
        "category": "dental",
        "priority": 7,
        "monetize": ["payormap"],
        "urgency": "48h",
    },
    {
        "name": "NADP",
        "url": "https://www.nadp.org/rss",
        "category": "dental",
        "priority": 7,
        "monetize": ["payormap"],
        "urgency": "48h",
    },
]

# ── KEYWORDS — triggers that elevate a story's trend score ──────────────────
HIGH_VALUE_KEYWORDS = {
    # Immediate action triggers (score +5 each)
    "immediate": [
        "prior authorization", "prior auth", "preauthorization",
        "denial", "claim denied", "claim rejection", "underpayment",
        "fee schedule", "reimbursement rate", "payment policy",
        "network access", "credentialing", "umbrella network",
        "silent ppo", "leased network", "network stacking",
        "CMS final rule", "CMS proposed rule", "Medicare advantage",
        "Medicaid managed care", "parity law", "surprise billing",
        "No Surprises Act", "price transparency",
    ],
    # Strong signal keywords (score +3 each)
    "strong": [
        "revenue cycle", "RCM", "billing", "coding", "CPT", "ICD-10",
        "HCPCS", "EOB", "remittance", "claims processing",
        "denial management", "denial rate", "appeals", "RAC audit",
        "overpayment", "medical necessity", "prior auth burden",
        "administrative burden", "payor policy", "coverage policy",
        "UnitedHealthcare", "Aetna", "Cigna", "Humana", "BCBS",
        "MetLife", "Delta Dental", "Careington", "DenteMax", "Zelis",
        "DSO", "dental service organization", "group practice",
    ],
    # Supporting keywords (score +1 each)
    "supporting": [
        "healthcare", "insurance", "provider", "payer", "patient",
        "hospital", "physician", "dental", "specialty", "ambulatory",
        "AI", "automation", "technology", "efficiency", "workflow",
        "staffing", "burnout", "shortage",
    ],
}

# ── MONETIZATION MAPPING ─────────────────────────────────────────────────────
MONETIZATION_MAP = {
    "axlow": {
        "name": "Axlow",
        "url": "https://axlow.com",
        "cta": "Find the exact payor policy in 20 seconds — no PDFs, no portals.",
        "cta_short": "Search any payor policy instantly → axlow.com",
        "trigger_keywords": ["policy", "prior auth", "coverage", "billing rule", "payor", "CMS", "denial"],
    },
    "payormap": {
        "name": "PayorMap",
        "url": "https://payormap.com",
        "cta": "See exactly which network is repricing your claims — and where your carve-out opportunities are.",
        "cta_short": "Map your claim routing in seconds → payormap.com",
        "trigger_keywords": ["network", "PPO", "umbrella", "leased", "Careington", "DenteMax", "Zelis", "routing", "DSO", "dental"],
    },
    "ppo_playbook": {
        "name": "PPO Playbook",
        "url": "https://payormap.com/playbook",
        "cta": "Download the free PPO Network Stacking Playbook — understand how your claims are really being repriced.",
        "cta_short": "Free guide: How umbrella networks reprice your claims →",
        "trigger_keywords": ["PPO", "network", "leased", "umbrella", "fee schedule", "dental"],
    },
}

# ── CONTENT TEMPLATES — article structures ───────────────────────────────────
CONTENT_ANGLES = {
    "regulatory": [
        "What [RULE] Means for RCM Teams: A Practical Breakdown",
        "[PAYOR] Just Changed [POLICY] — Here's What to Do Before [DATE]",
        "CMS Finalizes [RULE]: 5 Things Revenue Cycle Leaders Must Do Now",
        "Breaking: [NEWS] — Impact on Claim Submissions Explained",
    ],
    "denial_management": [
        "Why [PAYOR] Is Denying [CLAIM TYPE] Claims Right Now",
        "The [PAYOR] Denial Spike: What's Behind It and How to Fight Back",
        "[PROCEDURE] Denial Rate Hits All-Time High — Here's the Root Cause",
        "How to Win [PAYOR] Appeals for [CLAIM TYPE]: A Step-by-Step Guide",
    ],
    "network": [
        "Is [PAYOR] Repricing Your Claims Through [NETWORK]? Here's How to Check",
        "The Hidden [NETWORK] Lease: Why Your [PAYOR] Reimbursement Is Lower Than It Should Be",
        "Silent PPO Alert: [PAYOR] and [NETWORK] — What DSOs Need to Know",
        "Carve-Out Opportunity: How to Escape [NETWORK] Repricing for [PAYOR]",
    ],
    "industry_trend": [
        "The RCM Industry Is Talking About [TOPIC] — Here's What You Need to Know",
        "[TOPIC] Is Reshaping Revenue Cycle Management in [YEAR]",
        "Why Every DSO Needs a [TOPIC] Strategy Before [DATE]",
        "The [TOPIC] Problem No One in RCM Is Talking About (Yet)",
    ],
}
