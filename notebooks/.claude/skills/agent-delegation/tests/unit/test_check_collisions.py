"""Unit tests for scripts/check_collisions.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_collisions import (
    normalize, paths_collide, find_collisions, main as cc_main,
)


def test_normalize_strips_trailing_slash():
    assert normalize("src/auth/") == ("src/auth", True)


def test_normalize_double_glob():
    assert normalize("src/auth/**") == ("src/auth", True)


def test_normalize_single_glob():
    assert normalize("src/auth/*") == ("src/auth", True)


def test_normalize_explicit_file():
    # foo.py has a dot — treated as exact, not prefix
    assert normalize("src/auth/login.py") == ("src/auth/login.py", False)


def test_paths_collide_exact_match():
    assert paths_collide(("src/auth", True), ("src/auth", True)) is True


def test_paths_collide_prefix():
    assert paths_collide(("src/auth", True), ("src/auth/login.py", False)) is True


def test_paths_collide_disjoint():
    assert paths_collide(("src/auth", True), ("src/billing", True)) is False


def test_paths_collide_unrelated_files():
    assert paths_collide(("src/auth/login.py", False), ("src/billing/checkout.py", False)) is False


def test_find_collisions_safe(safe_payloads):
    result = find_collisions(safe_payloads)
    assert result == []


def test_find_collisions_unsafe(colliding_payloads):
    result = find_collisions(colliding_payloads)
    assert len(result) == 1
    assert set(result[0]["agents"]) == {"alpha", "beta"}
    assert "src/shared/" in result[0]["files"] or any("shared" in f for f in result[0]["files"])


def test_find_collisions_three_way():
    payloads = [
        {"agent_type": "a", "focus_files": ["src/shared/util.py"]},
        {"agent_type": "b", "focus_files": ["src/shared/util.py"]},
        {"agent_type": "c", "focus_files": ["src/shared/util.py"]},
    ]
    result = find_collisions(payloads)
    # 3-choose-2 = 3 colliding pairs
    assert len(result) == 3


def test_find_collisions_empty_focus():
    payloads = [
        {"agent_type": "a", "focus_files": []},
        {"agent_type": "b", "focus_files": []},
    ]
    result = find_collisions(payloads)
    assert result == []


def _run(*args):
    old = sys.argv
    sys.argv = ["check_collisions.py", *args]
    try:
        import io
        old_out = sys.stdout
        buf = io.StringIO()
        sys.stdout = buf
        try:
            rc = cc_main()
        finally:
            sys.stdout = old_out
        return rc, buf.getvalue()
    finally:
        sys.argv = old


def test_main_safe(tmp_path, safe_payloads):
    p = tmp_path / "payloads.json"
    p.write_text(json.dumps(safe_payloads))
    rc, out = _run("--payloads-json", str(p))
    assert rc == 0
    data = json.loads(out)
    assert data["safe"] is True
    assert data["collisions"] == []


def test_main_unsafe(tmp_path, colliding_payloads):
    p = tmp_path / "payloads.json"
    p.write_text(json.dumps(colliding_payloads))
    rc, out = _run("--payloads-json", str(p))
    assert rc == 0
    data = json.loads(out)
    assert data["safe"] is False
    assert len(data["collisions"]) == 1


def test_main_single_payload_is_safe(tmp_path, valid_payload):
    p = tmp_path / "payloads.json"
    p.write_text(json.dumps([valid_payload]))
    rc, out = _run("--payloads-json", str(p))
    assert rc == 0
    data = json.loads(out)
    assert data["safe"] is True


def test_main_invalid_json(tmp_path):
    p = tmp_path / "payloads.json"
    p.write_text("not json")
    rc, out = _run("--payloads-json", str(p))
    assert rc == 0
    data = json.loads(out)
    assert data["safe"] is False
    assert "error" in data


def test_main_not_a_list(tmp_path):
    p = tmp_path / "payloads.json"
    p.write_text(json.dumps({"agent_type": "a"}))
    rc, out = _run("--payloads-json", str(p))
    assert rc == 0
    data = json.loads(out)
    assert data["safe"] is False
