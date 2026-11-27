import csv
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
P01 = ROOT / "p01-lead-router"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rules = load("p01_rules", P01 / "rules.py")
seed = load("p01_seed", P01 / "seed" / "fake_leads.py")
build = load("p01_build", P01 / "build_icp.py")
ICP = rules.load_icp()
LEADS = seed.leads()

EDGE_CASES = [
    {},
    {"email": None, "role": None},
    {"company_size": "constructor", "timeline": "toString"},
    {"company_size": " 51-200 ", "timeline": "NOW", "role": "  HEAD, of Sales "},
    {"role": "Student Manager"},
    {"role": "Leadership coach"},
    {"role": "Vice-President"},
    {"use_case": "automate automation automating"},
    {"use_case": "automate improve replace scale integrate reporting crm pipeline"},
    {"use_case": "latest contest"},
    {"email": "a@b@GMAIL.com"},
    {"email": "no-at-sign"},
]


def score(**lead):
    return rules.score_lead(lead, ICP)


@pytest.mark.parametrize("lead", LEADS, ids=lambda l: l["case"])
def test_each_made_up_person_gets_the_expected_grade(lead):
    assert rules.score_lead(lead, ICP)["tier"] == lead["expected_tier"]


def test_seed_mix_is_5_a_5_b_4_c_and_1_duplicate():
    cases = [l["case"] for l in LEADS]
    assert [sum(c.startswith(x) and c != "DUP" for c in cases) for x in "ABC"] == [5, 5, 4]
    emails = [l["email"].lower() for l in LEADS]
    assert len(emails) == 15 and len(set(emails)) == 14


def test_expected_csv_matches_the_people():
    with (P01 / "seed" / "expected.csv").open() as f:
        rows = [(r["case"], r["email"], r["expected_tier"]) for r in csv.DictReader(f)]
    assert rows == [(l["case"], l["email"], l["expected_tier"]) for l in LEADS]


def test_online_rules_file_is_in_step_with_icp_yaml():
    assert build.TARGET.read_text() == build.render(), "run: uv run p01-lead-router/build_icp.py"


def test_python_and_typescript_give_identical_results():
    people = LEADS + EDGE_CASES
    out = subprocess.run(["node", str(ROOT / "tests" / "run_rules.mjs")], input=json.dumps(people), capture_output=True, text=True, check=True)
    assert json.loads(out.stdout) == [rules.score_lead(p, ICP) for p in people]


@pytest.mark.parametrize("points,tier", [(39, "C"), (40, "B"), (69, "B"), (70, "A")])
def test_grade_boundaries(points, tier):
    icp = {**ICP, "company_size": {"x": points}, "size_labels": {"x": "x"}}
    assert rules.score_lead({"company_size": "x"}, icp) == {"score": points, "tier": tier, "reason": "X"}


def test_score_stays_between_0_and_100():
    assert score(role="intern", use_case="asdf", email="a@gmail.com")["score"] == 0
    best = score(company_size="51-200", role="founder", timeline="now", use_case="automate improve replace scale")
    assert best["score"] == 100


def test_whole_words_only_and_variants_count_once():
    assert score(role="Leadership coach")["score"] == ICP["role"]["other"]["points"]
    assert score(use_case="latest contest")["score"] == 0
    assert score(use_case="automate automation")["score"] == ICP["use_case"]["points_per_need"]


def test_student_outweighs_manager_and_empty_is_explained():
    assert "student or intern" in score(role="Student Manager")["reason"].lower()
    assert score() == {"score": 0, "tier": "C", "reason": "Not enough information"}


def test_reason_is_short():
    assert all(len(rules.score_lead(l, ICP)["reason"]) <= 200 for l in LEADS)
