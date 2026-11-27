import importlib.util
from pathlib import Path

from dotenv import dotenv_values

spec = importlib.util.spec_from_file_location("set_env", Path(__file__).parent.parent / "scripts" / "set_env.py")
set_env = importlib.util.module_from_spec(spec)
spec.loader.exec_module(set_env)

SAMPLE = [
    "# --- Supabase ---",
    "SUPABASE_URL=",
    "SUPABASE_ANON_KEY=                 # publishable key",
    "BQ_LOCATION=US                     # MUST be US",
]


def parse(lines, tmp_path):
    f = tmp_path / ".env"
    f.write_text("\n".join(lines) + "\n")
    return dotenv_values(f)


def test_fills_empty_value_and_keeps_comment(tmp_path):
    out = set_env.set_line(list(SAMPLE), "SUPABASE_ANON_KEY", "sb_publishable_abc")
    assert "# publishable key" in out[2]
    assert parse(out, tmp_path)["SUPABASE_ANON_KEY"] == "sb_publishable_abc"


def test_replaces_existing_value(tmp_path):
    out = set_env.set_line(list(SAMPLE), "BQ_LOCATION", "EU")
    assert parse(out, tmp_path)["BQ_LOCATION"] == "EU"
    assert len(out) == len(SAMPLE)


def test_appends_unknown_variable(tmp_path):
    out = set_env.set_line(list(SAMPLE), "NEW_VAR", "x")
    assert parse(out, tmp_path)["NEW_VAR"] == "x"


def test_value_with_hash_or_space_is_quoted(tmp_path):
    out = set_env.set_line(list(SAMPLE), "SUPABASE_URL", "a b#c")
    assert parse(out, tmp_path)["SUPABASE_URL"] == "a b#c"


def test_mask_hides_middle():
    masked = set_env.mask("sb_secret_1234567890abcdef")
    assert "1234567890" not in masked
    assert masked.startswith("sb_s")
