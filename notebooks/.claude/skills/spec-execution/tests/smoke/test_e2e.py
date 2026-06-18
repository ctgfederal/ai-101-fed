"""End-to-end smoke for spec-execution."""
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
    for s in ("state_manager.py", "next_task.py", "record_tdd_step.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path):
    # Set up specs root with one feature folder containing PLAN.md.
    specs_root = tmp_path / "specs"
    feature = "feat-x"
    fdir = specs_root / feature
    fdir.mkdir(parents=True)
    plan_text = (
        "# PLAN — feat-x\n"
        "## Phase 1\n"
        "- [ ] **T-001**: First task\n"
        "- [ ] **T-002**: Second task\n"
    )
    (fdir / "PLAN.md").write_text(plan_text)

    # init
    init = _run("state_manager.py", "init", "--feature", feature, "--specs-root", str(specs_root))
    assert init.returncode == 0, init.stderr
    state_file = fdir / "execution-state.json"
    assert state_file.exists()

    # next_task → T-001
    nxt = _run("next_task.py", "--feature", feature, "--specs-root", str(specs_root))
    assert nxt.returncode == 0
    payload = json.loads(nxt.stdout)
    assert payload["id"] == "T-001"

    # record red → fail
    red = _run(
        "record_tdd_step.py",
        "--feature", feature, "--specs-root", str(specs_root),
        "--task-id", "T-001", "--step", "red", "--result", "fail",
        "--note", "no implementation",
    )
    assert red.returncode == 0, red.stderr

    # record green → pass
    green = _run(
        "record_tdd_step.py",
        "--feature", feature, "--specs-root", str(specs_root),
        "--task-id", "T-001", "--step", "green", "--result", "pass",
    )
    assert green.returncode == 0, green.stderr

    # mark T-001 done via update
    patch_file = tmp_path / "patch.json"
    patch_file.write_text(json.dumps({
        "current_task": "T-002",
        "tasks": {"T-001": {"status": "done"}},
    }))
    upd = _run(
        "state_manager.py", "update",
        "--feature", feature, "--specs-root", str(specs_root),
        "--patch", str(patch_file),
    )
    assert upd.returncode == 0, upd.stderr

    # next_task → T-002 (T-001 is done, T-002 had no deps)
    nxt2 = _run("next_task.py", "--feature", feature, "--specs-root", str(specs_root))
    assert nxt2.returncode == 0
    payload2 = json.loads(nxt2.stdout)
    assert payload2["id"] == "T-002"

    # validate state
    validate = _run(
        "validate_output.py",
        "--file", str(state_file),
        "--plan", str(fdir / "PLAN.md"),
    )
    assert validate.returncode == 0, validate.stderr


def test_invalid_status_rejected_e2e(tmp_path):
    specs_root = tmp_path / "specs"
    feature = "f"
    fdir = specs_root / feature
    fdir.mkdir(parents=True)
    (fdir / "PLAN.md").write_text("- [ ] T-001: only task\n")
    _run("state_manager.py", "init", "--feature", feature, "--specs-root", str(specs_root))
    bad_patch = tmp_path / "bad.json"
    bad_patch.write_text(json.dumps({"tasks": {"T-001": {"status": "wat"}}}))
    out = _run(
        "state_manager.py", "update",
        "--feature", feature, "--specs-root", str(specs_root),
        "--patch", str(bad_patch),
    )
    assert out.returncode == 1
