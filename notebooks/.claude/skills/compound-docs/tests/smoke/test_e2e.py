"""End-to-end smoke test for compound-docs.

Runs the full pipeline against fixtures in a temp solutions/ root:
  validate_frontmatter -> generate_slug -> write_solution -> validate_output
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(script: str, *args: str, **kw):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, **kw,
    )


def test_help_runs_for_every_script():
    """Every script must respond to --help with exit 0."""
    for s in ("validate_frontmatter.py", "generate_slug.py",
              "search_solutions.py", "write_solution.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help exited {result.returncode}"
        assert "usage:" in result.stdout.lower()


def test_full_pipeline(tmp_path, valid_payload):
    solutions_root = tmp_path / "solutions"
    solutions_root.mkdir()

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")

    # write
    write_result = _run(
        "write_solution.py",
        "--payload", str(payload_file),
        "--solutions-root", str(solutions_root),
    )
    assert write_result.returncode == 0, write_result.stderr
    output_path = Path(write_result.stdout.strip())
    assert output_path.exists()
    assert output_path.parent.name == valid_payload["category"]

    # validate
    val_result = _run("validate_output.py", "--file", str(output_path))
    assert val_result.returncode == 0, val_result.stderr


def test_search_finds_written_file(tmp_path, valid_payload):
    solutions_root = tmp_path / "solutions"
    solutions_root.mkdir()

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")

    _run("write_solution.py", "--payload", str(payload_file),
         "--solutions-root", str(solutions_root))

    search_result = _run(
        "search_solutions.py",
        "--solutions-root", str(solutions_root),
        "--module", valid_payload["module"],
    )
    assert search_result.returncode == 0
    assert valid_payload["module"] in search_result.stdout
