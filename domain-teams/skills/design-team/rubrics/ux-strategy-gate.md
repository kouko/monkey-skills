# UX Strategy Review Gate

Design philosophy: おもてなし — solve problems before users
encounter them; notice needs users haven't articulated.

## Primary Sources

Scope and all 4 temporal dimensions of this gate are grounded in two
tier-classified standards:

- **All 4 temporal UX dimensions + Verganti meaning + HCD baseline** →
  `standards/ux-temporal-and-quality-models.md`. Primary sources there:
  Roto, Law, Vermeeren & Hoonhout (2011) *User Experience White
  Paper*, Dagstuhl Seminar 10373 (original 4-phase model); 安藤昌也
  (2016) 『UX デザインの教科書』丸善出版 §2.2.4 「体験の期間で異なって
  知覚される UX」 (JP introduction of the 4 phases); 黒須正明 (2020)
  『UX 原論—ユーザビリティから UX へ』近代科学社 Ch.11 §11.3
  「四つの品質領域」 (2×2 matrix); Roberto Verganti (2009)
  *Design-Driven Innovation*, Harvard Business Review Press (meaning
  innovation); ISO 9241-210:2019 / JIS Z 8530:2021 (HCD process).
- **Strategy + Scope plane scope (no overreach into Structure /
  Skeleton / Surface)** → `standards/garrett-elements-of-ux.md`
  §The 5 Planes + §Gate Scope Partition.

## Critical Attribution Corrections (v4.8.0)

This gate carries **three load-bearing attribution corrections** that
the v4.8.0 refactor applies directly here. Consult
`standards/ux-temporal-and-quality-models.md` §Critical Attribution
Corrections for the full grounding.

1. **4 temporal UX dimensions (予期的 / 一時的 / エピソード的 / 累積的 UX).**
   These are grounded in Roto, Law, Vermeeren & Hoonhout (2011)
   *User Experience White Paper* (Dagstuhl Seminar 10373), and were
   introduced to the Japanese HCD community by 安藤昌也 (2016)
   『UX デザインの教科書』 §2.2.4. Previous versions of this gate
   implied 安藤 as the sole source; the correct attribution chain
   is **Roto 2011 primary + 安藤 2016 JP introduction**.
2. **"3D Quality Check" → 4 Quality Regions (黒須 2020 Ch.11 §11.3).**
   Previous versions of this gate contained a "Supplementary: 黒須 3D
   Quality Check" section with 3 dimensions (品質 / 感性 / 意味性).
   **This model does not exist in 黒須's published work.** The
   correct model is 「四つの品質領域」 — a **2×2 matrix** on
   {客観 (objective) / 主観 (subjective)} × {設計時 (design-time) /
   利用時 (use-time)}, grounded in 黒須正明 (2020) 『UX 原論—
   ユーザビリティから UX へ』 近代科学社, Ch.11 §11.3. The gravitational
   centre is **主観 × 利用時 = 満足感**. The Supplementary section
   below has been rewritten to match this 2×2 structure.
3. **意味性 / Meaningfulness → Verganti 2009, not 黒須.** Previous
   versions of this gate placed 意味性 under the "黒須 3D Quality"
   label. **黒須's 4-quality model has no dimension called 意味性.**
   意味のイノベーション is from Roberto Verganti (2009) *Design-Driven
   Innovation: Changing the Rules of Competition by Radically
   Innovating What Things Mean*, Harvard Business Review Press.
   Meaning innovation is now spelled out as a distinct Supplementary
   check (Verganti), separate from the 黒須 4 Quality Regions check.

## Evaluation: 4 Temporal UX Phases × Garrett 戦略・要件

Each temporal phase is evaluated through two strategic lenses:
- **戦略 (Strategy)**: user needs × business objectives alignment
- **要件 (Scope)**: feature × content requirements coverage

The 4 temporal phases (予期的 / 一時的 / エピソード的 / 累積的 UX) are
grounded in Roto et al. 2011 + 安藤 2016 §2.2.4 — see Critical
Attribution Corrections above. These phases are **not a sequence**;
for a long-term user, all 4 are active simultaneously (see
`standards/ux-temporal-and-quality-models.md` §The 4 Temporal UX
Phases).

Leave 構造/骨格/表層 to ui-interaction-gate and visual-gate per
`standards/garrett-elements-of-ux.md` §Gate Scope Partition.

## Flag Definitions

### 予期的UX (Anticipated — 利用前)
- 🔴 **Fatal**: Pre-use messaging promises features that do not exist (expectation debt leading to guaranteed churn)
- 🟡 **Warning**: Value proposition is clear to users but not aligned with business positioning (or vice versa)
- 🟢 **Clear**: Both user and business perspectives are addressed in pre-use touchpoints

