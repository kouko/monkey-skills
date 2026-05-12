# systems-thinking-toolkit v0.1.0 Quality Audit + v0.1.1 Description Patch

**Date**: 2026-05-12
**Audit branch**: `audit/systems-thinking-toolkit-v0.1.0`
**Released as**: v0.1.1 description-triggering optimization
**Cohort under review**: 10 skills (9 v0.1.0 merged/standalone + 1 entry/router)

## Method

Two-round audit dispatched via `dev-workflow` toolchain:

- **Round 1 — Quality scoring (`skill-judge`)**: 10 parallel opus subagents, each applied the 8-dimension 0-120 rubric (D1 Knowledge Delta / D2 Mindset+Procedures / D3 Anti-Pattern Quality / D4 Spec Compliance / D5 Progressive Disclosure / D6 Freedom Calibration / D7 Pattern Recognition / D8 Practical Usability) against one SKILL.md plus its `references/cases.md` companion.
- **Round 2 — Description-triggering optimization (`skill-creator-advance` methodology)**: 10 parallel opus subagents, each examined the frontmatter `description` field for trigger quality (WHAT / WHEN / KEYWORDS / NOT-for / length budget) and proposed either `keep`, `patch`, or `rewrite`.

## Round 1 results

| # | Skill | Pre-merge baseline | **Post-merge v0.1.0** | Δ | Pattern |
|---|---|---|---|---|---|
| 1 | `cld-craft` | sk03=107 / sk04=110 | **114 / A** | +4 ↗ | Process |
| 2 | `loop-and-link-primitives` | sk01=110 / sk02=109 | **113 / A** | +3 ↗ | Process |
| 3 | `strategy-lever-and-cascade` | sk07=110 / sk08=107 | **114 / A** | +4 ↗ | Mindset |
| 4 | `stakeholder-and-team-thinking` | sk09=110 / sk10=108 | **113 / A** | +3 ↗ | Mindset |
| 5 | `simulation-modeling` | sk11=107 / sk12=105 | **112 / A** | +5 ↗ | Process |
| 6 | `limits-to-growth-take-the-brakes-off` | sk05=110 | **113 / A** | +3 ↗ | Tool |
| 7 | `variance-target-action-template` | sk06=110 | **115 / A** | +5 ↗ | Tool ⭐ |
| 8 | `innovaction-martian-test` ⚠ V1-weak | sk13=89 | **92 / C** | +3 ↗ | Process |
| 9 | `manager-personality-quadrant` ⚠ V1-weak | sk14=78 | **89 / C** | **+11** ⭐ | Tool |
| 10 | `using-systems-thinking-toolkit` (entry) | n/a | **109 / A** | new | Navigation |

### Cohort statistics

| Cohort | Mean | Median | % A grade |
|---|---|---|---|
| Pre-merge 14 (original cache) | 105 | 108.5 | 57% |
| **Post-merge 10 (v0.1.0)** | **108.4** | **113** | **80%** |
| Post-merge excluding V1-weak | 112.9 | 113 | 100% |

### Key observations

