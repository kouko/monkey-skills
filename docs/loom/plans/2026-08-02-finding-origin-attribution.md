# Plan: reviewer findings carry a quote-gated origin

Source brief: docs/loom/specs/2026-08-02-finding-origin-attribution.md
Total tasks: 6
Critical-path depth: 5 (≤5) — Task 1 → 2 → 3 → 5 → 6; Task 4 is a depth-3 leaf
Execution order: sequential
Plan-document-reviewer verdict: PENDING

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
  The quote is matched at the **reviewed commit**, never at HEAD (§Resolved
  Questions 1).

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

- Description: Extend `_finding_problems` in `loom_gate_markers.py` so a
  finding block whose `dimension:` is in the code-arm set must carry an
  `origin:` line valued either `none` or `<path> :: "<quote>"`. A finding
  carrying a docs-arm dimension is untouched. Grammar only — the quote is not
  yet checked against any file (Task 2). Transcribe both pins VERBATIM.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
  - loom-code/skills/requesting-docs-review/SKILL.md
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_docs_arm_finding_without_origin_still_mints` — a verdict whose findings all carry docs-arm dimensions and no `origin:` must still validate. This is the discriminating case: a naive global requirement passes every other test and fails only this one, and failing it would block docs-only and mixed-branch pushes.
  - GREEN: a code-arm finding without `origin:` refuses; `origin: none` and `origin: docs/loom/plans/x.md :: "seven call sites"` both validate; a bare path with no quote and a quote with no path both refuse; docs-arm findings are unaffected; `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none — stdlib `re`, matching the module's existing imports.
- Reuse-adequacy:
  - Observed: `_finding_problems` already splits the verdict into per-finding blocks and requires a path-like `where:` in each, refusing to mint otherwise — `read loom-code/scripts/loom_gate_markers.py:224-247`
  - Observed (blast radius): the docs arm mints the SAME marker through the same validator — `read loom-code/skills/requesting-docs-review/SKILL.md:56`
  - Observed (precedent): a per-finding field scoped by arm already ships, annotated inline — `read loom-code/skills/requesting-code-review/SKILL.md:150`
  - Intended: reuse the per-finding block split and the refuse-to-mint path unchanged; the `where:` check's **unconditional** shape does NOT carry over — `origin:` must branch on the finding's own `dimension:` value, or it breaks every docs-only and mixed branch.
- Dependencies: none
- Independent: false
- Brief item covered: "A finding carrying a code-arm dimension must carry `origin:`; one carrying a docs-arm dimension is untouched."

## Task 2 — Verify the quote at the reviewed commit, and say so when you cannot

- Description: Add quote verification as a distinct step in `_cmd_review_pass`,
  **after** `head_sha` resolves — not inside `validate_verdict_text`, which
  runs before the sha exists and is also reachable from a subcommand that has
  no repo. For each code-arm finding whose `origin:` names a path and quote,
  read that path at the reviewed sha and refuse to mint unless the quote
  occurs, naming path, sha and quote in the message. Distinguish "file absent
  at that sha" from "sha unresolvable" — the current git helper collapses both
  to `None`. On the `validate` dry-run path, state in the output that quote
  verification did not run.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_origin_quote_present_only_at_head_refuses_to_mint` — a temp repo where the quoted sentence exists at HEAD but NOT at the reviewed sha must refuse. This is the case that distinguishes reviewed-commit lookup from HEAD lookup; a HEAD-based implementation passes every other case and fails only this one.
  - GREEN: a quote present at the reviewed sha mints; absent-at-sha, file-absent-at-sha and unresolvable-sha each refuse with distinct messages; `origin: none` skips verification; `validate --verdict-file <f>` prints that quote verification did not run and does not silently pass; `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: `git` CLI via `subprocess` — already the module's mechanism, no new dependency. Use `git show <sha>:<path>`; reading the worktree is wrong by construction.
- Reuse-adequacy:
  - Observed: `_git` shells out and returns `None` on ANY failure, discarding stderr — `read loom-code/scripts/loom_gate_markers.py:90-103`
  - Observed: `_cmd_review_pass` validates at `:257` and only resolves `head_sha` at `:275` — the sha does not exist when validation runs — `read loom-code/scripts/loom_gate_markers.py:254-276`
  - Observed: the `validate` subcommand registers only `--verdict-file` and `--suite-line`; it has no repo and no HEAD — `read loom-code/scripts/loom_gate_markers.py:468-470`
  - Intended: reuse `_git`'s subprocess mechanism, but NOT its collapse-to-`None` contract — Task 2's GREEN needs "file absent at sha" and "sha unresolvable" to be distinguishable, so this call site must inspect the failure rather than inherit `None`. Reuse of `_cmd_review_pass`'s ordering does not carry over either: the check must be placed after `:275`, not alongside the `:257` validation.
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
