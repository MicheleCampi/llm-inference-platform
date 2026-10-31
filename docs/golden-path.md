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
3. **Declare an objective and a budget.** **Break 2:** there are no fields for them. One
   objective applies to every service: time to first token within 1 s for 95% of requests
   (ADR-0013, `deploy/monitoring/slo-rules.yaml` in the operator). *Next:* objective and
   budget in the spec, evaluated per service by the same burn-rate rules.
4. **Delivery.** Argo CD (app of apps, sync waves) on
   [GKE](https://github.com/MicheleCampi/gke-llm-inference-platform) follows the signed
   release tag `v0.1.0`; the L4 GPU pool scales 0..1 behind a taint. *Today:* works for the
   platform's own components; team manifests wait on break 1.
5. **Serving.** The operator handles warm-up, placement, preemption and scale to zero with
   KEDA. *Today:* works in CI and in one measured L4 session (27 October 2026).
6. **Observe.** vLLM metrics go to Grafana Cloud through Alloy; fast and slow burn-rate
   alerts fire on the objective. *Today:* works, and the alerts fired in the L4 session;
   one objective for everyone (break 2).
7. **Pay.** 4.38 to 8.07 EUR per million generated tokens within the L4 objectives
   (ADR-0025). **Break 3:** cost is per scenario, not attributed to a team (no showback).
8. **Isolation.** **Break 4:** services share a namespace, one static key per service gives
   no per-client attribution (R2 in the [threat model](threat-model.md)), and there are no
   quotas or rate limits (D3). *Next:* namespace, quota and identity per team.

Where the breaks go: tenancy (break 4) first, then delivery of team manifests through
Argo CD (break 1), then objective and budget in the contract (break 2), then showback
(break 3).
