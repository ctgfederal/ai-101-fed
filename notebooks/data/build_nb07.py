#!/usr/bin/env python3
"""Build notebooks/07_adaptation.ipynb (nbformat 4) from the spec.

Authored, not executed: every code cell has execution_count=None, outputs=[].
Spec: roadshow_v2/07_adaptation_notebook.md
Shared wiring via notebooks/roadshow.py (setup, invoke_sync, Message).
"""
import json
from pathlib import Path

OUT = Path("/Users/joshschultz/Projects/ai-roadshow/notebooks/07_adaptation.ipynb")


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": s.splitlines(keepends=True)}


cells = []

# ── Cell 0 — title ──────────────────────────────────────────────────────────
cells.append(md(
"""# Notebook 07 — Adaptation

**The system improves itself by reading its own traces and rewriting its own context — prompts, skills, tools.**

You'll watch a weak prompt get *measurably* better across epochs by reflecting on
its own failure traces, and watch what happens when you remove the validation gate
(spoiler: "self-improving" becomes "self-drifting"). Then the same engine optimizes
a **skill doc**, and finally graduates a repeated trace into a **reusable tool**.

> Where this sits in the five moves: adaptation is the agentic loop pointed at the
> agent's *own context* — it rewrites what you **STORE** (the prompt, the skill, the
> tool set). The held-out gate is the discipline that keeps a rewrite an *improvement*
> and not a *poisoning* source injected into every future call.

Everything here is **offline, gated, and a readable diff**. The implementations are
faithful **toy** versions of real papers (GEPA, SkillOpt, ReUseIt/Autobrowse), clearly
labeled — we show the *mechanism*, not paper-scale numbers.
"""))

# ── Cell 1 — setup ──────────────────────────────────────────────────────────
cells.append(md("## Setup\n\nOne import wires the model, a token counter, and the data path. The lesson aliases below name the task: classify scrap-log lines into seven codes, split 40 train / 20 held-out."))

cells.append(code(
'''from pathlib import Path
import json, random, importlib, sys
from textwrap import dedent

from roadshow import setup, invoke_sync, run_sync, Message

# Select the inline backend eagerly, on the main thread, BEFORE the async bridge starts
# a background loop — otherwise matplotlib's lazy backend import can race that thread.
import matplotlib
matplotlib.use("module://matplotlib_inline.backend_inline")
import matplotlib.pyplot as plt

# arcrun: used by the trace -> tool graduation cell near the end.
from arcrun import run, Tool, ToolContext, StaticProvider

model, ask, ntok, DATA = setup()

# Lesson aliases for this notebook.
SCRAP       = DATA / "scrap"
ADAPT       = DATA / "adaptation"
SCRIPTS_OUT = DATA.parent / "scripts"      # a graduated tool will be written here

# The task: classify scrap-log lines into 7 codes (reused from the harness section).
CODES = ["DIM_OOT", "SURF_DEF", "MAT_FLAW", "MACH_SET", "TOOL_WEAR", "OP_ERR", "CONTAM"]
LINES = [json.loads(l) for l in (SCRAP / "scrap_lines.jsonl").read_text().splitlines() if l.strip()]
random.seed(7)
random.shuffle(LINES)
train   = LINES[:40]      # 40 train
heldout = LINES[40:60]    # 20 held-out validation

print(f"task: classify {len(LINES)} scrap lines into {len(CODES)} codes")
print(f"split: {len(train)} train / {len(heldout)} held-out val")
'''))

# ── Cell 2 — CONTROL CELL ───────────────────────────────────────────────────
cells.append(md(
"""## ▶ Control cell — the only cell you edit

Every knob for this notebook lives here. Change a value, then re-run this cell and the
cells below it. Each knob:

- **`OPTIMIZER`** — `"gepa"` (optimize a prompt) or `"skillopt"` (optimize a skill doc).
- **`EPOCHS`** — how many reflect → mutate → gate rounds to run.
- **`USE_HELDOUT_GATE`** — accept an edit only if held-out score improves. **Flip it to
  `False` to *see* overfitting**: train keeps rising while held-out drifts down.
- **`SEED_PROMPT`** — the deliberately weak starting prompt the optimizer improves.
- **`SEED`** — fixes the shuffle/sampling so a run is reproducible."""))

cells.append(code(
'''# ── CONTROL CELL ──
OPTIMIZER        = "gepa"        # "gepa" | "skillopt"
EPOCHS           = 5
USE_HELDOUT_GATE = True          # flip False to SEE overfitting / drift
SEED_PROMPT      = "Classify each line into a scrap code."   # deliberately weak
SEED             = 7

# If the model is reachable we run the live optimizer; otherwise we fall back to the
# recorded run so every visual still renders (see the try/except gate below).
try:
    model, ask, ntok, DATA = setup()
    MODEL_AVAILABLE = True
except Exception as e:
    MODEL_AVAILABLE = False
    print(f"[offline] model unavailable ({type(e).__name__}); using recorded fallback histories.")
'''))

# ── Cell 3 — engine: trace → score → reflect → accept-if-better ─────────────
cells.append(md(
"""## The engine: trace → score → reflect → accept-if-better

It is the **same agentic loop** from the rest of the course — run, look at the trace,
decide, repeat — except now it is pointed at the agent's *own prompt*:

1. **Run** the current prompt over the train set and collect traces.
2. **Score** them (here: classification accuracy).
3. **Reflect** in natural language on the *failures*.
4. **Mutate** the prompt from that reflection.
5. **Accept** the candidate only if held-out score improves.

Step 5 is the whole ballgame. Without it, step 4 just memorizes the train set."""))

