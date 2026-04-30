---
name: 4dx-d3-scoreboard
description: |
  Multi-scope coach for D3 Compelling Scoreboard across the 3 roles
  the user can occupy. Detects scope (solo / team-leader-designer /
  team-member-reader) and loads the matching protocol. EN: "Help me
  design my scoreboard", "Design our team scoreboard", "How do I read
  my team's scoreboard?". JP:「自分用の scoreboard を設計したい」
  「チームの scoreboard を設計したい」「team の scoreboard をどう読む？」.
  zh-TW:「設計自己的計分板」「幫團隊設計 scoreboard」「我們 team 的
  scoreboard 怎麼看」. Players' scoreboard 5-second-test grammar shared;
  voice differs (personal coach / consultant-to-leader / personal coach
  to member). NOT for enterprise BI / KPI dashboards, agile burndown,
  OKR check-in dashboards, before D1/D2 are defined, or for cadence
  questions (→ 4dx-d4-cadence).
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: Chapter 4 — Discipline 3: Keep a Compelling Scoreboard; Chapter 14 — Applying Discipline 3
source_language: en
tags: [d3, scoreboard, multi-scope, players-scoreboard, visualization, engagement, 4dx, solo, team-leader, team-member]
related_skills:
  - 4dx-meta-strategy-triage
  - 4dx-d1-wig-formulation
  - 4dx-d2-lead-measures
  - 4dx-d4-cadence
  - 4dx-sustain-personal-momentum-rescue
  - 4dx-meta-team-leader-onboarding
  - using-four-dx-coach
---

# 4dx-d3-scoreboard — Compelling players' scoreboard across all roles (multi-scope)

## Mission

Coach the user through D3 — designing or reading a **compelling players'
scoreboard** — in whichever of three roles they occupy: designing their
own private scoreboard (solo); facilitating the team to build a public
team scoreboard (team-leader); or reading an inherited team scoreboard
to locate personal contribution and surface breakage (team-member).
Same players'-scoreboard grammar (≤4 elements, lead + lag with pacing
line, 5-second winning test); different voice per role; one shared
standard set for what counts as glance-readable, what distinguishes
players' from coaches', and what visual elements belong on the board.

## When this skill activates

### Multilingual trigger phrasings (covering all 3 modes)

**Solo (personal scoreboard, voice = personal coach):**
- EN: "Help me design my scoreboard", "I have a WIG + leads but my
  tracker is too complex", "How do I make my progress visible?",
  "Should I use a sticky note / whiteboard / app?"
- JP: 「自分用の scoreboard を設計したい」「ダッシュボードが複雑すぎて見ない」
  「進捗を可視化したい」「Notion で管理してるけど開かない」
- zh-TW: 「我做了一個追蹤表，可是都沒在看」「怎麼讓進度看得見？」
  「我的追蹤工具太複雜了」「設計自己的計分板」

**Team-leader (facilitate team-built public board, voice = consultant-to-leader):**
- EN: "Help me design our team scoreboard", "How should our team
  display the WIG and lead measures?", "Should I put this on a wall
  or in our team channel?", "My team has the goals but the dashboard
  isn't motivating anyone"
- JP: 「チームの scoreboard を設計したい」「チーム全員が見える進捗の出し方」
  「team の scoreboard を build するのを facilitate したい」
- zh-TW: 「幫團隊設計 scoreboard」「團隊計分板要怎麼設計？」
  「怎麼讓全隊都看得到進度？」

**Team-member (read inherited board, voice = personal coach to member):**
- EN: "How do I read my team's scoreboard?", "Our team has a
  scoreboard — what should I be looking at?", "Where do I show up on
  the team scoreboard?", "Our scoreboard hasn't moved in weeks — is
  that real?"
- JP: 「team の scoreboard をどう読む？」「scoreboard はあるけど自分の貢献が見えない」
  「scoreboard を見ても勝ってるのか分からない」「pacing line がおかしい気がする」
