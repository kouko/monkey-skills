---
name: using-four-dx-coach
description: |
  Router for 4DX coaching — routes vague or scope-ambiguous 4-Disciplines-of-Execution queries to the right sub-skill (personal / team-leader / member). Use on '4DX where do I begin?', 'stuck on my goal', or '4DX 不知道從哪開始'.
source_book: The 4 Disciplines of Execution — McChesney, Covey, Huling, Thele, Walker (2nd ed., 2021)
source_language: en
tags: [router, entry-point, dispatcher, 4dx, scope-triage, personal, team-leader, team-member, multi-file]
related_skills:
  - 4dx-audit
  - 4dx-meta-strategy-triage
  - 4dx-d1-wig-formulation
  - 4dx-d2-lead-measures
  - 4dx-d3-scoreboard
  - 4dx-d4-cadence
  - 4dx-meta-whirlwind-triage
  - 4dx-d1-wig-cascade
  - 4dx-meta-team-leader-onboarding
  - 4dx-meta-xps-evaluation
  - 4dx-sustain-momentum-rescue
---

# using-four-dx-coach — 4DX Router (entry point)

## Mission

Route generic / vague / scope-ambiguous 4DX queries to the correct topical
skill. Triage first by **scope** (personal / team-leader / team-member),
then by **4DX stage**. If 4DX is the wrong methodology for the user's
problem, decline and redirect — do not bend the problem onto the wrong
shape.

> "The 4 Disciplines are a matched set, not a menu of choices."
> — McChesney et al., *Chapter 1*

This router is the entry door. Each topical skill behind it owns its own
gate logic; the router only decides *which door to open*. The 5 multi-file
skills self-route internally to the correct protocol via a one-question
Socratic check, so this router does **not** need to disambiguate scope
when handing off to a multi-file skill — just pass the query through.

---

## Pre-routing check — coach mode vs audit mode (v0.8.0 dual-mode)

Before scope triage, check whether the user has provided **artifacts** (a strategy doc, OKR sheet, KPI dashboard, scoreboard image / description, past WIG-Session notes, chat history of attempts). v0.8.0 dual-mode architecture means every topic skill ships its own `audit-mode.md`, so artifact-aware routing is now layer-specific:

