# Growth Ops Lab

A personal portfolio of growth and marketing-ops systems, built on free tiers: lead routing, monitoring alerts, conversion feedback loops, funnel analytics, quizzes, calculators and audits. Brand-neutral, and adaptable to any kind of organisation.

Everything runs in **demo mode** by default: synthetic or public data only, test events only, and nothing touches a real ad account.

**Live site:** https://vishnuujm.github.io/growth-ops-lab/

## Projects

| # | Project | What it does | Status |
|---|---|---|---|
| 00 | Foundation | Repo, accounts, keys, shared code | In progress |
| P01 | Lead Router | Scores and routes inbound leads to CRM + Slack | Planned |
| P02 | Feedback Loop | Sends qualified leads back to Meta CAPI + Google | Planned |
| P03 | Funnel Command Center | BigQuery + GA4 sample + Looker Studio | Planned |
| P04 | Bike Quiz | "Which bike should I buy?" quiz | Planned |
| P05 | Lead-Gen Calculator | Paid-ads budget & break-even calculator | Planned |
| P06 | AEO Tracker | AI-answer visibility tracker | Planned |
| P07 | Creative Pattern Lab | Competitor creative tagging with vision AI | Planned |
| P08 | Ad Account Auditor | CSV-based Google/Meta account audit | Planned |
| P09 | PlanFair | Finish, instrument and launch PlanFair | Planned |
| P10 | Organic Drop Monitor | Daily Slack alert when organic traffic or leads fall | Planned |

## Layout

- `common/`: shared Python helpers (config, Supabase, Slack, HubSpot, hashing, logging)
- `supabase/`: database migrations and edge functions
- `site/`: GitHub Pages site, one subfolder per project
- `scripts/`: setup and connectivity checks
- `plans/`: the build plan for each project

## Running locally

```bash
cp .env.example .env   # then fill in values
uv run pytest
```
