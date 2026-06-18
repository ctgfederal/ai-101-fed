"""End-to-end smoke for agent-delegation.

Pipeline: validate payload → render prompt → validate rendered file →
run check_collisions on a 2-payload set.
"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(name, *args, stdin=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        input=stdin, capture_output=True, text=True,
    )


def test_help_runs_for_every_script():
    for s in ("validate_delegation.py", "render_prompt.py", "check_collisions.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path, valid_payload):
    payload_path = tmp_path / "p.json"
    payload_path.write_text(json.dumps(valid_payload))

    # 1. validate payload
    v = _run("validate_delegation.py", "--payload", str(payload_path))
    assert v.returncode == 0, v.stderr

    # 2. render prompt
    out = tmp_path / "prompt.md"
    r = _run("render_prompt.py", "--payload", str(payload_path), "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert out.exists()

    # 3. validate rendered prompt
    vo = _run("validate_output.py", "--file", str(out))
    assert vo.returncode == 0, vo.stderr


def test_collision_pipeline_safe(tmp_path, safe_payloads):
    payloads_path = tmp_path / "payloads.json"
    payloads_path.write_text(json.dumps(safe_payloads))
    cc = _run("check_collisions.py", "--payloads-json", str(payloads_path))
    assert cc.returncode == 0
    data = json.loads(cc.stdout)
    assert data["safe"] is True


def test_collision_pipeline_unsafe(tmp_path, colliding_payloads):
    payloads_path = tmp_path / "payloads.json"
    payloads_path.write_text(json.dumps(colliding_payloads))
    cc = _run("check_collisions.py", "--payloads-json", str(payloads_path))
    assert cc.returncode == 0
    data = json.loads(cc.stdout)
    assert data["safe"] is False
    assert len(data["collisions"]) >= 1
