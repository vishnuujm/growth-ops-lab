"""Copy icp.yaml into the JSON file the online scoring function reads.

    uv run p01-lead-router/build_icp.py
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "icp.yaml"
TARGET = HERE.parent / "supabase" / "functions" / "score-lead" / "icp.json"


def render() -> str:
    return json.dumps(yaml.safe_load(SOURCE.read_text()), indent=2) + "\n"


if __name__ == "__main__":
    TARGET.write_text(render())
    print(f"Wrote {TARGET.relative_to(HERE.parent)}")
