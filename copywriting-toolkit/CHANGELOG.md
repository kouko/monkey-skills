# copywriting-toolkit — CHANGELOG

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
Phase 5    copywriting-voice-positioning-stage
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
| `copywriting-voice-positioning-stage` | executor | Phase 5 Voice Quadrant (Vaughn × Halliday) + Schwartz routing |
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

5. **`copywriting-voice-positioning-stage` Schwartz × Quadrant conflict has no inline worked example** — the detail lives in `standards/voice-quadrant-positioning.md §With persuasion-psychology-anchor.md Schwartz Levels`. Add worked example if user feedback shows confusion.

6. **No Mermaid pipeline diagram** — the 9-phase ASCII diagram in README is clear but a Mermaid diagram for the bounce-back + revise-loop control flow would aid onboarding. Deferred to v1.1 documentation pass.

7. **Inline-duplication drift risk** — `persuasion-psychology-anchor.md` lives as 5 identical copies across Phase-4 workflow skills; `sns-evolution-aisas-ulssas.md` as 2 identical copies. No sync script. Accept as design cost (each skill stays self-contained); if drift observed, add a sync script rather than attempting cross-skill runtime loading.

8. **`audit_trail[]` rendering / persistence** — the field is defined in `envelope.schema.json` and documented in CLAUDE.md §Audit Trail, but the router's rendering to the user on `halt-ask-user` is specified as SHOULD (not MUST) and persistence is left to the caller. First real-world usage will surface whether a stronger contract is needed.

---

## Upgrade path (for future versions)

- **Additive fields** in the envelope: callers should preserve unknown fields verbatim on re-entry (forward-compatible). See CLAUDE.md §External Caller Guide §Envelope evolution.
- **Required-field changes** or enum restrictions: will bump minor version (v1.x → v1.y) at minimum, with a CHANGELOG entry naming the field and the breaking change.
- **Agent tier changes**: if `copywriter` or `copywriter-evaluator` move to different model tiers, CHANGELOG will flag it explicitly — evaluator persona discipline (no aesthetic capture) is sensitive to tier.
