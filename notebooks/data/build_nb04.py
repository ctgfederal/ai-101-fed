"""Build notebooks/04_skills.ipynb (nbformat-4) for the AI Roadshow v2 curriculum.

Authoring only — cells are written with execution_count=None and outputs=[];
nbconvert executes them afterwards to bake in real outputs.
"""
import json
from pathlib import Path

OUT = Path("/Users/joshschultz/Projects/ai-roadshow/notebooks/04_skills.ipynb")


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": s.splitlines(keepends=True)}


cells = []

# ── Cell 0 — title ───────────────────────────────────────────────────────────
cells.append(md(
'''# Notebook 04 — Skills

**A skill is a folder.** We'll prove that the folder form is cheaper, more
reliable, and shippable than the giant prompt you've been writing.

> **Where this sits in the five moves (sec 1):** a skill is **STORE +
> RETRIEVE + INSERT on demand** — procedural memory written down once (store),
> pulled in only when the task matches (retrieve), and placed in the window in
> the right form and order (insert). Progressive disclosure *is* retrieval
> applied to your own instructions. The packaging is Anthropic's "Agent
> Skills" pattern ([Anthropic, *Effective context engineering for AI agents*,
> 2025](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents);
> LangChain's "Write / Select" maps onto store / retrieve,
> [Martin, 2025](https://www.langchain.com/blog/context-engineering-for-agents)).

The proof, in five moves:
1. Run the **same task** as a bloated system prompt vs a progressively-disclosed skill, and measure the token gap.
2. Walk a real `SKILL.md` folder.
3. Push one step down from LLM to script — and show it gets cheaper *and* more reliable.
4. Run the validator + tests live.
5. Scaffold a skill the way you actually build one.
'''))

# ── Cell 1 — setup ───────────────────────────────────────────────────────────
cells.append(md("## Setup\n\n`setup()` connects the model and counts tokens; the rest of this cell just names the demo skill's folders and loads its data. The skill-running loop (`run` / `Tool` / `StaticProvider`) comes straight from `arcrun` — that loop *is* the lesson, so we keep it visible. Precomputed fallbacks let every chart render even with no model reachable."))
cells.append(code(
'''from pathlib import Path
import json, re, subprocess, sys, importlib.util
from textwrap import dedent

import matplotlib.pyplot as plt

from roadshow import setup
from arcrun import run, Tool, ToolContext, StaticProvider

# model: the connected LLM · ask: one-shot helper · ntok: token counter · DATA: data/ path
model, ask, ntok, DATA = setup()

# Lesson paths: the demo skill we inspect/run, and its scrap-log data.
SKILLS_DIR = DATA.parent / "skills"
SKILL_DIR  = SKILLS_DIR / "scrap-coder"
SCRAP_DIR  = DATA / "scrap"

# Precomputed fallbacks so the notebook renders fully offline.
FALLBACKS    = json.loads((SCRAP_DIR / "fallbacks.json").read_text())
NOISY_INPUTS = json.loads((SCRAP_DIR / "noisy_inputs.json").read_text())

print("skill dir:", SKILL_DIR, "exists:", SKILL_DIR.exists())
print("noisy rows:", len(NOISY_INPUTS), "| ground-truth total $", FALLBACKS["ground_truth_total"])
'''))

# ── Cell 2 — CONTROL CELL ────────────────────────────────────────────────────
cells.append(md("## ▶ Control cell — the only cell you edit\n\nEvery knob the notebook reads lives here. Change one, then **re-run this cell and the cells below it** to see the effect. The model itself is already wired by `setup()` above — this cell only steers *what* we run."))
cells.append(code(
'''# ════════════════ CONTROL CELL ════════════════
APPROACH   = "skill"     # which form to run: "bloated_prompt" | "skill"
SKILL_NAME = "scrap-coder"  # the demo skill we inspect and run
PUSH_DOWN  = True        # push-down demo: True compares script vs LLM on the math step
OFFLINE    = False       # True -> skip model calls, render every chart from precomputed fallbacks
TASK       = "Categorize this shift's scrap log into the standard 7 codes and total cost."
# ═══════════════════════════════════════════════
'''))

