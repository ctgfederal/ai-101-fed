# data/logs/oss04.csv

Per-request write latencies for Lustre object storage server `oss-04` on
2026-04-22, the day of incident STG-48117 (`data/incidents/storage_incident_2026-04-22.md`).

- 2000 rows: `ts, oss, op, latency_ms`
- Generated reproducibly: `numpy.random.default_rng(20260422)`, lognormal
  baseline (median ~2.1ms) + a ~12% degraded tail injected around the 02:47
  SAS-expander fault.
- **Ground-truth p90 = 51.09 ms** (computed with `numpy.percentile(.,90)`),
  which BREACHES the 50 ms write-latency SLO by a small, honest margin.

Used by notebook `02_agentic_loop.ipynb`: a single-shot model can only *guess*
this number from the filename; the closed-loop agent reads the bytes and gets
51.09. The tight margin is deliberate — a lazy estimate ("~18ms, within SLO")
is unambiguously wrong.
