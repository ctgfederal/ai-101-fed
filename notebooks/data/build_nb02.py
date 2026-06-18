#!/usr/bin/env python3
"""Build notebooks/02_agentic_loop.ipynb (nbformat 4) from the spec.

Authored, not executed: every code cell has execution_count=None, outputs=[].
Conventions: shared `roadshow.setup()` for plumbing; exactly one CONTROL CELL;
A/B contrasts as loops; base matplotlib; offline-robust (precomputed fallback
for every live-call cell). Spec: roadshow_v2/02_agentic_loop_notebook.md
"""
import json
from pathlib import Path
from uuid import uuid4

OUTPUT = Path(__file__).resolve().parent.parent / "notebooks" / "02_agentic_loop.ipynb"


def _uid():
    return uuid4().hex[:8]


def md(s):
    return {
        "cell_type": "markdown",
        "id": _uid(),
        "metadata": {},
        "source": s.splitlines(keepends=True),
    }


def code(s):
    return {
        "cell_type": "code",
        "id": _uid(),
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": s.splitlines(keepends=True),
    }


cells = []

# ── Cell 0 — title ────────────────────────────────────────────────────────────
cells.append(md(
"""# Notebook 02 — The Loop

We write the **entire agent in one cell, from scratch**, before we ever import a
framework. Then we see why the loop beats a single shot.

The loop we build is a named, peer-reviewed pattern — **ReAct**
(reason -> act -> observe -> revise, [Yao et al., 2022](https://arxiv.org/abs/2210.03629)).
The hardening we add at the end is **Reflexion** (verbal self-feedback,
[Shinn et al., NeurIPS 2023](https://arxiv.org/abs/2303.11366)). We're hand-building
two real agent patterns, not inventing one.

**Honesty up front:** "closed-loop beats single-shot" is *task- and model-dependent*,
not a law. The win is real only when the task needs grounding in something outside
the model's weights — here, the actual bytes of a CSV. We pick a grounding task on
purpose so the contrast is honest, and we ship a precomputed transcript so the point
survives offline.
"""))

# ── Cell 1 — markdown: setup ──────────────────────────────────────────────────
cells.append(md(
"""## Setup

One line wires the model, the token counter, and the data path. Everything else
in this notebook is the lesson.
"""))

# ── Cell 2 — setup code ───────────────────────────────────────────────────────
cells.append(code(
"""# Shared wiring: the model, an async ask() helper, a token counter, the data path.
from roadshow import setup, Message
import io, csv, json, contextlib
import numpy as np
import matplotlib.pyplot as plt

model, ask, ntok, DATA = setup()       # model is Anthropic by default
PRECOMP = DATA / "precomputed"         # vendored transcripts for the offline path
print("ready · model:", getattr(model, "name", model.__class__.__name__))
"""))

# ── Cell 3 — markdown: the one tool ──────────────────────────────────────────
cells.append(md(
"""## The one tool the loop can call: `run_python`

The agent gets exactly one capability: run a snippet of Python and read back its
stdout/stderr. We show the body so it isn't a black box.

**Security aside (worth saying aloud):** a tool that executes model-written code
is exactly the attack surface security and compliance staff care about. In a real
deployment this `run_python` should be a sandbox — a resource-capped subprocess,
no network, a scratch directory only. The *agent* never runs code itself; it emits
a tool *request*, and the harness decides whether to honor it. We harden this in
the harness notebook.
"""))

# ── Cell 4 — tool code ────────────────────────────────────────────────────────
cells.append(code(
"""# run_python: execute a snippet, capture stdout+stderr as a string observation.
# Pre-bind a few safe names so the model can read our data without imports.
def run_python(code: str) -> str:
    buf = io.StringIO()
    g = {"np": np, "csv": csv, "json": json, "Path": type(DATA),
         "DATA": DATA}
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            exec(code, g)   # demo sandbox stand-in; real deployments isolate this
    except Exception as exc:
        return f"{buf.getvalue()}{type(exc).__name__}: {exc}"
    out = buf.getvalue().strip()
    return out or "(no output)"

TOOLS = {"run_python": run_python}
print("tools:", list(TOOLS))
"""))

# ── Cell 5 — markdown: CONTROL CELL rule ─────────────────────────────────────
cells.append(md(
"""## ▶ Control cell — the only cell you edit

Everything downstream reads these plain variables. **Change a value, then re-run
the cells below it.** No widgets, no hidden state.
"""))

