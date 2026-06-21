# Research synthesis — spec-toolkit & OpenSpec (Station 1 / GENERATE)

> **Type**: research synthesis (decision aid; not a build spec, not a brief)
> **Date**: 2026-06-11
> **Driver**: kouko — "認真研究 spec-toolkit & OpenSpec" before any build. Station 1 (GENERATE) is the real open gap in the 4-station "stably produce code" pipeline.
> **Method**: deep-read 5 vault notes + repo OpenSpec brief + this session's 4-station eval, in parallel with a fresh EN+JA web check of OpenSpec's 2026-06 state.
> **Status**: research complete → awaiting go for brainstorm. **No code. No commit.**

---

## 0. The one-paragraph answer

The vault already did the hard thinking and reached a **sound, internally-consistent decision**: build **`spec-toolkit` as a separate plugin** (the GENERATE layer = USM×OOUX×state-grid spec-expansion engine), wire it to `code-toolkit` (the VERIFY layer) through an **OpenSpec change-folder as a neutral file-based contract** (the DECLARE layer). This session's job was to (a) verify that reasoning still holds and (b) re-check OpenSpec's fast-moving state. **Both check out — with three concrete reconciliations** the prior research explicitly flagged as "verify before building." Nothing forces a re-decision; the open work is a focused brainstorm → plan for spec-toolkit's MVP, plus a small refresh of the 2026-05-30 OpenSpec brief to current versions.

---

## 1. The settled model (do NOT re-litigate)

Three orthogonal layers, each its own plugin/tool, joined by a file contract:

| Layer | Job | Owner | Status |
|---|---|---|---|
| **GENERATE** | Expand a sparse seed → high-recall spec draft + edge cases + candidate acceptance criteria; completeness-critic finds blind spots | **`spec-toolkit`** (new plugin) | 🟡 designed, not built — **this is the gap** |
| **DECLARE** | Persist the spec as files; delta tracking (`ADDED/MODIFIED/REMOVED`); cross-session/tool durable | **OpenSpec** (`openspec/changes/<id>/`) | ✅ decision locked (brief Q1–Q9, 2026-05-30), unimplemented |
| **VERIFY** | Atomize → TDD → execution-gate → review; "trust is earned by execution, not by a spec that looks complete" | **`code-toolkit`** | ✅ shipped (v0.15.0, command-surface merged) |

Flow is **one-directional**: `spec-toolkit` *writes* → OpenSpec change-folder (contract) → `code-toolkit` *reads + verifies*. The single semantic joint is **`#### Scenario:` acceptance criteria → RED/GREEN tests**.

**Why separate, not crammed into code-toolkit** (vault packaging note §3, deep-research 24/25 claims confirmed): industry SDD tools split into two camps — *own-the-agent* tools (GitHub Spec Kit, AWS Kiro) integrate spec+implement as sequential phases; *layer-onto-an-agent* tools (OpenSpec, Tessl, BMAD) keep the spec layer independent and tool-agnostic. **code-toolkit is a layer-on tool** (it injects discipline into Claude Code via SessionStart hook; it does not own the agent) → its peer group is OpenSpec/Tessl/BMAD → its spec-generation layer should be **independent**. Tessl is the strongest single precedent: it deliberately ships "how to work" (SDD plugin) and "what tools" (registry plugin) as two separate versioned artifacts.