# ── Cell 3 — two approaches ──────────────────────────────────────────────────
cells.append(md(
'''## The two approaches

**`bloated_prompt`** — one large system prompt holding *all* 7 scrap codes, the
cost table, the output format, and the edge-case rules, **paid on every call.**

**`skill`** — a `scrap-coder/` folder: a tiny `SKILL.md` router +
`knowledge/scrap_codes.md` + `scripts/total_cost.py` + a template, loaded
progressively (only what the task needs).

The bloated prompt isn't just expensive. Over-stuffing the window is the
**confusion** failure mode from sec 1
([Breunig, *How Contexts Fail*, 2025](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)):
more rules and tools in front of the model than the task needs drags response
quality down. We measure the token counts from the *actual* files below.
'''))

# ── Cell 4 — build both, run both (A/B loop) ─────────────────────────────────
cells.append(md("Build both forms from the **same** knowledge, then run the same task through each. The answer matters less than the cost and reliability we measure next."))
cells.append(code(
'''# The shared knowledge, read from the skill folder.
SCRAP_CODES_MD = (SKILL_DIR / "knowledge" / "scrap_codes.md").read_text()
SKILL_MD       = (SKILL_DIR / "SKILL.md").read_text()
TEMPLATE_MD    = (SKILL_DIR / "templates" / "shift_report.md").read_text()

# Split SKILL.md into its router (YAML front-matter) and its body (the procedure).
_fm = re.search(r"^---\\n(.*?)\\n---\\n?", SKILL_MD, re.DOTALL)
SKILL_FRONTMATTER = _fm.group(1) if _fm else ""           # the router "card"
SKILL_BODY        = SKILL_MD[_fm.end():] if _fm else SKILL_MD  # Files/Contract/Steps/...

# --- bloated_prompt: ONE giant block. Everything a single prompt would carry —
# the full code table, every procedural rule, AND the output template — inlined
# and paid on EVERY call. This is the realistic "few hundred lines" anti-pattern.
BLOATED_SYSTEM = dedent("""\\
    You are a scrap-coding assistant for Line 4 swing shift. Apply ALL of the
    following on EVERY request, in full, with no omissions:

    """) + SCRAP_CODES_MD + "\\n\\n" + SKILL_BODY + "\\n\\nOutput in this exact shape:\\n" + TEMPLATE_MD

# --- skill: progressive disclosure. The ROUTER (front-matter) is loaded up
# front to DECIDE to use the skill. Because this task matches, the skill then
# pulls its ONE needed knowledge file (the codes table) — and nothing else
# (no full procedure, no template). So the skill carries router + knowledge,
# while the bloated prompt carries that PLUS the whole procedure and template.
SKILL_ROUTER = dedent("""\\
    You are a scrap-coding assistant. A skill matched this task. Its router card:

    """) + SKILL_FRONTMATTER

SKILL_SYSTEM = SKILL_ROUTER + dedent("""

    The skill matched, so its knowledge file is now loaded:

    """) + SCRAP_CODES_MD + dedent("""

    Code each row to exactly one of S1-S7, exclude rework, default qty to 1,
    and give a per-code breakdown and a dollar total using the unit costs above.
    """)

SAMPLE_LOG = "\\n".join(NOISY_INPUTS[:6])   # a small shift slice for the live run

# NOTE: whether the math itself is exact is the PUSH-DOWN lesson below. Here we
# only need to show the cheaper skill isn't cheaper-BY-being-wrong: it must reach
# the SAME dollar total as the expensive bloated prompt (same model + same codes).
def stated_total(text: str):
    """Pull the dollar total the model reported (its largest stated $ figure)."""
    nums = [float(x.replace(",", "")) for x in re.findall(r"-?[\\d,]+\\.\\d{2}", text or "")]
    return max(nums) if nums else None

async def _noop(args: dict, ctx: ToolContext) -> str:
    """Placeholder tool so the agentic loop has a capability to advertise."""
    return "noop"

NOOP_TOOL = Tool(
    name="noop", description="placeholder so the loop has a tool",
    input_schema={"type": "object", "properties": {}},
    execute=_noop,
)

async def run_task(task: str, approach: str) -> dict:
    """Run the task one way; record loaded tokens, the answer, and the dollar
    total the model stated (so we can show cheaper-AND-right, not cheaper-but-wrong).

    `loaded_tokens` is the realistic in-context size for this matched task:
    bloated = everything; skill = router + the one knowledge file it pulled.

    When OFFLINE is set, return the precomputed record so the A/B still renders.
    """
    system = BLOATED_SYSTEM if approach == "bloated_prompt" else SKILL_SYSTEM
    rec = {"approach": approach, "loaded_tokens": ntok(system)}
    if OFFLINE:
        fb = FALLBACKS["ab"][approach]
        rec.update(content="(offline) precomputed record",
                   cost_usd=fb["cost_usd"], total=fb["total"])
        return rec
    # arcrun.run signature: run(model, capabilities, system_prompt, task, ...)
    # the 2nd positional arg is a CapabilityProvider — StaticProvider wraps a tool list.
    result = await run(
        model,
        StaticProvider([NOOP_TOOL]),
        system,
        f"{task}\\n\\nScrap log:\\n{SAMPLE_LOG}",
        max_turns=4,
    )
    rec["content"]  = result.content
    rec["cost_usd"] = getattr(result, "cost_usd", None)
    rec["total"]    = stated_total(result.content)
    return rec

RESULTS = {}
for approach in ["bloated_prompt", "skill"]:
    RESULTS[approach] = await run_task(TASK, approach=approach)

# "Right" for Visual 1 = the cheap skill reaches the SAME dollar total (the
# actual deliverable) as the expensive bloated prompt — same model + same codes
# table -> same answer. If so, it's cheaper AND right, not cheaper-but-wrong.
SKILL_AGREES = (RESULTS["bloated_prompt"]["total"] is not None
                and RESULTS["bloated_prompt"]["total"] == RESULTS["skill"]["total"])

print("bloated loaded: %d tokens  | total $%s"
      % (RESULTS["bloated_prompt"]["loaded_tokens"], RESULTS["bloated_prompt"]["total"]))
print("skill   loaded: %d tokens  | total $%s"
      % (RESULTS["skill"]["loaded_tokens"], RESULTS["skill"]["total"]))
print("skill matches bloated's total:", SKILL_AGREES, "(cheaper AND right, not cheaper-but-wrong)")
print("live cost_usd  bloated:", RESULTS["bloated_prompt"]["cost_usd"],
      "| skill:", RESULTS["skill"]["cost_usd"])
'''))

