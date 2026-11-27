# P04 · "Which Bike Should I Buy?" Quiz (passion project, real users)

**Time:** ~5–6 hrs · **Needs:** 00 done · **Cost:** ₹0 · **Hosting:** GitHub Pages (`/site/bike-quiz/`)

**One-liner:** "A fun quiz I built for Indian riders that shows the full growth stack on a tiny product: a funnel, events, Pixel + server-side CAPI with dedupe, UTM-tracked organic launch, and a results dashboard."

---

## How to start this chat
```
Read CLAUDE.md and plans/P04-bike-quiz.md. Follow it phase by phase.
I know bikes — ask me to confirm the shortlist and spot-check specs. Stop after each phase.
```

---

## Architecture

```
GitHub Pages /bike-quiz/ (vanilla HTML/CSS/JS, no build step)
  ├─ quiz.js: questions → hard filters → weighted score → top 3 + "why"
  ├─ analytics.js: GA4 gtag events + Meta Pixel (browser) with event_id
  ├─ consent banner: analytics/ads only after "OK"
  ├─ POST response → Supabase REST (anon key, INSERT-only RLS)
  └─ POST server event → Supabase Edge Function `capi-relay` (same event_id → Meta dedupes)
Supabase view quiz_stats_public (aggregates only) → /bike-quiz/stats.html (anon SELECT on view only)
```

There's no Make here, so it costs 0 credits.

---

## Files

```
site/bike-quiz/
├── index.html            # landing + quiz
├── stats.html            # public aggregate dashboard
├── quiz.js               # logic
├── analytics.js          # GA4 + Pixel + CAPI relay calls
├── consent.js
├── styles.css
├── bikes.json            # the dataset (with source_url + checked_on)
└── questions.json
p04-bike-quiz/
├── README.md
├── data/build_bikes.py   # validates bikes.json (schema, ranges, required sources)
├── tests/test_scoring.mjs  # node --test; same logic as quiz.js
└── launch/LAUNCH.md      # UTM links + where to post + post copy
supabase/migrations/0003_quiz.sql
supabase/functions/capi-relay/index.ts
```

---

## Phase 1 · Shortlist + questions (YOU + Claude, 45 min)

**YOU:** give Claude your shortlist of ~25 current Indian-market bikes across commuter, street/naked, sport, ADV/tourer, cruiser and retro, spanning ₹1L–₹4L. You know this better than any model; that's why it's a passion project.

**Prompt:**
```
P04 Phase 1. Draft questions.json (10 questions):
budget band, main use (city/highway/mixed/trails), riding experience, rider height, pillion frequency, weekly km, top priority (mileage/performance/comfort/looks/reliability), style preference, service-network importance, open to any brand vs preferred brands.
Each option maps to scoring signals. Show me the questions for approval before writing scoring.
```

**CHECK:** you approve the questions (edit wording to sound like a rider, not a marketer).

---

## Phase 2 · Bike dataset (60–90 min)

**Prompt:**
```
P04 Phase 2. For each bike in my shortlist, research current specs from the manufacturer's official India site (WebSearch/WebFetch), and fill bikes.json:
name, brand, segment, engine_cc, power_ps, torque_nm, kerb_weight_kg, seat_height_mm, fuel_tank_l, abs (single/dual), price_inr_approx (ex-showroom, lowest variant), type, tags (beginner-friendly, highway, city, pillion-friendly, off-road-capable, low-maintenance), short pros (2) and cons (2) in your own words, source_url, checked_on (today).
Rules: never invent a number — if not found, set null and list it for me. No images (copyright).
Then write data/build_bikes.py to validate: required fields, plausible ranges (cc 100–1300, seat 700–900 mm), every row has source_url.
```

**YOU:** spot-check 5 bikes against the official sites, fix any nulls you know, and approve.

**CHECK:** the validator passes, and the null list is empty or accepted.

---

## Phase 3 · Scoring + tests (60 min)

**Prompt:**
```
P04 Phase 3. quiz.js scoring:
1. Hard filters: price within budget band +10%; seat_height_mm ≤ rider-height threshold table (e.g. <165 cm → ≤ 800 mm) unless no bikes pass → relax with a note.
2. Weighted score from answers → tags/specs (document every weight in a comment table).
3. Output top 3 with 2-line "why" generated from matched signals (template text, no AI).
4. Tie-break by price fit.
Write tests/test_scoring.mjs (node --test) with 8 personas (short beginner city rider ₹1.5L, tall highway tourer ₹3.5L, etc.) and expected bikes in top 3. Make quiz.js export functions so tests import the same code.
```

**CHECK:** `node --test p04-bike-quiz/tests` is green, and the personas' results feel right to you.

---

## Phase 4 · UI (60 min)

**Prompt:**
```
P04 Phase 4. Build index.html + styles.css: mobile-first, one question per screen, progress bar, back button, results page with top 3 cards (specs table, why, pros/cons, 'source' link), share buttons (WhatsApp, copy link with ?utm_source=share), 'retake'. Fast: no frameworks, no images, < 100 KB total. Disclaimer: 'Prices approx ex-showroom, checked <date>. Always test ride.'
Local preview: python -m http.server in /site and give me the URL.
```