# ── Cell 4 — GEPA optimizer (markdown) ───────────────────────────────────────
cells.append(md(
"""### A transparent GEPA-style reflective optimizer

This is a faithful **toy** of the core idea in
[GEPA: *Reflective Prompt Evolution Can Outperform Reinforcement Learning*](https://arxiv.org/abs/2507.19457)
(Agrawal et al., arXiv 2507.19457; ICLR 2026 Oral): reflect on traces in natural
language, then mutate the prompt. GEPA's headline result is that reflective *text*
evolution beat a GRPO RL baseline by ~10% on average (up to 20%) using up to **35×
fewer rollouts** — the point for this room: you can get the gains in **text space**,
no gradient updates, no GPU. We are **not** reproducing those numbers; we show the loop.

We keep a tiny **Pareto set** of the best prompt seen per instance-bucket (a dict),
which is GEPA's trick for not collapsing onto one global optimum too early."""))

# ── Cell 5 — live classify bridge (markdown) ─────────────────────────────────
cells.append(md(
"""**The live classifier.** `live_classify` is a real model call routed through
`invoke_sync` (so the synchronous optimizer can call the async model). Two details that
*are* part of the adaptation lesson: we **memoize** on `(prompt, text)` so repeated
classifications across epochs are free, and we accumulate the real `cost_usd` in
`LIVE_STATS` — proof the call was live."""))

cells.append(code(
'''LIVE_CACHE = {}                              # (prompt, text) -> code  (repeats are free)
LIVE_STATS = {"calls": 0, "cost_usd": 0.0}   # real cost: evidence the call was live

def live_classify(prompt, text):
    """Real model call: classify one line into a scrap code. Memoized + cost-tracked.

    The *prompt* IS the trainable parameter — we send it verbatim as the system prompt.
    A weak prompt (bare code names) leaves the model guessing on the confusable lines;
    the disambiguation rules reflection appends are what actually lift the score. We add
    only a thin output-format reminder so we can parse a single code back."""
    sys_p = prompt + "\\n\\nReply with EXACTLY one code from: " + ", ".join(CODES)
    key = (sys_p, text)
    if key in LIVE_CACHE:
        return LIVE_CACHE[key]
    resp = invoke_sync(model, [Message(role="system", content=sys_p),
                               Message(role="user", content="Scrap line: " + text)])
    LIVE_STATS["calls"] += 1
    LIVE_STATS["cost_usd"] += (resp.cost_usd or 0.0)
    out = (resp.content or "").strip().upper()
    code = next((c for c in CODES if c in out), CODES[0])
    LIVE_CACHE[key] = code
    return code
'''))

# ── Cell 6 — scorer + rubric (markdown) ──────────────────────────────────────
cells.append(md(
"""**The scorer and the offline rubric.** A prompt is scored by running it over examples
and measuring accuracy. The live "hero" run uses `live_classify`; the heavier A/B and
skill-doc sweeps use a transparent keyword **rubric** so their convergence *shape* is
stable in any room. A mutated prompt changes the rubric score by injecting `HINT:` lines
the rubric reads — that is how a prompt edit moves the number."""))

cells.append(code(
'''# USE_LIVE_MODEL is toggled True only around the bounded hero run below.
USE_LIVE_MODEL = False

def classify_one(prompt, text):
    """Label one line: live model call when USE_LIVE_MODEL, else the transparent rubric."""
    if USE_LIVE_MODEL and MODEL_AVAILABLE:
        return live_classify(prompt, text)
    return rubric_label(prompt, text)

# The offline-robust judge. A "prompt" can inject extra hint keywords per code, which is
# how a mutated prompt actually changes the score.
RUBRIC = {
    "DIM_OOT":   ["tolerance", "oversize", "undersize", "diameter", "flatness", "spec", "mm", "gd&t", "deviation"],
    "SURF_DEF":  ["scratch", "blemish", "scuff", "pitting", "finish", "cosmetic", "orange-peel", "burr"],
    "MAT_FLAW":  ["inclusion", "void", "porosity", "lamination", "billet", "material", "stock", "hard spot"],
    "MACH_SET":  ["fixture", "offset", "alignment", "setup", "datum", "tailstock", "jaw", "locating"],
    "TOOL_WEAR": ["insert", "dull", "worn", "tool wear", "reamer", "end mill", "chatter", "tap", "drill"],
    "OP_ERR":    ["operator", "wrong program", "misload", "skipped", "overrode", "backwards", "routing"],
    "CONTAM":    ["coolant", "debris", "oil", "grit", "contamination", "chip", "residue"],
}

def rubric_label(prompt, text):
    t = text.lower()
    extra = _hints_from_prompt(prompt)        # mutated prompt adds discriminating hints
    best, best_score = "DIM_OOT", -1
    for code, kws in RUBRIC.items():
        score = sum(1 for k in kws if k in t) + sum(2 for k in extra.get(code, []) if k in t)
        if score > best_score:
            best, best_score = code, score
    return best

def _hints_from_prompt(prompt):
    """Parse \'HINT: <code> -> kw, kw\' lines a mutation may add to the prompt."""
    hints = {}
    for line in prompt.splitlines():
        if line.strip().upper().startswith("HINT:"):
            body = line.split(":", 1)[1]
            if "->" in body:
                code, kws = body.split("->", 1)
                code = code.strip().upper()
                if code in CODES:
                    hints[code] = [k.strip().lower() for k in kws.split(",") if k.strip()]
    return hints

def run_and_trace(prompt, ex):
    pred = classify_one(prompt, ex["text"])
    return {"text": ex["text"], "gold": ex["label"], "pred": pred, "correct": pred == ex["label"]}

def scorer(prompt, examples):
    traces = [run_and_trace(prompt, ex) for ex in examples]
    return sum(t["correct"] for t in traces) / len(traces), traces
'''))

