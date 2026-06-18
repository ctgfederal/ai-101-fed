"""End-to-end smoke for spec-prd-generator."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(s, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / s), *args], capture_output=True, text=True)


def test_help_runs_for_every_script():
    for s in ("init_prd.py", "allocate_req_ids.py", "write_prd.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed"


def test_full_pipeline(tmp_path, valid_payload):
    specs = tmp_path / "specs"

    init = _run("init_prd.py", "--feature", "feature-search", "--specs-root", str(specs))
    assert init.returncode == 0
    target = init.stdout.strip()

    alloc = _run("allocate_req_ids.py", "--specs-root", str(specs), "--count", "2")
    assert alloc.returncode == 0
    assert alloc.stdout.strip() == "REQ-001 REQ-002"

    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    write = _run("write_prd.py", "--payload", str(p), "--out", target)
    assert write.returncode == 0, write.stderr

    validate = _run("validate_output.py", "--file", target)
    assert validate.returncode == 0, validate.stderr
