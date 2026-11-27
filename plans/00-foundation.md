# 00 · Foundation (do this once, before any project)

**Time:** ~3 hrs · **Cost:** ₹0 · **Machine:** Mac · **Builder:** Claude Code (Pro plan)

This sets up the repo, accounts, keys and shared code that every project file (P01–P09) assumes exists. Later files reference names created here. Follow the build order below, which says what to do now and what is later.

---

## How to start this chat

1. Create the folder: `mkdir -p ~/growth-ops-lab/plans`
2. Copy all 10 plan files (`00-foundation.md`, `P01…P09`) into `~/growth-ops-lab/plans/`.
3. Open **Claude Desktop → Code tab**, choose folder `~/growth-ops-lab`, new session.
4. First message (paste exactly):

```
Read plans/00-foundation.md. Follow it phase by phase (F0, F1, ...).
Rules: you write and run all code; I have limited coding skills.
Anything marked YOU is mine to do in the browser — give me exact clicks and tell me what to paste back to you.
At the end of each phase, run the CHECK steps, show me proof, commit, then stop and wait for me.
Never set or use ANTHROPIC_API_KEY. Never put secrets in git.
```

---

## Build order (updated 2026-11-27)

F0–F4 and F8 are done. F5 has the key saved; the model is step 3 below. Do these in order. **Nothing else until they are done.**

| Order | Item | What | Est. | Shows |
|---|---|---|---|---|
| 1 | F8 | Make account + webhook-only scenario (becomes Scenario A) | 20 min | |
| 1a | Webflow check | Data API, MCP and paste-in HTML options, Starter limits, from Webflow's own docs | 30 min | Claude Code, Webflow |
| 2 | F9 | Webflow portfolio site: Home + Contact page with demo form | 2 hrs | Webflow |
| 3 | F5 (finish) | Set `GEMINI_MODEL`, write and run `scripts/ping_gemini.py` | 20 min | |
| 3a | F10 slice | GitHub Pages, Actions secrets, keepalive | 30 min | |
| 4 | P01 | Lead router end to end, including the failed-submission path | 5–6 hrs | Claude Code |
| 5 | P10 | Organic drop monitor with Slack alert | 2–3 hrs | Monitoring and alerts |
| 6 | Demo scripts | A 5-minute demo script each for F9, P01 and P10 | 1 hr | |

Stop after each phase and say what is needed in the browser.

### Later (kept, not deleted)

F6 BigQuery · F7 Meta CAPI · rest of F10 (monthly heartbeat) · F11 final check · P02 feedback loop · P03 funnel command center · P04 bike quiz · P05 calculator · P06 AEO tracker · P07 creative pattern lab · P08 ad account auditor · P09 PlanFair

**Make free = 2 active scenarios.** A (P01) and B (P02, later) are the only two, ever. Everything else runs as Python scripts, GitHub Actions or Supabase Edge Functions.

---

## Demo scripts (step 6)

**Prompt:**
```
Demo scripts. Write demo-scripts/f9.md, demo-scripts/p01.md and demo-scripts/p10.md, each a 5-minute walkthrough for any audience: minute-by-minute actions, what to say, the proof on screen, a fallback if the live demo fails, and 5 likely questions with honest answers. Only describe what was actually built and tested.
```

**CHECK:** each script is rehearsed once against the live system within 5 minutes.

---

## Verified free-tier limits (checked 26 Nov 2026) — the rules every file follows

