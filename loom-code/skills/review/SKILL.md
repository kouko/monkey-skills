---
name: review
description: |
  Runs the one closing review over completed functional content, executes package and adversarial verification once, and generates a content-bound attestation. Use when Build is complete or a functional change invalidates prior evidence.
version: 1.3.0
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

Before every host-native dispatch, the station must read the
[shared dispatch profile](../../references/dispatch-profile.md), classify the
task from its evidence, and resolve the atomic model-and-effort profile against
the selected model's verified host capabilities. Record the requested and
effective profile with its evidence-grounded reason in active task context only.
Apply the resolved overrides at invocation time; a static model or effort pin in
an agent contract is invalid. Repeat this resolution for every reviewer,
second-vendor reviewer, blind runner, and adversary dispatch; role and round
labels supply no routing evidence.

- Every change: two fresh-context reviewers from distinct agents.
- A configured second vendor remains required when the repository asks for it.

Reviewer independence is a quality requirement, not a ledger field. Give each
reviewer the branch base, changed paths, intent, spec when present, plan, and
the applicable lens from `references/lenses.md`. Reviewers return the
structured YAML required by `agents/reviewer.md`; the orchestrator converts
the accepted fields to the temporary JSON consumed by finalization.

On Codex, when the selected second vendor is Claude Code, send that complete
reviewer prompt on stdin to one installed-plugin invocation:

```text
python3 <loom-code>/scripts/claude_reviewer.py --model <model> --timeout-seconds 600
```

Run this invocation outside the Codex sandbox with reusable host approval
scoped to the installed `python3 <loom-code>/scripts/claude_reviewer.py`
command. This is the standard Codex-to-Claude path because the sandbox can
hide an existing Claude login that the same runner can use outside it. If that
narrowly scoped permission is denied or unavailable, report an authorization
blocker. Do not fall back to a sandboxed Claude invocation, infer that the user
logged out, run a separate authentication preflight, or request broader Python
or shell access. Do not read, copy, or move Claude credentials into the
sandbox. Only an unauthenticated result from this outside-sandbox invocation
produces the Claude login diagnosis; stop without treating it as transient.

The runner executes one Claude attempt and does not retry. Exit 0 carries the
raw non-empty reviewer output, which must still satisfy `agents/reviewer.md`.
Its JSON stderr names `empty-output` for blank stdout and `timeout` when the
attempt exceeds the bound. Do not run a model-backed preflight. Treat either
result as the transient executor failure already governed below: invoke the
runner at most once more for the same functional-content digest and reviewer
identity. If that attempt also fails before a conforming verdict exists, report
both diagnostics and end the episode as `EXECUTION_FAILED`.

## 3. Run blind and adversarial checks

Use a blind run when an Acceptance line cannot be settled mechanically. For
code, skill, spec, or gate changes, create committed adversarial programs that
exercise the relevant boundary and pass their paths and commands to
`finalize-review`. Do not record a claimed result; finalization executes them.

## 4. Converge within one bounded episode

<!-- gate: review.bounded-episode -->
A closing Review episode starts when fresh reviewers first evaluate completed
functional content for one confirmed-intent commit. Only a newly confirmed
intent starts another episode. The episode admits at most three distinct
functional-content digests; changing the task, app, branch, reviewer, vendor,
model, or technical design does not reset that limit.
A digest is distinct whenever a functional-content file changed since the
content the reviewers last read; publication-only edits do not change it.

- **Round 1 — full review.** Review the cumulative functional content.
- **Round 2 — fix verification.** Batch fatal and important findings, return to
  Build, and resume the same reviewers over the functional fix delta.
- **Round 3 — terminal verification.** If Round 2 still has blockers, first
  stop local patching and perform a technical design re-look. The agent owns
  that re-plan when it preserves requirements, visible behavior, and
  guarantees. Review the resulting final digest once. `NEEDS_REVISION` ends
  the episode as `NON_CONVERGENT`; never dispatch Round 4.

Treat the episode as stuck when the same blocker survives two consecutive
rounds, the blocker count does not decrease after a functional fix, or the fix
repeats the same mechanism shape. Stop local patching at that point and use the
next available round only after the technical design re-look.

Do not ask the user whether to continue or which technical repair to choose.
Ask only when resolving the blocker would change requirements, visible
behavior, or guarantees; that change requires a newly confirmed intent rather
than another round in this episode.

A malformed response, unavailable executor, or other transient failure before
a conforming verdict exists may retry once against the same functional-content
digest. That retry is not a review round. A second executor failure ends the
episode as `EXECUTION_FAILED`; a conforming `NEEDS_REVISION` always consumes
the current round.

Keep this episode in the active task context. Do not create a review-round
ledger or committed state schema. Wording-only publication edits do not reopen
Review.
<!-- /gate -->

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
with any remaining publication metadata; publication validates that single
attestation directly.

## Handoff

Report the reviewers, executed commands, functional digest, and unresolved
findings. On PASS, hand the matching attestation to `loom-code:ship`.
