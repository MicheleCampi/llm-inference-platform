# Failure-mode analysis

How the platform fails, how we would know, and what limits the damage. Every
row links its evidence; the last column says what is not covered. Reviewed
10 November 2026.

| Failure mode | Effect | Detection | Mitigation | Evidence | Gap |
|---|---|---|---|---|---|
| No GPU capacity (stockout) | No replica; requests wait | FailedScaleUp events, autoscaler status | Several zones, flex-start, stop rule ([runbook 1](runbook.md)) | [PM-001](postmortems/pm-001-l4-stockouts.md), scale-up failure in the [DR drill](https://github.com/MicheleCampi/gke-llm-inference-platform/blob/main/docs/upgrade-and-dr.md#drill-9-november-2026) | No reservation: capacity is not guaranteed |
| Apply from CI fails halfway | Partial resources billing | Failed apply job | Targeted destroy ([runbook 2](runbook.md)) | [PM-003](postmortems/pm-003-ci-apply-stockout.md) | None known |
| Service billed but unused | Cost above estimate | Billing read after every session | Set explicitly in Terraform, CI check ([runbook 3](runbook.md)) | [PM-002](postmortems/pm-002-managed-prometheus-billed.md) | No budget alert during a session |
| Node drained or preempted under load | Open streams cut | Preemption notice | preStop drain ([runbook 5](runbook.md)) | 4 open streams, 0 cut ([R6](r6-report.md)) | Tested on kind, not on a GPU node |
| Node cordoned | Replica unavailable | Pod rescheduled | Replica moves to another worker | Ready on the other worker ([R6](r6-report.md)) | Tested on kind |
| Cluster lost | All serving down | Everything fails | Rebuild from Git ([runbook 6](runbook.md)) | RTO 46 min 11 s ([drill](https://github.com/MicheleCampi/gke-llm-inference-platform/blob/main/docs/upgrade-and-dr.md#drill-9-november-2026)) | One drill, one region, no standby |
| First token too slow | Objective missed | Burn-rate alerts, fired on live series | [Latency runbook](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/docs/runbooks/ttft-burn-rate.md) | [PRR](prr.md) | None known |
| Metrics missing | Alerts blind | Target down 5 min; replicas without metrics 30 min | Alert on missing data | [PRR](prr.md) | None known |
| Requests lost before the replica | Errors not counted in the objective | Client-side only | None | [PRR](prr.md) | No alert |
| Load on one pod of three | Uneven latency | None | None | [R6 open limits](r6-report.md) | Cause not investigated |
