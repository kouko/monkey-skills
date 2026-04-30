# Protocol: Team-leader — Facilitate the team's lead-measure selection (voice = consultant-to-leader)

> Loaded by SKILL.md orchestrator when scope detection identifies a
> team-leader (3-9 direct reports) facilitating their team's discovery of
> 2-3 lead measures for an already-defined Team WIG. The agent coaches
> the leader through the facilitation; the agent does NOT facilitate the
> team directly, and the leader must not author the leads themselves.

## R — Reading (verbatim source quote)

> The lead measures with the most impact come from a collaboration between the leader and the frontline team. ... The leader can veto an idea they believe will not work, but they cannot dictate what the final lead measures should be.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 3

## I — Interpretation (mode-specific)

A team-leader who picks lead measures alone gets compliance, not
commitment. A team-leader who fully delegates loses strategic alignment
with the Team WIG. The book's answer is structured collaboration: leader
provides the WIG and holds the line on quality; team provides the
leverage points because they know the operation.

The facilitation has four moving parts the leader must hold
simultaneously:

1. **WIG as anchor.** Team WIG must be defined as *From X to Y by When*.
   Leads built on a vague WIG are noise; halt and route upstream if the
   WIG is not yet crisp.
2. **Brainstorm wide, then narrow ruthlessly.** More candidates → higher
   quality. Cap at 2-3 leads; 2 is ideal, 3 is the maximum.
3. **Two-axis test as the gate.** Every surviving candidate must be both
   *predictive* of the Team WIG AND *influenceable* by THIS team without
   significant dependence on another team. Failing either axis
   disqualifies completely.
4. **Veto, don't dictate (Rule 3, Ch 7).** When the team proposes a bad
   lead, the leader rejects it ("this won't move the WIG because…") —
   but does NOT author the replacement. Silence is the leader's tool.

Two structural confusions to surface loudly. **A battle is not a lead
measure** (Ch 7 explicit caution): sub-goals like "improve arrival
experience" are lag measures on a smaller scale. **A task is not a
measure**: "complete the cache rewrite" is one-shot; "% of requests
served from cache, weekly" is a measure that drives behavior across the
quarter.

Voice contrast vs sibling protocols: the agent acts as **consultant to
the leader**, not as facilitator-in-the-room. The agent coaches the
leader on stance, scripts, and veto language; the leader runs the actual
session.

## A1 — Past Application

### Case 1: Opryland Hotel — 75 functionally-diverse teams under 3 Key Battles
- **Problem**: Primary WIG of guest satisfaction 42→55 (top-box). Each
  of 75 frontline teams had to discover their own lead measures under a
  Team WIG (e.g. bellstand: luggage delivery 106 min → 12 min).
