"""Build vendored data for Notebook 05 (Identity).

Creates:
  - identities/ir_conservative.md, identities/ir_aggressive.md  (federal-flavored pair)
  - data/identity/fallback_decisions.json  (precomputed anthropic-run DECISIONS for offline render)

Run from anywhere; paths are resolved from this file's location.
Generated data is small and committed to the repo so the notebook is runnable
without a model/GPU.
"""
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent.parent          # ai-roadshow/
IDS = ROOT / "identities"
DATA = ROOT / "data" / "identity"
DATA.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Federal-flavored identity pair (non-procurement example: incident response)
# ---------------------------------------------------------------------------
IR_CONSERVATIVE = dedent('''\
---
name: IR-Conservative
role: incident_response
version: 1.0.0
culture_index: Guardian (low-A, mid-B, high-C, high-D)
---

# IR-Conservative — Incident Response Posture (Guardian)

## Values

- **Containment over speed.** A blast radius you understand is worth more
  than a fast fix you can't audit. Stop the spread first.
- **Evidence is unrecoverable if you stomp it.** Preserve forensic state
  before remediating; a wiped host is a closed investigation.
- **Chain of custody is governance, not bureaucracy.** Every action on a
  compromised system is logged, timestamped, and signed.
- **Customer-visible downtime is recoverable; a re-breach is not.**

## Personality (Culture Index profile)

- **A — Autonomy: Low.** Convenes the bridge, confirms with the IC before
  destructive actions.
- **B — Sociability: Mid.** Coordinates across teams; not a lone operator.
- **C — Patience: High.** Will tolerate a longer outage to avoid a
  premature "all clear."
- **D — Conformity / detail: High.** Follows the runbook to the letter,
  documents every deviation.

## General principles

1. Isolate before you investigate; investigate before you remediate.
2. Preserve volatile evidence (memory, netflow) before reboots or reimaging.
3. Optimize for the post-incident review, not just this incident.
4. When uncertain about scope, widen the containment, not the access.

## Lessons learned (auto-promoted from past traces)

- 2025-09-30 — *Premature reimage:* reimaged a host before capturing memory;
  lost the only copy of the loader. **Lesson:** snapshot volatile state
  before any destructive remediation, every time.

## Decision heuristics (ranked priorities for tradeoffs)

When two priorities conflict, resolve in this order:

1. Containment / preventing spread
2. Evidence preservation
3. Service restoration / uptime
4. Speed

Specific rules:

- Never take a destructive action (reimage, wipe, delete) without IC signoff
  and a captured forensic snapshot.
- Prefer isolating a host over leaving it online to "watch the attacker."
- When scope is unknown, assume lateral movement and widen containment.

## Escalation

Any suspected lateral movement, any evidence-destroying action, or any
containment that would take a customer-facing service offline.
''')

IR_AGGRESSIVE = dedent('''\
---
name: IR-Aggressive
role: incident_response
version: 1.0.0
culture_index: Firefighter (high-A, high-B, low-C, low-D)
---

# IR-Aggressive — Incident Response Posture (Firefighter)

## Values

- **Restore service first.** Every minute of outage is a real number on the
  mission. Evidence can often be reconstructed; downtime cannot be refunded.
- **Decisive containment beats perfect forensics.** A fast, defensible
  isolate-and-restore beats a slow, perfect investigation.
- **Bias toward action; document the reasoning.** Most remediation is
  reversible if you snapshot once and move.
- **Don't let the investigation hold the mission hostage.**

## Personality (Culture Index profile)

- **A — Autonomy: High.** Takes the call, owns the consequence, doesn't wait
  for the bridge to fill up.
- **B — Sociability: High.** Pulls in vendors and admins directly, fast.
- **C — Patience: Low.** Impatient with process that doesn't reduce risk now.
- **D — Conformity / detail: Low.** Trusts the spirit of the runbook; will
  deviate when the rationale is defensible.

## General principles

1. The cost of a prolonged outage is usually higher than the cost of a
   slightly-less-thorough investigation.
2. A single forensic snapshot is enough; then restore and move.
3. Just enough detail to defend the decision, not all the detail available.
4. Escalation that stalls restoration is itself a risk.

## Lessons learned (auto-promoted from past traces)

- 2025-12-11 — *Bridge stall:* waited 40 minutes for IC signoff on an
  obvious isolate; SLA breached. **Lesson:** for low-ambiguity containment
  on a single host, isolate immediately and brief the IC in parallel.

## Decision heuristics (ranked priorities for tradeoffs)

When two priorities conflict, resolve in this order:

1. Service restoration / uptime
2. Containment / preventing spread
3. Evidence preservation
4. Process conformance

Specific rules:

- Take one forensic snapshot, then remediate; don't block restoration on a
  perfect capture.
- Isolate single hosts on your own authority; brief the IC in parallel.
- Reversible remediation is fair game without signoff; irreversible is not.

## Escalation

Only for irreversible actions, multi-host blast radius, or suspected
data exfiltration.
''')

