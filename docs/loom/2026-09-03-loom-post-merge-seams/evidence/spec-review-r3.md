# Spec review round 3 — verdicts (spec v4, blob 035cf38, HEAD cc5a67a9)

## codex-review-spec-3 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: PASS
  incorrect-fact: PASS_WITH_NOTES
  missing-population: PASS
  spec-conformance: NEEDS_REVISION
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: NEEDS_REVISION
  user-judgment-leak: NEEDS_REVISION
findings:
  - severity: fatal
    dimension: principles-conformance
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:6"
    text: "REQ-1 says a docs-typed file smuggled into the close commit is caught only by the user reading the PR diff. That directly contradicts PRINCIPLES.md:5, :9, and :15: this user cannot judge diff quality, quality must come from machines, and the workflow must not ask the user to review a diff for quality. Consequently, a closed line and unrelated unreviewed content can reach trunk when the client-side push gate is bypassed and the user merges."
    fix: "Require the ordinary review station to review the close commit before producing the review-only HEAD: at least two fresh-context reviewers must inspect its complete delta, with the required blind run and adversarial pass recorded and re-pinned. Remove the claim that the user's PR-diff reading is the quality backstop."
  - severity: important
    dimension: spec-conformance
    anchor: "docs/loom/intent/2026-09-03-loom-post-merge-seams.md:23"
    text: "spec-C8 remains partly open. REQ-3 promises negative behavior for altered, added, deleted, and mode-changed plumbing entries, but Acceptance #3 covers only changing one byte or adding one file. Deletion and mode-only changes can therefore be omitted while every Acceptance line passes."
    fix: "Extend Acceptance #3 to require the same push-gate rejection for a deleted canonical plumbing file and a mode-only change."
  - severity: nit
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:8"
    text: "The sentence saying deletion makes this 'a different file with no closed ever recorded' is inaccurate for the specified path-history command: deleting and recreating the same path does not erase earlier commits from `git log ... -- <intent path>`."
    fix: "Replace that clause with the precise boundary: the reopen check holds while the commit that introduced `status: closed` remains in the current branch's ancestry; only rewritten ancestry can remove that evidence."
notes:
  - "spec-R2: closed — REQ-2 says: `the date must pass the same is_real_date() the confirmed branch uses (a real calendar date; the checker does not compare it to today's clock)`."
  - "spec-R6: closed — REQ-2 says: `intake.confirmed also blocks when the intent file's history on the current branch ... shows a closed status while the current status is anything else`."
  - "spec-C6: closed — REQ-3 says: `When the checker doing the push is the copy ... there is no canonical to compare against and no exemption applies`."
  - "spec-C7: closed — REQ-6 now ends with `Acceptance #6`, and intent Acceptance #6 names all five carried nits."
  - "spec-C8: still-open — intent Acceptance #3 says only `把副本裡任一檔改一個字（或多放一個檔）`; it does not cover deletion or mode-only changes promised by REQ-3."
  - "spec-S4: closed — the spec says `the closed date goes through is_real_date() in the same branch as confirmed`."
  - "spec-S5: closed — the spec says `The reopen check reads the intent file's git history on the branch ... a recompute, not a flag`."
  - "spec-S6: closed — REQ-2 identifies CI's same-path invocation with `-v` and says only the exit code must agree."
  - "spec-R8: closed as a disclosed residual, but it exposes the fatal principles violation above — REQ-1 says `the close commit's own contents are not machine-checked beyond trailer duty`."
  - "spec-R9: closed as a disclosed residual — REQ-1 says `CI does not run loom_checker.py push (the push gate is client-side)`."
  - "spec-R10: closed — the Design decision says the canonical is whichever checkout the hook invoked, and a copy stamped with another version fails comparison and owes a trailer."
  - "All Current state evidence anchors were opened. ship/SKILL.md:326-336, loom_checker.py:791, :825-835, :1557, :389-400, :2085, :2095, manifest.yaml:85, templates/intent.md:7, and test_loom_checker_intake.py:385-447 resolve and support their historical-state claims; the CI workflow confirms the package suite uses `-v`."
  - "There is no DESIGN.md, so design-conformance is N/A."
  - "The content-bound plumbing exemption is sound where the running checker has an external canonical source. On Codex the exemption is disabled, so altered plumbing remains trailer-bearing; the explicitly recorded gap is that genuine scaffold refresh and first-contact scaffold commits also retain trailer duty."
