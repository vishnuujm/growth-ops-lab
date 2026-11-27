# P09 · PlanFair: finish, instrument, launch

**Time:** ~5–6 hrs (depends on current state) · **Needs:** existing PlanFair repo + Supabase + Vercel · **Cost:** ₹0

**What it is:** group trip budget agreement *before* booking. Each friend privately sets their max; the group sees an agreed range without anyone's number being exposed.

**One-liner:** "A consumer product with a built-in growth loop: every trip creator invites friends, so I measure activation and the viral coefficient, not just signups."

---

## How to start this chat
Open Claude Code **in the PlanFair repo folder** (not growth-ops-lab). Copy this file into it as `plans/P09-planfair.md`.
```
Read plans/P09-planfair.md. Start with Phase 0 (audit) and do not change any code until I approve the audit's plan.
```

---

## Phase 0 · Audit what exists (30 min, read-only)

**Prompt:**
```
P09 Phase 0. Read-only audit. Report:
1. Stack (framework, Supabase usage, auth, hosting/Vercel config), how to run locally, env vars needed (names only).
2. What works end-to-end today vs half-built vs missing, against the MVP list in this plan.
3. Database tables + RLS policies (paste them). Flag any table where one member could read another member's budget.
4. Deploy status: is there a live Vercel URL? Does it build?
5. Analytics present? (GA4/Pixel/anything)
6. Risks (secrets in repo, missing RLS, no tests).
Then propose a phase plan using this file's phases, adjusted to what's already done. Wait for my approval.
```

**CHECK:** you read the audit and approve or adjust it.

---

## MVP definition (done = all true)

1. Create a trip (name, dates optional, destination optional) → get a share link.
2. A friend opens the link → joins with name (+ optional magic-link login or anonymous token).
3. Each member enters a **private** max budget per person (and optional comfort level).
4. Once ≥ 2 members have submitted, everyone sees the **agreed range**: the max everyone can afford (= min of maxes), shown as a band (e.g. "₹8–10k per person"). Optionally the median, without revealing any individual's number.
5. A suggested hotel/stay price band per night, derived from the agreed budget (simple rule, documented).
6. Shareable result card (WhatsApp share).
7. Works on mobile.

---

## Phase 1 · Privacy-correct data model (60 min)

This is the one thing that must be right. A budget app that leaks your friend's budget is dead.

**Prompt:**
```
P09 Phase 1 (adjust to existing schema).
- members can read trips they belong to; members can INSERT/UPDATE only their own budget row; NO member can SELECT other members' budget rows.
- A SECURITY DEFINER function get_trip_summary(trip_id) returns only: member_count, submitted_count, agreed_max (min of maxes), band_low/band_high (rounded to nearest ₹500 so a 2-person trip doesn't reveal the other's exact number), median (only if ≥ 4 submissions).
- Check the caller is a member inside the function.
- Write SQL tests (or a script) proving: member A cannot read member B's row via the REST API with A's token; summary works; non-members get nothing.
```

**CHECK:** the leak test fails to read others' budgets (that's the pass); the summary returns rounded bands.

**Privacy edge case:** in a 2-person trip, "min of maxes" can reveal that the other person's number is lower. Mitigate with rounding to bands, plus copy that says "the group's comfortable range". Document it in the README as a deliberate trade-off.

---

## Phase 2 · Finish the MVP flows (2–3 hrs, per the audit)

**Prompt:** `P09 Phase 2. Implement the missing MVP items from the audit one at a time; after each, run it locally and show me. Keep UI simple and mobile-first. Add basic tests for the summary rounding and the stay-band rule.`

**Stay-band rule (simple, documented):** nightly stay budget = agreed per-person budget × 35–45% ÷ nights × people per room. Show it as a range with "rule of thumb" copy.

---

## Phase 3 · Instrumentation + growth loop metrics (60 min)

**YOU:** create a GA4 property "PlanFair" (free) and give Claude the Measurement ID.

**Prompt:**
```
P09 Phase 3. Add GA4 with consent banner. Events (with trip_id hashed, never names/budgets):
trip_created, invite_link_copied, invite_shared (channel), invite_opened, member_joined, budget_submitted, summary_viewed, result_shared.
Supabase metrics view (service-role only) + a small /admin page behind my login or a script:
- activation = trips with ≥ 2 budgets submitted within 48h / trips created
- invites per trip, join rate = members joined / invite opens
- K-factor ≈ (avg invites per creator) × (join rate) × (share of joiners who create their own trip)
UTMs on all launch links.
```

**CHECK:** one full test trip with 3 browsers/profiles → all events appear in GA4 Realtime; the metrics view shows activation for that trip.

---

## Phase 4 · Deploy + launch (YOU + Claude, 60 min)

**Vercel Hobby is for non-commercial use.** A free personal project is fine; don't add payments or ads.

**Prompt:** `P09 Phase 4. Make sure the Vercel production build passes; env vars set in Vercel (names only listed for me to paste values); add OG image + meta tags so WhatsApp previews look good; add a 404 and an error page. Write launch/LAUNCH.md with UTM links and 3 post drafts in my voice for: friends' trip WhatsApp groups, r/IndiaTravel or r/solotravel-style communities (check rules), Instagram story, LinkedIn build-in-public post.`

**Keep Supabase awake:** this project uses your first free Supabase slot. Add the same keepalive GitHub Action as growth-ops-lab (ping every 3 days).

**YOU:** use it for a real trip with friends first. One real group trip is your best story.

---

## Phase 5 · README + portfolio card (30 min)

**Prompt:** `P09 Phase 5. README: problem (money awkwardness kills group trips), how privacy works (RLS + summary function + rounding trade-off), the growth loop and metrics definitions, launch results (fill real numbers), what I'd do next (trip templates, booking deep links, reminders). Then give me a 3-line project card + link to add to growth-ops-lab's README and site/index.html.`

**YOU:** add the card to growth-ops-lab (one small commit there) and to the Webflow Home page.

## Anomalies handled
| Risk | Handling |
|---|---|
| Budget leakage between friends | RLS + security-definer summary + rounding + leak test |
| 2-person inference | Banded output + documented trade-off |
| PII in analytics | Hashed trip id only; no names/budgets in events |
| Supabase pause | Keepalive action |
| Vercel Hobby terms | Non-commercial; no payments/ads |
| Changing working code blindly | Phase 0 read-only audit + approval |

## DONE checklist
- [ ] Audit approved
- [ ] Privacy tests prove no leaks
- [ ] MVP 1–7 working on mobile
- [ ] GA4 events + activation/K-factor metrics
- [ ] Live on Vercel with good share previews; keepalive on
- [ ] Used for one real trip; launched with UTMs
- [ ] README + card in growth-ops-lab

## Design highlights
- "Consumer problem, privacy-first design, and the growth loop is the product: every creator brings 3–6 people."
- "I measure activation and K-factor rather than signups, because that's what tells you whether it spreads."
