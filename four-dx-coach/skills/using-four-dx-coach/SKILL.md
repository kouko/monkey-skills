---
name: using-four-dx-coach
description: |
  Router for the four-dx-coach plugin. Activates on generic / vague 4DX
  queries OR when the user's scope is unclear. Triages by scope first —
  personal (solo) / team-leader / team-member — then by 4DX stage, and
  dispatches across 20 atomic skills (plus 5 topic-routers between this router
  and the atomic skills). EN: "I want to start using 4DX",
  "help my team apply 4 Disciplines", "where do I begin with 4DX?",
  "I joined a team using 4DX". JP: 「4DX を使い始めたい」「4 つの規律
  をチームに導入したい」「4DX の始め方」「4DX のチームに入った」.
  zh-TW: 「想要開始用 4DX」「4 個執行紀律怎麼開始」「想用 4DX 帶
  團隊」「我加入了一個用 4DX 的團隊」. 20 atomic skills: 7 personal (meta /
  whirlwind / WIG / leads / scoreboard / session / sustain), 8 team-leader
  (meta / primary-WIG / cascade / onboarding / lead-measure-facilitation /
  scoreboard-design / session-lead / XPS-eval), 5 team-member
  (WIG-comprehension / lead-measure-influence / scoreboard-reading /
  commitment-prep / account-debrief).
  Hands off when 4DX doesn't fit — habit-stacking / OKR / agile / burnout.
  Do NOT activate when user names a specific skill or has full WIG+leads+
  scoreboard+cadence running with a discipline-specific question.
source_book: The 4 Disciplines of Execution — McChesney, Covey, Huling, Thele, Walker (2nd ed., 2021)
source_language: en
tags: [router, entry-point, dispatcher, 4dx, scope-triage, personal, team-leader, team-member]
related_skills:
  - 4dx-meta-personal-strategy-triage
  - 4dx-d1-personal-whirlwind-triage
  - 4dx-d1-personal-wig-defining
  - 4dx-d2-personal-lead-measure-discovery
  - 4dx-d3-personal-scoreboard
  - 4dx-d4-personal-wig-session
  - 4dx-sustain-personal-momentum-rescue
  - 4dx-meta-team-strategy-triage
  - 4dx-d1-team-primary-wig-selection
  - 4dx-d1-team-wig-cascade
  - 4dx-meta-team-leader-onboarding
  - 4dx-d2-team-lead-measure-facilitation
  - 4dx-d3-team-lead-scoreboard-design
  - 4dx-d4-team-wig-session-lead
  - 4dx-meta-team-xps-evaluation
  - 4dx-d1-member-team-wig-comprehension
  - 4dx-d2-member-lead-measure-influence
  - 4dx-d3-member-scoreboard-reading
  - 4dx-d4-member-commitment-prep
  - 4dx-d4-member-account-debrief
---

# using-four-dx-coach — 4DX Router (entry point)

## Mission

Route generic / vague / scope-ambiguous 4DX queries to the correct atomic
skill. Triage first by **scope** (personal / team-leader / team-member),
then by **4DX stage**. If 4DX is the wrong methodology for the user's
problem, decline and redirect — do not bend the problem onto the wrong
shape.

> "The 4 Disciplines are a matched set, not a menu of choices."
> — McChesney et al., *Chapter 1*

This router is the entry door. Each atomic skill behind it owns its own
gate logic; the router only decides *which door to open*.

---

## The 20 atomic skills indexed by scope

### Personal scope (solo practitioner — 7 skills)

| Skill slug | Stage | Canonical activation signal | Role |
|---|---|---|---|
| `4dx-meta-personal-strategy-triage` | Pre-D1 gate | "Should I use 4DX for [X]?" / 「4DX 適してる？」 | Decide if 4DX fits the goal at all (6-verdict triage). |
| `4dx-d1-personal-whirlwind-triage` | D1 prereq | "I'm always firefighting / no time for the goal." | 7-day time audit; surface BAU vs strategic capacity. |
| `4dx-d1-personal-wig-defining` | D1 | "My goal is vague / too many priorities." | Coach to one *From X to Y by When* WIG. |
| `4dx-d2-personal-lead-measure-discovery` | D2 | "I have the goal — what do I DO daily?" | Discover 2-3 predictive AND influenceable lead measures. |
| `4dx-d3-personal-scoreboard` | D3 | "My tracker is too complex / I don't look at it." | Players' scoreboard, ≤4 elements, 5-second test. |
| `4dx-d4-personal-wig-session` | D4 | "I want a weekly review for goal momentum." | Run 20-30 min weekly Account → Review → Plan. |
| `4dx-sustain-personal-momentum-rescue` | Recovery | "Haven't done my 4DX in weeks / lost momentum." | Diagnose broken layer; route to matching restart. |

### Team-leader scope (positional authority on goal-setting — 8 skills)

