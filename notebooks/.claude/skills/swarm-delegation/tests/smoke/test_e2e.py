"""End-to-end smoke for swarm-delegation."""
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
    for s in (
        "validate_handoff.py",
        "render_handoff.py",
        "check_chain.py",
        "validate_output.py",
    ):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline_single_handoff(tmp_path, valid_handoff):
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_handoff))

    # validate
    val = _run("validate_handoff.py", "--file", str(payload_file))
    assert val.returncode == 0, val.stderr
    body = json.loads(val.stdout)
    assert body["valid"] is True

    # render
    out = tmp_path / "prompt.md"
    rend = _run("render_handoff.py", "--payload", str(payload_file), "--out", str(out))
    assert rend.returncode == 0, rend.stderr
    assert out.exists()

    # validate output
    vo = _run("validate_output.py", "--file", str(out))
    assert vo.returncode == 0, vo.stderr


def test_chain_pipeline(tmp_path, valid_chain):
    chain_file = tmp_path / "chain.json"
    chain_file.write_text(json.dumps(valid_chain))

    cc = _run("check_chain.py", "--chain-json", str(chain_file))
    assert cc.returncode == 0, cc.stderr
    body = json.loads(cc.stdout)
    assert body["valid"] is True
    assert body["pattern"] == "linear"


def test_chain_pipeline_cycle_caught(tmp_path, cyclic_chain):
    chain_file = tmp_path / "chain.json"
    chain_file.write_text(json.dumps(cyclic_chain))

    cc = _run("check_chain.py", "--chain-json", str(chain_file))
    assert cc.returncode == 1
    body = json.loads(cc.stdout)
    assert body["valid"] is False


def test_invalid_handoff_blocks_render(tmp_path, invalid_handoff):
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(invalid_handoff))

    out = tmp_path / "prompt.md"
    rend = _run("render_handoff.py", "--payload", str(payload_file), "--out", str(out))
    assert rend.returncode == 1
    assert not out.exists()
