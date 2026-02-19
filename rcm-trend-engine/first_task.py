#!/usr/bin/env python3
"""
RCM Trend Engine — First Task
Generates: Starter trend report + 2-week content calendar + first 3 content pieces.
"""
import sys, json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent / 'engine'))

from trend_monitor import load_trending
from content_engine import generate_brief, generate_linkedin_post, generate_x_thread, save_brief
from content_types import validate_trend, generate_full_blog_post, generate_email_newsletter, generate_downloadable_resource

OUTPUT_DIR = Path(__file__).parent / 'content'
OUTPUT_DIR.mkdir(exist_ok=True)

TODAY = datetime.now()

def build_content_calendar(articles: list) -> list:
    """Build a 2-week prioritized content calendar."""
    validated = []
    for art in articles:
        v = validate_trend(art)
        if v['validated']:
            validated.append({**art, 'validation': v})

    calendar = []
    day_offset = 0
    content_types_cycle = ['blog_post', 'linkedin_post', 'x_thread', 'blog_post', 'resource', 'linkedin_post', 'newsletter']

    for i, art in enumerate(sorted(validated, key=lambda x: -x['score'])[:14]):
        pub_date = TODAY + timedelta(days=day_offset)
        urgency = art.get('urgency', '48h')
        if urgency == 'immediate':
            pub_date = TODAY
        elif urgency == '24h':
            pub_date = TODAY + timedelta(days=1)

        ct = content_types_cycle[i % len(content_types_cycle)]
        calendar.append({
            'publish_date': pub_date.strftime('%Y-%m-%d'),
            'content_type': ct,
            'title': art.get('title', ''),
            'article_id': art.get('id', ''),
            'score': art.get('score', 0),
            'urgency': urgency,
            'products': art.get('products', []),
            'keywords': art.get('keywords', [])[:3],
            'source': art.get('source', ''),
        })
        if i > 0 and i % 2 == 0:
            day_offset += 1

    return sorted(calendar, key=lambda x: x['publish_date'])


