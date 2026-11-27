"""Tiny Supabase REST (PostgREST) client using the service-role / secret key.

Server-side only: the secret key bypasses RLS. Never ship it to a browser.

    from common import supabase
    row = supabase.insert("events_log", {"project": "f2", "event": "ping", "ok": True})
    rows = supabase.select("events_log", filters={"id": f"eq.{row['id']}"})
    supabase.update("leads", {"status": "qualified"}, filters={"id": f"eq.{lead_id}"})

Filters use PostgREST syntax: {"column": "op.value"}, e.g. "eq.5", "gte.2026-01-01", "is.null".
"""

from __future__ import annotations

from typing import Any

import httpx

from common.config import settings

TIMEOUT = httpx.Timeout(20.0)


class SupabaseError(RuntimeError):
    pass


def _auth_headers(key: str) -> dict[str, str]:
    headers = {"apikey": key}
    # Legacy service_role keys are JWTs and also go in Authorization.
    # New "sb_secret_..." keys are not JWTs: the apikey header alone is correct.
    if key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {key}"
    return headers


def _client() -> httpx.Client:
    url, key = settings.require("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
    return httpx.Client(
        base_url=f"{url.rstrip('/')}/rest/v1",
        headers={**_auth_headers(key), "Content-Type": "application/json"},
        timeout=TIMEOUT,
    )


def _check(resp: httpx.Response) -> Any:
    if resp.is_error:
        # PostgREST errors are JSON {code, message, details, hint}; they never echo the key.
        raise SupabaseError(f"Supabase {resp.status_code} on {resp.request.method} {resp.request.url.path}: {resp.text[:500]}")
    return resp.json() if resp.content else None


def insert(table: str, rows: dict | list[dict], *, upsert_on: str | None = None) -> Any:
    """Insert one row (returns it) or many (returns a list).

    upsert_on: comma-separated column(s) with a plain unique constraint to merge on.
    """
    prefer = ["return=representation"]
    params = {}
    if upsert_on:
        prefer.append("resolution=merge-duplicates")
        params["on_conflict"] = upsert_on
    with _client() as c:
        data = _check(c.post(f"/{table}", json=rows, params=params, headers={"Prefer": ",".join(prefer)}))
    return data[0] if isinstance(rows, dict) and data else data


def select(
    table: str,
    *,
    columns: str = "*",
    filters: dict[str, str] | None = None,
    order: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    params: dict[str, Any] = {"select": columns, **(filters or {})}
    if order:
        params["order"] = order
    if limit is not None:
        params["limit"] = limit
    with _client() as c:
        return _check(c.get(f"/{table}", params=params))


def update(table: str, values: dict, *, filters: dict[str, str]) -> list[dict]:
    """Update rows matching filters. Filters are required so a typo can't update every row."""
    if not filters:
        raise SupabaseError("update() needs at least one filter.")
    with _client() as c:
        return _check(c.patch(f"/{table}", json=values, params=filters, headers={"Prefer": "return=representation"}))
