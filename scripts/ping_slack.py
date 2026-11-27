"""Post a hello message to the Slack channel behind SLACK_WEBHOOK_URL.

    uv run scripts/ping_slack.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich import print  # noqa: E402

from common.config import ConfigError  # noqa: E402
from common.slack import SlackError, post_message  # noqa: E402

MESSAGE = "Growth Ops Lab is wired up ✅"


def main() -> int:
    try:
        post_message(MESSAGE)
    except (ConfigError, SlackError) as exc:
        print(f"[red]Slack ping failed:[/red] {exc}")
        return 1
    print(f"[green]Slack accepted the message:[/green] {MESSAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
