# Standard: Lead + lag + pacing — the ≤4 elements and what each shows

## Statement

A players' scoreboard renders the team's bet in **≤4 visual
elements**, each carrying a specific job:

1. **Lag measure trend** — the WIG outcome over time, with **target
   line** ("where we should be by today" / the goat / pacing line
   on the lag).
2. **Lead measure trend(s)** — one per chosen lead (typically 1-2
   for solo, 2-3 for team), each with its own **standard / target
   line** (e.g. 90% sustained line, weekly tick).
3. **Pacing line / where-you-should-be marker** on the lag — the
   non-obvious mandatory element. **Status without trajectory is
   data, not a scoreboard.**
4. (Optional) **Delta-from-pace** indicator — single number or
   color cue showing ahead / on-pace / behind.

The pacing line is the visual signature that distinguishes a players'
scoreboard from a progress bar, a fitness ring, or a habit grid.
Bare progress without a target marker fails D3 by the same mechanism
in all three scopes.

## Source

> A players' scoreboard … shows lead AND lag measures. … It must show both where they are and where they should be — within five seconds.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 4 (Compelling Players' Scoreboard, criteria 3 + 4)

> The board needs a clear "where we should be by now" line — without it, the players see status but not trajectory.
>
> — *4DX* 2nd ed., Ch. 14 (Applying D3, Step 2 — Design)

## Why it matters

The pacing line is what turns a static state display into a motion-
vs-static visual that triggers the **want-to-win** affect. Without
it, three failure modes flow:

1. **Status-without-trajectory (CE-09)** — user / team can see
   where they are, but not whether that's winning. Common with
   progress bars without target ticks, fitness rings without weekly
   goals, habit grids without pacing lines.
2. **Lead without lag** — board shows daily lead activity but never
   the WIG outcome. Team executes the lead religiously and never
   sees whether the bet is paying off.
3. **Lag without lead** — board shows the WIG outcome but no
   leading indicator. Team has no week-to-week steering signal; by
   the time the lag moves it's too late to adjust.

The ≤4 elements cap (cross-ref `players-vs-coaches-board.md`) is
the structural enforcement; the lead+lag+pacing combination is the
**content** rule. Both have to hold for D3 to function.

For a knowledge-work team where the lead requires per-person tracking
(per Serena Lead 1: "2 quality site visits per associate per
week"), the per-person breakdown counts as one element of the lead
trend, not as 6 separate elements — the gestalt is "the lead trend,
broken down."

## Application across modes

| Mode | How this standard applies |
|---|---|
| **Personal-design** | Steps 3 and 4 of E section. Step 3 picks the lead viz (weekly bar / streak / checkbox grid / cumulative count). Step 4 designs the lag with where-you-should-be line — pacing marker is **mandatory**. User must point to "where I am" AND "where I should be by today" on the design before step 5 (5-second test). |
| **Team-lead-design** | Rule 3 of the four firm rules: WIG/lag must show "where we should be by today" line; each lead must show its standard. Per-person breakdown if the lead requires individual tracking. Leader vetoes any board missing target lines on lag or leads. |
| **Member-read** | Steps 4 and 5 of E section. Step 4 reads the trend per focus lead (up / flat / down; on / off pace) — the pacing line is what makes "on / off pace" answerable. Step 5 calibration check: has the pacing line gone stale relative to current reality (headcount changed, baseline superseded, lead definition drifted)? Member flags as calibration-drift; leader fixes. |

The standard is the same across all three modes; what differs is
*who renders / vetoes / reads* the elements.
