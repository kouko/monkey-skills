# Protocol: Personal — Design a glance-readable solo scoreboard

> Loaded by SKILL.md orchestrator when scope detection identifies a solo
> user designing their own private scoreboard for a personal WIG. Voice
> = personal coach. The user is simultaneously coach and player; the
> artifact you design is the *player's*.

## R — Reading (verbatim source quote)

> If you can't tell within five seconds whether you're winning or losing, you haven't passed this test.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 4 (Characteristics of a Compelling Players' Scoreboard, criterion 4)

## I — Interpretation (mode-specific)

A scoreboard is not a dashboard. The book draws a sharp line:

- A **coach's scoreboard** is data-rich and analytic — exists to help
  the manager *decide*. Spreadsheets, Notion DBs, multi-metric
  fitness apps — all coach's scoreboards.
- A **players' scoreboard** is simple and emotional — exists to make
  the player *want to win*. Must pass four tests: simple, visible,
  shows lead AND lag, answers "am I winning?" in five seconds.

For a personal goal, you are simultaneously coach and player — but
the artifact you live alongside daily must be the *player's*. The
coach's view is fine in a weekly review, terrible on the wall.

The non-obvious design element is the **where-you-should-be line**
(the "goat" in the book's mountain-store example). Without it, you
can see where you are but not whether that's winning. Status without
trajectory is data, not a scoreboard.

Voice contrast vs sibling protocols: the team-leader protocol coaches
the leader to facilitate the *team* to build a public board; this
protocol coaches *one user* designing for *one user* on a private
surface.

## A1 — Past Application

### Case 1: Northrop Grumman — the blown-down stadium scoreboard
- Coast Guard cutter design team had no visible execution scoreboard;
  engagement diffused into the whirlwind. A leader described a local
  stadium scoreboard blown down by Hurricane Katrina — fans went
  silent, "no one could tell you what the score was."
- Authors used this as the diagnostic: if you cannot tell the score,
  you have the blown-down scoreboard. Visible score is upstream of
  engagement, not downstream.

### Case 2: Remote Canadian plant — 74 → 94 quality via shift-vs-shift boards
- Quality stuck at 74; standard managerial pressure not moving it.
- Replaced the management report with shift-level visible boards
  posted where the next shift could see the previous shift's number.
  No new tools, no new training. Quality climbed to 94.
- The cleanest demonstration of "scoreboard lift" without
  confounding interventions — visibility itself is the active
  ingredient.

### Case 3: Fighter-plane developers — "a project plan is not a scoreboard"
- Aerospace team insisted their 14-page Gantt was their scoreboard.
- Jim Stuart's challenge: a Gantt doesn't pass the 5-second test,
  doesn't show lead-vs-lag, and isn't visible during work. They built
  a separate one-glance scoreboard alongside the project plan.
- Establishes the rule: complexity of work does not justify
  complexity of scoreboard. The two artifacts coexist.

## A2 — Future Trigger

When a solo user needs this protocol:

1. User has a personal WIG + lead measures already defined and asks
   "now how do I track this?" or "what app should I use?"
2. User reports a tracker that exists but isn't doing anything —
   Notion page they don't open, habit-app they ignore, Excel sheet
   they stopped updating, fitness app with 50 metrics that doesn't
   motivate.
3. User describes their tracking artifact and it's clearly a coach's
   scoreboard: multi-tab spreadsheet, multi-metric dashboard, Gantt
   chart, project plan — and asks why it's not driving action.
4. User wants the *visibility* of their goal increased — sticky note,
   wall calendar, lock-screen widget — but doesn't know what to put
   on it.
5. User attempted D1 + D2 and momentum is fading after 2-4 weeks
   (often a missing-scoreboard symptom, not a willpower problem).

EN: "I built a Notion dashboard but I don't actually look at it",
"My fitness app shows me too many things, none of them motivate me"
JP: 「ダッシュボードが複雑すぎて見ない」「進捗を可視化したい」
zh-TW: 「我做了一個追蹤表，可是都沒在看」「怎麼讓進度看得見？」

## E — Execution

Voice is **personal coach**. Run a Socratic design dialogue. Goal is
a scoreboard spec the user commits to displaying somewhere visible
during work, not a discussion of tracking philosophy.

1. **Confirm WIG + lead measures are defined.**
   - Ask: "What's the WIG (in From-X-to-Y-by-When form) and what are
     your one or two lead measures?"
   - Completion: user produces both, in writing.
   - Halt: WIG missing → redirect to `4dx-d1-wig-formulation`. Lead
     measures missing → redirect to `4dx-d2-lead-measures`. Do NOT
     proceed without both.

2. **Choose a display medium based on user's actual day.**
   - Ask: "Where will your eyes naturally land 3-5 times during a
     working day, even on a bad day?" Examples: sticky note on
     monitor, whiteboard above desk, fridge magnet, lock-screen
     widget, paper wall calendar near workstation, printed page
     taped to a door.
   - Completion: user names a specific physical or digital surface,
     not "an app I'll check."
   - Anti-pattern: any "I'll set up a Notion page / Obsidian
     dashboard / dedicated app" without an existing habit of opening
     it daily — flag and redirect to a passive surface already in
     their visual field.

3. **Design the lead measure visualization.**
   - Pick one of: weekly bar chart, running streak (consecutive
     days), checkbox grid (e.g. 7 boxes per week), cumulative count
     (running tally).
   - Rule: drawable / updatable in <30 seconds, by the user, by hand
     if needed.
   - Completion: user can sketch it on paper and say "I'd fill this
     in like this."

4. **Design the lag measure with a where-you-should-be line.** — see
   `../standards/lead-lag-pacing-elements.md`
   - Pick one of: progress bar with target marker, line chart with
     pacing line, thermometer with weekly target ticks.
   - The pacing line / goat / target marker is **mandatory**.
     Without it, user can see status but not whether status =
     winning.
   - Completion: user can point to "where I am" AND "where I should
     be by today" on the design.

5. **Apply the 5-second test.** — see `../standards/5-second-test.md`
   - Show or describe the design back to the user cold and ask: "If
     you hadn't built this and saw it for the first time, could you
     tell in 5 seconds whether you're winning?"
   - Completion: user answers yes without hedging. If no → simplify
     (cut elements, enlarge winning indicator, add a color or
     position cue), then re-test.
   - Hard cap: ≤4 visual elements on the final scoreboard. If more,
     cut. — see `../standards/players-vs-coaches-board.md`

6. **Lock the display location and the update cadence.**
   - User commits to (a) where it lives, (b) who updates it (always
     the user, never an app's automation if avoidable — manual
     update is part of the engagement loop), (c) when (daily for
     lead, weekly for lag is the typical default).
   - Completion: one-line statement of the form "I will post this on
     [location] and update [lead] daily / [lag] weekly."

7. **Output: scoreboard spec and immediate physical action.**
   - Write up: medium, lead viz, lag viz with target line, update
     plan, 5-second-test passing rationale.
   - Suggest one physical setup action *today* (print, stick the
     note, draw the bars on the whiteboard) — not "this weekend."
     Inertia is the failure mode this protocol exists to prevent.

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **Team contexts** — multi-stakeholder public board for a team
  the user manages → load `protocols/team-lead-design.md`.
- **Member contexts** — user is reading an inherited team board, not
  designing → load `protocols/member-read.md`.
- **Org-wide BI / KPI dashboards** — coach's scoreboards are valid
  artifacts; just not what this protocol produces.
- **Before D1 / D2 are defined** — redirect upstream.
- **Stroke-of-the-pen goals** ("buy a new desk") — nothing to
  scoreboard; execute and done.
- **Reactive / on-call / firefighting domains** where the whirlwind
  IS the strategic work — see `4dx-meta-strategy-triage`.

### Author-warned failure modes (CEs)
- **Coach's-as-players' substitution (CE-08)** — Notion DB / Excel /
  Gantt / multi-metric dashboard fails 5-sec + simple. Most common
  failure mode in personal use.
- **Status-without-trajectory (CE-09)** — progress bar without
  target ticks, fitness ring without weekly goal, habit grid without
  pacing line. Add the where-you-should-be line.
- **Project plan as scoreboard (CE-18)** — Gantt / milestone list /
  Notion task DB. Useful for analysis, useless for engagement. The
  two artifacts coexist.
- **Hidden scoreboard** — lives in an app the user doesn't open, a
  tab in Excel, a folder in Notion. Out of sight = out of mind.
- **App / automation updates the score, not the player** — fitness
  app auto-syncs all numbers; user has zero ritual of touching the
  score. Manual update is the feature.
- **Effort hours instead of lead measure outcomes** — confuses input
  with leading indicator (CE-21).
- **Goodhart misuse / vanity metric drift** — gaming the streak by
  redefining "counts." Reframe as private accountability tool, not
  a trophy.

### Author's blind spots
- **Solo / remote contexts** — book's strongest exemplars are
  co-located industrial; solo workers don't get the cross-shift
  comparison effect, so the only engagement comes from the user's
  own act of looking. Compensate with passive-surface placement.
- **Attention-economy realities** — the 2021 edition leans on the
  4DX app, but a scoreboard inside another app competes with
  notifications. Physical / passive surfaces (sticky note, paper,
  lock screen) often beat in-app dashboards.
- **"Winning" framing repels some users** — for creative /
  recovery / collaborative non-competitive goals, reframe as
  "progress visible to me"; visualization mechanism identical,
  affective frame is not.

### Easily-confused neighbours
- **OKR scorecards / KPI dashboards** — strategic-alignment
  communication, not scoreboards. Don't apply 5-second / ≤4-element
  rules.
- **Habit trackers (Atomic Habits streak grids)** — track frequency
  of one behavior; missing the lag-trend + pacing line combination.
- **Bullet journal weekly review pages** — closer to coach's view;
  reviewed periodically, not glanced at constantly.

## Standards used

- `../standards/5-second-test.md` — Step 5 test
- `../standards/players-vs-coaches-board.md` — Step 5 ≤4 cap; Step 2
  passive surface choice
- `../standards/lead-lag-pacing-elements.md` — Steps 3 & 4 element
  rules; pacing-line mandatory rule

## References

See `../references/industry-grounding.md` sections **Tufte** (data-ink
ratio + chartjunk), **Few** (dashboard-vs-database / glance
monitoring), **Ware** (pre-attentive processing) for the perception
science behind the 5-second test and ≤4 element rules.
