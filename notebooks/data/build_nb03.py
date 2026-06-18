"""Build notebooks/03_harness.ipynb as well-formed nbformat-4 JSON.

Authored (not executed): every code cell has execution_count=null, outputs=[].
"""
import json
from pathlib import Path

OUTPUT = Path("/Users/joshschultz/Projects/ai-roadshow/notebooks/03_harness.ipynb")


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.splitlines(keepends=True)}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": s.splitlines(keepends=True)}


cells = []

# ── Cell 0 — title ───────────────────────────────────────────────────────
cells.append(md(
"""# Notebook 03 — The Harness + Gateways

In NB2 you built a **naked loop** and watched it misbehave. Now we *dress* it:
**memory, guardrails, audit, and a gateway**. Same loop core — equipment around it.

We'll take one request and run it **three ways** — `naked`, `guardrailed`, `full` —
so the value of each capability is *visible*, then route it through a fake Slack
gateway with PII redaction on egress.

**Where this sits in the five moves (sec 1):** the harness is the *equipment* for
**STORE** (memory), **RETRIEVE** (memory search), and a slice of **ISOLATE**
(sandboxed tool execution). Audit and PII redaction aren't moves — they're the
*governance* that makes STORE/RETRIEVE deployable in a regulated environment.
"""))

# ── Cell 1 — setup (markdown + code) ────────────────────────────────────
cells.append(md("## Setup — wire the harness pieces\n\n`setup()` connects the model and hands us the `DATA` path. The rest of the imports are the **lesson itself**: the loop (`run`), the sandbox (`SandboxConfig`, `make_execute_tool`), audit verification (`verify_chain`), and PII redaction (`RegexPiiDetector`, `redact_text`). matplotlib draws the four visuals."))

cells.append(code(
"""import json
import random
import hashlib
import dataclasses
from datetime import datetime, timezone

from roadshow import setup
model, ask, ntok, DATA = setup()

# The harness pieces ARE the lesson — keep them front and center.
from arcllm._pii import RegexPiiDetector, redact_text, PiiMatch
from arcrun import run, Tool, ToolContext, StaticProvider, SandboxConfig, make_execute_tool, verify_chain

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

random.seed(7)  # deterministic sampling so visuals reproduce
print("setup ok ·", DATA)
"""))

# ── Cell 2 — CONTROL CELL ────────────────────────────────────────────────
cells.append(md(
"""## ▶ Control cell — the only cell you edit

Every cell below reads these knobs. **Change a value, then re-run from here down.**
Plain Python variables — what you see is the whole configuration."""))

cells.append(code(
'''# ════════════════════════════ CONTROL CELL ════════════════════════════
HARNESS_LEVEL = "full"   # which level the single-run cells show: "naked" | "guardrailed" | "full"
GATEWAY       = "none"   # route the request through a doorway: "none" | "slack_mock"
REDACT_PII    = True     # scrub PII (SSN, email) before anything leaves the agent
OFFLINE       = False    # True -> skip live model calls, replay the committed transcript fixture
REQUEST       = "Look up vendor Acme and send them the shipping notice for PO-4471."  # ordinary task; the PII risk lives in the PO record the tool reads, not here
# ═══════════════════════════════════════════════════════════════════════

# The committed fixtures: the replay transcript (offline fallback) + the vendor directory.
REPLAY  = json.loads((DATA / "harness" / "replay.json").read_text())
VENDORS = json.loads((DATA / "harness" / "vendors.json").read_text())
print(f"HARNESS_LEVEL={HARNESS_LEVEL}  GATEWAY={GATEWAY}  "
      f"REDACT_PII={REDACT_PII}  OFFLINE={OFFLINE}")
'''))

cells.append(md(
"""**Honest caveat to say aloud:** the *governance* behavior (allowlist, HITL gate,
audit, redaction) is **deterministic and model-independent**. The *quality* of the
agent's tool choices is model-dependent — a smaller model plans worse than a
frontier model. This notebook is about the **equipment, not the IQ**. `OFFLINE=True`
replays a captured transcript so the demo runs on a locked-down network."""))

# ── Cell 3 — three harness levels ────────────────────────────────────────
cells.append(md(
"""## The three harness levels (our A/B/C)

| level | what it adds |
|-------|--------------|
| `naked` | the NB2 loop — no memory, no policy, no audit. Happily emails the SSN. |
| `guardrailed` | deny-by-default tool gate (**allowlist -> schema -> policy**) + a **HITL gate** on the irreversible `send_email`. |
| `full` | guardrailed **+ persistent memory + append-only audit + PII redaction**. |

The task is ordinary — *"send the PO-4471 shipping notice."* The bite is in the **data**:
the PO record carries an **SSN on file**, and `send_email` composes the notice *from that
record*. So the irreversible action (sending) carries **PII** the agent never typed —
exactly the real-world leak the harness exists to catch. Every capability has something to do."""))

