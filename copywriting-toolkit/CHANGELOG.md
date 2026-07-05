# copywriting-toolkit — CHANGELOG

## v1.14.1 — 2026-07-05 (Codex dispatch-portability + declared external dependency)

`copywriting-ideation/protocols/{copy-ideation-parallel.md,copy-ideation-advanced.md}` §"Parallel dispatch"/§"Instinct-axis subagent dispatch" already named `loom-code:dispatching-parallel-agents` by delegation but never pointed to a concrete per-host call shape (Codex dispatch-portability survey finding, `docs/skill-mining/2026-07-05-codex-dispatch-portability-survey.md`). Added a one-line pointer to `loom-code/skills/using-loom-code/references/{claude-code-tools.md,codex-tools.md}` in both protocol files — kept byte-identical to the `domain-teams:copywriting-team` source files (same fix applied upstream in the same session, not a plugin-specific divergence).

Also declared `loom-code:dispatching-parallel-agents` in `using-copywriting-toolkit/SKILL.md`'s new External Plugins table (survey side-finding: this dependency was undeclared, unlike `code-team/SKILL.md`'s own External Plugins table for its `feature-dev:code-architect` dependency).

- `plugin.json`: 1.14.0 → 1.14.1

**Follow-up (same session, behavioral dogfood)**: a cold-reader flagged
`using-copywriting-toolkit/SKILL.md`'s "No other cross-plugin
delegation is wired in v1.0.0" as reading self-contradictory directly
below the new External Plugins table — reworded to qualify "task"
delegation and clarify loom-code is a runtime dependency, not a task
handoff. The two protocol files' appended pointer sentences (flagged
as "bolted on") were also reworded inline, still kept byte-identical
to the domain-teams source.

## v1.14.0 — 2026-04-23 (anchor autonomy on voice conflicts)

Addresses the `anchor-honoring reflex is addition-oriented when subtraction would be correct` pattern surfaced in v1.12.1 data-collection (Briefs 1/3/4). Root cause: when `brief.form_hint` / `brief.tone_cue` / Phase 4 draft structure conflicts with anchor's voice mechanics, LLM default is compromise — producing graft-feel copy that does Xu-style language inside 3-bullet container (or any similar structural-voice mismatch). This release clarifies the conflict-resolution hierarchy: **anchor wins on voice conflicts**.

**Change scope**:

- `skills/copywriting-voice-tone-stage/SKILL.md` §Pass 3 Step 4 — adds rule 4 (anchor autonomy on voice conflicts) — ~3-4 lines.
- `plugin.json`: 1.13.3 → 1.14.0

**What the rule says**:

```
Step 4 rule 4 (v1.14.0): when anchor's §Prose mechanics or §Don't
conflicts with brief.form_hint / brief.tone_cue / Phase 4 draft structure,
anchor wins. Mechanics are binding requirements, not suggestions.
Do NOT override brief.output_language / audience / product / goal
(intake Level-1 fields, immutable). Example: form_hint "3 feature bullets"
vs anchor refusing enumeration → bullets subtracted.
```

**What the rule does NOT change**:

- anchor file contents (zero anchor edits)
- envelope schema (zero new fields)
- intake UX (zero new questions)
- lint (zero new checks)
- gate dimensions (zero new gates)
- anchor selection (Step 2 unchanged)

Pure behavioral instruction at Pass 3 Step 4. Tiebreaker rule, not new mechanism.

**Validation path**:

- N=10 dry-runs across 10 briefs + 4 mechanism variants (baseline / thesis_core hint / yaml discipline schema / prompt autonomy) converged on: prompt-level clarification is sufficient; additional taxonomy (MAY override lists, SUBTRACTION LICENSE naming, yaml schema) is either redundant with anchor prose or inducing compliance theater.
- Final 1-sentence vs 3-4 line comparison (Briefs 1+4, 2026-04-23) showed: 1 sentence worked on both, but agents flagged variance risk; adding explicit immutable-field clause + concrete example reduces variance without scope creep.
- Dry-run research archive: `docs/tests/v1.14.0-anchor-autonomy-research.md` (to be authored post-ship).

**What's explicitly NOT in v1.14.0 (deferred to v1.14.x research)**:

- Dual license (subtraction + addition) for JP/ZH craft-gate anchors whose Don't blocks are addition-oriented (require concrete payload) rather than subtraction-oriented. N=10 showed autonomy framing works well on EN commercial anchors with subtraction-oriented Don't blocks; less well on payload-depth masters.
- Anchor §Don't block quality audit. N=10 suggests unevenness (岩崎 / Chouinard / 許舜英 / 青木耕平 prescriptive and work well; thinner Don't blocks may degrade autonomy to agent aesthetic). No library-wide audit in v1.14.0; real usage signal drives prioritization.
- Library coverage gap mitigation (zh-HK has only 3 anchors all Q2). Cross-lang borrowing policy formalization deferred.
- Origin-tell handling (when anchor itself is the cliché the brief is trying to escape — e.g., Chouinard for anti-greenwashing briefs). Second-order subtraction deferred.
- `named_master_fit_warning` extension to log autonomy overrides. Current field only fires on forced-rank conflicts; autonomy-triggered element de-emphasis not logged. Deferred.

**Meta-reflection**: this release is 4 lines of SKILL.md after a long design exploration. Iteration path (thesis_core → yaml discipline schema → 15-line autonomy framework → 1-sentence → 3-4 lines) kept shrinking scope as each larger proposal was audited for complexity. Load-bearing change is `anchor wins on voice conflicts` — everything else is elaboration or scope expansion that N=10 testing did not justify.

## v1.13.3 — 2026-04-22 (format unification — single canonical anchor structure)

Unifies three silent-alternative formats that accumulated during v1.4.0-v1.12.x anchor library expansion. All 90 anchors now conform to one canonical structure; lint enforces the single form.

**Problem**: v1.13.2 lint was tolerant of two formats for `Native critical read` (inline bold vs standalone H2) and two for Metadata (grouped vs flat). This meant two invisible sub-standards coexisted in the library — same content, different structural layout. Cosmetic inconsistency, no runtime impact, but unmanageable for future edits.

**Decision**: Pattern B (standalone H2) as canonical for `Native critical read`, despite being the 9-file minority. Chosen over Pattern A (81 files) because:
- Semantic clarity: separate H2 reflects distinct function (evidence vs framing)
- Parseable structure: H2 is load-bearing Markdown; nested bold is decoration
- Lint simplicity: one-step H2 lookup

Paid the 81-file migration cost via one-off mechanical script (no prose rewrite).

**Format unification scope**:

1. **Native critical read** — 81 files: inline `**Native critical read**:` bold (Pattern A) → `## Native critical read` standalone H2 (Pattern B canonical). Migrated via one-off script.
2. **Metadata grouping** — 5 files: flat `## Trigger slug:` / `## Over-mimic risk:` H2-per-field → grouped `## Metadata` with bullet items. Manually fixed (Miyazawa / Sakamoto / Umeda / KC Tsang / Mike Chu).
3. **Voice direction label** — 1 file (龔大中): bilingual `**What this register achieves (中文)**:` → English canonical `**What this register achieves**:`. 1 file (Tim Delaney): missing label → added.

**Lint tightening** (`scripts/lint-anchor-library.py`):

- `REQUIRED_BODY_SECTIONS` — added `## Native critical read` and `## Metadata` as required H2 sections.
- `check_native_critical_read()` — now checks for H2 section only (Pattern B). Pattern A no longer accepted.
- `check_metadata()` — now requires fields inside grouped `## Metadata` H2 section. Warns on legacy flat `## <field>:` H2 headers.
- `check_voice_direction()` — NEW. Enforces canonical `**What this register achieves**:` label (blocks bilingual or missing variants).

**Baseline change**:

| | v1.13.2 | v1.13.3 |
|---|---|---|
| Clean | 76 | 85 |
| Clean with warnings | 2 | 2 |
| Failed | 12 | 3 |

Rules are STRICTER in v1.13.3 yet clean count rose. Two mechanisms:
- 9 Pattern B files that v1.13.2 lint false-positive-failed (mismatched regex for "missing Native critical read") now genuinely clean under canonical-only rule.
- Format unification removed format-drift failures; remaining 3 are substantive (2 dual-quadrant + 1 KC Tsang Examples<5).

**Affected files**: 88 of 90 anchors edited (structural only — zero prose rewrites):
- 81 files: Native critical read label → H2 migration
- 5 files: flat Metadata → grouped
- 1 file: bilingual label → English (龔大中; content prose unchanged)
- 1 file: missing label added (Tim Delaney)

**CI lint gate** (bundled in this release — previously deferred pending baseline reduction):

- New `scripts/lint-baseline.txt` lists 3 accepted failures (2 dual-quadrant + 1 Examples<5) as exception list.
- Lint script adds `--baseline <file>` flag. Under baseline mode: current failures ⊆ baseline → exit 0; new failure outside baseline → exit 1; baseline entry now passing → exit 0 + nudge.
- New job `copywriting-anchor-lint` in `.github/workflows/skill-structure.yml` runs on push to main + every PR targeting main. Consumes `--baseline` mode so only NEW drift blocks merge.

**Other changes**:

- `docs/tests/lint-baseline-v1.13.2.md` → `docs/tests/lint-baseline-v1.13.3.md` (full rewrite with canonical structure documented + migration audit trail + CI integration).
- `plugin.json`: 1.13.2 → 1.13.3

**Supersedes PR #129**: that PR added Pattern A + Pattern B fallback logic to lint — rendered obsolete by v1.13.3's canonical-only enforcement. #129 closed.

**Meta-reflection**: fourth consecutive audit in the v1.13.x series surfacing the "dead ceremony" pattern — v1.13.3 closes the main format-drift surface. With 3 substantive failures remaining (vs 19 in v1.13.0), CI lint gate becomes practical (follow-up PR).

## v1.13.2 — 2026-04-22 (lint rule audit — drop no-consumer field checks, fix bold-markup regex)

Pure housekeeping. No runtime behavior change. No anchor file content modified.

**Problem discovered**: when user questioned whether `creator_type` has any runtime use, a grep audit found ZERO consumers — neither SKILL.md nor any rubric / agent / protocol reads the value. The lint script (introduced in v1.13.0 C2) was enforcing presence of a field nothing uses. Similar dead-ceremony for `Trigger slug` and `Pairs with form` (also zero consumers).

Separately: re-inspection of the 3 "missing Over-mimic risk:" baseline failures revealed the files DID have the line, written as `Over-mimic risk: **HIGH**`. Lint regex `([A-Z+\-]+)` didn't match through the `**bold**` markup — a false-positive lint bug.

**Lint rule changes** (`scripts/lint-anchor-library.py`):

1. `REQUIRED_FRONTMATTER_FIELDS` — dropped `creator_type` (no runtime consumer). Reduced from 6 fields to 5: `schema_version`, `anchor_slug`, `culture`, `quadrant`, `landmark`.
2. `check_metadata()` — `Over-mimic risk:` regex changed from `([A-Z+\-]+)` to `\*{0,2}([A-Z+\-]+)\*{0,2}` to accept bold-wrapped values.
3. `check_metadata()` — removed warnings for `Trigger slug:` / `Pairs with form:` missing (no runtime consumer; documentation-only).
4. `check_metadata()` — removed "prefer grouped `## Metadata` section" warning (formatting preference, no functional impact).
5. Docstring updated to explicitly list which fields have runtime consumers (schema_version / anchor_slug / culture / quadrant / landmark / Over-mimic risk) vs which are documentation-only (creator_type / Trigger slug / Pairs with form).

**Baseline change**:

| | v1.13.0 | v1.13.2 |
|---|---|---|
| Clean | 71 | 76 |
| Clean with warnings | 0 | 2 |
| Failed | 19 | 12 |

Removed from failure set:
- 5 files missing `creator_type` → lint no longer requires
- 3 files with bold-wrapped `Over-mimic risk: **HIGH**` → regex now matches

Remaining 12 failures are real content/schema drift (deferred to v1.14.x): 9 missing Native critical read + 2 dual-quadrant descriptive + 1 Examples count < 5.

**Other changes**:

- `docs/lint-baseline-v1.13.0.md` → `docs/tests/lint-baseline-v1.13.2.md` (moved into tests/ per v1.13.1 reorg; rewritten with new numbers + runtime-consumer audit table).
- `plugin.json`: 1.13.1 → 1.13.2

**Meta-reflection**: this finding was itself an example of the same dead-ceremony pattern v1.13.0 Pass 3 simplification tackled. The original v1.13.0 C2 commit added a lint that enforced fields no runtime consumer cares about — my own defense-in-depth accumulation, caught by user's "does this field actually matter?" challenge. Lint now mirrors the v1.13.0 principle: enforce only what is verifiably load-bearing.

## v1.13.1 — 2026-04-22 (docs reorg + schema/CLAUDE.md cleanup)

Pure housekeeping release. No runtime behavior change. No API / envelope field change.

**docs/ subdirectory consolidation (7 → 3)**:
- `docs/voice-anchor-deep-dives/` + `docs/voice-anchor-research-notes/` → `docs/voice-anchor-notes/` (69 files; layer 2/3 research + rejected-candidate trails in one place)
- `docs/voice-anchor-e2e-tests/` + `docs/e2e-tests/` + `docs/data-collection/` → `docs/tests/` (test artifacts across versions unified; data-collection retained as subdir)
- `docs/format-templates/` + `docs/register-references/` → `docs/anchor-references/` (18 files; non-Layer-1 references — institutional / platform / format-template + movement / campaign / register-reference — unified per consolidated README)

All `git mv` with preserved history. All active path references updated in standards files (9 quadrant routers + voice-anchor-meta.md + 2 anchor files) + docs/anchor-schema-v2.md + docs/voice-library-recast-audit.md + docs/voice-anchor-notes/README.md. Historical snapshots (CHANGELOG past entries / ab-retrospective / anchor-schema-v2-pilot-findings / implementation-plan / E2E test snapshots) retain original path references as-is (those describe state at time of writing).

**`.claude-plugin/envelope.schema.json` cleanup**: `immutable_fields_enforced.description` dropped the "(was tone_notes.lineage_gap pre-v1.13.0)" legacy annotation. v1.13.0 shipped; migration note no longer needed in schema comment.

**`CLAUDE.md §Immutable fields — preservation contract` cleanup**: split one 8-row table into two coherent tables:
- Voice-pipeline fields (5 rows): voice_quadrant object, schwartz_alignment, named_master_fit_warning, brief.* L1, express_mode_used
- Router bookkeeping (3 rows): audit_trail, retries.*, violation

Router bookkeeping table drops the "Readers" column since router is the sole writer AND reader; reduces table clutter. Voice-pipeline table drops the "(was lineage_gap)" legacy annotation.

**`plugin.json` version**: 1.13.0 → 1.13.1

No CI behavior, no Pass 3 behavior, no envelope field additions/renames.

## v1.13.0 — 2026-04-22 (Pass 3 simplification — consolidate meta files + linear-flow Pass 3 + library CI lint)

Pure simplification release. Three commits in one PR, each leaves repo in valid state:

### Commit 1 — Library standards consolidation

Merged `voice-anchor-meta-core.md` + `voice-anchor-meta-detail.md` + `axis-extreme-anchors.md` into single `voice-anchor-meta.md` (499 lines). Former split (hot path vs deep path) optimized token budget but produced mental overhead tracking which file held which rule; v1.13.0 collapses into unified SSOT. axis-extreme content absorbed as `§Axis Extreme candidates` section (orthogonal cross-language concept preserved).

All active consumers updated: SKILL.md Pass 3 load instructions, voice-consistency-gate.md Dimension 6, 4 quadrant router cross-ref sections (jp-q2, jp-q3, zh-q2, zh-q3), voice-and-tone.md, intake express-mode protocol, ideation SKILL + protocol, plugin CLAUDE.md, active docs. Historical snapshots (data-collection/, e2e-tests/v*.md, test-*.md, CHANGELOG entries, implementation-plan) preserved as-is.

Commit 1 ships mechanical changes only — no runtime behavior change, Pass 3 still runs as 4-branch dispatch.

### Commit 2 — Library CI lint introduction

New `scripts/lint-anchor-library.py` implements v2 schema structural check + machine-checkable portions of 4-condition rubric. Baseline run on 90 anchors: 71 pass clean / 19 have pre-existing structural drift documented in `docs/lint-baseline-v1.13.0.md`. Lint prepares for commit 3's removal of runtime 4-condition check.

### Commit 3 — Pass 3 simplification + breaking envelope field renames

Pass 3 refactored from 4-branch dispatch (Pass 3a JP Craft Gate / 3b ZH Craft Gate / 3c Axis Extreme / 3d Register Signal) to single 8-step linear flow:

1. Load `voice-anchor-meta.md` + landmark-targeted quadrant router section
2. Build candidate pool (automatic rejection + negation-of-axis + named-creator forced rank 1)
3. Fit judgment + ranking + self-report confidence (v1.12.1 instrumentation retained)
4. Apply primary + mitigation inline (anchor file SSOT + 9-author fallback registry)
5. Thesis-conflict self-check
6. Safe-substitute suggestion (conditional)
7. Secondary anchor (opt-in, max 1)
8. Output

Named-creator routing (formerly JP/ZH_CRAFT_MASTER_MAP 1:1 lookup) absorbed into Step 2.3 as candidate-pool priority — named anchor forced rank 1 with optional `named_master_fit_warning` if agent's fit assessment is MEDIUM or LOW.

Removed:
- `§Pass 3 activation guard` 3-tier branching (replaced by §When Pass 3 applies single predicate)
- `§Pre-pass schwartz_alignment awareness note` (v1.2.0 downgraded; v1.13.0 removes residual ceremony — Phase 8 8b remains sole consumer)
- v1 schema dual detection (all 81 anchors are v2)
- Runtime 4-condition rubric re-validation (moved to CI lint per commit 2)
- JP_CRAFT_MASTER_MAP / ZH_CRAFT_MASTER_MAP lookup tables (collapsed into candidate-pool priority)

**Breaking: envelope field renames**

Three `tone_notes` top-level fields REMOVED; semantics merged into `register_signal_applied`:

- `tone_notes.lineage_applied` → `tone_notes.register_signal_applied.primary_anchor_slug`
- `tone_notes.lineage_gap` → `tone_notes.register_signal_applied.named_master_fit_warning` (richer structured warning)
- `tone_notes.axis_extreme_applied` → `tone_notes.register_signal_applied.landmark_position` (axis landmarks flow through uniformly)

Downstream updated in same commit:
- `rubrics/voice-consistency-gate.md` — Dimension 6 simplified SSOT precedence (anchor file first, fallback registry second); Dimension 7 read path updated
- `CLAUDE.md §Immutable fields` — `lineage_gap` row replaced with `register_signal_applied.named_master_fit_warning`
- `.claude-plugin/envelope.schema.json` — `tone_notes` schema updated with `register_signal_applied` object (primary_anchor_slug / named_master_fit_warning / agent_selection_confidence / thesis_self_check)

### Impact (measured, not estimated)

**Static files** (`git diff main...HEAD` + `wc -l` / `wc -w`):

| Dimension | v1.12.1 | v1.13.0 | Delta |
|---|---|---|---|
| SKILL.md total lines | 537 | 431 | −20% |
| SKILL.md word count | 4,301 | 3,227 | −25% |
| Standards files count (meta) | 3 (core + detail + axis-extreme) | 1 (voice-anchor-meta.md) | −67% |
| Meta files total words | 5,442 (2,253+2,613+576) | 4,600 | −15% |
| SKILL+meta total words | 9,743 | 7,827 | **−20% (~−3K tokens at 1.5 tok/word)** |
| Branch dispatch control paths | 4 mutually exclusive | 1 linear flow | simpler |
| Runtime 4-condition re-validation | yes | no (CI lint) | removed |
| Schwartz pre-pass ceremony | present | removed (inline passthrough only) | removed |
| v1/v2 schema dual detection | present | v2-only | removed |
| Library CI lint | none | 90 anchors / 71 clean / 19 drift documented | new |

**Runtime per-Pass-3-invocation** (depends on path):

| Path | v1.12.1 load (words) | v1.13.0 load (words) | Delta |
|---|---|---|---|
| Register Signal (most common) | SKILL 4.3K + meta-core 2.3K + meta-detail 2.6K + router ~0.5K ≈ **9.7K** | SKILL 3.2K + meta 4.6K + router ~0.5K ≈ **8.3K** | **−14%** |
| Craft Gate (named master) | SKILL 4.3K + meta-core 2.3K (+conditional meta-detail 2.6K) + anchor ≈ 6.6-9.2K | same as Register Signal ≈ **8.3K** | neutral to +10% |
| Axis Extreme (rare) | SKILL 4.3K + meta-core 2.3K + axis-extreme 0.6K ≈ **7.2K** | same as Register Signal ≈ **8.3K** | +15% |

**Honest note**: the "−30 to −50% token load" wording in early drafts was over-optimistic. True savings are **~−14% on the common Register Signal path**; Axis Extreme slightly increased because the unified flow loads the merged meta file rather than only the relevant slice. The primary value of v1.13.0 is **mental-model simplification + SSOT + removing dead ceremony (schwartz pre-pass, v1 schema detection, 4-branch dispatch, runtime 4-condition re-validation)** — not raw token count.

### Not done in this PR (deferred to future releases)

