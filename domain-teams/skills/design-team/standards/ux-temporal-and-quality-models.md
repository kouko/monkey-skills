---
title: UX Temporal and Quality Models
tier: 3
---

# UX Temporal and Quality Models

Tier 3 standard: fully self-contained. Consolidates three distinct
models that together cover "when is UX happening?" and "what kind of
judgment is being made?" — the 4 temporal UX phases (Roto et al. 2011
+ 安藤 2016), the 4 Quality Regions 2×2 matrix (黒須 2020), the 3
innovation paths including meaning innovation (Verganti 2009), and
the ISO 9241-210 / JIS Z 8530 human-centred design process. This file
is the v4.7.2 load-bearing test case: it replaces a "3D Quality Check"
model that does not exist in 黒須's published work, and reassigns
意味のイノベーション from 黒須 to Verganti 2009 where it actually
originates.

## Primary Sources

- Virpi Roto, Effie Lai-Chong Law, Arnold P.O.S. Vermeeren, Jettie Hoonhout (2011) *User Experience White Paper: Bringing clarity to the concept of user experience*. Dagstuhl Seminar 10373. http://www.allaboutux.org/uxwhitepaper. Original source for the 4 temporal UX phases.
- 安藤昌也 (2016) 『UX デザインの教科書』. 丸善出版. §2.2.4 「体験の期間で異なって知覚される UX」 introduces the 4 temporal phases to the Japanese HCD community.
- 黒須正明 (2020) 『UX 原論—ユーザビリティから UX へ』. 近代科学社. Ch.11 §11.3 「四つの品質領域」 defines the 2×2 quality matrix (objective / subjective × design-time / use-time).
- Roberto Verganti (2009) *Design-Driven Innovation: Changing the Rules of Competition by Radically Innovating What Things Mean*. Harvard Business Review Press. Primary source for meaning innovation and interpreters. **Not 黒須.**
- ISO 9241-210:2019 *Ergonomics of human-system interaction — Part 210: Human-centred design for interactive systems*. https://www.iso.org/standard/77520.html. International standard for the human-centred design process and its 6 principles.
- JIS Z 8530:2021 人間工学—人とシステムとのインタラクション—インタラクティブシステムの人間中心設計. Japanese MOD adoption of ISO 9241-210:2019.

## Critical Attribution Corrections

- **"3D Quality" does not exist.** Earlier `ux-strategy-gate.md`
  referred to a "黒須 3D Quality Check" framework with 3 axes
  (品質 / 感性 / 意味性). This model does not exist in 黒須's
  published work. The correct model is **四つの品質領域 (4 Quality
  Regions)**, a 2×2 matrix of {objective 客観 / subjective 主観} ×
  {design-time 設計時 / use-time 利用時}, grounded in 黒須 2020
  Ch.11 §11.3. **Do not cite "3D Quality".**
- **意味のイノベーション attribution.** Earlier `ux-strategy-gate.md`
  attributed 意味性 / Meaningfulness to 黒須. 黒須's 4-quality
  model has **no dimension called 意味性**. Meaning innovation is
  from Verganti 2009, where it is the third strategic path
  alongside technology-push and market-pull. Cite Verganti 2009,
  not 黒須, for any 意味 claim.
- **黒須 2020 metadata correction.** Earlier Phase 1 gap report
  listed 黒須's book with year 2013 and publisher "KOKUSAI". The
  correct metadata is **year 2020, publisher 近代科学社**. 黒須 does
  have a separate 2013 book (『人間中心設計の基礎』, 近代科学社) but
  that is a distinct title; do not conflate the two. The full
  13-digit catalogue identifier for the 2020 *UX 原論* is recorded
  in the layer-3 research note per the v4.7.2 catalogue-identifier-
  in-research-only rule.

## Framing

UX is experienced on two orthogonal axes:

- **Time** — when is the user experiencing this? Anticipated,
  momentary, episodic, or cumulative.
- **Quality** — what kind of judgment is being made? Objective or
  subjective, at design-time or at use-time.

Time answers *"when"*, quality answers *"what kind of judgment"*.
This standard consolidates both models, plus the complementary
meaning-innovation strategic frame (Verganti) and the process
baseline (ISO 9241-210 / JIS Z 8530).

## The 4 Temporal UX Phases (Roto et al. 2011)

Introduced to the Japanese HCD community by 安藤 2016 §2.2.4. The 4
phases are distinct temporal loci at which a user forms an
experience of the same artifact.

| Phase | English | JP | Temporal locus | Judgment criteria |
|---|---|---|---|---|
| Anticipated UX | Anticipated | 予期的 UX | Before first use | Brand impression, marketing promise, word of mouth, app-store preview, icon and name evoke expectation |
| Momentary UX | Momentary | 一時的 UX | During interaction | Immediate feedback, motion response, haptic, sensory delight in the instant |
| Episodic UX | Episodic | エピソード的 UX | After a concrete session | Memory of a specific episode ("yesterday's checkout was fast"), narrative recall, willingness to tell others |
| Cumulative UX | Cumulative | 累積的 UX | Long-term, across many episodes | Habit formation, loyalty / attrition, brand love, integration into daily life |

**Important: these phases are not a sequence.** For a long-term
user, all 4 are active **simultaneously** — current in-session
(Momentary), memory of the last session (Episodic), anticipation of
an upcoming feature release (Anticipated), and long-term habit
(Cumulative). A design evaluation should check all 4 regions, not
just the one in which the evaluation session takes place; a
satisfaction score taken at the end of a task-based usability test
only measures Episodic UX and should not be reported as the
"overall UX".

