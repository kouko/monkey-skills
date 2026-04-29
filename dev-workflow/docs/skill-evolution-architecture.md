# Skill Evolution Architecture — Planning + Status Doc

**Status**: LIVING DOCUMENT. Originally pre-implementation planning;
now also tracks implementation status across the 5-PR rollout.
**Scope**: dev-workflow plugin's family of skill-modifying skills.
**Created**: 2026-04-29
**Last status update**: 2026-04-29 (post-PR-5, v1.9.0)
**Trigger**: research into `alchaincyf/darwin-skill` + critique of LLM-as-judge for taste-sensitive output.

## Implementation Status (as of v1.9.0)

| PR | Version | Scope | Status |
|---|---|---|---|
| PR-1 | v1.5.0 | Architecture doc + skill-creator-advance scope tightening | ✅ Merged |
| PR-2 | v1.6.0 | skill-refactor (Phase A — refactor hat) | ✅ Merged |
| PR-3 | v1.7.0 | skill-tasting (Phase B — feature hat) | ✅ Merged |
| PR-4 | v1.8.0 | Governance layer: convention drift CI + skill-judge drift detection + governance / audit docs | ✅ Merged |
| PR-5 | v1.9.0 | Telemetry scaffold + self-training stub enhancement + test-prompts.json bootstrap × 7 + this status section | ✅ Merged |

### Horizon coverage

| Horizon | Items | Coverage |
|---|---|---|
| **H1** (Option II baseline) | skill-creator-advance scope; skill-refactor; skill-tasting | ✅ Complete |
| **H2** (Layer 2 upgrades to refactor / tasting) | Multi-judge ensemble (refactor); structured equivalence; constitutional pre-filter (tasting); blind A/B; per-iteration human gate | ✅ Complete |
| **H3** (Layer 3 / governance) | Cross-skill regression CI (drift); skill-judge drift detection; SSOT registry; quarterly audit runbook | ✅ Complete |
| **H4** (Foundation + closed-loop) | Test-prompts.json bootstrap × 7; telemetry scaffold; self-training stub | ✅ Scaffolded (training pipeline activates at ≥1000 preference pairs per skill — currently far below threshold; stub fails fast with activation methodology) |

### Outstanding validation gates

These are validation gates from earlier PRs not yet performed:

| Gate | From | Status | Tracked in |
|---|---|---|---|
| skill-refactor: dry-run on ≥2 existing skills, ≥90% equivalence-check agreement | PR-2 | OUTSTANDING | quarterly-audit-runbook step 5 |
| skill-tasting: 1 real-skill walkthrough validating A/B flow | PR-3 | OUTSTANDING | quarterly-audit-runbook step 5 |

These do not block any further work — they're tracked as audit
items per the runbook. If outstanding for >2 quarters, an
explicit accept-risk or schedule-validation decision is required.

## Original Planning Doc Begins Below

---

## 1. Context — Why This Doc Exists

### What we already have

dev-workflow currently ships:
- `skill-creator-advance` — creation + general iterative improvement + eval infrastructure (grader / comparator / analyzer agents + run_loop scripts) + description optimization
- `skill-judge` — advisory 8-dimension quality rubric (0–120 scale, never modifies)
- `git-memory` — out of scope here
- `proposal-critique` — out of scope here
- `complexity-critique` — out of scope here

### What triggered this re-architecture

External research into `alchaincyf/darwin-skill` (1.9k stars, 2026-04-13), an autoresearch-inspired skill optimization system that runs hill-climbing against an 8-dim rubric with git ratchet ("only commits that improve the score survive"). On audit it has a structural weakness: **its single rubric mixes mechanical structural improvements with taste-sensitive output quality**, and uses LLM-as-judge for both. The "score can only go up" ratchet then hill-climbs in the *judge subagent's preference space*, which can drift away from *human user's preference space* (Goodhart). Especially fragile on taste-sensitive dimensions (output style, voice, creative work).

