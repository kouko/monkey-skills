# Changelog

All notable changes to deconstruct-toolkit are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3] — 2026-05-05

i18n completion. v0.2.2 shipped per-skill READMEs in EN-only, missing
the tri-language convention established by PR #150 (`project_i18n_multilingual_readme.md`).
This release adds JP + zh-TW variants for all 4 skill READMEs and adds
language-switcher lines to the EN versions.

### Added

- `skills/artifact-deconstruct/README.ja.md` (130 lines) + `README.zh-TW.md` (130 lines)
- `skills/argument-deconstruct/README.ja.md` (94 lines) + `README.zh-TW.md` (94 lines)
- `skills/assumption-surface/README.ja.md` (114 lines) + `README.zh-TW.md` (106 lines)
- `skills/using-deconstruct-toolkit/README.ja.md` (117 lines) + `README.zh-TW.md` (117 lines)

8 new files; ~902 lines of translation. All translations follow:

- Glossary `docs/i18n/glossary-ja.md` § 制作物脱構築領域 + `glossary-zh-TW.md` § 作品解構域 (the just-merged v0.2.1 reversal rule)
- English-noun preservation: `skill` / `plugin` / `slash command` /
  `protocol` / `fixture` / `framework` / `pipeline` / `router` /
  `dispatch` / `lens combination` / `warrant` (with first-mention gloss
  `論証根拠` / `論證根據`) all kept English
- Proper nouns kept English: Toulmin / Burke / Cialdini / Goffman /
  Lakoff / Brignull / Swales / Bhatia / Nielsen-Norman / Althusser /
  Balibar / Popper / Hinds / Doi / Yamamoto / Hwang / Hu / Markus &
  Kitayama / Peng & Nisbett / 木下是雄 / 甲田直美 / 山口周 / 劉勰
- Skill names + lens file names + `-anglo` / `-ja` / `-zh` variant
  suffixes kept English
- ZH `artifact` → **作品** (not 文物 — applying just-merged v0.2.1 reversal)
- `polished` modifier dropped (per just-merged v0.2.1 rule)
- `dimension` (rubric sense) → `観点` (JA) / `維度` (ZH) per
  `feedback_dimension_translation.md`
- All cross-reference paths preserved unchanged

### Changed

- `skills/{4-skills}/README.md` — added language switcher line after H1:
  `**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)`
  (matches `domain-teams/skills/docs-team/README.md` canonical pattern)

### Validator

15 eval cases, 21 lens references, 4 skills all valid.

## [0.2.2] — 2026-05-05

Per-skill READMEs added. Each of the 4 skills (`using-deconstruct-toolkit`
/ `artifact-deconstruct` / `argument-deconstruct` / `assumption-surface`)
gets a thick GitHub-browser-facing README authored directly per
`feedback_skill_internal_readme_exempt_from_docs_team.md` convention
(skill-internal READMEs follow lighter rules than docs-team-managed
docs: language switcher / English-noun / link to SKILL.md / no
contradiction with SKILL.md).

### Added

- `skills/artifact-deconstruct/README.md` (140 lines) — flagship skill
  README. 6-step workflow summary + lens library table with full
  per-variant author attributions + 6-dimension backbone + ethical-
  position legend (🟢/🟡/🔴/⚫) + cultural-variant routing rule + verified
  pointers to all 11 worked-example fixtures (3 Anglo + 8 JP/ZH).
- `skills/argument-deconstruct/README.md` (113 lines) — argument-focused
  deep-dive README. Toulmin 6-component table with warrant emphasis +
  8 hidden-warrant patterns (count verified against
  `references/lens-toulmin.md`) + Burke pentad 6-ratio table +
  argument-map mermaid output description.
- `skills/assumption-surface/README.md` (113 lines) — atomic-skill
  README. 4-move method (reverse-Toulmin / Althusser symptomatic
  reading / counterfactual probe / frame audit) + 3-tier strength
  classification + Popper falsifiability test + Althusser & Balibar
  (1965/1968, Brewster 1970 trans.) citation matched to lens reference.
- `skills/using-deconstruct-toolkit/README.md` (114 lines) — router
  README. Boundary checks (sourceatlas / philosophers-toolkit /
  forward-production) + two-axis routing (artifact type × user intent)
  + three pre-dispatch filters (length / info-only / multi-modal) +
  cultural-variant detection step (EN/JA/ZH per ADR-0004).