- zh-TW: 「我們 team 的 scoreboard 怎麼看」「scoreboard 跟我有什麼關係不知道」
  「我們的 scoreboard 看了也看不出在贏」「目標線好像跟現實對不上」

### Non-activation signals (DO NOT fire when…)

- **WIG / lead measures not yet set** → run D1 / D2 first; D3 has
  nothing to display. Route to `4dx-d1-wig-formulation` /
  `4dx-d2-lead-measures`.
- **Query is about cadence / WIG Session** → `4dx-d4-cadence`
- **Enterprise BI / KPI dashboards** (Tableau / Power BI / Looker
  enterprise, multi-team aggregated rollups, executive-review
  scorecards) → out of 4DX; hand off via `using-four-dx-coach`
- **Agile burndown / sprint velocity / Scrum charts** → wrong
  artifact (sprint scope completion, not lead-against-lag)
- **OKR check-in dashboards / BSC scorecards / status reports** →
  different purpose (strategic-alignment communication; analytic;
  drill-down)
- **User is mid-flow inside an active D3 protocol** — don't interrupt
- **Member sees broken board and wants to redesign it unilaterally**
  → fire member-read protocol (not redesign); the board is the
  leader's to fix; member surfaces with Model-II inquiry

## Scope detection

When this skill activates:

1. Determine **role**: solo (designer of own private board) /
   team-leader-facilitator (designer of team's public board) /
   team-member (reader of leader-designed board)
2. Determine **verb**: design (build new) vs read (interpret existing)
3. Load the matching protocol file from `protocols/`
4. Follow that protocol's E section step-by-step

If ambiguous after reading the user's query, ask ONE Socratic
question:

> EN: "Quick check — what's your role with respect to the scoreboard:
> **designing your own private one** (solo), **facilitating your
> team to build a public one** (leader), or **reading the one your
> team already has** (member)? I'll route to the right protocol."
>
> JP: 「scoreboard に対する role を確認 — **自分専用のものを design**（solo）、
> **team が public な scoreboard を build するのを facilitate**（leader）、
> **既に team が持っているものを read**（member）のどれ？適切な protocol に
> 振り分けます。」
>
> zh-TW: 「先確認 — 你跟 scoreboard 的關係：**設計自己用的**（solo）、
> **帶 team 一起 build 公用的**（leader）、**讀 team 已經有的**（member）？
> 我幫你導到對的 protocol。」

If the signal in the original query is strong, skip the question and
load the protocol directly.

## Protocol routing table

| Detected mode | Load protocol | Agent voice |
|---|---|---|
| Solo, design own private scoreboard | `protocols/personal-design.md` | personal coach |
| Team-leader, facilitate team-built public scoreboard | `protocols/team-lead-design.md` | consultant-to-leader |
| Team-member, read inherited team scoreboard | `protocols/member-read.md` (V1 ⚠️ partial) | personal coach to member |

After loading the protocol, follow its E section step-by-step. Each
protocol carries its own R / I / A1 / A2 / E / B sections; this
orchestrator does not run any design or reading content directly.

### Edge-case routing

- **Solo + already has a tracker that "doesn't work"** — fire
  `personal-design.md`; the redesign step diagnoses
  coach's-as-players' substitution and routes to a passive surface.
- **Team-leader + has board but team treats it as "management's"** —
  fire `team-lead-design.md`; the team-build session re-anchors
  ownership.
- **Member + sees a broken team board** — fire `member-read.md`; its
  step 6 has the Model-II escalation script. Do NOT fire
  `team-lead-design.md` for the member; they don't own the redesign.
- **WIG / lead measures not yet set** — fire D1 / D2 skills first;
  D3 has nothing to operate on without upstream artifacts.
- **Personal-vs-team scope ambiguous in solo professional context**
  ("I run a 1-person consultancy") — fire `personal-design.md`; the
  team-build dynamic doesn't apply when there's no peer team.

## Shared standards

Each protocol references these standards (load on demand):

- `standards/5-second-test.md` — the glance-readable rule (book Ch 4
  criterion 4); applies to design (passes / fails) and reading
  (member's diagnostic flag); grounded in Tufte data-ink + Few
  glance-monitoring + Ware pre-attentive processing
- `standards/players-vs-coaches-board.md` — book's primary
  distinction (player = engaged, coach = analytical); collapsing the
  two is the most common D3 failure mode across all three modes
- `standards/lead-lag-pacing-elements.md` — the ≤4 elements rule,
  what each element shows (lead trend, lag trend, pacing /
  where-you-should-be line, optional delta), and why pacing is the
  motion-vs-static visual distinguishing scoreboard from progress bar

## Cross-skill relations

- **Upstream (D1 / D2 prerequisites)** — `4dx-d1-wig-formulation`
  defines the lag the scoreboard displays; `4dx-d2-lead-measures`
  defines the leads; without both, this skill has nothing to render.
  Halt and route upstream.
- **Compose-with downstream** — `4dx-d4-cadence` segment 2 (Review)
  reads the artifact this skill produces; the scoreboard is the
  artifact, the WIG Session is the cadence. They compose, not
  compete.
- **Compose-with rescue** — `4dx-sustain-personal-momentum-rescue`
  routes back here when the diagnosis is "scoreboard hidden" or
  "scoreboard is a coach's view only".
- **Compose-with team-context** — `4dx-meta-team-leader-onboarding`
  is upstream of the leader running team-build; the scoreboard is
  one of the four artifacts a leader installs.
- **Plugin-router fallback** — `using-four-dx-coach` handles
  cold-start triage and out-of-4DX queries (BI dashboards, OKR
  scorecards, agile burndown, status reports).

## Boundary (cross-mode common)

The mode-specific boundary lives in each protocol's B section. The
cross-mode common boundary:

- **A players' scoreboard is a specific artifact**, not a generic
  "tracking display". Four characteristics — simple / visible / shows
  lead AND lag with pacing / 5-second winning test — apply across
  all three modes. Don't let the request collapse the artifact into
  a coach's BI dashboard.
- **The 5-second test is the single sharpest gate** across all three
  modes. Solo: design must pass it for the user. Team-leader: design
  must pass for any teammate or stranger glancing past. Member: if
  the existing board fails it, that is a signal to surface, not a
  member competence gap.
- **Manual update by the player(s) is the engagement loop** — across
  all three modes, a board updated only by automation collapses the
  ownership mechanism. Solo: user updates by hand. Team-leader: team
  updates, not leader, not auto-feed. Member: notices when the board
  has gone stale and surfaces.
- **Pacing / where-you-should-be line is mandatory** — across all
  three modes, status without trajectory is data, not a scoreboard.
  Bare progress bar without target marker, fitness ring without
  weekly goal, habit grid without pacing line — all fail D3 by the
  same mechanism.
- **High-context-culture caveat** — book's strongest exemplars
  (juice-bottling shifts, hotel front desk) are co-located industrial
  settings with peer-visible scoreboards; for JP / ZH / KR knowledge
  teams or for users for whom "winning" framing repels, soften
  person-vs-person comparison to team-vs-target / progress-visible-
  to-me — the visualization mechanism is identical, the affective
  frame differs.

## Audit metadata

- **Skill type**: multi-file orchestrator (merged from 3 atomic D3
  skills + 1 topic-router; pattern matches `4dx-d4-cadence`)
- **Verification status**: V1 ✓ for personal-design + team-lead-design
  (both leader-POV in source book); V1 ⚠️ partial for member-read
  (book authors leader side of design rubric only; member-read
  protocol = symmetric inversion of the four design criteria + two
  member-only steps for locate-my-contribution and escalate-if-broken,
  anchored on Tufte / Few / Ware perception literature, Eurich 95/15
  self-awareness gap, and Argyris Model-II inquiry)
- **Created**: 2026-04-30
- **Output language**: SKILL.md body + protocols/standards in English;
  description + scope-detection prompts multilingual EN/JP/zh-TW;
  member-read protocol's escalation script is multilingual
