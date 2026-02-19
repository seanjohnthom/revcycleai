# RevCycleAI Cold Outreach Sequence
## Axlow Lead List → RevCycleAI Subscribers → Axlow Trials

---

## Sequence Overview

| Email | Day | Subject | Goal |
|---|---|---|---|
| Email 1 | Day 0 | Free: See how your denial rate compares to peers | Tool offer, first touch |
| Email 2 | Day 4 | What are RCM directors earning in your market? | Second tool, soft newsletter pitch |
| Email 3 | Day 10 | The tool that helps with those denials | Axlow intro — warm by now |

**Stop sequence** if they: click any link, subscribe to newsletter, or reply.

---

## Email 1 — Day 0
**Subject:** Free: See how your denial rate compares to peers (by specialty)
**Preview text:** Takes 30 seconds, no login, no PHI required.
**File:** `email-1-denial-tool.html`

**Personalization tokens:**
- `{{first_name}}` — first name
- `{{personalization_line}}` — use the personalization_line from master_leads.csv
- `{{unsubscribe_url}}` — MailerLite auto-populates
- `{{company_name}}` — your company name (for CAN-SPAM footer)
- `{{company_address}}` — your address (for CAN-SPAM footer)

**Notes:**
- Send Tuesday or Wednesday 8–10am CT
- Use sender name: Alex | sender email: alex@revcycleai.com (once domain verified)
- The personalization_line should reference their specific company/role/pain point

---

## Email 2 — Day 4
**Subject:** What are RCM directors earning in your market?
**Preview text:** Free salary benchmarking by role, region, and practice type — 30 seconds.
**File:** `email-2-salary-tool.html`

**Notes:**
- Only send to those who did NOT click Email 1
- References Email 1 casually — feels like a human follow-up, not a drip sequence
- Newsletter CTA is inline, low pressure
- Send Thursday or Friday 8–10am CT

---

## Email 3 — Day 10
**Subject:** The tool that helps with those denials
**Preview text:** One more thing — built specifically to cut down denial research time.
**File:** `email-3-axlow-intro.html`

**Notes:**
- Only send to those who did NOT click Emails 1 or 2
- First time Axlow is mentioned by name — they've had 10 days of value-first touchpoints
- "I'll only reach out again if I build something worth your time" — closes the sequence gracefully
- No hard pitch language — let the product sell itself
- Send Tuesday 8–10am CT

---

## MailerLite Setup

1. **Create campaign group:** "RevCycleAI — Axlow Leads Outreach"
2. **Import leads:** Upload master_leads.csv — map first_name, email, company, personalization_line
3. **Create automation:** Trigger = contact added to group
   - Wait 0 days → Send Email 1
   - Wait 4 days → Check if Email 1 clicked → if NO → Send Email 2
   - Wait 6 more days → Check if Email 1 or 2 clicked → if NO → Send Email 3
   - End sequence
4. **Unsubscribe handling:** MailerLite handles automatically — anyone who unsubscribes is removed from all sequences
5. **Sender domain:** Verify revcycleai.com in MailerLite → Domains before sending

## CAN-SPAM Compliance
- ✅ Unsubscribe link in every email (MailerLite `{{unsubscribe_url}}`)
- ✅ Physical address in footer (`{{company_address}}`)
- ✅ Honest subject lines (no "Re:" or "Fwd:" tricks)
- ✅ Sender name and email clearly identified
- ✅ Footer explains why they're receiving this

## Expected Performance Benchmarks
- Cold outreach open rate: 30–45% (strong personalization + relevant subject)
- Click rate: 8–15% (tool offer is low-friction)
- Subscribe rate from clickers: 40–60%
- Axlow trial rate from Email 3: 3–8%

At 100 leads:
- ~35–45 opens per email
- ~10–15 tool clicks
- ~5–8 newsletter subscribers
- ~1–3 Axlow trials from sequence
