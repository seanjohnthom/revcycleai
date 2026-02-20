#!/usr/bin/env python3
"""
Auto-generate blog posts from RCM trends
Converts top trend into full 800-1000 word blog post
"""

import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
TRENDS_FILE = BASE_DIR / "data" / "trending.json"
BLOG_DIR = Path("/Users/shackleton/.openclaw/workspace/revcycleai/public/blog")
BLOG_INDEX = BLOG_DIR / "index.html"


def slugify(text: str) -> str:
    """Convert title to URL-safe slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:60].strip('-')


def generate_blog_post(trend: dict, verbose: bool = True) -> dict:
    """
    Generate full blog post from trend
    Returns dict with: title, slug, html_content, date, category, urgency
    """
    
    title = trend.get('title', 'Untitled')
    summary = trend.get('summary', '')
    source = trend.get('source', 'Industry News')
    category = trend.get('category', 'general')
    urgency = trend.get('urgency', 'medium')
    products = trend.get('products', [])
    date = datetime.now().strftime('%B %d, %Y')
    
    # Generate slug
    slug = slugify(title)
    
    # Generate blog content (800-1000 words)
    # This is a simplified version - you can enhance with more sophisticated content generation
    
    intro = f"""
<p class="lead">{summary}</p>

<p>This development was reported by {source} and represents a significant shift in the revenue cycle landscape. Here's what billing teams need to know.</p>
"""

    # Section 1: What Changed
    what_changed = """
<h2>What Changed</h2>

<p>The new requirements represent a fundamental shift in how healthcare organizations must approach this aspect of revenue cycle management. Key changes include:</p>

<ul>
<li><strong>Timeline compression:</strong> Significantly reduced turnaround times for critical processes</li>
<li><strong>Transparency requirements:</strong> Enhanced documentation and disclosure obligations</li>
<li><strong>Technology mandates:</strong> New electronic submission and tracking requirements</li>
<li><strong>Compliance deadlines:</strong> Immediate or near-term implementation timelines</li>
</ul>

<p>These changes affect both the operational workflow and the technology infrastructure that supports revenue cycle operations.</p>
"""

    # Section 2: Impact on Your Organization
    impact = """
<h2>Impact on Your Organization</h2>

<p>The implications vary by organization size and current technology stack, but common impacts include:</p>

<div class="callout">
<h3>For Small to Mid-Size Practices</h3>
<p>Organizations with 1-50 providers will need to update staff training immediately and may require workflow automation to meet new timelines. Manual processes that worked under previous requirements are no longer viable.</p>
</div>

<div class="callout">
<h3>For Large Groups and Health Systems</h3>
<p>Enterprise organizations must coordinate across multiple departments, update EHR/PM system configurations, and ensure all sites comply with standardized procedures. The compliance burden scales with organizational complexity.</p>
</div>

<p>Regardless of size, the financial impact of non-compliance can be significant. Organizations that fail to adapt risk claim denials, delayed reimbursement, and potential regulatory penalties.</p>
"""

    # Section 3: Action Plan
    action_plan = """
<h2>Your 48-Hour Action Plan</h2>

<p>Immediate steps to ensure compliance and minimize disruption:</p>

<h3>Day 1: Assessment</h3>
<ol>
<li><strong>Audit current processes</strong> — Document existing workflows and identify gaps against new requirements</li>
<li><strong>Review technology capabilities</strong> — Verify your EHR/PM system supports required electronic submissions</li>
<li><strong>Identify affected claims volume</strong> — Quantify the scope of impact on your revenue stream</li>
<li><strong>Assess staff capacity</strong> — Determine if current staffing can handle compressed timelines</li>
</ol>

<h3>Day 2: Implementation Planning</h3>
<ol>
<li><strong>Update workflow documentation</strong> — Revise standard operating procedures to reflect new requirements</li>
<li><strong>Schedule staff training</strong> — All relevant team members must understand changes before go-live</li>
<li><strong>Configure system updates</strong> — Work with your EHR/PM vendor to implement necessary changes</li>
<li><strong>Establish monitoring</strong> — Set up dashboards to track compliance metrics</li>
</ol>
"""

    # Section 4: Tools and Resources
    tools_section = ""
    if 'axlow' in products:
        tools_section += """
<div class="tool-cta">
<h3>Find Exact Policy Language with Axlow</h3>
<p>Navigating payor policy changes requires access to the most current requirements. Axlow provides instant search across all major payor policies, including prior authorization criteria, coverage guidelines, and appeals procedures.</p>
<p><a href="https://axlow.com" class="btn">Try Axlow Free →</a></p>
</div>
"""
    
    if 'payormap' in products:
        tools_section += """
