# Example 1 — Scaffold + update one section

This example shows the typical workflow:

1. Scaffold all four steering docs into a fresh repo.
2. Fill the `Tech Stack` section of `tech.md` from a known stack.
3. Validate.

## Step 1 — scaffold

```bash
python scripts/init_steering.py --steering-root .claude/steering
```

Result: four files are created at `.claude/steering/`:

- `product.md`
- `tech.md`
- `structure.md`
- `roadmap.md`

Each is a literal copy of the matching template. Every required heading is
present; many sections still contain `[NEEDS CLARIFICATION]` markers.

## Step 2 — fill the Tech Stack section

```bash
python scripts/update_doc.py \
  --steering-root .claude/steering \
  --doc tech \
  --section "Tech Stack" \
  --body "$(cat examples/example-1/tech-stack-body.md)"
```

The body file contents are reproduced in `tech-stack-body.md` in this folder.

## Step 3 — validate

```bash
python scripts/validate_output.py \
  --file .claude/steering/tech.md \
  --doc tech
```

Exits 0. The expected `tech.md` is at `expected-output/tech.md`.

## Step 4 — full root validation

```bash
python scripts/validate_steering.py --steering-root .claude/steering
```

This will report `PASS` for `tech.md` (which we filled) and validate the
required sections of the other three are still present (note: this skill's
`validate_steering.py` does not flag remaining `[NEEDS CLARIFICATION]`
markers — those must be resolved before docs are considered final).
