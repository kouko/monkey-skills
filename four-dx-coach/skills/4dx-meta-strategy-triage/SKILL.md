---
name: 4dx-meta-strategy-triage
description: |
  Multi-scope gate for "Should X use 4DX?" — decides whether 4 Disciplines of
  Execution even fits the user's situation BEFORE installing D1-D4. Detects
  scope (solo individual / team-leader) and loads the matching triage
  protocol. EN: "Should I use 4DX for X?", "Will 4DX work for my goal?",
  "Should our team adopt 4DX?", "Is 4DX right for a team of N?". JP:
  「この目標に 4DX 使える？」「私たちのチームに 4DX 合うか？」「4DX 合ってる？」.
  zh-TW: 「4DX 適合我這個目標嗎？」「我們團隊適合導入 4DX 嗎？」「4DX 適合嗎？」.
  Returns one of 6 verdicts per mode (solo: APPLICABLE / habit / portfolio /
  emergency / creative / no-time-sovereignty; team-leader: TEAM-APPLICABLE /
  stroke-of-pen / whirlwind-handleable / wrong-team-shape / single-shot-project
  / mission-misaligned, with TEAM-NOT-YET-READY variant for change-readiness
  failures). Stroke-of-pen vs behavioral-change distinction shared.
  NOT for already-committed users asking "how do I start?" (route to D1).
  NOT for team members inheriting a WIG (route to
  4dx-d1-wig-formulation — members don't triage methodology
  fit). NOT for enterprise multi-team rollout (read book Ch 6-10 directly +
  4dx-d1-team-wig-cascade).
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: Chapter 1 (The Real Problem With Execution) + Chapter 6 (Choosing Where to Focus)
source_language: en
tags: [decision-gate, scope-triage, methodology-fit, 4dx, meta-gate, pre-d1, multi-scope, solo, team-leader]
related_skills:
  - 4dx-d1-personal-whirlwind-triage
  - 4dx-d1-wig-formulation
  - 4dx-d1-wig-formulation
  - 4dx-d1-team-wig-cascade
  - 4dx-d1-wig-formulation
  - 4dx-meta-team-leader-onboarding
  - 4dx-sustain-personal-momentum-rescue
  - using-four-dx-coach
---

# 4dx-meta-strategy-triage — Should you (or your team) use 4DX at all?

## Mission

Decide whether 4DX even applies BEFORE installing the four disciplines. The
book's stroke-of-the-pen / whirlwind / behavioral-change taxonomy is the core
test, layered with personal-scale anti-patterns (solo mode) and team-shape +
change-readiness gates (team-leader mode). Refusing 4DX when it doesn't fit
is the skill's job — not bending the goal back into 4DX shape. Same triage
logic across modes; voice and gates differ per scope.

## When this skill activates

### Multilingual trigger phrasings (covering both modes)

**Solo (personal, agent = personal coach):**
- EN: "Should I use 4DX for [X]?", "Is 4DX right for my goal?", "Will 4DX help me lose weight / write a novel / handle on-call?", "Does 4DX apply to a personal goal?"
- JP: 「この目標に 4DX 使える？」「4DX は〜に向いてる？」「4DX 適用できますか」「4DX 自分に合ってるか分からない」
- zh-TW: 「4DX 適合我這個目標嗎？」「我這個目標可以用 4DX 嗎？」「4DX 對個人目標有用嗎？」「不確定 4DX 是不是適合我」

**Team-leader (agent = consultant):**
- EN: "Should our team adopt 4DX?", "Will 4DX work for my team?", "Is 4DX right for a team of N?", "Should I roll out 4DX to my direct reports?", "Is my team ready for 4DX?"
- JP: 「私たちのチームに 4DX 合うか？」「うちのチームで 4DX 効くかな」「チームに 4DX 導入すべき？」「うちの規模で 4DX は合う？」
- zh-TW: 「我們團隊適合導入 4DX 嗎？」「團隊要不要用 4DX？」「我這個團隊用 4DX 有用嗎？」「我該不該對下屬團隊推 4DX？」

**Ambiguous-scope fallback** — query lacks explicit actor:
- EN: "Is 4DX a good fit?", "Should we use 4DX?", "Is 4DX overkill?"
- JP: 「4DX 適してる？」「4DX 合ってる？」「4DX で大丈夫？」
- zh-TW: 「4DX 適合嗎？」「4DX 會不會太重？」

### Non-activation signals (DO NOT fire when…)

- User has already committed to 4DX and asks *"how do I start?"* / *"where do I begin?"* — route to `4dx-d1-personal-whirlwind-triage` (solo) or `4dx-d1-wig-formulation` (team).
- User asks about a specific discipline (lead measures, scoreboard, WIG session mechanics) — route to the matching D-skill.
- User is a team-member who **inherits** a WIG already chosen by a leader — members don't triage methodology fit; route to `4dx-d1-wig-formulation`.
- User runs a multi-team enterprise rollout (cascading WIGs across many teams) — read book chapters 6-10 directly + `4dx-d1-team-wig-cascade`.
- User asks about non-4DX methodologies (OKR / agile / habit-stacking / scrum / kanban) — hand off via `using-four-dx-coach`.
- User is in the middle of an active triage session — do not re-route mid-flow.

## Scope detection

When this skill activates:

1. Determine **scope**: solo (one person, one goal) vs team-leader (3-12 person team, leader judging team adoption).
2. Load the matching protocol file from `protocols/`.
3. Follow that protocol's E section step-by-step.

