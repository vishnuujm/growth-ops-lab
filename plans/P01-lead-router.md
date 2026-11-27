# P01 · Lead Router Agent (+ nightly CRM hygiene)

**Time:** ~4–5 hrs · **Needs:** F0–F5, F8, F9 and the F10 slice · **Uses Make slot:** Scenario A · **Cost:** ₹0

**One-liner:** "Any inbound form lands in the CRM scored against the ICP, with a reason, in under a minute — hot leads ping sales in Slack, and a nightly job keeps the CRM clean. If the AI is down, a rules model scores it instead, so nothing is ever lost."

---

## How to start this chat
New Claude Code session in `~/growth-ops-lab`, first message:
```
Read CLAUDE.md and plans/P01-lead-router.md. Follow it phase by phase.
After each phase run the CHECK steps, show proof, commit, and wait for me.
Anything marked YOU is mine in the browser — give me exact clicks.
```

---

## Architecture

```
Webflow form (custom action)  ─┐
Calculator form (P05)          ├─► Make Scenario A: Custom webhook
seed script (demo)            ─┘        │
                                        ▼
                         HTTP → Supabase Edge Function `score-lead`
                         (validates, dedupes, Gemini score → rules fallback,
                          inserts/updates `leads`, returns JSON)
                                        │
                                        ▼
                         HubSpot: create/update contact (by email)
                                        │
                              Router (0 credits)
                         tier A ─► Slack "hot lead" (HTTP)
                         B/C   ─► (nothing now; nightly digest)
                                        ▼
                         Webhook response: 200 + HTML meta-refresh → /thanks.html

GitHub Actions 02:30 IST nightly → hygiene/nightly.py (Python, no Make credits)
```

**Why scoring sits in an Edge Function, not in Make:**
- The Gemini key never sits in Make.
- The rules fallback is real code with tests.
- It saves 1–2 Make credits per lead (Make would need an extra "Parse JSON" module).
- Make still does the orchestration (CRM, routing, Slack, response).

**Credits per lead:** webhook 1 + HTTP 1 + HubSpot 1 + Slack 1 (A only) + response 1 = **4–5**.

---

## Files this project creates

```
p01-lead-router/
├── README.md
├── icp.yaml                       # scoring rubric (brand-neutral, editable)
├── prompts/score_lead.md          # Gemini prompt template
├── seed/
│   ├── fake_leads.py              # 15 leads with known expected tiers
│   ├── expected.csv               # answer key for tests
│   └── send_to_webhook.py         # posts leads to MAKE_WEBHOOK_LEADS_URL
├── hygiene/nightly.py             # dedupe, rescore, reconcile, digests
├── make/
│   ├── BUILD.md                   # module-by-module settings (Claude writes)
│   └── scenario-A.blueprint.json  # exported from Make after build
├── webflow/FORM.md                # exact field names + settings
├── tests/test_rules.py            # Python mirror of rules for test parity
└── docs/architecture.md           # mermaid diagram
supabase/functions/score-lead/index.ts
supabase/functions/score-lead/rules.ts
.github/workflows/p01-nightly.yml
```

---

## Data contract (webhook payload)

All fields are strings unless noted. Missing fields are allowed except `email`.

