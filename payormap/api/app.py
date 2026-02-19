#!/usr/bin/env python3
"""PayorMap — Flask API"""
import sys, json, os, feedparser
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_from_directory
from engine.router import route_claim

app   = Flask(__name__)
DATA  = Path(__file__).parent.parent / 'data'
UI    = Path(__file__).parent.parent / 'ui'


def load(filename):
    return json.loads((DATA / filename).read_text())


@app.route('/')
def index():
    return send_from_directory(UI, 'index.html')


@app.route('/api/route', methods=['POST'])
def api_route():
    d = request.json or {}
    payor     = (d.get('payor') or '').strip()
    plan_type = (d.get('plan_type') or '').strip() or None
    contracts = d.get('practice_contracts') or []
    state     = (d.get('state') or '').strip() or None
    if not payor:
        return jsonify({'error': 'payor is required'}), 400
    return jsonify(route_claim(payor, plan_type=plan_type, practice_contracts=contracts, state=state))


@app.route('/api/payors')
def api_payors():
    payors = load('payors.json')['payors']
    return jsonify([{'id': p['id'], 'name': p['name'], 'aka': p.get('aka', []),
                     'confusion_score': p.get('confusion_score', 0),
                     'silent_ppo_risk': p.get('silent_ppo_risk', 'unknown')} for p in payors])


@app.route('/api/networks')
def api_networks():
    return jsonify(load('networks.json')['umbrella_networks'])


@app.route('/api/state-routing')
def api_state_routing():
    return jsonify(load('state_routing.json'))


@app.route('/api/cdt')
def api_cdt():
    try:
        data = load('cdt_allowables.json')
        q    = request.args.get('q', '').lower()
        cat  = request.args.get('category', '')
        codes = data.get('codes', [])
        if q:
            codes = [c for c in codes if q in c['code'].lower() or q in c['description'].lower()]
        if cat:
            codes = [c for c in codes if c.get('category','').lower() == cat.lower()]
        return jsonify({'codes': codes, 'metadata': data.get('metadata', {}), 'total': len(codes)})
    except FileNotFoundError:
        return jsonify({'error': 'CDT data not yet available', 'codes': [], 'total': 0})


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'service': 'payormap', 'version': '1.0.0'})


@app.route('/api/news')
def api_news():
    data    = load('news_feed.json')
    alerts  = data.get('network_alerts', [])
    sources = data.get('feed_sources', [])
    articles = []
    for src in sources[:3]:  # Try top 3 sources
        try:
            feed = feedparser.parse(src['rss'])
            for entry in feed.entries[:3]:
                articles.append({
                    'title':   entry.get('title', ''),
                    'summary': entry.get('summary', '')[:200] + '...',
                    'link':    entry.get('link', ''),
                    'date':    entry.get('published', ''),
                    'source':  src['name'],
                    'type':    src['type'],
                })
        except Exception:
            pass
    return jsonify({'alerts': alerts, 'articles': articles})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(debug=False, host='0.0.0.0', port=port)
