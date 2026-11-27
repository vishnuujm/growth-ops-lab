# P08 · Ad Account Auditor (Google + Meta exports → findings → Claude-written audit)

**Time:** ~5 hrs · **Needs:** 00 done · **Cost:** ₹0

**One-liner:** "Drop in standard Google Ads and Meta exports. A rules engine finds the money leaks with evidence and ₹ impact, and a Claude Code skill writes the audit a client would actually read. It's tested against planted problems, so I know it catches them."

---

## How to start this chat
```
Read CLAUDE.md and plans/P08-ad-account-auditor.md. Follow it phase by phase. Stop after each phase.
```

---

## Ground rules
- **Never run this on client or employer data** without permission. Demo uses synthetic exports only. `input/real/` is gitignored.
- CSV exports (not the Google Ads API) are deliberate: no developer-token approval wait, and it works for any account the user can export from.
- Deterministic checks find the issues (with evidence + numbers). Claude only explains and prioritises; it doesn't invent findings.

---

## Real export quirks to handle (the hard part)

| Quirk | Handling |
|---|---|
| Google Ads CSVs often start with 1–2 title lines (report name, date range) before the header | Auto-detect the header row by known column names |
| Total rows at the bottom ("Total: Account", "Total: Search", "Total: Campaign") | Drop rows whose first cell starts with "Total" |
| Numbers as text: "1,234", "₹1,234.56", "--", " --", "< 10%", "12.5%" | One `to_number()` with tests |
| Column names vary by language, the columns chosen and the export UI version | `column_map.yaml` with aliases per canonical field; fail with a clear "missing column X" message |
| Meta exports: "Amount spent (INR)", "Results" + "Result indicator", "Reporting starts/ends" and optional "Day" breakdown | Map; require a Day breakdown for the fatigue checks, else skip them with a note |
| Encodings (UTF-8 with BOM, UTF-16 from Excel "Unicode text") | Try utf-8-sig → utf-16 → latin-1 |

---

## Files

```
p08-ad-account-auditor/
├── README.md
├── column_map.yaml
├── rules.yaml                 # thresholds (editable per account)
├── auditor/
│   ├── load.py                # robust CSV loader + normalizer
│   ├── checks_google.py
│   ├── checks_meta.py
│   ├── findings.py            # Finding model: id, severity, title, evidence rows, impact_inr, fix
│   └── run.py                 # CLI: run --google <dir> --meta <dir> --out out/
├── synth/make_exports.py      # synthetic exports WITH planted issues + answer_key.json
├── tests/
│   ├── test_load.py           # quirks table above
│   └── test_planted.py        # every planted issue is found
└── out/                       # findings.json + report.md/.html (gitignored)
.claude/skills/ad-audit/SKILL.md   # Claude Code skill that writes the report
```

---

## Phase 1 · Synthetic exports with planted issues (60 min)

**Prompt:**
```
P08 Phase 1. synth/make_exports.py (seeded) writes realistic exports in input/demo/:
Google: search_terms.csv (Search term, Match type, Added/Excluded, Campaign, Ad group, Keyword, Clicks, Impr., CTR, Avg. CPC, Cost, Conversions, Cost / conv., Conv. rate), keywords.csv (incl. Quality Score + Search lost IS (rank)), campaigns.csv (incl. Search lost IS (budget), Budget). Include the 2 title lines + Total rows + "--" values, like real exports.
Meta: ads_daily.csv (Day, Campaign name, Ad set name, Ad name, Amount spent (INR), Impressions, Reach, Frequency, Link clicks, CTR (link click-through rate), Results, Result indicator, Cost per result).
Plant these and record them in answer_key.json:
G1 search terms with spend > 2× target CPA and 0 conversions (incl. 'free', 'jobs', 'salary', 'course pdf')
G2 broad-match keyword matching many unrelated terms (leakage)
G3 keywords with QS ≤ 4 and high spend
G4 a converting campaign losing > 30% IS to budget
G5 a campaign with CPA > 2× account average
M1 ad set with 7-day frequency > 4 and CTR down > 30% vs its first week (fatigue)
M2 ad set spent > 3× target CPA with 0 results
M3 > 10 ad sets each with < 10 results/week (fragmentation / learning-limited proxy)
M4 one ad taking > 80% of an ad set's spend with worse CPA than siblings
```