**CHECK:** works on your phone (use the Pages URL after pushing); Lighthouse mobile performance ≥ 90.

---

## Phase 5 · Supabase storage (30 min)

**Prompt:**
```
P04 Phase 5. 0003_quiz.sql:
- quiz_responses(id uuid, created_at, session_id text, answers jsonb, top3 jsonb, utm_source, utm_medium, utm_campaign, referrer text, completed boolean, is_demo boolean default false)
- RLS: anon can INSERT only (with check: answers is not null, size limit via length(answers::text) < 5000); anon cannot SELECT/UPDATE/DELETE.
- view quiz_stats_public: completions per day, top recommended bikes, answer distributions (aggregates only, no rows, no referrer).
- grant select on the view to anon (security_invoker off / documented).
Show SQL for me to run. Then wire quiz.js to POST the response via REST with the anon key (Prefer: return=minimal). Write stats.html reading the view with Chart.js from a CDN.
```

**YOU:** run the SQL.

**CHECK:** complete the quiz → a row appears (in Table Editor). In the browser console, a `select` on `quiz_responses` with the anon key **fails**, and a select on the view works.

---

## Phase 6 · Analytics: GA4 + Pixel + CAPI relay (75 min)

**YOU:**
1. analytics.google.com → create a free GA4 property "Bike Quiz" → Web stream for your github.io URL → copy the Measurement ID.
2. Meta: use the dataset from F7 (or create a 2nd dataset "bike-quiz" in the same portfolio, which is cleaner). Give Claude the IDs.

**Prompt:**
```
P04 Phase 6.
1. analytics.js: load GA4 + Pixel ONLY after consent. Events: quiz_start, question_answered (index), quiz_complete (top1 segment), result_click, share_click. Pixel: PageView, custom 'QuizComplete', 'Lead' only if the user opts into the optional "email me new comparisons" field (skip the field if it complicates — default: no email capture).
2. Every Pixel event gets an event_id (uuid); the same id is sent to capi-relay.
3. supabase/functions/capi-relay/index.ts: CORS allowlist = my github.io origin only; allowlist of event names; takes event_name, event_id, event_source_url, fbp/fbc cookies, client_user_agent from headers, client_ip_address from x-forwarded-for; sends to Meta CAPI with action_source 'website' and test_event_code when DEMO_MODE=true. Basic abuse guard: reject bodies > 2 KB, unknown events, wrong origin.
4. Secrets: META token/dataset/test code + DEMO_MODE via supabase secrets set. Deploy with --no-verify-jwt.
5. Verify: GA4 DebugView/Realtime shows events; Meta Test events shows browser AND server events with the same event_id marked deduplicated.
```

**CHECK:** Meta Test events shows both sources for QuizComplete, with dedupe; GA4 Realtime shows quiz_complete.

**Privacy:** the consent banner and a short privacy note on the page. Don't collect email by default.

---

## Phase 7 · Launch (YOU, ongoing ~1 hr)

**Prompt:** `P04 Phase 7. Write launch/LAUNCH.md: UTM-tagged links per channel (reddit, instagram, whatsapp, team-bhp, friends), 3 post drafts in my voice (casual, not salesy, rider-to-rider), posting rules to respect (read each community's self-promo rules first), and a week-1 metrics table to fill in (visits, starts, completion rate, shares).`

**YOU:**
- Post where allowed: r/IndianBikes, riding WhatsApp groups, your Instagram story, friends.
- Read each community's rules first. Some ban self-promo; ask the mods, or post it as "built this for fun, feedback welcome".

**CHECK after 7 days:** stats.html shows real completions. Screenshot it for the README.

---

## Phase 8 · README (20 min)
**Prompt:** `P04 Phase 8. README: why I built it, scoring design, dataset sourcing, tracking architecture (consent → GA4 + Pixel + CAPI with dedupe), privacy choices, launch results (numbers), what I'd do with an ad budget (lookalikes on QuizComplete, creative tests by segment). Update root README + hub card.`

## Demo vs Live
It's already live with real users. The only "live switch" is `DEMO_MODE=false` on capi-relay (drops test_event_code). Do it after you've seen dedupe working.

## Anomalies handled
| Risk | Handling |
|---|---|
| CAPI token can't be in a static site | Edge-function relay |
| Double counting browser + server | Shared event_id |
| Anyone can spam the relay | CORS allowlist, event allowlist, size limit |
| Public anon key reading responses | INSERT-only RLS; aggregates via a view |
| Wrong/old prices | source_url + checked_on + disclaimer |
| Copyrighted bike photos | No images |
| Community self-promo bans | Rules check in LAUNCH.md |
| Consent | Tags load after consent |

## DONE checklist
- [ ] Questions + dataset approved; validator green
- [ ] Scoring tests green
- [ ] UI live on Pages; mobile Lighthouse ≥ 90
- [ ] Supabase insert-only + stats view
- [ ] GA4 + Pixel + CAPI dedupe verified
- [ ] Launched; week-1 numbers in README

## Design highlights
- "Small product, full stack: consent, GA4, Pixel + CAPI with dedupe, UTM launch, and a public stats page."
- "Real users, zero spend — I treated distribution as part of the build."