- Fix the 19 pre-existing anchor lint failures (baseline documented in `docs/lint-baseline-v1.13.0.md`; mechanical fixes in v1.13.x patches, content/schema fixes in v1.14.x)
- Thesis weight range mechanism (new intake schema for thesis element priorities — Brief 1 / 4 pattern from v1.12.1 data collection; deferred to v1.14.0 design)
- Pass 3 degradation detection (Pre-Pass-3 vs Post-Pass-3 delta check — Brief 3 / 4 pattern from v1.12.1 data collection; needs design)
- Wire CI GitHub Actions step for `scripts/lint-anchor-library.py` (manual invocation only in v1.13.0; CI block gating after baseline cleanup)

## v1.12.1 — 2026-04-22 (Step 3 confidence instrumentation + 5-brief data collection)

v1.12.1 is a non-breaking additive patch. Added `agent_selection_confidence ∈ {HIGH, MEDIUM, LOW}` self-report field to Pass 3d Step 3 output schema. 5 engineered test briefs run to measure correlation between agent meta-cognition and user-graded copy mediocrity. Full data-collection results + decision rationale in `docs/data-collection/v1.12.1-step3-confidence-vs-mediocrity/results-summary.md`. Findings informed v1.13.0 direction (external simplification first, thesis weight range + Pass 3 degradation detection deferred).

## v1.12.0 — 2026-04-22 (anchor gap-fill round 2 — 3 new anchors + 5th JP craft-gate + 2 research notes + cross-anchor analysis)

Research-first protocol continues (user directive from v1.11.0: "如果研究後發現資料不足以規則化語氣 那就只留研究筆記"). 6 parallel research agents dispatched; 3 candidates passed v2 eligibility gate, 2 failed (produced research notes), 1 cross-anchor analysis produced findings note.

### Anchor count: 87 → 90 (+3)

### 3 new v2 anchors

- **`anchor-jp-nakahata-takashi-kougo-chokugen.md`** (JP Q3 center, toward-Q2 hinge) — 仲畑貴志 口語直言 / 肉声ウィット; TCC 殿堂 2015; 「おしりだって、洗ってほしい。」(TOTO 1982-83) /「目のつけどころが、シャープでしょ。」/「ココロも満タンに。」. **5th JP craft-gate master** — `JP_CRAFT_MASTER_MAP` extended. Over-mimic HIGH+.
- **`anchor-jp-mitani-koki-group-scene-dialogue-comedy.md`** (JP Q2 toward-Q1) — 三谷幸喜 群像会話劇 + 遮り + 敬語ズレ + Billy Wilder 系譜; 『古畑任三郎』『12人の優しい日本人』. Over-mimic MEDIUM.
- **`anchor-jp-kudo-kankuro-youth-colloquial-mashup.md`** (JP Q3 toward-Q2) — 宮藤官九郎 若者口語×時代 mashup グルーヴ; 『あまちゃん』「じぇじぇじぇ」/『いだてん』落語章 mashup. Over-mimic HIGH.

### 5th JP craft-gate master

`JP_CRAFT_MASTER_MAP` in SKILL.md extended from 4 to 5 masters:

```
JP_CRAFT_MASTER_MAP = {
  糸井重里: itoi-shigesato-state-proposal,
  岩崎俊一: iwasaki-shunichi-yonin,
  眞木準: maki-jun-craft-aphorism,
  谷山雅計: taniyama-masakazu-discipline,
  仲畑貴志: nakahata-takashi-kougo-chokugen,    # v1.12.0 NEW
}
```

Pass 3a JP craft-gate activation list expands accordingly. TCC ホール・オブ・フェイム 2015 顕彰 + 糸井重里 50 年来の親友 peer attribution + 谷山雅計 "日本のコピー20本" 仲畑作選 = 同業評価確立.

### 2 research-only notes (candidates rejected)

- **`zh-tw-sun-dawei-taiwan-advertising-canon.md`** — 孫大偉 FAILED. 2/4 gate pass: verbatim slogans 齊備 + native critical read 足 + failure-mode 可寫,但 sentence-level prose mechanics <5 (body copy corpus 線上不可及;slogan layer ≤12 字不足歸納機制;散文 register ≠ 廣告 register). zh-TW Q4 槽位**預留**給孫大偉不另覓替代 (其「台灣 4A 奧美 canon」條件在華文圈無對等人選). Next-round strategy: 由線上搜尋升級至圖書館 + 紙本 archive.
- **`zh-tw-ho-jung-hsing-investigative-journalism.md`** — 何榮幸 FAILED. Personal-vs-institutional voice mismatch: 調查記者 register 早已內化為報導者集體 style; 個人散文 register 屬社運世代通用抒情體不 distinctive. 建議下一輪候選: 房慧真 / 張娟芬 / 阿潑 / 吳介民 / 吳叡人.

### 1 cross-anchor analysis note

- **`zh-tw-li-xu-stylistic-siblings-analysis.md`** — 李欣頻 ↔ 許舜英 substitute feasibility. **Verdict**: confirm reject (Option V1 + partial V2). Even with risk-differential correction (李 MEDIUM vs 許 HIGH — could pass strict-lower-rule in 李→許 direction), mechanism is fundamentally distinct (許's `X 是一種 Y` definitional-inversion + power-disparity payload ≠ 李's 排比枚舉 + antecedent-work dialogue + 具名文化座標). Neither direction qualifies as substitute per schema v2 condition 2 ("delivers adjacent register empirically verified").

### Stylistic-sibling annotations added (mirror 許↔張愛玲 precedent)

- `anchor-zh-tw-xu-shunying-ideological-definitional.md` now carries `Stylistic-sibling (not transferability): 李欣頻` with mechanism-distinct rationale
- `anchor-zh-tw-lee-hsin-ping-literary-consumption.md` now carries reciprocal `Stylistic-sibling (not transferability): 許舜英`

Prevents future re-proposal of the pairing as substitute.

### Rejected safe_substitute_for relationships (research discipline)

Research agents proposed several `safe_substitute_for` candidates that were rejected on v1.11.1 strict-lower-risk rule:
- 仲畑 HIGH+ → 坂元 MEDIUM-HIGH: rejected (仲畑 higher risk; mechanics overlap PARTIAL-only)
- 仲畑 HIGH+ → 谷山 LOW: rejected (仲畑 higher risk; mechanics overlap WEAK)
- 三谷 → Sorkin: rejected (Sorkin's 3 核心技法 — rhetorical Q-plus-self-answer / moral verdict / walk-and-talk — 全欠落)
- クドカン → 坂元裕二: rejected (register family 反対 — 動的 grooves vs 静的 peer-warm)

HIGH-risk masters still gap-flagged for substitute: Sorkin, 坂元裕二, DFW (EN-native).

### Router updates

- `jp-q3-anchors.md`: Landmark center +仲畑貴志; Landmark toward-Q2 +宮藤官九郎
- `jp-q2-anchors.md`: Landmark toward-Q1 +三谷幸喜
- `SKILL.md`: Pass 3a JP craft-gate activation list + `JP_CRAFT_MASTER_MAP` code block both extended to 5 masters

### Files touched

- `copywriting-toolkit/skills/copywriting-voice-tone-stage/standards/` — 3 new anchor-*.md + 2 router updates (jp-q2, jp-q3) + 2 anchor updates (許, 李 stylistic-sibling lines)
- `copywriting-toolkit/skills/copywriting-voice-tone-stage/SKILL.md` — JP_CRAFT_MASTER_MAP + Pass 3a activation list
- `copywriting-toolkit/docs/voice-anchor-research-notes/` — +3 notes (孫大偉 / 何榮幸 / 李許 analysis)

### Eligibility discipline recap

Research-first protocol rate: 3/6 PASS → anchor, 2/6 FAIL → research note, 1/6 cross-anchor-analysis. Protocol prevented biographical-overclaim pollution (孫大偉 slogan-only corpus / 何榮幸 institutional-voice conflation) while capturing positive additions (仲畑 completes craft-gate roster; 三谷 + クドカン fill distinct registers).

---

## v1.11.2 — 2026-04-22 (Phase 5 / Phase 6 unification — Brand Corpus ↔ anchor library cross-refs)

User-directed consolidation: Phase 5 quadrant diagnosis landmarks now explicitly link to Phase 6 anchor library entries, eliminating two-tier confusion.

### CLAUDE.md §Provenance Principle scope refinement

Previous default treated entire `skills/*/standards/*.md` as Tier 1 byte-identical. Refined to apply Tier 1 only to **third-party framework text within standards files** (e.g., Halliday Tenor theory, Vaughn FCB grid, Schwartz 5-level taxonomy, PASONA definitions). Team-curated segments inside standards files (Brand Corpus selections, exemplar lists) are Tier 2 — plugin may diverge to align with plugin-specific anchor library decisions.

Also clarified: the entire Phase 6 anchor system (87 `anchor-*.md` + meta-core/meta-detail + 12 routers + `anchor-schema-v2.md`) is plugin-native with no upstream counterpart — not subject to `diff -q`.

### Phase 5 positioning.md — 19 Brand Corpus entries annotated with Phase 6 cross-refs

For each entry, added `**Phase 6 anchor**` (individual-creator match exists) OR `**Phase 6 handoff**` (institutional entry; names nearest individual anchor for rewrite).

**11 entries with direct Phase 6 anchor match** (linked inline):
- Q1: Rolls-Royce → Ogilvy
- Q2: Apple → Lee Clow / MUJI → 原研哉 / Patagonia → Chouinard / 誠品 → 李欣頻 / 中興 → 許舜英 / 左岸 → 葉明桂
- Q3: 西武 → 糸井重里 / ミツカン → 岩崎俊一 / ほぼ日 → 糸井 / 全聯 → 龔大中
- Q4: UNIQLO → 佐藤可士和

**8 institutional entries retained as quadrant landmarks with Phase 6 handoff pointers** (no individual-creator anchor per v2 schema):
- Economist / 報導者 (Q1) — rotating-author institutional
- Nike (Q2) — Wieden+Kennedy agency-rotating
- Dove (Q3) — campaign-level
- JR九州 (Q3) — brand-era; 仲畑貴志 era has no standalone anchor (flagged for future research)
- Shopee / Amazon (Q4) — in-house rotating

### Phase 5 SKILL.md — cross-language maestro examples refreshed

Step 5 example list updated:
- Mailchimp → `anchor-en-kate-kiefer-lee-mailchimp-voice-tone.md` (Kate Kiefer Lee recast)
- Innocent → `anchor-en-richard-reed-innocent-wackaging.md` (Richard Reed recast)
- zh-TW Q3 → `anchor-zh-tw-gong-dazhong-*` (龔大中 recast, not "全聯經濟美學派")
- JP Q3 → 糸井重里 / 岩崎俊一 anchor slugs

Added new §Two-tier voice curation section clarifying Phase 5 Brand Corpus vs Phase 6 Anchor Library division of labor.

### Rationale

User surfaced: "Phase 5 quadrant 診斷用的識別 landmark 應該要用 Phase 6 裡對應的 anchor — 這樣才不會讓使用者產生疑惑". Pre-v1.11.2 users could see Mailchimp in Phase 5 and then find it "moved to format-templates" in Phase 6's v2 library with no explanation. Post-v1.11.2, every Phase 5 entry explicitly resolves to a Phase 6 handoff.

The 8 institutional-retained entries remain valuable as **quadrant landmarks** (Economist IS a Q1 register exemplar even without individual-creator voice) but no longer confuse users about Phase 6 rewrite targets.

### Files touched

- `copywriting-toolkit/CLAUDE.md` — §Provenance Principle scope refinement
- `copywriting-toolkit/skills/copywriting-voice-quadrant-stage/standards/voice-quadrant-positioning.md` — 19 Brand Corpus entries + 4 quadrant preambles annotated
- `copywriting-toolkit/skills/copywriting-voice-quadrant-stage/SKILL.md` — Step 5 examples refreshed + §Two-tier voice curation added

No anchor changes. No agent changes. No Phase 6 routing changes.

---

## v1.11.1 — 2026-04-22 (safe_substitute predicate fix + router prose parity + invalid-pairing cleanup)

Post-v1.11.0 E2E surfaced a trigger-predicate bug + 2 invalid pairings + router prose parity gap. 4 parallel Pass 3 simulation agents run against main post-merge; findings documented in `docs/voice-anchor-e2e-tests/v1.11.0-post-merge-findings.md`.

### Bug 1: Safe-substitute trigger restricted to HIGH-registry targets (silent failure)

**Symptom**: Test 3 (張愛玲→白先勇 substitute) — v1.11.0 wired `safe_substitute_for: [張愛玲]` on 白先勇 anchor, but Pass 3 never emits `substitute_suggested` because meta-core §Safe-substitute lookup required named master to be in the HIGH-risk registry table. 張愛玲 is MEDIUM risk, not in registry → trigger silently fails.

**Fix**: Broaden predicate in `voice-anchor-meta-core.md §Safe-substitute lookup` + mirror update in `SKILL.md` Pass 3d step 6.

- **Before**: `"When brief.voice_reference names a master with HIGH over-mimic risk in the registry ..."`
- **After**: `"When brief.voice_reference names any master AND at least one anchor lists that master in frontmatter.safe_substitute_for[]. Substitute qualifies iff over-mimic risk is strictly lower (LOW < MEDIUM < MEDIUM-HIGH < HIGH < HIGH+)."`

Risk lookup order: anchor's own frontmatter → meta-core registry → default MEDIUM.

### Bug 2: v1.11.0 introduced 2 invalid safe_substitute_for pairings (risk reversed)

Audit of all v1.11.0 pairings against schema v2 rule "substitute's risk must be strictly lower":

| Pair | Substitute | Target | Valid? |
|---|---|---|---|
| Carver → Hemingway | MEDIUM-HIGH | HIGH | ✓ |
| Ephron → Didion | MEDIUM | HIGH | ✓ |
| Hammett → Chandler | MEDIUM | HIGH | ✓ |
| 谷川 → 糸井 | LOW | HIGH+ | ✓ |
| 白先勇 → 張愛玲 | LOW | MEDIUM | ✓ |
| 錢鍾書 → DFW | LOW-MEDIUM | HIGH | ✓ |
| **養老 → 原研哉** | **MEDIUM-HIGH** | **MEDIUM** | **✗ removed v1.11.1** |
| **外山 → 伊丹** | **MEDIUM** | **LOW** | **✗ removed v1.11.1** |

Both invalid pairings came from research agents that suggested axis-intent relationships (Q2 manifesto avoidance / essay lineage) misfiled under the risk-based `safe_substitute_for` field. These relationships are real but belong in a different conceptual slot (not risk-reduction). Removed from:
- `anchor-jp-yoro-takeshi-baka-no-kabe.md` — frontmatter field + router entry in `jp-q1-anchors.md`
- `anchor-jp-toyama-shigehiko-shikou-seiri.md` — frontmatter field + router entry in `jp-q4-anchors.md`

Preserved prose note in each anchor's Metadata Safe-substitute line documents why removed (so future readers don't re-propose).

### New: tone_cue contamination upgrade

