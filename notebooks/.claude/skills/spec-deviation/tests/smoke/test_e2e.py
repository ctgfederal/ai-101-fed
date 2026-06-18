"""End-to-end smoke for spec-deviation."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(s, *args, stdin=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / s), *args],
        capture_output=True,
        text=True,
        input=stdin,
    )


def test_help_runs_for_every_script():
    for s in (
        "validate_deviation.py",
        "allocate_deviation_id.py",
        "append_deviation.py",
        "validate_output.py",
    ):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path, valid_payload, clean_sdd):
    # 1. allocate an ID against an empty specs root → DEV-001
    specs_root = tmp_path / "specs"
    specs_root.mkdir()
    alloc = _run("allocate_deviation_id.py", "--specs-root", str(specs_root), "--count", "1")
    assert alloc.returncode == 0
    dev_id = alloc.stdout.strip()
    assert dev_id == "DEV-001"

    # 2. validate the payload
    valid_payload["deviation_id"] = dev_id
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload))
    val = _run("validate_deviation.py", "--payload", str(payload_file))
    assert val.returncode == 0, val.stderr

    # 3. append to a fresh SDD
    sdd_file = tmp_path / "SDD.md"
    sdd_file.write_text(clean_sdd)
    ap = _run("append_deviation.py", "--payload", str(payload_file), "--sdd", str(sdd_file))
    assert ap.returncode == 0, ap.stderr

    # 4. validate the resulting SDD
    vo = _run("validate_output.py", "--sdd", str(sdd_file))
    assert vo.returncode == 0, vo.stderr

    # 5. allocate the next ID — should jump because DEV-001 is now in the SDD
    specs_dir = specs_root / "feature-x"
    specs_dir.mkdir()
    (specs_dir / "SDD.md").write_text(sdd_file.read_text())
    alloc2 = _run("allocate_deviation_id.py", "--specs-root", str(specs_root), "--count", "1")
    assert alloc2.returncode == 0
    assert alloc2.stdout.strip() == "DEV-002"


def test_pipeline_refuses_invalid_payload(tmp_path, bad_payload, clean_sdd):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(clean_sdd)
    p = tmp_path / "p.json"
    p.write_text(json.dumps(bad_payload))
    val = _run("validate_deviation.py", "--payload", str(p))
    assert val.returncode == 1
    ap = _run("append_deviation.py", "--payload", str(p), "--sdd", str(sdd))
    assert ap.returncode == 1
    # SDD should be untouched
    assert sdd.read_text() == clean_sdd


def test_pipeline_force_overwrite(tmp_path, valid_payload, clean_sdd):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(clean_sdd)
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    # first append
    ap1 = _run("append_deviation.py", "--payload", str(p), "--sdd", str(sdd))
    assert ap1.returncode == 0
    # second append with same DEV-NNN should refuse
    ap2 = _run("append_deviation.py", "--payload", str(p), "--sdd", str(sdd))
    assert ap2.returncode == 1
    # third with --force should succeed and result in still-one block
    valid_payload["status"] = "approved"
    p.write_text(json.dumps(valid_payload))
    ap3 = _run("append_deviation.py", "--payload", str(p), "--sdd", str(sdd), "--force")
    assert ap3.returncode == 0
    body = sdd.read_text()
    assert body.count("### DEV-001") == 1
    assert "Status**: approved" in body
    # validate the final state
    vo = _run("validate_output.py", "--sdd", str(sdd))
    assert vo.returncode == 0, vo.stderr