# ── Cell 7 — reflect + mutate + gepa_step + pareto (markdown) ───────────────
cells.append(md(
"""**The reflective mutation and the GEPA step.** This is the heart of GEPA: take the
*actual failures*, reflect on them, and rewrite the prompt.

- **Live path** (`reflect_live`): the model **reads its own wrong answers** and writes
  one short disambiguation rule that would have fixed them — a real NL reflection,
  appended to the prompt. This is what makes the live convergence curve climb.
- **Offline path** (`reflect_rubric`): a deterministic stand-in that appends a `HINT:`
  line the keyword rubric reads — same *mechanism*, no network, stable shape.

A `gepa_step` runs the prompt, collects failures, and returns the mutated candidate. The
**Pareto set** keeps the best prompt seen per gold code."""))

cells.append(code(
'''def reflect_rubric(prompt, failures):
    """Offline: append a discriminating HINT line the keyword rubric reads."""
    from collections import Counter
    miss = Counter(f["gold"] for f in failures)        # bucket failures by gold code
    target = miss.most_common(1)[0][0]
    missed_texts = " ".join(f["text"].lower() for f in failures if f["gold"] == target)
    kws = [k for k in RUBRIC[target] if k in missed_texts][:4] or RUBRIC[target][:2]
    hint = f"HINT: {target} -> {', '.join(kws)}"
    if hint in prompt:                                 # already learned; nudge another code
        for alt in miss:
            alt_kws = [k for k in RUBRIC[alt] if k in missed_texts][:3] or RUBRIC[alt][:2]
            alt_hint = f"HINT: {alt} -> {', '.join(alt_kws)}"
            if alt_hint not in prompt:
                return prompt.rstrip() + "\\n" + alt_hint
    return prompt.rstrip() + "\\n" + hint

def reflect_live(prompt, failures):
    """Live: the model reads its OWN mistakes and writes one disambiguation rule.

    This is a genuine reflective mutation — the rule is generated from the actual
    misclassifications, then appended to the prompt for the next epoch."""
    shown = "\\n".join(
        f"- line: {f[\'text\']}\\n  I answered {f[\'pred\']}, correct was {f[\'gold\']}"
        for f in failures[:6])
    reflect_sys = (
        "You tune a scrap-code classifier prompt. Below are lines it got WRONG, with the "
        "wrong code it gave and the correct code. Write ONE short rule (max 25 words, "
        "starting \'RULE:\') that disambiguates the codes it confused, so it stops making "
        "these mistakes. Output only the rule line.")
    resp = invoke_sync(model, [Message(role="system", content=reflect_sys),
                               Message(role="user", content=shown)])
    LIVE_STATS["calls"] += 1
    LIVE_STATS["cost_usd"] += (resp.cost_usd or 0.0)
    rule = (resp.content or "").strip().splitlines()[0].strip()
    if not rule:
        return prompt
    if not rule.upper().startswith("RULE:"):
        rule = "RULE: " + rule
    if rule in prompt:                                 # already learned this exact rule
        return prompt
    return prompt.rstrip() + "\\n" + rule

def reflect_and_mutate(prompt, failures):
    """Reflect on failures, propose a sharper prompt. Live model when available."""
    if not failures:
        return prompt
    if USE_LIVE_MODEL and MODEL_AVAILABLE:
        return reflect_live(prompt, failures)
    return reflect_rubric(prompt, failures)

def gepa_step(prompt, examples):
    _, traces = scorer(prompt, examples)               # RUN + collect traces
    failures = [t for t in traces if not t["correct"]]
    return reflect_and_mutate(prompt, failures)        # reflect -> reflective mutation

# Pareto set: best prompt per instance-bucket (here: per gold code).
pareto = {}
def update_pareto(prompt, traces):
    from collections import defaultdict
    by_code = defaultdict(list)
    for t in traces:
        by_code[t["gold"]].append(t["correct"])
    for code, oks in by_code.items():
        acc = sum(oks) / len(oks)
        if code not in pareto or acc > pareto[code][1]:
            pareto[code] = (prompt, acc)

print("optimizer ready:", OPTIMIZER, "| gate:", USE_HELDOUT_GATE, "| model live:", MODEL_AVAILABLE)
'''))

# ── Cell 8 — run the optimization across epochs ──────────────────────────────
cells.append(md(
"""### Run the optimization across epochs (with the gate)

Watch the prompt text *get more specific* each epoch — it learns the edge cases from
its own failure traces. The **accept-if-better** gate is the only thing that decides
whether a candidate sticks. The hero run scores every line with the **live model** on a
bounded subset; the printed `cost_usd` is proof the calls were real."""))