v1.11.1 adds a stronger-signal path: if `brief.tone_cue` contains tokens matching the substitute anchor's `Don't / Failure mode` warning about named-master contamination, upgrade `substitute_suggested` → `substitute_recommended_strong` in envelope. Example: brief `voice_reference: 張愛玲` + `tone_cue: 華麗頹廢` matches 白先勇's Don't-block warning "LLM 常把白先勇誤讀為張愛玲式華麗頹廢" → recommends 白先勇 strongly rather than merely suggesting.

### Router prose parity (6 pairs added)

v1.11.0 frontmatter pairings were queryable but router-level discoverability was asymmetric (JP routers inlined substitute notes; EN/ZH did not). v1.11.1 adds one-line substitute notes to router entries for all 6 valid pairings:

- `en-q1-anchors.md` §Hemingway — note Carver as substitute + paired Carver cross-ref
- `en-q2-anchors.md` §Didion — note Ephron as substitute
- `en-q4-anchors.md` §Chandler — note Hammett as substitute + paired Hammett cross-ref
- `zh-q2-anchors.md` §錢鍾書 — note DFW cross-lang substitute relationship
- `zh-q2-anchors.md` §白先勇 — note 張愛玲 substitute relationship + contamination trigger
- `zh-q2-anchors.md` §張愛玲 — note 白先勇 as substitute (reverse-direction discoverability)
- `jp-q3-anchors.md` §谷川 — note 糸井 substitute relationship

### E2E test results

4 parallel simulations:
- Test 1 (池上彰 explicit NHK brief) — PASS, clean routing
- Test 2 (Hemingway→Carver pet-food brief) — PASS_WITH_NOTES (router parity fix now applied)
- Test 3 (張愛玲→白先勇 Shanghai hotel brief) — PASS_WITH_NOTES (predicate bug fix now applied)
- Test 4 (松浦 auto-select 暮しの手帖 brief) — PASS_WITH_NOTES (negation-of-axis fires correctly)

Full findings: `docs/voice-anchor-e2e-tests/v1.11.0-post-merge-findings.md`.

### Valid pairings post-v1.11.1

7 total (dropped 2 from v1.11.0):
- Carver → [Hemingway]
- Ephron → [Didion, Joan Didion]
- Hammett → [Chandler, Raymond Chandler]
- 谷川俊太郎 → [糸井重里]
- 白先勇 → [張愛玲]
- 錢鍾書 → [David Foster Wallace, DFW]
- 吉本ばなな → [村上春樹] (from v1.10.0)

---

## v1.11.0 — 2026-04-22 (anchor gap-fill — 6 new + 1 research-only + 6 safe_substitute_for relationships)

Research-first, fallback-to-note protocol per user directive: "先深入研究候選 如果研究後發現資料不足以規則化語氣 那就只留研究筆記但放棄成為 anchor". 8 parallel research agents dispatched; 6 candidates passed the v2 Layer-1 eligibility gate (≥5 verbatim + ≥3 attributed native critical read + ≥5 actionable sentence-level mechanics + failure mode + ≤15-word mitigation), 1 candidate failed and produced a research note, 1 agent ran the Phase C cross-anchor sweep.

### Anchor count: 81 → 87 (+6)

### 6 new v2 anchors

**JP (+4)**:
- `anchor-jp-ikegami-akira-kaisetsu-journalism.md` (JP Q1 center) — 池上彰 わかりやすさ解説; 和文和訳 + 擬人化直接話法. Over-mimic MEDIUM.
- `anchor-jp-yoro-takeshi-baka-no-kabe.md` (JP Q1 center, toward-Q2 secondary) — 養老孟司 口述→整文 intellectual register; 『バカの壁』『死の壁』. `safe_substitute_for: [原研哉]`. Over-mimic MEDIUM-HIGH.
- `anchor-jp-matsuura-yataro-teinei-essay.md` (JP Q3 toward-Q4) — 松浦弥太郎「今日もていねいに」; 暮しの手帖 + 100の基本. Over-mimic HIGH. (Agent re-slotted Q4→Q3 based on ですます調+一人称ぼく evidence.)
- `anchor-jp-toyama-shigehiko-shikou-seiri.md` (JP Q4 toward-Q1) — 外山滋比古 思考エッセイ; 『思考の整理学』+ 英文学者的 familiar essay. `safe_substitute_for: [伊丹十三]`. Over-mimic MEDIUM.

**EN (+2)**:
- `anchor-en-schwartz-eugene-direct-response-breakthrough.md` (EN Q4 center) — Eugene Schwartz direct-response canon; *Breakthrough Advertising* 1966 + Rodale seminar 1994. Over-mimic HIGH.
- `anchor-en-levine-matt-money-stuff.md` (EN Q4 center) — Matt Levine insider-wry financial exegesis; Bloomberg Money Stuff 2015-present. Over-mimic HIGH.

### 1 research-only note (candidate rejected)

- `docs/voice-anchor-research-notes/zh-tw-lin-chun-ming-tw-4a-canon.md` — 林俊明 candidate FAILED. Research surfaced biographical misattribution (Jimmy Lam is 香港 Leo Burnett/DDB lineage, not 台灣 4A 奧美), corpus thin (2 verbatim, need ≥5), culture category error (zh-HK / 粵語 register, not zh-TW). Note preserves research trail + recommends 孫大偉 as true zh-TW Q4 candidate for future research.

### 6 `safe_substitute_for:` cross-references added (from Phase C sweep)

Sweep agent analyzed 81 existing anchors for valid substitute relationships (target in meta-core registry OR widely-pastiched; mechanics overlap documented; substitute's over-mimic risk < target's).

| Anchor modified | safe_substitute_for added | Justification |
|---|---|---|
| `anchor-en-carver-working-class-precision.md` | `[Hemingway]` | Self-declared Hemingway descendant; iceberg omission + flat declarative + said-only tags; brand-name load-bearing nouns resist generic-object parody trap |
| `anchor-en-ephron-warm-wit.md` | `[Didion, Joan Didion]` | Ephron in "Didion/Ephron/Dunham personal-essay line" (Sloane Crosley NYTBR); list-as-argument + flat punchline replaces Didion's antithesis-tic |
| `anchor-en-hammett-terse-procedural.md` | `[Chandler, Raymond Chandler]` | Chandler names Hammett as progenitor (1944 essay); Hammett's own Don't block explicitly targets "Chandler-contaminated Hammett" |
| `anchor-jp-tanikawa-shi-no-kotoba.md` | `[糸井重里]` | Documented lineage (ほぼ日『ぼく』2013 collab); ひらがな優位 + breath-scaled lines; avoids 糸井's「。」-on-fragment surface-mimic trap |
| `anchor-zh-tw-pai-hsien-yung-elegiac-diaspora.md` | `[張愛玲]` | 白's own Don't block flags Chang-contamination; Chang-mechanics sans aphoristic-metaphor density that drives 張's failure modes |
| `anchor-zh-qianzhongshu-erudite-sardonic-metaphor.md` | `[David Foster Wallace, DFW]` | Cross-cultural equivalent declared in own Metadata; 博喻三連 + 譏誚 delivers recursive erudite maximalism without DFW's nested-footnote failure |

### 1 substitution pair REJECTED

- Allebach ↔ Parvez (same HIGH risk; violates schema rule "substitute's risk must be LOWER than target's"). Both anchors retained independently as era-locked individual SM operators; cross-reference kept prose-only.

### Router updates (4 files)

- `jp-q1-anchors.md` Landmark: center filled (was pointing to toward-edges only) — 池上彰 + 養老孟司
- `jp-q3-anchors.md` Landmark: toward-Q4 added — 松浦弥太郎
- `jp-q4-anchors.md` Landmark: toward-Q1 extended — 外山滋比古 (alongside 佐藤可士和)
- `en-q4-anchors.md` Landmark: center extended — Eugene Schwartz + Matt Levine (alongside Basecamp)

### Flagged for future research (HIGH-risk masters with NO current substitute)

- Aaron Sorkin — unique register, no JP/ZH/EN candidate covers rhetorical-Q-plus-self-answer + walk-and-talk
- 坂元裕二 — no adjacent JP craft-gate anchor covers 具体数字+固有名詞積層 + 敬語 peer-warm + 比喩の橋は張らない
- 許舜英 ↔ 李欣頻 — both HIGH, mechanism-distinct per 許's Metadata ("Stylistic-sibling — not transferability"); no safe substitute
- David Foster Wallace — EN-native lower-risk substitute does not exist (錢鍾書 is cross-lang only)

### Eligibility discipline

Research-first protocol prevented 1/8 candidates (12.5%) from entering the library despite having a proposed slot. Demonstrates the protocol's value: user directive ensured research gate held even when an anchor name was on the plan. Research notes preserve the trail so future corpus access (e.g., 《廣告痴人說夢話》紙本掃描) can revisit.

### New directory

- `copywriting-toolkit/docs/voice-anchor-research-notes/` — holds rejected-candidate research artifacts. Distinct from `voice-anchor-deep-dives/` (Layer 2/3 research for accepted anchors) and `voice-anchor-gap-research.md` (planning doc).

---

## v1.10.0 — 2026-04-22 (auto-selection polish — 3 improvements from v1.9.x E2E findings)

Post-v1.9.x E2E (6 agent-simulated Pass 3 runs, 3 explicit-voice + 3 auto-select) surfaced 3 architectural improvements, all shipped together as v1.10.0:

### 1. `safe_substitute_for:` anchor frontmatter field (schema v2 extension)

Addresses v1.9.x Test 1 finding: "吉本ばなな is Murakami safe substitute" was only in router prose, not queryable by Pass 3 auto-selector.

- Added optional `safe_substitute_for: [higher-risk-master-name, ...]` frontmatter field to v2 schema spec (`docs/anchor-schema-v2.md §Safe substitute for`)
- Applied to `anchor-jp-yoshimoto-banana-j-bungaku.md` with `safe_substitute_for: [村上春樹]`
- Pass 3 can now query deterministically: when user specifies a HIGH-over-mimic-risk master, find anchors where named-master ∈ `safe_substitute_for[]` and suggest safer alternative
- Emits `register_signal_applied.substitute_suggested` alongside primary; user confirmation retains default primary

### 2. §Condition 5 Negation-of-axis rule (meta-core selection rubric)

Addresses v1.9.x Test 1 finding: `tone_cue` containing negation of axis (e.g., "calming, not corporate") is a strong deterministic signal that wasn't codified.

New condition in `voice-anchor-meta-core.md §Anchor selection rubric`:

> When `brief.tone_cue` contains explicit negation of an axis or axis-adjacent cluster — "not corporate" / "not artisan-snob" / "not preachy" / "not aspirational" etc. — Pass 3 auto-selector MUST:
> 1. Forbid the negated axis/cluster from consideration
> 2. Record forbidden axis in `voice_quadrant.rationale` for Phase 6 gate verification
> 3. If no anchor satisfies the negation, emit violation to intake

Example from v1.9.x E2E (JP 瞑想 app): `tone_cue: "calming, not corporate"` → Authority axis forbidden → Q1/Q2 craft-gate eliminated → Q3 private-space 吉本ばなな selected.

### 3. `secondary_anchors[]` Pass 3d output schema extension

Addresses v1.9.x Test 3 finding (EN Fried+DHH + Stratechery dual-anchor): Pass 3d output schema only had single primary; dual-anchor apply (primary register + supplementary discipline) is a natural pattern that was emitted ad-hoc.

SKILL.md Pass 3d §Register-Signal apply added step 5 (Secondary anchor application) and step 6 (Safe-substitute suggestion). Output schema `register_signal_applied` now includes:

```json
{
  "primary_anchor_slug": "...",
  "secondary_anchors": [
    {"slug": "...", "role": "secondary-discipline", "rationale": "..."}
  ],
  "substitute_suggested": {"slug": "...", "rationale": "..."} | null,
  ...
}
```

Common secondary roles:
- `"secondary-discipline"` — borrow sentence-level rule only (e.g., Stratechery "earn every declarative")
- `"secondary-cadence"` — borrow rhythm only (e.g., cross-lang borrowing 糸井 cadence in zh-TW output without vocabulary)
- `"cross-lang-borrowing"` — borrow structure across language without vocabulary transplant

Hard limit: **max 1 secondary per rewrite** — 3+ anchors compose as pastiche.

### No behavioral regression

All 3 changes are additive. Pass 3 with no secondary anchor + no substitute suggestion behaves identically to v1.9.2. Backward-compatible.

## v1.9.2 — 2026-04-22 (meta-core + meta-detail legacy cleanup — drop v1 schema body spec, consolidate drift catalogs)

Post-v1.9.0 audit identified two legacy-era bloat areas in meta files:

1. **meta-core §v1 schema body spec** — obsolete since v1.8.0 (all 81 anchors v2); no writer / consumer remaining
2. **meta-detail dual drift catalogs** — v1.9.0's `§Cross-Master Context §Critical Attribution Corrections` (Z1-Z8 + JP-8 full text) duplicated the older `§Drift corrections catalog (Z5-Z11)` section; and both sections were 100% redundant with per-anchor inline drift corrections except Z6 (孫大偉) which has no anchor home

### Changes

**meta-core** (242 → 210 lines, -500 tokens):
- Removed §v1 schema body spec (full 30-line field structure) — obsolete
- Removed §Field semantics table (documented v1-only fields) — obsolete
- Kept §Schema version selector (still used for frontmatter auto-detect)
- Kept §Anchor selection rubric + §Over-mimic mitigation registry + §Quick reference (all still load-bearing)
- §v1 schema now reads: "As of v1.9.2, no anchor files use v1 schema body. 9 v1-only authors remain as registry-row entries only (村上 / 金庸 / 三島 / 太宰 / 余華 / McCarthy / DFW / Ellroy / 莫言). Anchors default to v2; v1 schema fallback preserved for future compatibility."

**meta-detail** (298 → 242 lines, -1K tokens):
- Replaced full-text duplicate drift catalogs with single §Drift corrections catalog (pointer index) — all drifts (Z1-Z11 + JP-8) listed as 1-line entries pointing to their authoritative per-anchor home
- Only Z6 (孫大偉 agency = 奧美 → 偉太, NOT JWT) keeps full-text treatment — no 孫大偉 anchor exists
- Removed §Cross-Master Context §Critical Attribution Corrections full-text block (v1.9.0 addition, now redundant with per-anchor inlines + pointer index)
- Kept §Verified lineage map + §Cross-reference-valid-for registry + §Cross-cultural unified label rubric + §Generational Context + §LLM Reproduction Gap cross-master summary + §Voice selection guidance + §Cross-master Anti-Patterns (all genuinely cross-master, not in per-anchor)

### Pass 3a/3b conditional trigger simplification

SKILL.md Pass 3a/3b conditional load triggers simplified:

**Before (v1.9.0)**:
1. Cross-master lineage / era / critical debate
2. **Attribution-risk** (always triggered meta-detail load)
3. Multi-master comparison
4. (ZH) 意識形態 era context

**After (v1.9.2)**:
1. Cross-master lineage / era / critical debate (genuinely cross-master)
2. Multi-master side-by-side comparison
3. (ZH only) Brief references **孫大偉** — Z6 lives in meta-detail, not in any anchor
4. (ZH only) 意識形態 institutional-era context (Generational Context section)

Attribution-risk no longer auto-routes to meta-detail — all drift corrections (Z1-Z5, Z7-Z11, JP-8) are already inlined at authoritative per-anchor source. Pass 3a/3b loads meta-detail only for genuinely cross-master content.

### Token impact

Per Pass 3d trigger: meta-detail smaller → **~1K tokens saved per trigger** (5K → 4K). Pass 3a/3b default unchanged (conditional path rarely fires; when it does, section-targeted read is smaller than before).

### Drift corrections catalog (v1.9.2 pointer index)

Authoritative sources per drift:

| # | Drift | Source |
|---|---|---|
| Z1 | Altenberg | `anchor-zh-tw-ye-mingui-*` |
| Z2 | 寺山 allusion | `anchor-zh-tw-lee-hsin-ping-*` |
| Z3 | 意識形態 1987 | `anchor-zh-tw-xu-shunying-*` |
| Z4 | Content-farm discipline | `anchor-zh-tw-xu-shunying-*` |
| Z5 | 多喝水 | `anchor-zh-tw-wu-nien-jen-*` |
| **Z6** | **孫大偉 agency** | **meta-detail (no anchor)** |
| Z7 | I SEE YOU | `anchor-zh-tw-wu-nien-jen-*` |
| Z8 | 全聯 ECD | `anchor-zh-tw-gong-dazhong-*` + zh-q3 router |
| Z9 | KC Tsang identity | `anchor-zh-hk-kc-tsang-*` |
| Z10 | 全聯 Q3-center | `anchor-zh-tw-gong-dazhong-*` + zh-q3 router |
| Z11 | 意識形態 鄭松茂 | `anchor-zh-tw-xu-shunying-*` |
| JP-8 | リゲイン | `anchor-jp-iwasaki-shunichi-*` |

## v1.9.0 — 2026-04-21 (craft-lineage dissolution — absorb cross-master content into meta-detail)

Empirical analysis revealed 95% redundancy between `{jp,zh}-copy-craft-lineage.md` per-master sections and the v2 `anchor-{slug}.md` files introduced v1.7.0+. The remaining 5% (Z# attribution corrections, cross-master lineage map, generational era context, cross-master comparison tables, anti-patterns) genuinely cross-cuts masters and belongs in meta-detail, not per-anchor.

v1.9.0 dissolves the craft-lineage files: cross-master content absorbed into `voice-anchor-meta-detail.md §Cross-Master Context`; unique Z# corrections inlined into corresponding anchor Metadata sections; 2 craft-lineage standalone files deleted.

### What got absorbed into meta-detail

New `§Cross-Master Context` section in `voice-anchor-meta-detail.md`:
- **Primary Sources** (aggregate bibliography for JP + ZH craft-gate masters)
- **Critical Attribution Corrections** full text (Z1-Z8 JP+ZH + drift #JP-8)
- **Generational Context** (JP 1980s コピーライターブーム + ZH 1980s-1990s 解嚴後都會消費主義覺醒)
- **LLM Reproduction Gap Cross-master Summary** table
- **Voice selection guidance** table
- **Cross-master Anti-Patterns**
- **Cross-tradition transplant forbidden** discipline

meta-detail grows ~181 → ~380 lines (~3K → ~5K tokens). Pass 3d register-signal path regression: +~2K per trigger (acceptable, vs proposed +12K if whole craft-lineage was absorbed).

### What got inlined into anchor files

- **Z1** (Altenberg sinicized, not 葉明桂) — already inlined in `anchor-zh-tw-ye-mingui-strategic-aphorism.md §Don't` (v1.6.0)
- **Z2** (寺山修司 1967 allusion in 李欣頻 誠品) — already preserved in `anchor-zh-tw-lee-hsin-ping-literary-consumption.md §Metadata` as documented lineage
- **Z3** (意識形態 founded 1987, not 1988; canonical window 1988-1999) — NEW inline in `anchor-zh-tw-xu-shunying-ideological-definitional.md §Metadata`
- **Z4** (content-farm source discipline — canonical = 《許舜英購物日記》+ award archives) — NEW inline in 許舜英 anchor Metadata
- **Z5** (多喝水 non-吳念真) — already in `anchor-zh-tw-wu-nien-jen-taiyu-peer-intimate.md` + zh-q3 router
- **Z7** (長榮 VO 金城武) — already in 吳念真 anchor
- **Z8** (全聯 ECD 龔大中) — already in 龔大中 anchor + zh-q3 router
- **drift #JP-8** (リゲイン 非岩崎) — already in `anchor-jp-iwasaki-shunichi-yonin.md` (v1.4.x)
- **Z6** (孫大偉 JWT misattribution) — KEPT in meta-detail only (no dedicated anchor for 孫大偉; conditional-load triggers on 孫大偉-brief)

### Files removed

- `standards/jp-copy-craft-lineage.md` (269 lines)
- `standards/zh-copy-craft-lineage.md` (459 lines)

Content byte-identical-preserved: cross-master sections absorbed into meta-detail; per-master voice bodies already in anchor-*.md; per-master biographical arc stays preserved in `docs/voice-anchor-deep-dives/pilot-layer1-v2-{slug}.md` seed files (Layer 2/3 deep-dive home, Pass 3 does NOT load).

### SKILL.md changes

- §"When lineage craft applies" (lines 35-75) — stale v1.2.0 framing removed; now correctly reflects v1.7.0+ per-master anchor load via JP_CRAFT_MASTER_MAP / ZH_CRAFT_MASTER_MAP
- Pass 3a/3b conditional load target: `jp/zh-copy-craft-lineage.md` → `voice-anchor-meta-detail.md §Cross-Master Context` (section-targeted read ~1.5K, was ~4-8K wholesale load)
- §"What This Skill Owns" — craft-lineage entries replaced with per-master anchor references
- Summary of Critical Attribution Corrections added inline (quick-reference)

### Reference updates (batch sed across ~14 files)

14 other files referencing craft-lineage filenames updated:
- `standards/voice-anchor-meta-core.md` (anchor lookup flow)
- `standards/voice-anchor-meta-detail.md` (§Cross-Master Context additions + self-reference fix for Z1 pointer)
- `standards/voice-and-tone.md` (theory-layer reference)
- `standards/{jp-q2,jp-q3,zh-q2}-anchors.md` (router craft-gate pointers)
- `standards/anchor-zh-tw-xu-shunying-*.md` (Native critical read citations)
- `skills/copywriting-ideation/SKILL.md` + `protocols/copy-ideation-advanced.md` (workflow references)
- `skills/copywriting-intake/protocols/express-mode.md` (intake grounding)

### Provenance & Divergence carve-out

craft-lineage files were Tier 1 byte-identical from `domain-teams:copywriting-team` upstream. v1.9.0 **absorbs** the content into meta-detail rather than deleting: byte-identical text preserved inside the absorbing file's `§Cross-Master Context` section. This is a structural reorganization within copywriting-toolkit, NOT content divergence from upstream canon. Upstream `domain-teams:copywriting-team/standards/{jp,zh}-copy-craft-lineage.md` remain untouched; if domain-teams wants to mirror this consolidation, a separate upstream PR would be required.

### Cumulative state (v1.9.0)