def run_first_task():
    print("=" * 70)
    print("RCM TREND ENGINE — FIRST TASK REPORT")
    print(f"Generated: {TODAY.strftime('%B %d, %Y at %I:%M %p CT')}")
    print("=" * 70)

    articles = load_trending()
    if not articles:
        print("\n⚠️  No articles in trending.json yet. Run a scan first.")
        return

    # ── SECTION 1: TOP TRENDS ──────────────────────────────────────────────
    print(f"\n📡 TOP {min(10, len(articles))} TRENDING RCM TOPICS RIGHT NOW")
    print("-" * 70)

    for i, art in enumerate(sorted(articles, key=lambda x: -x['score'])[:10], 1):
        v = validate_trend(art)
        status = "✅ VALIDATED" if v['validated'] else "⚠️  NEEDS REVIEW"
        products = ' + '.join(art.get('products', ['general']))
        print(f"\n{i}. [{art['score']}pts] {art['title'][:75]}")
        print(f"   Source: {art['source']} | Urgency: {art['urgency'].upper()}")
        print(f"   Products: {products} | {status}")
        print(f"   Keywords: {', '.join(art.get('keywords', [])[:4])}")

    # ── SECTION 2: CONTENT CALENDAR ──────────────────────────────────────
    print(f"\n\n📅 2-WEEK CONTENT CALENDAR")
    print("-" * 70)

    calendar = build_content_calendar(articles)
    cal_path = OUTPUT_DIR / 'content_calendar.json'
    cal_path.write_text(json.dumps(calendar, indent=2))

    last_date = ''
    for item in calendar:
        if item['publish_date'] != last_date:
            print(f"\n  📆 {item['publish_date']}")
            last_date = item['publish_date']
        icon = {'blog_post': '📝', 'linkedin_post': '💼', 'x_thread': '𝕏', 'resource': '📥', 'newsletter': '📧'}.get(item['content_type'], '📄')
        products_str = ' + '.join(item['products']) if item['products'] else 'general'
        print(f"     {icon} {item['content_type'].replace('_',' ').title()}: {item['title'][:55]}...")
        print(f"        [{item['score']}pts] → {products_str}")

    print(f"\n  ✅ Calendar saved to: content/content_calendar.json")

    # ── SECTION 3: FIRST 3 CONTENT PIECES ────────────────────────────────
    print(f"\n\n✍️  FIRST 3 CONTENT PIECES")
    print("-" * 70)

    top_articles = sorted(articles, key=lambda x: -x['score'])

    # Piece 1: Full blog post on highest-urgency trend
    blog_article = next((a for a in top_articles if validate_trend(a)['validated']), top_articles[0])
    brief = generate_brief(blog_article)
    blog_content = generate_full_blog_post(brief)
    blog_path = OUTPUT_DIR / f"blog-{blog_article['id'][:8]}.md"
    blog_path.write_text(blog_content)
    save_brief(brief)
    print(f"\n📝 PIECE 1: Full Blog Post (1,500–2,500 words)")
    print(f"   Title: {brief['recommended_title']}")
    print(f"   Target keywords: {', '.join(brief['primary_keywords'][:3])}")
    print(f"   CTA: {brief['product_ctas'][0]['inline_cta'] if brief['product_ctas'] else 'N/A'}")
    print(f"   Publish on: revcycleai.com/blog/")
    print(f"   Saved: {blog_path.name}")

    # Piece 2: LinkedIn post on a high-engagement pain point
    linkedin_article = next((a for a in top_articles if a.get('id') != blog_article.get('id') and validate_trend(a)['validated']), top_articles[1] if len(top_articles) > 1 else top_articles[0])
    brief2 = generate_brief(linkedin_article)
    linkedin_post = generate_linkedin_post(brief2)
    li_path = OUTPUT_DIR / f"linkedin-{linkedin_article['id'][:8]}.txt"
    li_path.write_text(linkedin_post)
    print(f"\n💼 PIECE 2: LinkedIn Post")
    print(f"   Topic: {linkedin_article['title'][:65]}")
    print(f"   Angle: {brief2['content_angle']} | Products: {', '.join(brief2['product_ctas'][:1] and [c['product'] for c in brief2['product_ctas'][:1]] or ['N/A'])}")
    print(f"   Saved: {li_path.name}")
    print(f"\n   PREVIEW:")
    print('\n'.join(f"   {line}" for line in linkedin_post.split('\n')[:8]))

    # Piece 3: Downloadable resource concept
    resource_article = next((a for a in top_articles if 'payormap' in a.get('products', []) or 'network' in a.get('category', '')), top_articles[0])
    resource = generate_downloadable_resource(resource_article.get('title', ''), resource_article)
    res_path = OUTPUT_DIR / f"resource-{resource_article['id'][:8]}.json"
    res_path.write_text(json.dumps(resource, indent=2))
    print(f"\n📥 PIECE 3: Downloadable Resource ({resource['type']})")
    print(f"   Title: {resource['title']}")
    print(f"   Gate: Email capture at revcycleai.com/free/")
    print(f"   Projected downloads: {resource['estimated_downloads']}")
    print(f"   Email sequence: {resource['email_sequence_trigger']}")
    print(f"   CTA: {resource['product_cta']}")
    print(f"   Saved: {res_path.name}")

    # ── SECTION 4: WEEKLY NEWSLETTER DRAFT ───────────────────────────────
    newsletter = generate_email_newsletter(top_articles[:3], TODAY.strftime('%B %d, %Y'))
    nl_path = OUTPUT_DIR / f"newsletter-{TODAY.strftime('%Y-%m-%d')}.txt"
    nl_path.write_text(newsletter)
    print(f"\n📧 BONUS: Weekly Newsletter Draft")
    print(f"   Subject: This Week in RCM — {TODAY.strftime('%B %d, %Y')}")
    print(f"   Saved: {nl_path.name}")

    # ── SECTION 5: NEXT STEPS ────────────────────────────────────────────
    print(f"\n\n🚀 NEXT STEPS")
    print("-" * 70)
    print("1. Register revcycleai.com (central content hub)")
    print("   → Set up: /blog, /free, /tools, /newsletter")
    print("2. Publish blog post on revcycleai.com — TODAY (immediate urgency)")
    print("3. Post LinkedIn post — TODAY at 8am or 12pm CT")
    print("4. Create PDF of resource and gate it at revcycleai.com/free/")
    print("5. Set up email capture (ConvertKit/Beehiiv) before first publish")
    print("6. Schedule next 5 LinkedIn posts from content calendar")
    print("7. Run daily scan via cron (already configured at 8am CT)")
    print()
    print("💰 Revenue Path:")
    print("   Blog → Axlow trial → $97/month/user")
    print("   Blog → PayorMap trial → $497/month")
    print("   Resource download → Email list → Weekly newsletter → Product sales")
    print()
    print(f"All content saved in: {OUTPUT_DIR}")
    print("=" * 70)

    return {
        'trends_found': len(articles),
        'validated': len([a for a in articles if validate_trend(a)['validated']]),
        'calendar_items': len(calendar),
        'content_pieces': 3,
    }


if __name__ == '__main__':
    run_first_task()
