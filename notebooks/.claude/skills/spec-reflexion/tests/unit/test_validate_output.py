"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import (  # noqa: E402
    validate_memory_file, validate_index, main as validate_main,
)


def _write_memory(tmp, name, body=None, missing_field=None, bad_type=False, empty_body=False):
    """Helper to write a sample memory file."""
    name_field = "Sample Title" if missing_field != "name" else ""
    desc_field = "Sample description" if missing_field != "description" else ""
    type_field = ("garbage" if bad_type else "user") if missing_field != "type" else ""
    parts = ["---"]
    if missing_field != "name":
        parts.append(f"name: {name_field}")
    if missing_field != "description":
        parts.append(f"description: {desc_field}")
    if missing_field != "type":
        parts.append(f"type: {type_field}")
    parts.append("---")
    parts.append("")
    parts.append("" if empty_body else (body or "Body text."))
    f = tmp / name
    f.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return f


def _write_index(tmp, filename, description="ok"):
    idx = tmp / "MEMORY.md"
    idx.write_text(
        f"# Memory Index\n\n- [{filename}]({filename}) - {description}\n",
        encoding="utf-8",
    )
    return idx


def test_validate_happy_path(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md")
    _write_index(tmp_path, "user_sample.md")
    assert validate_memory_file(f) == []
    assert validate_index(f) == []


def test_validate_missing_name(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md", missing_field="name")
    errs = validate_memory_file(f)
    assert any("name" in e for e in errs)


def test_validate_missing_description(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md", missing_field="description")
    errs = validate_memory_file(f)
    assert any("description" in e for e in errs)


def test_validate_missing_type(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md", missing_field="type")
    errs = validate_memory_file(f)
    assert any("type" in e for e in errs)


def test_validate_bad_type(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md", bad_type=True)
    errs = validate_memory_file(f)
    assert any("type must be" in e for e in errs)


def test_validate_empty_body(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md", empty_body=True)
    errs = validate_memory_file(f)
    assert any("body" in e.lower() for e in errs)


def test_validate_no_frontmatter(tmp_path):
    f = tmp_path / "x.md"
    f.write_text("just a plain file", encoding="utf-8")
    errs = validate_memory_file(f)
    assert errs


def test_validate_index_missing_file(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md")
    # do not create MEMORY.md
    errs = validate_index(f)
    assert any("MEMORY.md" in e for e in errs)


def test_validate_index_missing_entry(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md")
    (tmp_path / "MEMORY.md").write_text("# Memory Index\n\n", encoding="utf-8")
    errs = validate_index(f)
    assert any("missing index entry" in e for e in errs)


def test_validate_index_empty_description(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md")
    (tmp_path / "MEMORY.md").write_text(
        "# Memory Index\n\n- [user_sample.md](user_sample.md) - \n",
        encoding="utf-8",
    )
    errs = validate_index(f)
    assert any("empty description" in e for e in errs)


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return validate_main()
    finally:
        sys.argv = old


def test_main_pass(tmp_path, capsys):
    f = _write_memory(tmp_path, "user_sample.md")
    _write_index(tmp_path, "user_sample.md")
    rc = _run("--file", str(f))
    assert rc == 0
    assert capsys.readouterr().out.strip() == "OK"


def test_main_fail(tmp_path):
    f = _write_memory(tmp_path, "user_sample.md", missing_field="name")
    _write_index(tmp_path, "user_sample.md")
    rc = _run("--file", str(f))
    assert rc == 1


def test_main_missing_file(tmp_path):
    rc = _run("--file", str(tmp_path / "nope.md"))
    assert rc == 1
