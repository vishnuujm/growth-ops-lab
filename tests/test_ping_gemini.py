import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("ping_gemini", Path(__file__).parent.parent / "scripts" / "ping_gemini.py")
ping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ping)


def reply(*parts):
    return {"candidates": [{"content": {"parts": list(parts)}}]}


def test_parses_json_and_skips_thoughts():
    data = reply({"text": "thinking...", "thought": True}, {"text": '{"ok": true, "model": "m"}'})
    assert ping.parse_reply(data) == {"ok": True, "model": "m"}


@pytest.mark.parametrize("data", [{}, {"candidates": []}, reply({"text": "not json"}), reply({"text": '{"ok": "yes", "model": "m"}'}), reply({"text": "[1]"})])
def test_bad_replies_raise_value_error(data):
    with pytest.raises(ValueError):
        ping.parse_reply(data)


def test_explains_limit_and_missing_model():
    assert "429" in ping.explain(429, "")
    assert "GEMINI_MODEL" in ping.explain(404, "")