| Skill slug | Stage | Canonical activation signal | Role |
|---|---|---|---|
| `4dx-meta-team-strategy-triage` | Pre-D1 gate | "Should my team use 4DX vs OKR / agile?" | Verify 4DX fits the team's goal class. |
| `4dx-d1-team-primary-wig-selection` | D1 (org) | "Help my org pick our Primary WIG." | Single Primary WIG for the whole org / division. |
| `4dx-d1-team-wig-cascade` | D1 (cascade) | "How do I cascade WIGs to my sub-teams?" | Translate Primary WIG into team-level WIGs. |
| `4dx-meta-team-leader-onboarding` | Leader prep | "I'm about to lead a 4DX team — where do I start?" | Leader-of-leaders cadence + ownership setup. |
| `4dx-d2-team-lead-measure-facilitation` | D2 (lead) | "Help me facilitate my team picking 2-3 leads." | Veto-not-dictate facilitation of team's lead discovery. |
| `4dx-d3-team-lead-scoreboard-design` | D3 (lead) | "Help me design our team scoreboard." | Facilitate team to build public players' scoreboard. |
| `4dx-d4-team-wig-session-lead` | D4 (lead) | "How do I run my team's weekly WIG Session?" | Facilitate team's 20-30 min Account → Review → Plan. |
| `4dx-meta-team-xps-evaluation` | XPS audit | "Is our team's 4DX execution actually scoring?" | XPS (Execution Performance Score) audit + remediation. |

### Team-member scope (joined a team that runs 4DX — 5 skills)

| Skill slug | Stage | Canonical activation signal | Role |
|---|---|---|---|
| `4dx-d1-member-team-wig-comprehension` | D1 (member) | "My manager set our team's WIG — what does it mean for me?" | Decode the team WIG; locate personal contribution. |
| `4dx-d2-member-lead-measure-influence` | D2 (member) | "Our team's leads are set — how do I influence them?" | Map per-lead 0-5 influence; pick 1-2 focus; escalate no-influence. |
| `4dx-d3-member-scoreboard-reading` | D3 (member) | "How do I read my team's scoreboard?" | ≤5-min weekly diagnostic + escalation if board broken. |
| `4dx-d4-member-commitment-prep` | D4 prep | "WIG Session is tomorrow — what should I commit to?" | Prep one high-impact weekly commitment. |
| `4dx-d4-member-account-debrief` | D4 debrief | "I missed my commitment last week — what now?" | Honest account in next session; recover ownership. |

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

### Step 2 — Ask scope explicitly (only when ambiguous)

> "Before I route you to the right tool — are you applying 4DX to:
> (a) **a personal / solo goal** (you set it, you execute it),
> (b) **a team you lead** (you have authority to set the team's WIG),
> or (c) **a team you've joined** (someone else set the WIG, you execute
> within it)?"

Wait for the answer; do not guess.

### Step 2.5 — If topic is clear but role/scope is ambiguous, defer to a topic-router

If the user's **topic is already clear** (meta-strategy-triage / D1-WIG / D2-leads / D3-scoreboard / D4-cadence)
but **role or scope is still ambiguous**, defer to the matching topic-router —
do **NOT** route directly to atomic skills:

| Topic signal in query | Defer to topic-router |
|---|---|
| "Should X use 4DX?" / "Is 4DX a good fit?" (no actor named) | `4dx-meta-strategy-triage` |
| "Help me with my WIG" / "How do I set a WIG?" (no actor + verb) | `4dx-d1-wig-formulation` |
| "Help me with lead measures" / "How do I find lead measures?" (no role) | `4dx-d2-lead-measures` |
| "Help me with the scoreboard" / "How should I track this?" (no role + verb) | `4dx-d3-scoreboard` |
| "Help with my WIG Session" / "weekly cadence" (no role + timing) | `4dx-d4-cadence` |

The topic-router will run its own ONE-question disambiguation, then hand off to
the precise atomic skill. This prevents the plugin router from guessing at
mid-topic queries where the user's signal is locally narrow.

### Step 3 — Route within scope by 4DX stage

#### Personal scope routing

1. Fit unsure → `4dx-meta-personal-strategy-triage`
2. No time / always firefighting → `4dx-d1-personal-whirlwind-triage`
3. Goal vague / multi-priority → `4dx-d1-personal-wig-defining`
4. WIG set, daily action unclear → `4dx-d2-personal-lead-measure-discovery`
5. Tracker noisy / unread → `4dx-d3-personal-scoreboard`
6. Need weekly cadence → `4dx-d4-personal-wig-session`
7. Lapsed practice → `4dx-sustain-personal-momentum-rescue`

#### Team-leader scope routing

1. Fit unsure (team) → `4dx-meta-team-strategy-triage`
2. About to lead → `4dx-meta-team-leader-onboarding`
3. Need a single org-level WIG → `4dx-d1-team-primary-wig-selection`
4. Need to cascade Primary WIG to sub-teams → `4dx-d1-team-wig-cascade`
5. Need to facilitate team picking lead measures → `4dx-d2-team-lead-measure-facilitation`
6. Need to facilitate team building scoreboard → `4dx-d3-team-lead-scoreboard-design`
7. Need to run weekly team session → `4dx-d4-team-wig-session-lead`
8. Auditing whether 4DX is actually working → `4dx-meta-team-xps-evaluation`