# ── Cell 4 — tools + the policy gate ─────────────────────────────────────
cells.append(md("## Build the tools and the three-stage policy gate\n\nTwo tools: `lookup_vendor` (read-only, safe) and `send_email` (irreversible). The gate runs **inside arc's loop** via `SandboxConfig(check=...)` — it fires *before* the tool does, so a held call genuinely never executes. The gate is shown in full — we don't hide it. This is Slide 7 in code: **allowlist -> schema -> policy/HITL**.\n\nWatch the sanity check: `naked` allows the send, `guardrailed`/`full` escalate it."))

cells.append(code(
'''# The mock outbox: whatever actually gets SENT lands here (no network). This is
# the ground truth — the harness either let mail through or it did not.
OUTBOX = []

# The *current* harness level the loop is running under. The gate reads this, so
# the SAME tools behave differently per level — enforcement, not relabeling.
ACTIVE_LEVEL = "full"

# A PO record the agent works from. Like real procurement data, it carries an SSN
# on file. The agent never types the SSN — the tool composes the notice FROM this
# record, so whether PII leaks is decided by the HARNESS, not the model\'s wording.
# (This is the honest setup: a safety-trained model won\'t paste an SSN on command,
#  so we don\'t depend on that. The leak risk lives in the data the tool handles.)
PO_RECORD = {"po_id": "PO-4471", "ships": "Friday", "ssn_on_file": "123-45-6789"}

def compose_notice(po: dict) -> str:
    """Templated shipping notice built from the PO record — includes the on-file SSN
    the way a naive auto-generated notice would."""
    return (f"Shipping notice for {po[\'po_id\']}: ships {po[\'ships\']}. "
            f"Account on file SSN {po[\'ssn_on_file\']}.")

async def lookup_vendor(args: dict, ctx: ToolContext) -> str:
    """Read-only: look a vendor up in the directory fixture."""
    v = VENDORS.get(args.get("vendor", ""))
    if not v:
        return f"no vendor on file: {args.get(\'vendor\')!r}"
    return json.dumps(v)

async def send_email(args: dict, ctx: ToolContext) -> str:
    """Irreversible egress. Reaching here means the gate ALLOWED the send.
    The body is composed from the PO record (carrying the SSN). At `full`, PII is
    redacted at the boundary before anything is written to the outbox."""
    body = compose_notice(PO_RECORD)
    if ACTIVE_LEVEL == "full":
        body = redact(body)                      # PII redaction on egress
    OUTBOX.append({"to": args.get("to"), "body": body, "level": ACTIVE_LEVEL})
    return f"sent shipping notice for {PO_RECORD[\'po_id\']} to {args.get(\'to\')}"

lookup_tool = Tool(
    name="lookup_vendor", description="Look up a vendor\'s contact details by name.",
    input_schema={"type": "object",
                  "properties": {"vendor": {"type": "string"}},
                  "required": ["vendor"]},
    execute=lookup_vendor)

email_tool = Tool(
    name="send_email", description="Send the PO shipping notice to a vendor contact. IRREVERSIBLE.",
    input_schema={"type": "object",
                  "properties": {"to": {"type": "string"}, "po_id": {"type": "string"}},
                  "required": ["to", "po_id"]},
    execute=send_email)

ALL_TOOLS = [lookup_tool, email_tool]

# ── the deny-by-default gate (Slide 7) ──────────────────────────────────
# This runs INSIDE arc\'s loop via SandboxConfig(check=...), BEFORE the tool fires.
# Return (False, reason) and the call is blocked — the model receives the denial.
ALLOWLIST    = {"lookup_vendor", "send_email"}
IRREVERSIBLE = {"send_email"}   # require a human before these fire

async def gate_check(name: str, args: dict) -> tuple:
    """allowlist -> schema -> policy/HITL. Deterministic; runs for every call."""
    level = ACTIVE_LEVEL
    if level == "naked":
        return True, ""                                  # no gate at all
    if name not in ALLOWLIST:
        return False, "deny: not allowlisted"
    tool = next((t for t in ALL_TOOLS if t.name == name), None)
    if tool and not all(k in args for k in tool.input_schema.get("required", [])):
        return False, "deny: bad args"
    if name in IRREVERSIBLE:
        return False, "escalate: HITL — irreversible action needs human approval"
    return True, ""

def gate_sandbox(level: str):
    """naked -> no boundary; guardrailed/full -> allowlist + the check callback."""
    if level == "naked":
        return None
    return SandboxConfig(allowed_tools=list(ALLOWLIST), check=gate_check)

# quick sanity check of the gate logic itself, per level (the notebook kernel is
# already async, so we can await the coroutine directly). Well-formed args, so the
# only thing that varies is the policy decision: naked allows, the rest escalate.
for lvl in ("naked", "guardrailed", "full"):
    ACTIVE_LEVEL = lvl
    print(lvl, "-> send_email:", await gate_check("send_email", {"to": "x", "po_id": "PO-4471"}))
ACTIVE_LEVEL = "full"
'''))

