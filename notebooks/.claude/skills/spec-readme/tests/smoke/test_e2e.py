"""End-to-end smoke for spec-readme."""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _run(s, *args, input_text: str | None = None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / s), *args],
        capture_output=True,
        text=True,
        input=input_text,
    )


def test_help_runs_for_every_script():
    for s in ("init_readme.py", "update_status.py",
              "append_phase_note.py", "validate_output.py"):
        result = _run(s, "--help")
        assert result.returncode == 0, f"{s} --help failed: {result.stderr}"


def test_full_pipeline(tmp_path):
    specs_root = tmp_path / "specs"
    specs_root.mkdir()

    # 1. init
    init = _run("init_readme.py",
                "--feature", "feature-search",
                "--specs-root", str(specs_root))
    assert init.returncode == 0, init.stderr
    readme_path = Path(init.stdout.strip())
    assert readme_path.is_file()

    # 2. update_status (PRD -> approved)
    upd = _run("update_status.py",
               "--feature", "feature-search",
               "--specs-root", str(specs_root),
               "--doc", "prd",
               "--status", "approved")
    assert upd.returncode == 0, upd.stderr

    # 3. append_phase_note (Phase 1)
    note = _run("append_phase_note.py",
                "--feature", "feature-search",
                "--specs-root", str(specs_root),
                "--phase", "1",
                "--name", "Foundation",
                "--note", "Spec under-specified caching layer.")
    assert note.returncode == 0, note.stderr

    # 4. validate_output
    val = _run("validate_output.py", "--file", str(readme_path))
    assert val.returncode == 0, val.stderr

    # Body checks.
    body = readme_path.read_text()
    assert "| PRD | approved |" in body
    assert "### Phase 1: Foundation" in body
    assert "Spec under-specified caching layer." in body


def test_full_pipeline_with_stdin_note(tmp_path):
    specs_root = tmp_path / "specs"
    specs_root.mkdir()

    init = _run("init_readme.py",
                "--feature", "feat-x",
                "--specs-root", str(specs_root))
    assert init.returncode == 0, init.stderr
    readme_path = Path(init.stdout.strip())

    note = _run("append_phase_note.py",
                "--feature", "feat-x",
                "--specs-root", str(specs_root),
                "--phase", "2",
                "--name", "Core",
                input_text="Stdin-piped note for phase 2.")
    assert note.returncode == 0, note.stderr

    val = _run("validate_output.py", "--file", str(readme_path))
    assert val.returncode == 0, val.stderr

    body = readme_path.read_text()
    assert "Stdin-piped note for phase 2." in body
