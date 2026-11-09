# Simulated production: the R6 report

Designed, built and verified under simulated production load, evidence in CI. Not operated in production: no real users, no real traffic. File:line references point to [vllm-coldstart-operator](https://github.com/MicheleCampi/vllm-coldstart-operator) (ADRs in docs/adr/) unless stated.

## Validity envelope

- Server: llm-d-inference-sim v0.8.2 on kind (CI and a development host), and one L4 on GKE for short windows (B-004, B-005).
- Model on the L4: Qwen2.5-7B-Instruct, bf16, vLLM v0.11.0.
- Load: one trace-derived profile, replayed open loop (ADR-0012).
- Not shown: queueing of the simulator against the L4 (ADR-0024), more than one GPU replica, real tenants.

## Architecture

A team declares a model, a latency objective and a budget; [platform.md](../conversations/2026-11-03-platform-engineer/platform.md) walks the full path. Here: the operator (VllmService, FleetService) on kind or GKE, KEDA and its HTTP add-on for scaling, Prometheus for the objective.

## Objectives (ADR-0013, ADR-0022 D1)

- TTFT within 1000 ms for 95% of requests; on the L4, prompts above 2048 tokens within 2000 ms.
- TPOT within 100 ms on the L4 and 50 ms on the simulator; 99.5% of requests served.

## Results

| Claim | Number | Where | Source |
|---|---|---|---|
| Profile replayed on schedule | 222 of 222, send delay p99 3.0 ms | Docker | ADR-0012:126-128 |
| Capacity of one L4 replica | 0.229 to 0.345 req/s | L4 | ADR-0022:52-66 |
| Fleet against one replica, TTFT within 1 s | 96.4% against 68.9% | CI run 39334011664 | ADR-0014:181-188 |
| Wake from zero, first token | 8.164 s, all 222 answered 200 | CI run 39575073713 | ADR-0015:241-256 |
| Back to zero | 334 s after the last response | CI run 39575073713 | ADR-0015:255 |
| Drain and preemption notice under load | 4 open streams, 0 cut | kind | ADR-0019:71, ADR-0024:48-49 |
| Cordon moves the replica | Ready on the other worker | kind, job preemption | ADR-0017:62-67 |
| Simulator against L4, TTFT p50/p95 | 258/1126 against 217/1198 ms | kind, L4 | ADR-0024:51-54 |
| Cost per million generated tokens | 4.38 to 8.07 EUR within objectives, 1.16 outside | B-005 records | ADR-0025:47-59 |
| Billed cost of one CI apply to a ready cluster | 0.1196 EUR net, all services (0.1194 on rows labelled cost-center=inference) | billing export, read 2026-11-09 | finops/README.md in gke-llm-inference-platform |

Cold starts on the L4: docs/BENCHMARKS.md in the operator.

## Reproduce

- Every push runs the jobs in `.github/workflows/ci.yml`: preemption (line 799), faults-under-load (977), sim-load (1096), scale-out (1357), scale-from-zero (1526).
- Judge a run with `hack/loadgen/slo_check.py`, price it with `hack/loadgen/cost.py`; tests in `hack/loadgen/test_slo_check.py` and `hack/loadgen/test_cost.py`.
- GPU session: `hack/gpu-session/gke-l4/run-load.sh NAME KEEP SEED MODEL OUTDIR [TARGET_URL]`.
- Billed cost: `finops/showback.sql` in gke-llm-inference-platform.

## Open limits

- The simulator does not model queueing on the L4 (ADR-0024).
- Load concentrates on one pod with three Ready; cause not investigated (ADR-0014:161-168, ADR-0015:186-193).
- Node boot at each wake not measured (ADR-0015:293).
- One profile, one model, one GPU class.
