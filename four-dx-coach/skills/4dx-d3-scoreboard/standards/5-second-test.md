# Standard: 5-second test — glance-readable in five seconds

## Statement

A players' scoreboard must let any glancing observer answer **"are
we winning?"** within **five seconds**. The test is binary: pass or
fail; "kind of" is fail. Applies to design (the artifact must pass)
and to reading (member's diagnostic flag if the artifact fails for
them). The test is the **single sharpest gate** in D3 across all
three scopes.

## Source

> The fourth and most important characteristic of a great players' scoreboard is that you can tell quickly whether you're winning or losing. Specifically, if you can't tell within five seconds whether you're winning or losing, you haven't passed this test.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 4 (Characteristics of a Compelling Players' Scoreboard, criterion 4)

## Why it matters

The test sits on a 40-year information-design literature that names
the perception mechanism the book asserts without derivation —
primary citations consolidated in `references/industry-grounding.md`:

- **Tufte (1983 / 2001), *The Visual Display of Quantitative
  Information*** — *data-ink ratio* + *chartjunk*. Decoration that
  lowers the ratio (gradients, 3D, ornamental gridlines, themed
  icons) delays the eye's path to the trend by hundreds of
  milliseconds; compounds over a 6-month cadence into a material
  reduction in scoreboard usage.
- **Few (2006 / 2013), *Information Dashboard Design*** — dashboards
  (single-screen at-a-glance monitoring) vs databases / reports
  (drill-down analytical artifacts). Mixing them produces an
  artifact that fails both. The 5-second test is Few's
  glance-monitoring criterion in behavioral form.
- **Ware (2012), *Information Visualization: Perception for Design***
  — pre-attentive processing operates in ~200 ms via position /
  length / limited-palette hue. Numbers and text labels require
  focal attention and **cannot** be glanced. A scoreboard whose
  state is encoded only in numeric digits or text labels cannot
  pass the test no matter how "compelling" its decoration is.

The test thus has three operational checks behind it:

1. **Tufte data-ink check** — is the lag-trend the most prominent
   ink? Are decorations stripped to minimum?
2. **Few purpose check** — single-screen, glance-monitoring, no
   drill-down on this artifact?
3. **Ware pre-attentive encoding check** — lead, lag, pacing
   encoded via position / length / limited-palette hue, not text or
   numerics alone?

A scoreboard that fails any of the three will be checked once on
day 1, twice in week 1, and ignored by week 4 — exactly the failure
curve the book attributes to "lack of compelling design" without
naming the perception mechanism.

## Application across modes

| Mode | How this standard applies |
|---|---|
| **Personal-design** | Step 5 of E section runs the test cold on the user. If user hesitates ("kind of"), simplify (cut elements, enlarge winning indicator, add color or position cue), then re-test. Hard cap ≤4 elements. |
| **Team-lead-design** | Rule 4 of the four firm rules the leader holds during the team-build session. A teammate or stranger walking past must answer in 5 seconds. Cross-role legibility check before locking: each functional sub-group glances and reports — divergent answers mean decoration is doing the divergent work; cut it. |
| **Member-read** | Step 2 of E section. Member glances at the existing board *now* and answers in 5 seconds. If "I can't tell," flag as **scoreboard-fails-5-second-test** — the failure is data about the artifact, not member competence. Surface via step 6a Model-II script. |

Across all three modes, the test is the same: 5 seconds, binary,
pass or fail. What differs is *who applies it* (designer / leader-
plus-team / member to themselves) and *what action follows the fail*
(redesign / veto / surface).
