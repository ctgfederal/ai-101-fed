"""End-to-end smoke."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(s, *a):
    return subprocess.run([sys.executable, str(SCRIPTS / s), *a], capture_output=True, text=True)


def test_help():
    for s in ("init_plan.py", "extract_ids.py", "allocate_task_ids.py", "write_plan.py", "validate_output.py"):
        r = _run(s, "--help")
        assert r.returncode == 0


def test_pipeline(tmp_path, valid_payload, fake_prd, fake_sdd):
    init = _run("init_plan.py", "--feature", "feature-search", "--specs-root", str(tmp_path / "specs"))
    assert init.returncode == 0
    target = init.stdout.strip()

    alloc = _run("allocate_task_ids.py", "--specs-root", str(tmp_path / "specs"), "--count", "2")
    assert alloc.stdout.strip() == "T-001 T-002"

    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    write = _run("write_plan.py", "--payload", str(p), "--out", target,
                 "--prd", str(fake_prd), "--sdd", str(fake_sdd))
    assert write.returncode == 0, write.stderr

    val = _run("validate_output.py", "--file", target, "--prd", str(fake_prd), "--sdd", str(fake_sdd))
    assert val.returncode == 0, val.stderr
