"""Build script for Section 04 (skills) notebook data.

Vendors:
  - skills/scrap-coder/        a real, validator-passing demo skill
  - data/scrap/noisy_inputs.json   ~20 messy scrap-log rows
  - data/scrap/fallbacks.json      precomputed token/reliability/test arrays
                                   so every visual renders offline (no model/GPU)

Run:  python3 data/build_skills_04.py
Idempotent: safe to re-run.
"""
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent          # ai-roadshow/
SKILL = ROOT / "skills" / "scrap-coder"
SCRAP = ROOT / "data" / "scrap"

# ─────────────────────────────────────────────────────────────────────────────
# 1. The scrap-coder skill folder (8-section SKILL.md + script + knowledge + tests)
# ─────────────────────────────────────────────────────────────────────────────
for d in ["scripts", "templates", "knowledge", "validation", "tests/unit", "examples/simple"]:
    (SKILL / d).mkdir(parents=True, exist_ok=True)

# The 7 standard scrap codes + cost table — this is the "knowledge" the bloated
# prompt would otherwise carry on every single call.
SCRAP_CODES = dedent('''\
    # Scrap codes — standard 7 (Line 4, swing shift)

    Every scrap event maps to exactly one of these codes. Cost is USD per unit
    scrapped (material + labor already burned at the scrap point).

    | Code | Name              | Trigger phrase in the log              | Unit cost (USD) |
    |------|-------------------|----------------------------------------|-----------------|
    | S1   | Setup / first-off | "setup", "first off", "first article"  | 4.50            |
    | S2   | Dimensional       | "out of tol", "oversize", "undersize"  | 12.00           |
    | S3   | Surface defect    | "scratch", "burr", "porosity", "pit"   | 9.25            |
    | S4   | Material flaw     | "inclusion", "void", "bad stock"       | 18.75           |
    | S5   | Machine fault     | "spindle", "crash", "tool break"       | 27.40           |
    | S6   | Operator error    | "wrong program", "misload", "fat finger"| 15.00          |
    | S7   | Unknown / other   | anything that matches none of the above | 6.00           |

    Rules:
    - One code per row. If two could apply, the more specific wins (S5 > S7).
    - "rework" is NOT scrap — exclude it from the total.
    - Quantity defaults to 1 if the row does not state a count.
''')
(SKILL / "knowledge" / "scrap_codes.md").write_text(SCRAP_CODES)

# scripts/total_cost.py — the deterministic core. Same input → same output.
TOTAL_COST = dedent('''\
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

    _QTY = re.compile(r"(?:qty|x)\\s*[:=]?\\s*(\\d+)", re.I)


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
''')
(SKILL / "scripts" / "total_cost.py").write_text(TOTAL_COST)

# templates/shift_report.md
(SKILL / "templates" / "shift_report.md").write_text(dedent('''\
    # Scrap report — {shift}

    | Code | Name | Units | Cost (USD) |
    |------|------|-------|-----------|
    {rows}

    **Total scrap cost: ${total:.2f}**  ·  Excluded (rework): {excluded}
'''))

# validation/quality-checklist.md
(SKILL / "validation" / "quality-checklist.md").write_text(dedent('''\
    # Quality checklist — scrap-coder

    Walk this cold against the artifact before bumping version.

    - [ ] All 8 sections present in SKILL.md, in order
    - [ ] Description includes "Use when..." AND "Do NOT use for..."
    - [ ] Every script in scripts/ has a matching tests/unit/test_*.py
    - [ ] total_cost.py is deterministic (same input -> same output)
    - [ ] Cost table in knowledge/ matches UNIT_COST in total_cost.py
    - [ ] Examples/simple/ has a worked input + expected output
'''))