- **standards/**: 97 files (was 99 in v1.8.0; -2 craft-lineage)
  - 81 `anchor-{slug}.md` flat v2 bodies
  - 12 `{lang}-q{N}-anchors.md` router indexes
  - 2 meta (voice-anchor-meta-core + meta-detail, meta-detail now carries §Cross-Master Context)
  - 1 voice-and-tone
  - 1 axis-extreme-anchors
- **Pass 3 dispatch unchanged structurally**: Pass 3a/3b still load per-master anchor + meta-core; conditional cross-master load target changed from craft-lineage file to meta-detail §Cross-Master Context section
- **0 orphan files** (audited post-change)

### v1.9.0 E2E validation (structural)

- No broken references: batch grep confirms 0 remaining links to deleted craft-lineage files in voice-tone-stage scope
- Pass 3 dispatch paths intact: Pass 3a/3b mapping tables unchanged; only conditional-load target updated
- Byte-identical content preservation: Z1-Z8 + era context + cross-master tables verbatim in meta-detail §Cross-Master Context

Full Pass 3 agent-run E2E test against v1.9.0 deferred to v1.9.1 — structural migration low risk (no hot-path change; only conditional-load target reorganization).

## v1.8.0 — 2026-04-21 (backlog sweep: 11 recasts + 3 zh-TW Q1 new + F2/F4 fixes)

Closes the v1.6.1/v1.7.0 "RECAST pending research" backlog and fills the zh-TW Q1 individual-creator gap. Total: 14 new `anchor-{slug}.md` files (81 total anchors now in standards/). Also addresses E2E Findings 2 and 4 from v1.7.0 agent-run test.

### 11 recasts completed (resolved "RECAST pending research" markers)

Institutional / campaign / brand-era entries now have named-individual anchors:

**JP** (4):
- 原研哉 (MUJI Q2 center design AD 2001-) → `anchor-jp-hara-kenya-design-manifesto.md`
- 太田恵美 (JR東海「そうだ 京都、行こう。」Q2 center, CD 佐々木宏) → `anchor-jp-jr-central-souda-kyoto-discovery.md`
- 佐藤可士和 (UNIQLO LifeWear Q4 toward-Q1, AD 2006-) → `anchor-jp-uniqlo-sato-kashiwa-lifewear.md`
- 青木耕平 + 佐藤友子 (クラシコム Q4 toward-Q3, 2006-) → `anchor-jp-kurashicom-aoki-kohei-lifestyle-narrative.md`

**EN** (7):
- Dan Wieden (Nike "Just Do It" Q2 center, W+K 1988-) → `anchor-en-wieden-just-do-it-minimal-imperative.md`
- David Abbott (AMV BBDO Economist Q1 center, 1977-) → `anchor-en-david-abbott-economist-aphoristic.md`
- Kate Kiefer Lee (Mailchimp Voice & Tone Q3 center, 2013-) → `anchor-en-kate-kiefer-lee-mailchimp-voice-tone.md`
- Richard Reed (Innocent Drinks Q3 center, 1999-2009 STRICT era lock) → `anchor-en-richard-reed-innocent-wackaging.md`
- **Geoff Hayes + Graham Turner** (Absolut Vodka Q2 toward-Q1, 1980 founding ad) → `anchor-en-absolut-two-word-bottle-formula.md`
  - ⚠ **Attribution correction from v1 audit**: v1.3.x audit named "Costello + Hayes"; primary-source research (Adweek 2015 Hayes obituary + Communication Arts 1980 credits + Lewis *Absolut Book* 1996) confirms **Geoff Hayes (AD) + Graham Turner (CW)**. Richard Costello was TBWA equity partner / US president, not creative on this campaign.
- Jason Fried + DHH (Basecamp Rework Q1 toward-Q2 + Q4 center dual) → `anchor-en-basecamp-fried-dhh-contrarian-manifesto.md`
- John Schoolcraft (Oatly Q2 toward-Q3 + Q3 center, 2012- pre-2021-IPO canonical) → `anchor-en-schoolcraft-oatly-activist-typewriter.md`

### 3 zh-TW Q1 new entries (fills individual-creator gap)

v1.6.0 audit flagged zh-TW Q1 individual pool as 0 entries (all v1 entries were institutional/rotating-author). v1.8.0 fills with:

- 龍應台 (public intellectual essayist, Q1 toward-Q2) → `anchor-zh-tw-lung-ying-tai-public-intellectual.md`
- 南方朔 (lexical archaeology essayist, Q1 center) → `anchor-zh-tw-nan-fang-shuo-lexical-archaeology.md`
- 楊照 (lecture-hall essay, Q1 toward-Q4) → `anchor-zh-tw-yang-zhao-lecture-hall-essay.md`

### Router + format-template updates

- `jp-q2-anchors.md` center: 原研哉 + 太田恵美 now named anchors (was "RECAST pending")
- `jp-q4-anchors.md` center + toward-Q1: 青木耕平 + 佐藤可士和 added
- `en-q1-anchors.md` center + toward-Q2: David Abbott + Fried/DHH added
- `en-q2-anchors.md` center + toward-Q1 + toward-Q3: Dan Wieden + Absolut + Schoolcraft added
- `en-q3-anchors.md` center: Kate Kiefer Lee + Richard Reed + Schoolcraft (Q3 mode) added
- `en-q4-anchors.md` center: Fried/DHH (plain-practical mode) added
- `zh-q1-anchors.md` center + toward-Q2 + toward-Q4: 南方朔 + 龍應台 + 楊照 added
- `docs/format-templates/en-institutional-and-platform-aggregate.md`: 7 "RECAST pending" markers updated to "COMPLETE" with forward pointers

### E2E Findings 2 and 4 fixes

- **F2 (Cross-reference-valid-for normalization)**: 許舜英 anchor's free-text field `zh 張愛玲 aphoristic parallel (stylistic, not documented)` normalized to schema-compliant `jp: WEAK; en: WEAK` + separate `Stylistic-sibling` field pointing to 張愛玲 anchor. Semantic distinction between cross-lang transferability (STRONG/MEDIUM/WEAK per lang) and cross-master stylistic-sibling made explicit.
- **F4 (strip §Coverage self-check meta-commentary)**: 4 anchors (糸井 / 向田邦子 / Didion / 張愛玲) had leftover §Coverage self-check sections from research-agent research phase — stripped via batch script, saving ~80 tokens × 4 = ~320 tokens non-operational load.
- **F3 deferred**: Form enum sub-form granularity (e.g. `mid-form-brand-tagline` not in Phase 4 enum) — remains Phase 4 form-taxonomy scope, not voice-tone-stage.

### Anchor count

- v1.7.1: 67 flat `anchor-{slug}.md` in standards/
- v1.8.0: **81 flat anchors** (67 + 11 recasts + 3 zh-TW Q1)
- All 81 have `schema_version: 2.0` frontmatter
- All 81 reachable from Pass 3 routing (either via Pass 3a/3b craft-gate or Pass 3d register-signal)

### Still deferred (v1.9.0+ backlog)

- Layer 2/3 deep-dive research content (64 seed files in `docs/voice-anchor-deep-dives/` currently match Layer 1; biographical / era / lineage / awards research pending)
- Actual deployed-plugin Pass 3 E2E test (current tests are agent-simulated; deployed marketplace test requires live plugin loading)
- zh-TW Q4 individual DR tradition (genuinely thin — may remain cross-ref-only indefinitely)
- Remaining craft-lineage byte-identical v1 entries that have no v2 anchor yet (村上春樹 / 金庸 / 三島 etc. — low priority; mitigation already in meta-core registry)

## v1.7.1 — 2026-04-21 (over-mimic registry SSOT dedup — resolves v1.7.0 E2E Finding 1)

v1.7.0 E2E test (`docs/voice-anchor-e2e-tests/v1.7.0-pass-3ab-agent-run-findings.md`) surfaced a SSOT violation in `voice-anchor-meta-core.md §Over-mimic mitigation registry`: 8 entries for v2-migrated anchors duplicated their own `anchor-{slug}.md §Don't / Over-mimic` blocks, risking drift. v2 schema already declared anchor-as-SSOT for mitigation (§Dimension 6 consumer change); registry was not swept during v1.4.0+ migration.

v1.7.1 restructures the registry into two explicit categories and moves 8 v2-migrated entries from the registry table to a pointer-index section.

### Changes

- **Split §Over-mimic mitigation registry** into:
  - **Registry table (v1-only + movement / campaign / category entries)**: 村上春樹 / 金庸 / 三島 / 莫言 / 太宰 / 余華 / McCarthy / DFW / Ellroy / XR Declaration / Nike Dream Crazy / Extreme luxury manifesto (12 rows)
  - **v2 anchors with inline mitigation (SSOT in anchor file)**: 王家衛 / 夏目漱石 / Hemingway / Didion / Chandler / Sorkin / Duolingo-Parvez / 許舜英 (8 rows, pointer-only)
- **Updated §Usage rule**: 3-step precedence — (1) v2-migrated → read anchor's own `Don't` block, (2) v1-only → read registry table, (3) movement/category → read registry table
- Voice Consistency gate (Dimension 6) follows same precedence

### Why

Preserves v2 schema invariant: "anchor is SSOT for mitigation". Prevents drift when anchor file's `Don't` block evolves (v2 migration intent) but registry lags (v1 habit). Discoverability preserved — v2 pointer index lists the 8 anchors + their file paths so reviewers can find mitigation source at a glance.

### Not changed

- Anchor `Don't / Over-mimic` blocks in the 8 anchor files — untouched; they remain the authoritative source
- 12 v1-only / movement / category registry rows — untouched (still canonical there)
- Pass 3 dispatch logic (SKILL.md) — no change; Dimension 6 precedence was already implicit in v2 consumer change rule, now explicit

### v1.7.0 E2E Findings 2-4 deferred

- Finding 2: `Cross-reference-valid-for` tier inconsistency (許舜英 anchor) → v1.8.0+
- Finding 3: Form enum granularity gap → Phase 4 form taxonomy refinement (separate scope)
- Finding 4: anchor §Coverage self-check cleanup → v1.8.0+ optional

## v1.7.0 — 2026-04-21 (Pass 3a/3b craft-gate v2 anchor integration — resolves 7 orphaned anchor files)

Post-v1.6.1 audit surfaced 7 craft-gate `anchor-{slug}.md` files that existed as valid v2 Layer 1 bodies but had no Pass 3 load path (Pass 3a/3b was wholesale-loading `{jp,zh}-copy-craft-lineage.md` directly per v1.2.0 behavior, bypassing per-master v2 anchors introduced in v1.4.0+). v1.7.0 rewires Pass 3a/3b to load per-master v2 anchors as primary, with craft-lineage.md becoming conditional-only (attribution corrections / cross-master lineage / era context).

### SKILL.md changes

- Pass 3a/3b dispatch rewritten: load `anchor-{jp|zh-tw}-{master}.md` per voice_reference match, not `{jp,zh}-copy-craft-lineage.md` wholesale
- New **JP_CRAFT_MASTER_MAP** + **ZH_CRAFT_MASTER_MAP** tables define master → anchor-*.md routing
- `{jp,zh}-copy-craft-lineage.md` now loaded **conditionally** when brief requires cross-master lineage, attribution correction risk, era context, or multi-master comparison

### Master → anchor mapping (7 previously-orphan files now on Pass 3 hot path)

**JP** (Pass 3a):
- 糸井重里 → `anchor-jp-itoi-shigesato-state-proposal.md`
- 岩崎俊一 → `anchor-jp-iwasaki-shunichi-yonin.md`
- 眞木準 → `anchor-jp-maki-jun-craft-aphorism.md`
- 谷山雅計 → `anchor-jp-taniyama-masakazu-discipline.md`

**ZH** (Pass 3b):
- 許舜英 → `anchor-zh-tw-xu-shunying-ideological-definitional.md`
- 李欣頻 → `anchor-zh-tw-lee-hsin-ping-literary-consumption.md`
- 葉明桂 → `anchor-zh-tw-ye-mingui-strategic-aphorism.md`

### Token impact

- Craft-gate trigger cost: 8-10K wholesale craft-lineage load → ~1.2K per-master anchor body + ~2K meta-core = **~3-5K total** (down ~50% per trigger)
- Non-craft-gate paths unaffected (Pass 3c/3d token budgets unchanged)
- Attribution corrections still enforced: Z1-Z11 corrections authoritative source remains `{jp,zh}-copy-craft-lineage.md`; Pass 3a/3b conditional-load when attribution risk detected

### Architecture alignment

Resolves v1.6.1 audit finding that 7 craft-gate anchor-*.md files were "additive v2-schema translations with no load path". Now:
- JP/ZH craft-gate → Pass 3a/3b per-master v2 anchor (uniform with register-signal path)
- EN craft-gate → still uses Pass 3d register-signal (no upstream craft-lineage file; EN masters always ran via per-master anchors)
- All 67 `anchor-{slug}.md` files now reachable from Pass 3 hot path (up from 60)

### Backward compatibility

- `{jp,zh}-copy-craft-lineage.md` files unchanged (still Tier 1 byte-identical from domain-teams upstream; Provenance & Divergence Principle preserved)
- Pass 3a/3b branch condition unchanged (same 7 master names trigger gate)
- `voice-anchor-meta-core.md §Over-mimic mitigation registry` still consulted for v1 entries; v2 entries continue to use inline `Don't / Over-mimic` block

### Deferred to v1.7.1+

- Actual Pass 3 agent-run E2E test with a JP/ZH craft-gate brief (v1.6.1 only did structural verification)
- Migration of Z1-Z11 attribution corrections into per-anchor Metadata sections (optional, for fully self-contained v2 anchors)

## v1.6.1 — 2026-04-21 (restore docs/voice-anchor-deep-dives/ — accidental delete in v1.6.0)

**Bug fix**: v1.6.0 migration removed `docs/voice-anchor-deep-dives/` and 64 pilot files. Intent was to move the Layer 1 content to `standards/anchor-{slug}.md` (correct), but the folder itself is per `anchor-schema-v2.md` the designated **Layer 2/3 research artifacts home** — biographical / era / lineage / awards / primary-source bibliography beyond Layer 1 critic citations. Without the folder, future deep-dive research has nowhere to go.

**Fix**: restored all 64 files verbatim from commit `b9b1c39` (pre-delete snapshot, post-scaffolding-cleanup). Added README explaining Layer 1 vs Layer 2/3 separation and usage rules (Pass 3 MUST NOT load Layer 2/3; Dimension 6 evaluator MAY cite optionally; updates to Layer 1 and Layer 2/3 are independent commits).

Current state: the 64 files are identical to the corresponding `anchor-{slug}.md` files in `standards/` — they're **seed material** for future deep-dive expansion, not yet Layer 2/3 research. Allowed to diverge going forward.

Filename alignment deferred: v1.7.0+ may rename `pilot-layer1-v2-{slug}.md` → `{trigger-slug}.md` to match Layer 1 slugs for audit tooling simplicity.

## v1.6.0 — 2026-04-21 (full standards/*.md migration: router index + flat per-entry + institutional move-outs)

Follows v1.5.0's Phase B/C/D groundwork with the actual structural refactor. 12 quadrant aggregate files become **router indexes**; all 67 individual-creator voice anchors live in flat `anchor-{slug}.md` files alongside the routers (single-layer flat per Anthropic skill-authoring guidance, no nested subdirs); ~25 institutional / rotating-author entries moved out of voice library to `docs/format-templates/` + `docs/register-references/`. `docs/voice-anchor-deep-dives/` folder removed (all pilot files migrated).

### Structural change

**Before (v1.5.x)**:
```
standards/
  {lang}-q{N}-anchors.md  (~300-500 lines each, 5-10 inline entries)
docs/voice-anchor-deep-dives/
  pilot-layer1-v2-*.md    (64 flat pilot files, Layer 1 v2 entries)
```

**After (v1.6.0)**:
```
standards/
  {lang}-q{N}-anchors.md  (~70-120 lines, router index per quadrant)
  anchor-{slug}.md        (67 flat per-entry voice anchor bodies)
  voice-anchor-meta-core.md + meta-detail.md  (unchanged)
  {jp,zh}-copy-craft-lineage.md  (unchanged)
  axis-extreme-anchors.md  (unchanged)
docs/format-templates/
  ~15 institutional / platform / wire format templates
docs/register-references/
  ~5 documented-movement / magazine register references
```

### Pass 3d two-step read protocol

1. Load `{lang}-q{N}-anchors.md` router → extract landmark-section listing
2. Match landmark position → load named `anchor-{slug}.md` file for full voice body

Token cost per Pass 3 read: router ~1K + anchor body ~1.2K ≈ 2.2K (comparable to v1.5.x landmark-targeted section read of ~1.5K).

### Migration scope

**Committed across 6 incremental commits on this PR**:
1. `5c3122f` zh-q3 pilot (6 anchors + 2 move-outs + router)
2. `b9b1c39` scaffolding cleanup (strip research-spec `(≥N)` / `(≥5, 中文)` etc. from 62 files)
3. `ad4ea8a` jp-q1 migration (2 + 4 move-outs + router)
4. `94b90af` jp-q2/q3/q4 migration (11 anchors + 3 move-outs + 3 routers)
5. `8b6bc68` zh-q1/q2/q4 migration (7 anchors + 10 move-outs + 3 routers)
6. `67f4c29` EN all 4 quadrants (31 anchors + EN institutional aggregate + 4 routers)

### Individual anchors by quadrant (67 total)

- **JP Q1**: 夏目漱石 / 伊丹十三 (2)
- **JP Q2**: 寺山修司 / 谷崎 / 川端 (3)
- **JP Q3**: 向田邦子 / 坂元裕二 / 谷川俊太郎 / 宮沢賢治 / 吉本ばなな / 梅田悟司 / 澤本嘉光 SoftBank-recast (7)
- **JP Q4**: ジャパネットたかた 高田明 (era-locked) (1)
- **JP craft-gate**: 糸井 / 岩崎 / 眞木 / 谷山 (4, additive to jp-copy-craft-lineage.md)
- **zh-HK**: 朱家鼎 Mike Chu / 王家衛 / KC Tsang (3)
- **zh canonical**: 錢鍾書 / 張愛玲 (2)
- **zh-TW Q2**: 白先勇 / 朱天文 (2)
- **zh-TW Q3**: 龔大中 / 吳念真 / 胡湘雲 / 黃春明 / 三毛 (5) + 金鵬遠 Durex (CN, 1) = 6
- **zh-TW craft-gate**: 許舜英 / 李欣頻 / 葉明桂 (3, additive to zh-copy-craft-lineage.md)
- **EN Q1**: Ogilvy / Puris / Hopkins / Bernbach / McPhee / Hemingway / Carver / Hempel / Strunk&White / Orwell (10)
- **EN Q2**: Lee Clow / Tim Delaney / Yvon Chouinard / Morrison / Baldwin / Ishiguro / Didion / Sorkin (8)
- **EN Q3**: Ephron / Allebach / Parvez / Waller-Bridge / Cessario / Saunders / Waititi / Gerwig / Dubin / Chekhov (10)
- **EN Q4**: Halbert / Jayme / Thompson / Chandler / Hammett / Lieberman (6)

### Move-out summary (~25 entries)

- **JP format-templates**: 天声人語 / 東洋経済+日経ビジネス / ロイター JP / 日経社説 / クックパッド / 通販生活 / ワークマン (7)
- **zh-TW format-templates**: 研之有物 / 故宮粉絲團 / e-commerce aggregate (PChome+MOMO+OPEN將+全聯 SNS+Shopee+Pinkoi) (3 files, 7 entries aggregate)
- **zh-TW register-references**: 天下雜誌 / 報導者 (center+extreme) / 商業周刊 / 台灣吧 (4)
- **EN aggregate**: WebMD/Reuters/Bloomberg + Economist + Amazon + REI + IKEA + Basecamp + Nike JDI + Nike Dream Crazy + XR + Absolut + MailChimp + Innocent + Oatly + Morning Brew (1 file, 14 entries aggregate)

### Remaining Phase B recast gaps → v1.7.0+

Individual-creator recasts that returned from Phase B research agents but were not persisted before session compaction, OR require additional research:

- 原研哉 (MUJI Q2), 太田恵美 (JR東海 Q2), 青木耕平 (北欧 Q4), 佐藤可士和 (UNIQLO Q4)
- Dan Wieden (Nike Just Do It Q2 / Dream Crazy Q2 extreme)
- David Abbott (AMV Economist Q1)
- Kate Kiefer Lee (Mailchimp Q3), Richard Reed (Innocent Q3)
- Richard Costello / Geoff Hayes (Absolut Q2 toward-Q1)
- Jason Fried + DHH (Basecamp Q1 toward-Q2 + Q4 center, dual-author audit)
- John Schoolcraft (Oatly Q2 toward-Q3 + Q3 center, audit)

Additional research gaps:
- zh-TW Q1 individual essayists (龍應台 / 南方朔 / 楊照 candidates)
- zh-TW Q4 individual DR tradition (genuinely thin — may remain cross-ref-only)

## v1.5.0 — 2026-04-21 (Phase B recasts + Phase C folder scaffolding + Phase D schema selector)

10 individual-creator recasts for previously institutional/brand/campaign anchors; new `docs/format-templates/` + `docs/register-references/` folders holding migrated-out entries; `voice-anchor-meta-core.md` v2 schema spec added alongside v1 (both coexist during migration); SKILL.md Pass 3d auto-detects schema version via frontmatter.

### Phase B — 10 Layer 1 v2 recast entries (all 5/5 pass)

Brand/campaign anchors recast to their named individual creators per `docs/anchor-schema-v2.md` inclusion criterion.

- 金鵬遠 (zh-CN/zh-TW Q3 extreme) — 杜蕾斯借勢文案 2011-2017 era lock (STRICT)
- 龔大中 (zh-TW Q3 center) — 全聯格言體 craft-gate
- Lee Clow (EN Q2 extreme) — visionary manifesto (Apple "1984" + "Think Different" + "Get a Mac" across 20+ year ECD tenure)
- Michael Dubin (EN Q3 toward-Q4) — DTC founder-spokesperson deadpan (Dollar Shave Club 2012 launch)
- 澤本嘉光 (JP Q3 center) — 白戸家世界観 (SoftBank 2007-)
- Tim Delaney (EN Q2 toward-Q1) — Patek Philippe stewardship register (1996- "Generations")
- Alex Lieberman (EN Q3 center) — Morning Brew peer-finance 2015-2020 era
- Mike Cessario (EN Q3 toward-Q4) — Liquid Death heavy-metal-water (2019-)
- Yvon Chouinard (EN Q2 toward-Q4) — Patagonia conscience register (Don't Buy This Jacket 2011 + Let My People Go Surfing)
- Martin Puris (EN Q1 extreme) — BMW engineering-precision (1975-1996 Ammirati & Puris tenure)

### Phase C — `docs/format-templates/` + `docs/register-references/` folder scaffolding

New non-anchor holding folders per `docs/voice-library-recast-audit.md` MOVE-OUT decisions:

- **`docs/format-templates/README.md`** — purpose, scope (magazines / newspapers / wire services / institutional platforms / SNS / IP mascots / e-commerce platforms / brand institutional voices), entries slated to migrate (天声人語, 東洋経済, Reuters JP, 日経社説, クックパッド, 通販生活, ワークマン, 研之有物, 故宮粉絲團, PChome, 7-ELEVEN OPEN 將, 全聯 SNS post-2020, Shopee, Pinkoi, Amazon, REI, IKEA), and rule that Pass 3 does NOT load these as voice anchors.
- **`docs/register-references/README.md`** — purpose, scope (documented movements / magazine institutional voices / campaign-level entries with rotating authorship), entries slated to migrate (XR Declaration, Economist brand voice, 天下雜誌, 報導者, 商業周刊, Nike "Dream Crazy"), and rule that these are mitigation-only references (anti-patterns for Dimension 6), not voice sources.

Actual entry-by-entry migration from v1 `standards/*-anchors.md` into these folders is progressive — entries move as Phase D refactors each `-anchors.md` file to v2 schema. v1 entries remain in place during migration window so Pass 3 still resolves them.

### Phase D — schema selector + Pass 3d auto-detect

- `voice-anchor-meta-core.md` adds **§Schema version selector** + **§v2 schema (Layer 1 purpose-centric, preferred going forward)** alongside the preserved §v1 schema. Both schemas coexist during migration; Pass 3 detects via `schema_version: 2.0` frontmatter.
- SKILL.md Pass 3d §Register-Signal apply updated: step 1 now includes schema auto-detect instructions + pointer to `docs/voice-anchor-deep-dives/pilot-layer1-v2-*.md` as the current v2 entry location; step 2 clarifies v2 entries carry their own over-mimic mitigation inline (the anchor file IS the single source of truth for v2), while v1 entries still use meta-core's legacy registry table.

Full `standards/*.md` replacement (v1 entries → v2) deferred to v1.6.0+; requires per-file rewrite for 14 anchor files and is substantial enough for its own release. Current v1.5.0 state: Pass 3 routes work against v1 standards (still 100% valid), v2 pilot entries are reachable by name via audit file, and schema selector is in place so the migration can proceed incrementally.

### Cumulative v2 state (after v1.5.0)

- **54 Phase A entries** (already-individual) +  **10 Phase B recasts** (institutional → individual) = **64 Layer 1 v2 entries** in `docs/voice-anchor-deep-dives/pilot-layer1-v2-*.md`
- 2 new holding folders (`format-templates/` + `register-references/`) with READMEs + migration lists
- Schema selector live: Pass 3 reads either v1 or v2 based on frontmatter
- v1 `standards/*-anchors.md` files unchanged — full migration incremental

### Still deferred (post-v1.5.0)

- **v1.6.0+**: per-`standards/*-anchors.md`-file rewrite replacing v1 entries with v2 structure; physically move MOVE-OUT entries into `format-templates/` + `register-references/` bodies (not just lists)
- **Phase B remainder (optional)**: 青木耕平 (北欧、暮らしの道具店), 佐藤可士和 (UNIQLO LifeWear), 謝政豪/蕭宇辰 (台灣吧), Richard Costello/Geoff Hayes (Absolut) — these are lower-priority and may stay as v1 entries until corpus justification
- **Cross-reference integrity sweep**: after v1.6.0 refactor, re-map `cross-reference-valid-for` links in meta-detail

## v1.4.5 — 2026-04-21 (Phase A batch 7 — 10 final entries, Phase A COMPLETE)

10 final Layer 1 v2 entries. All 5/5 pass. **Phase A migration complete** across the audit KEEP list of ~52 individual-creator anchors.

### Batch 7 (10 entries — larger than usual to close Phase A)
- Kazuo Ishiguro (EN Q2 toward-Q3) — restrained denial
- Phoebe Waller-Bridge (EN Q3 extreme) — Fleabag fourth-wall
- Aaron Sorkin (EN Q2 toward-Q1) — rhetorical rapid-fire (net-new entry)
- Taika Waititi (EN Q3 toward-Q2) — deadpan-absurd-warmth
- Greta Gerwig (EN Q3 toward-Q2) — ensemble intimacy
- Dashiell Hammett (EN Q4 toward-Q3) — terse procedural
- Anton Chekhov (EN Q3 toward-Q4) — compassionate realism (in translation)
- Ben Thompson Stratechery (EN Q4 toward-Q1) — peer-analytical framework-naming
- Nathan Allebach (EN Q3 extreme, 2017-2021 era lock) — Steak-umm Twitter
- Zaria Parvez (EN Q3 extreme, 2021-2022 era lock) — Duolingo TikTok

### Phase A complete — 54 Layer 1 v2 entries

**Cumulative coverage**:
- JP: 14 anchors (craft-gate 4/4 complete)
- zh-TW: 11 anchors (craft-gate 3/3 complete)
- zh-HK: 2 anchors
- EN: 27 anchors (Q1/Q2/Q3/Q4 all covered; includes authors, screenwriters, poets, copywriters, SM operators)
- 100% 5/5 coverage pass rate across all 54

**Creator types covered**:
- Authors / essayists / novelists / poets (22)
- Screenwriters / directors (8)
- Named copywriters (craft-gate) (10)
- Named CDs (creative directors) (5)
- Journalists / analysts (3)
- Individual SM operators (era-locked) (2)
- Author duo / creative partnership (2)
- Essayist + film director hybrid (1)
- Essayist + screenwriter hybrid (1)

**4 languages**: JP / zh-HK / zh-TW / EN

### Still deferred (Phase B-D, future versions)

- **Phase B** (v1.5.0+): recast ~20 institutional-to-individual candidates (原研哉 / 太田恵美 / 金鵬遠 / Kate Kiefer Lee / Richard Reed / Dan Wieden / David Abbott / Lee Clow / Mike Cessario / Michael Dubin / Alex Lieberman etc.)
- **Phase C** (v1.6.0): move ~25 institutional/brand/platform entries to `format-templates/` + `register-references/` folders
- **Phase D** (v1.7.0): Update `voice-anchor-meta-core.md` to v2 schema; update Pass 3 SKILL.md §Pass 3d to read v2 (or auto-detect schema_version); replace v1 `standards/*.md` content with v2 Layer 1 entries

## v1.4.4 — 2026-04-21 (Phase A batch 6 — 6 more Layer 1 v2 entries, EN-focused)

6 saved Layer 1 v2 entries from batch 6 (8 dispatched, 6 saved this commit; 2 under review). All 5/5 pass.

### Batch 6 saved (6 entries)
- Amy Hempel (EN Q1 toward-Q4) — compressed minimalism, Lish lineage
- George Orwell (EN Q1 toward-Q4) — political plain prose, 6 rules
- James Baldwin (EN Q2 toward-Q3) — sermonic cadence, Black-church periodic sentence
- Gary Halbert (EN Q4 extreme, craft-gate) — DR letter, Hopkins→Ogilvy→Halbert lineage
- Bill Jayme (EN Q4 extreme) — direct-mail seduction, envelope teaser discipline
- Nora Ephron (EN Q3 center) — warm-wit personal essay

### Cumulative v2: 44 Layer 1 entries (dispatched)

- JP: 14 anchors (craft-gate 4/4 + Q1/Q2/Q3/Q4 coverage)
- zh-TW: 11 anchors (craft-gate 3/3 + Q1/Q2/Q3 coverage)
- zh-HK: 2 anchors (Mike Chu + KC Tsang — already institutional moved-out, 2 kept individual)
- EN: 17 anchors (Q1/Q2/Q3/Q4 all major creators)

### Remaining KEEP audit (~10 EN)

- Kazuo Ishiguro / Phoebe Waller-Bridge / Aaron Sorkin / Taika Waititi / Greta Gerwig
- Dashiell Hammett / Anton Chekhov / Ben Thompson (Stratechery)
- Nathan Allebach / Zaria Parvez

### Still deferred

- No `standards/*.md` integration
- No `voice-anchor-meta-core.md` schema update
- No Pass 3 routing change

## v1.4.3 — 2026-04-21 (Phase A batch 5 — 8 more Layer 1 v2 entries)

8 additional Layer 1 v2 individual-creator entries, all native-language (no English-scaffold problem from v1.4.2 pilot entries).

### Batch 5 (8 entries)
- 吉本ばなな (JP Q3 extreme, author) — 大胆な省略 / J文学
- 伊丹十三 (JP Q1 toward-Q4, essayist + film director) — 軽妙洒脱
- 高田明 (JP Q4 extreme, TV shopping founder 1990-2015) — 2秒の間 / 序破急
- 白先勇 (zh-TW Q2 toward-Q1, author) — elegiac diaspora / 今昔之感
- 三毛 (zh-TW Q3 toward-Q2, author) — 流浪文學 / 任性宣告
- 胡湘雲 大眾銀行系列 (zh-TW Q3 center, named CD) — narrative TVC / 不平凡的平凡大眾
- Strunk & White (EN Q1 toward-Q4, author duo) — *The Elements of Style*, Ogilvy lineage
- George Saunders (EN Q3 toward-Q2, author) — compassionate absurd

### Cumulative v2: 36 entries, 100% 5/5 pass rate

- **JP craft-gate 4/4 complete**: 糸井 / 岩崎 / 眞木 / 谷山
- **zh-TW craft-gate 3/3 complete**: 許舜英 / 李欣頻 / 葉明桂
- **JP Q3 landscape** essentially complete: 向田 / 坂元 / 吉本 / 梅田 / 宮沢 / 谷川 (6 anchors)
- **zh-TW Q3 landscape** complete across positions: 吳念真 / 胡湘雲 center, 黃春明 / 三毛 toward-Q2
- **zh-TW Q2 landscape** complete: craft-gate + 張愛玲 / 朱天文 / 白先勇 / 錢鍾書 / 王家衛 / 朱家鼎
- **EN Q1 landscape** strengthened: Ogilvy / Bernbach / Strunk&White / McPhee / Hemingway / Carver / 漱石 (spans JP→EN parity)
- **EN Q2-Q3-Q4** key anchors: Didion / Morrison / Chandler / Hopkins / Saunders

### Remaining KEEP audit (~12 anchors)

- EN (~12): Amy Hempel / Orwell / James Baldwin / Kazuo Ishiguro / Phoebe Waller-Bridge / Aaron Sorkin / Taika Waititi / Greta Gerwig / Nora Ephron / Dashiell Hammett / Anton Chekhov / Ben Thompson (Stratechery) / Gary Halbert / Bill Jayme / Nathan Allebach / Zaria Parvez

### Still deferred

- No `standards/*.md` integration (v2 entries remain in docs/voice-anchor-deep-dives/)
- No schema update to voice-anchor-meta-core.md
- No Pass 3 routing change

## v1.4.2 — 2026-04-21 (Phase A batch 3 + 4 + language-consistency rewrite)

16 additional Layer 1 v2 individual-creator entries (8 batch 3 + 8 batch 4), plus language-consistency rewrite of 14 earlier entries whose Voice direction / Prose mechanics / Don't-Failure-mode / Mitigation sections were in English when the anchor's native language is JP or zh.

### Batch 3 (8 entries)
- 寺山修司 (JP Q2 extreme, poet/playwright) — documented lineage 寺山 → 李欣頻《誠品副作用》
- 許舜英 (zh-TW Q2 center, craft-gate) — power-disparity word rule, 意識形態廣告
- 李欣頻 (zh-TW Q2 center, craft-gate) — 具名引用 lineage preserved
- 葉明桂 (zh-TW Q2 center, craft-gate) — strategic gate before drafting; Z1 drift
- 川端康成 (JP Q2 toward-Q3) — sensory-ellipsis, 新感覚派
- 谷崎潤一郎 (JP Q2 toward-Q1) — shadow-aesthetic, 陰翳礼讃
- Bill Bernbach (EN Q1 toward-Q2, ECD craft-gate) — confession-before-claim
- John McPhee (EN Q1 toward-Q4) — longform precision

### Batch 4 (8 entries)
- 岩崎俊一 (JP Q3 center, craft-gate) — 余韻 / 無常、JP craft-gate 4 人完成
- 眞木準 (JP Q2 toward-Q3, craft-gate) — 諧謔×知性 deadpan、two-gate wordplay test
- 谷山雅計 (JP craft-gate) — 解決・意味提案, 3-reasons gate
- 錢鍾書 (zh Q2 toward-Q1) — 博喻, 學者型小說家
- 黃春明 (zh-TW Q3 toward-Q2) — 鄉土文學, humane vernacular
- Claude Hopkins (EN Q4 center, craft-gate) — Ogilvy lineage "read seven times"
- Toni Morrison (EN Q2 toward-Q3) — the-ancestor, lyrical inheritance
- Raymond Carver (EN Q1 toward-Q4) — working-class precision, Hemingway descendant

### Language-consistency rewrite (14 entries affected)

User flag: anchor entries must describe themselves in the anchor's **native language**, not in English. Applied native rewrite (not translation) to Voice direction / Prose mechanics / Don't Failure mode / Mitigation sections for:

JP anchors: 坂元裕二 / 梅田悟司 / 宮沢賢治 / 糸井重里 / 寺山修司 / 岩崎俊一 / 眞木準 / 谷山雅計

zh-HK / zh-TW anchors: 朱家鼎 Mike Chu / 曾錦程 KC Tsang / 研之有物 / 故宮粉絲團 / 許舜英 / 葉明桂

What stays English (intentional):
- Schema section labels (Voice direction / Prose mechanics / Examples / Metadata)
- Metadata enums (Trigger slug / Over-mimic risk / Pairs with form / Cross-reference-valid-for) for machine-readability
- Enum values (HIGH / MEDIUM / LOW / STRONG / WEAK)

### Cumulative v2 progress

- Total Layer 1 v2 entries: **28** (pilot 4 + batch 2-4 × 8 each)
- Creator types covered: essayist / novelist / poet / screenwriter / director / craft-gate copywriter / craft-gate CD / journalist / hardboiled author
- Languages: JP / zh-HK / zh-TW / EN
- **100% full pass rate (28/28 at 5/5 coverage)** — Schema v2 empirically validated across wide spread of creators

### JP / zh craft-gate tier fully covered

- **JP craft-gate masters (4/4)**: 糸井重里 / 岩崎俊一 / 眞木準 / 谷山雅計 — all Layer 1 v2
- **zh-TW craft-gate masters (3/3)**: 許舜英 / 李欣頻 / 葉明桂 — all Layer 1 v2

### Still deferred

- No `standards/*.md` integration (v2 entries remain in docs/voice-anchor-deep-dives/)
- No schema update to voice-anchor-meta-core.md
- No Pass 3 routing change
- ~20 audit KEEP individual anchors remaining (JP Hemingway-descendants, zh-TW 白先勇/三毛/胡湘雲, EN Hempel/Strunk&White/Orwell/Baldwin/Ishiguro/Waller-Bridge/Saunders/Waititi/Gerwig/Chekhov/Ephron/Halbert/Jayme/Thompson/Hammett/Allebach/Parvez etc.)

## v1.4.1 — 2026-04-21 (Phase A batch 2 — 8 Layer 1 v2 individual-creator entries)

Eight additional individual-creator voice anchor entries researched + formatted to Layer 1 v2 schema. All 8 hit full 5/5 coverage under refined research-agent prompt with hard rules (no bio, no structural, ≥5 verbatim, native vocab, ≥5 mechanics).

### Batch 2 deliveries

Cross-culture / cross-type coverage (eight individual creators):

| Anchor | Culture | Quadrant | Creator type |
|---|---|---|---|
| 谷川俊太郎 | JP | Q3 extreme | poet |
| 王家衛 Wong Kar-wai | zh-HK | Q2 extreme | screenwriter/director |
| 吳念真 | zh-TW | Q3 center | named CW + VO + director |
| 朱天文 | zh-TW | Q2 toward-Q3 | novelist + screenwriter |
| David Ogilvy | EN | Q1 center | named copywriter (craft-gate) |
| Ernest Hemingway | EN | Q1 toward-Q4 | author |
| Raymond Chandler | EN | Q4 toward-Q3 | author |
| 夏目漱石 | JP | Q1 toward-Q2 | author |

### Cumulative v1.4.0 + v1.4.1 Layer 1 v2 entries

12 individual-creator anchors fully documented at Layer 1 v2:
- Round 1 (v1.4.0): 向田邦子 / 張愛玲 / Joan Didion / 糸井重里
- Round 2 (v1.4.1): 谷川俊太郎 / 王家衛 / 吳念真 / 朱天文 / Ogilvy / Hemingway / Chandler / 夏目漱石

**12/12 = 100% 5/5 coverage pass rate**. Schema v2 validated across 7 creator types and 4 languages (JP / zh-HK / zh-TW / EN).

### Per-entry refinements beyond meta-core over-mimic registry

- Hemingway: added "4-turn tag-less cap" (beyond registry's 2) + "named-physical-object discipline" (addresses generic-object vague nouns)
- Chandler: suggested registry upgrade — "cap similes to 1 per scene; single adjectives only; no abstract emotional nouns in narrator voice; aphorism once per chapter max" (beyond existing "1 per 50 words")
- 王家衛: refined to "三件套替代形容詞堆疊" rule (addresses 形容詞堆疊 specific failure)
- 吳念真: added 勿堆鄉愁形容詞 anti-kitsch guard
- 夏目漱石: 3-sub failure mode (archaic 文末 / 一方向 snark / 漢語羅列 misread)

### Observations for Phase A (continued)

- Research-agent prompt v2 is stable across 8 parallel independent dispatches — hard rules consistently respected
- Zero attribution bugs surfaced in batch 2 (batch 1 surfaced Mike Chu / KC Tsang split + 康熙 / 雍正 correction)
- Copywriter mechanics cluster observation (糸井 from v1.4.0) holds: Ogilvy also clusters in 4 families (punctuation / elision / specificity / structure-doctrine). Non-copywriter anchors span wider
- `pairs_with_form` continues to hint at Phase 4 form taxonomy refinement needs (Ogilvy: long-form-pasona + long-form-extended + mid-form)

### Still deferred to later versions

- No actual `standards/*.md` integration yet (Layer 1 v2 entries remain in `docs/voice-anchor-deep-dives/` as pilots)
- No `voice-anchor-meta-core.md` schema update
- No Pass 3 SKILL.md routing change
- No format-templates/ / register-references/ directory created
- ~40 individual-creator anchors remaining in audit KEEP list

## v1.4.0 — 2026-04-21 (Anchor Schema v2 — purpose-centric, individual-creator-only)

Major rethinking of anchor content design. v1.3.x schema was researcher-catalog-centric (Era / Agency / Primary sources / Representative lines / Voice signature / Over-mimic / Cross-ref / Trigger slug), mixing three readers' needs in one bullet list. v2 splits into layers, keeps only **Layer 1 inside skill**, moves Layer 2/3 (biographical / agency / awards / provenance) to `docs/voice-anchor-deep-dives/` as research artifacts.

### Design principle change

**Anchor file content = what Pass 3 copywriter agent needs to rewrite a draft in this voice, and nothing else.**

### Inclusion criterion (new)

An entity qualifies as a voice anchor IF AND ONLY IF it is an **individual creator** whose sentence-level register is identifiable across a body of work:
- Authors / novelists / essayists / screenwriters / poets
- Named copywriters with craft-gate signature
- Named creative directors with recognizable craft across multiple campaigns

Disqualifying types (move to `format-templates/` or `register-references/`):
- Magazines / newspapers / wire services with rotating authors
- Institutional platforms / SNS / IP / brand mascots
- Brand house-style guides without a single named author
- E-commerce platforms with distributed authorship
- Campaign-level entries without clear individual authorship
- Documented movements / genres

### Schema v2 Layer 1 (what ships in skill)

```markdown
### {anchor} ({culture} | {quadrant} {landmark})

## Voice direction
**What this register achieves**: {1 sentence}
**Native critical read** (≥3, attributed verbatim): ...

## Prose mechanics (≥5, sentence-level voice rules only)
- ...

## Examples (≥5 verbatim from ≥2 works)
- ...

## Don't / Over-mimic
- Failure mode: ...
- Mitigation (≤15 words): ...

## Metadata
- Trigger slug / Over-mimic risk / Pairs with form (list) / Cross-reference
```

### Delivered in v1.4.0

1. **`docs/anchor-schema-v2.md`** — full schema spec + inclusion criterion + recast rules
2. **`docs/voice-library-recast-audit.md`** — 105 anchors classified: ~52 KEEP as-is individual / ~20 RECAST institutional-to-individual / ~25 MOVE-OUT (format-templates/register-references)
3. **`docs/anchor-schema-v2-pilot-findings.md`** — two rounds of pilot results
4. **8 Round-1 pilot entries** (`pilot-layer1-*.md`) — mixed individual + institutional; surfaced the structural-contamination problem
5. **4 Round-2 pilot entries** (`pilot-layer1-v2-*.md`) — individual-creator only; 100% 5/5 full pass:
   - 向田邦子 (JP Q3 center, essayist + screenwriter)
   - 張愛玲 Eileen Chang (zh Q2 toward-Q3, novelist + essayist)
   - Joan Didion (EN Q2 toward-Q3, essayist + novelist; net-new entry)
   - 糸井重里 (JP Q3 center, craft-gate master named copywriter)

### What did NOT ship in v1.4.0

- No changes to `standards/*.md` (v1.3.x entries preserved)
- No changes to `voice-anchor-meta-core.md` anchor schema spec
- No changes to Pass 3 SKILL.md routing
- No movement of institutional entries out (deferred to Phase C)

**Rationale**: v1.4.0 is pilot + design artifact. Actual migration of ~52 individual-creator anchors begins in v1.4.1+ (Phase A). This preserves v1.3.6 functionality unchanged while the design is validated.

### Key schema insights surfaced during pilots

1. **Biographical/structural content contaminates Prose mechanics in v1 schema** — 5+ of 8 Round-1 entries had "4-sentence contract", "byline 三欄制", "週循環 SOP", "T字型思考法", "historical-event anchoring", etc. — these are Phase 4 (framework) territory, not Phase 6 (voice) territory. Cleanly separated in v2.
2. **Institutional anchors often cannot produce ≥5 voice-level mechanics** — 研之有物 after purification had only 3 voice mechanics (hedging preservation / 擬人 subhead / 嘆號 frequency). Rest was attribution protocol / structural template.
3. **Individual creators produce ≥5 voice mechanics cleanly** — all 4 Round-2 entries hit 7.
4. **Copywriter mechanics cluster** (糸井 insight): copywriter anchors gravitate to 4 families (punctuation / elision / register / mora). Acceptable but worth monitoring.
5. **Phase 4 form taxonomy may need refinement** — 糸井 `pairs_with_form` proposed `short-form-catchcopy` / `mid-form-brand-tagline` / `light-action-lifestyle` not currently in Phase 4 enum.

### Phase plan (v1.4.1+)

- **Phase A** (v1.4.1-v1.5.0): migrate ~48 remaining individual-creator anchors via parallel research-agent batches
- **Phase B** (v1.5.x): recast ~20 institutional-to-individual candidates (原研哉, 太田恵美, 金鵬遠, Kate Kiefer Lee, Richard Reed, Dan Wieden, David Abbott, etc.)
- **Phase C** (v1.6.0): move ~25 institutional / brand / platform entries to `format-templates/` + `register-references/`
- **Phase D** (v1.7.0): Update `voice-anchor-meta-core.md` to v2 schema; update Pass 3 SKILL.md Pass 3d to read v2; delete v1 schema compatibility shims

## v1.3.6 — 2026-04-21 (Revert `anchor_marginal_value` — premature optimization)

Removes the `anchor_marginal_value` schema field added in v1.3.5 Item 3. Decision: the field was a typed slot for future Pass 3 skip-on-LOW optimization (estimated savings ~1.7% of total pipeline tokens), but:

- v1.3.5 shipped it unpopulated (all 105 anchors marked `unevaluated`), creating fabrication pressure
- Populating properly requires ~$50 + 3 hours of cross-model-judge automation (Tier 1 pipeline designed but not built)
- Skip-on-LOW saves ~1.7% cost but carries maintenance overhead (field documentation, Pass 3 branching, evidence standard enforcement)
- Alternative observability already in place: `docs/voice-anchor-e2e-tests/` regression baseline + Dimension 6/7 gates + `cw_toolkit` CHANGELOG per-run token estimates

Net: a field that doesn't pay for its upkeep yet. Removed to reduce schema entropy. If Pass 3 token cost becomes an observed bottleneck, reintroduce alongside a built Tier 1 evaluation pipeline.

### Changes

- `voice-anchor-meta-core.md` — removed `anchor marginal value` row in anchor entry schema + field semantics table + entire `§anchor_marginal_value semantics` section
- `docs/voice-anchor-e2e-tests/findings-apply-rewrite.md` — updated pending-work bullet to note revert rationale
- No anchor file content changed
- No SKILL.md / gate rubric / Pass 3 logic changed (v1.3.5 already specified field was read-only, no skip-logic was ever wired)

### Retained from v1.3.5

- Item 1 (`anchor_candidates_ranked[]` output) — kept
- Item 2 (Pass 3 thesis-conflict self-check) — kept
- Item 3 (`anchor_marginal_value` field) — **reverted**

## v1.3.5 — 2026-04-21 (Pass 3 transparency + thesis self-check + marginal-value schema stub)

Three small improvements folded in after v1.3.4 e2e testing, each addressing a specific gap surfaced during the apply-rewrite round. Token cost estimate: +2-4% per pipeline run short-term, +1-2.6% long-term once `anchor_marginal_value` populates.

### Item 1 — Pass 3 ranked candidates output schema

`tone_notes.register_signal_applied` now includes `anchor_candidates_ranked[]` (top-3) + `primary_anchor_slug` (rank 1) instead of a single anchor slug. Surfaces Pass 3's interpretation space — the same brief across runs may legitimately select different primaries, but the candidate set should stabilize. Downstream reviewers and regression audits can see the alternatives.

**Motivation**: v1.3.x e2e tests showed the same zh-TW Q3 brief picked different primary anchors across runs (Test 02 → 吳念真; Apply A2 → 全聯). Not a bug, but was being swallowed by single-slug output schema.

### Item 2 — Pass 3 thesis-conflict self-check

Pass 3d adds a self-check step BEFORE emitting polished draft: scan rewrite for spans reintroducing concepts `envelope.message_thesis` explicitly negates. If detected, revise (drop conflicting imagery, keep anchor cadence / discipline). Records outcome in `thesis_self_check: clear | revised_once | escalate`. Escalate cases flow to Dimension 7 gate for terminal catch.

**Motivation**: Documented failure mode (v1.3.4 Dimension 7) where anchor register pulled rewrite into thesis-violating imagery (zh-TW Q3「不是懷舊」thesis + anchor reintroduced 放學路上 nostalgia). Self-check at Pass 3 = defense in depth; Dimension 7 remains the terminal gate.

### Item 3 — `anchor_marginal_value` schema field (stub, unpopulated)

New optional field in meta-core anchor schema: `HIGH / MEDIUM / LOW / unevaluated`. Concept: some anchors make drafts distinctly different from no-anchor baseline (HIGH — e.g. 向田邦子 ト書き); others produce cadence changes but similar structural shape (MEDIUM); others are swamped by the quadrant baseline (LOW — e.g. zh-TW Q3 peer-warm generic).

**v1.3.5 does NOT populate values** on any existing anchor — all default to `unevaluated`. Schema field is added now to prevent drift when future iterations fill in data from apply-rewrite test rounds.

**Future use (not v1.3.5)**: Pass 3 may skip anchor load for LOW-marginal anchors to save ~1.5K tokens per Pass 3 invocation. Not activated yet — needs enough populated values to justify the branch.

**Meta-note on evidence standards**: values MUST come from apply-rewrite A/B evidence (baseline vs anchor-applied draft pair); NOT from rationale-only tests or `native_critical_vocab_cited` count (v1.3.3 A/B showed vocab count is a misleading proxy).

### No regressions

- Existing `tone_notes.register_signal_applied` consumers continue to work — `primary_anchor_slug` is the new name for what was `anchor_slug`; downstream reads may need an additive alias (kept in v1.3.5 CHANGELOG as a known touchpoint; callers should adopt `primary_anchor_slug` going forward)
- No anchor file content changed
- No Pass 3 routing / tier precedence changed
- Gate dimensions 1-7 behavior unchanged
- `anchor_marginal_value` read-only in v1.3.5 — no skip-logic activates

### Token cost impact (estimated)

Baseline per-pipeline-run (v1.3.2 reference): ~26K tokens.

| Change | Per Pass 3 cost | Per pipeline run (Pass 3 fires ~80%) |
|---|---|---|
| Item 1 candidates_ranked | +200-500 | +160-400 |
| Item 2 thesis self-check (incl. 15% revise rate) | +275 weighted avg | +220 |
| Item 3 marginal_value stub | +50-100 | +40-80 |
| **Aggregate short-term** | +525-1000 | **+420-800 (~+1.6-3.1%)** |
| **Aggregate long-term** (once marginal_value populates and Pass 3 skips LOW) | +175-600 | **+140-480 (~+0.5-1.8%)** |

All within CLAUDE.md §Verification Density Principle 5% marginal-cost ceiling.

## v1.3.4 — 2026-04-21 (Voice Consistency Dimension 7 — Thesis Alignment + e2e test artifacts)

Empirical outcome from first end-to-end pipeline tests of the v1.3.x anchor library. Test harness in `docs/voice-anchor-e2e-tests/` shipped as artifacts so future iterations have a regression baseline. One concrete bug surfaced → Dimension 7 added to Voice Consistency gate.

### What changed

- **Rubric `rubrics/voice-consistency-gate.md` — Dimension 7 (RUB-CTW-VC-007) added**: catches anchor-induced drift from `envelope.message_thesis`. Scope: applies only when Pass 3 ran AND thesis is non-empty. Fires 🔴 when Pass 3 output reintroduces a concept the thesis explicitly negated, or undermines an assertion. Remediation pattern documents "anchor register must serve thesis; drop conflicting imagery, keep cadence / discipline only".
- **SKILL.md gate reference updated** to list Dimension 7 alongside 5 / 6.
- **Docs folder `docs/voice-anchor-e2e-tests/`**: README + 4 initial test specs + findings from Pass 3 rationale tests + findings from apply-rewrite tests. Preserves concrete before/after draft pairs for 2 briefs (zh-TW Q3 center / JP Q3 center).

### Empirical finding that drove Dimension 7

zh-TW Q3 brief with thesis「古早味不是懷舊，是我們今天還在過的日常」→ Pass 3 applied 全聯 格言體 + 吳念真 stance anchors → polished draft contained「放學路上那個沒什麼煩惱的下午」— a nostalgic frame the thesis explicitly rejected. Anchor register was pulling the rewrite toward register-canonical imagery (身體感官的懷舊記憶) that felt right stylistically but violated the argument. No existing gate dimension caught this (D1-D5 check voice coherence not argument; D6 checks registered over-mimic tropes not thesis).

### Empirical findings NOT fixed this version (recorded for future iteration)

- **Anchor ROI varies with register distinctiveness** — JP Q3 (向田 ト書き register) → large shape change; zh-TW Q3 center →细微 delta (generic peer-warm quadrant). Suggests future `anchor_marginal_value: HIGH/MEDIUM/LOW` field in meta-core so Pass 3 can skip anchor load when marginal value is LOW. Not shipped this version — needs dedicated design pass.
- **Anchor selection non-deterministic** — same brief, same pipeline, different Pass 3 invocations can select different primary anchors (Test 02 chose 吳念真; Apply A2 chose 全聯). Legitimate interpretation space but should be surfaced via `anchor_candidates_ranked[]` rather than single-slug output. Not shipped — schema change deferred.
- **Native-reviewer blind evaluation not performed** — all analysis in this version is self-inspection. Real TW/JP copywriter blind rating of baseline-vs-applied drafts is the missing ground truth.

### No regressions

- No anchor file content changed
- No routing / envelope / Pass 3 load logic changed
- Existing dimensions 1-6 behavior unchanged
- `not_applicable` scoping preserved for Dimensions 3 / 5 / 6 / 7

## v1.3.3 — 2026-04-21 (JP + zh-TW anchor native-source vocabulary rewrite)

Content-layer polish: replaced English-translated voice signatures with native critical vocabulary researched from primary sources (JP: Wikipedia JA / 宣伝会議 / 朝日新聞 / 岩波 / 学術紀要 / author's own books; zh-TW: 動腦 / 數位時代 / 小魚廣告網 / 中央社文化 / 機構自述 / 學界批評).

Previous anchor files had English-structured signatures with native names pasted in — this version reads like TW/JP critics actually write. No schema changes; no lineage changes; no over-mimic-registry changes.

### What changed

- **8 files rewritten**: `jp-q{1,2,3,4}-anchors.md` + `zh-q{1,2,3,4}-anchors.md`
- **Schema labels stay EN**: Era / Agency / Primary sources / Voice signature / LLM corpus depth / Over-mimic risk / Cross-reference-valid-for / Trigger slug — consistency with meta-core
- **Enum values stay EN**: DEEP / MEDIUM / HIGH / STRONG / WEAK
- **Trigger slugs stay kebab-case machine-readable**
- **Voice signature bullets use native critical terms** actually used by TW/JP critics, agency self-descriptions, and academic 批評

### Critical attribution corrections (research agent flags)

- **JR東海「そうだ 京都、行こう。」** main copywriter corrected from 一倉宏 → **太田恵美**（CD: 佐々木宏）per JP research agent flag against Wikipedia JA + 宣伝会議 archive
- **報導者 extreme vocab** corrected「血淚調查」→「公共領域調查報導 / 時間成本／半年一篇 / 不受廣告業主干預」per zh research agent flag (「血淚」is not native critical vocabulary for 報導者 register)

### Representative native vocabulary applied

JP:
- 糸井重里 lineage references now cite「状態提案」(自稱)、「ほぼ日」(媒體自稱)
- 宮沢賢治「心象スケッチ」(自稱ジャンル名)、「非慣習的オノマトペ」(田守育啓 論文定式化)
- 谷川俊太郎「詩のことば」≠「伝達のことば」(谷川 自述, ほぼ日)
- 坂元裕二「言葉の魔術師」(BuzzFeed 2017 見出し定着)、「余白」(神戸大学紀要)
- 吉本ばなな「大胆な省略」(辻井喬 書評)、「J 文学」(1990s 批評標識)

zh-TW:
- 天下雜誌「積極、前瞻、放眼天下」(殷允芃自述 DNA)
- 報導者「三不原則」(不擁有、不干預、不回收)、「自己的新聞自己救」(何榮幸 創辦宣言)
- 研之有物「言之有物」(命名出處《周易·家人》)
- 吳念真「氣口」(台語 CW 術語、吳本人用語)
- 胡湘雲「不平凡的平凡大眾 / 真人真事改編」(campaign 自述)
- 故宮「讓歷史走進生活 / 故宮小編 / 古物擬人化」
- 台灣吧「知識娛樂化 / 幹話體」
- 黃春明「鄉土文學」(1970s 鄉土文學論戰 canonical 學界術語)
- 三毛「流浪文學」(自述 genre)
- 錢鍾書「博喻 / 打通 / 學者型小說家」(錢自創 + 學界沿用)
- 張愛玲「蒼涼 / 參差的對照」(張自述美學、《自己的文章》)
- 朱天文「世紀末 / 物質書寫」(批評定型語)

### Rationale

Original v1.3.0-v1.3.2 anchor content was generated by translating English critical analyses of these voices into English-with-zh/jp-character-names. That structure doesn't match how TW/JP critics actually write about these voices natively, and Phase 6 Pass 3 anchor rationale output read as "outsider translation". Research agents working in JP-Wikipedia / CNA 文化 / 動腦 / 宣伝会議 / 神戸大学紀要 / 岩波 etc. surfaced the actual critical vocabulary circulating in each tradition. Rewriting ensures voice-reference rationale in envelope.audit_trail matches what a native-language copywriter would cite.

### No regressions

- Tier 1 (Craft Gate) unaffected — craft-lineage files unchanged
- Tier 3 (Axis Extreme) unaffected — placeholder unchanged
- Meta-core / meta-detail / gate rubric unchanged
- Pipeline routing unchanged
- Envelope contract unchanged
- `voice_quadrant.position` field behavior unchanged

## v1.3.2 — 2026-04-21 (EN anchor content + Pass 3 3-tier refactor + position field + gate rubric)

PR 3 of 3 for voice anchor library expansion. Completes EN content population AND wires up the register-signal + axis-extreme branches in Phase 6 Pass 3. Adds `voice_quadrant.position` optional envelope field + gate rubric over-mimic adherence dimension.

### EN content populated (4 files × 4 landmarks = 16 sections)

- `en-q1-anchors.md` — Ogilvy Rolls-Royce/Hathaway + Abbott Economist + BMW Ultimate (center) + Economist brand voice + wire cluster + Hopkins Scientific (extreme) + Bernbach DDB (**LINEAGE VERIFIED** with Strunk & White per meta-detail) + Basecamp manifesto (toward-Q2) + McPhee/Hemingway/Carver/Hempel/Strunk&White/Orwell (toward-Q4)
- `en-q2-anchors.md` — Apple Think Different + Nike JDI + Patagonia Don't Buy (center) + XR Declaration (civic-only mitigation) + Nike Dream Crazy/Crazier (anaphoric cap mitigation) [extreme] + Patek Generations + Absolut (toward-Q1) + Oatly activist + Morrison/Baldwin/Ishiguro/Didion edge (toward-Q3)
- `en-q3-anchors.md` — MailChimp Voice & Tone + Innocent wackaging (with cliché flag) + Oatly center + Ephron (center) + Steak-umm Allebach + Duolingo Parvez 2021-22 (STRICT era flag) + PWB Fleabag + Liquid Death (extreme) + Saunders/Waititi/Gerwig (toward-Q2) + Dollar Shave Club/Chekhov (toward-Q4)
- `en-q4-anchors.md` — Amazon/REI/Basecamp Rework/IKEA (center) + Gary Halbert Boron Letters + Bill Jayme (Type 5 PROMOTE per research) + Hopkins (extreme) + Morning Brew/Stratechery (toward-Q1) + Chandler hard-boiled + Hammett (toward-Q3)

### Phase 6 Pass 3 load logic — 3-tier branching

Upgraded v1.2.0's single "craft gate" path to 3-tier:

1. **Tier 1 — Craft Gate** (preserved v1.2.0 behavior): voice_reference ∈ {6 canonical masters} → load jp/zh-copy-craft-lineage.md + voice-anchor-meta-core.md
2. **Tier 2 — Register Signal** (NEW v1.3.2): default Pass-3-triggered case → load meta-core + meta-detail + `{lang}-q{N}-anchors.md` (landmark-targeted section read per voice_quadrant.position); cross-language STRONG triggers additional quadrant file load
3. **Tier 3 — Axis Extreme** (NEW v1.3.2, MVP): voice_quadrant.position starts with "axis-*" → load meta-core + axis-extreme-anchors.md

Tier precedence: Craft Gate > Axis Extreme > Register Signal.

### `voice_quadrant.position` optional envelope field

Added to `copywriting-voice-quadrant-stage/SKILL.md` I/O contract. Values:
- `center` (default fallback) / `extreme` / `toward-Q{1-4}` / `axis-{authority,affinity,reason,emotion}-extreme` / `null`

Phase 5 diagnosis derives position when intensity signal is strong in brief; fallback to `center` when absent. Cross-adjacency rule: Q1 may go toward-Q2 or toward-Q4 (axis-sharing); diagonal (Q1 toward-Q3) forbidden.

### Voice Consistency gate — Dimension 6: Over-Mimic Adherence

`rubrics/voice-consistency-gate.md` adds Dimension 6 (RUB-CTW-VC-006). Scope: applies ONLY when Pass 3 Register Signal or Axis Extreme branch activated AND anchor is registered in meta-core over-mimic registry.

Checks output for leaked tropes per mitigation clauses covering 20 anchors. Verdict contributions:
- 🔴 Fatal: mitigation violated with load-bearing leaked trope
- 🟡 Warning: minor mitigation leakage (≤2 sentences)
- 🟢 Clear: all applicable mitigations respected
- `not_applicable`: anchor not in registry

### Token cost analysis (v1.3.2 post-refactor)

Pass 3 load logic now matches the 4-optimization plan:
- No-Pass-3 runs (~10% briefs): no meta load — ~20K tokens (down from 25K pre-refactor)
- Craft Gate (~20% briefs): meta-core only + lineage — ~25-27K (baseline ~24K)
- Register Signal (~40% briefs): meta-core + meta-detail + quadrant section — ~26.5K
- Register Signal cross-lang (~20% briefs): +additional quadrant file section — ~28.5K
- Axis Extreme (~5% briefs): meta-core + axis-extreme placeholder — ~24K
- Weighted per-run avg: **~26K** (+18% vs baseline, -9% vs original plan without optimizations)

### Documented lineages now load-bearing in pipeline

- Ogilvy → Strunk & White (referenced in en-q1 center entries)
- 糸井重里 → 谷川俊太郎 (referenced in jp-q3 extreme entries)
- 李欣頻 → 寺山修司 / 阿莫多瓦 / 徐四金 / 村上春樹 (referenced in zh-q2 + jp-q2 center/extreme entries)
- 葉明桂 / 台灣奧美 → Peter Altenberg (referenced in zh-q2 center drift correction)

### What's next (post-v1.3.2 backlog)

- V2 axis-extreme research (BBC/NHK/Reuters for authority-extreme; Mailchimp help/Reddit for affinity-extreme; Wikipedia/Stratechery for reason-extreme; Hallmark/cinematic-MV for emotion-extreme)
- Phase 7/8 meta-core dependency audit (Option 4 full-benefit — currently meta-core always loaded by Pass 3; if Phase 8 8b doesn't need it, can be further lazy)
- Cross-cultural label matrix orphans (monologue-fragment-temporal JP/EN candidates)

---

## v1.3.1 — 2026-04-21 (JP + zh-TW anchor content + drift corrections Z5-Z11)

PR 2 of 3. Populates JP + zh-TW per-quadrant anchor inventory (8 files × 4 landmarks = 32 landmark sections). Applies Z5-Z11 drift corrections to existing zh-copy-craft-lineage.md + new zh-q2/zh-q3 inventory entries.

### Files changed

**Drift correction** (existing Tier 1 toolkit-originated):
- `zh-copy-craft-lineage.md` — added Z5-Z8 drift corrections to §Critical Attribution Corrections:
  - Z5: 多喝水 ≠ 吳念真 (奧美 in-house)
  - Z6: 孫大偉 agency = 台灣奧美 / 偉太 (NOT JWT)
  - Z7: 長榮〈I SEE YOU〉VO = 金城武 (NOT 吳念真)
  - Z8: 全聯經濟美學 creative lead = 龔大中 (NOT 林敬凱; 邱彥翔 is actor)
  - (Z11 covered by existing Z3: 意識形態 founders = 許舜英 + 鄭松茂)

**JP quadrant inventory (populated)**:
- `jp-q1-anchors.md` — 朝日天声人語 (center) + 東洋経済/日経ビジネス (center) + Reuters JP/日経社説 (extreme with intl-wire caveat) + 夏目漱石 (toward-Q2) + 伊丹十三 (toward-Q4)
- `jp-q2-anchors.md` — MUJI 原研哉 (center) + JR東海 そうだ京都 (center) + 寺山修司 (extreme, LINEAGE VERIFIED with 李欣頻) + 谷崎《陰翳礼讃》(toward-Q1) + 川端康成 (toward-Q3) + craft-gate pointers to 糸井/岩崎/眞木/秋山
- `jp-q3-anchors.md` — 向田邦子 + 坂元裕二 (center) + 谷川俊太郎 (extreme, LINEAGE VERIFIED with 糸井) + 宮沢賢治 + 吉本ばなな (extreme) + 梅田悟司 Georgia (toward-Q2)
- `jp-q4-anchors.md` — クックパッド + Kurashicom Q4-subset (center, with Q3/Q4 boundary warning) + ジャパネットたかた 高田明 1990-2015 founder (extreme) + 通販生活 + UNIQLO LifeWear (toward-Q1) + ワークマン SNS (toward-Q3)

**zh-TW quadrant inventory (populated)**:
- `zh-q1-anchors.md` — 天下雜誌 + 報導者 center register + 研之有物 (center) + 報導者 investigative (extreme, Q1-Q2 edge flag) + 商業周刊 (toward-Q4); Q1-toward-Q2 gap flagged for V2
- `zh-q2-anchors.md` — 中興百貨/誠品/左岸 brand-era pointers to craft-gate (center) + **朱家鼎 KC Tsang** 鐵達時 HK (extreme, **Z9 correction applied**: KC Tsang NOT Calvin Choy; BBDO NOT JWT) + 王家衛 (extreme, per meta-core over-mimic mitigation) + 錢鍾書 圍城 + 白先勇 (toward-Q1) + 張愛玲 (toward-Q3, stylistic parallel to 許舜英 flag) + 朱天文 侯孝賢 lineage
- `zh-q3-anchors.md` — **全聯 TV-era 2006-2014 格言體 (center, Z10 re-classification)** + 吳念真 保力達B (Z5/Z7 inline) + 胡湘雲 大眾銀行 (center) + 故宮「朕知道了」+ 台灣吧 + 杜蕾斯 CN cross-pollination (extreme) + 黃春明 + 三毛 (toward-Q2)
- `zh-q4-anchors.md` — PChome/MOMO/7-ELEVEN OPEN 將 (center) + 全聯 SNS post-2020 (extreme, distinct from TV-era Z10) + 蝦皮 雙11 + Pinkoi designer-story (toward-Q3) + JP Q4 heavy cross-ref (native corpus thin)

### Critical drift corrections surfaced in active inventory

- **Z9 (applied in zh-q2-anchors.md)**: HK CD name = **KC Tsang** (NOT Calvin Choy, unrelated finance YouTuber); agency path = **BBDO HK ECD 1998** (NOT JWT). Per [曾錦程 Wikipedia zh-HK](https://zh.wikipedia.org/zh-hant/曾錦程) + ISBN 9621780233 + ISBN 9888488279.
- **Z10 (applied in zh-q3-anchors.md)**: 全聯 TV-era 2006-2014 re-classified as **Q3-CENTER** (格言 / aphorism register), NOT Q3-extreme. Q3-extreme reserved for peer-intimate voices (故宮 / 台灣吧) where brand speaks as friend-at-2am. 對仗結構「本錢 / 本事」is aphoristic discipline, not peer-intimate.
- **Stylistic parallel flag (張愛玲 / 許舜英)**: marked as "critical-consensus stylistic parallel, NOT documented citation" per meta-detail §Inferred parallels.

### Documented lineages applied

Two craft-gate master lineages referenced via verified meta-detail map:
- 糸井重里 → 谷川俊太郎 (cross-linked in jp-q3 extreme landmark)
- 李欣頻 → 寺山修司 (cross-linked in jp-q2 extreme landmark via meta-detail verified map)

### Token cost

Pass 3 load logic NOT refactored in v1.3.1 (lands in v1.3.2 PR 3). Content is in place but skill still uses v1.2.0 lineage-only Pass 3 path. Token cost unchanged until PR 3 merges.

### Out of scope (PR 3 v1.3.2)

- EN quadrant inventory (en-q1/q2/q3/q4-anchors.md) — still skeleton
- Pass 3 load logic refactor (register-signal + axis-extreme branches)
- `voice_quadrant.position` optional envelope field
- Voice Consistency gate over-mimic adherence dimension

---

## v1.3.0 — 2026-04-21 (Voice Anchor Library foundation — scaffold + meta split + landmark sections)

Foundation PR for voice anchor library expansion. 15 new toolkit-originated files scaffolded; content population lands in subsequent releases (v1.3.1 JP+zh / v1.3.2 EN+pipeline integration).

### Purpose

Prior to v1.3.0, Phase 6 Pass 3 lineage craft only supported 6 canonical masters (糸井 / 岩崎 / 眞木 / 谷山 JP + 許舜英 / 李欣頻 / 葉明桂 zh-TW). Any brief citing a non-master anchor (Didion / Hemingway / 張愛玲 / 向田邦子 / brand-era / literary primer) fell through to Pass 3's "no lineage match" default — losing register-signal refinement opportunity.

v1.3.0 establishes the foundation for a register-signal branch (alongside existing craft-gate + new axis-extreme branches) that gives Pass 3 access to ~70 additional anchors across EN/JP/zh-TW, grouped by quadrant × landmark position.

### Architecture (Option B3 + 4 token optimizations)

1. **Existing Tier 1 untouched** — `jp-copy-craft-lineage.md` + `zh-copy-craft-lineage.md` + `voice-and-tone.md` unchanged
2. **Flat layout** — all 15 new files directly under `standards/` per Anthropic skill-authoring "one level deep"
3. **Meta split (token optimization ①)** — hot-path schema/rubric/mitigation in `meta-core.md`; deep-path lineage/cross-ref/labels/corrections in `meta-detail.md`; Craft Gate loads core only, Register Signal loads both
4. **Landmark sections per quadrant file (token optimization ②)** — each `{lang}-q{N}-anchors.md` has explicit `## Landmark: {center/extreme/toward-Qn}` markers enabling section-targeted Pass 3 read (~1.5K vs ~3K whole-file)
5. **Cross-lang independent load (JP→zh-TW STRONG)** — register-signal path loads both `zh-q{N}` and `jp-q{N}` when applicable
6. **Axis extreme single cross-language file** — `axis-extreme-anchors.md` covers all 4 axis positions (authority/affinity/reason/emotion extreme) across EN/JP/zh-TW in one file; MVP placeholder pending V2 research

### Files added (15)

**Meta (2)**:
- `voice-anchor-meta-core.md` — schema definition + 4-condition selection rubric + over-mimic mitigation registry (20 entries)
- `voice-anchor-meta-detail.md` — verified lineage map (9 primary-source citations + 7 inferred-parallel flags) + cross-reference registry (JP→zh-TW STRONG directions) + 19×4 cross-cultural label rubric matrix + drift corrections catalog Z5-Z11

**Per-quadrant (12, landmark-organized skeletons)**:
- JP: `jp-q{1,2,3,4}-anchors.md`
- zh-TW: `zh-q{1,2,3,4}-anchors.md`
- EN: `en-q{1,2,3,4}-anchors.md`

Each quadrant file has 4 Landmark sections (`center` / `extreme` / `toward-Q{adj1}` / `toward-Q{adj2}`) + Overview + Cross-references. Placeholder comments note specific anchor candidates to be populated in v1.3.1 (JP+zh) / v1.3.2 (EN).

**Axis extreme (1)**:
- `axis-extreme-anchors.md` — 4 axis position stubs + candidate list + V2 research trigger criteria

### Files NOT changed (Tier 1 byte-identical preserved)

- `voice-and-tone.md`
- `jp-copy-craft-lineage.md`
- `zh-copy-craft-lineage.md` (Z5-Z11 drift corrections land in v1.3.1 via upstream domain-teams sync)
- `voice-quadrant-positioning.md` (optional `position` field lands in v1.3.2)

### Drift corrections catalog (documented in meta-detail)

Surfaced during research waves 2026-04-21; corrections will propagate into active inventory as files populate (v1.3.1+):

- Z5: 多喝水 ≠ 吳念真（奧美 in-house）
- Z6: 孫大偉 agency = 台灣奧美 / 偉太（非 JWT）
- Z7: 長榮〈I SEE YOU〉旁白 = 金城武（非 吳念真）
- Z8: 全聯經濟美學 creative lead = 龔大中（非 林敬凱）
- Z9: HK CD 名字 = KC Tsang（非 Calvin Choy）；agency = BBDO（非 JWT）
- Z10: 全聯 TV-era 2006-2014 = **Q3-CENTER（格言）**，非 Q3-extreme
- Z11: 意識形態廣告 = 許舜英 **+ 鄭松茂** 共同創辦

### Token cost (baseline, since no Pass 3 load logic changed)

No token cost impact in v1.3.0 — Pass 3 load logic refactor (to actually consume the new files) lands in v1.3.2. Current Pass 3 behavior unchanged: only craft-gate 6 masters supported.

### Research provenance

15 files scaffolded based on 6 research waves on `research/copywriting-voice-anchor-expansion` branch:
- 4 parallel research agents (EN / JP / ZH / KR+EU+other) — brand-era + copywriter persona
- 2 parallel Layer-0 research agents (JP/ZH + EN/KR) — literary / screenwriter primers
- 1 Type 5 verification agent — deferred candidates (國井美果 / SHIRO / KC Tsang / Dan Kennedy / Bill Jayme)
- 3 parallel gap-filler agents — JP Q1/Q4 + zh-TW Q1/Q3 + EN Q2/Q3 extreme

Research docs preserved in `copywriting-toolkit/docs/`:
- `voice-anchor-research.md` (initial brand-era + persona synthesis)
- `voice-anchor-layer-0-research.md` (literary register primer)
- `voice-anchor-archived-references.md` (skip list + KR scope-excluded + Type 5 verdicts)
- `voice-anchor-gap-research.md` (6 landmark gap fill)
- `voice-anchor-implementation-plan.md` (this PR executes PR 1 of 3-PR plan)

---

## v1.2.1 — 2026-04-20 (Quadrant Signal Mode — fix JP-thinking leakage on cross-language maestro refs)

**Observed failure** (v1.2.0 E2E test): user brief cited 糸井重里 + `output_language: zh-TW`. Pipeline produced zh-TW output but internally **ideated in Japanese first** and translated, yielding candidates like「冷蔵庫の奥、賞味期限切れの醤油が、3本。」 — clearly Japanese prose wrapped in nominal zh-TW output. Root cause: Express Mode's v1.2.0 dual-trigger resolution Option C wording ("譯化") misled the drafter into a JP→zh translation workflow instead of native zh-TW ideation.

**User insight that redirected the fix**: `standards/voice-quadrant-positioning.md` already has per-language native anchors in each quadrant (EN: Ogilvy/Apple/MailChimp — JP: 糸井/岩崎/谷山 — ZH: 許舜英/龔大中 etc.). Fix = use target-language anchor directly, not translate from source maestro.

### Fix — Quadrant Signal Mode

When user brief quotes a maestro whose native language ≠ `output_language`, the maestro is parsed as a **quadrant signal** (e.g. 糸井 → Q3), NOT a source text. The Phase 5 output then names the **target-language native anchor** in that same quadrant as `voice_quadrant.execution_reference`. Phase 4 drafters ideate **natively in `output_language` from the first keystroke** using that anchor's register — no translation stage ever occurs.

### Files changed

- **`skills/copywriting-intake/protocols/express-mode.md`** — Option C rewritten as Quadrant Signal Mode. Dual-trigger (cross-language maestro + output_language) parsed into quadrant lookup + target-language anchor lookup; `voice_notes.user_intent_signal` preserved for audit.
- **`agents/copywriter.md`** — Persona rule 2 rewritten: lineage matches `output_language`, not user's cited maestro. Added rules: native ideation from first keystroke, cross-tradition transplant is anti-pattern (Anti-Patterns in `voice-and-tone.md`), cross-language maestro is quadrant signal + Phase 5 names target-language native anchor.
- **`skills/copywriting-voice-quadrant-stage/SKILL.md`** — new Workflow step 5: cross-language execution anchor resolution. Output envelope `voice_quadrant` gains `execution_reference` + `user_intent_signal` fields.

### Impact

- Zero-cost fix on the quadrant-lookup side (standard already exists)
- No additional gates added — preserves v1.2.0 verification-density budget
- Phase 6 Pass 3 activation guard (v1.2.0) unaffected — when `execution_reference` is target-language native, Pass 3 matches that lineage's canon standard (e.g. `zh-copy-craft-lineage.md` for zh-TW Q2-Q3); no dual-lineage load

### Preserved

- All v1.2.0 creative divergence widths unchanged
- Immutable fields contract unchanged (`voice_quadrant` as whole still immutable after Phase 5)
- Same-language maestro references (e.g. 谷山 + ja, Ogilvy + en) unchanged — `execution_reference` simply equals `voice_reference` in that case

---

## v1.2.0 — 2026-04-20 (Verification Density Principle — token pruning, zero divergence loss)

Post-v1.1.0 token-cost analysis showed +25-40% cost vs `domain-teams:copywriting-team` baseline. Root cause: **17 verification / gate points** accumulated across v1.0.x-v1.1.0 (baseline has ~5), each individually justified when added but collectively over-dense. v1.2.0 prunes verification redundancy while **preserving 100% of creative divergence width** — candidate counts, runner-up pools, full-draft alternatives, 谷山 3-reason application per-candidate all unchanged.

### New principle — §Verification Density

plugin CLAUDE.md adds §Verification Density Principle (v1.2.0) — tiers verifications:

- **Load-bearing** — never prune (Intake Completeness MUST / Ethics MUST / Form 8a MUST / 谷山 3-reason per candidate)
- **Consolidatable** — merge overlapping scans; keep one authoritative enforcement point
- **Lazy / conditional** — guard by predicate; do not execute "just in case"
- **Format-level** — compress verbosity without losing content

Plus: a process discipline for future versions — before adding any new verification, map failure mode + check existing coverage + estimate marginal token cost + CHANGELOG justification.

### 7 prunes applied (estimated savings ~8K tokens per typical pipeline run)

**Consolidate (merge overlapping)**:

1. **Voice drift enforcement unified at Voice Consistency SHOULD gate** — Phase 6 Pass 1 axis drift scan downgraded to "catch the obvious" self-check; rigorous per-sentence enumeration is sole responsibility of Voice Consistency gate. Saves ~1K.
2. **`schwartz_alignment` consumer consolidated at Phase 8 8b** — Phase 6 Pre-pass downgraded to `tone_notes.schwartz_awareness_note` lightweight acknowledgement; 8b rubric is sole authoritative fidelity consumer. Saves ~500.

**Scope reduction (remove redundant scans)**:

3. **Express Phase 0.5-B grill scoped to 2 scans** (down from 4) — ethics boundary + voice-conflict check retained; premise / dependency + form-brief mismatch moved to Intake Completeness MUST gate (which already covered them). Saves ~1K.

**Lazy / conditional (guard by predicate)**:

4. **Router §2.4 invariant check → lazy mode** — runs only on non-consecutive phase / retry state / empty audit_trail / present violation / anomalous envelope size. Normal in-session continuation skips. Saves ~500 per transition.
5. **Phase 6 Pass 3 activation guard (hardened)** — agent MUST verify trigger predicate evaluates TRUE before loading any lineage standard. The ~700-line JP + ZH lineage files (~8-10K tokens) no longer load "just in case" — common Express Mode runs with `voice_reference = "default"` (dual-trigger resolution Option C case) skip Pass 3 entirely. **Saves ~2-3K on non-lineage runs (most Express cases).**

**Format-level (compress without losing content)**:

6. **3-reason rationale → structured object contract** — copywriter agent persona rule 3 adds v1.2.0 output contract: `{candidate, three_reasons: {to_whom, why_new, why_resonant}, verdict}` with each reason ≤ 30 words / 1 sentence. Replaces prior prose paragraph. ~70 tokens saved per candidate × ~28 candidates per pipeline run = **~2K per run**.
7. **Cumulative structural tightening** across §Verification Density Principle itself — ~500 saved in SKILL.md cross-references (pointers instead of duplicated inline logic).

### Preserved (NOT touched per user constraint)

- Phase 2 candidate counts: scoped 8-12 / standard 40-64 / full 64-100+ — **unchanged**
- Phase 4 inline micro-ideation: **3-5 candidates per framework stage — unchanged**
- Runner-up pools preserved
- Full-draft alternative pass (2-3 alternatives) preserved
- 谷山 3-reason test per candidate **unchanged in application** — only output format compressed
- Mandatory-with-rationale skip rule for Phase 2 unchanged
- All Load-bearing MUST gates unchanged (Intake Completeness / Ethics / Form 8a)
- All Tier 1 standards (academic canon) byte-identical per §Provenance & Divergence

### Expected impact

- Token cost per typical pipeline run: -8 to -9K (from ~85K → ~77K)
- Relative to baseline: v1.1.0 +25-40% → v1.2.0 **+15-25%**
- Catch rate on v1.1.0 E2E test brief (禾井): **unchanged** (all 7 load-bearing gates still active)
- Divergence width: **unchanged**
- Voice lineage execution: **unchanged** (Pass 3 still activates when triggers match; only "just in case" loads removed)

### Files changed

- `copywriting-toolkit/CLAUDE.md` — §Verification Density Principle added (with future-version process discipline)
- `copywriting-voice-tone-stage/SKILL.md` — Pass 3 activation guard + Pre-pass downgrade to awareness note + Pass 1 self-check downgrade
- `using-copywriting-toolkit/protocols/phase-decision-tree.md` — §2.4.1 lazy-mode activation rule added
- `copywriting-intake/protocols/express-mode.md` — Phase 0.5-B grill scope reduced to 2 scans
- `copywriting-form-check-stage/rubrics/form-appropriate-gate.md` — §schwartz_alignment dimension marked as v1.2.0 sole consumer
- `copywriting-toolkit/agents/copywriter.md` — persona rule 3 adds structured 3-reason output contract
- `copywriting-toolkit/.claude-plugin/plugin.json` — version 1.1.0 → 1.2.0

No Tier 1 files modified. DIVERGED header convention from v1.1.0 maintained for Tier 2 modifications.

## v1.1.0 — 2026-04-20 (architectural minor release — Provenance & Divergence principle + Phase 2 mandatory + Phase 4 inline micro-ideation)

**Minor version bump** (1.0.x → 1.1.0) signals architectural changes beyond spec clarification. Three concurrent layers.

### Layer 1 — Provenance & Divergence supersedes Copy-First

v1.0.x's "Copy-First" principle (all cp'd files byte-identical to source, zero modification) served initial development but became a drag as copywriting-toolkit's own mechanics (L1/L2/L3 preconditions, Express Mode tier taxonomy, brief+draft scope, conflict_flagged cross-phase consumers, retry-cap mechanics) outgrew the original `domain-teams:copywriting-team` scope. Continuing caused workaround sprawl (plugin-specific logic in SKILL.md §Evaluator hints, §Execution Paths, §8b extensions) that fragmented cohesive rules across 2+ files.

v1.1.0 formalizes a 2-tier policy in plugin CLAUDE.md §Provenance & Divergence Principle:

- **Tier 1 (immutable)**: standards/*.md + research/*.md — academic canon (神田 / 谷山 / Cialdini / Schwartz / Vaughn / Halliday etc.). `diff -q` must return empty.
- **Tier 2 (may diverge with documentation)**: protocols/*.md + checklists/*.md + rubrics/*.md — execution SOPs + gate criteria + qualitative rubrics legitimately vary per plugin. Every modified file carries a `<!-- DIVERGED FROM -->` header; changes are additive only (no deletion / re-order of original prose); every modification logged in CHANGELOG.

Exception: `zh-copy-craft-lineage.md` (new in v1.0.1, never cp'd — newly authored for this toolkit) is Tier 1 immutable without a diffable source.

### Layer 1b — v1.0.1-1.0.4 workarounds migrated to Tier 2 files

The SKILL.md-resident workarounds accumulated since v1.0.1 are now relocated to their natural home:

- `ethics-checklist.md` (now DIVERGED) — inherits §copywriting-toolkit evaluator hints for common TW/JP D2C patterns (aggregate-count social-proof / 業界首創 / 市價 dual-pricing / comparative-price w/o benchmark / repeating false-urgency); evaluator reads these alongside CHK-CTW-ETH-001 through 010 directly.
- `form-appropriate-gate.md` (now DIVERGED) — inherits §copywriting-toolkit additional dimensions (word-count band adherence with 🔴/🟡/🟢 thresholds + `schwartz_alignment: conflict_flagged` voice-fidelity dimension).
- `copywriting-ethics-check-stage/SKILL.md` — §Evaluator hints collapsed to a short pointer to the migrated checklist section.
- `copywriting-form-check-stage/SKILL.md` — §8b additional dimensions collapsed to a pointer.

Net effect: evaluator opens the checklist/rubric and finds the hints in one place. No more "read SKILL.md AND checklist AND cross-reference" cognitive tax.

### Layer 2 — Phase 2 ideation MANDATORY with depth control

Prior to v1.1.0, Phase 2 was skippable by default when a brief looked concrete. Express Mode routinely bypassed it. This violated 谷山 discipline's `散らかす → 選ぶ → 磨く` canon (`ideation-taniyama-discipline.md §なんかいいよね禁止` requires every candidate to justify against *other* candidates, which requires multiple candidates to exist).

v1.1.0:

- `phase-decision-tree.md §Step 3` rewritten — Phase 2 always runs; only **depth** varies:
  - **scoped** (8-12 candidates, single-pass, Express default)
  - **standard** (40-64 candidates, parallel subagents × 曼陀羅, Q1-Q10 default)
  - **full** (64-100+, standard + advanced overlays, for complex briefs)
- Skip only valid with **explicit rationale** recorded in `envelope.ideation_skip_rationale` (valid examples: pre-existing approved angle, known-winner baseline A/B, external concept re-draft). Silent skip → router force-upgrades to scoped.
- `copywriting-ideation/SKILL.md` §When to use rewritten — depth table + skip-rationale requirements.
- `express-mode.md` — predicted-pipeline template updated to surface depth choice.

### Layer 3 — Phase 4 drafter inline micro-ideation

Phase 2 alone is **angle-level** divergence (which concept direction?). Drafting a single non-compared prose per stage still violates 谷山 discipline at the **stage level**. v1.1.0 adds inline micro-ideation to all 5 Phase 4 protocols:

- `write-short-form-copy.md` (x2 — short-form + light-action) — 3-5 candidates per 切入點 or PREP/CREMA stage, 3-reason test, select 1
- `write-mid-form-copy.md` — 3-5 candidate sentences per BEAF stage, stage-specific discipline (B reject Feature contamination, E reject empty claims, A reject absolute superlatives, F reject marketing-copy language)
- `write-long-form-copy.md` (x2 — pasona + extended) — 3-5 candidate paragraph leads per stage + optional full-draft-level 2-3 alternative pass (tone-axis variations)

All 5 protocols carry DIVERGED header + §Inline micro-ideation section added at bottom. Original prose preserved verbatim.

`copywriter.md` agent persona rule 3 extended with v1.1.0 corollary: "NEVER deliver a single non-compared draft. If no Phase 2 candidates exist, run inline micro-ideation at stage-lead level yourself. 谷山 discipline is scale-invariant — diverge-select applies at angle level (Phase 2) AND stage level (Phase 4)."

### Files touched (v1.1.0)

- `copywriting-toolkit/CLAUDE.md` — §Copy-First rewritten as §Provenance & Divergence
- `copywriting-toolkit/skills/copywriting-ethics-check-stage/checklists/ethics-checklist.md` — DIVERGED + evaluator hints migrated
- `copywriting-toolkit/skills/copywriting-ethics-check-stage/SKILL.md` — §Evaluator hints collapsed to pointer
- `copywriting-toolkit/skills/copywriting-form-check-stage/rubrics/form-appropriate-gate.md` — DIVERGED + 2 dimensions migrated
- `copywriting-toolkit/skills/copywriting-form-check-stage/SKILL.md` — §8b dimensions collapsed to pointer
- `copywriting-toolkit/skills/using-copywriting-toolkit/protocols/phase-decision-tree.md` — §Step 3 rewritten (Phase 2 mandatory)
- `copywriting-toolkit/skills/copywriting-intake/protocols/express-mode.md` — predicted-pipeline template updated
- `copywriting-toolkit/skills/copywriting-ideation/SKILL.md` — §When to use rewritten (depth table)
- 5x Phase 4 protocols — DIVERGED + §Inline micro-ideation appended:
  - `copywriting-short-form/protocols/write-short-form-copy.md`
  - `copywriting-light-action/protocols/write-short-form-copy.md`
  - `copywriting-mid-form/protocols/write-mid-form-copy.md`
  - `copywriting-long-form-pasona/protocols/write-long-form-copy.md`
  - `copywriting-long-form-extended/protocols/write-long-form-copy.md`
- `copywriting-toolkit/agents/copywriter.md` — persona rule 3 corollary added
- `copywriting-toolkit/.claude-plugin/plugin.json` — version 1.0.4 → 1.1.0

**Zero deletion** of original cp'd prose. Every divergence is additive and marked. Run `grep -l "DIVERGED FROM" copywriting-toolkit/skills/**/*.md` to enumerate modified Tier 2 files.

## v1.0.4 — 2026-04-20 (topology-driven spec gaps closed)

Mermaid pipeline diagram added in v1.0.3 README surfaced 4 real spec gaps — not diagram artifacts, actual definitions missing from SKILL.md / protocol files that a rigorous agent walking the topology would notice. All 4 closed in this patch:

### #1 Shape C mid-pipeline re-entry semantics undefined

`using-copywriting-toolkit/protocols/phase-decision-tree.md §Step 2` defined phase-based routing forward but not **session resumption** / **external caller re-entry**. Added §2.3 Re-entry semantics + §2.4 Envelope invariant check:

- Retry-cap short-circuit (total_retries ≥ 4 → HALT before routing)
- Active violation routing (if `envelope.violation` present, route to `bounce_to`)
- Unknown phase rejection (malformed envelope → structured error)
- Stale envelope detection (missing L1 fields → route to intake)
- Cheap presence check on immutable fields — bounces to the skill that last wrote a dropped field

This closes the gap where external callers (scripts, UI, cron, resumed session) could arrive with a partially-populated envelope and router had no defined behavior.

### #2 Audit rewrite variant re-gating loop undefined

`copywriting-audit-stage/SKILL.md §When rewrites are produced` said "additional ethics re-gate on each rewrite" but didn't formalize the loop. Added formal 6-step contract:

1. Construct per-variant envelope (clone + swap draft + reset variant revise counter)
2. Run Phase 7 on variant
3. On PASS → run Phase 8
4. On NEEDS_REVISION → skip Phase 8, record findings, do NOT auto-revise (audit reports, doesn't re-draft)
5. Per-variant revise budget (revise_round_count < 2 allows FIXABLE auto-revise)
6. Aggregate `total_retries` across main + all variants; HALT at 4 regardless of which sub-pipeline got there

Plus: serial execution default; Voice Consistency gate runs once cross-variant; 谷山 3-reason rule applied locally (not via ideation).

`envelope.schema.json` adds `rewrite_variants[]` structure with per-variant verdicts + independent `revise_round_count`.

### #3 `conflict_flagged` preservation contract — and all cross-phase flags in general

Phase 5's `voice_quadrant.schwartz_alignment = conflict_flagged` travels 3 hops (Phase 5 emit → Phase 6 Pre-pass consumer → Phase 8 8b consumer). No explicit rule required preservation, so a misbehaving Phase 6 output could silently drop it. Same gap for `tone_notes.lineage_gap`, `audit_trail[]`, `retries.*` counters.

`copywriting-toolkit/CLAUDE.md §Handoff Envelope` adds §Immutable fields — preservation contract with 9 fields listed (writer / readers / mutability). Key rules:

- **Immutable after writer phase**: voice_quadrant object, schwartz_alignment, tone_notes.schwartz_conflict_carried, tone_notes.lineage_gap, brief L1, express_mode_used
- **Append-only**: audit_trail[]
- **Monotonic**: retries.* (counters only increment; resetting hides stall loops)

Enforcement: router's Step 2.4 re-entry invariant check bounces any envelope with a dropped immutable field to the last-writer skill. Cheap presence check, not semantic validation.

`envelope.schema.json` adds `immutable_fields_enforced[]` as documentation marker.

### #4 Phase 6 BLOCKED dual-trigger conflict bypassed the router

`copywriting-voice-tone-stage/SKILL.md §When lineage craft applies` said "if both JP + ZH triggers match → BLOCKED; return to intake" as a SELF-DISPATCHED bounce. This violated the L2 single-enforcement-point contract (CLAUDE.md §Router Validation: "skills do NOT self-dispatch bounce; they return the violation shape and let the router route"). Fragmented the `bounce_round` counter across skill-local and router-local scopes.

Fixed by changing the instruction to emit a proper `violation` envelope (with `detected_by`, `malformed`, `bounce_to: copywriting-intake`, `user_message`). Router handles the actual bounce + counter increment.

### Changes

- `using-copywriting-toolkit/protocols/phase-decision-tree.md` — §2.3 + §2.4 added
- `copywriting-audit-stage/SKILL.md` — §When rewrites are produced expanded with 6-step contract
- `copywriting-toolkit/CLAUDE.md` — §Handoff Envelope gains §Immutable fields section
- `copywriting-voice-tone-stage/SKILL.md` — Pass 3 dual-trigger block now emits violation, does not self-bounce
- `.claude-plugin/envelope.schema.json` — `rewrite_variants[]` + `immutable_fields_enforced[]` added

No behavioural regression. These are spec-completeness fixes that make existing de-facto behavior explicit + catch silent drops.

plugin.json: 1.0.3 → 1.0.4.

## v1.0.3 — 2026-04-20 (grill resolution strategy scope clarification — superpowers-aligned)

Post-v1.0.2 incomplete-brief E2E test surfaced a protocol gap: the tier taxonomy (T1/T2/T3) was defined only in `protocols/express-mode.md §Tiered FATAL handling` but `copywriting-brainstorming.md §Q8` (cp'd byte-identical from `domain-teams:copywriting-team`) didn't reference it. A rigorous agent running Q1-Q10 could either over-escalate (abort on every FATAL candidate) or under-escalate (resolve inline but lose the carry-forward metadata).

**Design question**: should the gap be closed by unifying both paths under a shared tier SSOT, or by scoping tier logic to Express-only and declaring Q1-Q10 inline-resolving?

Consulted `superpowers` precedent — `brainstorming` (interactive) and `subagent-driven-development` (status codes: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) are kept as **two separate skills with different return contracts**. `superpowers` explicitly does NOT unify interactive and non-interactive paths. Tier codes are the non-interactive mode's substitute for follow-up questions, not a universal mechanism.

Applied the same pattern:

- `protocols/express-mode.md §Tiered FATAL handling` — added Scope note at top: tier classification is an OUTPUT CONTRACT for `copywriter-evaluator` under Express grill specifically, analogous to subagent status codes. Does NOT apply to Q1-Q10.
- `copywriting-intake/SKILL.md §Execution Paths` — extended with §Grill resolution strategy differs by path section. Documents:
  - Q1-Q10 inline probe-and-resolve (A/B/C option menu at Q8; no tier concept)
  - Express structured tier return (T1/T2/T3 classification)
  - Explicit §Rationale for not unifying citing `superpowers` precedent
- Did NOT modify `copywriting-brainstorming.md` (cp'd, byte-identical — copy-first).
- Did NOT create a shared tier-SSOT file (rejected per superpowers pattern).

No behavioural logic changed — this is a documentation-contract clarification. Both paths were already working correctly in E2E tests; v1.0.3 makes the design intent explicit so future agents don't need to "apply by analogy".

plugin.json bumped 1.0.2 → 1.0.3.

## v1.0.2 — 2026-04-20 (Fix #6 rubric reconciliation)

Post-v1.0.1 re-test found one internal contradiction in Fix #6 (word-count band adherence in Phase 8 8b): the rubric example said "新 PASONA at 1500 chars → 🟡" but the threshold rule stated "≤60% of band floor → 🔴". 1500 / 3000 floor = 50%, which falls under the ≤60% rule → actual verdict should be 🔴, not 🟡 as the example claimed.

Reconciled by restating the rubric as three ordered thresholds (🔴 ≤60% / 🟡 60-99% / 🟢 ≥100%) and updating the example:

- 新 PASONA at 1500 chars (50% of floor) → 🔴 (recommend 旧 PASONA)
- 新 PASONA at 2500 chars (83% of floor) → 🟡

File changed: `copywriting-toolkit/skills/copywriting-form-check-stage/SKILL.md §8b Word-count band adherence`.

No other fixes touched; all 7 v1.0.1 fixes remain as designed. Bump plugin.json 1.0.1 → 1.0.2.

## v1.0.1 — 2026-04-20 (post-E2E-test hardening)

End-to-end pipeline test (4 parallel agents on a zh-TW coffee subscription brief with a planted 30% 有利誤認 claim) surfaced 7 design tensions. All fixed in this patch:

- **Tiered FATAL handling in Express Mode** (`copywriting-intake/protocols/express-mode.md`) — replaced one-size-fits-all "any FATAL → ABORT Express" with three tiers: T1 AI-inferred FATAL → abort; T2 user-stated FATAL candidate with missing benchmark → carry to Phase 7; T3 user-stated outright violation → abort. Defense-in-depth with Phase 7 for the common comparative-claim case.
- **Phase 7 artifact scope clarified** (`copywriting-ethics-check-stage/SKILL.md §Artifact scope`) — evaluator judges both `draft` text AND brief-level claims that will accompany delivery in real placement. Closes the gap where `copywriter` agent's legitimate claim-drop at Phase 4 could silently slip a FATAL past a draft-only adjudication.
- **ZH anchors added to Express high-stakes exclusion** (`express-mode.md`) — restricted maestro list now covers {許舜英, 李欣頻, 葉明桂} in addition to the JP set {糸井重里, 岩崎俊一, 眞木準, 谷山雅計}. Express must not auto-infer these as voice_reference — they trigger Phase 6 Pass 3 lineage craft which re-writes the draft.
- **NEW `zh-copy-craft-lineage.md`** (Tier 3 ZH lineage standard, 428 lines) — primary-source-researched deep-dive on 許舜英 (意識形態 / 中興百貨 1988-1999, 11 dated corpus entries), 李欣頻 (誠品敦南 1990s-2000s, 7 entries), 葉明桂 (奧美 / 左岸 1998-, 3 campaign lines + strategic-framework quotes). 4 attribution corrections (#Z1 Altenberg, #Z2 寺山修司, #Z3 意識形態 founding year, #Z4 content-farm drift). Per-master LLM reproduction gap analysis. Primary Sources bibliography with ISBNs. This is NOT a verbatim cp from `domain-teams:copywriting-team` — it is newly authored for this toolkit.
- **Phase 6 Pass 3 extended to ZH branch** (`copywriting-voice-tone-stage/SKILL.md`) — "When JP lineage applies" became "When lineage craft applies" with separate JP and ZH triggers. Pass 3 now has Pass 3a (JP) and Pass 3b (ZH). Cross-transplant explicitly forbidden. Dual-trigger conflict (e.g. `voice_reference: 糸井重里` + `output_language: zh-TW`) → BLOCKED, return to intake.
- **`schwartz_alignment: conflict_flagged` now has downstream consumers** — Phase 6 Pre-pass reads the flag and compensates 4-axis defaults; Phase 8 8b rubric checks whether voice-intent vs delivery mismatches in conflict_flagged context, raising 🟡 on fidelity failure. Closes the "flag with no consumer" loop.
- **Word-count band adherence added to Phase 8 8b** — `copywriting-form-check-stage/SKILL.md §Gate Definition § 8b` now flags drafts below framework's canonical band floor (🟡 boundary, 🔴 far-below). Surfaces e.g. 新 PASONA at 1500 chars (below 3000 floor) as a tunable flag, not silent pass.
- **Evaluator hints added for common TW/JP D2C patterns** (`copywriting-ethics-check-stage/SKILL.md §Evaluator hints`) — aggregate-count social-proof ("5,000 位訂閱者") routes through CHK-003 + CHK-006 simultaneously; "first in industry" / "業界首創" → CHK-003; "市價 X 元" dual-pricing → CHK-004; comparative-price without benchmark → CHK-004; repeating false-urgency → CHK-002. Closes v1.0.0 checklist gaps without modifying the cp'd checklist file.

## v1.0.0 — 2026-04-20

Initial release. Pipeline-structured refactor of `domain-teams:copywriting-team` (505-line SKILL.md, 19 standards, 9 protocols, ~12K lines) into a 14-skill plugin with formal precondition / bounce-back / Express Mode mechanics. Original `domain-teams:copywriting-team` remains untouched for A/B comparison.

### Pipeline

9-phase primary path + audit alt-entry:

```
Phase 0-1  copywriting-intake              (Q1-Q10 OR Express Mode)
Phase 2    copywriting-ideation            skippable
Phase 3    copywriting-neta-injection      skippable; hybrid pre/post placement
Phase 4    one of 5 form-specific drafters:
             copywriting-short-form / mid-form /
             long-form-pasona / long-form-extended / light-action
