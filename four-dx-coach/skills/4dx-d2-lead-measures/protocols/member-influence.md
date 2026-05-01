# Protocol: Team-member — Map personal sphere of influence on inherited team leads (voice = personal coach to member)

> Loaded by SKILL.md orchestrator when scope detection identifies a team
> member working with leads chosen by their leader / team. The agent fills
> the role of personal coach to the member, helping locate where their
> personal influence actually lives across the inherited lead set.
>
> **V1 ⚠️ partial**: the source book treats lead-measure selection as a
> leader-side / team-side activity. The member POV used here is inferred
> from (a) Ch. 3's two-axis test read from the individual seat, (b)
> Ch. 12's daily question, and (c) Ch. 13's frontline cases where
> individual contributors moved leads they did not select. The cited
> cases are leader-side; the member protocol is the symmetric inverse.

## R — Reading (verbatim source quotes)

> A good lead measure has two primary characteristics: It's predictive ... and it's influenceable.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 3

> Each team member, every day, must be able to answer one question: "What is the most important thing I can do today to advance my team's lead measure?"
>
> — *4DX* 2nd ed., Ch. 12

## I — Interpretation (mode-specific)

The book defines a lead measure as both *predictive* of the WIG and
*influenceable* by the team. The leader-side use of the test is "did we
pick a good lead measure?" The member-side use is the same test, applied
one position narrower: **"of the leads my team picked, which can *I*,
from my actual seat, actually move this week?"**

Most members on a 4DX team inherit lead measures they did not choose.
Three things are then true at once:

1. **All team leads ladder to the team WIG.** That is what made them
   survive selection. The member doesn't need to re-litigate that —
   they need to understand the ladder so they can act on it instead of
   guessing.
2. **The member's personal sphere of influence on those leads is uneven.**
   A frontline rep can move a "discovery calls per week" lead directly;
   a back-office colleague on the same team can move it only indirectly
   (e.g. by preparing call lists faster). Some members can move all team
   leads; some can move only one; a few may genuinely have no daily-
   influence handle on any of them. That unevenness is not a flaw of
   the leads — it is the cost of a single team WIG with mixed-role
   members, and it has to be mapped, not denied.
3. **The member's job is to convert influence into focus, not into
   coverage.** Pick the 1-2 leads where personal influence is highest as
   the primary weekly focus. The remaining leads stay supported (the
   member doesn't sabotage them) but are not the member's anchor for
   D4 commitment-making. Trying to "contribute equally to all leads"
   recreates the whirlwind under a 4DX label.

When the influence map comes back genuinely empty — when a member's role
does not, structurally, allow them to move *any* of the team's leads —
that is *not* a member problem to solve alone. It is a signal to the
leader that either (a) the lead set didn't decompose to this role, or
(b) this role is on the wrong team for this WIG. The protocol surfaces
that escalation explicitly rather than letting the member fake influence
to keep up appearances.

Voice contrast vs sibling protocols: this is **personal coach to the
member** — Socratic, never inventing the influence map, protecting the
honest "no influence here" answer when it appears.

## A1 — Past Application (member-side mirrors of leader-side cases)

### Case 1: Younger Brothers Construction — frontline workers moving an inherited safety-compliance lead set
- **Leader-side as written**: six observable safety-compliance behaviors
  (hard hat, eye protection, scaffolding, etc.) selected by leadership
  against a serious-incidents lag.
- **Member-side mirror**: each crew member, regardless of trade, had to
  find their personal handle on those six. A framer's influence on
  "scaffolding compliance" looks different from an electrician's on
  "eye protection" — both leads ladder to the same WIG, but personal
  influence varies by role. Members who mapped their per-lead influence
  concentrated on the 1-2 they could move daily; members who tried to
  "keep all six in mind every shift" defaulted to the whirlwind.
- **Outcome**: Annual serious incidents fell from 57 to 12.

### Case 2: Towne Park valet — retrieval-time lead acted on by individual valets
- **Leader-side as written**: team chose retrieval-time as the lead for
  guest satisfaction.
- **Member-side mirror**: each valet found their own handle — running
  the route, staging cars by departure window, breaking the concrete-
  wall bottleneck. An individual valet's influence map produced action
  the leader's selection brief never specified (literally breaking down
  a wall on a Saturday).
- **Outcome**: retrieval times dropped, satisfaction rose; the case is
  the book's flagship D2 example. Member-side reading: the lead unlocked
  individual influence the leader couldn't have prescribed.

### Case 3: The daily question at the individual contributor seat (Ch. 12)
- **Problem**: without a per-lead influence map, members default to
  whatever screams loudest in the whirlwind, even when they nominally
  know the team leads.
- **Methodology**: Ch. 12's daily question — *"What is the most
  important thing I can do today to advance my team's lead measure?"* —
  operates only when the member has already located their personal
  influence handle. Without that, the question collapses into "what
  feels urgent today?"
