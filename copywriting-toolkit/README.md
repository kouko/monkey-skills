# copywriting-toolkit

Pipeline-structured copywriting plugin. Refactored from `domain-teams:copywriting-team` into 14 specialized skills — each with ONE job, self-contained standards, and JSON-Schema-validated hand-off envelopes between stages. Two execution paths (Express Mode + Q1-Q10 intake), layered precondition / bounce-back mechanics, and primary-source-grounded JP + ZH voice lineage craft.

## Status

- **v1.0.3** — current. Grill resolution strategy scope clarified per `superpowers` precedent.
- **v1.0.2** — Phase 8 word-count band rubric reconciled.
- **v1.0.1** — post-E2E-test hardening: tiered FATAL, Phase 7 brief-scope, conflict_flagged consumers, ZH lineage standard (新).
- **v1.0.0** — initial release. Coexists with `domain-teams:copywriting-team` for A/B comparison.

See [`CHANGELOG.md`](CHANGELOG.md) for full history.

## 9-Phase Pipeline

```
Phase 0  copywriting-intake                       mandatory (Q1-Q10 or Express)
Phase 1  [inline in intake]                       mandatory, LOOSE recommend planning-team
Phase 2  copywriting-ideation                     skippable
Phase 3  copywriting-neta-injection               skippable, hybrid pre/post
Phase 4  one of:                                  mandatory
           copywriting-short-form
           copywriting-mid-form
           copywriting-long-form-pasona
           copywriting-long-form-extended
           copywriting-light-action
Phase 5  copywriting-voice-positioning-stage      mandatory
Phase 6  copywriting-voice-tone-stage             mandatory
Phase 7  copywriting-ethics-check-stage           mandatory, evaluator-only
Phase 8  copywriting-form-check-stage             mandatory, evaluator-only
Alt      copywriting-audit-stage                  alternate entry for external copy
```

Entry router: `using-copywriting-toolkit`.

## Pipeline Flow

Full routing + validation + bounce-back topology:

