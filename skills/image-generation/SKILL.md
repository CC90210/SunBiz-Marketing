# SKILL: AI Image Generation (Gemini Imagen / Nano Banana)

> Generate professional ad creatives using Google Gemini's image generation for SunBiz Funding MCA campaigns.

---

## Overview
This skill uses Google Gemini's native image generation (Imagen 3 / "Nano Banana") to create ad images directly from text prompts. No need for Canva, Photoshop, or external designers — the AI generates complete, ready-to-post ad creatives for MCA consolidation and growth capital campaigns.

## Setup
```bash
pip install google-genai Pillow
```
Add to `.env.agents`:
```
GEMINI_API_KEY=your_api_key_here
```
Get API key from: https://aistudio.google.com/apikey

## Models
| Model | Capability | Best For |
|-------|-----------|----------|
| `gemini-2.5-flash-image` | Nano Banana — fast, production-ready native image gen | Primary model for all ad creatives |
| `gemini-2.0-flash-exp` | Legacy experimental native image gen | Fallback if 2.5 unavailable |
| `imagen-3.0-generate-002` | Dedicated image generation (standalone API) | Final fallback |

**SDK:** `google-genai` (NOT the deprecated `google-generativeai`)

## How to Generate Ads

### Consolidation Ad (Before/After)
```python
from scripts.imagen_generate import generate_consolidation_ad

result = generate_consolidation_ad(
    headline="STOP THE DAILY DRAIN",
    before_daily="$2,100/day across 4 funders",
    after_daily="$850/day — one partner",
    savings="Save $1,250/day",
    cta="See If You Qualify",
    company_name="SunBiz Funding",
    size="1080x1080",
    campaign_name="consolidation_q1",
    style="before_after",  # or "roadmap" or "payment_table"
)
```

### Growth Capital Ad
```python
from scripts.imagen_generate import generate_growth_ad

result = generate_growth_ad(
    headline="SMART CAPITAL FOR GROWING BUSINESSES",
    cta="See Your Options",
    company_name="SunBiz Funding",
    size="1080x1080",
    campaign_name="growth_q1",
)
```

### A/B Test Variants
```python
from scripts.imagen_generate import generate_ad_variants

results = generate_ad_variants(
    base_prompt="Professional MCA consolidation ad with navy blue background...",
    campaign_name="consolidation_test",
    variants=3,
    size="1080x1080",
)
```

### All Platform Sizes
```python
from scripts.imagen_generate import generate_all_sizes

results = generate_all_sizes(
    prompt="Your detailed MCA ad prompt...",
    campaign_name="consolidation_q1",
)
# Generates: meta_feed_square, meta_feed_portrait, meta_stories, google_display
```

## MCA Ad Prompt Templates

### Template 1: Before/After Consolidation (Primary)
```
Professional MCA consolidation advertisement with dark navy blue (#001F54) background.
Bold white headline: "STOP THE DAILY DRAIN".
Clean infographic showing BEFORE vs AFTER:
BEFORE (red tinted): "4 MCA Positions — $2,100/day in payments"
AFTER (green tinted): "1 Position — $850/day — Save $1,250/day"
Arrow or visual flow from before to after.
Company name "SunBiz Funding" in white at top.
Orange (#FF6B35) CTA button: "See If You Qualify".
Small disclaimer: "Merchant Cash Advance products are not loans. Subject to underwriting approval."
4K, professional, clean, analytical financial advisor aesthetic.
```

### Template 2: Multi-Phase Roadmap
```
Professional financial roadmap infographic with navy blue (#001F54) background.
Bold headline: "YOUR PATH TO FINANCIAL HEALTH".
Four connected phases shown as a journey/timeline:
Phase 1: "Consolidate" — reduce daily burden (orange icon)
Phase 2: "Buy Out" — eliminate multiple funders (orange icon)
Phase 3: "One Funder" — single payment, single relationship (orange icon)
Phase 4: "Line of Credit" — best terms, lowest cost (green icon)
"SunBiz Funding" branding. Orange CTA button: "Start Your Journey".
Clean, modern, professional. No stock photos. Infographic style.
```