- **Coach mode (default)** — user has a vague intent or fragment ("I want to start using 4DX", "should I use 4DX?", "WIG 怎麼寫"). Run scope triage below and dispatch to a topic skill's coach-mode protocol.
- **Single-layer audit mode (topic skill's `audit-mode.md`)** — user pastes / attaches / describes ONE artifact at ONE layer + asks for diagnosis / synthesis. Route to that topic skill's audit-mode directly:
  - WIG only ("here's our WIG, diagnose it") → `4dx-d1-wig-formulation` audit-mode
  - Lead-measure list only → `4dx-d2-lead-measures` audit-mode
  - Scoreboard / dashboard only → `4dx-d3-scoreboard` audit-mode
  - WIG-Session log / cadence only → `4dx-d4-cadence` audit-mode
  - Cascade tree only → `4dx-d1-wig-cascade` audit-mode
  - Strategy-fit memo only → `4dx-meta-strategy-triage` audit-mode
  - 7-day time log / capacity only → `4dx-meta-whirlwind-triage` audit-mode
  - Leader-onboarding artifacts only → `4dx-meta-team-leader-onboarding` audit-mode
- **Cross-layer aggregator (`4dx-audit`)** — user provides artifacts spanning **≥2 D-layers** OR cannot name which layer is broken. Examples: "strategy doc + OKR + dashboard + meeting notes — audit our 4DX" / "I don't know which layer is broken — look at the whole picture" / 「資料跨好幾層幫整理現況」. The aggregator maps multi-artifact context to all 5 layers, diagnoses per-layer status, surfaces cross-layer sequencing gaps, and routes back into specific topic-skill audit-mode or coach-mode for deep work.

Decision rule: count distinct D-layers represented in the artifacts. **0 layers** (no artifact) → coach mode. **1 layer** → that topic skill's audit-mode. **≥2 layers OR layer unknown** → `4dx-audit` cross-layer aggregator.

The router, single-layer audit-mode, and cross-layer aggregator are **complementary entry points**: router handles cold-start dialogue, single-layer audit-mode handles depth at one layer, cross-layer aggregator handles breadth across layers. None replaces the topic skills' coach-mode; all three route into them.

---

## The 11 topical skills indexed by scope and stage

### Cross-layer aggregator (1 — sibling, not dispatched-into by this router)

| Skill slug | Role | Activation signals |
|---|---|---|
| `4dx-audit` | Cross-layer aggregator | Multi-artifact spanning ≥2 D-layers OR layer-unknown failures. "Strategy doc + OKR + dashboard + meeting notes — audit 4DX across the board" / "WIG + leads + scoreboard but cadence broken — diagnose across layers" / "I don't know which layer is broken" / 「複数文書から 4DX 現状整理」 / 「資料跨好幾層幫整理現況」. **Single-layer audits go to that topic skill's audit-mode instead** (see audit-mode dispatch table below). |

When pre-routing detects ≥2-layer artifacts OR layer-unknown intent, hand off to `4dx-audit` directly. When pre-routing detects single-layer artifact, hand off to that topic skill's `audit-mode.md` directly. Do not run the scope-triage decision tree below in either case.

### Multi-file scope-flex topic skills (5 — auto-detect scope internally; dual-mode)

Each multi-file skill carries one `SKILL.md` orchestrator + scope-variant protocol files (coach-mode) + a single `audit-mode.md` (audit-mode). The orchestrator runs an internal Socratic check to pick the right scope+mode protocol; this router only needs to dispatch the topic.

| Skill slug | Stage | Coach-mode protocols | Audit-mode | Canonical activation signals |
|---|---|---|---|---|
| `4dx-meta-strategy-triage` | Pre-D1 fit gate | `personal-mode`, `team-mode` | `audit-mode` | Coach: "Should X use 4DX?" / "Is 4DX a good fit?". Audit: "Here's our fit-memo, diagnose 4DX applicability" |
| `4dx-d1-wig-formulation` | D1 | `personal-define`, `team-select`, `member-comprehend` | `audit-mode` | Coach: "Help me write a WIG", "Pick our Primary WIG", "Decode the team's WIG". Audit: "Here's our WIG only — diagnose against From-X-to-Y-by-When grammar" |
| `4dx-d2-lead-measures` | D2 | `personal-discover`, `team-facilitate`, `member-influence` | `audit-mode` | Coach: "What's the daily action", "Help my team find leads". Audit: "Here's our 12 lead measures — apply two-axis test" |
| `4dx-d3-scoreboard` | D3 | `personal-design`, `team-lead-design`, `member-read` | `audit-mode` | Coach: "Design a scoreboard". Audit: "Here's our dashboard — apply 5-second test" |
| `4dx-d4-cadence` | D4 | `solo-session`, `team-leader-session`, `member-prep`, `member-debrief` | `audit-mode` | Coach: "Weekly review", "Run our team session", "Prep for tomorrow's WIG Session". Audit: "Here's 4 weeks of WIG-Session log — diagnose Account → Review → Plan grammar" |

### Single-file scope-specific topic skills (5 — scope locked by topic; dual-mode where applicable)

The book has no cross-scope variant for these topics. v0.8.0 added dual-mode (coach + audit protocols) to the three topics where artifact-rich starts are common; xps-evaluation and sustain-momentum-rescue are inherently audit-shaped (the skill itself IS the audit / diagnostic — no separate audit-mode protocol needed).

| Skill slug | Scope | Stage | Coach-mode | Audit-mode | Canonical activation signals |
|---|---|---|---|---|---|
| `4dx-meta-whirlwind-triage` | Personal | D1 prereq | `coach-mode` | `audit-mode` | Coach: "I'm always firefighting / no time for the goal" / 「日常業務に追われて目標に手がつかない」. Audit: "Here's my 7-day time log — diagnose capacity" |
| `4dx-d1-wig-cascade` | Team-leader | D1 (cascade) | `coach-mode` | `audit-mode` | Coach: "Cascade the org WIG to sub-teams". Audit: "Here's our cascade tree — diagnose Targets-not-Plans alignment" |
| `4dx-meta-team-leader-onboarding` | Team-leader | Leader prep | `coach-mode` | `audit-mode` | Coach: "I'm about to lead a 4DX team". Audit: "Here's my onboarding artifacts — diagnose buy-in (commitment vs compliance)" |
| `4dx-meta-xps-evaluation` | Team-leader | XPS audit | (audit-shaped) | (intrinsic) | "Is our team's 4DX execution actually working?" / "Post-quarter audit" |
| `4dx-sustain-momentum-rescue` | Personal | Recovery | (diagnostic) | (intrinsic) | "Haven't done my 4DX in weeks / lost momentum" |

---

## Routing logic — Socratic decision tree

### Step 1 — Detect scope

Read the query for scope signals. If unambiguous, proceed to Step 3. If
ambiguous, go to Step 2.

| Signal class | Example phrasings | Scope |
|---|---|---|
| First-person individual goal | "I want to", "my goal is", "I personally", "my own [X]" | **Personal** |
| Positional authority on goal-setting | "my team", "our team's WIG", "I lead", "help my team", "my direct reports", "as a manager" | **Team-leader** |
| Joined a team that already uses 4DX | "I joined", "given a WIG", "manager set", "for my team's WIG Session", "missed my commitment" | **Team-member** |
| No scope marker — vague | "I want to start using 4DX", "explain 4DX", 「4DX を使い始めたい」 | **Ambiguous → Step 2** |

### Step 2 — Ask scope explicitly (only when ambiguous and no clear topic)

> "Before I route you to the right tool — are you applying 4DX to:
> (a) **a personal / solo goal** (you set it, you execute it),
> (b) **a team you lead** (you have authority to set the team's WIG),
> or (c) **a team you've joined** (someone else set the WIG, you execute
> within it)?"

Wait for the answer; do not guess.

### Step 2.5 — If topic is clear, defer to the matching multi-file skill (let IT do scope detection)

If the user's **topic is already clear** (meta / D1 WIG / D2 leads / D3
scoreboard / D4 cadence) but role is ambiguous, **defer the scope question
to the multi-file skill**. Each one runs its own one-question Socratic
disambiguation and loads the right internal protocol. This router does
not need to ask the same question twice.

