"""End-to-end smoke for spec-requirement-tracer."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(script: str, *args: str):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
    )


def test_help_runs_for_every_script():
    for s in (
        "extract_ids.py",
        "build_matrix.py",
        "write_matrix.py",
        "validate_output.py",
    ):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path, fake_prd, fake_sdd, fake_plan, fake_code_root):
    # 1. Extract IDs
    extract = _run(
        "extract_ids.py",
        "--prd", str(fake_prd),
        "--sdd", str(fake_sdd),
        "--plan", str(fake_plan),
        "--code-root", str(fake_code_root),
    )
    assert extract.returncode == 0, extract.stderr
    ids_payload = json.loads(extract.stdout)
    assert ids_payload["prd_reqs"] == ["REQ-001", "REQ-002", "REQ-003"]

    ids_file = tmp_path / "ids.json"
    ids_file.write_text(json.dumps(ids_payload))

    # 2. Build matrix
    build = _run(
        "build_matrix.py",
        "--ids-json", str(ids_file),
        "--feature", "feature-search",
    )
    assert build.returncode == 0, build.stderr
    matrix_payload = json.loads(build.stdout)
    assert matrix_payload["feature"] == "feature-search"
    by_req = {r["req"]: r for r in matrix_payload["rows"]}
    assert by_req["REQ-001"]["status"] == "covered"
    assert by_req["REQ-002"]["status"] == "partial"
    assert by_req["REQ-003"]["status"] == "uncovered"

    matrix_file = tmp_path / "matrix.json"
    matrix_file.write_text(json.dumps(matrix_payload))

    # 3. Write report
    out = tmp_path / "TRACEABILITY.md"
    write = _run(
        "write_matrix.py",
        "--payload", str(matrix_file),
        "--out", str(out),
    )
    assert write.returncode == 0, write.stderr
    assert out.exists()
    body = out.read_text(encoding="utf-8")
    assert "REQ-001" in body
    assert "{{" not in body

    # 4. Validate report
    validate = _run(
        "validate_output.py",
        "--file", str(out),
        "--prd", str(fake_prd),
    )
    assert validate.returncode == 0, validate.stderr
