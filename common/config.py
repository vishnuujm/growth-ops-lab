"""Load settings from .env (locally) or the environment (GitHub Actions, etc.).

Usage:
    from common.config import settings, DEMO_MODE

    url = settings.require("SUPABASE_URL")             # one value, or a clear error
    url, key = settings.require("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
    model = settings.get("GEMINI_MODEL", "fallback")   # optional value
    settings.SUPABASE_URL                              # same as require("SUPABASE_URL")

A variable that is missing or empty counts as "not set". Real environment
variables win over .env, so GitHub Actions secrets override local values.
Values are never printed: errors name the variable, not its contents.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

load_dotenv(ENV_FILE, override=False)

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


class ConfigError(RuntimeError):
    """Raised when a script needs a variable that is not set."""


def _parse_bool(name: str, raw: str | None, default: bool) -> bool:
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ConfigError(f"{name} must be true or false, got an unrecognised value.")


class Settings:
    def get(self, name: str, default: str | None = None) -> str | None:
        value = os.environ.get(name)
        if value is None or value.strip() == "":
            return default
        return value.strip()

    def require(self, *names: str) -> str | tuple[str, ...]:
        missing = [n for n in names if self.get(n) is None]
        if missing:
            listed = ", ".join(missing)
            raise ConfigError(
                f"Missing setting(s): {listed}. "
                f"Add them to {ENV_FILE} (see .env.example), "
                "or to GitHub Actions secrets when running in CI."
            )
        values = tuple(self.get(n) for n in names)
        return values[0] if len(values) == 1 else values  # type: ignore[return-value]

    def get_int(self, name: str, default: int | None = None) -> int | None:
        raw = self.get(name)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            raise ConfigError(f"{name} must be a whole number.") from None

    def get_bool(self, name: str, default: bool = False) -> bool:
        return _parse_bool(name, os.environ.get(name), default)

    @property
    def demo_mode(self) -> bool:
        # Safe default: anything unset means demo mode ON.
        return self.get_bool("DEMO_MODE", default=True)

    def __getattr__(self, name: str) -> str:
        if name.isupper():
            return self.require(name)  # type: ignore[return-value]
        raise AttributeError(name)


settings = Settings()
DEMO_MODE: bool = settings.demo_mode
