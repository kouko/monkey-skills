# Spec review round 2 — verdicts (spec v3, blob 5e7a104, HEAD 82b33ce5)

## codex-review-spec-2 (openai) — NEEDS_REVISION

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
  spec-conformance: NEEDS_REVISION
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: NEEDS_REVISION
  user-judgment-leak: PASS
findings:
  - severity: fatal
    dimension: inconsistency
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:21"
    text: "REQ-3 promises that altered host-plumbing content counts as gate work, but on Codex the running checker and its canonical sibling files are the repository copies being tested. The checker, git_exec.py, and contract/<rel> comparisons can therefore compare each committed path with itself, not merely loom_checker.py as the spec states. Modified contract or sibling code can remain exempt from trailer duty. This contradicts REQ-3 and leaves the round-1 R7 escape open on Codex."
    fix: "Define a non-self-referential canonical source or authenticated digest for every exempted Codex copy, or explicitly scope REQ-3 to hosts where an external canonical package exists and retain trailer duty for Codex copies. Add negative acceptance cases for modified checker, git_exec.py, shim, contract file, added contract file, deletion, and mode-only changes."
  - severity: important
    dimension: ambiguity
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:7"
    text: "REQ-2 calls closed terminal, but the specified behavior only blocks intake while the file currently says closed. Nothing requires rejection of a later closed-to-confirmed edit, after which the old change can enter write-plan again."
    fix: "Specify and test the repository transition rule that prevents closed-to-confirmed reopening, or narrow the requirement from terminal to 'intake blocks while status is closed' and reconcile the new-intent message."
  - severity: important
    dimension: omission
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:20"
    text: "The shared status regex does not say that a closed date must pass is_real_date(). An implementation may accept an impossible or future date while still satisfying the stated grammar and intake behavior."
    fix: "Require the closed date to pass the same real-date validation as confirmed, define whether future real dates are allowed, and add boundary tests."
  - severity: important
    dimension: spec-conformance
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:16"
    text: "REQ-6 explicitly traces only to a Constraint and says that no Acceptance line names it. This fails the requested bidirectional REQ-to-Acceptance mapping, so the five carried fixes can be omitted while all five Acceptance lines pass."
    fix: "Add an Acceptance line covering all five named nit fixes, or remove REQ-6 from Requirements and keep it solely as a Constraint with an explicit verification obligation."
  - severity: important
    dimension: spec-conformance
    anchor: "docs/loom/intent/2026-09-03-loom-post-merge-seams.md:23"
    text: "Acceptance #3 tests only genuine scaffold output. It does not exercise REQ-3's converse guarantee that noncanonical content under a plumbing path retains trailer duty, which is the behavior intended to close the original escape."
    fix: "Extend Acceptance #3 with negative cases showing that altered, added, deleted, and mode-changed plumbing entries are not exempt."
