# four-dx-coach

> Multi-scope coach for *The 4 Disciplines of Execution* — personal solo use, team-leader facilitation, AND team-member participation. The agent shape-shifts: peer-witness for solo, consultant for leaders, personal coach for members operating inside someone else's WIG.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 0.2.0
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

## What scope are you in?

| If you... | Use the ... skills | Agent role |
|---|---|---|
| ... are pursuing a personal goal alone | `personal-*` | peer-witness |
| ... lead a team that's adopting 4DX | `team-*` | consultant-to-leader |
| ... are a member of a team running 4DX | `member-*` | personal coach to member |

If you're not sure, start with the router (`using-four-dx-coach`) — it does scope triage first.

## Skills (26 total — full 3-scope coverage of D1–D4)

### Personal (7)

| Stage | Skill | What it does |
|---|---|---|
| meta | [`4dx-meta-personal-strategy-triage`](skills/4dx-meta-personal-strategy-triage/) | Decide whether 4DX fits your goal *before* you start |
| D1 | [`4dx-d1-personal-whirlwind-triage`](skills/4dx-d1-personal-whirlwind-triage/) | Surface BAU vs WIG conflict via 7-day audit |
| D1 | [`4dx-d1-personal-wig-defining`](skills/4dx-d1-personal-wig-defining/) | Coach From X to Y by When formulation |
| D2 | [`4dx-d2-personal-lead-measure-discovery`](skills/4dx-d2-personal-lead-measure-discovery/) | Find 2–3 predictive + influenceable lead measures |
| D3 | [`4dx-d3-personal-scoreboard`](skills/4dx-d3-personal-scoreboard/) | Design a 5-second-test players' scoreboard |
| D4 | [`4dx-d4-personal-wig-session`](skills/4dx-d4-personal-wig-session/) | Run the 20–30 min weekly WIG Session — agent = peer-witness |
| sustain | [`4dx-sustain-personal-momentum-rescue`](skills/4dx-sustain-personal-momentum-rescue/) | Diagnose where the cadence broke and route to the right rescue |

### Team-leader (8)

| Stage | Skill | What it does |
|---|---|---|
| meta | [`4dx-meta-team-strategy-triage`](skills/4dx-meta-team-strategy-triage/) | Decide whether your team should adopt 4DX |
| D1 | [`4dx-d1-team-primary-wig-selection`](skills/4dx-d1-team-primary-wig-selection/) | Pick the org Primary WIG using the Battles 2x2 |
| D1 | [`4dx-d1-team-wig-cascade`](skills/4dx-d1-team-wig-cascade/) | Translate org WIG into team WIGs (Targets-not-Plans discipline) |
| meta | [`4dx-meta-team-leader-onboarding`](skills/4dx-meta-team-leader-onboarding/) | Get direct-report leaders bought in — commitment vs compliance |
| **D2** | [**`4dx-d2-team-lead-measure-facilitation`**](skills/4dx-d2-team-lead-measure-facilitation/) | **Facilitate the team finding 2-3 lead measures (veto-not-dictate)** |
| **D3** | [**`4dx-d3-team-lead-scoreboard-design`**](skills/4dx-d3-team-lead-scoreboard-design/) | **Facilitate team to build a public, multi-stakeholder players' scoreboard** |
| D4 | [`4dx-d4-team-wig-session-lead`](skills/4dx-d4-team-wig-session-lead/) | Run the team WIG Session as facilitator |
| meta | [`4dx-meta-team-xps-evaluation`](skills/4dx-meta-team-xps-evaluation/) | XPS audit framework for an intra-team 4DX implementation |

### Team-member (5)

| Stage | Skill | What it does |
|---|---|---|
| D1 | [`4dx-d1-member-team-wig-comprehension`](skills/4dx-d1-member-team-wig-comprehension/) | Understand the team WIG you've been given |
| **D2** | [**`4dx-d2-member-lead-measure-influence`**](skills/4dx-d2-member-lead-measure-influence/) | **Identify your sphere of influence on inherited team lead measures** |
| **D3** | [**`4dx-d3-member-scoreboard-reading`**](skills/4dx-d3-member-scoreboard-reading/) | **Read team scoreboard + locate own contribution + escalation if broken** |
| D4 | [`4dx-d4-member-commitment-prep`](skills/4dx-d4-member-commitment-prep/) | Prep your specific commitment for the next WIG Session |
| D4 | [`4dx-d4-member-account-debrief`](skills/4dx-d4-member-account-debrief/) | Honest self-account before / after a session |

### Topic-routers (5) — for ambiguous-scope queries within a known topic

| Topic | Skill | Routes between |
|---|---|---|
| meta-triage | [`4dx-meta-strategy-triage`](skills/4dx-meta-strategy-triage/) | personal vs team strategy-triage |
| D1 WIG | [`4dx-d1-wig-formulation`](skills/4dx-d1-wig-formulation/) | personal-define / team-select / member-comprehend |
| **D2 leads** | [**`4dx-d2-lead-measures`**](skills/4dx-d2-lead-measures/) | **personal-discover / team-facilitate / member-influence** |
| **D3 scoreboard** | [**`4dx-d3-scoreboard`**](skills/4dx-d3-scoreboard/) | **personal-design / team-lead-design / member-read** |
| D4 cadence | [`4dx-d4-cadence`](skills/4dx-d4-cadence/) | solo-session / team-lead-session / member-prep / member-debrief |