## The 4 Quality Regions (NOT "3D Quality") — 黒須 2020 Ch.11 §11.3

**This model is never called "3D Quality" in 黒須's work.** The
correct name is **四つの品質領域**, a 2×2 matrix built on two
orthogonal axes:

- **Axis 1:** 客観 (objective) / 主観 (subjective)
- **Axis 2:** 設計時 (design-time) / 利用時 (use-time)

The full 2×2 table:

|  | 設計時 (design-time) | 利用時 (use-time) |
|---|---|---|
| **客観 (objective)** | usability, functionality, performance, reliability, safety, compatibility, cost, maintainability | effectiveness, efficiency, productivity, risk avoidance, quality in use |
| **主観 (subjective)** | 魅力 (attractiveness), 感性訴求性, 欲求訴求性 | 達成感, 安心感, 楽しさ, 喜び → 満足感 |

**Gravitational centre: 主観 × 利用時 = 満足感.** All four regions
flow toward subjective-at-use-time satisfaction as the integrating
outcome:

- Objective design-time qualities (reliability, safety, maintainability)
  are **preconditions** — they do not themselves generate
  satisfaction, but their absence blocks it.
- Objective use-time qualities (efficiency, productivity, quality in
  use) are **mid-stream measures** — observable during the task but
  not the endpoint.
- Subjective design-time qualities (attractiveness, 感性訴求性,
  欲求訴求性) are **onboarding predictors** — they pull users in
  and set expectations for the use-time experience.
- Subjective use-time qualities converge into **満足感** — the
  integrating endpoint.

**Judgment criteria per region:**

- **客観 × 設計時** — testable, specification-driven; measured in
  QA, performance audits, security reviews, and architectural
  review.
- **客観 × 利用時** — measured in usability tests and telemetry:
  task success rate, time-on-task, error rate, recovery time.
- **主観 × 設計時** — measured by Kansei Engineering and SD
  instruments (see `kansei-engineering-and-sd.md`) and by expert
  aesthetic critique before release.
- **主観 × 利用時** — measured by post-use surveys, interviews,
  diary studies, satisfaction ratings, and NPS.

## Meaning Innovation (意味のイノベーション) — Verganti 2009, not 黒須

**Critical attribution:** 意味のイノベーション is from Verganti 2009.
黒須's 4-quality model contains **no** dimension named 意味性. Any
load-bearing 意味 claim in the design-team gate hierarchy must cite
Verganti, not 黒須.

**Verganti's 3 innovation paths:**

1. **Technology-push** — innovation driven by R&D capability. The
   product is novel because the underlying technology is new
   (e.g., the first capacitive multi-touch phone).
2. **Market-pull** — innovation driven by user-research refinement.
   The product is better because it answers observed user needs
   more precisely (e.g., incremental feature additions guided by
   A/B tests).
3. **Design-driven innovation** — innovation by radically changing
   the **meaning** of the artifact. The Nintendo Wii changed the
   meaning of game consoles from "hardcore leaderboard device" to
   "family living-room activity"; the iPod changed the meaning of
   MP3 players from "pocket device" to "music collection curator".
   Competitors cannot close this gap by better specs alone, because
   the meaning — not the spec — is what the user is buying.

**Interpreters.** Verganti's mechanism for design-driven innovation
is not direct user research: users extrapolate from current meaning
and cannot articulate a not-yet-existing new meaning. Instead, the
designer engages a **network of interpreters** — artists, other
industry designers, critics, craft experts, magazine editors,
academic researchers, technology suppliers — each of whom is
independently sensing cultural shifts in their own domain. The
designer **synthesizes across interpreters** to anticipate a
meaning shift that no single user or interpreter could articulate.
This is why user interviews alone cannot produce design-driven
innovation: the signal lives between interpreters, not inside
individual respondents.

## Human-Centred Design Process — ISO 9241-210:2019 / JIS Z 8530:2021

ISO 9241-210:2019 defines the human-centred design process for
interactive systems. The standard lists **6 principles**:

1. The design is based upon an explicit understanding of users,
   tasks, and environments.
2. Users are involved throughout design and development.
3. The design is driven and refined by user-centred evaluation.
4. The process is iterative.
5. The design addresses the whole user experience (not only the
   artifact itself; includes anticipated, momentary, episodic, and
   cumulative UX — cross-reference the 4 temporal phases above).
6. The design team includes multidisciplinary skills and
   perspectives.

**JIS Z 8530:2021** is the Japanese MOD (modified) adoption of
ISO 9241-210:2019 — the 6 principles are identical; JIS Z 8530
adds Japan-specific normative references and terminology anchors.
When citing in a Japanese-language context, cite both: the ISO
principle is the international anchor; the JIS adoption is the
domestic normative reference.

## How the Three Models Compose

- **ISO 9241-210 / JIS Z 8530** defines the **process** a team
  should run.
- **Roto 2011 / 安藤 2016** defines the **temporal scope** that
  process must cover (all 4 phases, not only the evaluation
  session).
- **黒須 2020** defines the **quality regions** the process must
  evaluate at each phase (4 regions, centred on 主観 × 利用時 =
  満足感).
- **Verganti 2009** defines the **strategic posture** the process
  can take (technology-push, market-pull, or design-driven
  meaning innovation).

A design-team workflow that runs ISO 9241-210 iterations, evaluates
all 4 temporal phases, scores all 4 quality regions, and chooses a
deliberate strategic posture is fully grounded. Omitting any of the
four composes a blind spot: skipping the temporal axis misses
cumulative UX; skipping quality regions misses subjective
design-time predictors; skipping strategic posture reduces design
to incrementalism.
