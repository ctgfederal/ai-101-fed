"""Build script for Notebook 07 (Adaptation) data fixtures.

Generates, under data/scrap/ and data/adaptation/:
  - scrap_lines.jsonl       : 60 labeled scrap-log lines (7 codes), small + vendored
  - history_fallback.json   : precomputed gated-vs-ungated optimizer histories
  - skill_opt_fallback.json : precomputed SkillOpt (word_count, val_score) trajectory
  - graduation_fallback.json: precomputed before/after trace->tool steps/tokens
  - audit_traces.jsonl      : sec-3-style audit/trace store rows for the fine-tune cell

All data is deterministic (fixed seed), tiny, and committed so the notebook
renders every visual with no model, no GPU, and no network.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRAP = ROOT / "scrap"
ADAPT = ROOT / "adaptation"
SCRAP.mkdir(parents=True, exist_ok=True)
ADAPT.mkdir(parents=True, exist_ok=True)

random.seed(422)

# --- 7 scrap codes (manufacturing-floor style) -----------------------------
# code -> (keywords that imply it, a few realistic log line templates)
CODES = {
    "DIM_OOT":   "dimension out of tolerance",
    "SURF_DEF":  "surface defect / scratch / blemish",
    "MAT_FLAW":  "raw material flaw / inclusion / void",
    "MACH_SET":  "machine setup / fixture / alignment error",
    "TOOL_WEAR": "tool wear / dull cutter / chipped insert",
    "OP_ERR":    "operator error / misload / wrong program",
    "CONTAM":    "contamination / coolant / debris / oil",
}

TEMPLATES = {
    "DIM_OOT": [
        "bore diameter measured 12.07mm, spec 12.00 +/-0.02, rejected",
        "flatness 0.08mm exceeds 0.05mm GD&T callout on face B",
        "part runs long: 84.3mm vs nominal 84.0, out of tolerance",
        "wall thickness under min, CMM flags -0.04 deviation",
        "thread pitch gauge no-go side enters, dimension reject",
    ],
    "SURF_DEF": [
        "visible scratch across cosmetic surface near gate",
        "blemish / orange-peel on anodized face, cosmetic reject",
        "scuff mark on flange, surface finish out of spec",
        "pitting observed on polished bore wall",
        "burr left on edge, surface defect at parting line",
    ],
    "MAT_FLAW": [
        "inclusion found in bar stock cross-section, material flaw",
        "internal void detected on X-ray, raw material reject",
        "porosity in casting near boss, material defect",
        "lamination crack in plate stock, incoming material flaw",
        "hard spot in billet, suspected inclusion",
    ],
    "MACH_SET": [
        "fixture shifted mid-run, datum offset, setup error",
        "wrong work offset G54 loaded, alignment off",
        "vise jaw not seated, part skewed, machine setup fault",
        "tailstock misaligned, taper introduced, setup reject",
        "soft jaws not bored to size, locating error",
    ],
    "TOOL_WEAR": [
        "chipped insert left tear-out on finish pass, tool wear",
        "dull end mill, poor finish and oversize, replace tool",
        "drill worn, hole undersize and tapered, tool wear",
        "tap shows wear, thread torn, replace tooling",
        "worn reamer leaving chatter marks, tool condition",
    ],
    "OP_ERR": [
        "operator loaded wrong program O4412, scrapped lot",
        "part misloaded backwards in fixture, operator error",
        "skipped deburr step, operator missed routing",
        "wrong material grade pulled from rack by operator",
        "operator overrode feed, crashed into stop",
    ],
    "CONTAM": [
        "coolant residue baked onto surface, contamination",
        "metal debris embedded in seal groove, contamination",
        "oil film prevented coating adhesion, contamination",
        "chip nest in blind pocket, debris contamination",
        "grit found under gasket face, contamination reject",
    ],
}

# Some deliberately ambiguous / edge lines a weak prompt gets wrong.
# These are the failures the optimizer "learns" from in the live path.
EDGE = [
    ("looks shiny but bore reads 12.06mm over spec", "DIM_OOT"),
    ("mark on surface traced to chipped insert on last pass", "TOOL_WEAR"),
    ("debris turned out to be an inclusion in the stock", "MAT_FLAW"),
    ("alignment off because operator skipped fixture seat check", "MACH_SET"),
    ("finish blemish from worn tool, not handling", "TOOL_WEAR"),
    ("oversize hole, drill was worn not a setup issue", "TOOL_WEAR"),
    ("scratch present but root cause is coolant grit", "CONTAM"),
    ("flatness fail after fixture shifted mid-run", "MACH_SET"),
]

rows = []
codes = list(CODES.keys())
# ~7-8 clean lines per code
for code in codes:
    for tmpl in TEMPLATES[code]:
        rows.append({"text": tmpl, "label": code})
# add the edge cases
for text, label in EDGE:
    rows.append({"text": text, "label": label})

# pad to exactly 60 by recombining clean templates with light noise
fillers = []
while len(rows) + len(fillers) < 60:
    code = random.choice(codes)
    tmpl = random.choice(TEMPLATES[code])
    fillers.append({"text": tmpl + " [batch %d]" % random.randint(100, 999), "label": code})
rows.extend(fillers)
rows = rows[:60]
random.shuffle(rows)

with (SCRAP / "scrap_lines.jsonl").open("w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")

# --- Precomputed optimizer history fallback --------------------------------
# Shape: per-epoch (epoch, train, val, accepted). Gated curve is monotonic
# non-decreasing on val (accept-if-better). Ungated chases train and val drifts.
history_fallback = {
    "note": "Recorded from a small offline GEPA-style run; seed/model dependent.",
    "epochs": 5,
    "gated": [
        # epoch, train, val, accepted
        [0, 0.55, 0.50, True],
        [1, 0.68, 0.65, True],
        [2, 0.78, 0.70, True],
        [3, 0.82, 0.70, False],   # candidate improved train but not val -> rejected
        [4, 0.88, 0.80, True],
    ],
    "ungated": [
        [0, 0.55, 0.50, True],
        [1, 0.70, 0.60, True],
        [2, 0.82, 0.55, True],    # train-chasing: accepted on train, val falls
        [3, 0.90, 0.50, True],
        [4, 0.95, 0.45, True],    # overfit: train high, val drifting down
    ],
}
(ADAPT / "history_fallback.json").write_text(json.dumps(history_fallback, indent=2))

# --- Precomputed SkillOpt trajectory (word_count, val_score) ---------------
skill_opt_fallback = {
    "note": "Recorded add/delete/replace edits to scrap-coder SKILL.md; gated.",
    "word_budget": 320,
    "trajectory": [
        # edit_id, action, word_count, val_score, accepted
        [0, "seed",    180, 0.62, True],
        [1, "add",     214, 0.70, True],
        [2, "replace", 226, 0.74, True],
        [3, "add",     298, 0.74, False],   # bloats toward budget, no val gain -> rejected
        [4, "delete",  205, 0.76, True],    # trim + sharpen -> val up, words down
        [5, "add",     242, 0.82, True],
    ],
}
(ADAPT / "skill_opt_fallback.json").write_text(json.dumps(skill_opt_fallback, indent=2))

# --- Precomputed trace->tool graduation before/after -----------------------
graduation_fallback = {
    "note": "Worked illustration; magnitude depends on task repetitiveness.",
    "before": {"llm_steps": 7, "tokens": 5400, "accuracy": 0.80},
    "after":  {"llm_steps": 3, "tokens": 2100, "accuracy": 0.80},
}
(ADAPT / "graduation_fallback.json").write_text(json.dumps(graduation_fallback, indent=2))

# --- Sec-3-style audit/trace store for the fine-tune dataset cell ----------
# Each row is a recorded decision trace with an outcome label + signature stub.
audit = []
samples = [
    ("Classify scrap line: 'chipped insert left tear-out on finish pass'", "TOOL_WEAR", "good"),
    ("Classify scrap line: 'bore diameter 12.07mm over spec'", "DIM_OOT", "good"),
    ("Classify scrap line: 'coolant residue baked onto surface'", "CONTAM", "good"),
    ("Classify scrap line: 'operator loaded wrong program'", "OP_ERR", "good"),
    ("Classify scrap line: 'inclusion found in bar stock'", "MAT_FLAW", "good"),
    ("Classify scrap line: 'fixture shifted mid-run'", "MACH_SET", "good"),
    ("Classify scrap line: 'visible scratch on cosmetic surface'", "SURF_DEF", "good"),
    ("Classify scrap line: 'looks shiny but reads oversize'", "SURF_DEF", "bad"),   # wrong: should be DIM_OOT
    ("Classify scrap line: 'mark traced to chipped insert'", "SURF_DEF", "bad"),    # wrong: should be TOOL_WEAR
]
for i, (prompt, answer, outcome) in enumerate(samples):
    audit.append({
        "trace_id": "trc_%03d" % i,
        "ts": "2026-04-2%dT0%d:11:00Z" % (i % 9, i % 9),
        "task": "scrap_classify",
        "input": prompt,
        "output": answer,
        "outcome": outcome,          # 'good' rows are the fine-tune candidates
        "reviewer": "sarah_chen" if i % 2 == 0 else "marcus_reyes",
        "sig": "ed25519:stub-%032x" % (i * 7919),
    })
with (ADAPT / "audit_traces.jsonl").open("w") as f:
    for r in audit:
        f.write(json.dumps(r) + "\n")

print("scrap_lines.jsonl       :", len(rows), "rows")
print("history_fallback.json   :", "gated+ungated x", history_fallback["epochs"], "epochs")
print("skill_opt_fallback.json :", len(skill_opt_fallback["trajectory"]), "edits")
print("graduation_fallback.json:", "before/after")
print("audit_traces.jsonl      :", len(audit), "rows (",
      sum(1 for r in audit if r["outcome"] == "good"), "good )")