All four READMEs:
- Are English-only (matching plugin-level convention)
- Link to their respective `SKILL.md` as full canon (NOT duplicating
  large blocks)
- Cross-reference sister skills with relative links
- Verify all cited fixture / case file paths exist
- Pass `scripts/check-eval-cases.py` validator

## [0.2.1] — 2026-05-05

Translation reversal: zh-TW `artifact` and JP `文物脱構築` corrected;
`精緻` modifier dropped across zh-TW. **Reverses the v0.1.0 glossary
lock that rendered "artifact" as 文物 承襲「設計文物」用法.**

### Why this is a reversal, not a typo fix

v0.1.0 `docs/i18n/glossary-zh-TW.md:171` deliberately chose 文物 with
the rationale: 「承襲『文化文物』『設計文物』用法。**避免**『製作物』
（日文式）/『成品』（過於通俗）」. In review, the choice was wrong:

- **文物** in zh-TW core semantics = museum / archaeology / cultural
  relic (古董). Applied to landing pages / UI flows / SOPs (modern,
  produced, often quotidian artifacts) it is a category error. The
  same word in copywriting-toolkit's 故宮 anchor files is **correct**
  (literal museum objects), but the deconstruct-toolkit context is
  not antiquity.
- **精緻** modifier carries aesthetic-quality judgment (精緻料理 /
  精緻包裝 = exquisite / fine). It narrows plugin scope to "only
  beautiful artifacts" — but a boring corporate landing page is also
  a "polished artifact" worth deconstructing. The EN "polished"
  modifier means "finished / non-draft," NOT "exquisite." JP README
  validates this: 「制作物」省略 polished 修飾語 entirely.

### Changed

- `docs/i18n/glossary-zh-TW.md` § renamed 「文物解構域」→「作品解構域」;
  artifact entry rewritten with reversal rationale; new `polished`
  entry locks the "drop modifier" rule.
- `docs/i18n/glossary-ja.md` § renamed 「文物脱構築領域」→「制作物
  脱構築領域」; artifact entry annotated with the no-aesthetic-modifier
  rule.
- `deconstruct-toolkit/README.zh-TW.md` (10 places) 文物 → 作品;
  「精緻」removed from 4 places. Roadmap section updated to v0.2.0
  (was stuck at v0.1.0 in this file — drift from v0.2.0 PR which
  updated en/ja but missed zh-TW).
- `deconstruct-toolkit/skills/artifact-deconstruct/SKILL.md`
  description bilingual line: 「文物逆向解構」→「作品逆向解構」.
- `deconstruct-toolkit/.claude-plugin/plugin.json` description ZH
  fragment: 「文物」→「作品」; version bumped 0.2.0 → 0.2.1.
- `README.md` / `README.ja.md` / `README.zh-TW.md` (repo top-level)
  plugin table entries: version 0.1.0 → 0.2.1 (catches up + this
  bump); zh-TW description rewritten 文物 → 作品 + 精緻 dropped;
  ja description fragment 「文物脱構築」→「制作物脱構築」; all 3
  description cells now mention EN/JA/ZH cultural variants.

### Unchanged (intentional historical record)

- `deconstruct-toolkit/docs/design-proposal.md` (2026-05-04) — v0.1.0
  approved-design-proposal record; its term-decision table at line 374
  documents the **original** (now-reversed) choice. Glossary is the
  current SoT; design-proposal is preserved as historical record per
  ADR-style convention.
- `copywriting-toolkit/docs/anchor-references/*` references to 文物
  are CORRECT — those refer to literal 故宮 museum objects (NPM
  meme account anchor), not the design-discourse artifact sense.

### Hard exclusions (still in force)

- ❌ AI-generated translations of Anglo lens content (per v0.2.0 §2.3)
- ❌ Korean / Vietnamese / Thai variants (per ADR-0004)

## [0.2.0] — 2026-05-05

