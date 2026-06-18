"""Unit tests for scripts/extract_learnings.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from extract_learnings import extract, main as extract_main  # noqa: E402


def test_extract_local_and_global(sample_readme):
    items = extract(sample_readme)
    assert len(items) >= 4
    locals_ = [i for i in items if i["scope"] == "local"]
    globals_ = [i for i in items if i["scope"] == "global"]
    assert locals_, "should detect local learnings"
    assert globals_, "should detect global learnings"
    assert any("Josh prefers explicit error types" in i["text"] for i in globals_)
    assert any("REQ-104" in i["text"] for i in locals_)


def test_extract_phase_detection(sample_readme):
    items = extract(sample_readme)
    phases = {i["phase"] for i in items}
    assert "T-005" in phases


def test_extract_strips_checkboxes(sample_readme):
    items = extract(sample_readme)
    for i in items:
        assert not i["text"].startswith("[ ]")
        assert not i["text"].startswith("[x]")


def test_extract_empty_readme(empty_readme):
    items = extract(empty_readme)
    assert items == []


def test_extract_handles_what_worked_section():
    text = """# README

## Learnings

### Phase T-001

**What Worked**
- Used a hash map; saved 200ms.
- Tail-call optimisation kept stack flat.
"""
    items = extract(text)
    assert len(items) >= 1
    assert all(i["scope"] == "local" for i in items)


def test_extract_for_memorize_section_only_global():
    text = """# README

## Learnings

### For /memorize (Global Learnings)

- [ ] React 19 useOptimistic is great for forms → type: `reference`
"""
    items = extract(text)
    assert len(items) == 1
    assert items[0]["scope"] == "global"


def test_extract_no_section_no_items():
    text = "# Just a heading\n\n- bullet outside any learnings section\n"
    items = extract(text)
    assert items == []


def _run(*args):
    old = sys.argv
    sys.argv = ["extract_learnings.py", *args]
    try:
        return extract_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--readme", str(tmp_path / "nope.md"))
    assert rc == 1


def test_main_emits_json(tmp_path, sample_readme, capsys):
    f = tmp_path / "README.md"
    f.write_text(sample_readme)
    rc = _run("--readme", str(f))
    assert rc == 0
    out = capsys.readouterr().out
    items = json.loads(out)
    assert isinstance(items, list)
    assert len(items) >= 4