<div class="tool-cta">
<h3>Optimize Claim Routing with PayorMap</h3>
<p>Network changes and repricing arrangements can significantly impact reimbursement. PayorMap helps DSOs and large groups identify optimal claim routing paths and avoid silent PPO leakage.</p>
<p><a href="https://payormap.com" class="btn">See PayorMap →</a></p>
</div>
"""

    # Conclusion
    conclusion = """
<h2>Looking Ahead</h2>

<p>This change represents the latest in an ongoing evolution of revenue cycle requirements. Organizations that invest in robust processes and technology today will be better positioned for future regulatory shifts.</p>

<p>The key to successful adaptation is treating this not as a one-time compliance exercise, but as an opportunity to strengthen your revenue cycle infrastructure. Teams that embrace automation, enhance staff training, and leverage specialized tools will emerge stronger and more resilient.</p>

<p class="byline">Published by RevCycleAI Research · {date}</p>
""".format(date=date)

    # Combine all sections
    full_content = intro + what_changed + impact + action_plan + tools_section + conclusion
    
    return {
        'title': title,
        'slug': slug,
        'content': full_content,
        'date': date,
        'category': category,
        'urgency': urgency,
        'products': products,
        'source': source
    }


def create_blog_post_html(post: dict) -> str:
    """Generate complete HTML file for blog post"""
    
    urgency_class = post['urgency']
    urgency_label = {
        'immediate': '🔴 Immediate',
        '24h': '🟡 24h',
        '48h': '🟢 48h',
        'low': '🔵 Industry News'
    }.get(urgency_class, '🔵 News')
    
    category_label = post['category'].replace('_', ' ').title()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{post['title']} — RevCycleAI</title>
<meta name="description" content="{post['title']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{ --bg: #fff; --text: #09090B; --text2: #52525B; --text3: #A1A1AA; --border: #E4E4E7; --accent: #1D4ED8; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.7; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  nav {{ background: #fff; border-bottom: 1px solid var(--border); padding: 0 24px; }}
  .nav-inner {{ max-width: 900px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 60px; }}
  .wordmark {{ font-size: 18px; font-weight: 900; color: var(--text); }}
  .wordmark span {{ font-weight: 400; }}
  .wordmark em {{ display: inline-block; background: var(--accent); color: #fff; font-size: 9px; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-left: 6px; letter-spacing: 0.5px; vertical-align: middle; font-style: normal; text-transform: uppercase; }}
  .nav-links {{ display: flex; gap: 24px; font-size: 14px; }}
  .nav-links a {{ color: var(--text2); }}

  .article {{ max-width: 720px; margin: 60px auto 80px; padding: 0 24px; }}
  .article-meta {{ font-size: 13px; color: var(--text3); margin-bottom: 8px; }}
  .article-tags {{ display: flex; gap: 8px; margin-bottom: 20px; }}
  .tag {{ font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .tag.immediate {{ background: #FEE2E2; color: #DC2626; }}
  .tag.high {{ background: #FEF3C7; color: #D97706; }}
  .tag.medium {{ background: #D1FAE5; color: #16A34A; }}
  h1 {{ font-size: 36px; font-weight: 900; line-height: 1.2; margin-bottom: 24px; color: var(--text); }}
  .lead {{ font-size: 19px; line-height: 1.6; color: var(--text2); margin-bottom: 32px; font-weight: 500; }}
  h2 {{ font-size: 24px; font-weight: 700; margin: 48px 0 16px; color: var(--text); }}
  h3 {{ font-size: 18px; font-weight: 700; margin: 32px 0 12px; color: var(--text); }}
  p {{ margin-bottom: 20px; }}
  ul, ol {{ margin: 0 0 20px 24px; }}
  li {{ margin-bottom: 8px; }}
  strong {{ font-weight: 700; color: var(--text); }}
  .callout {{ background: #F4F4F5; border-left: 4px solid var(--accent); padding: 20px; margin: 24px 0; border-radius: 4px; }}
  .callout h3 {{ margin-top: 0; font-size: 16px; }}
  .tool-cta {{ background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border: 2px solid var(--accent); border-radius: 8px; padding: 24px; margin: 32px 0; }}
  .tool-cta h3 {{ margin-top: 0; color: var(--accent); }}
  .btn {{ display: inline-block; background: var(--accent); color: #fff; padding: 10px 20px; border-radius: 6px; font-weight: 700; text-decoration: none; }}
  .btn:hover {{ background: #1E40AF; text-decoration: none; }}
  .byline {{ font-size: 14px; color: var(--text3); margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border); }}

  footer {{ background: var(--text); color: #71717A; padding: 32px 24px; font-size: 12px; text-align: center; }}
  footer a {{ color: #71717A; }}
  .footer-wordmark {{ font-size: 16px; font-weight: 900; color: #fff; margin-bottom: 8px; }}
</style>
</head>
<body>

<nav>
  <div class="nav-inner">
    <a href="/" class="wordmark">Rev<span>Cycle</span><em>AI</em></a>
    <div class="nav-links">
      <a href="/blog">← Back to Intelligence</a>
    </div>
  </div>
</nav>

<article class="article">
  <div class="article-meta">{post['source']} · {post['date']}</div>
  <div class="article-tags">
    <span class="tag {urgency_class}">{urgency_label}</span>
  </div>
  <h1>{post['title']}</h1>
  
  {post['content']}
</article>

<footer>
  <div class="footer-wordmark">RevCycleAI</div>
  <p>RCM intelligence for billing teams, directors, and DSO operators.</p>
  <p style="margin-top: 8px;"><a href="/">Home</a> · <a href="/blog">Intelligence</a> · <a href="/newsletter">Newsletter</a></p>
</footer>

</body>
</html>
"""
    return html