Phase 5    copywriting-voice-quadrant-stage
Phase 6    copywriting-voice-tone-stage
Phase 7    copywriting-ethics-check-stage     (MUST gate, evaluator-only)
Phase 8    copywriting-form-check-stage       (MUST gate, evaluator-only)
Alt        copywriting-audit-stage            (audit external copy, Phases 5-8)
Router     using-copywriting-toolkit          (entry, validator, Express qualifier)
```

### Skills added (14)

| Skill | Archetype | Role |
|---|---|---|
| `using-copywriting-toolkit` | router | Entry + Preconditions validator + Express Mode qualifier |
| `copywriting-intake` | router | Phase 0-1 brief intake; Q1-Q10 or Express Mode; Intake Completeness MUST gate |
| `copywriting-ideation` | executor | Phase 2 divergence (曼陀羅 + VS + 小霜) + convergence (KJ + 谷山) |
| `copywriting-neta-injection` | executor | Phase 3 hybrid bake-in / overlay; 4 techniques; WebSearch Phase A-D; Neta Safety SHOULD gate |
| `copywriting-short-form` | executor | Phase 4 catchcopy (7-15 chars, AIDMA A+I, 5 切入點) |
| `copywriting-mid-form` | executor | Phase 4 EC product copy (BEAF) |
| `copywriting-long-form-pasona` | executor | Phase 4 PASONA / 新PASONA / PASBECONA (神田) |
| `copywriting-long-form-extended` | executor | Phase 4 QUEST (Fortin 2005) / PASTOR (Edwards 2016) |
| `copywriting-light-action` | executor | Phase 4 PREP / CREMA micro-conversions (Kaushik 2007) |
| `copywriting-voice-quadrant-stage` | executor | Phase 5 Voice Quadrant (Vaughn × Halliday) + Schwartz routing |
| `copywriting-voice-tone-stage` | executor | Phase 6 4-axis tone + Mailchimp context switching + JP lineage |
| `copywriting-ethics-check-stage` | ops | Phase 7 MUST gate — 景表法 / FTC / dark patterns |
| `copywriting-form-check-stage` | ops | Phase 8 MUST + SHOULD gate — framework / length / CTA |
| `copywriting-audit-stage` | router | Alt entry — audit external copy through Phases 5-8 |

### Agents added (2)

| Agent | Tier | Role |
|---|---|---|
| `copywriter` | sonnet | Worker — drafting / ideation / audit variants. Persona: reader-first 糸井 / Ogilvy lineage with 谷山 discipline and 小霜 honesty. |
| `copywriter-evaluator` | opus | Gate evaluator. Persona: strict legal / framework reviewer — explicitly NOT a copywriter (aesthetic-capture anti-pattern called out). |

### Precondition + bounce-back mechanism (L1 / L2 / L3)

Introduced a formal precondition / bounce-back / Express Mode contract in three layers:

- **L1**: Every downstream SKILL.md declares a `## Preconditions` section with required envelope fields (Level 1 BLOCKED), optional fields, and upstream bounce targets. Field names + types match `.claude-plugin/envelope.schema.json`.
- **L2**: Plugin CLAUDE.md §Envelope Violation defines the bounce-back envelope shape + 5 routing rules. Three-counter retry cap: `bounce_round` (schema loop), `revise_round_count` (evaluator loop), and `total_retries` aggregate. `total_retries >= 4` forces HALT-and-ask-user (mirrors `superpowers:executing-plans` stop-and-ask).
- **L3**: `using-copywriting-toolkit` becomes the single enforcement point — routes, validates Preconditions before every skill launch, and qualifies Shape A for Express Mode.

