"""Tiny HubSpot CRM client (private app token, developer TEST account).

    from common import hubspot
    contact = hubspot.upsert_contact("asha@example.com", {"firstname": "Asha", "lead_tier": "A"})
    deal = hubspot.create_deal("Asha - demo", contact["id"], amount=500)
    hubspot.update_deal_stage(deal["id"], "qualifiedtobuy")

Safety: while DEMO_MODE is on, writes are refused unless the token belongs to a
developer test account or sandbox.
Rate limit: calls are spaced to stay under 100 per 10 s, and 429s are retried.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any
from urllib.parse import quote

import httpx

from common.config import settings

BASE = "https://api.hubapi.com"
TIMEOUT = httpx.Timeout(20.0)
MAX_CALLS, WINDOW_S = 90, 10.0  # a little under HubSpot's 100 per 10 s
MAX_RETRIES = 4
SAFE_ACCOUNT_TYPES = {"DEVELOPER_TEST", "SANDBOX"}
DEAL_TO_CONTACT = 3  # HubSpot-defined association type id

_calls: deque[float] = deque()
_verified_token: str | None = None


class HubSpotError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(f"HubSpot {status}: {message}")
        self.status = status


def _throttle() -> None:
    now = time.monotonic()
    while _calls and now - _calls[0] >= WINDOW_S:
        _calls.popleft()
    if len(_calls) >= MAX_CALLS:
        time.sleep(WINDOW_S - (now - _calls[0]))
        _calls.popleft()
    _calls.append(time.monotonic())


def _retry_delay(resp: httpx.Response, attempt: int) -> float:
    try:
        return min(float(resp.headers["Retry-After"]), 30.0)
    except (KeyError, ValueError):
        return float(min(2**attempt, 30))  # 1, 2, 4, 8 seconds


def request(method: str, path: str, *, json: Any = None, params: dict | None = None) -> Any:
    """One API call with throttling and 429 backoff. Returns parsed JSON or None."""
    headers = {"Authorization": f"Bearer {settings.require('HUBSPOT_TOKEN')}"}
    for attempt in range(MAX_RETRIES + 1):
        _throttle()
        resp = httpx.request(method, BASE + path, json=json, params=params, headers=headers, timeout=TIMEOUT)
        if resp.status_code != 429 or attempt == MAX_RETRIES:
            break
        time.sleep(_retry_delay(resp, attempt))
    if resp.is_error:
        try:
            message = resp.json().get("message", resp.text)
        except ValueError:
            message = resp.text
        raise HubSpotError(resp.status_code, str(message)[:500])
    return resp.json() if resp.content else None


def account_info() -> dict:
    return request("GET", "/account-info/v3/details")


def ensure_safe_to_write() -> None:
    """In DEMO_MODE, refuse to write to anything that looks like a real account."""
    global _verified_token
    if not settings.demo_mode:
        return
    token = settings.require("HUBSPOT_TOKEN")
    if token == _verified_token:
        return
    info = account_info()
    if info.get("accountType") not in SAFE_ACCOUNT_TYPES:
        raise HubSpotError(0, f"DEMO_MODE is on but this token is for a {info.get('accountType')} account. Use a developer test account.")
    expected = settings.get("HUBSPOT_PORTAL_ID")
    if expected and str(info.get("portalId")) != expected:
        raise HubSpotError(0, f"HUBSPOT_PORTAL_ID is {expected} but the token belongs to portal {info.get('portalId')}.")
    _verified_token = token


# --- contacts -------------------------------------------------------------


def get_contact_by_email(email: str, properties: list[str] | None = None) -> dict | None:
    """Look up one contact by email. Uses the direct lookup, which (unlike the
    search endpoint) sees newly created contacts immediately."""
    params = {"idProperty": "email"}
    if properties:
        params["properties"] = ",".join(properties)
    try:
        return request("GET", f"/crm/v3/objects/contacts/{quote(email.strip().lower(), safe='')}", params=params)
    except HubSpotError as exc:
        if exc.status == 404:
            return None
        raise


def list_contacts(limit: int = 1) -> list[dict]:
    return request("GET", "/crm/v3/objects/contacts", params={"limit": limit})["results"]


def upsert_contact(email: str, properties: dict | None = None) -> dict:
    """Create the contact, or update it if the email already exists."""
    ensure_safe_to_write()
    email = email.strip().lower()
    props = {**(properties or {}), "email": email}
    if settings.demo_mode:
        props["is_demo"] = "true"

    existing = get_contact_by_email(email)
    if existing is None:
        try:
            return request("POST", "/crm/v3/objects/contacts", json={"properties": props})
        except HubSpotError as exc:
            if exc.status != 409:  # 409 = created by someone else a moment ago
                raise
            existing = get_contact_by_email(email)
            if existing is None:
                raise
    return request("PATCH", f"/crm/v3/objects/contacts/{existing['id']}", json={"properties": props})


# --- deals ----------------------------------------------------------------


def create_deal(
    name: str,
    contact_id: str,
    *,
    stage: str = "appointmentscheduled",
    pipeline: str = "default",
    amount: float | None = None,
    properties: dict | None = None,
) -> dict:
    """Create a deal already associated with a contact."""
    ensure_safe_to_write()
    if settings.demo_mode and not name.startswith("[DEMO]"):
        name = f"[DEMO] {name}"
    props = {"dealname": name, "dealstage": stage, "pipeline": pipeline, **(properties or {})}
    if amount is not None:
        props["amount"] = str(amount)
    association = {
        "to": {"id": str(contact_id)},
        "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": DEAL_TO_CONTACT}],
    }
    return request("POST", "/crm/v3/objects/deals", json={"properties": props, "associations": [association]})


def update_deal_stage(deal_id: str, stage: str) -> dict:
    ensure_safe_to_write()
    return request("PATCH", f"/crm/v3/objects/deals/{deal_id}", json={"properties": {"dealstage": stage}})


# --- properties -----------------------------------------------------------


def ensure_contact_property(definition: dict) -> str:
    """Create a contact property if it does not exist. Returns 'created' or 'exists'."""
    try:
        request("GET", f"/crm/v3/properties/contacts/{definition['name']}")
        return "exists"
    except HubSpotError as exc:
        if exc.status != 404:
            raise
    ensure_safe_to_write()
    request("POST", "/crm/v3/properties/contacts", json={"groupName": "contactinformation", **definition})
    return "created"
