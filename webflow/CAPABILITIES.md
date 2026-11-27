# Webflow: what Claude Code and the free Starter plan can do

Checked 2026-11-27. The tables below are from docs and search; see "Tried on our account" for what has been tested.

## Tried on our account (2026-11-27, free Starter, MCP connector 2.2.0, Designer closed)

| Action | Result |
|---|---|
| Create the second page with slug, SEO title and description | Worked (stored; not yet checked in published HTML) |
| Build sections and styles from HTML + CSS | Worked |
| Create a native form, inputs, textarea, selects, names, required flags, POST method, button text | Worked |
| Field names from inserted HTML | Not carried over; set through element settings |
| New text inputs | Came out required by default; switched off for optional fields |
| Add options to a select | No tool found; add by hand in the Designer |
| Form Action URL | Set by hand (Send to → Custom Action, after removing the default destinations). Published and confirmed on Starter |
| Published pages | Titles, descriptions, field names, dropdown values and POST action confirmed in live HTML; no sideways scroll at phone width; badge shown |

**Confidence:** **Read** = the Webflow developer page was fetched and read. **Search** = taken from web-search summaries; Webflow's help centre refused automated fetching (403) and the pricing page could not be parsed.

## Ways to use Claude Code

| Option | What it does | Needs | Confidence |
|---|---|---|---|
| MCP server, data tools | Create and edit elements and styles, insert elements from HTML + CSS strings (`data_whtml_builder`), page SEO metadata, publish the site. Designer does not need to be open | OAuth sign-in; only site owners and admins can authorise | Read (page and publish tools partly from a summary of the page) |
| MCP server, Designer tools | Selection, page switching, canvas navigation, snapshots, image upload | Designer open with the MCP Bridge App | Read |
| MCP on free Starter | Listed as available | | Search |
| Data API | Page metadata updates; 60 requests/minute on Starter | API token | Search |
| Content edits through the API/MCP in the primary language | Docs conflict or are silent: element tools write to pages, but the localisation docs limit static-content API edits to secondary locales | Test before relying on it | Unconfirmed |
| Set a form's Action URL through MCP | The Designer API has a form `setSettings` call; no MCP tool page mentions it | Do it by hand | Unconfirmed |
| Paste a whole HTML page into the Designer | Not available; custom code goes in Code Embed or head/footer fields, which need a paid plan | | Search |

In the Claude desktop app, a **Webflow** connector (`https://mcp.webflow.com/mcp`) is listed in the connector directory; it is not connected. The `claude` command-line tool is not on this Mac's PATH.

Install command for the command-line tool (Read): `claude mcp add --transport http webflow https://mcp.webflow.com/mcp`, then `/mcp` to sign in.

## Free Starter plan

| Item | Finding | Confidence |
|---|---|---|
| Static pages | 2 | Search |
| Publishing | webflow.io subdomain only; no custom domain | Search |
| Badge | "Made with Webflow" badge shown | Search (third party) |
| Custom code / Code Embed | Paid plans only | Search |
| Form submissions stored by Webflow | 50 total | Search |
| Form custom Action URL | Supported as a form setting; Webflow then stores nothing, sends no notification and does no spam filtering. Behaviour on Starter not confirmed | Search; test in F9 |
| SEO title and description on Starter | Not found | Test in F9 |
| Whether 404/password pages count toward the 2 | Not found | Check in the Designer |
| Traffic limits | 1,000 visits/month, 50 CMS items | Search |

## Recommendation for F9

1. Claude writes the page copy, SEO fields and field names.
2. Try the MCP server to build the layout, authorised for the `growth-ops-lab` site only. If it cannot, build by hand from the same file.
3. Set the form Action URL and method by hand, so the webhook URL never enters a chat.
4. Publish and review by hand.

## Sources

- https://developers.webflow.com/mcp/installing/claude-code
- https://developers.webflow.com/mcp/reference/how-it-works
- https://developers.webflow.com/mcp/reference/getting-started
- https://developers.webflow.com/mcp/v1.0.0/faqs
- https://developers.webflow.com/mcp/tools/data-tools
- https://developers.webflow.com/mcp/tools/designer-tools
- https://developers.webflow.com/data/reference/rate-limits
- https://developers.webflow.com/data/reference/pages/update-page-settings
- https://developers.webflow.com/designer/reference/form-element/set-form-settings
- https://webflow.com/pricing
- https://help.webflow.com/hc/en-us/articles/33961232582419-Choose-a-Site-plan
- https://help.webflow.com/hc/en-us/articles/33961344521235-Form-submissions
- https://help.webflow.com/hc/en-us/articles/33961332238611-Custom-code-embed
- https://webflow.com/blog/customize-webflow-form-notification-emails
