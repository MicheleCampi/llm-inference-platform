# PM-003: first apply from CI failed on a stockout

**Date:** 4 November 2026 · **Session:** B-006 · **Cost:** 0.0073 EUR (billing export, provisional)

## Impact

The first apply run from CI (run 41901126729) created 8 of 11 resources (four
APIs, VPC, subnet, node service account, IAM) and failed at 20:02 UTC: Compute
Engine had insufficient resources in us-central1. The cluster was left in
ERROR, with no VM.

## Response

The session checklist stops on a stockout. A full destroy would also have
removed `eso-grafana-reader` and its access to the Grafana Cloud secret, which
lives outside the session, so it was rejected. A targeted destroy removed
`module.gke_gpu`, the subnet and the VPC (6 resources, including the
Workload Identity binding that the next apply recreates). Afterwards: no
cluster, no instance.

## What it proved

The CI path worked up to resource creation on GCP: keyless plan, approval,
apply as a second identity. The next session (B-007, us-east1) reached a ready
cluster from CI.

## Lessons

Destroy what the session created, not everything Terraform knows: a full
destroy would have broken a long-lived identity to clean up a failed cluster.
