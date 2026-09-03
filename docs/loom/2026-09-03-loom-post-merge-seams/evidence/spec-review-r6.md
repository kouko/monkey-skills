# Spec review round 6 — verdicts (spec v7, blob 9a6f71e, HEAD e6f3062c)

## codex-review-spec-6 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: PASS
  ambiguity: NEEDS_REVISION
  inconsistency: NEEDS_REVISION
  incorrect-fact: NEEDS_REVISION
  missing-population: PASS
  spec-conformance: PASS
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: NEEDS_REVISION
  user-judgment-leak: PASS
findings:
  - severity: fatal
    dimension: inconsistency
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:6"
    text: "REQ-1 states unconditionally that `closed` reaches the trunk only by the merge, but the Design decision at line 19 says this holds only if the trunk receives only merges and explicitly records that an admin can push `closed` directly to `main` without review or merge. Thus v7 still presents a guarantee that its own stated boundary disproves; the two tightened rules cannot enforce it when the client-side push gate is bypassed."
    fix: "Qualify the line-6 sentence with the same assumption as line 19, for example: `under the stated assumption that the trunk receives only merges, closed reaches the trunk only by the merge`; retain the direct-admin-push residual and out-of-scope boundary."
notes:
  - "spec-C11: closed — spec.md:6 says `push.reviewed-sha` requires every latest-round non-spec verdict to carry `sha` resolving to the same object as `reviewed_sha`, and `push.review-only-head` recomputes that the close commit changes exactly the intent status line."
  - "spec-R19: closed — spec.md:8 states that a locally fabricated `main` or `origin/main` ref is indistinguishable from a fetched ref because case (ii) verifies no fetch provenance."
  - "spec-R20: closed — spec.md:21 requires identification by the invoked path using `Path(__file__)` without `.resolve()` and states that a mode-120000 plumbing entry is never exempt."
  - "Round-5 unnamed-candidate-list nit: closed — spec.md:8 names `REOPEN_TRUNK_CANDIDATES = (\"origin/main\", \"main\", \"origin/master\", \"master\")` and distinguishes it from `TRUNK_CANDIDATES`."
  - "Round-5 cold-read G1 mode-only: closed — spec.md:21 requires blob-and-mode comparison through `git show --raw`, so a mode-only change fails, and explicitly denies exemption to symlinks."
  - "REQ-1 through REQ-6 trace one-to-one to Acceptance lines 1 through 6, and every Acceptance line has a corresponding REQ."
  - "All requested Current state evidence anchors resolve and support their claims: ship/SKILL.md:326-336; loom_checker.py:389-400, :791, :825-835, :1557, :2085, :2095; manifest.yaml:85; templates/intent.md:7; test_loom_checker_intake.py:385-447. The current checker reports 27 rule ids."
  - "The tightenings identify the field (`verdicts[].sha`), comparison (resolved git object id equality), commit (`HEAD^`, the reviewed close commit), and status-line regex source sufficiently for implementation and tests. They add no rule or waiver."
  - "No DESIGN.md exists. No user is assigned a quality-catching role; the remaining user action is pressing merge."

```

## sonnet-review-spec-6 (anthropic) — PASS

```yaml
verdict: PASS
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: PASS
  incorrect-fact: PASS
  missing-population: PASS
  spec-conformance: PASS
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: PASS
  user-judgment-leak: PASS
findings: []
notes:
  - "Round-5 opens: spec-C11 (fatal) closed at spec.md:6 — push.reviewed-sha now ties every non-spec verdict's sha to reviewed_sha as a git-object-id compare, and push.review-only-head mechanically recomputes that a closed-introducing commit touches exactly its status line; verified against the current (unpatched) check_verdicts at loom_checker.py:2278-2302."
  - "spec-R19 and spec-R20 both closed at spec.md:8 and :21 with the exact fix the redteam-r5 finding asked for."
  - "Redteam-r5 nit (3) closed via REOPEN_TRUNK_CANDIDATES at spec.md:8; cold-read G1 (mode-only) closed via the explicit 'blob and mode' sentence at spec.md:21."
  - "--list-rules confirmed 27 rule ids; push.reviewed-sha / push.review-only-head are existing ids (tightened, not added)."
```
