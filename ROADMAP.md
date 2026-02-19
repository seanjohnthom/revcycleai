# ROADMAP.md — Deductible Capital Product Ecosystem

> **The big picture:** Build Axlow, PayorMap, PPO Playbook, and RevCycleAI as revenue-generating tech assets,
> use them to establish industry credibility and deal flow, then deploy as the value creation engine
> inside a PE-backed RCM rollup (Deductible Capital, $25M Fund I).

---

## 🟢 LIVE / DONE

- [x] Kalshi trading bot — daily scan, Kelly sizing, Telegram P&L report
- [x] Axlow MVP — AI payor policy search tool
- [x] Axlow leads autopilot — 100 personalized leads, Monday hunter cron
- [x] PayorMap — dental PPO routing intelligence, Flask API, enterprise UI
- [x] RCM Trend Engine — 14 RSS feeds, trend scoring, content generation
- [x] RevCycleAI site — editorial news layout, all pages, MailerLite integration
- [x] Deductible Capital pitch deck — 11 slides, drafted tech layer + leadership slides

---

## 🔵 TONIGHT (Feb 19, 2026)

- [ ] Push revcycleai/ and payormap/ to GitHub
- [ ] Connect revcycleai.com → Netlify + set MAILERLITE_API_KEY + MAILERLITE_GROUP_ID
- [ ] Connect payormap.com → Railway
- [ ] Stripe integration for PayorMap (self-serve checkout)
- [ ] LinkedIn automation setup:
  - Create RevCycleAI company page (linkedin.com/company/setup/new)
  - Create developer app at developer.linkedin.com
  - Request "Share on LinkedIn" + "Manage Company Pages" products
  - Share Client ID + Client Secret → I build linkedin_poster.py + wire to 6am cron

---

## 🟡 NEXT (This Week)

### RevCycleAI
- [ ] Wire RCM Trend Engine → auto-publish to blog (write HTML article files on scan)
- [ ] Add Stripe checkout to /advertise for self-serve $300/week and $500/issue slots
- [ ] Verify revcycleai.com on Resend for outbound email (advertiser responses, media kit delivery)

### PayorMap
- [ ] Add 15–20 more payors to payors.json
- [ ] Build BCBS state-by-state routing detail (each state's dental network path)
- [ ] Add Stripe payment + 14-day trial flow
- [ ] Verify payormap.com on Resend for reports@payormap.com

### Axlow
- [ ] Redeploy sheets_webhook.gs in Google Apps Script
- [ ] Push personalization lines to Google Sheet
- [ ] Begin outreach sequence on 100 leads

### Deductible Capital Pitch Deck
- [ ] Add Slide: Proprietary Technology Layer (Axlow + PayorMap + PPO Playbook)
- [ ] Fill in Slide 5: Acquisition Criteria (target EBITDA, geography, specialty, revenue size)
- [ ] Enhance Leadership slide with full resume details
- [ ] Add operating partner / advisor to leadership slide
- [ ] Add deal pipeline mention (even "5 targets in early diligence")

---

## 🟠 PHASE 2 (Next 30–60 Days)

### Ad Ops System (RevCycleAI)
- [ ] Stripe checkout for ad slots — self-serve for sidebar ($300/wk) and newsletter ($500/issue)
- [ ] Creative submission form — logo upload, headline, copy, CTA URL, preferred dates
- [ ] Automated review pass — check image dimensions, link validity, basic content safety
- [ ] Telegram notification → one-tap approval → ad goes live
- [ ] `ads.json` config — site reads this to inject creatives into slots; no redeploy needed
- [ ] Auto-deactivation when campaign end date hits
- [ ] AI copy assist — I draft headline + body copy options for advertisers based on their product

### PayorMap
- [ ] Network change alerts — push notifications when payor/network relationships change
- [ ] Carve-out opportunity scanner — identify fee schedule leakage from umbrella networks
- [ ] Contract expiration calendar — manual entry, 90/60/30 day reminders
- [ ] Interactive US state map with BCBS routing overlay
- [ ] PayorMap sales autopilot — clone Axlow pipeline, ICP: VP Revenue Cycle at DSOs 25-500+ offices
- [ ] SOC 2 Stage 1: encryption at rest, access controls, audit logging

### PPO Playbook
- [ ] Define product scope: fee schedule negotiation system
- [ ] Build negotiation framework (step-by-step guide + templates)
- [ ] Build fee schedule comparison calculator
- [ ] Pricing: TBD (likely $497–997 one-time or annual subscription)
- [ ] Launch as first paid product in RevCycleAI /tools section

### RCM Trend Engine
- [ ] Auto-publish generated blog posts to revcycleai.com/blog
- [ ] LinkedIn auto-post via company page API (RevCycleAI page, anonymous)
- [ ] Weekly newsletter auto-draft → review → send via MailerLite

---

## 🔴 PHASE 3 (60–120 Days)

### Deductible Capital Fund Development
- [ ] Finalize pitch deck with all gaps filled
- [ ] Build financial model: fund-level returns, deal-level IRR, LP waterfall
- [ ] Identify and approach 2–3 anchor LPs (family offices, healthcare operators)
- [ ] Get 1–2 Axlow/PayorMap reference customers → case studies for fund deck
- [ ] Write 90-day value creation playbook (what we do to an acquired company in 90 days)
- [ ] Identify first acquisition target (motivated seller, $500K–$1M EBITDA, anesthesia or dental)
- [ ] Begin SBA or seller-financed deal structuring

### Revenue Milestones to Hit Before Fund Raise
- [ ] Axlow: $10K MRR (validates market, proves sales motion)
- [ ] PayorMap: 5 paying DSO customers (validates enterprise motion)
- [ ] RevCycleAI: 1,000 newsletter subscribers (validates audience)
- [ ] PPO Playbook: 50 sales (validates product-market fit)

### Content / Brand
- [ ] Publish Sean's operator POV articles under Deductible Capital brand (not RevCycleAI)
- [ ] LinkedIn presence for Deductible Capital (separate from RevCycleAI)
- [ ] Submit to HFMA, AAPC, ADA publications for guest articles
- [ ] Conference presence: HFMA Annual, MGMA, NADP

---

## 📌 ONGOING / AUTOMATED

| What | Schedule | Status |
|---|---|---|
| Kalshi market scan + trades | Daily 8am CT | ✅ Live |
| Kalshi P&L report → Telegram | Daily 9pm CT | ✅ Live |
| RCM Trend Engine scan + content | Daily 6am CT | ✅ Live |
| Axlow lead hunter (150-250 prospects) | Every Monday 7am CT | ✅ Live |
| LinkedIn auto-post (RevCycleAI page) | Daily after 6am scan | 🔧 Pending LinkedIn API setup |
| Newsletter auto-draft | Weekly | 🔧 Pending MailerLite setup |

---

## 💡 IDEAS / PARKING LOT

- **Resend domain verification** for payormap.com and revcycleai.com
- **Axlow affiliate program** — billing companies refer clients, earn % of subscription
- **PayorMap API** — sell data access to clearinghouses and practice management systems
- **RCM salary benchmarking tool** — free resource that drives massive search traffic
- **Denial rate benchmarking by specialty** — free tool, email-gated
- **Deductible Capital newsletter** — separate from RevCycleAI, PE/M&A focus, for future LPs
- **SOC 2 roadmap** — Stage 1 now, Type I at 3-6mo, Type II + pen test at 12mo+ (unlocks contract upload for PayorMap)
- **TrancheHealth reactivation** — consulting arm for Deductible Capital pre-fund (generates cash + deal flow)

---

*Last updated: February 19, 2026*