- **Methodology applied**: Each team-leader facilitated brainstorm +
  two-axis filter. Bellstand team chose lead measures around delivery
  routing and staging — operational, influenceable by every bellman,
  predictive of luggage time. Leaders veto'd lag-masquerading-as-lead
  candidates ("guest satisfaction score for our area" — that's the lag).
- **Outcome**: Top-box satisfaction beat target — 42 → 61 in nine months
  across all 75 teams.

### Case 2: Surgical team — verbal confirmation 17% lift
- **Problem**: Existing lead "audit surgical tray" plateaued. Clinical-
  lead facilitated refinement rather than imposing a new lead.
- **Methodology applied**: Team brainstormed quality-axis enhancements;
  proposed "audit + complete a verbal confirmation of every procedure"
  — small qualitative tweak, team-authored, leader veto'd vague
  "communicate better in the OR" (failed influenceability +
  measurability).
- **Outcome**: Perioperative-incident reduction lifted by 17%.

### Case 3: Front-desk team — 7-foot eye-contact rule, 38% lift
- **Problem**: Front-desk lead "warmly welcome every guest" was vague.
- **Methodology applied**: Team-leader facilitated team's redefinition;
  team proposed "make eye contact and greet within 7 feet of arriving
  guest" — specific, influenceable by every clerk, predictive of
  satisfaction. Leader veto'd softer rewordings.
- **Outcome**: 38% lift on the relevant satisfaction sub-measure.

## A2 — Future Trigger

When a team-leader would need this protocol:

1. Team-leader has a defined Team WIG and needs to run a working session
   to choose 2-3 lead measures — unsure how to facilitate without
   dictating.
2. Team-leader is about to pre-write the leads themselves "to save the
   team time" — needs redirection to facilitation.
3. First attempt produced 6+ candidate leads; team couldn't narrow.
4. Team proposed a candidate the leader senses is wrong (lag-masquerading,
   gated by another team, vanity metric like "more meetings") — leader
   needs the veto-don't-dictate language.
5. Team is split: half says "we control X", other half says "no, X is
   gated by team B" — leader needs to mediate without dictating.
6. Team proposed "complete the cache rewrite by Q4" as a lead — leader
   needs to surface that this is a TASK, not a MEASURE.

## E — Execution

The agent acts as **consultant to the leader**, coaching stance + scripts.
The leader runs the team session; the agent does not. Steps below run
sequentially across one or two coaching conversations (pre-session +
post-session debrief if needed).

1. **Team WIG gate check**
   - Ask: "State your Team WIG in one sentence — From X to Y by When."
   - Halt: if leader can't, STOP and route to the appropriate Team-WIG
     skill. Do NOT proceed.

2. **Leader-stance briefing (anti-dictate inoculation)**
   - Brief the leader on the four facilitation rules BEFORE the session:
     (a) you do not pre-write the leads; (b) you can veto, you cannot
     dictate; (c) silence is your tool — when team is stuck, do NOT
     fill it with your own answer; (d) cap at 2-3 leads, with 2 as
     ideal.
   - Ask: "Which of these four will be hardest for you?" — surfaces the
     leader's specific failure mode (most common: filling silence).
   - Completion: leader names their personal-risk rule and commits to a
     specific behavior to counter it (e.g. "when team is silent for 60s
     I will ask 'what's a non-obvious option?' rather than offer one").

3. **Coach the brainstorm — wide, no filtering (5-10 candidates)** — see
   `../standards/lead-vs-lag-distinction.md`
   - Coach the leader to ask the team: "What daily or weekly behaviors,
     if you did them consistently, would drive [Team WIG]? Don't filter
     — list as many as you can."
   - Provide veto scripts for common failures:
     - One-shot task ("ship the cache PR"): "that's a deliverable, not
       a measure — what's the underlying behavior we'd track every
       week?"
     - Vanity lead ("more meetings", "send more emails"): "what's the
       causal chain to the WIG?"
     - Sub-WIG masquerading as lead ("improve arrival experience"):
       "that's a lag — what's the daily behavior that drives it?"
   - Completion: leader has scripts ready; ≥5 team-authored candidates
     expected.

4. **Coach the two-axis test** — see
   `../standards/predictive-and-influenceable.md`
   - For each candidate, the team scores together:
     - **Predictive (1-5)**: "If we did this consistently for 6 weeks,
       how confident are we the WIG moves? State the causal chain in
       one sentence."
     - **Influenceable (1-5)**: "Can THIS team move this measure THIS
       week WITHOUT permission from another team?"
   - Mediation script for influenceability disagreement: "what fraction
     of X do we directly control? Score it as that fraction × 5." If
     <60% controllable, the lead needs to be re-scoped to the
     controllable portion or dropped.
   - Completion: leader has the mediation script ready; every candidate
     gets both scores + a one-sentence causal chain.

5. **Coach the veto pass — drop anything <4 on either axis**
   - When dropping, the leader names WHY ("this fails predictive — no
     causal chain to WIG") but does NOT propose a replacement.
   - Coach the leader: silence after a veto is the team's cue to
     produce the next candidate. Do NOT fill it.
   - Completion: leader practices vetoing without replacing on a sample
     candidate; only 4-5★ candidates expected to remain.

6. **Coach the narrowing — 2-3 final, prefer one frequency + one quality**
   - Coach the leader to ask: "Pick 2-3 — at most. Ideally one small
     outcome (a weekly result with method-latitude) and one leveraged
     behavior (a specific action performed consistently)."
   - Force-cut script: "more than three recreates the whirlwind —
     which one drops?" The TEAM decides which drops.
   - Completion: 2-3 named team-authored lead measures expected.

7. **Coach the operational-definition pass (team writes; leader proofreads)**
   - Team writes for each lead: what exactly counts as "done", how/when
     it gets logged, who logs it, weekly target number.
   - Leader's role: proofread for vagueness. If a definition is vague,
     leader veto's it ("this isn't specific enough — another team
     member couldn't apply it") and the team revises. Leader does NOT
     write the revision.
   - Completion: leader has the proofread script.

8. **Goodhart-self-check coaching** — see
   `../standards/goodhart-self-check.md`
   - Coach the leader to surface the gaming risk in the session: "If we
     attach visibility / bonuses / public ranking to this lead, where
     could it get gamed?" Pair frequency with quality; commit to 4-week
     causal-chain re-check.
   - Industry cases (Wells Fargo / Phoenix VA / Atlanta APS) generalize
     directly to team scale; brief the leader so they can name the
     pattern when the team rationalizes ("but our culture would never…").

9. **Coach the causal-chain commitment**
   - Team writes (collaboratively): "If we hit our lead targets every
     week for 6 weeks, here's why we expect [Team WIG] to have moved
     by [Y]…"
   - Falsifiable forecast — anchor for D4 weekly review and trigger
     for `4dx-sustain-personal-momentum-rescue` if the lag stays flat.

10. **Output & hand-off**
    - 2-3 named lead measures, each with team-authored operational
      definition + weekly target + team-authored causal-chain
      rationale.
    - Hand off to `4dx-d3-scoreboard` for visual artifact and to
      `4dx-d4-cadence` (team-leader mode) for weekly review.

## B — Boundary (mode-specific)

### Do NOT use this protocol in:

- **No defined Team WIG yet** — route to the appropriate Team-WIG
  skill.
- **Solo personal-WIG context** — load `personal-discover.md`. Member-
  side leads (user is a team-member with WIG handed down) → load
  `member-influence.md`.
- **Multi-team / matrix context** — out of plugin scope; treat each
  team as one application of this protocol.
- **Stroke-of-pen WIGs** — single decision (sign, reorg, hire). No
  behavioral pattern to discover.
- **Knowledge-work with months-long feedback loops** — apply two-axis
  rigorously and shorten the loop by one decomposition layer, or
  honestly admit the lead-to-lag chain doesn't fit a weekly cadence.

### Author-warned failure modes

- **Lag-masquerading-as-lead at team scale (CE-01 + Ch 7 caution)** —
  see veto script in Step 3.
- **Predictive but not influenceable, gated by another team (CE-02 +
  CE-16)** — re-scope to controllable portion ("our service's error
  budget consumption", not "decrease infra outage rate" gated by
  another team's pager).
- **Lead-data-too-hard-so-skipped (CE-17)** — pay the price (P-11);
  awkwardness is not grounds to drop, only failing the two-axis test
  is.
- **Compliance without commitment (CE-15)** — team accepts whatever
  the leader implies. The 4-week tell: leads green, lag flat, team
  affect flat. If observed, re-run this skill — original session was
  leader-dictated even if it didn't feel that way.
- **Leader hijacks the team's work (CE-23, "Marcus pattern")** — under
  pressure, leader starts personally executing the lead. D4 failure
  mode rooted in D2 ownership transfer that didn't actually happen.
- **Lead at frequency-only quality (CE-21)** — pair frequency with
  quality (Step 6). If team picks two frequency-based, leader vetoes
  the second.
- **Goodhart / measure-gaming (CE-24)** — see
  `../standards/goodhart-self-check.md`.

### Author's blind spots

- **Operational-work bias** — knowledge-work teams need the two-axis
  test applied more carefully. Resist copying retail patterns.
- **High-context-culture peer dynamics** — in JP/ZH/KR enterprise,
  public veto can read as face-loss. Run pre-session 1:1s to surface
  candidates privately, then merge.
- **Authority-assumption** — weaker in flat / partnership / holacracy
  settings; reframe veto as collective quality gate.

### Easily-confused neighbouring concepts

- **Battles vs lead measures (Ch 7)** — battle is sub-WIG (lag); lead
  is daily behavior driving Team WIG.
- **Tasks vs lead measures** — "ship the cache PR" is a task; "% of
  requests served from cache, weekly" is a lead.
- **OKR Key Results** — mix of lag and lead. Run this skill against
  the WIG, not the KR list.

### Member-misfire patterns

- **Member as facilitator** (leader delegated): reduced veto authority
  — bring 2-3 candidates that all pass; let the leader weigh in
  before lock-in.
- **Member experiencing inherited leads**: redirect to
  `member-influence.md`.
- **Single-team leader vs leader-of-leaders** — leaders of leaders
  should NOT have lead measures at their level (P-10). Route to
  `4dx-meta-team-xps-evaluation`.

## Standards used

- `../standards/predictive-and-influenceable.md` — Step 4 + Step 5
- `../standards/lead-vs-lag-distinction.md` — Step 3 brainstorm guard
- `../standards/goodhart-self-check.md` — Step 8 + ongoing 4-week
  re-check

## References

See `../references/industry-grounding.md` sections **Edmondson**
(psychological safety precondition), **Lencioni** (trust → conflict →
commitment chain for veto debate), **Pfeffer & Sutton** (evidence-based
skepticism on copy-pasted leads).
