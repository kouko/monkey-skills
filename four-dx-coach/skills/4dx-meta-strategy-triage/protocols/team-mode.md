# Protocol: Team-leader — Triage 4DX-fit for adopting in a team (3-12 reports)

> Loaded by SKILL.md orchestrator when scope detection identifies a team
> leader judging whether to adopt 4DX across their team — the agent acts
> as consultant to the leader.

## R — Reading (verbatim source quote)

> The first mainly requires a stroke of the pen; the second is a breakthrough, requiring a change in behavior.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 1

> The 4 Disciplines are a matched set, not a menu of choices.
>
> — *4DX* 2nd ed., Ch. 1

> Begin by populating the left and right sections of the Strategy Map with the stroke-of-the-pen aspects … as well as the key metrics of your whirlwind.
>
> — *4DX* 2nd ed., Ch. 6 (Choosing Where to Focus)

## I — Interpretation (mode-specific)

Before a team leader installs 4DX, two questions: (1) is the team's
headline goal a 4DX-shaped problem? (2) is the team the right shape to
run all four disciplines together?

The three-bucket triage carries to team scope. **Stroke-of-pen** =
leader's own authority delivers (sign contract / hire / change rule).
**Whirlwind** = team's existing work a bit better. **Behavioral-change**
= many people sustain new daily practices for months — only this needs
4DX. The Strategy Map (Ch 6) carves visually: left = stroke-of-pen,
right = whirlwind, middle = behavioral-change zone where Primary WIG
lives.

Team scope adds gates the personal version doesn't have: firefighting
roles where reactive IS strategic (ER, frontline support, on-call SRE);
teams <3 (no peer accountability) or >12 (cadence becomes report-out
theater); leader has no authority to carve protected WIG time;
single-shot fixed-plan projects (PM beats continuous-cadence OS);
candidate WIGs violating mission/vision (P-45 veto). Three additional
change-readiness preconditions (Kotter urgency / Galbraith STAR /
Schein assumption-fit) gate the TEAM-NOT-YET-READY variant.

Voice contrast vs sibling: personal-mode IS the coach for one user; this
protocol is consultant *to* a leader who runs a team.

## A1 — Past Application

### Case 1: Spartanburg Marriott — capital alone failed
$20M renovation + capital approval insufficient; residual gap required
front-line teams (housekeeping, front desk, F&B) to change daily
behaviors over months. Triaged behavioral-change; installed all four
disciplines across team layers. Outcome: breakthrough satisfaction;
flagship example, seeded 70K-Marriott-leader rollout.

### Case 2: Beverly Walker — Georgia child welfare (mission-critical, scaled)
Repeat child-abuse cases flat across ~20K caseworkers despite reorgs
and policy. Walker recognized residual gap was structural behavior
change across many small teams. Reframed as 4DX-shaped (home-visit
protocols, follow-up cadence). Outcome: repeat cases declined; proof
point that team-scope triage is domain-agnostic.

### Case 3: Comcast Greater Chicago — last-to-first turnaround
Division ranked last in customer experience for years despite reorgs,
training, scripts. Stroke-of-pen levers exhausted; residual gap
behavioral across hundreds of frontline-team installations. Each got
Team WIG, lead measures, scoreboard, weekly Session. Outcome: worst to
best; team-triage holds even in overworked operational settings when
shape gates clear.

## A2 — Future Trigger

When a team leader would need this protocol:

1. **Pre-rollout sanity check** — leader has read the book or attended a workshop and is deciding whether to spend a quarter installing 4DX.
2. **OKR-fatigue rebound** — team tried OKRs / quarterly goals / a balanced scorecard and lost steam; reaching for 4DX as the next thing, may again be a wrong-shape fit.
3. **Annual-planning fork** — leader has a list of annual targets and is choosing operating cadence (4DX vs PM vs OKR vs status-quo).
4. **Methodology-evangelism resistance** — leader's boss or peer is pushing 4DX; leader wants a defensible "yes / no / not yet" rooted in the book's own scope rules.
5. **Post-fail re-triage** — team installed 4DX and stalled at month 2-3; leader wonders whether the fit was wrong from day one.

EN signal: "Should our team adopt 4DX?", "Will 4DX work for my team?", "Is my team ready for 4DX?"
JP: 「私たちのチームに 4DX 合うか？」「うちのチームで 4DX 効くかな」
zh-TW: 「我們團隊適合導入 4DX 嗎？」「我這個團隊用 4DX 有用嗎？」

## E — Execution