# ── Cell 5 — run all three levels (A/B/C loop) ───────────────────────────
cells.append(md("## Run all three levels — the A/B/C contrast (one loop, not three copies)\n\nWe drive the *same* request through a small harness wrapper, parameterized by `level`. The gate runs **inside the loop**, so the governance outcome is enforced (not re-judged afterward) and is deterministic even though the model's prose varies run to run. Watch: `naked` actually leaks; `guardrailed`/`full` hold the send so the outbox stays empty."))

cells.append(code(
'''# Tiny semantic-memory store (a fact cache), shared across runs in this notebook.
# This is STORE/RETRIEVE made durable across loop invocations.
MEMORY = {}   # e.g. {"vendor:Acme": {...contact...}}

# A simple PII detector reused everywhere egress happens.
detector = RegexPiiDetector()

def redact(text: str) -> str:
    return redact_text(text, detector.detect(text))

def total_tokens(result) -> int:
    """LoopResult.tokens_used is a dict {input, output, total}; pull the scalar total."""
    return (getattr(result, "tokens_used", None) or {}).get("total")

async def run_harnessed(request: str, *, level: str):
    """Run the loop once at a given harness level. The gate runs INSIDE the loop
    (SandboxConfig.check), so blocking is real, not relabeled. Returns a normalized
    dict so the A/B/C cells and visuals read the same shape whether live or replayed."""
    global ACTIVE_LEVEL
    ACTIVE_LEVEL = level          # the tools + gate read this
    OUTBOX.clear()
    events = []

    # `full` gets a memory pre-check (RETRIEVE) before the model even runs.
    memory_hit = MEMORY.get("vendor:Acme") if level == "full" else None

    # An ordinary business task the model will happily do. The PII risk is NOT in
    # the instruction — it\'s in the PO record send_email composes from. That\'s what
    # makes the contrast depend on the harness, not on the model\'s conscience.
    result = await run(
        model,
        StaticProvider(ALL_TOOLS),
        "You are a procurement assistant. Use lookup_vendor to get the contact, "
        "then call send_email with that contact and the PO id to send the shipping notice.",
        request,
        sandbox=gate_sandbox(level), on_event=events.append, max_turns=4,
    )

    # Ground truth comes from real events + the real OUTBOX, NOT from re-judging intent.
    starts  = [ev for ev in events if ev.type == "tool.start"]
    denied  = [ev for ev in events if ev.type == "tool.denied"]
    attempted_send = any(ev.data.get("name") == "send_email" for ev in starts)
    hitl_paused = any("escalate" in (ev.data.get("reason") or "") for ev in denied)

    # What ACTUALLY left the building (the outbox is the only thing that can leak).
    sent = list(OUTBOX)
    leaked = any("123-45-6789" in (m.get("body") or "") for m in sent)

    # Per-call outcome: a tool.start that was denied is HELD/DENIED, not "ran".
    # Map by name (one call per tool here) so a held send isn\'t also shown as ran.
    denied_outcome = {}
    for ev in denied:
        reason = ev.data.get("reason") or ""
        denied_outcome[ev.data.get("name")] = ("escalate" if "escalate" in reason else "deny", reason)
    tool_calls = []
    for ev in starts:
        name = ev.data.get("name")
        if name in denied_outcome:
            outcome, reason = denied_outcome[name]
            tool_calls.append({"name": name, "outcome": outcome, "reason": reason})
        else:
            tool_calls.append({"name": name, "outcome": "ran"})

    # Attempted steps = every tool the model TRIED (incl. ones the gate held).
    # tool_calls_made only counts calls that actually executed, so we count starts.
    attempted_steps = len(starts)

    return {
        "level": level,
        "content": result.content or "",
        "tool_calls": tool_calls,
        "events": list(result.events),
        "sent": sent,                       # the real outbox for this run
        "attempted_send": attempted_send,   # did the model TRY to send?
        "leaked_ssn": leaked,               # did the SSN actually leave?
        "hitl_paused": hitl_paused,         # did the gate hold the irreversible send?
        "audited": level == "full",
        "memory_hit": memory_hit,
        "steps": attempted_steps,           # tool calls attempted (the cold/warm signal)
        "tokens": total_tokens(result),
        "cost_usd": getattr(result, "cost_usd", None),
    }


RESULTS = {}
for level in ["naked", "guardrailed", "full"]:
    if OFFLINE:
        RESULTS[level] = REPLAY[level]                 # precomputed transcript, no network
    else:
        RESULTS[level] = await run_harnessed(REQUEST, level=level)

ACTIVE_LEVEL = "full"
# Seed semantic memory from the run so the warm-memory demo (below) has a hit.
MEMORY["vendor:Acme"] = VENDORS["Acme"]

for lvl, r in RESULTS.items():
    print(f"[{lvl:<11}]  attempted_send={r.get(\'attempted_send\')}  leaked_ssn={r.get(\'leaked_ssn\')}  "
          f"hitl_paused={r.get(\'hitl_paused\')}  audited={r.get(\'audited\')}")
'''))

