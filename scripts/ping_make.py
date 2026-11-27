"""POST one synthetic lead to the Make webhook (MAKE_WEBHOOK_LEADS_URL).

    uv run scripts/ping_make.py

The URL is a secret and is never printed. Costs Make credits if the scenario runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402
from rich import print  # noqa: E402

from common.config import ConfigError, settings  # noqa: E402

# P01 data contract. example.com is reserved for tests, so this is nobody's address.
SAMPLE_LEAD = {
    "email": "test.lead@example.com",
    "first_name": "Test",
    "last_name": "Lead",
    "company": "Example Co",
    "company_size": "51-200",
    "role": "Head of Operations",
    "use_case": "Improve lead tracking and reporting",
    "timeline": "1-3m",
    "source": "seed",
    "utm_source": "test",
    "utm_medium": "script",
    "utm_campaign": "f8_ping",
    "gclid": "",
    "fbclid": "",
    "page_url": "https://example.com/contact",
    "is_demo": "true",
}


def main() -> int:
    try:
        url = settings.require("MAKE_WEBHOOK_LEADS_URL")
    except ConfigError as exc:
        print(f"[red]Make ping failed:[/red] {exc}")
        return 1
    if not url.startswith("https://hook.") or ".make.com/" not in url:
        print("[red]Make ping failed:[/red] MAKE_WEBHOOK_LEADS_URL does not look like https://hook.<region>.make.com/...")
        return 1
    try:
        # Form-encoded, the same way a Webflow form posts.
        resp = httpx.post(url, data=SAMPLE_LEAD, timeout=20)
    except httpx.HTTPError as exc:
        print(f"[red]Make ping failed:[/red] could not reach Make ({type(exc).__name__}).")
        return 1
    if resp.is_error:
        print(f"[red]Make ping failed:[/red] HTTP {resp.status_code} {resp.text[:200]}")
        return 1
    print(f"[green]Make accepted the lead:[/green] HTTP {resp.status_code} {resp.text[:100]!r}")
    print(f"Sent {len(SAMPLE_LEAD)} fields: {', '.join(SAMPLE_LEAD)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