If ambiguous after reading the user's query, ask ONE Socratic disambiguation question:

> EN: "Quick clarification — are you thinking about this for **yourself as an individual** (one person, one goal), or for **a team you lead** (3-12 reports adopting 4DX together)? I'll route to the right triage."
>
> JP: 「先に確認 —— **自分一人の目標**（一人、一つのゴール）として 4DX を検討中ですか？それとも **率いる team**（3-12 人の直属メンバー）として？適切な triage に振り分けます。」
>
> zh-TW: 「先確認一下 —— 你是想用 4DX 解決 **個人一個目標**（一人、一目標），還是 **你帶的團隊**（3-12 人直屬）導入？我幫你導到對的 triage。」

If the signal in the original query is strong (first-person singular alone → solo; first-person plural + team / department → team), skip the question and load the protocol directly.

### Member edge case (NO protocol — route out)

If user identifies as a **member** receiving an inherited WIG ("my manager already picked the WIG" / 「上司が WIG を決めた」 / 「老闆已經訂好 WIG」), triage is moot. Members inherit; they don't assess methodology fit. Route directly to `4dx-d1-wig-formulation` — there is no "member-mode" protocol in this skill by design. Member scope is **intentionally absent** from V1; member-side concerns belong to comprehension and prep skills, not the methodology-fit gate.

## Protocol routing table

| Detected mode | Load protocol | Agent voice |
|---|---|---|
| Solo individual | `protocols/personal-mode.md` | personal coach |
| Team-leader (3-12 reports) | `protocols/team-mode.md` | consultant to leader |

After loading the protocol, follow its E section step-by-step. Each protocol carries its own R / I / A1 / A2 / E / B sections; this orchestrator does not run any triage content directly.

## Shared standards

Each protocol references these standards (load on demand):

- `standards/6-verdict-rubric.md` — the 6-verdict triage taxonomy shared across both modes (with mode-specific labels: APPLICABLE vs TEAM-APPLICABLE; habit / portfolio / emergency / creative / no-time-sovereignty for solo; stroke-of-pen / whirlwind-handleable / wrong-team-shape / single-shot-project / mission-misaligned for team)
- `standards/stroke-of-pen-vs-behavior-change.md` — the Ch 1 distinction that gates the entire triage; goals that authority alone solves don't need 4DX
- `standards/readiness-preconditions.md` — Kotter urgency, Galbraith STAR alignment, Schein culture-fit, Heath Path; team-mode-primary but referenced from personal-mode for the time-sovereignty check

## Cross-skill relations

- **Downstream after APPLICABLE** — `4dx-d1-personal-whirlwind-triage` (solo) or `4dx-d1-wig-formulation` (team) is the next gate; `4dx-d1-wig-formulation` follows for WIG drafting.
- **Compose-with team-context** — `4dx-meta-team-leader-onboarding` follows TEAM-APPLICABLE to get leaders bought in; `4dx-d1-team-wig-cascade` translates an upper-level WIG down through sub-teams (out of scope for this skill).
- **Rescue back-loop** — `4dx-sustain-personal-momentum-rescue` runs after a stalled WIG and may route back here if the original triage was wrong-shaped.
- **Plugin-router fallback** — `using-four-dx-coach` handles cold-start and out-of-4DX queries (OKR, agile, habit stacking); not a substitute for this skill, but the right hand-off when the user's question turns out not to be 4DX-fit triage at all.

## Boundary (cross-mode common)

The mode-specific boundary lives in each protocol's B section. The cross-mode common boundary:

- **Triage is the gate, not the install** — this skill issues a verdict and routes; it does NOT define a WIG, pick lead measures, or run a session. The instant a verdict is issued, control hands off to D1 (if APPLICABLE) or to the alternative methodology (if redirected).
- **6 verdicts only — no "kind of fits"** — the rubric is discrete. Refusing to issue a clean verdict because "it's complicated" is the documented failure mode (4DX gets installed by default → wastes attention budget). When in doubt, the default is NOT-APPLICABLE; the user can always re-triage later if conditions change.
- **The matched-set rule (P-23) is non-negotiable across both modes** — 4DX is all four disciplines or none. If the user wants to cherry-pick (e.g. "just D1 + D4"), the verdict is automatically NOT-APPLICABLE — recommend a lighter framework instead. This rule applies the same in solo and team mode.
- **Stroke-of-the-pen check is the strongest filter** — both modes ask first: is there a single decision (purchase, hire, rule change, contract) that delivers the goal? If yes, 4DX is overkill regardless of all other gates. The book's strongest scope warning (CE-06).
- **Refusal is a feature** — across both modes, returning a non-APPLICABLE verdict is the correct outcome ~50% of the time. The skill's value is *not* greenlighting 4DX; it's protecting the user from misapplication.

## Audit metadata

- **Skill type**: multi-file orchestrator (merged from 3 source skills — 2 atomic triage + 1 topic-router)
- **Verification status**: V1 ✓ for both solo + team-leader modes (both grounded directly in book Ch 1 + Ch 6); V1 ⚠️ N/A for member scope — intentionally out of V1 by design (members inherit WIG, do not triage methodology fit)
- **Created**: 2026-04-30
- **Output language**: SKILL.md body + protocols/standards in English; description + scope-detection prompts multilingual EN/JP/zh-TW
