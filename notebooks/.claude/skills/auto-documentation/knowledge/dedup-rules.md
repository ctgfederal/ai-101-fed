# Deduplication Rules

How `dedupe.py` decides whether a candidate auto-doc duplicates an existing one. The point is to keep the archive *one canonical place per topic*.

## Similarity signals

Three signals, weighted:

1. **Title similarity** — Tokenize title to lowercase words, drop stopwords (`the`, `a`, `of`, `in`, `for`, `to`, `and`, `or`). If Jaccard similarity of the token sets is ≥ 0.6, that's a strong signal.
2. **Tag overlap** — Intersection / union of the tag sets. If ≥ 0.5, that's a strong signal.
3. **Scope hash** — Lowercase + collapse whitespace + strip punctuation, then hash. Exact scope-hash match is a *very* strong signal regardless of title.

A candidate is flagged duplicate if **any** of:
- Scope hash matches AND category matches AND tag overlap ≥ 0.3, OR
- Title similarity ≥ 0.6 AND category matches, OR
- Tag overlap ≥ 0.5 AND category matches AND title similarity ≥ 0.4.

## When to merge vs create new

If `dedupe.py` flags a candidate, the LLM has three choices — pick one:

- **Merge** — The new insight refines or extends the existing doc. Open the existing file, append to `## Examples` or `## Related`, and stop. No new file.
- **Replace** — The new insight contradicts the existing doc (the rule changed). Document the change in the existing file's `## Description` ("As of YYYY-MM-DD..."), update the examples, and stop. No new file.
- **Create anyway** — The matched file covers a different scope despite signal overlap. Use `--force` and explicitly note in the new doc's `## Related` why this is *not* a duplicate.

The default is **merge**. Creating despite a flag requires explicit reasoning.

## What does NOT signal duplication

- Same category alone — categories are coarse.
- Same single tag — tags are by design overlapping.
- Same author or source — sources differ even when topics overlap.

## Tuning

The thresholds above are intentionally conservative — better to flag and merge than to silently fork the archive. If false-positive rate becomes painful, raise the title-similarity threshold first; do not raise the scope-hash signal.