### Express Mode (Phase 0-1 fast path)

`copywriting-intake/protocols/express-mode.md` — for briefs that already carry all Level 1 fields. Replaces Q1-Q10 elicitation with:

1. **Synthesis** — `copywriter` restates the brief in 9-phase toolkit vocabulary (form, Schwartz, voice quadrant, framework, predicted pipeline route)
2. **Automated grill** — `copywriter-evaluator` runs 景表法 / FTC / premise / voice-conflict / form-mismatch checks
3. **Single-turn confirmation** — user confirms or adjusts item-by-item
4. **Intake Completeness MUST gate** — same gate as Q1-Q10 path

Guardrails:

- Level 1 fields MUST be sourced from user's exact words (never inferred)
- `brief.voice_reference` MUST NOT auto-infer a specific maestro (糸井 / 岩崎 / 眞木 / 谷山) — Phase 6 treats these as HARD TRIGGERS for JP lineage craft; silent mis-inference would re-write the draft in the wrong voice. Default to `"default"` + prompt user to override.
- Bounce-back re-entry ALWAYS forces Q1-Q10 (bounce means synthesis missed something; interactive mode surfaces the gap)

### Grounding (primary sources preserved verbatim)

All 19 standards + 9 protocols + 3 checklists + 3 rubrics + 8 grounding notes are byte-identical copies of `domain-teams:copywriting-team` source (verified via `diff -q` across every file). Canonical grounding:

