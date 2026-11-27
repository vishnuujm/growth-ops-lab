"""Post to Slack through the app's incoming webhook.

    from common.slack import post_message
    post_message("Hot lead: Asha from Acme")
    post_message("fallback text", blocks=[...])

The webhook URL is a secret: it is never included in errors or logs.
"""

from __future__ import annotations

import time

import httpx

from common.config import settings

TIMEOUT = httpx.Timeout(15.0)
PREFIX = "https://hooks.slack.com/"


class SlackError(RuntimeError):
    pass


def post_message(text: str, blocks: list[dict] | None = None, *, retries: int = 2) -> None:
    """Send a message. Raises SlackError if Slack does not accept it."""
    url = settings.require("SLACK_WEBHOOK_URL")
    if not url.startswith(PREFIX):
        raise SlackError(f"SLACK_WEBHOOK_URL should start with {PREFIX}")

    body: dict = {"text": text}
    if blocks:
        body["blocks"] = blocks

    for attempt in range(retries + 1):
        try:
            resp = httpx.post(url, json=body, timeout=TIMEOUT)
        except httpx.HTTPError as exc:
            # "from None": httpx errors can carry the secret URL.
            raise SlackError(f"Could not reach Slack ({type(exc).__name__}).") from None
        if resp.status_code == 429 and attempt < retries:
            time.sleep(min(float(resp.headers.get("Retry-After", 1)), 30))
            continue
        if resp.is_error:
            raise SlackError(f"Slack rejected the message: HTTP {resp.status_code} {resp.text[:200]}")
        return