- **Outcome**: the daily question becomes operational — and weekly D4
  commitment-making becomes specific — only after the influence map is
  honest.

## A2 — Future Trigger

When a team-member would need this protocol:

1. The user is on a 4DX team where leads have been chosen and wants to
   know how to engage with them rather than just "comply with" them.
2. The user can recite the team's leads verbatim but doesn't know which
   ones are *theirs* to move from where they sit.
3. The user has been "supporting all the team leads" and feels stretched
   thin — needs to concentrate on 1-2.
4. The user suspects their role doesn't have a handle on any of the
   current leads (e.g. back-office on a customer-facing lead set) and
   isn't sure whether that's their gap or a real role-fit signal.
5. The user wants to bring the daily question into their morning but
   doesn't yet know which lead to answer it against.
6. The user is about to write a D4 weekly commitment but isn't sure
   which lead the commitment should anchor on.

## E — Execution

The agent acts as **personal coach** in a Socratic dialogue. Do not
invent the leads, the influence map, or the focus pick — extract what
the member knows, surface where personal influence lives, and protect
the honest "no influence here" signal when it appears.

1. **Comprehension gate — confirm the team leads are known.**
   - Ask: "List your team's lead measures, ideally verbatim. How many
     are there?"
   - Completion: member names each team lead clearly, with operational
     definition where they know it.
   - Halt: if member can't list the leads or names the WIG (lag)
     instead, halt and route to
     `4dx-d1-wig-formulation`. Influence-mapping over an
     unknown lead set produces theatre.

2. **Ladder check — does each lead actually predict the team WIG?** —
   see `../standards/predictive-and-influenceable.md`
   - For each lead, ask: "Walk me through the causal chain — when this
     lead moves, why does the team WIG move? In one sentence."
   - Completion: member can state a one-sentence causal chain for each
     lead, or explicitly flag the ones where they can't.
   - Note: if the member can't articulate the chain for any lead,
     that's a comprehension gap — assign homework to ask the leader,
     but do not block the rest of this protocol (mapping influence on
     leads-without-clear-chain is still useful and surfaces the gap).

3. **Per-lead influence audit — score 0–5 for each.**
   - For each team lead, ask the member: "From where you sit, this
     week, with no permission required, can you move this measure?
     Score 0 (cannot touch it) → 5 (I am the primary mover)."
   - Push for specificity about *what they would actually do* for any
     lead they score ≥3. Vague "I'd help out" answers score 1, not 3.
   - Completion: every team lead has a 0–5 score plus a one-line "what
     I'd do" for any score ≥3.

4. **Map check — interpret the distribution.**
   - **Multiple high scores (≥3 on most leads)**: typical for
     generalist roles; pick 1-2 highest as primary focus, support the
     rest. Move to step 5.
   - **One or two high scores, rest low**: typical for specialist
     roles; the high scores are the focus. Move to step 5.
   - **All low (no score ≥3)**: this is the no-influence escalation
     case. Move to step 6 instead — do NOT force a focus pick out of
     low-influence leads.

5. **Focus pick — name 1-2 primary-focus leads.**
   - Ask: "Of the leads where you scored ≥3, which 1-2 will be your
     primary focus? Where will weekly D4 commitments anchor?"
   - Push back on "I'll do all of them" — the cap is hard. Trying to
     act on 4+ leads is the whirlwind in 4DX clothing.
   - Push back on picking based on "what the leader expects" rather
     than where personal influence is highest. Self-chosen focus
     follows the influence map, not political optics.
   - Completion: 1-2 leads named as primary focus, with a one-sentence
     "this is my anchor because…"

6. **No-influence escalation path (if step 4 routed here).**
   - Validate the signal: "If you genuinely cannot move any of these
     leads from where you sit, that is information, not a failure. Two
     possibilities — (a) the leads decomposed to roles your seat
     doesn't sit in, or (b) your seat is on the wrong team for this
     WIG."
   - Assign homework: "Schedule 15 minutes with your leader. Frame it
     as: *'I want to be useful on the team WIG. I've mapped my position
     against each lead and I don't see a daily-influence handle. Can we
     look at this together and either find one I'm missing, or rescope
     my contribution?'* This is a contribution to team learning, not a
     complaint."
   - Completion: member commits to scheduling the conversation, with
     the framing rehearsed.

7. **Translate the focus into the daily question (forward to D4).**
   - Ask: "Each morning, can you carry the question — *'What is the
     most important thing I can do today to advance my team's lead
     measure?'* — and answer it against your 1-2 focus leads
     specifically?"
   - Quality check: member should be able to imagine answering it
     tomorrow morning with a concrete action, not a generic intent.
   - Completion: member agrees and names where the question will live
     (calendar block / sticky / morning ritual).

