# Stripe Price Update Required

## New Pricing (Effective Immediately)
- **Monthly:** $19/mo (was $29/mo)
- **Annual:** $179/yr (was $249/yr)

## Steps to Complete in Stripe Dashboard

1. **Log into Stripe:** https://dashboard.stripe.com
2. **Navigate to:** Products → RevCycleAI Pro (or create if doesn't exist)
3. **Create two new prices:**
   - **Monthly recurring:** $19.00 USD / month
   - **Annual recurring:** $179.00 USD / year
4. **Copy the new Price IDs** (they look like `price_xxxxxxxxxxxxx`)
5. **Update Netlify environment variables:**
   - Go to: Netlify Dashboard → revcycleai → Site settings → Environment variables
   - Update `STRIPE_PRICE_MONTHLY` with new $19/mo price ID
   - Update `STRIPE_PRICE_ANNUAL` with new $179/yr price ID
   - Click "Save"
6. **Redeploy the site** (Netlify will auto-redeploy, or trigger manual deploy)

## Existing Subscribers
- Keep existing subscribers at their current rate ($29/mo or $249/yr)
- Stripe will continue billing them at the old price
- Only NEW subscribers get the $19/$179 pricing

## Why We Lowered the Price
Current Pro offering (17 downloadable resources) justifies $99-149 one-time purchase, but not $29/mo recurring. $19/mo is more defensible until we add weekly premium reports.

## Files Updated
- `/public/pro/index.html` — pricing page
- `/public/index.html` — homepage Pro CTAs (2 places)
- `/.env.example` — documentation
- This file

## Test Before Launch
After updating Stripe price IDs in Netlify:
1. Visit https://revcycleai.com/pro
2. Click "Get Pro access" on either plan
3. Verify Stripe checkout shows correct price ($19/mo or $179/yr)
4. Do NOT complete payment (unless you want to test end-to-end)
5. Check that redirect to `/pro/welcome` works after payment

---

**Next:** Create the new Stripe prices and update Netlify env vars.