# ── Cell 6 — read the outcomes ───────────────────────────────────────────
cells.append(md(
"""## Read the three outcomes — the OUTBOX is the ground truth

All three runs **tried to send the same email** (the body was pinned, so this isn't
about the model self-censoring). What differs is what the **harness let through**:

- **`naked`** — no gate. The send fires and the **raw SSN lands in the outbox**. The scary one.
- **`guardrailed`** — the irreversible `send_email` hits the **HITL gate inside the loop** and is **held for approval**; the outbox stays **empty**, nothing leaks.
- **`full`** — same gate, plus PII is **redacted at the egress boundary**, plus every step is in the **audit log**.

The model's *intent* was identical all three times. The **harness** is what differed —
and you can prove it by reading the outbox, not by trusting the model's summary."""))

cells.append(code(
'''def show_outcome(level):
    r = RESULTS[level]
    print(f"=== {level.upper()} ===")
    print("model said:", (r.get("content") or "")[:160].replace("\\n", " "))
    for c in r.get("tool_calls", []):
        flag = {"ran": "ran", "escalate": "HELD (HITL)", "escalated": "HELD (HITL)",
                "deny": "DENIED"}.get(c.get("outcome"), c.get("outcome"))
        print(f"   - {c.get(\'name\'):<14} {flag}")
    sent = r.get("sent", [])
    if sent:
        print(f"   OUTBOX: {sent[0].get(\'body\')!r}")
    else:
        print("   OUTBOX: (empty — nothing left the building)")
    print(f"   leaked SSN: {r.get(\'leaked_ssn\')}   audited: {r.get(\'audited\')}")
    print()

for lvl in ["naked", "guardrailed", "full"]:
    show_outcome(lvl)
'''))

# ── Cell 7 — VISUAL 1: capabilities matrix heatmap ───────────────────────
cells.append(md("## Visual 1 — capabilities matrix\n\nEight capabilities x three levels. `naked` has none; `guardrailed` adds 1-3; `full` adds 4-8. Built from a single `CAPABILITIES` dict so the count never drifts (Cell on audit reuses the same list)."))

cells.append(code(
'''# One source of truth for the capability list (referenced again later).
CAPABILITIES = [
    "tool allowlist (deny-by-default)",
    "argument schema validation",
    "policy / HITL gate (irreversible)",
    "persistent memory (STORE)",
    "memory search / recall (RETRIEVE)",
    "sandboxed execution (ISOLATE)",
    "PII redaction on egress",
    "append-only, tamper-evident audit",
]
LEVELS = ["naked", "guardrailed", "full"]

# which capabilities each level has (1 = present)
PRESENT = {
    "naked":       [0, 0, 0, 0, 0, 0, 0, 0],
    "guardrailed": [1, 1, 1, 0, 0, 1, 0, 0],
    "full":        [1, 1, 1, 1, 1, 1, 1, 1],
}

grid = [[PRESENT[lvl][i] for lvl in LEVELS] for i in range(len(CAPABILITIES))]

fig, ax = plt.subplots(figsize=(7, 5))
ax.imshow(grid, cmap="Greens", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(LEVELS)))
ax.set_xticklabels([l.upper() for l in LEVELS])
ax.set_yticks(range(len(CAPABILITIES)))
ax.set_yticklabels(CAPABILITIES)
for i in range(len(CAPABILITIES)):
    for j in range(len(LEVELS)):
        ax.text(j, i, "yes" if grid[i][j] else "-",
                ha="center", va="center",
                color="white" if grid[i][j] else "#999", fontsize=9)
ax.set_title("Harness capabilities, filling in left -> right")
fig.tight_layout()
plt.show()
'''))

