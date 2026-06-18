#!/usr/bin/env python3
"""Build vendored data for Notebook 01 — Context Engineering.

Creates:
  data/incidents/distractors/*.md          — 14 plausible-but-irrelevant ops docs
  data/incidents/fallback_position_scores.json — precomputed recall-by-position
  data/incidents/oss04_running_log.md       — a ~40-turn running incident log (CONDENSE demo)

Run once; output is small and vendored into the repo so the notebook is runnable
without a model or network.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent
INC = DATA / "incidents"
DIST = INC / "distractors"
DIST.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 14 distractor docs: real-feeling HPC/storage/ops material that does NOT
# explain the OSS-04 p99 latency spike. They share vocabulary (latency, OSS,
# Lustre, SAS, NVMe) so lexical retrieval has to actually discriminate, and so
# a "stuffed" window has plenty of plausible wrong answers to latch onto.
# ---------------------------------------------------------------------------
DISTRACTORS = {
    "01_network_maintenance.md": """# Change Record CHG-90412 — InfiniBand fabric firmware

**Window:** 2026-04-19 01:00–03:00 UTC (completed clean)
**Scope:** o2ib fabric, leaf switches 7–12

Rolled HDR firmware to 27.2010. Verified subnet manager failover. No client
impact observed. p99 RDMA write latency steady at 9–11us across the window.
This change predates the OSS-04 event by three days and is unrelated.
""",
    "02_capacity_report.md": """# Weekly Capacity Report — /scratch2

Utilization 71% (up 3pts WoW). Projected to cross 80% soft cap in ~6 weeks.
No OSTs above 85%. Recommend opening a procurement ticket for an OSS shelf.
Inode pressure nominal. Nothing here touches availability or tail latency.
""",
    "03_scheduler_backlog.md": """# Slurm Backlog Note

Queue `genomics` had 340 pending jobs at 08:00 due to a large Ortega-lab
array submission. Backlog is a scheduling artifact, not a storage fault.
Fairshare rebalanced by 10:30. Mentions the genome pipeline but not latency.
""",
    "04_old_oss03_incident.md": """# Incident STG-44120 (2026-01-09) — OSS-03 reboot

OSS-03 kernel panic in `mlx5_core` after an untested driver bump. Hard reboot
at 14:22, fsck clean, back in service 14:51. Different OSS, different month,
different root cause (driver, not backplane). Closed.
""",
    "05_vendor_advisory.md": """# Vendor Advisory DELL-ADV-2026-031

Advisory covers a *controller cache* battery degradation on a DIFFERENT
storage line (PowerVault), not the NVMe/SAS backplane in the OSS shelves.
Recommends a BBU swap. Not applicable to /scratch2 OSSes. Informational only.
""",
    "06_monitoring_runbook.md": """# Runbook: reading the per-OSS latency panel

How to interpret the Grafana per-OSS p50/p95/p99 panels. Thresholds, alert
routes, escalation. Procedure doc — explains the *tooling*, never says what
happened on any given night.
""",
    "07_security_scan.md": """# Quarterly Security Scan — storage subnet

OpenSCAP run on storage hosts. 2 medium findings (telnet enabled on a BMC,
weak SNMP community). No CVEs tied to availability. Unrelated to the spike.
""",
    "08_dr_test.md": """# DR Failover Test — 2026-03-30

Simulated loss of MDS-01, exercised standby promotion. RTO 4m12s. Storage
OSSes untouched. Test artifact; no production latency impact.
""",
    "09_client_node_oom.md": """# Compute node c0421 OOM

A user job on c0421 OOM-killed at 02:31 UTC. Node-local, not a storage fault.
Coincidentally near the OSS-04 window, but the OOM is a memory cgroup issue
on the client, not write latency on the filesystem.
""",
    "10_power_pdu_note.md": """# Facilities PDU readings — Row J

Routine PDU telemetry for Row J (compute), within tolerance all week. The OSS
shelves are in Row C; this row's power is irrelevant to the backplane event.
""",
    "11_lustre_tuning.md": """# Lustre client tuning guide

max_rpcs_in_flight, max_dirty_mb, checksum settings. A tuning reference for
throughput. Discusses latency in general terms but is not an incident record.
""",
    "12_smart_policy.md": """# SMART monitoring policy (standing doc)