```mermaid
flowchart TD
    Start([User brief OR resumed envelope]) --> Router[using-copywriting-toolkit<br/>router + validator<br/>single enforcement point]

    Router --> PreCheck{Entry type?}

    PreCheck -->|Shape A<br/>new raw brief| Q05[Step 0.5<br/>Express qualification]
    PreCheck -->|Shape B<br/>external copy + review| AuditEntry[copywriting-audit-stage<br/>Phase 1 Type ID]
    PreCheck -->|Shape C<br/>envelope present| ReentryChk[Step 2.3/2.4 re-entry checks]
    PreCheck -->|Shape D<br/>explicit skill name| DirectDispatch[Direct dispatch<br/>no routing]

    ReentryChk -->|total_retries >= 4<br/>OR bounce_round >= 3| Halt([HALT<br/>ask user])
    ReentryChk -->|violation present| BounceRoute[Route to violation.bounce_to<br/>bounce_round++]
    ReentryChk -->|unknown phase| Reject([Reject malformed<br/>structured error])
    ReentryChk -->|immutable field dropped| BounceWriter[Route to last-writer skill]
    ReentryChk -->|stale / missing L1| Q1Q10
    ReentryChk -->|valid continuation| PhaseRoute[Route by envelope.phase<br/>to next phase]

    BounceRoute --> Q1Q10
    BounceWriter -.-> P5 & P6 & P0
    PhaseRoute -.-> P2 & P4 & P5 & P6 & P7 & P8

    Q05 -->|ALL L1 present<br/>no red flag| Express[copywriting-intake<br/>Express Mode<br/>synthesis + 1-turn confirm]
    Q05 -->|L1 gaps OR<br/>red flag| Q1Q10[copywriting-intake<br/>Q1-Q10 multi-turn]

    Express --> Grill_E[Phase 0.5-B grill<br/>T1/T2/T3 classify<br/>Express-only output contract]
    Q1Q10 --> Grill_I[Q8 grill<br/>inline probe-and-resolve<br/>no tier concept]

    Grill_E -->|T1 AI-inferred FATAL| FallQ1Q10[ABORT Express<br/>force Q1-Q10]
    Grill_E -->|T3 outright violation| FallQ1Q10
    Grill_E -->|T2 user-stated<br/>benchmark missing| Confirm
    Grill_E -->|PASS / PASS_WITH_NOTES| Confirm[Single-turn confirmation<br/>Understanding Summary]
    Grill_I --> Q9[Q9 Understanding Summary<br/>3-option probe menu: supply/rewrite/drop]
    FallQ1Q10 --> Q1Q10

    Confirm --> P0[Intake Completeness<br/>MUST gate]
    Q9 --> P0
    P0 -->|PASS| Ideation{Phase 2 ideation?}
    P0 -->|NEEDS_REVISION| Q1Q10

    Ideation -->|yes| P2[copywriting-ideation<br/>Mandalart + KJ + Taniyama + VS]
    Ideation -->|skip| Neta1{Phase 3 pre-draft?}
    P2 --> Neta1

    Neta1 -->|bake-in<br/>default per brief heuristic| P3_Pre[copywriting-neta-injection<br/>Phase A-D WebSearch<br/>+ Neta Safety gate]
    Neta1 -->|skip| P4
    P3_Pre --> P4

    P4[Phase 4 drafter<br/>short / mid / long-pasona /<br/>long-extended / light-action]
    P4 --> Neta2{Phase 3 overlay?}

    Neta2 -->|overlay<br/>default when ambiguous| P3_Post[copywriting-neta-injection<br/>overlay + Neta Safety gate]
    Neta2 -->|skip| P5
    P3_Post --> P5

    P5[Phase 5<br/>voice-positioning-stage<br/>Q1-Q4 + Schwartz routing<br/>emits schwartz_alignment]
    P5 --> P6[Phase 6<br/>voice-tone-stage<br/>Pre-pass consumes schwartz_alignment<br/>+ 4-axis Pass 1 + context Pass 2]

    P6 --> P6Dual{Pass 3 trigger?}
    P6Dual -->|JP only<br/>ja / JP maestro / Q3+state-proposal| JPL[Pass 3a<br/>jp-copy-craft-lineage.md]
    P6Dual -->|ZH only<br/>zh / ZH maestro / Q2+TW 都會| ZHL[Pass 3b<br/>zh-copy-craft-lineage.md]
    P6Dual -->|both triggers match<br/>e.g. 糸井+zh-TW| P6Conflict[Emit violation<br/>bounce_to: intake<br/>router handles bounce]
    P6Dual -->|none| P7
    JPL --> P7
    ZHL --> P7
    P6Conflict -.-> Router

    P7[Phase 7<br/>ethics-check-stage<br/>MUST gate<br/>reads brief + draft]
    P7 -->|PASS| P8[Phase 8<br/>form-check-stage<br/>8a MUST + 8b SHOULD<br/>word-count band check<br/>schwartz_alignment consumer]
    P7 -->|NEEDS_REVISION<br/>景表法/FTC FAIL_FATAL| LoopP4[Default: Phase 4 drafter<br/>user-override: re-submit Phase 7 /<br/>restart thesis / drop claim]
    P7 -->|PASS_WITH_NOTES| P7Fix[Auto-revise FIXABLE<br/>max 1 round]
    P7Fix --> P7

    P8 -->|PASS| Deliver([Deliver final copy])
    P8 -->|PASS_WITH_NOTES| DeliverNotes([Deliver with notes])
    P8 -->|NEEDS_REVISION<br/>framework / length / CTA| LoopP4

    AuditEntry --> AuditDiag[Phase 2 Diagnose<br/>issue list by severity]
    AuditDiag --> AuditSug[Phase 3 Suggest<br/>+ optional rewrite variants]
    AuditSug --> P5

    AuditSug -->|N variants| VariantLoop[Per-variant sub-pipeline<br/>Phase 7 + 8 serial<br/>independent revise_round_count]
    VariantLoop -->|each variant| P7
    VariantLoop --> AuditReport([Audit report<br/>rewrite_variants with verdicts])

    LoopP4 -->|revise_round_count < 2<br/>AND total_retries < 4| P4
    LoopP4 -->|>= 2 OR total_retries >= 4| Halt

    classDef router fill:#e1f5ff,stroke:#0277bd,stroke-width:2px
    classDef gate fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef draft fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef halt fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef deliver fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef audit fill:#f9fbe7,stroke:#827717,stroke-width:2px

    class Router,Q05,PreCheck,ReentryChk,BounceRoute,BounceWriter,PhaseRoute,P6Conflict router
    class P0,P7,P8,P7Fix gate
    class P4,P5,P6,JPL,ZHL,P2,P3_Pre,P3_Post draft
    class Halt,LoopP4,FallQ1Q10,Reject halt
    class Deliver,DeliverNotes,AuditReport deliver
    class AuditEntry,AuditDiag,AuditSug,VariantLoop audit
```