### Template 3: Daily Payment Comparison Table
```
Clean financial comparison table on navy blue background.
Headline: "CONSOLIDATE AND SAVE".
Professional table with two columns:
CURRENT: Multiple rows showing daily debits ($450, $380, $520, $750 = $2,100/day)
AFTER SUNBIZ: Single row showing $850/day
Green highlighted savings: "Save $1,250/day | $37,500/month"
"SunBiz Funding" logo. Orange CTA: "Get Your Free Analysis".
Modern, data-driven, financial advisor style.
```

### Template 4: Growth Capital (A-Paper)
```
Professional business funding ad with clean white/light gray background.
Bold dark headline: "SMART CAPITAL FOR GROWING BUSINESSES".
Professional business imagery (office, growth chart, or business owner).
Key selling points in clean cards:
"Funded in 24-48 Hours" | "No Equity Required" | "Revenue-Based"
Green (#28A745) accent for approved/growth messaging.
"SunBiz Funding" branding. Orange CTA: "See Your Options".
Professional, clean, trustworthy.
```

### Template 5: Stories/Vertical (1080x1920)
```
Vertical 9:16 dark navy (#001F54) background.
Bold white text "DROWNING IN MCA PAYMENTS?" at top.
Visual comparison in center:
BEFORE: Stack of 4 payment cards (red tint, stressed)
AFTER: Single clean payment card (green tint, relief)
Large savings number: "Save $1,250/day"
"SunBiz Funding" at bottom.
Orange CTA: "Swipe Up to Qualify".
Bold, mobile-optimized, high contrast.
```

## Visual Rules (from SOP)

### Colors
| Color | Hex | Use |
|-------|-----|-----|
| Navy Blue | #001F54 | Primary background |
| Orange | #FF6B35 | CTA buttons |
| Green | #28A745 | Savings, approved, growth |
| White | #FFFFFF | Text on dark backgrounds |
| Dark Charcoal | #333333 | Text on light backgrounds |

**AVOID:** Red (risk/danger), yellow alone (cheap), black-heavy (intimidating)

### Style Guidelines
- **Clean, analytical** — financial advisor, not used car salesman
- **Charts/infographics** — before/after, roadmaps, comparison tables
- **NO cheesy stock photos** of people throwing money or celebrating
- **Professional business imagery** when people are shown
- **Bold sans-serif typography** — clear, readable at mobile size

### What Makes MCA Ads Convert
1. **Before/after comparison** — shows concrete savings ($2,100 → $850/day)
2. **Multi-phase roadmap** — differentiates SunBiz from "just another funder"
3. **Specific numbers** — "$1,250/day saved" beats vague promises
4. **Dark backgrounds** — navy with white text, 40% higher engagement
5. **Orange CTA on navy** — perceived 34% more trustworthy

### What to NEVER Include
- "Loan" text anywhere in generated images
- Guaranteed approval language
- Specific factor rates without disclaimers
- Red as primary color (signals risk in financial contexts)
- Cheesy stock photos or clip art
- Too much text (>30% of image area)

## Image Quality Checklist
- [ ] Text is readable at mobile size (test at 400px width)
- [ ] Brand colors match (Navy #001F54, Orange #FF6B35, Green #28A745)
- [ ] "SunBiz Funding" name present
- [ ] Before/after numbers are realistic and accurate
- [ ] MCA disclaimer text included
- [ ] No "loan" language anywhere
- [ ] CTA is clear and prominent (orange button)
- [ ] Image meets platform size requirements
- [ ] No AI artifacts or distortions

## Iteration Process
1. Generate 3 variants with different creative concepts (not just color variants)
2. Review all 3 — pick best foundation
3. Regenerate winner with refinements
4. Generate all platform sizes from winning prompt
5. Upload and launch as A/B test
6. After 500+ impressions, declare winner by CPQL
7. Use winning style as template, create 10-15 distinct concepts per campaign