- 神田昌典 2016/2021 PASONA / 新PASONA / PASBECONA
- 谷山雅計 2007 散らかす→選ぶ→磨く + なんかいいよね禁止
- 今泉浩晃 1987 曼陀羅発想法
- 川喜田二郎 1967 KJ法
- Cialdini 1984 *Influence*
- Schwartz 1966 *Breakthrough Advertising*
- Zhang et al. 2025 Verbalized Sampling (arXiv:2510.01171)
- Fortin 2005 QUEST / Edwards 2016 PASTOR
- 小霜和也 2010/2014 本能分析
- 秋山・杉山 2004 AISAS / 飯髙 2019 ULSSAS
- Kaushik 2007 micro/macro conversion
- McQuarrie & Mick 1996 rhetorical operations / Lakoff & Johnson 1980 conceptual metaphor / Thornton 1995 subcultural capital
- 景品表示法 2023 amendment (effective 2024-10-01) + ステマ告示 (effective 2023-10-01)
- FTC Endorsement Guides 16 CFR 255 (effective 2023-07-01)
- Vaughn 1980 FCB × Halliday 1978 SFL (team-synthesis 2-axis combination)
- JP voice tradition: 糸井重里, 岩崎俊一, 眞木準 via TCC 年鑑

### A/B coexistence

