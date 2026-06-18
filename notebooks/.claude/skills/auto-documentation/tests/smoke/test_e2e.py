"""End-to-end smoke test for auto-documentation.

Runs the full pipeline against fixtures in a temp docs/auto/ root:
  categorize -> dedupe -> write_doc -> validate_output
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
    for s in ("categorize.py", "dedupe.py", "write_doc.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help exited {result.returncode}"
        assert "usage:" in result.stdout.lower()


def test_full_pipeline(tmp_path, valid_payload):
    docs_root = tmp_path / "auto"
    docs_root.mkdir()

    # 1. categorize the underlying insight (sanity check)
    cat_result = _run("categorize.py", "--text", valid_payload["title"])
    assert cat_result.returncode == 0
    # Whatever the heuristic decides should be a canonical category.
    assert cat_result.stdout.strip() in {
        "business-rule", "technical-pattern", "service-interface", "domain-rule",
    }

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")

    # 2. dedupe (empty archive — should report no duplicates)
    dedupe_result = _run(
        "dedupe.py",
        "--payload", str(payload_file),
        "--docs-root", str(docs_root),
    )
    assert dedupe_result.returncode == 0
    parsed = json.loads(dedupe_result.stdout.strip())
    assert parsed["is_duplicate"] is False

    # 3. write
    write_result = _run(
        "write_doc.py",
        "--payload", str(payload_file),
        "--docs-root", str(docs_root),
    )
    assert write_result.returncode == 0, write_result.stderr
    output_path = Path(write_result.stdout.strip())
    assert output_path.exists()
    assert output_path.parent.name == valid_payload["category"]

    # 4. validate
    val_result = _run("validate_output.py", "--file", str(output_path))
    assert val_result.returncode == 0, val_result.stderr


def test_dedupe_detects_after_write(tmp_path, valid_payload):
    docs_root = tmp_path / "auto"
    docs_root.mkdir()

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")

    write_result = _run(
        "write_doc.py",
        "--payload", str(payload_file),
        "--docs-root", str(docs_root),
    )
    assert write_result.returncode == 0

    # Now a second run should flag the existing file as a duplicate.
    dedupe_result = _run(
        "dedupe.py",
        "--payload", str(payload_file),
        "--docs-root", str(docs_root),
    )
    assert dedupe_result.returncode == 0
    parsed = json.loads(dedupe_result.stdout.strip())
    assert parsed["is_duplicate"] is True
    assert len(parsed["similar"]) == 1