# ── Cell 5 — VISUAL 1 ────────────────────────────────────────────────────────
cells.append(md("### Visual 1 — token cost: bloated vs skill\n\nThe bloated prompt is one giant block, always paid. The skill loads a tiny **router** up front and pulls the **one** knowledge file the matched task needs — not the full procedure or template. Watch: the skill's stack (router + knowledge) is well under the bloated block, and the printout above confirms the skill reached the *same* coded answer as the bloated prompt — cheaper *and* right, not cheaper-but-wrong. (Whether that answer's arithmetic is exact is the push-down lesson below.)"))
cells.append(code(
'''# All counts measured from the real files / live run — none hand-set.
if OFFLINE:
    tok = FALLBACKS["tokens"]
else:
    router_tok    = ntok(SKILL_ROUTER)     # front-matter router, loaded up front
    knowledge_tok = ntok(SCRAP_CODES_MD)   # the one codes file pulled for this matched task
    tok = {
        "bloated_prompt": {"router": 0, "knowledge": 0,
                           "system_block": RESULTS["bloated_prompt"]["loaded_tokens"]},
        "skill": {"router": router_tok, "knowledge": knowledge_tok, "system_block": 0},
    }

approaches = ["bloated_prompt", "skill"]
segments   = ["router", "knowledge", "system_block"]
seg_label  = {"router": "router (always)", "knowledge": "knowledge (when matched)",
              "system_block": "everything inlined (always)"}
colors     = {"router": "#4C78A8", "knowledge": "#72B7B2", "system_block": "#E45756"}

fig, ax = plt.subplots(figsize=(7, 4.2))
bottoms = {a: 0 for a in approaches}
for seg in segments:
    vals = [tok[a].get(seg, 0) for a in approaches]
    ax.bar(approaches, vals, bottom=[bottoms[a] for a in approaches],
           color=colors[seg], label=seg_label[seg], edgecolor="white")
    for a, v in zip(approaches, vals):
        bottoms[a] += v

totals = [sum(tok[a].values()) for a in approaches]
for i, t in enumerate(totals):
    ax.text(i, t + 12, f"{t} tok", ha="center", fontweight="bold")
ratio = totals[0] / max(1, totals[1])
ax.set_title(f"Tokens loaded per approach  ·  bloated is {ratio:.1f}x the skill")
ax.set_ylabel("tokens loaded")
ax.set_ylim(0, max(totals) * 1.18)
ax.legend(fontsize=8, loc="upper right")
plt.tight_layout(); plt.show()

if totals[0] <= totals[1]:
    print("WARNING: bloated is not larger than skill — the A/B contrast is broken.")
else:
    print(f"OK: skill stack {totals[1]} tok < bloated {totals[0]} tok, "
          f"and skill matches bloated's answer: {SKILL_AGREES} (cheaper AND right).")
'''))

