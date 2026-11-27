"""Rules-based lead score. Python mirror of supabase/functions/score-lead/rules.ts.

A test runs both on the same people and fails if they ever disagree.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ICP_FILE = Path(__file__).resolve().parent / "icp.yaml"


def load_icp() -> dict:
    return yaml.safe_load(ICP_FILE.read_text())


def _clean(value) -> str:
    return str(value or "").strip().lower()


def _words(text: str) -> str:
    return " " + " ".join(re.findall(r"[a-z0-9]+", text)) + " "


def _has_any(padded: str, words: list[str]) -> bool:
    return any(f" {w} " in padded for w in words)


def score_lead(lead: dict, icp: dict) -> dict:
    total = 0
    good: list[str] = []
    bad: list[str] = []

    size = _clean(lead.get("company_size"))
    if size in icp["company_size"]:
        total += icp["company_size"][size]
        good.append(icp["size_labels"][size])

    role = _words(_clean(lead.get("role")))
    r = icp["role"]
    if role.strip():
        if _has_any(role, r["negative"]["words"]):
            total += r["negative"]["points"]
            bad.append(r["negative"]["label"])
        else:
            level = next((k for k in ("senior", "manager") if _has_any(role, r[k]["words"])), "other")
            total += r[level]["points"]
            good.append(r[level]["label"])

    timeline = icp["timeline"].get(_clean(lead.get("timeline")))
    if timeline:
        total += timeline["points"]
        good.append(timeline["label"])

    need = _words(_clean(lead.get("use_case")))
    u = icp["use_case"]
    matched = sum(1 for group in u["needs"] if _has_any(need, group))
    if matched:
        total += min(matched * u["points_per_need"], u["max_points"])
        good.append("clear need")
    if _has_any(need, u["junk"]["words"]):
        total += u["junk"]["points"]
        bad.append("message looks like junk or a job request")

    email = _clean(lead.get("email"))
    domain = email.rsplit("@", 1)[1] if "@" in email else ""
    if domain in icp["free_email"]["domains"]:
        total += icp["free_email"]["points"]
        bad.append("personal email")

    score = max(0, min(100, total))
    tier = "A" if score >= icp["thresholds"]["A"] else "B" if score >= icp["thresholds"]["B"] else "C"

    # Concerns come first for weak leads, so the reason explains the grade.
    parts = bad + good if tier == "C" else good + bad
    reason = ", ".join(parts) or "not enough information"
    reason = reason[0].upper() + reason[1:]
    return {"score": score, "tier": tier, "reason": reason[:200]}
