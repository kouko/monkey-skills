# Protocol: Personal — Triage 4DX-fit for a solo individual goal

> Loaded by SKILL.md orchestrator when scope detection identifies a solo
> user with a personal goal — the agent acts as personal coach.

## R — Reading (verbatim source quote)

> Whether you call it a strategy, a goal, or simply an effort at improvement, any initiative you as a leader drive… will fall into one of two categories. The first mainly requires a stroke of the pen; the second is a breakthrough, requiring a change in behavior.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 1

> We cannot stress enough that the 4 Disciplines of Execution are not designed for managing your whirlwind, and they are not designed to manage stroke-of-the-pen initiatives.
>
> — *4DX* 2nd ed., Ch. 1

> The 4 Disciplines are a matched set, not a menu of choices… leave one out, and you'll have a far less effective result.
>
> — *4DX* 2nd ed., Ch. 1 (operating-system metaphor)

## I — Interpretation (mode-specific)

Before installing 4DX on a personal goal, two questions: (1) does the goal
need 4DX? (2) can the user run all four disciplines together?

The book carves goals into three buckets — **stroke-of-the-pen** (single
decision suffices), **whirlwind** (existing routine working better
suffices), **behavioral-change** (sustained new daily action over months —
the only bucket needing 4DX). Misapplying 4DX to the first two wastes
breakthrough currency — the scarce attention budget for goals that need
structural discipline.

For personal-coach scope the three-bucket triage is necessary but not
sufficient. Four personal-scale anti-patterns the book never addresses:
tiny daily habits (atomic-habits territory); portfolios of speculative
bets (OKR / lean experiments — 4DX assumes the goal is right); reactive
emergency roles (whirlwind IS strategic value); pure creative output
(Goodhart corrupts lead measures). One additional hard gate: absent
time-sovereignty.

Output is a single verdict from the rubric. Refusing 4DX when it doesn't
fit is the skill's job. Voice contrast vs sibling: team-mode coaches a
leader judging team adoption; this protocol IS the personal coach helping
one user assess fit for their own goal.

## A1 — Past Application

### Case 1: Spartanburg Marriott — capital alone failed
- $20M renovation planned for guest satisfaction; initially treated as
  stroke-of-pen capital decision. Re-triaged: even with renovation, the
  satisfaction target required front-line behavior change. Installed all
  four disciplines. Outcome: breakthrough scores; flagship 4DX example.
  Personal corollary: even "bought the gym membership" / "hired the coach"
  doesn't deliver the lag — residual gap is behavior change.

### Case 2: Beverly Walker — Georgia child welfare
- Repeat child-abuse cases flat despite reorgs and policy. Walker
  recognized stroke-of-pen options were spent; residual gap was structural
  behavior change. Reframed as 4DX-shaped. Outcome: repeat cases declined.
  Personal corollary: if every authority-only lever has been pulled and
  the lag still hasn't moved, the gap is behavioral — 4DX applicable.

## A2 — Future Trigger

When a solo user would need this protocol:

1. **Goal-shopping mode** — user just heard about 4DX and wants to know "does this apply to my situation?" before investing learning time.
2. **Failed-other-method rebound** — user tried OKRs, GTD, atomic habits, or willpower and stalled; reaching for 4DX next, may again be a wrong fit.
3. **Shape-of-problem ambiguity** — user has a goal but isn't sure if it's "buy this thing" (stroke-of-pen), "do my job better" (whirlwind), or "I need to become a different daily operator" (behavioral change).
4. **Methodology evangelism resistance** — user suspects 4DX is being over-applied (to a habit, a creative project, an on-call role) and wants a sanity check.
5. **Pre-D1 entry** — personal-coach pipeline gates here before any WIG-defining work begins.

EN signal: "Should I use 4DX for X?", "Will 4DX help me with…", "Does 4DX apply to a personal goal?"
JP: 「この目標に 4DX 使える？」「4DX 自分に合ってるか分からない」
zh-TW: 「4DX 適合我這個目標嗎？」「不確定 4DX 是不是適合我」

## E — Execution

The agent runs a Socratic triage as **personal coach** — asks, doesn't
lecture. Each step has a completion criterion that decides whether to
proceed or route out. Verdicts come from `../standards/6-verdict-rubric.md`.

1. **Surface the goal in concrete terms.**
   - Ask: *"What's the goal in one sentence? If you achieved it, what would change in your life or work?"*
   - Completion: user has named the goal explicitly enough that the agent can classify it. Vague aspirations ("be better at life") get a follow-up: *"What would 'better' look like in 3 months?"*

2. **Stroke-of-the-pen check** — see `../standards/stroke-of-pen-vs-behavior-change.md`.
   - Ask: *"Is there a single decision, purchase, hire, or rule change that — by itself — would achieve this goal? Or would you still need to do new things every day for weeks/months?"*
   - Completion: user converges on {one-decision-suffices / sustained-new-action-required / unsure}.
   - **Halt**: if one-decision-suffices → return verdict **stroke-of-the-pen, 4DX overkill** with example ("e.g. 'fix back pain' → buy a sit-stand desk; 4DX would be ceremony"). Skill ends.

3. **Whirlwind-handleable check.**
   - Ask: *"Could you achieve this just by doing your existing routine a bit better — no new categories of action, no new daily practice — just sharper execution of what you already do?"*
   - Completion: yes/no.
   - **Halt**: if yes → return verdict **whirlwind-handleable, 4DX overkill** ("just optimize your existing flow"). Skill ends.

