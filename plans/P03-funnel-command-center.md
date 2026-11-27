# P03 · Funnel Command Center (BigQuery + GA4 sample + Looker Studio)

**Time:** ~4 hrs · **Needs:** 00 done (BigQuery dataset in US) · **Cost:** ₹0 (sandbox) / pennies with the budget cap if billing is linked

**One-liner:** "One warehouse, one model, one dashboard: spend by channel joined to real GA4 behaviour, with CPA/ROAS and funnel drop-off — and the ad-spend tables are swappable for real connectors."

---

## How to start this chat
```
Read CLAUDE.md and plans/P03-funnel-command-center.md. Follow it phase by phase.
Show bytes processed for every query before running it. Stop after each phase.
```

---

## Facts about the data (read before building — these break most first attempts)

| Fact | Consequence |
|---|---|
| Public GA4 sample = `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`, dates **2020-11-01 → 2021-01-31** only | All synthetic ad data uses the SAME dates. Looker date control must default to this range ("last 28 days" shows **nothing**) |
| Public dataset is in **US** | Our dataset `growth_ops` must be US (done in F6) or joins fail |
| Sample is obfuscated: values like `(data deleted)`, `<Other>` appear | Map them into an "Unknown" channel; never filter them out silently |
| `traffic_source.*` in the export is the **user's first-touch** source, not session source | Label the dashboard "first-user channel". Don't call it last-click |
| The sample has Google cpc / organic / referral / direct but **no paid social** | Meta leg = synthetic sessions + spend, clearly labelled. Google cpc leg joins real sample traffic |
| Sandbox: no DML (INSERT/UPDATE/DELETE), no streaming, tables expire in 60 days; DDL like `CREATE OR REPLACE TABLE … AS SELECT` works; load jobs work | Everything is rebuilt by one `build.sh`; never write row-level updates |
| Full scans of `events_*` cost a few GB | Build small summary tables once; Looker reads only those |

---

## Model

```
raw (Google public)                     synthetic (we load)
ga4 events_*  ─► stg_ga4_daily_channel   ads_google_daily  (date, campaign, impr, clicks, cost, conv)
               ─► stg_ga4_funnel_daily   ads_meta_daily    (date, campaign, impr, clicks, spend, results, est_sessions, est_purchases, est_revenue)
                                          crm_leads_daily   (optional: from P01 Supabase export)
                         \                 /
                          mart_channel_daily   (date, channel, spend, clicks, sessions, purchases, revenue, cpa, roas, cvr, is_synthetic)
                          mart_funnel_daily    (date, channel, sessions, view_item, add_to_cart, begin_checkout, purchase)
                          mart_kpis            (single-row totals for scorecards)
```

---

## Files

```
p03-funnel-command-center/
├── README.md
├── sql/
│   ├── 01_stg_ga4_daily_channel.sql
│   ├── 02_stg_ga4_funnel_daily.sql
│   ├── 10_mart_channel_daily.sql
│   ├── 11_mart_funnel_daily.sql
│   └── 12_mart_kpis.sql
├── synth/generate_ads.py        # writes CSVs matching real export schemas
├── synth/load.py                # BigQuery load jobs (WRITE_TRUNCATE)
├── build.sh                     # full rebuild: stg → synth load → marts
├── checks/data_tests.py         # row counts, nulls, date range, totals reconcile
└── docs/dashboard.md            # Looker Studio build steps + screenshot
```

---

## Phase 1 · Explore the sample (30 min)

**Prompt:**
```
P03 Phase 1. Using dry runs first (print bytes), then real runs with maximum_bytes_billed:
1. Confirm min/max event_date in events_*.
2. Distinct traffic_source.source / medium / name with event counts (top 50).
3. List campaign names where medium='cpc' — I need these to generate matching synthetic Google Ads campaigns.
4. Count events by event_name (session_start, page_view, view_item, add_to_cart, begin_checkout, purchase).
Write findings into p03-funnel-command-center/README.md under "Data notes".
```