# ── Cell 6 — CONTROL CELL ─────────────────────────────────────────────────────
cells.append(code(
"""# ═══════════════════════════════════════════════════════════════════════════
#  CONTROL CELL — edit these, then re-run everything below
# ═══════════════════════════════════════════════════════════════════════════
MODE      = "closed_loop"   # "closed_loop" = the agent loop with tools
                            # "single_shot" = one model call, no tools
MAX_STEPS = 6               # stop after this many loop turns (anti-runaway cap)
TASK      = ("Compute the 90th percentile of the latencies in data/logs/oss04.csv "
             "and say whether it breaches the 50ms SLO.")   # the grounding task
OFFLINE   = False           # True  = replay the vendored transcript (no API calls)
                            # False = run live against the model
VERBOSE   = True            # True  = print the full event stream as the loop runs

print(f"MODE={MODE}  MAX_STEPS={MAX_STEPS}  OFFLINE={OFFLINE}")
"""))

# ── Cell 7 — markdown: "here is the whole agent" ─────────────────────────────
cells.append(md(
"""## Here is the whole agent

The next cell is the **entire loop**. Four moves, repeated until done:

> **reason -> act -> observe -> revise**

We need three tiny helpers first — a system prompt that tells the model how to
call our one tool, a `parse_tool_call` that reads the model's reply, and a thin
`llm()` wrapper over `model.invoke` (the loop needs raw message lists, so it
talks to the model directly rather than through `ask`). Then the loop itself is
~20 lines.
"""))

# ── Cell 8 — the loop from scratch ────────────────────────────────────────────
cells.append(code(
"""import re
from dataclasses import dataclass

@dataclass
class ToolCall:
    name: str
    args: dict

def system_prompt(tools: dict) -> Message:
    names = ", ".join(tools)
    return Message(role="system", content=(
        "You are a careful data agent. You may call ONE tool: run_python(code).\\n"
        "To call it, reply with EXACTLY one fenced block:\\n"
        "```tool\\n{\\\"name\\\": \\\"run_python\\\", \\\"args\\\": {\\\"code\\\": \\\"<python>\\\"}}\\n```\\n"
        "Make ONE tool call per reply, then wait for the TOOL RESULT before the next.\\n"
        "The sandbox has these names PRE-BOUND (do NOT import or pip-install them, "
        "do NOT use subprocess): np (numpy), csv, json, Path, and DATA — a pathlib "
        "Path to the data directory. Read files via DATA / 'subdir' / 'file.csv'. "
        "CSV files have a header row; oss04.csv has a 'latency_ms' column. "
        "The code may print results. When you have the answer, reply in plain prose "
        "with NO fenced block. Available tools: " + names + "."
    ))

def user(task: str) -> Message:        return Message(role="user", content=task)
def assistant(text: str) -> Message:   return Message(role="assistant", content=text)
def tool_result(obs: str) -> Message:  return Message(role="user", content=f"TOOL RESULT:\\n{obs}")

async def llm(context: list) -> str:
    # The loop passes a growing list of Messages, so it calls the model directly.
    resp = await model.invoke(context)
    return resp.content or ""

def parse_tool_call(text: str):
    # Find the FIRST ```tool ...``` block and parse it. Degrade gracefully -> None.
    m = re.search(r"```tool\s*(\{.*?\})\s*```", text, re.DOTALL)  # noqa: W605
    if not m:
        return None
    try:
        # strict=False: models routinely put raw newlines inside the "code" string,
        # which is illegal in strict JSON. Tolerating them is what makes the loop run.
        d = json.loads(m.group(1), strict=False)
        return ToolCall(name=d["name"], args=d.get("args", {}))
    except Exception:
        return None   # malformed (common on small models) -> loop just answers


# ── THE WHOLE AGENT ──────────────────────────────────────────────────────────
async def agent(task, tools, max_steps):
    context = [system_prompt(tools), user(task)]
    events = []
    for step in range(max_steps):
        thought = await llm(context)                      # REASON
        events.append(("reason", step, thought))
        call = parse_tool_call(thought)
        if call is None:                                  # REVISE: done?
            events.append(("final", step, thought)); break
        obs = tools[call.name](**call.args)               # ACT
        events.append(("act", step, call))
        events.append(("observe", step, obs))             # OBSERVE
        context.append(assistant(thought))
        context.append(tool_result(obs))                  # the window GROWS
    return events
"""))

