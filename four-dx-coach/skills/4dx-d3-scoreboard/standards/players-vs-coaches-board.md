# Standard: Players' vs coach's scoreboard — primary distinction

## Statement

The book's primary D3 distinction. A **players' scoreboard** is
simple and emotional; it exists to make the player(s) want to win.
A **coach's scoreboard** is data-rich and analytic; it exists to
help the manager / analyst decide. Both are valid artifacts; **D3
produces the players' scoreboard only**. Collapsing the two — using
a coach's scoreboard where a players' scoreboard belongs — is the
**most common failure mode** across all three D3 scopes. Hard cap
on players' scoreboard: **≤4 visual elements**.

## Source

> A coach's scoreboard is for the coach. It's data-rich and complex. … A players' scoreboard is for the players. It's simple, it's visible, and it shows lead and lag measures. Most of all, it tells the players within five seconds whether they are winning or losing.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 4 (Players' vs. Coach's Scoreboards)

## Why it matters

The distinction operationalizes Stephen Few's
**dashboard-vs-database** distinction (single-screen at-a-glance
monitoring vs drill-down analytic). Mixing the two produces an
artifact that fails *both* purposes — too dense to glance at, too
shallow to analyze. Consequences manifest differently per scope:

- **Solo personal use** — "coach's-as-players' substitution
  (CE-08)": the user's scoreboard is a Notion DB / Excel / Gantt /
  multi-metric dashboard. Fails 5-second + simple. The user opens
  it once, doesn't open it twice, and momentum dies in week 4.
- **Team scope** — leader rebadges a management BI dashboard (15
  panels, drill-down filters, year-over-year comparisons) as the
  "team scoreboard." It satisfies neither audience: the team can't
  glance, executives can't drill down. Most common team-leader
  failure mode.
- **Member read** — member is handed a multi-tab Notion / Tableau /
  14-page Gantt and told "that's our scoreboard." Reading produces
  fatigue, not signal. Member's "I can't read this in 5 seconds" is
  a category error in the artifact, not a member competence gap.

The **≤4 visual elements** rule is the operational test that keeps a
players' scoreboard a players' scoreboard. Typical legitimate
contents: Team WIG/lag with target line + N lead trends with target
line + (optional) delta-from-pace indicator. Anything more — supporting
data, historical comparisons, projections, status updates,
communications — drifts toward the coach's view.

## Application across modes

| Mode | How this standard applies |
|---|---|
| **Personal-design** | Step 5 of E section: hard cap ≤4 elements. If user proposes more, cut. The passive surface (sticky note, lock screen) physically constrains element count; the rule is what makes the constraint a feature. |
| **Team-lead-design** | Rule 1 of the four firm rules: ≤4 visual elements total. Team WIG + lag trend + N lead trends. No supporting data, no historical comparisons, no projections, no status updates. Leader vetoes additions during team-build. The ≤4 cap is what prevents drift toward Power BI / Tableau substitution. |
| **Member-read** | Step 2 flag: if the inherited board has 15 panels / multi-tab / drill-down filters, it is a coach's scoreboard masquerading as a players' scoreboard. Flag and surface — the failure is the leader's to fix, not the member's to compensate for. |

The standard is the same across all three modes; what differs is
*who enforces the cap* (designer / leader-plus-team / member-as-
diagnostic).