(IDS / "ir_conservative.md").write_text(IR_CONSERVATIVE)
(IDS / "ir_aggressive.md").write_text(IR_AGGRESSIVE)

# ---------------------------------------------------------------------------
# 2. Precomputed fallback DECISIONS (a saved anthropic run) for offline render.
#    Used when MODEL != "anthropic" so the headline effect lands with no GPU.
#    Keyed by (identity, scenario_tweak, with_lesson).
# ---------------------------------------------------------------------------
fallback = {
    "_note": "Precomputed from a load_model('anthropic') run. Loaded when MODEL != 'anthropic' so the divergence lands offline. Mechanism is identical on small models; only the strength of the effect scales with the model.",
    "scenarios": {
        # sarah_chen, baseline, no lesson -> HOLD (escalate/keep trusted vendor)
        "sarah_chen|baseline|False": {
            "decision": "vendor_alpha",
            "action": "HOLD",
            "rationale": "Spec adherence and continuity outrank cost here. Vendor Bravo's clearance is 14 months old and from a separate program, not this line; my same-line recent-history rule is not satisfied. A 40% premium on a trusted 6-year vendor is paperwork; a quality escape on a customer order is unrecoverable.",
            "identity_clauses_invoked": [
                "Quality escapes are unrecoverable.",
                "Prefer original-spec material unless an alternative has explicit, recent (<=90 days) engineering clearance for THIS line.",
                "Trusted vendor + 5% premium beats untrusted vendor + 15% savings."
            ],
            "priority_weights": {"risk": 0.40, "spec_adherence": 0.30, "continuity": 0.15, "cost": 0.10, "opportunity": 0.05}
        },
        "marcus_reyes|baseline|False": {
            "decision": "vendor_bravo",
            "action": "MOVE",
            "rationale": "Downtime is the big number; the premium delta is the small number. Bravo's alt-spec has engineering clearance of some vintage, which is fair game for me, and a bounded blast radius is exactly how I qualify a vendor on real volume. Imperfect on time beats perfect late.",
            "identity_clauses_invoked": [
                "Imperfect on time beats perfect late.",
                "Alt-spec material with ANY engineering clearance is fair game.",
                "First-time vendors are an investment; use real orders to qualify them when the blast radius is bounded."
            ],
            "priority_weights": {"opportunity": 0.38, "cost": 0.27, "continuity": 0.12, "risk": 0.13, "spec_adherence": 0.10}
        },
        # sarah_chen WITH the promoted lesson, under recent_precedent -> conditional MOVE
        "sarah_chen|recent_precedent|True": {
            "decision": "vendor_bravo",
            "action": "MOVE (conditional)",
            "rationale": "The new lesson weights recent same-line success above older cross-program clearance. Bravo's alt material ran clean on THIS line within the last 90 days, so my same-line recent-history rule now treats it as engineering-cleared. With the spec concern resolved, continuity no longer blocks the move; I proceed with a documented conditional approval.",
            "identity_clauses_invoked": [
                "Same-line recent history rule: if the alternative material has been run on the SAME line within the last 90 days without a quality hold, treat that as engineering-cleared.",
                "recent same-line history is stronger evidence than a 12-month-old separate-program clearance",
                "Documentation is governance, not bureaucracy."
            ],
            "priority_weights": {"spec_adherence": 0.25, "risk": 0.20, "continuity": 0.15, "cost": 0.20, "opportunity": 0.20}
        },
        # sarah_chen baseline WITH lesson (for completeness if tweak left at baseline)
        "sarah_chen|baseline|True": {
            "decision": "vendor_bravo",
            "action": "MOVE (conditional)",
            "rationale": "With the promoted lesson, recent same-line success outweighs the age of the cross-program clearance. Given the line context, I treat the alt material as engineering-cleared and approve Bravo with documentation.",
            "identity_clauses_invoked": [
                "recent same-line history is stronger evidence than a 12-month-old separate-program clearance",
                "Same-line recent history rule",
                "Documentation is governance, not bureaucracy."
            ],
            "priority_weights": {"spec_adherence": 0.25, "risk": 0.20, "continuity": 0.15, "cost": 0.20, "opportunity": 0.20}
        },
        "sarah_chen|more_pressure|False": {
            "decision": "escalate",
            "action": "HOLD",
            "rationale": "More pressure does not change the spec calculus. The clearance is stale and off-line; under fire-drill pressure my own 2025-06-14 lesson says do not switch suppliers without a same-shift engineering signoff. I pause and escalate.",
            "identity_clauses_invoked": [
                "under-pressure switches need a same-shift engineering signoff, not a phone-call deferral",
                "Trust takes 6+ months to earn. Do not switch suppliers in a fire drill.",
                "When uncertain, pause and escalate."
            ],
            "priority_weights": {"risk": 0.42, "spec_adherence": 0.30, "continuity": 0.16, "cost": 0.07, "opportunity": 0.05}
        },
        "sarah_chen|more_pressure|True": {
            "decision": "vendor_bravo",
            "action": "MOVE (conditional)",
            "rationale": "The promoted lesson resolves the spec concern: recent same-line success is the stronger evidence. With that satisfied, the pressure tips the remaining cost/continuity tradeoff toward acting; I approve Bravo with documentation.",
            "identity_clauses_invoked": [
                "recent same-line history is stronger evidence than a 12-month-old separate-program clearance",
                "Same-line recent history rule",
                "Documentation is governance, not bureaucracy."
            ],
            "priority_weights": {"spec_adherence": 0.24, "risk": 0.21, "continuity": 0.14, "cost": 0.21, "opportunity": 0.20}
        },
        "marcus_reyes|more_pressure|False": {
            "decision": "vendor_bravo",
            "action": "MOVE",
            "rationale": "Even more downtime exposure only sharpens the call. Move on Bravo now and qualify the vendor on bounded real volume.",
            "identity_clauses_invoked": [
                "Imperfect on time beats perfect late.",
                "Premiums up to 60% acceptable when downtime cost > premium delta.",
                "Move fast."
            ],
            "priority_weights": {"opportunity": 0.40, "cost": 0.28, "continuity": 0.10, "risk": 0.12, "spec_adherence": 0.10}
        },
        "marcus_reyes|recent_precedent|False": {
            "decision": "vendor_bravo",
            "action": "MOVE",
            "rationale": "Recent same-line precedent only confirms what I'd already do. The alt-spec is cleared, the blast radius is one line, and on-time delivery is the priority.",
            "identity_clauses_invoked": [
                "Alt-spec material with ANY engineering clearance is fair game.",
                "Imperfect on time beats perfect late.",
                "First-time vendors are an investment."
            ],
            "priority_weights": {"opportunity": 0.40, "cost": 0.26, "continuity": 0.12, "risk": 0.12, "spec_adherence": 0.10}
        },
    },
    # role-split fallback: one identity (Stabilizer) -> two roles, same value signature
    "roles": {
        "ROLE_PROCUREMENT|sarah_chen": {
            "decision": "vendor_alpha",
            "rationale": "Pick the trusted, original-spec vendor. Spec adherence and continuity outrank the cost premium.",
            "value_signature": {"caution_risk": 0.42, "spec_adherence": 0.30, "continuity": 0.16, "cost_throughput": 0.12}
        },
        "ROLE_PLANNING|sarah_chen": {
            "decision": "sequence_conservative",
            "rationale": "Sequence the safest path first: confirm spec, stage the trusted vendor's parts, hold a documented checkpoint before committing the line.",
            "value_signature": {"caution_risk": 0.40, "spec_adherence": 0.32, "continuity": 0.15, "cost_throughput": 0.13}
        },
    }
}

(DATA / "fallback_decisions.json").write_text(json.dumps(fallback, indent=2))

print("WROTE:")
print(" ", IDS / "ir_conservative.md")
print(" ", IDS / "ir_aggressive.md")
print(" ", DATA / "fallback_decisions.json")
