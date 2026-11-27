"""Ask GEMINI_MODEL for a tiny JSON reply, to prove the key and model work.

    uv run scripts/ping_gemini.py

Free-tier data may be used by Google, so only synthetic text is ever sent.
Any error is explained; the script never crashes on one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402
from rich import print  # noqa: E402

from common.config import ConfigError, settings  # noqa: E402

BASE = "https://generativelanguage.googleapis.com/v1beta/models"
SCHEMA = {
    "type": "OBJECT",
    "properties": {"ok": {"type": "BOOLEAN"}, "model": {"type": "STRING"}},
    "required": ["ok", "model"],
}


def parse_reply(data: dict) -> dict:
    """Pull the JSON object out of a generateContent response. Raises ValueError."""
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        result = json.loads(text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"unexpected reply shape ({type(exc).__name__})") from None
    if not isinstance(result, dict) or not isinstance(result.get("ok"), bool) or not isinstance(result.get("model"), str):
        raise ValueError("reply is missing 'ok' (true/false) or 'model' (text)")
    return result


def explain(status: int, message: str) -> str:
    if status == 429:
        return "Free limit reached for now (429). Try again later."
    if status == 404:
        return "Model not found (404). Check GEMINI_MODEL."
    if status in (400, 401, 403):
        return f"Google refused the request ({status}). Check the key. {message}"
    return f"Google returned an error ({status}). {message}"


def main() -> int:
    try:
        key, model = settings.require("GEMINI_API_KEY", "GEMINI_MODEL")
    except ConfigError as exc:
        print(f"[red]Gemini ping failed:[/red] {exc}")
        return 1
    body = {
        "contents": [{"parts": [{"text": f"Reply with ok true and model set to {model}."}]}],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json", "responseSchema": SCHEMA},
    }
    try:
        resp = httpx.post(f"{BASE}/{model}:generateContent", json=body, headers={"x-goog-api-key": key}, timeout=30)
        if resp.is_error:
            try:
                message = str(resp.json()["error"]["message"])[:200]
            except (ValueError, KeyError, TypeError):
                message = ""
            print(f"[red]Gemini ping failed:[/red] {explain(resp.status_code, message)}")
            return 1
        result = parse_reply(resp.json())
    except httpx.HTTPError as exc:
        print(f"[red]Gemini ping failed:[/red] could not reach Google ({type(exc).__name__}).")
        return 1
    except ValueError as exc:
        print(f"[red]Gemini ping failed:[/red] {exc}")
        return 1
    print(f"[green]Gemini ping OK[/green] (model {model})")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