Alert when grown-defect-list increments exceed 8/week per drive. Policy text.
(Note: the real incident's drive logged 4/week — under threshold — but THIS
doc only states the policy, it does not record any drive's actual counts.)
""",
    "13_oss05_thermal.md": """# OSS-05 thermal warning (2026-04-20)

Inlet temp on OSS-05 brushed 32C for 11 minutes during a CRAC maintenance.
Auto-throttle did not engage. Different OSS, thermal not backplane, two days
prior. No latency excursion recorded.
""",
    "14_change_freeze.md": """# Change Freeze Notice

Standard end-of-quarter change freeze 2026-04-25 → 2026-05-02. Administrative
notice. No technical content about any incident.
""",
}

for name, body in DISTRACTORS.items():
    (DIST / name).write_text(body)

print(f"wrote {len(DISTRACTORS)} distractor docs -> {DIST}")

# ---------------------------------------------------------------------------
# Precomputed recall-by-position scores (fallback for VISUAL 3).
# Vendored from a long-context frontier run (Claude / GPT-4o class model on a
# ~30-distractor window). Shows the canonical "lost in the middle" dip. Used
# when the live small-model run is flat/noisy so the lesson still lands.
# Scores are mean "did it name the OSS-04 backplane/slot-42 cause?" over trials.
# ---------------------------------------------------------------------------
FALLBACK = {
    "source": "Precomputed on a long-context frontier model (Claude-class) with ~30 distractor chunks, 10 trials/position. Illustrative of Liu et al. 2024 / NoLiMa 2025.",
    "positions": ["start", "q1", "middle", "q3", "end"],
    "scores": {
        "start": 0.90,
        "q1": 0.70,
        "middle": 0.40,
        "q3": 0.65,
        "end": 0.95,
    },
    "trials": 10,
}
(INC / "fallback_position_scores.json").write_text(json.dumps(FALLBACK, indent=2))
print(f"wrote fallback_position_scores.json -> {INC}")

# ---------------------------------------------------------------------------
# A ~40-turn running incident log (CONDENSE demo). Chatty Slack/bridge-call
# style. The KEY DECISION that must survive condensation: "manually evict
# OST-0042 at 03:11" and "add SAS-expander power-excursion -> auto-evict rule".
# ---------------------------------------------------------------------------
LOG_TURNS = [
    ("02:48 patel", "p99 on /scratch2 just went vertical — 12ms to 4.2s. opening bridge."),
    ("02:49 kim", "which OSS?"),
    ("02:49 patel", "per-OSS panel fingers OSS-04. others nominal."),
    ("02:50 kim", "client errors?"),
    ("02:50 patel", "none. apps are hanging, not failing. classic stuck-io."),
    ("02:52 patel", "pulling dmesg on oss-04."),
    ("02:54 patel", "got it: mpt3sas IOC reset, then 'rejecting I/O to offline device' sd 8:0:42:0."),
    ("02:55 kim", "slot 42. that's an NVMe behind the SAS expander right?"),
    ("02:56 patel", "yep nvme8n1, part of OST-0042."),
    ("02:58 ops-bot", "Sev-2 auto-filed STG-48117."),
    ("03:00 kim", "anything in BMC?"),
    ("03:01 patel", "BMC shows a transient power excursion on the SAS expander at 02:47:03, ~0.6s."),
    ("03:02 patel", "vendor MIB: 'unrecoverable backplane fault' slot 42 at 02:47:08."),
    ("03:03 kim", "so backplane power blip -> expander reset -> drive dropped offline -> stuck writes. that's the chain."),
    ("03:04 patel", "agreed. autopilot should've evicted but didn't."),
    ("03:05 kim", "why not?"),
    ("03:06 patel", "threshold is 5 consecutive errors in 30s. we only logged 3 before it wedged."),
    ("03:07 ortega-lab", "our genome assembly is stalled, we have a 06:00 deadline."),
    ("03:08 patel", "aware. working it."),
    ("03:09 kim", "recommend manual eviction of OST-0042 now, let lustre retry route around it."),
    ("03:10 patel", "risk?"),
    ("03:10 kim", "low. striped across 4, survivors hold. clients will retry."),
    ("03:11 patel", "DECISION: manually evicting OST-0042 now."),
    ("03:11 patel", "evicted."),
    ("03:12 ops-bot", "p99 dropping… 2.1s … 800ms …"),
    ("03:12 patel", "apps unsticking. ~40s for client retry to kick."),
    ("03:14 ortega-lab", "pipeline checkpointed, restarting on survivors."),
    ("03:18 patel", "opened vendor RMA DELL-228714 for the slot-42 drive."),
    ("03:30 kim", "escalating to Sev-1 for the customer-visible miss? deadline at risk."),
    ("04:18 patel", "Sev-1. genome pipeline will be late."),
    ("04:02 ops-bot", "RMA shipped."),
    ("05:10 kim", "drafting RCA notes. root cause: SAS-expander transient power excursion -> backplane fault slot 42."),
    ("05:12 patel", "ACTION: file autopilot policy change — treat a logged SAS-expander power excursion as an immediate auto-evict trigger, don't wait for the 5-error threshold."),
    ("05:13 kim", "second action: lower the SMART grown-defect alert from 8/week to 4/week. slot 42 logged 4 last week and we missed it."),
    ("05:14 patel", "third: ask Ortega lab to tighten checkpoint cadence from 60min; recovery was marginal."),
    ("06:42 ortega-lab", "pipeline finished. 42 min late, customer-visible."),
    ("06:45 patel", "logging customer impact. closing bridge, RCA Tuesday."),
    ("06:46 kim", "summary for handoff: backplane power excursion on OSS-04 slot 42 took OST-0042 offline; auto-evict didn't fire (threshold); manual eviction at 03:11 recovered in ~40s; three follow-up actions filed."),
    ("06:47 patel", "ack. good work all."),
]
lines = ["# OSS-04 Incident Bridge Log — 2026-04-22 (running transcript)\n"]
for who, msg in LOG_TURNS:
    lines.append(f"**{who}:** {msg}\n")
(INC / "oss04_running_log.md").write_text("\n".join(lines))
print(f"wrote oss04_running_log.md ({len(LOG_TURNS)} turns) -> {INC}")

print("done.")
