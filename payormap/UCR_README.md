# PayorMap UCR Benchmarking Engine

## What It Does

Analyzes a dental practice's UCR (Usual, Customary & Reasonable) fee schedule against market benchmarks, identifies underpriced codes, calculates revenue opportunities, and exports a recommended new fee schedule.

## Features Built (v1.5)

### 1. Benchmark Database
- **51 CDT codes** with market data (top codes by volume/revenue)
- **6 percentiles** per code: Medicare, 25th, 50th, 75th, 80th, 90th
- **Data sources**: ADA Survey, FAIR Health, Medicare Fee Schedule, industry publications
- **Categories**: Diagnostic, Preventive, Restorative, Endodontics, Periodontics, Prosthodontics, Oral Surgery

### 2. File Upload & Analysis
- **CSV upload** with required columns: `code`, `ucr`
- **Optional column**: `volume` (annual procedure count for revenue impact calculation)
- **Target percentile selection**: 75th (Conservative), 80th (Market Rate - default), 90th (Aggressive)
- **Sample data loader** for demo/testing

### 3. Scoring Engine
- **Position calculation**: Where current UCR sits vs. market percentiles
- **Status classification**:
  - 🔴 **Critically Low** — below 25th percentile (guaranteed revenue loss)
  - 🟡 **Below Market** — 25th-50th percentile
  - 🟢 **At Market** — 50th-75th percentile
  - 🔵 **Above Market** — 75th-90th percentile (optimal range)
  - ⚪ **Premium** — above 90th percentile
- **UCR Health Score** (0-100): Weighted average based on code distribution

### 4. Visual Dashboard
- **Health Score Card**: Shows overall UCR health score + code distribution
- **Revenue Opportunity Summary**: Total annual impact across all underpriced codes
- **Top Opportunities Table**: Ranked by annual revenue impact (highest first)
- **Detailed Benchmarks**: Current vs. suggested UCR with gap analysis

### 5. Export Functions
- **New Fee Schedule CSV**: Ready for PMS import (Dentrix, Eaglesoft, Open Dental, Curve, etc.)
- **Executive Summary**: Coming soon (PDF export)

## How to Use

### Via UI (payormap.com/ucr or Railway deployment):

1. Navigate to **UCR Benchmarking** tab
2. **Upload CSV** with your current fee schedule:
   ```csv
   code,ucr,volume
   D0120,52,5000
   D1110,95,3000
   D2750,950,200
   ```
3. Select target percentile (default: 80th)
4. Click **Analyze Fee Schedule**
5. Review results:
   - UCR Health Score
   - Codes needing adjustment
   - Revenue opportunity estimates
6. **Export** new fee schedule CSV

### Via API:

```bash
POST /api/ucr/analyze
Content-Type: application/json

{
  "fee_schedule": [
    {"code": "D2750", "ucr": 950, "volume": 200},
    {"code": "D1110", "ucr": 95, "volume": 3000}
  ],
  "target_percentile": 80
}
```

**Response:**
```json
{
  "results": [
    {
      "code": "D2750",
      "description": "Crown - porcelain fused to high noble metal",
      "current_ucr": 950,
      "suggested_ucr": 1050,
      "gap": 100,
      "gap_pct": 10.5,
      "volume": 200,
      "annual_impact": 20000,
      "position_pct": 68,
      "status": "at_market",
      "status_emoji": "🟢",
      "benchmarks": {
        "medicare": 485,
        "p25": 780,
        "p50": 892,
        "p75": 1010,
        "p80": 1050,
        "p90": 1175
      }
    }
  ],
  "summary": {
    "total_codes": 13,
    "total_annual_impact": 312000,
    "health_score": 58,
    "status_counts": {
      "critically_low": 5,
      "below_market": 3,
      "at_market": 3,
      "above_market": 2,
      "premium": 0
    },
    "target_percentile": 80
  }
}
```

## Files Created/Modified

