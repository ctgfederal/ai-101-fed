---
name: log_analyst
version: 1.0.0
description: |
  Triage an experiment- or storage-run log from an HPC/national-lab cluster:
  fetch the log, identify the dominant anomaly (hardware fault, storage
  incident, job failure, or clean completion), and write a one-paragraph
  triage note recommending the next action. Use when asked to "triage run
  <id>", "what went wrong with run <id>", or "look at this run log". Do NOT use
  for live alerting, capacity planning, or security-incident forensics — those
  are separate skills.
triggers:
  - "triage run"
  - "what went wrong with run"
  - "look at this run log"
tools:
  - read_log
  - grep_log
  - skill_lookup
  - write_triage_note
model: claude-sonnet-4-6
---

# log_analyst

Turn a noisy run log into a short, decision-ready triage note.

## Method

1. **Fetch** the log with `read_log(run_id)`. If it is truncated, use
   `grep_log(run_id, pattern)` to pull the relevant slices rather than
   re-reading the whole file.
2. **Classify the dominant signal.** Scan for the highest-severity evidence and
   pick exactly one primary category — do not bury the lede under minor warnings:

   | Category            | Look for                                                            |
   |---------------------|---------------------------------------------------------------------|
   | `hardware_fault`    | `ECC`, `DRAM`, `Xid`, `GPU fell off the bus`, `MCE`, `thermal trip`  |
   | `storage_incident`  | `OSS`, `OST`, `Lustre`, `I/O error`, `EIO`, `quota`, `degraded RAID` |
   | `job_failure`       | `OOM`, `segfault`, `non-zero exit`, `CUDA error`, `timeout`, `NaN`   |
   | `network`           | `NCCL timeout`, `IB link down`, `retransmit`, `unreachable`          |
   | `clean_completion`  | `job complete`, `exit 0`, no ERROR/FATAL lines                       |

3. **Localize.** Name the first node/timestamp where the primary signal appears
   and whether it spread (single node vs. fleet-wide). The first occurrence is
   usually the root cause; later lines are often downstream fallout.
4. **Recommend ONE next action**, scoped to the category — e.g. drain & RMA the
   faulting node, fail the OST over to its backup and open a storage ticket,
   resubmit with a larger memory request, or close the run as healthy.

## Triage note format

Always finish by calling `write_triage_note` with a single paragraph:

> **Run <id> — <category>.** <1 sentence: what happened, where, and the key
> evidence line>. <1 sentence: blast radius / is it isolated>.
> **Next action:** <one concrete, owner-ready step>.

## Rules

- Quote the actual evidence line (timestamp + node) — never assert an anomaly
  you cannot point to in the log.
- One primary category per run. Note secondary signals in a trailing clause only
  if they change the recommended action.
- If the log is clean, say so plainly and recommend closing the run — a
  confident "no action" is a valid triage outcome.
