# Known failure modes — run/storage log triage

Reference catalog for the `log_analyst` skill. Look a candidate signal up here
before classifying, then quote the matching evidence line from the log.

## hardware_fault

- **DRAM ECC (uncorrectable)** — `EDAC`, `UE`, `ECC error`, `DRAM`, `MCE`.
  Uncorrectable ECC on a DIMM corrupts memory mid-run. First occurrence names
  the faulting node + DIMM slot. **Next action:** drain the node, RMA the DIMM,
  resubmit the job elsewhere.
- **GPU Xid / fell off the bus** — `Xid`, `GPU has fallen off the bus`,
  `NVRM`. Often thermal or power related. **Next action:** drain node, check
  power/thermal, RMA if it recurs.
- **Thermal trip** — `thermal trip`, `over-temp`, `throttling`. **Next
  action:** check cooling/airflow before returning the node to service.

## storage_incident

- **OST degraded / failover** — `OSS`, `OST`, `Lustre`, `degraded RAID`,
  `EIO`, `I/O error`. A failing Object Storage Target stalls or errors I/O for
  every job touching that stripe. Localize to the OST and its OSS. **Next
  action:** fail the OST over to its backup OSS, open a storage ticket, verify
  RAID rebuild.
- **Quota exhaustion** — `quota exceeded`, `EDQUOT`, `no space`. Job-scoped,
  not hardware. **Next action:** raise quota or relocate output; not an
  infrastructure incident.

## job_failure

- **OOM** — `OOM`, `Out of memory`, `oom-kill`, `MemoryError`. **Next
  action:** resubmit with a larger memory request.
- **Segfault / non-zero exit** — `segfault`, `core dumped`, `non-zero exit`.
  **Next action:** return to the job owner with the failing step.
- **CUDA / numerical** — `CUDA error`, `NaN`, `inf`. **Next action:** owner
  fixes inputs/kernel; not an infra fault.

## network

- **NCCL / IB** — `NCCL timeout`, `IB link down`, `retransmit`,
  `unreachable`. **Next action:** check the fabric / the implicated link before
  blaming the job.

## clean_completion

- `job complete`, `exit 0`, no ERROR/FATAL lines. A confident "no action,
  close the run" is a valid triage outcome.

## Triage discipline

- One **primary** category per run — pick the highest-severity signal; list
  secondary signals only if they change the recommended action.
- The **first** occurrence of the primary signal is usually root cause; later
  lines are downstream fallout.
- Never assert an anomaly you cannot quote (timestamp + node) from the log.
