#!/usr/bin/env python3
"""
DentalNet IQ — Claim Routing Engine
Given a payor + plan type + practice contracts, returns a probability-ranked
list of all possible network paths a claim could take.
"""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / 'data'


@dataclass
class RouteResult:
    path_id: str
    label: str
    path_type: str           # 'direct' | 'leased'
    umbrella: Optional[str]  # umbrella network id if leased
    plan_types: list
    probability: float       # 0.0–1.0
    confidence: str          # 'high' | 'medium' | 'low'
    silent_ppo_risk: bool
    override_risk: str       # 'none' | 'low' | 'medium' | 'high'
    notes: str
    alerts: list             # Any critical warnings


def load_data():
    payors = json.loads((DATA_DIR / 'payors.json').read_text())['payors']
    networks = json.loads((DATA_DIR / 'networks.json').read_text())['umbrella_networks']
    payor_map = {p['id']: p for p in payors}
    # Also index by aka
    for p in payors:
        for alias in p.get('aka', []):
            payor_map[alias.lower()] = p
        payor_map[p['name'].lower()] = p
    network_map = {n['id']: n for n in networks}
    return payor_map, network_map


PAYOR_MAP, NETWORK_MAP = load_data()


def find_payor(query: str) -> Optional[dict]:
    """Find payor by name, id, or alias (case-insensitive)."""
    q = query.lower().strip()
    # Exact id match
    if q in PAYOR_MAP:
        return PAYOR_MAP[q]
    # Partial match
    for key, payor in PAYOR_MAP.items():
        if q in key or key in q:
            return payor
    return None


def normalize_plan_type(plan_type: str) -> str:
    """Normalize common plan type variations."""
    pt = plan_type.lower().strip()
    if any(x in pt for x in ['ppo', 'preferred provider']):
        return 'PPO'
    if any(x in pt for x in ['hmo', 'dmo', 'dhmo']):
        return 'DHMO'
    if any(x in pt for x in ['fedvip', 'federal', 'government employee']):
        return 'FEDVIP'
    if 'pdp plus' in pt:
        return 'PDP Plus'
    if 'pdp' in pt:
        return 'PDP'
    if 'premier' in pt:
        return 'Premier'
    if 'indemnity' in pt or 'fee for service' in pt:
        return 'Indemnity'
    return plan_type.title()