**No conflict with the locked OpenSpec hard-couple (Q6=A)**: that decision locked the **DECLARE** layer (OpenSpec as code-toolkit's persistence). spec-toolkit independence is about **GENERATE** — a different layer. The net effect is OpenSpec gets *promoted* from "code-toolkit's internal persistence" to "a shared neutral boundary artifact both plugins use." The Q6=A investment (safe-archive.sh, validate gate, 3-tier, version pin) is fully preserved.

---

## 2. OpenSpec — current 2026-06 state (the fresh, time-sensitive finding)

Re-checked live (npm registry API + GitHub API + official docs, 2026-06-11):

| Fact | Value | Source |
|---|---|---|
| Latest version | **1.4.1** (2026-06-03; 1.4.0 was 2026-06-01) | npm registry `@fission-ai/openspec` |
| Repo | still **`Fission-AI/OpenSpec`**, MIT, **pushed 2026-06-10** (active) | GitHub API |
| Traction | ~54k stars / 3.7k forks / 7 releases across 2026 (1.1.0 Jan → 1.4.1 Jun) | GitHub + npm |
| Install | `npm i -g @fission-ai/openspec@latest`; Node ≥ 20.19.0 | README |
| `openspec/` layout | `specs/` (source of truth, by domain) · `changes/` (active) · `changes/archive/` · `config.yaml` | docs/concepts.md |
| Change-folder | `proposal.md` + `design.md` + `tasks.md` + `specs/` (delta) + `.openspec.yaml` | docs/concepts.md |
| **Spec delta format** | `## ADDED/MODIFIED/REMOVED Requirements` → `### Requirement: …` (SHALL/MUST on the **body line**) → **`#### Scenario:` with GIVEN/WHEN/THEN/AND** (RFC-2119) | docs/concepts.md |
| **`openspec validate` scope** | **STRUCTURE ONLY** — "validate changes and specs for structural issues" (headers, scenario format, keyword placement). **No spec↔code alignment, no coverage, no completeness.** | docs/cli.md, concepts.md |

**Three things that CHANGED since the brief was written (early 2026 / v1.3.x) — these are the reconciliations:**

1. **Workflow model: rigid 3-phase → fluid "OPSX".** The old `propose → apply → archive` rigid phases are gone; v1.4 is "actions not phases." Current slash commands: `/opsx:propose`, `/opsx:apply`, `/opsx:archive`, **plus** `/opsx:new`, `/opsx:continue`, `/opsx:ff`, **`/opsx:verify`**, `/opsx:sync`, `/opsx:bulk-archive`, `/opsx:onboard`. → The vault packaging note's appendix A.3 "待辦: 落地前實跑一次 `openspec init` 確認命名" is now answered: **don't hard-code `propose/apply/sync/archive` — the namespace is `/opsx:*` and richer.**

2. **`/opsx:verify` is new (closes OpenSpec issue #381).** This is the maintainers acknowledging the exact gap the vault flagged: "today OpenSpec validates spec *structure*… no built-in way to verify alignment against an approved change." BUT — **it is an AI-prompt/slash-command workflow, NOT a deterministic checker.** The CLI `openspec validate` remains structure-only. → **The "規格層不驗對齊, 執行才是真理" thesis still holds at v1.4.1**; `/opsx:verify` does not replace code-toolkit's execution gate (it's LLM-driven, not execution-truth). Worth noting it exists so we don't reinvent its *prompt-template* role, but it is not a substitute for the VERIFY layer.

3. **New layers: workspaces + context-store/initiatives + `config.yaml`.** Multi-repo shared context (`workspace *`, `context-store *` CLI namespaces) and a `config.yaml` that injects stack/style/testing rules into the agent. → Mostly irrelevant to a monorepo (brief Q1 already chose single-root `openspec/`), but `config.yaml` is a *new* injection point worth a glance during plan.

**Critically unchanged (the load-bearing facts the whole design rests on):**
- OpenSpec is **still purely DECLARE/persistence** — no GENERATE layer, no completeness engine, no requirement expansion. "Generation" is whatever the connected LLM does at `/opsx:propose` time. **spec-toolkit fills a real, un-filled gap — it is not reinventing anything OpenSpec ships.**
- Its agent template is still **"lightweight by default / smallest testable spec"** — the *opposite* design philosophy to spec-toolkit's "systematically expand all paths/edges." → They reconcile via **proportional rigor**: routine change → OpenSpec lightweight; high-risk change → call spec-toolkit for full fan-out. OpenSpec decides *whether to call* the engine; the engine does *the covering*. No philosophy clash.
- The delta format **is** `#### Scenario:` Gherkin — so the contract joint (scenario → RED/GREEN) is real and current. **One refinement: it's GIVEN/WHEN/THEN/AND, not bare WHEN/THEN** (the vault notes mostly say "WHEN/THEN" — slightly out of date; trivially absorbed).

---

## 3. spec-toolkit — proposed design (from the vault, validated)

### 3.1 The engine (5-stage pipeline, GENERATE)

From `USM×OOUX 自動規格擴展引擎` §2, grounded in 30 yrs of Model-Based Testing (state-machine → auto-generated coverage) + LLM spec-synthesis evidence:

```
sparse seed
  ① extract objects + CTAs                    (extraction)
  ② OOUX fan-out: per-object attrs/states/relationships/CTAs   (LLM prior — sweet spot)
  ③ USM backbone × object × CTA × state grid  (cartesian, mechanical — sweet spot)
  ④ lens layer: state-transition legality / BVA / CRUD / perms / empty-error-loading / NFR checklist   (prune — sweet spot)
  ⑤ completeness-critic: what object/actor/state/NFR/policy is missing? loop-until-dry → re-seed ①
  ⑥ human / verification gate
→ high-recall spec draft + provenance (seeded / inferred / critic-found)
```

The bridge that makes "happy path → all paths" rigorous (from `從 Happy Path 到完整路徑` §4): model each OOUX object's states as a **state machine**, then apply ISTQB **state-transition testing** (every-transition coverage = "all paths"; invalid-transition = "edge cases") + **BVA** (data edges). System-layer failures (concurrency / network / perms / timing) come from a QA-lens checklist, not OOUX (OOUX is necessary-not-sufficient).

### 3.2 Three hard theoretical boundaries (the honesty rails)

The engine **auto-expands (strong), but cannot auto-complete (theoretical floor)**:
1. **Seed sets the ceiling** — external completeness is relative to all external knowledge; a sparse seed + LLM priors are not a complete source. Critic re-seeding raises the ceiling locally but cannot break it.
2. **Combinatorial ≠ aspectual completeness, and it over-generates** — the grid enumerates `object×CTA×state` (internal) but MBT's combinatorial explosion proves it over-produces illegal cells while missing system-layer/NFR aspects. Must prune (legality + USM priority) + critic-补.
3. **False completeness is the most dangerous** — a filled grid *looks* thorough → false confidence. Same epistemology as command-surface ("trust earned by execution, not appearance"). Resolved by routing output through code-toolkit's execution gate.

→ Behavioral guardrails: **ban the word "complete"** (use "coverage relative to seed + N lenses"); mark every item `provenance`; critic must emit its own blind spots (baseline Rule 12 "Fail loud").

### 3.3 Proposed skill set (vault packaging note §6.1)

| skill | role |
|---|---|
| `using-spec-toolkit` (router) | SessionStart inject; judge tier; decide whether to expand at all |
| `spec-discovery` | intent clarification + sparse-seed definition (may delegate to `code-toolkit:brainstorming` for the intent axes) |
| `spec-expansion` | the USM×OOUX engine (§3.1); multi-agent fan-out |
| `completeness-critic` | loop-until-dry; **must output blind spots** |
| `spec-persist` | write OpenSpec change-folder + `openspec validate` (DECLARE landing) |

### 3.4 Knowledge layer — share via SSOT, do not re-author

code-toolkit's `standards/rubrics/checklists` are a byte-identical functional copy of `domain-teams:code-team`, synced by `scripts/distribute.py` + drift-checked by `verify-drift.py`. **spec-toolkit should mirror this**: treat `spec-consistency.md` (SSOT in code-team, grounded in arc42 + IEEE/ISO/IEC 29148) as a shared SSOT and take a functional copy — avoid two plugins each maintaining a spec-knowledge layer (the named "duplicated knowledge layers" failure mode).

### 3.5 The handoff contract (vault packaging note §7)

- **Boundary artifact** = OpenSpec change-folder (`openspec/changes/<id>/{proposal.md, specs/ delta, design.md, tasks.md}`). spec-toolkit writes, code-toolkit reads.
- **Load-bearing element** = traceable acceptance criteria. spec-toolkit writes path/edge matrix as `#### Scenario: GIVEN/WHEN/THEN`; code-toolkit's `writing-plans` reads them, one scenario → one RED test / GREEN condition.
- **Trigger boundary** = proportional rigor + one-directional. Full tier only → call spec-toolkit; code-toolkit's verification gate is final truth.
- **Delegation mechanism** = skill-level explicit `Skill(skill: "plugin:skill")`, same pattern as `finishing-a-development-branch → dev-workflow:git-memory`. Zero new paradigm.

---

## 4. Concrete deltas to reconcile before building

1. **Refresh the OpenSpec brief's version pin.** Brief pins `~1.3.x`; current is **1.4.1**. v1.4.0 changed the workflow model (rigid → OPSX) and added validator hints (SHALL/MUST on body line). Decide: bump pin to `~1.4.x` or re-pin, and update the brief's Q5 multi-source version writes. (Brief Gap 2 / scenario-conversion-template: superseded by `/opsx:verify` existing — note, don't rebuild.)
2. **Don't hard-code OpenSpec command names.** Use `/opsx:*` namespace; the set is now propose/apply/archive/new/continue/ff/verify/sync/bulk-archive/onboard. The CLI surface (`openspec instructions/validate/archive --json`) is the stabler integration point per appendix A.3's "pure A" decision — prefer CLI over slash-command names.
3. **Scenario format = GIVEN/WHEN/THEN/AND**, not bare WHEN/THEN. Trivial, but the engine's emitter and the writing-plans reader must agree on the current Gherkin shape.
4. **DECLARE is still unimplemented.** The OpenSpec brief (Q1–Q9 locked) has *no plan and no code* — `openspec/` does not exist in the repo (verified). So the contract spec-toolkit writes to is itself not yet built. **Sequencing question for the brainstorm:** does spec-toolkit's MVP need OpenSpec wired first, or can `spec-persist` write the change-folder format directly (the format is just markdown) and defer the full code-toolkit OpenSpec integration?

---

## 4b. Prior art — surfaced from a broader vault sweep (2026-06-11)

The handoff named 5 notes; a full vault sweep (`research/`, `wiki/`, `reading_list/`, `references/`) surfaced **shipped prior art and a foundational course the 5 notes did not foreground**. This materially changes the build-vs-adopt and differentiation picture — spec-toolkit's GENERATE layer is *less* greenfield than the packaging note implied.

### Shipped prior art that already does spec-generation/expansion

| Tool | Type | Does GENERATE? | Borrow | Differentiate / avoid |
|---|---|---|---|---|
| **CoDD `codd-dev`** (`shio_shoppaize`, pip, v1.2.0) | **shipped** | **Yes, directly** — `spec.md (37 lines) → codd generate --wave 1..N → 1,353-line design docs`, dependency-ordered waves, `codd validate` quality gate, `@generated-from` traceability, impact-propagation on change | wave/dependency-ordered expansion; `validate` gate (rejects TODO/TBD/missing-Mermaid); Harness-as-Code (CLI + per-step model swap) | **expand-only, no critic** — "spec質=出力質", faithfully expands a seed but never *challenges* it (no completeness-critic). This is exactly spec-toolkit's differentiator. |
| **VSDD / VCSDD** (`sc30gsw/vsdd-claude-code`) | **shipped CC plugin** | Partial — Phase 1a crystallizes seed → EARS + verification-arch; 1c adversarial spec-review | adversarial spec-review *before* impl; mechanical `PreToolUse` gate (physically blocks code-before-test); Chainlink Bead `REQ→PROP→TEST→IMPL→FIND→PROOF` traceability; CEG coherence gate catches *spec-level* gaps tests can't | assumes you *bring* a spec to crystallize — spec-gen from a sparse seed isn't its focus. Overlaps heavily with **code-toolkit's VERIFY** (TDD + adversarial review) — note the boundary. |
| **GitHub Spec Kit** | shipped | `/speckit.specify` + `/speckit.clarify` (interactive gap-fill) + `/speckit.analyze` (Duplication / Coverage-Gap / Terminology-Drift / Ambiguity detection) | the `clarify`/`analyze` **gap-detection taxonomy** | generic, not adversarial/critic-driven |
| **Anthropic Planner-Generator-Evaluator** | Anthropic-built framework | Planner expands 1-4 sentence prompt → full spec | the canonical critic loop: **writer≠judge** (self-eval fails — returns confident praise), **Sprint Contract** (agree on "done" + how-to-verify *before* generating), per-dimension binary gate, **fresh context per critic round** | research framework, not packaged |

**Net:** the completeness-critic is the genuine gap — **CoDD expands-only (no critic), VSDD critiques-but-assumes-a-seed, Spec Kit clarifies-but-not-adversarial.** spec-toolkit's defensible value = adversarial completeness-critic (finds *omissions*, not just inconsistencies) feeding traceable acceptance criteria into code-toolkit's TDD. **Build-vs-adopt is now a real fork:** CoDD already does the wave-expansion mechanics — adopting/wrapping it (vs reimplementing) is worth weighing in the brainstorm.

### The harness-engineering-course (`research/harness-engineering-course/`, 12 lessons) — the model's origin

The 4-station model derives from this course. The load-bearing refinement for spec-toolkit:

- **L08 — the Feature List is a *runtime primitive*, not a hand-off document.** Format = the triple **`(behavior, verification-command, state)`**; "docs can be ignored, primitives cannot be bypassed." The root failure it fixes is the GENERATE argument itself: *"you never told it what 'done' means, so it used its own"* — the spec must externalize done-criteria + edge cases the overconfident model would skip. Granularity rule: each item = "completable in one session."
- **This challenges the "static spec file handoff" framing (packaging note §7).** The course's spec is a **live state machine the VERIFY layer writes back into** (verifier flips `not_started→passing`, agent cannot self-edit pass-state) — *stronger* than a markdown file code-toolkit reads once. Reconcile in the brainstorm: is spec-toolkit's output a static OpenSpec change-folder, or a live state object? (OpenSpec's `tasks.md` checkbox + `openspec instructions apply --json` state machine is the bridge — the DECLARE layer already provides write-back state.)
- **L06 bundles spec-gen *into* the initialization phase** (alongside env setup), not as an isolated upstream plugin — compatible with a separate plugin only if it still emits the verification-bound triple, not bare requirement prose.
- DECLARE maps: **L03** repo-as-single-source-of-truth + **Fresh-Session-Test** (5-question completeness gate) · **L05** persist *why* before *what*. VERIFY maps: **L09** worker≠checker + 3-layer termination · **L10** only-E2E-counts + Review-Feedback-Promotion (recurring findings → permanent checks).

### Two cautions that tighten the honesty rails (already in the 3 hard boundaries, now with field evidence)

- **要件定義 (PM essay):** the hinge of requirements is **業務要件の整理 (distilling business reality), not enumerating features** — the customer's own 解像度 is low; there is no complete answer to extract. → A generator can expand/structure/surface-blind-spots but **cannot manufacture missing business-domain reality**; spec-toolkit must emit "needs human/field input" gaps as **first-class output** (per `feedback_declaration_gate_when_script_cant_infer`), not silently hallucinate. Pairs with the engine's "critic must output its own blind spots."
- **NTT DATA half-year field report:** design + build went fine; **testing failed because the テスト観点表 (test-viewpoint table) wasn't updated → mass bug leakage.** → Spec recall **must propagate into test-case extraction**, or downstream TDD silently under-covers. Directly validates the contract's "scenario → RED/GREEN" joint as load-bearing (and warns it's where doc-driven AI pipelines actually break).

### Name note
The "NEW Spec Toolkit Ends Vibe Coding" video titles (WorldofAI, Bart Mode) are **clickbait framing of Superpowers** (obra/superpowers), not a product named "spec-toolkit." No hard name collision — but the phrase "spec toolkit" is associated in the wild with *full-workflow* tools (brainstorm→spec→implement). Worth a deliberate naming/positioning choice so spec-toolkit reads as the GENERATE *layer*, not a Superpowers competitor.

### QA grounding confirmed
`research/2026-04-10 歐美軟體測試最佳實踐 (ISTQB)` + `research/2026-04-10 日本 QA 社群測試實踐 (JSTQB/VSTeP/テスト観点)` both exist — they ground the engine's lens layer (state-transition + BVA + テスト観点 system-failure lenses). Not re-read in full; cited as trusted by the happy-path note's bridge.

## 5. Open questions for the brainstorm (P2)

- **Build vs adopt vs wrap (NEW, from §4b).** CoDD `codd-dev` already ships wave-based spec→design-doc expansion + a validate gate. Options: (a) build the engine from our own primitives; (b) wrap/adopt CoDD for the expansion mechanics and add our completeness-critic on top; (c) reimplement the *pattern* only. The defensible differentiator either way = the **adversarial completeness-critic** + the scenario→TDD joint. Resolve in brainstorm.
- **Static spec file vs live state object (NEW, from §4b/L08).** Does spec-toolkit emit a static OpenSpec change-folder (markdown), or a live state machine the VERIFY layer writes back into? OpenSpec's `tasks.md` + `instructions apply --json` already provides write-back state — likely the reconciliation.
- **Overlap with VSDD (NEW).** VSDD's adversarial review + mechanical gates overlap code-toolkit's VERIFY; its EARS crystallization overlaps spec-toolkit's GENERATE. Map the boundary so spec-toolkit doesn't reinvent code-toolkit's reviewer.

- **MVP scope.** Whole engine (5 stages + critic + persist) is large. Smallest valuable slice? Candidates: (a) `spec-expansion` core only (seed → grid → matrix), persist as plain markdown, no critic yet; (b) `spec-discovery + spec-expansion` (intent → draft); (c) the full §6.1 set. Lean unknown — needs brainstorm.
- **Sequencing vs OpenSpec DECLARE.** Build spec-toolkit against the *file format* now (markdown, no OpenSpec dependency) and integrate the OpenSpec CLI later? Or land the OpenSpec brief's plan first so the contract exists? (Delta #4.)
- **Plugin skeleton cost.** ~6 files (`plugin.json` + skills/ + README×3 + SessionStart hook router) per the packaging note's measurement. Acceptable.
- **Where the engine's fan-out runs.** `dispatching-parallel-agents` / Workflow — multi-agent per-object expansion. Confirm it fits the skill model.
- **Dogfood target.** Use code-toolkit's own brainstorm→plan→SDD flow to build spec-toolkit (consistent with repo practice). Branch off main.

---

## 6. Recommendation / next step

**The research holds; the decision does not need re-opening.** spec-toolkit (separate plugin, GENERATE) → OpenSpec change-folder (shared contract, DECLARE) → code-toolkit (VERIFY) is sound and current as of OpenSpec 1.4.1. The only new information is the three version/format reconciliations in §4 — all minor, none structural.

**Proposed next move (await kouko's go):** run `code-toolkit:brainstorming` on **spec-toolkit's MVP** — specifically resolving (1) MVP scope, (2) sequencing vs the unimplemented OpenSpec DECLARE layer, (3) plain-markdown-now vs OpenSpec-CLI-now for `spec-persist`. Then `writing-plans` → SDD. Branch off main; no commit/push without approval.

---

## Sources

**Vault (prior research, deep-read this session):**
- `2026-06-10 USM×OOUX 自動規格擴展引擎研究` — the engine (5-stage pipeline, completeness-critic, 3 hard boundaries, §7.4 GENERATE→DECLARE→VERIFY)
- `2026-06-10 規格層封裝決策` — the packaging decision (independent plugin + OpenSpec contract; §6 skill set; §7 handoff contract; appendix A pure-A)
- `2026-06-10 從 Happy Path 到完整路徑` — completeness method (USM body / OOUX scaffold / ISTQB state-transition + BVA bridge)
- `2026-06-09 Task vs Object 設計之爭` (USM/OOUX theory, upstream) · `2026-05-26 OpenSpec × code-toolkit 整合 Playbook` (original 2-layer DECLARE/VERIFY model)

**Repo:**
- `docs/loom/specs/2026-05-30-openspec-integration-brief.md` — locked DECLARE brief (Q1–Q9; out-of-scope explicitly excludes generation/completeness)
- `code-toolkit/docs/loom/specs/2026-06-10-auto-build-harness-evaluation.md` — 4-station eval (note: its "C chosen" was later superseded — Station 4 = already-shipped discipline, don't build; Station 1 GENERATE is the gap)

**Vault — prior art & foundations (broader sweep, 2026-06-11):**
- `research/harness-engineering-course/` (12 lessons + roadmap + resources) — the harness curriculum the 4-station model derives from; L06/L07/L08/L09/L10 load-bearing for GENERATE/VERIFY; `feature_list.json` triple + evaluator-rubric templates
- `reading_list/2026-03-29 VSDD Claude Code` + `wiki/concepts/vsdd-claude-code-plugin-sc30gsw` — VSDD shipped plugin
- `reading_list/2026-04-07 Harness as Code — CoDD` + `wiki/concepts/harness-as-code-codd-spec-design-doc-code-2026` — CoDD `codd-dev` shipped pkg (spec→design-doc wave expansion)
- `reading_list/2026-04-07 VSDD × CoDD` + `wiki/concepts/vsdd-coherence-engine-vcsdd-...` — VCSDD merged plugin
- `reading_list/2026-03-29 一個生成一個評審` + `wiki/concepts/gan-inspired-multi-agent-planner-generator-evaluator` — Anthropic Planner-Generator-Evaluator (writer≠judge, Sprint Contract)
- `reading_list/2026-03-30 PM 要件定義` + `wiki/concepts/pm-business-requirements-yochi-zenn` — requirements-distillation caution
- `reading_list/2026-04-21 設計書・コード・テストを全部AIに書かせて` (NTT DATA) — test-viewpoint-propagation failure
- `reading_list/2026-03-31 技術調査 spec駆動開発` + `wiki/concepts/spec-driven-development-sdd` — SDD survey (EARS, Constitution, spec ontology)
- `research/2026-04-10 歐美軟體測試最佳實踐 (ISTQB)` + `research/2026-04-10 日本 QA 社群測試實踐 (JSTQB/VSTeP)` — engine lens-layer grounding
- `references/finance/2026-03-09` + `references/ai/2026-04-22` — "NEW Spec Toolkit" = Superpowers clickbait (name note)

**OpenSpec 2026-06 live (web, 2026-06-11):**
- npm registry `@fission-ai/openspec` (v1.4.1, 2026-06-03) · GitHub `Fission-AI/OpenSpec` (README, docs/{concepts,cli,getting-started}.md, releases, issue #381)
- Competitive landscape: Reenbit/Medium "BMAD vs Spec Kit vs OpenSpec 2026" · MarkTechPost "9 best SDD tools 2026" · intent-driven.dev "Spec Kit vs OpenSpec" · Martin Fowler "exploring-gen-ai/sdd-3-tools" (spec persistence spectrum)