8. **Goodhart self-check (member-side)** — see
   `../standards/goodhart-self-check.md`
   - Once a focus lead is fixed, the same self-Goodhart risks apply:
     hitting the count without the quality (called three customers but
     didn't follow the script; logged 30 min writing but stared at the
     screen). Re-check the causal chain (step 2) every 4 weeks against
     actual lag movement.

9. **Output the influence card & hand-off.**
   - Write back to the user, in their own words:
     - **Team lead measures** (as listed): …
     - **My influence scores (0–5)**: …
     - **My primary focus (1-2 leads)**: …
     - **What I'll actually do on each focus lead**: …
     - **Daily question, anchored**: *"Most important thing I can do
       today to advance [focus lead]?"*
     - **Open questions for my leader** (if any): …
   - If "open questions for leader" is non-empty, that's the correct
     output — do not paper over.
   - Hand off to `4dx-d4-cadence` (member-prep mode) for converting the
     focus lead into a specific weekly commitment.

## B — Boundary (mode-specific)

### Do NOT use this protocol in:

- **Solo / individual-goal contexts** — load `personal-discover.md`.
- **Leader-facilitating-team-selection contexts** — load
  `team-facilitate.md`.
- **WIG / lead comprehension gap** — route to
  `4dx-d1-wig-formulation` first.
- **Weekly commitment writing** — produces the focus map; converting a
  focus lead into a specific *weekly* commitment is
  `4dx-d4-cadence` member-prep.
- **As a substitute for asking the leader directly** — some answers
  (whether a lead's causal chain is real, whether the lead set
  decomposes to this role) can only authoritatively come from the
  leader. The protocol surfaces those gaps and routes them; it does
  not invent plausible-sounding answers.
- **As an end-run around fundamental disagreement with the leads** —
  this protocol comprehends and maps; it does not litigate. The
  dissent conversation is a 1:1 with the leader, not coaching.

### Author-warned failure modes (member-side mirrors)

- **Predictive-but-not-influenceable trap (CE-02, member-side)** —
  don't pick a *focus lead* you personally can't influence. A score-2
  lead the team can move collectively but you can't move from your
  seat is not your focus pick — even if it's "the most important"
  lead overall.
- **Coverage-instead-of-focus (member-side mirror of CE-03)** — trying
  to act meaningfully on 4+ leads recreates the whirlwind. Cap at 1-2.
- **Compliance-without-commitment (CE-15, member-side)** — member
  scores everything 3, picks one randomly to "look engaged" — without
  having located genuine influence. The honest answer might be "I
  don't have an influence handle on any of these," and the right move
  is escalation (Step 6), not faking a focus.
- **Lead-as-personal-task confusion** — member treats a team lead as
  their personal to-do list. The team lead is a *team* measure; the
  member's contribution is a slice of the lead, not the whole lead.
- **Goodhart self-targeting (CE-24)** — see
  `../standards/goodhart-self-check.md`.
- **Whirlwind invasion of the focus** — focus lead doesn't get acted
  on because the whirlwind eats the slot. Step 7 (anchor the daily
  question on the focus lead) is the first defense; D4 commitment
  prep is the second.

### Author's blind spots

- **Member voice underrepresented in selection-side cases** — book is
  leader-POV throughout Ch. 3 + Ch. 13. This protocol fills that gap.
- **Hierarchical assumption** — in flat / peer-driven teams, the "ask
  your leader" homework in Step 6 may need re-routing to "ask the
  team" or to a peer-collective decision moment.
- **Operational-work bias** — knowledge-work members face leads where
  personal influence is murky or runs through long feedback loops.
  Apply Step 3's "what would you actually do" test rigorously.
- **Single-team assumption** — in matrix orgs the member may be on
  multiple teams; this protocol handles one team at a time and does
  not arbitrate between competing influence maps.

### Easily-confused neighbouring methodologies

- **OKR cascading** — OKRs cascade Objectives + KRs through layers;
  4DX gives the team a shared lead set and decomposes contribution on
  the lead side, not the KR side.
- **Generic "ownership" coaching** — too vague. 4DX is more specific —
  per-lead 0-5 score, 1-2 lead focus pick, daily-question anchor.
- **MBO-style "your individual objectives"** — MBO assigns each person
  their own objective; 4DX assigns the team a shared lead set.
- **RACI matrix** — RACI assigns roles on tasks; influence-mapping is
  upstream of RACI.

## Standards used

- `../standards/predictive-and-influenceable.md` — Step 2 ladder check
  (read from member seat)
- `../standards/goodhart-self-check.md` — Step 8 self-targeting risk
- `../standards/lead-vs-lag-distinction.md` — Step 1 comprehension
  guard (lead vs lag vs task vs sub-WIG)

## References

See `../references/industry-grounding.md` sections **Pfeffer**
(power-axes for influence-score literacy), **Cialdini** (six-principle
non-positional leverage), **Argyris** (skilled-incompetence / Model-II
inquiry for Step 6 escalation script).