def route_claim(
    payor_name: str,
    plan_type: str = None,
    practice_contracts: list = None,
    state: str = None,
) -> dict:
    """
    Core routing function.

    Args:
        payor_name: Insurance company name (e.g., "MetLife", "Cigna")
        plan_type: Plan type if known (e.g., "PDP Plus", "DPPO", "FEDVIP")
        practice_contracts: List of networks practice is contracted with
                           Can include payor names AND umbrella networks
                           e.g., ["MetLife", "Careington", "DenteMax"]
        state: Two-letter state code (used for geographic restrictions)

    Returns:
        dict with routing analysis, probability matrix, and alerts
    """
    practice_contracts = [c.lower().strip() for c in (practice_contracts or [])]
    plan_type_norm = normalize_plan_type(plan_type) if plan_type else None

    payor = find_payor(payor_name)
    if not payor:
        return {
            'error': f'Payor "{payor_name}" not found in database',
            'suggestion': 'Try a common alias (e.g., "UHC" for UnitedHealthcare)'
        }

    routes = []
    global_alerts = []

    # Check each network path
    for path in payor.get('network_paths', []):
        path_type = path.get('type', 'direct')
        umbrella_id = path.get('umbrella')
        path_plan_types = path.get('plan_types', [])

        # ── Plan type filter ──────────────────────────────────────────────
        plan_type_match = True
        plan_type_confidence = 1.0

        if plan_type_norm and path_plan_types:
            matched = any(
                plan_type_norm.lower() in pt.lower() or pt.lower() in plan_type_norm.lower()
                for pt in path_plan_types
            )
            if not matched:
                # Path exists but plan type doesn't match → very low probability
                plan_type_confidence = 0.05
                plan_type_match = False

        # ── Geographic filter ─────────────────────────────────────────────
        geo_restriction = path.get('geographic_restriction', '')
        geo_confidence = 1.0
        if geo_restriction and state:
            if state.upper() not in geo_restriction.upper():
                geo_confidence = 0.1  # Wrong state for this path

        # ── Practice contract check ───────────────────────────────────────
        has_direct_with_payor = any(
            payor['id'] in c or payor['name'].lower() in c
            or any(aka.lower() in c for aka in payor.get('aka', []))
            for c in practice_contracts
        ) if practice_contracts else None

        has_umbrella_contract = False
        if umbrella_id and practice_contracts:
            network = NETWORK_MAP.get(umbrella_id, {})
            network_aliases = [umbrella_id] + [a.lower() for a in network.get('aka', [])]
            has_umbrella_contract = any(
                any(alias in c for alias in network_aliases)
                for c in practice_contracts
            )

        # ── Compute adjusted probability ──────────────────────────────────
        base_prob = path.get('base_probability', 0.33)
        adjusted_prob = base_prob * plan_type_confidence * geo_confidence

        # Boost/reduce based on contract knowledge
        contract_note = ''
        if practice_contracts:
            if path_type == 'direct' and has_direct_with_payor:
                adjusted_prob = min(1.0, adjusted_prob * 1.4)
                contract_note = '✓ Practice has direct contract with this payor'
            elif path_type == 'direct' and not has_direct_with_payor:
                adjusted_prob *= 0.3
                contract_note = '✗ No direct contract found — path less likely'
            elif path_type == 'leased' and has_umbrella_contract:
                adjusted_prob = min(1.0, adjusted_prob * 1.3)
                contract_note = f'✓ Practice has {NETWORK_MAP.get(umbrella_id, {}).get("name", umbrella_id)} contract'
            elif path_type == 'leased' and not has_umbrella_contract:
                adjusted_prob *= 0.4
                contract_note = f'✗ No {NETWORK_MAP.get(umbrella_id, {}).get("name", umbrella_id)} contract — path less likely'

        # ── Build alerts ──────────────────────────────────────────────────
        alerts = []
        if path.get('silent_ppo_alert'):
            alerts.append('⚠️ SILENT PPO RISK: This path may reprice claims without notifying the practice')
        if path.get('plan_type_critical'):
            alerts.append('🔴 PLAN TYPE CRITICAL: This path only applies to specific plan types — verify before assuming in-network status')
        if path.get('override_risk') in ('medium', 'high'):
            alerts.append(f"⚠️ OVERRIDE RISK ({path['override_risk'].upper()}): Leased network rate may override your direct contract rate")
        if geo_restriction and not state:
            alerts.append(f'📍 GEOGRAPHIC RESTRICTION: {geo_restriction} — provide state for accurate routing')
        if contract_note:
            alerts.append(contract_note)

        # ── Confidence rating ─────────────────────────────────────────────
        if adjusted_prob >= 0.6:
            confidence = 'high'
        elif adjusted_prob >= 0.25:
            confidence = 'medium'
        else:
            confidence = 'low'

        umbrella_name = None
        if umbrella_id:
            umbrella_name = NETWORK_MAP.get(umbrella_id, {}).get('name', umbrella_id)

        routes.append(RouteResult(
            path_id=path['path_id'],
            label=path['label'],
            path_type=path_type,
            umbrella=umbrella_name,
            plan_types=path_plan_types,
            probability=round(adjusted_prob, 3),
            confidence=confidence,
            silent_ppo_risk=bool(path.get('silent_ppo_alert')),
            override_risk=path.get('override_risk', 'none'),
            notes=path.get('notes', ''),
            alerts=alerts,
        ))

    # Sort by probability descending
    routes.sort(key=lambda r: r.probability, reverse=True)

    # Normalize probabilities to sum to 1.0
    total = sum(r.probability for r in routes)
    if total > 0:
        for r in routes:
            r.probability = round(r.probability / total, 3)

    # Global alerts
    if payor.get('silent_ppo_risk') in ('high', 'very_high'):
        global_alerts.append(
            f"⚠️ HIGH SILENT PPO RISK: {payor['name']} is a frequent silent PPO offender — verify routing on every claim"
        )

    # Build routing rules
    routing_rules = payor.get('routing_rules', [])

    return {
        'payor': payor['name'],
        'payor_id': payor['id'],
        'plan_type_queried': plan_type_norm or 'Not specified',
        'state': state or 'Not specified',
        'practice_contracts_provided': len(practice_contracts) > 0,
        'confusion_score': payor.get('confusion_score', 0),
        'silent_ppo_risk': payor.get('silent_ppo_risk', 'unknown'),
        'routes': [
            {
                'rank': i + 1,
                'path_id': r.path_id,
                'label': r.label,
                'type': r.path_type,
                'umbrella_network': r.umbrella,
                'applicable_plan_types': r.plan_types,
                'probability': r.probability,
                'confidence': r.confidence,
                'override_risk': r.override_risk,
                'silent_ppo_risk': r.silent_ppo_risk,
                'notes': r.notes,
                'alerts': r.alerts,
            }
            for i, r in enumerate(routes)
        ],
        'routing_rules': routing_rules,
        'global_alerts': global_alerts,
        'recommendation': _build_recommendation(routes, payor),
    }


