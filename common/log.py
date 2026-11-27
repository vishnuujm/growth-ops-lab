"""Write a row to Supabase events_log. Logging never crashes the caller.

    from common.log import log_event
    log_event("p01", "lead_scored", ok=True, payload={"tier": "A"})
"""

from __future__ import annotations

from typing import Any

from rich.console import Console

from common import supabase

_console = Console(stderr=True)


def log_event(project: str, event: str, *, ok: bool = True, payload: dict[str, Any] | None = None) -> dict | None:
    row = {"project": project, "event": event, "ok": ok, "payload": payload or {}}
    try:
        return supabase.insert("events_log", row)
    except Exception as exc:  # noqa: BLE001 — a failed log must not break the real work
        _console.print(f"[yellow]events_log write failed ({project}/{event}): {exc}[/yellow]")
        return None
