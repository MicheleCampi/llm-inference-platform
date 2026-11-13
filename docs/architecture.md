# Architecture

C4 views of the platform: who uses it (context) and what runs inside it
(containers). Validity: designed, built and verified under simulated
production load on GKE, one region (us-central1), not operated in
production. The AWS side is a separate project and is not drawn here.

## Context

```mermaid
flowchart LR
  team["Product team<br/>declares a model, a latency objective and a budget"]
  platform["Inference platform<br/>provisions, delivers, secures, observes and prices"]
  gcp["Google Cloud<br/>GKE, L4 GPUs"]
  grafana["Grafana Cloud<br/>burn-rate alerts by email"]
  billing["Billing export<br/>BigQuery, cost per team"]
  team --> platform
  platform --> gcp
  platform --> grafana
  platform --> billing
```

## Containers

```mermaid
flowchart TB
  team["Product team"]
  subgraph delivery["Delivery"]
    bridge["model-promotion-bridge<br/>promoted model to FleetService manifest"]
    argocd["ArgoCD<br/>syncs manifests pinned to signed tags"]
  end
  subgraph cluster["GKE cluster, one namespace per team"]
    operator["vllm-coldstart-operator<br/>VllmService, FleetService: cold start, placement, preemption, scale to zero"]
    keda["KEDA and HTTP add-on<br/>scale from and to zero"]
    vllm["vLLM on L4<br/>serves the model"]
    alloy["Alloy and Prometheus<br/>metrics and SLO rules"]
  end
  iac["gke repo<br/>Terraform, plan and apply from CI with approval"]
  grafana["Grafana Cloud<br/>alerting"]
  inferscope["inferscope<br/>measurement and diagnosis"]
  team --> bridge
  bridge --> argocd
  argocd --> operator
  iac --> cluster
  operator --> vllm
  keda --> vllm
  vllm --> alloy
  alloy --> grafana
  inferscope -.-> vllm
```

## Where each piece lives

- Operator: [vllm-coldstart-operator](https://github.com/MicheleCampi/vllm-coldstart-operator)
- Cluster and GitOps: [gke-llm-inference-platform](https://github.com/MicheleCampi/gke-llm-inference-platform)
- Readiness against a checklist: [prr.md](prr.md); numbers: [r6-report.md](r6-report.md)
