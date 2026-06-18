"""Unit tests for scripts/classify_learning.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from classify_learning import classify, main as classify_main  # noqa: E402


def test_classify_global_framework_pattern():
    text = "React 19 useOptimistic is the right primitive for form state"
    scope, _ = classify(text)
    assert scope == "global"


def test_classify_global_user_preference():
    text = "Josh prefers explicit error types over Result wrappers"
    scope, _ = classify(text)
    assert scope == "global"


def test_classify_global_anti_pattern_phrasing():
    text = "Anti-pattern: never use any in TypeScript interfaces"
    scope, _ = classify(text)
    assert scope == "global"


def test_classify_local_specific_path():
    text = "Update src/foo/bar.py to handle the case where input is None"
    scope, _ = classify(text)
    assert scope == "local"


def test_classify_local_pinned_id():
    text = "REQ-104 was renumbered after the merge from main"
    scope, _ = classify(text)
    assert scope == "local"


def test_classify_local_we_phrasing():
    text = "We tried memoisation here and it did not help"
    scope, _ = classify(text)
    assert scope == "local"


def test_classify_default_local_on_tie():
    # Empty string and pure neutral phrasing default to local (conservative)
    scope, _ = classify("Mostly unremarkable observation")
    assert scope == "local"


def test_classify_empty_input():
    scope, _ = classify("")
    assert scope == "local"


def test_classify_returns_signals():
    _, signals = classify("Josh prefers React 19 useOptimistic")
    assert "global_score" in signals
    assert signals["global_score"] >= 1


def _run(*args, stdin: str = ""):
    """Invoke classify_learning.main() with optional stdin."""
    import io
    old_argv, old_stdin = sys.argv, sys.stdin
    sys.argv = ["classify_learning.py", *args]
    sys.stdin = io.StringIO(stdin)
    try:
        return classify_main()
    finally:
        sys.argv, sys.stdin = old_argv, old_stdin


def test_main_with_text_arg(capsys):
    rc = _run("--text", "Josh prefers explicit error types")
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == "global"


def test_main_with_stdin(capsys):
    rc = _run(stdin="REQ-104 was renumbered")
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == "local"
