"""Create the custom contact properties (if missing), then fetch one contact.

    uv run scripts/hubspot_setup.py

Safe to run repeatedly.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich import print  # noqa: E402

from common import hubspot  # noqa: E402
from common.config import ConfigError  # noqa: E402


def _options(values: list[tuple[str, str]]) -> list[dict]:
    return [{"label": label, "value": value, "displayOrder": i} for i, (label, value) in enumerate(values)]


PROPERTIES = [
    {"name": "lead_score", "label": "Lead score", "type": "number", "fieldType": "number"},
    {
        "name": "lead_tier",
        "label": "Lead tier",
        "type": "enumeration",
        "fieldType": "select",
        "options": _options([("A", "A"), ("B", "B"), ("C", "C"), ("unscored", "unscored")]),
    },
    {"name": "lead_reason", "label": "Lead reason", "type": "string", "fieldType": "textarea"},
    {"name": "lead_source_detail", "label": "Lead source detail", "type": "string", "fieldType": "text"},
    {
        "name": "is_demo",
        "label": "Is demo",
        "type": "bool",
        "fieldType": "booleancheckbox",
        "options": _options([("Yes", "true"), ("No", "false")]),
    },
]


def main() -> int:
    try:
        info = hubspot.account_info()
        print(f"Account: portal {info['portalId']} ({info['accountType']})")
        hubspot.ensure_safe_to_write()
        for definition in PROPERTIES:
            result = hubspot.ensure_contact_property(definition)
            print(f"  property {definition['name']:<20} {result}")
        contacts = hubspot.list_contacts(limit=1)
    except (ConfigError, hubspot.HubSpotError) as exc:
        print(f"[red]HubSpot setup failed:[/red] {exc}")
        return 1

    if contacts:
        c = contacts[0]
        print(f"Fetched 1 contact: id={c['id']} email={c['properties'].get('email')}")
    else:
        print("Token works; the account has no contacts yet.")
    print("[green]HubSpot setup OK[/green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
