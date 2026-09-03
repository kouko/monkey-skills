# Spec review round 1 — verdicts

Spec blob 702f5b7 at HEAD 93b6ea10; reviewed_sha (branch base) 4e25360c.

## codex-review-spec-1 (openai, lens: spec) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: NEEDS_REVISION
  ambiguity: NEEDS_REVISION
  inconsistency: NEEDS_REVISION
  incorrect-fact: NEEDS_REVISION
  missing-population: PASS
  spec-conformance: PASS_WITH_NOTES
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: NEEDS_REVISION
  user-judgment-leak: PASS
findings:
  - severity: fatal
    dimension: inconsistency
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:19"
    text: "The proposed intent-only HEAD cannot both pass and leave every other push rule unchanged. The current push path needs a review.json selected by check_review_only_head, and push.reviewed-sha requires that record's reviewed_sha to equal HEAD^. A post-merge close commit has no review.json in HEAD and its parent is the merged trunk commit, not the pre-merge reviewed commit. The specification therefore permits incompatible implementations, including silently bypassing review-dependent rules."
    fix: "Define the complete close-commit push path: how the change id and existing review record are located, exactly which push rules remain applicable, and what replaces or scopes push.reviewed-sha for this lifecycle transition. Require regression tests proving the close shape passes while an extra content change, mode change, rename, malformed status, missing review record, or unresolved finding still blocks."
  - severity: fatal
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:35"
    text: "The cited anchor at test_loom_checker_intake.py:385 is only the test declaration and does not support the claim that the test expects only intake.spec-pass. Lines 429–447 dynamically derive up to intake.spec-pass and intake.confirmed-behavior, while the current checker can additionally short-circuit on intake.confirmed."
    fix: "Replace the anchor with the full supporting span and state the actual dynamic oracle precisely. If the PR #781 failure is required evidence, cite a committed log or evidence artifact containing that exact failure."
  - severity: fatal
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:16"
    text: "REQ-6 says six carried nits but enumerates only five: R24-O2, R28-O2, and R30-O1 through R30-O3. The same wrong count appears in the intent constraint and spec boundary evidence."
    fix: "Change every occurrence from six to five, or identify and specify the missing sixth nit. Use complete repo-relative anchors for all five items."
  - severity: important
    dimension: omission
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:8"
    text: "The requirement says the full package command must be green, while Acceptance #2 names suites under both loom-code/scripts/ and scripts/ without defining the exact local and CI commands. An implementer cannot tell which commands constitute complete verification."
    fix: "Name the exact package-test commands and the CI workflow or jobs that must run them, preserving Acceptance #2's coverage of both directories."
  - severity: important
    dimension: ambiguity
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:19"
    text: "\"the diff of that file is exactly one line\" does not define whether one replaced line means one deletion plus one addition, nor whether mode-only metadata, rename status, duplicate status fields, or missing final newline are allowed."
    fix: "Specify the check in Git terms: one non-renamed regular intent file, unchanged mode, exactly one removed status line and one added status line, no other content or metadata change, a unique status field, and the required confirmed-to-closed grammar."
notes: []```

## sonnet-review-spec-1 (anthropic, lens: spec) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
dimension_scores: {omission: PASS, ambiguity: PASS, inconsistency: NEEDS_REVISION, incorrect-fact: NEEDS_REVISION, missing-population: PASS, spec-conformance: NEEDS_REVISION, design-conformance: "N/A — no DESIGN.md", principles-conformance: PASS_WITH_NOTES, user-judgment-leak: PASS}
findings:
  - {id: spec-S1, severity: important, dimension: inconsistency, anchor: "spec.md :: \"push.review-only-head gains a second accepted shape\"", text: "The intent's Constraints say no rule semantics change; a second accepted shape for review-only-head is a semantics change the spec's own Boundary line concedes.", fix: "Reconcile: express it as a declared shared table entry, or take the conflict back to the user as a one-line consequence question."}
  - {id: spec-S2, severity: important, dimension: incorrect-fact, anchor: "spec.md :: \"REQ-6 … → Acceptance #2\"", text: "No Acceptance line names the carried nits; the suite is green without them. The obligation is a Constraint.", fix: "Trace REQ-6 to Constraints, or add an Acceptance line with the user's sign-off."}
  - {id: spec-S3, severity: nit, dimension: incorrect-fact, anchor: "spec.md :: \"is_host_plumbing() (loom_checker.py:401)\"", text: "The predicate is `_is_host_plumbing` at :400.", fix: "Correct symbol and line."}
notes:
  - "All other anchors verified exactly (ship SKILL.md:326-336, loom_checker.py:1557/:2085/:2095/:455, manifest.yaml:85, templates/intent.md:7, the five nit anchors)."
  - "principles-conformance PASS_WITH_NOTES: the extension is diff-recomputed, so PRINCIPLES itself is not breached; the conflict is with the intent's stricter Constraint."
```

## Blind run (cold read) — sonnet-coldread-spec-1: 3 guesses, 1 anchor mismatch → evidence/spec-coldread-r1.md
## Adversarial (red-team) — sonnet-redteam-spec-1: NEEDS_REVISION, 3 fatal / 3 important → evidence/spec-redteam-r1.md

## Round outcome: NEEDS_REVISION. Findings opened as spec-C1..C5 (codex), spec-S1..S3 (sonnet), spec-R1..R7 (red team), spec-B1..B3 (cold read).
