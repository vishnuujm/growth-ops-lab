"""Safely put values into .env without pasting secrets into chat.

    uv run scripts/set_env.py SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY

Asks for each variable in turn. Secret-looking names (KEY, TOKEN, SECRET, WEBHOOK,
PASSWORD) are typed hidden, so nothing shows on screen — paste and press Enter.
Press Enter on an empty line to skip a variable and keep its current value.
Only the first and last few characters are ever shown back.
"""

from __future__ import annotations

import getpass
import re
import sys
from pathlib import Path

ENV = Path(__file__).resolve().parent.parent / ".env"
SECRET_WORDS = ("KEY", "TOKEN", "SECRET", "WEBHOOK", "PASSWORD")


def mask(value: str) -> str:
    if len(value) <= 10:
        return "*" * len(value)
    return f"{value[:4]}…{value[-4:]} ({len(value)} chars)"


def format_value(value: str) -> str:
    if re.search(r"[\s#'\"]", value):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return value


def set_line(lines: list[str], name: str, value: str) -> list[str]:
    pattern = re.compile(rf"^{re.escape(name)}=(\S*)(\s*#.*)?$")
    for i, line in enumerate(lines):
        m = pattern.match(line)
        if m:
            comment = m.group(2) or ""
            new = f"{name}={format_value(value)}"
            if comment:
                new = f"{new}   {comment.strip()}"
            lines[i] = new
            return lines
    lines.append(f"{name}={format_value(value)}")
    return lines


def main(names: list[str]) -> int:
    if not names:
        print(__doc__)
        return 1
    if not ENV.exists():
        print(f"{ENV} not found. Run: cp .env.example .env")
        return 1

    lines = ENV.read_text().splitlines()
    changed = []
    for name in names:
        secret = any(w in name.upper() for w in SECRET_WORDS)
        prompt = f"{name}{' (hidden — paste, then Enter)' if secret else ''}: "
        value = (getpass.getpass(prompt) if secret else input(prompt)).strip()
        if not value:
            print(f"  skipped {name}")
            continue
        lines = set_line(lines, name, value)
        changed.append(name)
        print(f"  saved {name} = {mask(value) if secret else value}")

    ENV.write_text("\n".join(lines) + "\n")
    ENV.chmod(0o600)
    print(f"\nDone. Updated {len(changed)} value(s) in .env: {', '.join(changed) or 'none'}")
    print("You can close this tab and tell Claude it's done.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
