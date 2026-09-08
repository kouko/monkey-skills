---
name: review
description: |
  Runs the one closing review over completed functional content, executes package and adversarial verification once, and generates a content-bound attestation. Use when Build is complete or a functional change invalidates prior evidence.
version: 1.1.0
---

# Review

Reviewer findings and generated evidence are written in English.

Review decides whether the completed functional content is ready. It produces
`docs/loom/<change-id>/attestation.json`; agents never edit that file by hand.

## 1. Establish the content

Resolve the branch base, read the confirmed intent and plan, and list the
cumulative diff. If only publication metadata changed and a matching
attestation already exists, stop: the evidence is still valid and Ship owns
the remaining work.

## 2. Choose the risk lane

- Small: one fresh-context reviewer.
- Full: two fresh-context reviewers from distinct agents.
- A configured second vendor remains required when the repository asks for it.

Reviewer independence is a quality requirement, not a ledger field. Give each
reviewer the branch base, changed paths, intent, spec when present, plan, and
the applicable lens from `references/lenses.md`. Reviewers return structured
JSON containing reviewer, vendor, model, lens, verdict, and findings.

## 3. Run blind and adversarial checks

Use a blind run when an Acceptance line cannot be settled mechanically. For
code, skill, spec, or gate changes, create committed adversarial programs that
exercise the relevant boundary and pass their paths and commands to
`finalize-review`. Do not record a claimed result; finalization executes them.

## 4. Fix functional findings once

Any fatal or important finding returns to Build. Collect fixes into one batch,
rerun only the checks affected by changed functional content, then obtain fresh
passing verdicts. Wording-only publication edits do not reopen Review.

## 5. Finalize

Write reviewer output and adversarial command declarations to a temporary JSON
input outside the repository:

```json
{
  "verdicts": [
    {"reviewer":"<id>","vendor":"<vendor>","model":"<model>","lens":"code","verdict":"PASS","findings":[]}
  ],
  "findings": [],
  "adversarial": [
    {"command":"python3 <path>","artifact":"<path>"}
  ]
}
```

Then run:

```text
python3 <loom-code>/scripts/loom_checker.py finalize-review <change-id> --input <temporary-json>
```

The checker runs the declared package suite and each adversarial program once.
Only after all executions and verdicts pass does it atomically generate the
attestation bound to the functional-content digest. Commit the generated file
with any remaining publication metadata; no review-only commit shape or SHA
pinning is required.

## Handoff

Report the reviewers, executed commands, functional digest, and unresolved
findings. On PASS, hand the matching attestation to `loom-code:ship`.