# ── Cell 9 — markdown: name the four moves ───────────────────────────────────
cells.append(md(
"""Point at each move in the code above: **reason** (`llm`), **act**
(`tools[...]()`), **observe** (append the result), **revise** (loop again or
stop). That's the **ReAct** loop ([Yao et al., 2022](https://arxiv.org/abs/2210.03629)).
Everything else today is a refinement of these lines.

Notice `context.append(...)` runs **twice every turn** — the window grows on
every step. That's the seed of the runaway in the failure section, and the
reason **compaction** (CONDENSE, one of Section 1's five context moves) is
mandatory, not optional.
"""))

# ── Cell 10 — markdown: run the loop ─────────────────────────────────────────
cells.append(md(
"""## Run the loop and read the event stream

Run the agent on `TASK` and watch the event stream. With `VERBOSE`, you literally
read the agent think, call `run_python`, see the result, and conclude. With
`OFFLINE=True` it replays the vendored transcript instead of calling the model.
"""))

# ── Cell 11 — run + print events ──────────────────────────────────────────────
cells.append(code(
"""LABELS = {"reason":"💭 reason", "act":"🔧 act   ", "observe":"👁  observe",
          "final":"✅ final "}

def print_events(events):
    for kind, step, payload in events:
        if kind == "act":
            body = f"{payload.name}({list(payload.args)})"
        else:
            body = str(payload).strip().replace("\\n", "\\n            ")
        print(f"  step {step}  {LABELS.get(kind, kind)} | {body[:300]}")

def load_precomputed_events(path):
    # Reshape a vendored transcript JSON into agent()'s event tuples.
    d = json.load(open(path))
    ev = []
    for e in d["events"]:
        if e["kind"] == "act":
            ev.append(("act", e["step"], ToolCall(e["tool"], e.get("args", {}))))
        else:
            ev.append((e["kind"], e["step"], e["text"]))
    return ev, d

if OFFLINE:
    EVENTS, _meta = load_precomputed_events(PRECOMP / "02_healthy_run.json")
    print("(OFFLINE) replaying vendored transcript:\\n")
else:
    EVENTS = await agent(TASK, TOOLS, MAX_STEPS)

if VERBOSE:
    print_events(EVENTS)

final = next((p for k, s, p in EVENTS if k == "final"), "(no final answer)")
print("\\nFINAL:", str(final).strip())
"""))

# ── Cell 12 — markdown: VISUAL 1 ─────────────────────────────────────────────
cells.append(md(
"""## VISUAL 1 — the loop as an event timeline

The ReAct circle from the deck, **unrolled in time**. One row per step; colored
segments for reason / act / observe. Watch how each step repeats the same four
moves — that's the loop made visible.
"""))

# ── Cell 13 — VISUAL 1 ───────────────────────────────────────────────────────
cells.append(code(
"""# Build a mini-Gantt: one row per step, a colored segment per move.
phase_color = {"reason": "#4C78A8", "act": "#F58518", "observe": "#54A24B", "final": "#B279A2"}
order = ["reason", "act", "observe", "final"]

by_step = {}
for kind, step, _ in EVENTS:
    by_step.setdefault(step, []).append(kind)

fig, ax = plt.subplots(figsize=(9, 0.7 * max(len(by_step), 1) + 1))
for step in sorted(by_step):
    x = 0
    for kind in order:
        if kind in by_step[step]:
            ax.barh(step, 1.0, left=x, color=phase_color[kind], edgecolor="white")
            ax.text(x + 0.5, step, kind, ha="center", va="center",
                    color="white", fontsize=8, fontweight="bold")
            x += 1.0
ax.set_yticks(sorted(by_step))
ax.set_yticklabels([f"step {s}" for s in sorted(by_step)])
ax.invert_yaxis()
ax.set_xlabel("the four moves, left -> right within each step")
ax.set_title("VISUAL 1 — ReAct loop unrolled: reason -> act -> observe -> (revise)")
ax.set_xlim(0, 4)
handles = [plt.Rectangle((0, 0), 1, 1, color=phase_color[k]) for k in order]
ax.legend(handles, order, ncol=4, loc="lower right", fontsize=8, framealpha=0.9)
plt.tight_layout()
plt.show()
"""))

# ── Cell 14 — markdown: open-loop vs closed-loop ─────────────────────────────
cells.append(md(
"""## Open-loop vs closed-loop — the core claim

The loop beats a single shot **because it checks the world**. Same task, two modes:

- `single_shot`: one model call, **no tools**. It can only *guess* a percentile
  from the filename — it never sees the bytes.
- `closed_loop`: the agent runs `run_python` on the actual CSV and gets the real number.

We print both answers next to the ground truth computed directly with numpy.

**Honest framing:** this is NOT "loops are smarter." A single shot literally
*cannot* know a number that lives in a file it was never given — the loop wins
because it has a *path* to the data, not because it reasons better. A well-behaved
model may *refuse to guess* in single-shot (also a fine outcome) — we show it
rather than hiding it.
"""))

