import pytest

from common.config import ConfigError, Settings


def test_require_names_missing_variables(monkeypatch):
    monkeypatch.delenv("GOL_TEST_A", raising=False)
    monkeypatch.setenv("GOL_TEST_B", "   ")  # blank counts as missing
    with pytest.raises(ConfigError) as err:
        Settings().require("GOL_TEST_A", "GOL_TEST_B")
    assert "GOL_TEST_A" in str(err.value)
    assert "GOL_TEST_B" in str(err.value)


def test_require_returns_values(monkeypatch):
    monkeypatch.setenv("GOL_TEST_A", "one")
    monkeypatch.setenv("GOL_TEST_B", " two ")
    s = Settings()
    assert s.require("GOL_TEST_A") == "one"
    assert s.require("GOL_TEST_A", "GOL_TEST_B") == ("one", "two")
    assert s.GOL_TEST_A == "one"


def test_error_never_contains_secret_value(monkeypatch):
    monkeypatch.setenv("GOL_TEST_INT", "sk-secret-123")
    with pytest.raises(ConfigError) as err:
        Settings().get_int("GOL_TEST_INT")
    assert "sk-secret-123" not in str(err.value)


@pytest.mark.parametrize(
    "raw,expected",
    [(None, True), ("", True), ("true", True), ("TRUE", True), ("1", True), ("false", False), ("0", False), ("no", False)],
)
def test_demo_mode_defaults_to_true(monkeypatch, raw, expected):
    if raw is None:
        monkeypatch.delenv("DEMO_MODE", raising=False)
    else:
        monkeypatch.setenv("DEMO_MODE", raw)
    assert Settings().demo_mode is expected


def test_demo_mode_rejects_garbage(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "maybe")
    with pytest.raises(ConfigError):
        Settings().demo_mode


def test_get_int(monkeypatch):
    monkeypatch.setenv("GOL_TEST_INT", "5000000000")
    assert Settings().get_int("GOL_TEST_INT") == 5_000_000_000
    monkeypatch.delenv("GOL_TEST_INT")
    assert Settings().get_int("GOL_TEST_INT", 7) == 7
