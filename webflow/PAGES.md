# F9 · Portfolio site: copy and settings

Single source for both pages. Open to any kind of organisation: no company, vendor or industry targeting. Demo project: no customers, quotes, logos or results are claimed.

## Page settings

| Page | Slug | SEO title | Meta description |
|---|---|---|---|
| Home | `/` | Growth Ops Lab: Marketing Operations Portfolio | A portfolio of marketing and growth operations projects: lead routing, monitoring alerts, reporting and more, built on free tools. |
| Contact | `contact` | Contact · Growth Ops Lab | Tell us what you want to improve in lead capture, routing, tracking or reporting. A demo form for the Growth Ops Lab portfolio. |

---

## Home

### Hero
**H1:** Growth Ops Lab
**Subhead:** A portfolio of systems for capturing leads, routing them, measuring results and spotting problems early.
**Button:** Get in touch → `/contact`

### Projects
**H2:** Projects
**Note:** Statuses are updated as each project ships.

| Title | Text | Status |
|---|---|---|
| Lead router | Scores each form submission, adds it to a CRM and alerts the team. | In progress |
| Organic drop monitor | Compares recent traffic and leads with earlier weeks and sends an alert on a large fall. | Planned |
| Conversion feedback loop | Sends qualified outcomes from the CRM back to ad platforms. | Planned |
| Funnel dashboard | Joins spend and site behaviour in one report. | Planned |
| Product-finder quiz | Asks a few questions and recommends a match. | Planned |
| Budget calculator | Estimates what a lead can cost and what budget a target needs. | Planned |
| AI visibility tracker | Records which brands AI assistants recommend in a category. | Planned |
| Creative pattern lab | Tags public ads and turns the patterns into briefs. | Planned |
| Ad account auditor | Checks exported ad data for wasted spend. | Planned |
| PlanFair | Helps a group agree a budget without exposing anyone's number. | Planned |

**Footer (both pages):** Demo project. Not a commercial service.

---

## Contact

### Hero
**Eyebrow:** Contact
**H1:** Tell us what you want to improve
**Subhead:** For any team that collects enquiries and wants to follow them up, measure them and notice when something breaks.
**Button:** Go to the form → `#demo`

### Benefits
**H2:** What these systems are designed to do

| Title | Text |
|---|---|
| Capture every enquiry | A form sends each submission straight into an automated flow. |
| Prioritise follow-up | Submissions are scored against rules you can read and change. |
| Keep records tidy | Duplicates are merged and missing records are checked. |
| Notice problems early | Alerts point to what changed and what to check. |

### FAQ
**H2:** Common questions

**Who is this for?**
Any organisation that collects enquiries, whatever its size or industry. The scoring rules and tools can be swapped.

**Is this a live service?**
No. It is a portfolio demo.

**Which tools does it use?**
Webflow, Make, Supabase, HubSpot and Slack on free or test plans, with scripts written in Python.

**What happens to what I type?**
It is sent to demo tools for testing, so please do not enter real personal data.

### Form (section id `demo`)
**H2:** Send a message
**Note under the heading:** Demo project. Please do not enter real personal data.

| Field name (exact) | Label | Type | Required | Options (value = label) |
|---|---|---|---|---|
| `email` | Work email | Email | yes | |
| `first_name` | First name | Text | no | |
| `company` | Organisation | Text | no | |
| `role` | Your role | Text | no | |
| `company_size` | Organisation size | Select | no | `1-10`, `11-50`, `51-200`, `201-1000`, `1000+` |
| `use_case` | What do you want help with? | Textarea | no | |
| `timeline` | When do you want to start? | Select | no | value `now` "Now" · `1-3m` "In 1–3 months" · `3-6m` "In 3–6 months" · `exploring` "Just exploring" |

Selects start with an empty "Choose one" option.

**Submit button:** Send message

**Form settings (set by hand in the Designer):** Send to = Custom action · Method = POST · Action = `MAKE_WEBHOOK_LEADS_URL` from `.env`. Never commit it or paste it into a chat.

Until P01 is connected, a submission shows Make's plain "Accepted" reply.
