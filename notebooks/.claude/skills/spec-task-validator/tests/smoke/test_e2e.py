"""End-to-end smoke for spec-task-validator."""
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
    for s in ("parse_tasks.py", "validate_tasks.py", "write_report.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline_pass(tmp_path, good_plan, good_prd, good_sdd):
    plan_file = tmp_path / "PLAN.md"
    plan_file.write_text(good_plan)
    prd_file = tmp_path / "PRD.md"
    prd_file.write_text(good_prd)
    sdd_file = tmp_path / "SDD.md"
    sdd_file.write_text(good_sdd)

    parsed = _run("parse_tasks.py", "--plan", str(plan_file))
    assert parsed.returncode == 0, parsed.stderr
    tasks = json.loads(parsed.stdout)
    assert len(tasks) == 3

    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(json.dumps(tasks))

    validated = _run("validate_tasks.py",
                     "--tasks", str(tasks_file),
                     "--prd", str(prd_file),
                     "--sdd", str(sdd_file),
                     "--plan", str(plan_file))
    assert validated.returncode == 0, validated.stderr
    payload = json.loads(validated.stdout)
    assert payload["verdict"] == "PASS"

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload))

    report_file = tmp_path / "report.md"
    write = _run("write_report.py", "--payload", str(payload_file), "--out", str(report_file))
    assert write.returncode == 0, write.stderr
    assert report_file.exists()

    final = _run("validate_output.py", "--file", str(report_file), "--payload", str(payload_file))
    assert final.returncode == 0, final.stderr


def test_full_pipeline_fail(tmp_path, bad_plan):
    plan_file = tmp_path / "PLAN.md"
    plan_file.write_text(bad_plan)

    parsed = _run("parse_tasks.py", "--plan", str(plan_file))
    assert parsed.returncode == 0
    tasks = json.loads(parsed.stdout)

    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(json.dumps(tasks))

    validated = _run("validate_tasks.py", "--tasks", str(tasks_file))
    assert validated.returncode == 0
    payload = json.loads(validated.stdout)
    assert payload["verdict"] == "FAIL"
    assert payload["summary"]["fail"] >= 1

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload))
    report_file = tmp_path / "report.md"
    write = _run("write_report.py", "--payload", str(payload_file), "--out", str(report_file))
    assert write.returncode == 0

    final = _run("validate_output.py", "--file", str(report_file))
    assert final.returncode == 0, final.stderr