# ── Cell 15 — A/B contrast ────────────────────────────────────────────────────
cells.append(code(
"""# Ground truth, computed directly — no model involved.
def true_p90():
    rows = list(csv.DictReader(open(DATA / "logs" / "oss04.csv")))
    v = np.array([float(r["latency_ms"]) for r in rows])
    return round(float(np.percentile(v, 90)), 2)

def _extract_ms(text):
    # Pull the claimed p90 (in ms) out of free text, ignoring the 50ms SLO threshold
    # the prompt itself mentions (otherwise a refusal that echoes "50ms SLO" looks
    # like a confident guess of 50).
    if not text:
        return None
    nums = [(m.start(), float(m.group(1)))
            for m in re.finditer(r"(\d+(?:\.\d+)?)\s*ms", text)]  # noqa: W605
    # drop any "<n> ms SLO/threshold/limit/target" — that's the SLO, not a claim
    nums = [(pos, v) for (pos, v) in nums
            if not re.match(r"\s*(slo|threshold|limit|target)",
                            text[pos:].split("ms", 1)[-1].lower())]
    # No ms-tagged number that isn't the SLO -> the model gave no real claim
    # (e.g. it refused to guess). Returning None shows that honestly on VISUAL 2.
    return nums[0][1] if nums else None

async def solve(task, mode):
    # A/B as a single function over a mode flag (no duplicated cells).
    if OFFLINE:
        d = json.load(open(PRECOMP / "02_ab_pair.json"))
        return {"answer": d[mode]["answer"],
                "claimed_p90": d[mode].get("claimed_p90"),
                "tool_calls": d[mode].get("tool_calls", 0)}
    if mode == "single_shot":
        # one call, NO tools — the model cannot see the file, so any number is a prior.
        answer = await ask(
            task + " You cannot read the file, so estimate from priors and commit to a "
            "single best-guess number, formatted exactly as '<N> ms'.",
            system="You have NO tools and cannot read files. Give your best estimate "
                   "as a single number in ms; do not refuse.")
        return {"answer": answer, "claimed_p90": _extract_ms(answer), "tool_calls": 0}
    # closed loop — real tools, real bytes
    events = await agent(task, TOOLS, MAX_STEPS)
    final = next((p for k, s, p in events if k == "final"), "")
    n_tools = sum(1 for k, *_ in events if k == "act")
    return {"answer": final, "claimed_p90": _extract_ms(final), "tool_calls": n_tools}

RESULTS = {}
for mode in ["single_shot", "closed_loop"]:
    RESULTS[mode] = await solve(TASK, mode=mode)

TRUTH = true_p90()
print(f"GROUND TRUTH p90 (numpy)        : {TRUTH} ms  ->  {'BREACH' if TRUTH > 50 else 'within'} 50ms SLO\\n")
for mode in ["single_shot", "closed_loop"]:
    r = RESULTS[mode]
    print(f"[{mode}]  claimed p90 = {r['claimed_p90']}  tool_calls = {r['tool_calls']}")
    print(f"   {str(r['answer']).strip()[:400]}\\n")
"""))

# ── Cell 16 — markdown: VISUAL 2 ─────────────────────────────────────────────
cells.append(md(
"""## VISUAL 2 — guess vs grounded vs truth

Watch where each bar lands: the closed-loop bar should sit on the numpy truth;
single-shot misses. The 50 ms SLO line tells you which answers would have raised
the wrong alarm.
"""))

# ── Cell 17 — VISUAL 2 ───────────────────────────────────────────────────────
cells.append(code(
"""# Bars: single-shot guess, closed-loop computed, numpy truth — against the SLO.
ss   = RESULTS["single_shot"]["claimed_p90"]
cl   = RESULTS["closed_loop"]["claimed_p90"]
vals = [("single_shot\\n(guess)", ss, "#F58518"),
        ("closed_loop\\n(computed)", cl, "#54A24B"),
        ("numpy truth", TRUTH, "#4C78A8")]

fig, ax = plt.subplots(figsize=(8, 4))
for i, (label, v, c) in enumerate(vals):
    h = v if v is not None else 0
    ax.bar(i, h, color=c, width=0.6)
    txt = f"{v} ms" if v is not None else "refused\\nto guess"
    ax.text(i, h + 1, txt, ha="center", va="bottom", fontweight="bold")
ax.axhline(50, color="crimson", linestyle="--", linewidth=1.5)
ax.text(2.4, 51, "50ms SLO", color="crimson", va="bottom", ha="right", fontsize=9)
ax.set_xticks(range(len(vals)))
ax.set_xticklabels([v[0] for v in vals])
ax.set_ylabel("p90 write latency (ms)")
ax.set_title("VISUAL 2 — only the closed loop lands on the truth")
ax.set_ylim(0, max([v for _, v, _ in vals if v] + [TRUTH, 50]) * 1.25)
plt.tight_layout()
plt.show()
"""))

