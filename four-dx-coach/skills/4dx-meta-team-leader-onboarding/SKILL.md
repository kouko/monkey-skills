---
name: 4dx-meta-team-leader-onboarding
description: |
  Coaches a leader-of-leaders to earn commitment (not compliance) from report team-leaders before launching 4DX. Use when rolling 4DX out without prepping buy-in: 'get my leaders on board', 'pilot or mandate?'. Bought-in cascade → wig-cascade.
source_book: "The 4 Disciplines of Execution (2nd ed.) — Chris McChesney, Sean Covey, Jim Huling, Scott Thele, Beverly Walker"
source_chapter: "Chapter 8 — Getting Your Leaders on Board"
source_language: en
tags: [change-management, buy-in, leader-of-leaders, commitment-vs-compliance, pre-cascade, organizational-rollout, audit, onboarding-diagnosis]
related_skills:
  - 4dx-meta-strategy-triage
  - 4dx-d1-wig-cascade
  - 4dx-d4-cadence
  - 4dx-sustain-momentum-rescue
  - 4dx-audit
  - using-four-dx-coach
---

# 4dx-meta-team-leader-onboarding — Earning commitment, not compliance (dual-mode)

## Mission

Coach the leader-of-leaders through earning genuine commitment from
their direct-report team-leaders before 4DX launches — in whichever of
two modes the situation demands: **coach-mode** (prepare the buy-in
conversation Socratically, no past artifacts) or **audit-mode**
(diagnose what went wrong on a past onboarding attempt from rollout
email / kickoff slides / 1:1 transcripts / team feedback). Same
Chapter-8 rule set (transparency / understanding / involvement +
voluntary-opt-in pilot) applied in two voices: forward-looking
Socratic for coach-mode, backward-looking artifact-synthesis for
audit-mode.

## When this skill activates

### Coach-mode triggers (no past artifacts; preparing the conversation)

- EN: "How do I get my team-leaders on board with 4DX?", "My direct
  reports will resist this — how do I roll it out?", "How do I avoid
  this looking like another corporate flavor-of-the-month?",
  "Should I pilot or mandate?", "Leader X will hate this — what do
  I say?"
- JP: 「部下リーダーに 4DX を腹落ちさせたい」「直属マネージャーが
  反発しそう、どう導入する」「また流行りの施策と思われたくない」
  「全社展開かパイロットか」「〇〇さんが反対しそう、どう話す」
- zh-TW: 「我要怎麼讓我的下屬 leader 們真心接受 4DX？」
  「我的直屬主管會抵抗，要怎麼導入」「不想被當成又一個流行 KPI 工具」
  「要全面導入還是先做 pilot？」「〇〇 一定會反對，我要怎麼跟他談」

### Audit-mode triggers (past onboarding ran; diagnosing from artifacts)

- EN: "Audit our onboarding — team isn't bought in", "Leaders
  complying not committing — what went wrong?", "Got feedback our
  rollout didn't land — diagnose", "Stakeholder wants to revisit how
  we onboarded leaders", "My boss flagged the team isn't really
  bought in — help me see why", "Here's the rollout email + 1:1
  transcripts — diagnose"
- JP: 「チーム導入したが反発が強い、何が間違ってた？」「リーダー陣が
  表面的に従ってるだけ、何が抜けた？」「上司にフィードバックされた、
  rollout 見て」「マネージャーから方向性を直したいと言われた、
  onboarding 診断して」「ロールアウトメールと議事録、見て診断して」
- zh-TW: 「導入了 4DX 但團隊不買單，幫我診斷」「下屬 leader 表面配合
  心裡抗拒，問題在哪？」「主管覺得 rollout 沒做好，幫看哪裡」「review
  後想討論 onboarding 方向」「rollout 信件加上幾週的 leader 回饋，幫
  我看哪裡走樣」

### Non-activation signals (DO NOT fire when…)

- User has not decided 4DX fits the org → `4dx-meta-strategy-triage` first
- Buy-in is already secured; user wants the technical cascade →
  `4dx-d1-wig-cascade`
