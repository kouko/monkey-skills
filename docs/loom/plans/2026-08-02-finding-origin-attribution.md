# Plan: reviewer findings carry a quote-gated origin

Source brief: docs/loom/specs/2026-08-02-finding-origin-attribution.md
Total tasks: 6
Critical-path depth: 5 (≤5) — Task 1 → 2 → 3 → 5 → 6; Task 4 is a depth-3 leaf
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-02, round 4) — 15/15, no gaps; supersedes the round-3 PASS that the round-3-note amendment made stale

## Notes

- **Round-1 re-cut.** The plan-document-reviewer's first round falsified this
  plan's premise, not merely its wording: the previous version shipped the
  contract on `code-quality-reviewer` because that agent caught the arc's
  eighth-site defect — but per-task review **mints no marker**, so the chosen
  enforcement point never sees its output. The brief's §Smallest End State was
  re-cut before this plan was rewritten; both now name `code-reviewer` as the
  marker-validated agent and state the per-task asymmetry explicitly. Three
  further round-1 gaps (shared-validator blast radius, sha-unavailable-at-
  validation, `requesting-code-review` §Verdict structure being the
  whole-branch schema) are addressed by Tasks 1, 2 and 5 respectively.

- **Round-2 fixes (2026-08-02), applied before this round-3 dispatch.** Four
  gaps and two advisory notes, all closed in this document rather than in a
  dispatch packet (a packet is ephemeral; every later gate reads only this
  file). (a) Task 1's RED was already GREEN today — re-cut to the code-arm case
  that fails now, with the docs-arm case kept as a *named* GREEN regression
  assertion so its discriminating power is not lost. (b) Task 2's RED was
  **unconstructible**: it posited a quote "present at HEAD but not at the
  reviewed sha", and there is no separate reviewed sha — re-cut to
  committed-content-vs-worktree, which fails today and passes only a `git show`
  implementation. (c) The dimension-gated requirement **failed open** — see
  §Pinned dimension partition's new fail-closed clause and Task 1's second named
  GREEN assertion. (d) A `head_sha` line citation was off by one (`:275` is
  `branch`), and its Intended slot repeated the wrong number as a *placement*
  instruction, which would have put the check between the two `_git` calls.
  Advisory 1 (Task 2's GREEN spanning two behaviours) is closed by naming a
  second RED, with the reason it stays one task written into that entry;
  advisory 2 (unreachable sha-unresolvable branch) is closed by pinning it to a
  helper-level unit test in GREEN.

  Fix (b) had a **wider blast radius than the finding named**: the same
  non-existent distinction was carried at eight sites — the brief's §Decision
  and §Resolved Questions 1, and this plan's §Pinned field grammar (which Tasks
  1, 3, 4 and 5 transcribe VERBATIM into shipped contracts), Task 2's title,
  Description, RED, GREEN and External surfaces. All eight are corrected;
  correcting only the two the reviewer pointed at would have shipped the wrong
  wording through the pin into three agent/skill files.

- **Round-3 amendment (2026-08-02) — the plan misstated a fact about its own
  target suite.** Round 3 returned PASS with a non-fatal note that the
  fail-closed clause's closing phrase — *"invisible to a suite whose fixtures
  all carry well-formed dimensions"* — reads as a claim that
  `test_loom_gate_markers.py`'s fixtures carry dimensions. They do not:
  independently measured, that file contains **zero** per-finding `dimension:`
  lines. Two consequences, both now written down rather than left for the
  implementer to hit: the clause is replaced by the measurement, and Task 1
  declares the fixture updates the fail-closed rule forces (every pre-existing
  finding fixture refuses to mint under it, and several tests assert a
  successful mint). Task 1's GREEN also gains the present-but-empty
  `dimension:` case, closing the one divergence round 3 flagged between the
  pin's "no *parseable* `dimension:`" and the naive "no `dimension:` line".

  Worth naming, because it is this arc's own subject matter: the phrase was a
  **plan fact that was wrong, actionable and silent** — introduced by the very
  edit that closed round 2's fail-open gap, and caught one stage before any code
  existed. The PASS it arrived with is superseded by this amendment (a change to
  a task's Description and GREEN is outside `writing-plans`' three-item
  no-re-review list), so the header returns to PENDING for round 4.

