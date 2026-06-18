"""Allow pytest to collect *_eval.py files in this directory."""
collect_ignore_glob = []


def pytest_collect_file(parent, file_path):
    """Hook: tell pytest to collect any file ending in _eval.py."""
    import pytest
    if file_path.suffix == ".py" and file_path.name.endswith("_eval.py"):
        return pytest.Module.from_parent(parent, path=file_path)
    return None