Cultural-variant release. Closes the v0.1.0 grounding gap acknowledged
in `docs/grounding-v0.1.0.md`: the 4 culturally-sensitive lenses
(rhetoric / persuasion / genre / frame) now ship per-language variants
for **EN / JA / ZH** instead of pretending universality from an
Anglo-only primary-source base. Plugin scope is permanently locked at
the EN/JA/ZH triaxis per [ADR-0004](docs/adr/0004-cultural-lens-variants.md);
artifacts in other languages get an `-anglo` fallback **with explicit
caveat** rather than silent miscoverage.

### Added

#### Cultural lens variants (8 new files)

- `lens-rhetoric-ja.md` — Hinds (1983 *Text* 3:2 / 1987 Connor & Kaplan
  eds., *Writing Across Languages*) + Oh (2025 *TEXT* 29:2)
  kishōtenketsu (起承転結) + JP academic 序論-本論-結論 dual-mode +
  reader-responsibility surface signals.
- `lens-rhetoric-zh.md` — 劉勰《文心雕龍·知音》六觀 (位體 / 置辭 /
  通變 / 奇正 / 事義 / 宮商), 周振甫 / 王運熙 critical editions; ZH-specific
  moves (對偶 / 排比 / 比興 / 用典); TW vs HK vs PRC register notes.
- `lens-persuasion-ja.md` — Cialdini (2021) re-weighted on Hofstede JP
  profile (PD~54, IDV~46, UAI~92) + 4 JP-specific mechanisms (建前/本音
  per Doi 1971, 婉曲表現, 空気を読む per Yamamoto 1977, 老舗/暖簾
  longevity authority); JP-register dark-pattern translation table.
- `lens-persuasion-zh.md` — Cialdini (2021) re-weighted on Hofstede CN
  profile (PD~80, IDV~20) + 5 ZH-specific mechanisms (面子/臉 per Hu
  1944, 關係/人情 per Hwang 1987 *AJS*, 自己人/外人, 禮); ZH-specific
  dark patterns (道德綁架 / 話術 / 假關係); TW/HK/PRC register fork.
- `lens-genre-ja.md` — Swales (1990) + Bhatia (1993) + 木下是雄
  『理科系の作文技術』(中公新書, 1981) + Hinds (1987); JP academic
  序論-本論-結論 + IMRaD overlay + 7-move 拝啓-formula JP business
  letter + abbreviated メール genre.
- `lens-genre-zh.md` — Swales + Bhatia + TW 行政院《文書處理手冊》公文
  sub-genres (函 / 通知 / 報告 / 請示 / 公告 with 主旨-說明-辦法-擬辦
  slots) + 緒論-本論-結論 academic + 八股 起承轉合 legacy in op-ed;
  TW vs PRC GB/T 9704-2012 vs HK British colonial-administrative fork.
- `lens-frame-ja.md` — Goffman (1974) + Lakoff (1980) + Doi (1971) +
  Yamamoto (1977) + Markus & Kitayama (1991 *Psychological Review*
  98:2); 建前/本音 dual-frame, 空気 collective frame-reading, 間 (ma)
  silence-as-frame, JP conceptual metaphors (心 / 道 / 縁 / 場).
- `lens-frame-zh.md` — Goffman + Lakoff + Hu (1944 *American
  Anthropologist* 46:1) + Hwang (1987 *AJS*) + Peng & Nisbett (1999
  *American Psychologist* 54:9 — yin-yang dialectical thinking);
  面子/臉 dual-face, 關係/圈子 in-group framing, 陰陽 dialectical
  metaphor as challenge to Lakoff binary, ZH conceptual metaphors
  (道 / 氣 / 緣 / 心 / 圈子).

#### Variant routing infrastructure

- `protocols/lens-variant-selection.md` (NEW) — language detection
  algorithm + variant selection + complications (mixed-language,
  translation artifacts, Korean/etc. fallback with caveat,
  TC-vs-SC disambiguation, register dual-mode).
- `using-deconstruct-toolkit/SKILL.md` (UPDATE) — new "Detect language
  and cultural register" step; signals passed to receiving skill.
- `artifact-deconstruct/SKILL.md` (UPDATE) — Step 4 resolves variant
  via `protocols/lens-variant-selection.md` before reading lens
  references; report MUST state which variant was applied.

#### Documentation

- `docs/adr/0004-cultural-lens-variants.md` (NEW) — codifies the
  variant pattern + permanent EN/JA/ZH scope decision.