# examples/simple/
(SKILL / "examples" / "simple" / "input.txt").write_text(dedent('''\
    setup scrap, first off
    out of tol on bore qty:2
    spindle crash trashed the part
    rework only - re-ran ok
'''))
(SKILL / "examples" / "simple" / "README.md").write_text(
    "Input: 4 rows (S1 x1, S2 x2, S5 x1, one rework).\n"
    "Expected: total = 4.50 + 24.00 + 27.40 = 55.90; excluded = 1."
)

# tests/unit/test_total_cost.py — hard-coded expected literals, no reimplementation.
(SKILL / "tests" / "unit" / "test_total_cost.py").write_text(dedent('''\
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
'''))

# CHANGELOG.md
(SKILL / "CHANGELOG.md").write_text(dedent('''\
    ## 1.0.0 — 2026-06-02
    - Initial: 7 scrap codes, deterministic total_cost.py, unit tests, examples.
'''))

# SKILL.md — the 8-section router. Description has Use-when AND Do-NOT-use.
DESCRIPTION = (
    'Categorize a shift’s scrap log into the 7 standard scrap codes (S1-S7) and '
    'total the cost. Use when an operator or supervisor asks to "code this scrap '
    'log", "total tonight’s scrap", or "categorize the shift’s rejects". '
    'Produces a per-code breakdown and a dollar total. Do NOT use for rework '
    'tracking, downtime coding, or quality-escape (RMA) analysis — those are '
    'separate skills with their own code sets.'
)
SKILL_MD = dedent(f'''\
    ---
    name: scrap-coder
    version: 1.0.0
    description: |
      {DESCRIPTION}
    triggers:
      - "code this scrap log"
      - "total tonight's scrap"
      - "categorize the shift's rejects"
    tools:
      - bash_tool
      - view
    model: claude-sonnet-4-6
    ---

    # scrap-coder

    Turn a shift's free-text scrap log into coded line items and a cost total.

    ## Files
    - `scripts/total_cost.py` — **Deterministic.** `categorize(rows)` codes each
      row and totals cost. Call this; do not redo the math inline.
    - `knowledge/scrap_codes.md` — the 7 codes, trigger phrases, unit costs.
      Load only when a row is ambiguous and you need the rule.
    - `templates/shift_report.md` — the output shape.
    - `validation/quality-checklist.md` — pre-bump checklist.
    - `examples/simple/` — smallest worked example; pattern-match against it.

    ## Contract
    Given a list of scrap-log rows, produce a result such that:
    1. Every non-rework row is assigned exactly one code in S1..S7.
    2. The more specific code wins on ambiguity (S5 machine-fault > S7 unknown).
    3. Rows containing "rework" are excluded from the cost total.
    4. Quantity defaults to 1 when a row states no count.
    5. `total_cost` equals the sum of (unit_cost * qty) over coded rows, rounded
       to cents.

    ## Knowledge
    The authoritative code list, trigger phrases, and unit costs live in
    `knowledge/scrap_codes.md`. Read it only for an ambiguous row.

    ## Steps
    1. Collect the shift's scrap rows (caller supplies them).
    2. Call `total_cost.categorize(rows)` for codes + totals.
    3. For any row coded S7 (unknown), re-check against `knowledge/scrap_codes.md`.
    4. Render the result into `templates/shift_report.md`.

    ## Output
    A breakdown table (code, name, units, cost) plus a dollar total and an
    excluded-rework count, as in `templates/shift_report.md`.

    ## Antipatterns
    - Doing the cost arithmetic in the model's head instead of calling
      `total_cost.categorize` — it drifts and is unauditable.
    - Counting "rework" rows toward scrap cost.
    - Inventing a code outside S1..S7.

    ## Validation
    - Run `pytest tests/unit/` — must exit 0.
    - Walk `validation/quality-checklist.md` cold against the artifact.

    ## Examples
    - `examples/simple/` — setup + dimensional + machine-fault + one rework.
      Expected total $55.90, 1 excluded.
''')
(SKILL / "SKILL.md").write_text(SKILL_MD)

