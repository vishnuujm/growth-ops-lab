# P07 · Creative Pattern Lab (competitor ads → tagged patterns → briefs)

**Time:** ~4–5 hrs · **Needs:** 00 done · **Cost:** ₹0

**One-liner:** "I pull a category's live ads from the Meta Ad Library, have Claude tag every creative against a fixed taxonomy, use how long each ad has run as a proxy for what's working, and turn the patterns into creative briefs."

---

## How to start this chat
```
Read CLAUDE.md and plans/P07-creative-pattern-lab.md. Follow it phase by phase. Stop after each phase.
```

---

## Verified constraint → design
- **The Ad Library API doesn't return commercial ads delivered in India/US** (it covers EU/UK-delivered ads and political/issue ads). So you capture by hand from the **Ad Library website**, which shows all active ads.
- Claude Code reads the screenshots (image input). Tagging ~10 images per session keeps your Pro usage in check.
- **Copyright/brand safety:** raw screenshots stay **local** (gitignored). The public repo and page show only tags, counts and your own written descriptions. No creatives are republished.
- **Performance data:** competitors' ad performance isn't public. "Days running" is the proxy (ads kept live 30+ days are more likely to be working). Demo mode adds a clearly labelled **synthetic** performance table to show how real CTR/CPA would plug in.

---

## Files

```
p07-creative-pattern-lab/
├── README.md
├── taxonomy.yaml
├── data/
│   ├── raw/                    # screenshots (gitignored)
│   ├── capture.csv             # one row per ad (you + Claude fill)
│   └── tags.jsonl              # Claude's tags
├── analysis/
│   ├── analyze.py              # frequencies, longevity lift, co-occurrence
│   ├── synth_performance.py    # demo-only
│   └── report.md               # generated
├── briefs/briefs.md            # 5 creative briefs
└── tests/test_analyze.py
site/creative-lab/index.html    # tag charts, no images
```

---

## Phase 1 · Choose a category + taxonomy (30 min)

**YOU:** pick a category you know and that has lots of active Meta ads in India: e.g. D2C skincare, protein/nutrition, or online upskilling courses. Pick 6–8 advertisers. Brand names are fine in your private notes; the public report can anonymise them as Brand A–H if you prefer.

**Prompt:**
```
P07 Phase 1. Write taxonomy.yaml (closed vocabularies so tags are comparable):
hook_type [problem, outcome, social_proof, offer, curiosity, demo, founder, ugc_testimonial, comparison, authority, trend/meme],
format [static, carousel, video, collection], aspect [1:1, 4:5, 9:16, 16:9],
offer [none, discount_pct, bogo, free_shipping, free_trial, bundle, limited_time],
proof [none, ratings, reviews_quote, numbers, certifications, press, before_after],
visual_style [product_only, lifestyle, text_heavy, ugc_selfie, studio_model, illustration, before_after],
text_density [low, medium, high], language [english, hindi, hinglish, regional],
cta [shop_now, learn_more, sign_up, order_now, get_offer, other],
emotion [aspiration, fear/avoidance, convenience, value, belonging, curiosity],
plus primary_message (≤15 words, my own paraphrase).
Also capture.csv header: ad_id, advertiser, file, started_running_on, platforms, format_seen, landing_domain, notes.
```

---

## Phase 2 · Capture (YOU, 60–75 min)

1. Open the Meta **Ad Library** website → Country: India → Ad category: All ads → search each advertiser → filter **Active**.
2. For each advertiser, take screenshots of **4–6 ads**, ~30–40 total. Capture the whole card, including "Started running on …".
   - **Videos:** screenshot the thumbnail + caption. Optionally note the first 3 seconds' hook in `notes`.
3. Save them as `data/raw/<advertiser>_<n>.png`.
4. Fill `capture.csv` (advertiser, file, started_running_on, landing domain). Or let Claude read the date off the screenshot in Phase 3 and you verify it.

---

## Phase 3 · Tagging with Claude vision (60 min across 3–4 sessions)

**Prompt (repeat per batch of 10):**
```
P07 Phase 3, batch <n>. Read the next 10 images in data/raw not yet in tags.jsonl. For each: read 'Started running on' (fill capture.csv if empty), then tag strictly with taxonomy.yaml vocabularies; add confidence 0–1 per field; write primary_message as your own paraphrase (no copying ad text beyond 5 words). Append to tags.jsonl. Then show a table of the 10 rows for my review.
```

**YOU:** review every row in the first batch closely, then spot-check ~20% of later batches. Fix tags in place. Note the agreement rate in the README ("I agreed with X% of tags on review").

**CHECK:** every image has one tags row; every value is inside the vocabulary (a validator script, below).

---

## Phase 4 · Analysis (60 min)

**Prompt:**
```
P07 Phase 4.
1. A validator: all tags within taxonomy; dates parse; no missing files.
2. analyze.py:
   - days_running = today − started_running_on; long_runner = days_running ≥ 30.
   - Frequency of each tag value overall and by advertiser.
   - Longevity lift: share among long runners ÷ share among all (with counts; flag n < 5 as 'low confidence').
   - Co-occurrence of hook_type × format and offer × proof (top pairs).
   - Whitespace: tag values nobody uses.
3. synth_performance.py (DEMO only): adds ctr/cpa per ad with a plausible relationship to tags; every output that uses it is labelled 'SYNTHETIC'.
4. tests/test_analyze.py for lift math and low-n flagging.
5. Write analysis/report.md: top 5 patterns, what long-runners share, whitespace, caveats (proxy ≠ performance, small n, snapshot date).
```
**CHECK:** tests green; report numbers match a quick manual count on one tag.

---

## Phase 5 · Briefs + page (45 min)

**Prompt:** `P07 Phase 5. Write briefs/briefs.md: 5 creative briefs for a NEW brand in this category, each with: hypothesis (which pattern/lift it tests), hook line options (3), format/aspect, proof element, offer, visual direction, success metric for a test, and what result would kill it. Then site/creative-lab/index.html: charts of tag frequencies, longevity lift (with low-n flags), co-occurrence heatmap, whitespace list, methodology — no images.`

---

## Phase 6 · README (20 min)
**Prompt:** `P07 Phase 6. README: why (creative is the biggest lever on Meta now), method, taxonomy, the Ad Library API limitation and the manual workaround, longevity proxy and its limits, my tag-agreement rate, findings, briefs, demo vs live, 'at scale' (pull own-account performance via Meta Insights API by ad id, auto-tag new ads weekly, test pipeline). Update root README + hub card.`

## Demo vs Live
- **Demo:** real competitor tags + synthetic performance overlay.
- **Live:** join the tags to an account's own ad-level results (Meta Insights API or Ads Manager export) on ad_id, and replace the synthetic table.

## Anomalies handled
| Risk | Handling |
|---|---|
| No Ad Library API for India commercial ads | Manual capture from the website |
| Copyright | Screenshots local only; paraphrased messages; no images published |
| Tag drift | Closed vocabularies + validator + human review |
| Over-reading longevity | Labelled as a proxy; low-n flags |
| Pro usage limits on images | 10 per batch, across sessions |

## DONE checklist
- [ ] Taxonomy + capture.csv
- [ ] 30–40 ads captured and tagged; validator green
- [ ] Analysis tests green; report written
- [ ] 5 briefs; page live (no images)
- [ ] README + hub card

## Design highlights
- "Tagging turns 'I scrolled competitors' into data: which hooks and proofs the long-running ads share, and the gaps nobody's using."
- "I said clearly that run length is a proxy, and showed how real performance data plugs in."