4. **Personal anti-pattern screen** (the 4 traps the book misses).
   - Ask each in turn, only as relevant:
     - *"Is the goal 'do tiny thing X every day'? (e.g. floss, meditate 5 min, take vitamin)"* → if yes, return verdict **habit-formation, recommend habit-stacking / atomic habits**.
     - *"Are you running multiple bets and unsure which will pay off? (multi-startup founder, portfolio investor, R&D explorer)"* → if yes, return verdict **portfolio-bet, recommend OKR / lean experimentation**.
     - *"Is your job mostly reactive — you exist to handle whatever incoming crisis arrives? (ER doctor, firefighter, on-call SRE, customer-support frontline)"* → if yes, return verdict **emergency-role, the whirlwind IS your strategic value, 4DX inverts wrong**.
     - *"Is the output you want pure creative work whose quality is judged subjectively? (novelist, painter, composer, designer)"* → if yes, return verdict **creative-output, Goodhart risk on lead measures, recommend constraint-based methods (writing routines, deliberate practice)**.
   - Completion: each anti-pattern explicitly checked and either matched (skill ends with redirect) or cleared.

5. **Time-sovereignty check** — see `../standards/readiness-preconditions.md`.
   - Ask: *"Do you have at least ~20% of your weekly hours that you control — that you could redirect into new behaviors? Or is your schedule so over-committed / coerced that there's no room to install new daily practice?"*
   - Completion: user reports on time-sovereignty.
   - **Halt**: if no time sovereignty → return verdict **no-time-sovereignty, root cause is upstream; 4DX won't fix; address the schedule problem first**.

6. **Matched-set capacity check (P-23).**
   - Ask: *"4DX is all four disciplines or none. You'll need to: (1) name one breakthrough goal in From-X-to-Y-by-When form, (2) identify daily lead measures, (3) keep a visible weekly scoreboard, (4) hold a weekly 20-30 min review with me as your peer-witness. Are you in for all four?"*
   - Completion: user explicitly says yes / no.
   - **Halt**: if user wants to cherry-pick → flag P-23 (matched set, not menu) and offer either commit-to-all-four or use a lighter framework instead.

7. **Verdict + handoff.**
   - If all gates passed → return verdict **APPLICABLE — proceed to `4dx-d1-personal-whirlwind-triage`**.
   - In all other branches the redirect verdict is the output; do not bend the goal back into 4DX shape.
   - Completion: a single verdict has been issued from the 6-category set.

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **Team-leader fit assessment** — for a leader judging team adoption, load `protocols/team-mode.md` instead.
- **Already-committed users asking "how do I start?"** — route to D1 skills, not back through this gate.
- **Specific-discipline questions** ("what's a lead measure?") — route to the matching D-skill.
- **Enterprise rollout** — out of scope; read book Ch 6-10 directly.

### Author-warned failure modes

- **CE-06 — Stroke-of-the-pen miscategorization.** Applying 4DX where authority alone suffices; strongest scope warning. Look actively for "is there a single decision that solves this?"
- **CE-25 — Wrong-WIG-locked-in (no kill criteria).** No built-in mechanism to detect WIG itself is wrong; exploratory users spend 6-month cycles perfecting wrong goals.
- **CE-26 — Whirlwind-as-strategic-work.** Reactive roles (ER, on-call SRE, frontline support) — whirlwind IS strategic value; 20% sub-WIG inverts the role.
- **CE-27 — Knowledge-work feedback too long.** Drug discovery, hardware, regulatory cycles = 6-month loops; weekly cadence becomes theatrical.
- **CE-30 — FranklinCovey selection bias.** All ~4,000 case studies are paying clients; failures anecdotal. Don't pre-commit to "4DX works for any goal".
- **CE-31 — Winning-as-master-motivator over-claim.** SDT: autonomy + mastery drive engagement, not "winning". Use mastery / autonomy vocabulary if "winning" repels user.

### Author's blind spots

- US-anglophone-corporate dominant; "public peer commitment" assumes low-context culture. JP / ZH / KR public accountability can read as face-loss; agent-as-peer-witness is personal-scale workaround.
- Pre-dates remote-default work; in-person social pressure was original active ingredient.
- Glosses knowledge-work / R&D / creative cases — operational dominates, why the four anti-pattern checks matter.

### Easily-confused neighbors

- **Atomic habits / habit-stacking** (Clear) — tiny-daily-action goals; lighter than 4DX.
- **OKRs / lean startup** (Doerr / Ries) — portfolio-of-bets; built-in kill criteria 4DX lacks.
- **GTD / time-blocking** (Allen) — whirlwind productivity issues; no breakthrough-WIG concept.
- **Deliberate practice / constraint-based routines** — creative-output goals where Goodhart corrupts.

## Standards used

- `../standards/6-verdict-rubric.md` — the 6-verdict rubric (solo labels)
- `../standards/stroke-of-pen-vs-behavior-change.md` — Step 2 + Step 3 foundation
- `../standards/readiness-preconditions.md` — Step 5 time-sovereignty + Heath Path layer

## References

See `../references/industry-grounding.md` sections **Kotter** (urgency
upstream of execution), **Heath & Heath** (Rider/Elephant/Path; environment
shaping precedes 4DX), **March** (exploration vs exploitation; WIG-too-early
failure mode for users in exploratory phases).