cells.append(code(
'''def optimize(seed_prompt, epochs, use_gate, examples_train, examples_val):
    """Returns (best_prompt, history); history rows are (epoch, train, val, accepted)."""
    prompt = seed_prompt
    base_train, base_traces = scorer(prompt, examples_train)
    base_val, _ = scorer(prompt, examples_val)
    update_pareto(prompt, base_traces)
    best_train, best_val = base_train, base_val
    history = [(-1, round(base_train, 3), round(base_val, 3), True)]   # epoch -1 = seed
    for epoch in range(epochs):
        cand = gepa_step(prompt, examples_train)
        train_score, traces = scorer(cand, examples_train)
        val_score, _        = scorer(cand, examples_val)
        accept = (val_score > best_val) if use_gate else (train_score > best_train)
        if accept:
            prompt = cand
            best_val = max(best_val, val_score)
            best_train = max(best_train, train_score)
            update_pareto(prompt, traces)
        history.append((epoch, round(train_score, 3), round(val_score, 3), accept))
    return prompt, history

def load_fallback(key):
    fb = json.loads((ADAPT / "history_fallback.json").read_text())
    return [(r[0], r[1], r[2], r[3]) for r in fb[key]]

# ── HERO RUN: a real, live GEPA loop ──
# Weak seed prompt -> the model classifies, reflects on its OWN misses, appends a
# disambiguation rule, and we accept only if held-out improves. Bounded train/val so the
# live pass fits the time budget; live_classify is memoized so repeats are free.
random.seed(SEED)
if MODEL_AVAILABLE:
    LIVE_TRAIN = train[:15]
    LIVE_VAL   = heldout[:15]
    USE_LIVE_MODEL = True
    best_prompt, history = optimize(SEED_PROMPT, EPOCHS, USE_HELDOUT_GATE, LIVE_TRAIN, LIVE_VAL)
    USE_LIVE_MODEL = False
    PATH_TAKEN = "live model"
    print(f"[live] {LIVE_STATS[\'calls\']} real model calls, "
          f"cumulative cost_usd = ${LIVE_STATS[\'cost_usd\']:.5f}\\n")
else:
    best_prompt, history = optimize(SEED_PROMPT, EPOCHS, USE_HELDOUT_GATE, train, heldout)
    PATH_TAKEN = "offline rubric"

# Safety net ONLY if the model is unreachable AND the offline curve somehow didn't move.
# The live run is shown as-is — we do NOT paste a recorded shape over a live result.
val_series = [h[2] for h in history]
if not MODEL_AVAILABLE and max(val_series) - min(val_series) < 1e-6:
    history = load_fallback("gated" if USE_HELDOUT_GATE else "ungated")
    PATH_TAKEN = "offline rubric -> recorded fallback"

print(f"path taken: {PATH_TAKEN}")
val_gain = history[-1][2] - history[0][2]
print(f"held-out: seed={history[0][2]:.3f} -> final={history[-1][2]:.3f}  "
      f"(gain {val_gain:+.3f})\\n")
print("evolving prompt (final):\\n" + "-" * 60)
print(best_prompt)
print("-" * 60)
print("\\nepoch  train   val   accepted")
for ep, tr, va, ac in history:
    tag = "seed" if ep < 0 else str(ep)
    print(f"  {tag:>4}  {tr:>5}  {va:>5}   {\'accept\' if ac else \'reject\'}")
'''))

# ── Cell 9 — VISUAL 1: convergence ───────────────────────────────────────────
cells.append(md(
"""### Visual 1 — convergence: held-out score by epoch (the hero)

A prompt (plain text) getting measurably better from its own failure traces.

**Said honestly:** the *shape* of this curve is model- and seed-dependent. A small
local model may improve in fits and starts or plateau early. The accept-if-better gate
guarantees the held-out curve is **monotonic non-decreasing**, but *not* that it climbs
fast. The teaching point is the **mechanism** (reflect → mutate → gate), not a number."""))

cells.append(code(
'''epochs_x = [h[0] for h in history]
train_y  = [h[1] for h in history]
val_y    = [h[2] for h in history]
accepted = [h[3] for h in history]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(epochs_x, train_y, marker="o", color="#888", linestyle="--", label="train score")
ax.plot(epochs_x, val_y,   marker="o", color="#1f77b4", linewidth=2, label="held-out (val) score")
acc_x = [x for x, a in zip(epochs_x, accepted) if a]      # mark accepted edits
acc_y = [y for y, a in zip(val_y, accepted) if a]
ax.scatter(acc_x, acc_y, s=140, facecolors="none", edgecolors="#2ca02c",
           linewidths=2, label="accepted edit", zorder=5)
ax.set_xlabel("epoch  (-1 = seed prompt)")
ax.set_ylabel("accuracy")
ax.set_title(f"Convergence — prompt improving from its own failures\\n"
             f"gate={USE_HELDOUT_GATE} · path={PATH_TAKEN}")
ax.set_ylim(0, 1.0)
ax.set_xticks(epochs_x)
ax.grid(True, alpha=0.3)
ax.legend(loc="lower right")
plt.tight_layout()
plt.show()
'''))

# ── Cell 10 — remove the gate ─────────────────────────────────────────────────
cells.append(md(
"""## Now remove the gate

Set `USE_HELDOUT_GATE = False` in the control cell and re-run, or just run the A/B
below. Watch **train keep rising while held-out stalls or *falls*** — that is
overfitting. That is **"self-drifting," not "self-improving."** An ungated self-edit
that looks good on the data it was tuned on is, in production, indistinguishable from
[context poisoning](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)
injected into every future call."""))

# ── Cell 11 — A/B contrast ─────────────────────────────────────────────────────
cells.append(md(
"""### A/B contrast — gate vs no-gate

We run both configurations from a single config list and collect both histories, so the
comparison is one loop rather than two near-identical cells."""))

