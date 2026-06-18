"""Unit tests for scripts/generate_slug.py."""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from generate_slug import slugify, parse_date, build_filename, main as gs_main


# --- slugify ---

def test_slugify_basic():
    assert slugify("N+1 query in brief generation") == "n-1-query-in-brief-generation"


def test_slugify_collapses_punctuation():
    assert slugify("Foo!! Bar?? -- Baz") == "foo-bar-baz"


def test_slugify_unicode():
    # café → cafe
    assert slugify("Café crash") == "cafe-crash"


def test_slugify_truncates():
    long = "a" * 100
    assert len(slugify(long)) == 60


def test_slugify_empty_raises():
    with pytest.raises(ValueError):
        slugify("")


def test_slugify_only_punctuation_raises():
    with pytest.raises(ValueError):
        slugify("!!!---???")


def test_slugify_strips_trailing_hyphen():
    out = slugify("Trailing punctuation!!")
    assert not out.endswith("-")


# --- parse_date ---

def test_parse_date_happy():
    assert parse_date("2026-02-14") == date(2026, 2, 14)


def test_parse_date_invalid():
    with pytest.raises(ValueError):
        parse_date("Feb 14")


# --- build_filename ---

def test_build_filename():
    assert build_filename("Foo Bar", date(2026, 2, 14)) == "2026-02-14-foo-bar.md"


# --- main entry point ---

def _run_main(argv):
    old = sys.argv
    sys.argv = ["generate_slug.py"] + argv
    try:
        return gs_main()
    finally:
        sys.argv = old


def test_main_happy(capsys):
    rc = _run_main(["--title", "Hello World", "--date", "2026-02-14"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "2026-02-14-hello-world.md"


def test_main_default_date(capsys):
    rc = _run_main(["--title", "Hello"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out.endswith("-hello.md")
    assert out.startswith(date.today().isoformat())


def test_main_invalid_date(capsys):
    rc = _run_main(["--title", "Hello", "--date", "not-a-date"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "YYYY-MM-DD" in err


def test_main_empty_title(capsys):
    rc = _run_main(["--title", "   "])
    assert rc == 1
