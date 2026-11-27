# Day-1 checks

Results of verifying free-tier limits and plan assumptions. Fill in **Result** as each check is done.

| # | Check | How | Result | If it fails |
|---|---|---|---|---|
| 1 | Make webhook is instant on free | P01 phase 3 test | | Report; still fine with "Run once" demos |
| 2 | HubSpot test account has Workflows | F4 step 3 | **Pass** (2026-11-26): yes, Create workflow is available (Marketing Hub Enterprise trial) | P02 uses `qualify.py` fallback trigger |
| 3 | Meta "Generate access token" visible | F7 step 3 | Later | Business settings → give yourself full control |
| 4 | Webflow form custom action saves and survives re-publish | P01 phase 4 | **Pass** (2026-11-27): address and dropdown values still correct after publishing again (no Designer edit in between) | Re-enter action URL after each Designer save; or move the form to GitHub Pages |
| 5 | Gemini free model + RPD noted | F5 | **Model passed** (2026-11-27): `gemini-3.5-flash-lite`, free tier, 15 RPM, 250K TPM, test call OK. RPD still to be noted | Rules fallback handles it |
| 6 | BigQuery billing linked? | F6 | Later | Budget alert set |
| 7 | Own Google Ads account can be created without billing + UPLOAD_CLICKS conversion action | P02 phase 5 | Later | P02 stays at level L0 (offline payload validation) |
| 8 | Supabase project count ≤ 2 | F2 | 2026-11-26: `growth-ops-lab` created, tables + RLS verified. Projects in this account: 1 (≤ 2, pass) | Pause an unused project |
| 9 | What Webflow Starter and Claude Code can do together | Before F9, Webflow's own docs | 2026-11-27: researched, see `webflow/CAPABILITIES.md`. Connector tried: builds pages and forms on Starter without the Designer; select options need hand entry; custom action not yet tested | Build by hand in the Designer |
| 10 | P01 failed submission shows retry message and posts Slack alert | P01 phase 3b | | Fix before demo |
| 11 | P10 drop scenario alerts; normal stays quiet; failure step works | P10 phase 4 | | Run locally with `--dry-run` |

## Build status (order set 2026-11-27)

| Order | Item | Status |
|---|---|---|
| done | F0–F4 | Done |
| 1 | F8 Make webhook | Done 2026-11-27: test lead accepted (200), Make shows "Successfully determined"; account noted below |
| 1a | Webflow capability check | Done 2026-11-27 (docs only) |
| 2 | F9 Webflow portfolio: Home + Contact | Done 2026-11-27: published, live pages checked, test submission arrived in Make, form address survived re-publish |
| 3 | F5 finish: Gemini model + ping | Done 2026-11-27 (daily limit still to be noted) |
| 3a | F10 slice: Pages, secrets, keepalive | To do |
| 4 | P01 lead router | To do |
| 5 | P10 organic drop monitor | To do |
| 6 | Demo scripts (F9, P01, P10) | To do |
| later | F6, F7, rest of F10, F11, P02–P09 | Later |

## Account notes

- Make: plan = Free, credits = 1,000, active scenario limit = 2 (confirmed 2026-11-27)
- Gemini model id: `gemini-3.5-flash-lite` · RPM: 15 · RPD: to be noted
- Webflow site: https://growth-ops-lab.webflow.io (free Starter), first published 2026-11-27

## Surprises log

Dated notes on any limit or plan behaviour that differed from the plan.

- 2026-11-26 · F1: `uv` defaulted to Python 3.14; pinned 3.12 via `.python-version` as the plan requires.
- 2026-11-26 · F2: the email unique index is on `lower(email)` and partial, so Supabase REST `on_conflict` cannot target it. P01 upserts need a database function or select-then-insert/update.
- 2026-11-26 · F2: PlanFair is not in this Supabase account, which holds only `growth-ops-lab`. The plan assumed PlanFair used one slot; confirm where it lives before P09.
- 2026-11-26 · F4: HubSpot developer test account verified (type DEVELOPER_TEST, region na2, timezone US/Eastern, currency USD). Renew the 90-day trial around 2027-02-19 (day 85, counted from today).
- 2026-11-26 · F5: marked done for key setup only. Before P01: set `GEMINI_MODEL`, note RPD, write and run `scripts/ping_gemini.py` (not written yet, so the key is untested).
- 2026-11-27 · Webflow: the plan assumed all page building is manual. Webflow's MCP docs describe headless element-building tools; untested on our account.
- 2026-11-27 · Scope: the portfolio is open to any organisation. The site is Home (portfolio overview) and Contact; plans and sample data are generic.
- 2026-11-27 · F9: custom form action works on free Starter, but only after removing the default "Webflow" and "Email Notifications" destinations. A "Made in Webflow" badge shows on the live site.