notes:
  - "spec-C1: closed — spec.md:6 and :19 replace the special close-commit HEAD shape with the ordinary reviewed-sha plus review-only-HEAD sequence."
  - "spec-C2: closed — spec.md:37 now cites test_loom_checker_intake.py:385-447 and accurately describes its dynamic intake.spec-pass and intake.confirmed-behavior oracle."
  - "spec-C3: closed — spec.md:15-16 and the intent Constraint consistently identify five nits."
  - "spec-C4: closed — spec.md:8 names the exact package command and CI job."
  - "spec-C5: closed — the special one-line push shape was removed; spec.md:6 uses the existing review-only commit gate."
  - "spec-S1: closed — spec.md:19 and :30 reject the second push.review-only-head shape, preserving unchanged push-rule semantics."
  - "spec-S2: still-open — spec.md:16 correctly points REQ-6 to the Constraint but expressly admits that no Acceptance line covers it."
  - "spec-S3: closed — spec.md:21 names _is_host_plumbing at loom_checker.py:400."
  - "spec-R1: closed — spec.md:19 makes the reviewed branch merge, rather than the PR-number text, the carrier of closed onto trunk and explicitly rejects PR-number verification."
  - "spec-R2: still-open — spec.md:20 requires a shared regex but never requires is_real_date validation or defines future-date handling."
  - "spec-R3: closed — spec.md:6 puts the close commit beneath the existing review-only HEAD, whose implementation uses --no-renames."
  - "spec-R4: closed — spec.md:6 requires a dedicated close commit followed by review and the unchanged push gate."
  - "spec-R5: closed — spec.md:6 requires the close commit to be reviewed and re-pins reviewed_sha to it."
  - "spec-R6: still-open — spec.md:7 says closed is terminal, but :20 only blocks intake while the current status remains closed."
  - "spec-R7: still-open — spec.md:21 makes comparisons content-bound for an external checker, but Codex uses the repository copies as their own comparison oracle."
  - "spec-B1: closed — spec.md:6 gives the exact close-intent commit subject."
  - "spec-B2: closed — spec.md:8 gives the literal package-test command."
  - "spec-B3: closed — spec.md:14 names each plugin.json version and the installed cache path, then uses --list-rules to observe the closed grammar."
  - "All requested current-state anchors resolve and support their historical-state claims: ship/SKILL.md:326-336, loom_checker.py:791, :825-835, :1557, :2085, :2095, manifest.yaml:85, templates/intent.md:7, and test_loom_checker_intake.py:385-447."
  - "Under the specified non-bypass workflow, a closed line cannot reach trunk without its close commit being covered by a review-only HEAD and the branch being merged. The PR-number annotation itself is not verified."
  - "PRINCIPLES.md conformance fails at principle 3 for REQ-3 on Codex: comparison against the mutable running copy does not independently establish canonical scaffold content."```

## sonnet-review-spec-2 (anthropic) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
rereview_of: {spec-C1: closed, spec-C2: closed, spec-C3: closed, spec-C4: closed, spec-C5: closed, spec-S1: closed, spec-S2: closed, spec-S3: closed, spec-R1: closed, spec-R2: still-open, spec-R3: closed (moot), spec-R6: still-open, spec-R7: closed (content-bound), spec-B1: closed, spec-B2: closed, spec-B3: closed}
dimension_scores: {omission: NEEDS_REVISION, ambiguity: PASS, inconsistency: NEEDS_REVISION, incorrect-fact: PASS_WITH_NOTES, missing-population: PASS, spec-conformance: PASS_WITH_NOTES, design-conformance: "N/A — no DESIGN.md", principles-conformance: PASS_WITH_NOTES, user-judgment-leak: PASS}
findings:
  - {id: spec-S4, severity: important, dimension: omission, anchor: "spec.md:7", text: "closed date never routed through is_real_date (spec-R2 still open).", fix: "State that the closed branch calls is_real_date like confirmed."}
  - {id: spec-S5, severity: important, dimension: inconsistency, anchor: "spec.md:7", text: "'closed is terminal' claimed but no rule blocks closed→confirmed (spec-R6 still open).", fix: "Add the transition rule or state the gap as accepted and drop 'terminal'."}
  - {id: spec-S6, severity: nit, dimension: incorrect-fact, anchor: "spec.md:8", text: "CI runs the package command with -v, spec says -q.", fix: "Match CI verbatim or say only the exit code must agree."}
notes:
  - "All anchors re-verified exact; round-1 id count is 16 (R4/R5/R8 never minted)."
```

## Cold read — sonnet-coldread-spec-2: zero guesses → evidence/spec-coldread-r2.md
## Red team — sonnet-redteam-spec-2: NEEDS_REVISION (1 fatal: Codex self-comparison incl. git_exec/contract; important: R2, R4/R5 close-commit contents unchecked by machine, CI never runs the push gate, "running checker" across two cached versions) → evidence/spec-redteam-r2.md

## Round outcome: NEEDS_REVISION. New ids: spec-C6 (Codex self-referential comparison, fatal), spec-C7 (REQ-6 needs an Acceptance line), spec-C8 (Acceptance #3 negative cases), spec-S4..S6, spec-R8 (close-commit contents not machine-checked; user's PR diff is the backstop), spec-R9 (CI does not run the push gate), spec-R10 (running checker across cached versions).
