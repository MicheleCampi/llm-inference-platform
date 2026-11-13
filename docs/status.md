# Platform status

How far the platform is, counted against the maintainer's checklist of a full
company platform. Percentage = (done + partial/2) / items. CI
(`ci/check-status.py`) recomputes the totals from this table and fails if the
README stops matching it.

## Layers

| Layer | Items | Done | Partial |
|---|---|---|---|
| Foundations: truth and verification | 22 | 22 | 0 |
| Provisioning on two clouds | 3 | 2 | 0 |
| Delivery: GitOps and models | 3 | 3 | 0 |
| Self-service contract | 8 | 3 | 2 |
| Signals | 4 | 0 | 1 |
| Security and tenancy | 2 | 2 | 0 |
| Reliability | 8 | 8 | 0 |
| Cost | 2 | 2 | 0 |
| Operations and readiness | 5 | 3 | 0 |
| **Platform layers (foundations excluded)** | **35** | **23** | **3** |

## Billed GPU sessions

| Session | GPU run (UTC) | Region | L4 hours | Net cost | Billing read | Outcome |
|---|---|---|---|---|---|---|
| B-005 | 27 October 2026, apply 06:40, destroy 10:06 (cluster up without GPU on 26 October) | us-central1 | 2.86 | 2.48 EUR (2.484147; gross 2.56) | 28 October 2026 | Whole chain end to end; VllmTtftBudgetBurnSlow and Fast fired and emailed. Analysis in ADR-0022 of the operator. |
| B-006 | 4 November 2026, apply from CI failed on a GCE stockout; cluster in ERROR without VMs, targeted destroy | us-central1 | 0 | 0.0073 EUR | 13 November 2026 | No GPU. Postmortem PM-003. |
| B-007 | 5 November 2026, first apply from CI to a ready cluster, no GPU used | us-east1 | 0 | 0.1196 EUR | 13 November 2026 | Tenancy proven live: quota, LimitRange, default-deny between teams. |
| B-008 | 8 November 2026, apply 11:24, destroy 13:28 | us-east1 | 0 | 0.3491 EUR | 13 November 2026 | L4 stockout in us-east1-c and -d, no GPU node. External Secrets and the team Role verified live. |
| B-009 | 9 November 2026, apply 19:41, destroy 21:33 | us-central1 | 1.477 | 1.2689 EUR | 13 November 2026 | DR drill: RTO 46 min 11 s, first 200 in 1.68 s. Showback: team-demo 68.8%, platform 31.2%. |
| B-010 | 12 November 2026, apply 17:41, destroy 18:57 | us-central1 | 0.472 | 0.5217 EUR | 13 November 2026 | Model delivery live: a FleetService rendered by model-promotion-bridge, synced by ArgoCD, answered 200 from the L4. TPOT mean 61.9 ms, 21 of 21 requests (light sequential load). Showback: team-demo 50.4%. |

The billing CSV of B-005 is kept in the maintainer's private evidence store, not published.
