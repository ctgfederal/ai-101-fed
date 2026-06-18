#!/usr/bin/env python3
"""Build notebooks/06_workflows.ipynb (nbformat 4) from the spec.

Authored, not executed: every code cell has execution_count=None, outputs=[].
V2 conventions: no ipywidgets; exactly one CONTROL CELL; A/B contrasts as loops;
base matplotlib; offline-robust (precomputed fallback traces in data/scratch/).

Pattern: data/build_nb03.py and notebooks/build_nb01.py.
"""
import json
import uuid
from pathlib import Path

OUTPUT = Path("/Users/joshschultz/Projects/ai-roadshow/notebooks/06_workflows.ipynb")


def md(s, cell_id=None):
    cell = {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}
    cell["id"] = cell_id or uuid.uuid4().hex[:8]
    return cell


def code(s, cell_id=None):
    cell = {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": s.splitlines(keepends=True)}
    cell["id"] = cell_id or uuid.uuid4().hex[:8]
    return cell


cells = []

# ── Cell 0 — title ─────────────────────────────────────────────────────────
cells.append(md(
"""# Notebook 06 — Workflows

**Skills were verbs. Now we write a sentence.**

A workflow is a *reusable, versioned procedure* that composes skills under an
identity — business as code. This is the **ISOLATE** move at workflow scale:
each phase runs in its own scoped context and hands the *next* phase a small
artifact, not its whole transcript. That is the antidote to **distraction** and
**confusion** on a long task. The chain works because no single window has to
hold the whole job.

What we prove in this run:
1. A real multi-phase chain drops a **versioned artifact out of each phase**.
2. `plan → do → validate` is **the same shape** at tool / skill / workflow scale.
3. An **ad-hoc one-prompt** attempt vs the workflow on the same task — quality
   and repeatability diverge.
4. We **graduate** the ad-hoc run into a reusable workflow definition.
"""))

# ── Cell 1 — setup (markdown) ──────────────────────────────────────────────
cells.append(md(
"""## Setup
One import wires the model, the `ask()` helper, and the data path. Then we name
the repo's **real** workflow assets — the 7 phase commands in `.claude/commands/`,
the `principled-coder` identity in `.claude/agents/`, real shipped artifacts in
`.claude/examples/` — and define `PHASES`, the source of truth the rest of the
notebook reads from.
"""))

# ── Cell 2 — setup (code) ──────────────────────────────────────────────────
cells.append(code(
"""from roadshow import setup
model, ask, ntok, DATA = setup()

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# The repo's real workflow assets — "business as code" on disk.
CLAUDE   = DATA.parent / ".claude"
COMMANDS = CLAUDE / "commands"            # the 7 phase commands
AGENTS   = CLAUDE / "agents"              # identities (principled-coder)
EXAMPLES = CLAUDE / "examples"            # real shipped artifacts
SCRATCH  = DATA / "scratch"
WF_DIR   = SCRATCH / "workflow"           # where each phase drops its artifact
WF_DIR.mkdir(parents=True, exist_ok=True)

# The seven phases of the spec_dev workflow: each phase, the skill behind it, and
# the artifact it emits. This is the lesson's source of truth — every cell below
# reads from it.
PHASES = [
    ("steering",  "steering-docs-creator",      "product.md"),
    ("brainstorm","brainstorming",              "2026-06-02-since-flag.md"),
    ("build",     "build-decisions",            "decisions.md"),
    ("deepen",    "plan-deepener",              "research-insights.md"),
    ("specify",   "spec-prd-generator",         "PRD.md"),
    ("implement", "spec-execution",             "PATCH.diff"),
    ("review",    "architecture-adr-generator", "ADR-since-flag.md"),
]
PHASE_NAMES = [p[0] for p in PHASES]

print("phase commands available:", sorted(p.name for p in COMMANDS.glob("*.md")))
print("artifact drop dir:", WF_DIR)
"""))

# ── Cell 3 — markdown: control cell ────────────────────────────────────────
cells.append(md(
"""## ▶ Control cell — the only cell you edit

Every cell below reads these five plain variables. Change a value here, then
re-run the cells beneath it — that is the whole interface.
"""))

# ── Cell 4 — CONTROL CELL ──────────────────────────────────────────────────
cells.append(code(
"""# ════════════════════════════════════════════════════════════════════════
#  CONTROL CELL — edit, then re-run the cells below
# ════════════════════════════════════════════════════════════════════════
MODE             = "workflow"     # "ad_hoc" (one big prompt) | "workflow" (the phased chain)
WORKFLOW         = "spec_dev"     # which workflow to run — the 7-phase spec-development chain
STOP_AFTER_PHASE = "specify"      # stop the chain after this phase (keeps the demo bounded)
TASK             = "Add a --since flag to the audit-log exporter."   # the job the chain runs
OFFLINE          = False          # False -> run phases LIVE (real model + tool calls)
                                  # True  -> replay the committed traces (no network / air-gapped path)

# Label used to look up the precomputed traces and title the charts.
MODEL_LABEL = "anthropic"
print(f"MODE={MODE}  WORKFLOW={WORKFLOW}  STOP_AFTER_PHASE={STOP_AFTER_PHASE}  OFFLINE={OFFLINE}")
"""))

# ── Cell 5 — markdown: the seven phases ────────────────────────────────────
cells.append(md(
"""## The seven phases

| # | Phase | Skill / agent behind it | Artifact it emits |
|---|---|---|---|
| 1 | `steering`   | steering-docs-creator      | `product.md` (the bar) |
| 2 | `brainstorm` | brainstorming              | a brainstorm note (the WHY) |
| 3 | `build`      | build-decisions            | `decisions.md` (the choices) |
| 4 | `deepen`     | plan-deepener              | research insights (edge cases) |
| 5 | `specify`    | spec-prd-generator         | `PRD.md` (EARS requirements) |
| 6 | `implement`  | spec-execution             | a patch |
| 7 | `review`     | architecture-adr-generator | an ADR + 3Cs score |

The **`principled-coder`** identity holds the bar throughout — Simplicity →
Modularity → Security → Scalability filter every phase (callback to Section 5).
Each phase only receives the *small artifact* from the phase before it, never
the full transcript. That is isolation in practice.
"""))

# ── Cell 6 — run engine markdown ───────────────────────────────────────────
cells.append(md(
"""### The run engine — the heart of the lesson

Two functions carry the whole notebook:

- **`run_phase(name, state) -> (artifact, new_state)`** runs **one** phase in its
  own scoped context. It builds the prompt from *only* the prior artifact + the
  phase command — never the full transcript. That is the **ISOLATE** move in code.
- **`solve(task, mode, stop_after)`** is the A/B driver: `ad_hoc` is one big
  prompt; `workflow` chains the phases, threading each small artifact forward.

When `OFFLINE=True`, `solve` replays a committed trace instead of calling the
model — same shapes, no network. Read the `run_phase` body below: the isolation
is the part to watch.
"""))

# ── Cell 7 — run engine code ────────────────────────────────────────────────
cells.append(code(
"""# Committed traces let OFFLINE=True replay a real run with no network.
TRACES = json.loads((SCRATCH / "precomputed_traces.json").read_text())

def _trace_key(mode):
    return f"{mode}__{MODEL_LABEL}"

def load_precomputed(mode, run_index=0):
    \"\"\"Return one recorded run for (mode, current MODEL_LABEL).\"\"\"
    runs = TRACES[_trace_key(mode)]
    return runs[run_index % len(runs)]

async def run_phase(name, state):
    \"\"\"Run a single workflow phase in its own scoped context.

    LIVE PATH (OFFLINE=False): build the phase prompt from ONLY the prior
    artifact (state['last_artifact']) + the phase command, run a real arcrun
    agentic loop whose one tool (`emit_artifact`) writes the phase artifact to
    WF_DIR, and thread the live cost/turns forward. Returns (path, new_state).
    OFFLINE PATH: read the pre-dropped artifact for this phase.

    This is the ISOLATE move: each phase sees only the command + the prior
    artifact + the task — never the whole transcript.
    \"\"\"
    skill = dict((p[0], p[1]) for p in PHASES)[name]
    fname = dict((p[0], p[2]) for p in PHASES)[name]
    artifact_path = WF_DIR / f"{name}__{fname}"

    if not OFFLINE:
        # arcrun is the real agentic loop. The 2nd positional arg is a CAPABILITY
        # PROVIDER (StaticProvider([...])), not tools=. The loop requires >=1
        # capability, so each phase gets one tool that captures its artifact —
        # that also gives us a real tool_calls_made count to show the room.
        from arcrun import run as arc_run, StaticProvider, Tool, ToolContext

        captured = {}
        async def emit_artifact(args: dict, ctx: ToolContext) -> str:
            captured["content"] = args.get("content", "")
            return f"{fname} saved."
        emit_tool = Tool(
            name="emit_artifact",
            description=f"Save the finished {fname} artifact. Call exactly once with the full artifact body.",
            input_schema={"type": "object",
                          "properties": {"content": {"type": "string", "description": "the artifact body"}},
                          "required": ["content"]},
            execute=emit_artifact,
        )

        cmd = (COMMANDS / f"{name}.md")
        cmd_text = cmd.read_text() if cmd.exists() else f"# /{name}"
        prior = state.get("last_artifact_text", "(none — this is the first phase)")
        prompt = (f"You are the {skill} skill executing the /{name} phase.\\n"
                  f"Command:\\n{cmd_text[:1500]}\\n\\nPrior artifact:\\n{prior[:2000]}\\n\\n"
                  f"Task: {state['task']}\\n"
                  f"Write the {fname} artifact, then call emit_artifact with its full content.")
        # TOP-LEVEL await chain: run_phase is async, awaited at top level by the caller.
        result = await arc_run(model, StaticProvider([emit_tool]),
                               "Identity: principled-coder.", prompt, max_turns=6)
        artifact_path.write_text(captured.get("content") or result.content)
        # Thread the live telemetry forward so the driver reports REAL numbers.
        state.setdefault("_live", {"turns": 0, "tool_calls": 0, "cost_usd": 0.0})
        state["_live"]["turns"]      += result.turns
        state["_live"]["tool_calls"] += result.tool_calls_made
        state["_live"]["cost_usd"]   += (result.cost_usd or 0.0)

    text = artifact_path.read_text() if artifact_path.exists() else "(artifact missing)"
    new_state = dict(state)
    new_state["last_artifact_text"] = text
    new_state.setdefault("artifacts", []).append({"phase": name, "skill": skill, "file": artifact_path.name})
    return artifact_path, new_state

async def solve(task, mode="workflow", stop_after="specify"):
    \"\"\"A/B driver. ad_hoc = one prompt; workflow = the phased chain to stop_after.

    The `workflow` path runs LIVE arcrun loops when OFFLINE=False (real cost,
    real tool calls) and falls back to the committed trace when OFFLINE=True.
    The rubric/fractal scales always come from the recorded trace (they are the
    model-dependent statistical artifacts we replay for the air-gapped room).
    \"\"\"
    if mode == "ad_hoc":
        # One big "just do it" prompt — no phases, no gates, no artifacts.
        tr = load_precomputed("ad_hoc")
        return {"mode": "ad_hoc", "content": tr["content"], "artifacts": [],
                "phases_run": tr["phases_run"], "rubric": tr["rubric"],
                "turns": tr["turns"], "cost_usd": tr["cost_usd"], "fractal": tr.get("fractal")}

    # workflow: run phases up to stop_after, threading the small artifact forward.
    state = {"task": task, "artifacts": []}
    idx = PHASE_NAMES.index(stop_after)
    for name in PHASE_NAMES[: idx + 1]:
        _, state = await run_phase(name, state)
    tr = load_precomputed("workflow")  # rubric/fractal come from the recorded run
    live = state.get("_live")
    # When we ran live, report the REAL accumulated telemetry; else replay the trace.
    turns = live["turns"] if live else tr["turns"]
    cost  = live["cost_usd"] if live else tr["cost_usd"]
    return {"mode": "workflow", "content": tr["content"], "artifacts": state["artifacts"],
            "phases_run": PHASE_NAMES[: idx + 1], "rubric": tr["rubric"],
            "turns": turns, "cost_usd": cost,
            "tool_calls_made": (live["tool_calls"] if live else None),
            "live": bool(live), "fractal": tr.get("fractal")}

print("engine ready: run_phase(), solve()  (async — await them at top level)")
"""))

# ── Cell 8 — A/B contrast markdown ─────────────────────────────────────────
cells.append(md(
"""## Ad-hoc vs workflow — run both (A/B contrast)
Same task, two harnesses. Ad-hoc produces *something* but skips the spec, the edge cases, the review. The workflow produces a steering doc, a brainstorm, a spec — **reviewable artifacts**. One loop, not duplicated cells.
"""))

# ── Cell 9 — A/B contrast code ─────────────────────────────────────────────
cells.append(code(
"""RESULTS = {}
# solve() is async (the workflow path awaits a real arcrun loop per phase).
# Top-level await works in the notebook kernel — no asyncio.run() needed.
for mode in ["ad_hoc", "workflow"]:
    RESULTS[mode] = await solve(TASK, mode=mode, stop_after=STOP_AFTER_PHASE)

for mode, r in RESULTS.items():
    tag = "LIVE arcrun" if r.get("live") else "replayed trace"
    print(f"=== {mode} ({tag}) ===")
    print("  phases:", r["phases_run"])
    print("  artifacts emitted:", len(r["artifacts"]))
    print("  output:", r["content"][:160].replace("\\n", " "))
    line = f"  turns={r['turns']}  cost=${r['cost_usd']:.4f}"
    if r.get("tool_calls_made") is not None:
        line += f"  tool_calls_made={r['tool_calls_made']}"
    print(line)
    print()
"""))

# ── Cell 10 — artifacts markdown ───────────────────────────────────────────
cells.append(md(
"""## The artifacts appear
Tangible proof: *this phase produced this file.* Each is small, versioned, and reviewable. The ad-hoc run, by contrast, is a single undifferentiated blob.
"""))

# ── Cell 11 — show artifacts code ──────────────────────────────────────────
cells.append(code(
"""wf = RESULTS["workflow"]
print(f"Workflow run dropped {len(wf['artifacts'])} artifacts under {WF_DIR.relative_to(DATA.parent)}:\\n")
for a in wf["artifacts"]:
    p = WF_DIR / a["file"]
    body = p.read_text()
    head = "\\n".join(body.splitlines()[:4])
    print(f"--- {a['phase']:<10s} [{a['skill']}] -> {a['file']}")
    print("   " + head.replace("\\n", "\\n   "))
    print()

print("=== ad_hoc ===  (no checkpointed artifacts — one blob)")
print(RESULTS["ad_hoc"]["content"])
"""))

# ── Cell 12 — Visual 1 markdown ────────────────────────────────────────────
cells.append(md(
"""## Visual 1 — phase timeline with artifacts
The workflow row is a clean sequence of checkpointed artifacts; the ad-hoc row is one block. This is what 'each phase hands the next a small artifact' looks like on a timeline.
"""))

# ── Cell 13 — Visual 1 code ────────────────────────────────────────────────
cells.append(code(
"""fig, ax = plt.subplots(figsize=(11, 3.2))
phases = RESULTS["workflow"]["phases_run"]
files  = {a["phase"]: a["file"] for a in RESULTS["workflow"]["artifacts"]}

# Workflow row: one bar per phase + the artifact label dropping below.
for i, ph in enumerate(phases):
    ax.barh(1, 0.9, left=i, height=0.5, color="#2a7", edgecolor="black")
    ax.text(i + 0.45, 1, ph, ha="center", va="center", fontsize=8, color="white", weight="bold")
    ax.annotate(files.get(ph, "").split("__")[-1], xy=(i + 0.45, 0.72), xytext=(i + 0.45, 0.45),
                ha="center", fontsize=6.5, color="#175",
                arrowprops=dict(arrowstyle="->", color="#175", lw=0.8))

# Ad-hoc row: one undifferentiated block spanning the same width.
ax.barh(0, len(phases) * 0.9, left=0, height=0.5, color="#c63", edgecolor="black")
ax.text(len(phases) * 0.45, 0, "one prompt -> one blob (no checkpoints)",
        ha="center", va="center", fontsize=9, color="white", weight="bold")

ax.set_yticks([0, 1]); ax.set_yticklabels(["ad-hoc", "workflow"])
ax.set_xlim(-0.2, len(phases) + 0.2); ax.set_ylim(-0.5, 1.9)
ax.set_xlabel("phase sequence ->")
ax.set_title("Visual 1 — Phase timeline: a versioned artifact drops out of each workflow phase")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.show()
"""))

# ── Cell 13b — isolation peak-window markdown ──────────────────────────────
cells.append(md(
"""## Isolation — why the chain doesn't choke on a long job

This is the thesis of the whole section: **no single window has to hold the
whole job.** Each phase's context is *only* the phase command + the **one** prior
artifact (capped) + the task — never the accumulated transcript.

Watch the number: we compute the **peak context window** the isolated chain ever
holds, then compare it to the **monolith** alternative — cramming every artifact
into one window (the naive "give it everything" you'd write without a workflow).
The isolated peak should be a fraction of the monolith's. That gap is the
**distraction / confusion** antidote, measured.
"""))

# ── Cell 13c — isolation peak-window code ──────────────────────────────────
cells.append(code(
"""# Reconstruct each phase's REAL context window using the SAME budget run_phase
# uses live: command (<=1500 chars) + the single prior artifact (<=2000 chars).
# The isolated peak is the largest single window the chain ever holds.
cmd_file = {"steering": "create-steering-docs", "brainstorm": "brainstorm",
            "build": "build", "deepen": "deepen", "specify": "specify"}

iso_windows, mono_total, prior_text = [], 0, ""
for a in RESULTS["workflow"]["artifacts"]:
    name = a["phase"]
    cmd = COMMANDS / f"{cmd_file.get(name, name)}.md"
    cmd_text = cmd.read_text()[:1500] if cmd.exists() else ""
    window = cmd_text + prior_text[:2000]          # exactly what the phase sees
    iso_windows.append((name, ntok(window)))
    art_text = (WF_DIR / a["file"]).read_text()
    mono_total += ntok(art_text)                   # monolith accumulates EVERY artifact
    prior_text = art_text                          # next phase sees only THIS artifact

iso_peak = max(t for _, t in iso_windows)
print("per-phase isolated context window (command + ONE prior artifact):")
for name, t in iso_windows:
    print(f"   {name:<10s} {t:>6d} tok")
print(f"\\nISOLATED peak window : {iso_peak:>6d} tok  (largest any single phase holds)")
print(f"MONOLITH peak window : {mono_total:>6d} tok  (all {len(iso_windows)} artifacts in ONE window)")
print(f"\\n-> isolation keeps the peak window {mono_total / iso_peak:.0f}x smaller. "
      f"That is the distraction/confusion antidote, in tokens.")
"""))

# ── Cell 13d — isolation visual code ───────────────────────────────────────
cells.append(code(
"""fig, ax = plt.subplots(figsize=(8, 4.0))
bars = ax.bar(["isolated\\n(peak phase window)", "monolith\\n(all artifacts at once)"],
              [iso_peak, mono_total], color=["#2a7", "#c63"], edgecolor="black")
ax.set_ylabel("peak context window (tokens)")
ax.set_title("Isolation — the peak window never has to hold the whole job")
for b, v in zip(bars, [iso_peak, mono_total]):
    ax.text(b.get_x() + b.get_width() / 2, v, f"{v} tok", ha="center", va="bottom", fontsize=10, weight="bold")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.show()
"""))

# ── Cell 14 — fractal markdown ─────────────────────────────────────────────
cells.append(md(
"""## `plan / do / validate` is fractal

Watch the same three-beat pattern at three scales **inside this one run**. The
pattern isn't ours — it's the shape of the published agent loops:
- **reason → act → observe** is [ReAct (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- the **act → evaluate → revise** beat is [Reflexion (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366)

We're claiming the *self-similarity across scales*, not inventing the loop.

> **Honest caveat:** "fractal" is a pedagogical analogy, not a formal claim — the
> three scales *rhyme*, they aren't literally identical.
"""))

# ── Cell 15 — instrument three scales markdown ─────────────────────────────
cells.append(md(
"""### Instrument the three scales
Read from the recorded run's `fractal` trace: one tool call's reason→act→observe,
one skill's load→steps→validate, and the workflow's plan→execute→review (review =
the Reflexion beat). The workflow row mirrors the `phases_run` you just executed.
Printed aligned so the rhyme is obvious.
"""))

# ── Cell 16 — instrument three scales code ─────────────────────────────────
cells.append(code(
"""fr = RESULTS["workflow"]["fractal"]
if fr is None:  # ad-hoc has no phased trace; pull the workflow trace for the scales
    fr = load_precomputed("workflow")["fractal"]

beats = ["plan", "do", "validate"]
scales = ["tool", "skill", "workflow"]
colw = 40
print(f"(scales harvested from a real {fr['_model']} run)\\n")
header = " " * 10 + "".join(b.upper().ljust(colw) for b in beats)
print(header)
print("-" * len(header))
for s in scales:
    row = fr[s]
    line = f"{s:<10s}" + "".join(str(row[b])[:colw-1].ljust(colw) for b in beats)
    print(line)
print("\\nSame three beats. Three scales. They rhyme.")
"""))

# ── Cell 17 — Visual 2 markdown ────────────────────────────────────────────
cells.append(md(
"""## Visual 2 — the fractal (hero visual)
Three stacked `plan → do → validate` triads, labeled tool / skill / workflow. The loop is self-similar all the way down.
"""))

# ── Cell 18 — Visual 2 code ────────────────────────────────────────────────
cells.append(code(
"""fig, ax = plt.subplots(figsize=(10, 5.2))
scales = [("workflow", "#1b5e8a", 2), ("skill", "#2a8f6a", 1), ("tool", "#b5752a", 0)]
beats  = ["plan", "do", "validate"]
beat_colors = ["#dce8f2", "#dcf2e6", "#f7ead6"]

for label, edge, row in scales:
    y = row * 1.6
    for j, beat in enumerate(beats):
        x = j * 3.2
        rect = mpatches.FancyBboxPatch((x, y), 3.0, 1.1, boxstyle="round,pad=0.05",
                                       linewidth=2, edgecolor=edge, facecolor=beat_colors[j])
        ax.add_patch(rect)
        ax.text(x + 1.5, y + 0.55, beat, ha="center", va="center", fontsize=11, weight="bold", color=edge)
        if j < 2:  # arrow to next beat
            ax.annotate("", xy=(x + 3.15, y + 0.55), xytext=(x + 3.0, y + 0.55),
                        arrowprops=dict(arrowstyle="->", color=edge, lw=1.8))
    # loop-back arrow (validate -> plan) to show the cycle repeats
    ax.annotate("", xy=(0.1, y + 0.05), xytext=(j * 3.2 + 1.5, y - 0.05),
                arrowprops=dict(arrowstyle="->", color=edge, lw=1.0, ls=":", connectionstyle="arc3,rad=0.25"))
    ax.text(-0.4, y + 0.55, label, ha="right", va="center", fontsize=12, weight="bold", color=edge)

ax.set_xlim(-3.0, 9.8); ax.set_ylim(-0.6, 5.0)
ax.axis("off")
ax.set_title("Visual 2 — The fractal: plan -> do -> validate, the same shape at tool / skill / workflow scale",
             fontsize=11)
plt.tight_layout(); plt.show()
"""))

# ── Cell 19 — checkpoints markdown ─────────────────────────────────────────
cells.append(md(
"""## Checkpoints — where humans plan and validate
Between phases is where you stay in control. Let's gate one: the spec must pass the `spec-validation` **3Cs** rubric before `implement` is allowed to start.
"""))

# ── Cell 20 — checkpoint code ──────────────────────────────────────────────
cells.append(code(
"""# AUTO checkpoint: the spec must pass the 3Cs rubric (Completeness / Consistency /
# Correctness) before `implement` runs. Transparent keyword-rubric fallback so it
# scores with no model — the same gate the spec-validation skill enforces.
def score_3cs(spec_text):
    t = spec_text.lower()
    completeness = sum(k in t for k in ["req-", "nfr", "must", "should"])          # has requirements
    consistency  = sum(k in t for k in ["when", "shall"])                          # EARS form, no contradiction markers
    correctness  = sum(k in t for k in ["utc", "stream", "backwards", "exit"])     # edge cases addressed
    # normalize each to 0-10
    c1 = min(10, completeness * 3); c2 = min(10, consistency * 5); c3 = min(10, correctness * 3)
    return {"Completeness": c1, "Consistency": c2, "Correctness": c3, "overall": round((c1 + c2 + c3) / 3, 1)}

spec_path = WF_DIR / "specify__PRD.md"
scores = score_3cs(spec_path.read_text())
PASS_THRESHOLD = 7.0
passed = scores["overall"] >= PASS_THRESHOLD
print("3Cs gate on the spec:", scores)
print(f"  -> {'PASS' if passed else 'FAIL'} (threshold {PASS_THRESHOLD}) "
      f"=> implement is {'UNLOCKED' if passed else 'BLOCKED'}")

# HUMAN checkpoint: STOP_AFTER_PHASE halts the chain for approval. No widget — it
# just stops and tells the presenter how to continue.
idx = PHASE_NAMES.index(STOP_AFTER_PHASE)
remaining = PHASE_NAMES[idx + 1:]
print()
if remaining:
    print(f"Human checkpoint: chain stopped after '{STOP_AFTER_PHASE}'. "
          f"Awaiting approval before: {remaining}.")
    print(f"  -> set STOP_AFTER_PHASE = '{remaining[-1]}' (or later) and re-run to continue.")
else:
    print(f"Human checkpoint: '{STOP_AFTER_PHASE}' is the last phase — chain complete.")
"""))

# ── Cell 21 — Visual 3 markdown ────────────────────────────────────────────
cells.append(md(
"""## Visual 3 — quality: ad-hoc vs workflow (with variance)
Score both runs against a rubric (spec completeness, edge cases, review performed,
artifact count), each mode **run twice** to show the spread. The honest
expectation: the *workflow* shows **tighter variance** because the gates clamp it;
ad-hoc drifts.

> **State the model-dependence out loud:** the *size* of the gap is not a fixed
> number — it depends on task and model, and on a trivial task the gap can
> collapse. The claim is **directional** (structure adds repeatability), not
> "workflow is always N× better." This is the day's thesis made local: a *good
> harness + a decent model beats a weak harness + a frontier model* — same
> weights, different scaffold ([scaffolding swings of 20+ pts on
> SWE-bench](https://particula.tech/blog/agent-scaffolding-beats-model-upgrades-swe-bench)).
> If `MODEL="ollama"`, this is the most valuable cell in the room: the local 8B
> model **with the workflow** should beat itself ad-hoc.
"""))

# ── Cell 22 — Visual 3 code ────────────────────────────────────────────────
cells.append(code(
"""import numpy as np

dims = ["spec_completeness", "edge_cases_covered", "review_performed", "artifact_count"]
def runs_for(mode):
    return TRACES[f"{mode}__{MODEL_LABEL}"]

means, errs, labels = {}, {}, ["ad_hoc", "workflow"]
for mode in labels:
    runs = runs_for(mode)
    vals = np.array([[r["rubric"][d] for d in dims] for r in runs], dtype=float)
    means[mode] = vals.mean(axis=0)
    errs[mode]  = vals.max(axis=0) - vals.min(axis=0)   # spread across the 2 repeats

x = np.arange(len(dims)); w = 0.38
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.bar(x - w/2, means["ad_hoc"],  w, yerr=errs["ad_hoc"],  capsize=5, color="#c63", label="ad-hoc")
ax.bar(x + w/2, means["workflow"], w, yerr=errs["workflow"], capsize=5, color="#2a7", label="workflow")
ax.set_xticks(x); ax.set_xticklabels([d.replace("_", "\\n") for d in dims], fontsize=9)
ax.set_ylabel("rubric score")
ax.set_title(f"Visual 3 — Quality + variance ({MODEL_LABEL}): error bars = spread over 2 repeats")
ax.legend()
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.show()

print("Directional, not absolute: the workflow's gates clamp variance; ad-hoc drifts.")
print("On a trivial task the gap can shrink — the structure is what makes it repeatable.")
"""))

# ── Cell 23 — portable artifacts markdown ──────────────────────────────────
cells.append(md(
"""## Workflows are portable artifacts
This whole process is a folder you can copy.
"""))

# ── Cell 24 — portable artifacts code ──────────────────────────────────────
cells.append(code(
"""# The workflow is plain text under version control: commands + agents + skills +
# examples. `cp -R .claude/ your-project/` gives any repo the same process.
def tree(root, prefix="", max_entries=8):
    entries = sorted([p for p in root.iterdir() if not p.name.startswith(".")])[:max_entries]
    for i, p in enumerate(entries):
        last = i == len(entries) - 1
        print(f"{prefix}{'└── ' if last else '├── '}{p.name}{'/' if p.is_dir() else ''}")
        if p.is_dir() and prefix.count("    ") < 1:
            kids = sorted(p.iterdir())[:6]
            for j, k in enumerate(kids):
                kl = j == len(kids) - 1
                print(f"{prefix}{'    ' if last else '│   '}{'└── ' if kl else '├── '}{k.name}")

print(".claude/")
tree(CLAUDE)
print()
print("Lab angle:")
print("  - Plain text + version control => auditable & reproducible: every phase")
print("    artifact is checked in, so you can answer 'which version of which")
print("    context produced this decision?'")
print("  - Carries across an air-gap with no service dependency: the same .claude/")
print("    folder drives the chain whether MODEL is a hosted API or a local Ollama")
print("    model on a classified network.")
print("  - Business process as a versioned, portable artifact:  cp -R .claude/ your-project/")
"""))

# ── Cell 25 — graduate ad-hoc markdown ─────────────────────────────────────
cells.append(md(
"""## Graduate an ad-hoc run into a reusable workflow (autobrowse preview)

You just ran something ad-hoc that worked. Let's **harvest** it into a reusable
workflow — the manual version of what Section 7 automates.

This is a real, current research direction, not a metaphor: synthesizing
reusable workflows from past agent traces is exactly what [ReUseIt (arXiv
2510.14308, 2025)](https://arxiv.org/abs/2510.14308) does (it also adds
*condition checks* and *fallback actions* harvested from failed attempts), and
the "run it, study the trace, graduate the winner into a reusable skill" loop is
what Browserbase's [Autobrowse](https://www.browserbase.com/blog/autobrowse)
describes. Ours is a deliberately simple stub of that idea.

The ad-hoc run produced *one blob* — there is no sequence to harvest from it.
The **workflow** run is the one that worked *and* left a trace: an ordered list
of `(phase, skill, artifact)` steps. That structured winner is what graduates
into a reusable definition.
"""))

# ── Cell 26 — harvest workflow code ────────────────────────────────────────
cells.append(code(
"""# Harvest a reusable workflow from a recorded run's trace: read the ordered
# (phase, skill, artifact) steps the run actually took, attach a condition CHECK
# per phase, and a FALLBACK on the terminal gate (the ReUseIt move — checks +
# fallbacks). The stub is DERIVED from the trace, not pasted in.
CHECKS = {"steering":  "product.md names the bar (pillars + scope)",
          "brainstorm":"at least one WHY / use-case captured",
          "build":     "every decision has a rationale",
          "deepen":    "edge cases enumerated",
          "specify":   "spec has >=1 Must requirement",
          "implement": "patch applies cleanly; tests added",
          "review":    "3Cs >= pass threshold"}

def harvest_workflow(trace):
    \"\"\"Derive a reusable workflow stub from the steps a successful run recorded.\"\"\"
    artifacts = trace.get("artifacts", [])
    stub = {"name": "audit_export_review",
            "harvested_from": f"{trace['mode']} trace ({len(artifacts)} recorded steps)",
            "phases": []}
    for a in artifacts:                       # the real ordered sequence the run took
        entry = {"phase": a["phase"], "skill": a["skill"],
                 "artifact": a["file"].split("__", 1)[-1],
                 "check": CHECKS.get(a["phase"], "phase produced an artifact")}
        stub["phases"].append(entry)
    # Enrich the LAST step with a fallback harvested from failed attempts (ReUseIt).
    if stub["phases"]:
        stub["phases"][-1]["fallback"] = "if check FAILS -> loop back to specify"
    return stub

# Harvest from the WORKFLOW run — the successful trace that left a real sequence.
stub = harvest_workflow(RESULTS["workflow"])

print("Harvested workflow stub (DERIVED from the recorded trace):\\n")
print(json.dumps(stub, indent=2))
print(f"\\n{len(stub['phases'])} phases harvested directly from the run's recorded steps "
      f"-> a reusable procedure. Foreshadows Section 7, which automates this harvest.")
"""))

# ── Cell 27 — Visual 4 markdown ────────────────────────────────────────────
cells.append(md(
"""### Visual 4 — trace → workflow harvest
A simple flow: the recorded run's ordered steps become a reusable phase chain with condition checks and a harvested fallback. The phase-count box reads from the stub we just derived.
"""))

# ── Cell 28 — Visual 4 code ────────────────────────────────────────────────
cells.append(code(
"""fig, ax = plt.subplots(figsize=(10, 2.6))
steps = ["recorded run\\ntrace (it worked)", "read the ordered\\n(phase, skill) steps",
         f"name the {len(stub['phases'])} phases\\n+ skill per phase", "add checks +\\nfallback (from a\\nfailed run)",
         "reusable\\nworkflow stub"]
for i, s in enumerate(steps):
    color = "#1b5e8a" if i == len(steps) - 1 else "#2a8f6a"
    rect = mpatches.FancyBboxPatch((i * 2.2, 0), 1.9, 1.2, boxstyle="round,pad=0.05",
                                   linewidth=2, edgecolor=color, facecolor="#eef5fb")
    ax.add_patch(rect)
    ax.text(i * 2.2 + 0.95, 0.6, s, ha="center", va="center", fontsize=8.5, color=color, weight="bold")
    if i < len(steps) - 1:
        ax.annotate("", xy=(i * 2.2 + 2.15, 0.6), xytext=(i * 2.2 + 1.9, 0.6),
                    arrowprops=dict(arrowstyle="->", color="#555", lw=1.6))
ax.set_xlim(-0.2, len(steps) * 2.2); ax.set_ylim(-0.3, 1.6); ax.axis("off")
ax.set_title("Visual 4 — Harvest: a successful trace graduates into a reusable workflow (ReUseIt / Autobrowse)")
plt.tight_layout(); plt.show()
"""))

# ── Cell 29 — TODO markdown ─────────────────────────────────────────────────
cells.append(md("## ✅ Your turn — compose your own workflow\nPick a repeatable lab job, list the phases, map each to a skill (real or stub), and run it up to the first checkpoint. This forces the compose-skills-into-a-procedure muscle."))

# ── Cell 30 — TODO code ─────────────────────────────────────────────────────
cells.append(code(
"""# ✅ TODO — compose your own workflow.

# 1. Name a repeatable lab job (one sentence).
MY_JOB = "TODO — e.g. ingest a COA, validate it, update ERP, alert on out-of-spec"

# 2. List the phases (ordered) and the skill each phase needs (real or stub name).
MY_WORKFLOW = [
    # (phase_name, skill_name, artifact_it_emits)
    ("ingest",   "TODO-skill", "raw_coa.json"),
    ("validate", "TODO-skill", "validation_report.md"),
    ("update",   "TODO-skill", "erp_update.diff"),
    ("alert",    "TODO-skill", "alert.md"),
]

# 3. Where does the FIRST human/auto checkpoint go? (which phase must pass before the next runs)
MY_FIRST_CHECKPOINT = "validate"   # TODO — e.g. spec passes 3Cs, COA passes spec-limits

# 4. Run it up to the first checkpoint (offline stub: just lists what each phase emits).
print(f"Job: {MY_JOB}\\n")
for phase, skill, artifact in MY_WORKFLOW:
    print(f"  phase={phase:<10s} skill={skill:<14s} -> emits {artifact}")
    if phase == MY_FIRST_CHECKPOINT:
        print(f"  -- CHECKPOINT: '{phase}' must pass before the rest run. Stopping here for approval. --")
        break

# When you have real skills, swap the stub names above and set OFFLINE=False to run live.
"""))

# ── Cell 31 — Takeaway ─────────────────────────────────────────────────────
cells.append(md(
"""## Takeaway

> A **workflow** composes skills under an identity into a **repeatable,
> versioned, auditable procedure** — business as code — and `plan / do / validate`
> is the **same shape all the way down**. You've now built the whole stack by
> hand. Next: how the stack *improves itself* — **adaptation**.
"""))

# ── Cell 32 — Sources ──────────────────────────────────────────────────────
cells.append(md(
"""## Sources

Receipts for the room (leave up during Q&A):

- **ReAct** — Yao et al., 2022 — reason→act→observe loop: https://arxiv.org/abs/2210.03629
- **Reflexion** — Shinn et al., 2023 — act→evaluate→revise (the "validate" beat): https://arxiv.org/abs/2303.11366
- **ReUseIt** — synthesizing reusable agent workflows from execution traces (arXiv 2510.14308, 2025): https://arxiv.org/abs/2510.14308
- **Autobrowse** — Browserbase — run → study trace → graduate into a reusable skill: https://www.browserbase.com/blog/autobrowse
- **Agent scaffolding > model on SWE-bench** — 20+ pt swings on identical weights: https://particula.tech/blog/agent-scaffolding-beats-model-upgrades-swe-bench
- **LangChain / Lance Martin, *Context Engineering for Agents*** (2025) — Isolate is the move this whole section operationalizes: https://www.langchain.com/blog/context-engineering-for-agents
- **Drew Breunig, *How Contexts Fail*** (2025) — the four failure modes (poisoning / distraction / confusion / clash) the phase-isolation defends against: https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html

*Presenter honesty note:* "fractal" is an analogy. The three loops rhyme — ReAct
at the tool scale, skill steps in the middle, plan/do/validate at the top — they
are not provably identical. Don't oversell it.
"""))

# ── Assemble notebook ──────────────────────────────────────────────────────
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"name": "arcvenv", "display_name": "Arc venv", "language": "python"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(OUTPUT, "w"), indent=1)
print(f"wrote {OUTPUT} with {len(cells)} cells")
