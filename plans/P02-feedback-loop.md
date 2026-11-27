# P02 · Qualified-Lead Feedback Loop (CRM → Meta CAPI + Google Data Manager)

**Time:** ~4–5 hrs · **Needs:** 00 + P01 done · **Uses Make slot:** Scenario B · **Cost:** ₹0

**One-liner:** "Ad platforms optimise for whatever you tell them is a conversion. This sends *qualified* and *won* deals from the CRM back to Meta and Google, so bidding chases pipeline, not form fills."

---

## How to start this chat
```
Read CLAUDE.md and plans/P02-feedback-loop.md. Follow it phase by phase.
After each phase run the CHECK steps, show proof, commit, and wait for me.
```

---

## What's verified and what it forces

| Fact | Consequence |
|---|---|
| Google Ads API stopped accepting new offline-conversion adopters (15 Jun 2026) | Google leg uses the **Data Manager API** |
| Data Manager needs a Google Ads account ID (`operatingAccount`) + a conversion action of type **UPLOAD_CLICKS**, scope `datamanager`, and supports `validateOnly` | 3 levels below; L0 always works |
| Google Ads test accounts can't import conversions | Don't use a test account for L1 |
| Meta CAPI works with just a dataset + token; `test_event_code` shows events in Test Events with no ad account or spend | Meta leg is fully live in demo |
| Meta rejects website/system events older than 7 days | Demo events always use `event_time = now` |
| HubSpot workflows ("Send a webhook") may or may not show in the test account | Trigger has primary + fallback |
| Make polling costs credits on every check | Trigger is a webhook, never "Watch deals" |

### Google levels
- **L0 (always works):** build the exact Data Manager request, validate it locally (pydantic schema + normalization + hashing checks), save it to `out/google_request_<id>.json`.
- **L1 (try):** call `events:ingest` with `validateOnly: true` against your own Google Ads account. Needs CHECKS.md #7 = yes.
- **L2 (live):** same call with `validateOnly: false` on a real account. Config change only.

---

## Architecture

```
HubSpot (test account)
  deal moves to "qualifiedtobuy" (SQL) or "closedwon"
        │  PRIMARY: HubSpot workflow → "Send a webhook"
        │  FALLBACK: p02/qualify.py moves the stage via API AND posts the same payload
        ▼
Make Scenario B: Custom webhook
  → HTTP: POST Meta CAPI /{dataset}/events (sha256 in Make, test_event_code)
  → HTTP: Supabase insert `conversions` row (meta_status, meta_response, google_status='pending')
  → (optional, tier A only) Slack "✅ SQL sent to Meta"
        ▼
GitHub Actions every 6h (or manual): p02/google_uploader.py
  reads conversions where google_status='pending' → L0 / L1 / L2 → updates row
```

**Credits per event:** webhook 1 + Meta HTTP 1 + Supabase HTTP 1 (+ Slack 1) = **3–4**.

---

## Files

```
p02-feedback-loop/
├── README.md
├── mapping.yaml              # stage → event name, value, currency
├── qualify.py                # demo driver: create deals, move stages, post to Make (fallback trigger)
├── google_uploader.py        # L0/L1/L2 Data Manager uploader
├── schemas.py                # pydantic models for both payloads
├── make/BUILD.md
├── make/scenario-B.blueprint.json
├── tests/test_payloads.py    # hashing, normalization, event_id dedupe, schema
└── out/                      # L0 request files (gitignored)
supabase/migrations/0002_conversions.sql
.github/workflows/p02-google.yml
```

---

## Phase 1 · Schema + mapping (30 min)

**Prompt:**
```
P02 Phase 1.
1. supabase/migrations/0002_conversions.sql: table conversions (id uuid pk, created_at, lead_id uuid references leads(id), hubspot_deal_id text, stage text, event_name text, value numeric, currency text, event_id text unique, email_sha256 text, gclid text, fbc text, meta_status text, meta_response jsonb, google_level text, google_status text default 'pending', google_response jsonb, is_demo boolean default true). RLS on, no anon policies. Show SQL for me to run.
2. p02-feedback-loop/mapping.yaml:
   qualifiedtobuy → event_name "QualifiedLead", value 5000, currency INR
   closedwon → event_name "Purchase", value from deal amount, currency INR
   (HubSpot default pipeline internal stage ids: verify by listing pipelines via API and print them.)
3. schemas.py + tests: email normalization (trim, lowercase), sha256 hex, fbc format fb.1.<ms>.<fbclid>, event_id = f"{deal_id}:{stage}" (stable → dedupes retries).
uv run pytest.
```