```

## sonnet-review-spec-3 (anthropic) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: spec
reviewed_sha: 4e25360c
rereview_of:
  spec-R2: closed — spec.md:8 "the date must pass the same `is_real_date()` the `confirmed` branch uses"
  spec-R6: closed (original hand-edit attack) — spec.md:8 terminal check blocks a `closed→confirmed` hand-edit on a branch that carries the closed commit; see new finding F2 for a scope gap this doesn't cover
  spec-C6: closed — spec.md:6/21 Design decision: on Codex ("the checker doing the push is the copy") "no canonical exists, and the exemption is off ... every plumbing edit keeps trailer duty"
  spec-C7: closed — spec.md REQ-6 "→ Acceptance #6"; intent.md Acceptance #6 added
  spec-C8: closed — intent.md Acceptance #3 "而把副本裡任一檔改一個字（或多放一個檔）再 commit，同一條規則照樣擋"
  spec-S4: closed — spec.md:8 (same sentence as R2)
  spec-S5: closed (as scoped) — spec.md:8 terminal rule added; see F2 for an uncovered case
  spec-S6: closed — spec.md:8 "the declared package command ... `-q` passes locally, and the CI job ... same paths with `-v`; only the exit code must agree"
  spec-R8: closed — spec.md:6 "Two residuals are stated, not hidden..."; see F1 — stating it does not resolve a PRINCIPLES.md conflict newly checked this round
  spec-R9: closed — spec.md:6 "CI does not run `loom_checker.py push` (the push gate is client-side...)"
  spec-R10: closed — Design decision, "Two cached plugin versions" paragraph
dimension_scores:
  omission: PASS_WITH_NOTES — the branch-fork reopen gap (F2) is an omission not stated as a residual
  ambiguity: PASS
  inconsistency: NEEDS_REVISION — F2, REQ-2's absolute "terminal" claim vs. the narrower guarantee its own mechanism delivers
  incorrect-fact: PASS — all cited anchors verified to exist and say what the spec claims
  missing-population: PASS
  spec-conformance: PASS_WITH_NOTES — REQ-6→Acceptance #6 and Acceptance #3's negative case are both present as required by round 2
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: NEEDS_REVISION — F1, REQ-1's close-commit residual contradicts PRINCIPLES.md Non-negotiables 1 and 2
  user-judgment-leak: PASS — Merge is explicitly user-decided
findings:
  - severity: fatal
    dimension: principles-conformance
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:6"
    text: "REQ-1's stated residual — 'the close commit's own contents are not machine-checked beyond trailer duty (a docs-typed file smuggled into it is caught only by the user reading the PR diff before pressing merge — the user is the merge gate by their own decision)' — contradicts two ordered Non-negotiables in PRINCIPLES.md: #1 ('never a question that requires reading code') and #2 ('Quality comes from machines, not from the user's sign-off'). The design explicitly assigns catching a real defect class (smuggled non-trailer-duty content) to the user's own diff read at merge time. Stating the gap (as round 2's spec-R8 asked) documents it but does not make it conform — PRINCIPLES.md is new ground truth this round and neither round-2 reviewer scored this sentence against it."
    fix: "Add a machine check for the close commit's shape — e.g. a rule asserting the close commit's diff touches only the intent file's `status:` line — instead of relying on the user's PR-diff read as the backstop."
  - severity: important
    dimension: inconsistency
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:7"
    text: "REQ-2 headlines 'closed is terminal' and its body's own hedge already scopes the guarantee to branches whose ancestry includes the close commit. A branch checked out from a point on trunk before the close merged (or any ref that never carries that commit) has an empty `git log -S'status: closed'` result and a current status of `confirmed`, so `intake.confirmed` passes and write-plan can proceed on what is, on trunk, a closed change. The follow-on sentence answers only the history-rewrite attack, not the never-carried-it case, so 'terminal' overstates what the mechanism (which only ever inspects the current checkout's own history) can deliver."
    fix: "Either state this as a third accepted residual next to R8/R9, or extend the terminal check to also read the intent file's status from the tracking remote's default branch when reachable (e.g. `git show origin/main:<path>`) with a stated no-network fallback, and adjust REQ-1's Acceptance #1 wording to acknowledge the scope."
notes:
  - "All 8 Current-state-evidence anchors and all round-2 open-id resolutions were independently re-verified against the live files at HEAD cc5a67a9."
  - "REQ-3's Codex carve-out does not contradict Acceptance #3: the Acceptance line is explicitly scoped to the Claude Code side."
  - "'the checker doing the push is identified by `Path(__file__).resolve()`' is a genuine recompute, not a claim taken from repo content."
```
