# Golden path: a new team serves a model

Who it is for: a product team that wants an LLM endpoint on the platform. Each step says
what the team does, what the platform does, and whether it works today. Breaks are stated,
not hidden.

Status as of 13 November 2026, gke release `v0.8.4`.

1. **Promote a model.** The team promotes a model version in MLflow.
   [model-promotion-bridge](https://github.com/MicheleCampi/model-promotion-bridge) renders a
   VllmService, or with `--kind fleet` a FleetService, that pins that exact revision, both in
   `extraArgs` (as vLLM's `--revision`) and in annotations. The manifest goes under
   `teams/<team>/` in gke, and the team's Argo CD application syncs it at the signed release tag.
   *Today:* works; on 12 November 2026 (session B-010) a FleetService rendered by the bridge
   was synced by Argo CD and answered 200 from an L4. **Break 1: closed.**
2. **Declare the service.** The fields are `model`, `replicas`, `warmupStrategy`, `image` and
   `gpu` (`deploy/examples/qwen-7b.yaml` in
   [vllm-coldstart-operator](https://github.com/MicheleCampi/vllm-coldstart-operator)). For
   several replicas, FleetService adds `placement`, `hysteresis` and a `template`.
   *Today:* works, with end-to-end tests on kind in the operator's CI.
3. **Declare an objective and a budget.** `objective: {ttftSeconds, percentile}` and
   `budget: {eurPerMonth}` in the VllmService spec, validated by the CRD (since operator v0.8.0;
   `teams/demo/qwen-7b.yaml` in gke). Since operator v0.10.0 a FleetService carries them too
   and copies them to each replica. Each service is evaluated on its own error budget,
   `1 - percentile/100`. *Today:* works for a 1 s objective; any other value raises a ticket
   alert (`VllmTtftObjectiveUnsupported`). **Break 2, still open:** the latency threshold is
   not yet per service.
4. **Delivery.** Argo CD (app of apps, sync waves) on
   [GKE](https://github.com/MicheleCampi/gke-llm-inference-platform) follows the signed
   release tag `v0.8.4`; `scripts/promote-tag.sh` checks the tag's signature and ancestry
   before moving the cluster to it. The L4 GPU pool scales 0..1 behind a taint.
   *Today:* platform and team applications ran live at `v0.8.3` (sessions B-009 and B-010);
   `v0.8.4` has passed CI and has not yet run on a live cluster.
5. **Serving.** The operator handles warm-up, placement, preemption and scale to zero with
   KEDA. *Today:* works in CI and in three measured L4 sessions (27 October, 9 and 12 November
   2026). Asking the GPU node from zero for a FleetService (`nodePool.provisionOnEmpty`,
   operator v0.10.0) passes CI and has not yet run live.
6. **Observe.** vLLM metrics go to Grafana Cloud through Alloy; fast and slow burn-rate
   alerts fire on the objective. *Today:* works, and the TTFT alerts fired in the L4 session
   of 27 October; each team on its own error budget; the threshold is 1 s for everyone
   (break 2). Burn-rate alerts on time per output token and on success rate (operator
   ADR-0026) are tested with promtool and have not yet been seen firing live.
7. **Pay.** 4.38 to 8.07 EUR per million generated tokens within the L4 objectives
   (ADR-0025). Cost per team comes from the Cloud Billing export (`finops/showback.sql` in
   gke); every billed session is in [status](status.md). **Break 3, narrowed:** showback
   works; the declared budget is not yet compared with cost.
8. **Isolation.** Each team has its own namespace, a GPU quota, a LimitRange, a deny-all
   NetworkPolicy, and a deployer ServiceAccount bound to a team Role, onboarded with one
   command, checked in CI and part of the release. *Today:* quota, LimitRange and default-deny
   proven on a live cluster (session B-007). **Break 4: closed.** Still open at the edge: one
   static key per service gives no per-client attribution (R2 in the
   [threat model](threat-model.md)), and there are no rate limits (D3).

Where the remaining work goes: a latency threshold per service (break 2), then comparing the
declared budget with cost (break 3), then per-client identity and rate limits at the edge
(R2, D3).
