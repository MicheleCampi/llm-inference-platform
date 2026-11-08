# PM-001: L4 stockouts, three sessions without a GPU

**Date:** 24-25 October 2026 · **Sessions:** B-001, B-002, B-003 · **Cost:** 0.69 EUR (0.40 + 0.29, billed), no GPU time

## Impact

Three GKE sessions came up, but the L4 node never joined: the vLLM pod stayed
Pending. No measurement was possible until the fourth session, a day later.

## Timeline (UTC)

- **24 Oct 15:57**, europe-west4: apply; the VllmService exists at 16:09:20, the pod stays Pending with FailedScaleUp "GCE out of resources" in europe-west4-a, the pool's only zone. Evidence copied, destroyed at 17:05:31.
- **24 Oct 18:39**, europe-west4, pool now on zones a/b/c: scale-up triggered in -c, then the same FailedScaleUp.
- **24 Oct 20:13**, europe-west1 (b/c): scale-up at 20:21:52, FailedScaleUp at 20:23:47; the autoscaler reports RESOURCE_POOL_EXHAUSTED.
- **24 Oct**, B-003, europe-west1 with flex-start: queued for about 45 minutes without a node.
- **25 Oct**, us-central1 with flex-start: -b out of resources, the L4 node Ready in -c about 4 minutes after scale-up; vLLM pod Ready at 10:12:54.

## Cause

The pool asked for one on-demand L4 in a single zone, then in single regions,
where capacity was exhausted at that moment. On-demand requests fail instead of
waiting.

## What changed

- [gke #5](https://github.com/MicheleCampi/gke-llm-inference-platform/pull/5): GPU pool across every zone with L4, `location_policy = ANY`, total cap of one node, so the budget is unchanged.
- [gke #6](https://github.com/MicheleCampi/gke-llm-inference-platform/pull/6): region moved, chosen on capacity and on prices read from the Cloud Billing Catalog that day.
- [gke #9](https://github.com/MicheleCampi/gke-llm-inference-platform/pull/9): us-central1 with flex-start (Dynamic Workload Scheduler), which queues the request at the on-demand price instead of failing.
- [operator #52](https://github.com/MicheleCampi/vllm-coldstart-operator/pull/52): the session checklist waits for the VllmService, copies the events and stops on a stockout instead of waiting with no end time.

## Lessons

A stockout has no end time, so the rule is to copy the evidence, destroy and fix it in code, not wait. Every session ended with the cluster and instance lists empty.
