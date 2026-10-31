# Golden path: a new team serves a model

Who it is for: a product team that wants an LLM endpoint on the platform. Each step says
what the team does, what the platform does, and whether it works today. Breaks are stated,
not hidden.

1. **Promote a model.** The team promotes a model version in MLflow.
   [model-promotion-bridge](https://github.com/MicheleCampi/model-promotion-bridge) renders a
   VllmService that pins that exact revision, both in `extraArgs` (as vLLM's `--revision`)
   and in annotations. *Today:* works as a CLI. **Break 1:** nothing applies its output;
   there is no Argo CD application for team manifests yet.
2. **Declare the service.** The fields are `model`, `replicas`, `warmupStrategy`, `image` and
   `gpu` (`deploy/examples/qwen-7b.yaml` in
   [vllm-coldstart-operator](https://github.com/MicheleCampi/vllm-coldstart-operator)). For
   several replicas, FleetService adds `placement`, `hysteresis` and a `template`.
   *Today:* works, with end-to-end tests on kind in the operator's CI.
3. **Declare an objective and a budget.** `objective: {ttftSeconds, percentile}` and
   `budget: {eurPerMonth}` in the VllmService spec, validated by the CRD (operator v0.8.0;
   `teams/demo/qwen-7b.yaml` in gke). Each service is evaluated on its own error budget,
   `1 - percentile/100`. *Today:* works for a 1 s objective; any other value raises a ticket
   alert (`VllmTtftObjectiveUnsupported`). **Break 2, narrowed:** the latency threshold is not
   yet per service.
4. **Delivery.** Argo CD (app of apps, sync waves) on
   [GKE](https://github.com/MicheleCampi/gke-llm-inference-platform) follows the signed
   release tag `v0.5.0`; the L4 GPU pool scales 0..1 behind a taint. *Today:* works for the
   platform's own components; team manifests wait on break 1.
5. **Serving.** The operator handles warm-up, placement, preemption and scale to zero with
   KEDA. *Today:* works in CI and in one measured L4 session (27 October 2026).
6. **Observe.** vLLM metrics go to Grafana Cloud through Alloy; fast and slow burn-rate
   alerts fire on the objective. *Today:* works, and the alerts fired in the L4 session;
   each team on its own error budget; the threshold is 1 s for everyone (break 2).
7. **Pay.** 4.38 to 8.07 EUR per million generated tokens within the L4 objectives
   (ADR-0025). **Break 3:** cost is per scenario, not attributed to a team (no showback); the declared
   budget is exported as a metric but not yet compared with cost.
8. **Isolation.** **Break 4, in part closed:** each team now has its own namespace, a GPU
   quota, a LimitRange and a deny-all NetworkPolicy, onboarded with one command and checked
   in CI; not yet in a release or run on a live cluster. Still open: one static key per
   service gives no per-client attribution (R2 in the [threat model](threat-model.md)),
   there are no rate limits (D3), and no identity per team. *Next:* identity per team.

Where the breaks go: tenancy (break 4) first, then delivery of team manifests through
Argo CD (break 1), then a latency threshold per service (break 2), then showback
(break 3).
