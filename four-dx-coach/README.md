# four-dx-coach

> Multi-scope coach for *The 4 Disciplines of Execution* — personal solo use, team-leader facilitation, AND team-member participation. The agent shape-shifts: peer-witness for solo, consultant for leaders, personal coach for members operating inside someone else's WIG.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 0.6.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

## Background

*The 4 Disciplines of Execution* (McChesney / Covey / Huling / Thele / Walker, 2nd ed., 2021) is a corporate-execution methodology validated across ~4,000 client engagements. Its prescription:

1. **D1 — Focus on the Wildly Important Goal** (one WIG, expressed as *From X to Y by When*)
2. **D2 — Act on the Lead Measures** (predictive AND influenceable)
3. **D3 — Keep a Compelling Scoreboard** (players' scoreboard, not coach's dashboard)
4. **D4 — Create a Cadence of Accountability** (weekly WIG Session of peer commitments)

The book is written primarily for **leaders rolling 4DX out across teams**. This plugin extends the methodology to two additional scopes the book under-serves:

- **Personal** — a single user adopting 4DX for an individual goal; agent fills the peer-witness role the book assumes is a colleague.
- **Team-leader** — a leader running 4DX inside a single team (not multi-team rollout); agent acts as consultant.
- **Team-member** — a contributor on a team where the leader has already chosen a WIG; agent helps you participate well, not redesign the system.

## Architecture

11 skills in three categories:

- **1 plugin router** (`using-four-dx-coach`) — cold-start dispatcher for ambiguous, cross-topic, or out-of-4DX queries.
- **5 multi-file scope-flex skills** — one topic each, with 2-4 internal protocol files covering personal / team-leader / team-member variants. The skill auto-detects scope via a one-question Socratic check, then loads the matching protocol. This replaces the 2026-04-30 pre-merge state of 15 atomic skills + 5 topic-routers.
- **5 single-file scope-specific skills** — one scope each, no internal split. The source book has no cross-scope variant for these topics, so they remain compact single-file `SKILL.md` skills.

Multi-file skills consolidate scope-overlap surface area without losing primary-source grounding: every protocol still carries its `### Industry-experience addendum` and shares the parent skill's `references/industry-grounding.md`.

## Skills (11 total)

### 1. Plugin router (1)

| Skill | What it does |
|---|---|
| [`using-four-dx-coach`](skills/using-four-dx-coach/) | Entry point for cold-start / cross-topic / out-of-4DX queries — scope-triages to personal / team-leader / team-member or hands off if 4DX doesn't fit |

### 2. Multi-file scope-flex skills (5)

Each skill below auto-detects scope via internal Socratic disambiguation, then loads the matching protocol file from `protocols/`.

| Skill | Topic | Internal protocols [multi-file scope-flex] |
|---|---|---|
| [`4dx-meta-strategy-triage`](skills/4dx-meta-strategy-triage/) | Pre-D1 fit gate (6-verdict triage) | `personal-mode.md`, `team-mode.md` |
| [`4dx-d1-wig-formulation`](skills/4dx-d1-wig-formulation/) | Write / select / decode a *From X to Y by When* WIG | `personal-define.md`, `team-select.md`, `member-comprehend.md` |
| [`4dx-d2-lead-measures`](skills/4dx-d2-lead-measures/) | Discover / facilitate / map sphere-of-influence on lead measures | `personal-discover.md`, `team-facilitate.md`, `member-influence.md` |
| [`4dx-d3-scoreboard`](skills/4dx-d3-scoreboard/) | Design / facilitate / read a players' scoreboard | `personal-design.md`, `team-lead-design.md`, `member-read.md` |
| [`4dx-d4-cadence`](skills/4dx-d4-cadence/) | Run / facilitate / prep / debrief the weekly WIG Session | `solo-session.md`, `team-leader-session.md`, `member-prep.md`, `member-debrief.md` |

### 3. Single-file scope-specific skills (5)

These topics live in one scope only because the source book has no cross-scope variant.

| Skill | Scope | What it does |
|---|---|---|
| [`4dx-d1-personal-whirlwind-triage`](skills/4dx-d1-personal-whirlwind-triage/) | Personal | 7-day time audit; surface BAU vs WIG conflict; protect ~20% WIG slot |
| [`4dx-d1-team-wig-cascade`](skills/4dx-d1-team-wig-cascade/) | Team-leader | Translate Primary WIG into Battle WIGs (Targets-not-Plans); multi-team-only concept |
| [`4dx-meta-team-leader-onboarding`](skills/4dx-meta-team-leader-onboarding/) | Team-leader | Direct-report leader buy-in (commitment vs compliance) |
| [`4dx-meta-team-xps-evaluation`](skills/4dx-meta-team-xps-evaluation/) | Team-leader | Post-quarter XPS audit (0-4 scale; C1-C4 layers) |
| [`4dx-sustain-personal-momentum-rescue`](skills/4dx-sustain-personal-momentum-rescue/) | Personal | Diagnose where the 4-discipline stack broke and route to the matching restart |

## How scope detection works

You don't pick a scope manually. Three ways scope gets resolved:

1. **The plugin router** (`using-four-dx-coach`) detects clear scope signals ("my team", "I joined", "*my* goal") and dispatches to the right skill.
2. **Multi-file scope-flex skills** ask one Socratic question at top of flow when scope is unclear, then auto-load the matching protocol — no manual selection.
3. **Single-file scope-specific skills** activate only on signals that already constrain scope (e.g. cascade → team-leader, whirlwind triage → personal).

If you're not sure where to start, just describe the situation and the router will figure it out.

## When to use this plugin

Activates on signals like:

- "Should I use 4DX for X?" / 「4DX 適合我嗎？」 / 「この目標に 4DX 使える？」
- "I'm always firefighting" / 「日常業務に追われて目標に手がつかない」
- "Goal too vague / too many priorities"
- "I have a goal but don't know what daily action drives it"
- "I track the wrong thing / dashboard too complex"
- "Want a weekly cadence to keep my goal momentum"
- "WIG cadence broke — how do I restart?"
- "Pick our team's Primary WIG / cascade the org WIG"
- "How do I get my leaders bought in (not just complying)?"
- "Run a WIG Session for my team"
- "I joined a team running 4DX — how do I participate?"
- "Prep my commitment for tomorrow's WIG Session"

Hands off for:

- Enterprise rollout across multiple teams → read the book's Part 2 (Ch 6-10) directly, or contact FranklinCovey consulting
- Habit formation → atomic habits / habit stacking is the right tool
- Portfolio bets / multi-startup founders → OKR or lean experimentation
- Emergency-responder roles where firefighting *is* the strategic work
- Pure creative output (novelist, artist) where Goodhart effects corrupt lead measures
- Clinical burnout / depression → seek professional support, not 4DX

## Install

```bash
# In Claude Code
/plugin marketplace add kouko/monkey-skills
/plugin install four-dx-coach@monkey-skills
```

The router skill `using-four-dx-coach` activates on generic queries; specific skills activate on their own signals.

## Industry-grounded boundaries

Every topical skill (5 multi-file + 5 single-file = 10 atomic-equivalents) carries an `### Industry-experience addendum` in its Boundary section, citing primary academic + regulatory + credentialed-author sources **beyond** the source book — to address the book's selection-bias and member-POV gaps. Each skill's `references/industry-grounding.md` lists the verified citations:

- D2 lead-measure-discovery: Goodhart 1975 / Strathern 1997 / CFPB 2016 (Wells Fargo) / VA OIG 2014 (Phoenix) / GBI 2011 (Atlanta APS) — Goodhart failure-mode evidence
- D1 personal-define: Christensen 1997 / March 1991 / Dweck 2006 — over-focus risk + exploration vs exploitation
- D3 personal-scoreboard: Tufte 1983 / Few 2006 / Ware 2012 — perception-design grounding for the 5-second test
- D4 solo + team WIG-Session: Rogelberg 2019 / Lencioni 2004 / Edmondson 2012 — meeting-science empirical warrant
- Member protocols: Edmondson 2018 / Grant 2016 / Meyer 2014 / Pfeffer 2010 / Drucker HBR 1999 / Cialdini 1984 / Eurich 2017 / Wiseman 2010 — fills the book's leader-POV gap
- Team-leader skills: Akao 1991 / Doerr 2018 / Kaplan & Norton 2001 / Ryan & Deci 2017 / Argyris HBR 1991 / Kotter 1996 / Galbraith / Schein / Rumelt / Porter / Mintzberg / Hambrick & Fredrickson / CMMI / McKinsey OHI / Gallup Q12

48 verified primary-source citations preserved through the Plan U merge.

## Multilingual triggers

Skill `description` and trigger signals support **English / 日本語 / 繁體中文** — you can ask in any of the three. Skill body content (Interpretation, Execution steps, Boundary) is in English for portability.

## Recommended progression

### Personal (solo) — starting from zero

1. `4dx-meta-strategy-triage` → `personal-mode.md` — verify 4DX fits your goal (or get redirected)
2. `4dx-d1-personal-whirlwind-triage` — clarify BAU vs WIG-work
3. `4dx-d1-wig-formulation` → `personal-define.md` — formulate the WIG (X → Y → When)
4. `4dx-d2-lead-measures` → `personal-discover.md` — find your 2-3 lead measures
5. `4dx-d3-scoreboard` → `personal-design.md` — design a glance-readable scoreboard
6. `4dx-d4-cadence` → `solo-session.md` — start the weekly cadence
7. `4dx-sustain-personal-momentum-rescue` — load on demand when momentum slips

### Team-leader — starting from zero

1. `4dx-meta-strategy-triage` → `team-mode.md` — confirm 4DX is the right move for your team
2. `4dx-d1-wig-formulation` → `team-select.md` — Battles 2x2 to pick the Primary WIG
3. `4dx-d1-team-wig-cascade` — cascade to team WIGs as Targets-not-Plans
4. `4dx-meta-team-leader-onboarding` — secure commitment (not compliance) from direct reports
5. `4dx-d4-cadence` → `team-leader-session.md` — run the weekly WIG Session as facilitator
6. `4dx-meta-team-xps-evaluation` — periodically audit your team's 4DX implementation

### Team-member — joining a team that already runs 4DX

1. `4dx-d1-wig-formulation` → `member-comprehend.md` — understand the team WIG you've been given
2. `4dx-d4-cadence` → `member-prep.md` — prep your commitment for the next session
3. `4dx-d4-cadence` → `member-debrief.md` — honest self-account after each session

## Attribution

Distilled from *The 4 Disciplines of Execution* (2nd ed., 2021) by Chris McChesney, Sean Covey, Jim Huling, Scott Thele, Beverly Walker (Simon & Schuster). Pipeline: `tsundoku:book-distill` (RIA-TV++ adapted from kangarooking/cangjie-skill, MIT). 26 → 11 skill consolidation via Plan U merge (2026-04-30). See [ATTRIBUTION.md](ATTRIBUTION.md).

## Related plugins

- [`tsundoku`](../tsundoku/) — the book→skill distillation pipeline that produced this plugin
- [`philosophers-toolkit`](../philosophers-toolkit/) — sibling personal-thinking-method plugin
