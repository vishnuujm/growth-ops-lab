import re
from pathlib import Path

PAGES = (Path(__file__).parent.parent / "webflow" / "PAGES.md").read_text()


def test_seo_lengths():
    rows = re.findall(r"^\| (?:Home|Contact) \| `[^`]+` \| (.+?) \| (.+?) \|$", PAGES, re.M)
    assert len(rows) == 2
    for title, description in rows:
        assert len(title) <= 60, title
        assert len(description) <= 155, description


def test_form_fields_match_data_contract():
    fields = re.findall(r"^\| `(\w+)` \|", PAGES, re.M)
    assert fields == ["email", "first_name", "company", "role", "company_size", "use_case", "timeline"]
