"""End-to-end smoke test for plan-deepener."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(script, *args, stdin_text=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, input=stdin_text,
    )


def test_help_runs_for_every_script():
    for s in ("parse_target.py", "match_skills.py", "merge_research.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed"
        assert "usage:" in result.stdout.lower()


def test_full_pipeline(tmp_path, sample_target_md, sample_findings, fake_skills_root):
    target = tmp_path / "target.md"
    target.write_text(sample_target_md, encoding="utf-8")

    # parse
    parse = _run("parse_target.py", "--file", str(target))
    assert parse.returncode == 0
    parsed = json.loads(parse.stdout)
    assert "postgres" in parsed["technologies"]

    # match skills using technologies as keywords
    match = _run("match_skills.py", "--skills-root", str(fake_skills_root),
                 stdin_text=json.dumps(parsed["technologies"]))
    assert match.returncode == 0

    # merge fixture findings
    findings_file = tmp_path / "findings.json"
    findings_file.write_text(json.dumps(sample_findings))
    merge = _run("merge_research.py", "--target", str(target), "--findings-json", str(findings_file))
    assert merge.returncode == 0

    # validate
    validate = _run("validate_output.py", "--target", str(target))
    assert validate.returncode == 0, validate.stderr

    # deepened doc has insights blocks
    text = target.read_text()
    assert "## Deepening Summary" in text
    assert text.count("### Research Insights") == 2  # both sections deepened
