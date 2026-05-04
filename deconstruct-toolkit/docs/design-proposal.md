---
title: deconstruct-toolkit Plugin Design Proposal
type: plugin-design-proposal
date: 2026-05-04
status: approved
approved_date: 2026-05-04
approved_by: kouko
target_plugin_name: deconstruct-toolkit
target_repo: monkey-skills
target_branch: feat/deconstruct-toolkit
mvp_version: v0.1.0
---

# deconstruct-toolkit — Plugin Design Proposal

> **One-liner**: A toolkit for reverse-engineering polished artifacts (copy, UI, document packs, arguments, products, organizations) — surfacing design blueprints, hidden frameworks, rhetorical mechanisms, and intentional omissions. Grounded in Derrida (philosophical), BCG (business strategy), Lakoff (frame), Barthes (semiotic), Toulmin (argument), Cialdini (persuasion).

**Status**: approved 2026-05-04 · **Branch**: `feat/deconstruct-toolkit` · **Author**: kouko · **Date**: 2026-05-04

---

## Table of Contents

1. [Motivation](#1-motivation)
2. [Scope & Boundary](#2-scope--boundary)
3. [Naming Convention (Convention B)](#3-naming-convention-convention-b)
4. [MVP v0.1 — 4 件套](#4-mvp-v01--4-件套)
5. [Lens Shared Library](#5-lens-shared-library)
6. [Primary-Source Grounding](#6-primary-source-grounding)
7. [i18n / Tri-language Description](#7-i18n--tri-language-description)
8. [Roadmap v0.1 → v1.0](#8-roadmap-v01--v10)
9. [Eval Cases (write evals first)](#9-eval-cases-write-evals-first)
10. [Risk Register](#10-risk-register)
11. [Plugin File Structure](#11-plugin-file-structure)
12. [Resolved Decisions](#12-resolved-decisions-was-open-questions)

---

## 1. Motivation

### 1.1 Why now

Three signals converge:

1. **Scattered "reverse" skills exist across monkey-skills but lack a coherent surface**: 9 skills already perform some kind of reverse operation (`socratic-method`, `descartes-methodical-doubt`, `popper-falsifiability`, `complexity-critique`, `proposal-critique`, `skill-judge`, `copywriting-audit-stage`, sourceatlas's reverse skills) — but they are dispersed across 4 plugins, with no shared lens library or unified mental model.

2. **A concrete v0.1 design already exists**: kouko's research note `2026-05-04 SKILL.md 設計提案——artifact-deconstruct.md` provides a complete spec for the flagship skill, including 6-lens library, 6-dimension analysis, eval cases, and skill-creator-advance handoff brief.

3. **Market gap in the Claude Code plugin ecosystem**: existing reverse-engineering plugins (DEFRA `claude-legacy-reveng-plugin`, `android-reverse-engineering-skill`, `claude-code-analysis`) are all **code-focused**. **No plugin targets non-code artifact deconstruction** (copy, UI, playbook, argument, strategy). This is a structural opportunity.

### 1.2 Why "deconstruct" (vs teardown / reverse-engineering)

Web research (2026-05-04) confirms three terms have **distinct industry meanings**:

| Term | Domain dominance | Semantic core |
|---|---|---|
| **Reverse Engineering** | Engineering / hardware / code | Disassemble to **replicate** |
| **Teardown** | Product / consumer apps / hardware | Disassemble to **understand strategy** |
| **Deconstruct** | Philosophy / design criticism / BCG strategy | Reveal **hidden structure & oppositions** |

Our 6-lens × 6-dimension methodology aligns most precisely with **deconstruct** — it surfaces implicit warrants, binary oppositions, and design decisions, not just disassembles.

The Japanese reception is especially strong: BCG's 「バリュー・チェーンの脱構築」is a canonical business-analysis term in Japan, with treatment in Frontier Eyes, MindMeister (山口周『武器になる哲学』), Japan Research Institute, and 一般社団法人グローバル都市経営学会. This gives the Japanese plugin description a strong cultural anchor.

### 1.3 Why a new plugin (not extend existing)

Boundary analysis against existing plugins:

| Plugin | Description | Why artifact-deconstruct doesn't fit |
|---|---|---|
| `copywriting-toolkit` | Pipeline-structured copy **production** | Wrong direction (forward, not reverse); only lens-persuasion / lens-rhetoric overlap; lens-ux / lens-genre / lens-semiotic unrelated to copy production |
| `dev-workflow` | Skill creation + **dev-artifact critique** (proposals / changes / skills) | Object mismatch: `dev-workflow`'s critique trio targets dev artifacts, not external marketing / UX / playbook artifacts |
| `domain-teams` | Worker + evaluator + checkpoint gate **team shape** | Abstraction mismatch: teams have worker/evaluator agents; deconstruct skills are analytical tools, not teams |
| `philosophers-toolkit` | Philosophical thinking for **self-reflection** | Object mismatch: philosophers act on `you vs your problem`; deconstruct acts on `you vs external object` |
| `sourceatlas` | **Codebase** reverse-engineering | Object mismatch: covers code; we cover non-code artifacts |

A new plugin is the cleanest home.

---

## 2. Scope & Boundary

### 2.1 What this plugin does

Operates on **external, polished, non-code artifacts** with reverse-direction analysis:

- Marketing copy, landing pages, advertising
- Document packs (playbooks, SOPs, onboarding kits)
- Presentation decks, slide narratives
- UI screens, app onboarding flows
- Long-form arguments (proposals, op-eds, political texts)
- Products (SaaS / app strategy, pricing, retention loops)
- Organizations (org charts, job postings, strategy artifacts)
- Literature, film, advertising imagery (semiotic)

### 2.2 What this plugin does NOT do

Hard fences against scope creep:

| Excluded | Reason | Lives in |
|---|---|---|
| Codebase reverse-engineering | sourceatlas already does this well | `sourceatlas` (impact / flow / overview / pattern / deps) |
| Self-thinking / problem clarification | Different abstraction — operates on `you vs your problem` | `philosophers-toolkit` |
| Dev-artifact critique (proposals / commits / skills) | Different domain | `dev-workflow` (proposal-critique / complexity-critique / skill-judge) |
| Forward-direction copy / doc / design production | This is a reverse toolkit; production lives elsewhere | `copywriting-toolkit`, `docs-team`, `design-team` |
| Investment / equity reverse-engineering | Domain-specific, has its own grounding stack | `investing-toolkit` |

### 2.3 Boundary statement (will be in plugin README)

> `deconstruct-toolkit` reverses external, polished, non-code artifacts to surface their hidden design. For codebase reverse use `sourceatlas`. For self-reflection / problem clarification use `philosophers-toolkit`. For dev-artifact critique use `dev-workflow`. For forward-direction copy / doc / design production use `copywriting-toolkit` / `docs-team` / `design-team`.

---

## 3. Naming Convention (Convention B)

Following the trade-off analysis from research:

### 3.1 Rule

```
Mainstream skills:        <noun>-deconstruct          (artifact / argument / product / org / pricing)
Specialized verb skills:  <noun>-<verb>               (assumption-surface / frame-reveal / bias-audit)
Router skill:             using-deconstruct-toolkit   (matches existing router pattern)
```

### 3.2 Why mixed (Convention B) — not strict suffix (Convention A)

- `bias-deconstruct` is semantically wrong — bias is *exposed*, not *deconstructed*
- `assumption-deconstruct` loses the precision of `surface` (= bring up from below)
- `frame-deconstruct` is acceptable but `reveal` is more vivid

Forcing every skill into `<noun>-deconstruct` would either degrade naming precision or exclude legitimate family members. Mixed naming preserves semantic accuracy.

### 3.3 Naming gate

Every new skill in this plugin **must** pass two checks:
1. **Verb gate**: the skill verb belongs to the deconstruct family — `deconstruct / surface / reveal / audit / decode / expose / archaeology`
2. **Object gate**: the skill object is an external, polished, non-code artifact (per §2.1)

If a proposed skill fails either gate, it does not belong in this plugin.

### 3.4 Precedent in monkey-skills

This pattern is validated:
- `copywriting-toolkit` has 14 skills with `copywriting-*` prefix but stage names vary (`intake / ideation / audit / form-check / neta-injection`)
- `philosophers-toolkit` has skills named after philosophers with no shared verb suffix

---

## 4. MVP v0.1 — 4 件套

The minimum-viable plugin proves "this is not a 1-skill plugin" while keeping marginal cost low.

### 4.1 Skill 1: `using-deconstruct-toolkit` (router)

**Role**: route user intent to the right skill. Mirrors `using-copywriting-toolkit` / `using-philosophers-toolkit` pattern.

**Trigger phrases (any language)**:
- 「拆解 / 反推 / 解構 / 反向分析 / teardown / deconstruct / reverse-engineer」
- 「為什麼這份寫得這麼好」「這個 SOP 是怎麼設計的」「這個落地頁的設計」

**Decision tree**:
```
Artifact type?
├─ Marketing copy / landing / advertising → artifact-deconstruct (lens-persuasion + lens-rhetoric)
├─ Document pack / playbook / SOP         → artifact-deconstruct (lens-genre + 6-dim)
├─ UI / onboarding flow                   → artifact-deconstruct (lens-ux + lens-persuasion)
├─ Long-form argument / op-ed / proposal  → argument-deconstruct (Toulmin + warrant surface)
├─ Hidden assumptions in any text         → assumption-surface
└─ Speech / political text / literature   → artifact-deconstruct (lens-rhetoric + lens-frame)
```

**Output**: dispatches user to the correct sibling skill with the lens preselected.

### 4.2 Skill 2: `artifact-deconstruct` (flagship)

Full spec already written in `2026-05-04 SKILL.md 設計提案——artifact-deconstruct.md`. Adapted to monkey-skills convention:

```
deconstruct-toolkit/skills/artifact-deconstruct/
├── SKILL.md                      ~180 行 / ~1500 tokens
├── protocols/
│   ├── six-dimensions.md         6-dim 分析 prompt 集
│   └── lens-selection.md         lens 選擇決策樹
├── references/
│   ├── lens-semiotic.md          Barthes 5 codes
│   ├── lens-rhetoric.md          Burke pentad + Toulmin
│   ├── lens-frame.md             Goffman + Lakoff
│   ├── lens-genre.md             Swales CARS + Bhatia
│   ├── lens-ux.md                NN/g + Norman
│   └── lens-persuasion.md        Cialdini 7 + Brignull dark patterns
├── assets/
│   ├── report-template.md        6-section output template
│   └── samples/                  eval fixtures (3 worked examples)
│       ├── dropbox-landing-2024.md
│       ├── notion-onboarding-pack/
│       └── stripe-signup-flow.md
└── checklists/
    └── anti-patterns.md          self-check before delivery
```

**Note**: subfolder structure conforms to monkey-skills CLAUDE.md rule (single-level subfolders, no nesting). Original `~/.claude/skills/` flat layout from the research note has been **rearranged** to fit repo convention.

**Eval gate before merge**: must pass 3 worked-example eval cases (see §9.1).

### 4.3 Skill 3: `argument-deconstruct`

**Why split from artifact-deconstruct**: when the artifact is *primarily* an argument (op-ed, proposal, political text, paper introduction), full 6-lens overkill — Toulmin alone gets 80% of the value.

**Lens stack**:
- Toulmin model (Claim / Grounds / Warrant / Backing / Rebuttal / Qualifier)
- Burke's pentad ratio analysis
- Hidden warrant surfacing (the critical move)
- Genre move analysis (Swales CARS for academic; rollout-doc moves for business)

**Output**: argument map (mermaid) + warrant explicitization + missing-rebuttal table + ethical position.

**Length**: ~150 lines SKILL.md + 1 protocol + 2 references + 1 example.

### 4.4 Skill 4: `assumption-surface`

**Why standalone**: hidden-assumption surfacing is a frequent atomic operation that doesn't always need full deconstruction. It's a high-value tactical skill.

**Method**:
1. **Reverse-Toulmin** — for each claim, identify the warrant the writer would have to believe
2. **Symptomatic reading** (after Althusser) — what is *not said* that is necessary for the claim to hold
3. **Counterfactual probe** — "if the opposite were true, would the artifact still cohere?"
4. **Frame audit** — what is the implicit world-model? (Lakoff lite)

**Output**: assumption table (5–15 rows) with strength rating (foundational / load-bearing / decorative) + falsifiability check per assumption.

**Length**: ~120 lines SKILL.md + 1 protocol + 1 reference + 1 example.

### 4.5 Why these 4 (not 3, not 5)

| Skill | Marginal cost | Marginal value | Verdict |
|---|---|---|---|
| using-* router | Low (template available) | High (signals plugin shape) | Required |
| artifact-deconstruct | High (6 lenses + 3 evals) | Highest (the flagship) | Required |
| argument-deconstruct | Low (reuses lens-rhetoric) | High (atomic, frequently needed) | Required — proves "not 1-skill plugin" |
| assumption-surface | Low (~120 lines) | High (atomic, useful in many workflows) | Required — proves family naming Convention B |
| product-teardown / pricing-decode / etc. | Higher (new lens library) | Medium | Defer to v0.2 |

**4 is the smallest set that demonstrates** (a) plugin shape, (b) flagship depth, (c) atomic skills, (d) Convention B naming.

---

## 5. Lens Cross-skill Strategy

### 5.1 Decision: strict skill independence (Anthropic compliance)

**Adopted on 2026-05-04**: each skill is fully self-contained with its own `references/lens-*.md`. **No plugin-level SoT directory. No cross-skill imports.**

Rationale: Anthropic's official Skills convention emphasizes that each skill is independently loadable and self-describing. SSOT-and-functional-copy (pattern from PR #159, used cross-plugin) was considered but rejected here because:

1. The cross-plugin SSOT use case (PR #159) is materially different — there each consumer is in a different plugin (no in-plugin alternative)
2. Within one plugin, allowing skills to reference plugin-level SoT erodes the independence principle
3. Skill consumers (e.g., `dev-workflow:skill-creator-advance`) load one skill's directory at a time; plugin-level SoT is invisible to them
4. Anthropic best-practice docs treat each skill as a self-contained unit of progressive disclosure

### 5.2 The shared-content reality

6 lenses appear across multiple skills. Each skill ships its own copy:

| Lens | artifact | argument | assumption | future product | future pricing |
|---|---|---|---|---|---|
| Toulmin (argument model) | ✓ | ✓ | ✓ | | |
| Cialdini 7 (persuasion) | ✓ | | | ✓ | ✓ |
| Lakoff (frame metaphor) | ✓ | ✓ | ✓ | ✓ | |
| Brignull dark patterns | ✓ | | | ✓ | ✓ |
| Bhatia genre moves | ✓ | ✓ | | | |
| NN/g 10 heuristics | ✓ | | | ✓ | |

This means up to 5 copies of `lens-cialdini` content across the plugin at v1.0. **This duplication is intentional, not accidental.**

### 5.3 Anti-drift mitigation (without violating self-containment)

Manual but disciplined:

1. **Primary-source anchor at top of every lens file** — each `references/lens-*.md` opens with version-locked citation:
   > Source: Cialdini, *Influence: The Psychology of Persuasion*, expanded ed. (Harper Business, 2021). Ch 3 pp 84-98.

   This locks the version. Anyone editing must respect the same source.

2. **Different operationalizations are allowed and expected** — `lens-persuasion` in `artifact-deconstruct` may emphasize different examples than the same lens in `product-deconstruct`. The lens files do NOT need to be byte-identical; they need to be *primary-source-faithful*.

3. **Quarterly skill audit** (already in dev-workflow `quarterly-audit-runbook.md`) folds in lens consistency check: when 2+ skills cite the same primary source, audit confirms (a) version consistency, (b) no contradictions in core method.

4. **Same-PR conscientiousness rule** — when a PR touches a lens that lives in multiple skills, the PR description must list all instances and either justify why only one is changed, or update all consistently.

### 5.4 Trade-off accepted

| Cost | Benefit |
|---|---|
| Up to 5x duplication for high-reuse lenses (Cialdini / Lakoff / Toulmin) | Each skill is independently loadable per Anthropic spec |
| Manual sync discipline required when primary sources update | No CI complexity, no functional-copy headers, no SSOT lint |
| Risk of slow drift between same-source lenses | Skills can specialize lens operationalization without shared-file constraint |

**Why this is fine**: lens content is grounded in published primary sources (Cialdini 2021 ed., Toulmin 1958, Lakoff & Johnson 1980). These do not change frequently. Drift over months is recoverable; drift over years is unlikely without external trigger (new edition).

---

## 6. Primary-Source Grounding

Following copywriting-toolkit / philosophers-toolkit / domain-teams precedent: every method should trace to a primary source.

### 6.1 Grounding sources (10)

| # | Source | Provides | Used in |
|---|---|---|---|
| 1 | Derrida《Of Grammatology》《Writing and Difference》 | Philosophical foundation: deconstruction as binary-opposition reveal | All skills (philosophical anchor) |
| 2 | Barthes《S/Z》(1970) | 5 codes (HER / PRO / SEM / SYM / REF) | lens-semiotic |
| 3 | Burke《A Grammar of Motives》(1945) | Dramatistic pentad + ratios | lens-rhetoric / argument-deconstruct |
| 4 | Toulmin《The Uses of Argument》(1958) | 6-component argument model | lens-rhetoric / argument-deconstruct / assumption-surface |
| 5 | Goffman《Frame Analysis》(1974) | Primary framework / keying / fabrication / frame break | lens-frame |
| 6 | Lakoff & Johnson《Metaphors We Live By》(1980) | Conceptual metaphor source-target mapping | lens-frame / assumption-surface |
| 7 | Swales《Genre Analysis》(1990) + Bhatia《Analysing Genre》(1993) | CARS + move analysis | lens-genre |
| 8 | Cialdini《Influence》(latest 2021) | 7 principles (incl. unity) | lens-persuasion |
| 9 | Brignull `deceptive.design` (12 patterns, 2024) | Dark pattern taxonomy | lens-persuasion / lens-ux |
| 10 | Nielsen 10 heuristics + Norman《Design of Everyday Things》(1988, rev. 2013) | UX critique | lens-ux |

### 6.2 BCG / Yamaguchi Shu as practitioner anchor (JP/biz)

For the Japanese / business audience, supplementary anchors (not primary methods, but credibility hooks):
- BCG《Blown to Bits》(Evans & Wurster, 2000) — value-chain deconstruction
- 山口周『武器になる哲学』(2018) — popular treatment of 脱構築 in business

These appear in JP README and `using-deconstruct-toolkit` description, not in skill methodology proper.

### 6.3 Citation discipline

Every lens reference file must:
- Open with **primary source citation** (author, work, year)
- Include **page-number-level pointer** for at least 1 key concept
- Distinguish **method as written by the author** vs **operationalization for this skill**
- Avoid synthesizing across primary sources without flagging

This matches domain-teams citation grounding standards.

---

## 7. i18n / Tri-language Description

Per repo convention (PR #150) every plugin has 3-language README + glossary.

### 7.1 plugin.json description (one-line, tri-language)

```json
{
  "name": "deconstruct-toolkit",
  "version": "0.1.0",
  "description": "Reverse-engineer polished artifacts (copy, document packs, UI, arguments, products) — surface design blueprints, hidden frameworks, rhetorical mechanisms, intentional omissions. Grounded in Derrida, Barthes, Toulmin, Lakoff, Goffman, Cialdini, Bhatia, Nielsen-Norman. 文物・論証・製品の脱構築。BCG バリュー・チェーン脱構築の系譜。文物・論證・產品的逆向解構工具組。"
}
```

### 7.2 README opening anchors

**EN** (`README.md`):
> Reverse-engineer polished artifacts to surface design decisions, borrowed frameworks, rhetorical mechanisms, and intentional omissions. Where `sourceatlas` reverses code and `philosophers-toolkit` clarifies your own thinking, `deconstruct-toolkit` deconstructs external, polished, non-code artifacts.

**JP** (`README.ja.md`):
> 制作物（コピー、ドキュメントパック、UI、論証、製品、組織）を逆向きに分解し、設計判断・借用フレームワーク・修辞メカニズム・意図的な省略を可視化するツールキット。BCG「バリュー・チェーンの脱構築」(Evans & Wurster) と山口周『武器になる哲学』に登場する脱構築方法論を、Derrida / Barthes / Toulmin / Lakoff / Goffman / Cialdini の primary source に紐付けて agent skill として実装。

**ZH-TW** (`README.zh-TW.md`):
> 將精緻文物（文案、文件包、UI、論證、產品、組織）進行逆向解構，揭露設計決策、借用框架、修辭機制、與刻意省略。理論底座結合 Derrida（哲學）、Barthes（符號學）、Toulmin（論證）、Lakoff（框架）、Goffman（社會框架）、Cialdini（說服）、Bhatia（體裁）、Nielsen-Norman（UX）八大傳統。

### 7.3 Glossary discipline (`docs/i18n/glossary-{en,ja,zh-TW}.md`)

Lock these terms early to prevent translation drift:

| EN | JP | ZH-TW | Note |
|---|---|---|---|
| deconstruct | 脱構築 | 解構 | Never localize as デコンストラクション in body (verbose) — only in title |
| artifact | 制作物 / アーティファクト | 文物 | JP prefers 制作物 (concrete) over アーティファクト (loanword) |
| lens | レンズ | 透鏡 (lens) — keep English term `lens` in body | ZH: keep English to avoid 透鏡 (optical-only connotation) |
| frame | フレーム | 框架 | |
| warrant | ウォラント / 論拠 | 論證根據 / warrant | Toulmin 譯名兩可，body 直接保留 warrant |
| dark pattern | ダークパターン | 黑暗模式 / dark pattern | |
| binary opposition | 二項対立 | 二元對立 | |
| affordance | アフォーダンス | affordance | ZH 沒有確立譯名，保留英文 |

---

## 8. Roadmap v0.1 → v1.0

### 8.1 Version path

| Version | Scope | Skills | New material |
|---|---|---|---|
| **v0.1.0** | MVP (this proposal) | 4 | router + artifact + argument + assumption — 6 lenses, 10 grounding sources, 3 eval cases |
| **v0.2.0** | Expand to product/business | +2 | `product-deconstruct`, `pricing-decode` — adds business-model lens, pricing psychology lens |
| **v0.3.0** | Atomic deepenings | +3 | `frame-reveal`, `bias-audit`, `decision-archaeology` |
| **v1.0.0** | Hardening | (no new skills) | 20+ real eval cases, fixture corpus, JP-region case study, open-source release polish |

### 8.2 Excluded from this plugin (v0.1 boundary)

- **enterprise-rollout-pack** (originally proposed in artifact-deconstruct §10.3 as forward-direction sibling) — does NOT belong here (forward production, not reverse). To live in `copywriting-toolkit` or `docs-team`, or as separate plugin.
- **codebase-reverse** — covered by `sourceatlas`
- **investment thesis reverse** — covered by `investing-toolkit:report-equity-memo` (forward) and not currently a reverse skill candidate

### 8.3 Cadence

- v0.1 → v0.2: ~1 month after v0.1 lands
- v0.2 → v0.3: ~1 month after v0.2 lands
- v1.0: when 20 real-world eval cases pass

---

## 9. Eval Cases (write evals first)

Per Anthropic guidance ("write eval before skill"), every skill ships with passing eval cases.

### 9.1 artifact-deconstruct (3 cases)

```yaml
case_1:
  artifact: dropbox-landing-2024.md
  query: "拆解這個 Dropbox 落地頁的設計"
  expected_lenses: [lens-persuasion, lens-rhetoric]
  must_find:
    - at_least_4_of_cialdini_7
    - PASONA_or_AIDA_structure_in_hero
    - social_proof_elements_named
    - ethical_position_assigned

case_2:
  artifact: notion-onboarding-pack/
  query: "拆解 Notion 的 onboarding 文件包"
  expected_lenses: [lens-genre]
  expected_dimensions: ALL_6
  must_find:
    - at_least_6_components_in_pack
    - probable_writing_order_inferred
    - audience_layering_identified
    - at_least_3_negative_space_observations
    - at_least_1_inherited_framework_named

case_3:
  artifact: stripe-signup-flow-screenshots/
  query: "拆解 Stripe 註冊流程"
  expected_lenses: [lens-ux, lens-persuasion]
  must_find:
    - all_10_nielsen_heuristics_applied
    - at_least_3_affordances_analyzed
    - all_12_dark_patterns_checked
    - ethical_position_per_persuasion_principle
```

### 9.2 argument-deconstruct (2 cases)

```yaml
case_1:
  artifact: op-ed-on-AI-regulation.md
  query: "拆解這篇社論的論證結構"
  must_find:
    - claim_grounds_warrant_explicit
    - at_least_2_hidden_warrants_surfaced
    - missing_rebuttal_named
    - qualifier_or_lack_of_qualifier_called_out

case_2:
  artifact: vc-pitch-memo.md
  query: "拆解這份創投備忘錄的論證"
  must_find:
    - genre_move_map (problem / opportunity / solution / traction / ask)
    - at_least_1_burke_pentad_ratio
    - argument_map_mermaid_rendered
```

### 9.3 assumption-surface (2 cases)

```yaml
case_1:
  artifact: company-strategy-memo.md
  query: "揭露這份策略備忘錄的隱性假設"
  must_find:
    - assumption_table (10-15 rows)
    - foundational_vs_load_bearing_vs_decorative_classification
    - at_least_1_falsifiability_test_per_foundational_assumption

case_2:
  artifact: tweet-thread-on-productivity.md
  query: "這串推文背後的假設是什麼"
  must_find:
    - implicit_world_model_named
    - at_least_3_counterfactual_probes
```

### 9.4 Eval scoring

| Score | Criterion |
|---|---|
| 🟢 PASS | 100% must_find satisfied |
| 🟡 PARTIAL | 70%+ |
| 🔴 FAIL | <70% OR wrong lens chosen |

CI runs eval cases on every PR touching the relevant skill.

---

## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Scope creep** ("analysis toolkit" 總集) | High | High | Plugin description locks verbs (deconstruct/surface/reveal/audit/decode/expose); §3.3 naming gate; §2.2 hard fences |
| **Boundary collision with philosophers-toolkit** (Socratic vs assumption-surface) | Medium | Medium | self-vs-artifact distinction; cross-link router skills; READMEs explicitly disclaim |
| **Boundary collision with sourceatlas** | Low | Medium | Hard fence: this plugin excludes code; README explicit |
| **Lens drift across skills** | Medium-High | Medium | Strict skill self-containment (§5.1) means up to 5x duplication is accepted by design. Mitigated via version-locked primary-source anchors at top of each lens file (§5.3.1), quarterly audit (§5.3.3), and same-PR conscientiousness rule (§5.3.4). Drift is recoverable not catastrophic. |
| **Fixture sample shortage** | High | Medium | 3 worked examples per skill at v0.1; build curated fixture corpus toward v1.0 |
| **Highbrow signaling** (deconstruct = 文青 詞) | Medium | Low | Plugin description leads with concrete verbs ("reverse-engineer / surface / decode"); BCG anchor in JP |
| **JP destructuring confusion** (脱構築 vs JS destructuring) | Low | Low | JP README opens with BCG / 山口周 anchor — disambiguates immediately |
| **MVP not proving "not 1-skill plugin"** | Low | High | 4-skill MVP (router + 3 substantive); §4.5 rationale |
| **Eval fixture copyright** (using real Dropbox / Notion / Stripe artifacts) | Medium | Medium | Use publicly-accessible artifacts; cite URL + access date; treat as fair-use educational analysis (no full reproduction) |
| **Skill author drift from primary sources** | Medium | High | §6.3 citation discipline; lens reference files must lead with primary source citation |

---

## 11. Plugin File Structure

```
deconstruct-toolkit/
├── .claude-plugin/
│   └── plugin.json
├── README.md                                  ← EN
├── README.ja.md                               ← JP (BCG anchor)
├── README.zh-TW.md                            ← ZH-TW
├── CHANGELOG.md
├── docs/
│   ├── i18n/
│   │   ├── glossary-en.md
│   │   ├── glossary-ja.md
│   │   └── glossary-zh-TW.md
│   ├── design-proposal.md                     ← this file
│   └── adr/                                   ← future decision records
│       └── 0001-convention-b-mixed-naming.md  ← v0.1.0 ships with this
└── skills/
    ├── using-deconstruct-toolkit/
    │   └── SKILL.md
    ├── artifact-deconstruct/
    │   ├── SKILL.md
    │   ├── protocols/
    │   │   ├── six-dimensions.md
    │   │   └── lens-selection.md
    │   ├── references/
    │   │   ├── lens-semiotic.md
    │   │   ├── lens-rhetoric.md
    │   │   ├── lens-frame.md
    │   │   ├── lens-genre.md
    │   │   ├── lens-ux.md
    │   │   └── lens-persuasion.md
    │   ├── assets/
    │   │   ├── report-template.md
    │   │   ├── sample-dropbox-landing-2024.md
    │   │   ├── sample-notion-onboarding-pack.md
    │   │   └── sample-stripe-signup-flow.md
    │   └── checklists/
    │       └── anti-patterns.md
    ├── argument-deconstruct/
    │   ├── SKILL.md
    │   ├── protocols/
    │   │   └── argument-mapping.md
    │   ├── references/
    │   │   ├── lens-toulmin.md
    │   │   └── lens-burke-pentad.md
    │   └── assets/
    │       ├── sample-op-ed-AI-regulation.md
    │       └── sample-vc-pitch-memo.md
    └── assumption-surface/
        ├── SKILL.md
        ├── protocols/
        │   └── reverse-toulmin.md
        ├── references/
        │   └── lens-symptomatic-reading.md
        └── assets/
            ├── sample-company-strategy-memo.md
            └── sample-tweet-thread-productivity.md
```

**Total file count** at v0.1.0: ~35 files, ~12-15k tokens written content.

**Compliance with monkey-skills CLAUDE.md**:
- ✅ All subfolders are single-level — no `assets/samples/` nesting
- ✅ Fixture files use flat naming `sample-<name>.md` directly under `assets/`
- ✅ Zero risk against `.claude/hooks/validate-skill-folder-structure.sh`

---

## 12. Resolved Decisions (was: Open Questions)

All 6 open questions answered by kouko on 2026-05-04:

| # | Question | Decision | Implication |
|---|---|---|---|
| Q1 | Eval fixtures: real vs synthetic | **Real public artifacts** (Dropbox / Notion / Stripe) with URL + access date | Treat as fair-use educational analysis. Each fixture leads with `Source: <URL>` and `Accessed: YYYY-MM-DD`. |
| Q2 | `assets/samples/` nesting | **Flat layout** — `assets/sample-<name>.md` directly under `assets/` | Zero hook risk. §11 file structure already updated. |
| Q3 | MVP size | **4 skills** (router + artifact-deconstruct + argument-deconstruct + assumption-surface) | `product-deconstruct` and `pricing-decode` strictly deferred to v0.2.0. |
| Q4 | `lens` term in body | **Keep English `lens`** in JP / ZH-TW body | Glossary entry §7.3 final. Avoids ZH 透鏡 (optical-only) ambiguity; aligns with PR #150 English-noun-preservation rule. |
| Q5 | Fixture storage | **All in repo** as Markdown text (≤5KB each) | CI runs offline, no fetch dependency. Fixtures hand-converted from HTML using defuddle / manual cleanup — no screenshots. |
| Q6 | `marketplace.json` update | **Same PR** as plugin v0.1.0 | Follows PR #4 full-plugins-array format. Plugin installable from day one. |

### 12.1 Resolution-driven follow-ons

- §11 file structure updated to flat `assets/sample-*.md` (Q2)
- §13 Implementation Sequence Commit 9 confirms `marketplace.json` in same PR (Q6)
- §10 Risk Register: copyright risk re-rated — fair-use educational stance with URL + access date is the active mitigation (Q1)
- §7.3 Glossary entry for `lens` finalized (Q4)
- §9 Eval cases stay at 7 (3 + 2 + 2) for the 4-skill MVP (Q3)
- §11 Total file count adjusted: ~35 files becomes the firm figure under flat layout (Q2)

---

## 13. Implementation Sequence (post-approval)

After review and any revisions:

1. **Commit 1**: this proposal + ADR-0001 (Convention B) + ADR-0002 (strict skill self-containment, §5) — under `deconstruct-toolkit/docs/`
2. **Commit 2**: `plugin.json` + 3-lang `README.md` + glossary stubs
3. **Commit 3**: `using-deconstruct-toolkit` SKILL.md + decision tree
4. **Commit 4**: `artifact-deconstruct` skill — SKILL.md + 6 self-contained lens references + 2 protocols + 1 report template + 1 anti-pattern checklist + 3 fixtures
5. **Commit 5**: `argument-deconstruct` skill — SKILL.md + 2 self-contained lens references + 1 protocol + 2 fixtures
6. **Commit 6**: `assumption-surface` skill — SKILL.md + 1 self-contained lens reference + 1 protocol + 2 fixtures
7. **Commit 7**: eval CI hook — runs 7 cases against the 4 skills, blocks merge on FAIL
8. **Commit 8**: `marketplace.json` update + CHANGELOG.md + final README polish
9. **PR**: open as draft, run all evals, request review

Estimated effort: ~10-13 hours post-approval (down from 12-16h: removed plugin-level SoT lens authoring; lens content duplicated inside skills is faster to write than coordinating SoT + functional copy).

---

## 14. Approval Checklist

Before proceeding to implementation, confirm with user:

- [x] Plugin name `deconstruct-toolkit` final (2026-05-04)
- [x] Convention B (mixed naming) accepted (2026-05-04, will be ADR-0001)
- [x] MVP scope = 4 skills (router + artifact + argument + assumption) accepted (Q3)
- [x] Boundary fences (§2.2) accepted — including exclusion of `enterprise-rollout-pack` (2026-05-04)
- [x] 10 primary-source grounding list accepted (2026-05-04)
- [x] Lens cross-skill strategy: **strict skill self-containment** (Anthropic-compliant, §5 rewritten 2026-05-04, will be ADR-0002)
- [x] Tri-language description draft accepted (2026-05-04)
- [x] Open questions §12 answered (all 6 resolved 2026-05-04)

---

**End of proposal — ready for review.**