| Topic signal in query | Defer to multi-file skill |
|---|---|
| "Should X use 4DX?" / "Is 4DX a good fit?" | `4dx-meta-strategy-triage` |
| "Help me with my WIG" / "How do I set a WIG?" | `4dx-d1-wig-formulation` |
| "Help me with lead measures" / "How do I find lead measures?" | `4dx-d2-lead-measures` |
| "Help me with the scoreboard" / "How should I track this?" | `4dx-d3-scoreboard` |
| "Help with my WIG Session" / "weekly cadence" | `4dx-d4-cadence` |

### Step 3 — Route within scope by 4DX stage

#### Personal scope routing

1. Fit unsure → `4dx-meta-strategy-triage` (loads `personal-mode`)
2. No time / always firefighting → `4dx-meta-whirlwind-triage`
3. Goal vague / multi-priority → `4dx-d1-wig-formulation` (loads `personal-define`)
4. WIG set, daily action unclear → `4dx-d2-lead-measures` (loads `personal-discover`)
5. Tracker noisy / unread → `4dx-d3-scoreboard` (loads `personal-design`)
6. Need weekly cadence → `4dx-d4-cadence` (loads `solo-session`)
7. Lapsed practice → `4dx-sustain-momentum-rescue`

#### Team-leader scope routing

1. Fit unsure (team) → `4dx-meta-strategy-triage` (loads `team-mode`)
2. About to lead → `4dx-meta-team-leader-onboarding`
3. Need a single org-level WIG → `4dx-d1-wig-formulation` (loads `team-select`)
4. Need to cascade Primary WIG to sub-teams → `4dx-d1-wig-cascade`
5. Need to facilitate team picking lead measures → `4dx-d2-lead-measures` (loads `team-facilitate`)
6. Need to facilitate team building scoreboard → `4dx-d3-scoreboard` (loads `team-lead-design`)
7. Need to run weekly team session → `4dx-d4-cadence` (loads `team-leader-session`)
8. Auditing whether 4DX is actually working → `4dx-meta-xps-evaluation`