**YOU:** run the SQL in the Supabase SQL Editor.

**CHECK:** the table exists; tests are green; the pipeline stage ids printed match mapping.yaml.

---

## Phase 2 · Make Scenario B (60 min, mostly YOU)

**Prompt first:** `P02 Phase 2. Write make/BUILD.md for Scenario B: exact modules, the webhook payload fields (deal_id, stage, amount, email, gclid, fbclid, lead_id, is_demo), the Meta CAPI JSON body using Make's sha256() and lower()/trim() functions, and the Supabase insert body.`

**Meta event body (shape only — `{{…}}` are placeholders; Claude replaces them with exact Make functions, e.g. Unix seconds for event_time, in BUILD.md):**
```json
{
  "data": [{
    "event_name": "QualifiedLead",
    "event_time": "{{timestamp}}",
    "event_id": "{{deal_id}}:{{stage}}",
    "action_source": "system_generated",
    "user_data": {
      "em": ["{{sha256(lower(trim(email)))}}"],
      "external_id": ["{{sha256(lead_id)}}"],
      "fbc": "fb.1.{{timestamp_ms}}.{{fbclid}}"
    },
    "custom_data": { "value": 5000, "currency": "INR", "event_source": "crm", "lead_event_source": "HubSpot" }
  }],
  "test_event_code": "{{META_TEST_EVENT_CODE}}"
}
```
Omit `fbc` when fbclid is empty (use a Make `if()`; an empty fbc string is rejected or wasted).

**YOU (Make UI):**
1. New scenario **"P02 Feedback Loop"** → Custom webhook `crm-stage-change` → copy URL → `MAKE_WEBHOOK_FEEDBACK_URL` to Claude.
2. Ask Claude: `run qualify.py --one --post-only` so Make learns the structure.
3. HTTP → POST `https://graph.facebook.com/{ver}/{dataset}/events?access_token={token}`, body above, Parse response Yes.
4. HTTP → POST `{SUPABASE_URL}/rest/v1/conversions` with headers `apikey` + `Authorization: Bearer <service key>` + `Prefer: return=minimal`; body maps the Meta response into `meta_status`/`meta_response`.
   - The service key in a Make HTTP header is acceptable (Make stores scenario data privately).
   - Alternative if you prefer: create a 2nd edge function `log-conversion` with the intake secret. Claude can do it — same pattern as P01.
5. Error handler on the Meta module → **Resume**, so the Supabase log still records `meta_status='error'`.
6. Scheduling: Immediately. **ON.** Export the blueprint.

**CHECK:** `uv run p02-feedback-loop/qualify.py --one --post-only` → Events Manager → Test events shows **QualifiedLead** with matched keys (em, external_id); Supabase `conversions` row with `meta_status='sent'`.

---

## Phase 3 · Trigger: primary (HubSpot workflow) or fallback (15–45 min)

Check CHECKS.md #2.

**If workflows ARE available (YOU):**
1. Test account → Automation → Workflows → Create → **Deal-based** → Enrollment trigger: Deal stage is any of *Qualified to buy*, *Closed won*. Allow re-enrollment.
2. Action: **Send a webhook** → POST → `MAKE_WEBHOOK_FEEDBACK_URL` → include deal properties (deal id, dealstage, amount) and associated contact email.
   - If the webhook action can't include the contact email, Make adds 1 HubSpot "Get contact" module (+1 credit). Note this in BUILD.md.
3. Turn on.

**If NOT available:** `qualify.py` is the trigger (it already moves the stage AND posts the payload). In live mode, a portal with a workflow-capable HubSpot tier uses the primary path. Write that in the README; it's an honest design choice.

**Prompt (both cases):**
```
P02 Phase 3. Finish qualify.py:
--create N: for N demo leads from Supabase (tier A/B, is_demo), create a HubSpot deal associated to the contact (stage appointmentscheduled), store deal id.
--advance: move 60% to qualifiedtobuy and 20% to closedwon (amounts 50k–3L INR).
--post-only: also POST the payload to Make (use when HubSpot workflows are unavailable).
Synthetic gclid/fbclid for ~70% of leads (realistic shapes). Max 10 deals per run. Show a table of what happened.
```

**CHECK:** run `qualify.py --create 8 --advance` (with `--post-only` if needed) → Test events shows ~6–7 events; Supabase has matching rows; nothing is duplicated when you re-run (event_id is stable).

---

## Phase 4 · Google uploader L0 (45 min)