- `docs/v0.2.0-cultural-variants-design-proposal.md` (NEW) — full
  design rationale + commit plan + resolved open questions.
- `docs/grounding-v0.2.0.md` (NEW) — primary-source verification log,
  parallel to `grounding-v0.1.0.md`.

#### Eval fixtures (8 new synthetic-representative artifacts)

- `sample-ja-op-ed.md` — JP newspaper op-ed (kishōtenketsu)
- `sample-zh-op-ed.md` — TW op-ed (通變 + 用典 + 對偶/排比)
- `sample-ja-ec-lp.md` — JP DTC LP (老舗 + 限定 + 婉曲)
- `sample-zh-ec-lp.md` — TW e-commerce LP (老字號 + 關係 + 面子)
- `sample-ja-business-letter.md` — JP 7-move 拝啓-formula letter
- `sample-zh-gongwen.md` — TW 公文 函 (主旨/說明/辦法 三段式)
- `sample-ja-political-speech.md` — JP press conference (建前/本音 + 空気)
- `sample-zh-political-speech.md` — TW speech (面子/關係 + 陰陽 + 圈子)

All 8 carry explicit honesty flags (synthetic-representative, not
real-fetched) in their metadata blocks.

#### Eval cases (8 new YAML cases)

- `artifact-deconstruct-04-ja-op-ed.yaml` through `-11-zh-political-speech.yaml`.
  Each `must_find` includes a `variant-named-in-output` item testing
  that the analysis attributes which language variant was applied.

### Changed

- `lens-rhetoric.md` / `lens-persuasion.md` / `lens-genre.md` /
  `lens-frame.md` — content moved to `-anglo.md` siblings; originals
  now serve as universal-core routers (1-page meta) per Q5.
- README files (en / zh-TW / ja) — clarified plugin scope is
  permanently EN / JA / ZH per Q4.

### Roadmap shifts

| Version | Original scope | New plan |
|---|---|---|
| v0.2.0 | product-deconstruct + pricing-decode | **Cultural variants** (this release) |
| v0.3.0 | frame-reveal / bias-audit / decision-archaeology | product-deconstruct + pricing-decode (pushed) |
| v0.4.0 | (unplanned) | frame-reveal / bias-audit / decision-archaeology (pushed) |
| v0.5.0 | — | lens-semiotic + lens-ux variants (deferred medium-sensitivity) |

### Hard exclusions

- ❌ AI-generated translations of Anglo lens content (cosplay rigor)
- ❌ Per-language fixtures that are translations of v0.1.0 fixtures
- ❌ Korean / Vietnamese / Thai variants (permanent out-of-scope per ADR-0004)
- ❌ `lens-semiotic` / `lens-ux` variants (deferred to v0.5)

## [0.1.0] — 2026-05-04

Initial release. Plugin established as a reverse-engineering toolkit for
non-code artifacts (copy / document packs / UI / arguments / products /
organizations) — surfacing design blueprints, hidden frameworks, rhetorical
mechanisms, and intentional omissions.

### Added

#### Skills (4)
- **`using-deconstruct-toolkit`** — router. Two-axis routing (artifact-type
  default + user-intent override) + 3 filters (length / information-only /
  multi-modal) + 3 boundary checks (sourceatlas / philosophers-toolkit /
  forward-production plugins).
- **`artifact-deconstruct`** — flagship. 6-step workflow (type → lens select →
  6-dim run → lens apply → report → self-check) over a 6-lens library
  (semiotic / rhetoric / frame / genre / ux / persuasion) × 6-dimension
  analysis × ethical-position verdict.
- **`argument-deconstruct`** — argument-focused deep dive. Toulmin model
  (with 8 hidden-warrant patterns catalogued) + Burke pentad ratio analysis
  + mermaid argument map with hidden-warrant emphasis.
- **`assumption-surface`** — atomic skill. Reverse-Toulmin + Althusser-
  influenced symptomatic reading + 3-tier strength classification
  (foundational / load-bearing / decorative) + falsifiability tests.

#### Lens references (9)
- 6 in `artifact-deconstruct/references/`: semiotic (Barthes 1970), rhetoric
  (Burke 1945 + Toulmin 1958), frame (Goffman 1974 + Lakoff 1980), genre
  (Swales 1990 + Bhatia 1993), ux (Norman 1988/2013 + Nielsen 1994/2020),
  persuasion (Cialdini 2021 + Brignull 2024).