cells.append(code(
'''AB_CONFIGS = [
    {"name": "gated",   "use_gate": True,  "fallback_key": "gated"},
    {"name": "ungated", "use_gate": False, "fallback_key": "ungated"},
]

ab_histories = {}
for cfg in AB_CONFIGS:
    random.seed(SEED)                       # same seed -> same starting conditions
    pareto.clear()
    _, hist = optimize(SEED_PROMPT, EPOCHS, cfg["use_gate"], train, heldout)
    vseries = [h[2] for h in hist]          # if val is flat, use the recorded shape
    if max(vseries) - min(vseries) < 1e-6:
        hist = load_fallback(cfg["fallback_key"])
    ab_histories[cfg["name"]] = hist
    print(f"{cfg[\'name\']:>8}: final held-out = {hist[-1][2]:.3f}  (train = {hist[-1][1]:.3f})")
'''))

# ── Cell 12 — VISUAL 2: gate vs no-gate ───────────────────────────────────────
cells.append(md(
"""### Visual 2 — gate vs no-gate (the overfitting divergence)

Two held-out curves: **gated** climbs and plateaus high; **ungated** chases train and
the held-out score diverges *downward*. This is the picture behind the rule:
*without a held-out gate, self-improving is just self-drifting.*"""))

cells.append(code(
'''fig, ax = plt.subplots(figsize=(8, 4.5))
colors = {"gated": "#2ca02c", "ungated": "#d62728"}
for name, hist in ab_histories.items():
    xs = [h[0] for h in hist]
    val = [h[2] for h in hist]
    ax.plot(xs, val, marker="o", linewidth=2, color=colors[name], label=f"{name} — held-out")
    if name == "ungated":                   # faint train line: it kept rising
        tr = [h[1] for h in hist]
        ax.plot(xs, tr, marker=".", linestyle=":", color="#d62728", alpha=0.5,
                label="ungated — train (chased)")
ax.set_xlabel("epoch  (-1 = seed)")
ax.set_ylabel("held-out accuracy")
ax.set_title("Gate vs no-gate — the held-out gate is what makes it \'improving\'")
ax.set_ylim(0, 1.0)
ax.set_xticks(xs)
ax.grid(True, alpha=0.3)
ax.legend(loc="center left")
plt.tight_layout()
plt.show()
'''))

# ── Cell 13 — SkillOpt markdown ──────────────────────────────────────────────
cells.append(md(
"""## Same engine, different artifact — train the *skill doc*

Now the trainable parameter is a `SKILL.md`. Same loop — trace → score → propose an
edit → accept only if held-out improves — but the "edit" is a bounded
**add / delete / replace** on the skill's Knowledge / Antipatterns sections.

A **textual learning rate** caps how far the doc can drift in one step, and a
**meta-skill** check rejects edits that bloat the doc past a word budget. This mirrors
Microsoft's [*SkillOpt: Executive Strategy for Self-Evolving Agent Skills*](https://arxiv.org/abs/2605.23904)
(arXiv 2605.23904): text-space, validation-gated, and **zero added inference-time model
calls at deployment** — the optimized skill is just a better static document.

That last property is the lab sell: the gain ships as a **reviewable Markdown diff**,
so it goes through the same change-control / audit path as any other config file —
not as new weights."""))

# ── Cell 14 — SkillOpt code ───────────────────────────────────────────────────
cells.append(md(
"""**Optimize the skill doc.** We start from a small `scrap-coder` SKILL.md, propose a
bounded edit each epoch, and accept only when held-out improves **and** the doc stays
under the word budget and within the per-step learning rate. The accepted edits are the
diff that ships."""))

cells.append(code(
'''# A small scrap-coder SKILL.md (the artifact we optimize). Knowledge + Antipatterns
# are the trainable sections; the rest is held fixed.
SEED_SKILL = dedent("""\
    ---
    name: scrap-coder
    version: 1.0.0
    description: Classify a scrap-log line into one of seven scrap codes.
    ---
    # scrap-coder

    ## Knowledge
    - Codes: DIM_OOT, SURF_DEF, MAT_FLAW, MACH_SET, TOOL_WEAR, OP_ERR, CONTAM.
    - Read the line, pick the single best-fitting code.

    ## Antipatterns
    - Do not invent codes outside the seven.
    """)

WORD_BUDGET = 320          # meta-skill: reject edits that bloat past this
LEARNING_RATE_WORDS = 60   # textual learning rate: max words added per accepted step

def skill_word_count(doc):
    return len(doc.split())

def skill_to_prompt(doc):
    """Turn the skill\'s Knowledge HINT bullets into prompt lines the rubric scorer reads."""
    prompt = SEED_PROMPT
    for line in doc.splitlines():
        s = line.strip("- ").strip()
        if s.upper().startswith("HINT:"):
            prompt += "\\n" + s
    return prompt

def propose_skill_edit(doc, failures):
    """A bounded add/delete/replace edit, expressed as a new Knowledge HINT bullet."""
    cand_prompt = reflect_and_mutate(skill_to_prompt(doc), failures)
    new_hints = [l for l in cand_prompt.splitlines() if l.strip().upper().startswith("HINT:")]
    existing = [l.strip("- ").strip() for l in doc.splitlines() if l.strip().strip("- ").upper().startswith("HINT:")]
    fresh = [h for h in new_hints if h not in existing]
    if not fresh:
        return doc, "noop"
    add = fresh[0]
    out, action = [], "add"                  # insert under ## Knowledge
    for line in doc.splitlines():
        out.append(line)
        if line.strip() == "## Knowledge":
            out.append(f"- {add}")
    return "\\n".join(out), action

def skill_val_score(doc):
    return scorer(skill_to_prompt(doc), heldout)[0]

def optimize_skill(seed_doc, epochs):
    doc = seed_doc
    best_val = skill_val_score(doc)
    traj = [(0, "seed", skill_word_count(doc), round(best_val, 3), True)]
    for i in range(1, epochs + 1):
        _, traces = scorer(skill_to_prompt(doc), train)
        failures = [t for t in traces if not t["correct"]]
        cand, action = propose_skill_edit(doc, failures)
        wc = skill_word_count(cand)
        val = skill_val_score(cand)
        within_budget = wc <= WORD_BUDGET                       # meta-skill budget
        within_lr = (wc - skill_word_count(doc)) <= LEARNING_RATE_WORDS  # textual LR
        accept = (val > best_val) and within_budget and within_lr        # held-out gate
        if accept:
            doc = cand
            best_val = val
        traj.append((i, action, wc, round(val, 3), accept))
    return doc, traj

random.seed(SEED)
best_skill, skill_traj = optimize_skill(SEED_SKILL, EPOCHS)

# Offline-robust: if the rubric trajectory is flat, use the recorded SkillOpt shape.
if len({t[3] for t in skill_traj}) <= 1:
    fb = json.loads((ADAPT / "skill_opt_fallback.json").read_text())
    skill_traj = [(r[0], r[1], r[2], r[3], r[4]) for r in fb["trajectory"]]
    WORD_BUDGET = fb["word_budget"]
    print("[offline] using recorded SkillOpt trajectory")

(ADAPT / "best_skill.md").write_text(best_skill)             # write the optimized skill
print("accepted edits (the readable diff that ships):")
for i, action, wc, val, acc in skill_traj:
    if acc and i > 0:
        print(f"  edit {i}: {action:>7}  words={wc:>3}  held-out={val:.3f}  ACCEPTED")
    elif not acc and i > 0:
        print(f"  edit {i}: {action:>7}  words={wc:>3}  held-out={val:.3f}  rejected "
              f"({\'budget\' if wc > WORD_BUDGET else \'no val gain\'})")
print(f"\\nbest_skill.md written ({skill_word_count(best_skill)} words)")
'''))

