# OSS-04 Incident Bridge Log — 2026-04-22 (running transcript)

**02:48 patel:** p99 on /scratch2 just went vertical — 12ms to 4.2s. opening bridge.

**02:49 kim:** which OSS?

**02:49 patel:** per-OSS panel fingers OSS-04. others nominal.

**02:50 kim:** client errors?

**02:50 patel:** none. apps are hanging, not failing. classic stuck-io.

**02:52 patel:** pulling dmesg on oss-04.

**02:54 patel:** got it: mpt3sas IOC reset, then 'rejecting I/O to offline device' sd 8:0:42:0.

**02:55 kim:** slot 42. that's an NVMe behind the SAS expander right?

**02:56 patel:** yep nvme8n1, part of OST-0042.

**02:58 ops-bot:** Sev-2 auto-filed STG-48117.

**03:00 kim:** anything in BMC?

**03:01 patel:** BMC shows a transient power excursion on the SAS expander at 02:47:03, ~0.6s.

**03:02 patel:** vendor MIB: 'unrecoverable backplane fault' slot 42 at 02:47:08.

**03:03 kim:** so backplane power blip -> expander reset -> drive dropped offline -> stuck writes. that's the chain.

**03:04 patel:** agreed. autopilot should've evicted but didn't.

**03:05 kim:** why not?

**03:06 patel:** threshold is 5 consecutive errors in 30s. we only logged 3 before it wedged.

**03:07 ortega-lab:** our genome assembly is stalled, we have a 06:00 deadline.

**03:08 patel:** aware. working it.

**03:09 kim:** recommend manual eviction of OST-0042 now, let lustre retry route around it.

**03:10 patel:** risk?

**03:10 kim:** low. striped across 4, survivors hold. clients will retry.

**03:11 patel:** DECISION: manually evicting OST-0042 now.

**03:11 patel:** evicted.

**03:12 ops-bot:** p99 dropping… 2.1s … 800ms …

**03:12 patel:** apps unsticking. ~40s for client retry to kick.

**03:14 ortega-lab:** pipeline checkpointed, restarting on survivors.

**03:18 patel:** opened vendor RMA DELL-228714 for the slot-42 drive.

**03:30 kim:** escalating to Sev-1 for the customer-visible miss? deadline at risk.

**04:18 patel:** Sev-1. genome pipeline will be late.

**04:02 ops-bot:** RMA shipped.

**05:10 kim:** drafting RCA notes. root cause: SAS-expander transient power excursion -> backplane fault slot 42.

**05:12 patel:** ACTION: file autopilot policy change — treat a logged SAS-expander power excursion as an immediate auto-evict trigger, don't wait for the 5-error threshold.

**05:13 kim:** second action: lower the SMART grown-defect alert from 8/week to 4/week. slot 42 logged 4 last week and we missed it.

**05:14 patel:** third: ask Ortega lab to tighten checkpoint cadence from 60min; recovery was marginal.

**06:42 ortega-lab:** pipeline finished. 42 min late, customer-visible.

**06:45 patel:** logging customer impact. closing bridge, RCA Tuesday.

**06:46 kim:** summary for handoff: backplane power excursion on OSS-04 slot 42 took OST-0042 offline; auto-evict didn't fire (threshold); manual eviction at 03:11 recovered in ~40s; three follow-up actions filed.

**06:47 patel:** ack. good work all.
