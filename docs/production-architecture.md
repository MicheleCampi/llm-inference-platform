# Production architecture: index of evidence

A synthesis of the readiness work, pointing to the evidence instead of
repeating it. Validity: designed, built and verified under simulated
production load on GKE, one region, not operated in production. The AWS
side is a separate project.

| Area | Where the evidence is |
|---|---|
| Architecture (C4, contracts, failure domains) | [architecture.md](architecture.md) |
| Service objectives and error budget | [slo-policy.md](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/docs/slo-policy.md), [slo-rules.yaml](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/deploy/monitoring/slo-rules.yaml) |
| Cost model | ADR-0025 in the operator; billed sessions in [status.md](status.md) |
| Threats and supply chain | [threat-model.md](threat-model.md); SLSA Build L2 on the operator image |
| Failure modes and runbooks | [fmea.md](fmea.md), [runbook.md](runbook.md), [postmortems](postmortems/README.md) |
| Readiness review | [prr.md](prr.md) |
| Measured numbers | [r6-report.md](r6-report.md) |

## Not done

What is still open is listed in the README section "What is not done yet"
and in the open rows of [prr.md](prr.md); the count is in [status.md](status.md).
