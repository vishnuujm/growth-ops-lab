"""Read one HubSpot contact, so the developer test account counts as active.

    uv run scripts/ping_hubspot.py

Read-only. Prints no contact details, because GitHub Actions logs are public.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich import print  # noqa: E402

from common import hubspot  # noqa: E402
from common.config import ConfigError  # noqa: E402


def main() -> int:
    try:
        contacts = hubspot.list_contacts(limit=1)
    except ConfigError as exc:
        print(f"[red]HubSpot ping failed:[/red] {exc}")
        return 1
    except hubspot.HubSpotError as exc:
        print(f"[red]HubSpot ping failed:[/red] HTTP {exc.status}")
        return 1
    print(f"[green]HubSpot ping OK[/green] (read {len(contacts)} contact)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