### The reframing

Split skill optimization into two *epistemically distinct* concerns:

| Concern | Goal | Constraint | Eval mode |
|---|---|---|---|
| **Phase A — structure / process refactor** | Reduce token count / improve structural clarity | Output quality stays stable | Automated (LLM equivalence check is reliable for binary same/different) |
| **Phase B — output quality A/B** | Improve actual output | Structure / token count is whatever it needs to be | Manual (human picks; LLM-as-judge for taste is unreliable) |

This split is the **Fowler Two Hats principle** applied to skills: refactor hat (preserve behavior) vs feature hat (change behavior). monkey-skills `code-team/standards/refactoring-standard.md` already enshrines this principle; we extend it to skill authoring.

---

## 2. Decision — Option II with Size-Based Scope Split

### Decision summary

**Add two new skills to dev-workflow** as siblings to `skill-creator-advance`:

- `skill-refactor` — Phase A: token / structure refactor with auto equivalence check + git ratchet
- `skill-tasting` — Phase B: human-judged A/B for output quality

`skill-creator-advance` retains its existing scope but is **rescoped** to "creation + major redesign" (large-size-bin work) instead of "creation + any-size improvement". `skill-judge` is unchanged.

### The four-skill picture (size × evaluation axis)

```
size →    small                medium                large                new
       ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
       │ skill-tasting  │  │ skill-refactor │  │ skill-creator-advance         │
       │                │  │                │  │ (rewrite + creation)         │
       │ output quality │  │ token / struct │  │                              │
       │ A/B variants   │  │ same behavior  │  │ spec-first redesign / new    │
       │                │  │                │  │                              │
       │ HUMAN judge    │  │ LLM equiv.     │  │ user-led iteration loop +    │
       │ each iteration │  │ + git ratchet  │  │ optional AI A/B comparator   │
       └────────────────┘  └────────────────┘  └──────────────────────────────┘
                                                         
       skill-judge: advisory scoring at any time, doesn't modify
```

### Why size-based, not "auto vs manual"

- `auto vs manual` is a *consequence* of *what's being evaluated*, not the other way around
- Mechanical changes (refactor) → equivalence check is reliable → can auto
- Taste-sensitive changes (output quality) → human judgment irreplaceable → must manual
- The user invokes based on "what kind of change is this" (size + scope), not "do I want auto or manual"

---

## 3. Scope Boundaries (canonical reference)

### When to invoke each skill

| User intent | Handler | Why |
|---|---|---|
| New skill from scratch | `skill-creator-advance` | Only one with spec-from-scratch flow |
| Major rewrite (add/split/merge phases, change agent decomposition, change input/output contract) | `skill-creator-advance` | Spec re-审 + full eval; refactor/tasting can't reach |
| Token reduction / structure cleanup with **output equivalence** | `skill-refactor` | Auto equivalence + git ratchet; high-frequency / low-cost operation |
| Output quality improvement / A/B variant exploration / **human-judged taste calls** | `skill-tasting` | Human preference accumulates real signal |
| Vague "improve this skill" | `skill-creator-advance` (router fallback) | "Improving an Existing Skill" section asks user to clarify, then routes |
| AI-judge blind A/B (existing capability) | `skill-creator-advance` Advanced (comparator agent) | Existing optional advanced tool; not duplicated by skill-tasting |
| Description triggering optimization | `skill-creator-advance` | Existing run_loop.py handles this |
| Advisory scoring (no modification) | `skill-judge` | Pure observation |

### Trigger disambiguation table

