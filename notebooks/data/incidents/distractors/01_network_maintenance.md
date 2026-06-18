# Change Record CHG-90412 — InfiniBand fabric firmware

**Window:** 2026-04-19 01:00–03:00 UTC (completed clean)
**Scope:** o2ib fabric, leaf switches 7–12

Rolled HDR firmware to 27.2010. Verified subnet manager failover. No client
impact observed. p99 RDMA write latency steady at 9–11us across the window.
This change predates the OSS-04 event by three days and is unrelated.
