"""End-to-end smoke test for brainstorming."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True,
    )


def test_help_runs_for_every_script():
    for s in ("init_brainstorm.py", "write_brainstorm.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed"
        assert "usage:" in result.stdout.lower()


def test_full_pipeline(tmp_path, valid_payload):
    root = tmp_path / "brainstorms"

    init = _run("init_brainstorm.py", "--topic", valid_payload["topic"], "--brainstorms-root", str(root))
    assert init.returncode == 0
    target = init.stdout.strip()

    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")

    write = _run("write_brainstorm.py", "--payload", str(payload_file), "--out", target)
    assert write.returncode == 0, write.stderr

    validate = _run("validate_output.py", "--file", target)
    assert validate.returncode == 0, validate.stderr
