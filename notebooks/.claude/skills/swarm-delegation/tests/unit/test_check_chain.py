"""Unit tests for scripts/check_chain.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_chain import check, detect_cycle, detect_pattern, main as cc_main


def test_check_valid_chain(valid_chain):
    result = check(valid_chain["chain"])
    assert result["valid"] is True
    assert result["pattern"] == "linear"
    assert result["issues"] == []


def test_check_cyclic(cyclic_chain):
    result = check(cyclic_chain["chain"])
    assert result["valid"] is False
    assert any("cycle" in i.lower() for i in result["issues"])


def test_check_self_handoff():
    chain = [
        {
            "from_agent": "alpha",
            "to_agent": "alpha",
            "task": "self",
            "context_files": [],
            "success_criteria": ["x"],
            "return_format": "x",
            "output_type": "x",
            "expected_input_type": "x",
        }
    ]
    result = check(chain)
    assert result["valid"] is False
    assert any("self-handoff" in i for i in result["issues"])


def test_check_type_mismatch(mismatched_chain):
    result = check(mismatched_chain["chain"])
    assert result["valid"] is False
    assert any("type mismatch" in i for i in result["issues"])


def test_check_empty():
    result = check([])
    assert result["valid"] is False
    assert any("empty" in i for i in result["issues"])


def test_check_not_a_list():
    result = check("not a list")
    assert result["valid"] is False


def test_check_missing_from():
    chain = [{"to_agent": "beta", "task": "t"}]
    result = check(chain)
    assert result["valid"] is False
    assert any("from_agent" in i for i in result["issues"])


def test_check_missing_to():
    chain = [{"from_agent": "alpha", "task": "t"}]
    result = check(chain)
    assert result["valid"] is False
    assert any("to_agent" in i for i in result["issues"])


def test_detect_cycle_simple():
    edges = [("a", "b"), ("b", "a")]
    nodes = detect_cycle(edges)
    assert "a" in nodes and "b" in nodes


def test_detect_cycle_self():
    edges = [("a", "a")]
    nodes = detect_cycle(edges)
    assert "a" in nodes


def test_detect_cycle_none():
    edges = [("a", "b"), ("b", "c"), ("c", "d")]
    assert detect_cycle(edges) == []


def test_detect_pattern_linear():
    chain = [
        {"from_agent": "a", "to_agent": "b"},
        {"from_agent": "b", "to_agent": "c"},
    ]
    assert detect_pattern(chain) == "linear"


def test_detect_pattern_fan_out():
    chain = [
        {"from_agent": "orch", "to_agent": "b"},
        {"from_agent": "orch", "to_agent": "c"},
    ]
    assert detect_pattern(chain) == "fan-out"


def test_detect_pattern_fan_in():
    chain = [
        {"from_agent": "b", "to_agent": "merger"},
        {"from_agent": "c", "to_agent": "merger"},
    ]
    assert detect_pattern(chain) == "fan-in"


def test_detect_pattern_mixed():
    chain = [
        {"from_agent": "orch", "to_agent": "b"},
        {"from_agent": "orch", "to_agent": "c"},
        {"from_agent": "b", "to_agent": "merger"},
        {"from_agent": "c", "to_agent": "merger"},
    ]
    assert detect_pattern(chain) == "mixed"


def test_check_missing_output_type():
    chain = [
        {
            "from_agent": "a",
            "to_agent": "b",
            "task": "t",
            "context_files": [],
            "success_criteria": ["x"],
            "return_format": "x",
            # output_type missing
            "expected_input_type": "task-spec",
        },
        {
            "from_agent": "b",
            "to_agent": "c",
            "task": "t2",
            "context_files": [],
            "success_criteria": ["x"],
            "return_format": "x",
            "output_type": "x",
            "expected_input_type": "x",
        },
    ]
    result = check(chain)
    # missing output_type on linear should flag
    assert any("output_type" in i for i in result["issues"])


def _run(*args):
    old = sys.argv
    sys.argv = ["check_chain.py", *args]
    try:
        return cc_main()
    finally:
        sys.argv = old


def test_main_happy(tmp_path, valid_chain):
    f = tmp_path / "c.json"
    f.write_text(json.dumps(valid_chain))
    rc = _run("--chain-json", str(f))
    assert rc == 0


def test_main_cyclic(tmp_path, cyclic_chain):
    f = tmp_path / "c.json"
    f.write_text(json.dumps(cyclic_chain))
    rc = _run("--chain-json", str(f))
    assert rc == 1


def test_main_missing_file(tmp_path):
    rc = _run("--chain-json", str(tmp_path / "nope.json"))
    assert rc == 1


def test_main_invalid_json(tmp_path):
    f = tmp_path / "c.json"
    f.write_text("not json")
    rc = _run("--chain-json", str(f))
    assert rc == 1