**Diagram legend**:

- 🔵 **Router nodes** (light blue) — `using-copywriting-toolkit`, Step 0.5 qualification, Step 2.3/2.4 re-entry checks, Phase 6 dual-trigger violation emit, and intermediate routing decisions. All bounce logic lives here (L2 single enforcement point).
- 🟠 **Gates** (light orange) — Intake Completeness MUST + Phase 7 ethics MUST + Phase 8 form 8a/8b.
- 🟣 **Drafting skills** (light purple) — Phase 2/3/4/5/6 where `copywriter` agent produces artifacts.
- 🟡 **Audit sub-pipeline** (light yellow) — Phase 1/2/3 of audit-stage + per-variant re-gating loop.
- 🔴 **HALT / abort paths** (light red) — retry-cap exhaustion, malformed envelope rejection, Q1-Q10 fallback.
- 🟢 **Delivery** (light green) — final artifact exit points.

Dashed edges represent routing hand-offs (router-mediated), solid edges are direct pipeline flow.

## Two Execution Paths for Intake

Paths resolve FATAL candidates differently, by design (mirrors `superpowers:brainstorming` vs `superpowers:subagent-driven-development`):

| Path | Trigger | Turns | Grill resolution |
|---|---|---|---|
| **Q1-Q10** | Brief missing Level 1 fields, bounce-back, or user asks for full intake | ~10-14 user turns | **Inline probe-and-resolve** — agent offers 3-option menu (supply / rewrite / drop) at Q8; no tier concept |
| **Express** | Brief carries all Level 1 fields; no red flag | ~3 user turns | **Structured tier return** — T1 ABORT / T2 CARRY / T3 ABORT; tier is an evaluator output contract, analogous to `superpowers` subagent status codes |

See [`skills/copywriting-intake/SKILL.md §Execution Paths`](skills/copywriting-intake/SKILL.md).

## Skills

| Skill | Phase | Role |
|---|---|---|
| `using-copywriting-toolkit` | router | Entry + Preconditions validator + Express qualification + bounce-back enforcement |
| `copywriting-intake` | 0-1 | Brief intake (Q1-Q10 or Express) + Intake Completeness MUST gate |
| `copywriting-ideation` | 2 | Mandalart + KJ + Taniyama + VS divergence / convergence |
| `copywriting-neta-injection` | 3 | Neta overlay (pre-draft bake-in or post-draft overlay) + Neta Safety SHOULD gate |
| `copywriting-short-form` | 4 | キャッチコピー / headline (7-15 chars, AIDMA A+I, 5 切入點) |
| `copywriting-mid-form` | 4 | EC product copy (BEAF: Benefit → Evidence → Advantage → Feature) |
| `copywriting-long-form-pasona` | 4 | PASONA / 新PASONA / PASBECONA (神田昌典 canonical) |
| `copywriting-long-form-extended` | 4 | QUEST (Fortin 2005) / PASTOR (Edwards 2016) |
| `copywriting-light-action` | 4 | PREP / CREMA micro-conversion (Kaushik 2007) |
| `copywriting-voice-positioning-stage` | 5 | Voice Quadrant (Authority↔Affinity × Reason↔Emotion) + Schwartz routing |
| `copywriting-voice-tone-stage` | 6 | 4-axis tone + Mailchimp context-switching + JP/ZH lineage Pass 3 |
| `copywriting-ethics-check-stage` | 7 | 景品表示法 / FTC / Cialdini misuse / dark-pattern MUST gate |
| `copywriting-form-check-stage` | 8 | Framework adherence (8a MUST) + qualitative (8b SHOULD) |
| `copywriting-audit-stage` | alt | Audit external copy through Phases 5-8 |

