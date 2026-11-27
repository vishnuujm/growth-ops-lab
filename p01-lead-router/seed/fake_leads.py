"""15 made-up people with the grade each one SHOULD get.

    uv run p01-lead-router/seed/fake_leads.py      # writes expected.csv

The expected grade is a human judgement written here by hand; it is not
calculated by the rules. All people and addresses are synthetic.
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "expected.csv"

FIELDS = ["email", "first_name", "last_name", "company", "company_size", "role", "use_case", "timeline"]

# (case, expected grade, then the form fields in FIELDS order)
PEOPLE = [
    ("A1", "A", "priya.shah@northwind.example", "Priya", "Shah", "Northwind Example", "51-200", "Head of Operations", "We want to automate lead follow-up and improve reporting", "now"),
    ("A2", "A", "marco.rossi@bluepeak.example", "Marco", "Rossi", "Blue Peak Example", "201-1000", "Marketing Director", "Replace our CRM and integrate it with our forms", "1-3m"),
    ("A3", "A", "aisha.khan@lumen.example", "Aisha", "Khan", "Lumen Example", "11-50", "Founder", "Need to scale our sales pipeline", "now"),
    ("A4", "A", "daniel.okafor@harbor.example", "Daniel", "Okafor", "Harbor Example", "1000+", "VP Growth", "Integrate our CRM and automate reporting", "now"),
    ("A5", "A", "mei.tan@cedar.example", "Mei", "Tan", "Cedar Example", "51-200", "Operations Manager", "Automate data entry and improve our pipeline reports", "now"),
    ("B1", "B", "sam.lee@orchard.example", "Sam", "Lee", "Orchard Example", "11-50", "Marketing Manager", "Improve our reporting", "3-6m"),
    ("B2", "B", "nina.verma@quartz.example", "Nina", "Verma", "Quartz Example", "51-200", "Analyst", "Looking at CRM options", "1-3m"),
    ("B3", "B", "omar.haddad@gmail.com", "Omar", "Haddad", "Haddad Studio", "1-10", "Owner", "Want to automate our enquiries", "1-3m"),
    ("B4", "B", "lena.fischer@meadow.example", "Lena", "Fischer", "Meadow Example", "201-1000", "Director", "", "exploring"),
    ("B5", "B", "ravi.menon@summit.example", "Ravi", "Menon", "Summit Example", "1000+", "Team Lead", "Integrate two internal tools", "3-6m"),
    ("C1", "C", "asdf@asdf.example", "asdf", "", "asdf", "1-10", "asdf", "test asdf", "exploring"),
    ("C2", "C", "gol-synthetic-student@gmail.com", "Jo", "Park", "", "1-10", "Student", "Looking for an internship", "now"),
    ("C3", "C", "gol-synthetic-browser@yahoo.com", "Alex", "Doe", "", "", "", "Just looking around", "exploring"),
    ("C4", "C", "kim.cho@pebble.example", "Kim", "Cho", "Pebble Example", "11-50", "Assistant", "Is there a free job opening?", "3-6m"),
    # Same person as A1 writing again, with different capitals: must not become a second record.
    ("DUP", "A", "Priya.Shah@Northwind.example", "Priya", "Shah", "Northwind Example", "51-200", "Head of Operations", "Following up: we want to automate lead follow-up", "now"),
]


def leads() -> list[dict]:
    """Form payloads in the P01 data-contract shape, with the case id and expected grade."""
    return [
        {"case": case, "expected_tier": tier, **dict(zip(FIELDS, values)), "source": "seed", "is_demo": "true"}
        for case, tier, *values in PEOPLE
    ]


def write_expected(path: Path = OUT) -> None:
    with path.open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["case", "email", "expected_tier"])
        writer.writerows([l["case"], l["email"], l["expected_tier"]] for l in leads())


if __name__ == "__main__":
    write_expected()
    print(f"Wrote {len(PEOPLE)} rows to {OUT.name}")
