import httpx
import pytest

from common import hubspot


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("HUBSPOT_TOKEN", "pat-test-secret")
    monkeypatch.setenv("HUBSPOT_PORTAL_ID", "111")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setattr(hubspot, "_verified_token", None)
    hubspot._calls.clear()


@pytest.fixture
def sleeps(monkeypatch):
    log = []
    monkeypatch.setattr(hubspot.time, "sleep", log.append)
    return log


def fake_api(monkeypatch, handler):
    seen = []

    def request(method, url, json=None, params=None, headers=None, timeout=None):
        path = url.removeprefix(hubspot.BASE)
        seen.append((method, path, json))
        return handler(method, path, json)

    monkeypatch.setattr(hubspot.httpx, "request", request)
    return seen


def account(kind="DEVELOPER_TEST", portal=111):
    return httpx.Response(200, json={"accountType": kind, "portalId": portal})


def test_retries_429_with_backoff(monkeypatch, sleeps):
    replies = [httpx.Response(429), httpx.Response(429, headers={"Retry-After": "3"}), httpx.Response(200, json={"ok": 1})]
    fake_api(monkeypatch, lambda *a: replies.pop(0))
    assert hubspot.request("GET", "/x") == {"ok": 1}
    assert sleeps == [1.0, 3.0]


def test_gives_up_after_max_retries(monkeypatch, sleeps):
    seen = fake_api(monkeypatch, lambda *a: httpx.Response(429, json={"message": "slow down"}))
    with pytest.raises(hubspot.HubSpotError) as err:
        hubspot.request("GET", "/x")
    assert err.value.status == 429
    assert len(seen) == hubspot.MAX_RETRIES + 1
    assert "pat-test-secret" not in str(err.value)


def test_throttle_waits_when_window_full(monkeypatch, sleeps):
    monkeypatch.setattr(hubspot.time, "monotonic", lambda: 100.0)
    for _ in range(hubspot.MAX_CALLS):
        hubspot._throttle()
    assert sleeps == []
    hubspot._throttle()
    assert sleeps == [hubspot.WINDOW_S]


@pytest.mark.parametrize("kind,portal", [("STANDARD", 111), ("DEVELOPER_TEST", 999)])
def test_demo_mode_blocks_wrong_account(monkeypatch, kind, portal):
    seen = fake_api(monkeypatch, lambda *a: account(kind, portal))
    with pytest.raises(hubspot.HubSpotError):
        hubspot.upsert_contact("a@example.com")
    assert [m for m, *_ in seen] == ["GET"]  # nothing was written


@pytest.mark.parametrize("exists,expected", [(False, "POST"), (True, "PATCH")])
def test_upsert_creates_or_updates(monkeypatch, exists, expected):
    def handler(method, path, body):
        if path.startswith("/account-info"):
            return account()
        if method == "GET":
            return httpx.Response(200, json={"id": "5"}) if exists else httpx.Response(404, json={"message": "nf"})
        return httpx.Response(200, json={"id": "5"})

    seen = fake_api(monkeypatch, handler)
    hubspot.upsert_contact(" A@Example.com ", {"lead_tier": "A"})
    method, _, body = seen[-1]
    assert method == expected
    assert body["properties"] == {"lead_tier": "A", "email": "a@example.com", "is_demo": "true"}


def test_deal_is_labelled_and_associated(monkeypatch):
    seen = fake_api(monkeypatch, lambda m, p, b: account() if "account-info" in p else httpx.Response(201, json={"id": "9"}))
    hubspot.create_deal("Asha", "5", amount=500)
    body = seen[-1][2]
    assert body["properties"]["dealname"] == "[DEMO] Asha"
    assert body["associations"][0]["to"]["id"] == "5"


def test_existing_property_is_not_recreated(monkeypatch):
    seen = fake_api(monkeypatch, lambda *a: httpx.Response(200, json={"name": "lead_score"}))
    assert hubspot.ensure_contact_property({"name": "lead_score"}) == "exists"
    assert len(seen) == 1