**Prompt:**
```
P02 Phase 4. Fetch the Data Manager API docs for events:ingest (send events + formatting/normalization guide). Then write google_uploader.py:
- Read conversions where google_status='pending'.
- Build the request: destinations[{operatingAccount:{product/accountType: GOOGLE_ADS, accountId: GADS_CUSTOMER_ID or "0000000000" in L0}, productDestinationId: GADS_CONVERSION_ACTION_ID or "0"}], encoding HEX, events with adIdentifiers.gclid, eventTimestamp (RFC3339), transactionId=event_id, conversionValue, currency, userData email hashed per Google's normalization rules (follow the doc exactly, e.g. gmail handling), consent fields per docs, validateOnly true.
- Level auto-detect: L0 if GADS ids empty; L1 if ids set and DEMO_MODE; L2 if ids set and DEMO_MODE=false.
- L0: validate with pydantic, write out/google_request_<event_id>.json, set google_status='validated_offline', google_level='L0'.
- Add tests for the normalization and the request shape.
Then .github/workflows/p02-google.yml: every 6 hours + workflow_dispatch.
```

**CHECK:** the request JSON files look exactly like the doc's example; tests green; Supabase rows updated to `validated_offline`.

---

## Phase 5 · Google uploader L1 (optional, 45 min)

**YOU:**
1. ads.google.com with your **personal** Gmail → create a new account. If offered, **Switch to Expert Mode → Create an account without a campaign**.
   - If it forces billing or a campaign before continuing, stop. You stay at L0 (CHECKS.md #7 = no).
2. If created: Goals → Conversions → New → **Import → Website (import from clicks)**, i.e. an **UPLOAD_CLICKS**-type action named `Qualified lead (CRM)`. Copy the account ID (no dashes) + conversion action ID.
3. GCP console → enable **Data Manager API**. Terminal:
   `gcloud auth application-default login --scopes=https://www.googleapis.com/auth/datamanager,https://www.googleapis.com/auth/cloud-platform`
4. Give Claude both IDs.

**Prompt:** `P02 Phase 5. Implement L1: call POST https://datamanager.googleapis.com/v1/events:ingest with validateOnly true using application-default credentials and the quota project header. Store the full response. If it errors, show me the error verbatim and explain it — don't guess-fix more than twice.`

**CHECK:** a 200 with a requestId → `google_status='validated_api'`.
- If it errors because the gclids are synthetic, that is expected. Record it in the README: "the request is valid; only real clicks can attribute".
- If it errors on permissions, fix the user/account access once, then stop at L0.

---

## Phase 6 · README + Loom (30 min)

**Prompt:** `P02 Phase 6. README: why offline conversions matter (algorithm learns from SQLs not form fills), architecture, the June-2026 Google API change and why Data Manager, levels L0/L1/L2, event dedupe via event_id, hashing/consent, timings (Meta 7-day window), demo vs live, credit math, 'at scale' (value-based bidding using predicted deal value, lead-ads lead_id path, server-side GTM). Update root README + hub card.`

**YOU:** Loom: move a deal in HubSpot (or run qualify.py) → Test Events shows the event → Supabase row → the L0 request file.

---

## Demo vs Live

| | Demo | Live |
|---|---|---|
| CRM | HubSpot test account; qualify.py | Real portal workflow → same Make webhook |
| Meta | Dataset + `test_event_code` | Client dataset + token; remove test code (DEMO_MODE=false) |
| Google | L0 / L1 validateOnly | L2 with the client's account + UPLOAD_CLICKS action |
| Values | Fixed 5,000 INR for SQL | Predicted or real deal value |

## Anomalies handled
| Risk | Handling |
|---|---|
| Duplicate events on retries | Stable event_id (`deal:stage`) for Meta; transactionId for Google; unique index |
| Empty fbc/gclid | Omitted instead of sent empty |
| PII in logs | Only hashes stored in Supabase |
| Old events rejected | Demo uses now(); live runs within minutes |
| Workflows missing in test account | qualify.py fallback trigger |
| Google L1 blocked | L0 is a complete, documented deliverable |
| Make credits | ≤10 deals per run; 3–4 credits each |

## DONE checklist
- [ ] conversions table; tests green
- [ ] Scenario B on; blueprint exported
- [ ] Events visible in Meta Test events
- [ ] Trigger working (workflow or fallback)
- [ ] Google L0 files (+ L1 if possible)
- [ ] Actions workflow green
- [ ] README + Loom + hub card

## Design highlights
- "Lead-gen accounts usually optimise for junk because the platform only sees the form fill. This closes the loop."
- "Google deprecated the old offline-import path for new users in June 2026. I built on the Data Manager API with validate-only so it's ready the day a real account is connected."
