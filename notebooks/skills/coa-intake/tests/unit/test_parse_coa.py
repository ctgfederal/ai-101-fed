import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from parse_coa import parse_coa

def test_returns_dict():
    assert isinstance(parse_coa("lot: 42"), dict)