| User says (literal) | Routes to | Disambiguating signal |
|---|---|---|
| "create a skill" / "make a slash command" / "new skill for X" | skill-creator-advance | Creation intent |
| "rewrite skill" / "redesign skill" / "add a phase" / "拆 skill" / "merge skills" | skill-creator-advance | Structural change intent |
| "shorten skill" / "reduce SKILL.md" / "縮減 token" / "trim fat" / "behavior unchanged" | **skill-refactor** | Equivalence + size signal |
| "test outputs" / "A/B variants" / "improve writing style" / "compare different phrasings" / "我來評哪個比較好" | **skill-tasting** | Human judge + variant exploration signal |
| "score this skill" / "evaluate skill" / "is this skill good" | skill-judge | Pure scoring |
| "improve this skill" (vague) | skill-creator-advance | Router fallback; ask user to clarify size |

---

## 4. Architectural Asymmetries (skill-refactor vs skill-tasting)

Despite both being "skill modifies skill" with subagent editor + evaluator, they differ in 9 connected ways:

| Axis | skill-refactor | skill-tasting |
|---|---|---|
| Editor agent prompt | Refactor hat: equivalence-preserving moves only | Feature hat: explore variants with different output traits |
| Evaluator | LLM subagent (binary equivalence) | Human (preference; A / B / both / neither) |
| Decision authority | Metric drives auto keep/revert | Human direct selection |
| Loop autonomy | Bounded auto rounds (e.g. max 3) per skill | Each iteration requires human gate |
| Rollback mechanism | Git ratchet (auto revert if non-equivalent) | Git history; user decides |
| Data accumulation | results.tsv (token trend, equivalence pass rate) | preference log (A/B selections; future RLHF dataset) |
| Per-invocation cost | Low (automated) | High (human time) |
| Per-invocation value | Low (each round saves a few hundred tokens) | High (each round captures real preference signal) |
| Run frequency | High; can run in background | Sparse; high-value nodes |

These nine differences are the *implementation guidance* for the two SKILL.md files. Without enforcing them in skill prompts, the two skills could collapse into "one skill with a parameter".

---

## 5. Required Modifications to `skill-creator-advance`

### 5.1 Description rewrite

**Current** (lines 2–13 of SKILL.md):
> Create new skills, improve existing skills, and measure skill performance with iterative eval-driven development. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy. ...

**Problem**: "edit or optimize an existing skill" is too broad — it claims territory that skill-refactor and skill-tasting will own.

**Proposed**:
> Create new skills, do major redesigns of existing skills (add/split/merge phases, change agent decomposition, redesign workflow), measure skill performance with iterative eval-driven development, and optimize a skill's description for better triggering accuracy. Use when users want to create a skill from scratch, redesign or significantly rewrite a skill, run evals, benchmark, or optimize description triggering. Do NOT use for token / structure refactor with output equivalence (use `dev-workflow:skill-refactor`) or human-judged A/B output quality testing (use `dev-workflow:skill-tasting`). Do NOT use for domain-team skills (use `domain-teams:skill-team`). スキル作成・大規模再設計・評価ループ。技能建立・大幅重設計・評估迴圈。

### 5.2 "Improving an Existing Skill" section (lines 235–264) — convert to router

**Current**: linear flow (assess → 5-dim diagnose → propose → eval) that handles any size of improvement.

**Proposed structure**:

```
## Improving an Existing Skill

When a user wants to improve an existing skill, first determine
which kind of improvement:

(a) Token reduction / structure cleanup with output behavior unchanged
    → Hand off to `dev-workflow:skill-refactor`. Do not handle here.
    
(b) Output quality / A/B variant exploration with human judgment
    → Hand off to `dev-workflow:skill-tasting`. Do not handle here.
    
(c) Structural change — add/split/merge phases, change agent
    decomposition, redesign workflow, change input/output contract
    → Continue with the full creation flow below, using the existing
    skill as the starting baseline rather than starting from scratch.
    Snapshot first (`cp -r <skill-path> <workspace>/skill-snapshot/`).

If the user's intent is unclear, ask them to clarify which of (a),
(b), or (c) applies, then route accordingly. The original 5-dimension
diagnose checklist (triggering / instructions / structure / coverage
/ bundled files) only applies in case (c).
```