**CHECK:** the date range is 2020-11-01…2021-01-31; cpc campaign list saved; total bytes processed < 5 GB.

---

## Phase 2 · Staging tables (45 min)

**Prompt:**
```
P03 Phase 2. Write and run:
01_stg_ga4_daily_channel.sql → CREATE OR REPLACE TABLE growth_ops.stg_ga4_daily_channel:
 date, source, medium, campaign, channel (CASE: medium='cpc' and source='google' → 'Google Ads'; medium='organic' → 'Organic Search'; medium='referral' → 'Referral'; source='(direct)' → 'Direct'; else 'Unknown/Obfuscated'),
 sessions = COUNT(DISTINCT CONCAT(user_pseudo_id, CAST((SELECT value.int_value FROM UNNEST(event_params) WHERE key='ga_session_id') AS STRING))),
 users, purchases (event_name='purchase'), revenue = SUM(ecommerce.purchase_revenue).
 Filter with _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'.
02_stg_ga4_funnel_daily.sql → counts of sessions reaching view_item / add_to_cart / begin_checkout / purchase per date+channel.
Run both; print row counts and revenue total.
```

**CHECK:** each table has ~92 dates × channels; revenue total printed; `data_tests.py` (write a first version) passes for date range + no null dates.

---

## Phase 3 · Synthetic ad data (45 min)

**Prompt:**
```
P03 Phase 3. synth/generate_ads.py (seeded random, reproducible):
- ads_google_daily: for each cpc campaign found in Phase 1 and each date in range: impressions, clicks, cost (INR), conversions.
  Make clicks ≈ 0.9–1.3× GA4 cpc sessions that day for that campaign, so CPC/CTR look realistic (CTR 2–8%, CPC ₹15–60), and conversions ≈ GA4 purchases ± noise. Include a Black Friday / Christmas spike consistent with the GA4 data.
- ads_meta_daily: 3 synthetic campaigns (Prospecting, Retargeting, Catalog), CPM ₹120–250, CTR 0.8–2%, est_sessions = clicks×0.8, est_purchases, est_revenue with a lower ROAS than Google; is_synthetic=true.
- Column names mirror real exports (Google: Day, Campaign, Impressions, Clicks, Cost, Conversions; Meta: Day, Campaign name, Impressions, Link clicks, Amount spent (INR), Results) and a column map renames them to snake_case on load.
synth/load.py: load CSVs with WRITE_TRUNCATE + explicit schema.
Run both; print totals per channel.
```

**CHECK:** Google Ads blended CPC is ₹15–60, Meta ROAS < Google ROAS, and the spike weeks match GA4 spikes (print a weekly side-by-side).

---

## Phase 4 · Marts + data tests (45 min)

**Prompt:**
```
P03 Phase 4. Write marts (CREATE OR REPLACE TABLE, not views — Looker should hit small tables):
- mart_channel_daily: union of
  Google Ads: GA4 sessions/purchases/revenue (real) + ads_google spend/clicks (synthetic),
  Meta: all synthetic fields, is_synthetic=true,
  Organic/Referral/Direct/Unknown: GA4 real, spend 0.
  Derived: cpa = spend/NULLIF(purchases,0), roas = revenue/NULLIF(spend,0), cvr = purchases/NULLIF(sessions,0).
- mart_funnel_daily from stg_ga4_funnel_daily (+ Meta est rows flagged).
- mart_kpis: totals for the full range.
checks/data_tests.py: (1) date range exact, (2) no negative spend, (3) mart revenue for GA4 channels == stg revenue, (4) no division errors (cpa/roas null when denominator 0), (5) row counts > 0.
build.sh runs everything in order and stops on the first failure.
```

**CHECK:** `./build.sh` runs end-to-end green and prints the KPI row.

---

## Phase 5 · Looker Studio dashboard (60 min, YOU)

**Prompt first:** `P03 Phase 5. Write docs/dashboard.md: page-by-page build steps, every chart's dimension/metric, calculated fields (ROAS = SUM(revenue)/SUM(spend) — never AVG of a ratio), filters, and styling notes.`

