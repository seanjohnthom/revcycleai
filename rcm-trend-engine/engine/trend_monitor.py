#!/usr/bin/env python3
"""
RCM Trend Engine — Signal Monitor
Fetches RSS feeds, scores articles, stores trending topics.
"""
import json, hashlib, time, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

try:
    import feedparser
except ImportError:
    feedparser = None

from .signal_sources import RSS_FEEDS, HIGH_VALUE_KEYWORDS, MONETIZATION_MAP

DATA_DIR   = Path(__file__).parent.parent / 'data'
SEEN_FILE  = DATA_DIR / 'seen_articles.json'
TREND_FILE = DATA_DIR / 'trending.json'
DATA_DIR.mkdir(exist_ok=True)


def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set):
    SEEN_FILE.write_text(json.dumps(list(seen)))


def article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def score_article(title: str, summary: str) -> tuple[int, list, list]:
    """Score an article for trend relevance. Returns (score, matched_keywords, products)."""
    text = (title + ' ' + summary).lower()
    score = 0
    matched = []
    products = set()

    for tier, keywords in HIGH_VALUE_KEYWORDS.items():
        weight = {'immediate': 5, 'strong': 3, 'supporting': 1}[tier]
        for kw in keywords:
            if kw.lower() in text:
                score += weight
                matched.append(kw)

    # Map to monetization products
    for product_id, product in MONETIZATION_MAP.items():
        for kw in product['trigger_keywords']:
            if kw.lower() in text:
                products.add(product_id)
                break

    # Bonus for title keywords (title match = higher intent)
    title_lower = title.lower()
    for kw in HIGH_VALUE_KEYWORDS['immediate']:
        if kw.lower() in title_lower:
            score += 3  # Extra weight for title matches

    return score, matched, list(products)


def urgency_from_score(score: int) -> str:
    if score >= 20:   return 'immediate'
    if score >= 12:   return '24h'
    if score >= 7:    return '48h'
    if score >= 4:    return '72h'
    return 'low'


def parse_date(entry) -> Optional[datetime]:
    for attr in ['published_parsed', 'updated_parsed']:
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def fetch_feed(source: dict) -> list:
    """Fetch and parse one RSS feed. Returns list of raw articles."""
    if not feedparser:
        return []
    try:
        feed = feedparser.parse(source['url'])
        articles = []
        for entry in feed.entries[:20]:
            articles.append({
                'title':   entry.get('title', ''),
                'url':     entry.get('link', ''),
                'summary': re.sub('<[^>]+>', '', entry.get('summary', entry.get('description', ''))),
                'date':    parse_date(entry).isoformat() if parse_date(entry) else '',
                'source':  source['name'],
                'category': source['category'],
                'priority': source['priority'],
            })
        return articles
    except Exception as e:
        print(f"  [WARN] Feed {source['name']} failed: {e}")
        return []


def scrape_fresh_news(verbose: bool = True) -> list:
    """
    Scrape healthcare news sites for fresh stories when RSS is quiet.
    
    This function creates a marker file that signals the next cron run
    to manually scrape for fresh content. It's designed to work with
    OpenClaw's tools in the cron execution context.
    """
    # For now, just log that we need manual scraping
    # The actual scraping will happen in the cron context where web_fetch is available
    if verbose:
        print(f"  📰 Web scraping not yet implemented in trend_monitor.py")
        print(f"     Will rely on manual fresh content generation for now.")
    
    # TODO: Implement web scraping when web_fetch is available in this context
    # For now, return empty list
    return []


def scan_all_feeds(verbose: bool = True) -> list:
    """Scan all RSS feeds. Returns new scored articles above threshold."""
    seen = load_seen()
    new_articles = []

    for source in RSS_FEEDS:
        if verbose:
            print(f"  Scanning: {source['name']}...")
        articles = fetch_feed(source)
        for art in articles:
            aid = article_id(art['url'])
            if aid in seen:
                continue
            score, keywords, products = score_article(art['title'], art['summary'])
            if score < 3:  # Below minimum threshold
                seen.add(aid)
                continue
            art.update({
                'id':        aid,
                'score':     score,
                'keywords':  keywords[:10],
                'products':  products,
                'urgency':   urgency_from_score(score),
                'scanned_at': datetime.now(timezone.utc).isoformat(),
                'status':    'new',  # new | briefed | published | skipped
            })
            new_articles.append(art)
            seen.add(aid)

    save_seen(seen)
    new_articles.sort(key=lambda x: (-x['score'], x['date']))
    return new_articles


def load_trending() -> list:
    if TREND_FILE.exists():
        return json.loads(TREND_FILE.read_text())
    return []


def save_trending(articles: list):
    # Keep last 200 articles, sorted by score
    existing = load_trending()

    # Deduplicate by id
    existing_ids = {a['id'] for a in existing}
    new_only = [a for a in articles if a['id'] not in existing_ids]

    combined = new_only + existing
    combined.sort(key=lambda x: (-x['score'], x.get('scanned_at', '')))
    TREND_FILE.write_text(json.dumps(combined[:200], indent=2))
    return len(new_only)


def run_scan(verbose: bool = True) -> dict:
    """Main scan entrypoint. Returns summary dict."""
    if verbose:
        print(f"\n🔍 RCM Trend Engine — Scanning {len(RSS_FEEDS)} sources...")
        print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    new_articles = scan_all_feeds(verbose=verbose)
    
    # If RSS feeds are quiet (< 3 new articles), scrape news sites for fresh content
    if len(new_articles) < 3:
        if verbose:
            print(f"\n📰 RSS feeds quiet ({len(new_articles)} new). Scraping healthcare news sites...")
        scraped = scrape_fresh_news(verbose=verbose)
        new_articles.extend(scraped)
        if verbose and scraped:
            print(f"   Found {len(scraped)} fresh stories via web scraping")
    
    added = save_trending(new_articles)

    # Separate by urgency
    immediate = [a for a in new_articles if a['urgency'] == 'immediate']
    high      = [a for a in new_articles if a['urgency'] == '24h']
    medium    = [a for a in new_articles if a['urgency'] == '48h']

    if verbose:
        print(f"\n📊 Scan Results:")
        print(f"   New articles: {len(new_articles)} ({added} added to trending)")
        print(f"   🔴 Immediate (publish now):  {len(immediate)}")
        print(f"   🟡 High (publish <24h):      {len(high)}")
        print(f"   🟢 Medium (publish <48h):    {len(medium)}")
        if immediate:
            print(f"\n🚨 IMMEDIATE OPPORTUNITIES:")
            for a in immediate[:3]:
                print(f"   [{a['score']}] {a['title'][:80]}")
                print(f"        → {', '.join(a['products']) or 'general'} | Source: {a['source']}")

    return {
        'total_new': len(new_articles),
        'immediate': len(immediate),
        'high': len(high),
        'medium': len(medium),
        'top_stories': new_articles[:10],
    }


if __name__ == '__main__':
    run_scan(verbose=True)
