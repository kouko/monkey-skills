---
name: using-four-dx-coach
description: |
  Router for the four-dx-coach plugin. Activates on generic / vague 4DX
  queries OR when the user's scope is unclear OR on **short scope-less
  fragment queries** that mention 4DX vocabulary without specifying
  scope (e.g. 「目標卡住」 / 「scoreboard 看不懂」 / 「WIG 不會訂」
  / "stuck on my goal" / "4DX where to start"). Triages by scope first
  — personal (solo) / team-leader / team-member — then by 4DX stage,
  and dispatches across 10 topical skills (5 multi-file scope-flex +
  5 single-file scope-specific). Multi-file skills self-route to their
  internal protocol; this router only picks the right door. EN: "I
  want to start using 4DX", "help my team apply 4 Disciplines", "where
  do I begin with 4DX?", "I joined a team using 4DX", "4DX 不知道從何
  開始". JP: 「4DX を使い始めたい」「4 つの規律をチームに導入したい」
  「4DX の始め方」「4DX のチームに入った」「4DX どこから始めれば」.
  zh-TW: 「想要開始用 4DX」「4 個執行紀律怎麼開始」「想用 4DX 帶
  團隊」「我加入了一個用 4DX 的團隊」「4DX 不知道從哪裡開始」. 5
  multi-file scope-flex skills: 4dx-meta-strategy-triage /
  4dx-d1-wig-formulation / 4dx-d2-lead-measures / 4dx-d3-scoreboard /
  4dx-d4-cadence (each bundles 2-4 internal protocols covering
  personal / team-leader / team-member variants). 5 single-file
  scope-specific skills: 4dx-meta-whirlwind-triage (personal,
  pre-D1), 4dx-d1-wig-cascade (team-leader, leader-of-leaders only),
  4dx-meta-team-leader-onboarding (team-leader),
  4dx-meta-xps-evaluation (team-leader), 4dx-sustain-momentum-rescue
  (personal, recovery only). Hands off when 4DX doesn't fit —
  habit-stacking / OKR KRs / agile sprint / burnout / clinical mental
  health. **Fallback rule**: when a query is too short or vague to
  unambiguously identify a single skill, prefer this router over a
  guess. Do NOT activate when the user names a specific skill or has
  a full WIG+leads+scoreboard+cadence running with a
  discipline-specific question.
source_book: The 4 Disciplines of Execution — McChesney, Covey, Huling, Thele, Walker (2nd ed., 2021)
source_language: en
tags: [router, entry-point, dispatcher, 4dx, scope-triage, personal, team-leader, team-member, multi-file]
related_skills:
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

## The 10 topical skills indexed by scope and stage

### Multi-file scope-flex skills (5 — auto-detect scope internally)

Each multi-file skill carries one `SKILL.md` orchestrator + 2-4 protocol
files. The orchestrator runs an internal Socratic check to pick the right
protocol; this router only needs to dispatch the topic.

| Skill slug | Stage | Protocols inside | Canonical activation signals |
|---|---|---|---|
| `4dx-meta-strategy-triage` | Pre-D1 fit gate | `personal-mode`, `team-mode` | "Should X use 4DX?" / "Is 4DX a good fit?" / 「4DX 適してる？」 |
| `4dx-d1-wig-formulation` | D1 | `personal-define`, `team-select`, `member-comprehend` | "Help me write a WIG", "Pick our Primary WIG", "Decode the team's WIG" |
| `4dx-d2-lead-measures` | D2 | `personal-discover`, `team-facilitate`, `member-influence` | "What's the daily action", "Help my team find leads", "How do I influence inherited leads" |
| `4dx-d3-scoreboard` | D3 | `personal-design`, `team-lead-design`, `member-read` | "Design a scoreboard", "Build the team scoreboard", "Read our team scoreboard" |
| `4dx-d4-cadence` | D4 | `solo-session`, `team-leader-session`, `member-prep`, `member-debrief` | "Weekly review", "Run our team session", "Prep for tomorrow's WIG Session", "I missed my commitment" |

### Single-file scope-specific skills (5 — scope locked by topic)

The book has no cross-scope variant for these topics, so they remain
single-file with no internal protocol switch.

| Skill slug | Scope | Stage | Canonical activation signals |
|---|---|---|---|
| `4dx-meta-whirlwind-triage` | Personal | D1 prereq | "I'm always firefighting / no time for the goal" / 「日常業務に追われて目標に手がつかない」 |
| `4dx-d1-wig-cascade` | Team-leader | D1 (cascade) | "Cascade the org WIG to sub-teams" / "How do I split the Primary WIG into Battles" |
| `4dx-meta-team-leader-onboarding` | Team-leader | Leader prep | "I'm about to lead a 4DX team" / "Get my direct-report leaders bought in" |
| `4dx-meta-xps-evaluation` | Team-leader | XPS audit | "Is our team's 4DX execution actually working?" / "Post-quarter audit" |
| `4dx-sustain-momentum-rescue` | Personal | Recovery | "Haven't done my 4DX in weeks / lost momentum" |

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
  + 1 plugin router = 11 total)
- **Output language**: description multilingual (EN + JP + zh-TW); body
  English; A2 trigger phrasings multilingual; metadata English.
- **Source basis**: BOOK_OVERVIEW.md + 10 topical skill SKILL.md
  frontmatter (A2 triggers + execution outputs).