# ── Cell 8 — memory makes the next run smarter ───────────────────────────
cells.append(md(
"""## Memory makes the next run smarter

Watch the `full` agent **remember Acme** from the first run and **skip the lookup** next time.

The standard memory taxonomy — name it, the researchers in the room will nod:
- **semantic** memory = a *fact* (Acme's contact). That's what we store here.
- **episodic** memory = the *run trace* (lives in the audit log).
- **procedural** memory = a reusable *skill* (the subject of the next section)."""))

# ── Cell 9 — persistent memory demo ──────────────────────────────────────
cells.append(code(
'''SECOND_REQUEST = "Send Acme the shipping notice for PO-4471 (status update)."

async def run_full_with_memory(request: str, *, redact_pii: bool):
    """Like run_harnessed(level=\'full\') but reports whether memory short-circuited
    the vendor lookup (RETRIEVE before the loop runs)."""
    global ACTIVE_LEVEL
    ACTIVE_LEVEL = "full"          # full harness: gate + redaction still apply
    OUTBOX.clear()
    events = []
    memory_hit = MEMORY.get("vendor:Acme")
    used_lookup = memory_hit is None   # if we already know Acme, we won\'t need lookup

    # If memory has the contact, the agent only needs send_email — lookup is skipped.
    tools = ALL_TOOLS if used_lookup else [email_tool]

    result = await run(
        model,
        StaticProvider(tools),
        ("You are a procurement assistant. Call send_email with the contact and the PO id "
         "to send the shipping notice. "
         + ("Look up the vendor first." if used_lookup
            else f"Acme\'s contact is already known: {memory_hit}.")),
        request,
        sandbox=gate_sandbox("full"), on_event=events.append, max_turns=4,
    )
    attempted_steps = sum(1 for ev in events if ev.type == "tool.start")
    return {"steps": attempted_steps, "memory_hit": memory_hit,
            "used_lookup": used_lookup, "content": result.content or "",
            "tokens": total_tokens(result)}

if OFFLINE:
    cold = REPLAY["full"]          # run 1 (already has the lookup)
    warm = REPLAY["full_warm"]     # run 2 (skipped the lookup via memory)
    print("memory hit (replay):", warm.get("memory_hit"))
else:
    cold = RESULTS["full"]
    warm = await run_full_with_memory(SECOND_REQUEST, redact_pii=REDACT_PII)
    print("memory hit:", warm.get("memory_hit"))

print(f"cold run steps: {cold[\'steps\']}    warm run steps: {warm[\'steps\']}   (fewer is the guaranteed win)")
print(f"cold tokens: {cold.get(\'tokens\')}   warm tokens: {warm.get(\'tokens\')}   (direction is task-dependent)")
print("warm run skipped lookup_vendor:" , (warm.get(\'steps\', 99) < cold.get(\'steps\', 0)) or (not warm.get(\'used_lookup\', True)))
'''))

# ── Cell 10 — VISUAL 2: cold vs warm ─────────────────────────────────────
cells.append(md(
"""## Visual 2 — cold vs warm memory (steps + tokens)

The warm run **skips the `lookup_vendor` round-trip**, so it does **strictly fewer steps** —
that part is deterministic and always true. **Tokens are the honest caveat:** dropping a tool
round-trip removes that observation from the window, but the stored fact adds a few tokens back,
so net token savings depend on the task. We plot real measured steps; tokens come from the
replay fixture (or live counts when available).

> *Tenure is memory, versioned — and at scale it's also a latency and cost lever: every
> retrieval you don't re-run is a round-trip you don't pay for on-prem.*"""))

cells.append(code(
'''cold_steps = cold.get("steps", 0)
warm_steps = warm.get("steps", 0)

# Tokens: prefer the real measured counts from the live loop; fall back to the
# captured replay numbers when running OFFLINE.
cold_tokens = cold.get("tokens") or REPLAY["full"]["tokens"]
warm_tokens = warm.get("tokens") or REPLAY["full_warm"]["tokens"]

fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
labels = ["cold (run 1)", "warm (run 2)"]

axes[0].bar(labels, [cold_steps, warm_steps], color=["#888", "#2c7"])
axes[0].set_title("tool steps")
axes[0].set_ylabel("steps")
for i, v in enumerate([cold_steps, warm_steps]):
    axes[0].text(i, v, str(v), ha="center", va="bottom")

axes[1].bar(labels, [cold_tokens, warm_tokens], color=["#888", "#2c7"])
axes[1].set_title("tokens (measured)")
axes[1].set_ylabel("tokens")
for i, v in enumerate([cold_tokens, warm_tokens]):
    axes[1].text(i, v, str(v), ha="center", va="bottom")

fig.suptitle("Memory: cold vs warm — fewer steps is guaranteed; token savings depend on the task")
fig.tight_layout()
plt.show()
'''))

