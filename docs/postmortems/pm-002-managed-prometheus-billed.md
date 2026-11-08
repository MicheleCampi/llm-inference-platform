# PM-002: Managed Prometheus collected and billed metrics nothing read

**Date:** 27 October 2026 · **Session:** B-005 · **Cost:** 0.067520 EUR, not in the estimate

## Impact

The bill of B-005 had a line no estimate predicted: Prometheus Samples
Ingested, 0.067520 EUR for 1,278,986 samples. Alloy, remote writing to Grafana
Cloud, is the platform's only metrics pipeline, so nothing read those samples.

## Detection

Reading the billing line by line after the session, as every paid session is.

## Cause

Nothing in the Terraform turned managed collection on, and the cluster is
Standard on the REGULAR channel; yet its collectors ran on both nodes. The
provider leaves the setting optional and computed, so leaving it unset did not
mean off.

## What changed

- [gke #11](https://github.com/MicheleCampi/gke-llm-inference-platform/pull/11) (acd6916): `monitoring_config.managed_prometheus.enabled = false` in the gke-gpu module, with a comment saying why.
- `ci/validate.sh` gained a check that rejects the module without that setting, with a negative case proving it fails for the right reason.
- The session checklist now checks the `gmp-system` namespace and the billing ([operator #65](https://github.com/MicheleCampi/vllm-coldstart-operator/pull/65)).

## Lessons

A setting left unset is a setting chosen by someone else. Billing is read
after every session because it is the only place this showed up.