| Tool | Limit that matters | Rule we follow |
|---|---|---|
| Claude Code | Included in Pro; if `ANTHROPIC_API_KEY` is set it bills the API instead | Never set it. Check with `echo $ANTHROPIC_API_KEY` (must be empty) |
| Make free | 1,000 credits/month, 2 active scenarios, 1 credit per module run; polling triggers cost 1 credit per check even when empty; webhooks are instant | Webhook triggers only. No "Watch" modules. Budget below |
| Supabase free | 2 active projects, 500 MB, pauses after 7 days idle | PlanFair already uses 1 slot → Growth Ops Lab is slot 2. Keepalive ping every 3 days |
| HubSpot | Free CRM has no workflows. Developer test accounts: free, up to 10, 90-day Enterprise trial, expire if no API calls | Use a developer test account. Keepalive API call weekly |
| Webflow Starter | Free, webflow.io domain, 2 pages, **no Code Embed / custom code**; forms can use a custom action URL (bypasses Webflow storage, so no 50-submission cap) | Webflow = landing pages + simple forms only. All JS tools live on GitHub Pages |
| Gemini API free | No card. Free models and daily limits change often (cut sharply before). No free Search grounding on newer models | Model name is an env var. Every AI call has a rules-based fallback |
| BigQuery | Sandbox: 10 GB storage, 1 TB query/month, 60-day table expiry, no DML. If billing is linked you're NOT in sandbox | If billing linked: budget alert + `maximum_bytes_billed` on every query |
| GitHub Actions | Free on public repos; scheduled workflows disable after 60 days of no repo activity | Monthly heartbeat commit |
| GitHub Pages | Free on public repos | One Pages site serves `/site` with a subfolder per project |
| Slack free | 10 apps, 90-day history, no Workflow Builder | One app, incoming webhook only |
| Meta | Business portfolio + dataset + CAPI token are free; no ad account or spend needed for Test Events | All server events carry `test_event_code` in demo |

### Make credit budget (1,000/month)

| Use | Credits per run | Monthly allowance |
|---|---|---|
| Scenario A (lead router) | ~5 | max 100 runs → 500 |
| Scenario B (feedback loop) | ~3 | max 100 runs → 300 |
| Buffer for testing | — | 200 |

Seed scripts default to **15 leads**, never 50. Check usage at Make → Organization → Usage before each demo.

---

## Repo layout created in this file

```
growth-ops-lab/
├── CLAUDE.md                  # global rules Claude Code auto-loads
├── README.md                  # hub: what this is, project table, links
├── CHECKS.md                  # day-1 verification results (fill as you go)
├── .env.example               # every variable, commented
├── .env                       # real values (gitignored)
├── .gitignore
├── pyproject.toml             # uv-managed, Python 3.12
├── plans/                     # these 10 plan files
├── common/
│   ├── __init__.py
│   ├── config.py              # loads .env, exposes DEMO_MODE + settings
│   ├── supabase.py            # tiny REST client (httpx), service-role
│   ├── slack.py               # post_message(text, blocks=None)
│   ├── hubspot.py             # tiny client: get/search/upsert contact, deals
│   ├── hashing.py             # normalize + sha256 for email/phone
│   └── log.py                 # writes to Supabase events_log
├── supabase/
│   ├── migrations/0001_core.sql
│   └── functions/             # edge functions added by P01, P04
├── site/                      # GitHub Pages root
│   ├── index.html             # simple hub page
│   └── thanks.html            # generic thank-you page
├── .github/workflows/
│   ├── keepalive.yml
│   └── pages.yml
└── p01-…/ p02-…/ … (created by each project)
```

---

## Environment variables (`.env.example`)

```
# --- global ---
DEMO_MODE=true                     # true = synthetic/test only. Never touch real accounts.
SITE_BASE_URL=https://<github-username>.github.io/growth-ops-lab

# --- Supabase ---
SUPABASE_URL=
SUPABASE_ANON_KEY=                 # "publishable"/anon key — safe in browser ONLY with RLS
SUPABASE_SERVICE_ROLE_KEY=         # "secret"/service_role key — server/Actions only
SUPABASE_PROJECT_REF=

# --- Slack ---
SLACK_WEBHOOK_URL=

# --- HubSpot (developer TEST account) ---
HUBSPOT_TOKEN=                     # private app token from the test account
HUBSPOT_PORTAL_ID=

# --- Gemini ---
GEMINI_API_KEY=
GEMINI_MODEL=                      # copy exact free model id from AI Studio rate-limit page

# --- Meta ---
META_DATASET_ID=                   # a.k.a. Pixel ID
META_CAPI_TOKEN=
META_TEST_EVENT_CODE=              # TESTxxxxx from Events Manager → Test events
META_GRAPH_VERSION=                # e.g. v24.0 — Claude: look up current version

# --- Google Cloud / BigQuery ---
GCP_PROJECT_ID=
BQ_DATASET=growth_ops
BQ_LOCATION=US                     # MUST be US to join the GA4 public sample
BQ_MAX_BYTES_BILLED=5000000000     # 5 GB safety cap per query

# --- Google Ads (P02, optional level L1) ---
GADS_CUSTOMER_ID=
GADS_CONVERSION_ACTION_ID=

# --- Make ---
MAKE_WEBHOOK_LEADS_URL=            # Scenario A (P01)
MAKE_WEBHOOK_FEEDBACK_URL=         # Scenario B (P02)

# --- Shared secret for edge functions ---
INTAKE_SECRET=                     # random 32+ chars; Make sends it as a header
```

