# P05 · Paid-Ads Budget & Break-even Calculator (lead magnet)

**Time:** ~3–4 hrs · **Needs:** 00 + P01 done (uses Make Scenario A) · **Cost:** ₹0

**One-liner:** "A free calculator that answers 'what can I afford to pay per lead, and what budget hits my target?' It doubles as an inbound lead magnet that feeds the lead router with full UTM context."

---

## How to start this chat
```
Read CLAUDE.md and plans/P05-lead-gen-calculator.md. Follow it phase by phase. Stop after each phase.
```

---

## Why it's split across Webflow and GitHub Pages
Webflow's free Starter plan can't run custom code or Code Embed, so the calculator JS can't live there. Webflow's **Calculator** page is the SEO landing page; the tool itself is on GitHub Pages (`/site/calculator/`). The tool's form posts to the P01 webhook with hidden fields (inputs, outputs, UTMs). The Webflow form can't send those.

```
Webflow /calculator (landing, SEO) ──CTA──► GitHub Pages /calculator/ (tool)
                                              │ "Save my plan & get a review" form
                                              ▼ fetch POST (form-urlencoded)
                                       Make Scenario A (P01) → score-lead → HubSpot → Slack
```

---

## The math (single source of truth, tested)

Inputs: `deal_value` (avg first-year revenue per customer), `gross_margin_pct`, `lead_to_sql_pct`, `sql_to_won_pct`, `target_customers_per_month`, optional `current_cpl`, optional `target_payback_months` (default 12), currency (INR/USD).

```
lead_to_customer = lead_to_sql × sql_to_won
gross_profit_per_customer = deal_value × gross_margin
breakeven_cac = gross_profit_per_customer × (target_payback_months / 12)
max_cpl = breakeven_cac × lead_to_customer
leads_needed = target_customers / lead_to_customer
budget_at_max_cpl = leads_needed × max_cpl
if current_cpl: budget_at_current = leads_needed × current_cpl; headroom_pct = (max_cpl − current_cpl) / max_cpl
breakeven_roas = 1 / gross_margin   (on revenue)
```

**Worked test case (must pass):**
- Inputs: deal ₹1,00,000, margin 70%, lead→SQL 20%, SQL→won 25%, target 10 customers/month, payback 12 months.
- lead_to_customer = 5%; GP/customer = ₹70,000; breakeven CAC = ₹70,000; **max CPL = ₹3,500**; leads needed = 200; **budget = ₹7,00,000/month**; breakeven ROAS = 1.43.

Edge cases:
- Any rate = 0 → show a message, not Infinity/NaN.
- Percentages outside 0–100 → field error.
- Values formatted with `Intl.NumberFormat('en-IN')` for INR (lakh grouping).

---

## Files

```
site/calculator/
├── index.html
├── calc.js            # pure functions, exported (ES module)
├── ui.js              # DOM, sliders, formatting, UTM capture, form submit
├── styles.css
└── print.css          # "Download PDF" via window.print()
p05-lead-gen-calculator/
├── README.md
├── tests/calc.test.mjs        # node --test
└── webflow/LANDING.md         # copy + SEO fields for the Webflow page
```

---

## Phase 1 · Math + tests (45 min)

**Prompt:**
```
P05 Phase 1. Write site/calculator/calc.js as pure exported functions implementing the plan's formulas, returning an object with all outputs + warnings[]. Write tests/calc.test.mjs: the worked example (exact numbers), zero-rate case, >100% validation, USD formatting, payback 6 vs 12 months. Run node --test.
```
**CHECK:** all tests green; the worked example matches exactly.

---

## Phase 2 · UI (60 min)

**Prompt:**
```
P05 Phase 2. Build index.html + ui.js + styles.css:
- Inputs with sliders + number boxes, sensible defaults (the worked example), currency toggle.
- Results update live: max CPL, leads needed, budget, breakeven ROAS, and if current_cpl set: headroom badge (green/amber/red).
- A short 'How to read this' explainer and the formulas in a collapsible.
- "Download as PDF" (window.print with print.css).
- Mobile-first, no frameworks, accessible labels.
```
**CHECK:** works on mobile; numbers match tests; print preview looks clean.

