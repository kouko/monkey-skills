# Changelog

All notable changes to the `loom-code` plugin (formerly `code-toolkit`) will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.27.7] — 2026-07-08 — name "deterministic sync-script output" as a mechanical-exemption category

### Added

- **`Review-weight: mechanical` now explicitly names a second qualifying
  category**: a task whose entire content is running an established,
  deterministic sync/mirror script (e.g. `sync-primitives.sh`,
  `sync_codex_manifests.py`) and committing its output, verified by a
  checksum match or the script's own paired drift-detection test. The
  existing wording ("an identical or near-identical edit reproducible
  from an exact spec") already covered this case, but wasn't obvious
  without naming it — an ambiguous-but-technically-covered gap is
  exactly the shape that has caused real misapplication before (see
  the two documented "compressing an exemption section flips its
  polarity" incidents in machine-local memory). Per this repo's own
  precedent, the fix is a named example, not a rule change.
- `subagent-driven-development`'s mechanical self-check gained a second
  **Content match** shape for this category: re-run the named script
  and confirm zero diff against the committed output, or run its
  paired drift-detection test and require exit 0 — since a sync-script
  task has no pre-known literal string to grep the way a literal-edit
  task does.
- Origin: PR #519's CI-drift-fix commit (deep-deep-research bake-off-2
  bugfixes) hit exactly this task shape twice in one commit
  (`research-toolkit/scripts/sync-primitives.sh`,
  `scripts/sync_codex_manifests.py`) without a clean way to mark it
  mechanical under the prior wording.

## [0.27.6] — 2026-07-08 — close-out push routing: requesting-code-review is the floor, not the close-out

### Fixed

- **Root-caused a live self-violation of PR #515's memory-timing rule.**
  This session closed out PR #511 and PR #516 by calling
  `requesting-code-review` directly and pushing by hand — never
  invoking `finishing-a-development-branch` — so its Step 8
  memory-timing check (shipped in #515, already merged before either
  branch started) never had a chance to fire. Two lessons distilled
  from those branches ended up in a separate post-merge branch,
  exactly the anti-pattern #515 exists to prevent.
- **Root cause**: `requesting-code-review`'s own "Push-as-trigger"
  section is self-contained and never mentions or defers to
  `finishing-a-development-branch`, even though `finishing-a-
  development-branch`'s own §When to use table says a push meant to
  finish/merge the branch should route there instead. Its Red Flags
  table (row: "Agent infers 'this branch is done, let me push'") already
  *named* the correct redirect, but the numbered "Procedure when
  push-as-trigger fires" never *operationalized* it — no decision
  branch checked for the close-out case before running the narrower
  review-then-push flow directly.
- **Fix**: added Step 0 to `requesting-code-review`'s Push-as-trigger
  procedure — an executable check: if the push is a real close-out
  (not just a mid-work review opinion), stop and invoke
  `finishing-a-development-branch` instead (it delegates to this skill
  as its own Step 1, so review still runs, plus verification +
  memory-timing + git-memory trailer decision). Numbered as Step 0
  (not renumbering 1-6) because `§Asking the user` cross-references
  "push-as-trigger steps 4-6" by number elsewhere in the same file —
  same retire-in-place discipline as PR #516's Check 5.
- Router card (`hooks/router-card.md`, SessionStart-injected every
  session) and `using-loom-code/SKILL.md` rule #4 reworded to state
  the same distinction — review PASS is the floor, `finishing-a-
  development-branch` is the actual close-out path. Router card kept
  terse (+31 words only — it's paid every session).
- Suite: 219 passed (docs-only change; no test asserted the prior
  Push-as-trigger wording).
- **Addendum** (close-out review caught, fixed same release): the
  substantive edits to `requesting-code-review/SKILL.md` and
  `using-loom-code/SKILL.md` initially bumped only the plugin-level
  `plugin.json` version, not these two files' own frontmatter
  `version:` fields — breaking this repo's established per-skill
  versioning convention (both files have bumped their own version on
  every prior substantive edit). Fixed: `requesting-code-review`
  0.12.0→0.13.0, `using-loom-code` 0.11.0→0.12.0.

## [0.27.5] — 2026-07-08 — writing-plans drops the time-box criterion entirely

### Changed

- **`writing-plans`**'s splitting framework no longer has a time-based
  criterion at any tier (0.27.4 demoted it to secondary; this removes
  it). The framework is now 3 criteria: acceptance (one failing test,
  primary), module scope, no hidden coupling. A new §No time-box
  criterion section documents why, including a cross-system survey
  (Devin, Cursor, Windsurf, Replit, Copilot Workspace, Amazon Q, Codex
  CLI, LangGraph/AutoGen/CrewAI reference implementations) that found
  no major coding-agent product with a documented time-based splitting
  rule — the two with any concrete secondary axis (Copilot Workspace,
  Amazon Q) both use file count, which criterion 2 (module scope)
  already covers.
- `plan-document-reviewer-prompt.md`'s Check 5 (the time estimate) is
  **retired** — always N/A, never applied — rather than renumbered, so
  every cross-reference to Checks 6-16 elsewhere in the plugin stays
  valid. `checks_passed` denominator updated 15→14 (Checks 5 and 15
  both now non-blocking). **This is a real behavior change**: a task
  previously flaggable by Check 5 alone (estimated time long, but a
  single clean assertion) now passes — only Check 6 (the RED test) can
  fail a task on sizing grounds.
- Cross-file consistency sweep: `agents/implementer.md` (role contract,
  BLOCKED trigger, dispatch template — the implementer's own contract
  no longer claims a time-box), `hooks/router-card.md` +
  `using-loom-code/SKILL.md` (router rule #3 card text),
  `subagent-driven-development/SKILL.md` + its `README.md`
  (frontmatter/summary — the `>1 hour` OR `>1 module` trigger for
  invoking SDD at all is untouched; that is a separate, independent
  threshold from per-task sizing), `brainstorming/references/
  handoff-brief-format.md`, `requesting-code-review/README.md`, and
  `writing-plans/README.{md,ja.md,zh-TW.md}` (all three languages) —
  all updated to stop describing a "≤5-minute" atomic-task unit.
  Historical/archival files (`docs/announcement/`, `docs/example-runs/`,
  prior CHANGELOG entries) intentionally left untouched as point-in-time
  records.
- `test_sdd_review_weight_marker.py::test_plan_document_reviewer_has_check_16`
  updated to assert the new `<14>` denominator (was `<15>`).
- Suite: 219 passed.
- **Addendum** (whole-branch review caught, fixed same release): the
  first draft of this removal left an orphaned mechanism — the
  "Structural-split escape hatch" still triggered on a >5-min condition
  tied to the now-retired Check 5, unreachable in practice — plus an
  "all four criteria" leftover from the pre-removal 4-row table, and
  four sibling skill READMEs (subagent-driven-development +
  requesting-code-review, ja + zh-TW each) and two living design docs
  (PRODUCT-SPEC.md, ROADMAP.md) that still described the removed rule
  as current. All fixed within this same 0.27.5 release before merge.

## [0.27.4] — 2026-07-08 — writing-plans reframes task-sizing primary axis

### Changed

- **`writing-plans`**'s splitting framework reorders its four criteria:
  the acceptance-criterion (one failing test) is now stated as the
  **primary** sizing constraint; the ≤5-minute time-box is reframed as
  a **secondary smell-check**, not the authoritative ceiling. An agent
  has no experiential grounding in duration (arXiv:2510.23853); Toby
  Ord's decay model (arXiv:2505.05115) does tie reliability to minutes,
  but its "minute" is an externally-benchmarked human-difficulty rating
  (the METR methodology), not a plan-writer's guess at how long an
  LLM implementer will take — no equivalent calibration exists for the
  latter, which is the quantity this criterion actually demoted.
  Traditional SE research on change size (Google `eng-practices`,
  Rigby & Bird 2013) sizes by file/diff boundary instead, never by
  completion time.
- Frontmatter `description` and the "What this skill does" bullets
  reordered to match; `plan-document-reviewer-prompt.md` Check 5
  (time estimate) gains a cross-reference noting it is secondary to
  Check 6 (RED test) — **no change to pass/fail behavior**, framing
  only.
- The separate critical-path **depth**-ceiling rationale (`≤5`, a
  different axis — chain length, not per-task minutes) gains a second
  citation: Ord's paper models a constant per-minute failure hazard
  against a task's human-difficulty rating and names no specific
  step-count or step-horizon — cited only as further evidence that
  reliability decays with task magnitude on some axis, not as support
  for any particular number near 5 (a round of review caught an
  earlier draft of this same citation mischaracterizing the paper as
  step-based with a fabricated "5-7 step-horizon" figure; corrected
  after independently re-fetching the abstract).
- Suite: 219 passed (no test asserted the prior wording — pure framing
  change, zero output-behavior delta expected in the common case).

## [0.27.3] — 2026-07-08 — finishing-a-development-branch enforces same-branch memory timing

### Added

- `finishing-a-development-branch` Step 8 gains a "Memory-timing check"
  bullet (mirrors the existing living-spec-index-regen precedent):
  a durable, already-known fact discovered during a branch's work must
  be recorded into `docs/loom/memory/` on THAT branch, landing in the
  same close-out commit — never a separate post-merge branch+PR.
- `docs/loom/memory/README.md` charter gains a "## When to record"
  section stating the rule + its one exception (genuinely post-merge-
  observable facts still need a follow-up branch, batched not
  one-PR-per-discovery).
- Suite: 219 passed (`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest
  loom-code/scripts/ -q`).

## [0.27.2] — 2026-07-08 — SDD per-task mechanical review-weight exemption

### Added

- **`writing-plans`**'s plan schema gains an opt-in per-task field,
  `Review-weight: mechanical`, parallel in spirit to the existing
  `Independent: true` marker. Default (field absent) is unchanged:
  every task still gets the full implementer + spec-reviewer +
  code-quality-reviewer triad. The field is **kind-gated, not
  size-gated** — it may only be set when a task's Description is an
  identical or near-identical edit reproducible from an exact spec
  (a concrete string/diff the implementer must match verbatim); never
  for logic, heuristic, hook, or security-surface changes, regardless
  of size.
- **`plan-document-reviewer`** gains Check 16, validating the
  `Review-weight: mechanical` co-condition — that the field is only
  set on tasks whose Description is genuinely an exact-spec mechanical
  edit — following the same validation pattern as Checks 13-14
  (`Independent: true` vs. `Files touched` disjointness).
- **`subagent-driven-development`**'s per-task triad gains a skip
  branch: when a task carries `Review-weight: mechanical` and the
  implementer returns `DONE`, SDD replaces the spec-reviewer +
  code-quality-reviewer dispatch with a deterministic grep/diff
  self-check confirming the exact expected string landed in each
  target file. A match resolves the task with no reviewer verdict
  needed; any mismatch falls back to the full triad (fail-closed
  toward review, never toward skipping on ambiguity).

See `docs/loom/specs/2026-07-08-sdd-mechanical-review-weight.md` for
the full brief, including rejected alternatives (LOC-based tiering,
reliance on operator discipline) and the evidence that the prior
informal "batch-mechanical" convention was inert.

Verification stamp: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest
loom-code/scripts/ -q` — 217 passed.

## [0.27.1] — 2026-07-08 — brainstorming fork-table default (dogfood F1)

### Fixed

- **`brainstorming`**'s fork-guidance region (the "lead with the
  stakes" rule) now carries the markdown-comparison-table default
  pointer at the FORK moment itself, not only at the summary seam. A
  weak-model actor was observed rendering a 2-option fork as bullet
  lists because the relay pointer only fired downstream. See
  `docs/skill-dogfood/2026-07-08-family-relay-behavioral/report.md`
  finding F1.

Verification stamp: `loom-pipeline/scripts/test_family_relay.py` — 159
passed (relay contract tests live in `loom-pipeline`).

## [0.27.0] — 2026-07-07 — family rollup card adoption + channel-aware visual degradation

### Changed

- **SDD wave reports/sign-offs** and **`requesting-code-review`**'s
  review relay now adopt the family rollup card — a pointer to
  `loom-pipeline`'s `family-relay.md` — instead of restating the full
  relay payload inline.
- **`brainstorming`**'s visual catalog gains channel-aware
  degradation: when the target channel is a terminal (no rich
  rendering), diagrams degrade to `ascii-graph-toolkit` tables/ASCII
  instead of Mermaid.

Verification stamp: `loom-pipeline/scripts/test_family_relay.py` — 8
passed (relay contract tests live in `loom-pipeline`).

## [0.26.0] — 2026-07-06 — review panel default + codex-tools autonomy correction

### Changed

- **`requesting-code-review`** now dispatches **two `code-reviewer`
  subagents in parallel** (byte-identical prompts) instead of one. The
  gate verdict comes from applying the aggregation rule to the
  **union** of both arms' findings, not either arm's own verdict.
  Evidence: `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md` —
  a single-Sonnet verdict missed the correct call 1-of-2 times; union
  aggregation reproduced the correct verdict with zero false positives
  across all 4 tested arms. Reviewers still inherit the session model (no pinning) — the 2×Sonnet panel is exactly the configuration G4 measured; the report cautions against cross-tier extrapolation.
- **`using-loom-code/references/codex-tools.md`** — corrected the
  stale "explicit-trigger only" claim about Codex subagent spawning.
  Live probes on 2026-07-06 (codex-cli 0.139.0, `multi_agent`
  stable+on, `codex exec`) showed model-initiated spawning from both a
  plain prompt instruction and an AGENTS.md standing delegation
  directive paired with a delegation-free prompt — no per-spawn
  approval observed. Interactive mode not yet exercised. Added a
  panel-dispatch mapping for `requesting-code-review`'s 2-reviewer
  panel.

## [0.25.0] — 2026-07-06 — gate friction pack

### Added

- **Patch-id relaxation** — `loom_gate_markers.py` records `base_sha` +
  `patch_id` (merge-base..HEAD, `git patch-id --stable`); `git-guard.py`
  accepts a stale `head_sha` marker IFF the recomputed patch-id matches —
  message-only amends and content-preserving rebases no longer force a
  re-review. Fail-closed on any computation error; old-format markers
  keep strict head_sha equality (backward compatible).
- **cd-chain cwd tracking** — `cd /other/repo && git push` now gates
  against the TARGET repo's markers (absolute/relative/~ forms; dynamic
  paths keep the previous cwd, fail-closed). Closes the
  loom-git-guard-evaluates-in-shell-cwd gotcha.
- **`validate` subcommand** — dry-run schema check for verdict files +
  suite lines reporting ALL violations in one pass (ends the
  discover-format-by-crash retry loop).
- **Gate-markers spec** — `skills/requesting-code-review/references/gate-markers-spec.md`.
  Origin: docs/loom/plans/2026-07-06-gate-friction-pack.md (3 live
  friction data points, 2026-07-06).

## [0.24.0] — 2026-07-06 — SessionStart router-card slim

### Changed

- **`hooks/session-start`** now injects the new `hooks/router-card.md`
  (~2.1 KB: coding mandate + five load-bearing rules + SUBAGENT-STOP +
  pull-pointer) instead of the full `using-loom-code` SKILL.md body
  (~11 KB). The full body loads via the Skill tool on invocation —
  pull, not push. Restores TECH-SPEC §2.3's original size constraint
  (the SKILL.md had grown ~4× past it since v0.1.0). Harness-wide the
  old embed cost ~3.1M input tokens/30d across 865 sessions
  (docs/harness-audit/2026-07-06-a-harness-diagnosis.md diagnosis #1);
  matcher `startup|clear|compact` and every-project reach made it the
  single largest measured context injection.
- Escape hatch (`LOOM_CODE_MODE=off`), 3-key defensive emission, and
  fail-open-on-missing-file behavior unchanged.

### Added

- `hooks/router-card.md` — the slim pre-invocation card (wording kept
  contract-stable per docs/loom/memory/preamble-wording-is-contract-surface.md).
- `tests/integration/test-router-card-slim.sh` — RED→GREEN gate: size
  1-5 KB, load-bearing tokens present, full-body markers absent, 3-key
  shape intact.
- Firing A/B gate (user-mandated 驗證過才准剪): 28-record corpus, both
  arms `--model sonnet`, report at
  docs/loom/dogfood/2026-07-06-router-card-firing-ab.md.

## [0.23.1] — 2026-07-04 — named-Agent dispatch gotcha

### Fixed

- **`references/environment-gotchas.md`** — new §A1: adding `name:` to an
  `Agent({subagent_type: "loom-code:..."})` dispatch call turns a one-shot
  blocking call into a persistent mailbox-semantics teammate whose
  plain-text output is never delivered (only an explicit `SendMessage`
  transmits it) — `description:` is unrelated and always required
  regardless. Hit in production: a named `code-reviewer` dispatch
  completed a correct review but the orchestrator only ever saw empty
  `idle_notification` heartbeats (recorded in monkey-skills memory
  `feedback_named_agent_dispatch_requires_sendmessage.md`). A single
  incident was initially judged DROP (no fix) under a recurring-pattern
  bar, but the failure has an identifiable structural trigger (the `Agent`
  tool's own naming affordance vs. this plugin's silent unnamed-only
  assumption) rather than being random noise, and the fix is a one-line
  doc addition — cheap enough not to wait for a second incident.
- `requesting-code-review`, `dispatching-parallel-agents`,
  `subagent-driven-development`, and `writing-plans` SKILL.md — every
  `Agent()`/evaluator-subagent dispatch site now points at §A1 and states
  the unnamed requirement inline (`writing-plans`'s `plan-document-reviewer`
  dispatch was the one site a first pass at this fix missed — caught by
  whole-branch review before merge). §A1's own header consumer list in
  `environment-gotchas.md` updated to match.
- **`references/codex-tools.md`** §Subagent dispatch — upgraded from
  "Assumed (not exercised)" to **Verified, mixed evidence grain**
  (2026-07-05): the `multi_agent` feature flag itself is live-confirmed
  (`codex features list` on a local Codex 0.139.0 install); the exact verb
  names and behavioral claims below it are doc-confirmed only (OpenAI's
  official Codex manual + a direct re-fetch/quote-match of
  `obra/superpowers`'s own `codex-tools.md`), not session-exercised — the
  file's own §Subagent dispatch banner spells out this breakdown in full.
  Codex's
  real subagent primitive is the `multi_agent` feature exposing
  `spawn_agent`/`wait_agent`/`close_agent` — not the previously-guessed
  `Agent(subagent_type, prompt)`-shaped call. Documents why §A1's gotcha is
  structurally Claude-Code-only (Codex's explicit-verb model has no
  overloaded call for an extra parameter to silently hijack) and flags that
  loom-code's plugin-bundled `agents/*.md` role-prompts still have no
  confirmed Codex-native equivalent (open gap). Full survey:
  `loom-code/research/2026-07-05-claude-code-codex-dual-compat-patterns.md`.

### Changed

- **Host-neutral SKILL.md bodies** (`requesting-code-review`,
  `dispatching-parallel-agents`, `subagent-driven-development`,
  `writing-plans`) — removed every literal Claude-Code-specific
  `Agent({subagent_type: ..., prompt: ...})` call-syntax occurrence from
  the shared skill text, replacing it with host-neutral prose ("dispatch a
  `<role>` subagent," a fan-out invariant expressed as pseudocode) plus a
  pointer to the reader's own host's tool-mapping reference
  (`claude-code-tools.md` / `codex-tools.md`) for the concrete call shape.
  Matches the pattern `obra/superpowers` already uses (confirmed via this
  branch's own research), where the skill body stays host-neutral and all
  host-specific syntax lives in per-harness reference files. The concrete
  Claude Code `Agent()` examples (including the parallel-fan-out
  concurrent-vs-sequential shape previously inline in
  `dispatching-parallel-agents`) moved to `claude-code-tools.md`;
  `codex-tools.md` gained a new "Re-binding loom-code's dispatch points
  onto Codex" section mapping each role to `spawn_agent`/`wait_agent`/
  `close_agent`.

## [0.23.0] — 2026-07-04 — **mechanical gates (harness-engineering audit follow-up)**

### Added

- **`hooks/git-guard.py`** (new PreToolUse hook, Bash matcher) — deterministic
  enforcement of three disciplines that previously lived in prose only
  (audit: `docs/loom/audits/2026-07-04-harness-engineering-audit.md`):
  blocks `git commit --no-verify`/`-n` (incl. bundled short-option clusters);
  blocks `git push` / `gh pr create` / `gh pr merge` unless BOTH
  `.git/loom/review-pass.json` and `.git/loom/verified.json` match the current
  HEAD sha (stale green lights and un-reviewed pushes fail loudly at the push
  choke point — Option 2 of the completion-gate design, chosen over a Stop
  hook for fatigue/timeout safety); honors a ONE-SHOT `.git/loom/waiver.json`
  (consumed atomically, fail-closed when undeletable). `git push --dry-run`/`-n`
  exempt; non-git cwd and `LOOM_CODE_MODE=off` pass through; malformed hook
  input fails open with a stderr note. 41 tests.
- **`scripts/loom_gate_markers.py`** (new CLI) — the only sanctioned marker
  writer: `review-pass --verdict-file` schema-validates the reviewer's verdict
  text BEFORE minting (NEEDS_REVISION exit 3 / malformed exit 4 — a failed or
  malformed review can never mint a pass; this consolidates the audit's
  verdict-schema-validation item), `verified --suite-line` rejects
  non-green summary lines, `waiver --reason` requires a real justification and
  warns loudly. Atomic writes; `--repo` per-subcommand. 23 tests.
- **SKILL.md wiring** — requesting-code-review Process step 3 mints the review
  marker on verdict; verification-before-completion Process step 5 mints the
  verified marker; finishing-a-development-branch gains step 9c (re-mint both
  at the FINAL HEAD after the close-out commit; substantive post-verdict
  changes require re-review; user-instructed waivers only, never self-minted).

## [0.22.1] — 2026-07-04 — firing-harness accounting fix

- `loom_firing_harness.py` grade mode keeps `{success, error_max_turns}`
  (an over-cap session that fired is a success signal — F3 dropped 6/28 valid
  records); `unparsed_lines` summed across kept AND discarded records into the
  grade aggregate. loom-spec README §Scope synced in the same PR (#489).

## [0.22.0] — 2026-07-04 — **loom family connective tissue (E1/E2/F-track)**

### Added

- **Brainstorming Axis 0 — upstream artifacts (family §Intake)** — a new
  section fronting the 5-axis framework: before Axis 1, check the target
  repo against the loom family reception's on-ramp criteria table
  (`loom-pipeline/hooks/family-reception.md`, pointed to, never copied). On
  a triggered row, surface the recommendation ONCE (naming the concrete
  design-side sequence), record the user's choice under a `## Design-side
  on-ramp` brief line, and never re-raise after a decline. Negative guard:
  bug fix / refactor / test-covered increment → skip silently. "5-axis" is
  retained as the framework's historical name; the mandatory walk now
  starts at Axis 0. Guarded by `scripts/test_brainstorming_axis0.py`.
- **`using-loom-code` red-flag row + family pointer** — the router's
  red-flags table now names skipping brainstorming's Axis 0 upstream check
  before writing a brief as a violation; §Coexistence gains a one-line
  pointer to the loom family reception (`loom-pipeline`'s SessionStart
  hook) as the family map + on-ramp criteria SSOT; rule #1 gains a one-clause
  historical-name note ("5-axis" name, walk starts at Axis 0). Net growth
  of `using-loom-code/SKILL.md` held to 2 lines against a 15-line
  test-asserted cap (this file is hook-injected every session). Doc sweep:
  `brainstorming/README.md` and `references/visual-companion.md` pick up
  the same Axis-0-inclusive wording where they asserted walk-scope
  completeness (brand-name "5-axis" mentions elsewhere left untouched).
- **`loom_firing_harness.py`** (new, stdlib-only) — a behavioral firing-test
  harness for the loom family's skill-routing: JSONL corpus parser with a
  self-containedness validator and a session-limit contamination filter
  (discarded records surfaced with a count, never graded); a `grade` mode
  scoring EXACT / FAMILY / MISS / OVER per record with a per-corpus
  aggregate (expected-NONE + non-loom fire is EXACT, never OVER); a `run`
  mode shelling out to `claude -p ... --output-format stream-json` (list-form
  args, `--max-turns` floor of 4, first `Skill` tool_use extracted as
  fired) with an argparse `run`/`grade` CLI. Run records tolerate non-JSON
  stdout noise (skipped lines surfaced as `unparsed_lines`, never silent),
  and a per-record failure is captured as a `harness_error` record that the
  contamination filter discards downstream — one bad record never aborts
  the batch. Six documented method traps (five from the 2026-06-24/25
  firing-test memory + the corpus-grading trap #6) are baked in. Guarded by
  `scripts/test_loom_firing_harness.py`.
- **Firing corpora** — `docs/loom/firing-corpus/{goal-oriented,near-miss,
  direct-ask}.jsonl` (8/10/10 self-contained lines): goal-oriented
  (design-side recommendation path), near-miss (must NOT fire the two new
  thin entries), direct-ask (#456 regression parity). Validated by the
  harness's corpus validator.

## [0.21.2] — 2026-07-03

### Fixed

- **`@req` namespace guard (implementer rule 11)** — the `@req`
  Definition-of-Done is now conditional on the dispatch carrying
  registered REQ-ids: tag only with an id that already exists in the
  living-spec namespace, never mint or pattern-match one (a dangling id
  fails the living-spec CI — PR #479 produced 33 such failures), and
  when the dispatch carries no registered ids, omit tags entirely
  (untagged tests are not INCOMPLETE in that case). The same
  omit-and-note escape applies per test when registered ids are in
  scope but a specific test corresponds to none of them — never
  stretch an unrelated id to fit. Resolves the
  contract-vs-CI conflict re-confirmed live on the v1.1 batch-mode
  branch, where every dispatch needed a hand-carried standing
  exemption. Guarded by `scripts/test_implementer_req_tag_guard.py`.

## [0.21.1] — 2026-07-03

### Added

- **D8 jurisdiction note** — `agents/code-reviewer.md` §D8 now states
  explicitly that `— check:` clauses in ANY of PRINCIPLES.md's
  jurisdiction sections (`## Product Principles` / `## Design Principles`
  / `## Engineering Principles`) are judged under the same existing
  subject-matter severity rule — no per-jurisdiction severity tier.

### Fixed

- **code-reviewer role anchor** — a dispatched `code-reviewer` could be
  role-confused by "review request" phrasing into acting as an orchestrator
  ("I've dispatched the whole-branch review" — to nobody, no verdict;
  observed live 2026-07-03). The existing prohibition (role-contract rule 3,
  "may not dispatch other subagents") did not prevent it: a negative rule
  cannot fix a mistaken identity. Fix is a positive anchor — **"You ARE the
  reviewer"** — now carried in the agent's role contract (rule 0), inside
  the §Input-contract prompt template every dispatch copies, and as an
  explicit instruction in `requesting-code-review` §Process step 2; the
  "announced dispatch instead of reviewing" reply is listed as a rejected
  anti-pattern. Guarded by
  `scripts/test_reviewer_dispatch_role_anchor.py` (3 tests, RED-first).

## [0.21.0] — 2026-07-03 — **ui-verification: the rendered-UI runtime gate**

### Added

- **New skill `ui-verification`** (skill 12): drives the real rendered app
  through every state `docs/loom/<change-id>/ui-flows.md` enumerates (render
  variants, flows, entry/exit) using the host's browser/device automation
  (chrome-devtools / agent-device MCP class), producing a two-valued verdict
  (`PASS_WITH_NOTES` / `NEEDS_REVISION`; no bare PASS — coverage is relative
  to the enumeration). CONDITIONAL gate (D8 pattern): fires only when a
  ui-flows.md exists and the branch touched a UI surface; **N/A-loud** when
  tooling is absent — never fake a walkthrough from source. DESIGN.md token
  conformance explicitly out of scope (respects the #473 park). Born from the
  2026-07-03 pipeline dogfood, where 28/28 green tests shipped a GUI with
  zero behavioral verification. Wired into `finishing-a-development-branch`
  (Phase 2 conditional sibling), the router stage table (7b), and
  `verification-before-completion`'s boundary. Guarded by
  `test_ui_verification_skill.py`.

- **Complex-fork briefing escalation rolled to the remaining asking gates.**
  `brainstorming` already mandated `dev-workflow:brief-before-asking` for
  genuinely complex forks (≥3 trade-offs / ≥2 implementation paths /
  architectural blast radius); `subagent-driven-development` and
  `requesting-code-review` gate ② now carry the same escalation (mirror
  principle per #355/#358 — in-place sentence, no copied block), so
  implementation-time technical decisions and complex remediation forks brief
  the user (Mental Model first) instead of handing over options they cannot
  evaluate. The threshold triple is a shared trigger contract guarded lockstep
  by `test_asking_user_briefing_escalation.py`.

## [0.20.0] — 2026-06-23 — **executable both-carrier memory verify gate at branch close-out**

### Added

`finishing-a-development-branch` now runs an **executable both-carrier verify
gate** at branch close-out, turning the P2 "verification required" prose into a
step that actually executes.

- **Commit-carrier gate (post-commit, pre-push).** After the close-out commit,
  the flow runs `dev-workflow/skills/git-memory/scripts/memory-grep.sh --verify
  HEAD`. When the branch is memory-worthy (git-memory's Phase-3 trailer set was
  non-empty) and `--verify` reports the commit carrier empty (**exit 4**), the
  flow **hard-STOPs** — the memory must be retrievable via `git log --grep` on
  `main` before push. A routine branch (empty trailer set) treats exit 4 as
  expected and proceeds.
- **PR-carrier check (at PR creation).** When opening the PR for a memory-worthy
  branch, the flow confirms the PR body carries a `## Memory` section before
  declaring the PR ready, per the both-carrier policy.
- The existing P2 verify prose now points at this enforced gate, so the
  description and the enforcement agree.

This closes the authoring-time-under-recording leak that #445's own dogfood
exposed (its squash commit `--verify`'d to **exit 4** — recorded only in the PR
`## Memory`, not in the commit carrier). **Verification-class** scaffolding: it
runs a check and surfaces a hard exit-4 signal — **no new generative mechanism**
(Phase 3/4 already authors the trailers).

## [0.19.0] — 2026-06-22 — **deliberate-simplification ledger (LOOM-SIMPLIFY marker + review-gate harvest)**

### Added

A new **deliberate-simplification ledger** makes scope-bounded shortcuts an
auditable, surfaced decision rather than silent debt. The canonical standard
`domain-teams/skills/code-team/standards/deliberate-simplification.md` (with a
byte-identical functional copy in the SDD bundled standards) defines a
`LOOM-SIMPLIFY:` in-code marker with four fields —
`shortcut` / `ceiling` / `upgrade` / `ref`.

- **Implementer** (`implementer.md` rule 10) leaves the `LOOM-SIMPLIFY:` marker
  inline whenever it takes a scope-bounded shortcut, so the simplification is
  recorded at the exact site it applies.
- **Whole-branch code-reviewer** (`code-reviewer.md` §D9) harvests the markers
  across the cumulative diff and completeness-checks them (kind well-formed,
  scope claim plausible, no marker hiding a real defect).
- **`requesting-code-review`** surfaces the harvested ledger at the merge gate,
  so a reviewer sees every deliberate shortcut before approving the branch.

**In-code markers are the single source of truth** — there is no persisted
ledger file to drift. The marker is **not a TDD waiver**: shortcut code is still
written test-first under the Iron Law; the marker only records that the scope was
deliberately bounded.

## [0.18.0] — 2026-06-21 — **spec→code seam wired (resolves the Tier-2 deferral)**

### Added

The spec→code delegation deferred in 0.16.0 is now **built**. `writing-plans`
gains a second input contract — a validated `loom-spec` change-folder (see its
**§Consuming a loom-spec change-folder**) — so a full spec flows
spec → plan → code. Each `#### Scenario:` GIVEN/WHEN/THEN maps to one task's
`Acceptance: RED/GREEN`, and `brainstorming`'s `loom-spec:spec-expansion`
forward-pointer is flipped from **Tier-2-deferred** to **active / wired**.
Continuous-mode freeze accepts an approved, `validate_spec_output.py`-clean
change-folder as an entry artifact (discriminated by user-declaration +
named-artifact presence + validator exit 0, not content-shape sniffing; STOP
contract + never-auto-merge unchanged).

Plan traceability now joins back to the spec: the `Brief item covered:` field
accepts a **stable join key** referent — `<change-id> / Requirement: <name> /
Scenario: <name>` — so every task traces to its originating scenario, and
`plan-document-reviewer` Check 3 accepts either a brief item or this spec
join-key provenance (point-don't-copy; loom-spec stays SSOT, consumer read-only).

This **resolves the two "deferred (Tier 2)" notes in 0.16.0 below** (the
forward-pointer activation condition — "active once `writing-plans` reads
OpenSpec change-folders" — and the blocked-on-unbuilt-wiring delegation item):
that wiring has now landed.

### Dogfood hardening

Fixes from dogfooding the wired seam before release:
- The upstream `loom-spec` validator now accepts `## MODIFIED` /
  `## REMOVED Requirements` blocks (was `ADDED`-only), so MODIFIED/REMOVED
  change-folders flow through to plan + code (loom-spec 0.3.1).
- Documented the brief-entry asymmetry: a spec join-key referent and a
  brainstorming brief item are interchangeable provenance for
  `Brief item covered:`, but only the join key round-trips back to the spec.
- De-jargoned the consumer-facing prose in `using-loom-code` / `writing-plans`
  / `plan-format`.
- Added an empty-recon sentinel so an empty Current-State reconnaissance is an
  explicit declared state, not a silently-skipped step.

## [0.17.0] — 2026-06-21

### Changed — **BREAKING: renamed `code-toolkit` → `loom-code`**

Part of the loom-pipeline suite rename (the visible "one suite" identity deferred
from PR #421, which shipped the `loom-pipeline` keyword tag). The 4 design→code
pipeline plugins now carry the `loom-` prefix:
`code-toolkit→loom-code`, `spec-toolkit→loom-spec`,
`interface-design-toolkit→loom-interface-design`,
`product-principles-toolkit→loom-product-principles`.

**Breaking for loom-code:**
- Plugin id, marketplace entry, and source path are now `loom-code`.
- Every `code-toolkit:<skill>` / `subagent_type: code-toolkit:<agent>` reference
  is now `loom-code:…` (operative refs repointed; frozen dated docs keep the old
  ids as historical record).
- Env var `CODE_TOOLKIT_MODE` → `LOOM_CODE_MODE` (hard cut, no fallback).
- Router skill `using-code-toolkit` → `using-loom-code`; CI workflow
  `code-toolkit-ci.yml` → `loom-code-ci.yml`.
- The shared SDD doc archive moved `docs/code-toolkit/` → `docs/loom/`
  (suite-named, matching the OpenSpec / Spec Kit / Kiro tool-named-dir norm);
  brainstorming / writing-plans now write new briefs/plans to `docs/loom/`.

Installed users must re-add the plugin under its new name; old `code-toolkit:`
ids and the old env var no longer resolve.

### Migrating old references (other repos / shells / configs)

There is **no alias** — old references break and must be repointed. When you
hit a pre-rename reference anywhere, apply this mapping:

```
code-toolkit               → loom-code
spec-toolkit               → loom-spec
interface-design-toolkit   → loom-interface-design
product-principles-toolkit → loom-product-principles
CODE_TOOLKIT_MODE          → LOOM_CODE_MODE
docs/code-toolkit/         → docs/loom/
```

- **Installed plugin**: re-add under `loom-code` (remove old, add new).
- **Shell rc**: rename any `CODE_TOOLKIT_MODE` export to `LOOM_CODE_MODE`.
- **Other repos' CLAUDE.md / .claude/settings.json / scripts**: grep + sed the
  tokens above (order: env var → longest token → shortest token last).
- **Old HANDOFF / session files**: historical — leave them; repoint only when you
  actually resume that session.

**Changing the skill's output path does NOT move existing files** — the skill
only sets where *new* briefs are written. To migrate an existing
`docs/code-toolkit/` archive in another repo (one-time, history-preserving):

```bash
git mv docs/code-toolkit docs/loom
grep -rIl 'docs/code-toolkit' . | grep -v node_modules | while read f; do
  sed -i '' 's#docs/code-toolkit#docs/loom#g' "$f"; done
grep -rIl 'docs/code-toolkit' . | grep -v node_modules | wc -l   # expect 0
```

## Journey overview (v0.1.0 → v1.0.0)

The toolkit emerged from a single design question — *"is there a way to combine Superpowers' process discipline with code-team's canon-grounding into one plugin?"* — and shipped 6 versions in ~3 weeks of solo dogfood + hybrid testing cadence:

| Version | Date | Theme | Net effect |
|---|---|---|---|
| **v0.1.0** | 2026-05-16 | MVP shell + 3 core skills | Router + tdd-iron-law + subagent-driven-development + SessionStart hook + SSOT-and-functional-copy pipeline (12 functional copies from code-team). 4 phases of build, 2 phases of ritual feedback, 2 bugs caught (YAML colon-space + hookEventName missing) + fixed before ship. |
| **v0.2.0** | 2026-05-16 | Phase 2 — discovery + planning + repair | + brainstorming + writing-plans + systematic-debugging. Discovery's 5-axis framework + writing-plans BLOCKED fallback (Beck Child Test) + systematic-debugging 4-phase REPRODUCE→ISOLATE→HYPOTHESIZE→VERIFY shipped as the workflow's mental-model layer. |
| **v0.2.1** | 2026-05-16 | Phase 1.5 rolling patches | tdd-iron-law gains Feathers (2004) Ch.13 §Legitimate legacy-code backfill distinction (closes "I just wrote 200 lines" rationalization gap surfaced in ritual); systematic-debugging description tuned for production-bug auto-fire (closes the auto-discovery miss surfaced in v0.2.0 ritual). |
| **v0.3.0** | 2026-05-16 | Phase 3 — close-branch cluster + full Superpowers parity | + requesting-code-review + verification-before-completion + finishing-a-development-branch + using-git-worktrees = 9 of 9 planned skills shipped. Push-without-review gap caught + fixed (Fix 1+2+3 + Path A patches). End-to-end orchestrator ritual validated 3-of-4 Phase 3 skills in one cascading session. |
| **v0.4.0** | (current draft) | Phase 2.5 + Phase 3.5 + Phase 4 prep | Codex CLI variant manifest + integration tests + 3 worked examples (Python / TypeScript / Swift) + 5 cross-plugin integration test scripts + announcement draft + multi-version retrospective. Build complete; verification rituals deferred to user-side Codex / superpowers sessions. |
| **v0.7.0** | 2026-05-16 | Policy-reset merge-to-main | Catches `main` up to the post-policy quality bar. Synthesizes v0.3.0 → v0.6.1 (Codex variant, reviewer-discipline R1+R2, Current State Evidence, `docs/superpowers/` → `docs/loom/` migration). No new feature; the merge artifact. |
| **v0.8.0** | 2026-05-18 | Across-domain parallel dispatch | + `dispatching-parallel-agents` (auxiliary skill borrowed from superpowers v5.1.0, adapted with TDD iron-law per branch + 3-valued verdict aggregation). `writing-plans` schema extended with `Independent` + `Files touched` per-task markup as the parallel-dispatch eligibility oracle. 11 skills total. |
| **v0.9.0** | 2026-05-18 | Inline rule-sheet — reviewer load reduction | Reviewer upfront standards load shrinks from ~80K → ~8K chars via inline `_rule-sheet.md` (1,531 bytes) injected into all 4 plugin-level agents through `distribute.py`'s `_baseline.md`-style BEGIN/END marker mechanism. 7 standards files unchanged in role — shifted from preload input to on-demand citation target. Cite-on-fire discipline codified (徳丸本 Ch.6 / OWASP ASVS section numbers MUST `Read` before citing; Beck / Clean Code / Fowler chapters may cite from memory). +1 integration test (rule-sheet drift). |
| **v1.0.0** | (target) | GA | After v0.8.0 dogfood adds 4 more notes (`research/dogfood-*.md`) + announcement publish + public release. Phase 4 GA criteria from ROADMAP met. |

**Cumulative artifact count at v0.4.0-draft**: 10 skills + 1 SessionStart hook + 12 byte-identical knowledge-layer functional copies + 3 SSOT pipeline scripts + 24 pressure-prompt test files across 9 test clusters + 5 integration test scripts + 2 Codex CLI verification scripts + 3 worked examples. ~28 commits on the long-lived `feat/code-toolkit-design` branch (per Q4 worktree convention).

**Hybrid testing cadence (TC-1 decision, 2026-05-16)**: each Phase ship gates on a 3-minute ritual (`claude plugin validate` + reinstall + 1 pressure prompt). Catches measure-level / behavior-level bugs early; defers full systematic test suite to v1.0.0 release engineering. Found 7 substantive bugs across rituals (YAML / hookEventName / Feathers gap / systematic-debugging auto-fire / push-without-review / check-skill-structure allowlist / plugin-rooted-path) — all caught before Phase ship, none after.

---

## [0.16.0] — 2026-06-11 — **brainstorming greenfield UI-coverage nudge (Tier 1)**

Adds a greenfield-gated, UI/state-surface-gated lightweight nudge to `brainstorming`:
when Current-State-Evidence is `N/A — greenfield` / thin **AND** the feature has a
UI / interaction / stateful surface, enumerate UI states across six categories
(empty / error / loading / state-transition / permission / boundary) **before
finalizing the brief** — plus a forward-pointer to `spec-toolkit:spec-expansion`
for the heavy case (was **Tier 2, deferred** until `writing-plans` reads OpenSpec
change-folders; **delivered in 0.18.0** — now active / wired).
Additive prose inside an existing skill (minor bump); **zero
cross-plugin dependency**.

Grounded in a 3-archetype greenfield A/B (eyedropper / collections / side-by-side)
showing plain brainstorming is thin on UI-edge coverage in greenfield (8/17, 6/12,
3/13) while the regime is brownfield-neutral (Current-State-Evidence recon
compensates there) — hence the **greenfield gate** (firing it in brownfield would be
near-dead-text). **DRY:** category reminder only; the full lens method (BVA /
state-machine / permission matrix) stays SSOT in `spec-toolkit:spec-expansion`.

### What ships

- **brainstorming** — new greenfield UI-state nudge subsection (after Current State
  Evidence, where the `N/A — greenfield` determination is made) + a Tier-2/deferred
  forward-pointer in `## Cross-skill delegation`. Skill version 0.10.1 → 0.11.0.
- **test** — `scripts/test_brainstorming_greenfield_nudge.py` grep-guards the six
  categories / the two-pronged gate + both exclusions (not-brownfield, not-pure-logic)
  / the forward-pointer / the DRY guardrail (stdlib-only, intent-tolerant).
- **~~deferred (Tier 2)~~ → delivered in 0.18.0:** brainstorming
  judging + delegating the full spec to `spec-toolkit:spec-expansion` via the
  OpenSpec change-folder contract — was blocked on the unbuilt OpenSpec DECLARE
  wiring (writing-plans reading change-folders; 2026-05-30 OpenSpec brief Q6=A);
  that wiring has now landed (`writing-plans` §Consuming a loom-spec change-folder).
- **post-ship verification (not shipped code):** greenfield A/B (with-nudge vs
  without, same 3 seeds) to confirm the nudge lifts coverage above the no-nudge
  baseline — if it doesn't, it's dead text (per the A/B-baseline lesson).

---

## [0.15.0] — 2026-05-31 — **asking-the-user Pattern-③ rollout to brainstorming + router**

Discharges the **v0.2 deferred item from PR #355** (the asking-the-user
investigation): the three-gate model — gate ① *whether to ask*, gate ② *research
before asking*, gate ③ *plain phrasing* — is now rolled out to `brainstorming`
and the `using-code-toolkit` router via **Pattern ③ (mirror-principle)**. Additive
guidance inside an existing skill (minor bump), consistent with #355's 0.13.0; no
contract or dependency change.

### What ships

- **brainstorming** — native **gate-③ phrasing rules** added to the one-axis-per-`AskUserQuestion`-call
  guidance, written tailored to the axis-question context: (a) open with a one-line
  **state anchor INSIDE the `question` field** (not only chat prose above it); (b)
  **outcome, not mechanism** (each option says what the user gets, not internal
  machinery); (c) **numbers carry their meaning** (translate raw counts/symbols). Gate
  ① already lives in **Axis 1** (confident JTBD read → don't re-ask) and gate ② in
  **Axis 4** (research-then-"My take: Recommend"), so only gate ③ was the gap. **No
  `## Asking the user` block** — the rules are folded natively into the existing axis
  guidance.
- **router (`using-code-toolkit`)** — rule #5 gains a **one-line pointer** that gates
  ①/③ are enforced downstream in `brainstorming` / `subagent-driven-development` /
  `requesting-code-review`. Pointer only; no gate definitions duplicated.

### Method note — Pattern ③ (mirror-principle)

Each skill carries its **own audience-tailored** version of the gate-③ rules; the
**PR #355 brief is the concept SSOT** (augmented with a §Cross-skill rollout section).
Explicitly: **NO cross-skill file reference, NO distribute-script, NO copied block** —
chosen to honor Anthropic skill-independence ("每個 skill 是自包含目錄"). The block is
audience-tailored, not byte-identical, so a shared-file or distribute mechanism would
be the wrong tool (those fit byte-identical SSOT like `_baseline.md` / `_rule-sheet.md`,
not register-shifted prose).

## [0.14.1] — 2026-05-31 — **writing-plans depth-ceiling grounding correction**

Documentation-only patch — **no behavior change**; the critical-path depth ≤5 ceiling is unchanged. Corrected the *grounding* of the depth ceiling after a challenge that the prior justification (human working-memory + scheduling analogies) was the wrong domain for an LLM-agent plan:

- The agent-native reason to bound **depth** is **error compounding over sequential LLM steps** — chain reliability ≈ per-step-success^depth, and per-step accuracy itself decays as the chain lengthens (long-horizon-execution research, e.g. "The Illusion of Diminishing Returns", arXiv 2509.09677). A depth-5 chain at ~95% per-step reliability ≈ 77% success.
- Added an honest marker that the value **`5` is a heuristic / default trigger, not a measured constant** — it was inherited from the prior count-based ceiling, and the literature finds **no universal optimal step count** (the principled limit is a function of per-step reliability; tune it accordingly).
- Bazel critical-path / Kanban WIP demoted to secondary framing analogies (they support depth-not-count, but are human/scheduling, not agent-native).

Provenance: the human-study research trail (Miller 7±2 / Cowan 4±1 / WBS 3-5 levels / span-of-control) and the LLM-native trail (error compounding / METR long-horizon reliability) are recorded in the session that produced this patch; the takeaway is that the *axis* (depth not count) is well-grounded but the *value* (5) is a tunable heuristic.

## [0.14.0] — 2026-05-31 — **writing-plans parallelism-aware ceiling**

Made `writing-plans` **parallelism-aware**: the plan-size ceiling is now
**critical-path DEPTH ≤5** (longest chain of tasks linked by `Dependencies`),
**not** total task count. A wide-but-shallow plan — many disjoint independent
leaves at one dependency level — is **no longer force-split**: width fans out
freely (mark `Independent: true`) and the dispatch/harness layer queues
concurrency. Additive planning guidance (minor bump); no contract or dependency
change. Dependencies stays the execution floor throughout.

### What ships

- **Depth-based ceiling** in `writing-plans/SKILL.md`: replaces the count-based
  "≤5 atomic tasks (total)" ceiling. N independent same-level tasks count as
  **one level**, not N; **no hard width cap** (the harness owns concurrency,
  `dispatching-parallel-agents` names no number). The "10-task plan is almost
  always a discovery failure" line is reframed to depth — a deep chain is a
  discovery failure, a wide-shallow plan is not. The "split into N sequential
  briefs" path now fires on **DEPTH** overflow, not width.
- **Active parallel-marking pass** in the splitting framework: after splitting,
  mark same-level disjoint tasks `Independent: true`. Guarded by
  **disjoint-files ≠ independent** — a real semantic dependency
  (doc-mirrors-code, consumer-imports-producer) keeps tasks sequential
  regardless of file disjointness; `Dependencies` remains the floor.
- **Advisory Check 15** in `plan-document-reviewer`: two tasks with disjoint
  `Files touched` and no dependency edge but NOT marked `Independent: true` →
  emit a **non-fatal NOTE** ("possible missed parallel opportunity"), never
  NEEDS_REVISION. Balances the existing one-directional Check 14 (over-claiming).
  **Check 2** is now depth-based.

This fixes: wide parallel work (i18n sweeps, one-change-across-N-modules,
multi-source fetches, multi-module audits) was being chopped into sequential
plans, which also multiplied the per-plan/per-run user confirmations ~N× —
a direct regression of the v0.13.0 confirmation-fatigue fix.

### Grounding

The industry bounds work by **depth + concurrency, never total count** (EN + JA
agreement): **Bazel** critical-path scheduling (parallelism limited by the
critical path + a `--jobs` cap, width is free); **Kanban WIP limits**
(cap in-flight work, explicitly not the backlog total — conflating the two is
the named anti-pattern); **Critical Path Method** (find the longest chain,
parallelize everything off it).

Brief: docs/loom/specs/2026-05-31-writing-plans-parallelism-aware-ceiling.md

## [0.13.0] — 2026-05-31 — **`## Asking the user` three-gate redesign**

Restructured the `## Asking the user` guidance in **both**
`subagent-driven-development` and `requesting-code-review` from a flat
seven-rule list into three sequenced gates. Additive behavioral guidance
(minor bump); no contract or dependency change.

### What ships

- **Three-gate structure** in both skills:
  - **① Whether to ask** — tier by reversibility × cost-of-being-wrong:
    reversible + inferable → act and mention after (no per-step re-confirm
    under standing authorization); irreversible / outward-facing / costly →
    always confirm; genuine taste / scope / un-inferable → ask via gate ②.
  - **② What to bring** — bring a researched `(Recommended)` option and
    confirm it; never punt an open-ended question to the user. The old
    standalone phrasing rule #5 ("research industry practice first; don't
    invent options") is **absorbed into and strengthened as gate ②**.
    `requesting-code-review` carries a lighter gate ② (its asks are
    "fix now / defer / merge anyway").
  - **③ How to phrase** — the kept 6 phrasing rules (verbatim), plus the
    ✅/❌ worked example and the calibration-target line.
- `requesting-code-review`'s `code-reviewer` structured-verdict boundary
  note is preserved unchanged (its R2 evidence-citation contract is not
  loosened).

### Grounding

Anchored in **Horvitz, *Principles of Mixed-Initiative User Interfaces*
(CHI 1999)** — the act-vs-ask threshold scales with the cost of being
wrong (expected-utility threshold; scope precision to confidence).

### Provenance

The plain-language operative rules are a **deliberate translation** of
察する (sense without being told) / 確連報 (確認・連絡・報告) / 忖度 +
confirmation-fatigue — the original research terminology is intentionally
kept OUT of the rule bodies but recorded so future edits can trace it. Full
lineage: `docs/loom/specs/2026-05-31-asking-the-user-three-gate-redesign.md`
§Terminology Provenance.

---

## [0.12.0] — 2026-05-30 — **Skill-refactor sweep — evidence-based de-bloat**

A systematic `dev-workflow:skill-refactor` (Ablation mode) sweep of all 11
skills, motivated by the observation that code-toolkit had grown to ~1.66× its
`obra/superpowers` ancestor in words/skill. The headline result is a **negative
finding**: the skills are mostly *not* bloated — 7 of 9 swept skills cannot lose
10% without cutting load-bearing content, and the gate refused to ship cosmetic
trims. Only two skills carried genuine, behavior-preserving bloat.

### What ships

- **`verification-before-completion` −19%** (1324→1073 words, 7 sections → 5):
  merged the HARD-GATE + Red-Flags redundancy-trap pair's *duplication*;
  compressed Process (dropped the detection-signal sublist that duplicates
  `references/test-invocation-by-stack.md`); consolidated Cross-skill-contract +
  What-this-does-NOT-do + See-also into one "Boundaries & related skills".
  "When NOT to use" kept verbatim (ablation positive control: load-bearing).
  Adds `test-prompts.json` (the skill-refactor gate's eval input).
- **`dispatching-parallel-agents` −15%** (1748→1488 words, 12 sections → 9):
  merged When-to-use + When-NOT-to-use into one table; folded
  What-this-does-NOT-do into the opener; folded See-also into the Cross-skill
  contract table (every sibling link preserved).

### Verification

Each refactor passed the skill-refactor Q1/Q2/Q3 gate (Q1 = multi-judge
equivalence ensemble on real behavioral runs; Q2 = ≥10% word reduction; Q3 =
frontmatter / dependency / link invariants intact). Whole-branch
`requesting-code-review`: **PASS** (0 🔴 / 0 🟡 / 2 🟢). Validators clean
(plugin-description-coherence, verify-drift, skill-folder-structure).

### Not shipped (gate working as designed)

- 7 skills returned `NO_SAFE_CUT` (<10% without harming behavior):
  requesting-code-review, writing-plans, systematic-debugging,
  subagent-driven-development, finishing-a-development-branch, tdd-iron-law,
  using-code-toolkit.
- `using-git-worktrees` reached 10.1% but the equivalence gate caught that the
  cut flipped a recommendation polarity on the NFS-mount exemption boundary
  (2/3 judges NOT_EQUIVALENT) → rejected. Same failure class as round 1's
  exemption-boundary sensitivity.

## [0.10.0] — 2026-05-30 — **Asking the user — plain-language question block**

Makes the questions and options the orchestrator shows the human user
easier to understand. Adds one `## Asking the user` rule block to the
two highest-friction skills — `subagent-driven-development` and
`requesting-code-review` — so that when the orchestrator stops to ask
"what next?" or "how should I handle these review findings?", the
question reads cleanly on its own.

### What ships

- **New `## Asking the user` block in two skills**
  (`subagent-driven-development` + `requesting-code-review`). Each
  skill ships its **own copy** (self-contained-directory convention) —
  no shared reference file.
- The block tells the orchestrator to:
  - name **what you'll get** from each option, not the internal
    mechanism behind it (plain, outcome-framed options);
  - drop or explain internal jargon the user didn't introduce;
  - open every question with a **one-line state anchor** (we just did
    X; now Y needs deciding) so a context-switched reader isn't lost;
  - keep it to **≤4 options**;
  - **research how the industry does it first** for design / strategy /
    tech-stack questions, instead of inventing options on the spot.

### Why this ships

Grounded in a closed investigation of **608 real `AskUserQuestion`
instances across 9 projects** (6 recurring failure modes — jargon
leak, cold-start with no context, made-up options, ESC-on-confusion,
too-many-options error, compound overload). 83% of questions already
read fine; this targets the ~17% tail, not a rewrite.

### Boundary (what does NOT change)

- The **code-reviewer agent's verdict stays machine-precise** —
  every finding keeps its evidence citation and the structured YAML
  verdict is untouched. These rules govern only the orchestrator's
  human-facing relay, never the agent-to-agent verdict.

### Scope

- Per-skill placement: each of the two skills carries its own copy of
  the block.
- The other **6 question-emitting skills** are a deliberate future
  rollout — prove the block on these two via real dogfood first, then
  roll it out (no mechanical 8-skill rollout up front).

## [0.9.0] — 2026-05-18 — **Inline rule-sheet — reviewer standards-loading optimization (V1)**

Replaces the upfront `Read` of 7 standards in every reviewer dispatch
with a single inline `_rule-sheet.md` (~1.5K chars) injected into the 4
plugin-level agent prompts via the same BEGIN/END marker mechanism
that ships `_baseline.md` and `_reviewer-discipline.md`. Standards
files keep their role as canonical text — they shift from "preload
input" to "on-demand citation target", read only when a flag's
`source:` field cites a specific section.

### Why this ships

Dogfood observation (2026-05-18): every reviewer dispatch was loading
~80K chars (~20K tokens) of standards / rubrics / checklists upfront,
regardless of whether the task triggered any of them. A typical 5-task
SDD plan burned 250K-400K tokens in reviewer context alone — repeated
for every plan. Adopting Anthropic Skills' 3-tier progressive
disclosure model (skill body always loaded; referenced files
on-demand) cuts the upfront load by ≥90% in the standards portion
without compromising code-toolkit's primary-source-grounded
differentiator vs `obra/superpowers`.

### What v0.9.0 ships

**New SSOT file — `code-toolkit/scripts/_rule-sheet.md`** (1,531 bytes):

- code-toolkit house thresholds (20-line soft / 50-line hard / 100-line
  gate-warning function length; etc.) — the *delta* between general
  LLM training data and toolkit specifics.
- Verdict aggregation rules (2🟡 = NEEDS_REVISION; opaque flag =
  NEEDS_REVISION; etc.).
- Dimension → standard path mapping table for cite-on-fire navigation.
- Cite-on-fire discipline: 徳丸本 Ch.6 sections / OWASP ASVS V5
  §X.Y.Z numbers / house thresholds **MUST** `Read` before citing
  (high hallucination risk on specific numbers). Clean Code chapter
  names / Fowler smell names / Beck Preface rule **MAY** cite from
  memory (canonical literature in training data).
- Does NOT contain: SOLID definitions, what F.I.R.S.T means, why DRY
  matters, generic smells — general LLM knowledge the agent already
  has.

**4 plugin-level agents now carry `rule-sheet-v1` BEGIN/END injection
block** (`implementer.md` + `spec-reviewer.md` + `code-quality-reviewer.md`
+ `code-reviewer.md`), managed by `scripts/distribute.py` — mirrors the
existing `baseline-v1` / `reviewer-discipline-v1` mechanism. As
embedded in `code-toolkit/agents/code-quality-reviewer.md`, the
rule-sheet block measures **1,531 bytes content / 1,703 bytes including
markers** — this is the **V2 measurement baseline** for future
compression / auto-gen comparisons (per brief §Alternatives Considered
#4: LLMLingua-style compression kept as V2 fallback).

**`scripts/distribute.py` extended**:

- New routing rule injects `_rule-sheet.md` content into all 4 agent
  files between `BEGIN rule-sheet-v1` / `END rule-sheet-v1` markers.
- Existing baseline + reviewer-discipline routing unchanged.

**Reviewer agent prompts updated** (`spec-reviewer.md`,
`code-quality-reviewer.md`, `code-reviewer.md`): the former "Standards
(load via Read before scoring)" preload list is replaced with a brief
"Standards (load on cite)" note pointing at the rule-sheet's
cite-on-fire discipline. Standards files themselves are unchanged in
role and content — they remain SSOT for canonical text, sourced from
`domain-teams/skills/code-team/standards/` via functional copy.

**New integration test —
`code-toolkit/tests/integration/test-rule-sheet-drift.sh`**: covers
rule-sheet drift detection — verifies the BEGIN/END block in each of
the 4 agent files matches `scripts/_rule-sheet.md` byte-for-byte and
that `verify-drift.py` fails loudly on intentional drift.

### Token impact

Standards-portion upfront load per reviewer dispatch:

| | Before (v0.8.0) | After (v0.9.0) | Reduction |
|---|---|---|---|
| 7 standards files | ~55K chars | 0 (on-demand) | -100% |
| 2 rubrics + 1 checklist | ~20K chars | ~20K chars | unchanged (still Tier 2) |
| Inline rule-sheet | — | ~1.5K chars | new |
| **Total standards portion** | **~80K chars** | **~8K chars** | **≥90%** |

Per-reviewer total upfront token load: ~20K → ≤2.5K tokens
(target met). On-demand `Read` of a full standard is still available
when a flag's `source:` field cites a specific section.

### What becomes obsolete

| Artifact | Status after V1 |
|---|---|
| Agent prompt section "Standards (load via Read before scoring)" with full preload list | **Replaced** — becomes "Standards (load on cite)" pointing at rule-sheet's cite-on-fire discipline |
| Always-load behavior at dispatch | **Removed** — inline rule-sheet replaces it |
| 7 standards files themselves | **Role shift, not deleted** — from "preload input" to "citation target". Still SSOT for canonical text. |
| `distribute.py` / `verify-drift.py` | **Extended** — `_rule-sheet.md` joins the agent-injection routing table. Existing standards-copy routing unchanged. |

### Deferred to V2

- Adding `## quick-rules` sections to each of the 7 standards files
  (prerequisite for auto-gen).
- Auto-generating `_rule-sheet.md` from standards (V2; V1 is
  hand-written + manually drift-checked).
- Token-measurement instrumentation (V1 eyeballs the savings; V2
  instruments if needed).
- LLMLingua-style compression of the rule-sheet itself (V2 fallback
  if cite-on-fire navigation fails in dogfood).

### References

- Brief: `docs/loom/specs/2026-05-18-inline-rule-sheet.md`
- Plan: `docs/loom/plans/2026-05-18-inline-rule-sheet.md`

### Migration

No migration steps for existing users. The change is internal to
plugin-agent dispatch. Reviewer behavior preserved: same flag
triggers, same verdict semantics, same primary-source citation
discipline — just with the canonical rule text inline instead of
preloaded. Users running the agents via `claude plugin install` /
`update` pick up the new injection blocks automatically; users on a
local clone should run `python3 code-toolkit/scripts/distribute.py`
once after pulling.

---

## [0.8.0] — 2026-05-18 — **Across-domain parallel dispatch + plan-schema markup**

Adds the 11th skill — `dispatching-parallel-agents` — borrowed from
`obra/superpowers` v5.1.0's same-named skill and adapted for
code-toolkit's discipline stack (TDD iron-law per branch + three-valued
verdict aggregation + clear coexistence boundary with SDD's per-task
reviewer parallelism). Plus an opt-in plan-schema extension in
`writing-plans` that gives the new skill a machine-checkable
eligibility signal.

### Why this ships

Dogfood observation (this session, 2026-05-18): code-toolkit's SDD
parallels the two reviewers inside one task (`spec-reviewer` +
`code-quality-reviewer` in one assistant message), but **across-task**
parallelism — when the plan contains genuinely independent atomic
tasks — was not surfaced as a first-class pattern. SDD also forbids
multiple-implementers-on-one-plan as a default safety rule, which is
correct *unless* the plan author has done the independence work.

superpowers v5.1.0 ships a dedicated `dispatching-parallel-agents`
skill that scopes the pattern cleanly: one agent per independent
problem domain, dispatched in one message. The borrowed shape
solves the gap without changing SDD's per-task safety floor.

### What v0.8.0 ships

**New skill — `dispatching-parallel-agents`** (auxiliary; no Skill
Priority stage; lateral utility like `using-git-worktrees`):

- Borrowed from `obra/superpowers` v5.1.0 `dispatching-parallel-agents`.
- Adapted: TDD iron-law applies per branch (not waived); three-valued
  verdict aggregation (`PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION`)
  matching code-toolkit's reviewer contract; explicit coexistence
  boundary with `subagent-driven-development` (this skill is across-
  task; SDD is within-task per-triad reviewer parallelism).
- Trigger conditions: 2+ independent problem domains (multiple
  unrelated test failures, multiple modules to audit, N disjoint data
  fetches, atomic tasks the plan marks `Independent: true`).
- Refusal conditions: shared file / shared symbol / sequential data
  dependency / investigation phase / within-SDD-triad attempts to
  double-wrap.
- Dispatch shape: **one assistant message, multiple `Agent` tool
  calls** (Claude Code's concurrency primitive).

**Plan schema extension in `writing-plans` (P15-15)**:

- Per-task fields `Independent: true | false` (default `false`) and
  `Files touched: <comma-separated paths>` added to the plan format
  at `skills/writing-plans/references/plan-format.md`.
- New §"Parallel-dispatch markup (v0.8.0+)" section in
  `skills/writing-plans/SKILL.md` documents the contract: a task is
  parallel-dispatch-safe **only when** both `Independent: true` AND
  `Files touched` is disjoint from other independent tasks.
- New anti-pattern in `plan-format.md` §Anti-patterns refuses
  `Independent: true` with overlapping `Files touched`.
- Worked example in `plan-format.md` updated to show the new fields
  on all three tasks (Task 1 + Task 2 mark `Independent: true` with
  disjoint files; Task 3 marks `false` because it touches Task 1's
  files).

**Router update — `using-code-toolkit/SKILL.md`**:

- §Skill priority's Auxiliary section expanded from one line to a
  bulleted list, adding `dispatching-parallel-agents` alongside
  `using-git-worktrees`.

**Version bump across artifacts**:

- All 11 SKILL.md frontmatter `version: 0.7.0` → `0.8.0`.
- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` version
  `0.7.0` → `0.8.0`; description "10 skills" → "11 skills";
  longDescription (Codex) updated to mention auxiliary parallel
  dispatch.
- All 3 READMEs (EN / JA / TW) "10 skills" → "11 skills" + status
  paragraph updated + skill table row added.

### Why NOT to learn other superpowers v5.1.0 patterns

Two patterns from superpowers v5.1.0 deliberately NOT carried into
code-toolkit at v0.8.0:

- **superpowers SDD's strict spec-rev → quality-rev sequencing**.
  code-toolkit's SDD already parallels them (one message, two
  `Agent` calls) — superpowers' sequencing is more conservative
  (saves wasted quality-rev compute when spec-rev fails) but
  code-toolkit's 3-round retry cap caps the waste; the latency win
  from parallelism dominates. No change.
- **`Task("...")` API shape**. superpowers' examples use a
  Claude-Agent-SDK shape that does not match Claude Code's
  `Agent({subagent_type: ..., prompt: ...})`. The new skill uses
  Claude Code's canonical shape and references it explicitly.

### Ship gate (same as v0.7.0)

No new ship-blocking criteria. v0.8.0 ships under v0.7.0's
"merge-to-main post-policy-reset" quality bar — all 11 skills validate
through `claude plugin validate`; no behavioral regression in the 10
prior skills.

Codex CLI live verification remains explicitly deferred (precedent
since v0.4.0).

### Migration

No migration steps for existing users. The new skill is auxiliary
(no Skill Priority stage, no auto-fire); the plan schema extension
is opt-in (existing plans without `Independent` / `Files touched`
behave identically to v0.7.0 plans). Users who want parallel
dispatch:

1. Mark independent atomic tasks `Independent: true` in the plan.
2. Declare `Files touched` for each.
3. Invoke `dispatching-parallel-agents` (or let `using-code-toolkit`'s
   router suggest it when the plan declares 2+ `Independent: true`
   tasks with disjoint `Files touched`).

---

## [0.7.0] — 2026-05-16 — **POLICY-RESET MERGE-TO-MAIN SHIP**

Second merge-to-main of code-toolkit. The first merge was PR #294
(`feat(code-toolkit): v0.3.0-draft`) which landed an early-state
snapshot before user enforced the "完全做好之前不合 main" policy
on 2026-05-16. After that policy was set, v0.3.0 → v0.6.1 ran on
the `feat/code-toolkit-design` branch through 4 minor + 2 patch
versions plus extensive ritual + drift cleanup. v0.7.0 is the
**policy-reset merge** — the version that catches main up to the
post-policy quality bar.

No behavioral or architectural change from v0.6.1. v0.7.0 is the
merge artifact + narrative consolidation, not a feature release.

### Why minor-version (0.6.1 → 0.7.0) for a no-feature merge

Symbolic. The `0.7.x` line marks "first shipped through main since
the policy was set" — the quality bar finally met user's
"完全做好之前不合 main" gate. Users who installed code-toolkit from
the `monkey-skills` marketplace would have seen v0.3.0-draft state
(from PR #294) until now; v0.7.0 brings them current with the 4
minor versions of design / build / ritual / drift cleanup that
ran on the branch:

- v0.4.0 — Codex CLI variant build + Phase 3.5/4 release engineering
- v0.5.0 — P15-10 router rule #5 "Research before asking" +
  brainstorming Axis 4 WebSearch protocol
- v0.5.1 — P15-11 Axis 4 multilingual coverage (EN + JA minimum)
- v0.5.2 — P15-12 Phase 1 plugin-level implementer + SSOT baseline
- v0.6.0 — P15-12 Phase 2 (3 reviewer agents promoted to plugin-
  level) + cross-task-coherence dimension active
- v0.6.1 — P15-14 doc-drift cleanup (TECH-SPEC / README / 2 tests/
  READMEs)
- v0.7.0 — this merge

### Ship gate met (redefinition from original v1.0.0 plan)

The original ROADMAP made v1.0.0 wait for P15-4 (soft-mode flag) +
P15-5 (≥5 dogfood notes) to satisfy before merge. Both turned out
to be **dogfood-gated**: they need real plugin usage to drive their
design, and real plugin usage needs the plugin deployed. Chicken-
and-egg.

Resolution: redefine both as post-ship backlog rather than ship-
blocking:

- **P15-4** soft-mode → "post-v0.7.0; across v0.5.x→v0.6.x cycle no
  skill emerged as too-strong; HARD-GATEs all earned their strictness.
  Dogfood Note #1 §"What didn't work" raises possibility P15-4 is
  YAGNI to be retired"
- **P15-5** ≥5 dogfood notes → "v0.7.0 ships with 1 retroactive note
  (`research/dogfood-2026-05-16-self-toolkit-architectural-shift.md`,
  scope=meta toolkit-on-toolkit). Capture ≥4 more from external
  real-work sessions over next release cycle"

Codex CLI live verification remains explicitly deferred per user
direction (precedent — has been deferred through 4 prior ships).

### What v0.7.0 ships (synthesizing v0.1.0 → v0.6.1)

**Architecture**:
- 10 skills: router (`using-code-toolkit`) + 8 stage skills (Discovery
  / Planning / Execution / Discipline / Repair / Review / Verification
  / Branch close) + 1 auxiliary (`using-git-worktrees`)
- 4 plugin-level subagents at `code-toolkit/agents/`:
  `implementer` + `spec-reviewer` + `code-quality-reviewer` +
  `code-reviewer`. Cross-plugin reusable via
  `Agent({subagent_type: "code-toolkit:<role>"})`
- SSOT-and-functional-copy machinery in 2 variants:
  - Whole-file: 12 byte-identical copies from
    `domain-teams:code-team` (Beck 2002 / Martin 2008 / Fowler 2018
    / Feathers 2004 / OWASP ASVS v5 / 徳丸本 Ch.6 + 2 rubrics +
    2 checklists)
  - In-file section: 12-rule engineering baseline injected from SSOT
    at `scripts/_baseline.md` into 4 agent files via marker pair
    `<!-- BEGIN baseline-v1 ... -->` / `<!-- END baseline-v1 -->`
- `scripts/verify-drift.py` gates both variants on every CI run
- SessionStart hook auto-injects router charter (`additional_context`
  / `additionalContext` / `hookSpecificOutput.additionalContext` —
  portable across Claude Code + Codex CLI + legacy hook shapes)

**Five load-bearing router rules (cumulative v0.1.0 → v0.5.0)**:
1. Brainstorm before implementing
2. TDD is the iron law (Beck 2002 Preface verbatim)
3. Split + dispatch on >1hr / >1 module (SDD)
4. Never push without review (push commands fire
   `requesting-code-review`, not bypass)
5. Research before asking (non-trivial design questions must cite
   WebSearch findings; Axis 4 protocol enforces EN + JA minimum
   since v0.5.1)

**Two cross-plugin coexistence contracts**:
- `domain-teams:code-team` passive gate — same knowledge layer
  byte-identical via SSOT
- `dev-workflow:{git-memory, complexity-critique, proposal-critique}`
  — delegated to at the right moments
- `obra/superpowers` — overlapping skill names + dual SessionStart
  hook; resolved via `CODE_TOOLKIT_MODE=off`

**Ritual coverage**:
- Phase 1 i-already-wrote-it (v0.1.0): PASS — Beck 2002 cited
- Phase 2 silence-with-try-except (v0.2.0): PASS — systematic-
  debugging auto-fire
- Phase 3 push-without-review (v0.3.0): caught critical gap → 3
  fixes shipped same release
- Phase 4 4-session orchestrator ritual (v0.4.0): PASS 3 of 4
  sessions (Session 4 SKIP per P15-9 — superpowers installed but
  not enabled in user environment)
- v0.5.0 rate-limiting research-before-asking ritual: 9 EN sources
  surfaced; identified single-language coverage gap → drove P15-11
- v0.5.1 multilingual self-check: bilingual research with 9 JA
  sources cited
- v0.5.2 SDD dispatch validation: implementer plugin-level resolved
  cleanly; baseline visible in system prompt; BLOCKED-vs-NEEDS_CONTEXT
  discrimination stronger than predicted
- v0.6.0 SDD triad parallel + whole-branch code-review:
  spec-reviewer + code-quality-reviewer plugin-level dispatch +
  code-reviewer whole-branch with cross-task-coherence dimension
  catching 5 real doc-drift findings
- Cumulative: 8+ ritual cycles validated across 4 dispatch surfaces
  (implementer / 2 SDD reviewers / whole-branch reviewer)

**Marketplace integration**:
- `.claude-plugin/marketplace.json` on `main` now lists code-toolkit
  (added at merge time)
- Install: `claude plugin install code-toolkit@monkey-skills`

### Files changed in this commit

- 10 skill SKILL.md `version:` 0.6.1 → 0.7.0
- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` 0.6.1
  → 0.7.0
- `monkey-skills/.claude-plugin/marketplace.json` — added
  code-toolkit entry (insertion only, no other changes)
- `ROADMAP.md` — P15-4 + P15-5 reclassified as post-v0.7.0;
  acceptance line updated to reflect ship gate met
- `research/dogfood-2026-05-16-self-toolkit-architectural-shift.md` —
  Dogfood Note #1 (retroactive, scope=meta)
- `CHANGELOG.md` — this entry

### Post-merge work (v0.7.x+ / v1.0.0 GA target)

- **Capture Dogfood Notes #2-#5** from external real-work sessions
  (different repos / different problem domains). Target: v1.0.0 GA
  when ≥5 notes accumulate
- **Codex CLI live verification ritual** when a real Codex CLI
  use-case appears
- **P15-4 soft-mode** decide retire vs implement based on dogfood
  data
- **P15-13** `scripts/check-skill-structure.py` allowlist fix (low
  priority — code-toolkit no longer surfaces the false-positive but
  other plugins might)
- **Wider doc-drift sweep** as standard part of every minor version
  bump (lesson from v0.6.0 → v0.6.1 cycle: drift-finding has a
  long tail)

### Acknowledgements

Built with Claude Code Opus 4.7 across ~28 commits / 17+ versions
(0.1.0-draft → 0.7.0) on `feat/code-toolkit-design` worktree per
Q4 design decision (one repo, N checkouts). Grounded in 8 primary
sources + a popular CLAUDE.md 12-rule template. The ritual cycle
discipline (1 pressure prompt per Phase ship) caught 9+ substantive
bugs that would otherwise have shipped silently — making this
release engineering pattern itself worth reusing.

---

## [0.6.1] — 2026-05-16

**Patch — doc-drift cleanup beyond v0.6.0 code-reviewer ritual scope.**

The v0.6.0 ritual's whole-branch code-reviewer found 5 doc-drift
findings in skills/ (all fixed before v0.6.0 ship). A wider post-ship
scan surfaced 4 more drift items in TECH-SPEC + README + 2 tests/
README files that the reviewer didn't flag — its dimension scoring
prioritized dispatch-affecting drift over pure documentation drift
elsewhere in the plugin tree. This patch cleans those up.

### What changed

1. **`TECH-SPEC.md`** — 6 references to deleted per-skill prompt
   templates (`agents/*-prompt.md`) updated to plugin-level paths
   (`code-toolkit/agents/*.md`):
   - §2.1 dirtree: removed per-skill `agents/` subdir from SDD
     skill block; added new plugin-level `agents/` + `scripts/` block
     describing v0.5.2 + v0.6.0 layout
   - §2.4 subagent data flow: rewrote 3 prompt-template entries to
     reference plugin-level dispatch via
     `Agent({subagent_type: "code-toolkit:<role>"})`; added 4th entry
     for `code-reviewer` (was missing in original spec)
   - §3.3 SKILL.md sections table: `Prompt Templates` row updated to
     `Subagent dispatch` with current path + version migration note
   - §3.4 Subagent prompts: 3 section headers updated from
     `*-prompt.md` to plugin-level forms; intro paragraph added
   - Revision history: new row added documenting the v0.6.0 agent-
     layer migration (P15-12 Phase 1+2) and pointing at v0.5.2 +
     v0.6.0 CHANGELOG entries for rationale

2. **`README.md`** — landing-page status updated:
   - Status line: `v0.4.0-draft (9 of 9 skills shipped; Codex CLI
     build complete; verification rituals pending → v1.0.0 target)`
     → `v0.6.0 (10 skills shipped — full Superpowers parity since
     v0.3.0; 4 plugin-level subagents with SSOT-injected 12-rule
     baseline since v0.6.0 / P15-12; …)`
   - §Install / Codex CLI section reworded — Codex live verification
     deferred per user, not "pending" indefinitely
   - §Compatibility table — Claude Code row updated to enumerate the
     multiple ritual cycles validated (Phase 3 / Phase 4 / v0.5.1
     multilingual / v0.5.2 + v0.6.0 plugin-level dispatch / v0.6.0
     whole-branch code-review)

3. **`tests/integration/README.md`** — removed `(Phase 3 ship)`
   annotations from 4 test directory descriptions. Phases shipped
   in v0.3.0; annotations were stale.

4. **`tests/codex-cli/README.md`** — wholesale version refresh:
   - Title block: `v0.4.0 — Phase 2.5 BUILD complete` → "build
     complete; tracked in lock-step with `.claude-plugin/plugin.json`
     since v0.4.0; live verification still deferred per user direction"
   - §When to run: removed `v0.4.0 Phase 2.5` phase-stamped section
     title (the ritual is timeless; phase-stamping it tied it to a
     past moment that no longer exists)
   - §Prerequisite line: removed `As of v0.4.0 build` qualifier
   - PASS clause: was `drop -draft → v0.4.0 ship`; now "note in
     CHANGELOG against the current plugin version"
   - See-also: `.codex-plugin/plugin.json (v0.4.0-draft)` →
     "tracked in lock-step with `.claude-plugin/plugin.json`"

### Why a patch, not a major bump

No architectural change. No agent contract change. No SKILL behavior
change. Pure documentation drift cleanup. The code-reviewer's
selection bias (dispatch-affecting drift first) is real and predictable
— periodic wider sweeps catch what the per-ritual scope misses.

### Version bumps

- 10 skill SKILL.md `version:` 0.6.0 → 0.6.1
- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` 0.6.0 → 0.6.1

### Gate status pre-commit

- `claude plugin validate`: PASS (no warnings)
- `check-skill-structure`: 10/10 PASS
- `verify-drift`: 12 functional-copy pairs + 4 baseline blocks all OK
- Post-fix grep for `v0\.[0-5]\.` / `agents/.*-prompt\.md` /
  `Phase 3 ship` / `Phase 2.5 BUILD` / `v0\.4\.0-draft` outside
  CHANGELOG / ROADMAP / historical narrative: clean

### Learning — drift-finding has a long tail

The v0.6.0 code-reviewer ritual surfaced 5 high-priority drift items
(dispatch-affecting). The post-ship wider scan surfaced 4 more
(documentation-only). A future v1.0.0 release-engineering pass
should expect another low-priority tail (probably in PRODUCT-SPEC.md,
hooks/ scripts, or `using-code-toolkit/references/codex-tools.md`
TBD-marked sections). Drift accumulates faster than any single
ritual catches it; cadence > comprehensiveness.

---

## [0.6.0] — 2026-05-16

**Ship status**: ritual PASS (see §Phase 2 ritual verification at end
of this entry). 5 doc-drift findings caught by the v0.6.0 code-reviewer
ritual were fixed before drop-`-draft`. Dropped `-draft` from version
field after fixes.

Phase 1.5 patch **P15-12 (Phase 2)** — promote remaining 3 agents to
plugin-level (`spec-reviewer` / `code-quality-reviewer` /
`code-reviewer`), each carrying the 12-rule engineering baseline via
SSOT injection. Per-skill `agents/` directories emptied → CHK-SKL-012
false-positive naturally resolved.

This completes the P15-12 architectural shift started in v0.5.2 Phase
1. All 4 plugin-level agents now live at `code-toolkit/agents/`; SDD
orchestrator + requesting-code-review skill dispatch via
`Agent({subagent_type: "code-toolkit:<role>"})` exclusively.

### Why minor-version bump (0.5.2 → 0.6.0)

v0.5.2 was a single-agent proof-of-mechanism (1 of 4 promoted). v0.6.0
completes the architectural shift: the SDD orchestrator's per-task
triad (implementer + spec-reviewer + code-quality-reviewer) is now
fully plugin-level, plus the whole-branch reviewer from
`requesting-code-review`. Cross-plugin reusability is no longer
hypothetical — other plugins (e.g. `domain-teams:code-team`) can now
dispatch any of the 4 reviewers via marketplace identifier.

### What shipped

**Created (3 new plugin-level agent files at `code-toolkit/agents/`)**:
- `spec-reviewer.md` — binary PASS/NEEDS_REVISION verdict on spec
  consistency (was: `skills/subagent-driven-development/agents/spec-reviewer-prompt.md`)
- `code-quality-reviewer.md` — 3-valued verdict + 6-dimension scores
  + severity-tagged flags on per-task code quality (was:
  `skills/subagent-driven-development/agents/code-quality-reviewer-prompt.md`)
- `code-reviewer.md` — whole-branch reviewer with unique
  cross-task-coherence dimension (was:
  `skills/requesting-code-review/agents/code-reviewer-prompt.md`)

Each carries the 12-rule baseline via `<!-- BEGIN baseline-v1 -->` /
`<!-- END baseline-v1 -->` markers; injected by `distribute.py` from
SSOT at `scripts/_baseline.md`; drift-gated by `verify-drift.py`.

**Deleted (3 in-skill prompt templates, replaced by plugin-level)**:
- `skills/subagent-driven-development/agents/spec-reviewer-prompt.md`
- `skills/subagent-driven-development/agents/code-quality-reviewer-prompt.md`
- `skills/requesting-code-review/agents/code-reviewer-prompt.md`

**Removed (empty `agents/` directories)**:
- `skills/subagent-driven-development/agents/`
- `skills/requesting-code-review/agents/`

**Updated (3 SKILL.md dispatch refs)**:
- `skills/subagent-driven-development/SKILL.md` — §Process Step 3
  now dispatches via `Agent({subagent_type:"code-toolkit:spec-reviewer"})`
  + `Agent({subagent_type:"code-toolkit:code-quality-reviewer"})`;
  §Prompt templates rewritten; §See also updated
- `skills/requesting-code-review/SKILL.md` — §Process Step 2 now
  dispatches via `Agent({subagent_type:"code-toolkit:code-reviewer"})`;
  §See also updated

**Extended (`scripts/distribute.py` route table)**:
```python
AGENT_BASELINE_TARGETS: list[str] = [
    "agents/implementer.md",          # v0.5.2 / Phase 1
    "agents/spec-reviewer.md",        # v0.6.0 / Phase 2
    "agents/code-quality-reviewer.md",# v0.6.0 / Phase 2
    "agents/code-reviewer.md",        # v0.6.0 / Phase 2
]
```

**Bumped (12 manifests)**:
- 10 skill SKILL.md `version:` 0.5.2 → 0.6.0-draft
- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` version
  0.5.2 → 0.6.0-draft

### What was NOT promoted

**systematic-debugging has no agent directory** — the skill's
4-phase REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY protocol runs
inline; no separate dispatched agent. No `debugger.md` in this batch.
The original P15-12 Phase 2 plan listed 4 agents; actual scope was 3.

### CHK-SKL-012 false-positive — naturally resolved

The script `scripts/check-skill-structure.py`'s `OPTIONAL_SUBDIRS`
allowlist (`{"research", "references"}`) was narrower than
`CLAUDE.md`'s §Skill Structure spec which permits `agents/`. Before
v0.6.0, 2 skills had per-skill `agents/` subdirs which the lint
script flagged. v0.6.0 empties both directories (and removes them);
`check-skill-structure.py` now PASSes all 10 skills clean.

The underlying allowlist gap in the script remains — if any other
plugin starts using per-skill `agents/`, the false-positive will
re-surface. Tracked as P15-13 (low priority; v1.0.0 cleanup).

### Phase 2 ritual verification — PASS (two complementary rituals)

#### Ritual A — SDD triad parallel dispatch (fictional artifact)

Pressure prompt: `"refactor UserService.authenticate to add MFA"` →
push past brainstorming into SDD task dispatch → at Step 3 dispatch
spec-reviewer + code-quality-reviewer in parallel against the
fictional artifact paths the Phase 1 plan declares (`src/services/UserService.ts`).

**Both reviewer agents PASS the discipline**:

| Signal | spec-reviewer | code-quality-reviewer |
|---|---|---|
| Plugin-level dispatch | ✅ `Agent({subagent_type:"code-toolkit:spec-reviewer"})` resolved cleanly | ✅ `Agent({subagent_type:"code-toolkit:code-quality-reviewer"})` resolved cleanly |
| Verdict | NEEDS_REVISION (3 gaps; root cause: brief Open Q #1 setup unresolved) | NEEDS_REVISION (2× 🔴 fatal + 1× 🟡; refused to load standards on absent artifact citing Rule 6 token budget + Rule 12 fail loud) |
| Scope boundary | Cited spec coverage only | Cited rubrics + standards only; forwarded process-fit observation to `notes` (didn't blend) |
| Baseline rule fingerprint | Rule 12 (fail loud) — no PASS on absent artifact | Rule 6 + Rule 12 quoted to justify refusing standard-load |

**Meta-signal**: agent self-reported breaking the parallel-dispatch
rule (sent serially across 2 messages instead of 1 message with 2
tool calls). Rule 12 (fail loud) fired even at the meta-level — agent
surfaced its own protocol deviation rather than hiding it. Strong
discipline signal.

#### Ritual B — whole-branch code-reviewer (real diff)

Pressure prompt: `"Run requesting-code-review on this branch
(feat/code-toolkit-design). I want to see the whole-branch review
with cross-task-coherence dimension scored."`

**The code-reviewer plugin-level agent worked AS DESIGNED**:

- ✅ `Agent({subagent_type:"code-toolkit:code-reviewer"})` resolved
  cleanly; 63 tool uses / 142.8K tokens / 4m 17s of real work
- ✅ All 7 dimensions scored (including unique cross-task-coherence)
- ✅ Verdict: PASS_WITH_NOTES (5 findings — 3 🟡 + 2 🟢, no 🔴)
- ✅ Cited primary sources where relevant
- ✅ **Found 5 real doc-drift bugs** that earlier phases of this
  branch introduced — exactly what the cross-task-coherence dimension
  is designed to catch (items individually correct at time of writing
  but contradicted by cumulative branch state)

The 5 findings (all valid):

| # | Severity | Where | What |
|---|---|---|---|
| 1 | 🟡 cross-task-coherence | `using-code-toolkit/references/engineering-baselines.md:41-50` | ASCII layout claimed `agents/_baseline.md` (moved to `scripts/` per 172fc01) + listed "Phase 2 will add reviewer.md / debugger.md" (actual promoted set is spec-reviewer / code-quality-reviewer / code-reviewer; no debugger) |
| 2 | 🟡 cross-task-coherence | `using-code-toolkit/references/claude-code-tools.md:24` | Referenced deleted `skills/subagent-driven-development/agents/*-prompt.md` directory |
| 3 | 🟡 correctness | `subagent-driven-development/SKILL.md:103-104` | Cross-skill contract still described `writing-plans` as "(Phase 2)" with "until Phase 2 ships" fallback, and `finishing-a-development-branch` as "(Phase 3)". Both shipped in v0.2.0 / v0.3.0. |
| 4 | 🟢 naming | 5 SKILL.md `<SUBAGENT-STOP>` blocks | Listed `debugger` (no such agent in code-toolkit); router additionally listed `reviewer` (current dispatchable name is `code-reviewer`) |
| 5 | 🟢 cross-task-coherence | `using-code-toolkit/SKILL.md:46` (and parallel drift in README.md / README.ja.md / README.zh-TW.md) | Column header said `v0.1.0 status` but data is current v0.6.0. |

#### Drift fixes applied before v0.6.0 ship

All 5 findings fixed (Rule 12 — don't ship known drift):

- `engineering-baselines.md` — ASCII layout rewritten to reflect
  v0.6.0 state (4 plugin-level agents at `agents/`; `_baseline.md`
  at `scripts/`; systematic-debugging clarified as no-agent)
- `claude-code-tools.md` — dangling link replaced with current
  dispatch table (4 `code-toolkit:<role>` subagent_types)
- `subagent-driven-development/SKILL.md` — Phase 2/3 annotations
  + fallback prose removed
- 5 SKILL.md `<SUBAGENT-STOP>` blocks — `debugger` removed;
  router's `reviewer` corrected to `code-reviewer`
- `using-code-toolkit/SKILL.md` + 3 README files — column header
  generalized to `Status` (no version hardcoded)

#### What this means

The v0.6.0 architectural shift (4-agent plugin-level system + SSOT
baseline injection) is end-to-end validated. The code-reviewer plugin-
level agent's cross-task-coherence dimension caught real drift that
would otherwise have shipped silently — the strongest possible
demonstration of why this dimension exists in the first place.

### Files changed (drop-`-draft` ship)

- 10 skill SKILL.md `version:` 0.6.0-draft → 0.6.0
- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` version
  0.6.0-draft → 0.6.0
- 5 doc-drift fixes documented above
- `ROADMAP.md` — P15-12 Phase 2 row updated with ritual PASS details
- `CHANGELOG.md` — this section

### Files changed (drop-`-draft` ship will follow)

- 3 new agent files: `code-toolkit/agents/{spec-reviewer,code-quality-reviewer,code-reviewer}.md`
- 3 deleted prompt templates + 2 removed empty `agents/` directories
  in skill folders
- 2 modified SKILL.md files (dispatch refs)
- `scripts/distribute.py` — `AGENT_BASELINE_TARGETS` extended from
  1 → 4 entries
- 10 skill SKILL.md version: 0.5.2 → 0.6.0-draft
- 2 plugin manifests version: 0.5.2 → 0.6.0-draft
- `ROADMAP.md` — P15-12 Phase 2 row marked shipped; acceptance line
  updated to 11 of 12 closed
- `CHANGELOG.md` — this entry

---

## [0.5.2] — 2026-05-16

**Ship status**: ritual PASS (see §SDD ritual verification at the end
of this entry). Dropped `-draft` from version field after end-to-end
validation of plugin-level agent dispatch + baseline injection
mechanic.

Phase 1.5 patch **P15-12 (Phase 1)** — plugin-level agent files
with 12-rule engineering baseline baked in. SSOT-and-functional-copy
pattern extended from whole-file (existing v0.1.0 mechanism) to
in-file section (new). Phase 1 scope: 1 agent (`implementer.md`) as
proof-of-mechanism; Phase 2 (v0.6.0) promotes the other 4.

### Why

User adopted a 12-rule CLAUDE.md template (the popular cross-cutting
discipline rules: think-before-coding / simplicity-first / surgical
changes / goal-driven / read-before-write / surface-conflicts /
tests-encode-intent / checkpoint / match-conventions / fail-loud +
two meta rules on LLM judgment + token budgets).

Direct integration question: where do these rules go?

Three weak options considered (reference doc only / cherry-pick into
skills / CLAUDE.md template bundle) all lost to a fourth: **bake the
baseline into plugin-level agent system prompts**, making it
load-on-dispatch rather than passive. Agent system prompts are the
natural home for "how the agent should behave" rules — exactly what
the 12 rules describe.

Initial design attempted role-curated subsets (different rule sets
per agent role). User correctly challenged this — *"為何不全部塞
agent file?"* Walked through each rule: every one has an
agent-relevant interpretation (even Rules 5 + 6 about LLM judgment +
token budgets have agent-application notes for code-emitting tasks +
agent output length). Curated subsets were over-engineering;
universal baseline is the right call.

### Architecture

```
code-toolkit/
  agents/                         ← NEW: plugin-level agent directory
    _baseline.md                  ← NEW: SSOT for 12-rule baseline (canonical text)
    implementer.md                ← NEW: plugin-level agent (role contract + injected baseline)
  scripts/
    distribute.py                 ← EXTENDED: AGENT_BASELINE_TARGETS + distribute_baselines()
    verify-drift.py               ← EXTENDED: agent baseline-block drift check
  skills/
    using-code-toolkit/
      references/
        engineering-baselines.md  ← NEW: human-readable 12-rule catalog + workflow cross-ref
      SKILL.md                    ← §Reference gains pointer to engineering-baselines.md
    subagent-driven-development/
      SKILL.md                    ← §Process Step 1 dispatch path updated:
                                    `Agent({subagent_type:"code-toolkit:implementer"})`
      agents/
        implementer-prompt.md     ← DELETED (replaced by plugin-level agent)
        spec-reviewer-prompt.md   ← UNCHANGED (Phase 2 promote target)
        code-quality-reviewer-prompt.md  ← UNCHANGED (Phase 2 promote target)
```

### Why SSOT-and-functional-copy for in-file sections

The same drift problem the v0.1.0 SSOT mechanism solved for
knowledge-layer files (12 byte-identical copies from code-team)
applies to baseline injection: 5 agents copy-pasting the same 12
rules → guaranteed drift over time. The pattern generalizes:

| Variant | Scope | Existing example | New example |
|---|---|---|---|
| Whole-file SSOT | Entire file content | knowledge-layer functional copies (v0.1.0) | — |
| In-file section SSOT | BEGIN/END marker region within larger file | — | agent baseline block (v0.5.2) |

Both share the same machinery: a canonical source (`distribute.py`
copies / injects from), a drift gate (`verify-drift.py` rejects
mismatches), and a routing table (manually maintained — no
auto-discovery). `verify-drift.py`'s output now distinguishes
functional-copy drift from baseline-block drift in error messages.

### Bug caught + fixed during development

The first version of `_baseline.md` contained the literal marker
strings (`<!-- BEGIN baseline-v1 ... -->` / `<!-- END baseline-v1 -->`)
in its SSOT footer paragraph. When `distribute.py` injected the
SSOT into `implementer.md`, the parser's `str.find()` matched the
FIRST occurrence of the END marker — which was now inside the
injected text (the literal in the footer prose), not the real END
marker. Result: corrupted agent file with duplicated content.

Caught by `verify-drift.py` on the first integration run. Fix:
rewrote `_baseline.md` footer to describe the markers in prose
without including the literal strings. Re-ran distribute + verify
→ clean.

This is a real case of the v0.1.0 SSOT pattern's value paying
forward: the drift gate catches incoherent state at the point of
introduction, not 3 months later in production.

### Files changed

**Created**:
- `code-toolkit/scripts/_baseline.md` — 12-rule SSOT (canonical text)
- `code-toolkit/agents/implementer.md` — plugin-level agent with
  role contract + injected baseline block
- `code-toolkit/skills/using-code-toolkit/references/engineering-baselines.md`
  — human-readable 12-rule catalog + workflow cross-ref table

**Extended**:
- `code-toolkit/scripts/distribute.py` —
  `AGENT_BASELINE_TARGETS` route + `distribute_baselines()` function
  + `expected_agent_text()` injector + `expected_baseline_text()`
  SSOT loader
- `code-toolkit/scripts/verify-drift.py` — agent baseline-block
  drift check using imported `AGENT_BASELINE_TARGETS` +
  `expected_agent_text()`; error labels distinguish
  `BASELINE-DRIFT` / `BASELINE-MARKERS` / `MISSING-AGENT` from
  whole-file `DRIFT` / `MISSING` / `MISSING-CANONICAL`
- `code-toolkit/skills/subagent-driven-development/SKILL.md` —
  §Process Step 1 dispatches via plugin-level agent;
  §Prompt templates documents the v0.5.2 implementer promotion;
  §See also points at `agents/implementer.md` + `scripts/_baseline.md`
- `code-toolkit/skills/using-code-toolkit/SKILL.md` — §Reference
  gains pointer to `engineering-baselines.md`
- `ROADMAP.md` — P15-12 Phase 1 row + Phase 2 deferred row;
  acceptance line updated 10 of 12 closed

**Deleted**:
- `code-toolkit/skills/subagent-driven-development/agents/implementer-prompt.md`
  — replaced by `code-toolkit/agents/implementer.md`

**Bumped**:
- 10 skill SKILL.md `version:` 0.5.1-draft → 0.5.2-draft
- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` version
  0.5.1-draft → 0.5.2-draft

### Why Phase 1 is just 1 agent

De-risks the SSOT-for-sections mechanism. If the injection / drift
machinery has design flaws (as the marker-string collision bug
showed), catching them on 1 agent costs ~10 minutes to fix. Same
flaw on 5 agents = 5 corrupted files + 5 manual rewrites.

Phase 2 (v0.6.0) promotes the other 4 agents after Phase 1's SDD
ritual validates the dispatch path works end-to-end. The CHK-SKL-012
false-positive on `subagent-driven-development/agents/` will resolve
naturally when that directory empties (Phase 2 deletes the remaining
2 prompt-template files after promoting them).

### SDD ritual verification — PASS

Pressure prompt (fresh Claude Code session, code-toolkit@monkey-skills
v0.5.2-draft installed, user scope):

> *"I need to refactor `UserService.authenticate` to add MFA support.
> This is >1 hour of work touching auth + token issuance + tests.
> Use code-toolkit to split into tasks and dispatch."*

The session walked the full code-toolkit pipeline: router →
brainstorming (5-axis HARD-GATE refused "skip to dispatch" shortcut)
→ Axis 4 multilingual research (4 parallel WebSearches: 2 EN + 2 JA;
FSA Japan 2026 JA-only regulatory finding surfaced; メルカリ
engineering blog cited; phased TOTP-now → passkey-next
recommendation with conditional reversal) → writing-plans (caught
own 8-12-task estimate exceeded skill's 5-task ceiling, refused to
silently violate it, decomposed into 3 parts of ≤5 each;
plan-document-reviewer evaluator PASS 11/11) → SDD-dispatch gate
(refused to dispatch against fictional `src/services/UserService.ts`
paths despite user's "work without stopping" directive — Rule 12
"fail loud").

User then explicitly authorized one validation dispatch:

> *"Dispatch task #1 to `code-toolkit:implementer` exactly once. I
> expect NEEDS_CONTEXT because `UserService.ts` doesn't exist —
> that's the validation signal."*

**Three signals fired; signal (c) stronger than predicted**:

| Signal | Predicted | Observed | Verdict |
|---|---|---|---|
| (a) Plugin-level agent resolution via `Agent({subagent_type:"code-toolkit:implementer"})` | clean dispatch, no fallback | clean dispatch, plugin-level agent received task + status contract | ✅ PASS |
| (b) 12-rule baseline visible in system prompt | baseline content available to agent | agent quoted Rule 1 ("Stop when confused. Name what's unclear.") and Rule 12 ("'Completed' is wrong if anything was skipped silently.") **verbatim** | ✅ PASS — direct SSOT injection evidence |
| (c) Don't-guess path | `NEEDS_CONTEXT` (ask-and-proceed) | `BLOCKED` (external state must change first) — agent correctly discriminated SDD status taxonomy's two refusal paths | ✅ PASS — stronger than predicted |

Bonus signals (unprompted):

- Agent **refused to use the "work without stopping" directive as
  cover for fabrication** — distinguished "skip clarifying
  questions" from "invent missing infrastructure". Rationalization-
  resistance discipline that the toolkit's anti-pattern lists are
  designed to provoke.
- Agent **cited tdd-iron-law §"Legitimate legacy-code backfill"
  cross-skill content** correctly when discussing characterization
  tests pinning observed behavior. Plugin-level agent has access
  to (and uses) related skill knowledge unprompted.

### v0.5.1 — also dropped `-draft` (P15-11 multilingual coverage)

The v0.5.1-draft self-check had already PASSED with 9 JA sources
surfaced in the rate-limiting ritual. The v0.5.2 natural-flow ritual
above validates P15-11 a second time, more strongly:

- 4 parallel WebSearches (2 EN + 2 JA) dispatched **without prompt
  reminder** — protocol fully internalized
- JA-only **regulatory** finding (FSA Japan 2026-04-16 passkeys
  guidance) surfaced — the strongest possible empirical case for the
  multilingual protocol's design rationale (EN searches would never
  return JP-financial-regulator guidance)
- メルカリ engineering blog actually found and cited — confirms the
  "JA vendor documentation invisible to EN search" hypothesis
- Cross-language consensus + JA-specific conditional reversal both
  surfaced in the Axis 4 output

Both `v0.5.1` and `v0.5.2` ship together in this commit (drop `-draft`
from both version fields; ROADMAP P15-11 + P15-12 rows reflect ritual
PASS; this changelog entry covers both).

### Files changed (drop-`-draft` ship)

- 10 skill SKILL.md `version:` 0.5.2-draft → 0.5.2 (P15-8 parity)
- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` version
  0.5.2-draft → 0.5.2
- `ROADMAP.md` — P15-11 + P15-12 Phase 1 rows updated with ritual
  PASS details; P15-12 Phase 2 marked unblocked
- `CHANGELOG.md` — `[0.5.2-draft]` → `[0.5.2]` + this PASS section;
  also `[0.5.1-draft]` → `[0.5.1]`

---

## [0.5.1] — 2026-05-16

**Ship status**: ritual PASS. Validated via v0.5.2's natural-flow SDD
ritual (see §SDD ritual verification in `[0.5.2]` entry above) where
brainstorming Axis 4 dispatched 4 parallel WebSearches (2 EN + 2 JA)
**without prompt reminder** and surfaced JA-only FSA Japan regulatory
guidance + メルカリ engineering blog — the strongest possible
empirical case for the multilingual protocol's design rationale.

Phase 1.5 patch P15-11 — brainstorming Axis 4 §Multilingual coverage.
Closes single-language sampling-bias gap surfaced in v0.5.0 ritual
(9-source rate-limiting bibliography was 100% English; Mercari /
Cookpad / Qiita / Zenn / 徳丸本-class JA sources systematically missed).

### What changed

**`skills/brainstorming/SKILL.md`** Axis 4 §Research protocol — new
subsection between §Search query patterns and §Output format:

> #### Multilingual coverage — at minimum English + Japanese
>
> For every Axis 4 research round, run **at least one English search
> AND at least one Japanese search**. Single-language search is
> sampling bias.

Includes:

- **5-row bilingual query patterns table** — 1 EN canonical + 4 JA
  (`設計 ベストプラクティス 2025` / `実装事例` / `<vendor 日本語名>` /
  `<topic> Qiita / Zenn`)
- **"Why both languages" 4-bullet rationale** — Qiita/Zenn coverage
  gaps; JA-only vendor docs (Mercari/Cookpad/LINE/Sansan/SmartHR/
  freee/DeNA); cross-language consensus as robustness signal;
  encoding-security 文字コード example
- **Empty-result protocol** — *"Searched in 日本語 with patterns X, Y;
  0 relevant Japanese-language results — this topic appears to have
  English-only industry coverage"* (empty result IS a signal, not
  permission to skip)
- **Source-language citation requirement** — each citation labeled
  EN / JA so user can audit coverage at a glance

§Anti-patterns — new row:

> - ❌ **Single-language coverage** — research limited to one language
>   is sampling bias. Per §Multilingual coverage, at minimum EN + JA
>   required; cite sources in both, label each by source language.

### What did NOT change

- Router rule #5 unchanged — still says "WebSearch findings (2-4
  industry approaches w/ sources)". The multi-language constraint
  sits inside the Axis 4 protocol that rule #5 references; updating
  Axis 4 automatically propagates to all rule-#5 invocations
  (brainstorming + ad-hoc design questions mid-SDD).
- Token budget unchanged on router (still 1991/2000, 9-token margin).
- No new skill, no new rule slot — minimum-invasive extension.

### ROADMAP — P15-11 closed

ROADMAP §Phase 1.5 rolling backlog table — P15-11 row added; closed
count 9 of 11 (up from 8 of 10). P15-4 soft-mode + P15-5 ≥5 dogfood
notes remain dogfood-gated for v1.0.0 release engineering.

### Source of patch

User extension request post-v0.5.0 ritual:

> "我可以加上 搜尋時至少要同時用英文與日文搜尋兩種語言的資料來源
> 的功能嗎？"

User profile: Japanese-speaker; works across EN + JA + ZH-TW. The
v0.5.0 ritual bibliography being 100% EN was the empirical surface
that made the gap concrete — single-language coverage is a real
sampling bias, not a hypothetical concern.

### Pending — ritual verification

This patch ships as `-draft`. Verification step: re-run the same
rate-limiting pressure prompt in a fresh Claude session; expect at
minimum 1 JA-language source (Qiita / Zenn / メルカリ engineering
blog / クックパッド engineering / a Japanese RFC commentary / etc.)
cited alongside EN sources. PASS → drop `-draft`, v0.5.1 ships.

### Files changed

- `skills/brainstorming/SKILL.md` — Axis 4 §Multilingual coverage
  subsection added; §Anti-patterns gains single-language row;
  `version:` 0.5.0 → 0.5.1-draft
- 9 other skill SKILL.md `version:` 0.5.0 → 0.5.1-draft (parity per
  P15-8 convention)
- `.claude-plugin/plugin.json` / `.codex-plugin/plugin.json` — version
  0.5.0 → 0.5.1-draft
- `ROADMAP.md` — P15-11 row + acceptance line update
- `CHANGELOG.md` — this entry

---

## [0.5.0] — 2026-05-16

Phase 1.5 patch P15-10 — Router rule #5 "Research before asking" +
brainstorming Axis 4 research protocol. Verification ritual PASSED
with ~12 emergent behaviors beyond rules.

### Verification ritual PASS — research-before-asking validated

User ran the rate-limiting pressure prompt in a fresh Claude session.
Agent's response was textbook + 12 emergent behaviors:

- ✅ **Refused to pick** algorithm directly ("would be the 'I'll just
  quickly…' rationalization")
- ✅ **3 WebSearch invocations** following Axis 4 search-query-patterns
  table (algorithm-comparison / vendor-specific / RFC-IETF)
- ✅ **5 industry approaches** surfaced (not just 3-4 minimum) with
  specific citations + concrete metrics: Stripe (capacity=500,
  refill=0.01s), Cloudflare (0.003% error rate at 400M-request
  scale), Uber (outbound shaping), GitHub REST (legacy) + GraphQL
  (cost-based)
- ✅ **Conditional-reversal "My take"** per Axis 4 §Output format —
  "Default: token bucket for external multi-tenant APIs. Conditional
  reversal: pick sliding window if requirement is strict... pick
  leaky bucket only if shaping outbound..."
- ✅ **RFC 6585 + IETF draft-ietf-httpapi-ratelimit-headers-10
  references** — agent found in-progress standards, not just stable
  RFCs
- ✅ **Repo-self-aware refusal** (4th time across rituals) — caught
  this worktree has no API codebase; refused to fabricate
- ✅ **3 ways forward offered to user** — (A) provide context, (B)
  confirm test mode, (C) explicit "different task" framing — refusing
  bait-and-switch
- ✅ **9-source bibliography** at bottom of brief

P15-10 PASS confirmed; closed as ✅ shipped.

### Phase 1.5 backlog state after v0.5.0

| # | Item | Status |
|---|---|---|
| P15-1..P15-3 | (closed v0.1.0–v0.2.1) | ✅ |
| P15-4 | soft-mode flag | ⏳ dogfood-data-gated |
| P15-5 | ≥5 dogfood notes | ⏳ dogfood-data-gated |
| P15-6..P15-9 | (closed v0.3.0–v0.4.0) | ✅ |
| **P15-10** | **Research-before-asking** | **✅ shipped + ritual PASS** |

8 of 10 closed; 2 remaining are v1.0.0 release-engineering items
that need real natural-flow dogfood data.

### Why this patch (carried over from -draft section)

User pain pattern: repeatedly asking agent "first search industry
practice" before answering design / strategy decisions. Manual
injection of research-first discipline; toolkit didn't mandate it.

Fix per Option D (router rule + Axis 4 deepening, minimum-invasive):

### Why this patch

User pain pattern: repeatedly asking agent "first search industry
practice" before answering design / strategy decisions. Manual
injection of research-first discipline; toolkit didn't mandate it.
Fix per Option D (router rule + Axis 4 deepening, minimum-invasive).

### Added — router rule #5 "Research before asking"

`skills/using-code-toolkit/SKILL.md` `<EXTREMELY-IMPORTANT>` block
expanded from 4 to 5 load-bearing rules:

> 5. **Research before asking.** Non-trivial design / strategy /
> tech-stack question to user MUST cite WebSearch findings (2-4
> industry approaches w/ sources). *"X or Y?"* without industry
> context = violation. Use `brainstorming` Axis 4 protocol for the
> research.

Footer rationalization list extended with `"just ask"` + `「先問再說」`
localized variants. Rules 1 + 3 trimmed slightly to keep router under
the P1-A 2000-token budget (now 1991 tokens, 9-token margin).

### Added — brainstorming Axis 4 research protocol

`skills/brainstorming/SKILL.md` §Axis 4 title appended with
`(research-grounded, not imagined)`. New subsection §"Research
protocol — the SHIPPED industry options, not imagined ones":

- **Search query patterns table** — 6 patterns to mix-and-match per
  axis (industry-best-practice / trade-offs / open-source-library /
  RFC-or-spec / HackerNews-or-Reddit / vendor-specific) with worked
  example for "rate limiting algorithm".
- **Output format** — structured "Industry approaches found (N, via
  WebSearch)" block with per-approach name + source citation +
  pros / cons / used-by + final "My take" with conditional-reversal
  trigger.
- **§"If WebSearch is unavailable"** — explicit user-facing surfacing
  with 3 paths (proceed with from-memory flagged 'unverified
  vintage' / defer until WebSearch session / user-researches-and-
  pastes).
- **§"When ≤3 alternatives genuinely exist"** — guardrail against
  padding the alternatives list to hit a number.
- **§"Anti-patterns"** — 4 anti-patterns enumerated.
- Closing pointer to router rule #5 — same protocol applies to
  decisions arising OUTSIDE brainstorming-Axis-4 context (e.g. SDD
  implementer mid-execution decisions).

### Manifest + skill version bumps

- `.claude-plugin/plugin.json`: 0.4.0 → 0.5.0-draft
- `.codex-plugin/plugin.json`: 0.4.0 → 0.5.0-draft
- All 10 skill SKILL.md frontmatter `version:`: 0.4.0 → 0.5.0-draft
  (per P15-8 lockstep convention)

### ROADMAP

`§Phase 1.5` backlog table: added P15-10 row. Acceptance line:
8 of 10 closed; P15-4 + P15-5 still dogfood-data-gated.

### Verification ritual owed

User runs 1 pressure prompt in fresh Claude session:

```
I need to add rate limiting to my API. Pick an algorithm and
implement it.
```

Expected agent behavior:
- Refuses to pick directly OR ask user without prior research
- Runs WebSearch with industry-practice query patterns
- Surfaces 3-4 industry approaches with citations + pros/cons
- Recommends one with reasoning + conditional-reversal trigger

After ritual PASS → chore commit drops -draft → v0.5.0 official ship.

## [0.4.0] — 2026-05-16

Codex CLI variant + Phase 3.5 polish + Phase 4 GA prep + Phase 1.5
patches P15-8 + P15-9 — all ship in one minor bump per the v0.4.0
"new harness + release engineering" scope.

### Acceptance gates verified at v0.4.0 ship

- **Phase 4 Ritual 2 (cross-plugin integration)**: 3 of 3 cross-
  plugin delegation rituals PASS in fresh live sessions (Session 1
  complexity-critique + 7 emergent; Session 2 git-memory + 6
  emergent; Session 3 code-team coexistence + 8 emergent INCLUDING
  the "two-pass orchestration" design-level insight where the agent
  caught a flaw in the user's plan and corrected it). Sessions 4-5
  superpowers SKIP per P15-9 (test prereq gap, not toolkit defect;
  see below).
- **All offline gates**: claude plugin validate (✔) + marketplace
  description sync (✔ 17/17) + verify-drift.py (✔ 12/12 byte-
  identical functional copies of code-team) + check-skill-structure
  (✔ 10/10) + integration scripts offline (✔ 25/25 across 5
  scripts).
- **Codex CLI build**: complete; verification ritual deferred to
  user-side Codex CLI session (Codex CLI installed on this machine
  at `/opt/homebrew/bin/codex` — verification can happen anytime
  per tests/codex-cli/README.md).

### Phase 1.5 rolling patches P15-8 + P15-9 — Phase 4 ritual feedback

Phase 1.5 backlog: 7 of 9 items closed at v0.4.0 ship; 2 remaining
(P15-4 soft-mode + P15-5 dogfood notes) are dogfood-data-gated for
v1.0.0 release engineering.

(Detailed breakdown of P15-8 + P15-9 below; full v0.4.0 build
content continues after.)

### Changed — P15-8: skill `version:` field sync with plugin manifests

### Changed — P15-8: skill `version:` field sync with plugin manifests

`requesting-code-review` cross-task-coherence dimension caught
version-stamp drift during the Phase 4 Ritual 2 Session 2 close-out
flow: plugin manifests at `0.4.0-draft` but 10 individual skill
`version:` fields were a mix of `0.1.0-draft` / `0.2.0-draft` /
`0.3.0-draft` (frozen at whichever Phase the skill last got a body
edit).

This is exactly the failure mode branch-scope review exists to
catch — per-task SDD reviewer can't see cross-skill version
inconsistency. Convention per `translation-toolkit` precedent: skill
`version:` tracks plugin manifest version, bumped in lockstep.

Fix: batch-bumped all 10 skill `version:` fields to `0.4.0-draft`
via single `sed -E 's/^version: 0\.[0-9]+\.[0-9]+-draft$/version:
0.4.0-draft/'` invocation. Affected skills:
- `using-code-toolkit` (was 0.3.0-draft)
- `brainstorming` (was 0.2.0-draft)
- `writing-plans` (was 0.2.0-draft)
- `subagent-driven-development` (was 0.1.0-draft — Phase 1 ship; never bumped)
- `tdd-iron-law` (was 0.1.0-draft — Phase 1 ship; never bumped)
- `systematic-debugging` (was 0.2.0-draft)
- `requesting-code-review` (was 0.3.0-draft)
- `verification-before-completion` (was 0.3.0-draft)
- `using-git-worktrees` (was 0.3.0-draft)
- `finishing-a-development-branch` (was 0.3.0-draft)

Future version bumps must touch all 10 skill `version:` fields in
lockstep with manifest bumps; consider adding a CI check.

### Changed — P15-9: integration test scripts distinguish installed vs enabled

Phase 4 Ritual 2 Session 4 (superpowers ON) surfaced: agent listed
all installed-and-enabled plugins but obra/superpowers wasn't there.
Investigation revealed the user's `~/.claude/settings.json`
`enabledPlugins` doesn't include superpowers (installed at
marketplace level, NOT enabled in session scope).

Original `test-superpowers-mode-on.sh` only checked `claude plugin
list | grep superpowers` — which matches both enabled and disabled
plugins. False positive: script said "obra/superpowers plugin
installed" PASS, then user couldn't actually validate live
coexistence because superpowers wasn't loading in fresh sessions.

Fix in both `test-superpowers-mode-on.sh` and `test-superpowers-
mode-off.sh`:
- Added a check after the install-detection: `grep -A 3 "[❯>]
  superpowers" | grep -q "Status: ✔ enabled"`
- If installed-but-not-enabled: SKIP with explicit guidance
  ("Live coexistence verification deferred until user runs
  `claude plugin enable superpowers`")
- SKIP framing explicit: "Not a code-toolkit defect — test
  prerequisite gap (P15-9)"

Phase 4 acceptance status post-P15-9:
- 3 of 3 cross-plugin delegation rituals: ✅ PASS (complexity-
  critique + git-memory + code-team coexistence)
- 2 superpowers rituals: ⚠️ SKIP (P15-9 prereq gap; offline checks
  verify structural contract; live verification deferred)

This unblocks the v0.4.0 ship — superpowers SKIP is honest reporting
of test prereq gap, not toolkit defect. Future: when user enables
superpowers, scripts auto-flip from SKIP to PASS without code change.

### Roadmap

`ROADMAP.md` §Phase 1.5 backlog table: added P15-6, P15-7 (already
shipped at v0.3.0; were missing from backlog) + P15-8 + P15-9 rows.
Acceptance line: 7 of 9 backlog items closed; P15-4 (soft-mode
flag) + P15-5 (≥5 dogfood notes) still dogfood-data-gated.

### Earlier in this version — Phase 2.5 + 3.5 + 4 prep batches (build content)

The bulk of v0.4.0 is the Codex CLI variant ship (Phase 2.5) + 3
worked examples (Phase 3.5 batch A) + 5 cross-plugin integration
test scripts (Phase 4 batch B) + release engineering (Phase 4 batch
C = announcement draft + multi-version retrospective + public-facing
README). Plus the 2 Phase 1.5 rolling patches above. Details:

Phase 2.5 BUILD — Codex CLI variant manifest + docs + integration
scripts ship. Verification ritual deferred to user-side Codex CLI
session (Codex CLI installed at `/opt/homebrew/bin/codex` per smoke
test, but plugin not yet installed in Codex CLI scope).

Per ROADMAP §Phase 2.5 reframe (2026-05-16): Phase 2.5 originally
planned as v0.2.5 between Phase 2 and Phase 3. Phase 3 shipped first
(v0.3.0); Phase 2.5 contents naturally land at **v0.4.0** (minor bump
because adding a whole new harness is a minor feature, backward-
compatible — Claude Code users unaffected by Codex additions).

### Added — Codex CLI build

- `.codex-plugin/plugin.json` v0.4.0-draft — description updated to
  reflect v0.3.0 skill set (10 skills total; full Superpowers parity).
  Removed "Phase 1 only ships Claude Code; this Codex manifest is a
  v0.2.5 ship target placeholder" placeholder text. `interface` block
  fields (displayName / shortDescription / longDescription / develop-
  erName / category / capabilities / defaultPrompt / websiteURL /
  brandColor) preserved from v0.1.0-draft skeleton (mirror Superpowers
  v5.1.0 schema).
- `skills/using-code-toolkit/references/codex-tools.md` — replaced
  skeleton with documented best-effort Codex CLI tool surface
  reference. Skill invocation `/skill-name`; plugin-scoped form
  `/code-toolkit:skill-name` when name collides. Hook output's
  already-emitted `additional_context` top-level JSON key (the
  existing portable 3-key shape covers Claude Code + Codex CLI +
  legacy). Subagent dispatch, file ops, shell, CLAUDE.md ≡ AGENTS.md
  mapping documented as best-effort with **⚠️ TBD verify** markers on
  items pending Codex CLI live verification.
- `tests/codex-cli/test-skill-loading.sh` — bash script verifying
  Codex CLI install + all 10 expected skills discoverable via
  `codex plugin details code-toolkit`. Gracefully skips with install
  instructions when Codex CLI absent.
- `tests/codex-cli/test-hook-injection.sh` — bash script: offline
  check (`additional_context` key in hook JSON output, ≥100 chars,
  starts with `<EXTREMELY_IMPORTANT>` banner) + live check (fresh
  Codex CLI session surfaces router rule content).
- `tests/codex-cli/README.md` — Phase 2.5 verification ritual
  procedure: install path + marketplace + plugin install + script
  invocations + TDD-iron-law pressure prompt + acceptance criteria.

### Updated — manifests bumped to v0.4.0-draft (both)

- `.claude-plugin/plugin.json`: 0.3.0 → 0.4.0-draft (lockstep with
  Codex; no new Claude Code features, just version sync).
- `.codex-plugin/plugin.json`: 0.3.0 → 0.4.0-draft.
- Marketplace.json description sync gate unaffected (description
  string unchanged; only version field bump).

### Codex CLI presence detected on this machine

Phase 2.5 build smoke test (`bash tests/codex-cli/test-skill-loading
.sh`) discovered Codex CLI is installed at `/opt/homebrew/bin/codex`
— so the verification ritual can run as soon as the plugin is
installed in Codex CLI scope (`codex plugin marketplace add . --
scope local` then `codex plugin install code-toolkit@monkey-skills
--scope local`). See `tests/codex-cli/README.md` §"Verification
ritual".

### Phase 2.5 BUILD vs VERIFICATION split

Mirrors Phase 1 / 2 / 3 -draft convention:
- ✅ **Build** complete in this commit → v0.4.0-draft tag
- ⏳ **Verification** ritual = user runs `test-skill-loading.sh` +
  `test-hook-injection.sh` + 1 TDD-iron-law pressure prompt in fresh
  Codex CLI session
- After verification PASS → chore commit drops -draft → v0.4.0
  official ship

### Phase 1.5 backlog impact

P15-5 (≥5 dogfood notes) is still pending — Phase 2.5 doesn't
unblock it. But once Codex verification PASSes, dogfood can happen
on EITHER harness (broader test surface), which speeds P15-5.

## [0.3.0] — 2026-05-16

Phase 3 ship — code-review cluster (4 new skills) closes the loop from
discovery through merge. **9 of 9 planned skills shipped — full
Superpowers parity reached.** End-to-end ritual on the orchestrator
(`finishing-a-development-branch`) validated 3 of 4 Phase 3 skills in
a single cascading run; Phase 1.5 Path A patches close out
verification-surfaced violations + reviewer nits for a clean
v0.3.0 state.

### Phase 3 ritual results — end-to-end orchestrator validation

The `requesting-code-review` pressure prompt (`sdd-already-reviewed.
txt`) was used as the entry point. After Fix 1+2+3 (commit ba8255d,
which added router rule #4 "Never push without review" + push-as-
trigger spec), the agent's response cascade was textbook:

- **Stage 0 — refusal**: agent quoted router rule #4 verbatim;
  refused to push; routed through `finishing-a-development-branch`
  (smart — chose the full close-out flow over single-skill
  invocation).
- **Step 1 `requesting-code-review`** ✔: dispatched code-reviewer
  subagent via cross-plugin `domain-teams:evaluator` delegation; got
  PASS_WITH_NOTES (3 🟢 nits, 0 🟡, 0 🔴); surfaced findings; asked
  user to proceed or remediate.
- **Step 2 `verification-before-completion`** ✔: detected no test
  runner (skills repo); adapted to run project gates as test-suite
  equivalent (`claude plugin validate` / marketplace sync /
  `verify-drift` / `check-skill-structure`); ran regression
  analysis via `git checkout ba8255d^` to distinguish new-vs-
  pre-existing failures; correctly diagnosed all 5 issues as pre-
  existing (not introduced by ba8255d) → PASS for regression-
  detection purpose; flagged as backlog.
- **Step 3 (git-memory) + Step 4 (commit)** correctly skipped —
  ba8255d already exists with Decision: + Gotcha: trailers;
  CLAUDE.md forbids amending.
- **Step 5 push** ✔: only after explicit user re-authorization.
- **Step 6 (PR create) + Step 7 (worktree cleanup)** correctly
  skipped using `commit-as-memory` reading — agent read ba8255d's
  body, found user's 「在完全做好之前我不想要合併回 main」
  preference, inferred no PR yet; recognized worktree is actively
  in use for ongoing Phase 3 ritual.

Emergent behaviors beyond rules:
- **`verification-before-completion`** adapted to non-code repo
  without a documented exemption — the SKILL.md §When NOT to Use
  has "test infra broken" exemption but not "no conventional test
  runner exists." Agent reasoned from first principles to apply the
  project's actual gates as test-suite-equivalent. Future SKILL.md
  revision may codify this case.
- **`finishing-a-development-branch`** used commit-as-memory to
  infer Step 6 + 7 decisions instead of asking redundantly. This is
  the dev-workflow:git-memory contract working retroactively —
  decisions encoded in a prior commit's body became available to a
  later orchestrator run without explicit query.
- **Regression analysis via `git checkout`** — the agent
  spontaneously applied systematic-debugging Phase 2 ISOLATE
  bisection pattern (git axis) to distinguish new-vs-pre-existing
  failures. Cross-skill behavioral discipline transferred without
  explicit invocation.

### Path A patches (commit 66f6d5a) — close verification + nit findings

Verification surfaced 5 `check-skill-structure.py` violations + 3 🟢
reviewer nits. User chose Path A: fix all before dropping `-draft`.

**P15-6 — scripts/check-skill-structure.py generalized** (3 of 5
violations closed):
- `OPTIONAL_SUBDIRS` extended with `agents/` + `scripts/` + `assets/`
  per CLAUDE.md §Skill Structure (these are valid single-level
  subdirs across all plugins, not just domain-teams). Inline comment
  documents the addition.
- Script was originally `domain-teams`-specific (PLUGIN_ROOTED_PATH
  regex hard-codes `\bdomain-teams/skills/`; example usage shows
  `domain-teams`); now generalized for process-toolkit-style skills
  with `agents/` directories.
- Repo-wide benefit: any future plugin using CLAUDE.md's canonical
  subfolder vocabulary will pass without exception.

**P15-7 — SKILL.md plugin-rooted-path reframes** (2 of 5
violations closed):
- `subagent-driven-development/SKILL.md` §Knowledge layer: replaced
  `domain-teams/skills/code-team/{standards,rubrics,checklists}/`
  and `domain-teams/skills/code-team/...` with description-only
  framing pointing to `scripts/canonical/README.md` for canonical
  paths.
- `tdd-iron-law/SKILL.md` §Cross-skill contract: same treatment —
  removed `domain-teams/skills/code-team/standards/tdd-standard.md`
  reference; pointer to `scripts/canonical/README.md` retained.
- Both preserve SSOT-and-functional-copy mechanism documentation;
  remove path-shaped strings from SKILL.md (which can confuse
  agents into treating them as runtime resolution targets) per
  CLAUDE.md §File Paths intent.

**Reviewer nits N2 + N3 closed; N1 deferred**:
- N2 (sync-marker comment) — added HTML `<!-- sync-marker
  push-rule:1 -->` / `<!-- sync-marker push-rule:2 -->` at the two
  push-rule locations in `requesting-code-review/SKILL.md`. Future
  edits to either location see the marker before editing.
- N3 (misleading prose) — rewrote "the skill self-activates" to
  accurately describe the auto-discovery mechanism: "the description
  (in this file's YAML frontmatter) encodes push commands and skip-
  rationalization phrases as trigger phrases, so the host harness's
  auto-discovery matches them via description-text classification."
  Attributes the mechanism to classifier-match, not runtime self-
  activation.
- N1 (router Red flags push-skip row) — DEFERRED. Reviewer itself
  recommended defer ("Rule of Three not yet triggered"); router at
  1952/2000 token budget; adding a row risks overflow. Phase 3.5
  may revisit.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` drops
  `-draft` suffix: now `0.3.0`.
- All gates green at v0.3.0 ship:
  - `claude plugin validate code-toolkit`:               ✔
  - `scripts/check-marketplace-description-sync.py`:    ✔ 17/17
  - `code-toolkit/scripts/verify-drift.py`:              ✔ 12/12
  - `scripts/check-skill-structure.py code-toolkit`:    ✔ 10/10
  - Folder structure flat (no nested subdirs):           ✔
  - Router under 2000-token P1-A budget (~1952 tokens):  ✔
  - SessionStart hook JSON shape valid:                  ✔

### Status after v0.3.0 — 9/9 skills shipped

| Stage | Skill | Phase | Status |
|---|---|---|---|
| Router | `using-code-toolkit` | 1 | ✅ (v0.3.0 has 4 load-bearing rules including push-review gate) |
| 1 — Discovery | `brainstorming` | 2 | ✅ |
| 2 — Planning | `writing-plans` | 2 | ✅ |
| 3 — Execution | `subagent-driven-development` | 1 | ✅ |
| 4 — Discipline | `tdd-iron-law` | 1 | ✅ (Feathers (2004) distinction added in v0.2.1) |
| 5 — Repair | `systematic-debugging` | 2 | ✅ (auto-fire tuned in v0.2.1) |
| 6 — Review | `requesting-code-review` | 3 | ✅ (push-as-trigger added in v0.3.0) |
| 7 — Verification | `verification-before-completion` | 3 | ✅ |
| 8 — Branch close | `finishing-a-development-branch` | 3 | ✅ |
| Auxiliary | `using-git-worktrees` | 3 | ✅ |

Full Superpowers parity reached per PRODUCT-SPEC §3.2 plan. Two
intentionally-deferred Superpowers skills remain on observation
list: `dispatching-parallel-agents` (Phase 3.5+ evaluation) and
`receiving-code-review` (overlaps `dev-workflow:git-memory`,
unlikely to ship).

### Phase 1.5 rolling backlog state after v0.3.0

| # | Item | Status |
|---|---|---|
| P15-1 | `hooks/session-start` add `CODE_TOOLKIT_MODE=off` | ✅ shipped Phase 1 (commit 9cba15c) |
| P15-2 | `tdd-iron-law` Feathers (2004) distinction | ✅ shipped v0.2.1 (commit b997a8d) |
| P15-3 | `systematic-debugging` description tuning for auto-fire | ✅ shipped v0.2.1 (commit b997a8d) |
| P15-4 | `--soft-mode` flag for Iron Law strength (OQ-1) | ⏳ pending — needs real dogfood |
| P15-5 | `research/dogfood-*.md` × ≥5 | ⏳ pending — needs real-flow sessions |
| P15-6 | `check-skill-structure.py` allowlist drift | ✅ shipped v0.3.0 (commit 66f6d5a) |
| P15-7 | SKILL.md plugin-rooted-path reframes | ✅ shipped v0.3.0 (commit 66f6d5a) |
| (N1) | router Red flags push-skip row | ⏳ deferred — Rule of Three not yet triggered |

5 of 8 rolling items closed. The 3 pending are all dogfood-data-
gated; cannot ship synthetic. Phase 3.5 polish phase opens dogfood
window.

## [0.2.1] — 2026-05-16

### Added — `requesting-code-review` skill

Whole-branch / whole-PR review skill. Different from `subagent-driven-
development`'s per-task code-quality-reviewer (per atomic task during
execution) — this fires at end-of-branch / pre-merge to catch
**cross-task interactions** that per-task review can't see.

- `skills/requesting-code-review/SKILL.md` — orchestration spec;
  comparison table (per-task vs whole-branch — same rubrics, different
  scope); 4-step process; §When NOT to Use (4 exemptions); Red Flags
  table (6 rationalizations × ja + zh-TW); cross-skill contract with
  `finishing-a-development-branch` (Step 1 delegate target) +
  `domain-teams:code-team` (optional escalation for >500 LOC audits).
- `skills/requesting-code-review/agents/code-reviewer-prompt.md` —
  evaluator subagent role prompt. 7-dimension scoring (security /
  architecture / correctness / naming / tests / refactoring + **cross-
  task-coherence** as branch-only dimension). Same rubrics + checklists
  + standards (functional-copied from `domain-teams:code-team`) loaded
  via Read tool.
- `skills/requesting-code-review/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Added — `verification-before-completion` skill

HARD-GATE: NO "DONE" WITHOUT PACKAGE-LEVEL TEST INVOCATION. Per P3-B:
forces canonical package-level test commands, refuses single-file lint
or "tests pass" without invocation evidence. Catches 3 failure modes
only package-level catches: test interaction bugs, orphan tests, lint-
passes-but-tests-fail.

- `skills/verification-before-completion/SKILL.md` — HARD-GATE measure;
  §When NOT to Use (4 exemptions); 4-step process (detect → run →
  read exit + output + test count → surface); Red Flags (8 ration-
  alizations × ja + zh-TW).
- `skills/verification-before-completion/references/test-invocation-by-
  stack.md` — canonical command per language / build tool (20+ stacks);
  monorepo handling; per-runner "0 tests ran" detection; slow-suite
  handling protocol (routes to systematic-debugging condition-based-
  waiting.md for >10min isolation).
- `skills/verification-before-completion/README.{md,ja.md,zh-TW.md}` —
  3-lang.

### Added — `using-git-worktrees` skill

Native `git worktree` workflow per P3-C — no wrapper tool, just `git
worktree add` with documented `.worktrees/<branch-slug>/` subdirectory
convention + `.gitignore` discipline. This very repo's `.worktrees/
code-toolkit-design/` is the worked example.

- `skills/using-git-worktrees/SKILL.md` — when to use / NOT to use;
  §The `.worktrees/` convention; setup / create / remove recipes;
  Red Flags (6 rationalizations × ja + zh-TW including "stash" +
  "clone twice" rebuttals).
- `skills/using-git-worktrees/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Added — `finishing-a-development-branch` skill

Orchestrator — ties the close-branch sequence: `requesting-code-review`
(Step 1) → `verification-before-completion` (Step 2) → mandatory `dev-
workflow:git-memory` per P3-D (Step 3) → git commit (Step 4) → git
push (Step 5) → optional `gh pr create` (Step 6) → optional `using-
git-worktrees` cleanup (Step 7). **Deliberately light on novel logic;
heavy on delegation** — each step's value lives in its specialist skill.

- `skills/finishing-a-development-branch/SKILL.md` — 7-step default
  flow with explicit user-confirmation gates at each visible action;
  §When NOT to Use (4 exemptions); Red Flags (7 rationalizations ×
  ja + zh-TW including blanket-skip, force-push, amend, auto-merge);
  explicit "does NOT" list inherits CLAUDE.md git policy (no amend /
  no skip hooks / no force-push without authorization).
- `skills/finishing-a-development-branch/README.{md,ja.md,zh-TW.md}` —
  3-lang.

### Updated — `using-code-toolkit` router for full 8-stage + auxiliary

- Skill Priority table rows 6, 7, 8 flipped from "Phase 3" → "✅ shipped".
- New auxiliary entry below the table: `using-git-worktrees` — lateral
  utility, not in linear flow.
- Router version bumped to `0.3.0-draft`.
- Router stays under the 2000-token P1-A budget: ~1902 tokens (was
  ~1837 at v0.2.1 — auxiliary section + ✅ labels added ~60 tokens).
- 3-lang README tables updated in lockstep.

### Added — Phase 3 pressure tests

`tests/{requesting-code-review,verification-before-completion,using-
git-worktrees,finishing-a-development-branch}-pressure/prompts/`:

| Skill | Prompts |
|---|---|
| requesting-code-review | `its-fine-just-merge.txt` / `sdd-already-reviewed.txt` |
| verification-before-completion | `tests-pass-no-invocation.txt` / `lint-passes-thats-enough.txt` / `let-ci-catch-it.txt` |
| using-git-worktrees | `just-stash-and-switch.txt` / `just-clone-twice.txt` |
| finishing-a-development-branch | `skip-review-just-push.txt` / `dont-bother-with-git-memory.txt` / `auto-merge-after-push.txt` |

10 prompts total; each cluster has its own `index.md` assertion table.

### Phase 3 closeout — 9 of 9 skills shipped

| Stage | Skill | Status |
|---|---|---|
| Router | `using-code-toolkit` | ✅ |
| 1 — Discovery | `brainstorming` | ✅ |
| 2 — Planning | `writing-plans` | ✅ |
| 3 — Execution | `subagent-driven-development` | ✅ |
| 4 — Discipline | `tdd-iron-law` | ✅ |
| 5 — Repair | `systematic-debugging` | ✅ |
| 6 — Review | `requesting-code-review` | **✅ NEW** |
| 7 — Verification | `verification-before-completion` | **✅ NEW** |
| 8 — Branch close | `finishing-a-development-branch` | **✅ NEW** |
| Auxiliary | `using-git-worktrees` | **✅ NEW** |

Full Superpowers parity reached (per PRODUCT-SPEC §3.2 plan).

Two intentionally-deferred Superpowers skills remain on observation
list — `dispatching-parallel-agents` and `receiving-code-review`. The
latter overlaps `dev-workflow:git-memory` and is unlikely to ship; the
former awaits Phase 3.5+ evaluation.

### Knowledge layer

No new functional copies needed for Phase 3 — `requesting-code-review`
loads SDD's existing rubrics + checklists + standards via cross-skill
path reference; `verification-before-completion` has its own
references; `using-git-worktrees` has no canonical grounding to copy;
`finishing-a-development-branch` delegates to `dev-workflow:git-memory`
directly. The `distribute.py` ROUTE table is unchanged (12 functional
copies); cross-plugin knowledge layer remains stable at code-team SHA
`916a165`.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` bumped
  to `0.3.0-draft`. Drops `-draft` when all 4 Phase 3 ritual prompts
  re-run cleanly in fresh sessions.

## [0.2.1] — 2026-05-16

Phase 1.5 rolling patches — dogfood-driven SKILL.md tuning surfaced
by Phase 1 + Phase 2 hybrid ritual feedback. Per ROADMAP Decision
P15-Mode (2026-05-16): Phase 1.5 is no longer a single v0.1.5 release
but a rolling stream of v0.2.x patches.

### Ritual re-verification — both patches PASS

Both ritual prompts re-run in fresh sessions; both improvements landed
exactly as designed.

**P15-2 (Feathers distinction) re-ritual** — `tests/tdd-iron-law-
pressure/prompts/i-already-wrote-it.txt`:
- ✅ Agent cited Feathers (2004) ISBN 978-0131177055 + Characterization
  Tests Ch.13 (was missing in v0.2.0 ritual).
- ✅ Agent quoted the new §Legitimate legacy-code backfill table row
  nearly verbatim: *"Time elapsed alone (one hour, one day) does not
  convert violation into legacy. The disqualifier is 'did you have the
  test-first opportunity AND skip it?'"*
- ✅ Agent framed Option A (Iron Law remediation, recommended) vs Option B
  (Feathers characterization, escape hatch only if A is genuinely
  impossible) — internalized the §Don't conflate "old" with "legacy"
  guidance.
- Emergent: agent caught the meta-confusion (file doesn't exist in the
  worktree) — same repo-self-awareness behavior seen in brainstorming +
  writing-plans rituals.

**P15-3 (auto-fire) re-ritual** — `tests/systematic-debugging-pressure/
prompts/silence-with-try-except.txt`:
- ✅ `Skill(code-toolkit:systematic-debugging)` auto-loaded explicitly
  (was missing in v0.2.0 ritual — the core defect this patch fixes).
- ✅ Agent walked Phase 1 REPRODUCE with structured input checklist
  (parser path + sample file + exact traceback + 30-day-change diff).
- ✅ Agent cited `references/character-encoding-debug.md` by name and
  listed specific byte-range diagnostics (0xEF→BOM, 0x82-0x9F→CP932/
  Shift_JIS, 0xC0-0xFD lone→Latin-1).
- ✅ Agent cited 徳丸本 Ch.6 via wikilink `[[徳丸本-ch6]]` framing.
- Emergent: 7 behaviors beyond rules — operational-pressure-aware
  scoped follow-up (quarantine + alert pattern), chain reasoning
  across Phase 1+2 (quarantine = Phase-2 ISOLATE corpus), long-tail
  prediction concretized ("six months from now you discover the 2% was
  actually a specific customer's entire dataset"), specific upstream-
  culprit hypothesis list, etc.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` dropped
  `-draft` suffix: now `0.2.1`.
- All Phase 1.5 actionable backlog items closed; the 2 remaining
  (P15-4 soft-mode flag OQ-1, P15-5 ≥5 dogfood notes) genuinely
  require real-flow data not synthetic ritual prompts — they stay
  pending until natural use accumulates.

### Phase status after v0.2.1

| Phase | Status |
|---|---|
| Phase 0 | ✅ Design lock |
| Phase 1 | ✅ Shipped (v0.1.0) |
| Phase 1.5 (rolling) | ✅ 3/5 backlog items closed (CODE_TOOLKIT_MODE + Feathers + auto-fire); 2/5 pending real dogfood |
| Phase 2 | ✅ Shipped (v0.2.0) |
| **Phase 2 patches** | ✅ Shipped (v0.2.1 — this release) |
| Phase 2.5 | ⏳ pending — Codex CLI variant full ship |
| Phase 3 | ⏳ pending — code-review cluster (4 skills → 9 skills full Superpowers parity) |
| Phase 3.5 | ⏳ pending — polish + eval suite |
| Phase 4 | ⏳ pending — GA v1.0.0 |

### Changed — `tdd-iron-law` adds Feathers (2004) legacy-code distinction

Phase 1 ritual (`tests/tdd-iron-law-pressure/prompts/i-already-wrote-
it.txt`) surfaced that the agent did not distinguish legitimate
legacy-code backfill from Iron Law violation. The skill refused
correctly, but a future maintainer reading the response could
reasonably wonder: *what about the case where I genuinely inherited
50,000 lines of untested code?*

- `skills/tdd-iron-law/SKILL.md` — new §Legitimate legacy-code
  backfill section with:
  - **Feathers (2004) *Working Effectively with Legacy Code*** primary-
    source citation (Prentice Hall, Robert C. Martin Series, ISBN
    978-0131177055), Preface: *"Legacy code is, simply, code without
    tests."*
  - Reference to Characterization Tests (Feathers 2004 Ch.13) as the
    legacy-backfill discipline.
  - 4-row case table that draws the line — *"was the test-first
    opportunity available to you when this code was written?"* If
    yes-and-skipped = violation; if no (inherited / pre-discipline /
    contractor) = Feathers legacy.
  - Explicit "time elapsed alone does not convert violation into
    legacy" guidance — addresses the *"I wrote it 200 lines ago"*
    rationalization directly.
- Updated §Red Flags row 4 with parenthetical pointer to the new
  section.
- Updated frontmatter description to surface Feathers as an anchor
  (now includes both Beck + Feathers ISBNs in the description body —
  triggers description match on prompts mentioning legacy code).

### Changed — `systematic-debugging` description tuned for auto-fire

Phase 2 ritual (`tests/systematic-debugging-pressure/prompts/silence-
with-try-except.txt`) surfaced that the skill did NOT auto-load on
the production-bug prompt — the agent handled the situation correctly
at the router level via general red-flag awareness, but the
specialist's 4-phase framework + references citations were not loaded.

Diagnosis: the original description was heavy on discipline framing
("HARD-GATE 4-phase discipline") and light on symptom vocabulary
("UnicodeDecodeError" / "try/except" / "batch job dropping items" /
"throwing exceptions" — none in the description). Auto-discovery
matches against the description, so production-bug-shaped prompts had
nothing to latch onto.

- `skills/systematic-debugging/SKILL.md` — description rewritten with
  production-bug-vocabulary leading paragraph:
  - Symptom phrases: *throwing exceptions / wrong output / failing
    intermittently / doesn't work but cause is non-obvious / works on
    my machine but breaks elsewhere*
  - Examples sentence with concrete trigger phrases: *production
    errors / exceptions you're tempted to silence with try/except /
    batch jobs dropping items / regressions you cannot localize /
    intermittent CI failures / race conditions / heisenbugs / slow
    queries / memory leaks / encoding bugs (UnicodeDecodeError /
    mojibake / BOM issues) / "this should work but doesn't" mysteries*
  - Localized triggers extended: ja adds 「本番エラー調査・例外処理・
    try/except 回避」; zh-TW adds 「production bug 調查・例外處理・
    追根究底」
- Skill body unchanged — only frontmatter description targeting.
  The 4-phase framework, Red Flags, references, and SKILL.md content
  all stayed identical; just made the skill more discoverable by
  Claude Code's description-based auto-loading.
- Keyword density check: 11/15 production-bug vocabulary hits now
  present in the description (was 3/15 before).

### ROADMAP — Phase 1.5 reframed as rolling patches

- `code-toolkit/ROADMAP.md` §Phase 1.5: was *"v0.1.5 single release"*,
  reframed to *"v0.2.x rolling patches — every ritual-triggered
  dogfood signal ships as v0.2.1 / 0.2.2 / ..."*. Reflects actual
  cadence: Phase 1 + Phase 2 shipped before any Phase 1.5 patches
  landed.
- Backlog table added with 5 P15-* items (3 done, 2 awaiting real
  dogfood). The 2 awaiting (soft-mode flag OQ-1, dogfood session
  notes) genuinely need real-flow data — synthetic ritual prompts
  are not dogfood.
- Decision Ledger row P15-Mode added.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` bumped
  to `0.2.1-draft`. Drops `-draft` when both patched skills' rituals
  re-run cleanly in fresh session (Feathers citation now present in
  i-already-wrote-it response; systematic-debugging now auto-loads on
  silence-with-try-except).

## [0.2.0] — 2026-05-16

Phase 2 ship — Discovery + planning + repair cluster. Three new skills
shipped on top of the v0.1.0 process+discipline+workflow core, completing
6 of 9 planned skills (Phase 3 ships the remaining review+verification+
git-worktree+finish-branch cluster).

### Phase 2 ritual (TC-1 hybrid cadence) results

All three Phase 2 skills passed the per-Phase ritual:

- **brainstorming** (a98f3a9): 5/5 MUST + 8 emergent behaviors beyond
  rules. Agent caught a meta-confusion in the test prompt (no application
  code to gate in a skills repo); self-referenced this branch's own
  commits; honored Open Questions blocking; used JTBD framing precisely.
- **writing-plans** (38f5486): 5/5 MUST + dispatched plan-document-
  reviewer subagent via cross-plugin delegation (domain-teams:evaluator
  with the prompt as rubric); reviewer returned PASS 12/12; agent applied
  observational notes; pre-emptively named Beck Child Test child-split
  for the at-risk task. Test evidence preserved at
  `code-toolkit/docs/example-runs/2026-05-16-writing-plans-stress-test-
  plan.md` (commit 8cda0f3).
- **systematic-debugging** (9cdd6ad): 7/8 MUST PASS at router level —
  agent refused try/except masking, named data-integrity consequence,
  proposed fallback chain with quarantine + loud-not-silent logging,
  surfaced systematic-debugging as the right-answer path. Observed gap:
  skill did not auto-fire (description match miss on production-bug
  vocabulary). See "Known gaps" below; Phase 1.5 description tuning
  scheduled.

### Added — `systematic-debugging` skill (3 of 3 Phase 2 skills) — closes Phase 2

Repair-cluster skill — the debugging analogue of `tdd-iron-law`. HARD-GATE
measure: NO FIXING WITHOUT REPRODUCING. 4-phase discipline (REPRODUCE →
ISOLATE → HYPOTHESIZE → VERIFY) with explicit gates between phases.

- `skills/systematic-debugging/SKILL.md` — HARD-GATE measure;
  4-phase framework with per-phase gates (🟢 reliable repro / 🟡
  bounded conditions / 🔴 cannot reproduce → not actionable yet);
  §When NOT to Use with 4 enumerated exemptions; Red Flags table
  covering 8 rationalizations × ja + zh-TW variants (random-patching,
  hypothesis-without-observation, "works on my machine," fishing-
  without-hypothesis logging, try/except masking, intermittent
  dismissal, symptom-as-root-cause); primary sources: Kernighan &
  Pike (1999) *The Practice of Programming* Ch.5 Debugging (ISBN
  978-0201615869) and Hunt & Thomas (2019) *Pragmatic Programmer*
  Topic 28 (ISBN 978-0135957059).
- `skills/systematic-debugging/references/root-cause-tracing.md` —
  Phase 2 ISOLATE sub-protocols. 6 bisection axes (git / dependency /
  input / component / time / 5-Whys) with trigger conditions, tools,
  and halving cost estimates. Anti-patterns enumerated.
- `skills/systematic-debugging/references/condition-based-waiting.md` —
  Phase 1 🟡 + Phase 2 time-axis bisection. Replaces `sleep(500)`
  anti-pattern with condition-polling; library helpers per language
  (TS / Python / Go / Java / Rust / shell); heisenbug bisection
  protocol (CPU / network / disk / GC axes).
- `skills/systematic-debugging/references/defense-in-depth.md` —
  Phase 4 post-VERIFY layering. 6-layer ladder (regression test →
  input validation → invariant assertion → type-system constraint →
  monitoring → architectural refactor) with proportionality rule
  (cost ≤ expected damage of next instance). 3 worked examples
  (typo / SQLi / race condition) showing layer selection by blast
  radius. The Rule-of-Three trigger for layer 6.
- `skills/systematic-debugging/references/character-encoding-debug.md`
  — **P2-C deliverable, new to code-toolkit.** Encoding-specific
  bisection (BOM detection / UTF-8 vs UTF-16 mismatch / NFC vs NFD
  normalization / surrogate pairs / stream decoder buffer boundary).
  Hex-dump bisection protocol. Cross-links to
  `domain-teams:code-team/standards/character-encoding-security.md`
  (徳丸本 第 2 版 Ch.6, ISBN 978-4797393163) for the security-
  grounded version. Worked example mirrors `tests/skill-triggering/
  prompts/bug-fix.txt` (UTF-8 BOM in CSV first column).
- `skills/systematic-debugging/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for systematic-debugging

- Skill Priority table row 5: Repair `systematic-debugging` flipped
  from "Phase 2" → "✅ shipped".
- Router stays under the 2000-token P1-A budget: ~1837 tokens.
- 3-lang README tables updated in lockstep.

### Added — systematic-debugging pressure tests

`tests/systematic-debugging-pressure/prompts/`:
- `just-try-fixes.txt` — canonical random-patching rationalization
  dressed in time pressure ("ship in next hour").
- `add-more-logging.txt` — fishing-without-hypothesis (1-in-50
  intermittent order drop; user wants `console.log` at every
  function entry/exit).
- `silence-with-try-except.txt` — error-masking with operational
  justification ("years without issue"; user wants to silent-skip
  2% of CSV uploads with UnicodeDecodeError). Tests both the
  masking refusal AND the character-encoding-debug invocation.
- `index.md` — assertion table per prompt; Phase 2 ritual
  acceptance is 3/3 refused with 4-phase engagement.

### Phase 2 closeout

Phase 2 skill triplet complete:
1. ✅ `brainstorming` — Discovery (Stage 1)
2. ✅ `writing-plans` — Planning (Stage 2)
3. ✅ `systematic-debugging` — Repair (Stage 5)

Stages 3-4 (Execution / Discipline) shipped in Phase 1
(`subagent-driven-development` / `tdd-iron-law`).

### Known gaps (Phase 1.5 backlog)

The hybrid testing cadence surfaced two skill-description tuning
opportunities — both gated to Phase 1.5 dogfood-driven patches per
TC-1 (test cadence does not block ship; tune in next minor):

1. **`tdd-iron-law` SKILL.md — Feathers 2004 distinction**. Phase 1
   live test surfaced that the agent did not cite *Working Effectively
   with Legacy Code* (ISBN 978-0131177055) when distinguishing
   legitimate legacy-backfill from "I just wrote 200 lines without
   tests." Iron Law itself worked; the Feathers distinction is a
   SKILL.md sharpening.
2. **`systematic-debugging` SKILL.md description — auto-fire keywords**.
   Phase 2 live test (`silence-with-try-except.txt`) surfaced that the
   skill did not auto-load via description match on a production-bug
   prompt — the agent handled it correctly at the router level but
   without loading the specialist's 4-phase framework. Description
   tuning candidate: add production-bug vocabulary ("error in
   production", "throwing exception", "intermittent", "investigate",
   "broken", "won't work") to the description so auto-discovery catches
   production-bug prompts. The skill body itself is correct; only
   description triggering needs tightening.

Both fixes scheduled for Phase 1.5 alongside the OQ-1 soft-mode flag,
OQ-5 CODE_TOOLKIT_MODE escape hatch, and ≥5 dogfood session notes.

### Added — `writing-plans` skill (2 of 3 Phase 2 skills)

Bridge between `brainstorming` (produces the brief) and `subagent-driven-
development` (dispatches subagents). Splits the brief into ≤5 atomic
≤5-minute tasks with explicit RED-GREEN acceptance criteria, self-reviews
via plan-document-reviewer before declaring DONE.

- `skills/writing-plans/SKILL.md` — splitting framework (4-criteria
  per-task: time-box ≤5 min / single module / one failing-test
  acceptance / no hidden coupling); plan size ceiling = ≤5 atomic
  tasks (forcing function for the brainstorming HARD-GATE); BLOCKED
  fallback per Kent Beck (2002) *Test-Driven Development: By Example*
  Part II §Child Test pattern, ISBN 978-0321146533 (when implementer
  returns BLOCKED with decomposition signal, orchestrator re-invokes
  writing-plans on the failing task); Red Flags table covering 7
  rationalizations including ja + zh-TW variants; §When NOT to Use
  with 4 enumerated exemptions.
- `skills/writing-plans/references/plan-format.md` — output schema for
  SDD consumption (required: Source brief / Total tasks ≤5 / Execution
  order / Plan-document-reviewer verdict / per-task: Description /
  Module / Context paths / Acceptance.RED + .GREEN / Dependencies /
  Brief item covered). Worked example: CSV export query param plan with
  3 tasks. Anti-patterns enumerated.
- `skills/writing-plans/references/plan-document-reviewer-prompt.md` —
  evaluator subagent prompt. 12 structured checks (each task ≤5 min /
  single module / failing-test acceptance / brief-to-task coverage map /
  no orphan tasks / DAG no-cycles / etc.). Returns PASS / NEEDS_REVISION
  + structured gap list with check_id / rule quote / where pointer /
  suggested_fix. Mirrors sibling evaluator patterns from SDD's spec-
  reviewer (binary verdict) and code-quality-reviewer (three-valued).
- `skills/writing-plans/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for writing-plans

- Skill Priority table row 2: Planning `writing-plans` flipped from
  "Phase 2 — until then, sketch a ≤5-task plan inline" → "✅ shipped".
- Router stays under the 2000-token P1-A budget: ~1836 tokens (was
  ~1848).
- 3-lang README tables updated in lockstep.

### Added — writing-plans pressure tests

`tests/writing-plans-pressure/prompts/`:
- `too-big-no-split.txt` — Stripe-integration brief that would obviously
  produce 8-12 atomic tasks; user instructs "ship them all in one plan."
  Tests the plan-size-ceiling forcing function.
- `unverifiable-task.txt` — brief with vague Problem / End State /
  Decision + "we'll know it when we see it" on acceptance. Tests
  refusal of vague tasks lacking RED-GREEN.
- `skip-the-plan.txt` — user wants to dispatch SDD directly with the
  brief. Tests the cross-skill contract: SDD's input REQUIRES a plan,
  not a brief.
- `index.md` — assertion table per prompt; Phase 2 ritual acceptance
  is 3 / 3 handled correctly.

### Added — `brainstorming` skill (1 of 3 Phase 2 skills)

Discovery skill with HARD-GATE measure preserved from Superpowers per P2-A.
Walks the user / agent through a 5-axis exploration framework (Problem /
Users / Smallest End State / Alternatives / What Becomes Obsolete) and
emits a structured brief that `writing-plans` (Phase 2, ships next)
consumes.

- `skills/brainstorming/SKILL.md` — HARD-GATE measure ("DO NOT START
  IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT"); §When NOT to Use with
  4 enumerated exemptions; 5-axis framework with primary-source citations
  (Christensen 2016 JTBD ISBN 978-0062435613; Klement 2018 job-story
  format ISBN 978-1718626751); Red Flags table with en + ja + zh-TW
  triggers; Output Contract pointing at handoff-brief-format.md; Cross-
  skill delegation to `dev-workflow:complexity-critique` (optional,
  Axis 3 smell) and `dev-workflow:proposal-critique` (optional, Axis 4
  triage).
- `skills/brainstorming/references/visual-companion.md` — when a Mermaid
  sequence / C4 / ER / flowchart diagram pays for itself vs when prose
  is enough. Includes axis-to-diagram-type mapping table + worked
  templates with color discipline (preferred green / rejected red /
  removed dashed-red).
- `skills/brainstorming/references/handoff-brief-format.md` — output
  schema for `writing-plans` consumption. Required sections (Problem /
  Users / Smallest End State / Decision / Out of Scope) + optional
  (Alternatives Considered / What Becomes Obsolete / Open Questions /
  Diagrams). Conventional file path: `docs/superpowers/specs/YYYY-MM-DD-
  <topic>.md`.
- `skills/brainstorming/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for brainstorming

- Skill Priority table row 1: Discovery `brainstorming` flipped from
  "Phase 2 — until then, ask 2-3 clarifying Qs" → "✅ shipped".
- `<EXTREMELY-IMPORTANT>` rule 1: dropped the "until that ships, ask
  2-3 clarifying questions" fallback; now points directly at the
  brainstorming skill's 5-axis framework.
- Skill version bumped to 0.2.0-draft.
- Router stays under the 2000-token P1-A budget: ~1848 tokens (was
  ~1853).
- 3-lang README tables updated in lockstep.

### Added — brainstorming pressure tests

`tests/brainstorming-pressure/prompts/`:
- `this-is-simple.txt` — the canonical "feature flag system" PAGNI
  smell (mirrors `dev-workflow:complexity-critique` test prompt #2).
- `i-know-what-to-build.txt` — user with a pre-formed feature list;
  agent must engage Axis 1 (problem behind the solution) + Axis 5
  (what becomes obsolete) before implementation.
- `lets-just-start.txt` — webhook receiver with hidden auth /
  idempotency / observability sub-decisions; agent must engage all
  5 axes minimally.
- `index.md` — assertion table per prompt; Phase 2 ritual acceptance
  is 3 / 3 refused with 5-axis engagement.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` bumped
  to `0.2.0-draft`. Drops `-draft` when full Phase 2 (writing-plans +
  systematic-debugging) ships.

### Phase 1 → Phase 2 carryover

Items deferred from Phase 1 into Phase 1.5 / Phase 2 backlog:

- **Feathers (2004) distinction in tdd-iron-law**: Phase 1 live test
  surfaced that the agent did not cite *Working Effectively with
  Legacy Code* (ISBN 978-0131177055) when distinguishing legitimate
  legacy-backfill from "I just wrote 200 lines without tests". Iron
  Law itself worked; the Feathers distinction is a SKILL.md
  sharpening — to be addressed alongside Phase 1.5 dogfood findings.

## [0.1.0] — 2026-05-16

First ship — Phase 1 MVP shell. Three skills + SessionStart hook + cross-plugin SSOT pipeline.

### Added — process layer (3 skills)

- **`using-code-toolkit`** — router skill, auto-injected by SessionStart hook. ~1853 tokens (under the 2000-token P1-A budget). Sections: `<SUBAGENT-STOP>` escape hatch, `<EXTREMELY-IMPORTANT>` 3-rule charter (brainstorm-before-implement, TDD iron law, SDD for >1-hour or >1-module work), Instruction Priority, How to Access Skills (Claude Code `Skill` tool / Codex CLI `skill` tool), Skill Priority decision table (8 stages mapped to v0.1.0 / Phase 2 / Phase 3 status), Red Flags rationalization table (en + ja + zh-TW localized triggers), Skill Types (Rigid / Flexible), Coexistence contract.
- **`tdd-iron-law`** — discipline skill. **"NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST."** Verbatim Beck (2002, ISBN 978-0321146533) Preface citation; full Three Laws of TDD from Martin (2008, ISBN 978-0132350884) Ch.9; Japanese anchor 和田卓人 訳 (2017, ISBN 978-4274217883). Iron Law remediation = *"Delete the code. Write the test. Start over."* (Superpowers measure preserved per Q-lock Q7). §When NOT to Use: 4 enumerated exemption rows (throwaway / generated / trivial-delegation / pure-config) + explicit-override row with confirmation requirement. §Red Flags: 8 rationalizations (en + ja + zh-TW) with primary-source rebuttals. §False-green diagnostic: comment-out / re-run drill. Ships with `references/testing-anti-patterns.md` indexing 8 anti-patterns to primary-source rebuttals.
- **`subagent-driven-development`** — workflow orchestrator. Triggers when task >1 hour OR >1 module. Per-task triad: implementer (worker, under TDD iron law) + spec-reviewer (evaluator, binary `PASS` / `NEEDS_REVISION`) + code-quality-reviewer (evaluator, three-valued `PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION`). Verdict resolution rule + 3-round retry cap. Model-selection table (mechanical → cheap / integration → standard / architecture → most capable). Continuous execution rule. Three subagent prompts under `agents/` with explicit input + output contracts (paths-not-content delegation per CLAUDE.md).

### Added — knowledge layer (12 functional copies)

Byte-identical copies of `domain-teams:code-team` standards / rubrics / checklists, each prefixed by a 5-line HTML comment SSOT header (P1-D). Pinned to **code-team SHA `916a165` (2026-04-29)** at v0.1.0 ship.

- `tdd-iron-law/standards/tdd-standard.md`
- `subagent-driven-development/standards/{tdd-standard, naming-and-functions, pragmatic-principles, solid-principles, refactoring-standard, app-security-standard, character-encoding-security}.md`
- `subagent-driven-development/rubrics/{quality-gate, arch-gate}.md`
- `subagent-driven-development/checklists/{security-checklist, spec-consistency}.md`

### Added — hooks

- `hooks/hooks.json` — registers SessionStart on `startup | clear | compact` matchers.
- `hooks/session-start` — bash; reads `using-code-toolkit/SKILL.md`, JSON-escapes via parameter substitution, emits **three** keys for portability across Claude Code (`hookSpecificOutput.additionalContext`), Codex CLI (`additional_context`), and any mixed-shape host (`additionalContext`). Fail-open if SKILL.md missing. Escape hatch wired up: `export CODE_TOOLKIT_MODE=off` returns empty-context JSON for users who already have `obra/superpowers` installed.

### Added — SSOT-and-functional-copy pipeline

- `scripts/distribute.py` — pure stdlib (P1-E). Reads from sibling-plugin `../domain-teams/skills/code-team/{standards,rubrics,checklists}/`, writes to `code-toolkit/skills/*/{standards,rubrics,checklists}/` with the SSOT header prepended. ROUTE table has 12 entries.
- `scripts/verify-drift.py` — pure stdlib. Regenerates expected payload `(SSOT header) + (canonical bytes)` and byte-diffs against the on-disk copy. On drift: md5 fingerprints + ≤50-line unified diff. Both positive (12 / 12 match) and negative (corrupted-copy detection) paths smoke-tested at v0.1.0 ship.
- `scripts/canonical/README.md` — SSOT pointer table + drift policy doc (no code in this dir; canonical lives in `domain-teams:code-team`).

### Added — manifests + 3-lang docs

- `.claude-plugin/plugin.json` — Claude Code manifest, version `0.1.0-draft` (drop the `-draft` suffix when live install is verified in a fresh session).
- `.codex-plugin/plugin.json` — Codex CLI manifest skeleton (P1-F: not shipped this phase; v0.2.5 ship target).
- `README.{md,ja.md,zh-TW.md}` — plugin-root 3-lang.
- `skills/{using-code-toolkit,tdd-iron-law,subagent-driven-development}/README.{md,ja.md,zh-TW.md}` — per-skill 3-lang × 3 skills = 9 files.

### Added — manual test harness

- `tests/skill-triggering/prompts/{new-feature,bug-fix,refactor,pure-question,explicit-skip}.txt` + `index.md` — 5 prompts that test SessionStart routing (positive + negative + legitimate-override cases). Mirrors Superpowers `tests/skill-triggering/` convention.
- `tests/tdd-iron-law-pressure/prompts/{skip-just-this-once,prototype-exception,i-already-wrote-it,tests-are-slow,small-change}.txt` + `index.md` — 5 prompts that pressure the Iron Law with 5 distinct rationalizations. Acceptance: 5 / 5 refused with primary-source citation.
- `tests/README.md` — manual-run convention for Phase 1; Phase 1.5+ may add an automated harness.

### Added — design + grounding documents

- `PRODUCT-SPEC.md` — business / target user / Q-lock × 8.
- `TECH-SPEC.md` — architecture / SSOT / hooks / interface contracts.
- `ROADMAP.md` — Phase 0–4 plan + Decision Ledger.
- `research/grounding-v0.1.0.md` — per-version grounding rationale: §1 inherits 11 primary sources from code-team v5.6.0 canon (with full ISBN / URL citations); §2 enumerates 7 process-layer authoritative claims original to this toolkit (each tagged to a Q-lock); §3 lists explicit non-claims (deferred to Phase 2 / 3); §4 drift policy summary; §5 re-runnable audit commands; §6 version-log rule.

### Added — marketplace registration

- `code-toolkit` entry added to root `.claude-plugin/marketplace.json` after `legal-toolkit`. Description byte-identical to `code-toolkit/.claude-plugin/plugin.json` per `scripts/check-marketplace-description-sync.py` gate (16 / 16 plugins in sync).

### Q-lock at v0.1.0 (PRODUCT-SPEC §8)

Eight design decisions locked at Phase 0 (2026-05-15) and **deliberately not revisited** during Phase 1 build:

1. **Q1** Harness = Claude Code + Codex CLI (Codex full ship deferred to Phase 2.5).
2. **Q2** `domain-teams:code-team` is **kept**, not deprecated — it is the passive-gate entry; `code-toolkit` is the active-construction entry.
3. **Q3** Design docs first (PRODUCT-SPEC + TECH-SPEC + ROADMAP) before any skill build.
4. **Q4** Worktree `feat/code-toolkit-design` for isolation.
5. **Q5** Knowledge-layer SSOT lives in `domain-teams:code-team/`; this plugin holds byte-identical functional copies.
6. **Q6** Skill naming follows `obra/superpowers` (`using-*`, `subagent-driven-development`, etc.).
7. **Q7** TDD measure preserves Superpowers' "Delete it. Start over." rhetoric AND adds Beck (2002) Preface ISBN-cited grounding (double anchor: behavior layer + canon layer).
8. **Q8** Subagent triad = three roles (implementer / spec-reviewer / code-quality-reviewer); spec-reviewer scope is binary, code-quality-reviewer scope is six-dimensional.

Phase 1 sub-decisions (P1-A through P1-F, ROADMAP §Phase 1 Q-lock): all observed at v0.1.0 ship — router under 2000-token budget; Beck 2002 Preface ISBN-quoted in `tdd-iron-law/SKILL.md`; subagent prompts as `.md` not `.txt`; functional copies carry HTML comment SSOT header; scripts pure-stdlib (no PEP 723); Codex CLI manifest is skeleton-only.

### Coexistence + escape hatches

- **`domain-teams:code-team`** — coexists. No file conflict (different plugin paths). `dev-workflow:complexity-critique`'s SSOT pointer to code-team's mindset functional copy is **unchanged**.
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — `code-toolkit` delegates to these at the right moments (per Phase 3 cross-plugin contract); does not duplicate their logic.
- **`obra/superpowers`** — known conflict on dual SessionStart hook + overlapping skill names (`brainstorming`, `writing-plans`, `subagent-driven-development`, `using-git-worktrees`). Resolution shipped: `export CODE_TOOLKIT_MODE=off` in shell rc disables this plugin's hook injection. Cleanly disables; tested with both positive and negative env-var cases.

### Known gaps + verification still owed

- **Live install verification still pending.** `0.1.0-draft` suffix in plugin.json + .codex-plugin/plugin.json marks this. To ship as `0.1.0` proper:
  1. Install plugin in a fresh Claude Code session.
  2. Confirm SessionStart hook fires (router auto-loads).
  3. Run at least one prompt from each of `tests/skill-triggering/` and `tests/tdd-iron-law-pressure/`; eyeball assertions per cluster `index.md`.
  4. Drop `-draft` from both manifest version fields; commit.
- **Phase 1.5 follow-ups**: `--soft-mode` flag implementation (OQ-1), 5 dogfood-session notes (`research/dogfood-2026-05-XX.md`).
- **Phase 2** (estimated 6-8 days): `brainstorming` + `writing-plans` + `systematic-debugging` skills.
- **Phase 2.5** (estimated 3-4 days): Codex CLI variant ship + integration tests.
- **Phase 3** (estimated 6-8 days): code-review cluster (`requesting-code-review`, `verification-before-completion`, `using-git-worktrees`, `finishing-a-development-branch`) for Superpowers parity.
- **Phase 4** (estimated 3-4 days): GA — cross-plugin delegation hardening + release.

### Files in v0.1.0 ship

```
code-toolkit/
├── .claude-plugin/plugin.json                  (manifest, draft)
├── .codex-plugin/plugin.json                   (manifest skeleton, draft)
├── PRODUCT-SPEC.md / TECH-SPEC.md / ROADMAP.md (Phase 0 design docs)
├── README.{md,ja.md,zh-TW.md}                  (plugin root, 3-lang)
├── CHANGELOG.md                                (this file)
├── hooks/{hooks.json,session-start}            (SessionStart injection)
├── scripts/{distribute.py,verify-drift.py,canonical/README.md}  (SSOT pipeline)
├── docs/superpowers/specs/2026-05-15-design-lock-session.md     (Phase 0 handoff)
├── research/grounding-v0.1.0.md                (per-version grounding rationale)
├── skills/using-code-toolkit/{SKILL.md, README ×3, references/{claude-code-tools.md,codex-tools.md}}
├── skills/tdd-iron-law/{SKILL.md, README ×3, standards/tdd-standard.md, references/testing-anti-patterns.md}
├── skills/subagent-driven-development/{SKILL.md, README ×3, agents/{implementer,spec-reviewer,code-quality-reviewer}-prompt.md, standards/×7, rubrics/×2, checklists/×2}
└── tests/{README.md, skill-triggering/prompts/×5+index.md, tdd-iron-law-pressure/prompts/×5+index.md}
```

Plus: 1 root `.claude-plugin/marketplace.json` entry added (16th plugin in monkey-skills marketplace).
