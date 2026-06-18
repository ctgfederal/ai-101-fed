# Score Thresholds

The verdict is computed deterministically from the three sub-scores.

| Verdict | Rule |
|---|---|
| **PASS** | All three sub-scores ≥ 8 |
| **WARN** | All three sub-scores ≥ 5 AND at least one is in [5, 7] |
| **FAIL** | Any sub-score < 5 |

## Sub-score bands

| Band | Range | Meaning |
|---|---|---|
| Excellent | 9-10 | Mechanically clean. Nothing to fix. |
| Good | 7-8 | Minor issues; address before merge but not blocking review. |
| Warn | 5-6 | Multiple issues; spec needs another pass. |
| Fail | 0-4 | Spec is not ready. Stop and fix. |

## Important: PASS is not approval

A `PASS` verdict means **mechanically clean**: required sections exist, cross-references resolve, formats are valid, no markers left behind. It does **not** mean:

- The product strategy is right.
- The architecture is sound.
- The tests will catch real bugs.
- A reviewer would approve.

That judgment stays with the human. This skill grades; humans approve.