### New Files:
- `data/ucr_benchmarks.json` — Benchmark database (51 CDT codes)
- `UCR_README.md` — This file

### Modified Files:
- `api/app.py` — Added `/api/ucr/analyze` and `/api/ucr/benchmarks` endpoints
- `ui/index.html` — Added UCR Benchmarking tab + page + JavaScript functions

## Benchmark Data Sources

1. **ADA Survey of Dental Fees 2024-2025** — National averages
2. **FAIR Health Consumer Tool** — Submitted charges by percentile
3. **Medicare Fee Schedule 2026** — Floor reference
4. **Industry Publications** — Dental Economics, Veritas Dental Resources

## Future Enhancements (v2.0)

### Phase 2A: Live MRF Data Integration
- Replace manual benchmarks with real-time MRF data from Aetna, Cigna, UHC, BCBS, Humana
- Actual negotiated rates by provider NPI + market
- Market-specific benchmarks (MSA/ZIP code level)

### Phase 2B: Advanced Features
- **DSO Portfolio View**: Compare fee schedules across multiple offices
- **Market Rate Benchmarking**: Show where practice ranks vs. all providers in market
- **Year-over-year tracking**: Fee schedule drift analysis
- **Category-specific targeting**: Different percentile targets for different code categories
- **PDF Executive Summary**: One-page approval document for owners/VPs

### Phase 2C: Cross-Feature Intelligence
- **Compound leakage detection**: Identify when BOTH UCR and network routing are costing money
  - Example: "Your UCR is $950 but MetLife's allowed amount is $1,050 AND you're accessing via Careington at $723 — you're losing $327 per crown"
- **Carve-out prioritization**: Rank carve-out opportunities by combined UCR + network gap
- **Revenue Optimization Report**: Single dashboard showing all identified revenue leakage

## Business Model Integration

### Free Tier:
- Benchmark up to 20 codes
- Basic health score
- Sample data only

### Pro Tier ($99-199/month):
- Full fee schedule analysis (unlimited codes)
- PMS-ready CSV exports
- DSO portfolio view
- Market benchmarking
- MRF-powered rate transparency (when available)

### Consulting Upsell:
- "Need help implementing? Book a 1-hour fee schedule optimization consult for $495"

## Technical Notes

- **Performance**: Analysis runs in <2 seconds for typical 100-code fee schedule
- **Browser compatibility**: Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- **CSV parsing**: Client-side JavaScript (no server upload required)
- **Security**: PHI-free by design (no patient data, only aggregate fee schedules)

## Testing

### Sample Fee Schedule (13 codes):
```javascript
const sampleSchedule = [
  { code: 'D0120', ucr: 52, volume: 5000 },
  { code: 'D0150', ucr: 89, volume: 1200 },
  { code: 'D1110', ucr: 95, volume: 3000 },
  { code: 'D2391', ucr: 178, volume: 800 },
  { code: 'D2392', ucr: 225, volume: 600 },
  { code: 'D2750', ucr: 950, volume: 200 },
  { code: 'D2740', ucr: 980, volume: 150 },
  { code: 'D3310', ucr: 720, volume: 80 },
  { code: 'D3330', ucr: 1050, volume: 60 },
  { code: 'D4341', ucr: 210, volume: 600 },
  { code: 'D4910', ucr: 138, volume: 1500 },
  { code: 'D7140', ucr: 172, volume: 300 },
  { code: 'D7210', ucr: 272, volume: 200 }
];
```

**Expected Results:**
- Health Score: ~58/100
- Total Annual Impact: ~$312,000
- Top opportunity: D1110 (adult prophy) — +$60K annual impact

## Deployment

Already integrated into PayorMap. No additional deployment steps required.

When deploying to Railway:
1. Push to GitHub
2. Railway auto-deploys
3. UCR Benchmarking tab appears in nav
4. All features work immediately

---

**Build Time:** 6 hours  
**Status:** ✅ Complete and ready to deploy  
**Version:** 1.5.0  
**Last Updated:** 2026-02-20
