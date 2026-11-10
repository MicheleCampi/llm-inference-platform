# Platform runbook

Incidents at the platform level: capacity, infrastructure from CI, cost and
teardown. Sections 1 to 4 come from real incidents ([postmortems](postmortems/README.md));
sections 5 and 6 from tested faults ([failure-mode analysis](fmea.md)).
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

## 5. Node drained or preempted under load

Symptom: a GPU node gets a preemption notice or is drained while streams are
open. Tested on kind under load: 4 open streams, 0 cut; a cordoned node's
replica came back Ready on the other worker ([R6](r6-report.md)).

1. Do not force-delete the pod: the preStop drain lets open streams finish.
2. Check the replacement replica: Pending with FailedScaleUp is section 1.
3. Not yet tested on a GPU node: record the timings if it happens there.

## 6. Cluster lost

Symptom: the cluster is gone or unusable. Workloads are stateless and secrets
live outside the cluster, so the recovery is a rebuild from Git
([drill](https://github.com/MicheleCampi/gke-llm-inference-platform/blob/main/docs/upgrade-and-dr.md#drill-9-november-2026): 46 min 11 s from no cluster to the team model Ready).

1. Dispatch `apply.yml` from CI and approve the plan.
2. Run `scripts/bootstrap-argocd.sh`, then apply `root-app.yaml`; Argo CD syncs the rest.
3. Wait for the GPU node: a stockout here is section 1.
4. Done when a team model answers HTTP 200.
