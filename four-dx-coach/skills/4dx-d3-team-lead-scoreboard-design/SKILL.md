---
name: 4dx-d3-team-lead-scoreboard-design
description: |
  Activate when a team leader (manager / director / supervisor) says they
  want to design a team scoreboard, the team has a Team WIG + 2-3 lead
  measures, and they need a single board visible to the whole team that
  passes the 5-second players'-scoreboard test. "Help me design our team
  scoreboard," 「team の scoreboard を設計したい」, 「幫我設計 team 的
  scoreboard」. Coaches the leader to facilitate the team building it
  (not author it solo), enforces ≤4 elements / WIG-anchoring / public
  visibility / target line, and rejects database-style management
  dashboards. Do NOT activate for personal-only scoreboards, individual
  team-members reading the board, enterprise-wide BI dashboards across
  many teams, or before D1/D2 are defined.
source_book: The 4 Disciplines of Execution (2nd ed.) — McChesney, Covey, Huling, Thele, Walker
source_chapter: Ch 4 "Discipline 3: Keep a Compelling Scoreboard"; Ch 14 "Applying Discipline 3"
source_language: en
tags: [execution, team-leadership, visualization, engagement, 4dx, players-scoreboard, facilitation]
related_skills: []
---

# Team Compelling Scoreboard — facilitating a team-built players' scoreboard

## R — Reading

> "Let the team build the scoreboard. The greater their involvement,
> the better—they will take more ownership of it if they build it
> themselves."
>
> — McChesney et al., *The 4 Disciplines of Execution*, Ch 14 (Applying D3, Step 3 — Build the Scoreboard)

---

## I — Interpretation

A team scoreboard is not a personal scoreboard scaled up, and it is not
a management dashboard scaled down. It is a third artifact with its own
constraints:

- **Public-by-design.** It lives where every team member sees it during
  work — wall, shared screen, the team's space. "Out of sight, out of
  mind" applies harder at team scale because no single person owns the
  ritual of looking.
- **Multi-stakeholder legibility.** A team has functional variety
  (engineers, ops, sales, support). The board must read instantly to
  everyone, not just to the leader who designed it. Anyone walking past
  — including a stranger — should answer "are we winning?" in five
  seconds.
- **Team-built, leader-vetoed.** The book's specific authority pattern:
  the team designs and builds it; the leader holds the WIG-anchor (no
  unrelated metrics), enforces simple/visible/lead+lag/5-second tests,
  and uses veto-not-dictate when the design drifts. Engagement is the
  point of letting them build it. A leader-authored board is technically
  cleaner and behaviorally dead.
- **Gestalt of the team's bet.** One view encodes Team WIG (lag, with
  target line) + each lead measure (with target line, individually if
  the lead requires per-person tracking). The whole "game" must be
  visible at once — not split across tabs or rotating dashboards.

The leader's job is therefore Socratic facilitation, not graphic design.
Hold the four firm rules; let the team own theme, layout, materials,
update ritual.

---

## A1 — Past Application

