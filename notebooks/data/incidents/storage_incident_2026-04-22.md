# Storage Incident Report — 2026-04-22 / OSS-04

**Reporter:** N. Patel (Storage Ops, swing shift)
**Submitted via:** ServiceNow ticket STG-48117
**Affected systems:** Lustre filesystem `/scratch2`, OSSes 03–06
**Customer impact:** Genome-assembly pipeline (PI: Ortega) missed 06:00 deadline
**Initial severity:** Sev-2 → escalated to Sev-1 at 04:18

## Narrative

At approximately 02:47 UTC operations dashboard alarmed on `/scratch2` write
latency: p99 from a steady ~12ms baseline jumped to 4.2s within a 90-second
window. OSS-04 was implicated by per-OSS panel. No client-side errors visible
at that moment — applications appeared to hang, not fail.

Patel pulled the dmesg ring buffer on OSS-04 and saw three recurring lines:

    [ 23947.108] mpt3sas_cm0: log_info(0x31110d00): originator(PL),
                 code(0x11), sub_code(0x0d00) — IOC was reset
    [ 23949.221] sd 8:0:42:0: rejecting I/O to offline device
    [ 23952.015] LustreError: 11-0: scratch2-OST0042-osc-...
                 operation ost_write to node 10.7.42.4@o2ib failed: rc = -107

Cross-checked against the per-OSS BMC: SAS expander had logged a transient
power excursion at 02:47:03 lasting 0.6 seconds. Vendor MIB surfaced an
"unrecoverable backplane fault" against slot 42 at 02:47:08. Slot 42 holds
NVMe drive `nvme8n1`, which OST-0042 stripes across alongside three peers.

Patel manually evicted OST-0042 at 03:11. Applications recovered within
~40 seconds (Lustre client retry kicked in). Genome pipeline checkpointed at
03:14, restarted on the survivor OSTs, and finished at 06:42 — 42 minutes
late, customer-visible.

## Open questions for the Tuesday RCA

- Why did the 02:47 SAS expander event not trigger an automatic OST eviction?
  The autopilot policy has the rule but the threshold (5 consecutive errors
  in 30s) was not crossed before manual intervention.
- Was there a quiet symptom 6–24 hours earlier that we missed? Slot 42 had
  recorded 4 SMART-grown defect-list increments over the preceding week, but
  none of them tripped the standing alert threshold of 8/week.
- The genome pipeline's checkpoint cadence is 60 minutes. With this
  recovery time, that's marginal. Should we revisit?

## On call this shift

- Primary: N. Patel (storage ops)
- Secondary: J. Kim (lustre admin)
- Vendor: ticket DELL-228714 opened 03:18, RMA shipped 04:02