---

## F0 · Mac tools (20 min)

**Prompt for Claude Code:**
```
Phase F0. Check and install what's missing, showing each version afterwards:
- Homebrew (if missing, print the official install command for me to run myself — it needs my password)
- git, gh (GitHub CLI), uv, jq via brew
- Google Cloud SDK: brew install --cask google-cloud-sdk
- Supabase CLI: brew install supabase/tap/supabase
- node (needed later for small JS tests): brew install node
Then confirm ANTHROPIC_API_KEY is NOT set in my shell or in ~/.zshrc / ~/.zprofile. If it is, tell me where and stop.
```

**CHECK:** `git --version`, `gh --version`, `uv --version`, `gcloud --version`, `supabase --version`, `node --version` all print versions. `echo $ANTHROPIC_API_KEY` prints nothing.

---

## F1 · Repo skeleton (20 min)

**YOU:** run `gh auth login` in Terminal (choose GitHub.com → HTTPS → browser login).

**Prompt for Claude Code:**
```
Phase F1. In ~/growth-ops-lab:
1. git init, create the layout from the plan (folders, empty __init__.py, site/index.html placeholder, site/thanks.html with a simple "Thanks — we got it" page).
2. Write CLAUDE.md with the global rules from the "CLAUDE.md contents" section of plans/00-foundation.md.
3. .gitignore: .env, .venv, __pycache__, *.pyc, .DS_Store, **/data/raw/, **/input/real/, **/out/, node_modules, supabase/.temp
4. .env.example exactly as in the plan; copy it to .env.
5. pyproject.toml via uv (python 3.12) with deps: httpx, python-dotenv, pydantic, pyyaml, faker, pandas, google-cloud-bigquery, google-auth, pytest, rich.
6. common/config.py: load .env, expose settings + DEMO_MODE bool; fail with a clear message naming any missing variable when a script asks for it.
7. Create public GitHub repo growth-ops-lab with gh and push.
```

### CLAUDE.md contents (Claude writes this file)
```
# Growth Ops Lab — rules for Claude Code
- Owner: Vishnu (limited coding). You write/run code; explain only manual browser steps.
- Personal, open portfolio: brand-neutral and usable by any kind of organisation. Nothing targeted at a particular company or industry. No client or employer names or data, ever.
- DEMO_MODE=true means: synthetic or public data only; Meta events must include test_event_code; Google uploads are validate-only or dry-run; nothing hits a real ad account.
- Every row written by a demo flow has is_demo=true.
- Secrets live only in .env (local), GitHub Actions secrets, Supabase function secrets, or Make connections. Never commit them. Never print full secrets in logs.
- Never set or use ANTHROPIC_API_KEY.
- Make: webhook triggers only; never add polling/"Watch" modules (they burn credits).
- Every external AI call needs a deterministic fallback.
- Python via `uv run`. Tests via `uv run pytest`. Add a test for every calculation or parser.
- After each phase: run checks, show proof, commit with a clear message, stop.
- Record any limit/plan surprise in CHECKS.md with date.
```

**CHECK:** repo visible on github.com; `uv run python -c "import common.config"` works; `git status` clean; `.env` NOT in the repo.

---

## F2 · Supabase (20 min)

**YOU:**
1. supabase.com → sign in → check how many projects you have. Free allows **2 active**. PlanFair is one. If you already have 2, pause one you don't need (Project settings → Pause).
2. New project → name `growth-ops-lab` → region **Mumbai (ap-south-1)** → generate a strong DB password (save in your password manager).
3. Project Settings → API (or "API Keys"): copy **Project URL**, **anon/publishable key**, **service_role/secret key**, and the **project ref** (the id in the URL). Paste them to Claude (it writes them into `.env` only).