#### Team-member scope routing

1. New to the team's WIG, decoding it → `4dx-d1-member-team-wig-comprehension`
2. Team leads set, mapping personal influence → `4dx-d2-member-lead-measure-influence`
3. Reading the team scoreboard → `4dx-d3-member-scoreboard-reading`
4. Prepping next session's commitment → `4dx-d4-member-commitment-prep`
5. Missed a commitment / debrief needed → `4dx-d4-member-account-debrief`

### Step 4 — If 4DX is wrong shape

Skip routing; use the hand-off scripts below.

---

## Recommended progression by scope

### Personal — solo first-time user

```
meta-personal-triage → d1-whirlwind → d1-wig-defining → d2-leads
  → d3-scoreboard → d4-session → (sustain on demand)
```

Sequential — 4DX is "a matched set, not a menu" (P-23). If the user wants
to cherry-pick (e.g. just D4 weekly reviews without a WIG), the meta-triage
skill will flag the mismatch.

### Team-leader — first-time team rollout

```
meta-team-triage → meta-team-leader-onboarding
  → (d1-primary-wig-selection OR d1-wig-cascade depending on level)
  → d4-team-wig-session-lead (start weekly cadence)
  → meta-team-xps-evaluation (after 4-8 weeks of cadence)
```

Cascade vs Primary depends on the leader's altitude: top of the org →
Primary WIG; mid-leader inheriting one → Cascade.

### Team-member — joined a 4DX team mid-flight

```
d1-member-team-wig-comprehension (one-time onboarding)
  → d4-member-commitment-prep (each session, before)
  → d4-member-account-debrief (each session, after)
  → loop weekly
```

Members have no D2/D3 ownership — those belong to the leader. Members
own commitment prep and honest accounting only.

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
> by Dec 31), come back via `4dx-d2-personal-lead-measure-discovery`."

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
  WIG?" → `4dx-d1-personal-wig-defining` directly. "Help my team pick a
  Primary WIG" → `4dx-d1-team-primary-wig-selection` directly. "I missed
  my commitment last week" → `4dx-d4-member-account-debrief` directly.
- **User has full D1+D2+D3+D4 already running and asks a specific
  question** — route to the matching atomic skill, skip the router.
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

## Topic routers (mid-flow disambiguation)

Five **topic-router** skills sit between this plugin router and the atomic
skills. They activate only on **ambiguous mid-topic queries** — when the user
has a topic in mind but hasn't yet named scope or role:

| Topic-router | Disambiguates | Routes to |
|---|---|---|
| `4dx-meta-strategy-triage` | scope (personal vs team) | `4dx-meta-personal-strategy-triage` / `4dx-meta-team-strategy-triage` |
| `4dx-d1-wig-formulation` | scope + verb (define / select / comprehend) | `4dx-d1-personal-wig-defining` / `4dx-d1-team-primary-wig-selection` / `4dx-d1-member-team-wig-comprehension` |
| `4dx-d2-lead-measures` | role (solo / leader-facilitator / member-influencer) | `4dx-d2-personal-lead-measure-discovery` / `4dx-d2-team-lead-measure-facilitation` / `4dx-d2-member-lead-measure-influence` |
| `4dx-d3-scoreboard` | role + verb (solo design / leader-facilitate-build / member-read) | `4dx-d3-personal-scoreboard` / `4dx-d3-team-lead-scoreboard-design` / `4dx-d3-member-scoreboard-reading` |
| `4dx-d4-cadence` | role + timing (solo / leader / member; before / during / after) | `4dx-d4-personal-wig-session` / `4dx-d4-team-wig-session-lead` / `4dx-d4-member-commitment-prep` / `4dx-d4-member-account-debrief` |

**Division of labour**:

- **This plugin router** (`using-four-dx-coach`) fires on **cold-start**,
  **out-of-4DX**, and **cross-topic** queries — the user is at the front door,
  hasn't named a discipline, or is asking whether 4DX even applies to a
  domain we should hand off elsewhere.
- **Topic-routers** fire on **mid-topic** queries — the user has clearly
  named a topic (fit / WIG / cadence) but their actor or timing is still
  ambiguous.
- **Atomic skills** fire when scope + verb + role are all explicit.

When a query already has a clear topic, defer to the topic-router rather
than routing directly to atomic skills. See Step 2.5 above for the deferral
table.

---

## Audit metadata

- **Skill type**: router (`using-*` convention)
- **Verification**: router skill — no triple verification needed (each
  atomic skill it dispatches to owns its own V1/V2/V3 audit).
- **Distilled at**: 2026-04-29 (v0.2 — scope-triage upgrade for 17 skills) /
  2026-04-30 (v0.3 — D2/D3 expansion: +4 atomic + 2 topic-routers → 20 atomic + 5 topic-routers + 1 plugin router = 26 total)
- **Output language**: description multilingual (EN + JP + zh-TW); body
  English; A2 trigger phrasings multilingual; metadata English.
- **Source basis**: BOOK_OVERVIEW.md + 20 atomic skill SKILL.md
  frontmatter (A2 triggers + execution outputs).