- 2 in `argument-deconstruct/references/`: lens-toulmin, lens-burke-pentad
  (split from artifact-deconstruct's combined lens-rhetoric for deeper
  argument focus).
- 1 in `assumption-surface/references/`: lens-symptomatic-reading
  (Althusser 1968/1970 *Reading Capital*, simplified-and-operationalized).

Each lens reference opens with a version-locked primary-source citation
per [ADR-0002](docs/adr/0002-strict-skill-self-containment.md) §5.3.1.

#### Eval suite (7 cases)
- 3 cases for `artifact-deconstruct`: Dropbox landing 2024, Notion onboarding
  pack, Stripe signup flow.
- 2 cases for `argument-deconstruct`: op-ed on AI regulation (synthetic),
  VC pitch memo (synthetic Series A).
- 2 cases for `assumption-surface`: Q3 SaaS strategy memo (synthetic), tweet
  thread on productivity (synthetic).

Each case is a YAML spec in `eval/cases/`. Each fixture has a
`## Annotations for evaluator` block specifying must_find expectations
as ground truth.

#### Tooling
- `scripts/check-eval-cases.py` — structural validator. Verifies eval YAMLs
  well-formed, fixtures exist + have annotation blocks, lens references
  have primary-source citations, skill folders are flat. CI-runnable, no
  PyPI dependency. Exit 1 on any failure.

#### Documentation
- [README.md](README.md) / [README.ja.md](README.ja.md) /
  [README.zh-TW.md](README.zh-TW.md) — tri-language plugin documentation.
  JP version anchors with BCG「バリュー・チェーンの脱構築」(Evans &
  Wurster, 2000) and 山口周『武器になる哲学』(2018); ZH version with
  Derrida → BCG/山口周 中文 lineage.
- [docs/design-proposal.md](docs/design-proposal.md) — full v0.1.0 design
  blueprint with 14 sections, 11 design decisions resolved, 7 eval cases
  spec.
- [docs/adr/0001-convention-b-mixed-naming.md](docs/adr/0001-convention-b-mixed-naming.md)
  — naming convention decision record.
- [docs/adr/0002-strict-skill-self-containment.md](docs/adr/0002-strict-skill-self-containment.md)
  — lens cross-skill strategy decision record (strict self-containment +
  4 anti-drift mechanisms).
- [eval/README.md](eval/README.md) — eval suite documentation including
  manual LLM-eval workflow until v1.0 runner.

#### Glossary entries (cross-plugin)
- 22 zh-TW + 24 ja terms added to `monkey-skills/docs/i18n/glossary-{ja,zh-TW}.md`
  under new "文物解構域 / 文物脱構築領域" sections. Locked terms include
  deconstruct / artifact / lens / frame + Toulmin set + UX set + Burke set
  + symptomatic-reading + boundary terms (teardown / reverse-engineering
  marked as **not used** in this plugin to enforce semantic precision).

### Design decisions

11 decisions resolved on 2026-05-04 (full record in
`docs/design-proposal.md` §12 Resolved Decisions):

- Eval fixtures: real public artifacts (URL + access date + fair-use)
- `assets/samples/` nesting: flat (`assets/sample-<name>.md`) — zero hook risk
- MVP: 4 skills (router + artifact + argument + assumption)
- `lens` term: keep English in body across all 3 languages
- Fixtures storage: in-repo Markdown (≤5KB each, CI runs offline)
- `marketplace.json`: same PR
- Convention B (mixed naming) accepted → ADR-0001
- Boundary fences accepted including exclusion of `enterprise-rollout-pack`
- 10 primary-source grounding accepted
- Strict skill self-containment over SSOT pattern → ADR-0002
- Tri-language description draft accepted

### Roadmap

See [README.md §Roadmap](README.md#roadmap) for v0.1 → v1.0 path.
Next minor version (v0.2.0) adds `product-deconstruct` and `pricing-decode`
(business-domain expansion).

[0.1.0]: https://github.com/kouko/monkey-skills/releases/tag/deconstruct-toolkit-v0.1.0