The 5-dimension diagnose stays for case (c). It's wrong-shape for cases (a) and (b).

### 5.3 Advanced Blind Comparison (lines 422–426) — boundary clarification

This section is fine as-is, but should add a note distinguishing from skill-tasting:

> The blind comparator uses a subagent as judge (LLM-as-judge). For taste-sensitive output where LLM-judge is known to be unreliable (creative writing, voice, design feel), use `dev-workflow:skill-tasting` instead — that skill uses human judgment per iteration and accumulates a preference log.

---

## 6. Implementation Phasing

### Phase A — write the docs and decide

- This document (DRAFT) is the artifact for review
- Decision points listed in §7

### Phase B — skill-creator-advance modifications (low risk)

If the architecture is approved:
1. Rewrite description
2. Convert "Improving an Existing Skill" section into router (3-way fork)
3. Add boundary note to Blind Comparison section

This is a single PR, mostly text edits. Doesn't break existing flows. Worth doing even if Phase C is deferred.

### Phase C — implement skill-refactor (medium risk)

Required components:
- `dev-workflow/skills/skill-refactor/SKILL.md` — Iron Law / Gate Function (equivalence Q + token Q + invariant Q) / verdict (PROCEED / RESHAPE / REJECT) / refactor hat editor prompt
- `dev-workflow/commands/skill-refactor.md`
- LICENSE / NOTICE if any upstream attribution
- `dev-workflow/skills/skill-refactor/README.{en,ja,zh-TW}.md`
- Optional: `references/equivalence-check-protocol.md` (how to check semantic output equivalence with subagent)
- Optional: `references/refactor-moves.md` (catalog of refactor-hat-safe transformations)
- plugin.json bump 1.5.0 → 1.6.0 + CHANGELOG
- `results.tsv` schema

Risk: LLM equivalence check needs validation. If "is output A equivalent to output B" turns out to be unreliable for SKILL.md outputs, the auto-ratchet doesn't work safely.

**Validation gate before merging**: dry-run skill-refactor on 2–3 existing monkey-skills with manual verification of the equivalence check accuracy. If <90% agreement with human judgment on equivalence, redesign before shipping.

### Phase D — implement skill-tasting (higher uncertainty)

Required components:
- `dev-workflow/skills/skill-tasting/SKILL.md` — variant-generation editor prompt, A/B harness protocol, preference logging
- `dev-workflow/commands/skill-tasting.md`
- LICENSE / NOTICE
- `dev-workflow/skills/skill-tasting/README.{en,ja,zh-TW}.md`
- Optional: `references/ab-harness.md` (how to spawn variants + present to user)
- Optional: `references/preference-log-schema.md`
- plugin.json bump + CHANGELOG

Risk: human-judged A/B is high-cost-per-iteration. Needs use-case validation that this is actually useful enough to justify a dedicated skill (vs. a manual workflow).

**Validation gate before merging**: pick a real skill the user has wanted to improve, run skill-tasting on it manually (without the skill itself, as a process), see if the workflow produces value. If the manual version doesn't produce value, the skill version won't either.

### Phasing options

| Option | Phase B | Phase C | Phase D |
|---|---|---|---|
| All-in | Yes | Yes | Yes |
| Refactor first | Yes | Yes | Defer until Phase C validates |
| Cautious | Yes | Defer | Defer |
| Doc only | Defer | Defer | Defer |

---

## 7. Open Decisions

These need user input before implementing:

| # | Decision | Options |
|---|---|---|
| 1 | Implement skill-refactor? | (a) Yes — Phase C; (b) Defer until value proven; (c) No — overlap with skill-creator-advance "Keep prompt lean" hint enough |
| 2 | Implement skill-tasting? | (a) Yes — Phase D; (b) Defer — manual A/B works for now; (c) No — comparator agent + human review of comparator output is enough |
| 3 | Modify skill-creator-advance? | (a) Yes regardless of C/D; (b) Only if C and/or D ship |
| 4 | LICENSE / attribution for skill-refactor? | (a) MIT, attribute to darwin-skill (joshuadavidthomas → softaworks chain); (b) MIT, no attribution (independent design); (c) Other |
| 5 | LICENSE / attribution for skill-tasting? | (a) MIT, attribute to darwin-skill where applicable; (b) MIT, no attribution; (c) Other |
| 6 | Cross-plugin coordination with code-team? | Are there mindset-style references that should land at code-team? Probably no — these are workflow skills not philosophical anchors. Confirm. |
| 7 | Test prompt registry strategy | (a) Per-skill `test-prompts.json` like darwin; (b) Centralized at dev-workflow level; (c) Skip until first user |
| 8 | Equivalence check fidelity | What counts as "equivalent output"? Exact match? Semantic match? Format-preserving + content-preserving? Needs spec. |
| 9 | Preference log retention / schema | Where stored, how long, what format. Affects future RLHF reuse. |
| 10 | Should skill-tasting also accumulate test-prompt registry? | Sharing with skill-refactor's registry would be efficient; but they test different things. |

---

## 8. Risks & Alternatives Considered

### Alternative 1: Don't add new skills, enhance skill-creator-advance internally

Add explicit "refactor mode" and "tasting mode" inside skill-creator-advance. Single skill, multiple modes.

**Rejected because**: SKILL.md already at 4868 words, near 4500-word soft cap (~6000 token budget per skill-team CHK-SKL-010). Adding two more workflows would push it over. Splitting is forced by the token budget anyway.

### Alternative 2: Adopt darwin-skill wholesale into dev-workflow

Install `alchaincyf/darwin-skill` as-is or fork it into a 5th dev-workflow skill.

**Rejected because**: darwin's monolithic 8-dim rubric with auto ratchet on taste-sensitive dimensions inherits the LLM-as-judge / Goodhart problems. Adopting wholesale would import the architectural weakness we just identified.

### Alternative 3: skill-refactor only, skip skill-tasting

The refactor case has a robust equivalence check; the tasting case has uncertain ROI. Ship A only.

**Plausible**. Listed as Phasing option "Refactor first". Decision deferred to user.

### Alternative 4: Pure-tool / CLI script instead of skill-shaped

Write `scripts/refactor-skill.py` and `scripts/taste-skill.py` instead of SKILL.md-shaped skills.

**Trade-off**:
- Pro: scripts are deterministic / reproducible / testable
- Con: skill-shaped is consistent with monkey-skills convention, easier for user to discover via `/skill-refactor` etc., naturally integrates with Claude Code agent invocation

**Compromise considered**: skill-shaped wrappers that delegate the deterministic parts (token counting, git operations, equivalence test orchestration) to bundled scripts under `scripts/`. This is similar to how `skill-creator-advance` already uses `scripts/run_loop.py`.

### Risk: Goodhart at the meta-level

Even with the split, hill-climbing in skill-refactor's "token reduction + equivalence" space could push skills toward "smallest verbose tokens that pass equivalence" — which might be skills that *appear* equivalent under LLM-judge but lose subtle disambiguation power.