**Prompt for Claude Code:**
```
Phase F2. Write supabase/migrations/0001_core.sql with:
- table leads (id uuid pk default gen_random_uuid(), created_at timestamptz default now(), source text, email text, first_name text, last_name text, company text, company_size text, role text, use_case text, timeline text, utm_source text, utm_medium text, utm_campaign text, gclid text, fbclid text, page_url text, score int, tier text check (tier in ('A','B','C','unscored')), reason text, scored_by text, hubspot_contact_id text, status text default 'new', is_demo boolean default true)
- unique index on lower(email) where status <> 'duplicate'  (so the edge function can upsert)
- table events_log (id bigserial pk, created_at timestamptz default now(), project text, event text, ok boolean, payload jsonb)
- enable RLS on both; NO anon policies (service role only)
Show me the SQL, then tell me to paste it into Supabase → SQL Editor → Run.
Then write common/supabase.py (insert, select, update via REST with service key) and common/log.py, and a script scripts/ping_supabase.py that inserts and reads one events_log row.
```

**YOU:** paste SQL in SQL Editor → Run.

**CHECK:** `uv run scripts/ping_supabase.py` prints the inserted row. Table Editor shows `leads` and `events_log` with RLS "enabled".

---

## F3 · Slack (10 min)

**YOU:**
1. slack.com → create a free workspace `growth-ops-lab` → channel `#leads`.
2. api.slack.com/apps → Create New App → From scratch → name `growth-ops-bot` → pick the workspace.
3. Incoming Webhooks → On → Add New Webhook to Workspace → `#leads` → copy URL → give to Claude.

**Prompt:** `Phase F3. Write common/slack.py and scripts/ping_slack.py that posts "Growth Ops Lab is wired up ✅". Run it.`

**CHECK:** message appears in #leads.

---

## F4 · HubSpot developer test account (20 min)