`domain-teams:copywriting-team` remains untouched. Both plugins can run in parallel on the same brief for comparison. Consolidation is deferred to post-A/B retrospective (no planned timeline).

### Registry

- Marketplace entry added to `/Users/kouko/GitHub/monkey-skills/.claude-plugin/marketplace.json`
- Root README updated: plugin count 4 → 6 (investing-toolkit + copywriting-toolkit); total skills 36 → 65
- `.claude-plugin/envelope.schema.json` published as SSOT for envelope shape across the 14 skills (router-validated, not JSON-Schema-enforced)

---

## Known limitations / deferred items

These are **intentional scope cuts**, tracked here rather than buried in code comments.

1. **Runtime validator not implemented** — L3 router validates Preconditions at prose-level; a full runtime validator that loads `envelope.schema.json` + each SKILL.md Preconditions table and enforces them programmatically is deferred to v1.1. Current enforcement is by the main agent executing the router protocol, not a standalone validator process.

2. **No `tests/` directory with envelope fixtures** — fixtures require the runtime validator to exercise them; without validator, fixtures are dead weight. Deferred to v1.1 with validator.

3. **`using-copywriting-toolkit` namespace duplication** — `copywriting-toolkit:using-copywriting-toolkit` has an echo. `skill-creator-advanced` audit suggested rename to `copywriting-router`. Rejected for v1.0.0 because `using-*` is the monkey-skills marketplace convention (mirrors `using-domain-teams`, `using-obsidian`, `using-investing-toolkit`). Re-evaluate only if broader naming convention changes.

4. **5 `-stage` suffixes on Phase 5-8 skills** — long but semantically consistent with the pipeline framing. Rename would cascade through every cross-reference in SKILL.md / envelope.schema.json / phase-decision-tree.md. Deferred unless a dedicated naming refactor is scheduled.

5. **`copywriting-voice-quadrant-stage` Schwartz × Quadrant conflict has no inline worked example** — the detail lives in `standards/voice-quadrant-positioning.md §With persuasion-psychology-anchor.md Schwartz Levels`. Add worked example if user feedback shows confusion.

6. **No Mermaid pipeline diagram** — the 9-phase ASCII diagram in README is clear but a Mermaid diagram for the bounce-back + revise-loop control flow would aid onboarding. Deferred to v1.1 documentation pass.

7. **Inline-duplication drift risk** — `persuasion-psychology-anchor.md` lives as 5 identical copies across Phase-4 workflow skills; `sns-evolution-aisas-ulssas.md` as 2 identical copies. No sync script. Accept as design cost (each skill stays self-contained); if drift observed, add a sync script rather than attempting cross-skill runtime loading.

8. **`audit_trail[]` rendering / persistence** — the field is defined in `envelope.schema.json` and documented in CLAUDE.md §Audit Trail, but the router's rendering to the user on `halt-ask-user` is specified as SHOULD (not MUST) and persistence is left to the caller. First real-world usage will surface whether a stronger contract is needed.

---

## Upgrade path (for future versions)

- **Additive fields** in the envelope: callers should preserve unknown fields verbatim on re-entry (forward-compatible). See CLAUDE.md §External Caller Guide §Envelope evolution.
- **Required-field changes** or enum restrictions: will bump minor version (v1.x → v1.y) at minimum, with a CHANGELOG entry naming the field and the breaking change.
- **Agent tier changes**: if `copywriter` or `copywriter-evaluator` move to different model tiers, CHANGELOG will flag it explicitly — evaluator persona discipline (no aesthetic capture) is sensitive to tier.