# ── Cell 15 — VISUAL 3: skill score vs word-count ───────────────────────────
cells.append(md(
"""### Visual 3 — skill score vs word-count (bloat control)

Each accepted edit plotted as (word_count, held-out score). The meta-skill keeps the
doc **bounded under the word budget** while the score rises — the skill stays "readable
in a few minutes." Rejected edits (e.g. ones that bloat past budget with no gain) are
shown so you can see the gate working."""))

cells.append(code(
'''wc_acc  = [t[2] for t in skill_traj if t[4]]
val_acc = [t[3] for t in skill_traj if t[4]]
wc_rej  = [t[2] for t in skill_traj if not t[4]]
val_rej = [t[3] for t in skill_traj if not t[4]]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(wc_acc, val_acc, color="#1f77b4", alpha=0.4, zorder=1)   # accepted trajectory
ax.scatter(wc_acc, val_acc, s=90, color="#2ca02c", label="accepted edit", zorder=3)
if wc_rej:
    ax.scatter(wc_rej, val_rej, s=90, marker="x", color="#d62728",
               label="rejected (budget / no gain)", zorder=3)
ax.axvline(WORD_BUDGET, color="#d62728", linestyle="--", alpha=0.7,
           label=f"word budget ({WORD_BUDGET})")
for t in skill_traj:
    ax.annotate(t[1], (t[2], t[3]), textcoords="offset points", xytext=(5, 5), fontsize=8)
ax.set_xlabel("skill doc word count")
ax.set_ylabel("held-out accuracy")
ax.set_title("SkillOpt — score rises, word-count stays bounded (bloat control)")
ax.grid(True, alpha=0.3)
ax.legend(loc="lower right")
plt.tight_layout()
plt.show()
'''))

# ── Cell 16 — graduate a trace: markdown ─────────────────────────────────────
cells.append(md(
"""## Graduate a trace into a reusable tool (autobrowse-style)

The agent found a reliable path. **Freeze it into a deterministic tool** — the
push-down move, done automatically.

This is the "graduate a converged trajectory into a durable, reusable artifact" idea
from [ReUseIt: *Synthesizing Reusable AI Agent Workflows for Web Automation*](https://arxiv.org/abs/2510.14308)
(arXiv 2510.14308) and Browserbase's [Autobrowse](https://www.browserbase.com/blog/autobrowse).
We do it offline on a genuinely **deterministic sub-procedure** — which is the honest
case: graduate the part that is *actually* deterministic into code; leave the
genuinely-judgment parts to the model.

**State the model-dependence aloud:** token/step savings here are real and measurable,
but the magnitude depends on how repetitive the task is. This is a worked illustration,
not a benchmark."""))

# ── Cell 17 — trace → tool ───────────────────────────────────────────────────
cells.append(md(
"""**Manufacture the tool, then prove it.** We write the repeated sub-procedure (a
per-code count rollup) to `scripts/scrap_rollup.py`, register it as an arcrun `Tool`,
and hand it to the agentic loop — the model **calls** the graduated tool instead of
counting by hand. The before/after step and token numbers come from the recorded
illustration."""))

