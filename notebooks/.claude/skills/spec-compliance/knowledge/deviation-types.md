# Deviation Types

Every deviation in a compliance report carries a `type` field. These are the catalogued kinds.

## missing-component

**What it means.** A component declared in the SDD has no file at any of its `expected_paths`.

**How it is detected.** `check_compliance.py` resolves each `expected_paths` entry against the repo root. If none of the resolutions exist, the component is marked `missing: true`.

**How to resolve.**
- Implement the component at one of the declared paths, OR
- Update the SDD's `Path:` line if the component was deliberately moved (and re-run compliance), OR
- Remove the component from the SDD if it was abandoned (and update PRD references).

**Common false positive.** A renamed component — see `renamed-component` below.

## renamed-component

**What it means.** A component declared in the SDD has no file at the expected path, but a file with the same component name *suffix* exists at a similar path. This is a **hint**, not a hard failure — it always co-occurs with `missing-component`.

**How it is detected.** Heuristic match: same basename stem, same parent directory but different last segment. Currently *not* emitted by the default `check_compliance.py` — listed here for the taxonomy. Extending the script to detect renames is a future enhancement.

**How to resolve.**
- If the rename is intentional: update the SDD's `Path:` line.
- If the rename is accidental: rename the file back.

## unreferenced-requirement

**What it means.** A requirement declared in the PRD is not mentioned anywhere in the repo.

**How it is detected.** `check_compliance.py` greps for the literal `REQ-NNN` token across all text-ish files (excluding vendored / cache dirs). If zero matches, the requirement is marked `unreferenced: true`.

**How to resolve.**
- Add a comment in the implementing code: `# Implements REQ-NNN`.
- Add a reference in a test docstring: `Tests REQ-NNN: ...`.
- If the requirement was deliberately dropped, remove it from the PRD (and verify no PLAN tasks reference it).

**Why this matters.** Requirements without code references cannot be traced. The PLAN task ID may be implemented, but the link from PRD → code is broken — meaning a future refactor cannot tell what the code is *for*.

## scope-creep

**What it means.** The repo references a `REQ-NNN` token that does not appear in the parsed PRD.

**How it is detected.** `check_compliance.py` collects every `REQ-NNN` token found anywhere in the repo, then subtracts the set of REQ-IDs declared in the PRD. Anything left is scope creep.

**How to resolve.**
- If the work is real: add a matching `**REQ-NNN**` requirement to the PRD.
- If the reference is stale: remove it from the code.

**Why this matters.** Code claiming to implement an undefined requirement is a maintenance trap. Either the spec is incomplete or the code is over-built — both must be reconciled.

## Severity

Compliance reports do not assign severity per deviation; the human reviewer decides. As a rule of thumb:

- `missing-component` and `unreferenced-requirement` are **blocking** — they mean the spec and code disagree on what was built.
- `scope-creep` is **noisy** — it might be a typo, a stale reference, or a real over-build.
- `renamed-component` is **informational** — fix the SDD or the file path, then re-run.
