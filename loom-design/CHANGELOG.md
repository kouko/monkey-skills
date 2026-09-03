# Changelog

All notable changes to the `loom-design` plugin will be documented in
this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

`loom-design` was assembled in 2026-08 out of five plugins. Their
histories used to sit in five files beside this one; 1.0.0 folded them in
as the `## Predecessor plugin histories` section at the end, so this file
is the whole record. Their version numbers never continued here —
`loom-design` started fresh at 0.1.0.

## [1.0.0] — 2026-09-02 — Two stations and two tools

**Breaking.** The pre-1.0 surface is deleted, not renamed or aliased.
Ten skills became four; nothing reads the old artifacts.

`budget-exception:` is not needed for this version — the mechanism net
count falls (10 skills → 4, 96 scripts and tests deleted); nothing is
added without a listed `eval:`.

### Added

- **Two stations**: `capture-intent` (interview → `intent.md` → decision
  point ①, the restatement the user confirms) and `write-spec` (confirmed
  intent → `spec.md` → decision point ②, the visible behaviour a product
  change's user reads back), each carrying the station summary table.
- **Two tools**: `product-principles` (PRINCIPLES.md, now carrying
  `ratified-by: <name> <date>`) and `design-system` (DESIGN.md tokens for
  GUI, a conventions stub for TUI/CLI; never blocks).
- **`requires-contract: ">=1.0"`** in `plugin.json`, and a
  `loom_checker.py contract --require 1.0` step at the top of every
  station and tool: loom-design reads loom-code's contract package and
  refuses to run against a version it does not understand.
- **References** carrying what the deleted skills knew:
  `capture-intent/references/interview.md` (from user-insights and
  business-value), `write-spec/references/spec-forms.md` and
  `ui-flows.md` (from spec-expansion and interaction-flows).

### Removed

- **Skills (10 → 4)**: `using-loom-design` and `using-loom-pipeline`
  (there is no router and no conductor), `user-insights` and
  `business-value` (the capture-intent interview asks what they asked),
  `spec-expansion` and `interaction-flows` (write-spec and its
  references), `completeness-critic` and `design-critic` (verdicts are
  rendered in loom-code's review station, under its spec and
  design-conformance lenses — a station that drafts no longer grades).
- **Scripts and tests (96 files)**: the whole `scripts/discovery/` (12)
  and `scripts/pipeline/` (47) directories — the Workflow drivers,
  `batch_queue.py`, the queue modules, `argv_exec.py`, `comms_metrics.py`
  and the fixtures, plus hook tests that loom-code already runs against
  its own copies. From `scripts/interface/` (13) and `scripts/spec/`
  (22): both copies of `mint_critic_verdict.py`,
  `validate_design_output.py`, `validate_spec_output.py`,
  `validate_intent_layer.py`, `pairwise.py`, and the skill grep-tests for
  the deleted skills. `scripts/principles/` lost its entry-router test.
- **The critic co-writer exemption** the repo's CLAUDE.md granted
  `design-critic` and `completeness-critic` — provenance-tagged additions
  to a draft — has no subject any more.

### Changed

- **`scripts/` is three stations, not five.** `pytest.ini`'s `pythonpath`
  and `test_unified_pytest_root.py` follow; the shadowed-basename set is
  empty now that the `mint_critic_verdict.py` SSOT/functional-copy pair
  is gone, so that line's order stops being load-bearing.
- **`test_marketplace_entry.py` and `test_plugin_manifest.py`** existed
  once per station, three near-identical copies of the same config
  assertions. One copy each sits at the suite root now, carrying the
  union of what the three asserted.
- **`design-system/references/knowledge-triage.md`** is re-aimed at the
  1.0 shape: the routed research resolves before the review station's
  design-conformance verdict (not `design-critic`'s), the deferral flows
  into `write-spec`'s intake (not spec-expansion's Phase ③), and a note
  after the transcribed pin repoints the craft bucket, whose route named
  the pre-1.0 Axis 4 protocol. The pin block itself is untouched.
- **`.github/workflows/loom-pipeline-ci.yml` → `loom-design-ci.yml`**,
  job `loom-design pytest`, triggering on `loom-design/**`. No branch
  protection check was bound to the old name.
- **Version 1.0.0**, with the plugin description, keywords, the Codex
  interface block, the marketplace entry and the root README rows (all
  three languages) moved off "deterministic pipeline conductor".

## [0.6.0] — 2026-09-01 — one pytest root, and a split batch queue

### Added

- **One pytest invocation now collects the whole plugin suite.**
  `scripts/pytest.ini` scopes a root at `loom-design/scripts/` and sets
  `--import-mode=importlib`, which lifts pytest's unique-basename rule so the
  stations can keep same-named test modules side by side. Because importlib
  mode stops putting a test file's own directory on `sys.path`, one enumerated
  `pythonpath` line restores the bare sibling imports that five per-directory
  `conftest.py` files used to prop up. CI drops from five per-station pytest
  jobs to one.

### Changed

- **`scripts/pipeline/batch_queue.py` split into three modules** — `queue_core.py`
  (state and lock handling), `queue_commands.py` (the subcommand bodies), and a
  thin argparse entry that remains `batch_queue.py`. Pure reorganisation: no
  observable behaviour changed, and both the importable main entry and the
  status subprocess contract are unchanged.

## [0.5.7] — 2026-08-28

### Changed

- Synced the family-reception copy: the decision-map layer's on-ramp
  update reached loom-design's own reception surface.

## [0.5.6] — 2026-08-28 — test pins assert invariants, not wording

### Changed

Structural pin tests across this plugin now assert the invariant each one
protects rather than the sentence that carried it, matching the loom-code
change of the same date. `scripts/pipeline/heading_window.py` is new: one
`line_leading()` shared by this package's heading windows. It is a separate
copy from loom-code's on purpose — the two plugin trees are hashed
independently as cold-install packages and must not import across each other.

No skill instruction text changed — this is a test-side change only.

## [0.5.5] — 2026-08-28

### Changed

- Synced `using-loom-design/references/family-relay.md` from its SSOT: the
  close-out card offers one merge path instead of two, its `🌐 Web merge` row
  becomes `🔗 PR link` — a link to view the PR, never a way to merge — and the
  merge row carries the full command inline, since a design-side install cannot
  resolve a pointer into loom-code.

## [0.5.4] — 2026-08-27

### Changed

- Added stage-owned complexity lenses for business, visual, interaction, and
  behavioral design, with standalone fallback and optional artifact relay.

### Fixed

- `business-value`: the artifact template's reasoned-N/A placeholder says it
  replaces the four business-complexity slots rather than joining them; the two
  readings previously forked what an author wrote.

## [0.5.3] — 2026-08-27 — restore the deletable-lenses section

### Fixed

- `completeness-critic`: restored the "Deletable lenses (Bitter Lesson)"
  section, including the standing prune candidate (state-completeness) and the
  last-to-go pair (NFR-security, permissions/data-boundary). The 0.5.2
  compaction dropped it while the sibling `design-critic` kept its copy.
- Removed the per-file word-count bounds from the `test_*_compaction.py` files.
  They froze the 0.5.2 compaction's own measurement into a permanent contract
  and could not detect a deleted rule; presence assertions now carry that job.

## [0.5.2] — 2026-08-26 — behavior-preserving skill compaction

### Changed

- Compacted all loom-design skill entrypoints with static invariants and
  Claude Code/Codex weak-model A/B evidence.
- Made dry-loop termination and the design-system → interaction-flows →
  integrated-validation seam executable without weakening its validators.

## [0.5.0] — 2026-08-23 — design-specialized standalone operation

### Changed

- Own design relay, critic-panel, and artifact contracts instead of borrowing
  loom-code's code-review and dispatch semantics.
- Resolve every station command from the installed plugin root and preserve
  hostile dynamic values through direct argv or the encoded pipeline bridge.
- Prove standalone and optional composition behavior from renamed isolated
  installs with sibling-absence and no-op mutation tests.

## [0.4.0] — 2026-08-20 — North Star retargeted to PURPOSE.md

### Changed

- **`## North Star` moved OUT of `PRINCIPLES.md`'s contract.**
  `PRINCIPLES.md` now holds only product / design / engineering
  principles; the project's long-horizon purpose lives in `loom-code`'s
  new `PURPOSE.md` artifact instead (see `loom-code` 0.91.0).
  `validate_principles_output.py` no longer requires or parses a
  `## North Star` section, and `product-principles`'s `SKILL.md` +
  `references/principles-rules.md` + `references/question-sets.md`
  stop asking for one.

## [0.3.0] — 2026-08-18 — requirement identifiers

### Added

- **`REQ-<n> — <name>` requirement-identifier header grammar** (T1–T3).
  `validate_spec_output.py` now parses id-form `### Requirement:` headers,
  rejects a near-miss token (`REQ1`, `req-1`, `R-1`), enforces all-or-nothing
  adoption per spec file (a file with one id-form header must use id-form
  for every header in it; legacy prose-only files are unaffected), and
  rejects a duplicate `REQ-<n>` declared more than once within a
  change-folder.
- **`references/requirement-identifiers.md`**, the SSOT for the `REQ-<n>`
  convention — form, authored-never-derived, monotonic-never-reused
  minting rule, change-folder/living-spec scope, and an anti-patterns list
  — pinned by `scripts/spec/test_requirement_ids.py` (T10).

### Changed

- **`spec-expansion`'s `SKILL.md` teaches one requirement-header grammar**
  instead of two: the skeleton and the status-suffix passage both now show
  `### Requirement: REQ-<n> — <name>` (with `[deferred]` etc. as a
  trailing suffix), pointing at `references/requirement-identifiers.md`
  for the id rules instead of restating them (T11).

## [0.2.0] — 2026-08-17 — artifact-layer table routing (spec side)

### Changed

- **`spec-expansion`'s `## Path × edge matrix` and `## Cross-object
  combinations` sections now specify a markdown-table body** with pinned
  `N/A` lines for the genuinely-empty case, instead of free-form prose.
- **`validate_spec_output.py` rejects a body that carries neither a
  table nor its `N/A` line** for those two sections.

## [0.1.0] — 2026-08-17 — the design side becomes one plugin (6→2)

### Added

- **`loom-design` — one plugin for the whole design side.** Four station
  plugins (`loom-discovery`, `loom-product-principles`,
  `loom-interface-design`, `loom-spec`) and the conductor
  (`loom-pipeline`) merged into this one. Nine member skills ship here:
  `business-value`, `user-insights`, `product-principles`,
  `design-system`, `interaction-flows`, `design-critic`,
  `spec-expansion`, `completeness-critic`, plus the conductor
  `using-loom-pipeline`.
- **One entry router, `using-loom-design`.** The four `using-loom-*`
  design routers merged into it — they shared ~70% of their skeleton and
  four separate entry points made "where do I start" harder to answer,
  not easier. It routes to whichever of the four stations the ask needs.

### Changed

- **Member skill names are unchanged** — only the plugin prefix moved
  (`loom-spec:spec-expansion` → `loom-design:spec-expansion`). A caller
  who invokes a station by name is unaffected.
- **Scripts live under per-station subdirectories**
  (`scripts/{discovery,principles,interface,spec,pipeline}/`) because
  four of the absorbed plugins shipped same-named files. The station
  suites must still be run as separate pytest invocations — the
  duplicate basenames collide at collection without `__init__.py`.

### Moved out

- **The family hooks and `loom-memory` went to `loom-code`** (0.84.0):
  they are family infrastructure, and loom-code is the always-installed
  plugin. See that changelog for the receiving side.

### Note for installed hosts

The marketplace drops from 6 loom entries to 2. Run `plugin update` to
pick up `loom-design` and the 0.84.0 `loom-code` that now carries the
family hooks; without it the retired plugins simply disappear.

## Predecessor plugin histories

The five plugins loom-design was assembled from, newest entry first within
each. Headings are demoted two levels; nothing else is edited. Version
numbers below belong to those plugins and do not continue above.

### loom-discovery

> absorbed into loom-design 0.1.0 (2026-08-17); its two skills, `user-insights` and `business-value`, became the capture-intent interview in 1.0.0.

#### [0.5.0] — 2026-08-15 — brief-before-fork dedup pointer

##### Changed

- **`using-loom-discovery` points at the family SSOT for the brief-before-fork
  trigger** instead of carrying an in-place copy of the threshold triple — the
  triple now lives once in `loom-pipeline/hooks/family-reception.md §Brief
  before a complex fork`.

#### [0.4.1] — 2026-08-07 — one-sentence plugin description

##### Changed

- **plugin.json / marketplace.json `description`**: cut from a 1005-char
  mini-README to one sentence (user request: a plugin description should
  be a single simple line). The detail it carried already lives in the
  plugin README and the two skills' own descriptions; both manifests stay
  verbatim-synced per the marketplace-description-sync gate.

#### [0.4.0] — 2026-07-25 — bba imperative in entry router

##### Added

- **`using-loom-discovery`**: §Intake's family-routing step gains a
  one-line `dev-workflow:brief-before-asking` imperative for non-trivial
  discovery forks (value commitment, on-ramp choice) — carries the
  trigger triple (≥3 trade-offs, ≥2 implementation paths, or
  architectural blast radius) verbatim, mirroring
  `using-loom-pipeline`'s gate (b) pattern.

#### [0.3.0] — 2026-07-18 — mandatory bounded validator step

##### Added

- **`user-insights`** and **`business-value`**: both SKILL.md files gain a
  mandatory validate step before declaring done — run
  `scripts/validate_discovery_artifacts.py` on the produced artifact dir;
  non-zero result → fix and re-run, bounded at 2 attempts, then surface to
  the user. Mirrors `loom-product-principles`'s Step 8 wiring pattern;
  tolerates greenfield/first-run artifact creation.

Design SSOT: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4
rec 5.

#### [0.2.0] — 2026-07-18 — evidence source-type column

##### Added

- **`user-insights` evidence template**: the evidence table gains a
  `Source type` column (`craft` / `domain-convention` / `project-local`) +
  a compact legend — evidence is typed at intake so downstream stations
  know which authority owns each claim.

#### [0.1.2] — 2026-07-14

##### Fixed

- **`user-insights` description reverted to the full pre-sweep 899-char
  version** (byte-identical to the 0.1.0 text). The post-merge A/B B-leg
  (plan Task 8) measured combined firing 100%→33%: two records were
  cross-family-attracted by loom-pipeline:loom-memory's pre-existing
  "check prior experience before loom work" clause once the slimmed
  170-char description lost its needs-research lexical thickness. A
  targeted 217-char restore was cache-experimented and ALSO failed
  (1/3 — the ja record newly flipped), demonstrating that mid-band
  lexical tuning near a sibling attractor is unstable — pin-literal
  revert per the plan's A/B bar. Evidence:
  `docs/skill-dogfood/2026-07-14-description-token-economy/ab-results.md`
  §remedy-experiment. Net sweep for this plugin stands at
  using-loom-discovery −566 / business-value −386 chars.

#### [0.1.1] — 2026-07-14

##### Changed

- Description token-economy sweep (two-tier standard,
  `skill-dev-toolkit/skills/skill-creator-advance/references/description-design.md`
  Principle 5 + cutting rules): frontmatter descriptions rewritten —
  `using-loom-discovery` 1,065→499 rendered chars (router exception band
  ≤500, firing-evidence YAML comment added above `description:` citing the
  2026-07-14 baseline 3/3 EXACT), `user-insights` 899→170, `business-value`
  616→230 (normal band, 250 soft lint). Bodies untouched; multilingual belt
  triggers preserved (需求研究 / 值不值得做 / ユーザーインサイト /
  時間の使い方 / ビジネスバリュー).

#### [0.1.0] — 2026-07-10

##### Added

- Initial plugin: dual manifest (`.claude-plugin/` + `.codex-plugin/`, Claude
  SSOT synced via `scripts/sync_codex_manifests.py`), `README.md`, this
  changelog; three skills — `using-loom-discovery` (family-entry router),
  `business-value` (adversarial worth-it check, GO / NO-GO /
  NEEDS-MORE-RESEARCH, skippable + re-entrant), `user-insights` (two-mode
  needs research with user-ratified value commitment) — plus
  `scripts/validate_discovery_artifacts.py` (assess-first intermediate state
  honored) and the behavioral-dogfood fix round
  (`docs/skill-dogfood/2026-07-10-loom-discovery/report.md`).
  Test count at close-out: 64 (loom-discovery suite; family suites green).

### loom-interface-design

> absorbed into loom-design 0.1.0 (2026-08-17); `design-system` survives as a 1.0.0 tool, `interaction-flows` and `design-critic` do not.

#### [0.12.0] — 2026-08-15 — brief-before-fork dedup pointer

##### Changed

- **`using-loom-interface-design` points at the family SSOT for the
  brief-before-fork trigger** instead of carrying an in-place copy of the
  threshold triple — the triple now lives once in
  `loom-pipeline/hooks/family-reception.md §Brief before a complex fork`.

#### [0.11.0] — 2026-08-11 — toolkit-guarded ascii-ui-patterns skeletons

##### Changed

- loom-interface-design 0.11.0: ascii-ui-patterns — skeletons are generated
  via ascii-graph-toolkit when available (availability-guarded degrade path,
  CJK labels never hand-drawn); example skeletons re-aligned.

#### [0.9.0] — 2026-07-25 — bba imperative in entry router

##### Added

- **`using-loom-interface-design`**: the entry router now names
  `dev-workflow:brief-before-asking` and carries its canonical trigger
  triple (`≥3 trade-offs, ≥2 implementation paths, or architectural blast
  radius`) verbatim, so a non-trivial design fork gets a proactive
  briefing reminder before the user is asked — mirroring the #475
  complex-fork escalation already wired into `using-loom-pipeline`.

#### [0.8.0] — 2026-07-18 — outer revision cap + minted critic verdicts

##### Added

- **`design-critic`**: the writer↔critic outer revision cycle is now capped
  at 2 — on the 2nd consecutive `NEEDS_REVISION` after a revision, the loop
  stops and hands back to the user with a plain-language list of unresolved
  findings instead of silently re-running.
- **`scripts/mint_critic_verdict.py`**: ported from `loom-spec` (byte-identical
  logic — `--files` has no default in either plugin, only docstrings differ,
  e.g. this plugin's docstrings noting the typical `DESIGN.md,ui-flows.md`
  file list) — content-hash-bound `mint`/`validate` critic-verdict CLI, plus
  a lockstep test pinning it to the `loom-spec` original so the two never
  drift.
- **`design-critic`**: the verdict step now additionally runs
  `mint_critic_verdict.py mint` for the change-folder on both verdict values.

Design SSOT: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4
recs 2/7 + §4c Fix-4.

#### [0.7.0] — 2026-07-18 — mechanical pre-check + literal SHAPING tier label

##### Added

- **Ending gates** (`interaction-flows` + `design-system`): an imperative
  action-moment card near each skill's head — before ending ANY run,
  confirm the artifact file exists on disk and the validate step ran; a
  narrated analysis with no file written is a FAILED run. Closes the
  weak-executor early-stop path that never reaches the buried validate
  step (live incident: 2026-07-18 dogfood, a haiku run ended without
  writing ui-flows.md; imperative cards are the evidence-backed carrier —
  docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md).

- **`design-critic`**: a mechanical pre-check step runs BEFORE panel
  dispatch — greps the artifact for (1) `evidence_needed:` values outside
  `craft | domain-convention | project-local` and (2) tier-label
  discipline on every `evidence_needed: domain-convention` tag, split into
  two literal sub-greps: (2a) an untiered tag with no literal `SHAPING` or
  `DEFERRABLE` label nearby, and (2b) a literal `SHAPING` label declared
  non-blocking/deferred WITHOUT a `deferred: <reason>` marker. Either hit
  emits a `NEEDS_REVISION` finding directly (no panel needed for that
  finding; the panel still runs for everything else). Classifying
  SHAPING-ness itself stays the panel's judgment — the pre-check only
  checks for the literal label. Verdict vocabulary (`PASS_WITH_NOTES` /
  `NEEDS_REVISION`) unchanged.
- **`interaction-flows` + `design-system`**: both
  `references/knowledge-triage.md` gain two identical one-sentence
  supplements placed AFTER the pinned vocabulary block (never inside it):
  "SHAPING never ships as non-blocking: it either resolves before this
  station's gate or carries `deferred: <reason>`." — closes the
  prose-only-consequence gap a weak drafter inverted in live dogfood (leg
  2, `docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`) —
  and "Every tagged open question written into ui-flows.md / DESIGN.md
  must carry a literal `SHAPING` or `DEFERRABLE` label alongside its
  `evidence_needed:` tag." — makes the tier label a literal artifact
  obligation the pre-check's mechanical grep can actually find, mirroring
  loom-spec's domain-tag-triage.md two-tier doctrine.

#### [0.6.0] — 2026-07-18 — HIGH-bar knowledge triage + critic evidence flag

##### Added

- **`interaction-flows` + `design-system`**: each gains
  `references/knowledge-triage.md` (pinned three-bucket vocabulary:
  craft / domain-convention / project-local) with an imperative mount at
  its drafting moment. SHAPING bar (HIGH, narrower than loom-spec's):
  the answer alters flow structure, a state machine, or a semantic
  display convention. SHAPING domain-convention facts get routed
  research BEFORE the critic verdict; deferrable ones become tagged open
  questions (`evidence_needed:`) in ui-flows.md / DESIGN.md for the spec
  station to inherit. Drafting skills never run WebSearch.
- **`design-critic`**: findings may carry the optional
  `evidence_needed: craft | domain-convention | project-local` tag —
  flag-never-search; verdict enum unchanged.

#### [0.5.0] — 2026-07-13

##### Added

- **Surface-treatment candidate pick** (`design-system`) — the station now
  proposes **3-5 surface-treatment candidates** from the new
  `references/canon-design-surface.md` (fit/tension notes), surfaces **1-2
  considered-but-rejected** with reasons, and the **user decides** (a
  `bespoke — no canon treatment fits` escape hatch is legal). The pick is
  **named + rationalized in prose** in Overview / Brand and then constrains the
  `## Elevation & Depth` and `## Shapes` token blocks. The anti-costume law
  carries over (a treatment never overrides a PRINCIPLES value) and a canon
  row's **WCAG risk flag is a blocker, not a note**. No 9th `##` section was
  added — the 8-section DESIGN.md contract is unchanged.
- **`references/canon-design-surface.md`** — relocated here from
  `loom-product-principles` (it is a stage-4 design-language sub-decision, not a
  constitution-stage one) and expanded **6 → 18 rows**, each with a
  live-verified source URL, era, currency note and WCAG risk flag. Grounded in
  `docs/loom/research/2026-07-12-ui-surface-treatments-canon.md`.

##### Changed

- **`design-system` now INHERITS the visual mood instead of inventing it.**
  Step 2 reads the `## Anchors` section of `PRINCIPLES.md` and treats the
  **3-5 tone & manner adjectives** as the **governing mood** — it does **not**
  re-derive them (`design-md-schema.md`'s derivation contract agrees; `brand_voice`
  is fed from the anchor). When no anchor row exists, it derives as before **and
  says so explicitly** — never silently inventing while appearing to inherit.
  This is a **read-and-honor prose instruction, not a parser** (rationale +
  reversal trigger: `docs/loom/specs/2026-07-13-axis-b-relocation-and-tone-manner-seam.md`
  §Alternatives). Closes the unwired seam left by loom-product-principles 0.8.0.

#### [0.4.2] — 2026-07-07

##### Changed

- `using-loom-interface-design` §Intake now points at the family relay
  discipline (`loom-pipeline/hooks/family-relay.md`). Verification:
  `test_family_relay.py::test_design_side_pointers[interface-design]` passed.

#### [0.4.1] — 2026-07-05

##### Added

- **`using-loom-interface-design/references/claude-code-tools.md`** +
  **`codex-tools.md`** — `design-critic`'s multi-lens panel already phrased
  subagent dispatch in host-neutral prose ("dispatch one subagent per
  lens... not bound to any one harness"), but had zero concrete reference
  for what that resolves to on either host. Added the same host-neutral
  skill body + per-host tool-mapping reference pattern `loom-code` uses
  (`obra/superpowers` is the confirmed prior-art source for this pattern).
  Codex side documents `multi_agent`/`spawn_agent`/`wait_agent`/
  `close_agent`, verified 2026-07-05 via `codex features list` on a live
  Codex 0.139.0 install (feature flag itself live-confirmed) + OpenAI's
  official Codex manual §Subagents (verb names/behavior doc-confirmed, not
  independently re-exercised for this plugin's specific dispatch points).
  `design-critic/SKILL.md`'s panel section now points at both files.

#### [0.4.0] — 2026-07-04

##### Added

- **`## §Intake`** section on `using-loom-interface-design/SKILL.md`
  (loom family connective-tissue work): step 1 checks the target against
  the `loom-pipeline` family-reception on-ramp criteria (PRINCIPLES.md
  gap recommends `using-loom-product-principles` first), step 2
  redirects spec/code asks to their own entries, step 3 keeps the
  existing design-system/interaction-flows routing. Guarded by
  `test_entry_intake.py`.

##### Changed

- **Next-station cross-refs** — `design-system/SKILL.md` (§Downstream)
  and `interaction-flows/SKILL.md` (§Boundary) each gain a "Next
  station." line pointing a finished `DESIGN.md` / `ui-flows.md` to
  `using-loom-spec` to expand the feature into a spec.
- `test_entry_intake.py`'s `§Intake`-section slice now stops at
  whichever comes first of the next `## ` heading or the
  `<EXTREMELY-IMPORTANT>` block — the old `\n## `-only boundary let the
  `<EXTREMELY-IMPORTANT>` block leak into the "§Intake section" a
  step-scoped assertion checked, mutation-proven (old test false-passed
  a stripped mutant; fixed test fails it).

##### Decided

- **`DESIGN.md` machine consumer: parked, with explicit re-triggers** (audit
  batch ③ close-out). Wiring a loom-code review gate / implementer intake was
  evaluated and rejected for now — it would front-run #456's documented
  decision that consumer-side machinery (including the shadcn-vs-Material
  color-naming question a conformance check must interpret) is undecidable
  until a real frontend consumer lands, and the upstream DESIGN.md spec is
  alpha with consumer behavior unspecified. Re-triggers recorded in README
  §Scope: first real GUI product wiring its frontend to the pipeline, or
  upstream spec 1.0 / second-vendor adoption.

##### Changed

- **`ui-flows.md` moves into a per-change folder** —
  `docs/loom/<change-id>/ui-flows.md`, sharing the `<change-id>`
  `loom-spec:spec-expansion` uses, so the design seed sits beside the spec
  delta it feeds. The old fixed product-level `docs/loom/ui-flows.md` meant
  the second feature overwrote the first ("per-feature/change" was declared
  but not honored by the path). `DESIGN.md` stays product-level.
  `validate_design_output.py` now resolves `DESIGN.md` most-specific-first
  (change folder, then its parent) — the legacy side-by-side layout still
  validates. `design-critic` inputs and README updated. Guarded by
  `test_change_folder_with_design_at_parent_passes` (+3 sibling tests),
  `test_ui_flows_emitted_per_change_folder`,
  `test_inputs_are_per_change_folder`.

##### Added

- `design-critic` now ends every run with a **machine-readable two-valued
  verdict** — `PASS_WITH_NOTES` / `NEEDS_REVISION` (no unqualified PASS — that
  would be a completeness claim). The router carries the stage-3 resolution
  rule (`NEEDS_REVISION` → back to the generators; `PASS_WITH_NOTES` →
  `ui-flows.md` hands to spec-expansion). Drift-alignment with
  `completeness-critic`: explicit **write-back contract** (augment in place,
  never overwrite, `critic-found` provenance tags, validator run post
  write-back) and the **overlap-rate panel-diversity diagnostic** reported in
  the new round summary. Guarded by `test_verdict_two_valued_enum`,
  `test_write_back_carries_provenance`, `test_overlap_rate_diagnostic_present`.

##### Fixed

- `design-system` / `interaction-flows` SKILL.md now state the correct
  skill-dir-relative validator path (`../../scripts/validate_design_output.py`);
  the previously claimed `scripts/…` form did not resolve from the skill
  directory in an installed plugin.
- README: `design-critic` listed as shipped (it landed in v0.2.0 but the README
  still called it deferred), scope section retitled to the current version line,
  and the `DESIGN.md` side-channel description aligned with the honest seam
  wording from #465 (no loom-code skill machine-reads `DESIGN.md`).
- Earlier unversioned post-0.3.0 fixes: trigger-description rewrites +
  DESIGN.md visual-concept layer (#456), reply-honesty prose + skill version
  fields (#465).

#### [0.3.0] — 2026-06-21

##### Changed

- **BREAKING**: plugin renamed `interface-design-toolkit` → `loom-interface-design`;
  router skill renamed `using-interface-design-toolkit` → `using-loom-interface-design`;
  artifact paths unified under `docs/loom/` (#440).

#### [0.2.0] — 2026-06-17

##### Added

- `design-critic` — adversarial writer≠judge panel hunting surface omissions
  (undrawn states, dead-end flows, a11y gaps) + principle conformance over the
  design change-folder, mirroring `loom-spec:completeness-critic` (#409).

#### [0.1.0] — 2026-06-15

##### Added

- MVP: `design-system` (GUI → 8-section `DESIGN.md`) + `interaction-flows`
  (`ui-flows.md`) + `using-interface-design-toolkit` router +
  `validate_design_output.py` change-folder validator. Cross-modal
  architecture (GUI/TUI/CLI), GUI-first (#399).

### loom-pipeline

> retired 2026-08-17; its conductor lived on as `using-loom-pipeline` until 1.0.0 deleted it, and `loom-memory` had already moved to loom-code 0.84.0.

#### [0.18.0] — 2026-08-15 — plain-relay contract + brief-before-fork SSOT

##### Changed

- **A plain-relay contract is the family SSOT for the relay/machine-artifact
  split.** `hooks/plain-relay.md` (7 rules + a token→meaning glossary + one
  ✅/❌ calibration pair) governs: user-facing chat messages strip internal
  jargon (stage names, verdict tokens, raw gate strings); machine artifacts
  (briefs/verdicts/commits/plan docs) stay machine-precise. `family-relay.md`
  and `relay-phrasing.md` gain one-line pointers to it.
- **A `<PLAIN-RELAY>` trigger card is injected at SessionStart.** The
  reception prepends a short imperative card so "reply in plain language" is
  auto-bound every turn, not a remembered rule (A/B-verified: injecting the
  short card works; supplying the long doc for reference does not).
- **The brief-before-fork trigger collapses to one SSOT.**
  `hooks/family-reception.md §Brief before a complex fork` is now the single
  home of the threshold triple (≥3 trade-offs / ≥2 implementation paths /
  architectural blast radius); the six routers/skills that carried in-place
  copies now point here. The reception line-budget grows to accommodate the
  trigger card + the SSOT section (both load-bearing).

#### [0.17.0] — 2026-08-10

##### Changed

- `hooks/family-reception.md` on-ramp criteria table gains a row: when
  the target repo has no `docs/loom/backlog/` (queue layer not
  adopted) and the work is loom-family-scoped, suggest running
  **loom-init** once — the scaffold verb shipped in loom-code. The
  table's existing "Recommend ONCE, never nag" rule covers it.

#### [0.16.0] — 2026-08-10

##### Changed

- `hooks/family-relay.md` §(a2) — the progress-card body renderer is
  now named as the `plan_card.py` that ships in the loom-code plugin,
  with a repo-root `scripts/` copy taking precedence when present
  (stated in prose only; reference files carry no
  placeholder literals) — the previous wording pointed only at the
  repo-root script, a path that does not exist in external repos.

#### [0.15.0] — 2026-08-07

##### Changed

- `skills/loom-memory/SKILL.md` — record steps 4-5 and prune's index
  duties flip from hand-append/hand-update to the generated-index
  regen procedure (`python3 scripts/check_loom_memory_integrity.py
  --write`, followed by `--check`); the SSOT pointer-discipline
  section is untouched. Skill frontmatter version 0.2.0 → 0.2.1.

#### [0.14.0] — 2026-08-06

##### Changed

- §(a2) Progress card switches to plain-ASCII marks (`[v]`/`[~]`/`[ ]`/`[!]`,
  goal-line prefix `goal:`) — emoji rendered inconsistently across
  terminals and fonts; the body renderer `scripts/plan_card.py` changed
  in the same commit (the pinned same-commit duty for format changes).
- The card becomes a roadmap: `scripts/plan_card.py` derives topological
  steps from `Dependencies:` and renders per-step separators, optional
  `Steps:` titles and per-task `Gloss:` lines; §(a2)'s frame contract v2
  replaces the one-line-frame rule — goal gloss, grounded `next:` gloss
  (cite the source item, never invent), stop-reason opening on every
  `[!]` row, pipeline-station narration banned from the frame.

#### [0.13.0] — 2026-08-06

##### Added

- family-relay.md gains §(a2) Progress card — the plan-progress
  variant of the user-rollup card (goal / task table / stage / next,
  body rendered by the repo-root `scripts/plan_card.py`, relayer adds
  only a localized one-line frame).

#### [0.12.0] — 2026-08-02 — loom-memory routes backlog items to the entry-per-file store

##### Changed

- **loom-memory's `## record` step no longer routes a backlog-shaped item
  to `docs/loom/BACKLOG.md`**: that file is now generated output
  (`docs/loom/backlog/README.md`) and must never be hand-edited. The
  classification step now routes such an item to creating an entry file in
  `docs/loom/backlog/` per its own charter.

#### [0.11.0] — 2026-07-22 — loom-memory recall staleness caveat

##### Changed

- **loom-memory recall now carries a staleness caveat**: recalled
  practice-memory entries can outlive the files/flags/skills they name.
  Before acting on a recalled entry, verify its named file, flag, or
  skill still exists — a stale recall silently reintroduces the exact
  gotcha the entry was recorded to prevent.

#### [0.10.0] — 2026-07-21 — batch terminal-mark precursor guard

##### Fixed

- **`batch_queue.py` terminal mark requires a RUNNING precursor**: `_cmd_mark`
  wrote done/failed with no precondition, so a QUEUED (never-dispatched) entry
  could jump straight to DONE — silently dropping work while the batch reported
  success. It now enforces the same precursor-state guard `_cmd_mark_running`
  already has, extracted to a shared `_require_running` helper (routed by
  `mark` / `mark-running` / `force-fail`).

#### [0.9.0] — 2026-07-18 — batch_queue recovery + reconciliation + dispatcher wiring

##### Added

- **`batch_queue.py` state locking**: all state load→modify→save now holds
  `fcntl.flock(LOCK_EX)` across the full read-modify-write, writing via
  `tempfile` + `os.replace()` atomic swap — fixes the pre-existing
  lost-update race under concurrent access. Lock target is a sidecar
  `<state-file>.lock` file (avoids the macOS truncating-open-before-flock
  trap).
- **`_dispatch_entry`**: records `dispatched_at` (wall-clock ISO timestamp).
  New `mark-running <id> --run-id <wf_...> --session-dir <path>` subcommand
  records the Workflow run id + session workflows dir on a RUNNING entry,
  called by the dispatcher immediately after `Workflow()` returns.
- **Recovery verbs**: `reset <id>` (RUNNING|FAILED → QUEUED, `attempts += 1`,
  audit line) and `force-fail <id> --reason <text>` (RUNNING → FAILED, audit
  line, counts toward the circuit breaker) — human-operator-only, gated on
  current status (wrong-state invocation errors without mutating). Every
  entry gains an append-only `audit[]` list (`verb`/`timestamp`/`reason`).
- **wf-record evidence reader**: given a runId + session-dir, reads
  `workflows/wf_<runId>.json` for its terminal status; any parse error or
  absence yields `None` (opportunistic evidence only, never raises).
- **`reconcile` subcommand** (+ invoked at the top of `next`, never inside
  `status`): force-FAILs a RUNNING entry with definitive failed/killed
  wf-record evidence (counts toward the breaker); flags `SUSPECT-COMPLETE`
  on completed-but-unmarked evidence (human confirms via `mark`); flags
  stale no-evidence RUNNING entries as `SUSPECT` (informational only). All
  transitions gate on `status == RUNNING`.
- **`using-loom-pipeline` dispatcher wiring**: the batch loop steps now
  document calling `mark-running` immediately after `Workflow()` returns, a
  session taking over a batch running `reconcile` before its first `next`,
  the `reset`/`force-fail` recovery verbs, and the `SUSPECT`/
  `SUSPECT-COMPLETE` human-operator handling — plus the `{"done": false,
  "non_terminal": [...]}` shape `next` can now print. `AGENTS.md`'s managed
  command-surface entry for `batch_queue.py` extended to the full verb set.

##### Changed

- **`next`'s `done` derivation**: now `terminal_count == total` instead of
  assumed — while QUEUED/RUNNING entries remain, `next` prints
  `{"done": false, "non_terminal": [...]}` (id/status/reason per entry)
  instead of ever silently claiming the batch finished (previously a stuck
  batch could print `{"done": true}` — a fix to existing behavior).

Design SSOT: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4c
(all points).

#### [0.8.1] — 2026-07-17

##### Added

- **Close-out card** (`hooks/family-relay.md` §(a)) — a 10-row table
  specialization of the user-rollup card for close-out reporting
  (finishing Step 13, any loom seam reporting a PR-open): PR, Purpose,
  Changes, Impact scope, Verification, Review, Review focus, Version,
  🌐 Web merge, 💻 CLI merge, plus conditional screenshots/rollback-plan
  rows. Cell rules (one line, " ・ " separator, ≤3 points/cell, no
  `<br>` in chat cards) mirror the existing rollup card's discipline.
  Provenance: converges Google eng-practices CL-description convention
  with the JA 影響範囲/動作確認/レビューポイント PR-template convention.

Verification: `python3 -m pytest loom-pipeline/scripts/ -q` green.

#### [0.8.0] — 2026-07-17

##### Added

- **`loom-memory` record-verb contradiction check (0.2.0)** — mandatory
  contradiction check between classify and write: grep the store for
  contradicted entries, update or replace on hit, never add a
  contradicting sibling. Mirrors `git-memory`'s backward-pointing
  Supersedes doctrine by pointer.

Verification: `python3 -m pytest loom-pipeline/scripts/ -q` green.

#### [0.7.1] — 2026-07-14

##### Changed

- **Description token economy** — rewrote `using-loom-pipeline` and
  `loom-memory` frontmatter descriptions under the two-tier standard
  (router/CONDITIONAL exception band ≤500 chars, firing-evidence
  required): 1,019→475 and 974→492 rendered chars. CONDITIONAL
  firing conditions + `N/A`-loud announcement semantics and the
  strongest multilingual triggers preserved; thin-conductor/station
  exposition and synonym triggers cut per skill-dev-toolkit
  description-design cutting rules. Firing-evidence YAML comments
  cite the 2026-07-14 pre-sweep baseline (4/4 EXACT each,
  `docs/skill-dogfood/2026-07-14-description-token-economy/baseline.md`).
  Bodies untouched.

#### [0.7.0] — 2026-07-10

##### Added

- **Reception preloads Visual defaults** — `hooks/session-start` now
  extracts `family-relay.md §(b) Visual defaults` at runtime (awk
  heading-range over the SSOT file; zero rule text duplicated in the
  script) and appends it to the injected reception context. Motivation:
  session-log telemetry showed the pull-based relay file was actually
  Read in 1/216 loom sessions — the visual contract existed on paper
  only. Weak-model dogfood
  (`docs/loom/dogfood/2026-07-10-visual-trigger-weak-model-dogfood.md`)
  shows the preload fixes rule *visibility*; triggering behavior is
  carried by ascii-graph-toolkit 0.5.0's imperative card (sibling PR).
- `test_family_relay.py::test_reception_includes_visual_defaults` —
  proves runtime extraction via a copy-mutate-rerun-same-script
  mechanism; fail-open (missing relay file) preserved.
- Suite: 161 passed (`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest
  loom-pipeline/scripts/ -q`).

#### [0.6.1] — 2026-07-08

##### Fixed

- `lang_detect`: harness-injected user turns (skill-body echoes
  `Base directory for this skill:`, `[Request interrupted`, workflow
  echoes `Run the "<name>" workflow.`) no longer pollute
  conversation-language detection — with the unfiltered ruler the
  language anchor never fired in skill-heavy sessions (detection → None).
- `lang_detect`: detectability floor is now `visible ≥ 20 OR CJK ≥ 8`
  chars, and undetectable turns no longer dilute the majority vote —
  short CJK confirmations (「修」-style) count again.
- `comms_metrics` inherits both via the shared
  `majority_language`/`is_harness_injection` helpers; ruler-v2 baseline
  recorded in `docs/loom/audits/2026-07-08-comms-metrics-ruler-v2.md`.
- Suite: 158 passed (`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest
  loom-pipeline/scripts/ -q`).

#### [0.6.0] — 2026-07-07

##### Added

- **Family relay discipline SSOT** — `hooks/family-relay.md` becomes the
  single source of truth for relay behavior; `hooks/family-reception.md`
  keeps only a 2-line pointer to it, staying within its 60-line budget
  (Task 14 carrier).
- **Conversation-language detection helper** — `hooks/lang_detect.py`
  (Task 14 carrier).
- **Tail language-anchor hook** — PostToolUse on `Skill`, reasserting the
  conversation's target language after a skill invocation (Task 14
  carrier).
- **Stop-hook language-consistency validator** — enforces an absolute
  target-script-count rule at session Stop (Task 14 carrier).
- **Comms metrics recipe** — `scripts/comms_metrics.py` plus a baseline
  audit doc (Task 14 carrier).

##### Verified

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-pipeline/scripts/ -q`
  — 150 passed.

#### [0.5.0] — 2026-07-06

##### Added

- **`loom-memory` skill** — three verbs over the repo-native
  practice-memory store at `docs/loom/memory/`: **record** a distilled
  practice/gotcha/process into the store per its charter, **recall**
  relevant memories by grepping the index then bodies (pull-based,
  honest no-hits), **prune** stale entries into a keep/merge/retire
  proposal (never auto-deletes). CONDITIONAL: fires only when the
  target repo has `docs/loom/memory/README.md` — otherwise
  `loom-memory: N/A` with the reason, loudly (Task 1).
- **Family-reception recall pointer** — `hooks/family-reception.md`
  gains a pointer-only recall note: when the target repo has
  `docs/loom/memory/`, run a recall pass via `loom-memory` before
  starting loom work; the hook preloads no memory content (Task 2).

#### [0.4.0] — 2026-07-04

##### Added

- **Family reception** — `hooks/family-reception.md` + `hooks/hooks.json` +
  `hooks/session-start` inject the loom family map, the three doors, and
  the on-ramp criteria table (SSOT) at the start of every session, mirroring
  loom-code's SessionStart hook mechanism (Task A1).
- **`§Intake` for `using-loom-pipeline`** — three steps (upstream check
  against the reception criteria, station check/handoff, and the
  unchanged N/A-loud fire-condition reaffirmation) added ahead of
  `§When it fires` (Task A2).
- **README §Family entries & naming convention** — documents the
  one-sentence rule (「要用 loom-X, 就從 using-loom-X 開始」), the
  `using-loom-*` entry vs. plain-name station convention, why
  `brainstorming` (loom-code's discovery skill) folds the family-entry
  intake into its own Axis 0 rather than duplicating a `§Intake` heading
  in `using-loom-code`, and a reception paragraph pointing at the
  `SessionStart` hook (Task A3).

#### [0.3.1] — 2026-07-04

##### Fixed

- **Dead `args.budget` plumbing removed (segment 3)** — `runSegment3`
  destructured a singular `budget` from args and threaded it through
  every station's opts, but nothing supplies that field (the run-input
  contract and the batch payload carry only `budgets` plural), so the
  value was always `undefined` and the ambient Workflow `budget` global
  did the real work via `resolveBudget`'s fallback. The pass-through is
  gone; `opts.budget` stays reserved for unit-test injection. Found by
  PR #483's whole-branch review; pre-existing since v0.1.0.
- **Adopt-if-valid is a cost-cut record, not an intervention** — the
  segment-1 principles preamble called an adopt a "cost-cut
  intervention", which mis-filed routine adopts into ledger bucket A
  (live-verify finding). The preamble now says: record the adopt in the
  verdict summary and do NOT file it as an `interventions[]` entry —
  interventions are for deviations needing triage (buckets A/B/C), not
  for taking the documented cheap path.

#### [0.3.0] — 2026-07-03

##### Added

- **Brief+plan freeze form** — `batch_queue.py`'s freeze predicate now
  accepts a second form: when no `docs/loom/<change-id>/` change folder
  exists, an entry is frozen if its (committed) plan file carries a
  `Plan-document-reviewer verdict: PASS` line. Real interactive work
  (observed live on a consumer project, 2026-07-03) produces
  brainstorm-brief + reviewer-PASSed plan with no OpenSpec change
  folder; v1.1's change-folder-only predicate would have SKIPPED every
  such entry. A change folder that exists but fails the validator is
  still a hard reject — never a fallback to the plan-verdict form.

#### [0.2.0] — 2026-07-03

Batch implementation mode (v1.1): a queue of FROZEN change-folders runs
Segment 3 unattended, one change at a time — N ledgers + N `loom/<id>`
PR branches out, merge stays human. Human gates (a) change-id and (c)
cost policy move to freeze time (queue-entry authoring); no scheduler,
time-agnostic.

- New host-side bookkeeping CLI `scripts/batch_queue.py`
  (`next` / `mark` / `status`): parses the human-edited
  `docs/loom/QUEUE.toml` (stdlib `tomllib`), keeps machine-owned state
  in `docs/loom/queue-state.json`, verifies the freeze predicate
  (loom-spec validator exit-0 + plan committed), creates the per-change
  worktree/branch (`.worktrees/loom-<id>`, branch `loom/<id>`), and
  emits ready-to-use Workflow args JSON for Segment 3.
- Failure isolation: ineligible entries are SKIPPED loudly with the
  predicate's reason (uncommitted-plan skips tear the just-created
  worktree back down); a failed change never stalls the queue.
- Circuit breaker: 2 consecutive FAILED terminal outcomes halt the
  queue (exit 3); `--override-halt` bypasses after human review.
- SKILL.md §Batch mode: the dispatcher-only loop contract
  (`next` → `Workflow({segment: 3, …})` → `mark`) — the main agent
  never parses the queue file, never composes git commands, never
  diagnoses failures mid-batch.
- Zero driver changes: the v1 `assets/loom-pipeline.js` asset and all
  `driver_*.js` sources are byte-identical to 0.1.0.

#### [0.1.0] — 2026-07-03

Conductor plugin born: the entry skill (`using-loom-pipeline`) plus the
build-assembled driver asset (`assets/loom-pipeline.js`, composed from
`scripts/driver_00_header.js` through `driver_60_ledger.js` — guard,
`runStation`, the 3 segments, ledger, and the `main` entrypoint).

- F1–F5 driver hardening baked in (per-station token budgets with
  fail-loud over-budget, wall-clock watchdog per station, rally cap
  ≤2 on critic↔writer loop-backs, change-strategy recovery ladder,
  stable-prefix dispatch convention).
- G1 (run-level + per-station token budgets), G3 (validator-checked
  Decisions section per artifact), and G6 (idempotent adopt-if-valid
  re-runs, journal resume, "checkpointed, not durable" naming) baked
  into the driver.
- G2 (critic false-positive rate) and G5 (per-judge verdicts,
  cross-vendor judging) recorded as ledger metrics — not solved in v1.
- Canonical 6-field run-input contract (change-id, project path,
  budgets, model policy, skillsRoot, optional resumeRunId), fail-loud
  on any missing required field.
- Fail-loud doctrine throughout: N/A conditions, missing fields, and
  over-budget runs all surface loudly rather than silently degrading
  or improvising a default.

### loom-product-principles

> absorbed into loom-design 0.1.0 (2026-08-17); `product-principles` survives as a 1.0.0 tool.

#### [0.13.0] — 2026-08-15 — brief-before-fork dedup pointer

##### Changed

- **`using-loom-product-principles` points at the family SSOT for the
  brief-before-fork trigger** instead of carrying an in-place copy of the
  threshold triple — the triple now lives once in
  `loom-pipeline/hooks/family-reception.md §Brief before a complex fork`.

#### [0.12.1] — 2026-08-02 — citation repoint after the backlog store split

##### Changed

- **`scripts/validate_principles_output.py` and
  `scripts/test_validate_principles_output.py`**: comment citations that
  pointed at a heading inside the old `docs/loom/BACKLOG.md` monolith now
  name the entry file that owns that item under `docs/loom/backlog/`. The
  monolith became generated output in the same arc, so the old in-file
  anchors no longer resolve. Comments only — no executable line changed.
  Each filename is kept on a single line so `grep` for it finds the
  citation; an earlier pass wrapped them mid-path, which silently
  reintroduced the un-findable-reference problem the repoint existed to fix.

#### [0.12.0] — 2026-07-25 — bba imperative in entry router

##### Added

- **`skills/using-loom-product-principles/SKILL.md`**: §Intake step 2 now
  carries a one-line `dev-workflow:brief-before-asking` imperative
  (#475 complex-fork escalation), mirroring
  `loom-pipeline/skills/using-loom-pipeline/SKILL.md:158` — before the
  router asks the user a non-trivial trade-off fork (≥3 trade-offs,
  ≥2 implementation paths, or architectural blast radius), it must run
  brief-before-asking first.

#### [0.11.0] — 2026-07-18 — mechanize marker whitelist + Anchors provenance

##### Added

- **`scripts/validate_principles_output.py`**: two new mechanical checks
  (BACKLOG.md §knowledge-triage v2.1 cut (d), leg-3 dogfood failure —
  `docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`). (1)
  `evidence_needed:` value whitelist {craft, domain-convention,
  project-local} and a non-empty-reason check on `— assumption:` markers,
  wherever either appears in the file. (2) A new OPTIONAL `--seed <path>`
  CLI argument: when given, `## Anchors` rows whose provenance cell claims
  seed origin (contains "seed") must share a literal substring
  (calibrated threshold, see `_PROVENANCE_MIN_MATCH`) with the seed file
  — catches the real leg-3 failure mode (Anchors rows labeled "anchored to
  seed" for numbers the seed never stated). No `--seed` -> the provenance
  check is skipped entirely (backward compatible).

#### [0.10.0] — 2026-07-18 — standing knowledge-triage at check-drafting

##### Added

- **`product-principles/references/knowledge-triage.md`**: pinned
  three-bucket vocabulary (craft / domain-convention / project-local);
  when a principle's `— check:` cannot be written without guessing a fact,
  classify FIRST — domain-convention facts route through the existing
  Tripwire punt to `using-loom-discovery` with `evidence_needed:` tag and
  the principle stays DRAFT until evidence returns or the user accepts an
  explicit `— assumption: <reason>` marker. Standing posture (constitution
  = one-way door), not stall-triggered. No live research in-station.

#### [0.9.1] — 2026-07-14

##### Changed

- `product-principles` skill description rewritten under the two-tier
  token-economy standard (569 → 329 rendered chars; "rendered" = length
  of the YAML-parsed description string, trailing newline stripped). The 150-250 soft band is
  exceeded with an in-file justification comment: the description
  retains three-jurisdiction principle-guidance triggers (product /
  design / engineering decisions, 設計原則 / 工程原則) that the routing
  corpus doesn't yet cover. English synonym triggers and identity
  restatement cut, negative redirect converted to a positive delegation
  (`design-critic/completeness-critic`). Frontmatter only — skill body
  unchanged.

#### [0.9.0] — 2026-07-13

##### Changed

- **The visual lens is now a SINGLE Axis-A round.** The surface-treatment axis
  (flat / skeuomorphic / neumorphic / glassmorphic eras) is **no longer decided
  here** — industry research placed it at **stage 4 (the visual design language)**,
  so it is now decided **downstream at the DESIGN station**
  (`loom-interface-design`), which owns the canon and names its pick in prose
  there. The Axis-A round (cultural / graphic-design movements) is unchanged:
  it keeps the 3-5 carve-out, the 1-2 divergent candidates, and the anti-costume
  law. The old cross-axis contamination guard is now **structural, not
  instructional** — the two axes live in different plugins, so their contexts
  cannot co-occur in one round by construction.
- The canon completeness-audit list drops to **four** files (the fifth,
  `canon-design-surface.md`, moved out — see Removed).

##### Removed

- **`references/canon-design-surface.md`** — relocated to
  `loom-interface-design/skills/design-system/references/` (its correct station).
  The forward-note added in 0.8.0 ("relocation deferred to Step 2") is spent and
  gone. `scripts/test_surface_canon.py` was deleted here; its contract test and
  research-doc guard now live in the receiving plugin.
  Rationale: `docs/loom/specs/2026-07-13-axis-b-relocation-and-tone-manner-seam.md`.

#### [0.8.0] — 2026-07-12

> Retroactive entry (2026-07-13): 0.8.0 shipped without a CHANGELOG record —
> reconstructed here from PR #553 so the file is not missing a version.

##### Added

- **Tone & manner primary anchor** — the Design lane's visual flow now derives
  **3-5 tone & manner adjectives** from the product's values BEFORE any canon
  round. They are the **primary visual anchor** and land as their own
  version-pinned `## Anchors` row (existing machinery, reused).
- 16 live-verified cultural entries in `references/canon-design-visual.md`
  (canon 19 → 35 rows): 6 Euro-American, 4 Japan, 1 Soviet, 5 Greater China.
  Six high-costume-risk rows carry per-row caveats; the two propaganda-origin
  rows additionally state "formal visual vocabulary only, never the propaganda
  freight."

##### Changed

- **Axis A reframed as value-constrained mood inspiration** — it is downstream
  of the tone & manner anchor, supplies **mood / creative-direction inspiration**,
  and is **never a pick-one menu**. The anti-costume rule is generalized into a
  law: a movement **never overrides a PRINCIPLES value** (the low-stimulus /
  Memphis case is demoted to its worked example).

#### [0.7.0] — 2026-07-12

##### Added

- **Visual-style movement anchoring, Phase 1** — the Design section's visual
  lens now runs as **two axis-typed candidate rounds**: Axis A (cultural /
  graphic movements, `references/canon-design-visual.md`) and Axis B (UI
  surface treatments, new `references/canon-design-surface.md`), each round
  reading ONLY its own file (a contamination guard so reasoning about one axis
  is not polluted by the other). The visual lens widens from 2-3 to **3-5
  candidates**, deliberately including **1-2 divergent/exploratory** candidates
  that deviate from the user's stated stance but stay defensible against the
  PRINCIPLES values (anti-costume: exploration never overrides the
  non-negotiable values). The generic 2-3 count for the Product and Engineering
  sections is unchanged.
- **`references/canon-design-surface.md`** — new Axis-B seed (~6 UI surface
  treatments with a `Currency` column and risk flags, e.g. neumorphism's
  low-contrast WCAG risk), grounded in
  `docs/loom/research/2026-07-12-ui-surface-treatments-canon.md`. Kept out of
  the ≥14-entry `CANON_FILES` contract by design (small, extensible seed).

##### Changed

- `references/canon-design-visual.md` is now Axis-A-only — the collapsed
  surface-treatment cycle row was rehomed to `canon-design-surface.md`.

#### [0.6.1] — 2026-07-12

##### Added

- **Mechanical seed-coverage gate** (#545): `§Headless/seeded mode` gains an
  inventory-authoring step (extract every seed-named entity into
  `seed-inventory.md` in the checker's oracle format BEFORE drafting;
  `named_anchors:`/`deferred_items:` only, `negative:` forbidden); Step 8
  now also runs `check_seed_traceability.py <artifact> <inventory>`
  exit-0-gated (interactive sessions derive the inventory from confirmed
  user answers). The prose "post-draft seed walk" self-report is
  superseded by the mechanical gate. Acceptance: replay-matrix pass-rate
  22% → 67% with the dominant failure class displaced
  (`docs/loom/dogfood/2026-07-12-mechanical-seed-gate-baseline/`).

#### [0.6.0] — 2026-07-11

##### Added

- (entry backfilled 2026-07-12 — release shipped without one) **Escalation
  appetite landing shape** (#537): `references/principles-rules.md` gains
  §Escalation appetite — the greppable `escalation appetite` entry contract
  under `## Engineering Principles`, consumed read-once by loom-code's
  kickoff briefing and SDD mid-implementation escalation.

#### [0.5.1] — 2026-07-10

##### Fixed

- **`§Headless/seeded mode` gains the seed-traceability invariant + a
  post-draft seed walk** (the headless mirror of the interactive coverage
  self-check): every seed item — each individual stance, named canon,
  tech-stack choice, or deferred marker, even when several share one
  bullet — must land in at least one of a carrying principle, an
  `## Anchors` row, an Open Question with a re-trigger, a
  `## Deviation Ledger` entry, or (for North-Star-bound facts) the
  `## North Star` section; out-of-jurisdiction seed content is noted, not
  silently skipped — no silent drops. Evidence: an n=4
  weak-model headless seeded replay of the construction flow
  (`docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/seed.md`)
  showed the seed's deferred stance dropped 4/4, seed-named canons
  dropped from Anchors (Apple Design Language 0/4, Core ML 0/4,
  JTBD 1/4), and stance coverage compressed 7→4-5 — one root cause: the
  mode had no rule for seed content that is neither an answer nor a gap.
- Oracle calibration in the cold-operator dogfood seed: the 「恰 7 條」
  count assertion replaced with the coverage form (count is not the
  invariant — merging is legitimate); the C9 negative pattern narrowed
  to development-team-as-decision-actor phrasings.
- The invariant's Open Question landing spot now has a defined format
  home: `references/principles-rules.md` gains an optional
  `## Open Questions` section (ordered list, one physical line per entry,
  literal `— re-trigger:` marker stating when to revisit) plus validator
  contract rule 8, and `validate_principles_output.py` enforces it when
  present (absent stays valid).
- **Never-out-of-jurisdiction guard for seed-named canons**: a post-fix
  weak-model replay (n=2) showed the out-of-jurisdiction landing being
  used as an escape hatch to drop seed-named canons/tech-stack choices,
  rationalized as "TECH-SPEC turf" or "downstream spec"; the invariant
  now states categorically that a seed-named canon, tradition, or
  tech-stack choice is never out-of-jurisdiction — that landing is
  scoped only to §Boundary's own categories (market / business-model /
  strategy-document content) — and names the misclassification a
  violation.

##### Verified

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-product-principles/scripts/ -q`
  → 170 passed (146 baseline + 24 new pins across three review rounds:
  5 validator + 9 rules + 10 skill, RED-then-GREEN). A follow-up 6-run
  replay matrix (deferred→Open Question 0/4→6/6, bait 5/5, validator
  6/6) confirmed the fix; residual prose-named-anchor gaps deferred to
  a future mechanical post-run verification.

#### [0.5.0] — 2026-07-10

##### Added

- **Construction-flow rewrite of `product-principles` SKILL.md's elicitation
  core**: user-states-first → question-set probing → same-axis canon
  candidates (with considered-but-rejected recorded per round) → the user
  decides the mix or goes bespoke → version-pinned `## Anchors` +
  `## Deviation Ledger` + falsifiable principles → per-section and final
  read-backs. New `§Headless/seeded mode` covers unattended runs, including
  a thin-seed `BLOCKED` refusal and greppable `(agent-decided)` markers for
  choices made without a human in the loop.
- New reference files: `references/question-sets.md` and four canon base
  lists — `references/canon-product.md`, `references/canon-design-interaction.md`,
  `references/canon-design-visual.md`, `references/canon-engineering.md` —
  supplying the same-axis candidates the construction flow proposes.
- `references/principles-rules.md` gains `## Anchors` and `## Deviation
  Ledger` format rules (enforce-when-present) plus validator contract
  rules 6–7 describing how `validate_principles_output.py` checks them.
- `scripts/validate_principles_output.py`: enforce-when-present checks for
  both the `## Anchors` and `## Deviation Ledger` sections.

##### Verified

- Cold-operator dogfood
  (`docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/`): 4 PASS +
  1 PARTIAL; findings F1–F3 folded back into the construction flow (see
  the `fix(loom-product-principles)` commit above).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-product-principles/scripts/ --collect-only -q`
  → 145 tests collected.

#### [0.4.1] — 2026-07-07

##### Changed

- **`using-loom-product-principles` §Intake points at the family relay
  discipline**: the entry skill's intake now cites
  `loom-pipeline/hooks/family-relay.md` as the shared reference for
  how it talks to the user, rather than restating relay rules locally.
  Verification: `test_family_relay.py::test_design_side_pointers[product-principles]`
  passed.

#### [0.4.0] — 2026-07-04

##### Added

- **New `using-loom-product-principles` entry skill**: a thin family-entry
  router (§Intake — 前站檢查 / 對站檢查 / handoff to `product-principles`)
  for users who aren't sure where to start. Its description is
  entry-framed and deliberately avoids `product-principles`' own
  direct-ask triggers (產品原則 / north star / 憲章) so the entry never
  steals the member's direct pull (#456 positive-specificity).
- `product-principles` SKILL.md gains a **Next station** close-out line:
  once `PRINCIPLES.md` is shipped, hand off to `using-loom-interface-design`
  for UI-bearing products, or to `using-loom-spec` to expand a feature
  directly for headless / CLI-only products.

Both changes are part of the loom-family connective-tissue pass wiring the
`using-loom-*` entry-skill convention across the pipeline.

#### [0.3.0] — 2026-07-03

##### Changed

- **Three-jurisdiction sections**: the required section renamed
  `## Principles` → `## Product Principles` (legacy `## Principles` files
  are detected and migrated with a one-line message, not silently
  rejected). Two new optional sections, `## Design Principles` and
  `## Engineering Principles`, each 1–7 falsifiable principles and never
  emitted empty — jurisdiction-appropriate content is elicited only when
  the product warrants it. `references/principles-rules.md` gained the
  Jurisdictions table and the posture-elicitation steps (does this product
  need a Design jurisdiction? an Engineering jurisdiction?) that decide
  whether each optional section is generated.
- Unqualified "product-level" claims in `SKILL.md` / `principles-rules.md`
  / `README.md` widened to project-constitution framing; the `## Product
  Principles` jurisdiction itself is unchanged in scope (product design
  principles + target user, not business/market/strategy).

- §Downstream updated to reflect the wired reality: named per-station intake
  sections (design generators, `loom-spec:spec-expansion` §Governing
  constraint, both critics' principles lenses) and the **live** loom-code
  `code-reviewer` D8 principles-conformance gate — replacing the stale "a
  future conformance gate may check artifacts" forward-reference.

##### Fixed

- Skill description restored to the proactive, trilingual-trigger form: fires
  BEFORE design/spec/build (not only when asked), carries 產品原則 / 產品憲章 /
  プロダクト指針 triggers and the "north star" phrasing the test suite encodes,
  and states a when-NOT boundary. #456's rewrite had dropped the CJK triggers
  and made the description reactive-only, silently breaking 2 tests (no CI ran
  them) and likely re-opening the pre-#456 under-firing this plugin was known
  for.

- `product-principles` SKILL.md now states the correct skill-dir-relative
  validator path (`../../scripts/validate_principles_output.py`); the
  previously claimed `scripts/…` form did not resolve from the skill directory
  in an installed plugin.
- Earlier unversioned post-0.2.0 changes: trigger-description rewrite (#456),
  reply-honesty prose fixes (#465).

#### [0.2.0] — 2026-06-21

##### Changed

- **BREAKING**: plugin renamed `product-principles-toolkit` →
  `loom-product-principles`; artifact path unified to
  `docs/loom/PRINCIPLES.md` (#440).

#### [0.1.0] — 2026-06-14

##### Added

- MVP: `product-principles` skill — turn a sparse product idea into a
  `PRINCIPLES.md` constitution (north-star + 3–7 falsifiable principles) —
  plus `validate_principles_output.py` structure validator (#398).

### loom-spec

> absorbed into loom-design 0.1.0 (2026-08-17); `spec-expansion` and `completeness-critic` became the write-spec station and loom-code's spec lens in 1.0.0.

#### [0.11.0] — 2026-08-15 — brief-before-fork dedup + conversation-language phase announcements

##### Changed

- **`using-loom-spec` points at the family SSOT for the brief-before-fork
  trigger** instead of carrying an in-place copy of the threshold triple — the
  triple now lives once in `loom-pipeline/hooks/family-reception.md §Brief
  before a complex fork`.
- **`spec-expansion` announces its phases in the conversation language, not
  internal markers.** Phase narration changed from verbatim "— Phase ① USM
  backbone —" chat markers to "next I'll lay the user-journey backbone" plain
  language; internal phase IDs stay in the artifact only.

#### [0.10.0] — 2026-08-14 — layered language policy for spec artifacts

##### Changed

- **spec-expansion SKILL.md declares the layered language policy.** Spec-delta
  **requirement lines** (RFC-2119) and **Scenario** GIVEN/WHEN/THEN criteria
  are written in English; proposal.md narrative (Problem / Users / Smallest
  End State / Decision reasoning) stays in the session's conversation
  language. `adjudication-view` is cited as the display layer for careful
  reading of the English precision content in zh-Hant/ja.

#### [0.9.0] — 2026-08-11 — OOUX Mermaid diagram forms

##### Changed

- loom-spec 0.9.0: OOUX visible artifact renders each object's state machine
  as Mermaid `stateDiagram-v2` and object relations as `erDiagram`,
  fill-or-declare with the pinned N/A line.

#### [0.8.1] — 2026-08-02 — citation repoint after the backlog store split

##### Changed

- **`scripts/validate_spec_output.py` and `scripts/test_consistency_lens.py`**:
  comment citations that pointed at a heading inside the old
  `docs/loom/BACKLOG.md` monolith now name the entry file that owns that
  item under `docs/loom/backlog/`. The monolith became generated output in
  the same arc, so the old in-file anchors no longer resolve. Comments only
  — no executable line changed. Each filename is kept on a single line so
  `grep` for it finds the citation; an earlier pass wrapped them mid-path,
  which silently reintroduced the un-findable-reference problem the repoint
  existed to fix.

#### [0.8.0] — 2026-07-25 — bba imperative in entry router

##### Added

- **`using-loom-spec`**: the router body now names
  `dev-workflow:brief-before-asking` and the canonical trigger triple
  (`≥3 trade-offs, ≥2 implementation paths, or architectural blast radius`)
  so a non-trivial spec-decision fork surfaced by the router gets a
  proactive briefing reminder before the agent asks the user. Mirrors
  `loom-pipeline/skills/using-loom-pipeline/SKILL.md`'s gate (b) pattern.
  Guarded by `scripts/test_spec_entry_skill.py::test_entry_router_names_bba`.

#### [0.7.0] — 2026-07-18 — outer revision cap + minted critic verdicts

##### Added

- **`completeness-critic`**: the writer↔critic outer revision cycle is now
  capped at 2 — on the 2nd consecutive `NEEDS_REVISION` after a revision, the
  loop stops and hands back to the user with a plain-language list of
  unresolved findings instead of silently re-running.
- **`scripts/mint_critic_verdict.py`**: new content-hash-bound critic-verdict
  CLI (`mint --change-folder --critic --verdict-file --files` /
  `validate --change-folder --critic --files`) — sha256-binds a verdict to the
  exact files it covered; `validate` exits 0 fresh-`PASS_WITH_NOTES`, 2 no-verdict,
  3 fresh-`NEEDS_REVISION`, 4 stale-hash. `NEEDS_REVISION` still mints (a
  rejected draft's verdict is itself evidence); overwrite-in-place, path- and
  UTF-8-guarded.
- **`completeness-critic`**: the verdict step now additionally runs
  `mint_critic_verdict.py mint` for the change-folder on both verdict values.
- **`spec-expansion`**: gains a validate-before-fan-out step consuming
  `loom-interface-design`'s design-critic verdict — runs
  `mint_critic_verdict.py validate --files DESIGN.md,ui-flows.md` and
  proceeds only on exit 0; on 2/3/4 it stops and reports which condition
  blocked (never-ran / critic-blocked / stale) instead of fanning out over an
  unreviewed or stale design.

Design SSOT: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` §4
recs 2/7 + §4c Fix-4.

#### [0.6.0] — 2026-07-18 — mechanize knowledge-triage enforcement semantics

##### Added

- **`scripts/validate_spec_output.py`**: three deterministic checks over the
  emitted spec directory (`proposal.md` + `specs/**/spec.md`) —
  (1) `evidence_needed:` value whitelist (craft / domain-convention /
  project-local; any other value fails naming file:line + the offending
  value); (2) every `evidence_needed: domain-convention` occurrence must
  carry a SHAPING or DEFERRABLE tier label in its own list item/paragraph
  or that block's governing heading/lead-in line (structural scoping, not
  a character-distance window); (3) a SHAPING-classed domain-convention
  item without a `deferred: <reason>` note in its own scope fails naming
  the VERIFY gate rule. Mechanizes the enforcement semantics that a 3-leg
  weak-model dogfood proved prose-only instructions do not survive (see
  `docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`).
- **`completeness-critic/references/consistency-lens.md`**: a cross-layer
  consistency lens — checks `proposal.md`'s FLAG/open-question items against
  `spec.md`'s requirement text; a requirement that silently resolves a
  question the proposal flagged as open is an OMISSION finding (severity 3
  by default), fed into the critic's existing consolidated/ranked pipeline.

#### [0.5.0] — 2026-07-18 — domain-tag triage at edge-case expansion

##### Added

- **`spec-expansion/references/domain-tag-triage.md`**: pinned three-bucket
  vocabulary (craft / domain-convention / project-local); non-derivable edge
  cases classify FIRST — domain-convention facts become tagged open questions
  (`evidence_needed:`), never invented answers. SHAPING-class tags (answer
  alters acceptance criteria, data semantics, or a state machine) block
  VERIFY unless explicitly `deferred: <reason>`; resolution routes OUTSIDE
  the skill between draft and gate — drafting stays closed-world.

#### [0.4.3] — 2026-07-15

##### Changed

- **`spec-expansion` SKILL.md 4,113 → 3,584 words (−12.9%)**: the persisted
  intent-layer sections (§Consuming prior-state + §Authoring TOP/MID) extracted
  to `references/intent-layer.md` with trigger-carrying pointers; the
  `[active|deferred]` declaration syntax and the ui-flows seam table stay
  inline. Behavior equivalence proven via 4 test prompts × 3-judge ensemble
  (12/12 EQUIVALENT); first `test-prompts.json` shipped for this skill.
  Slim round 2 of the Pocock token-economy roadmap.

#### [0.4.2] — 2026-07-07

##### Changed

- `using-loom-spec` §Intake now points at the family relay discipline
  (`loom-pipeline/hooks/family-relay.md`) instead of restating it inline —
  closes the BACKLOG loom-spec briefing-gate item. Verification:
  `test_family_relay.py::test_design_side_pointers[spec]` passed.

#### [0.4.1] — 2026-07-05

##### Added

- **`using-loom-spec/references/claude-code-tools.md`** + **`codex-tools.md`**
  — `completeness-critic`'s multi-lens panel already phrased subagent
  dispatch in host-neutral prose ("phrase this fan-out portably... not
  bound to any one harness/tool, because this skill is agent-portable"),
  but had zero concrete reference for what that resolves to on either
  host. Added the same host-neutral skill body + per-host tool-mapping
  reference pattern `loom-code` uses (`obra/superpowers` is the confirmed
  prior-art source for this pattern). Codex side documents `multi_agent`/
  `spawn_agent`/`wait_agent`/`close_agent`, verified 2026-07-05 via `codex
  features list` on a live Codex 0.139.0 install (feature flag itself
  live-confirmed) + OpenAI's official Codex manual §Subagents (verb
  names/behavior doc-confirmed, not independently re-exercised for this
  plugin's specific dispatch points). `completeness-critic/SKILL.md`'s
  panel section now points at both files.

#### [0.4.0] — 2026-07-04

##### Added

- `using-loom-spec` — a new thin entry/router skill completing the family's
  `using-loom-*` convention (loom family connective-tissue plan). §Intake
  checks upstream/peer fit against the loom-pipeline reception SSOT, then
  routes between loom-spec's two members by the specific verb: draft/expand
  from a seed → `spec-expansion`; critique/audit an existing draft → the
  member skill this router names — closing the #456-documented
  adjacent mis-route where a critique-an-existing-draft ask got sent to
  `spec-expansion` instead. Guarded by
  `scripts/test_spec_entry_skill.py`.

##### Changed

- `test_spec_entry_skill.py::test_intake_step2_peer_check_present` is now
  step-2-scoped: it slices Step 2's own paragraph (between the `**Step 2`
  and `**Step 3` markers) and asserts the three redirect-target names
  (`using-loom-interface-design`, `using-loom-product-principles`,
  `using-loom-code`) are present within it, rather than grepping the whole
  file for `對站檢查`/`step 2` — the prior assertion stayed green even if
  step 2's redirect targets were dropped (and a whole-§Intake slice was
  still too coarse: Step 1 independently names two of the three targets).
  Mutation-verified: all three assertions fail on a step-2-stripped copy.
  Found during C1/C2's quality reviews.
- README §Scope: the `using-loom-spec` PARK paragraph now reflects the
  supersession — the thin entry shipped in 0.4.0; the park stands for the
  tiering-capable upgrade only, re-triggers unchanged.

##### Verified

- `spec-expansion`'s existing `loom-code:writing-plans` next-station
  pointer (§Boundary — stops at GENERATE) already names the
  validated-change-folder → writing-plans handoff explicitly; no edit was
  needed — this release just confirms the wiring the brief asked to check.

#### [Unreleased]

##### Decided

- **[SUPERSEDED by 0.4.0]** — a THIN `using-loom-spec` entry (intake +
  member disambiguation, NO tiering judgment) shipped via the loom family
  connective-tissue plan; the park below concerned the tiering-capable
  router, whose re-triggers (DECLARE lands, discovery/persist scheduled)
  remain valid for adding tiering to the now-existing entry.
- **`using-loom-spec` router: parked, with explicit re-triggers** (audit
  close-out, reaffirming the MVP brief's v0.2 deferral). The router's
  load-bearing job per the 2026-06-11 research synthesis is the
  proportional-rigor **tiering judgment**, which depends on
  `spec-discovery` / `spec-persist` and the OpenSpec DECLARE layer — none
  built. The writer→judge sequencing concern that re-raised the question is
  already covered in-skill (spec-expansion handoff + completeness-critic
  verdict resolution, shipped in the audit's earlier PRs). Re-triggers in
  README §Scope: DECLARE lands, or discovery/persist are scheduled — the
  router ships with its tiering cargo, not before it. Also fixed the README's
  dead pointers to the pre-rename brief/research filenames (frozen docs keep
  old names; the pointers now match).

##### Changed

- `spec-expansion` §Consuming a `ui-flows.md` seed now names the seed's
  canonical per-change location (`docs/loom/<change-id>/ui-flows.md`, the same
  change folder this skill emits into) — following loom-interface-design's
  move of `ui-flows.md` off the fixed product-level path.

##### Added

- `completeness-critic` now ends every run with a **machine-readable two-valued
  verdict** — `PASS_WITH_NOTES` / `NEEDS_REVISION` (aligned with loom-code's
  reviewer vocabulary; an unqualified PASS is deliberately absent — it would be
  a completeness claim, and Blind spots is non-empty by construction). Verdict
  semantics: `NEEDS_REVISION` when a severity-3 finding cannot be concretely
  re-seeded or the validator fails post-write-back. The **severity scale is now
  defined** (3 = load-bearing / 2 = should-add / 1 = polish, same scale as
  design-critic), and the write-back is documented as the sanctioned
  GENERATE-station exception to the evaluator-does-not-modify rule (repo
  CLAUDE.md). Guarded by `test_verdict_two_valued_enum` +
  `test_severity_scale_defined`.

- `spec-expansion` now reads `docs/loom/PRINCIPLES.md` as a **governing
  constraint** before expanding (new §Governing constraint — constitution→spec
  seam): the constitution bounds the fan-out scope, steers Phase ③ pruning
  priorities, and sets the NFR posture; absence is surfaced loudly (expansion
  proceeds only with an explicit "ungoverned" caveat). Closes the seam gap
  where product-principles claimed to govern spec-expansion but only the
  completeness-critic's post-hoc lens ever read the constitution. Guarded by
  `test_body_reads_principles_as_governing_constraint`.

#### [0.3.1] — 2026-06-21

##### Changed

`validate_spec_output.py` now accepts `## MODIFIED Requirements` and
`## REMOVED Requirements` as valid delta-block openers, not just
`## ADDED Requirements`. An OpenSpec change may add, modify, or remove
requirements; gating the delta on `ADDED` alone walled off legitimate
MODIFIED/REMOVED change-folders. Backward-compatible — every input the
validator previously accepted still passes; it only stops rejecting the
two previously-walled-off block kinds. More OpenSpec-faithful.

Known edge (out of scope, documented in the validator): a pure
`## REMOVED Requirements` delta with no scenarios still fails the
GIVEN/WHEN/THEN scenario check — a removal may legitimately carry no
scenario. That is a separate, deeper decision; this change only makes
the three block openers reachable.