# ── Cell 18 — markdown: now break it ─────────────────────────────────────────
cells.append(md(
"""## Now break it — the two classic loop failures

A loop is only as good as its guardrails. We'll induce the two classic *loop*
failures and watch them feed the *context* failure modes from Section 1.

Be precise about vocabulary:

- **Non-termination** and **goal drift** are failures of the loop's **control flow**.
- They are distinct from — but *cause* — Drew Breunig's four **context** failure
  modes: *poisoning, distraction, confusion, clash*
  ([Breunig, 2025](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)).

A runaway loop piles tokens into the window until **distraction** sets in (the model
over-weights its own ballooning transcript) and reliability drops with sheer length —
that's Section 1's **context rot** ([Chroma, 2025](https://research.trychroma.com/context-rot)).
That is the bridge between this notebook and the opening deck.
"""))

# ── Cell 19 — markdown: induce non-termination ───────────────────────────────
cells.append(md(
"""### Induce non-termination + drift

Give the loop a tool that *always* says "not yet", a task with no terminal
condition, and a big step cap. Watch it spin: the goal is never re-asserted, so
it wanders and never stops. We track the context size each step. The 50-step live
spin burns tokens, so `OFFLINE=True` replays a vendored runaway transcript instead.
"""))

# ── Cell 20 — induce non-termination ─────────────────────────────────────────
cells.append(code(
"""def check_status() -> str:
    return "not yet"          # never returns a terminal state -> non-termination

RUNAWAY_TASK = "Wait until batch job 8841 has finished, then report its exit code."
RUNAWAY_MAX_STEPS = 50

if OFFLINE:
    runaway = json.load(open(PRECOMP / "02_runaway.json"))
    steps_taken = len(runaway["cumulative_tokens"])
    tokens_per_step = runaway["cumulative_tokens"]
    terminated = runaway["terminated"]
    print("(OFFLINE) vendored runaway transcript:")
    print(" ", runaway["reason"])
else:
    # Live: poll the never-terminating tool; estimate context growth as chars/4.
    poll_tools = {"check_status": lambda: check_status()}
    context = [Message(role="system", content=(
                   "You may call check_status() by replying with ```tool\\n"
                   "{\\\"name\\\": \\\"check_status\\\", \\\"args\\\": {}}\\n```. "
                   "Report the exit code once the job has finished.")),
               Message(role="user", content=RUNAWAY_TASK)]
    tokens_per_step, terminated = [], False
    cum = sum(len(m.content) for m in context) // 4
    for step in range(RUNAWAY_MAX_STEPS):
        thought = await llm(context)
        call = parse_tool_call(thought)
        if call is None:
            terminated = True
            tokens_per_step.append({"step": step, "cum_tokens": cum + len(thought)//4})
            break
        obs = poll_tools[call.name]()
        context.append(assistant(thought)); context.append(tool_result(obs))
        cum = sum(len(m.content) for m in context) // 4
        tokens_per_step.append({"step": step, "cum_tokens": cum})
    steps_taken = len(tokens_per_step)

print(f"\\nsteps taken: {steps_taken} / {RUNAWAY_MAX_STEPS}   terminated cleanly? {terminated}")
print(f"final window size: ~{tokens_per_step[-1]['cum_tokens']} tokens "
      f"(started ~{tokens_per_step[0]['cum_tokens']})")
print("Diagnosis: no terminal condition + goal never re-asserted -> non-termination + drift -> distraction.")
"""))

# ── Cell 21 — markdown: VISUAL 3 ─────────────────────────────────────────────
cells.append(md(
"""## VISUAL 3 — token growth: runaway vs healthy

Watch the runaway curve climb toward the rot zone while the healthy loop
terminates early. Cost and latency scale with this curve, so on-prem it's a
**budget line**, not just an accuracy one. The rot zone is annotated:
degradation shows up *well below* the hard window limit — a **length** effect
(context rot), distinct from **lost-in-the-middle**, which is a *position* effect
([Liu et al., TACL 2024](https://aclanthology.org/2024.tacl-1.9/)).
"""))