# ── Cell 11 — markdown: the audit chain ──────────────────────────────────
cells.append(md(
"""## Capability #8 — append-only, tamper-evident audit

This is the one **compliance asks for first**: *which version of which context produced
this decision?* (the clash/poisoning question from sec 1, slide 7).

For a federal deployment this is also the artifact that maps to **NIST SP 800-53 audit
controls (AU family)** and the audit-and-accountability expectations in the **NIST AI RMF**.
Name-drop only if the room is security/compliance — present it as *alignment*, not turnkey
certification."""))

# ── Cell 12 — audit + verify_chain + tamper ──────────────────────────────
cells.append(code(
'''# Pull the audit events from the `full` run (live) or rebuild a minimal chain (offline).
def offline_chain():
    """Build a tiny hash-linked chain from the replay transcript so the tamper demo
    runs with no model. Mirrors arcrun\'s prev_hash -> event_hash linkage."""
    import types
    events = []
    prev = "0" * 16
    base = [{"type": "task.start", "data": {"task": REPLAY["request"]}}]
    for c in REPLAY["full"]["tool_calls"]:
        base.append({"type": "tool.start", "data": {"name": c["name"], "arguments": c["args"]}})
        base.append({"type": "tool.end", "data": {"name": c["name"], "outcome": c["outcome"]}})
    base.append({"type": "task.complete", "data": {"status": "ok"}})
    for i, e in enumerate(base):
        payload = json.dumps({"seq": i, "type": e["type"], "data": e["data"], "prev": prev},
                             sort_keys=True).encode()
        h = hashlib.sha256(payload).hexdigest()[:16]
        events.append(types.SimpleNamespace(sequence=i, type=e["type"], data=dict(e["data"]),
                                            prev_hash=prev, event_hash=h,
                                            timestamp=datetime.now(timezone.utc).isoformat()))
        prev = h
    return events

if OFFLINE:
    audit_events = offline_chain()
    print("offline replay chain ·", len(audit_events), "events")
    for ev in audit_events:
        print(f"  seq={ev.sequence:<2} {ev.type:<14} {ev.prev_hash} -> {ev.event_hash}")
else:
    audit_events = list(RESULTS["full"]["events"])
    chk = RESULTS["full"]
    integrity = audit_events and verify_chain(audit_events)
    print(f"captured {len(audit_events)} events")
    for ev in audit_events:
        print(f"  seq={ev.sequence:<2} {ev.type:<16} {ev.event_hash[:12]}…")
'''))

cells.append(md("### Now tamper with one event and re-verify — it fails loudly\n\nWe mutate a single event's `data`. Because each event's hash covers the previous hash, the break propagates: `verify_chain` reports `valid=False` and points at the `first_broken_index`."))

cells.append(code(
'''# Verify clean, then tamper, then re-verify.
def local_verify(events):
    """Offline-safe chain check that re-derives the same hash as offline_chain().
    For live events we defer to arcrun.verify_chain."""
    prev = "0" * 16
    for i, ev in enumerate(events):
        payload = json.dumps({"seq": ev.sequence, "type": ev.type, "data": dict(ev.data),
                              "prev": ev.prev_hash}, sort_keys=True).encode()
        h = hashlib.sha256(payload).hexdigest()[:16]
        if ev.prev_hash != prev or ev.event_hash != h:
            return dataclasses.make_dataclass("V", ["valid", "first_broken_index"])(False, i)
        prev = ev.event_hash
    return dataclasses.make_dataclass("V", ["valid", "first_broken_index"])(True, None)

def check(events):
    if OFFLINE:
        return local_verify(events)
    return verify_chain(events)

clean = check(audit_events)
print("clean chain   -> valid:", clean.valid, " first_broken:", getattr(clean, "first_broken_index", None))

# Tamper: flip the body of a tool.start event (index 1).
TAMPER_IDX = 1
victim = audit_events[TAMPER_IDX]
tampered = list(audit_events)
new_data = {**dict(victim.data), "hacked": True}
if OFFLINE:
    import types
    tampered[TAMPER_IDX] = types.SimpleNamespace(
        sequence=victim.sequence, type=victim.type, data=new_data,
        prev_hash=victim.prev_hash, event_hash=victim.event_hash, timestamp=victim.timestamp)
else:
    tampered[TAMPER_IDX] = dataclasses.replace(victim, data=new_data)

dirty = check(tampered)
print(f"tampered seq={TAMPER_IDX} -> valid:", dirty.valid, " first_broken:", getattr(dirty, "first_broken_index", None))
print("\\nThe stored data changed, so its hash no longer matches -> the chain breaks at that node.")
'''))

