# Canva Template Specifications for Axlow LinkedIn

## Overview

Create these 5 template designs in Canva. Save each as a **template** so you can quickly duplicate and populate with new text via Canva API or manually.

---

## Color Palette (Add to Canva Brand Kit)

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Deep Teal | `#1D4740` | Headers, backgrounds, primary brand |
| Soft Mint | `#E8F4F0` | Backgrounds, cards |
| Pale Sage | `#DFE6E8` | Secondary backgrounds, borders |
| White | `#FFFFFF` | Clean contrast, text areas |
| Dark Gray | `#2D3748` | Body text |

---

## Typography (Add to Canva Brand Kit)

- **Headings:** Inter Bold (or Helvetica Neue Bold if Inter unavailable)
- **Body:** Inter Regular (or Helvetica Neue Regular)
- **Font sizes:**
  - Large stat/number: 60-72pt
  - Header: 32-36pt
  - Subheader: 24-28pt
  - Body: 16-18pt
  - Caption: 12-14pt

---

## Template 1: The Stat Card

**Dimensions:** 1200 x 1200px (square)

**Layout:**
```
┌──────────────────────────────────────┐
│                                      │
│                                      │
│          30 min → 20 sec            │  ← Large stat (60pt, Deep Teal)
│                                      │
│    Average payor policy search      │  ← Supporting text (18pt, Dark Gray)
│    time: before and after Axlow     │
│                                      │
│                                      │
│                         [Axlow Logo]│  ← Logo (80px, bottom-right)
└──────────────────────────────────────┘
```

