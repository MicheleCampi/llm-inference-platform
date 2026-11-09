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
| Delivery: GitOps and models | 3 | 0 | 1 |
| Self-service contract | 8 | 3 | 2 |
| Signals | 4 | 0 | 1 |
| Security and tenancy | 2 | 2 | 0 |
| Reliability | 8 | 6 | 1 |
| Cost | 2 | 1 | 1 |
| Operations and readiness | 5 | 2 | 0 |
| **Platform layers (foundations excluded)** | **35** | **16** | **6** |

## Billed GPU sessions

| Session | GPU run (UTC) | Region | L4 hours | Net cost | Billing read | Outcome |
|---|---|---|---|---|---|---|
| B-005 | 27 October 2026, apply 06:40, destroy 10:06 (cluster up without GPU on 26 October) | us-central1 | 2.86 | 2.48 EUR (2.484147; gross 2.56) | 28 October 2026 | Whole chain end to end; VllmTtftBudgetBurnSlow and Fast fired and emailed. Analysis in ADR-0022 of the operator. |

The billing CSV of B-005 is kept in the maintainer's private evidence store, not published.
