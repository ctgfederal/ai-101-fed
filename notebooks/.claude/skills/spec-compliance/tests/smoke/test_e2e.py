"""End-to-end smoke for spec-compliance."""
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
    for s in ("parse_spec.py", "check_compliance.py",
              "write_report.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path, sample_prd, sample_sdd, sample_repo):
    prd_file = tmp_path / "PRD.md"
    sdd_file = tmp_path / "SDD.md"
    prd_file.write_text(sample_prd)
    sdd_file.write_text(sample_sdd)

    parsed = _run("parse_spec.py", "--prd", str(prd_file), "--sdd", str(sdd_file))
    assert parsed.returncode == 0, parsed.stderr
    parsed_payload = json.loads(parsed.stdout)
    assert parsed_payload["reqs"] == ["REQ-001", "REQ-002"]

    parsed_file = tmp_path / "parsed.json"
    parsed_file.write_text(parsed.stdout)

    checked = _run("check_compliance.py",
                   "--spec-json", str(parsed_file),
                   "--repo-root", str(sample_repo))
    assert checked.returncode == 0, checked.stderr
    payload = json.loads(checked.stdout)
    assert payload["status"] == "partial"

    payload_file = tmp_path / "payload.json"
    payload_file.write_text(checked.stdout)

    report_file = tmp_path / "REPORT.md"
    write = _run("write_report.py",
                 "--payload", str(payload_file),
                 "--out", str(report_file))
    assert write.returncode == 0, write.stderr
    assert report_file.exists()

    validate = _run("validate_output.py", "--file", str(report_file))
    assert validate.returncode == 0, validate.stderr

    # also validate with --spec-json (required-coverage check)
    validate2 = _run("validate_output.py",
                     "--file", str(report_file),
                     "--spec-json", str(parsed_file))
    assert validate2.returncode == 0, validate2.stderr


def test_fully_compliant_repo(tmp_path, sample_prd, sample_sdd):
    """If both components exist and both REQs are referenced, status is compliant."""
    prd_file = tmp_path / "PRD.md"
    sdd_file = tmp_path / "SDD.md"
    prd_file.write_text(sample_prd)
    sdd_file.write_text(sample_sdd)

    repo = tmp_path / "repo"
    (repo / "src" / "search").mkdir(parents=True)
    (repo / "src" / "search" / "service.py").write_text("# REQ-001\n")
    (repo / "src" / "search" / "ranking.py").write_text("# REQ-002\n")

    parsed = _run("parse_spec.py", "--prd", str(prd_file), "--sdd", str(sdd_file))
    parsed_file = tmp_path / "parsed.json"
    parsed_file.write_text(parsed.stdout)

    checked = _run("check_compliance.py",
                   "--spec-json", str(parsed_file),
                   "--repo-root", str(repo))
    payload = json.loads(checked.stdout)
    assert payload["status"] == "compliant"
    assert payload["summary"]["deviation_count"] == 0


def test_non_compliant_repo(tmp_path, sample_prd, sample_sdd):
    """Empty repo — nothing implemented, nothing referenced."""
    prd_file = tmp_path / "PRD.md"
    sdd_file = tmp_path / "SDD.md"
    prd_file.write_text(sample_prd)
    sdd_file.write_text(sample_sdd)

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# nothing here")

    parsed = _run("parse_spec.py", "--prd", str(prd_file), "--sdd", str(sdd_file))
    parsed_file = tmp_path / "parsed.json"
    parsed_file.write_text(parsed.stdout)

    checked = _run("check_compliance.py",
                   "--spec-json", str(parsed_file),
                   "--repo-root", str(repo))
    payload = json.loads(checked.stdout)
    assert payload["status"] == "non-compliant"
