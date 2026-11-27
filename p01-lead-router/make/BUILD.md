# Make Scenario A: "P01 Lead Router"

What it does: receive the form → score it → save to HubSpot → reply to the visitor → alert Slack for grade A.

Never write real addresses or passwords into this file. `<...>` marks a value you paste into Make only.

```
1 Webhook ─► 2 HTTP: score ─► 3 HubSpot: save contact ─► 4 Webhook response ─► 5 Router ─(grade A)─► 6 HTTP: Slack
```

## 1 · Webhooks → Custom webhook
Already created (`lead-intake`).

## 2 · HTTP → Make a request (score the enquiry)

| Setting | Value |
|---|---|
| URL | `https://<project-ref>.supabase.co/functions/v1/score-lead` |
| Method | POST |
| Header name | `x-intake-secret` |
| Header value | `<INTAKE_SECRET>` |
| Body type | `application/x-www-form-urlencoded` |
| Parse response | Yes |

Body fields (name on the left, the matching webhook item on the right):
`email`, `first_name`, `last_name`, `company`, `company_size`, `role`, `use_case`, `timeline`, `source`,
`utm_source`, `utm_medium`, `utm_campaign`, `gclid`, `fbclid`, `page_url`, `is_demo`.

Form-style fields are used instead of hand-written JSON, so quotes or line breaks in a message cannot break the request.

## 3 · HubSpot CRM → Create/Update a Contact
Connect with the **developer test account** only.

| HubSpot field | Value |
|---|---|
| Email | `email` from step 2 |
| First name | `first_name` from step 1 |
| Last name | `last_name` from step 1 |
| Company name | `company` from step 1 |
| Job title | `role` from step 1 |
| Lead score | `score` from step 2 |
| Lead tier | `tier` from step 2 |
| Lead reason | `reason` from step 2 |
| Lead source detail | `webflow_form` |
| Is demo | `true` (Yes) |

Error handler: right-click this module → Add error handler → **Resume**. A HubSpot problem must not stop the reply or the Slack alert.

## 4 · Webhooks → Webhook response

| Setting | Value |
|---|---|
| Status | 200 |
| Header | `Content-Type` = `text/html` |
| Body | `<meta http-equiv="refresh" content="0;url=https://vishnuujm.github.io/growth-ops-lab/thanks.html">Thanks!` |

## 5 · Router
One route, filter label "Grade A": `tier` from step 2, **Text: Equal to**, `A`.

## 6 · HTTP → Make a request (Slack)

| Setting | Value |
|---|---|
| URL | `<SLACK_WEBHOOK_URL>` |
| Method | POST |
| Body type | `application/json`, entered as raw text |
| Body | `slack_body` from step 2, and nothing else |

## Switching on
1. Open the webhook's queue and delete old test messages.
2. Schedule: **Immediately as data arrives**.
3. Switch the scenario **ON**.

## Export (for the repository)
… menu → Export Blueprint. The file contains the secret and the Slack address: Claude replaces them and scans it before any commit.

Credits per enquiry: about 4–5.