**CHECK:** the files open in Excel or Numbers and look like real exports; answer_key.json lists 9 issues.

---

## Phase 2 · Robust loader (60 min)

**Prompt:** `P08 Phase 2. load.py + column_map.yaml + tests/test_load.py covering every quirk in the plan's table (title lines, Total rows, '--', currency symbols, %, '< 10%', BOM, UTF-16). Output tidy DataFrames with canonical snake_case columns and dtypes.`

**CHECK:** tests green, and loading `input/demo` prints the row counts.

---

## Phase 3 · Checks engine (75 min)

**Prompt:**
```
P08 Phase 3. rules.yaml thresholds (target_cpa default = account CPA, overridable).
checks_google.py: G1–G5 + negative keyword candidate list (n-gram analysis of wasted terms: 1–2 word grams with spend and 0 conv).
checks_meta.py: M1–M4 (skip M1 with a note if no Day column).
Each finding: id, severity (high/med/low by ₹ impact), title, evidence (top rows), impact_inr (estimated monthly waste or opportunity — show the formula), fix (concrete action).
run.py writes out/findings.json + a plain findings table.
tests/test_planted.py: every answer_key issue is found; no high-severity false positive on a clean synthetic account (generate one with --clean).
```

**CHECK:** all 9 planted issues are found; the clean account gives 0 high-severity findings.

---

## Phase 4 · Claude Code skill: write the audit (45 min)

**Prompt:**
```
P08 Phase 4. Create .claude/skills/ad-audit/SKILL.md (frontmatter: name ad-audit, description 'Write a client-ready ad account audit from out/findings.json').
Instructions in the skill:
- Read out/findings.json and rules.yaml; never add findings that aren't in the JSON; every ₹ number must come from the JSON.
- Classify the top 50 wasted search terms by intent (irrelevant / research / competitor / relevant-but-expensive) and propose negatives with match type.
- Output out/report.md: exec summary (3 bullets, total ₹ at stake), top 5 fixes ranked by impact × ease, details per finding with evidence table, negative keyword list, 30-day action plan, assumptions & data limits.
- Then convert to out/report.html with simple print-friendly CSS.
Test it: run the skill on the demo findings and show me the report.
```

**CHECK:** the report reads like something you'd send a client, and every number traces back to findings.json (spot-check 3).

---

## Phase 5 · README + sample report on Pages (30 min)

**Prompt:** `P08 Phase 5. Copy the demo report.html to site/auditor/sample-report.html (synthetic, labelled). README: why CSV-first, quirks handled, checks list with formulas, planted-issue test approach, skill design (facts from code, words from Claude), demo vs live, 'at scale' (Google Ads API + Meta Insights scheduled pulls into BigQuery from P03, weekly alerting to Slack). Update root README + hub card.`

## Demo vs Live
- **Demo:** synthetic exports.
- **Live:** export the same reports from any account you're allowed to audit → `input/real/<account>/` → `uv run auditor/run.py` → run the skill. Tune `rules.yaml` (target CPA, thresholds).

## Anomalies handled
| Risk | Handling |
|---|---|
| Messy real exports | Loader + tests per quirk |
| AI inventing numbers | Findings computed in code; skill forbidden to add findings |
| False positives | Clean-account test |
| Client data leakage | input/real gitignored; never committed |
| No API access | CSV-first by design |

## DONE checklist
- [ ] Synthetic exports + answer key
- [ ] Loader tests green
- [ ] 9/9 planted issues found; clean account clean
- [ ] Skill writes report; numbers trace back
- [ ] Sample report on Pages; README + hub card

## Design highlights
- "This is my day job turned into a tool: the checks I do by hand across 25+ accounts, made repeatable and tested."
- "Code finds the facts, Claude explains them. That split is what makes AI output trustworthy."