# ── Cell 22 — VISUAL 3 ───────────────────────────────────────────────────────
cells.append(code(
"""# Plot cumulative tokens vs step for the runaway run against a healthy run.
runaway_curve = [d["cum_tokens"] for d in tokens_per_step]
runaway_steps = [d["step"] for d in tokens_per_step]

curves = json.load(open(PRECOMP / "02_token_curves.json"))
healthy_curve = [d["cum_tokens"] for d in curves["healthy"]]
healthy_steps = [d["step"] for d in curves["healthy"]]
ROT_ZONE = curves["budget"]   # degradation tends to begin well below the hard limit

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(runaway_steps, runaway_curve, marker="o", color="#E45756", label="runaway loop")
ax.plot(healthy_steps, healthy_curve, marker="s", color="#54A24B", label="healthy loop (terminates)")
ax.axhspan(ROT_ZONE, max(runaway_curve + [ROT_ZONE]) * 1.05, color="crimson", alpha=0.08)
ax.axhline(ROT_ZONE, color="crimson", linestyle="--", linewidth=1)
ax.text(0.5, ROT_ZONE * 1.02, "context-rot zone (degradation begins BELOW the hard window limit)",
        color="crimson", fontsize=8, va="bottom")
ax.set_xlabel("loop step")
ax.set_ylabel("cumulative context (~tokens)")
ax.set_title("VISUAL 3 — context is a budget, not a bucket")
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()
"""))

# ── Cell 23 — markdown: add the guardrails ────────────────────────────────────
cells.append(md(
"""## Add the guardrails

Three fixes, each one line, each killing a specific failure:

| guardrail | one-liner | kills |
|---|---|---|
| **step cap** | `for step in range(max_steps)` | non-termination |
| **goal re-assertion** | re-inject the goal every turn | drift / distraction (the **Reflexion** move, [Shinn et al., 2023](https://arxiv.org/abs/2303.11366)) |
| **history compaction** | summarize older turns over a token budget | token blowup / context rot (**CONDENSE** from Section 1) |
"""))

# ── Cell 24 — markdown: hardened loop ────────────────────────────────────────
cells.append(md(
"""### The hardened loop

Same loop, three guardrails added inline — run against the **exact task that ran
away for 50 steps above**. The step cap guarantees it stops within `MAX_STEPS`,
goal re-assertion lets the model decide the job is stuck and stop on its own, and
compaction summarizes old turns when the window crosses a budget. Watch the step
count collapse from 50 and the window stay bounded; the compaction events print below.
"""))

# ── Cell 25 — hardened loop ───────────────────────────────────────────────────
cells.append(code(
"""def estimate_tokens(messages):
    return sum(len(m.content) for m in messages) // 4

def compact(context, goal, budget):
    # CONDENSE: replace older turns with a one-line summary; keep system+goal+recent.
    if estimate_tokens(context) <= budget:
        return context, None
    head = context[:1]                       # system prompt
    recent = context[-2:]                     # most recent turn
    middle = context[1:-2]
    summary = Message(role="user", content=(
        f"[COMPACTED {len(middle)} earlier messages] "
        f"Progress so far: polled status, no terminal result yet. Goal still open."))
    return head + [summary] + recent, f"compacted {len(middle)} msgs"

# Same never-terminating scenario as the runaway, now WITH the three guardrails.
HARD_SYS = ("You may call check_status() by replying with ```tool\\n"
            "{\\\"name\\\": \\\"check_status\\\", \\\"args\\\": {}}\\n```. "
            "Report the exit code once the job has finished.")

async def hardened_agent(task, tools, max_steps, token_budget=600):
    context = [Message(role="system", content=HARD_SYS), user(task)]
    events, compactions = [], []
    for step in range(max_steps):                         # GUARDRAIL 1: step cap
        # GUARDRAIL 2: re-assert the goal every turn (anti-drift / Reflexion)
        context.append(Message(role="user", content=f"REMINDER — your goal: {task}"))
        thought = await llm(context) if not OFFLINE else "Job still 'not yet'; stopping."
        events.append(("reason", step, thought))
        call = parse_tool_call(thought) if not OFFLINE else None
        if call is None:
            events.append(("final", step, thought)); break
        obs = tools[call.name](**call.args)
        events.append(("act", step, call)); events.append(("observe", step, obs))
        context.append(assistant(thought)); context.append(tool_result(obs))
        # GUARDRAIL 3: compaction (anti-blowup / CONDENSE) — keeps the window bounded
        context, note = compact(context, task, token_budget)
        if note:
            compactions.append((step, note))
            events.append(("compact", step, note))
    return events, compactions, estimate_tokens(context)

# The SAME task that ran away for 50 steps above — now bounded by the guardrails.
HARD_TASK = RUNAWAY_TASK
HARD_TOOLS = {"check_status": lambda: check_status()}

hard_events, compactions, final_window = await hardened_agent(HARD_TASK, HARD_TOOLS, max_steps=MAX_STEPS)
stopped_early = any(k == "final" for k, *_ in hard_events)
steps_used = max(s for _, s, _ in hard_events) + 1
print(f"runaway above: 50 / 50 steps, never stopped.")
print(f"hardened here: {steps_used} / {MAX_STEPS} steps  "
      f"({'stopped on its own' if stopped_early else 'cut off by the step cap'}).")
print(f"final window: ~{final_window} tokens (compaction budget 600) — bounded, not ballooning.")
print("compaction events:", compactions or "(none needed under budget)")
"""))

