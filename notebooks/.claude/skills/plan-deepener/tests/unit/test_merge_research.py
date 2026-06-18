"""Unit tests for scripts/merge_research.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from merge_research import (
    render_list, render_insights, render_summary,
    insert_summary, insert_insights, main as mr_main,
)


def test_render_list_empty():
    assert render_list([]) == "_(none)_"


def test_render_list_items():
    assert render_list(["a", "b"]) == "- a\n- b"


def test_render_insights_substitutes(sample_findings):
    block = render_insights(sample_findings["sections"]["Service pattern"])
    assert "{{" not in block
    assert "pgbouncer" in block


def test_render_summary(sample_findings):
    block = render_summary(sample_findings["summary"])
    assert "{{" not in block
    assert "2026-02-14" in block
    assert "compound-docs" in block


def test_insert_summary_no_existing(sample_target_md, sample_findings):
    block = render_summary(sample_findings["summary"])
    out = insert_summary(sample_target_md, block)
    # summary appears before any ## heading
    summary_at = out.index("## Deepening Summary")
    arch_at = out.index("## Architecture")
    assert summary_at < arch_at


def test_insert_summary_replaces_existing(sample_findings):
    block = render_summary(sample_findings["summary"])
    text = "# Title\n\n## Deepening Summary\n**Old:** stuff\n\n## Architecture\nbody\n"
    out = insert_summary(text, block)
    assert "Old:" not in out
    assert "Deepened on:" in out


def test_insert_insights_inserts(sample_target_md, sample_findings):
    block = render_insights(sample_findings["sections"]["Service pattern"])
    out, did = insert_insights(sample_target_md, "Service pattern", block, force=False)
    assert did
    assert "### Research Insights" in out


def test_insert_insights_no_section(sample_findings):
    block = render_insights(sample_findings["sections"]["Service pattern"])
    out, did = insert_insights("# nothing", "Service pattern", block, force=False)
    assert not did


def test_insert_insights_idempotent_without_force(sample_target_md, sample_findings):
    block = render_insights(sample_findings["sections"]["Service pattern"])
    once, _ = insert_insights(sample_target_md, "Service pattern", block, force=False)
    twice, did = insert_insights(once, "Service pattern", block, force=False)
    assert not did  # already has insights, skip without --force
    assert once == twice


def test_insert_insights_force_replaces(sample_target_md, sample_findings):
    block = render_insights(sample_findings["sections"]["Service pattern"])
    once, _ = insert_insights(sample_target_md, "Service pattern", block, force=False)
    new_block = render_insights({"solutions": ["new"], "best_practices": ["new bp"],
                                 "edge_cases": [], "performance": [], "references": []})
    twice, did = insert_insights(once, "Service pattern", new_block, force=True)
    assert did
    assert "new bp" in twice
    assert "pgbouncer" not in twice  # old replaced


def _run(*args, stdin_text=None):
    import io
    old, old_stdin = sys.argv, sys.stdin
    sys.argv = ["merge_research.py", *args]
    if stdin_text is not None:
        sys.stdin = io.StringIO(stdin_text)
    try:
        return mr_main()
    finally:
        sys.argv = old
        sys.stdin = old_stdin


def test_main_writes(tmp_path, sample_target_md, sample_findings):
    target = tmp_path / "t.md"
    target.write_text(sample_target_md, encoding="utf-8")
    findings = tmp_path / "f.json"
    findings.write_text(json.dumps(sample_findings))
    rc = _run("--target", str(target), "--findings-json", str(findings))
    assert rc == 0
    text = target.read_text()
    assert "## Deepening Summary" in text
    assert "### Research Insights" in text


def test_main_missing_target(tmp_path):
    findings = tmp_path / "f.json"
    findings.write_text("{}")
    rc = _run("--target", str(tmp_path / "no.md"), "--findings-json", str(findings))
    assert rc == 1


def test_main_invalid_json(tmp_path, sample_target_md):
    target = tmp_path / "t.md"
    target.write_text(sample_target_md, encoding="utf-8")
    findings = tmp_path / "f.json"
    findings.write_text("not json")
    rc = _run("--target", str(target), "--findings-json", str(findings))
    assert rc == 1
