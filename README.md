# LLM inference platform

A multi-repo platform for serving large language models on Kubernetes GPUs, built to be
verified by a stranger: every claim links to code, CI or a recorded measurement.

Designed, built and verified under simulated production load, with evidence in CI and one
measured session on a real NVIDIA L4. It has not served real users.

## Status

About 63% of a written 52-item roadmap: 31 items done, 4 partial (31 October 2026).
What is missing is listed in [What is not done yet](#what-is-not-done-yet).

## The problem

Serving an LLM is mostly paying for GPUs. Three forces pull against each other:

- **Cold start.** A new GPU node plus a 15 GB model takes minutes to become ready.
- **Latency objectives.** Time to first token and time per output token, per GPU class.
- **Cost.** Euros per million generated tokens, including the GPU time paid while idle.

## How it fits together

    Terraform (remote state, keyless plan in CI)
      -> GKE: CPU system pool + L4 GPU pool that scales 0..1, Workload Identity
        -> Argo CD (app of apps, sync waves): External Secrets, monitoring, operator, Alloy
          -> vllm-coldstart-operator: VllmService -> Deployment + Service + status
            -> vLLM on the L4 -> metrics -> Alloy -> Grafana Cloud
              -> burn-rate alerts on the L4 objectives -> cost per million generated tokens

The repositories are joined by explicit contracts: the operator's Helm chart pinned to a
release tag, its CRDs, the objective files, and CI tools pinned by SHA-256.

## Repositories

Platform core:

| Repository | Role |
|---|---|
| [gke-llm-inference-platform](https://github.com/MicheleCampi/gke-llm-inference-platform) | Terraform and Argo CD on GKE: scale-to-zero L4 pool, External Secrets via Workload Identity, Alloy to Grafana Cloud. |
| [vllm-coldstart-operator](https://github.com/MicheleCampi/vllm-coldstart-operator) | Kubernetes operator in Rust: VllmService and FleetService, placement, preemption, objectives, cost; 25 ADRs. |
| [eks-llm-inference-platform](https://github.com/MicheleCampi/eks-llm-inference-platform) | The AWS twin: Terraform and Argo CD on EKS deploying the same operator. |
| [inference-platform-ci](https://github.com/MicheleCampi/inference-platform-ci) | Pinned tools and shared verification helpers used by the CI of every repository. |
| [model-promotion-bridge](https://github.com/MicheleCampi/model-promotion-bridge) | Reads what MLflow promoted and emits the manifest that serves exactly that revision. |

Measurement:

| Repository | Role |
|---|---|
| [inferscope](https://github.com/MicheleCampi/inferscope) | Profiler in Rust: per-token timing correlated with /proc and NVML on one clock. |
| [vllm-coldstart-probe](https://github.com/MicheleCampi/vllm-coldstart-probe) | eBPF in Rust: decomposes vLLM cold start into phases by tracing syscalls. |

Experiments behind the design decisions:

| Repository | Role |
|---|---|
| [agentic-kv-energy-experiment](https://github.com/MicheleCampi/agentic-kv-energy-experiment) | How many agent trajectories a replica holds, and what waiting costs. |
| [cuda-graphs-experiment](https://github.com/MicheleCampi/cuda-graphs-experiment) | The CUDA graphs trade-off in vLLM: decode speed against throughput and cold start. |
| [lora-multitenancy-experiment](https://github.com/MicheleCampi/lora-multitenancy-experiment) | Cost per generated token of multi-tenant LoRA as adapters and skew grow. |
| [dynamo-kv-router-ab](https://github.com/MicheleCampi/dynamo-kv-router-ab) | A/B of NVIDIA Dynamo's KV-aware router against round-robin on a public trace. |
| [vllm-disagg-profiling](https://github.com/MicheleCampi/vllm-disagg-profiling) | Aggregated against disaggregated prefill/decode on equal hardware. |

Narrative:

| Repository | Role |
|---|---|
| [michelecampi.github.io](https://github.com/MicheleCampi/michelecampi.github.io) | The site, with a one-page summary at [/platform/](https://michelecampi.github.io/platform/). |

## Measured, with its envelope

- **One L4 session (27 October 2026):** the whole chain ran end to end; burn-rate alerts
  fired and notified. Cost of the session: 2.48 EUR.
- **L4 objectives:** time to first token 1 s (2 s above 2048 prompt tokens), time per
  output token 100 ms, for 95% of requests, 99.5% served.
- **Cost:** 4.38 to 8.07 EUR per million generated tokens within the L4 objectives (ADR-0025).
- **Envelope:** the load simulator is calibrated to one L4's medians, not its tails
  (ADR-0024). It proves the control plane and the logic, not GPU capacity.

## Security posture

A STRIDE [threat model](docs/threat-model.md) covers 23 threats: 13 mitigated, 6 partly
mitigated, 3 not mitigated, 1 not yet assessed. Each row states its status and residual
risk, and the document ends with a prioritised list of what to close next.

Open items, as named in the threat model:

- S4, not mitigated: EKS workloads use the node IAM role. Next: IRSA per service account (priority 4).
- R2, not mitigated: one shared static key per vLLM service, so no per-client attribution.
  Next: per-client identity (priority 1).
- D3, not mitigated: no rate limits or quotas, so one client can exhaust the GPU.
  Next: edge stack before any public exposure (priority 5).
- I4, not assessed: the Grafana Cloud secret is only referenced; its handling is not yet reviewed.

Last reviewed 31 October 2026; the threat model is reviewed on every security-relevant PR, and
CI fails if the counts above stop matching it.

## How to verify it yourself

Start from the operator's CI: eleven checks on kind clusters, including faults under load,
preemption, scale to zero with KEDA, and load replayed from a public production trace.
Every ADR states its evidence. The GKE repository runs a keyless Terraform plan in CI;
the EKS repository runs `terraform test` in CI with the same pinned tools.

## What is not done yet

- One region, one cloud in operation; GKE and EKS are still two separate definitions.
- No real traffic; no DDoS or edge protection in front of the service yet.
- Runbooks, failure-mode analysis and a production readiness review per component are
  on the roadmap, not written.
- Argo CD and the operator run as single replicas.

## This repository

- `README.md`: this entry point.
- `docs/`: platform documentation, starting with the [threat model](docs/threat-model.md).
- `presentations/`: short guided tours of the platform (coming).

The platform is under active development; what is missing is listed above.
