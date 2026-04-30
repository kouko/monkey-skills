# Protocol: audit-mode — Diagnose 4DX-fit from existing artifacts

> Loaded by SKILL.md orchestrator when the user provides current-state
> artifacts (strategy doc / current methodology in use / team context /
> goal description) and asks "is 4DX right for us / me?" — typically
> with the user **NOT yet 4DX-committed**. This skill IS the gate.
> Agent voice = **diagnostic consultant**: read artifacts, apply the
> 6-verdict rubric directly, return PASS / FAIL per gate with cited
> evidence from the artifact. Distinct from coach-mode protocols
> (`personal-mode.md` / `team-mode.md`), which Socratically question
> through 6 verdicts from zero. Audit-mode here is **fit-check from
> artifact** — different in kind from D1-D4 audit-modes (which are
> within-discipline diagnosis after 4DX is already committed).

## R — Reading (verbatim source quote)

> The first mainly requires a stroke of the pen; the second is a breakthrough, requiring a change in behavior.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 1

> We cannot stress enough that the 4 Disciplines of Execution are not designed for managing your whirlwind, and they are not designed to manage stroke-of-the-pen initiatives.
>
> — *4DX* 2nd ed., Ch. 1

> The 4 Disciplines are a matched set, not a menu of choices.
>
> — *4DX* 2nd ed., Ch. 1

## I — Interpretation (mode-specific)

The user has already produced strategic artifacts — a strategy
document, an OKR sheet, a leadership-team note, an existing-process
description, a goal statement, sometimes a stakeholder critique
("boss thinks 4DX won't work for us") — and asks whether 4DX fits.
The agent's job is to **diagnose the artifact**, not Socratically
re-derive the situation.

Three things differ from coach-mode:

1. **Posture is consultant, not coach.** Output is a per-gate verdict
   table (stroke-of-pen / whirlwind / anti-pattern screen / readiness /
   matched-set) with PASS / FAIL + artifact-line citation, followed
   by a single recommended verdict from `../standards/6-verdict-rubric.md`.
   No Socratic dialogue; the artifact answers the questions.
2. **Premise is pre-commitment.** Unlike D1-D4 audit-modes, the user
   here is NOT yet 4DX-committed. The diagnostic CAN end with "no,
   use OKR / atomic habits / project management instead" as a clean
   terminal verdict.
3. **Stakeholder critique is translatable.** When a critique is
   provided ("our team is too reactive", 「うちは無理」, 「不適合」),
   translate it to which verdict it implicitly invokes — then verify
   independently against the artifact.

Voice contrast vs sibling protocols: `personal-mode.md` / `team-mode.md`
ask 6-9 Socratic questions. This protocol reads finished artifacts and
returns a structured verdict in one pass. The user is not being
coached — they are being graded.

## A1 — Past Application

### Case 1: Spartanburg Marriott — capital-doc audit re-triage
- Initial strategy artifact: "$20M renovation will fix guest
  satisfaction by FY-end." Run as audit input:
  - Stroke-of-pen check: **PARTIAL FAIL** — capital alone is
    necessary-not-sufficient; satisfaction lag stays gappy after
    physical renovation lands.
  - Behavioral-change residual: **PASS as 4DX shape** —
    front-line daily action over months is the residual gap.
  - Verdict: APPLICABLE for the *behavioral residual*; the capital
    work itself is correctly stroke-of-pen and runs in parallel.
  - Lesson: an audit can split a strategy doc into stroke-of-pen +
    4DX-shaped layers in minutes, vs an hour of Socratic re-derivation.

### Case 2: Munger / Buffett portfolio counter-example
- Berkshire's investing operation is structurally portfolio-bet:
  many candidate investments, kill criteria built into thesis,
  exploration over commitment. Run as audit input:
  - Step 4 anti-pattern screen: **portfolio-bet match** — multi-bet
    exploration with kill criteria.
  - Verdict: NOT-APPLICABLE → recommend OKR-style stretch-vs-commit
    or lean experimentation. 4DX would force premature single-WIG
    commitment on an investment that should be killable.