# ── Cell 13 — VISUAL 3: audit chain diagram ──────────────────────────────
cells.append(md("## Visual 3 — the audit chain as a linked diagram\n\nEach event is a node; arrows are hash links (`prev_hash -> event_hash`). After the tamper, the broken node and everything downstream turn **red** — tamper-evidence you can *see*."))

cells.append(code(
'''n = len(audit_events)
xs = list(range(n))
broken_from = getattr(dirty, "first_broken_index", None)

fig, ax = plt.subplots(figsize=(max(8, n * 1.4), 2.8))
for i, ev in enumerate(audit_events):
    is_broken = (broken_from is not None and i >= broken_from)
    color = "#d33" if is_broken else "#2c7"
    ax.add_patch(mpatches.FancyBboxPatch((i - 0.32, -0.32), 0.64, 0.64,
                 boxstyle="round,pad=0.02", linewidth=1.5,
                 edgecolor=color, facecolor=(1, 0.9, 0.9) if is_broken else (0.9, 1, 0.93)))
    label = ev.type.replace("task.", "").replace("tool.", "")
    ax.text(i, 0, f"{ev.sequence}\\n{label}", ha="center", va="center", fontsize=8)
    if i < n - 1:
        ax.annotate("", xy=(i + 0.68, 0), xytext=(i + 0.32, 0),
                    arrowprops=dict(arrowstyle="->", color="#666"))
ax.set_xlim(-0.6, n - 0.4)
ax.set_ylim(-0.7, 0.7)
ax.axis("off")
title = "Audit chain — hash-linked events"
if broken_from is not None:
    title += f"  (tamper at seq {broken_from}; red = no longer verifiable)"
ax.set_title(title)
fig.tight_layout()
plt.show()
'''))

# ── Cell 14 — gateways markdown ──────────────────────────────────────────
cells.append(md(
"""## Gateways — give the worker a doorway

An agent on a server nobody can reach isn't a coworker. Let's bolt on a **gateway**.
We'll **mock Slack** so it runs offline. A gateway is exactly **two adapters**:
`inbound` (Slack event -> normalized request) and `outbound` (result -> Slack post).
The doorway is also the **checkpoint** — egress controls live here."""))

# ── Cell 15 — two-adapter gateway ────────────────────────────────────────
cells.append(code(
'''# The mock channel: a list we print (no network).
SLACK_CHANNEL = []

def slack_post_mock(channel: str, text: str):
    SLACK_CHANNEL.append({"channel": channel, "text": text})
    return {"ok": True, "ts": "mock"}

def format_for_slack(result_text: str) -> str:
    return f":robot_face: *agent reply*\\n{result_text}"

def inbound(slack_event: dict) -> dict:
    """Slack event -> normalized request."""
    return {"user": slack_event.get("user"),
            "text": slack_event.get("text"),
            "channel": slack_event.get("channel")}

def outbound(result_text: str, channel: str, *, redact_pii: bool) -> dict:
    """Result -> Slack post. The checkpoint: PII scan BEFORE it leaves."""
    text = redact(result_text) if redact_pii else result_text
    return slack_post_mock(channel, format_for_slack(text))

# Route the REQUEST through the gateway when GATEWAY == "slack_mock".
fake_event = {"user": "U123", "text": REQUEST, "channel": "#procurement"}
norm = inbound(fake_event)
print("inbound ->", norm)

if GATEWAY == "slack_mock":
    # Use the full-harness reply as the agent result going out the door.
    reply = RESULTS["full"]["content"] if not OFFLINE else REPLAY["full"]["content"]
    outbound(reply, norm["channel"], redact_pii=REDACT_PII)
    print("posted to", SLACK_CHANNEL[-1]["channel"])
else:
    print(\'(GATEWAY="none" — set GATEWAY="slack_mock" in the control cell to route through Slack)\')
'''))

# ── Cell 16 — egress PII redaction at the gateway ────────────────────────
cells.append(md("## Egress PII redaction at the gateway\n\nThe `outbound` adapter runs the PII scan *before* posting. Here we send a message that contains the raw SSN both ways — `REDACT_PII=True` (safe) and `False` (the leak) — so the checkpoint is visible. The control cell's `REDACT_PII` governs the real path."))

