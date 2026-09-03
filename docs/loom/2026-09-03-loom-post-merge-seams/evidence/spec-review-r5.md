# Spec review round 5 — verdicts (spec v6, blob 897f3a9, HEAD de4517d3)

## codex-review-spec-5 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
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
  principles-conformance: NEEDS_REVISION
  user-judgment-leak: PASS
findings:
  - severity: fatal
    dimension: principles-conformance
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:6"
    text: "REQ-1 knowingly makes an unverified close-commit review part of every ship: check_reviewed_sha ties reviewed_sha only to HEAD^, while check_verdicts accepts the latest passing verdict round without comparing verdicts[].sha to reviewed_sha. An agent can therefore move reviewed_sha to an unreviewed close commit while retaining verdicts for an older delta. Merely disclosing that this is enforced by station prose does not conform to PRINCIPLES.md Non-negotiable 3 or the Won't-do prohibition on prose-only gates; it lets unreviewed behavior reach trunk while all mechanical push checks pass. The gap is genuinely pre-existing in loom_checker.py:1670-1690 and :2265-2302, but v6 institutionalises it once per ship rather than preserving its former occasional exposure."
    fix: "Revise the constraint and close this in the present change: fold a verdict-to-reviewed_sha comparison and the required close-commit diff-shape recomputation into an existing checker rule, or choose a close flow that creates no commit after the mechanically verified branch-end checkpoint. Do not defer the only enforcement to a follow-up intent."
notes:
  - "spec-S8: closed — spec.md:21 states that a deliberately older loaded plugin remains its own older canonical, names the absent freshness check, and assigns the residual to a follow-up intent."
  - "spec-R14: closed — spec.md:6 says the design institutionalises the pre-existing verdict-sha gap and moves exposure from occasional to once per ship."
  - "spec-R15: closed — spec.md:19 makes the merge-proof claim conditional on trunk receiving only merges and states that enforce_admins is off, approvals are zero, and direct admin pushes are not caught."
  - "spec-R16: closed — spec.md:8 restricts the reopen lookup to origin/main, main, origin/master, and master, excludes @{upstream}, distinguishes absent from stale trunk state, and states the no-trunk-plus-rewritten-ancestry residual."
  - "spec-R17: closed — spec.md:21 gives the contract-package location separately for plugin/repo and Codex scaffold layouts, cites codex_scaffold.CONTRACT_COPY, and says the Codex-copy exclusion runs before the contract lookup."
  - "spec-R18: closed as disclosure, but the disclosed design still fails principles-conformance — spec.md:6 explicitly names the one-line-delta statement as a reviewer claim and its tension with the Won't-do line and Non-negotiable 3."
  - "spec-B4: closed — spec.md:16 records R28-O2 as moot because its probe was deleted and phrases R30-O1 as the required fix: pin literal 5."
  - "G1: closed — spec.md:6 explicitly says the ship station invokes loom-code:review again with scope branch-end for the close commit."
  - "G2: closed — spec.md:10 says a deleted entry remains in commit_paths() with no blob at the commit and therefore fails comparison."
  - "G3: closed — spec.md:16 identifies the former R28-O2 probe as deleted and requires only a moot record."
  - "G4: closed — spec.md:16 distinguishes the current self-derived oracle from the target fix that pins literal 5."
  - "All Current state evidence anchors were opened. ship/SKILL.md:326-336, loom_checker.py:389-400, :791, :825-835, :1557, :2085, :2095, manifest.yaml:85, templates/intent.md:7, and test_loom_checker_intake.py:385-447 resolve and support their stated current-state claims."
  - "The -G plus trunk-copy reopen design is sound within its expressly stated boundary: the grammar-derived -G detects removal of a reachable closed line, and the independently selected trunk copy covers rewritten ancestry only when a sufficiently current trunk ref exists."
  - "A closed line can reach trunk without review and merge through a direct privileged push; spec.md:19 now states that exact assumption and this repo's enforce_admins limitation instead of presenting merge provenance as guaranteed."
  - "REQ-1 through REQ-6 trace one-to-one to Acceptance lines 1 through 6, and no Acceptance line lacks a corresponding requirement."
```

## sonnet-review-spec-5 (anthropic) — PASS

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
  - "Round-4 still-open ids all close in v6 (spec-S8, R14, R15, R16, R17, R18, B4), each verified against verbatim text; cold-read G1-G4 also close."
  - "Independently re-derived: check_verdicts/scored_verdicts/latest_round (loom_checker.py:2265-2299) never compare a per-verdict sha to reviewed_sha and check_reviewed_sha (:1670) compares only the scalar field to HEAD^ — REQ-1's 'pre-existing gap' claim is accurate. TRUNK_CANDIDATES (:376) includes @{upstream} for branch_base, so REQ-2's contrast is correct. codex_scaffold.CONTRACT_COPY and the repo's own .codex/hooks/contract/ tree confirm the R17 per-host framing."
  - "The two vendors disagree on whether a disclosed prose-enforced round conforms to PRINCIPLES.md (Codex: fatal; this leg: PASS, the same trade-off every reviewed commit rests on). Recorded whole, not averaged."
```