**YOU (lookerstudio.google.com):**
1. Create → Report → **BigQuery** connector → My projects → `growth-ops-lab` → `growth_ops` → `mart_channel_daily`. Add `mart_funnel_daily` and `mart_kpis` as extra data sources.
2. Each data source → **Data credentials: Owner's credentials** (so viewers don't need BigQuery access).
3. **Date range control**: default **custom 2020-11-01 → 2021-01-31**. (Critical, or the report looks empty.)
4. Page 1 "Overview": scorecards (Spend, Revenue, ROAS, CPA, Purchases), time series (spend vs revenue), channel table with conditional formatting on ROAS.
5. Page 2 "Funnel": bar chart of sessions → view_item → add_to_cart → begin_checkout → purchase, with channel filter.
6. Page 3 "Data notes": a text box listing what's real vs synthetic, first-user channel caveat, sample date range.
7. Share → anyone with the link can **view**. Paste the link to Claude for the README.

**Calculated-field rule:** ratios are recalculated from sums (`SUM(revenue)/SUM(spend)`). Averaging daily ROAS is wrong, and reviewers notice.

**CHECK:** open the link in an incognito window and confirm the data shows and the KPI totals match `mart_kpis`.

---

## Phase 6 · Optional CRM leg (30 min)

**Prompt:** `P03 Phase 6 (optional). Export P01 leads (is_demo) from Supabase to CSV, load to growth_ops.crm_leads (load job), and add a mart_leads_daily (date, source, tier counts). Add a Looker page "Lead quality" (leads by tier by source).`

---

## Phase 7 · Sandbox expiry + README (20 min)

**Prompt:** `P03 Phase 7. If sandbox (no billing): add a note + a monthly GitHub Action 'p03-rebuild.yml' that runs build.sh (auth via a service account key stored as a secret — walk me through creating a service account with BigQuery Job User + Data Editor on the dataset only). README: architecture, model diagram, data notes, real vs synthetic, how to go live, 'at scale' (dbt, incremental models, GA4 daily export, Google Ads Data Transfer, Meta via a connector, attribution model choice).`

**YOU:** create the service account when Claude walks you through it (IAM → Service accounts). Download the key JSON once and give it to Claude to store as a GitHub secret. Then delete the local file.

**If key creation is blocked** (an org policy "disableServiceAccountKeyCreation" applies to Workspace-org projects, not usually personal Gmail projects): either let Claude set up Workload Identity Federation for GitHub Actions (no key), or simply run `./build.sh` locally once a month and set a calendar reminder. Both are fine.

---

## Demo vs Live

| | Demo | Live |
|---|---|---|
| GA4 | Public sample | Client property → BigQuery export (free daily export) → repoint `stg_` SQL to `analytics_<id>.events_*` |
| Google Ads | Synthetic | Looker native Google Ads connector or the Google Ads Data Transfer (needs billing) → same column map |
| Meta | Synthetic | Porter Metrics free plan (up to 3 accounts) / any connector / CSV upload → same column map |
| Dates | Fixed 2020–21 range | Rolling last 90 days |

## Anomalies handled
| Risk | Handling |
|---|---|
| Empty dashboard because of default date range | Custom default range |
| Cross-region join error | Dataset in US |
| Cost surprise | Dry runs + maximum_bytes_billed + small marts |
| Sandbox 60-day expiry | build.sh + monthly rebuild action |
| Wrong ROAS from averaged ratios | Ratios from sums |
| Misleading attribution | "First-user channel" label + data notes page |
| Obfuscated values | "Unknown/Obfuscated" channel kept visible |

## DONE checklist
- [ ] Data notes written
- [ ] stg + synth + marts built; data tests green
- [ ] Dashboard 3 pages, public view link, works in incognito
- [ ] Rebuild path documented / automated
- [ ] README + Loom + hub card

## Design highlights
- "I modelled it like I would at a company: staging, marts, tests, one source of truth — the dashboard is the last 5%."
- "I called out the first-touch limitation in the data instead of pretending it's last-click."