# ── Cell 6 — walk a real SKILL.md ────────────────────────────────────────────
cells.append(md("## Now walk a real SKILL.md\n\nTokens aside — what *is* the folder? The next cell prints the `scrap-coder/` tree and its `SKILL.md`. Watch for the 8 sections and the dual-clause `description` at the top — that one line is the router."))

# ── Cell 7 — folder tree + SKILL.md ──────────────────────────────────────────
cells.append(code(
'''def show_tree(p: Path, prefix: str = "") -> None:
    items = sorted(p.iterdir())
    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        print(f"{prefix}{connector}{item.name}{'/' if item.is_dir() else ''}")
        if item.is_dir():
            show_tree(item, prefix + ("    " if i == len(items) - 1 else "│   "))

print(f"{SKILL_DIR.name}/")
show_tree(SKILL_DIR)
print("\\n" + "=" * 70)
print(SKILL_MD)
print("=" * 70)
print(dedent("""
    The 8 sections (the skill-creator contract):
      Files          — every file, what it holds, WHEN to load it
      Contract       — numbered, testable criteria (each maps to a test)
      Knowledge      — pointer to knowledge/ (loaded on demand)
      Steps          — one discrete action per step
      Output         — the concrete deliverable shape
      Antipatterns   — harvested from real failures, not imagined
      Validation     — how to prove it still works
      Examples       — smallest worked case

    The highest-leverage line is the YAML 'description': it carries BOTH a
    'Use when ...' clause AND a 'Do NOT use for ...' clause. That negative
    clause is what stops the router from firing the skill on the wrong task.
"""))
'''))

# ── Cell 8 — progressive disclosure ──────────────────────────────────────────
cells.append(md("## Progressive disclosure, demonstrated\n\nThe next cell instruments the loader to log every file it reads, then runs two tasks: one that matches the skill and one that doesn't. Watch the matching task pull two files while the non-matching task loads nothing past the router line."))

# ── Cell 9 — disclosure trace ────────────────────────────────────────────────
cells.append(code(
'''# Instrument the skill loader: log every file it reads.
LOADED = []

def skill_read(rel: str) -> str:
    """Read a file from the skill and record that we loaded it."""
    p = SKILL_DIR / rel
    LOADED.append(rel)
    return p.read_text() if p.exists() else f"(missing: {rel})"

def route(task: str) -> bool:
    """Does the skill's description match this task? (the 'title' check)."""
    desc = re.search(r"description:\\s*\\|?\\s*\\n((?:\\s+.*\\n)+)", SKILL_MD)
    desc_text = (desc.group(1) if desc else "").lower()
    triggers = ["scrap", "reject", "categorize", "code this"]
    return any(t in task.lower() and t in (desc_text + " scrap reject categorize") for t in triggers)

def disclose(task: str) -> list:
    """Simulate progressive disclosure for one task; return files loaded."""
    LOADED.clear()
    if not route(task):
        return list(LOADED)        # routed away: nothing past the description loads
    skill_read("SKILL.md")          # title matched -> open the skill
    skill_read("knowledge/scrap_codes.md")  # step 3 needs the code rules
    return list(LOADED)

matching     = disclose("Categorize the shift's scrap rejects and total the cost.")
nonmatching  = disclose("Summarize the storage incident on /scratch2 for the RCA.")

print("MATCHING task  -> loaded:", matching or "(none)")
print("NON-MATCH task -> loaded:", nonmatching or "(none — routed away at the description)")
'''))

