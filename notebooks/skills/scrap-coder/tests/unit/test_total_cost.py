"""Unit tests for total_cost.py. Expected values are literals, not recomputed."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from total_cost import classify, quantity, categorize


def test_classify_setup_is_s1():
    assert classify("first off setup scrap") == "S1"


def test_classify_specific_beats_generic():
    # spindle crash (S5) should win over a bare 'pit' mention (S3)
    assert classify("spindle crash, left a pit") == "S5"


def test_rework_is_excluded():
    assert classify("rework only, re-ran ok") == "REWORK"


def test_quantity_parsed():
    assert quantity("out of tol qty:3") == 3
    assert quantity("plain row") == 1


def test_categorize_totals_example():
    rows = [
        "setup scrap, first off",
        "out of tol on bore qty:2",
        "spindle crash trashed the part",
        "rework only - re-ran ok",
    ]
    out = categorize(rows)
    assert out["total_cost"] == 55.90
    assert out["excluded"] == 1
    assert out["by_code"]["S2"] == 24.00
