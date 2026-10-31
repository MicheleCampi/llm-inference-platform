# Threat model (STRIDE)

## Validity envelope
- Scope: vllm-coldstart-operator @ deaf851, capstone-iac (GKE) @ acd6916, eks-llm-inference-platform @ f9420b3, bridge @ 18e021c.
- Method: every claim below was read in the repository at that commit. Where nothing was read, the row says "not assessed".
- Out of scope: `hack/` directories (lab manifests; they contain NodePort Services by design); live cluster state; Argo CD AppProjects (planned next).
- Status: lab platform, no public endpoint today. This model must be redone before any internet-facing exposure.

## Assets and trust boundaries
- Assets: model weights, the vLLM inference API, the Kubernetes control planes, the container images and their provenance, CI cloud credentials.
- Boundaries: internet -> cloud control plane; CI (GitHub Actions) -> cloud via OIDC; pod <-> pod inside the cluster; registry (GHCR) -> nodes.

## STRIDE

| # | Threat | Component | Status | Evidence / proposed fix |
|---|---|---|---|---|
| S1 | Spoofing: a pod calls vLLM as any client | operator / vLLM | Mitigated (operator PR #71) | `spec.apiKeySecretRef {name,key}` on VllmService (operator `src/lib.rs:94`, `:99`) and on the VllmFleet template (`src/fleet_types.rs:82`, copied to every replica at `src/fleet_controller.rs:251`) injects `VLLM_API_KEY` via `secretKeyRef` with `optional: false` (`src/main.rs:238`, `:243`): a missing Secret keeps the pod from starting instead of starting it open; the key is never in the container args. vLLM reads `VLLM_API_KEY` when `--api-key` is unset and its middleware guards `/v1`, `/v2`, `/inference`, `/cohere` (vLLM v0.28.1rc0 source, `entrypoints/serve/middleware/authenticate.py:11`, `register.py:33`), so `/health` and `/metrics` stay open for probes and Prometheus. Together with I2. Evidence: unit tests (env from the Secret, `optional=false`, absent when unset, key not in args) plus mutation check (`optional: Some(true)` fails it); CRD regenerated, deploy and chart identical; CI 11/11. Residual: the field is optional for back-compat and unset means no key, with no warning or event; the env is added only on GPU pods (`gpu > 0`, `src/main.rs:119`), so no CI e2e job runs with a key and the behaviour is not verified against a live vLLM; one shared static key per service, no per-tenant identity or quota; rotating the key needs a pod restart. |
| S2 | Spoofing: CI impersonation towards GCP | capstone-iac | Mitigated | Keyless OIDC federation bound to repository_id (`bootstrap/ci-identity/main.tf:19-61`). |
| S3 | Spoofing: workloads using node credentials | GKE | Mitigated | Workload Identity (`terraform/modules/gke-gpu/main.tf:19-22`); nodes run as a dedicated minimal SA (~`main.tf:58`). |
| S4 | Spoofing: workloads using node IAM role | EKS | NOT mitigated | No IRSA / Pod Identity. Fix: IRSA per service account. |
| T1 | Tampering: image swapped in registry | operator | Mitigated | SLSA Build L2 provenance via `actions/attest-build-provenance` (`.github/workflows/release-image.yml`); verifiable with `gh attestation verify`. L3 not claimed. |
| T2 | Tampering: CI inputs or base images drift | operator | Mitigated | Inputs pinned by digest (`ci.yml:18-37`); CI rejects unpinned Dockerfile frontend/builder (`ci.yml:93-94`). |
| T3 | Tampering: vLLM image or model swapped | bridge | Partly mitigated | vLLM image pinned by digest (`README.md:14`); model provenance carried as annotations (`bridge/render.py:25,78-82`), not cryptographically verified. Fix: pin model revision hash and verify at load. |
| T4 | Tampering: container filesystem | operator pod | Mitigated | readOnlyRootFilesystem, runAsNonRoot, no privilege escalation, capabilities dropped (`chart/templates/deployment.yaml:27,56-58`). |
| T5 | Tampering: vLLM pod hardening | vLLM pods | NOT mitigated | No securityContext on generated pods. Fix: same baseline as the operator, Pod Security Admission `restricted` where GPU allows. |
| T6 | Tampering: merge to main without CI | GKE repo | Mitigated | Ruleset `protect-main` (id 26236736, active, verified via `rules/branches/main`): validate required, no force-push, no deletion. Residual: terraform plan not required (needs environment approval, would block every merge); signed commits not required; admin can edit the ruleset; no required review (single maintainer). |
| R1 | Repudiation: who changed infra | GKE / CI | Partly mitigated | OIDC identity ties actions to a workflow; GCP audit logs default only. Fix: export Admin Activity logs. |
| R2 | Repudiation: who sent a prompt | vLLM | NOT mitigated | Only one shared static key per service (S1, operator PR #71), so no per-client attribution. |
| I1 | Information disclosure: inference API exposed | all | Mitigated (today) | 0 Ingress/Gateway/HTTPRoute/LoadBalancer/NodePort outside `hack/` in all 4 repos (mutation-checked against `hack/`); vLLM Service is ClusterIP (`main.rs:328,353-360`). |
| I2 | Information disclosure: lateral access inside cluster | all | Mitigated (operator PR #70) | The operator owns a default-deny ingress NetworkPolicy per VllmService (`build_network_policy_with`, operator `src/main.rs`): TCP 8000 is reachable only from same-namespace pods labelled `inference.michelecampi.dev/client=<name>`, from the metrics namespace (`networkPolicy.metricsNamespace`, default `monitoring`), and from namespaces listed in `networkPolicy.extraIngressNamespaces` (default empty: fail-closed). Evidence: unit test plus mutation check (`In` -> `NotIn` fails it); CI job scale-from-zero passes with the policy on through the KEDA HTTP interceptor (namespace `keda` admitted explicitly), and before that fix the same job hung, which shows kindnet enforces the policy. Residual: ingress only, no egress policy; `networkPolicy.enabled=false` in the two CI jobs that reach pods through a NodePort (source is the node IP after kube-proxy SNAT); enforcement on GKE/EKS depends on the CNI and is not verified on a live cluster; other namespaces (Alloy, Argo CD) are not default-denied. |
| I3 | Information disclosure: operator reads secrets | operator | Mitigated | ClusterRole grants no access to secrets, exec or configmaps. |
| I4 | Information disclosure: observability credentials | GKE monitoring | Not assessed | Grafana Cloud secret only referenced (`monitoring.yaml:25`). |
| D1 | DoS: GKE control plane reachable from internet | GKE | Mitigated | `master_authorized_networks_config` with empty default = nodes only (`main.tf:43-55`); CIDR injected at apply time (`variables.tf:54-55`). Endpoint is public but filtered (no private_cluster_config). |
| D2 | DoS / brute force on EKS API endpoint | EKS | Mitigated | `public_access_cidrs` has no default and is set at apply time; validation rejects `[]` and `0.0.0.0/0` (eks PR #1, main 63c66aa). Proven by `terraform test` with a mock provider: 3 passed, 0 failed. Residual: endpoint still public (filtered), no private endpoint; eks repo has no CI, the test is run by hand. |
| D3 | DoS: GPU exhaustion by a single client | vLLM | NOT mitigated | One shared key per service (S1) keeps out callers without it, but there are no rate limits and no quotas. Fix: see Edge section. |
| D4 | DoS: cost exhaustion | GKE | Partly mitigated | Budget ceiling 100 EUR (project rule); managed Prometheus disabled for cost (`main.tf:27-35`). |
| E1 | Elevation: operator compromise | operator | Mitigated | Delete only on `vllmservices`; create/patch limited to deployments and services. Residual: patching Deployments can run arbitrary images. Fix: admission policy on image digests. |
| E2 | Elevation: cluster-admin by creator | EKS | Partly mitigated | `authentication_mode="API"` but `bootstrap_cluster_creator_admin_permissions=true`. Fix: explicit access entries, drop creator admin. |
| E3 | Elevation: GitOps deploys anything anywhere | GKE Argo CD | Partly mitigated | gke PR #12 (main 0da76b9): AppProject `workloads` (operator, alloy, monitoring) limited to 3 repos, namespaces vllm-system and monitoring, 4 cluster kinds (`argocd/apps/projects.yaml`), validated by kubeconform -strict in CI. Residual: ClusterRoleBinding allowed in workloads (needs admission policy); `platform` is cluster-admin by construction; root-app stays in `default`; no live sync (cluster down). |

## DDoS and the edge
Today there is no public edge: the platform cannot be attacked at L7 from the internet because nothing is exposed (I1). The control planes are the only internet-facing surface (D1 mitigated, D2 open).

Design for exposure (proposed, not implemented):
1. L3/L4: cloud load balancer only (Google Cloud Armor / AWS Shield Standard). Volumetric attacks are absorbed by the provider, not by the cluster.
2. L7 at the edge: WAF rules, per-IP and per-key rate limits, request size cap (prompt tokens), TLS termination.
3. Gateway in cluster: authenticated API keys, per-tenant token budgets, max_tokens cap, concurrency limit per tenant. LLM DoS is measured in tokens, not requests.
4. vLLM: bounded queue (`--max-num-seqs`), reject early with 429 instead of queueing until timeout.
5. Scale: autoscaling bounded by budget. Unbounded autoscaling turns a DoS into a cost attack (D4).

## Priority of fixes
1. Per-client identity for vLLM (R2). S1 closed by the vLLM API key from a Secret (operator PR #71); I2 closed by the operator's NetworkPolicy (operator PR #70).
2. Private EKS endpoint or bastion (D2 residual; CIDRs closed by eks PR #1).
3. Admission policy for E3 residual (T6 closed by ruleset `protect-main`).
4. vLLM pod securityContext (T5), IRSA (S4).
5. Edge stack before any public exposure (D3).