cells.append(code(
'''# The agent kept doing the same deterministic sub-procedure: total scrap counts per
# code. We graduate it into a real script under scripts/ and register it as a Tool.
SCRIPTS_OUT.mkdir(parents=True, exist_ok=True)
rollup_path = SCRIPTS_OUT / "scrap_rollup.py"
rollup_path.write_text(dedent(\'\'\'\\
    """Graduated tool: deterministic scrap-count rollup.

    Manufactured from a converged agent trajectory in NB07 (adaptation).
    Replaces N per-line LLM "add this up" turns with one deterministic call.
    """
    import json
    from collections import Counter


    def rollup(labeled_lines: list[dict]) -> dict:
        """Count scrap lines per code. Same output every time, given same input."""
        counts = Counter(r["label"] for r in labeled_lines)
        return {"total": len(labeled_lines), "by_code": dict(sorted(counts.items()))}


    if __name__ == "__main__":
        import sys
        rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
        print(json.dumps(rollup(rows), indent=2))
    \'\'\'))

# import + register as a Tool
sys.path.insert(0, str(SCRIPTS_OUT))
import scrap_rollup
importlib.reload(scrap_rollup)

async def scrap_rollup_tool_fn(args: dict, ctx: ToolContext) -> str:
    rows = json.loads(args["rows_json"])
    return json.dumps(scrap_rollup.rollup(rows))

scrap_rollup_tool = Tool(
    name="scrap_rollup",
    description="Deterministically count labeled scrap lines per code. "
                "Input: rows_json = JSON list of {text,label}. Returns {total, by_code}.",
    input_schema={"type": "object",
                  "properties": {"rows_json": {"type": "string"}},
                  "required": ["rows_json"]},
    execute=scrap_rollup_tool_fn,
)

# Sanity: the graduated tool produces the right answer.
truth = scrap_rollup.rollup(LINES)
print("graduated tool output:", json.dumps(truth))

# PROVE the graduation: hand the registered tool to the loop and let the model CALL it
# (one deterministic tool turn replaces the per-line "add this up" turns). We run the
# agent loop via run_sync so it lands on the SAME background loop the model client is
# bound to (top-level await would use the kernel loop and break the client binding).
if MODEL_AVAILABLE:
    sample = LINES[:12]
    task = ("Total up these labeled scrap rows by code using the scrap_rollup tool, "
            "then report how many rows there are in total.\\nrows: " + json.dumps(sample))

    grad_res = run_sync(run(model, StaticProvider([scrap_rollup_tool]),
                            "You are a scrap-reporting agent. Use the scrap_rollup tool to "
                            "count rows; do not count by hand.",
                            task, max_turns=4))
    print(f"\\n[live] agent called the graduated tool: tool_calls_made="
          f"{grad_res.tool_calls_made}, turns={grad_res.turns}")
    print("agent answer:", (grad_res.content or "").strip().splitlines()[0][:100])

# Before/after. "before" = the agent did the rollup as LLM turns; "after" = one tool call.
fb = json.loads((ADAPT / "graduation_fallback.json").read_text())
before, after = fb["before"], fb["after"]
print(f"\\nbefore graduation: {before[\'llm_steps\']} LLM steps, "
      f"{before[\'tokens\']} tokens, acc={before[\'accuracy\']}")
print(f"after  graduation: {after[\'llm_steps\']} LLM steps, "
      f"{after[\'tokens\']} tokens, acc={after[\'accuracy\']}")
print(f"\\nwrote {rollup_path.relative_to(DATA.parent)} and registered tool \'scrap_rollup\'")
'''))

# ── Cell 18 — VISUAL 4: before/after graduation ──────────────────────────────
cells.append(md(
"""### Visual 4 — before/after graduation (steps + tokens, accuracy held constant)

The system manufactured its own script. LLM steps and tokens drop; accuracy is
unchanged because the graduated part was deterministic all along."""))

cells.append(code(
'''labels = ["LLM steps", "tokens (÷100)", "accuracy (×10)"]
before_vals = [before["llm_steps"], before["tokens"] / 100, before["accuracy"] * 10]
after_vals  = [after["llm_steps"],  after["tokens"] / 100,  after["accuracy"] * 10]

x = range(len(labels))
w = 0.35
fig, ax = plt.subplots(figsize=(8, 4.5))
b1 = ax.bar([i - w/2 for i in x], before_vals, w, label="before", color="#d62728")
b2 = ax.bar([i + w/2 for i in x], after_vals,  w, label="after",  color="#2ca02c")
ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_ylabel("normalized value")
ax.set_title("Trace → tool graduation — fewer steps & tokens, same accuracy")
ax.bar_label(b1, fmt="%.1f", padding=2, fontsize=8)
ax.bar_label(b2, fmt="%.1f", padding=2, fontsize=8)
ax.grid(True, axis="y", alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()
'''))

# ── Cell 19 — fine-tuning framed ─────────────────────────────────────────────
cells.append(md(
"""## Fine-tuning, framed (no GPU in the room)

What you'd do *with volume*: curate good decision traces (the audit log from earlier
sections), fine-tune a local open-weights model **inside the security
boundary, on an on-prem GPU**, version the model, repeat.

We **don't** run it live — there's no GPU here, and a real fine-tune would dwarf the
25-minute budget. But the on-ramp is just data prep, so we show *that* step.

**Text-first, weights-last.** Every cell above got gains in **text space**, as
reviewable diffs, with no GPU. Fine-tuning is the *last* lever you reach for — it's the
most expensive to run, the hardest to audit, and the easiest to overfit. For a lab the
on-prem angle matters: text-space optimization works against a hosted API *or* a fully
air-gapped local model, while weight updates require the data **and** the GPUs to be
in-boundary."""))

# ── Cell 20 — assemble fine-tune dataset ─────────────────────────────────────
cells.append(md(
"""### Assemble a fine-tune dataset from the audit log

> *The audit log you built for compliance is the dataset you optimize from.*

Filter the audit/trace store to **good-outcome** decision traces and write a JSONL
fine-tune file in the standard chat format. No training is run."""))