# ─────────────────────────────────────────────────────────────────────────────
# 2. NOISY_INPUTS — ~20 messy scrap-log rows for the reliability demo
# ─────────────────────────────────────────────────────────────────────────────
SCRAP.mkdir(parents=True, exist_ok=True)
NOISY_INPUTS = [
    "setup scrap first off qty:3",
    "out of tol on the bore, scrapped 2",
    "spindle crash — tool break, part trashed",
    "scratch on face qty:5",
    "porosity in weld, 1 ea",
    "inclusion in bar stock, bad stock x4",
    "wrong program loaded, misload qty:2",
    "burr not removed, 3 units",
    "first article check failed setup",
    "oversize OD .003 over, qty=2",
    "rework only, re-ran fine",          # excluded
    "pit on the chamfer x6",
    "fat finger wrong offset, 1",
    "void found on CT scan, 2 ea",
    "undersize bore by .001 qty:4",
    "tool broke mid-cut, 1",
    "something weird, op unsure",         # -> S7 unknown
    "first off setup, 2 parts",
    "scratch + minor burr cleaned, rework",  # excluded (rework wins)
    "misload jammed the fixture qty:3",
    "porosity cluster, scrapped 7",
    "out of spec runout, 2",
]
(SCRAP / "noisy_inputs.json").write_text(json.dumps(NOISY_INPUTS, indent=2))

# ─────────────────────────────────────────────────────────────────────────────
# 3. Fallbacks — precomputed so every visual renders with no model/GPU
# ─────────────────────────────────────────────────────────────────────────────
# Compute the ground-truth total from the deterministic core so the offline
# "script" answer is real, not invented.
import importlib.util
spec = importlib.util.spec_from_file_location("tc", SKILL / "scripts" / "total_cost.py")
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)
truth = tc.categorize(NOISY_INPUTS)

fallbacks = {
    "note": "Precomputed so notebook 04 renders fully offline (OFFLINE=True or no endpoint).",
    # VISUAL 1: tokens loaded per approach, segmented.
    "tokens": {
        "bloated_prompt": {"router": 0, "knowledge": 0, "template": 0,
                           "system_block": 612, "scratch": 140},
        "skill": {"router": 88, "knowledge": 196, "template": 0, "scratch": 140},
    },
    # VISUAL 2: files loaded per task.
    "files_loaded": {
        "matching_task": ["SKILL.md", "knowledge/scrap_codes.md"],
        "nonmatching_task": [],
        "router_line_only": True,
    },
    # VISUAL 3: reliability + cost, LLM-math vs script-math over the noisy set.
    # Script is exact every row; the LLM fallback shows a plausible model run
    # (a few arithmetic slips on messy rows). Model-dependent — labeled as such.
    "reliability": {
        "n": len(NOISY_INPUTS),
        "llm_does_math":    [1,1,1,1,1,0,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,1],
        "script_does_math": [1] * len(NOISY_INPUTS),
        "tokens_per_run": {"llm_does_math": 95, "script_does_math": 0},
        "caveat": "LLM error count is model-dependent; this is one illustrative run.",
    },
    # VISUAL 4: the four test layers.
    "test_layers": {
        "unit":        {"passed": True,  "catches": "logic bugs in a single function"},
        "integration": {"passed": True,  "catches": "wrong wiring between script + skill"},
        "evals":       {"passed": True,  "catches": "quality regressions on real inputs"},
        "e2e":         {"passed": True,  "catches": "broken end-to-end skill invocation"},
    },
    "ground_truth_total": truth["total_cost"],
    "ground_truth_excluded": truth["excluded"],
}
(SCRAP / "fallbacks.json").write_text(json.dumps(fallbacks, indent=2))

print("scrap-coder skill at:", SKILL)
for p in sorted(SKILL.rglob("*")):
    if p.is_file():
        print("  ", p.relative_to(SKILL.parent))
print("noisy_inputs.json rows:", len(NOISY_INPUTS))
print("ground-truth total:", truth["total_cost"], "excluded:", truth["excluded"])