### Case 1: Serena's Event Management team — a textbook three-component team scoreboard
- **Problem**: Five-star hotel event team had a Team WIG ("revenue from
  corporate events from \$22M to \$31M by Dec 31") and two leads
  (2 quality site visits / associate / week; upsell premium bar to
  90% of events) but no scoreboard.
- **Methodology applied**: Serena facilitated the team through the four
  steps (theme → design → build → keep updated). They defined the WIG
  + lag at top, added Lead 1 with per-associate detail graph, added
  Lead 2 as a 90%-target bar graph. Team built it.
- **Conclusion**: A scoreboard with exactly three components — WIG/lag
  with target line, Lead 1 individualized, Lead 2 with sustained-
  performance line — passed simple/visible/complete/5-second tests.
- **Outcome**: The book uses this as the canonical worked example of a
  team scoreboard that meets all four design standards.

### Case 2: Juice-bottling shifts — public visibility creates peer accountability
- **Problem**: A union shift at a Michigan juice-bottling plant had no
  cross-shift visibility; full-truckload counts were known internally
  but invisible across shifts.
- **Methodology applied**: A scoreboard placed where the next shift
  could see the previous shift's number — public, comparative, no other
  intervention.
- **Conclusion**: The visible score itself drove behavior. Workers chose
  to skip lunch breaks to overtake another shift's number — engagement
  pulled by visibility, not pushed by management.
- **Outcome**: Authors treat this as the cleanest evidence that public
  team visibility is upstream of engagement, not downstream.

### Case 3: Northrop Grumman post-Katrina — the blown-down stadium analogy
- **Problem**: Coast Guard cutter design team had no visible execution
  scoreboard; engagement diffused into the whirlwind. A leader described
  a local stadium scoreboard blown down by Hurricane Katrina — fans
  went silent, "no one could tell you what the score was."
- **Methodology applied**: Authors used this as a diagnostic for any
  team — if your team is silent on the WIG, your scoreboard is the
  blown-down one. The team installed visible, public scoreboards.
- **Conclusion**: The visible score is the engagement substrate; without
  it the team plays without knowing the game.
- **Outcome**: Canonical 4DX teaching analogy; engagement followed
  installation.

---

## A2 — Future Trigger ★

### When will the user need this skill?

1. A team leader has already run D1 (Team WIG defined in From-X-to-Y-by-
   When form) and D2 (2-3 leads chosen) and asks: "Now how do we track
   this so the team actually sees it?"
2. The leader's current "team scoreboard" is a Notion board / weekly-
   email metric / BI dashboard that nobody on the team looks at outside
   the WIG Session.
3. The leader is about to roll out 4DX to their team and wants the
   physical / digital artifact ready before the first WIG Session.
4. The leader has a board, but cross-functional team members
   (engineers + ops + sales) read it differently — some can't tell
   "are we winning?" in 5 seconds.
5. The leader designed the board solo and the team treats it as
   management's tracker, not theirs.

### Language signals (user phrasings that should activate)

- "Help me design our team scoreboard"
- "How should our team display the WIG and lead measures?"
- "We have a Team WIG and leads — what should the scoreboard look like?"
- "My team has the goals but the dashboard isn't motivating anyone"
- "Should I put this on a wall or in our team channel?"
- "team の scoreboard を設計したい"
- "チームのスコアボードをどう作る?"
- "チーム全員が見える進捗の出し方"
- "幫我設計 team 的 scoreboard"
- "團隊計分板要怎麼設計?"
- "怎麼讓全隊都看得到進度?"

### Distinction from neighboring skills

- vs. `4dx-d3-personal-scoreboard`: that skill produces a *one-person*
  glance artifact; this skill produces a *multi-stakeholder public*
  artifact and adds team-builds-it facilitation. Redirect there if the
  user is solo or designing for themselves.
- vs. `4dx-d1-team-primary-wig-selection` / `4dx-d1-team-wig-cascade`:
  those produce the *finish line* and the *team's slice*; this skill
  produces the *visible representation*. Redirect upstream if Team WIG
  is missing.
- vs. `4dx-d2-team-lead-measure-facilitation`: that skill produces
  *what to track* (the leads); this produces *how to display* lead +
  lag together. Redirect upstream if leads are not yet chosen.
- vs. `4dx-d4-team-wig-session-lead`: that skill produces the *weekly
  cadence* of accountability; this skill produces the *artifact* the
  cadence reviews.
- vs. `4dx-d1-member-team-wig-comprehension`: that skill is for an
  individual *member* trying to understand the team's WIG; this skill
  is for the *leader* designing the board the member will read.
- vs. enterprise BI / OKR / KPI dashboard design: those optimize for
  cross-team analytic insight (correctly complex, drill-down). This
  skill rejects that frame for single-team engagement use.

---

## E — Execution

When this skill activates, run a Socratic facilitation dialogue with
the leader. The goal is a scoreboard spec the leader will return to the
*team* to build, plus a team-build session plan. Do NOT design the
scoreboard for the leader.

1. **Confirm Team WIG + lead measures are already defined.**
   - Ask: "What's the Team WIG (in From-X-to-Y-by-When form) and what
     are your 2-3 lead measures?"
   - Completion criterion: leader produces both, in writing, both
     measurable.
   - Halt condition: if Team WIG is missing → redirect to
     `4dx-d1-team-primary-wig-selection` or `4dx-d1-team-wig-cascade`.
     If leads are missing → redirect to
     `4dx-d2-team-lead-measure-facilitation`. Do NOT proceed.

2. **Confirm the leader will let the team build it.**
   - Ask: "Will you facilitate the team to design and build this, or
     are you planning to author it yourself?" Surface book Step 3:
     team-built drives ownership; leader-authored boards die in week 4.
   - Completion criterion: leader commits to facilitating, not
     authoring. (Exception per book: very small discretionary time —
     leader produces, team still chooses theme.)
   - Anti-pattern: leader says "I'll just make it nice and show them" —
     name as engagement-killer, redirect.

3. **Lock the public display location.**
   - Ask: "Where will the team see this during work, not only in the
     WIG Session?" Examples: shared wall in team space, TV in team
     room, pinned channel post with shared image, 4DX app for
     dispersed teams. If geographically dispersed → must be on every
     desktop / mobile, not "I'll send the screenshot weekly."
   - Completion criterion: leader names a specific surface where 100%
     of the team will pass within a working day. "I'll put it in
     SharePoint" without an open-it-daily ritual fails.

4. **Specify the four firm rules the leader must hold.**
   The team owns layout, theme, materials. The leader vetoes when the
   board violates any of these:
   - Rule 1 — **Simple**: ≤4 visual elements total. Team WIG + lag
     trend + N lead trends. No supporting data, no historical
     comparisons, no projections, no status updates.
   - Rule 2 — **Visible**: large fonts, glance-readable from across
     the team space, posted publicly.
   - Rule 3 — **Lead AND lag with target lines**: WIG/lag must show
     "where we should be by today" line; each lead must show its
     standard (e.g. 90% sustained line). Per-person breakdown if the
     lead requires individual tracking (per Serena Lead 1).
   - Rule 4 — **5-second test**: a teammate or stranger walking past
     must answer "are we winning?" in 5 seconds.
   - Completion criterion: leader can recite the 4 rules and says they
     will hold them in the team-build session.

5. **Plan the team-build session.**
   - Ask: "When and how will you run the build session?" Recommend the
     book's 4 steps (Theme → Design → Build → Keep Updated) as the
     session agenda. Leader's role: open with the WIG and leads; let
     team pick theme; ask the four rule-questions during design; veto
     if violated, otherwise hands off.
   - Completion criterion: leader has a date, attendees, agenda, and
     understands they are facilitator not author.

6. **Lock the update ritual.**
   - Per book: leader makes very clear (a) who is responsible for
     updating the scoreboard, (b) when it is posted, (c) how often it
     is updated (≥ weekly). Updates are by the team, not by the
     leader, not by an automated feed alone — manual update is the
     engagement loop.
   - Completion criterion: leader produces a one-line statement: "X
     updates the scoreboard every Y, posted at Z."

7. **Output: spec + team-build plan + leader's holding-the-line
   prompts.**
   - Write up: location, the 4 firm rules, agenda for the team build,
     update ritual, and 3-4 sentences the leader can use in the
     session to redirect when the team starts adding extras (e.g.
     "that's data the weekly review needs, not a glance number — let's
     route it to the 1-pager log").
   - Suggest the leader hold the team-build session within 7 days.
     Inertia is the failure mode this skill exists to prevent.

---

## B — Boundary ★

### Do NOT use this skill in:

- **Personal-only scoreboards.** If the user is a solo professional
  designing for themselves alone, route to `4dx-d3-personal-scoreboard`
  — different audience, no team-build dynamic.
- **Member POV — reading a board, not designing one.** If the user is
  on a team and trying to understand the leader's board, route to
  `4dx-d1-member-team-wig-comprehension`. This skill is for the
  *leader* of one team designing for *that* team.
- **Enterprise-wide BI / multi-team aggregated dashboards.** A board
  rolling up across 30 teams for executives is correctly complex
  (coach's scoreboard, drill-down). This skill is single-team scope.
- **Before D1/D2 are defined.** A scoreboard without a Team WIG and
  leads visualizes the wrong things. Redirect upstream.
- **Stroke-of-the-pen team goals** (e.g. "complete the migration").
  Project-plan, not scoreboard, is the right artifact.
- **Reactive / on-call team contexts** where the whirlwind IS the
  strategic work; a separate WIG board creates phantom guilt.
- **High-context-culture teams where public peer-comparison reads as
  face-loss.** The book's juice-bottling shift-vs-shift exemplar
  generalizes poorly to JP / ZH / KR team settings — soften the
  comparison frame to team-vs-target rather than person-vs-person.

### Author-warned failure modes (CEs from the cluster)

- **Coach's-as-players' substitution (CE-08 at team scale)**: the
  leader's "team scoreboard" is a Power BI / Tableau / Notion DB / KPI
  dashboard with 15 panels. Fails simple + 5-second + single-purpose.
  Most common failure mode.
- **Hidden / out-of-sight scoreboard**: lives in a SharePoint folder /
  channel tab / app nobody opens. Book's "out of sight, out of mind"
  rule fires harder at team scale because no individual owns looking.
- **Status-without-trajectory (CE-09)**: lag shown but no target line.
  Team can see status but not whether status = winning. The book is
  firm: a target line MUST be visible on the scoreboard.
- **Project plan as scoreboard (CE-18)**: Gantt / milestone list /
  Jira board substituted as the "team scoreboard." Useful for
  analysis, dead for engagement. The two artifacts coexist.
- **Leader-authored board** (CE specific to team scale): leader
  designs and builds it solo, then unveils to the team. Visually
  cleaner, ownership zero. Book's Step 3 is explicit: let the team
  build it.
- **Leader updates the score, not the team**: removes the engagement
  loop. Per book, the leader makes who-and-when responsibility clear,
  but the team performs the update.
- **Communication-board drift**: scoreboard becomes a place to post
  reports, status updates, announcements. Book Ch 14 names this and
  bans it explicitly.
- **Dashboard rotation / multi-tab**: the "scoreboard" is 6 tabs
  rotating on a TV. Fails single-glance. Pick one view.
- **Dispersed-team excuse to skip the artifact**: "we're remote so
  it's hard." Per book: dispersed teams use the 4DX app or shared
  digital screen visible on every desktop / mobile — not no
  scoreboard.

### Author's blind spots / period limitations

- The 2021 edition leans on the 4DX app for digital scoreboards but
  doesn't engage with attention-economy realities — a scoreboard
  inside another app competes with notifications, email, Slack. For
  co-located teams the physical wall still beats in-app for visibility.
- The book's strongest team-scoreboard exemplars (juice-bottling
  shifts, hotel front desk, retail store) are co-located industrial
  settings where shift-vs-shift comparison creates engagement. Knowledge-
  work teams (engineering, research, design) need a softened version
  — team-vs-target, not person-vs-person leaderboard, especially in
  high-context cultures (JP / ZH / KR).
- "Players' scoreboard" framing is sports / hockey-rink culture. For
  teams where "winning" reads wrong (clinical, recovery, support,
  collaborative non-competitive), reframe as "progress visible to
  everyone" — the visualization mechanism is identical, the affective
  frame is not.
- The book under-engages multi-stakeholder legibility — boards designed
  by one functional sub-group (often engineers or ops) often fail to
  read clearly to other functions. Run a cross-role legibility check
  inside the team-build session before locking.

### Easily-confused neighboring methodologies

- **OKR scorecards / KPI dashboards**: serve strategic-alignment and
  cross-team analytic purposes. Do not apply 5-second / ≤4-element
  rules there.
- **Agile burndown / velocity charts**: work-in-progress charts, not
  WIG scoreboards. A burndown can complement but does not replace the
  team scoreboard (no lead+lag pairing, no WIG anchoring).
- **BSC (Balanced Scorecard) team boards**: 4-perspective scorecards
  serve strategic-alignment communication; they are coach's-view
  artifacts and do not pass the 5-second test by design.

### Industry-experience addendum

The book's 4 design rules + team-builds-it engagement claim sit on
40+ years of information-design and organizational-engagement research
naming the mechanisms — citations in `references/industry-grounding.md`:

- **Tufte (1983/2001), *Visual Display of Quantitative Information*
  (Graphics Press; ISBN 978-0961392147)** — data-ink + chartjunk
  (cross-ref from personal D3). At team scale, decoration reading as
  personality to one sub-group reads as noise to another, so "minimize
  non-data-ink" hits harder for multi-stakeholder legibility.
- **Few (2006/2013), *Information Dashboard Design* (O'Reilly /
  Analytics Press; ISBN 978-0596100162)** — dashboard (single-screen
  glance) vs database (drill-down). The single-team scoreboard is
  canonically Few's dashboard; org-wide BI is database. Mixing them is
  the most common team-leader failure.
- **Macey & Schneider (2008), "The Meaning of Employee Engagement,"
  *Industrial-Organizational Psychology* 1(1): 3-30** — peer-reviewed
  taxonomy (trait / state / behavioral). Public scoreboards trigger
  state-engagement (felt-energy from visible feedback) and behavioral-
  engagement (discretionary effort visible to peers). The mechanism
  behind the book's juice-bottling exemplar.

Team-coach implication: a board failing data-ink, dashboard-vs-database,
or public-feedback-loop checks goes invisible by week 4 — the failure
curve the book attributes to "lack of compelling design" without naming
the perception-and-engagement mechanisms producing it.

---

## Related skills

- `4dx-d1-team-primary-wig-selection` — depends-on — need a Team WIG
- `4dx-d1-team-wig-cascade` — depends-on — Team WIG cascaded from Primary
- `4dx-d2-team-lead-measure-facilitation` — depends-on — leads must exist
- `4dx-d4-team-wig-session-lead` — composes-with — session reads this artifact
- `4dx-d3-personal-scoreboard` — contrasts-with — solo vs team scope
- `4dx-d1-member-team-wig-comprehension` — contrasts-with — reader vs designer
- `4dx-d3-scoreboard` — composes-with — topic-router fallback when role unclear

---

## Audit metadata

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Test pass rate**: pending (see `test-prompts.json` and `test-results.md`)
- **Distilled at**: 2026-04-30
- **Output language**: body — English (matches source); metadata — English
