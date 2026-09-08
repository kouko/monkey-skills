---
name: ship
description: |
  Publishes a reviewed branch by validating its generated content attestation, running fast publication safety checks, opening the pull request, and verifying CI. Use after Review generated a matching attestation.
version: 1.1.0
---

# Ship

Ship validates publication state; it does not repeat functional verification.
It does not execute package tests or adversarial probes.
PR bodies and publication reports are written in English.

## 1. Confirm acceptance

Read the intent and blind-run report when one was required. Present the outcome
to the user and obtain decision point ③ before anything leaves the machine.

## 2. Prepare publication text

Use `loom-workflow:git-memory` to classify memory and compose commit or PR text.
Always run its deterministic secrets scan. Known public repository, PR, issue,
task, and vendor identifiers need no semantic privacy judge; ambiguous
private-party text does. A semantic false positive needs an audited
`Privacy-Bypass-Reason`; secret findings cannot be bypassed.

Publication-only edits do not change the functional digest and do not return to
Review. Functional edits invalidate the attestation and do.

## 3. Validate the publication

Run the installed plugin checker against the selected HEAD:

```text
python3 <loom-code>/scripts/loom_checker.py push --head HEAD --require-live-head
```

The fast gate verifies exactly one branch attestation, its schema, content
digest, execution identities/results, reviewer verdicts, and live HEAD.

The installed plugin's `PreToolUse` hook applies the same check automatically
to canonical `git push` and PR commands and retains destination/refspec safety.
No repository-local checker scaffold or hook-firing ledger is required.

## 4. Publish and observe CI

Push the exact selected HEAD to its current branch, open one PR, and report its
URL. CI is the external trust boundary: inspect every required check and fix a
real functional failure through Build → Review. A PR-text, version, or other
publication-only failure is fixed in place and reuses the matching attestation.

Do not merge without the user's explicit authorization.

## Handoff

Report the attestation digest, publication checks, PR URL, and CI state. Keep
the worktree until integration is verified.
