# Changelog

All notable changes to the dev-workflow plugin will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).
Versioning follows [Semantic Versioning](https://semver.org/).

## [2.2.0] — 2026-05-04

### Added — hardened AskUserQuestion pattern in skill-creator-advance

New reference: `skill-creator-advance/references/asking-user-questions.md`
documenting the empirically-validated 4-hardening pattern for skills that
need structured user input via Anthropic's `AskUserQuestion` tool.

The pattern closes three documented failure modes:
1. **Inline fallback** — model treats question as text instead of tool call
2. **Silent default** — model assumes "(recommended default)" and skips asking
3. **Tool unavailable** — subagent / web client / sandbox contexts have no
   AskUserQuestion; without explicit fallback, model silently defaults

The 4 hardenings (all validated via subagent A/B test on 2026-05-04):

1. **MUST verb** — `MUST call AskUserQuestion` instead of `Use AskUserQuestion`
2. **Args-schema example** — fenced ` ```json ` block showing tool-call args,
   not prose Q&A template
3. **Fallback contract** — explicit clause for tool-unavailable environments
4. **(Recommended) marker** — first option's `label` includes `(Recommended)`

Updates to `skill-creator-advance/SKILL.md`:
- New "Asking the User Structured Questions" subsection in §Skill Writing Guide
- New Pre-Creation Gate 3 ("User-input check") to prompt skill authors to
  apply the hardened pattern when drafting STEPs with user-input branching

Reference file includes:
- The Thariq canonical phrase (load-bearing tokens: `AskUserQuestion`,
  `interview`, `not obvious`)
- Anti-patterns table (7 documented failure modes)
- Copy-paste mandatory-gate template
- Industry references (Anthropic blog, Thariq gist, neonwatty walk-through,
  ClaudeLog, claude-code#9846 plan-mode bug)

Companion to domain-teams v5.6.0's CHK-SKL-014 gate that enforces the
same pattern for domain-team skills.

## [2.1.1] — 2026-05-04

### Fixed — duplicate hooks file load error on Claude Code v2.1.119+

Removed the redundant `"hooks": "./hooks/hooks.json"` field from
`plugin.json`. Claude Code automatically loads the standard
`hooks/hooks.json` location, so declaring the same path in
`manifest.hooks` triggered a duplicate-load error:

```
Failed to load hooks from .../hooks/hooks.json: Duplicate hooks file detected:
./hooks/hooks.json resolves to already-loaded file. The standard
hooks/hooks.json is loaded automatically, so manifest.hooks should
only reference additional hook files.
```

The PostToolUse skill-folder-structure validator added in 2.1.0 still
ships and still fires — only the redundant manifest entry was removed.

## [2.1.0] — 2026-05-03

### Added — plugin-shipped Stop hook for skill folder structure validation

dev-workflow now ships a `PostToolUse` hook on `Write|Edit` that
validates skill folder structure against the Anthropic convention
(subfolders may not themselves contain subfolders). The hook fires
in any project where dev-workflow is installed, catching nested
subdirectory violations the moment they're written.

**Files added**:
- `hooks/hooks.json` — registers `PostToolUse` hook on `Write|Edit`
  matcher pointing to `${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill-folder-structure.sh`
- `scripts/validate-skill-folder-structure.sh` — bash validator. Reads
  PostToolUse JSON from stdin, extracts `tool_input.file_path`, finds
  the affected skill root, runs `find <skill-root> -mindepth 2 -type d`
  to detect nested subdirs. Exit 2 (blocking) on violation, 0 otherwise.

**Plugin manifest** (`.claude-plugin/plugin.json`):
- Added `"hooks": "./hooks/hooks.json"` field

**Coexistence with repo-level hook (no duplicate firing)**:
The script includes explicit dedup logic: if the current repo has
its own `.claude/hooks/validate-skill-folder-structure.sh` (the
"D" pattern from the design discussion), this plugin hook SKIPS
and lets D handle it. This means:

- **In monkey-skills repo** (which ships D as part of its own
  `.claude/hooks/`): D is authoritative, plugin hook (B) defers
- **In any other repo where dev-workflow is installed**: B is the
  only hook, fires normally

Result: zero double-firing in the most common case (you developing
skills inside monkey-skills repo with dev-workflow loaded), AND
extended coverage to the previously-unprotected case (you or others
developing skills outside monkey-skills with dev-workflow installed).

**Test cases verified locally** (all 4 pass):
1. D exists in repo → plugin hook exits 0 (skip, defer to D)
2. No D, valid skill file → exit 0 (no nesting found)
3. No D, synthetic violation in /tmp → exit 2 + clear error message
4. Non-skill file → exit 0 (fast path, doesn't recurse)

**Why bump to 2.1.0** (minor not patch): adding plugin-shipped
hooks materially expands what users get when they install
dev-workflow — they now get runtime enforcement, not just
documentation. New optional capability = minor bump per SemVer.

## [2.0.0] — 2026-04-29

### BREAKING

**`skill-tasting` is renamed to `skill-tuning`.**

- Slash command: `/skill-tasting` → `/skill-tuning`
- Skill directory: `skills/skill-tasting/` → `skills/skill-tuning/`
- All cross-skill forward references updated (skill-creator-advance
  not-trigger; skill-refactor handoff in SKILL.md / READMEs;
  skill-refactor's bundled functional copy headers in 3 shared
  conventions; plugin.json description and keywords; plugin
  READMEs × 3; architecture doc; governance doc; audit runbook;
  telemetry-setup doc; check-shared-conventions-drift.py manifest)
- Migration: anyone using `/skill-tasting` should update to
  `/skill-tuning`. The skill's behavior, frontmatter description
  semantics, gate function, verdict vocabulary (ADOPT / DROP /
  DEFER / REFINE / ESCALATE), and references / scripts are
  otherwise unchanged from v1.7.0.

### Why rename

The "tasting" metaphor (wine/food tasting → subjective judgment)
was chosen in v1.7.0 PR-3 to evoke human-judgment / preference
accumulation and to distinguish from mechanical "testing". In
practice the metaphor proved insufficiently sticky:

- **Mental-model failure** observed: even the original maintainer
  recalled the skill as "skill-testing" rather than "skill-tasting"
  — t/t similarity defeats recognition
- **Multi-language friction**: "tasting" doesn't translate
  naturally; "tuning" maps cleanly via "チューニング" / "調整"
- **Cultural specificity**: wine/food tasting metaphor doesn't
  carry universally
- **Trajectory mismatch**: H4 horizon trains a preference judge
  from the log — that activity is industry-standardly called
  "fine-tuning" / "RLHF tuning". The new name echoes the
  long-term target.
- **Adjacency to anti-trigger**: skill-creator-advance has an
  explicit "Do NOT use /skill-test" anti-trigger; t/t collision
  created ambient confusion

Per the dev-workflow Goodhart audit pattern: when stick failure
is observed, name early and fix early. Cost of renaming at v1 /
single active user is far cheaper than future cross-reference
accumulation.

### Changed (skill-tuning vocabulary)

- Activity-noun replacements throughout skill-tuning's body:
  "tasting reveals" → "tuning reveals"; "tasting session" →
  "tuning session"; "tasting is overkill" → "tuning is overkill";
  "Skill Tasting" → "Skill Tuning"
- **Preserved deliberately**: "taste-sensitive", "Taste is the
  ceiling", "taste does not override", "taste dimension" — these
  use "taste" (the property / abstract concept), not "tasting"
  (the activity). The activity got renamed; the property
  descriptor stays. Skills produce taste-sensitive output; the
  workflow that improves it is now called tuning.
- Trigger keywords expanded with tuning-vocabulary:
  - English: "tune skill", "skill tuning",
    "fine-tune skill output", "preference tuning", "RLHF skill"
  - Chinese: "調整 skill 輸出"
  - Japanese: "スキル チューニング"
  - Multilingual postfix updated: "スキル チューニング" /
    "技能調整"
- Existing triggers preserved: "improve skill output",
  "A/B variants", "output quality", "taste-sensitive skill",
  "改善 skill 輸出", "試不同 phrasing", "出力品質"

### Changed (architecture doc Implementation Status)

`dev-workflow/docs/skill-evolution-architecture.md`:
- Implementation Status table extended with v2.0.0 row
- Note added explaining the rename rationale and that semantics
  / gate function are unchanged from v1.7.0

### Changed (plugin metadata)

- `plugin.json`: 1.9.0 → 2.0.0; description and multilingual
  postfix updated to reference skill-tuning; keywords already
  reflect the rename (set in this commit's bulk replace)
- Plugin READMEs (en/ja/zh-TW): skills table row updated;
  Skill-evolution architecture diagram updated; Repository
  Structure tree updated

### Bump rationale

**Major (1.9.0 → 2.0.0)**: per `skill-governance.md` versioning
policy, "removal of slash command" / "removal of public protocol"
is a major bump. The slash command rename is functionally a removal
of `/skill-tasting` (it no longer triggers anything) plus addition
of `/skill-tuning`. Even though the skill's underlying behavior
is unchanged, the user-facing interface broke.

This is the **first major bump** in dev-workflow's history.
Future breaking changes should follow the same naming-failure-
caught-early pattern: identify, surface, decide quickly, version-
bump rather than letting drift accumulate.

## [1.9.0] — 2026-04-29

### Context

**Final PR of the 5-PR skill-evolution series.** With this release,
H1–H4 horizons from `dev-workflow/docs/skill-evolution-architecture.md`
are all addressed at the scaffolding level. Specifically Layer 0
(foundation telemetry), Layer 5 (closed-loop self-training), and
test-prompts.json bootstrap for the 7 dev-workflow skills.

After this release the skill-evolution rollout is complete at
scaffold level; future work is data-driven (telemetry accumulation
→ audit decisions; preference log accumulation → trained-judge
activation). No further PRs in this series planned.

### Added (Layer 0 — Telemetry foundation)

`scripts/skill-telemetry.py`:
- log / summarize / export operations
- Append skill invocation events to opt-in per-user JSONL log
  (default `~/.claude/skill-telemetry.jsonl`)
- Privacy-conscious by default: prompt content hashed (sha256),
  not stored; prompt_summary opt-in
- Sanitized export with `--strip-*` flags
- Standard library only; standalone executable

`dev-workflow/docs/telemetry-setup.md` (~165 lines):
- Why telemetry (Layer 0 rationale; quarterly audit consumer)
- Privacy stance (local-only, hashed prompts, sanitized export)
- Setup options (manual logging vs hook-driven via Claude Code
  settings.json)
- Running summaries + sanitized export workflows
- Telemetry → quarterly audit integration queries
- What this scaffold does NOT do (no auto-aggregation, no
  cross-skill correlation, no hook event translation — deliberate
  gaps; user chooses what to build on top)
- Troubleshooting + schema versioning

### Changed (Layer 5 — Self-training stub enhancement)

`dev-workflow/skills/skill-tasting/scripts/judge_train_stub.py`:
- Insufficient-data path now prints 6-step activation methodology
  inline (load pairs → 80/20 split → Bradley-Terry training →
  ≥80% held-out gate → vs LLM-judge baseline → deploy as Tier-1
  pre-filter)
- Threshold-met path message now self-documents: reaching this
  path IS the activation signal; open a PR to replace the stub
- Removed version-specific language so the stub ages cleanly
- Reference doc (skill-tasting/references/self-trained-judge-pipeline.md)
  remains the canonical training methodology source; this stub
  output is a tighter pointer

### Added (test-prompts.json bootstrap)

`test-prompts.json` added to all 7 dev-workflow skills:
- skill-creator-advance: build new / redesign existing / vague
  improve (router test)
- skill-judge: 200-line skill scoring / self-referential meta /
  vague request
- git-memory: commit composition with trailers / PR body with
  Memory section / retrieval query
- proposal-critique: 7-item backlog / prose with supporting
  claims / user resistance to triage
- complexity-critique: feature add LOC eval / PAGNI greenfield
  test / vague "make simpler"
- skill-refactor: shrink-skill-creator-advance canonical case /
  taste-sensitive target self-abort / vague target
- skill-tasting: status-report tone / constitution rejection /
  vague output improvement

Each file follows references/test-prompts-schema.md format with
3 prompts (happy / edge / stress categories). These serve dual
purposes:
1. Manual validation by user (closing some validation gates)
2. Future cross-skill regression CI consumer
3. Future self-trained-judge training data

### Changed (architecture doc)

`dev-workflow/docs/skill-evolution-architecture.md`:
- Added "Implementation Status (as of v1.9.0)" section at top
  showing PR-1 through PR-5 status (all merged)
- Horizon coverage table: H1 / H2 / H3 / H4 all marked Complete
  (H4 explicitly noted as scaffolded; training activates at
  ≥1000 preference pairs per skill)
- Outstanding validation gates table: skill-refactor +
  skill-tasting gates noted as audit-tracked, not blocking
- Title bumped from "Planning Doc" to "Planning + Status Doc"
- Status banner: LIVING DOCUMENT
- "Original Planning Doc Begins Below" delimiter so the original
  planning content is preserved verbatim below the new status
  section

### Changed

- `dev-workflow/.claude-plugin/plugin.json`: 1.8.0 → 1.9.0

### Bump rationale

Minor (1.8.0 → 1.9.0): foundation / scaffold additions; no
breaking changes. The telemetry script is opt-in; the trained-
judge stub still fails fast (no behavior change for users who
weren't using it); test-prompts.json files are new artifacts
that don't change skill behavior.

### Final state of the skill-evolution architecture

After this release, dev-workflow ships:

```
proposal-critique  → complexity-critique → skill-creator-advance
(list / plan         (single change gate)   (creation + redesign)
 triage)

skill-judge          skill-refactor        skill-tasting
(advisory score      (Phase A: tokens /    (Phase B: output A/B,
 + drift detection)   structure, output     human judge,
                      preserved; multi-     preference log,
                      judge ensemble +      constitutional
                      git ratchet)          pre-filter)
```

Plus governance infrastructure:
- Cross-skill regression CI (shared-conventions-drift)
- Skill governance doc (SSOT registry, lifecycle states)
- Quarterly audit runbook (7-step checklist)
- Telemetry scaffold (Layer 0)
- Self-trained judge scaffold (Layer 5; activates at threshold)
- test-prompts.json × 7 bootstrap

The 4-skill family (creator / judge / refactor / tasting) +
3 critique skills (proposal / complexity / git-memory) compose to
cover skill creation, evaluation, behavior-preserving refactor,
taste-sensitive A/B, and lifecycle governance — all with explicit
SSOT discipline and same-PR drift rules enforced by CI.

## [1.8.0] — 2026-04-29

### Context

Fourth-of-five PR series (PR-4 of 5) implementing the
skill-evolution architecture. With the Two-Hats split complete in
v1.7.0, this release adds the **governance layer**: cross-skill
regression CI, optional skill-judge drift detection, SSOT registry
documentation, and quarterly audit runbook. The architecture doc
called this "Layer 4 — Governance"; PR-5 will add Layer 0
(telemetry) + Layer 5 (closed-loop self-training judge stub).

### Added (governance & CI)

**Cross-skill regression CI** — `scripts/check-shared-conventions-drift.py`
- Iterates a manifest of (canonical, functional-copies) pairs and
  diffs body content (header blockquote stripped before diff)
- Currently checks 3 conventions (golden-anchor-protocol /
  test-prompts-schema / constitution-schema) between skill-refactor
  (canonical SoT) and skill-tasting (functional copies)
- Verified locally: all 3 in sync at v1.7.0 baseline
- New CI job `shared-conventions-drift` in
  `.github/workflows/skill-structure.yml`; runs on every PR + push
  to main
- Enforces the same-PR drift rule documented in skill-refactor and
  skill-tasting NOTICE files
- Future extension: per-plugin convention manifests; test-prompts
  regression detection when skills have them

**skill-judge score history + drift detection** —
`dev-workflow/skills/skill-judge/scripts/score_history.py`
- New optional companion script (skill-judge remains stateless by
  default; opt-in per skill)
- Operations: append / query / drift
- Drift signal: z-score of most recent vs historical baseline;
  flags if z < -1.0σ (configurable); insufficient-history (<3)
  exits with clear message
- Constant-baseline edge case: absolute drop > 1 point flags
- Drift recommendation: run skill-tasting on flagged skill to
  capture human preference signal
- New "Optional: Score History Tracking (Drift Detection)" section
  in skill-judge SKILL.md (~32 lines added; explains advisory-only
  nature, drift signal mechanics, quick invocation)

**Skill governance documentation** —
`dev-workflow/docs/skill-governance.md`
- SSOT Registry: every shared resource's canonical location,
  functional copies, and CI enforcement mechanism (dev-workflow
  internal + cross-plugin entries)
- Ownership table per skill with attribution chain notes
- Skill Lifecycle States (Active / Deprecated / Retired) with
  transition criteria and current state of all 7 dev-workflow
  skills
- Convention evolution protocol (add / edit / delete)
- Cross-plugin contract reaffirmation
- Versioning policy with examples from dev-workflow history
- Decision authority table
- Anti-patterns

**Quarterly audit runbook** —
`dev-workflow/docs/quarterly-audit-runbook.md`
- 7-step audit checklist:
  1. SSOT registry verification
  2. Skill lifecycle state review
  3. Convention drift inspection
  4. External dependency audit (upstream MIT chains)
  5. Validation gate status
  6. Skill-judge score history drift detection
  7. Documentation freshness
- Audit report template
- Decision matrix for handling each finding type
- Self-extending guidance

### Changed

- `dev-workflow/.claude-plugin/plugin.json`: 1.7.0 → 1.8.0 (minor
  bump for governance additions; no skill behavior changes)

### Validation status carry-over

Outstanding from earlier PRs (now formally documented as audit-
trackable in the runbook):
- skill-refactor: dry-run on ≥2 existing skills, ≥90% equivalence-
  check agreement
- skill-tasting: 1 real-skill walkthrough validating A/B flow
  produces meaningful preference signal

These will be tracked as "Outstanding validation gates" in the
quarterly audit until completion.

### Bump rationale

Minor (1.7.0 → 1.8.0): governance additions (CI, scripts, docs);
no breaking change to skill behavior. The skill-judge SKILL.md
addition is opt-in (script is purely supplemental).

## [1.7.0] — 2026-04-29

### Context

Third-of-five PR series implementing the skill-evolution
architecture (`dev-workflow/docs/skill-evolution-architecture.md`).
PR-1 (v1.5.0) prepared scope; PR-2 (v1.6.0) shipped `skill-refactor`
(Phase A); this PR-3 / v1.7.0 ships `skill-tasting` (Phase B) — the
feature-hat counterpart to refactor's refactor-hat. The Two-Hats
split is now complete.

PR-4 / PR-5 will add governance (cross-skill regression CI,
skill-judge drift detection, audit runbook) and telemetry +
self-training pipeline scaffolding.

### Why skill-tasting exists

Skill outputs have *taste-sensitive dimensions* (style, voice,
tone, rhythm, persuasive force) that LLM-as-judge cannot reliably
evaluate. A skill that "works" can still produce outputs that are
flat, off-tone, or just not what the user wanted.

`skill-tasting` is the **feature hat** counterpart to
skill-refactor's refactor hat: refactor preserves behavior (using
LLM-as-judge to verify equivalence — a binary check LLMs handle
well); tasting deliberately changes behavior to find better outputs
(using human judgment because taste is exactly where LLM-as-judge
fails).

### Added (skill-tasting)

New `dev-workflow/skills/skill-tasting/`:

- **`SKILL.md`** — Iron Law (3-part: constitution honored + human
  preference captured + log updated), Before-You-Begin baseline +
  constitution + goldens prerequisites, 4-phase Gate Function
  (variant generation + constitutional pre-filter + blind A/B
  harness + verdict + log), verdict vocabulary (ADOPT / DROP /
  DEFER / REFINE / ESCALATE) parallel to other dev-workflow
  critique skills, Constitutional Judging mechanic, Preference
  Log → Self-Trained Judge horizon scaffold (H4), Red Flags,
  Rationalization Prevention, 2 worked examples (status-report
  tone improvement + variant rejected by constitution)
- **`commands/skill-tasting.md`** — slash command redirect
- Tasting-specific references (4 files):
  - `references/ab-harness-protocol.md` — variant generation
    rules, random label assignment, side-by-side display, 4-option
    capture, multi-evaluator extension, truncation, atomicity
  - `references/constitutional-judging.md` — how MUST clauses test
    variants in pre-filter; binary satisfied/violated; ambiguity
    handling; reporting filtered variants; constitution evolution
    from tasting; constitutional ratchet
  - `references/preference-log-schema.md` — JSONL format
    (append-only), per-pick entry schema, per-session summary,
    privacy considerations, retention, lifecycle events, querying
  - `references/self-trained-judge-pipeline.md` — H4 horizon
    scaffold; activation thresholds (≥1000 entries); training
    methodology (Bradley-Terry-style); deployment as Tier 1
    pre-filter; cross-skill transfer (research territory)
- Bundled functional copies of 3 shared conventions:
  - `references/golden-anchor-protocol.md`
  - `references/test-prompts-schema.md`
  - `references/constitution-schema.md`
  All carry "bundled functional copy" header blockquote pointing
  to skill-refactor as the canonical SoT for evolution. Same-PR
  drift rule documented in NOTICE.
- Scripts (3 scaffold files):
  - `scripts/ab_harness.py` — Phase 3 blind A/B orchestration
    (variant collection, random labels, side-by-side rendering,
    truncation, atomic decision capture)
  - `scripts/preference_log.py` — JSONL operations (append /
    query / summarize / export-for-training with ≥N threshold)
  - `scripts/judge_train_stub.py` — H4 stub; documents training
    interface; fails fast with "scaffolded, not active in v1.7.0"
- **`LICENSE`** — MIT, single copyright (c) 2026 kouko, original
  design (not a port or fork)
- **`NOTICE`** — 9 enumerated design distinctions vs darwin-skill;
  inspirations (autoresearch, darwin-skill, voice-anchors
  curation, RLHF/preference-modeling literature, Fowler Two Hats,
  internal architecture doc); convention sharing arrangement with
  skill-refactor
- **`README.{en,ja,zh-TW}.md`** — three-language READMEs

### Changed (skill-creator-advance)

- Description: added negative trigger routing output A/B testing
  to `skill-tasting`. The "Improving Existing Skill" router's
  case (b) now hands off to a real skill (was forward-reference
  in PR-1).
- Removed PR-1 transitional note about skill-refactor / skill-
  tasting being "referenced but not yet shipped" — both now ship.
  Case (c) intro text simplified accordingly.

### Changed (skill-refactor)

- All `*(when available)*` parenthetical placeholders next to
  skill-tasting references stripped — skill-tasting is now a
  concrete sibling, not a forward-reference. Affects SKILL.md
  and 3 READMEs.
- 3 shared convention files (golden-anchor-protocol /
  test-prompts-schema / constitution-schema): header blockquotes
  updated to mark skill-refactor as canonical SoT location and
  skill-tasting as functional copy. Same-PR drift rule documented.

### Changed (plugin)

- `plugin.json`: 1.6.0 → 1.7.0; description appended with
  "skill-tasting (blind variants + constitutional pre-filter +
  preference log)"; multilingual postfix updated; keywords gain
  "skill-tasting"
- `README.{en,ja,zh-TW}.md`: skills table adds skill-tasting row;
  Skill-evolution architecture diagram updated (Phase B no longer
  marked planned — it shipped); Repository Structure tree adds
  skill-tasting/ folder

### Cross-skill independence statement

`skill-tasting` is **runtime self-contained**. No cross-plugin
dependency. The 3 shared convention files are bundled functional
copies; runtime works with `dev-workflow` alone (no `domain-teams`,
no `skill-refactor` even — though they compose well together).

The SSOT-and-functional-copy pattern continues from PR #159
(code-team mindsets) and PR-2 (skill-refactor canonical conventions).

### Validation status

⚠️ Validation gate per architecture doc §6: "manually run
skill-tasting through 1 real-skill walkthrough; verify the A/B
flow produces meaningful preference signal."

**OUTSTANDING** — this PR ships before formal validation. PR
description notes the caveat. Recommended first validation
target: a copywriting / status-report style skill where taste-
sensitive output is the natural test case.

### Bump rationale

Minor (1.6.0 → 1.7.0): new skill addition; no breaking change.
skill-creator-advance description gains another not-trigger
(refinement, not behavior change). skill-refactor's
forward-reference cleanup is also a refinement.

## [1.6.0] — 2026-04-29

### Context

Second-of-five PR series implementing the skill-evolution
architecture (see `dev-workflow/docs/skill-evolution-architecture.md`).
PR-1 (v1.5.0 + skill-creator-advance scope tightening) prepared the
ground; this PR-2 / v1.6.0 lands `skill-refactor` — Phase A of the
Two-Hats split — with all H1-H3 features in one shot.

PR-3 will add `skill-tasting` (Phase B); PR-4 / PR-5 add governance,
cross-skill CI, telemetry, and self-training judge scaffolding.

### Why skill-refactor exists

Skills accumulate tokens. SKILL.md files grow over edits. Most
edits are additive — fixing corner cases, adding examples — and
result in larger skills with the same (or worse) output behavior.
Without an explicit gate, every edit defaults additive.

`skill-refactor` is the **refactor hat** applied to skills:
improve structure / shrink tokens **without changing what the skill
does**. Output equivalence is enforced by a multi-judge ensemble +
structured comparison; any behavior-changing edit is out-of-scope
and routes to `skill-creator-advance` (structural redesign) or
`skill-tasting` (output quality, taste-sensitive).

### Added (skill-refactor)

New `dev-workflow/skills/skill-refactor/`:

- **`SKILL.md`** — Iron Law (3-part discipline: equivalence + ≥10%
  token reduction + invariant preservation), Before-You-Begin
  baseline capture, Gate Function (Q1 multi-judge ensemble +
  structured comparison; Q2 token threshold; Q3 invariant snapshot
  diff), verdict vocabulary (PROCEED / RESHAPE / REJECT) parallel
  to `complexity-critique`, refactor moves catalog with risk
  classification, Tier 1/2/3 cascade for ensemble disagreement,
  Red Flags, Rationalization Prevention, 2 worked examples (token
  bloat success + subtle behavior-change rejection)
- **`commands/skill-refactor.md`** — slash command redirect
- **`references/equivalence-check-protocol.md`** — Q1 two-layer
  check details (Layer 1 structural / Layer 2 LLM-judge ensemble);
  consensus matrix; specific-behavior-diff override rule
- **`references/multi-judge-ensemble.md`** — 3-judge spawn protocol
  with varied prompt framing (utility / content / boundary);
  random output labeling for position-bias mitigation
- **`references/refactor-moves-catalog.md`** — Fowler-inspired
  catalog of refactor-hat-safe moves (Low/Medium/High risk);
  out-of-scope moves table routes to other skills
- **`references/golden-anchor-protocol.md`** — *shared convention*
  (also in skill-tasting when shipped); same-PR drift rule
- **`references/test-prompts-schema.md`** — *shared convention*
- **`references/constitution-schema.md`** — *shared convention*
- **`scripts/equivalence_check.py`** — Layer 1 structural
  comparison (5 deterministic checks); standalone Python, stdlib
  only
- **`scripts/multi_judge.py`** — Layer 2 ensemble aggregation +
  consensus rule application; specific-behavior-diff override via
  regex pattern matcher
- **`scripts/golden_compare.py`** — Tier 2 anchor similarity
  comparison (Jaccard + length ratio)
- **`LICENSE`** — MIT, single copyright (c) 2026 kouko, original
  design (not a port or fork)
- **`NOTICE`** — explicit design distinctions vs darwin-skill
  (8 enumerated differences); inspirations acknowledged
  (autoresearch, darwin-skill, Fowler Refactoring); no copyright
  dependencies
- **`README.{en,ja,zh-TW}.md`** — three-language READMEs

### Changed (skill-creator-advance)

- Description: added negative trigger routing token / structure
  refactor work to `skill-refactor`. Held back from PR-1 to avoid
  dangling reference; activated in this PR now that skill-refactor
  exists.

### Changed (plugin)

- `plugin.json`: 1.5.0 → 1.6.0; description appended with
  "skill-refactor (multi-judge ensemble + git ratchet)"; multilingual
  postfix updated (skill リファクタ / skill 重構); keywords gain
  "skill-refactor"
- `README.{en,ja,zh-TW}.md`: skills table adds skill-refactor row;
  "the critique line" diagram extended to show
  skill-refactor / skill-tasting positioning; Repository Structure
  tree adds the new skill folder

### Cross-plugin / inter-skill independence

`skill-refactor` is **runtime self-contained**. No cross-plugin
dependency. The 3 shared convention files (golden-anchor /
test-prompts / constitution) are bundled in the skill's own
`references/` directory. When `skill-tasting` ships in PR-3, the
same 3 convention files will be **functional copies** in that
skill's `references/`, governed by a same-PR drift rule. This
mirrors the SSOT-and-functional-copy pattern established for
code-team mindsets in PR #159.

### Validation status

⚠️ Validation gate per `dev-workflow/docs/skill-evolution-architecture.md`
§6: dry-run on ≥2 existing skills with ≥90% equivalence-check
agreement. **OUTSTANDING** — this PR ships the skill before formal
validation. PR description notes the caveat. Recommended first
validation target: skill-creator-advance itself (already over the
soft cap and a natural test bed).

### Bump rationale

Minor (1.5.0 → 1.6.0): new skill addition; no breaking change to
existing skills' behavior. skill-creator-advance description gains
a not-trigger, which is a refinement, not a behavior change.

## [1.5.0] — 2026-04-29

### Context

dev-workflow's "critique" line previously had one skill —
`proposal-critique` — that operates on multi-item proposals (lists,
plans, prose) **before any code is written**. A second failure mode
sits one stage downstream: a *single proposed change* to *existing
code* (refactor, feature add, debt cleanup) defaults to *additive*
unless something forces the design conversation to ask "what's the
smallest end state and what becomes obsolete".

Anthropic's `simplify` skill catches additive code *after* it is
written; `superpowers:brainstorming` catches greenfield design *with
no existing code as baseline*. The gap was the design-time gate for
*existing-code change decisions*.

`complexity-critique` (this release) closes that gap and forms a
sibling to `proposal-critique` with parallel gate-skill shape but
distinct scope:

```
proposal-critique  →  complexity-critique  →  Anthropic simplify
(list / plan       (single change to       (post-implementation
 / prose,           existing code,           diff review)
 before any code)   before implementing
                    the change)
```

### Added (complexity-critique)

New `dev-workflow/skills/complexity-critique/` — single-file gate
skill (~270 lines SKILL.md + 3-language READMEs) for evaluating any
change to an existing codebase through a deletion-first lens. Three
mechanical questions:

1. **Q1 — smallest end state.** Not the smallest *change* — the
   smallest *result*. Could the feature be deleted entirely? Could
   2 functions replace 14?
2. **Q2 — before/after LOC count.** If after > before, reject the
   change as proposed. The metric is end-state volume, not effort.
3. **Q3 — what becomes obsolete.** Every change makes something
   else available to delete.

Verdict vocabulary parallel to proposal-critique:
- **PROCEED** — change reduces total code; ship.
- **PROCEED-WITH-CAVEAT** — net-neutral or marginal; ship but name
  the trade-off bought ("30 lines bought, exhaustiveness check
  enforced"). Hidden growth is the failure mode this skill exists
  to prevent.
- **RESHAPE** — change adds; Q1 produced a smaller end state; propose
  the alternative.
- **REJECT** — change adds with no end-state justification; redirect
  to deletion.

The body adapts the same idiom as proposal-critique: Iron Law / Gate
Function / Verdict / Red Flags / Rationalization Prevention /
Reference Mindsets / Composes With / Worked Examples (×2: form
validation feature add + type-safety refactor) / When To Apply
(with explicit Not-triggers) / Bottom Line.

Three-language READMEs (en / ja / zh-TW) follow the dev-workflow
pattern with mermaid flow + verdict table + worked example +
relate-to-others + lineage + known limitations.

### Cross-plugin reference

The skill references 4 philosophical mindsets that live in
`domain-teams:code-team/standards/` (released in domain-teams v5.5.0):

- `mindset-data-over-abstractions.md` — Perlis Epigram #9 / Hickey
- `mindset-design-is-taking-apart.md` — Hickey / Out of the Tar Pit
- `mindset-expensive-to-add-later.md` — Willison PAGNI
- `mindset-simplicity-vs-easy.md` — Hickey

Per CLAUDE.md §Cross-Plugin Delegation Contract: paths only, no
content duplication. Mindsets are advisory deepening, not gates;
the three-question gate is self-sufficient when domain-teams is not
installed.

### Upstream chain (MIT)

```
joshuadavidthomas/agent-skills (MIT, original)
  → softaworks/agent-toolkit/skills/reducing-entropy (MIT, fork)
    → kouko monkey-skills/dev-workflow/complexity-critique (this)
```

Renamed from `reducing-entropy` for clearer trigger semantics
("entropy" is jargon; "complexity-critique" parallels the existing
`proposal-critique` skill). The 4 mindsets that lived inside the
upstream skill's `references/` directory are extracted to
`domain-teams:code-team` as separate standards with primary-source
citations rewritten against the underlying books / talks / papers
(Perlis 1982, Hickey 2011/2012, Moseley & Marks 2006, Ousterhout
2018, Brooks 1986, Willison/Plant/Kaplan-Moss 2021). Full chain
detail in `skills/complexity-critique/NOTICE`.

### Modifications vs upstream

- Renamed `reducing-entropy` → `complexity-critique` (rationale above)
- Mindset library extracted to `domain-teams:code-team/standards/`
  with primary-source citation rewrite
- Cross-plugin delegation: skill references mindsets via paths, not
  content duplication
- Added explicit verdict vocabulary (PROCEED / PROCEED-WITH-CAVEAT /
  RESHAPE / REJECT) parallel to proposal-critique
- Restructured frontmatter (negative triggers, multilingual keywords)
  to match dev-workflow conventions
- Scope clarified to *changes to existing codebase*; greenfield
  design and post-implementation review explicitly out of scope and
  delegated to `superpowers:brainstorming` and Anthropic `simplify`
  respectively
- Removed the upstream "load at least one mindset before proceeding"
  hard precondition; mindsets are now advisory deepening
- Added 2 worked examples (form validation feature add demonstrating
  RESHAPE; type-safety refactor demonstrating PROCEED-WITH-CAVEAT)
- Added 3-language READMEs following dev-workflow i18n pattern
- Removed upstream `references/` directory and
  `adding-reference-mindsets.md` meta-skill (replaced by skill-team
  conventions for adding new standards in domain-teams)

### Changed (plugin)

- `plugin.json` — version 1.4.0 → 1.5.0; description and keywords
  updated to include `complexity-critique`
- `README.md` / `README.ja.md` / `README.zh-TW.md` — Skills table
  adds `complexity-critique` row; Repository Structure tree adds
  the new skill directory; version line bumped (also catches up
  the missed bump from PR #158 / v1.4.0 skill-judge release —
  README version field was stuck at 1.0.4)

### Note on missed [1.4.0] CHANGELOG entry

The PR #158 / v1.4.0 release (skill-judge integration, 2026-04-29
earlier today) updated `plugin.json` to 1.4.0 but did not add a
[1.4.0] entry to this CHANGELOG. The [1.4.0] gap between [1.3.0]
and [1.5.0] is intentional in this release; a retroactive [1.4.0]
entry can be added in a separate housekeeping commit if desired.
The skill itself is fully documented in
`skills/skill-judge/README.md` and `skills/skill-judge/NOTICE`.

## [1.3.0] — 2026-04-25

### Context

This session repeatedly demonstrated a recurring failure mode: when
Claude proposes a multi-item plan / backlog / recommendation list,
the default behavior is to over-engineer (7-item P0–P3 lists,
speculative content, YAGNI violations). Without explicit user
pushback ("業界證實了嗎", "可以簡化嗎", "複雜度評估"), bloated
proposals ship as-is. The pattern recurred 4 times in this session
within a single artifact (description-design.md): a 7-item backlog
got triaged to 1 KEEP / 1 DEFER / 5 DROP; a 4-section anti-pattern
duplication got deleted; a "research → apply → reflect → simplify"
4-step pipeline proposal got narrowed to a single post-proposal
checkpoint. The recurring fix had a clear shape — three buckets and
two checks — that's now a skill anyone can invoke.

### Added (proposal-critique)

New `dev-workflow/skills/proposal-critique/` — single-file gate
skill (~215 lines) for triaging proposals into KEEP / DEFER / DROP
via evidence grounding (cited / heuristic / speculative) and YAGNI
(essential / speculative). User-invoked primary mechanism; auto-
trigger on Claude's own list-shape output explicitly **deferred to
Phase 2** until v0.1 dogfood proves user-driven triggering reliable.

The body adapts the `superpowers:verification-before-completion`
idiom: Iron Law / Gate Function / Triage Matrix / Common Failures /
Red Flags / Rationalization Prevention / Composes With / Worked
Examples (×2: list shape + prose shape with DECOMPOSE step) / When
To Apply / Bottom Line.

The skill is **shape-agnostic** — handles list-shaped proposals
(numbered backlog, P0/P1/P2) and prose-shaped proposals
(architecture decisions, strategy memos, single recommendations
with supporting claims) via an `ENUMERATE-OR-DECOMPOSE` first step.

### Changed

`dev-workflow/.claude-plugin/plugin.json` version 1.2.0 → 1.3.0
(minor, additive). `description` extended to name 3 skills.
`dev-workflow/README.md` Skills table extended; directory tree
updated. Repo-root `.claude-plugin/marketplace.json` description
extended (multilingual belt now includes 提案審查).

## [1.2.0] — 2026-04-25

### Context

Distills lessons from the `git-memory` skill's v0.1.5 description rewrite
(monkey-skills PR #142) into reusable guidance for `skill-creator-advance`.
The git-memory rewrite cut its `description` from 650 chars (read-path
triggers only, mechanism prose front-loaded) to 287 chars (Anthropic-aligned
WHAT+WHEN, both write/read paths, "about-to-violate" symptoms). The full
research — covering Anthropic Skills docs, Anthropic best-practices,
Agent Skills spec, and an empirical study of all 14 official superpowers
SKILL.md descriptions — is now reusable for any future skill author via
`skill-creator-advance`.

### Added (skill-creator-advance)

New `references/description-design.md` (~250 lines). Covers:

- How skill discovery actually works (LLM semantic match in the forward
  pass, not regex / fuzzy / vector embedding) and the three implications
- The Anthropic-vs-Superpowers tension resolved: WHAT (outcome) is
  Anthropic-approved; WORKFLOW (process steps) is what Superpowers
  warns against — different phenomena conflated by the rule statement
- Six design principles (WHAT+WHEN front-loading, third-person,
  about-to-violate symptoms, natural keywords, length budget,
  multilingual belt as optional insurance)
- "About-to-violate" symptom catalog drawn from 14 superpowers skills
  (`before writing implementation code`, `before merging`, etc.)
- Length empirics: superpowers median 107 chars, range 79–234, all
  well under 1024-char Agent Skills cap and 1536-char Claude Code
  truncation point
- YAML `>-` block-folded rendered length gotcha
- Validation checklist + anti-patterns table
- Worked example: git-memory v0.1.0 → v0.1.5 before/after rewrite

§Description Best Practices in SKILL.md reorganized into 7 numbered
patterns with a pointer to the new reference for the deep dive.
Existing guidance ("pushy", "negative triggers", "multilingual",
"before/after example") preserved verbatim.

### Changed

`dev-workflow/.claude-plugin/plugin.json` version 1.1.0 → 1.2.0
(minor: additive reference content + reorganized SKILL.md section,
backwards-compatible).

## [1.1.0] — 2026-04-24

### Context

monkey-skills PR #137 added the `git-memory` skill (portable
git-backed project memory via commit trailers + PR `## Memory`
section) to the `dev-workflow` plugin alongside the existing
`skill-creator-advance`. plugin.json version was bumped at PR #140
but the CHANGELOG entry was missed at the time; this entry is
retroactive to mark the additive skill addition.

### Added

`dev-workflow/skills/git-memory/` — portable, tool-agnostic project
memory using git commit messages and PR bodies as the substrate.
Phase 1 MVP includes:

- `SKILL.md` with the three pillars (carrier / structure / content)
- `standards/memory-conventions.md` — trailer schema (`Decision:` /
  `Learning:` / `Gotcha:` / `Related:`), PR body `## Memory`
  section layout, ASCII-vs-Mermaid diagram venue rules
- `protocols/compose-commit.md` + `protocols/compose-pr.md` — Claude
  authoring guidance for the write paths
- `scripts/memory-grep.sh` — retrieval primitive emitting plain or
  JSON output, parses trailers via `git interpret-trailers --parse`
  (added v0.1.2) and validates `--limit` as positive integer (v0.1.3)

dev-workflow plugin description updated to name both skills.

## [1.0.4] — 2026-04-15

### Context

Paired with `domain-teams` v4.21.1 (same PR). Domain-teams made Empty
Invocation Fallback a hard-required SKILL.md section with surface-
orientation synthesis and 5-source sufficient-context check. This
release adds a companion **guidance** (not hard requirement) to
`skill-creator-advance` so authors of generic Claude skills can apply
the same pattern when building conversational or multi-workflow skills.

### Added (skill-creator-advance)

New §Empty-Prompt Onboarding subsection under §Skill Writing Guide
(between "Principle of Lack of Surprise" and "Writing Patterns").

The subsection covers:
- When to include the pattern (recommended for conversational /
  multi-workflow skills; unnecessary for single-shot utility skills)
- 3-element pattern: Surface orientation / Route to intake /
  Sufficient-context skip
- Sufficient-context check must cover 5 sources: current prompt,
  prior conversation, IDE context, plan/memory, upstream handoff
- Common pitfall: triggering orientation on empty-current-prompt
  alone creates friction for returning users
- Cross-reference to `domain-teams/skills/skill-team/standards/skill-md-structure.md`
  §Empty Invocation Fallback Rules as the rigorous domain-team
  version (with §Surface Orientation Format skeleton and CHK-SKL-013
  gate)

+23 lines. No breaking change.

## [1.0.3] — 2026-04-15

### Context

PR #73 was merged at commit bd344a4 (Mermaid guidelines only); the
line→token budget migration commit (d0b1b2c) was not included. This
PATCH restores the dev-workflow portion of that migration.

### Fixed (skill-creator-advance — line→token budget consistency)

Completing the line→token budget migration per `plugin-conventions.md`
§Lightweight SKILL.md canonical guidance ("Use word/token count rather
than line count — lines vary too much in density"):

- `SKILL.md` Key patterns: reference TOC threshold
  ">300 lines" → ">~8,000 tokens"
- `SKILL.md` Working-with-existing-plugin enum:
  "line budgets" → "token budgets"
- `references/plugin-conventions.md` §Lightweight Structure:
  "under 300 lines" → "under ~3,000 tokens"

### Kept as-is (correct current usage)

- `NOTICE:46` — historical migration record
- `references/mermaid-usage-guidelines.md` mentions of "token or line
  count" — accurate discussion of both metrics
- `references/plugin-conventions.md:85` "Use word/token count rather
  than line count" — canonical guidance

## [1.0.2] — 2026-04-15

### Added (skill-creator-advance)
- **New reference**: `references/mermaid-usage-guidelines.md`.
  Generic skill-authoring guidance for when to use Mermaid diagrams
  vs prose. Covers decision criterion (≥3 branch conditions OR ≥4
  state transitions), strong-candidate categories (decision trees,
  state machines with retry loops, routing with failure branches),
  avoid-categories (bibliographies, rationale, corpora, philosophy,
  clean tables, linear sequences), cost-benefit framework, Mermaid
  type selection, syntax conventions, and anti-patterns.
- SKILL.md references/ listing updated to include the new reference.

### Rationale

Complements `domain-teams/skill-team v4.19.0` which shipped the
domain-team-specific version. This version is generic (no gate-system
assumptions) and serves any Claude skill author, not just domain-team
skills.

Empirical finding from the precedent: Mermaid adds clarity to
branching logic but does NOT reduce token/line count when paired
with explanatory prose. The value is eliminating prose ambiguity,
not compression.

## [1.0.1] — 2026-04-14

License compliance: add missing `LICENSE` and `NOTICE` files to the
`skill-creator-advance` skill and correct the upstream attribution
previously misstated in the v1.0.0 CHANGELOG.

### Corrected upstream attribution

v1.0.0 stated "based on Anthropic's skill-creator with 7 enhancements"
and that bundled agents/scripts came "from Anthropic skill-creator."
The accurate upstream chain is:

1. **Anthropic `skill-creator`** (MIT) — the earliest upstream; provides
   the eval-loop concept and file naming for bundled agents (grader,
   comparator, analyzer) and scripts (aggregate_benchmark, run_eval,
   run_loop, improve_description, package_skill, quick_validate,
   generate_report, utils).
   https://github.com/anthropics/skills/tree/main/skills/skill-creator
2. **AllanYiin (尹相志) `skill-creator-advanced`** (MIT, Copyright (c)
   2026 AllanYiin) — **the direct upstream** this plugin adapted from.
   https://github.com/AllanYiin/Amon
   Path: `src/amon/resources/skills/skill-creator-advanced/`
3. **`dev-workflow/skills/skill-creator-advance/`** (MIT, Copyright (c)
   2026 kouko) — this distribution.

The v1.0.0 CHANGELOG incorrectly implied direct derivation from
Anthropic. The direct upstream is Allan's work, which in turn draws
from Anthropic (Allan's own reference files in the upstream
acknowledge "upstream skill-creator").

### Added

- `dev-workflow/skills/skill-creator-advance/LICENSE` — MIT license
  preserving AllanYiin's copyright + adding kouko's copyright for
  modifications, per MIT requirement that upstream notices be retained
  in all copies or substantial portions.
- `dev-workflow/skills/skill-creator-advance/NOTICE` — detailed
  upstream chain, per-version modifications, and link to Allan's
  Facebook announcement of the original skill-creator-advanced.

### Also (repo-root, in the same fix PR)

- Root `LICENSE` (MIT) — corresponding to the MIT declaration in the
  main `README.md` which previously had no license file backing it.
- Root `ATTRIBUTION.md` — summary table of all third-party components
  across all plugins (obsidian kepano skills, obsidian axtonliu visual
  skills, skill-creator-advance lineage).
- `obsidian/skills/README.md` — fixed 3 axtonliu upstream URLs that
  incorrectly pointed to `github.com/anthropics/claude-code-skills`;
  corrected to `github.com/axtonliu/axton-obsidian-visual-skills`.

### Not a breaking change

No skill content modified. Pure license-compliance housekeeping.
v1.0.0 consumers continue to work unchanged; this PATCH only adds
license / attribution files and corrects documentation text.

## [1.0.0] — 2026-04-13

Initial release of the dev-workflow plugin with `skill-creator-advance`.

### Added

- **skill-creator-advance** skill — general-purpose skill creation and
  iterative improvement tool. Adapted from AllanYiin's `skill-creator-
  advanced` (MIT; upstream at github.com/AllanYiin/Amon, path
  src/amon/resources/skills/skill-creator-advanced/), which itself
  draws on Anthropic's upstream `skill-creator`. See LICENSE and NOTICE
  in the skill directory for the full upstream chain. Added the
  following 7 enhancements in this distribution:
  1. monkey-skills ecosystem integration guidance
  2. Description best practices (negative triggers, multilingual keywords)
  3. Eval flow tiering (quick path vs full path)
  4. Existing skill improvement workflow
  5. Slash command creation guidance
  6. Self-assessment pass (auto-fix obvious defects before human review)
  7. Auto-regression detection across iterations

- **Bundled agents**: grader, comparator, analyzer (inherited via
  AllanYiin's skill-creator-advanced, which in turn took the file
  naming convention from Anthropic's upstream skill-creator)

- **Bundled scripts**: aggregate_benchmark, run_eval, run_loop,
  improve_description, package_skill, quick_validate, generate_report
  (same inheritance chain as agents)

- **Reference files**:
  - `plugin-conventions.md` — plugin ecosystem conventions and slash commands
  - `iteration-automation.md` — self-assessment and regression detection protocols
  - `platform-adaptations.md` — Claude.ai and Cowork adjustments
  - `eval-methodology.md` — eval principles with primary source citations
  - `schemas.md` — JSON structures for evals, grading, benchmarks

- **Slash command**: `/skill-creator-advance`

### Design decisions

- Eval results presented **inline + markdown report** instead of browser-based
  eval-viewer (removed dependency on Python web server and browser)
- Token-based budget (~6,000 tokens) instead of line-based (500 lines)
- Platform adaptations extracted to reference file (optional, loaded on demand)
- Eval methodology grounded with primary source citations (Fisher 1935,
  Beck 2002, Hastie et al. 2009, Myers et al. 2011, ISTQB v4.0, etc.)
