# Spec review round 7 — verdicts (spec v8, blob 1e02f71, HEAD d7fd6d44)

## codex-review-spec-7 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: PASS
  ambiguity: NEEDS_REVISION
  inconsistency: NEEDS_REVISION
  incorrect-fact: PASS
  missing-population: PASS
  spec-conformance: NEEDS_REVISION
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: NEEDS_REVISION
  user-judgment-leak: PASS
findings:
  - severity: fatal
    dimension: inconsistency
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:19"
    text: "spec-R21 is still open. REQ-1 closes the scope-label escape by requiring every verdict of the latest round to carry a commit sha with no scope exemption, but Design decision 1 still says `verdicts[].sha` is required only on non-`spec` scopes. An implementer could follow line 19 and preserve the exact self-reported `scope: spec` bypass that REQ-1 and Acceptance #1 require the checker to reject. That would also violate PRINCIPLES.md Non-negotiable 3 by letting an agent-written scope claim control the gate."
    fix: "Replace the line-19 sentence with the line-6 rule: every verdict in the latest push-riding round requires `sha`, without a scope exemption. Explain separately that historical spec-only rounds use `spec_sha` and cannot be the latest round used by push."
notes:
  - "spec-C12: closed — spec.md:6 says: `under the stated assumption that the trunk receives only merges (Design decision 1), closed reaches the trunk only by the merge`; spec.md:19 retains the direct-admin-push residual and labels it out of scope."
  - "spec-R21: still-open — spec.md:6 says `There is no exemption by scope`, but spec.md:19 contradicts it with `verdicts[].sha is required only on non-spec scopes`."
  - "spec-R22: closed — spec.md:6 requires `HEAD^^` to touch only `review.json` and its historical `review.json` to record a `reviewed_sha` resolving to `HEAD^^^`, preventing an uncheckpointed interposed commit."
  - "Cold-read G1: closed — spec.md:6 selects exactly the latest round returned by `scored_verdicts()` and requires failures to name the rule id, offending field or commit, and expected value."
  - "Cold-read G2: closed — spec.md:6 says the checker collects every failure rather than stopping at the first, so both tightened rules report when both faults are present."
  - "Cold-read G3: closed — spec.md:8 requires the `git log -G` pattern to be rendered from the closed alternative of `STATUS`, with the same optional whitespace stripped by the frontmatter parser."
  - "Cold-read G4: closed — spec.md:10 identifies `codex_scaffold.plugin_version()` and its `.claude-plugin/plugin.json` source as the running checker version used for the stamp comparison."
  - "Cold-read G5: closed — spec.md:6 specifies `git diff -U0 HEAD^^ HEAD^ -- <path>`, exactly one removed and one added `status:` line, the shared closed-status regex, and the required failure-message contents."
  - "Every REQ-1 through REQ-6 traces one-to-one to Acceptance lines 1 through 6 and vice versa, except that the contradictory line-19 scope exemption would undercut Acceptance #1."
  - "All Current state evidence anchors were opened and support their claims: ship/SKILL.md:326-336; loom_checker.py:389-400, :791, :825-835, :1557, :2085, :2095; manifest.yaml:85; templates/intent.md:7; test_loom_checker_intake.py:385-447; and the named codex_scaffold symbols. The current checker lists 27 rule ids."
  - "No DESIGN.md exists. The spec adds no rule id or waiver, and it assigns the user only the merge action, not responsibility for catching quality defects."
```

## sonnet-review-spec-7 (anthropic) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: PASS
  ambiguity: PASS_WITH_NOTES — failure-message text of the two tightened rules specified by shape only, like existing rules
  inconsistency: NEEDS_REVISION
  incorrect-fact: PASS
  missing-population: PASS
  spec-conformance: PASS
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: NEEDS_REVISION
  user-judgment-leak: PASS
findings:
  - severity: fatal
    dimension: inconsistency
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:19 :: \"`verdicts[].sha` is required only on non-`spec` scopes because a spec round reviews a blob (`spec_sha`), not a commit\""
    text: "REQ-1 (spec.md:6) removed the scope-based exemption entirely (spec-R21), but Design decision 1 still states the old rule verbatim; an implementer building from the Design decision reproduces the exploitable scope-label exemption. v8 gives two contradictory specifications of the same rule."
    fix: "Rewrite the line-19 clause to match REQ-1: sha required on every verdict of the latest round regardless of scope; a spec-only round records spec_sha, not sha, and is never a round a push can ride on."
notes:
  - "spec-C12 closed (merge-proof sentence qualified at spec.md:6). spec-R22 closed (HEAD^^ must be a checkpoint). Cold-read G1b/G2/G3/G4/G5a/G5b closed; G1a/G5c (message wording) remain by shape only."
  - "All Current state evidence anchors opened and confirmed at HEAD; --list-rules prints 27 ids; git log 4e25360c..HEAD is docs-only."
  - "principles-conformance NEEDS_REVISION solely because of the same inconsistency (a self-reported scope label controlling a gate, Non-negotiable 3)."
```