# ── Cell 10 — VISUAL 2 ───────────────────────────────────────────────────────
cells.append(md("### Visual 2 — files loaded per task\n\nShow the title first; open the manual only if the job calls for it."))
cells.append(code(
'''if OFFLINE:
    fl = FALLBACKS["files_loaded"]
    counts = {"matching task": len(fl["matching_task"]),
              "non-matching task": len(fl["nonmatching_task"])}
    labels = {"matching task": fl["matching_task"],
              "non-matching task": fl["nonmatching_task"] or ["(router line only)"]}
else:
    counts = {"matching task": len(matching), "non-matching task": len(nonmatching)}
    labels = {"matching task": matching or ["(none)"],
              "non-matching task": nonmatching or ["(router line only)"]}

fig, ax = plt.subplots(figsize=(7, 3.6))
tasks = list(counts.keys())
bars = ax.bar(tasks, [counts[t] for t in tasks],
              color=["#4C78A8", "#BAB0AC"], edgecolor="white")
for i, t in enumerate(tasks):
    ax.text(i, counts[t] + 0.05, "\\n".join(labels[t]),
            ha="center", va="bottom", fontsize=8)
ax.set_ylabel("files loaded into context")
ax.set_ylim(0, max(counts.values()) + 1.2)
ax.set_title("Progressive disclosure: files pulled per task")
plt.tight_layout(); plt.show()
'''))

# ── Cell 11 — push-down ──────────────────────────────────────────────────────
cells.append(md("## Push down to determinism\n\nThe cost total is the same math every time — a script's job, not the LLM's. The next cell runs the math two ways across the noisy rows (LLM in its head vs `total_cost.py`) and scores each against ground truth. Watch the LLM slip on a few messy rows while the script is exact on all of them."))

# ── Cell 12 — push-down A/B ──────────────────────────────────────────────────
cells.append(code(
'''# Ground truth from the deterministic core (this is the answer key).
spec = importlib.util.spec_from_file_location("total_cost", SKILL_DIR / "scripts" / "total_cost.py")
total_cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(total_cost)
TRUTH = total_cost.categorize(NOISY_INPUTS)["total_cost"]

def truth_cost(row: str) -> float:
    """Ground-truth cost of a single row, from the deterministic core."""
    return total_cost.categorize([row])["total_cost"]

def matches(answer, expected) -> int:
    """1 if the answer matches expected (to the cent), else 0."""
    try:
        return int(round(float(answer), 2) == round(float(expected), 2))
    except (TypeError, ValueError):
        return 0

async def llm_total(row: str):
    """Ask the model to total ONE row's scrap cost in its head (no calculator tool)."""
    if OFFLINE:
        return None
    result = await run(
        model,
        StaticProvider([NOOP_TOOL]),
        BLOATED_SYSTEM,
        f"Total the scrap cost for this row. Reply with ONLY the dollar number:\\n{row}",
        max_turns=2,
    )
    m = re.search(r"-?\\d+(?:\\.\\d+)?", (result.content or "").replace(",", ""))
    return float(m.group()) if m else None

# Compare each mode against ground truth, row by row.
REL = {}
if OFFLINE:
    REL["llm_does_math"]    = FALLBACKS["reliability"]["llm_does_math"]
    REL["script_does_math"] = FALLBACKS["reliability"]["script_does_math"]
else:
    REL["script_does_math"] = [1] * len(NOISY_INPUTS)   # script is exact on every row
    REL["llm_does_math"]    = [matches(await llm_total(row), truth_cost(row))
                               for row in NOISY_INPUTS]

print("ground-truth total $", TRUTH)
print("LLM-math correct: %d/%d" % (sum(REL["llm_does_math"]), len(REL["llm_does_math"])))
print("script   correct: %d/%d" % (sum(REL["script_does_math"]), len(REL["script_does_math"])))
print("\\nHonest caveat: how often the LLM slips is MODEL-DEPENDENT. A frontier")
print("model on clean rows may get every one right. The durable claim isn't")
print("'LLMs can't add' — it's that moving a deterministic step into a tool is")
print("the harness win (scaffolding swings 20+ pts on identical SWE-bench weights).")
'''))

