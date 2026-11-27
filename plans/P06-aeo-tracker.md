# P06 · AEO Visibility Tracker (how AI assistants talk about a category)

**Time:** ~4 hrs build + ~30 min/week to run · **Needs:** 00 done · **Cost:** ₹0

**One-liner:** "A weekly tracker of which brands AI assistants recommend for a category's buying questions: share of voice by engine and funnel stage, plus which sites they cite. It shows where to earn mentions and which pages to fix."

---

## How to start this chat
```
Read CLAUDE.md and plans/P06-aeo-tracker.md. Follow it phase by phase. Stop after each phase.
```

---

## Verified constraints → design

| Constraint | Design |
|---|---|
| Gemini free tier has no free Google Search grounding on newer models | No free API gives grounded answers → **manual-assisted runs** in the chat apps; the code does everything else |
| Paid APIs (Claude API web search, OpenAI, Perplexity) cost money | `auto` adapter written but off by default (DEMO) |
| Answers are personalised (memory, location, history) and vary run to run | Use temporary/incognito chats with memory off; record engine, date, logged-in state; treat results as snapshots and trend them |
| Pasting 80 answers a week is too slow | 12 prompts × 3 engines = 36 pastes ≈ 30 min |

---

## Config (brand-neutral; the category is swappable)

`p06-aeo-tracker/config.yaml`
```yaml
category: "email marketing software for small businesses"   # demo category; swap anytime
market: "India"
engines: [claude, chatgpt, gemini]          # perplexity optional
brands:
  - name: Mailchimp
    aliases: [mailchimp, intuit mailchimp]
    domains: [mailchimp.com]
  - name: Brevo
    aliases: [brevo, sendinblue]
    domains: [brevo.com]
  # ... 6–8 brands total; Claude proposes, you approve
prompts:                                     # 12, tagged by stage
  - id: p01
    stage: awareness
    text: "What is the best way for a small business to start email marketing?"
  - id: p05
    stage: consideration
    text: "Best email marketing tools for a small business in India"
  - id: p10
    stage: decision
    text: "Mailchimp vs Brevo for a 5-person business"
```

---

## Files

```
p06-aeo-tracker/
├── README.md
├── config.yaml
├── aeo/
│   ├── cli.py            # new-run | parse | load | report | auto
│   ├── parse.py          # mentions, first-mention rank, citations, recommendation flag
│   ├── adapters/auto.py  # optional paid-API runner (disabled in demo)
│   └── fixtures/         # 2 weeks of synthetic answers for the demo
├── runs/2026-W49/        # created per week: checklist.md + answers/<engine>/<prompt_id>.md
└── tests/test_parse.py
supabase/migrations/0004_aeo.sql
site/aeo/index.html       # dashboard (Chart.js), reads public views
```

---

## Phase 1 · Config + schema (45 min)

**Prompt:**
```
P06 Phase 1.
1. Propose 8 brands (with aliases + domains) and 12 prompts (4 per stage) for the config category; show for my approval, then write config.yaml.
2. 0004_aeo.sql:
   aeo_runs(id, week text, engine text, run_date date, logged_in boolean, memory_off boolean, notes text)
   aeo_answers(id, run_id fk, prompt_id, stage, answer_text text, char_len int, is_demo bool)
   aeo_mentions(id, answer_id fk, brand text, mentioned bool, first_rank int, recommended bool, sentiment text)
   aeo_citations(id, answer_id fk, url text, domain text)
   public views (anon SELECT): v_share_of_voice (week, engine, stage, brand, mention_rate, avg_first_rank), v_top_domains (week, domain, count). No answer text in public views.
   RLS: tables service-role only.
Show SQL for me to run.
```
**YOU:** approve brands/prompts; run the SQL.

---

## Phase 2 · Parser + tests (60 min)

**Prompt:**
```
P06 Phase 2. parse.py:
- Mentions: case-insensitive word-boundary match on aliases; first_rank = order of first appearance among brands in the answer.
- recommended: brand appears in a list item / sentence with recommend/best/top/go with/choose (simple rules; document them).
- Citations: extract URLs (markdown links + bare URLs), normalize to registrable domain.
- sentiment: neutral by default; positive/negative via small keyword lists (flag as heuristic).
tests/test_parse.py with tricky cases: alias inside another word ("brevo" in "brevoxyz" must not match), numbered lists, markdown links, same brand mentioned twice, no brands.
Generate fixtures: 2 weeks × 3 engines × 12 prompts of realistic synthetic answers (is_demo).
```
**CHECK:** tests green; parsing the fixtures prints a sensible share-of-voice table.

