"""End-to-end smoke test for build-decisions."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(script, *args, stdin_text=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True,
        input=stdin_text,
    )


def test_help_runs_for_every_script():
    for s in ("state_manager.py", "allocate_ids.py", "federal_mandates.py",
              "append_decisions.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"
        assert "usage:" in result.stdout.lower()


def test_full_pipeline(tmp_path, valid_payload):
    builds_root = tmp_path / "builds"
    log_path = tmp_path / "decisions-log.md"

    # init state
    init = _run("state_manager.py", "init", "--feature", "feature-search",
                "--builds-root", str(builds_root))
    assert init.returncode == 0

    # allocate ids — empty log → D-001..D-005
    alloc = _run("allocate_ids.py", "--log", str(log_path), "--count", "5")
    assert alloc.returncode == 0
    assert alloc.stdout.strip() == "D-001 D-002 D-003 D-004 D-005"

    # append
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_payload))
    appended = _run("append_decisions.py", "--payload", str(payload_file), "--log", str(log_path))
    assert appended.returncode == 0, appended.stderr

    # validate
    validate = _run("validate_output.py", "--log", str(log_path), "--feature", "Feature Search")
    assert validate.returncode == 0, validate.stderr

    # next allocation continues from max
    alloc2 = _run("allocate_ids.py", "--log", str(log_path), "--count", "2")
    assert alloc2.stdout.strip() == "D-006 D-007"