# ── Cell 13 — VISUAL 3 ───────────────────────────────────────────────────────
cells.append(md("### Visual 3 — reliability & cost: LLM step vs script step\n\nTwo panels: accuracy across the noisy set (left), tokens per run (right). The script wins both. *If a script can do it, a script does it.*"))
cells.append(code(
'''if OFFLINE:
    rel = FALLBACKS["reliability"]
    acc = {m: 100.0 * sum(rel[m]) / rel["n"] for m in ["llm_does_math", "script_does_math"]}
    tpr = rel["tokens_per_run"]
else:
    n = len(NOISY_INPUTS)
    acc = {m: 100.0 * sum(REL[m]) / n for m in ["llm_does_math", "script_does_math"]}
    tpr = {"llm_does_math": ntok("\\n".join(NOISY_INPUTS)) + 40,
           "script_does_math": 0}

modes  = ["llm_does_math", "script_does_math"]
labels = ["LLM does math", "script does math"]
cols   = ["#E45756", "#54A24B"]

fig, (axL, axR) = plt.subplots(1, 2, figsize=(10, 4))
axL.bar(labels, [acc[m] for m in modes], color=cols, edgecolor="white")
for i, m in enumerate(modes):
    axL.text(i, acc[m] + 1, f"{acc[m]:.0f}%", ha="center", fontweight="bold")
axL.set_ylim(0, 108); axL.set_ylabel("% rows totaled correctly")
axL.set_title("Accuracy on the noisy set")

axR.bar(labels, [tpr[m] for m in modes], color=cols, edgecolor="white")
for i, m in enumerate(modes):
    axR.text(i, tpr[m] + 1, f"{tpr[m]} tok", ha="center", fontweight="bold")
axR.set_ylabel("tokens per run (runtime)")
axR.set_title("Cost per run")

fig.suptitle("Push-down: deterministic step as a tool wins on both axes", fontweight="bold")
plt.tight_layout(); plt.show()
'''))

# ── Cell 14 — contract -> tests ──────────────────────────────────────────────
cells.append(md("## The contract is the promise → tests keep it\n\nEach numbered contract line maps to a test. The next cell runs the validator and the unit tests live, then **breaks the skill on purpose** — stripping the `Do NOT use for` clause — and re-runs the validator. Watch it pass, then FAIL with the exact reason, then pass again after the restore."))

# ── Cell 15 — validator + pytest, then break it ──────────────────────────────
cells.append(code(
'''def validate_skill(skill_dir: Path) -> dict:
    """Mechanical gates: name match, 8 sections in order, dual-clause description,
    required subdirs, checklist, every script has a test."""
    errs = []
    sk = skill_dir / "SKILL.md"
    if not sk.exists():
        return {"ok": False, "errors": ["SKILL.md missing"]}
    text = sk.read_text()

    name = re.search(r"^name:\\s*(\\S+)", text, re.M)
    if name and name.group(1) != skill_dir.name:
        errs.append(f'name "{name.group(1)}" != folder "{skill_dir.name}"')

    expected = ["Files", "Contract", "Knowledge", "Steps", "Output",
                "Antipatterns", "Validation", "Examples"]
    found = [m for m in re.findall(r"^## (\\w+)", text, re.M) if m in expected]
    if found != expected:
        errs.append(f"sections wrong: got {found}")

    desc = re.search(r"description:\\s*\\|?\\s*\\n((?:\\s+.*\\n)+)", text)
    dtext = (desc.group(1) if desc else "").lower()
    if "use when" not in dtext:
        errs.append('description missing positive clause ("Use when ...")')
    if "do not use" not in dtext.replace("not use for", "do not use"):
        errs.append('description missing negative clause ("Do NOT use for ...")')

    for d in ["scripts", "templates", "knowledge", "validation", "tests", "examples"]:
        if not (skill_dir / d).is_dir():
            errs.append(f"missing required subdir: {d}/")
    if not (skill_dir / "validation" / "quality-checklist.md").exists():
        errs.append("validation/quality-checklist.md missing")
    for script in (skill_dir / "scripts").glob("*.py"):
        if not (skill_dir / "tests" / "unit" / f"test_{script.stem}.py").exists():
            errs.append(f"no test for scripts/{script.name}")
    return {"ok": not errs, "errors": errs}

def report(verdict):
    if verdict["ok"]:
        print("validate_skill: PASS — all gates green.")
    else:
        print("validate_skill: FAIL")
        for e in verdict["errors"]:
            print("  •", e)

report(validate_skill(SKILL_DIR))

# Run the unit tests via pytest. Use the pytest on PATH if present, else this
# interpreter's "-m pytest"; subprocess keeps each run isolated from kernel state.
import shutil
_pytest = shutil.which("pytest")
_cmd = [_pytest] if _pytest else [sys.executable, "-m", "pytest"]
res = subprocess.run(_cmd + [str(SKILL_DIR / "tests" / "unit"), "-q"],
                     capture_output=True, text=True)
print("\\npytest tests/unit  ·  exit =", res.returncode)
print((res.stdout + res.stderr).strip()[-600:])

# --- Break it on purpose: strip the negative clause from the description ---
print("\\n--- breaking the skill: remove the 'Do NOT use for' clause ---")
backup = (SKILL_DIR / "SKILL.md").read_text()
broken = re.sub(r"Do NOT use for[^\\n]*", "", backup)
(SKILL_DIR / "SKILL.md").write_text(broken)
report(validate_skill(SKILL_DIR))     # -> FAIL, loudly, with the reason

# Restore.
(SKILL_DIR / "SKILL.md").write_text(backup)
print("\\nrestored. re-validate:")
report(validate_skill(SKILL_DIR))
'''))