The agent acts as **consultant to the leader**. Each step asks the leader a
clarifying question about THEIR team — not about the leader as an
individual. Verdicts come from `../standards/6-verdict-rubric.md`.

1. **Surface the team and the candidate goal.**
   - Ask: *"How many people on the team, and what's the headline outcome you're trying to drive over the next 6-12 months? One sentence."*
   - Completion: leader has named team size + a goal explicit enough to classify. If goal is vague, follow up: *"What would 'improved' look like in measurable terms by when?"*

2. **Stroke-of-the-pen check** (Ch 1 + Ch 6 Strategy Map left column) — see `../standards/stroke-of-pen-vs-behavior-change.md`.
   - Ask: *"Is there a single decision YOU control — a contract to sign, a hire to make, a tool to buy, a rule to change — that by itself would deliver this outcome? Or does it require many people on your team to sustain new daily practices for months?"*
   - Completion: {single-decision / sustained-team-behavior / unsure}.
   - **Halt**: if single-decision → return verdict **stroke-of-the-pen, 4DX overkill** (e.g. "if it's 'replace the legacy CRM' — sign the contract; 4DX would be ceremony"). Skill ends.

3. **Whirlwind-handleable check** (Ch 6 Strategy Map right column).
   - Ask: *"Could the team hit this just by doing its existing work a bit better — sharper execution of the same routine, no new categories of action, no new daily practice?"*
   - Completion: yes/no.
   - **Halt**: if yes → return verdict **whirlwind-handleable, 4DX overkill** ("optimize the existing flow; pull the lever you have"). Skill ends.

4. **Team-shape screen** (the four team-scope traps).
   - Ask each in turn, only as relevant:
     - *"How many people report to you on this team — directly?"* → if <3 (no peer accountability) or >12 (WIG Session devolves to report-out), return verdict **wrong-team-shape (size out of 3-12)** with split / consolidate recommendation.
     - *"Is your team's primary purpose reactive — handling whatever comes in (incident response, customer support, ER, on-call)? Or is it proactive — pursuing an outcome?"* → if reactive-primary, return verdict **wrong-team-shape (firefighting role)** — the whirlwind IS your team's strategic value; 4DX inverts wrong. Tighten reactive-quality metrics instead.
     - *"Do you, as the leader, have the authority to carve out protected WIG time on the team's calendar — block ~20% of capacity from incoming demands?"* → if no, return verdict **no-time-authority** — fix the upstream demand-protection problem first.
     - *"Is this work a single-shot project with a fixed end-state and a known plan (build X, deliver, done)? Or an ongoing capability the team is building?"* → if single-shot fixed-plan, return verdict **single-shot-project — use project management not 4DX**.
   - Completion: each gate explicitly checked and either matched (skill ends with redirect) or cleared.

5. **WIG-shape check — From X to Y by When (P-30, P-45 mission-vision veto).**
   - Ask: *"Can the goal be expressed as 'from X to Y by when'? And does pursuing it support your team's stated mission and vision — would your boss and your team's senior leadership endorse it as on-mission?"*
   - Completion: leader either produces a draft From-X-to-Y-by-When that aligns to mission, or admits one or both gates fail.
   - **Halt**: if cannot express as From-X-to-Y-by-When → recurring service delivery without a transformative target; 4DX has no entry point. If WIG conflicts with mission/vision → return verdict **mission-misaligned** (P-45 hard rule).

6. **Adoption-curve readiness check (F-28 Models / Not Yets / Nevers).**
   - Ask: *"Of your team, who would you classify as Models (already disciplined when given a clear target), Not Yets (capable but inconsistent), Nevers (won't engage no matter what)? Roughly what's the split?"*
   - Completion: rough split (e.g. 3 / 4 / 1).
   - **Halt**: if Nevers majority or no Models, surface the risk — 4DX rollout will degrade to compliance theater. Recommend addressing the team-composition problem before installing the methodology.

7. **Change-readiness preconditions** — see `../standards/readiness-preconditions.md`.
   - Three layered checks (Kotter / Galbraith / Schein):
     - *"Is the **team's** sense of urgency on this WIG at least as high as your own?"* (Kotter Stage 1) — if no, fix urgency first; non-urgent team produces Friday ceremony.
     - *"Do existing performance reviews and bonuses reward whirlwind firefighting more than WIG progress?"* (Galbraith STAR — Reward lever) — if yes, the incentive system defeats the WIG within a quarter.
     - *"When a member's Friday WIG commitment conflicts with their boss's Monday request, which actually wins?"* (Schein assumption layer) — if boss-request always wins, the assumption is "compliance over commitment"; methodology installs only on Artifacts level, assumption wins silently.
   - **Halt**: if any of the three fails → return verdict **TEAM-NOT-YET-READY** (variant of mission-misaligned for change-readiness gap) — fix urgency, incentives, or assumption-alignment first.