---

## Phase 3 · Lead capture → P01 (45 min)

**Prompt:**
```
P05 Phase 3.
1. ui.js: on load capture utm_source/medium/campaign, gclid, fbclid from the URL into sessionStorage.
2. Form "Save my plan & get a free review": email (required), first_name, company, role, company_size (same options as P01), timeline. Hidden: source='calculator', page_url, UTMs, gclid, fbclid, and use_case = a one-line summary of their inputs/outputs (e.g. "Max CPL ₹3,500, needs 200 leads/mo, budget ₹7L").
3. Honeypot field 'website' (hidden by CSS) — if filled, don't submit.
4. Submit with fetch POST to MAKE_WEBHOOK_LEADS_URL as application/x-www-form-urlencoded (avoids CORS preflight). Use mode 'no-cors' if Make's response lacks CORS headers — then show success optimistically and log a GA4 event.
5. The webhook URL is public by nature; document that Make validates via the score-lead secret and junk ends as tier C.
Push and test from the live Pages URL with ?utm_source=test&utm_campaign=p05.
```

**CHECK:** a submission appears in Supabase with source=calculator, UTMs filled and the use_case summary, plus a HubSpot contact and a Slack ping if tier A. Make credits used ≈ 5.

**Copy honesty:** don't promise "we'll email you the plan" unless something sends email. "Save my plan & get a review" + Download PDF is accurate.

---

## Phase 4 · Webflow landing page (YOU, 45 min)

**Prompt first:** `P05 Phase 4. Write webflow/LANDING.md: H1, subhead, 3 benefit bullets, a 'how it works' 3-step strip, FAQ (4 Qs), SEO title (≤60 chars), meta description (≤155), slug 'calculator', CTA button text and link (SITE_BASE_URL/calculator/?utm_source=webflow&utm_medium=landing&utm_campaign=calculator).`

**YOU (Webflow Designer → Calculator page):** build it from LANDING.md with native elements only (headings, text, buttons, a FAQ built from simple sections). Page settings → SEO title + description. Link the Home page to it. Publish.

**CHECK:** Webflow page → CTA → calculator loads with UTMs → submit → lead tagged `utm_source=webflow`.

---

## Phase 5 · Analytics + README (30 min)

**Prompt:** `P05 Phase 5. Add GA4 (reuse a 'Growth Ops Lab' GA4 property — tell me how to create it if not existing) with events calc_interact (debounced), calc_result_viewed, pdf_download, lead_submit; load after a consent banner (reuse P04 consent.js). README: problem, formulas, worked example, architecture (Webflow→Pages→Make→router), why split, demo vs live, 'at scale' (gate advanced outputs, benchmark data by industry, HubSpot form embed on a paid site plan).`

---

## Demo vs Live
- **Demo:** your Webflow + Pages + P01 pipeline.
- **Live:** embed the calculator on a client site (any CMS with custom code, or a paid Webflow plan). Point the form at their lead webhook. Change defaults to their benchmarks.

## Anomalies handled
| Risk | Handling |
|---|---|
| Webflow free can't host JS | Tool on Pages; Webflow = landing |
| CORS on webhook POST | form-urlencoded + no-cors fallback |
| Spam | Honeypot + server validation + tier C |
| NaN/Infinity | Guarded with tests |
| Lakh formatting | Intl en-IN |
| Over-promising email | Honest CTA copy |

## DONE checklist
- [ ] calc tests green (worked example exact)
- [ ] UI live and mobile-friendly
- [ ] Lead lands in Supabase/HubSpot with UTMs + summary
- [ ] Webflow landing live and linked
- [ ] GA4 events; README + hub card

## Design highlights
- "It's a lead magnet that carries intent: the lead arrives with their own numbers, so sales opens with context."
- "I worked around the Webflow free-plan limit by splitting landing and tool — same pattern as a real site with a tools subdomain."
