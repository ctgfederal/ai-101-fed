# FOCUS / EXCLUDE Rules

## What counts as a path

A FOCUS or EXCLUDE entry is a string. It may be:

- An exact relative path (`src/auth/login.py`)
- A directory (`src/auth/` or `src/auth`)
- A simple glob (`src/auth/**` or `src/auth/*`)

Absolute paths work too but relative paths are preferred — they make prompts portable across worktrees.

## Glob behavior

`scripts/check_collisions.py` does *not* walk the filesystem. It treats trailing `*`, `**`, `/*`, `/**` as a prefix match. Two FOCUS entries collide when:

- The exact normalized paths are equal, OR
- One is a prefix of the other (after stripping trailing globs).

This is conservative — it errs on the side of declaring a collision. False positives are easy to fix (re-scope FOCUS); false negatives cause partial-write corruption, which is not.

## Bare directories are prefix matches

`src/auth/` and `src/auth` both match anything under `src/auth/`. If two agents have FOCUS `src/` and `src/auth/`, that's a collision — the first agent owns everything, the second is contained.

## Precedence: EXCLUDE wins

Inside the prompt, EXCLUDE is authoritative. If a path is in EXCLUDE, the agent must not edit it, even if it appears under a FOCUS directory. The validator rejects payloads where a path is in *both* FOCUS and EXCLUDE — that's ambiguous; pick one.

## Scoping by directory vs single file

Prefer directory scoping when:
- The work spans multiple files in one area (`src/auth/`).
- You don't yet know the exact file list.

Prefer single-file scoping when:
- The change is a surgical edit (`src/config.py` to bump a version).
- Co-located code in the same dir is owned by another agent.

## Don't FOCUS on shared infrastructure

Files that multiple modules import (`src/db.py`, `src/logger.py`, `src/types.py`) should rarely be in any single agent's FOCUS. If they need changes, do that work *before* parallel launch, then delegate the dependent work.
