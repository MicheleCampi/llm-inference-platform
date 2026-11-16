# How I work with AI

I deliver this platform AI-native, with a human in the loop. I set the
direction, make the decisions, review and merge every change, approve every
cost and run the live sessions; an AI coding agent (Claude Code) does the
typing: code, tests and most of the documentation. Every merged change is mine
to answer for. This page says what that means in practice, and where each part
can be checked.

## Who does what

| Step | Agent | Me |
|---|---|---|
| Problem and options | Researches, proposes options with trade-offs | Chooses; the choice is written down before work starts |
| Change | Writes code, tests and docs on a branch, opens a pull request | Reads the diff and the evidence in the description |
| Merge | Does not merge | Merges (squash), or asks for changes |
| Release | Cannot push tags | Tags and signs the release |
| Spend | Estimates the cost | Approves a cap before anything paid is switched on, then reconciles it with the bill |
| Live session | Prepares the runbook and the commands | Runs them, approves each deployment, checks the teardown |

## Where to check it

- **Decisions in writing.** 27 architecture decision records in the operator
  ([docs/adr](https://github.com/MicheleCampi/vllm-coldstart-operator/tree/main/docs/adr)),
  each with its evidence. Day-to-day decisions are numbered in a private notes
  repository and cited where they apply (for example D-0114 in the aws-ecs README).
- **Every change is a pull request.** The default branches are protected: on
  eks, a pull request and two checks are required and force-push is off
  (`gh api repos/MicheleCampi/eks-llm-inference-platform/branches/main/protection`);
  on gke, the ruleset `protect-main` ([threat model T6](threat-model.md)).
  Pull request descriptions state effect, cost, rollback and evidence, for
  example [aws-ecs #19](https://github.com/MicheleCampi/aws-ecs-delivery-platform/pull/19).
- **Nothing reaches a cloud without a person.** Applies run only by manual
  dispatch behind a GitHub environment approval
  ([aws-ecs case study](https://github.com/MicheleCampi/aws-ecs-delivery-platform/blob/main/docs/case-study.md),
  eks `.github/workflows/apply.yml`); a merge applies nothing.
- **Budget first, bill after.** Every paid GPU session is listed with its real
  cost and the date the bill was read ([status](status.md#billed-gpu-sessions));
  the EKS stack carries an AWS Budget in Terraform (eks `budget.tf`).
- **Signed releases.** Release tags on gke, eks, the operator, inferscope,
  inference-platform-ci and the tagged experiments are signed (`git cat-file -p <tag>`).

## Controls that do not depend on my review

Review can miss things, so the repositories also refuse bad changes on their own:

- **Required checks before merge** on the default branches (eks: validate and a
  read-only `terraform plan`; gke: `validate` in the ruleset).
- **Negative tests**: inputs that must be rejected, such as seven broken
  manifests in gke CI, or an empty or open `public_access_cidrs` in eks
  `terraform test`.
- **Mutation checks**: a test is accepted only if breaking the code it guards
  makes it fail (examples in the [threat model](threat-model.md), rows S1, S4, I2).
- **End-to-end jobs**: eleven CI jobs on kind clusters in the operator, including
  faults under load and preemption.

## Data rules

- **No secrets in git, none handed to the agent.** CI authenticates to AWS and
  GCP through OIDC, with no static keys; runtime secrets come from AWS Secrets
  Manager or GCP Secret Manager through External Secrets. The CI of the platform
  repositories (this one, gke, eks, aws-ecs, model-promotion-bridge) runs
  gitleaks on the full history (`ci/validate.sh`).
- **Identifiers masked.** The AWS account id is masked in CI logs from the first
  step of each job (eks v2.2.8, `.github/workflows/apply.yml`); published
  evidence redacts account ids, public IPs and emails
  ([eks live run](https://github.com/MicheleCampi/eks-llm-inference-platform/blob/main/docs/evidence/live-2026-11-15.md)).
- **Least privilege for the agent.** It reaches GitHub through an app installed
  on named repositories only, cannot push tags, and every cloud apply needs a
  person; the tools CI downloads are pinned by SHA-256
  ([inference-platform-ci](https://github.com/MicheleCampi/inference-platform-ci)).
- **No personal or customer data.** The platform has never served real users,
  so no personal data reaches the agent or the repositories. In a company I
  would use only the AI tools, and send only the data classes, that the company
  has approved, as its GDPR and security policies require.
- **Claims are checked.** A number on the profile or in a README links to the
  file or command that produces it; where the raw output was not kept, the page
  says so ([aws-ecs evidence](https://github.com/MicheleCampi/aws-ecs-delivery-platform#evidence)).

## What it does not mean

- I do not write the code by hand, and I say so up front. What I bring is the
  design, the decisions, the review and the operation, plus the cost model
  behind them.
- Speed is not the goal; control is. A change I cannot explain does not get
  merged, and a merged change has an owner: me.
- None of this has run in production with real users; every repository lists
  what is not done yet.