- **All 8 non-V1-weak skills earned A grade** (≥ 108). Profile-B merge + 9 improvements increased mean by 3.4 points and median by 4.5.
- **No dimension regression observed**: every merged skill scored at or above the better of its two pre-merge baselines on every dimension. Spec §6 Phase 0 halt condition was not triggered.
- **V1-weak skills got real improvements but stayed C grade**: sk14 (+11 from Tier-3 #8 lead-with-headline) and sk13 (+3 from Tier-3 #7 description framing). D1 Knowledge Delta capped at 11/20 due to structural prior-art overlap (TRIZ / DiSC etc.) — not fixable without changing skill scope.
- **D5 Progressive Disclosure ceiling unblocked**: pre-merge 14-skill mean was 12.5/15 (single-file dump). Post-merge with `references/cases.md` extraction, D5 mean reached 14/15. Spec §1 prediction confirmed.
- **D7 Pattern Recognition 5/10 skills earned 10/10** — masterful Process / Mindset / Tool fit. RIA-TV++ format proved to fit Anthropic's 5-pattern taxonomy after the merge.

### Top critical issues (body-level, not patched in v0.1.1)

- `stakeholder-and-team-thinking`: energy-pump metaphor is unfalsifiable by skill's own admission; no proxy metric (cadence + active-listening minutes) proposed. **Deferred to v0.2**.
- `variance-target-action-template`: needs numeric heuristic for "lengthen interval" in Step 5 and signal-vs-noise pre-check gate. **Deferred to v0.2**.
- `manager-personality-quadrant`: Guides quadrant circular definition not resolved in Execution. Observable-behavior signal table missing. **Deferred to v0.2**.
- `simulation-modeling`: no falsifiability / calibration step in Stage 2 despite Boundary acknowledging the gap. **Deferred to v0.2** (or paired with a Python companion script per ROADMAP).
- `cld-craft`: dangle list halt-condition (Step 2 > 8 items) is a hard number — needs OR clause for legitimately wide scopes. **Minor, deferred**.

## Round 2 results — description-triggering optimization

| # | Skill | Verdict | Words: was → is | Headline change |
|---|---|---|---|---|
| 1 | `cld-craft` | **patch** | 211 → 221 | +missing triggers ("causal map", "feedback loop"), +NOT-for vs adjacent diagram types (fishbone / mind-map / SFD) |
| 2 | `loop-and-link-primitives` | **patch** | 270 → 174 | Collapsed JA/zh-TW + KEYWORDS into one keyword roster, deduped near-duplicate triggers — 36% slimmer while preserving routing |
| 3 | `strategy-lever-and-cascade` | **patch** | 171 → 227 | Surfaced **dual entry depth** — Steps 2-3 reframe-only short-circuit vs Steps 4-8 full cascade (Round-1 critical fix) |
| 4 | `stakeholder-and-team-thinking` | **keep** | 177 (no Δ) | Description already optimal at dual-mode routing; body-level issues stay in body |
| 5 | `simulation-modeling` | **patch** | 137 → 161 | +**TEXT-ONLY discipline** clarifier (no executable simulator); cld-craft hand-off explicit |
| 6 | `limits-to-growth-take-the-brakes-off` | **patch** | 62 → 83 | +numeric **entry signature** ("3+ periods of decelerating growth rate"); NOT-for now points to specific competing skills |
| 7 | `variance-target-action-template` | **keep** | 133 (no Δ) | Description already optimal (115/A confirms); body-level issues stay in body |
| 8 | `innovaction-martian-test` ⚠ | **patch** | 80 → 95 | Softer Tier-3 #7 prefix ("Composes with..." instead of "Auxiliary skill —"); **3-way pick rule** vs TRIZ vs SCAMPER |
| 9 | `manager-personality-quadrant` ⚠ | **keep** | 141 (no Δ) | Description already implements Tier-3 #8 lead-with-headline |
| 10 | `using-systems-thinking-toolkit` | **patch** | 49 → 83 | Reframed from topic keywords to **intent-uncertainty** triggers + concrete user utterances (avoids competing with per-skill descriptions) |

**Patches applied: 7. Keeps: 3.**

### Highest-value patches

1. **`loop-and-link-primitives` 30%+ slimmer** — Round-1 explicitly flagged "very dense (~270 words)". Patch addresses directly.
2. **`simulation-modeling` +TEXT-ONLY** — Critical for routing honesty. Without it, users could mistake skill as containing an executable simulator (which it doesn't — Python companion deferred to v0.2 per ROADMAP).
3. **`using-systems-thinking-toolkit` intent-uncertainty reframe** — Router skill must NOT compete with per-skill activations. Previous description used topic keywords (feedback loops, vicious cycle, stock-flow) that overlap with downstream skills. New phrasing routes only on intent-uncertainty + concrete user utterances.

### Why 3 skills got "keep"

- `stakeholder-and-team-thinking`, `variance-target-action-template`, `manager-personality-quadrant`: their Round-1 critical findings live in the **body** (E procedure / I synthesis), not the description. Patching the description to "shadow-fix" body issues would dilute routing crispness. Body fixes deferred to v0.2.

## v0.1.1 release scope

This audit's PR ships:

- 7 SKILL.md description-triggering optimization patches (per Round 2 table above)
- `plugin.json` version bump 0.1.0 → 0.1.1
- This audit report under `docs/superpowers/audits/`

This audit's PR does **NOT** include:

- Body-level fixes (deferred — see "Top critical issues" above)
- New skills / scope changes
- Stock-flow Python companion (v0.2 candidate per ROADMAP)
- sk13 / sk14 V1-weak merger or replacement (v0.2+ decision per spec D2)

## Process notes

- **Round 1 dispatch**: 10 parallel opus subagents, all returned cleanly. ~30s wall-clock for the batch.
- **Round 2 dispatch**: 9 parallel opus subagents, all returned cleanly. ~30s wall-clock.
- **No quota gates** hit this time (daily Opus quota reset since v0.1.0 build).
- **No 1M-context billing gate** hit (used opus throughout for inheritance; sonnet would have failed per v0.1.0 build experience).

## Lessons that will accumulate in memory

This audit confirmed two existing memories:

- `feedback_phase_abc_orchestration` (parallel subagent dispatch works when target files don't overlap)
- `feedback_subagent_driven_development_validated` (fresh-subagent-per-task pattern preserves quality)

And generated no new memories — the audit pattern (skill-judge → skill-creator-advance for descriptions) is now a documented workflow under `dev-workflow:skill-creator-advance` and `dev-workflow:skill-judge`, ready for use on future plugin releases.

## Recommendations for v0.2

In priority order:

1. **Body-level fixes** to the 3 "keep" skills + the 1 cld-craft minor: address energy-pump unfalsifiability, V/T/A interval heuristic, Guides circularity, dangle halt OR-clause.
2. **`simulation-modeling` Python companion** — convert the TEXT-ONLY claim into "TEXT-ONLY in core skill, optional executable simulator in `simulation-modeling/scripts/`".
3. **sk13 / sk14 V1-weak decision** — observe v0.1.x use-feedback, then pick from ROADMAP options: (a) absorb sk13 into `strategy-lever-and-cascade` as facilitation extras, (b) replace with TRIZ + DiSC dedicated skills, or (c) keep standalone with stronger Boundary disclaimers.
4. **Per-skill skill-judge re-baseline** after each body-level change.

---

## v0.2.0 update — body-level fixes landed (A1-A5 + A8 + A9)

Released: 2026-05-12 (same-day as v0.1.0 + v0.1.1).
Scope: 5 body-level fixes from the deferred list above + JA/zh-TW description hint normalization + skill-judge re-baseline on 5 body-fixed skills.

### A1-A5 body fixes applied

| Tag | Skill | Change | Body Δ |
|---|---|---|---|
| A1 | cld-craft | Step 2 dangle halt gets narrow-vs-wide-scope AND clause; Rule 4 aggregation carries simplification when 8+ dangles is legitimate | +74w |
| A2 | stakeholder-and-team-thinking | Protocol I energy-pump operationalized via 4 observable proxies (cadence / active-listening / value-revisitation / symbol-narrative) + measurable exit criteria I1-I7 | +364w |
| A3 | variance-target-action-template | Step 0 SPC signal-vs-noise pre-check + Step 4(b) 1.5×-delay heuristic + Step 6 org-politics escalation | +253w |
| A4 | manager-personality-quadrant | E Step 2 observable-cue table + Guides circularity resolved (structural-not-outcome) + Step 4 framing-vs-analysis 4-question checklist | +265w |
| A5 | simulation-modeling | Stage-1 Step 7 fuzzy hand-off tightened + Stage-2 Step 10 worked numeric example + Step 11.5 NEW sensitivity-sweep / falsification check | +528w |

### A8 description hint normalization

v0.1.1 left 2/10 skill descriptions without JA/zh-TW hints. A8 adds them:
- `limits-to-growth-take-the-brakes-off`: 成長エンジンの減速・成長限界・制約解除 / 成長引擎減速・成長極限・解除約束
- `innovaction-martian-test`: 火星人テスト・特徴摂動・シナリオ生成 / 火星人測試・特徵擾動・情境生成

### A9 skill-judge re-baseline (5 body-fixed skills)

| Skill | v0.1.1 | **v0.2.0** | Δ |
|---|---|---|---|
| cld-craft | 114 | **115** | +1 |
| stakeholder-and-team-thinking | 113 | **113 (strict-cap) / 117 (observed)** | 0 / +4 |
| variance-target-action-template | 115 | **115** | =0 (already near 4-dim ceiling) |
| manager-personality-quadrant | 89 | **94** | +5 |
| simulation-modeling | 112 | **115** | +3 |

Plugin-wide mean: 108.4 → 109.3 (strict) / 109.7 (observed). No regressions detected.

### Notes

- D8 stakeholder-and-team-thinking subagent scored raw 19 (over the 15 cap); strict-clamp recompute keeps total at 113 (= v0.1.1). Observed-signal interpretation = 117. We accept either reading — both confirm "no regression" and the body fix adds real value internally even when capped.
- variance-target-action-template hit a real D2/D4/D7/D8 ceiling at v0.1.1. The A3 fixes raise floor (procedure more rigorous) without changing the total, which is the expected behavior near ceiling.
- manager-personality-quadrant (sk14 V1-weak) gained +5 from A4 (89→94) but D1 still capped at 13/20 by prior-art overlap (DiSC/MBTI/Hogan/Situational Leadership). Structural limit, not fixable without scope change.

### Still-deferred v0.3+ candidates

The following from the original audit's v0.2 recommendations stayed deferred:
- `simulation-modeling` Python companion (executable simulator) — significant scope; ROADMAP v0.3 candidate
- sk13 / sk14 V1-weak future decision (absorb / replace with TRIZ + DiSC dedicated / keep standalone with stronger disclaimers)
- Stricter cross-skill compose-with operationalization (e.g. explicit hand-off API between cld-craft fuzzy elevation and simulation-modeling sensitivity sweep)
- D8 cap interpretation policy for skill-judge (when raw score exceeds 15, should it ceiling at 15 or accept the signal?)
