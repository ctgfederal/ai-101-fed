"""End-to-end smoke for steering-docs-creator."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
    )


def test_help_runs_for_every_script() -> None:
    for name in (
        "init_steering.py",
        "validate_steering.py",
        "update_doc.py",
        "validate_output.py",
    ):
        result = _run(name, "--help")
        assert result.returncode == 0, f"{name} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path: Path) -> None:
    steering = tmp_path / "steering"

    # init scaffolds all four
    init = _run("init_steering.py", "--steering-root", str(steering))
    assert init.returncode == 0, init.stderr
    for doc in ("product", "tech", "structure", "roadmap"):
        assert (steering / f"{doc}.md").is_file()

    # validate root: passes
    v1 = _run("validate_steering.py", "--steering-root", str(steering))
    assert v1.returncode == 0, v1.stderr

    # update one section in tech
    body = "| Layer | Tech |\n|-------|------|\n| Lang | Python 3.12 |\n"
    upd = _run(
        "update_doc.py",
        "--steering-root", str(steering),
        "--doc", "tech",
        "--section", "Tech Stack",
        "--body", body,
    )
    assert upd.returncode == 0, upd.stderr
    assert "Python 3.12" in (steering / "tech.md").read_text()

    # validate per-doc
    vo = _run(
        "validate_output.py",
        "--file", str(steering / "tech.md"),
        "--doc", "tech",
    )
    assert vo.returncode == 0, vo.stderr

    # validate root again: still passes
    v2 = _run("validate_steering.py", "--steering-root", str(steering))
    assert v2.returncode == 0, v2.stderr


def test_idempotent_init(tmp_path: Path) -> None:
    steering = tmp_path / "s"
    r1 = _run("init_steering.py", "--steering-root", str(steering))
    assert r1.returncode == 0
    snapshot = (steering / "product.md").read_text()
    # mutate one to verify --force-less re-run does not overwrite it
    (steering / "tech.md").write_text("MUTATED\n")
    r2 = _run("init_steering.py", "--steering-root", str(steering))
    assert r2.returncode == 0
    assert (steering / "tech.md").read_text() == "MUTATED\n"
    assert (steering / "product.md").read_text() == snapshot