**Mitigation**: 
- Hard cap: token reduction must be ≥10% to keep (no cosmetic 5-token wins)
- After-each-skill human gate (don't ratchet across many skills without human review of one)
- Periodic re-run of skill-judge advisory score on refactored skill — if score drops by >1 standard deviation, flag

### Risk: skill-tasting is too expensive to run

Human A/B every iteration is high cost. If users only run it once and abandon, the dataset accumulation benefit is lost.

**Mitigation**: scope skill-tasting to *high-value skills only* (skills the user runs daily, skills with creative output, skills used by multiple people). Don't recommend running on every skill.

---

## 9. Out of Scope

- Auto-detect which skill (refactor / tasting / creator-advance) to use based on user prompt — that's the description / trigger system's job; not solved here
- Cross-plugin: this stays inside dev-workflow; no coupling with domain-teams beyond what already exists
- Replacement / deprecation of skill-creator-advance — explicitly NOT happening; only rescoping
- Replacement of skill-judge — explicitly NOT happening; it remains the advisory scoring tool
- Migration of existing skills to be "darwin-optimized" — that's a per-skill decision after these tools exist
- Building automatic preference-judge from accumulated skill-tasting log — possible future work; out of scope for v1

---

## 10. Acceptance Criteria (if implementing)

### For skill-refactor v1 to ship

- [ ] SKILL.md ≤4500 words
- [ ] Frontmatter description with negative triggers vs skill-tasting / skill-creator-advance
- [ ] Iron Law + Gate Function with three explicit checks (equivalence / token reduction / invariant preservation)
- [ ] Verdict vocabulary parallel to other dev-workflow critique skills (PROCEED / RESHAPE / REJECT)
- [ ] Equivalence check protocol documented
- [ ] Refactor-hat editor prompt explicitly excludes behavior-changing moves
- [ ] Git ratchet integration documented (mirrors complexity-critique's NOTICE for upstream attribution if applicable)
- [ ] 3-language READMEs (en / ja / zh-TW)
- [ ] Validation: dry-run on ≥2 existing skills, ≥90% equivalence-check agreement with manual review
- [ ] CHANGELOG entry + plugin.json bump

### For skill-tasting v1 to ship

- [ ] SKILL.md ≤4500 words
- [ ] Frontmatter description with negative triggers vs skill-refactor / skill-creator-advance
- [ ] A/B harness protocol (variant generation + side-by-side presentation + 4-option selection)
- [ ] Preference log schema documented
- [ ] Variant-exploration editor prompt explicitly distinct from refactor-hat
- [ ] Per-iteration human gate enforcement (no auto-ratchet)
- [ ] 3-language READMEs
- [ ] Validation: 1 real-skill walkthrough produces meaningful preference signal
- [ ] CHANGELOG entry + plugin.json bump

### For Phase B (skill-creator-advance modification) to ship

- [ ] Description rewrite per §5.1 lands without breaking existing trigger eval
- [ ] "Improving an Existing Skill" section converted to 3-way router per §5.2
- [ ] Advanced Blind Comparison section gains boundary note per §5.3
- [ ] No regression in trigger eval against existing skills

---

## Appendix A — Mapping to Existing monkey-skills Patterns

| New concept | Existing pattern it borrows from |
|---|---|
| Phase A / Phase B split | `code-team/standards/refactoring-standard.md` Fowler Two Hats |
| Refactor verdict vocabulary (PROCEED / RESHAPE / REJECT) | `dev-workflow/skills/proposal-critique` (KEEP / DEFER / DROP), `complexity-critique` (PROCEED / PROCEED-WITH-CAVEAT / RESHAPE / REJECT) |
| Three-question gate format | `complexity-critique` Q1 / Q2 / Q3 |
| Cross-plugin reference (if needed) | Cross-Plugin Delegation Contract in repo CLAUDE.md, recently extended in PR #159 with SSOT-and-functional-copy pattern |
| Human-anchor preference (skill-tasting) | `copywriting-toolkit/voice-anchors` (90 anchors curated by human) |
| Single-source-of-truth for evolving content | code-team mindsets SSOT pattern |
| Token-budget discipline | `skill-team` CHK-SKL-010 (4500 words / ~6000 tokens) |
| Description with negative triggers | `skill-creator-advance/references/description-design.md` §6 |
| 3-language README convention | PR #150 i18n rollout |

---

## Appendix B — What This Doc Is Not

- Not a SKILL.md (it doesn't tell Claude what to do; it's a design artifact for humans)
- Not a commit-ready deliverable (it lives on a planning branch as a draft)
- Not a prescription (decisions in §7 are still open)
- Not committed to monkey-skills convention until reviewed
