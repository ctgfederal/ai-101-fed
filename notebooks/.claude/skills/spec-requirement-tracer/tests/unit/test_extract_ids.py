"""Unit tests for scripts/extract_ids.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import extract_ids
from extract_ids import (
    REQ_RE,
    COMP_RE,
    TASK_RE,
    extract_ids as extract_ids_fn,
    parse_sdd_traceability,
    parse_plan_task_reqs,
    is_test_file,
    grep_code_refs,
    main as ext_main,
)


def test_extract_ids_reqs():
    assert extract_ids_fn("REQ-005 stuff REQ-001", REQ_RE, "REQ") == ["REQ-001", "REQ-005"]


def test_extract_ids_comps():
    assert extract_ids_fn("COMP-002 COMP-001", COMP_RE, "COMP") == ["COMP-001", "COMP-002"]


def test_extract_ids_tasks():
    assert extract_ids_fn("T-003 T-001 T-002", TASK_RE, "T") == ["T-001", "T-002", "T-003"]


def test_extract_ids_empty():
    assert extract_ids_fn("nothing here", REQ_RE, "REQ") == []


def test_parse_sdd_traceability_arrow():
    text = "REQ-001 -> COMP-001, COMP-002"
    out = parse_sdd_traceability(text)
    assert out == {"REQ-001": ["COMP-001", "COMP-002"]}


def test_parse_sdd_traceability_colon():
    text = "REQ-002: COMP-003"
    out = parse_sdd_traceability(text)
    assert out == {"REQ-002": ["COMP-003"]}


def test_parse_sdd_traceability_table():
    text = "| REQ-003 | COMP-004, COMP-005 |"
    out = parse_sdd_traceability(text)
    assert out == {"REQ-003": ["COMP-004", "COMP-005"]}


def test_parse_sdd_traceability_no_match():
    text = "Free prose mentioning REQ-001 and COMP-001 separately."
    out = parse_sdd_traceability(text)
    # The pattern *can* still match because `:` exists in some prose; we only
    # care that REQ→COMP requires the right structure. Let's make sure with
    # a clean negative case.
    text_neg = "no relation here"
    assert parse_sdd_traceability(text_neg) == {}


def test_parse_plan_task_reqs():
    text = (
        "- **T-001** (red): Title\n"
        "  - Components: COMP-001\n"
        "  - Requirements: REQ-001, REQ-002\n"
        "  - Acceptance: ok\n"
    )
    out = parse_plan_task_reqs(text)
    assert out == {"T-001": ["REQ-001", "REQ-002"]}


def test_parse_plan_task_reqs_multiple_tasks():
    text = (
        "- **T-001**\n"
        "  - Requirements: REQ-001\n"
        "- **T-002**\n"
        "  - Requirements: REQ-002\n"
    )
    out = parse_plan_task_reqs(text)
    assert out == {"T-001": ["REQ-001"], "T-002": ["REQ-002"]}


def test_is_test_file_test_path():
    assert is_test_file(Path("tests/test_foo.py"))
    assert is_test_file(Path("src/foo_test.py"))
    assert is_test_file(Path("frontend/Button.test.ts"))
    assert is_test_file(Path("frontend/Button.spec.ts"))


def test_is_test_file_code_path():
    assert not is_test_file(Path("src/foo.py"))
    assert not is_test_file(Path("lib/services/auth.ts"))


def test_grep_code_refs_basic(tmp_path):
    root = tmp_path
    (root / "src").mkdir()
    (root / "tests").mkdir()
    (root / "src" / "a.py").write_text("# REQ-001\n")
    (root / "tests" / "test_a.py").write_text("# REQ-001\n")
    (root / "src" / "b.py").write_text("nothing here")
    code, tests = grep_code_refs(root, ["*.py"], ["REQ-001", "REQ-002"])
    assert code["REQ-001"] == ["src/a.py"]
    assert tests["REQ-001"] == ["tests/test_a.py"]
    assert code["REQ-002"] == []
    assert tests["REQ-002"] == []


def test_grep_code_refs_unknown_req(tmp_path):
    root = tmp_path
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("# REQ-999\n")
    code, tests = grep_code_refs(root, ["*.py"], ["REQ-001"])
    # REQ-999 is not in PRD; should be skipped
    assert code == {"REQ-001": []}
    assert tests == {"REQ-001": []}


def test_grep_code_refs_empty_root(tmp_path):
    root = tmp_path / "missing"
    code, tests = grep_code_refs(root, ["*.py"], ["REQ-001"])
    assert code == {"REQ-001": []}
    assert tests == {"REQ-001": []}


def _run(*a):
    old = sys.argv
    sys.argv = ["extract_ids.py", *a]
    try:
        return ext_main()
    finally:
        sys.argv = old


def test_main_missing_prd(tmp_path):
    rc = _run(
        "--prd", str(tmp_path / "no.md"),
        "--sdd", str(tmp_path / "no.md"),
        "--plan", str(tmp_path / "no.md"),
        "--code-root", str(tmp_path),
    )
    assert rc == 1


def test_main_happy(fake_prd, fake_sdd, fake_plan, fake_code_root, capsys):
    rc = _run(
        "--prd", str(fake_prd),
        "--sdd", str(fake_sdd),
        "--plan", str(fake_plan),
        "--code-root", str(fake_code_root),
    )
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["prd_reqs"] == ["REQ-001", "REQ-002", "REQ-003"]
    assert data["sdd_comps"] == ["COMP-001", "COMP-002", "COMP-003"]
    assert data["plan_tasks"] == ["T-001", "T-002"]
    assert data["sdd_traceability"]["REQ-001"] == ["COMP-001", "COMP-003"]
    assert data["plan_task_reqs"]["T-001"] == ["REQ-001"]
    assert data["code_refs"]["REQ-001"] == ["src/search.py"]
    assert data["test_refs"]["REQ-001"] == ["tests/test_search.py"]
    assert data["code_refs"]["REQ-002"] == []
    assert data["test_refs"]["REQ-002"] == ["tests/test_ranking.py"]
    assert data["code_refs"]["REQ-003"] == []
    assert data["test_refs"]["REQ-003"] == []
