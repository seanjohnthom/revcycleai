#!/usr/bin/env python3
"""
Enrich incomplete leads using multi-source email lookup.
Hunter.io → Skrapp.io → Apollo.io → Pattern matching
"""
import json, requests, time
from pathlib import Path
from email_enrichment import find_email, verify_email

WORKSPACE    = Path(__file__).parent
try:
    config = json.loads((WORKSPACE / 'config.json').read_text())
    SCRIPT_URL = config.get('apps_script_url')
except:
    SCRIPT_URL = None

# Known domains for target companies
DOMAINS = {
    'HCA Healthcare':                        'hcahealthcare.com',
    'CommonSpirit Health':                   'commonspirit.org',
    'Ascension Health':                      'ascension.org',
    'UPMC':                                  'upmc.edu',
    'Tenet Healthcare':                      'tenethealth.com',
    'AdventHealth':                          'adventhealth.com',
    'Northwell Health':                      'northwell.edu',
    'Banner Health':                         'bannerhealth.com',
    'Baylor Scott & White Health':           'bswhealth.com',
    'Advocate Health':                       'advocatehealth.com',
    'Providence Health & Services':          'providence.org',
    'Sanford Health':                        'sanfordhealth.org',
    'Intermountain Health':                  'intermountainhealth.org',
    'Memorial Hermann Health System':        'memorialhermann.org',
    'Piedmont Healthcare':                   'piedmont.org',
    'Sutter Health':                         'sutterhealth.org',
    'LifePoint Health':                      'lpnt.net',
    'Community Health Systems (CHS)':        'chs.net',
    'Trinity Health':                        'trinity-health.org',
    'Universal Health Services (UHS)':       'uhsinc.com',
    'Ochsner Health':                        'ochsner.org',
    'Beaumont Health':                       'beaumont.org',
    'Spectrum Health':                       'spectrumhealth.org',
    'WellSpan Health':                       'wellspan.org',
    'Froedtert Health':                      'froedtert.com',
    'Geisinger':                             'geisinger.org',
    'Renown Health':                         'renown.org',
    'OSF HealthCare':                        'osfhealthcare.org',
    'Covenant Health':                       'covenanthealth.com',
    'Franciscan Missionaries':               'fmolhs.org',
    # DSOs
    'Heartland Dental':                      'heartland.com',
    'Pacific Dental Services':               'pacificdentalservices.com',
    'Aspen Dental':                          'aspendental.com',
    'Smile Brands':                          'smilebrands.com',
    'Western Dental':                        'westerndentalgroup.com',
    'Dental Care Alliance':                  'dentalcarealliance.com',
    'Affordable Care':                       'affordablecare.com',
    # ASCs
    'USPI':                                  'uspi.com',
    'SurgCenter Development':                'surgcenterdevelopment.com',
    'NovaBay Pharmaceuticals':               'novabay.com',
    # RCM Companies
    'Omega Healthcare':                      'omegahealthcare.com',
    'GeBBS Healthcare':                      'gebbs.com',
    'Conifer Health Solutions':              'coniferhealth.com',
    'Parallon':                              'parallon.com',
    'Ensemble Health Partners':              'ensemblehp.com',
    'nThrive':                               'nthrive.com',
    'Navicure':                              'navicure.com',
    'MedAssets':                             'medassets.com',
    'Streamline Health':                     'streamlinehealth.net',
    'Precyse':                               'precyse.com',
}

RCM_KEYWORDS = [
    'revenue cycle', 'rcm', 'billing', 'denial', 'coding',
    'patient financial', 'prior auth', 'credentialing', 'accounts receivable'
]

def get_domain(company):
    for name, domain in DOMAINS.items():
        if name.lower() in company.lower() or company.lower() in name.lower():
            return domain
    return None