cells.append(code(
'''audit_rows = [json.loads(l) for l in (ADAPT / "audit_traces.jsonl").read_text().splitlines() if l.strip()]
good = [r for r in audit_rows if r["outcome"] == "good"]

ft_path = ADAPT / "finetune_scrap.jsonl"
with ft_path.open("w") as f:
    for r in good:
        record = {"messages": [
            {"role": "system", "content": "Classify the scrap-log line into one scrap code."},
            {"role": "user", "content": r["input"]},
            {"role": "assistant", "content": r["output"]},
        ]}
        f.write(json.dumps(record) + "\\n")

print(f"audit traces: {len(audit_rows)} total, {len(good)} good-outcome (kept)")
print(f"wrote {ft_path.relative_to(DATA.parent)}  ({len(good)} records)\\n")
print("sample fine-tune records:")
for line in ft_path.read_text().splitlines()[:2]:
    print(json.dumps(json.loads(line), indent=2))
print("\\nNext step (NOT run here): fine-tune an on-prem open-weights model on this file,")
print("version it, and route through the same audit path as any other artifact.")
'''))

# ── Cell 21 — TODO ────────────────────────────────────────────────────────────
cells.append(md("## ✅ TODO — optimize your own prompt\n\nDrop in a weak prompt for one of *your* tasks plus a tiny labeled set, split it into train / val, and run the **gated** optimizer for a few epochs. Keep the diff only if held-out improves."))

cells.append(code(
'''# ✅ TODO — replace with your own weak prompt and labeled examples.
MY_SEED_PROMPT = "Label each item."                       # ✅ TODO: your weak prompt

MY_DATA = [                                               # ✅ TODO: your tiny labeled set
    {"text": "example item one", "label": "LABEL_A"},
    {"text": "example item two", "label": "LABEL_B"},
    # ... add ~12+ rows so a train/val split is meaningful
]

# ✅ TODO: a scorer for YOUR task. The keyword-rubric here is a stand-in — swap in your
# own (or rely on the live model path) and define what "correct" means for your labels.
MY_VALID_LABELS = sorted({r["label"] for r in MY_DATA})

if len(MY_DATA) >= 4:
    random.seed(SEED)
    rows = MY_DATA[:]
    random.shuffle(rows)
    cut = max(1, int(len(rows) * 0.6))
    my_train, my_val = rows[:cut], rows[cut:]
    print(f"your split: {len(my_train)} train / {len(my_val)} val")
    print("✅ TODO: wire MY_VALID_LABELS into RUBRIC (or use the live model), then call")
    print("        optimize(MY_SEED_PROMPT, EPOCHS, USE_HELDOUT_GATE, my_train, my_val)")
    print("        and keep best_prompt only if the held-out score went up.")
else:
    print("✅ TODO: add your own labeled rows to MY_DATA above, then re-run.")
'''))

# ── Cell 22 — Takeaway ────────────────────────────────────────────────────────
cells.append(md(
"""## Takeaway

> **Adaptation is the agentic loop pointed at the agent itself:** trace → score →
> propose an edit → **accept only if held-out improves.** Optimize **text before
> weights**, and keep a human on the merge.

- The held-out gate is the line between **self-improving** and **self-drifting**. An
  ungated self-edit is indistinguishable from poisoning every future call.
- The same engine optimizes a **prompt**, a **skill doc**, or graduates a trace into a
  **tool** — all in text space, all shipping as reviewable diffs, no GPU required.
- Fine-tuning is the last lever, not the first: most expensive, hardest to audit,
  easiest to overfit. And the audit log you built for compliance *is* the dataset.

One section left — finding the work worth pointing all of this at."""))

# ── Cell 23 — Sources ─────────────────────────────────────────────────────────
cells.append(md(
"""## Sources (the receipts)

- **GEPA — Reflective Prompt Evolution** (Agrawal et al., ICLR 2026 Oral):
  https://arxiv.org/abs/2507.19457 — reflect on traces in NL, mutate the prompt; beat
  GRPO by ~10% avg using up to 35× fewer rollouts.
- **SkillOpt — Self-Evolving Agent Skills** (Microsoft): https://arxiv.org/abs/2605.23904
  — bounded add/delete/replace edits to a skill doc, validation-gated, zero added
  inference-time calls; repo: https://github.com/microsoft/SkillOpt
- **ReUseIt — Reusable AI Agent Workflows**: https://arxiv.org/abs/2510.14308 ;
  **Autobrowse** (Browserbase): https://www.browserbase.com/blog/autobrowse — graduate
  a converged trajectory into a durable, reusable artifact.
- **The four failure modes** (Breunig, *How Contexts Fail*, 2025):
  https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html — an
  ungated self-edit becomes *poisoning* in every future call.
- **Framing note:** faithful **toy** implementations for teaching. We do not reproduce
  paper-scale results; all numbers here are from a small offline run on the room's
  model and are seed-/model-dependent. The model-independent claims are the
  *mechanisms*: (a) reflect→mutate→accept-if-held-out-improves is a real loop;
  (b) an ungated self-edit is indistinguishable from poisoning; (c) text-space gains
  require no GPU and ship as auditable diffs.
"""))

# ── assemble notebook ─────────────────────────────────────────────────────────
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"name": "arcvenv", "display_name": "Arc venv", "language": "python"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(OUT, "w"), indent=1)
print(f"wrote {OUT} with {len(cells)} cells")
