"""End-to-end smoke for spec-validation."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(s, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / s), *args],
        capture_output=True,
        text=True,
    )


def test_help_runs_for_every_script():
    for s in ("score_3cs.py", "write_report.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path, good_spec):
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(good_spec)

    score = _run("score_3cs.py", "--file", str(spec_file))
    assert score.returncode == 0, score.stderr
    payload = json.loads(score.stdout)
    assert payload["verdict"] == "PASS"

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload))

    report_file = tmp_path / "report.md"
    write = _run("write_report.py", "--payload", str(payload_file), "--out", str(report_file))
    assert write.returncode == 0, write.stderr
    assert report_file.exists()

    validate = _run("validate_output.py", "--file", str(report_file))
    assert validate.returncode == 0, validate.stderr


def test_full_pipeline_warn(tmp_path, bad_spec):
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(bad_spec)

    score = _run("score_3cs.py", "--file", str(spec_file))
    assert score.returncode == 0
    payload = json.loads(score.stdout)
    assert payload["verdict"] in {"WARN", "FAIL"}
    assert payload["issues"]

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload))
    report_file = tmp_path / "report.md"
    write = _run("write_report.py", "--payload", str(payload_file), "--out", str(report_file))
    assert write.returncode == 0

    validate = _run("validate_output.py", "--file", str(report_file))
    assert validate.returncode == 0, validate.stderr