def save_blog_post(post: dict, verbose: bool = True) -> Path:
    """Save blog post HTML to file"""
    post_dir = BLOG_DIR / post['slug']
    post_dir.mkdir(parents=True, exist_ok=True)
    
    html = create_blog_post_html(post)
    post_file = post_dir / "index.html"
    
    with open(post_file, 'w') as f:
        f.write(html)
    
    if verbose:
        print(f"✅ Blog post saved: {post_file}")
    
    return post_file


def update_blog_index(post: dict, verbose: bool = True):
    """Add new post to blog index page"""
    if not BLOG_INDEX.exists():
        if verbose:
            print("⚠️  Blog index not found, skipping index update")
        return
    
    with open(BLOG_INDEX, 'r') as f:
        html = f.read()
    
    # Create new post card HTML
    urgency_label = {
        'immediate': '🔴 Immediate',
        '24h': '🟡 High',
        '48h': '🟢 Medium',
        'low': '🔵 Industry'
    }.get(post['urgency'], '🔵 News')
    
    category_label = post['category'].replace('_', ' ').title()
    
    product_tags = ""
    for prod in post['products']:
        if prod == 'axlow':
            product_tags += '<span class="prod-tag axlow">Axlow</span>'
        elif prod == 'payormap':
            product_tags += '<span class="prod-tag payormap">PayorMap</span>'
    
    new_card = f"""
  <div class="post-card">
    <div class="post-tag {post['urgency']}">{urgency_label} · {category_label}</div>
    <div class="post-meta">{post['date']} · {post['source']} · 8 min read</div>
    <h2><a href="/blog/{post['slug']}">{post['title']}</a></h2>
    <p>{post['title']}</p>
    <a href="/blog/{post['slug']}" class="post-cta">Read full analysis →</a>
    <div class="post-products">{product_tags}</div>
  </div>
"""
    
    # Insert at the top of the posts grid
    posts_marker = '<div class="posts">'
    if posts_marker in html:
        html = html.replace(posts_marker, posts_marker + new_card, 1)
        
        with open(BLOG_INDEX, 'w') as f:
            f.write(html)
        
        if verbose:
            print(f"✅ Blog index updated with new post")
    else:
        if verbose:
            print("⚠️  Could not find posts marker in blog index")


def generate_from_trends(limit: int = 1, verbose: bool = True) -> list:
    """
    Generate blog posts from top N trends
    Returns list of saved post paths
    """
    if not TRENDS_FILE.exists():
        print("❌ No trends file found")
        return []
    
    with open(TRENDS_FILE) as f:
        trends = json.load(f)
    
    # Filter for high-scoring unprocessed trends
    candidates = [t for t in trends if t.get('score', 0) >= 30 and t.get('status') == 'new']
    
    if not candidates:
        if verbose:
            print("⚠️  No high-priority trends found for blog generation")
        return []
    
    posts_created = []
    
    for trend in candidates[:limit]:
        if verbose:
            print(f"\n📝 Generating blog post: {trend['title'][:60]}...")
        
        post = generate_blog_post(trend, verbose=verbose)
        post_path = save_blog_post(post, verbose=verbose)
        update_blog_index(post, verbose=verbose)
        posts_created.append(post_path)
        
        # Mark trend as processed
        trend['status'] = 'published'
    
    # Save updated trends
    with open(TRENDS_FILE, 'w') as f:
        json.dump(trends, f, indent=2)
    
    return posts_created


if __name__ == "__main__":
    import sys
    
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print("=" * 60)
    print("RevCycleAI Auto Blog Generator")
    print("=" * 60)
    
    posts = generate_from_trends(limit=limit, verbose=True)
    
    print(f"\n✅ Generated {len(posts)} blog post(s)")
    for p in posts:
        print(f"   {p}")
