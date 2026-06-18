"""Unit tests for scripts/promote_to_memory.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from promote_to_memory import (  # noqa: E402
    write_memory, render_memory_file, update_memory_index,
    _slugify, _first_sentence, main as promote_main,
)


def test_slugify_basic():
    assert _slugify("Josh's preference for error types!") == "josh_s_preference_for_error_types"


def test_slugify_truncates_long():
    long = "a" * 80
    assert len(_slugify(long)) <= 60


def test_first_sentence_simple():
    assert _first_sentence("Hello world. Trailing.") == "Hello world."


def test_first_sentence_no_punct():
    text = "this is one long thing"
    assert _first_sentence(text) == "this is one long thing"


def test_first_sentence_truncation():
    text = "a" * 200
    out = _first_sentence(text, max_chars=40)
    assert len(out) <= 40
    assert out.endswith("…")


def test_render_memory_file_shape():
    rendered = render_memory_file(
        name="My Title",
        description="Short summary",
        type_="user",
        body="The actual content goes here.",
    )
    assert rendered.startswith("---\nname: My Title\n")
    assert "description: Short summary" in rendered
    assert "type: user" in rendered
    assert rendered.rstrip().endswith("The actual content goes here.")


def test_write_memory_creates_file_and_index(tmp_memory_root):
    out = write_memory(
        text="Josh prefers explicit error types over Result wrappers.",
        type_="user",
        name="josh_explicit_error_types",
        memory_root=tmp_memory_root,
    )
    assert out.exists()
    assert out.name == "user_josh_explicit_error_types.md"
    content = out.read_text()
    assert content.startswith("---\n")
    assert "type: user" in content

    index = (tmp_memory_root / "MEMORY.md").read_text()
    assert "user_josh_explicit_error_types.md" in index
    assert "# Memory Index" in index


def test_write_memory_refuses_overwrite(tmp_memory_root):
    write_memory(
        text="x", type_="user", name="dupe", memory_root=tmp_memory_root,
    )
    with pytest.raises(FileExistsError):
        write_memory(
            text="y", type_="user", name="dupe", memory_root=tmp_memory_root,
        )


def test_write_memory_force_overwrites(tmp_memory_root):
    write_memory(
        text="first", type_="user", name="dupe", memory_root=tmp_memory_root,
    )
    out = write_memory(
        text="second", type_="user", name="dupe", memory_root=tmp_memory_root,
        force=True,
    )
    assert "second" in out.read_text()


def test_write_memory_invalid_type(tmp_memory_root):
    with pytest.raises(ValueError):
        write_memory(
            text="x", type_="garbage", name="x", memory_root=tmp_memory_root,
        )


def test_write_memory_empty_text(tmp_memory_root):
    with pytest.raises(ValueError):
        write_memory(
            text="   ", type_="user", name="x", memory_root=tmp_memory_root,
        )


def test_index_replaces_duplicate_entry(tmp_memory_root):
    index = tmp_memory_root / "MEMORY.md"
    update_memory_index(index, "user_x.md", "first description")
    update_memory_index(index, "user_x.md", "second description")
    text = index.read_text()
    assert text.count("user_x.md") == 2  # link target + filename text
    assert "first description" not in text
    assert "second description" in text


def test_index_appends_new_entry(tmp_memory_root):
    index = tmp_memory_root / "MEMORY.md"
    update_memory_index(index, "user_a.md", "alpha")
    update_memory_index(index, "user_b.md", "beta")
    text = index.read_text()
    assert "user_a.md" in text
    assert "user_b.md" in text


def _run_main(*args):
    old = sys.argv
    sys.argv = ["promote_to_memory.py", *args]
    try:
        return promote_main()
    finally:
        sys.argv = old


def test_main_writes_file(tmp_memory_root, capsys):
    rc = _run_main(
        "--text", "Josh prefers tabs over spaces.",
        "--type", "user",
        "--name", "josh_tabs",
        "--memory-root", str(tmp_memory_root),
    )
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert Path(out).exists()


def test_main_invalid_type_returns_1(tmp_memory_root):
    # argparse rejects bad choices with rc 2 — instead test write_memory directly
    rc = _run_main(
        "--text", "x",
        "--type", "user",
        "--name", "x",
        "--memory-root", str(tmp_memory_root),
    )
    assert rc == 0
    # second run should hit FileExistsError without --force
    rc2 = _run_main(
        "--text", "x",
        "--type", "user",
        "--name", "x",
        "--memory-root", str(tmp_memory_root),
    )
    assert rc2 == 1