**YOU:**
1. hubspot.com → sign up for the free CRM with your personal email (not a work account).
2. In that account: **Development** (left nav or top) → **Testing → Test accounts** → **Create developer test account** → name `growth-ops-demo` → keep default (Enterprise trials for all hubs).
3. Open the test account. Go to **Automation → Workflows**. Note in CHECKS.md: "Workflows available: yes/no". (P02 has a fallback if no.)
4. In the test account create a private app token: look under **Development → Legacy apps / Private apps** (HubSpot has renamed this area; if you can't find it, tell Claude and paste a screenshot). Name `growth-ops`. Scopes: `crm.objects.contacts.read`, `crm.objects.contacts.write`, `crm.objects.deals.read`, `crm.objects.deals.write`, `crm.schemas.contacts.write`. Copy the token and the portal (Hub) ID → give to Claude.

**Prompt for Claude Code:**
```
Phase F4. Write common/hubspot.py (search contact by email, upsert contact, create deal + associate to contact, update deal stage, create contact property if missing).
Write scripts/hubspot_setup.py that creates contact properties if missing:
lead_score (number), lead_tier (enumeration A/B/C/unscored), lead_reason (text), lead_source_detail (text), is_demo (booleancheckbox).
Run it, then fetch 1 contact to prove the token works.
Respect HubSpot's rate limit (≤100 requests per 10 s): add a small retry with backoff on 429.
```

**CHECK:** properties visible in HubSpot → Settings → Properties → Contact; script exits 0.

**Calendar reminder:** the Enterprise trial on the test account lasts 90 days. On day ~85, go to your main account → Development → Test accounts → hover the account → **Renew**. Keepalive API calls stop it from expiring for inactivity, but they don't renew the trial.

---

## F5 · Gemini key (10 min)

**YOU:**
1. aistudio.google.com → sign in with personal Gmail → **Get API key** → Create (no card).
2. Open the **rate limit** view in AI Studio. Pick the cheapest **Flash / Flash-Lite** model that shows free requests per day. Write the exact model id and its RPD into CHECKS.md. Give both the key and the model id to Claude.

**Prompt:**
```
Phase F5. Write scripts/ping_gemini.py: call generateContent on GEMINI_MODEL with temperature 0, responseMimeType application/json and a responseSchema {ok:boolean, model:string}. Print the parsed JSON. On 429 or any error print a clear message — don't crash.
```

**CHECK:** prints `{"ok": true, ...}`. Free-tier data may be used by Google to improve products → we only ever send synthetic data.

---

## F6 · Google Cloud + BigQuery (20 min) · LATER

You already have Google Cloud. Check one thing first.

**YOU:**
1. console.cloud.google.com → create project `growth-ops-lab` (note the project ID).
2. Billing → is a billing account linked to this project?
   - **No** → you're in the BigQuery sandbox (tables expire after 60 days; fine, P03 has a reload script).
   - **Yes** → Billing → Budgets & alerts → create budget ₹200/month with email alerts at 50/90/100%. Write "billing linked" in CHECKS.md.
3. Enable APIs: BigQuery API. (P02 later enables Data Manager API.)
4. Terminal: `gcloud auth login` then `gcloud config set project <PROJECT_ID>` then `gcloud auth application-default login`.

**Prompt:**
```
Phase F6. Create BigQuery dataset growth_ops in location US with bq CLI (US is required to query the GA4 public sample in the same job).
Write scripts/ping_bq.py: a dry-run query counting rows in bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_20210131 and print bytes processed, then run it with maximum_bytes_billed from .env.
```

**CHECK:** dataset exists in US; query returns a count; bytes processed printed.

---

## F7 · Meta Business portfolio, dataset, CAPI token (25 min) · LATER

Use your **own** Facebook account — not a work Business Manager.

**YOU:**
1. business.facebook.com → **Create a business portfolio** → name `Growth Ops Lab (Vishnu)`.
2. **Events Manager** → Connect data → **Web** → name `growth-ops-demo` → create (skip the website setup wizard). Copy the **Dataset ID** (= Pixel ID).
3. Dataset → **Settings** → Conversions API → **Generate access token** (under "Set up direct integration"/"Set up manually"). Copy it. If you can't see the button, your user lacks full/developer access on the portfolio — fix in Business settings → People.
4. Dataset → **Test events** tab → copy the test code (`TEST12345`).
5. Give Claude: dataset ID, token, test code.

**Prompt:**
```
Phase F7. Look up the current Meta Graph API version and set META_GRAPH_VERSION.
Write common/meta_capi.py: send_events(events, test=True) → POST https://graph.facebook.com/{ver}/{dataset}/events with access_token, data=[...], and test_event_code when DEMO_MODE or test=True. Hash em/ph/external_id with common/hashing.py (trim, lowercase, sha256 hex). Return Meta's JSON (events_received, fbtrace_id).
Write scripts/ping_meta.py sending one 'Lead' event (action_source 'website', event_source_url SITE_BASE_URL, synthetic email, event_id uuid, event_time now).
```

**CHECK:** response shows `"events_received": 1`; event visible in Events Manager → Test events within a minute.

---

## F8 · Make: account + webhook receiver (20 min)

**YOU:**
1. make.com → sign up free → region EU or US. Open Organization → check **1,000 credits**.
2. Create a scenario named **P01 Lead Router**. Add **Webhooks → Custom webhook** → Add → name `lead-intake` → copy the URL. Add no other modules yet.
3. Do not paste the URL in chat. Run `uv run scripts/set_env.py MAKE_WEBHOOK_LEADS_URL` and paste it at the hidden prompt.
4. On the webhook module click **Redetermine data structure**, leave it waiting, and tell Claude.

**Prompt:**
```
Phase F8. Write scripts/ping_make.py that POSTs one synthetic lead (example.com email, source seed, is_demo true) in the P01 data-contract shape to MAKE_WEBHOOK_LEADS_URL, without printing the URL. Run it once.
```

**CHECK:** Make shows the received fields. CHECKS.md records plan = Free, credits, scenario limit = 2.

Until P01 connects the rest of the scenario, the webhook only receives. There is no redirect to the thank-you page yet.

---

## F9 · Webflow portfolio site (2 hrs)

**Capability check done 2026-11-27:** see `webflow/CAPABILITIES.md`. The Webflow connector builds layout and forms (one site authorised); dropdown options and the form Action URL are set by hand; review and publish by hand.

**Source of page copy:** `webflow/PAGES.md`. Open to any kind of organisation; no company, vendor or industry targeting.

**Pages:** **Home** (portfolio overview) and **Contact** (lead form). The free plan allows 2 static pages (verify in the Designer), so the P05 Calculator page waits.

**YOU:**
1. Free Starter site `growth-ops-lab`, connector authorised for that site only.
2. Add the dropdown options from `webflow/PAGES.md`.
3. Demo form: Action = the Make webhook URL (from your `.env`, never committed), Method = POST.
4. Publish to the `.webflow.io` subdomain and give Claude the site URL (not secret).

**CHECK:** both published pages load on desktop and mobile; SEO titles and descriptions show in the page source; one synthetic form submission appears in Make; CHECKS.md #4 (action URL survives re-publish).

**Failure modes**
| Risk | Handled by |
|---|---|
| Free plan lacks a needed feature | Build by hand, or record the limit in CHECKS.md |
| Action URL lost after a Designer save | Re-check after every publish |
| Webhook URL is visible in the page source, so spam can use Make credits | Check Make Usage; turn the scenario off when not demoing |
| Submissions while the scenario is off or incomplete | Use synthetic test data only; check the webhook queue before turning P01 on |

---

## F10 · GitHub Actions + Pages (30 min)

**Now (slice):** steps 1–5 below, without the monthly heartbeat commit. **Later:** the heartbeat.

**Prompt for Claude Code:**
```
Phase F10.
1. .github/workflows/pages.yml: deploy the /site folder to GitHub Pages on push to main (actions/upload-pages-artifact + actions/deploy-pages).
2. .github/workflows/keepalive.yml:
   - cron every 3 days 04:00 UTC: run scripts/ping_supabase.py (keeps Supabase from pausing)
   - same job: a HubSpot GET (contacts limit 1) so the test account counts as active
   - on the 1st of each month: update .github/heartbeat.txt with the date and commit (keeps scheduled workflows from being disabled after 60 days of inactivity)
   - workflow_dispatch so I can run it manually
   Needs permissions: contents: write.
3. Push every needed secret from .env to GitHub Actions secrets using `gh secret set` (loop over keys; never echo values).
4. Tell me to enable Pages: repo Settings → Pages → Source: GitHub Actions.
5. Trigger keepalive manually with gh workflow run and show the run status.
```

**YOU:** enable Pages as instructed.

**CHECK:** `https://<you>.github.io/growth-ops-lab/` loads the hub placeholder; keepalive run is green.

---

## F11 · Day-1 checks (CHECKS.md)

Claude creates this table; you fill the YOU column.

| # | Check | How | Result | If it fails |
|---|---|---|---|---|
| 1 | Make webhook is instant on free | P01 phase 2 test | | Report; still fine with "Run once" demos |
| 2 | HubSpot test account has Workflows | F4 step 3 | | P02 uses `qualify.py` fallback trigger |
| 3 | Meta "Generate access token" visible | F7 step 3 | | Business settings → give yourself full control |
| 4 | Webflow form custom action saves and survives re-publish | P01 phase 4 | | Re-enter action URL after each Designer save; or move the form to GitHub Pages |
| 5 | Gemini free model + RPD noted | F5 | | Rules fallback handles it |
| 6 | BigQuery billing linked? | F6 | | Budget alert set |
| 7 | Own Google Ads account can be created without billing + UPLOAD_CLICKS conversion action | P02 phase 5 | | P02 stays at level L0 (offline payload validation) |
| 8 | Supabase project count ≤ 2 | F2 | | Pause an unused project |

---

## Foundation DONE checklist (items marked LATER are not needed yet)
- [ ] All tools installed; `ANTHROPIC_API_KEY` empty
- [ ] Repo public, CLAUDE.md present, `.env` not committed
- [ ] Supabase tables + RLS; ping works
- [ ] Slack ping works
- [ ] HubSpot test account + token + properties
- [ ] Gemini ping works (model id recorded)
- [ ] LATER: BigQuery dataset in US; ping works
- [ ] LATER: Meta test event visible in Test events
- [ ] Make account + webhook receives a test; Webflow Home and Contact pages published
- [ ] Pages live; keepalive green; secrets set
- [ ] CHECKS.md filled
