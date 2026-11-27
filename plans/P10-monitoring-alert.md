# P10 · Organic Drop Monitor (daily GitHub Action → Slack alert)

**Time:** ~2–3 hrs · **Needs:** F0–F3 and the F10 slice (Actions secrets) · **Uses Make slot:** none · **Cost:** ₹0

**One-liner:** "Every morning a job compares last week's organic traffic and leads with the four weeks before. On a drop of 25% or more it posts to Slack with the pages and sources that lost the most and what to check. It reports what changed, not why."

---

## How to start this chat
New Claude Code session in `~/growth-ops-lab`, first message:
```
Read CLAUDE.md and plans/P10-monitoring-alert.md. Follow it phase by phase.
After each phase run the CHECK steps, show proof, commit, and wait for me.
Anything marked YOU is mine in the browser — give me exact clicks.
```

---

## Architecture

```
GitHub Actions, daily 03:30 UTC (09:00 IST) + manual run
        │
        ▼
data source ── demo: synthetic generator (default)
        │   └─ later: GA4 Data API (off by default)
        ▼
detector (pure functions, tested)
        ├─ data missing        → Slack "data problem"
        ├─ baseline too small  → log only
        ├─ drop < 25%          → log only
        └─ drop ≥ 25%          → cooldown check → Slack alert
        ▼
Supabase events_log (project 'p10')

Any crash → Slack "monitor failed"
```

---

## Detection rules (single source of truth, tested)

| Rule | Value (in `config.yaml`) |
|---|---|
| Metrics | `sessions` and `leads`, organic only, each judged on its own |
| Current window | 7 complete days ending 3 days before the run date (the latest 2 days are skipped) |
| Baseline | The 28 days before the current window, divided by 4 (average week) |
| Drop | `(baseline - current) / baseline` |
| Alert when | drop ≥ 0.25 (exactly 25% alerts) |
| Too little data | baseline < 200 sessions/week, or < 20 leads/week → no alert |
| Missing data | any date absent in either window → "data problem" alert, no drop verdict |
| Zero vs missing | a date with a real 0 is data; an absent date is missing |
| Affected pages and sources | top 5 of each by absolute loss; only items that lost volume |
| Cooldown | no repeat for the same metric for 3 days, unless the drop worsens by 10 points or more |

Whole weeks on both sides keep weekday patterns from causing false alarms.

---

## Alert wording

```
[DEMO] ⚠️ Organic sessions down 31% (last 7 days vs previous 4-week average)
Window: 18 Nov – 24 Nov · 690 vs 1,000 per week
Pages that lost the most: /pricing −140 · /blog/guide −90
Sources that lost the most: google −260 · bing −30
To investigate: analytics tag and consent changes · forms and thank-you page ·
recent site releases, redirects and noindex · Search Console coverage and queries ·
holidays or campaign changes in the same window
Cause not determined.
```

The alert never names a cause. A test fails if the message contains "algorithm", "caused by" or "due to".

---

## Files this project creates

```
p10-monitoring-alert/
├── README.md
├── config.yaml                 # thresholds, windows, cooldown
├── synthetic.py                # seeded daily data: date, page, source, sessions, leads
├── detect.py                   # pure functions, no network
├── message.py                  # builds Slack text/blocks
├── monitor.py                  # CLI: --scenario, --as-of, --dry-run
└── ga4_source.py               # later
tests/test_p10_detect.py
tests/test_p10_message.py
.github/workflows/p10-monitor.yml
```

---

## Phase 1 · Synthetic data (30 min)

**Prompt:**
```
P10 Phase 1. Write synthetic.py: seeded, deterministic daily rows (date, page, source, sessions, leads) for at least 35 days up to the run date, with a weekday pattern and a little noise, using generic pages and sources.
Scenarios: normal, drop (two pages and one source lose enough that the total falls more than 25%), missing_days, low_volume.
Add tests: same seed + date → identical rows; each scenario has the property it claims.
```

**CHECK:** pytest green; print weekly totals per scenario as a table.

---

## Phase 2 · Detection (45 min)

**Prompt:**
```
P10 Phase 2. Write config.yaml and detect.py implementing "Detection rules".
Tests: 24.9% drop quiet; 25.0% alerts; growth quiet; zero baseline does not divide by zero; low volume quiet; missing date gives data_problem; real zeros are not "missing"; the latest 2 days are ignored; ranking by absolute loss; cooldown suppresses a repeat and allows a worse drop.
```