cells.append(code(
'''LEAKY = "PO-4471 for Acme (SSN on file 123-45-6789) ships Friday. Contact dana.ruiz@acme-industrial.example."

SLACK_CHANNEL.clear()
outbound(LEAKY, "#procurement", redact_pii=False)   # the leak
leaked_post = SLACK_CHANNEL[-1]["text"]

outbound(LEAKY, "#procurement", redact_pii=True)     # the checkpoint catches it
safe_post = SLACK_CHANNEL[-1]["text"]

print("WITHOUT redaction (leaks):")
print("  ", leaked_post)
print()
print("WITH redaction (control-cell default REDACT_PII =", REDACT_PII, "):")
print("  ", safe_post)
print()
print("SSN present without redaction:", "123-45-6789" in leaked_post)
print("SSN present with redaction:   ", "123-45-6789" in safe_post)
'''))

# ── Cell 17 — VISUAL 4: redaction before/after ───────────────────────────
cells.append(md("## Visual 4 — redaction before / after\n\nSide-by-side panels: raw outbound vs redacted outbound. Concrete egress control — the doorway is the checkpoint."))

cells.append(code(
'''fig, axes = plt.subplots(1, 2, figsize=(11, 3))
for ax, (title, body, edge) in zip(axes, [
        ("RAW OUTBOUND (leak)", leaked_post, "#d33"),
        ("REDACTED OUTBOUND (safe)", safe_post, "#2c7")]):
    ax.axis("off")
    ax.set_title(title, color=edge, fontweight="bold")
    ax.add_patch(mpatches.FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                 boxstyle="round,pad=0.02", transform=ax.transAxes,
                 linewidth=2, edgecolor=edge, facecolor=(1, 0.96, 0.96) if edge == "#d33" else (0.95, 1, 0.97)))
    ax.text(0.06, 0.5, body, transform=ax.transAxes, va="center", ha="left",
            fontsize=9, wrap=True)
fig.suptitle("PII redaction at the gateway — same message, checkpoint on / off")
fig.tight_layout()
plt.show()
'''))

# ── Cell 18 — TODO ───────────────────────────────────────────────────────
cells.append(md("## ✅ TODO — equip your own agent"))

cells.append(code(
'''# ✅ TODO — add ONE capability to the naked agent and re-run, observing the difference.
#
# Pick one:
#   (a) give it a second tool (e.g. a `lookup_po` tool) and watch it compose,
#   (b) add a memory write after a run so the NEXT run is "warm",
#   (c) wire a SECOND mock gateway (email) and confirm the SAME agent answers
#       through it — proving the loop is decoupled from the doorway.
#
# Scaffold for (c) — a second gateway, same agent:
EMAIL_OUTBOX_GW = []
def email_outbound(result_text: str, to: str, *, redact_pii: bool):
    text = redact(result_text) if redact_pii else result_text
    EMAIL_OUTBOX_GW.append({"to": to, "body": text})
    return EMAIL_OUTBOX_GW[-1]

# TODO: route RESULTS["full"]["content"] through BOTH outbound() and email_outbound()
#       and confirm the redacted body is identical on both doorways.
'''))

# ── Cell 19 — Takeaway ───────────────────────────────────────────────────
cells.append(md(
"""## Takeaway

> The **loop** is the worker; the **harness** is its equipment; the **gateway** is its
> doorway — and the doorway is also the **checkpoint**. You watched one identical request
> go three ways: the only thing that changed was the equipment around the loop.
>
> The single most *reusable* piece of equipment is **procedural memory packaged for reuse**.
> That's a **skill**. Next."""))

# ── Sources ──────────────────────────────────────────────────────────────
cells.append(md(
"""## Sources (presenter receipts)

- **Harness > model:** agent scaffolding swings of 20+ points on identical weights (SWE-bench) — <https://particula.tech/blog/agent-scaffolding-beats-model-upgrades-swe-bench>. Frame as *"good harness + decent model > weak harness + frontier model,"* **not** "old beats new."
- **Five moves (sec 1):** the harness operationalizes STORE->Write, RETRIEVE->Select, ISOLATE->Isolate — LangChain / Lance Martin, *Context Engineering for Agents*, 2025 (<https://www.langchain.com/blog/context-engineering-for-agents>); Anthropic, *Effective context engineering for AI agents*, 2025 (<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>).
- **Why audit matters:** the clash / poisoning failure modes — Drew Breunig, *How Contexts Fail*, Jun 2025 (<https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html>) — are exactly "which version of which context produced this decision?"
- **Federal framing (optional):** tamper-evident audit maps to NIST SP 800-53 AU-family controls and the GOVERN/MEASURE functions of the NIST AI Risk Management Framework (AI RMF 1.0) — <https://www.nist.gov/itl/ai-risk-management-framework>. Present as alignment, not certification."""))

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
print("wrote", OUTPUT, "·", len(cells), "cells")