**Design specs:**
- Background: Deep Teal (#1D4740) OR White (#FFFFFF)
- If white background: Add thick teal accent bar on left edge (40px wide)
- Large stat: Inter Bold, 60pt, centered
- Supporting text: Inter Regular, 18pt, centered, below stat
- Axlow logo: 80px width, bottom-right corner, 40px padding
- Generous whitespace: Stat + text takes up ≤40% of canvas

**Text placeholders:**
- `[STAT]` — The main number/comparison
- `[SUPPORTING_TEXT]` — Context for the stat

---

## Template 2: The Before/After Split

**Dimensions:** 1200 x 1200px (square)

**Layout:**
```
┌────────────┬──────────┬────────────┐
│  BEFORE    │    vs    │   AFTER    │
│            │          │            │
│  [Messy    │          │  [Clean    │
│   portal   │    →     │   Axlow    │
│   screen]  │          │   screen]  │
│            │          │            │
│  Muted     │          │  Teal +    │
│  grays     │          │  mint      │
│            │          │            │
│            │          │ [Logo]     │
└────────────┴──────────┴────────────┘
```

**Design specs:**
- Split canvas vertically 50/50
- Left side (BEFORE):
  - Screenshot of cluttered payor portal OR text describing manual process
  - Muted colors: grays, desaturated
  - "BEFORE" label top-left (14pt, gray)
- Dividing line:
  - Vertical line or arrow
  - "vs" or "→" centered
- Right side (AFTER):
  - Screenshot of clean Axlow interface OR text describing Axlow process
  - Bright colors: Deep Teal, Soft Mint
  - "AFTER" label top-right (14pt, teal)
- Axlow logo: Bottom-right of right panel

**Text placeholders:**
- `[BEFORE_IMAGE]` — Screenshot or text for "before" state
- `[AFTER_IMAGE]` — Screenshot or text for "after" state

---

## Template 3: The Quote Card

**Dimensions:** 1200 x 1200px (square)

**Layout:**
```
┌──────────────────────────────────────┐
│                                      │
│   "I recovered $14,000 in denied    │  ← Quote (28pt, Deep Teal)
│    claims in my first week."        │
│                                      │
│   — Sarah M., RCM Manager           │  ← Attribution (16pt, Dark Gray)
│                                      │
│                                      │
│                                      │
│                         [Axlow Logo]│
└──────────────────────────────────────┘
```

**Design specs:**
- Background: White (#FFFFFF) with subtle teal accent elements (optional thin border or corner element)
- Quote: Inter Bold, 24-28pt, Deep Teal, centered
- Opening quote marks: Large decorative """ in Soft Mint (optional)
- Attribution: Inter Regular, 16pt, Dark Gray, centered below quote
- Axlow logo: 80px, bottom-right corner

**Text placeholders:**
- `[QUOTE]` — The testimonial or quote
- `[ATTRIBUTION]` — Name, title (optional: company if allowed)

---

## Template 4: The Data Visualization

**Dimensions:** 1200 x 1200px (square)

**Layout:**
```
┌──────────────────────────────────────┐
│  Time Spent on Payor Research       │  ← Title (24pt, Deep Teal)
│                                      │
│  Manual:  ████████████  12.5 hrs    │  ← Bar chart
│  Axlow:   █  0.8 hrs                │
│                                      │
│  That's 93% time savings             │  ← Insight (18pt, Dark Gray)
│                                      │
│                         [Axlow Logo]│
└──────────────────────────────────────┘
```

**Design specs:**
- Background: White or Soft Mint
- Title: Inter Bold, 24pt, Deep Teal, top-center
- Chart/visualization:
  - Simple bar chart, pie chart, or comparison table
  - Branded colors only (Deep Teal for primary data, Pale Sage for secondary)
  - Clear labels, large readable text
  - Minimal gridlines, no clutter
- Key insight: Inter Bold, 18pt, Dark Gray, below chart
- Axlow logo: Bottom-right

**Text placeholders:**
- `[TITLE]` — Chart title
- `[DATA]` — The actual numbers/visualization
- `[INSIGHT]` — Key takeaway

---

## Template 5: The Tip Card / Listicle

**Dimensions:** 1200 x 1200px (square)

**Layout:**
```
┌──────────────────────────────────────┐
│  RCM Pro Tip                         │  ← Header (28pt, Deep Teal)
│  ━━━━━━━━━━━━                        │
│                                      │
│  1. First tip here...                │  ← List items (18pt, Dark Gray)
│                                      │
│  2. Second tip here...               │
│                                      │
│  3. Third tip here...                │
│                                      │
│                                      │
│                         [Axlow Logo]│
└──────────────────────────────────────┘
```

**Design specs:**
- Background: White
- Header: Inter Bold, 28pt, Deep Teal, top-left
- Optional: Teal underline or accent bar below header
- List items: Inter Regular, 18pt, Dark Gray, left-aligned
- Optional: Simple icons next to each item (use Canva icon library, keep minimal)
- Generous line spacing (1.5x)
- Axlow logo: Bottom-right

**Text placeholders:**
- `[HEADER]` — "RCM Pro Tip" or "3 Things to Know About..." or "How to..."
- `[TIP_1]` — First list item
- `[TIP_2]` — Second list item
- `[TIP_3]` — Third list item
- (Add more as needed, max 5 items for readability)

---

## Carousel Template

**Dimensions:** 1080 x 1350px (vertical)

**Slide 1 (Hook):**
```
┌──────────────────────────────┐
│                              │
│                              │
│    Bold Hook Question        │  ← Large text (36pt, Deep Teal)
│    or Statement              │
│                              │
│                              │
│                              │
│                 1/8          │  ← Page number (14pt, Pale Sage)
│         [Axlow Logo]         │
└──────────────────────────────┘
```

**Slides 2-7 (Content):**
```
┌──────────────────────────────┐
│  Topic Header                │  ← Header bar (Deep Teal bg, white text)
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│                              │
│  Content text here...        │  ← Body (18pt, Dark Gray)
│  One idea per slide.         │
│                              │
│  Use bullet points or        │
│  short paragraphs.           │
│                              │
│                 2/8          │
│         [Axlow Logo]         │
└──────────────────────────────┘
```

**Slide 8 (CTA):**
```
┌──────────────────────────────┐
│                              │
│   Try 3 Free Searches        │  ← CTA (32pt, Deep Teal)
│                              │
│   axlow.com  🔍              │  ← URL (24pt, Dark Gray)
│                              │
│                              │
│                 8/8          │
│         [Axlow Logo]         │
└──────────────────────────────┘
```

**Design specs:**
- Background: Alternating white and Soft Mint per slide for visual variety
- Header bar (slides 2-7): Deep Teal background, white text, full width
- Body text: Inter Regular, 18pt, Dark Gray, left-aligned, generous line spacing
- Page numbers: Top-right or bottom-right corner, 14pt, Pale Sage
- Axlow logo: Bottom-center, every slide
- Keep each slide simple: 1 idea per slide

---

## How to Use These Templates

### Option A: Manual Canva Workflow
1. Create all 5 templates in Canva (use "Custom Size" for exact dimensions)
2. Save each as a **template** in your Canva account
3. When generating content, duplicate the appropriate template
4. Replace placeholder text with actual post content
5. Export as PNG (high quality)

### Option B: Canva API Automation (Advanced)
1. Create templates in Canva with text placeholder names (e.g., `{STAT}`, `{SUPPORTING_TEXT}`)
2. Use Canva API to programmatically populate placeholders
3. Auto-export as PNG
4. (Requires Canva Pro + API access)

### Option C: Bannerbear (Alternative to Canva)
1. Recreate these designs in Bannerbear template editor
2. Use Bannerbear API to generate images programmatically
3. More automation-friendly but less design flexibility

---

## Canva Pro Tips

1. **Create a Brand Kit** in Canva with Axlow's colors + logo so every template auto-loads them
2. **Use folders** to organize templates by type (Stat Cards, Before/After, etc.)
3. **Name templates clearly:** "Axlow - Stat Card Template" so they're easy to find
4. **Lock the logo layer** so you don't accidentally move/delete it
5. **Use Canva's spacing guides** to ensure consistent padding

---

## Quality Checklist for Every Image

Before exporting, verify:

✅ Axlow logo is present (bottom-right, 80px width)  
✅ Colors match brand palette (no random colors)  
✅ Text is readable on mobile (minimum 16pt for body text)  
✅ Whitespace is generous (content ≤40% of canvas)  
✅ No typos or formatting errors  
✅ Consistent with Axlow's "trusted medical tool" aesthetic (clean, minimal, professional)

---

## Export Settings

**For LinkedIn:**
- **Format:** PNG (high quality)
- **Dimensions:**
  - Single posts: 1200 x 1200px
  - Carousel: 1080 x 1350px
- **Compression:** Medium (balance quality + file size)
- **Color space:** sRGB

---

## Need Help?

If you're not familiar with Canva:
1. Go to canva.com and sign up for Canva Pro (required for custom dimensions + brand kit)
2. Watch Canva's "Custom Templates" tutorial
3. Use these specs to recreate each template
4. Once templates are set up, generating images takes <5 minutes per post

Alternatively, hire a designer on Fiverr/Upwork to create these 5 templates for you (~$50-100 one-time cost).