## Agents

Plugin-local pair (not shared with `domain-teams`):

| Agent | Persona | Model | Role |
|---|---|---|---|
| `copywriter` | Reader-first in 糸井 / Ogilvy / Cialdini / Schwartz lineages + 谷山 discipline + 小霜「嘘をつかない」 | sonnet | Drafting, ideation, audit variants |
| `copywriter-evaluator` | Strict legal / framework reviewer — NOT a copywriter; aesthetic-capture explicitly anti-pattern | opus | Gate verdicts only; does not draft or soften |

Persona separation is deliberate — a charmed copywriter lets 景表法 claims through; a cautious evaluator produces clinical copy. Keeping them apart keeps each role honest.

## Envelope Contract

JSON-Schema-validated handoff between skills. See [`.claude-plugin/envelope.schema.json`](.claude-plugin/envelope.schema.json).

Key invariants:

- **Router is single enforcement point** — validates each skill's `## Preconditions` schema before launch. No downstream skill self-validates.
- **Violation envelope** — on precondition failure, router emits bounce-back shape (`detected_by`, `missing`, `bounce_to`, `bounce_round`, `user_message`) and routes upstream.
- **Retry caps** — `bounce_round ≥ 3` → HALT; `revise_round_count ≥ 2` per phase → HALT; `total_retries ≥ 4` aggregate → HALT.
- **Audit trail** — `audit_trail[]` on envelope logs skill-entered / gate-verdict / violation-detected / bounce-dispatched / halt-ask-user events.

## Grounding (primary sources)

Standards preserved byte-identical from `domain-teams:copywriting-team`:

- 神田昌典 2016/2021 PASONA / 新PASONA / PASBECONA
- 谷山雅計 2007 散らかす→選ぶ→磨く + なんかいいよね禁止
- 今泉浩晃 1987 曼陀羅発想法
- 川喜田二郎 1967 KJ法
- Cialdini 1984 *Influence*
- Schwartz 1966 *Breakthrough Advertising*
- Zhang et al. 2025 Verbalized Sampling (arXiv:2510.01171)
- Fortin 2005 QUEST / Edwards 2016 PASTOR
- 小霜和也 2010/2014 本能分析
- 秋山隆平・杉山恒太郎 2004 AISAS / 飯髙悠太 2019 ULSSAS
- Kaushik 2007 micro/macro conversion
- McQuarrie & Mick 1996 rhetorical operations / Lakoff & Johnson 1980 conceptual metaphor / Thornton 1995 subcultural capital
- 景品表示法 (2023 amendment, effective 2024-10-01) + FTC Endorsement Guides (16 CFR 255)
- Vaughn 1980 FCB × Halliday 1978 SFL (2-axis Voice Quadrant — team synthesis)

Voice lineage craft (Tier 3 deep-dive standards):

- **JP** — `jp-copy-craft-lineage.md` (cp from domain-teams): 糸井重里 / 岩崎俊一 / 眞木準 / 谷山雅計 via TCC 年鑑
- **ZH** — `zh-copy-craft-lineage.md` (NEW in v1.0.1, primary-source-researched for this toolkit): 許舜英 (意識形態 / 中興百貨 1988-1999, 11 dated corpus entries) / 李欣頻 (誠品敦南 1990s-2000s, 7 entries) / 葉明桂 (奧美 / 左岸 1998-, 3 entries + strategic frameworks). Includes 4 attribution corrections (#Z1-#Z4) and per-master LLM reproduction gap analysis.

## A/B with `domain-teams:copywriting-team`

Original `domain-teams:copywriting-team` remains untouched (copy-first principle — all cp'd files byte-identical). Run both on the same brief and compare output quality, gate catch rate, and interaction cost. Both plugins coexist; consolidation deferred to post-A/B retrospective.

## Install

Plugin loads via the `monkey-skills` marketplace. See repo-root `.claude-plugin/marketplace.json` entry. Once marketplace loads, all 14 skills + 2 agents + plugin-level conventions (CLAUDE.md) resolve automatically.

Setup detail, permissions, model tiers, persistence model: see [`CLAUDE.md §Setup`](CLAUDE.md).

## License

MIT — see repository root.
