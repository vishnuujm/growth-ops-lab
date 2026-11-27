import httpx
import pytest

from common import slack

URL = "https://hooks.slack.com/services/T000/B000/supersecret"


@pytest.fixture(autouse=True)
def webhook(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", URL)
    monkeypatch.setattr(slack.time, "sleep", lambda s: None)


def fake_post(monkeypatch, *responses):
    sent, queue = [], list(responses)

    def post(url, json, timeout):
        sent.append(json)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return httpx.Response(item, text="ok" if item == 200 else "invalid_payload")

    monkeypatch.setattr(slack.httpx, "post", post)
    return sent


def test_sends_text_and_blocks(monkeypatch):
    sent = fake_post(monkeypatch, 200)
    slack.post_message("hi", blocks=[{"type": "divider"}])
    assert sent == [{"text": "hi", "blocks": [{"type": "divider"}]}]


def test_retries_on_429(monkeypatch):
    sent = fake_post(monkeypatch, 429, 200)
    slack.post_message("hi")
    assert len(sent) == 2


@pytest.mark.parametrize("failure", [400, httpx.ConnectError(f"failed for {URL}")])
def test_errors_never_leak_webhook(monkeypatch, failure):
    fake_post(monkeypatch, failure)
    with pytest.raises(slack.SlackError) as err:
        slack.post_message("hi")
    assert "supersecret" not in str(err.value)


def test_rejects_wrong_url(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://example.com/x")
    with pytest.raises(slack.SlackError):
        slack.post_message("hi")