def _build_recommendation(routes: list, payor: dict) -> str:
    if not routes:
        return 'Unable to determine routing — insufficient data.'

    top = routes[0]
    second = routes[1] if len(routes) > 1 else None

    if top.confidence == 'high' and top.probability >= 0.60:
        rec = f"Most likely path: {top.label} ({top.probability:.0%} probability)."
    elif second and (top.probability - second.probability) < 0.15:
        rec = f"Ambiguous routing: {top.label} ({top.probability:.0%}) vs {second.label} ({second.probability:.0%}) — verify with payor."
    else:
        rec = f"Probable path: {top.label} ({top.probability:.0%}) — medium confidence."

    if any(r.silent_ppo_risk for r in routes[:2]):
        rec += " ⚠️ Monitor EOB for silent PPO repricing."

    return rec


if __name__ == '__main__':
    # Quick test
    import json

    print("\n=== TEST 1: MetLife, plan type unknown ===")
    result = route_claim('MetLife')
    print(f"Payor: {result['payor']} | Silent PPO Risk: {result['silent_ppo_risk']}")
    for r in result['routes']:
        print(f"  [{r['rank']}] {r['label']} — {r['probability']:.0%} ({r['confidence']})")
        for alert in r['alerts']:
            print(f"      {alert}")
    print(f"  → {result['recommendation']}")

    print("\n=== TEST 2: MetLife PDP Plus, with Careington contract ===")
    result = route_claim('MetLife', plan_type='PDP Plus', practice_contracts=['Careington', 'Delta Dental'])
    print(f"Payor: {result['payor']} | Plan: {result['plan_type_queried']}")
    for r in result['routes']:
        print(f"  [{r['rank']}] {r['label']} — {r['probability']:.0%} ({r['confidence']})")
        for alert in r['alerts']:
            print(f"      {alert}")
    print(f"  → {result['recommendation']}")

    print("\n=== TEST 3: UHC with no contract info ===")
    result = route_claim('UnitedHealthcare')
    print(f"Payor: {result['payor']} | Silent PPO Risk: {result['silent_ppo_risk']}")
    for r in result['routes']:
        print(f"  [{r['rank']}] {r['label']} — {r['probability']:.0%}")
    print(f"  → {result['recommendation']}")
    for alert in result['global_alerts']:
        print(f"  {alert}")
