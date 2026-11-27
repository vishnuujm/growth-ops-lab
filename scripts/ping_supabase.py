"""Insert one events_log row, read it back, print it. Exit 1 on failure.

    uv run scripts/ping_supabase.py

Also used by the keepalive workflow so the free project never pauses.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich import print  # noqa: E402

from common import supabase  # noqa: E402
from common.config import ConfigError  # noqa: E402


def main() -> int:
    try:
        inserted = supabase.insert(
            "events_log",
            {"project": "foundation", "event": "ping", "ok": True, "payload": {"host": platform.node() or "unknown", "is_demo": True}},
        )
        rows = supabase.select("events_log", filters={"id": f"eq.{inserted['id']}"})
    except (ConfigError, supabase.SupabaseError) as exc:
        print(f"[red]Supabase ping failed:[/red] {exc}")
        return 1

    if len(rows) != 1:
        print(f"[red]Inserted row {inserted['id']} but read back {len(rows)} rows.[/red]")
        return 1

    print("[green]Supabase ping OK[/green] — inserted and read back:")
    print(json.dumps(rows[0], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
