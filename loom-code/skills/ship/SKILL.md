---
name: ship
description: |
  Publishes a reviewed branch by validating its generated content attestation, running fast publication safety checks, opening the pull request, and verifying CI. Use after Review generated a matching attestation.
version: 1.1.0
---

# Ship

Ship validates publication state; it does not repeat functional verification.
It does not execute package tests or adversarial probes.
Write the PR body in the user's conversation language when the host can
establish it from the confirmed intent or active conversation. Repository
conventions still govern committed artifacts. Internal publication reports
remain English.

## 1. Confirm acceptance

Read the intent and blind-run report when one was required. A confirmed intent
that explicitly says its confirmation authorizes automatic publication carries
that decision into Ship; do not ask again. A legacy intent without that positive
evidence requires one publication decision before anything leaves the machine.
The user may still explicitly stop publication before the outward action.

## 2. Prepare publication text

Ship owns one top-level PR body schema. Reconstruct it from the current intent,
plan, recomputed Git change, generated attestation, and available CI evidence;
do not depend on conversation recall. Use these headings exactly once:

```markdown
## Context
<original problem, relevant history, and why the change is being made now>

## Intended outcome
<the confirmed outcome and success conditions>

## Scope
<included work and explicitly excluded work>

## Decisions
<auditable decision summaries>

## Implementation
<what changed and which components own each responsibility>

## Behaviour change
<observable before-and-after behaviour>

## Verification
<review, tests, attestation, available CI evidence, and known limits>

## Risks and rollback
<remaining risks and a concrete recovery path>

## Follow-ups
<deferred work, or "None">
```

Every decision summary states the chosen option, material alternatives,
trade-offs, supporting evidence, and observed or expected outcome. This is an
auditable rationale, never private or hidden chain-of-thought. Omit or label
unsupported claims as limitations instead of inventing an explanation.

Use Mermaid for meaningful decision branches and component interactions. Also
use it for state transitions or before-and-after behaviour flows when the
relationship carries information.
Select the matching decision, architecture, sequence, state, or comparison
diagram and introduce it with accessible prose. Simple changes omit diagrams;
never add a fixed diagram count or decorative graph.

Use `loom-workflow:git-memory` to classify the change and contribute durable
Decision, Learning, and Gotcha material inside this schema when earned. It does
not replace or reorder Ship's headings.
Always run its deterministic secrets scan. Known public repository, PR, issue,
task, and vendor identifiers need no semantic privacy judge; ambiguous
private-party text does. A semantic false positive needs an audited
`Privacy-Bypass-Reason`; secret findings cannot be bypassed.

Before publication, reject a body with a missing heading, evidence source that
was silently ignored, unsupported decision claim, hidden-reasoning claim, or a
diagram that is required by the relationships above but absent. Retired review
and probe accounting ledgers and their fields are not valid inputs.

Publication-only edits do not change the functional digest and do not return to
Review. Functional edits invalidate the attestation and do.

## 3. Publish once

For an intent carrying automatic-publication authorization, pass its absolute
path to the installed plugin's one publication command:

```text
python3 <loom-code>/scripts/loom_checker.py publish --intent <absolute-intent-path> --title <title> --body-file <absolute-path>
```

For a legacy intent, obtain one publication decision and acknowledge it with:

```text
python3 <loom-code>/scripts/loom_checker.py publish --confirm-authorized --title <title> --body-file <absolute-path>
```

The command verifies exactly one branch attestation, its schema, content
digest, execution identities/results, reviewer verdicts, and live HEAD. It
then derives the origin repository, default base, current branch, and exact
refspec; performs a non-forced push; and opens or reuses one PR. Do not run a
separate attestation preflight or construct Git push or PR-create commands.

The installed plugin's `PreToolUse` hook applies the same check automatically
to direct raw publication commands and retains destination/refspec safety for
callers that bypass `publish`. No repository-local checker scaffold or
hook-firing ledger is required.

## 4. Observe CI

The publication command reports the PR URL, inspects required CI immediately,
and checks again every 30 seconds while any required check remains pending.
It stops when all required checks pass, a required check fails or is cancelled,
or GitHub reports that user action is required. Optional checks do not keep the
command alive. Unchanged pending snapshots produce no repeated user-facing
output.

If checks remain pending after 120 polling intervals (60 minutes), stop and
report that a reliable terminal result could not be obtained. Treat an initial
empty required-check snapshot as registration delay and check once more after
30 seconds; if it is still empty, report that no required checks are registered
and finish successfully.

Observation belongs only to the active publication process. Do not create a
scheduler, daemon, persistent polling record, or restart recovery mechanism.
Stopping the task or Desktop app stops observation.

CI is the external trust boundary: fix a real functional failure through Build
→ Review. A PR-text, version, or other publication-only failure is fixed in
place and reuses the matching attestation.

Publication never authorizes or invokes merge. Do not merge without the user's
separate explicit authorization.
Once that authorization exists, take the root of the worktree whose branch
carries the attestation — `git rev-parse --show-toplevel` run from that
worktree, never the task or main checkout — and issue the direct merge as one
Bash command:

```text
cd '<absolute-repository-root>' && gh pr merge <number> --squash
```

Always render that absolute `cd`; never rely on the Bash tool's workdir,
because Codex may report the task root rather than the executor worktree to the
installed publication hook.

## Handoff

Report the attestation digest, publication checks, PR URL, and CI state. Keep
the worktree until integration is verified.