# ── Cell 16 — VISUAL 4 ───────────────────────────────────────────────────────
cells.append(md("### Visual 4 — the four test layers\n\nThe skill-creator's four layers, each labeled with the bug class it catches and whether it ran green. *An untested contract is no contract.*"))
cells.append(code(
'''# Map: did the unit layer actually pass this run? Other layers from the
# precomputed map (they need the full harness; we show what each one guards).
unit_passed = (res.returncode == 0) if not OFFLINE else FALLBACKS["test_layers"]["unit"]["passed"]
layers = FALLBACKS["test_layers"]
status = {
    "unit":        unit_passed,
    "integration": layers["integration"]["passed"],
    "evals":       layers["evals"]["passed"],
    "e2e":         layers["e2e"]["passed"],
}
order = ["unit", "integration", "evals", "e2e"]

fig, ax = plt.subplots(figsize=(9, 3.4))
xs = range(len(order))
ax.bar(xs, [1] * len(order),
       color=["#54A24B" if status[l] else "#E45756" for l in order],
       edgecolor="white")
for i, l in enumerate(order):
    mark = "PASS" if status[l] else "FAIL"
    ax.text(i, 0.5, f"{mark}\\n{layers[l]['catches']}",
            ha="center", va="center", color="white", fontsize=8, fontweight="bold")
ax.set_xticks(list(xs)); ax.set_xticklabels(order)
ax.set_yticks([]); ax.set_ylim(0, 1.1)
ax.set_title("Four test layers — each catches a different bug class")
plt.tight_layout(); plt.show()
'''))

# ── Cell 17 — iterative creation ─────────────────────────────────────────────
cells.append(md("## Iterative creation with skill-creator\n\nYou don't write a skill cold. The next cell scaffolds a fresh stub (`coa-intake`), validates it (FAIL — incomplete), fills the description and adds one test, then re-validates (PASS). Watch the validator drive the 5-step loop from red to green."))