# ── Cell 26 — markdown: VISUAL 4 ─────────────────────────────────────────────
cells.append(md(
"""## VISUAL 4 — compaction before/after

Overlay the runaway climb and the compacted curve. Watch compaction flatten the
climb — the loop **editing its own memory to survive**. Each drop is a CONDENSE event.
"""))

# ── Cell 27 — VISUAL 4 ───────────────────────────────────────────────────────
cells.append(code(
"""# Overlay runaway vs compacted token curves; mark each compaction drop.
compacted_curve = [d["cum_tokens"] for d in curves["compacted"]]
compacted_steps = [d["step"] for d in curves["compacted"]]

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(range(len(runaway_curve)), runaway_curve, marker="o", color="#E45756",
        label="runaway (no compaction)")
ax.plot(compacted_steps, compacted_curve, marker="s", color="#4C78A8",
        label="compacted (CONDENSE on budget)")
ax.axhline(curves["budget"], color="gray", linestyle=":", linewidth=1)
ax.text(1, curves["budget"] * 1.02, "token budget", color="gray", fontsize=8)
prev = None
for i, v in enumerate(compacted_curve):
    if prev is not None and v < prev:
        ax.annotate("compact", (i, v), textcoords="offset points", xytext=(0, -14),
                    ha="center", fontsize=7, color="#4C78A8")
    prev = v
ax.set_xlabel("loop step")
ax.set_ylabel("cumulative context (~tokens)")
ax.set_title("VISUAL 4 — compaction lets the loop survive its own memory")
ax.legend(loc="upper left")
plt.tight_layout()
plt.show()
"""))

# ── Cell 28 — markdown: one loop every framework ─────────────────────────────
cells.append(md(
"""## One loop, every framework

You just hand-built what `arcrun.run()` gives you. The same task through the real
framework has the **same event stream, same shape** — just hardened and observable
out of the box.

The Section-1 callback, stated plainly: the guardrails you just added *are* the
harness, and a good harness is worth more than a model upgrade — agent scaffolding
has produced **20+ point swings on SWE-bench on identical weights**
([Particula, 2025](https://particula.tech/blog/agent-scaffolding-beats-model-upgrades-swe-bench)).
Phrase it exactly: **good harness + decent model > weak harness + frontier model**.
For an on-prem deployment that's the thesis: you don't need the biggest model, you
need the loop around it to be sound.
"""))

# ── Cell 29 — markdown: arcrun.run() ─────────────────────────────────────────
cells.append(md(
"""Run the same task through `arcrun.run()` and compare. The 2nd positional arg is
a capability *provider* (`StaticProvider` wraps our tool); the system prompt and
task are positional. Watch the result come back with turns, tool calls, and cost
already measured.
"""))

