# Protocol: Audit-mode — Diagnose an existing D3 scoreboard

> Loaded by SKILL.md orchestrator when the user has an **existing
> scoreboard / dashboard / tracker** and asks for a diagnosis or
> revision recommendations — not a from-scratch coach session. Voice =
> consultant-to-user. Single-layer (D3 only); 4DX-committed. Output =
> audit report keyed to the three D3 standards, per-element disposition,
> and a minimum-viable redesign — not a Socratic dialogue.

## R — Reading

> If you can't tell within five seconds whether you're winning or losing, you haven't passed this test.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 4 (criterion 4)

## I — Interpretation

The user has a board. They (or a stakeholder) think it's not working.
The audit's job is **not** to redesign from zero — that's coach-mode.
The job is to diagnose the artifact against the three D3 standards
(5-second test, players'-vs-coaches', ≤4-elements / lead-lag-pacing),
translate stakeholder critique into the test it implicitly invokes,
and recommend per-element disposition (KEEP / DROP / RESTYLE) plus a
minimum-viable redesign.

The non-obvious move is **mapping the user's complaint to the test it
invokes**. "Nobody looks at it" is almost never a discipline problem;
it is one of (a) 5-second-test fail, (b) coaches'-board form, or (c)
hidden / non-passive surface. Naming the underlying test makes the
fix actionable; leaving it as "engagement problem" makes it a culture
lecture.

## A1 — Past Application (audit-shaped on book cases)

- **Northrop Grumman (Ch 14)** — Coast Guard cutter team had a 14-page
  Gantt as their "scoreboard". Audit verdicts: 5-second-test FAIL by
  absence of a winning indicator; coaches' form (analytic); pacing
  line absent. Disposition: DROP Gantt-as-scoreboard framing; ADD a
  separate one-glance lead+lag+pacing artifact alongside (Gantt for
  analysis, scoreboard for engagement coexist).
- **Marriott / hotel front-desk (Ch 14)** — leader-built multi-KPI
  dashboard in back office; team treats it as "management's".
  Critique mapping: "not theirs" → coaches' form + ownership collapse.
  Disposition: KEEP lag metric; DROP supporting KPIs; RESTYLE for
  glance-readability; relocate public; team rebuilds + owns updates.
- **CNRL Canadian plant (Ch 4)** — quality-74 management report,
  invisible to operators. Verdicts: 5-second-test FAIL (audience
  can't read it); coaches' form (audience mismatch). Disposition:
  REPLACE with shift-vs-shift visible boards. Same data, different
  artifact form; quality climbed to 94.

The pattern: artifact-shape + stakeholder critique → which test fails
→ per-element disposition. No invented from-scratch design.

## A2 — Future Trigger

When a user needs this protocol:

1. User describes / pastes / uploads an existing scoreboard, dashboard,
   tracker, or wall artifact AND asks for a 4DX-framed diagnosis.
2. User reports a stakeholder complaint about an existing board.
3. User wants someone to tell them what to KEEP / DROP / RESTYLE
   without rebuilding from zero.

EN: "Audit our scoreboard", "Team doesn't look at the scoreboard",
"Boss says our dashboard isn't useful"
JP: 「うちの scoreboard 誰も見てない、診断して」「dashboard を 4DX
視点で見て」
zh-TW: 「scoreboard 沒人看，幫我看哪裡有問題」「我們的 dashboard
老闆說沒用」

## E — Execution

Voice = **consultant-to-user**. Run a structured 9-step audit; output
is a written diagnosis + disposition table, not a dialogue.

1. **Read the scoreboard artifact.** Inventory every visual element
   (image description / element list / dashboard URL description /
   screenshot prose / paste). If only a vague description, ask ONCE
   for the element list; do not invent content.

2. **Read stakeholder / team critique if provided.** Capture verbatim
   ("nobody looks", "too complex", "boss says no signal"). If no
   critique, proceed with structural audit only and note the limit.

3. **5-second test simulation.** — see `../standards/5-second-test.md`
   Imagine a stranger walking past. Could they answer "are we
   winning?" in 5 seconds? PASS / FAIL. Cite mechanism if FAIL:
   text/numerics-only encoding (Ware), low data-ink ratio (Tufte),
   purpose-mixed (Few). Sharpest gate; record verdict explicitly.

4. **≤4 elements rule audit.** — see `../standards/players-vs-coaches-board.md`
   Count elements present. Categorize each as **essential** (lag
   trend with pacing, lead trend(s) with target, optional delta) or
   **decorative / coach's-data** (logos, supporting KPIs, drill-down
   filters, projections, status updates, historical comparisons).

5. **Players'-vs-coaches' diagnosis.** — see `../standards/players-vs-coaches-board.md`
   Does the board engage players (motivational, simple, public) or
   analyze for coaches (data-rich, drill-down, back-office)? Cite
   signs: location, audience, update mechanism (manual-by-team vs
   auto-feed), element density.