Each topic-router activates only when the topic is clear but scope/role is ambiguous. It asks ONE Socratic question to disambiguate, then defers to the atomic skill.

### Plugin router (1)

| Skill | What it does |
|---|---|
| [`using-four-dx-coach`](skills/using-four-dx-coach/) | Entry point for cold-start / cross-topic / out-of-4DX queries — scope-triages to personal / team-leader / team-member or hands off if 4DX doesn't fit |

## When to use this plugin

✅ **Activates on** signals like:

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

❌ **Hands off** for:

- Enterprise rollout across multiple teams → read the book's Part 2 (Ch 6–10) directly, or contact FranklinCovey consulting
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

Every atomic skill carries an `### Industry-experience addendum` in its Boundary section, citing primary academic + regulatory + credentialed-author sources **beyond** the source book — to address the book's selection-bias and member-POV gaps. Each skill's `references/industry-grounding.md` lists the verified citations:

- D2 lead-measure-discovery: Goodhart 1975 / Strathern 1997 / CFPB 2016 (Wells Fargo) / VA OIG 2014 (Phoenix) / GBI 2011 (Atlanta APS) — Goodhart failure-mode evidence
- D1 personal-wig-defining: Christensen 1997 / March 1991 / Dweck 2006 — over-focus risk + exploration vs exploitation
- D3 personal-scoreboard: Tufte 1983 / Few 2006 / Ware 2012 — perception-design grounding for the 5-second test
- D4 personal-wig-session + team-wig-session-lead: Rogelberg 2019 / Lencioni 2004 / Edmondson 2012 — meeting-science empirical warrant
- Member skills: Edmondson 2018 / Grant 2016 / Meyer 2014 / Pfeffer 2010 / Drucker HBR 1999 / Cialdini 1984 / Eurich 2017 / Wiseman 2010 — fills the book's leader-POV gap
- Team-leader skills: Akao 1991 / Doerr 2018 / Kaplan & Norton 2001 / Ryan & Deci 2017 / Argyris HBR 1991 / Kotter 1996 / Galbraith / Schein / Rumelt / Porter / Mintzberg / Hambrick & Fredrickson / CMMI / McKinsey OHI / Gallup Q12

48 verified primary-source citations across 16 skills.

## Multilingual triggers

Skill `description` and trigger signals support **English / 日本語 / 繁體中文** — you can ask in any of the three. Skill body content (Interpretation, Execution steps, Boundary) is in English for portability.

## Recommended progression

### Personal (solo) — starting from zero

1. `4dx-meta-personal-strategy-triage` — verify 4DX fits your goal (or get redirected)
2. `4dx-d1-personal-whirlwind-triage` — clarify BAU vs WIG-work
3. `4dx-d1-personal-wig-defining` — formulate the WIG (X → Y → When)
4. `4dx-d2-personal-lead-measure-discovery` — find your 2–3 lead measures
5. `4dx-d3-personal-scoreboard` — design a glance-readable scoreboard
6. `4dx-d4-personal-wig-session` — start the weekly cadence
7. `4dx-sustain-personal-momentum-rescue` — load on demand when momentum slips

### Team-leader — starting from zero

1. `4dx-meta-team-strategy-triage` — confirm 4DX is the right move for your team
2. `4dx-d1-team-primary-wig-selection` — Battles 2x2 to pick the Primary WIG
3. `4dx-d1-team-wig-cascade` — cascade to team WIGs as Targets-not-Plans
4. `4dx-meta-team-leader-onboarding` — secure commitment (not compliance) from direct reports
5. `4dx-d4-team-wig-session-lead` — run the weekly WIG Session as facilitator
6. `4dx-meta-team-xps-evaluation` — periodically audit your team's 4DX implementation

### Team-member — joining a team that already runs 4DX

1. `4dx-d1-member-team-wig-comprehension` — understand the team WIG you've been given
2. `4dx-d4-member-commitment-prep` — prep your commitment for the next session
3. `4dx-d4-member-account-debrief` — honest self-account before / after each session

## Attribution

Distilled from *The 4 Disciplines of Execution* (2nd ed., 2021) by Chris McChesney, Sean Covey, Jim Huling, Scott Thele, Beverly Walker (Simon & Schuster). Pipeline: `tsundoku:book-distill` (RIA-TV++ adapted from kangarooking/cangjie-skill, MIT). See [ATTRIBUTION.md](ATTRIBUTION.md).

## Related plugins

- [`tsundoku`](../tsundoku/) — the book→skill distillation pipeline that produced this plugin
- [`philosophers-toolkit`](../philosophers-toolkit/) — sibling personal-thinking-method plugin
