#!/usr/bin/env python3
"""RCM Trend Engine — Flask API + Dashboard"""
import sys, json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'engine'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request, send_from_directory

DATA_DIR    = Path(__file__).parent.parent / 'data'
CONTENT_DIR = Path(__file__).parent.parent / 'content'
UI_DIR      = Path(__file__).parent.parent / 'ui'

app = Flask(__name__)


def load_trending():
    f = DATA_DIR / 'trending.json'
    return json.loads(f.read_text()) if f.exists() else []


def load_briefs():
    briefs = []
    for f in sorted(CONTENT_DIR.glob('*.json'), reverse=True)[:50]:
        try:
            briefs.append(json.loads(f.read_text()))
        except Exception:
            pass
    return briefs


@app.route('/')
def index():
    return send_from_directory(UI_DIR, 'index.html')


@app.route('/api/trends')
def api_trends():
    articles = load_trending()
    urgency  = request.args.get('urgency', '')
    category = request.args.get('category', '')
    status   = request.args.get('status', '')
    limit    = int(request.args.get('limit', 50))

    if urgency:
        articles = [a for a in articles if a.get('urgency') == urgency]
    if category:
        articles = [a for a in articles if a.get('category') == category]
    if status:
        articles = [a for a in articles if a.get('status') == status]

    return jsonify({'articles': articles[:limit], 'total': len(articles)})


@app.route('/api/trends/<article_id>/brief', methods=['POST'])
def api_generate_brief(article_id):
    from content_engine import generate_brief, save_brief
    articles = load_trending()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    brief = generate_brief(article)
    path  = save_brief(brief)
    # Mark article as briefed
    for a in articles:
        if a['id'] == article_id:
            a['status'] = 'briefed'
    (DATA_DIR / 'trending.json').write_text(json.dumps(articles, indent=2))
    return jsonify(brief)


@app.route('/api/trends/<article_id>/linkedin', methods=['POST'])
def api_linkedin_post(article_id):
    from content_engine import generate_brief, generate_linkedin_post
    articles = load_trending()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    brief = generate_brief(article)
    post  = generate_linkedin_post(brief)
    return jsonify({'post': post, 'brief': brief})


@app.route('/api/trends/<article_id>/thread', methods=['POST'])
def api_x_thread(article_id):
    from content_engine import generate_brief, generate_x_thread
    articles = load_trending()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    brief  = generate_brief(article)
    thread = generate_x_thread(brief)
    return jsonify({'thread': thread, 'brief': brief})


@app.route('/api/scan', methods=['POST'])
def api_scan():
    from trend_monitor import run_scan
    result = run_scan(verbose=False)
    return jsonify(result)


@app.route('/api/briefs')
def api_briefs():
    return jsonify({'briefs': load_briefs(), 'total': len(load_briefs())})


@app.route('/api/stats')
def api_stats():
    articles = load_trending()
    briefs   = load_briefs()
    now      = datetime.now()

    immediate = [a for a in articles if a.get('urgency') == 'immediate' and a.get('status') == 'new']
    high      = [a for a in articles if a.get('urgency') == '24h' and a.get('status') == 'new']
    product_counts = {}
    for a in articles:
        for p in a.get('products', []):
            product_counts[p] = product_counts.get(p, 0) + 1

    return jsonify({
        'total_tracked':   len(articles),
        'briefs_generated': len(briefs),
        'needs_action':    len(immediate) + len(high),
        'immediate':       len(immediate),
        'high_priority':   len(high),
        'by_product':      product_counts,
        'last_scan':       articles[0].get('scanned_at', '') if articles else '',
        'sources_active':  len([f for f in __import__('signal_sources').RSS_FEEDS]),
    })


if __name__ == '__main__':
    app.run(debug=True, port=5051)