8. **Matched-set commitment (P-23 hard rule).**
   - Ask: *"4DX is all four disciplines or none — a Primary / Team WIG, daily lead measures, a visible weekly scoreboard, and a 20-30 min weekly WIG Session you personally lead with member commitments. Are you in for all four, sustained, for at least one quarter?"*
   - Completion: leader explicitly says yes / no.
   - **Halt**: if leader wants to cherry-pick → flag P-23 (matched set, not menu) and offer either commit-to-all-four or use a lighter framework instead.

9. **Verdict + handoff.**
   - If all gates passed → return verdict **TEAM-APPLICABLE — proceed to `4dx-d1-wig-formulation`** (often via `4dx-meta-team-leader-onboarding` first).
   - In all other branches the redirect verdict is the output; do not bend the team-shape back into 4DX.
   - Completion: a single verdict has been issued from the rubric.

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **Solo / individual-contributor goals** — load `protocols/personal-mode.md` instead. The team-shape gates (size 3-12, peer accountability, leader authority) are nonsensical for one person.
- **Already-committed teams asking how to start D1** — route to `4dx-d1-wig-formulation` and `4dx-d1-team-wig-cascade`; don't re-gate work past this stage.
- **Leader-of-Leaders multi-team rollout** — single-team scope only. For VPs / division leads cascading 4DX across multiple teams, recommend book Ch 6-10 + `4dx-d1-team-wig-cascade` once each team is scoped.
- **Specific-discipline questions** ("how do we pick lead measures?", "what goes on the scoreboard?") — route to the matching D-skill.

### Author-warned failure modes

- **CE-06 — Stroke-of-pen miscategorization.** Leader authority often suffices; strongest scope warning. Probe "single decision the leader can make?" — leaders default to elaborate methodology.
- **CE-25 — Wrong-WIG-locked-in (no kill criteria).** No built-in mechanism to detect WIG is wrong; exploratory teams burn 6-month cycles. If genuinely betting, OKR stretch-vs-commit gives kill criteria.
- **CE-26 — Whirlwind-as-strategic-work.** Reactive teams (ER, frontline support, on-call SRE, NOC) — whirlwind IS strategic value; 20% sub-WIG inverts the role.
- **CE-27 — Knowledge-work feedback too long.** Drug discovery, hardware, deep-research = multi-month loops; weekly cadence theatrical.
- **CE-30 — FranklinCovey selection bias.** All case studies are paying clients; failures anecdotal. Don't assume "4DX worked at Marriott so it'll work here".

### Author's blind spots

- US-anglophone-corporate dominant; knowledge-work / R&D / creative under-represented.
- "Public peer commitment" assumes low-context culture. JP / ZH / KR public accountability can read as face-loss; book offers no adaptation.
- Pre-dates remote-default work; in-person social pressure was original active ingredient.
- Team-size bands (3-12) from worked examples + practice, not controlled study. Strong heuristic, not hard cutoff.

### Easily-confused neighbors

- **OKR** (Doerr) — team-scale, From-X-to-Y; differs by (a) stretch-vs-commit kill criteria 4DX lacks; (b) quarterly grading replaces weekly cadence; (c) less lead-measure / weekly-ritual emphasis. Use OKR for portfolio / discovery mode.
- **Project management (PMI / Agile / Gantt)** — single-shot fixed-plan deliverables; 4DX overhead when there's a finite task list.
- **Balanced Scorecard / KPI dashboards** (Kaplan & Norton) — steady-state monitoring; no narrowing-to-one-WIG.
- **Personal 4DX triage** (`personal-mode.md`) — solo scope; missing team-shape gates.

## Standards used

- `../standards/6-verdict-rubric.md` — the 6-verdict rubric (team labels) + TEAM-NOT-YET-READY variant
- `../standards/stroke-of-pen-vs-behavior-change.md` — Step 2 + Step 3 foundation
- `../standards/readiness-preconditions.md` — Step 7 Kotter / Galbraith / Schein layered checks

## References

See `../references/industry-grounding.md` sections **Kotter** (Stage 1
urgency + Stage 2 guiding coalition), **Galbraith** (STAR Strategy /
Structure / Processes / Rewards / People alignment), **Schein**
(Artifacts / Espoused Values / Underlying Assumptions — methodology
touches only Artifacts; assumptions win silently).