6. **Lead-lag-pacing structure audit.** — see `../standards/lead-lag-pacing-elements.md`
   For each slot (lag trend / lead trend / pacing line / optional
   delta) record present / absent / wrong-shape. Pacing line is
   **mandatory**; flag explicitly if missing.

7. **Map stakeholder critique to invoked test.**
   - "Nobody looks" → 5-second-test fail OR coaches'-board form OR
     hidden surface (engagement collapse). Name which.
   - "Too complex" → ≤4 elements violation + coaches' form.
   - "Boss says no signal" → pacing line missing OR lag-without-lead.
   - "Treats it as management's" → coaches' form + ownership collapse.
   - "Looks like an Excel report" → coaches' form + Tufte data-ink
     violation.

   State the mapping explicitly so the fix is actionable.

8. **Per-element disposition + minimum-viable redesign.** For each
   element: **KEEP** (essential, well-formed) / **DROP** (decorative
   or coach's-data) / **RESTYLE** (right content, wrong visual
   encoding). Output a minimum-viable redesign: ≤4 elements, lag with
   pacing, 1-3 leads with targets, optional delta. State exactly what
   the revised board contains and what was removed.

9. **Offer route.** "If you want to rebuild from scratch with team
   buy-in, run coach-mode (`personal-design.md` solo /
   `team-lead-design.md` team). For redesigning *this* scoreboard,
   the recommendations above suffice." If the diagnosis revealed
   cross-discipline issues (WIG malformed, cadence collapsed), name
   them and route to `4dx-audit` or
   `4dx-sustain-momentum-rescue`.

### Output format

```markdown
# D3 Scoreboard Audit — [board label]

## Inventory
- [elements observed]

## Stakeholder critique (if provided)
- "[verbatim]"

## Test verdicts
| Test | Verdict | Finding |
|---|---|---|
| 5-second test | PASS / FAIL | [mechanism] |
| ≤4 elements | PASS / FAIL ([count]) | [essential vs decorative] |
| Players'-vs-coaches' | players' / coaches' | [signs] |
| Lead-lag-pacing | [present/absent per slot] | [pacing state] |

## Critique mapping
- "[quote]" → [test invoked]

## Per-element disposition
| Element | KEEP/DROP/RESTYLE | Reason |

## Minimum-viable redesign
- Lag / Lead(s) / Pacing / (Delta)

## Route
[coach-mode / 4dx-audit / sustain-rescue]
```

## B — Boundary

### Do NOT use this protocol for:

- **First-time scoreboard design without an existing artifact** —
  load `personal-design.md` (solo) or `team-lead-design.md` (team).
- **Cross-layer / cross-discipline audit** (WIG + leads + scoreboard +
  cadence + substrate) — load `4dx-audit`.
- **Member reading an inherited board** (just reading, not auditing
  for redesign) — load `member-read.md`; member doesn't own redesign.
- **BI / KPI dashboard audit without 4DX framing** (Tableau / Power BI
  quality review without 4DX commitment) — out of 4DX; hand off via
  `using-four-dx-coach`.
- **"Scoreboard ignored" as stalled-cadence symptom** — when user
  says "hasn't moved in a month / nobody updates / WIG Sessions
  stopped", the diagnosis is whole-stack collapse, not board-shape
  failure → `4dx-sustain-momentum-rescue`. Audit-mode assumes the
  board is the unit of analysis; rescue assumes the cadence is.

### Author-warned failure modes

- **Audit-as-redesign-from-zero** — easy to slide into Socratic
  rebuild; resist. The audit produces dispositions on the existing
  artifact. If user wants from-zero, route to coach-mode and exit.
- **Critique-laundering** — accepting "nobody looks at it" as the
  diagnosis. The stakeholder named a symptom; the audit names the
  test invoked. Don't echo back the symptom.
- **Forced-fit dispositions** — not every element fits KEEP / DROP /
  RESTYLE cleanly. If the artifact is a Gantt-as-scoreboard or
  category-error (BSC map), say so and route to from-scratch.
- **Single-snapshot bias** — audit reads what's described; if user
  provides only a static snapshot, can't see update cadence / team
  interaction / stale-pacing-line. Note explicitly when data-limited.
- **Cross-discipline drift** — if audit reveals WIG malformed or
  cadence collapsed, name it and route; don't expand this protocol
  into a 5-layer audit (that's `4dx-audit`).

### Easily-confused neighbours

- **`4dx-audit`** — cross-discipline synthesis across all 5 layers.
- **`4dx-sustain-momentum-rescue`** — whole-stack collapse including
  scoreboard-as-symptom.
- **`member-read`** — member reading inherited board for personal
  contribution + escalation; this protocol is for users who can act
  on the redesign.

## Standards used

- `../standards/5-second-test.md` — Step 3 simulation
- `../standards/players-vs-coaches-board.md` — Steps 4 + 5
- `../standards/lead-lag-pacing-elements.md` — Step 6

## References

See `../references/industry-grounding.md` sections **Tufte** (data-ink
+ chartjunk), **Few** (dashboard-vs-database), **Ware**
(pre-attentive processing) for the perception science behind the
5-second-test failure mechanisms.