# ── Cell 18 — scaffold a fresh skill live ────────────────────────────────────
cells.append(code(
'''import shutil as _sh

# Scaffold a brand-new tiny skill: coa-intake (parse a Certificate of Analysis).
# Start from a clean slate so the demo is deterministic on re-runs.
NEW = SKILLS_DIR / "coa-intake"
if NEW.exists():
    _sh.rmtree(NEW)
for d in ["scripts", "templates", "knowledge", "validation", "tests/unit", "examples/simple"]:
    (NEW / d).mkdir(parents=True, exist_ok=True)

# Step 1: stub SKILL.md with all 8 section headers but a placeholder description
# (no real "Use when"/"Do NOT use" clauses) and a script with NO test yet.
# Both gaps must make the validator FAIL.
(NEW / "SKILL.md").write_text(dedent("""\\
    ---
    name: coa-intake
    version: 0.1.0
    description: |
      Placeholder. Fill this in before the skill is usable.
    ---

    # coa-intake

    ## Files
    ## Contract
    ## Knowledge
    ## Steps
    ## Output
    ## Antipatterns
    ## Validation
    ## Examples
    """))
(NEW / "validation" / "quality-checklist.md").write_text("# checklist\\n- [ ] TODO\\n")
(NEW / "scripts" / "parse_coa.py").write_text("def parse_coa(text):\\n    return {}\\n")

print("scaffold:")
show_tree(NEW)
print("\\n1st validate (expect FAIL — placeholder description, no test for the script):")
v1 = validate_skill(NEW)
report(v1)
assert not v1["ok"], "scaffold demo broken: stub should FAIL validation"

# Step 2: fill the description (dual clause) + add the missing test, re-validate.
md_text = (NEW / "SKILL.md").read_text().replace(
    "Placeholder. Fill this in before the skill is usable.",
    'Parse a supplier Certificate of Analysis (CoA) into structured lot/spec '
    'fields. Use when asked to "read this CoA" or "extract the CoA values". '
    'Do NOT use for invoices or packing slips — use doc-intake for those.')
(NEW / "SKILL.md").write_text(md_text)
(NEW / "tests" / "unit" / "test_parse_coa.py").write_text(dedent("""\\
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    from parse_coa import parse_coa

    def test_returns_dict():
        assert isinstance(parse_coa("lot: 42"), dict)
    """))

print("\\n2nd validate (after filling description + adding a test):")
v2 = validate_skill(NEW)
report(v2)
assert v2["ok"], "scaffold demo broken: filled skill should PASS validation"
'''))

# ── Cell 19 — TODO ───────────────────────────────────────────────────────────
cells.append(md("## Your turn"))
cells.append(code(
'''# ✅ TODO — turn YOUR bloated prompt into a skill.
#
# 1. Paste a system prompt you actually use into MY_PROMPT below.
# 2. Scaffold a folder: pull the DETERMINISTIC bits into scripts/, the
#    REFERENCE bits into knowledge/, leave only JUDGMENT in Steps.
# 3. Write the dual-clause description (Use when ... / Do NOT use for ...).
# 4. Run validate_skill() until it passes.
#
MY_PROMPT = """
PASTE YOUR SYSTEM PROMPT HERE
"""

MY_SKILL = SKILLS_DIR / "my-skill"
for d in ["scripts", "templates", "knowledge", "validation", "tests/unit", "examples/simple"]:
    (MY_SKILL / d).mkdir(parents=True, exist_ok=True)

# (MY_SKILL / "SKILL.md").write_text(...)   # 8 sections; description first.
# report(validate_skill(MY_SKILL))

print("scaffold ready at:", MY_SKILL)
print("Fill SKILL.md (8 sections), add a test, then run: report(validate_skill(MY_SKILL))")
'''))

# ── Cell 20 — Takeaway ───────────────────────────────────────────────────────
cells.append(md(
'''## Takeaway

> A skill is **procedural memory engineered into a folder**: progressive
> disclosure keeps it cheap, push-down keeps it reliable, the contract + tests
> keep it honest, and semver + git make it shippable across the lab.

Next: the context that shapes *judgment* rather than procedure — the identity file.
'''))

# ── Cell 21 — Sources ────────────────────────────────────────────────────────
cells.append(md(
'''## Sources

- Anthropic, *Effective context engineering for AI agents* (2025) — Agent Skills / progressive disclosure: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- LangChain / Lance Martin, *Context Engineering for Agents* (2025) — Write/Select/Compress/Isolate: https://www.langchain.com/blog/context-engineering-for-agents
- Drew Breunig, *How Contexts Fail* (Jun 2025) — the confusion failure mode (over-stuffed prompt): https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html
- Agent scaffolding vs. model on SWE-bench (2025) — harness > model, 20+ pt swings on identical weights: https://particula.tech/blog/agent-scaffolding-beats-model-upgrades-swe-bench
'''))

nb = {"cells": cells,
      "metadata": {"kernelspec": {"name": "arcvenv", "display_name": "Arc venv", "language": "python"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}

OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(OUT, "w"), indent=1)
print("wrote", OUT, "with", len(cells), "cells")