def hunter_domain_search(domain, title_keywords):
    """Search Hunter.io for people at a domain matching RCM titles."""
    url = f'https://api.hunter.io/v2/domain-search'
    params = {
        'domain': domain,
        'api_key': HUNTER_KEY,
        'limit': 10,
        'type': 'personal',
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        emails = data.get('data', {}).get('emails', [])
        # Filter for RCM-related titles
        matches = []
        for e in emails:
            person_title = (e.get('position') or '').lower()
            if any(kw in person_title for kw in RCM_KEYWORDS):
                matches.append(e)
        # Fall back to any senior person if no RCM match
        if not matches:
            matches = [e for e in emails if e.get('position') and
                      any(t in (e.get('position') or '').lower()
                          for t in ['vp', 'vice president', 'director', 'senior', 'manager'])]
        return matches[:3]
    except Exception as ex:
        print(f'  Hunter error for {domain}: {ex}')
        return []

def hunter_email_finder(first, last, domain):
    url = 'https://api.hunter.io/v2/email-finder'
    params = {'domain': domain, 'first_name': first, 'last_name': last, 'api_key': HUNTER_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        d = data.get('data', {})
        if d.get('email'):
            return d['email'], d.get('confidence', 0)
    except Exception:
        pass
    return None, 0

def push_updated(lead):
    try:
        r = requests.post(SCRIPT_URL, json=lead, timeout=15)
        return r.json().get('ok', False)
    except Exception:
        return False


if __name__ == '__main__':
    with open(WORKSPACE / 'batch_parsed.json') as f:
        leads = json.load(f)

    incomplete = [(i, l) for i, l in enumerate(leads) if not l.get('first_name')]
    print(f'Enriching {len(incomplete)} incomplete leads via Hunter.io...\n')

    enriched = 0
    email_found = 0
    skipped = 0

    for i, (idx, lead) in enumerate(incomplete):
        company = lead.get('company', '')
        title   = lead.get('title', '')
        domain  = get_domain(company)

        if not domain:
            print(f'  [{i+1}/{len(incomplete)}] {company} — no domain mapping, skipping')
            skipped += 1
            continue

        print(f'  [{i+1}/{len(incomplete)}] {company} ({domain}) — searching...')
        matches = hunter_domain_search(domain, title)

        if matches:
            best = matches[0]
            first = best.get('first_name', '')
            last  = best.get('last_name', '')
            email = best.get('value', '')
            conf  = best.get('confidence', 0)
            pos   = best.get('position', '')

            if first and last:
                lead['first_name']  = first
                lead['last_name']   = last
                lead['notes']       = (lead.get('notes') or '') + ' | Name via Hunter.io domain search'
                enriched += 1

                if email:
                    lead['email']        = email
                    lead['email_source'] = f'Hunter.io ({conf}% confidence)'
                    email_found += 1
                    print(f'    ✓ Found: {first} {last} | {email} ({conf}%) | {pos}')
                else:
                    # Try direct finder
                    found_email, found_conf = hunter_email_finder(first, last, domain)
                    if found_email:
                        lead['email']        = found_email
                        lead['email_source'] = f'Hunter.io finder ({found_conf}%)'
                        email_found += 1
                        print(f'    ✓ Found: {first} {last} | {found_email} ({found_conf}%) | {pos}')
                    else:
                        print(f'    ✓ Name only: {first} {last} | {pos} (no email found)')

                leads[idx] = lead

                # Push updated row to sheet
                push_updated(lead)
        else:
            print(f'    ✗ No matches found')
            skipped += 1

        time.sleep(0.5)

    # Save updated JSON
    with open(WORKSPACE / 'batch_parsed.json', 'w') as f:
        json.dump(leads, f, indent=2)

    # Save report
    report = f"""# Enrichment Report — {__import__('datetime').date.today()}

## Results
- Total incomplete leads: {len(incomplete)}
- Names found: {enriched}
- Emails found: {email_found}
- Skipped (no domain): {skipped}

## Still incomplete: {len(incomplete) - enriched}
"""
    (WORKSPACE / 'enrichment_report.md').write_text(report)

    print(f'\n{"="*50}')
    print(f'Names found:  {enriched}/{len(incomplete)}')
    print(f'Emails found: {email_found}/{len(incomplete)}')
    print(f'Skipped:      {skipped}')
    print('batch_parsed.json updated.')
