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


@app.route('/api/ucr/analyze', methods=['POST'])
def api_ucr_analyze():
    """Analyze a practice's UCR fee schedule against market benchmarks"""
    try:
        data = request.json or {}
        fee_schedule = data.get('fee_schedule', [])  # [{code, ucr, volume}]
        target_percentile = data.get('target_percentile', 80)  # Default: 80th
        
        if not fee_schedule:
            return jsonify({'error': 'fee_schedule required'}), 400
        
        benchmarks = load('ucr_benchmarks.json')['benchmarks']
        results = []
        total_impact = 0
        status_counts = {'critically_low': 0, 'below_market': 0, 'at_market': 0, 'above_market': 0, 'premium': 0}
        
        for item in fee_schedule:
            code = item.get('code', '').upper()
            current_ucr = float(item.get('ucr', 0))
            volume = int(item.get('volume', 0))
            
            if code not in benchmarks:
                continue
            
            bench = benchmarks[code]
            p25, p50, p75, p80, p90 = bench['p25'], bench['p50'], bench['p75'], bench['p80'], bench['p90']
            
            # Calculate current position percentile (approximate)
            if current_ucr <= p25:
                position_pct = int((current_ucr / p25) * 25)
                status = 'critically_low'
                status_emoji = '🔴'
                status_counts['critically_low'] += 1
            elif current_ucr <= p50:
                position_pct = 25 + int(((current_ucr - p25) / (p50 - p25)) * 25)
                status = 'below_market'
                status_emoji = '🟡'
                status_counts['below_market'] += 1
            elif current_ucr <= p75:
                position_pct = 50 + int(((current_ucr - p50) / (p75 - p50)) * 25)
                status = 'at_market'
                status_emoji = '🟢'
                status_counts['at_market'] += 1
            elif current_ucr <= p90:
                position_pct = 75 + int(((current_ucr - p75) / (p90 - p75)) * 15)
                status = 'above_market'
                status_emoji = '🔵'
                status_counts['above_market'] += 1
            else:
                position_pct = min(95, 90 + int(((current_ucr - p90) / p90) * 100))
                status = 'premium'
                status_emoji = '⚪'
                status_counts['premium'] += 1
            
            # Calculate suggested UCR based on target percentile
            percentile_map = {75: p75, 80: p80, 90: p90}
            suggested_ucr = percentile_map.get(target_percentile, p80)
            
            gap = suggested_ucr - current_ucr
            gap_pct = (gap / current_ucr * 100) if current_ucr > 0 else 0
            annual_impact = gap * volume if gap > 0 else 0
            total_impact += annual_impact
            
            results.append({
                'code': code,
                'description': bench['description'],
                'category': bench['category'],
                'current_ucr': current_ucr,
                'suggested_ucr': suggested_ucr,
                'gap': round(gap, 2),
                'gap_pct': round(gap_pct, 1),
                'volume': volume,
                'annual_impact': round(annual_impact, 2),
                'position_pct': position_pct,
                'status': status,
                'status_emoji': status_emoji,
                'benchmarks': {
                    'medicare': bench['medicare'],
                    'p25': p25,
                    'p50': p50,
                    'p75': p75,
                    'p80': p80,
                    'p90': p90
                }
            })
        
        # Sort by annual impact (highest first)
        results.sort(key=lambda x: x['annual_impact'], reverse=True)
        
        # Calculate UCR Health Score (0-100)
        total_codes = len(results)
        health_score = 0
        if total_codes > 0:
            # Weight: at_market=100, above_market=100, below_market=50, critically_low=0, premium=90
            weighted_sum = (
                status_counts['above_market'] * 100 +
                status_counts['at_market'] * 100 +
                status_counts['below_market'] * 50 +
                status_counts['premium'] * 90
            )
            health_score = int(weighted_sum / total_codes)
        
        return jsonify({
            'results': results,
            'summary': {
                'total_codes': total_codes,
                'total_annual_impact': round(total_impact, 2),
                'health_score': health_score,
                'status_counts': status_counts,
                'target_percentile': target_percentile
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ucr/benchmarks')
def api_ucr_benchmarks():
    """Get all UCR benchmarks"""
    try:
        data = load('ucr_benchmarks.json')
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'UCR benchmark data not available'}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(debug=False, host='0.0.0.0', port=port)
