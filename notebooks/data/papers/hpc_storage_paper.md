# Adaptive I/O Scheduling for Mixed-Workload Parallel File Systems on Exascale Platforms

*Synthetic teaching paper — written for the AI-101-Fed curriculum. Mirrors the
voice, density, and structure of an SC/HPDC submission so participants can
practice prompt craft on a realistic DOE-style artifact without copyright.*

## Abstract

Parallel file systems on exascale platforms must service simultaneous workloads
whose I/O profiles span six orders of magnitude — from kilobyte metadata
operations on millions of small files (genomics, ML checkpoints) to multi-
terabyte streaming writes from coupled physics codes. We present **PACE**
(Priority-Aware Concurrent Elevator), an adaptive I/O scheduler that runs as a
Lustre 2.16 OSS plugin and reorders pending RPCs based on a continuously-
updated workload classifier trained on six months of system-wide telemetry from
a 27-petabyte production deployment.

PACE achieves a **2.4× median reduction in 99th-percentile latency** for
metadata-heavy workloads while holding bulk-transfer bandwidth within 3% of the
unmodified baseline. Across 1,184 production jobs replayed in our staging
cluster, PACE reduced cross-workload interference (measured as the
Kolmogorov-Smirnov distance between solo and concurrent latency
distributions) by 41%. We do **not** address client-side caching, OST
rebalancing, or HDR-IB fabric congestion — those remain orthogonal concerns.

The classifier, scheduler, and replay harness are released under a BSD-3
license; the production telemetry corpus is available to DOE-cleared
collaborators under embargo until 2027 (contact: storage-research@<lab>.gov).

## 1. Introduction

Exascale platforms — Frontier, Aurora, El Capitan, and their successors —
collapse three historically separate workload classes onto a single parallel
file system: traditional HPC simulation, AI/ML training, and high-throughput
experimental data ingest. Each class has a distinct I/O signature. Simulation
codes generate large coherent writes from O(10⁴) ranks. ML training generates
small random reads from O(10²) workers but at extreme aggregate IOPS. Data-
ingest pipelines from light sources and accelerators generate metadata-
dominated traffic with strict end-to-end deadlines.

Lustre's default OSS scheduler is FIFO with light per-client fairness. Under
mixed-workload pressure we observe latency tail explosions of 50–200× that
correlate with metadata storms from ML jobs colliding with bulk-write epochs
from physics codes. Two prior approaches have addressed this — deadline-based
schedulers (Hammerle et al., HPDC 2022) and reinforcement-learning controllers
(Park et al., SC 2024). The first improves tail latency by 1.6× but degrades
bandwidth by 8–14%. The second matches our results in simulation but has not
been demonstrated at production scale, and its 30-second control loop is too
slow for the bursty workloads we measure in practice.

Our contribution is threefold:

1. **Workload classifier (§3).** A small (12-feature, 4-class) decision tree
   trained on PFS telemetry that classifies in-flight RPCs in <40 µs.
2. **Concurrent-elevator scheduler (§4).** A two-level scheduler that
   preserves the seek-locality of an elevator within each priority band and
   round-robins between bands.
3. **Production replay harness (§5).** A faithful trace replay framework that
   reproduces the cross-workload interference patterns observed in production
   to within 7% on every measured percentile.

## 2. Threat Model and Constraints

Unlike workstation file systems, exascale PFS schedulers must operate under
hard constraints that rule out many otherwise-attractive algorithms:

- **No global state.** A scheduling decision cannot wait on a cluster-wide
  consensus; the OSS receives an RPC and must dispatch within microseconds.
- **No tenant trust.** Workloads are submitted by hundreds of distinct user
  groups. The scheduler cannot rely on user-supplied priority hints.
- **Federal audit posture.** Deployments at SCIF-tiered facilities must
  produce an event log sufficient to reconstruct any scheduling decision
  retrospectively (NIST 800-53 AU-2, AU-12).

PACE meets all three.

## 3. Workload Classifier

[paper continues — for the teaching exercise, the abstract + §1 + §2 are
sufficient. Real participants would summarize the abstract and §1; the rest is
detail.]