| Field | Values / notes |
|---|---|
| email | required; lowercase+trim in function |
| first_name, last_name, company, role | free text |
| company_size | `1-10`, `11-50`, `51-200`, `201-1000`, `1000+` |
| use_case | free text (what they want to solve) |
| timeline | `now`, `1-3m`, `3-6m`, `exploring` |
| source | `webflow_form`, `calculator`, `seed` (default `webflow_form` if missing) |
| utm_source / utm_medium / utm_campaign / gclid / fbclid / page_url | optional (Webflow free form can't send these — no hidden-field JS; calculator can) |
| is_demo | `true` for seed |

**Function response (what Make maps):**
```json
{"lead_id":"uuid","email":"...","score":82,"tier":"A","reason":"Mid-size team, buying now, clear use case","scored_by":"gemini|rules","is_duplicate":false}
```

---

## Phase 1 · ICP + rules model (45 min)

**Prompt for Claude Code:**
```
P01 Phase 1.
1. Write p01-lead-router/icp.yaml as a default fit profile that any organisation can edit (brand-neutral, no industry assumed):
   - company_size weights (51-200 and 201-1000 highest), role seniority keywords (head, director, vp, founder, manager, lead → points; intern/student → negative),
   - timeline weights (now > 1-3m > 3-6m > exploring),
   - use_case signals: positive keywords (automate, improve, replace, scale, integrate, reporting, CRM, pipeline) and junk signals (test, asdf, job, internship; "free" removed after review because it penalised real needs such as "free up time"),
   - free-email domains list (gmail, yahoo, outlook, hotmail, proton) → small penalty,
   - thresholds: A ≥ 70, B 40–69, C < 40.
2. Write supabase/functions/score-lead/rules.ts implementing it (pure function, returns {score,tier,reason}).
3. Write tests/test_rules.py with a Python mirror of the same logic, plus seed/fake_leads.py generating 15 leads: 5 designed A, 5 B, 4 C, plus 1 duplicate of an A lead; write seed/expected.csv with expected tiers.
4. uv run pytest — all expected tiers must match. Show the table.
```

**CHECK:** pytest green; table shows 15 leads with expected vs rules tier all matching.

---

## Phase 2 · Edge Function `score-lead` (60 min)

**YOU:** Terminal: `supabase login` (browser opens) → then tell Claude it's done.

**Prompt:**
```
P01 Phase 2.
1. supabase link --project-ref $SUPABASE_PROJECT_REF
2. Create supabase/functions/score-lead/index.ts (Deno):
   - Reject unless header x-intake-secret == INTAKE_SECRET (401).
   - Accept JSON or form-urlencoded (Webflow posts form-urlencoded).
   - Validate email format; normalize fields; default source.
   - Dedupe: if a non-duplicate lead with same lower(email) exists → update it (keep oldest id), is_duplicate=true.
   - Score: call Gemini (GEMINI_MODEL) with prompt from icp rubric, temperature 0, responseMimeType application/json, responseSchema {score:int 0-100, tier: enum A/B/C, reason: string ≤200 chars}; 8-second timeout. On any error/429/invalid JSON → rules.ts; set scored_by accordingly. If DEMO_MODE and GEMINI_API_KEY empty → rules only.
   - Insert/update leads using SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (available inside functions).
   - Return the response JSON from the plan. Never return the reason with PII beyond what was sent.
   - Log to events_log (project 'p01', event 'scored').
3. Set secrets: supabase secrets set GEMINI_API_KEY GEMINI_MODEL INTAKE_SECRET DEMO_MODE (from .env, don't echo values).
4. Deploy: supabase functions deploy score-lead --no-verify-jwt   (if it complains about Docker, retry with --use-api)
5. Test with curl: one good lead, one junk lead, one duplicate, one with wrong secret (expect 401). Show responses.
```

**CHECK:**
- Good lead → tier A or B, `scored_by: gemini`.
- Junk → tier C.
- Duplicate → `is_duplicate: true`, still one row in Supabase.
- Wrong secret → 401.
- Temporarily set `GEMINI_MODEL=nonexistent` → `scored_by: rules` (then restore).

---

## Phase 3 · Make Scenario A (60 min, mostly YOU)

**Prompt first:** `P01 Phase 3. Write p01-lead-router/make/BUILD.md with exact module-by-module settings for Scenario A from the plan, including the exact JSON body for the HTTP module and every field mapping. Then wait while I build it.`

**YOU (Make UI), following BUILD.md:**
1. Open the scenario **"P01 Lead Router"** created in F8.
2. The `lead-intake` **Custom webhook** module already exists from F8 (`MAKE_WEBHOOK_LEADS_URL` is in `.env`; never paste it in chat). On it, click **"Redetermine data structure"**, then ask Claude: `run seed/send_to_webhook.py --one`. Make captures the fields.
3. **HTTP → Make a request**: URL `https://<project-ref>.supabase.co/functions/v1/score-lead`, POST, header `x-intake-secret: <INTAKE_SECRET>`, body type Raw, content type JSON, body = the JSON from BUILD.md with mapped webhook fields, **Parse response: Yes**.
4. **HubSpot CRM → Create/Update a contact** (upsert by email; module name may differ slightly). Connect HubSpot with OAuth and choose the **test account** portal. Map lead_score, lead_tier, lead_reason, lead_source_detail, is_demo.
5. **Webhooks → Webhook response**, placed right after HubSpot and **before** the router so it always runs: status 200; header `Content-Type: text/html`; body `<meta http-equiv="refresh" content="0;url=SITE_BASE_URL/thanks.html">Thanks!`
6. **Router** → route 1 filter `tier = A` → **HTTP → Make a request** POST to `SLACK_WEBHOOK_URL`, JSON body from BUILD.md (🔥 name, company, score, reason, HubSpot link). There's no second route; B/C leads just end.
7. **Scheduling:** "Immediately as data arrives" (instant). Turn the scenario **ON**.
8. Export blueprint (… menu → Export Blueprint) → save as `p01-lead-router/make/scenario-A.blueprint.json`. **The export can contain the intake secret and Slack webhook URL: Claude replaces them with placeholders and scans the file before any commit.**

**Error handling:** right-click the HubSpot module → Add error handler → **Resume** (0 credits). A HubSpot hiccup must not stop the Slack alert or the response; nightly reconciles it.

**CHECK:** `uv run p01-lead-router/seed/send_to_webhook.py --one` → within ~10 s you see: Supabase row, HubSpot contact with lead_score, Slack ping if tier A. In Make, the run shows ~5 credits. Fill CHECKS.md #1 (instant: yes/no).

---

## Phase 3b · Failed-submission path (45 min)

A submission must never fail silently.

| Failure | Function reply | What happens |
|---|---|---|
| Invalid or missing email | 422 | Failure path; the function logs `submission_failed` (no full email) |
| Wrong secret | 401 | Failure path |
| Function error or timeout | 5xx / no reply | Failure path; it cannot log to Supabase, so the Slack alert and Make history are the record |

**Prompt:** `P01 Phase 3b. Make the function return these codes and log failures. Add to make/BUILD.md an error handler on the HTTP module: Slack "submission failed" (time and status, no personal data) → Webhook response with a "please try again" page linking back to the form → end the run. Set the HTTP module to treat error statuses as errors.`

**YOU:** add the error route in Make from BUILD.md, then re-export the blueprint.

**CHECK:** send an invalid email, then a temporarily wrong secret (restore it afterwards): each shows the retry page and posts one Slack alert; a good lead still succeeds. Fill CHECKS.md #10.

**Limit:** if Make itself is down or out of credits, this path cannot run.

---

## Phase 4 · Webflow form (30 min, YOU)

**Prompt first:** `P01 Phase 4. Write p01-lead-router/webflow/FORM.md: exact field names, field types and select options matching the data contract, plus Form Block settings.`

**YOU (Webflow Designer, Contact page form from F9):**
1. Use the demo-form **Form Block** built in F9 (add it if missing).
2. Fields with **Name** exactly: `email` (Email, required), `first_name`, `company`, `role`, `company_size` (Select: options from data contract), `use_case` (Textarea), `timeline` (Select).
3. Form Block settings → **Action** = `MAKE_WEBHOOK_LEADS_URL`, **Method** = POST.
4. Publish. Submit one real test with your own email.
5. Re-open Designer, make any small edit, save, publish again, and check the Action URL is still set (CHECKS.md #4).

**The intake secret header:** Webflow can't add headers, so Make adds it in the HTTP module. The secret sits in Make, never in the browser. That is why Make (not the form) calls the function.

**Spam note:** a custom action bypasses Webflow's spam filtering. The function rejects bad emails, and junk lands as tier C. Good enough for a demo; in live mode, add a honeypot on the calculator form (P05).

**CHECK:** the form submit redirects to /thanks.html, and the lead shows in Supabase + HubSpot.

---

## Phase 5 · Seed the demo (15 min)

**Prompt:**
```
P01 Phase 5. Run seed/send_to_webhook.py for all 15 leads with a 3-second gap (stay well under rate limits). Then query Supabase and compare tiers to expected.csv. Show a table: email, expected, actual, scored_by. Show Make credits used (estimate 15 × ~5 = 75).
```

**CHECK:** ≥ 13/15 match expected (Gemini may disagree on borderline B/C. That's fine, and the reason column explains why). The duplicate shows as one row.

---

## Phase 6 · Nightly hygiene (45 min)

**Prompt:**
```
P01 Phase 6. Write hygiene/nightly.py (uses common/ clients, no Make):
1. Rescore leads with tier 'unscored' or scored_by 'rules' in the last 7 days by calling the score-lead function (only if Gemini is reachable; max 10 per night to protect free RPD).
2. Dedupe: any leads sharing lower(email) → keep oldest, mark others status='duplicate'.
3. Reconcile HubSpot: for leads with empty hubspot_contact_id → search HubSpot by email; if found store id; if missing → upsert contact.
4. Stale hot leads: tier A, status still 'new' after 48h → Slack digest "⚠️ N hot leads untouched".
5. Daily digest: count by tier for last 24h + list of B leads → one Slack message.
6. Log a summary row in events_log.
Add --dry-run flag. Then .github/workflows/p01-nightly.yml: cron '0 21 * * *' (02:30 IST), workflow_dispatch, uses secrets. Run it manually via gh and show the Slack output.
```

**CHECK:** the Actions run is green; Slack digest posted; dry-run prints planned changes without writing.

---

## Phase 7 · README + diagram (30 min)

**Prompt:** `P01 Phase 7. Write p01-lead-router/README.md: problem, architecture (mermaid), tools and why each, data contract, demo vs live, credit math, failure modes and how each is handled, "Connect your account in 5 minutes" steps, and a 'what I'd change at scale' section (queue in front of Make, enrichment via Clay/Apollo, round-robin owner assignment, SLA tracking). Add a row to the root README project table and a card on site/index.html.`

**YOU:** record a 60–90 s Loom: submit the Webflow form → Slack ping → HubSpot contact with score/reason → Supabase row. Paste the link into the README.

---

## Demo vs Live

| | Demo (now) | Live (5 min) |
|---|---|---|
| Form | Your Webflow form + seed | Any form that can POST (Webflow, HubSpot form webhook, Typeform) → same Make URL |
| CRM | HubSpot developer test account | Reconnect Make HubSpot module to the real portal; create the 5 properties with hubspot_setup.py |
| ICP | Generic icp.yaml | Edit weights/keywords in icp.yaml + prompt |
| Slack | Your workspace | Client channel webhook |
| Flag | DEMO_MODE=true, is_demo=true | DEMO_MODE=false |

---

## Anomalies already handled (don't rediscover these)

| Risk | Handled by |
|---|---|
| Polling triggers burn Make credits | Webhook trigger only |
| Webflow can't send hidden fields / UTMs / headers | Default `source`; UTMs only from the P05 calculator; secret added by Make |
| Webflow posts form-urlencoded, not JSON | Function accepts both |
| Gemini free RPD tiny or model retired | Model in env; rules fallback; nightly rescore capped at 10 |
| HubSpot 429 / outage | Retry with backoff in Python; Make error handler "Resume"; nightly reconcile |
| Duplicate submits | Unique index + upsert in function; nightly dedupe |
| Edge function public URL abuse | `x-intake-secret` header check; validation |
| Secrets in browser | None; the browser only sees the Make URL |
| Supabase pause / HubSpot test-account expiry | Foundation keepalive |
| Running out of Make credits mid-demo | Seed is 15 leads; check Usage before demos |

## Troubleshooting
- **Make shows no fields:** click "Redetermine data structure" again, then resend one lead.
- **HTTP module 401:** the secret header name or value doesn't match the function secret. Re-run `supabase secrets list`.
- **HubSpot module can't see the test account:** delete the connection and re-add it while logged into the test portal in the same browser.
- **Form doesn't redirect:** the Webhook response module is missing, or isn't on the executed route.

## DONE checklist
- [ ] Rules tests green
- [ ] Function deployed; 5 curl tests pass
- [ ] Scenario A on; blueprint exported (webhook URL and secret removed before commit)
- [ ] Failed-submission path proven
- [ ] Webflow form works and action URL survives re-publish
- [ ] 15 seed leads processed; table shown
- [ ] Nightly action green
- [ ] README + Loom + hub card

## Design highlights
- "I moved the scoring into code so it's testable and has a fallback — the automation tool only orchestrates."
- "I designed around the free plan's limits: webhooks not polling, 4–5 credits per lead, and the secret stays server-side."
- "Same pattern fits any inbound motion: swap the ICP file and the CRM connection."