- Frontline-team-member buy-in (one level below this skill's scope) →
  D1 Team-WIG-choosing process via `4dx-d1-wig-cascade`
- Generic change management not 4DX-specific → Kotter / ADKAR /
  Bridges or domain-team change-management skill
- **Cadence collapsed multi-week post-onboarding** → `4dx-sustain-momentum-rescue`
  (this overrides audit-mode — audit-mode requires the *onboarding*
  was malformed, not that the cadence has since stopped)
- **Cross-layer audit** (WIG / leads / scoreboard / cadence diagnosed
  together from artifacts) → `4dx-audit` (this skill's audit-mode is
  **onboarding-layer-only**)

## Mode detection

When this skill activates:

1. Determine **interaction shape first**: **coach-mode** (Socratic,
   forward-looking, no past onboarding artifacts) vs **audit-mode**
   (synthesis from provided artifacts — rollout email / kickoff slides
   / 1:1 transcripts / team-feedback quotes, often + stakeholder
   critique). Audit signals: user pastes/attaches/references "rollout
   email", "kickoff deck", "leader 1:1 notes", "team feedback",
   "boss says...", "team says they're not bought in".
2. **Audit-mode pre-check** — before loading audit-mode, screen for
   **multi-week consecutive cadence collapse** post-onboarding. If
   present, route to `4dx-sustain-momentum-rescue` instead — the
   problem is downstream cadence breakage, not upstream onboarding
   malformation.
3. Load the matching protocol file from `protocols/`.
4. Follow that protocol's E section step-by-step.

If ambiguous after reading the user's query, ask ONE question:

> EN: "Quick check — are you (a) **preparing the buy-in conversation**
> (no rollout has happened yet)? Then I'll run coach-mode. Or (b)
> **diagnosing a past onboarding** (you have rollout email / 1:1
> transcripts / team feedback)? Then I'll run audit-mode."
>
> JP: 「確認: (a) **これから buy-in 対話を準備** (まだロールアウトしてない)
> なら coach-mode。(b) **過去の onboarding を診断** (rollout メール /
> 1:1 議事録 / チームフィードバックがある) なら audit-mode。」
>
> zh-TW: 「快速確認：(a) **準備 buy-in 對話**（還沒 rollout）→ coach-mode；
> (b) **診斷過去的 onboarding**（有 rollout 信件 / 1:1 紀錄 / 團隊回饋）→ audit-mode。」

If the signal in the original query is strong, skip the question and load the protocol directly.

## Protocol routing table

| Detected mode | Load protocol | Agent voice |
|---|---|---|
| Coach (no past artifacts; preparing) | `protocols/coach-mode.md` | consultant-to-single-leader-of-leaders |
| Audit (past artifacts + critique; diagnosing) | `protocols/audit-mode.md` | consultant-from-artifacts |

After loading the protocol, follow its E section step-by-step. Each protocol carries its own R / I / A1 / A2 / E / B sections; this orchestrator does not run any onboarding content directly.

### Edge-case routing

- **Past onboarding ran but cadence has since collapsed** — fire
  `4dx-sustain-momentum-rescue` first; audit-mode here is for
  malformed-onboarding-but-cadence-still-running, not collapse.
- **Audit request without artifacts** — if user asks for an audit but
  provides no rollout copy / 1:1 notes / team feedback, ask once for
  artifacts; if none available, decline audit-mode and route to
  coach-mode to prepare a re-launch from scratch.
- **Cross-layer audit (WIG + leads + scoreboard + cadence)** — that's
  `4dx-audit`, not this skill's audit-mode.
- **Pre-fit-decision rethink uncovered mid-audit** — if the audit
  reveals 4DX didn't fit the org in the first place, route to
  `4dx-meta-strategy-triage`; do not push through.

## Cross-skill relations

- **Upstream prerequisite** — `4dx-meta-strategy-triage` must conclude
  4DX fits the org before either mode of this skill is meaningful.
  Coach-mode also presumes draft Primary + Key Battle WIGs in hand.
- **Downstream successor** — `4dx-d1-wig-cascade` runs after coach-mode
  succeeds (buy-in earned → technical Team-WIG cascade); `4dx-d4-cadence`
  runs the live weekly WIG Session that buy-in unlocks.
- **Compose-with neighbour** — `4dx-sustain-momentum-rescue` runs *after*
  cadence breaks post-onboarding; audit-mode here runs *upstream* of
  rescue (the buy-in itself was malformed before cadence even started
  to break).
- **Cross-layer audit** — `4dx-audit` audits WIG / leads / scoreboard /
  cadence together; this skill's audit-mode is onboarding-layer-only.
- **Plugin-router fallback** — `using-four-dx-coach` handles cold-start
  triage and out-of-4DX queries; not a substitute for this skill, but
  the right hand-off when the user's question turns out not to be 4DX
  Chapter-8 onboarding.

## Boundary (cross-mode common)

The mode-specific boundary lives in each protocol's B section. The cross-mode common boundary:

- **Leader-of-leaders scope only** — both modes assume the user has
  named direct-report team-leaders. For frontline-member buy-in (one
  level below), use the D1 Team-WIG-choosing process in
  `4dx-d1-wig-cascade`. For solo / personal-scale 4DX, use
  `4dx-meta-strategy-triage` and downstream personal coach skills.
- **Commitment is the load-bearing mechanism across both modes** —
  coach-mode prepares for self-chosen buy-in; audit-mode diagnoses
  why self-chosen buy-in failed to emerge. Both reject the framing
  "I have authority, I just want a softer-sounding script for the
  mandate" — that produces compliance, not commitment, and 4DX
  won't take root.
- **Voluntary opt-in pilot is sacred** — coach-mode plans it;
  audit-mode flags its absence. CE-36 (conscripting resisters into
  the first pilot wave) is a binary failure mode in both directions.
- **High-context-culture caveat** — the book's voluntary-opt-in
  pattern was developed in US-anglophone-corporate settings where
  direct disagreement is permissible. In JP / ZH / KR contexts,
  "neutral" responses often mask dissent; both modes should probe
  more carefully before classifying any leader as neutral, and
  prefer private 1:1 over public clarifying-question rounds.
- **The four onboarding rules are the canonical rule set** —
  commitment-vs-compliance / Kotter Stage-1 urgency / per-leader
  steel-manning / pilot-vs-hold-back. Coach-mode applies them
  forward (planning); audit-mode diagnoses them backward (from
  artifacts). The rule set is shared.

## Audit metadata

- **Skill type**: multi-file orchestrator (path B refactor — coach-mode
  + audit-mode protocols, shared rule set, no separate standards/
  directory; the rule set lives inline in coach-mode §E and §B)
- **Verification status**: V1 ✓ for coach-mode (forward-Socratic,
  Chapter-8 verbatim source); V1 ⚠️ partial for audit-mode (artifact-
  synthesis is symmetric inverse of coach-mode, anchored on Argyris
  HBR-1991 + Ryan-Deci SDT + Kotter Stage-1 with industry grounding
  in `references/industry-grounding.md`; secondary Kotter anchor
  inferred from "another corporate initiative" critique-mapping)
- **Created**: 2026-04-29 (single-file v0.1.0); refactored to multi-file + audit-mode 2026-04-30
- **Output language**: SKILL.md body + protocols in English; description
  + mode-detection prompts multilingual EN/JP/zh-TW; audit-mode critique-
  to-rule mapping table is multilingual