#### Team-member scope routing

1. New to the team's WIG, decoding it → `4dx-d1-wig-formulation` (loads `member-comprehend`)
2. Team leads set, mapping personal influence → `4dx-d2-lead-measures` (loads `member-influence`)
3. Reading the team scoreboard → `4dx-d3-scoreboard` (loads `member-read`)
4. Prepping next session's commitment → `4dx-d4-cadence` (loads `member-prep`)
5. Missed a commitment / debrief needed → `4dx-d4-cadence` (loads `member-debrief`)

### Step 4 — If 4DX is wrong shape

Skip routing; use the hand-off scripts below.

---

## Recommended progression by scope

### Personal — solo first-time user

```
meta-strategy-triage (personal-mode)
  → d1-personal-whirlwind-triage
  → d1-wig-formulation (personal-define)
  → d2-lead-measures (personal-discover)
  → d3-scoreboard (personal-design)
  → d4-cadence (solo-session)
  → sustain-personal-momentum-rescue (on demand)
```

Sequential — 4DX is "a matched set, not a menu" (P-23). If the user wants
to cherry-pick (e.g. just D4 weekly reviews without a WIG), the
meta-strategy-triage skill will flag the mismatch.

### Team-leader — first-time team rollout

```
meta-strategy-triage (team-mode)
  → meta-team-leader-onboarding
  → d1-wig-formulation (team-select) OR d1-team-wig-cascade depending on altitude
  → d4-cadence (team-leader-session) — start weekly cadence
  → meta-team-xps-evaluation — after 4-8 weeks of cadence
```

Cascade vs Primary depends on the leader's altitude: top of the org →
Primary WIG; mid-leader inheriting one → Cascade.

### Team-member — joined a 4DX team mid-flight

```
d1-wig-formulation (member-comprehend) — one-time onboarding
  → d4-cadence (member-prep) — each session, before
  → d4-cadence (member-debrief) — each session, after
  → loop weekly
```

Members have no D2/D3 ownership — those belong to the leader. Members
own commitment prep and honest accounting; their D2/D3 protocols
(`member-influence`, `member-read`) are read-only diagnostics that
escalate to the leader if the inherited leads / scoreboard look broken.

---

## Hand-off scripts (non-applicable queries)

When the user's request doesn't fit 4DX, decline cleanly and route to the
right neighborhood. Do not bend the problem.

### Enterprise / 50+ team rollout

> "The four-dx-coach plugin scopes to **personal coaching, single-team
> leadership, and individual team-member execution**. For full enterprise
> rollout — Leader-of-Leaders cadence design across 50+ teams,
> organization-wide XPS reporting, change-management — the principles
> are the same but the operations layer requires consulting. Refer to
> *The 4 Disciplines of Execution* Part 2 (Chapters 6-10) and
> FranklinCovey consulting. The team-leader skills here cover up to a
> single intact team or a leader cascading to ≤5 sub-teams."

### Habit formation (no breakthrough lag)

> "4DX is overkill for habit formation. Goals like 'meditate 5 min daily'
> or 'floss every night' are recurring behaviors, not From-X-to-Y-by-When
> finish lines. James Clear's *Atomic Habits* (habit stacking,
> identity-based habits, 2-minute rule) is the better fit. If the habit
> is *in service of* a 4DX-shaped WIG (e.g. daily writing → finish novel
> by Dec 31), come back via `4dx-d2-lead-measures`."

### OKR / portfolio betting / lean experimentation

> "4DX assumes the WIG is already correct and worth a 6-12 month
> commitment. If you're running multiple bets and don't yet know which
> will pay off — multi-startup founder, R&D explorer, PM pre-PMF — OKR
> or lean-startup is the better fit (both have built-in kill criteria;
> 4DX has none). Use OKRs to *find* the right WIG; once one is validated,
> 4DX to *execute* on it."

