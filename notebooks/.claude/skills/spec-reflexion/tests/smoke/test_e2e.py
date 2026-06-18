"""End-to-end smoke for spec-reflexion.

Walks the full pipeline:
  1. extract_learnings.py on a sample README
  2. classify_learning.py on each global candidate
  3. promote_to_memory.py for the global ones
  4. validate_output.py on each written memory file
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(script, *args, stdin: str | None = None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        input=stdin,
    )


def test_help_runs_for_every_script():
    for s in (
        "extract_learnings.py",
        "classify_learning.py",
        "promote_to_memory.py",
        "validate_output.py",
    ):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path, sample_readme):
    readme = tmp_path / "README.md"
    readme.write_text(sample_readme)

    extract = _run("extract_learnings.py", "--readme", str(readme))
    assert extract.returncode == 0, extract.stderr
    items = json.loads(extract.stdout)
    globals_ = [i for i in items if i["scope"] == "global"]
    assert globals_, "expected at least one global candidate"

    memory_root = tmp_path / "memory"
    memory_root.mkdir()

    written: list[Path] = []
    for idx, item in enumerate(globals_):
        cls = _run("classify_learning.py", stdin=item["text"])
        assert cls.returncode == 0
        scope = cls.stdout.strip()
        assert scope in {"local", "global"}

        promote = _run(
            "promote_to_memory.py",
            "--text", item["text"],
            "--type", "user",
            "--name", f"smoke_{idx}",
            "--memory-root", str(memory_root),
        )
        assert promote.returncode == 0, promote.stderr
        out_path = Path(promote.stdout.strip())
        assert out_path.exists()
        written.append(out_path)

    for p in written:
        validate = _run("validate_output.py", "--file", str(p))
        assert validate.returncode == 0, validate.stderr

    index = (memory_root / "MEMORY.md").read_text()
    for p in written:
        assert p.name in index


def test_pipeline_handles_empty_readme(tmp_path, empty_readme):
    readme = tmp_path / "README.md"
    readme.write_text(empty_readme)
    extract = _run("extract_learnings.py", "--readme", str(readme))
    assert extract.returncode == 0
    items = json.loads(extract.stdout)
    assert items == []