- **Change-folder binding: none, by recorded decision — not by a fresh skip.**
  Detection layer (ii) finds two non-archived folders
  (`docs/loom/2026-07-12-us-sec-primary-source-layer/`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake/`), which would normally trigger
  the `>1 → ask` branch. The user's decision not to bind either is already
  recorded — carried forward from
  `docs/loom/plans/2026-08-01-backlog-one-entry-per-file.md` §Notes and
  independently corroborated by
  `docs/loom/backlog/2026-07-26-loom-docs-two-stale-change-folders-belong-to-shipped-arcs.md`,
  which records both as belonging to shipped arcs. A documented decision beats
  re-asking. `check_scenario_coverage.py` does not apply — the input is a
  brainstorming brief.

- **§Pinned field grammar** — Tasks 1, 3, 4 and 5 each write this into a
  different artifact. Transcribe **VERBATIM from this pin**, never from each
  other and never re-derived:

  ```
  origin: none
  origin: <path> :: "<verbatim quote from that file>"
  ```

  `none` is the only permitted no-quote value (brief §Resolved Questions 2).
  The quote is matched against **committed content**, never against the working
  tree (brief §Resolved Questions 1) — an uncommitted edit must not be able to
  satisfy the check. There is **no separate "reviewed sha"** to prefer over
  HEAD: `_cmd_review_pass` resolves exactly one sha, `head_sha` from
  `rev-parse HEAD`, and stamps it into the marker, so the committed content at
  that sha *is* the reviewed content. Any wording in a transcribed copy that
  contrasts "the reviewed commit" with "HEAD" is stale — see the brief's dated
  correction under §Resolved Questions 1.

- **§Pinned dimension partition** — the discriminator Task 1 branches on.
  Transcribe VERBATIM; do not re-derive from the agent files, and do not
  extend either set without re-reviewing this plan:

  ```
  code-arm  : security, architecture, correctness, naming, tests, refactoring,
              cross-task-coherence, external-surface-grounding,
              principles-conformance, deliberate-simplification
  docs-arm  : omission, ambiguity, inconsistency, incorrect-fact,
              missing-population
  ```

  Verified disjoint 2026-08-02. A finding carrying a code-arm dimension must
  carry `origin:`; a docs-arm dimension is untouched.

  **Fail closed on everything else — the requirement is the default, the
  docs-arm exemption is the branch.** A finding whose block carries no parseable
  `dimension:` line, or a `dimension:` value in neither set, is treated as
  **code-arm**: it refuses without `origin:`. This is not a detail — today
  `_finding_problems` never reads a per-finding `dimension:` at all (the
  module's only `dimension` reads are the `dimension_scores:` block-header
  check), so an implementation that grants the requirement only on a successful
  lookup into the code-arm set lets **every** unparseable finding escape it
  silently. Measured on the target suite 2026-08-02:
  `loom-code/scripts/test_loom_gate_markers.py` contains **zero** per-finding
  `dimension:` lines — every finding fixture in it *is* the unparseable case —
  so a fail-open implementation would leave the whole existing suite green while
  requiring `origin:` of nothing at all, and nothing in the suite would ever
  surface the hole. Write the exemption as the explicit branch
  (`dimension:` parses AND is in the docs-arm set → skip) rather than letting
  fail-closed emerge from a lookup happening to miss. Same shape as the `class:`
  precedent, verbatim: *"A finding whose class is unclear is tagged
  `instruction` (fail closed)"*
  (`loom-code/skills/requesting-docs-review/SKILL.md:55`).

- **Kickoff decision — enforcement lands before prose.** Tasks 1-2 ship before
  Tasks 3-5. Shipping the contract first would promise a field nothing
  enforces, which is the defect class this change exists to make countable.
  Hard dependency, not preference.

- **Kickoff decision — the `validate` dry-run must fail loud, never silent.**
  `validate` takes no `--repo`, so it cannot verify a quote. It must say so in
  its output. A silent pass there would be a fail-open on exactly the
  pre-flight path `requesting-code-review` Step 3 tells reviewers to use.

- **Kickoff decision — the stop rule is pre-registered and must not be edited
  after data lands.** Brief §Resolved Questions 3: accumulate ≥40 code-arm
  findings; all-`none` ⇒ delete the field; ≥1 human-confirmed true origin ⇒
  keep; the hit RATE is explicitly not the test (expected base rate ≈7%,
  measured n=14 on the 2026-08-02 arc).

- **No CI file is edited.** `loom-code-ci.yml:98` already runs
  `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v` and its
  `paths:` filter covers `loom-code/**` and `scripts/**` (verified round 1).

## Task 1 — Require `origin:` on code-arm findings only

- Description: Extend `_finding_problems` in `loom_gate_markers.py` so every
  finding block must carry an `origin:` line valued either `none` or
  `<path> :: "<quote>"`, **except** a block whose `dimension:` both parses and
  falls in the docs-arm set, which is untouched. Write it in that direction —
  requirement first, exemption as the explicit branch — so a block with an
  absent or unrecognised `dimension:` refuses rather than escaping (§Pinned
  dimension partition, fail-closed clause). Grammar only: the quote is not yet
  checked against any file (Task 2). Transcribe both pins VERBATIM.
  **Declared collateral — not incidental drift.** No finding fixture in
  `test_loom_gate_markers.py` carries a `dimension:` line today (measured
  2026-08-02: zero occurrences in the file), so under the fail-closed rule every
  pre-existing fixture refuses to mint and every test asserting a successful
  mint goes red. Updating those fixtures — give each one a code-arm `dimension:`
  and an `origin:`, keeping each test's original intent — is part of this task,
  and the file is already in `Files touched` for exactly this reason.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
  - loom-code/skills/requesting-docs-review/SKILL.md
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_code_arm_finding_without_origin_refuses_to_mint` — a verdict whose finding carries a code-arm `dimension:` (`correctness`) and no `origin:` line must fail validation. This fails **today**: no `origin:` requirement exists, so that verdict validates clean and mints.
  - GREEN: `origin: none` and `origin: docs/loom/plans/x.md :: "seven call sites"` both validate; a bare path with no quote and a quote with no path both refuse; `python3 -m pytest loom-code/scripts/` passes. Two assertions inside GREEN are **named, and each is load-bearing on its own**:
    - `test_docs_arm_finding_without_origin_still_mints` — a verdict whose findings all carry docs-arm dimensions and no `origin:` must still validate. This is the discriminating case against over-reach: a naive **global** requirement satisfies every other criterion in this task and fails only this one, and shipping it would block every docs-only and mixed-branch push.
    - `test_finding_with_unparseable_dimension_refuses_without_origin` — three cases must **each** refuse without `origin:`: a finding block carrying no `dimension:` line at all, one carrying a value in neither pinned set, and one carrying a `dimension:` key with an empty or whitespace-only value. This is the discriminating case against under-reach (§Pinned dimension partition, fail-closed clause): an implementation that requires `origin:` only on a successful code-arm lookup passes every other criterion here and fails only this one. The third case is what keeps "no *parseable* `dimension:`" (the pin's wording) and "no `dimension:` line" (the naive reading) from diverging — a present-but-empty key must not read as a docs-arm exemption.
    - Pre-existing fixtures updated per the Description's declared collateral, each keeping its original assertion intent, and `python3 -m pytest loom-code/scripts/` green with them.
- External surfaces: none — stdlib `re`, matching the module's existing imports.
- Reuse-adequacy:
  - Observed: `_finding_problems` already splits the verdict into per-finding blocks and requires a path-like `where:` in each, refusing to mint otherwise — `read loom-code/scripts/loom_gate_markers.py:224-247`
  - Observed (blast radius): the docs arm mints the SAME marker through the same validator — `read loom-code/skills/requesting-docs-review/SKILL.md:56`
  - Observed (precedent): a per-finding field scoped by arm already ships, annotated inline — `read loom-code/skills/requesting-code-review/SKILL.md:150`
  - Intended: reuse the per-finding block split and the refuse-to-mint path unchanged; the `where:` check's **unconditional** shape does NOT carry over — `origin:` must carry an exemption branch keyed on the finding's own `dimension:` value, or it breaks every docs-only and mixed branch. Note the asymmetry with `where:`: because `where:`'s requirement is unconditional, its parse cannot fail open, whereas `origin:`'s can — so the exemption must be what the code tests for, never the requirement (§Pinned dimension partition, fail-closed clause).
- Dependencies: none
- Independent: false
- Brief item covered: "A finding carrying a code-arm dimension must carry `origin:`; one carrying a docs-arm dimension is untouched."

## Task 2 — Verify the quote against committed content, and say so when you cannot

- Description: Add quote verification as a distinct step in `_cmd_review_pass`,
  **after** `head_sha` resolves — not inside `validate_verdict_text`, which
  runs before the sha exists and is also reachable from a subcommand that has
  no repo. For each finding whose `origin:` names a path and quote, read that
  path **out of the commit** (`git show <head_sha>:<path>`), never off disk, and
  refuse to mint unless the quote occurs, naming path, sha and quote in the
  message. Distinguish "file absent at that sha" from "sha unresolvable" — the
  current git helper collapses both to `None`. On the `validate` dry-run path,
  state in the output that quote verification did not run.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_origin_quote_present_only_in_worktree_refuses_to_mint` — a temp repo whose **committed** content at `head_sha` lacks the quoted sentence while the on-disk file contains it must refuse to mint. This is the discriminating case: it fails today (nothing verifies quotes), it still fails a `Path.read_text()` implementation, and it passes only a `git show`-based one.
  - RED (second entry point, same contract): `loom-code/scripts/test_loom_gate_markers.py::test_validate_dry_run_reports_quote_verification_did_not_run` — `validate --verdict-file <f>` on a verdict carrying a quoted `origin:` must print that quote verification did not run. Fails today: the subcommand is silent about it. **Why this stays inside Task 2 rather than becoming its own task**: the `validate` path has no `--repo`, so its only behaviour here is announcing the absence of the check the mint path performs — it is meaningless before that check exists and therefore cannot precede it; and splitting it out would place it on the enforcement-before-prose chain (§Notes kickoff decision), pushing critical-path depth from 5 to 6. Two entry points into one fail-loud contract, one module, one implementer move.
  - GREEN: a quote present in the committed content at `head_sha` mints; quote-absent-at-sha and file-absent-at-sha each refuse with **distinct** messages naming path, sha and quote; `origin: none` skips verification entirely; the `validate` dry-run does not silently pass; `python3 -m pytest loom-code/scripts/` passes. The **sha-unresolvable** refusal is exercised by a direct unit test on the new helper, **not** through `_cmd_review_pass` — on the integrated path the existing `if branch is None or head_sha is None` guard returns 2 before the check is reached, so that branch is unreachable end-to-end and an integration test for it would be untestable-by-construction rather than merely absent.
- External surfaces: `git` CLI via `subprocess` — already the module's mechanism, no new dependency. Use `git show <head_sha>:<path>`; reading the worktree is wrong by construction (brief §Resolved Questions 1).
- Reuse-adequacy:
  - Observed: `_git` shells out and returns `None` on ANY failure, discarding stderr — `read loom-code/scripts/loom_gate_markers.py:90-103`
  - Observed: `_cmd_review_pass` validates at `:257` and only resolves `head_sha` at `:276` (`:275` resolves `branch`, not the sha) — the sha does not exist when validation runs — `read loom-code/scripts/loom_gate_markers.py:257-279`
  - Observed: the `validate` subcommand registers only `--verdict-file` and `--suite-line`; it has no repo and no HEAD — `read loom-code/scripts/loom_gate_markers.py:468-470`
  - Intended: reuse `_git`'s subprocess mechanism, but NOT its collapse-to-`None` contract — Task 2's GREEN needs "file absent at sha" and "sha unresolvable" to be distinguishable, so this call site must inspect the failure rather than inherit `None`. Reuse of `_cmd_review_pass`'s ordering does not carry over either: place the check **after the `if branch is None or head_sha is None` guard at `:277-279`** — i.e. at the first point where `head_sha` is known non-`None` — never alongside the `:257` validation, and never between the two `_git` calls at `:275-276`, where `head_sha` is not yet bound.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "It runs as a distinct step in `_cmd_review_pass` after the sha resolves; the `validate` path reports loudly that quote verification did not run"

## Task 3 — Add the field to the code-reviewer contract

- Description: Add `origin:` to the finding schema in
  `loom-code/agents/code-reviewer.md` (schema block at `:346-350`) and state
  the quote gate as an action the reviewer performs, not a judgment it makes:
  name the upstream artifact ONLY when you can quote the wrong statement
  verbatim; otherwise write `none`. State explicitly that `none` carries no
  penalty — the field records what the reviewer holds, not what it can infer.
  Transcribe the grammar VERBATIM from §Pinned field grammar.
- Module: loom-code/agents/code-reviewer.md
- Files touched: loom-code/agents/code-reviewer.md, loom-code/scripts/test_finding_origin_attribution.py
- Context paths:
  - loom-code/agents/code-reviewer.md
  - loom-code/agents/docs-reviewer.md
  - docs/loom/specs/2026-08-02-finding-origin-attribution.md
- Acceptance:
  - RED: `loom-code/scripts/test_finding_origin_attribution.py::test_code_reviewer_schema_carries_origin_and_the_quote_gate` — asserts the finding schema names `origin:` AND that the surrounding text states both the verbatim-quote requirement and the no-penalty `none` fallback; fails against the current file.
  - GREEN: the assertions hold, the schema block's existing fields are unchanged, and `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none — prose edit plus a grep-window test.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "`code-reviewer` (whole-branch) is the agent whose output the marker validates."

## Task 4 — Add the field to the per-task reviewer, and state that it is unenforced

- Description: Add the same `origin:` field to
  `loom-code/agents/code-quality-reviewer.md` (schema block at `:339-343`),
  and state the asymmetry in the contract itself: per-task verdicts never
  reach `loom_gate_markers.py`, so this field is emitted but **not**
  marker-enforced here. Writing that down is the point — a reader who assumes
  symmetric enforcement would be wrong in exactly the way this plan's own
  round-1 premise was wrong. Transcribe the grammar VERBATIM from §Pinned
  field grammar.
- Module: loom-code/agents/code-quality-reviewer.md
- Files touched: loom-code/agents/code-quality-reviewer.md, loom-code/scripts/test_finding_origin_attribution.py
- Context paths:
  - loom-code/agents/code-quality-reviewer.md
  - loom-code/agents/code-reviewer.md
- Acceptance:
  - RED: `loom-code/scripts/test_finding_origin_attribution.py::test_code_quality_reviewer_states_origin_is_not_marker_enforced` — asserts the agent names `origin:` AND says per-task verdicts are not marker-enforced; fails against the current file.
  - GREEN: both assertions hold and `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "`code-quality-reviewer` (per-task) emits the same field, and is **not** marker-enforced … That asymmetry is written into the contract."

## Task 5 — Mirror the field into the whole-branch verdict structure

- Description: Add `origin:` to §Verdict structure in
  `loom-code/skills/requesting-code-review/SKILL.md` — the block that mirrors
  `code-reviewer`'s schema (confirmed by its `cross-task-coherence` and
  `principles-conformance` entries, which the per-task agent's block does not
  carry). Point at the agent for the quote-gate rule rather than restating it;
  a second copy of the rule is a second source of truth. Annotate the scoping
  inline, following the `class:` precedent at `:150`.
- Module: loom-code/skills/requesting-code-review/SKILL.md
- Files touched: loom-code/skills/requesting-code-review/SKILL.md, loom-code/scripts/test_finding_origin_attribution.py
- Context paths:
  - loom-code/skills/requesting-code-review/SKILL.md
  - loom-code/agents/code-reviewer.md
- Acceptance:
  - RED: `loom-code/scripts/test_finding_origin_attribution.py::test_review_skill_verdict_structure_names_origin_without_restating_the_rule` — asserts §Verdict structure names `origin:` and does NOT restate the quote-gate rule in full; fails against the current file.
  - GREEN: both assertions hold and `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "Enforcement is scoped by dimension family … This follows the existing arm-scoping precedent for `class:` (`requesting-code-review/SKILL.md:150`)."

## Task 6 — Bump the plugin and record the change

- Description: Bump `loom-code` from 0.44.0 to 0.45.0 (a new required field on
  a shipped contract is a behaviour change, not a fix), sync the Codex
  manifest by script, add the matching CHANGELOG entry, and rename the
  version-pin test that tracks the current shipping version by design. Do not
  hand-edit the Codex manifest — run
  `python3 scripts/sync_codex_manifests.py loom-code`.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
  - loom-code/scripts/test_docs_review_blocking_class.py
  - scripts/check_version_bump.py
- Acceptance:
  - RED: `loom-code/scripts/test_docs_review_blocking_class.py::test_plugin_version_and_changelog_at_0_45_0` — the renamed pin asserts `"version": "0.45.0"` and a `## [0.45.0]` CHANGELOG heading; fails while the manifest reads 0.44.0.
  - GREEN: both manifests read 0.45.0, the CHANGELOG entry matches the file's existing shape, `python3 scripts/check_version_bump.py --base main --head HEAD` reports OK, and `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/` passes.
- External surfaces: none — `sync_codex_manifests.py` is an in-repo script.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "enforced by `loom_gate_markers.py` in the same fail-closed way `where:` already is" — the shipped-content bump this repo's rule requires for any PR changing agent or skill content. Depends on Task 5 rather than Task 1 so the CHANGELOG describes the whole shipped contract, not just its enforcement half.