### Case 3: Kotter urgency-shortfall case (team artifact audit)
- Leadership-team artifact named a behavioral-change WIG ("From X
  customer-NPS to Y by EOY") with all team-shape gates passing.
  Stakeholder critique attached: "team isn't bought in." Run as audit:
  - Goal-shape: PASS. Team-shape: PASS. Matched-set: PASS.
  - Galbraith STAR: **FAIL** — bonus structure rewards quarterly
    revenue, not NPS lag.
  - Schein assumption: **FAIL** — boss's Monday request always
    overrides Friday WIG commitment in this org.
  - Verdict: TEAM-NOT-YET-READY. Fix incentives + assumption layer
    BEFORE installation; otherwise installs only on artifacts level.

## A2 — Future Trigger

When a user would need this protocol:

1. User pastes strategy doc / leadership-team note / annual plan and
   asks "is 4DX right for us?"
2. User describes current methodology (OKR, MBO, status-quo) + a goal
   and asks for a fit comparison.
3. User provides team context (size, role, charter) + a goal artifact
   and asks for diagnosis without Socratic walk-through.
4. Stakeholder critique ("boss says 4DX won't work", 「上司が反対」,
   「老闆覺得不合適」) attached to artifact — user wants the critique
   translated into 4DX rule terms.
5. User has read the book and wants a defensible written verdict for
   their team / boss / themselves, with cited evidence from the
   artifact, not a coaching transcript.

EN: "Audit whether 4DX fits our team given this strategy doc",
"Boss says 4DX won't work for us — diagnose", "Here's our annual plan,
is 4DX the right operating system?"

JP: 「うちの 4DX 適合性を診断して」「会社の状況見て 4DX 合うか判定」
「この戦略 doc で 4DX 使えるか audit して」

zh-TW: 「幫我看 4DX 適不適合我們團隊」「策略 doc 在這，4DX 適合我們嗎？」
「老闆說 4DX 不行，幫我診斷」

## E — Execution

When this protocol activates, the agent runs a structured fit-check
from the artifact. **Do not Socratically re-derive — diagnose, then
recommend a single verdict from the rubric.**

1. **Read the artifact(s).**
   - Extract scope (solo / team-leader), goal statement, current
     methodology (if named), team size + role (if team-mode), and
     any explicit X / Y / When the artifact already commits to.
   - Mark missing fields ABSENT — do not invent values. If the
     artifact is too thin to extract scope, ask ONE clarification
     before proceeding (then resume the audit, not Socratic mode).

2. **Read stakeholder critique (if provided).**
   - Note the verbatim complaint. Hold it aside for Step 6 — the
     gate-check runs first unbiased, then the critique gets mapped.

3. **Apply the 6-verdict rubric directly** — see
   `../standards/6-verdict-rubric.md`. Per artifact, run each gate
   and issue PASS / FAIL / N/A with one-line evidence cite from the
   artifact:
   - **Stroke-of-pen check** — see
     `../standards/stroke-of-pen-vs-behavior-change.md`. Does a
     single decision / hire / contract / rule change deliver the
     goal? FAIL → return verdict **stroke-of-the-pen, 4DX overkill**.
   - **Whirlwind-handleable check.** Does sharper execution of
     existing routine suffice? FAIL → return verdict
     **whirlwind-handleable**.
   - **Anti-pattern screen** (solo: habit / portfolio-bet / emergency
     / creative; team: wrong-team-shape size / firefighting / no-time
     -authority / single-shot / mission-misaligned). Match → return
     the matching redirect verdict.
   - **Time-sovereignty / time-authority** — see
     `../standards/readiness-preconditions.md`. ~20% slot
     carvable? FAIL → **no-time-sovereignty** (solo) /
     **no-time-authority** (team).
   - **Matched-set capacity (P-23).** Artifact commits to all four
     disciplines? FAIL → flag; recommend lighter framework.

4. **Apply readiness preconditions (team-mode only)** — see
   `../standards/readiness-preconditions.md`:
   - Kotter urgency: artifact evidence of team urgency on the goal?
   - Galbraith STAR: incentive system reward whirlwind or WIG?
   - Schein assumption: boss-request vs WIG-commitment, which wins?
   - Any FAIL → return **TEAM-NOT-YET-READY**.

5. **Stroke-of-pen vs behavior-change synthesis.** Does the goal
   need behavior change at all, or just authority? Cite the artifact
   line that made you decide. This is the strongest filter (CE-06).

6. **Map stakeholder critique to a verdict.**
   - "Too reactive" / 「忙しすぎる」/「太忙」 → emergency-role or
     wrong-team-shape (firefighting).
   - "Won't stick" / 「続かない」/「持續不了」 → matched-set FAIL or
     TEAM-NOT-YET-READY (Schein).
   - "Too rigid" / 「固すぎる」/「太死板」 → portfolio-bet (need OKR
     kill criteria) or single-shot-project.
   - "Too small to bother" / 「大げさ」/「小題大作」 → habit-formation.
   - Cite the rubric verdict + artifact evidence so the user can
     bring the diagnosis back to the stakeholder.

7. **Recommend verdict + next-step.**
   - Output exactly one verdict from the rubric.
   - For APPLICABLE / TEAM-APPLICABLE → next step is
     `4dx-d1-wig-formulation` (often via
     `4dx-meta-team-leader-onboarding` for team-mode).
   - For redirects → next step is the alternative framework (OKR /
     atomic-habits / project management / readiness-fix-first).
   - Surface any artifact gap as "needs input" rather than inventing.

8. **Offer route.**
   - "If you want a guided Socratic triage instead of artifact audit,
     run coach-mode: `personal-mode` for solo, `team-mode` for
     team-leader."
   - "If 4DX is already committed and you want within-discipline
     audit (WIG / lead / scoreboard / cadence), route to `4dx-audit`
     (full-stack)."

### Output format (audit card)

```markdown
# 4DX Fit Audit — [scope: solo / team-leader]

## Artifact summary
> [extracted goal / team / current method, verbatim where possible]

## Stakeholder critique (if provided)
> [verbatim complaint] → maps to **[rubric verdict]**

## Gate-check
| Gate | Verdict | Evidence (artifact line) |
|---|---|---|
| Stroke-of-pen | PASS / FAIL | … |
| Whirlwind-handleable | PASS / FAIL | … |
| Anti-pattern screen | PASS / [match] | … |
| Time sovereignty / authority | PASS / FAIL | … |
| Matched-set capacity (P-23) | PASS / FAIL | … |
| Readiness (Kotter / Galbraith / Schein) [team only] | PASS / FAIL | … |

## Verdict
**[one of: APPLICABLE / TEAM-APPLICABLE / stroke-of-the-pen /
whirlwind-handleable / habit-formation / portfolio-bet /
emergency-role / creative-output / no-time-sovereignty /
wrong-team-shape (size) / wrong-team-shape (firefighting) /
no-time-authority / single-shot-project / mission-misaligned /
TEAM-NOT-YET-READY]**

## Recommended next step
- …

## Artifact gaps to confirm
- …
```

## B — Boundary (mode-specific)

### Do NOT use this protocol for:
- **Cold-start without artifact** — no strategy doc, no goal
  statement, no team context → coach-mode (`personal-mode.md` /
  `team-mode.md`).
- **User already committed to 4DX** — skip the fit-check entirely;
  route to `4dx-d1-wig-formulation`.
- **Cross-layer audit when 4DX is already chosen** — within-discipline
  diagnosis (WIG / lead / scoreboard / cadence / substrate) → use
  `4dx-audit` (full-stack), not this protocol.
- **Member receiving inherited WIG** — members don't triage
  methodology fit; route to `4dx-d1-wig-formulation`.
- **Pure venting** — "boss is unreasonable" without artifact → not
  this skill.

### Author-warned failure modes
- **Verdict-without-evidence** — every gate verdict must cite the
  artifact line. "FAIL because it sounds reactive" is not evidence;
  "FAIL — artifact line 'team handles all P0/P1 incidents 24x7' →
  emergency-role" is.
- **Inventing values** — when X / Y / When / team size are absent,
  mark them ABSENT under "artifact gaps" rather than silently
  inferring. The audit's defensibility depends on artifact-grounding.
- **Coaching drift** — if the agent slips into "what would
  transformation look like for you?" Socratic mode, stop, return
  to the gate table. Audit is artifact-bound, not dialogue-driven.
- **CE-06 — Stroke-of-the-pen miscategorization.** Strongest filter;
  authority alone often suffices. Probe the artifact for "single
  decision the leader controls" before granting APPLICABLE.
- **CE-26 — Whirlwind-as-strategic-work.** When artifact describes
  reactive primary purpose (ER, on-call, frontline support), the
  whirlwind IS strategic value; 4DX inverts wrong.
- **CE-30 — FranklinCovey selection bias.** Don't grant APPLICABLE
  by analogy to Marriott / Comcast / Beverly Walker case studies;
  audit the artifact, not the cousin.

### Easily-confused neighbours
- **`personal-mode.md` / `team-mode.md`** (coach-mode) — Socratic
  from zero; this protocol is consultant on existing artifact.
- **`4dx-audit` (full-stack)** — covers all 5 layers post-4DX-commit;
  this protocol gates pre-commit.
- **D1-D4 audit-mode protocols** — within-discipline diagnosis
  assuming 4DX-committed; this protocol IS the fit gate.

## Standards used

- `../standards/6-verdict-rubric.md` — verdict taxonomy (solo + team
  labels)
- `../standards/stroke-of-pen-vs-behavior-change.md` — Step 3
  stroke-of-pen check + Step 5 synthesis
- `../standards/readiness-preconditions.md` — Step 4 Kotter /
  Galbraith / Schein layered checks (team-mode)

## References

See `../references/industry-grounding.md` sections **Kotter**
(urgency upstream of execution; Stage 1 audit for TEAM-NOT-YET-READY),
**Galbraith** (STAR Strategy / Structure / Processes / Rewards /
People — incentive-conflict diagnosis from artifacts), **Schein**
(Artifacts / Espoused Values / Underlying Assumptions — methodology
touches only Artifacts; assumption layer wins silently), **Rumelt**
(*Good Strategy / Bad Strategy* — kernel-of-strategy diagnosis frame
for artifact reading).