# ── Cell 30 — arcrun.run() ────────────────────────────────────────────────────
cells.append(code(
"""from arcrun import run, Tool, ToolContext, StaticProvider

# The same run_python capability, wrapped as a framework Tool.
async def run_python_tool_fn(args: dict, ctx: ToolContext) -> str:
    return run_python(args["code"])

run_python_tool = Tool(
    name="run_python",
    description=("Execute a short Python snippet and return its stdout/stderr. "
                 "PRE-BOUND names (do not import / pip-install / use subprocess): "
                 "np (numpy), csv, json, Path, and DATA (a pathlib Path to the data "
                 "dir). Read files via DATA / 'subdir' / 'file.csv'."),
    input_schema={
        "type": "object",
        "properties": {"code": {"type": "string", "description": "Python to execute"}},
        "required": ["code"],
    },
    execute=run_python_tool_fn,
)

if OFFLINE:
    d = json.load(open(PRECOMP / "02_healthy_run.json"))
    print("(OFFLINE) arcrun.run() would produce the same shape:")
    print("  final:", d["events"][-1]["text"])
    print("  turns: 2  tool_calls: 1  (same loop, hardened + observable)")
else:
    result = await run(
        model,
        StaticProvider([run_python_tool]),
        ("You are a careful data agent. Use run_python to compute on local files. "
         "The sandbox has DATA pre-bound (a pathlib Path to the data dir) plus np, "
         "csv, json, Path. Read files via DATA / 'subdir' / 'file.csv' — do not "
         "import, pip-install, or use subprocess."),
        TASK,
        max_turns=MAX_STEPS,
    )
    print(result.content)
    cost = f"${result.cost_usd:.4f}" if result.cost_usd is not None else "n/a"
    print(f"\\nturns: {result.turns}  tool_calls: {result.tool_calls_made}  cost: {cost}")
    print("\\nSame reason->act->observe->revise loop you hand-built — now hardened and observable.")
"""))

# ── Cell 31 — markdown: TODO ──────────────────────────────────────────────────
cells.append(md(
"""## ✅ TODO — give the loop your own tool

Write a **second** tool and a task that needs **two** tool calls in sequence, so
you feel the loop *chain* them. The model plans the order — you don't script it.
Fill in the `read_file` tool below, then run a task that forces `read_file` then
`run_python`.
"""))

# ── Cell 32 — TODO code ───────────────────────────────────────────────────────
cells.append(code(
"""# ✅ TODO — add a second tool, then run a task that needs BOTH in sequence.

async def read_file_tool_fn(args: dict, ctx: ToolContext) -> str:
    # TODO: read up to 2000 chars from args["path"] (resolve against DATA's parent),
    #       and return "Path not found: ..." if it doesn't exist.
    return "TODO"

read_file_tool = Tool(
    name="read_file",
    description="Read up to 2000 chars from a text file.",
    input_schema={
        "type": "object",
        # TODO: describe the "path" property and mark it required.
        "properties": {},
        "required": [],
    },
    execute=read_file_tool_fn,
)

# Once your tool works, run a task that forces read_file THEN run_python.
# Same call shape as the cell above: run(model, StaticProvider([...]), system_prompt, task).
# result = await run(
#     model,
#     StaticProvider([read_file_tool, run_python_tool]),
#     "You are a careful data agent. Use tools.",
#     ("Read data/incidents/storage_incident_2026-04-22.md, then compute the p90 "
#      "of data/logs/oss04.csv and say whether it explains the incident's latency spike."),
#     max_turns=MAX_STEPS,
# )
# print(result.content)   # watch it chain: read -> compute -> answer
"""))

# ── Cell 33 — markdown: Takeaway ─────────────────────────────────────────────
cells.append(md(
"""## Takeaway

> ✅ **Takeaway:** An agent is a loop that **reasons, acts, observes, and revises**
> (ReAct) while **managing its own context window** — and it only earns its keep when
> guardrails (**stop cap**, **goal re-assertion**, **compaction**) keep it from running
> away. Everything from here is about giving that loop better equipment; the first
> piece is the harness.

**Next:** [03 — The Harness →](./03_harness.ipynb)
"""))

# ── Cell 34 — markdown: Sources header ───────────────────────────────────────
cells.append(md(
"""## Sources

The receipts, printed below so they live in the notebook itself.
"""))

# ── Cell 35 — sources code ────────────────────────────────────────────────────
cells.append(code(
"""SOURCES = [
    ("ReAct (reason+act loop)",
     "Yao et al., 2022", "https://arxiv.org/abs/2210.03629"),
    ("Reflexion (verbal self-feedback / goal re-assertion)",
     "Shinn et al., NeurIPS 2023", "https://arxiv.org/abs/2303.11366"),
    ("Context failure modes (poisoning/distraction/confusion/clash)",
     "Breunig, 2025", "https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html"),
    ("Context rot (length effect, 18-model study)",
     "Chroma, 2025", "https://research.trychroma.com/context-rot"),
    ("Lost in the middle (position effect, distinct from rot)",
     "Liu et al., TACL 2024", "https://aclanthology.org/2024.tacl-1.9/"),
    ("Harness > model (20+ pt SWE-bench swing, same weights)",
     "Particula, 2025", "https://particula.tech/blog/agent-scaffolding-beats-model-upgrades-swe-bench"),
]
for title, cite, url in SOURCES:
    print(f"- {title}\\n    {cite} — {url}")
"""))

# ── Write output ──────────────────────────────────────────────────────────────
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