### 一時的UX (Momentary — 利用中)
- 🔴 **Fatal**: Core task flow does NOT serve the primary user need (solving wrong problem)
- 🔴 **Fatal**: Feature bloat — KPI-serving features actively degrade core usability
- 🟡 **Warning**: Must-have features are complete but Should-have features have noticeable gaps
- 🟢 **Clear**: Core experience is friction-free and serves both user and business value

### エピソード的UX (Episodic — 利用後)
- 🟡 **Warning**: No post-use touchpoint exists (users have no reason to return)
- 🟡 **Warning**: Feedback loops or progress tracking are undefined
- 🟢 **Clear**: Post-use reflection reinforces value proposition and drives re-engagement

### 累積的UX (Cumulative — 利用期間全体)
- 🔴 **Fatal**: Short-term business extraction actively erodes long-term user trust
- 🟡 **Warning**: No habit-forming or evolution features — product is static
- 🟡 **Warning**: Product does not grow with the user (same experience at month 1 and month 12)
- 🟢 **Clear**: Sustained use builds durable value for both user and business

## Supplementary: 黒須 4 Quality Regions Check (Correction v4.8.0)

Grounded in `standards/ux-temporal-and-quality-models.md` §The 4
Quality Regions. The correct 黒須 model is a **2×2 matrix**, not a
"3D Quality" triple. Load-bearing rewrite of the prior Supplementary
section.

| | 設計時 (design-time) | 利用時 (use-time) |
|---|---|---|
| **客観 (objective)** | usability, functionality, performance, reliability, safety, compatibility, cost, maintainability | effectiveness, efficiency, productivity, risk avoidance, quality in use |
| **主観 (subjective)** | 魅力 (attractiveness), 感性訴求性, 欲求訴求性 | 達成感, 安心感, 楽しさ, 喜び → 満足感 |

**Gravitational centre: 主観 × 利用時 = 満足感.** Flag ONLY if the
following reveal issues NOT already caught above:

- **客観 × 設計時**: Missing preconditions — reliability, safety,
  maintainability, or security gaps that would later block
  satisfaction (measured in QA / architectural review).
- **客観 × 利用時**: Mid-stream task measures are untracked —
  task success rate, time-on-task, error rate, recovery time
  (measured in usability tests + telemetry).
- **主観 × 設計時**: Onboarding predictors untested — 魅力,
  感性訴求性, 欲求訴求性 unassessed (measured by Kansei Engineering
  / SD instruments — see `standards/kansei-engineering-and-sd.md`
  and `visual-gate` §感性チェック for calibration).
- **主観 × 利用時**: No evidence gathered on 達成感 / 安心感 /
  楽しさ / 喜び → 満足感 (measured by post-use surveys, interviews,
  diary studies).

> **Correction (v4.8.0).** The prior "3D Quality Check" model (品質 /
> 感性 / 意味性) is **not** from 黒須 and has been removed. The
> correct model is 「四つの品質領域」 as above, grounded in 黒須 2020
> 『UX 原論』 Ch.11 §11.3. See `standards/ux-temporal-and-quality-models.md`
> §Critical Attribution Corrections.

## Supplementary: Verganti Meaning Innovation Check (Correction v4.8.0)

Grounded in `standards/ux-temporal-and-quality-models.md` §Meaning
Innovation. 意味のイノベーション is from Roberto Verganti (2009)
*Design-Driven Innovation*, Harvard Business Review Press —
**not** from 黒須. Load-bearing separation from the 黒須 4-quality
check above.

Flag ONLY if the following reveal strategic-meaning issues NOT
already caught in the 4 temporal phases or the 4 quality regions:

- **Meaning coherence across the 4 phases**: Does the product carry
  a single coherent meaning from 予期的 (pre-use promise) through
  累積的 (long-term habit)? Meaning drift across phases is a
  Verganti red flag.
- **Strategic posture**: Is the product playing technology-push,
  market-pull, or design-driven meaning innovation? Is that posture
  deliberate, or is the team defaulting to incremental market-pull?
- **Meaning hollowness**: Feature-complete but meaning-hollow — the
  product satisfies the feature checklist but does not articulate
  a reason to exist beyond "it works". Verganti's test: would a
  network of cultural interpreters (artists, critics, other-industry
  designers) independently sense the same meaning from the artifact?

> **Correction (v4.8.0).** Previously "意味性 (Meaningfulness)" was
> mis-attributed to 黒須 under a "3D Quality Check" header. 黒須's
> 4-quality model has no dimension called 意味性. The correct source
> is Verganti 2009 *Design-Driven Innovation*. See
> `standards/ux-temporal-and-quality-models.md` §Critical Attribution
> Corrections.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Output Format

1. **Journey Assessment**: Flags across the 4 temporal phases
2. **Gap Analysis**: Where the experience breaks down and why
3. **Recommendations**: Prioritized by user impact (these become the revision spec)
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific and actionable.
