# Production readiness review

Where the platform stands against a production readiness checklist, item by
item. **Met** has public evidence; **open** says what is missing. Reviewed
8 November 2026.

| Area | State | Evidence |
|---|---|---|
| Service objectives | Met | 95% of first tokens within 1 s (2 s above 2,048 prompt tokens), 100 ms per output token, 99.5% success: [slo-l4-qwen7b-bf16.json](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/hack/loadgen/slo-l4-qwen7b-bf16.json) |
| Alerting on the objective | Met | Multi-window burn rate, 14.4x over 1 h and 5 min (page), 6x over 6 h and 30 min (ticket); logic tested by promtool in CI: [slo-rules.yaml](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/deploy/monitoring/slo-rules.yaml); both burn alerts fired and emailed on live series in session B-005 ([billed sessions](status.md)) |
| Alerting on missing data | Met | Target down after 5 min, replicas asked for but no metrics after 30 min |
| Runbooks | Met | [Operator](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/RUNBOOK.md), [latency alerts](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/docs/runbooks/ttft-burn-rate.md), [platform](runbook.md) |
| Incident review | Met | [Three blameless postmortems](postmortems/README.md), each fix a merged PR |
| Cost control | Met | Per-session estimate and cap, billing read after every session ([billed sessions](status.md)); 4.38 to 8.07 EUR per million generated tokens within the L4 objectives (ADR-0025) |
| Security | Met | [Threat model](threat-model.md), 23 threats, counts checked in CI |
| Infrastructure change | Met | Keyless Terraform plan in CI, apply from CI as a second identity |
| Losses before the replica | Open | Refused connections and missing endpoints are only checked client-side; no alert |
| Time per output token | Open | Checked client-side only; no alert |
| GPU capacity | Open | No reservation: on-demand failed in two regions ([PM-001](postmortems/pm-001-l4-stockouts.md)); flex-start queues but does not guarantee |
| Upgrade and disaster recovery | Open | [Written down](https://github.com/MicheleCampi/gke-llm-inference-platform/blob/main/docs/upgrade-and-dr.md), not drilled: no measured recovery time |
| On-call | Open | Grafana-managed rules route through Grafana's built-in Alertmanager to one email contact point, `platform-oncall-email` ([ADR-0021](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/docs/adr/0021-burn-rate-alerts-on-the-time-to-first-token.md)); no paging service, no rotation; the routing lives in Grafana Cloud, not in a repository |