**CHECK:** pytest green; `--dry-run` for each scenario prints the expected verdict.

---

## Phase 3 · Slack alert (30 min)

**Prompt:**
```
P10 Phase 3. Write message.py and monitor.py using common/slack.py and common/log.py.
Prefix [DEMO] when DEMO_MODE. Every events_log payload carries is_demo and scenario. Read the last alert from events_log for the cooldown (GitHub runners keep no files).
If events_log cannot be read, send the alert anyway and say the repeat check was skipped.
Add the wording test (banned phrases).
```

**CHECK:** drop scenario posts one alert in Slack; running it again is suppressed by the cooldown; normal posts nothing.

---

## Phase 4 · Daily GitHub Action (30 min)

**Prompt:**
```
P10 Phase 4. Write .github/workflows/p10-monitor.yml: cron '30 3 * * *', workflow_dispatch with inputs scenario (default normal) and dry_run. Secrets: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SLACK_WEBHOOK_URL. DEMO_MODE=true.
Add an "if: failure()" step that posts "P10 monitor failed" with the run link to Slack.
Logs are public: never print secrets. Trigger normal and drop with gh and show both results.
```

**CHECK:** both runs green; drop alerts, normal stays quiet. One forced failure posts "monitor failed".

---

## Phase 5 · Real GA4 source (later)

- GA4 Data API with a read-only service account; key stored as a GitHub secret, entered through `scripts/set_env.py` locally.
- Dimensions `date`, `landingPage`, `sessionSource`; filter `sessionDefaultChannelGroup = Organic Search`; metrics `sessions`, `keyEvents` (as leads).
- Dates follow the GA4 property's time zone. Sampled or thresholded responses are reported in the alert.
- Selected by `P10_SOURCE=ga4`; refused while `DEMO_MODE=true`.

---

## Phase 6 · README (20 min)

**Prompt:** `P10 Phase 6. Write README.md: problem, mermaid diagram, detection rules, a sample alert, demo vs live, failure modes, limits, what I'd change at scale (seasonality model, per-page thresholds, deploy annotations, paging). Add a row to the root README and a card on site/index.html.`

**CHECK:** readable in 2 minutes.

---

## Demo vs Live

| | Demo | Live |
|---|---|---|
| Data | Synthetic | GA4 Data API |
| Scenario | Chosen at run time; scheduled runs use `normal` | Not applicable |
| Slack | Your workspace, `[DEMO]` prefix | Team channel |
| Flag | DEMO_MODE=true | DEMO_MODE=false |

---

## Failure modes

| Risk | Handled by |
|---|---|
| Small numbers swing wildly | Minimum weekly baseline |
| Recent days incomplete | Latest 2 days skipped |
| Missing data looks like a drop | "Data problem" alert instead |
| Same drop alerts daily | Cooldown |
| A long drop becomes the new baseline and alerts stop | Documented limit; at scale compare with a longer or year-ago baseline |
| One page falls but the total does not | Not detected (totals only); per-page thresholds at scale |
| Holiday or campaign end | Listed under "to investigate"; no cause claimed |
| Job crashes | "Monitor failed" Slack step |
| Slack itself is down | Run fails red in GitHub Actions |
| GitHub delays or skips a scheduled run | Manual run available; no guaranteed run time |
| GitHub disables schedules after 60 idle days | Monthly heartbeat (later part of F10) |
| Supabase unreachable | Alert still sent, repeat check skipped |

## Troubleshooting
- **No alert on the drop scenario:** check for a cooldown entry in `events_log`; use `--dry-run` to see the verdict.
- **Action fails with "Missing setting(s)":** that GitHub secret is not set; rerun the secrets step from F10.
- **Scheduled run not showing:** schedules run only from the default branch and can be late.

## DONE checklist
- [ ] Tests green, including 25% boundary and wording test
- [ ] Drop alerts in Slack; normal is quiet
- [ ] Daily Action green; manual run works
- [ ] Failure step proven
- [ ] README + hub card

## Design highlights
- "It separates 'traffic fell' from 'data is missing', because those need different people."
- "It lists where the loss is and what to check. It doesn't guess the cause."
- "Whole-week comparisons, a minimum volume and a cooldown keep it from being ignored."
