# Platform runbook

Incidents at the platform level: capacity, infrastructure from CI, cost and
teardown. Each section comes from a real incident ([postmortems](postmortems/README.md)).
Faults inside the operator and the latency alerts have their own runbooks:
[operator runbook](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/RUNBOOK.md),
[time to first token burn rate](https://github.com/MicheleCampi/vllm-coldstart-operator/blob/main/docs/runbooks/ttft-burn-rate.md).

## 1. The GPU node never joins (stockout)

Symptom: the vLLM pod stays Pending; events show FailedScaleUp "GCE out of
resources". ([PM-001](postmortems/pm-001-l4-stockouts.md))

1. Read the autoscaler's own state, not only the pod events, which can name
   one zone while every zone is exhausted:
   `kubectl -n kube-system get configmap cluster-autoscaler-status -o yaml`.
   RESOURCE_POOL_EXHAUSTED or STOCKOUT on every node group means no zone has capacity.
2. Copy the events now: they expire after an hour.
3. Stop rule: a stockout has no end time. Past the session's wait cap, destroy
   and fix it in code (zones, region, flex-start); do not wait with nodes billing.

## 2. Apply from CI fails halfway

Symptom: the apply job fails after creating part of the resources; the
cluster may exist in ERROR with no VM. ([PM-003](postmortems/pm-003-ci-apply-stockout.md))

1. List what exists: `terraform state list`, `gcloud container clusters list`,
   `gcloud compute instances list`.
2. Destroy what the session created, with `-target` on the cluster module and
   its network. Do not run a full destroy: it also removes long-lived
   identities, such as the reader of the Grafana Cloud secret.
3. Check the lists are empty before closing the session.

## 3. A billing line nobody estimated

Symptom: the post-session billing shows a SKU that is not in the estimate.
([PM-002](postmortems/pm-002-managed-prometheus-billed.md))

1. Find the service that produced it and whether anything reads its output.
2. If a provider default turned it on, set it explicitly in Terraform and add a
   check in `ci/validate.sh` with a negative case.
3. For Managed Prometheus: `kubectl get ns gmp-system` and its pods must show
   nothing running.

## 4. Closing every session

- Destroy by the session's time cap, whatever the state of the measurements.
- `gcloud container clusters list` and `gcloud compute instances list` empty.
- Read the billing for the day once it is final, against the estimate.