### Agile / scrum / kanban / sprint planning

> "Those are software-delivery cadence frameworks — different problem
> shape. 4DX is about behavioral-change strategic goals against a
> day-job whirlwind, not iterative product delivery. Sprint planning,
> retros, story points, backlog grooming — this plugin doesn't apply."

### Burnout / clinical mental-health

> "Time audits and goal-setting weaponize awareness without solving
> exhaustion. If you're describing sustained overwhelm, depression, or
> burnout, 4DX is not the right intervention — rest, coaching, or
> clinical support is. The four-dx-coach skills will not help here and
> may make it worse."

---

## Boundary — explicit non-activation signals

Do not activate this router on:

- **User names a specific skill or discipline** — e.g. "How do I write a
  WIG?" → `4dx-d1-wig-formulation` directly. "Help my team pick a
  Primary WIG" → `4dx-d1-wig-formulation` directly. "I missed
  my commitment last week" → `4dx-d4-cadence` directly.
- **User has full D1+D2+D3+D4 already running and asks a specific
  question** — route to the matching topical skill, skip the router.
- **Software / engineering process queries** — agile, scrum, kanban,
  sprint planning, story pointing, velocity, CI/CD cadence.
- **Pure productivity-tool shopping** — "Notion vs Sunsama vs Things",
  "best habit tracker" — tool selection, not strategy execution.
- **Mood / motivation / mental-health queries** — burnout, depression,
  ADHD coaching, exhaustion.
- **One-off projects** — "file my taxes this weekend", "book a flight"
  — stroke-of-pen, no behavioral-change at stake.
- **Generic decision queries with no 4DX vocabulary** — let other
  decision skills (e.g. philosophers-toolkit) handle.

---

## Division of labour

- **This plugin router** (`using-four-dx-coach`) fires on **cold-start**,
  **out-of-4DX**, and **cross-topic** queries — the user is at the front
  door, hasn't named a discipline, or is asking whether 4DX even applies
  to a domain we should hand off elsewhere.
- **Multi-file scope-flex skills** fire when the topic is clear; they
  internally pick the right protocol via one Socratic question.
- **Single-file scope-specific skills** fire when both topic and scope
  are constrained by the signal (e.g. cascade → team-leader only;
  whirlwind triage → personal only).

When a query already has a clear topic, defer to the matching multi-file
skill rather than asking the scope question yourself. See Step 2.5 above
for the deferral table.

---

## Audit metadata

- **Skill type**: router (`using-*` convention)
- **Verification**: router skill — no triple verification needed (each
  topical skill it dispatches to owns its own V1/V2/V3 audit).
- **Distilled at**: 2026-04-29 (v0.2 — scope-triage upgrade) /
  2026-04-30 (v0.3 — D2/D3 expansion: 20 atomic + 5 topic-routers + 1 plugin
  router = 26 total) /
  2026-04-30 (v0.6 — Plan U merge: 20 atomic + 5 topic-routers consolidated
  into 5 multi-file scope-flex skills + 5 single-file scope-specific skills
  + 1 plugin router = 11 total) /
  2026-04-30 (v0.7 — consultant-mode `4dx-audit` added as sibling entry
  point: 11 → 12 total. Pre-routing check added to detect artifact-rich
  starts and hand off to audit instead of running scope triage.) /
  2026-04-30 (v0.8 — dual-mode topic skills introduced (every topic ships
  `coach-mode.md` + `audit-mode.md`); `4dx-audit` repositioned to cross-layer
  aggregator only. Pre-routing check now layer-aware: 0 layers → coach;
  1 layer → topic-skill audit-mode; ≥2 layers OR layer-unknown → 4dx-audit
  cross-layer aggregator.)
- **Output language**: description multilingual (EN + JP + zh-TW); body
  English; A2 trigger phrasings multilingual; metadata English.
- **Source basis**: BOOK_OVERVIEW.md + 10 topical skill SKILL.md
  frontmatter (A2 triggers + execution outputs).