---

## Phase 3 · CLI run workflow (45 min)

**Prompt:**
```
P06 Phase 3. cli.py:
- new-run: creates runs/<ISO week>/checklist.md (each engine × prompt with a checkbox, exact prompt text to copy, run instructions) and empty answer stubs answers/<engine>/<prompt_id>.md with a header block (engine, date, logged_in, memory_off).
- parse + load: reads stubs, skips empty ones with a warning, loads to Supabase (idempotent: re-running a week replaces that week's rows).
- report: prints the week's share of voice and top cited domains, and writes runs/<week>/summary.md.
- load --demo: loads fixtures.
Run load --demo.
```

**Run instructions (Claude puts these in checklist.md):**
- **Claude:** new chat with memory/past-chat reference off, web search on. Paste the prompt. Copy the full answer including links.
- **ChatGPT:** temporary chat (memory off). Search on if available.
- **Gemini:** new chat; personalization off if available.
- Never edit the answers. One prompt per new chat.

---

## Phase 4 · Dashboard (45 min)

**Prompt:** `P06 Phase 4. site/aeo/index.html: Chart.js from CDN; reads v_share_of_voice and v_top_domains with the anon key; charts: share of voice by brand (stacked by engine), mention rate by stage, avg first rank, top cited domains, week selector; banner 'Demo data' when only demo weeks exist; methodology section (manual snapshots, personalization controls, limitations).`

**CHECK:** the dashboard renders the demo weeks on Pages. The anon key can't read `aeo_answers` (test it in the console).

---

## Phase 5 · First real run (YOU, 30–40 min) + weekly habit

1. `uv run aeo new-run` → open `checklist.md`.
2. Do the 36 pastes.
3. `uv run aeo parse && uv run aeo load && uv run aeo report`.
4. Read `summary.md`, then ask Claude: "Write 3 actions a brand in this category should take based on this week's gaps (pages to create, sites to get cited on)."

Do it weekly for 3–4 weeks so there's a trend line before you show it.

---

## Phase 6 · Optional auto adapter (30 min, off by default)

**Prompt:** `P06 Phase 6. adapters/auto.py: interface run(engine, prompt) → answer_text, citations. Implement a Claude API adapter using the web search tool, stubbed behind DEMO_MODE (never called when true; requires ANTHROPIC_API_KEY in a separate .env.auto that Claude Code never sources). Document cost per run estimate.`

Leave it off. It's there to show how it would automate with a budget.

---

## Phase 7 · README (20 min)
**Prompt:** `P06 Phase 7. README: what AEO is (plainly), method, controls for personalization/variance, metrics definitions, demo vs real weeks, findings from my real runs, how a brand would act on it (pages answering decision prompts, comparison pages, earning citations on the top domains), 'at scale' (API runs daily, more prompts, regional variants, alerting). Update root README + hub card.`

## Demo vs Live
- **Demo:** fixtures.
- **Live:** your weekly manual runs (already real data).
- **Client version:** swap category/brands/prompts in config.yaml, and optionally enable the auto adapter with their budget.

## Anomalies handled
| Risk | Handling |
|---|---|
| No free grounded API | Manual-assisted runs |
| Personalised answers | Memory off, temp chats, logged in/out recorded |
| Variance | Weekly snapshots + trend, not single answers |
| Alias false positives | Word-boundary match + tests |
| Leaking full answers publicly | Public views are aggregates only |
| Re-running a week duplicates data | Idempotent load per week |

## DONE checklist
- [ ] Config approved; schema run
- [ ] Parser tests green; demo loaded
- [ ] Dashboard live
- [ ] ≥1 real week loaded (aim for 3–4)
- [ ] README + hub card

## Design highlights
- "Search is splitting into answers. I measure how a category shows up there, by funnel stage, and which sites the engines trust."
- "I was explicit about the method's limits — personalisation and variance — and designed around them."
