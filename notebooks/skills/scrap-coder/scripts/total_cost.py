"""scrap-coder deterministic core.

Push the arithmetic down here: categorize each scrap-log row into one of the
7 standard codes and total the cost. Same input -> same output, exactly,
every time, at zero token cost. The LLM should CALL this, not redo the math.
"""
import re

# Code -> unit cost (USD). Mirrors knowledge/scrap_codes.md.
UNIT_COST = {
    "S1": 4.50, "S2": 12.00, "S3": 9.25, "S4": 18.75,
    "S5": 27.40, "S6": 15.00, "S7": 6.00,
}

# Ordered most-specific-first so S5 beats S7 on ambiguous rows.
_RULES = [
    ("S5", ("spindle", "crash", "tool break", "tool broke")),
    ("S4", ("inclusion", "void", "bad stock")),
    ("S6", ("wrong program", "misload", "fat finger", "wrong offset")),
    ("S2", ("out of tol", "oversize", "undersize", "out of spec")),
    ("S3", ("scratch", "burr", "porosity", "pit")),
    ("S1", ("setup", "first off", "first-off", "first article")),
]

_QTY = re.compile(r"(?:qty|x)\s*[:=]?\s*(\d+)", re.I)


def classify(text: str) -> str:
    """Return the scrap code (S1..S7) for one log row."""
    low = text.lower()
    if "rework" in low:
        return "REWORK"  # not scrap; excluded from total
    for code, phrases in _RULES:
        if any(p in low for p in phrases):
            return code
    return "S7"


def quantity(text: str) -> int:
    """Parse the unit count; default 1."""
    m = _QTY.search(text)
    return int(m.group(1)) if m else 1


def categorize(rows: list[str]) -> dict:
    """Categorize a shift's scrap rows and total the cost.

    Returns {"lines": [...], "by_code": {code: cost}, "total_cost": float,
             "excluded": int}.
    """
    lines, by_code, total, excluded = [], {}, 0.0, 0
    for row in rows:
        code = classify(row)
        qty = quantity(row)
        if code == "REWORK":
            excluded += 1
            lines.append({"row": row, "code": code, "qty": qty, "cost": 0.0})
            continue
        cost = round(UNIT_COST[code] * qty, 2)
        by_code[code] = round(by_code.get(code, 0.0) + cost, 2)
        total = round(total + cost, 2)
        lines.append({"row": row, "code": code, "qty": qty, "cost": cost})
    return {"lines": lines, "by_code": by_code,
            "total_cost": round(total, 2), "excluded": excluded}
