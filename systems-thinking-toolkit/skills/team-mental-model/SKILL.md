---
name: team-mental-model
description: |
  Surface team members' mental models as CLDs, converge on shared values, sustain with leadership-energy proxies — inward-harmony sibling of cld-overlay. Use when a team is 'excellent but slow', mental models drifted, or reviews turn contentious.
source_book: Seeing the Forest for the Trees — Dennis Sherwood
source_chapter: Chapter 1 (open-system / self-organization) + Chapter 9 (mental-models harmony + leadership-as-energy-pumping)
source_language: en
tags: [systems-thinking, teamwork, leadership, mental-models, harmony, open-systems, falsifiable-proxies]
related_skills:
  - slug: cld-craft
    relation: depends-on
  - slug: cld-overlay
    relation: composes-with
---

# Team Mental Model (Harmony + Falsifiable Leadership Energy)

## R — Reading

> "A high-performing team is a group of people whose mental models are naturally in harmony, especially as regards fundamental values."
>
> — Dennis Sherwood, Chapter 9 (the inward / harmony claim)

> "In the context of teamwork, that is what leadership is all about: the active, continuous, pumping of energy into and through the team, especially when the going gets tough."
>
> — Dennis Sherwood, Chapter 9 (the sustaining-practice claim)

> "Passive listening — letting people talk while you wait to reply — produces the *form* of dialogue without its substance."
>
> — Dennis Sherwood, p32 (paraphrase: active vs passive listening as the load-bearing leadership discipline)

## I — Interpretation

Sherwood frames a team as an **open thermodynamic system**: it sustains higher-than-random order only while energy keeps flowing through it from outside. The specific form of "order" that makes it high-performing is **mental-model harmony** — convergence on the underlying causal map, especially on fundamental values. Without continuous energy throughput, the team's order decays toward a random group of competent individuals who happen to share an office. Individual excellence is necessary but not sufficient; a leader-less team is structurally a closed system and will decay regardless of individual talent.

The build process is **surfacing-via-CLDs** (same machinery as `cld-overlay`, opposite goal): each team member draws their own CLD of "what causes our team to succeed," and the team negotiates **convergence**, not straddle-discovery. Tactical divergence is healthy; value-causality divergence is the binding constraint. Sherwood is explicit: harmony "especially as regards fundamental values" — at that level, divergence guarantees coordination cost compounds quarter-on-quarter.

The maintain process is **continuous leadership energy**. The leader is **not a decision-maker on top of the system**; the leader is the energy pump that keeps the open system in its ordered state. The Nelson "Band of Brothers" at Trafalgar (c18, see `references/cases.md`) is Sherwood's gold-standard exemplar — *years* of shared dinners, briefings, value-and-tactics conversations enabled audacious tactical innovation under battle chaos with minimal signaling. The Coopers & Lybrand 100-partner anti-case (c19) is the inverse: individually excellent professionals, repeated exhortations about teamwork, and zero continuous energy investment produced zero coordination improvement. Pep talks are one-shot inputs to an open system that needs continuous flow.

**The "energy pumping" metaphor is unfalsifiable as stated** — Sherwood gives no operational definition of how much energy, of what kind, applied how, produces what outcome. This skill operationalizes the metaphor via **four observable proxies** that make the leadership-energy claim falsifiable rather than poetic. Track them *before* and *during* the intervention; if none are moving, the open-system framing is not being delivered regardless of how the leader feels about effort spent:

- **Cadence proxy**: weekly mental-model check-in count. Target ≥ 1 / week sustained for ≥ 1 quarter without leader-prompting (team self-initiates).
- **Active-listening minutes**: leader-time spent surfacing dissenting CLDs per meeting (not advocating leader's own view). Target ≥ 15 min per hour-long meeting.
- **Value-revisitation count**: explicit references to the team's stated fundamental values during decision-making (in design docs, retros, code-review threads). Target ≥ 1 / week.
- **Symbol-and-narrative refresh** (optional): leadership's repeated articulation of team purpose in own words. Target weekly cadence.

If a leader cannot point to data on at least the first three proxies after 4-6 weeks, the team is functionally closed regardless of the leader's stated commitment. This is the falsifiability bar this skill imposes on Sherwood's metaphor.

**Counter-intuitive prediction**: a leader-less team is structurally a closed system and will decay regardless of individual talent. The "we don't need a leader, we're all senior" framing — common in flat orgs and senior-IC clusters — is structurally identical to the Coopers & Lybrand anti-case. Talent is the order; energy is what keeps it from decaying. Both are required.

**Paired sibling with `cld-overlay`.** Same mental-model-surfacing machinery; opposite goal. Outward conflict resolution between groups (`cld-overlay`) finds a straddle; inward team-building (this skill) negotiates convergence and sustains. Use them in sequence for post-merger / cultural-change scenarios: `cld-overlay` first to surface between-group differences; this skill second to sustain convergence among the integrated team.

## A1 — Past Application

The two cases that calibrate this skill — Nelson's Band of Brothers at Trafalgar (c18, the gold-standard exemplar) and Coopers & Lybrand 100-partner anti-case (c19, the exhortation anti-pattern) — plus the n=2 boundary case where the inward protocol collapses onto the same artifact as `cld-overlay` (theater-vs-dinner couple c17) are detailed in `references/cases.md`.

**MANDATORY — READ ENTIRE FILE**: Before prescribing a team intervention, you MUST read [`references/cases.md`](references/cases.md) (~60 lines) for the Nelson energy-pump exemplar, the Coopers & Lybrand exhortation anti-pattern (cite this case when a senior leader proposes "one big all-hands" or "another values workshop" instead of sustained weekly+ practice), and the n=2 interpersonal collapse case where outward and inward protocols share the same artifact.

## A2 — Future Trigger ★

### When will the user need this skill?

1. Hired star engineers from FAANG / star talent from competitors; code reviews now contentious, decisions take 3x longer, morale dropping despite individual excellence rising.
2. A team that "used to be great" is degrading after the founding leader stepped back or left.
3. Rapid scaling (team doubled in 12 months) and the original cultural coherence is fraying.
4. Cross-functional task force assembled from competent individuals that consistently underperforms expectations.
5. A senior leader is investing speeches and offsites in "team-building" but velocity and retention keep deteriorating.
6. Post-merger team integration where `cld-overlay` has already found a straddle and now the integrated team needs to sustain convergence — second-leg hand-off from `cld-overlay`.
7. A leader is convinced they are "doing leadership" but cannot point to any of the four observable proxies — the falsifiability gap.
8. A flat / self-managed team that began strong is decaying and "we don't need a leader" framing is preventing diagnosis.

### Language signals

- "individually excellent but team is slow" / "we hired stars and velocity dropped"
- "we built a band of brothers" / "the team used to just *get* it"
- "why are decisions taking forever?"
- "we need more team-building" / "another offsite"
- "code reviews / design reviews are contentious"
- "leadership vacuum" / "the team is decaying"
- "how do we measure team coordination?" / "leadership energy is unfalsifiable"
- "team doubled in 12 months and culture is fraying"

### Distinction from neighboring skills

- vs. `cld-craft`: That skill teaches the craft of drawing one CLD well; this skill assumes that craft and adds the convergence-negotiation move (Step 4) plus the falsifiable-proxy sustainment regime (Step 5). Each team member's mental model is a CLD drawn with `cld-craft` discipline.
- vs. `cld-overlay` (paired sibling): That skill handles **outward** conflict resolution between groups whose mental models structurally differ (find a straddle). This skill handles **inward** team-building among people whose mental models can be harmonized (negotiate convergence + sustain). Same machinery (mental-model surfacing via CLDs), opposite goal: straddle-discovery vs convergence-negotiation. Hand off in either direction for post-merger / cultural-change scenarios.
- vs. `loop-and-link-primitives`: Foundational ontology (R vs B classification). The team-as-open-system claim depends on recognising leadership-energy → harmony → performance → reputation → leadership-energy as a reinforcing loop whose collapse (when energy stops pumping) is structurally predictable.
- vs. `strategy-lever-and-cascade` (sk07): sk07 is for a single decision-maker conflating KPIs with controls; this skill is for a team whose members hold divergent causal beliefs about what causes the team to succeed.

## E — Execution

```
E flow:
  high individual talent, degrading collective output?
        │
        ├── no → wrong skill
        │
        v
  Step 1: diagnose open vs closed system (baseline 4 proxies)
        │
        ├── all 3 primary proxies at zero → name "team is closed and decaying"
        v
  Step 2: surface each member's CLD (voluntary; cld-craft)
        │
        ├── refusal → halt: mental-model surfacing requires voluntary
        v
  Step 3: compare CLDs side-by-side → find divergent S/O on fundamental values
        │
        v
  Step 4: negotiate convergence on FUNDAMENTAL VALUES (not tactics)
        │
        v
  Step 5: install continuous energy practices (weekly+, sustained)
        │
        v
  Step 6: leader = energy pump, not decision-maker (time-logged active listening)
        │
        v
  Step 7: re-surface mental models on every team composition change
```

### Observable proxies for "leadership energy"

The energy-pumping metaphor is unfalsifiable as stated (see Blind spots). To make this protocol actionable, operationalize "continuous energy" via four measurable signals. Track these *before* and *during* the intervention; if none are moving, the open-system framing is not being delivered regardless of how the leader feels about effort spent.

- **Cadence proxy**: weekly mental-model check-in count. Target ≥ 1 / week sustained for ≥ 1 quarter without leader-prompting (team self-initiates).
- **Active-listening minutes**: leader-time spent surfacing dissenting CLDs per meeting (not advocating leader's own view). Target ≥ 15 min per hour-long meeting.
- **Value-revisitation count**: explicit references to the team's stated fundamental values during decision-making (in design docs, retros, code-review threads). Target ≥ 1 / week.
- **Symbol-and-narrative refresh** (optional, 4th proxy): leadership's repeated articulation of team purpose in own words. Target weekly cadence.

If a leader cannot point to data on at least the first three proxies after 4-6 weeks, the team is functionally closed regardless of the leader's stated commitment.

### Steps

1. **Diagnose: is the team an open or closed system?** Is anyone investing continuous energy in surfacing mental models? "Continuous" means weekly+, sustained for quarters, not an annual offsite.
   - **Exit criterion**: baseline measurement on all three primary proxies (cadence count, active-listening minutes, value-revisitation count) over the prior 4 weeks. If all three are at zero, the team is functionally closed and decaying regardless of talent — name this explicitly before proceeding.

2. **Surface individual mental models.** Each team member draws their own CLD of "what causes our team to succeed over the next 12 months." Use `cld-craft` craft. Halt if anyone refuses; mental-model surfacing requires voluntary participation — coercion produces performative agreement, not genuine surfacing.
   - **Exit criterion**: one CLD per participating member, each satisfying `cld-craft` Rule 8 (S/O signing) and Rule 10 (recognized as real by its author).

3. **Compare CLDs side-by-side.** Look for divergent S/O labels on shared nodes, missing nodes that one person treats as load-bearing, conflicting causal beliefs about fundamental values. This is the inward analog of `cld-overlay` Step 4 signatures — but the goal is convergence-target identification, not straddle-search.
   - **Exit criterion**: ≥ 1 fundamental-value node with divergent S/O label identified per team member, documented in writing on a single overlay artifact.

4. **Negotiate convergence on fundamental values.** Focus on the value-level causality, not tactical disagreements. Sherwood is explicit: harmony "especially as regards fundamental values." Tactical divergence is healthy; value-causality divergence is the binding constraint. Run as a facilitated session (not a memo broadcast) — convergence is a co-authored artifact, not a declaration.
   - **Facilitation script cues** (apply in sequence):
     - **Open**: "Each of you drew a CLD in Step 2. Today's task is not to pick the 'right' one — it's to identify the *fundamental-value* nodes where we still disagree and the *tactical* nodes where we already agree."
     - **Surface divergence**: "On node X, A's CLD has S; B's has O. Tell us what value belief is behind your sign — not what you'd do about it." Force-name the value, defer the action.
     - **Distinguish layer**: After each divergence is named, ask: "Is this a disagreement about *how the world works* (causal belief = converge here) or *what we should do* (tactical = leave heterogeneous)?" Mark each on the overlay.
     - **Co-author, don't decree**: Write the convergence sentence on the same canvas everyone can edit — not on the leader's notepad. Use language drawn from participants' own phrasings, not management vocabulary.
     - **Close**: Read the value-causality statement aloud; each participant says yes / no / "with this clarification". Iterate until everyone's "yes" is unforced.
   - **Exit criterion**: a written values-causality statement that every participant recognizes as their own (Rule 10), covering at least the divergent value-nodes surfaced in Step 3.

5. **Install continuous energy practices.** Schedule sustained shared-discussion time, not one-shot offsites. Active listening discipline (Sherwood p32 — passive listening fails). Repeated revisitation as new members join or context changes. Cite Nelson (Case 4 in `references/cases.md`): *years* of shared dinners, not an annual all-hands.
   - **Exit criterion**: 4-6 consecutive weekly check-ins survive without leader-prompting (team self-initiates ≥ 1 / week); active-listening-minutes proxy holds ≥ 15 min/hr; value-revisitation proxy holds ≥ 1 / week. Below these, the practice has not taken root — re-run Step 4 before declaring done.

6. **Treat leadership as the energy pump.** Leader's primary job is throughput, not decision-making. The leader surfaces dissenting CLDs in every meeting; the leader revisits values when decisions are made; the leader produces narrative artifacts that re-articulate team purpose.
   - **Halt condition**: if leader role is unfilled or rotated quarterly, the open-system metaphor cannot operate; revert to other interventions or appoint a stable energy-pump role first.
   - **Exit criterion**: leader can produce time-logged evidence of the active-listening-minutes proxy over the prior month; if they cannot, the role is nominally filled but functionally vacant.

7. **Re-surface mental models on team composition change.** Every new joiner imports their prior team's mental model; re-run the convergence work, do not assume osmosis. This step is what distinguishes Nelson (re-investment with every captain promotion) from Coopers & Lybrand (one-time speeches, no re-investment).
   - **Exit criterion**: each new joiner produces their own CLD within their first 4 weeks; Step 3 overlay is updated; values-causality statement is re-recognized (or revised) by the expanded team.

### When to compose with `cld-overlay` (hybrid)

- Post-merger / post-acquisition team formation: run `cld-overlay` first to surface between-group mental-model differences and find a straddle; run this skill second to sustain convergence among the integrated team. The straddle from `cld-overlay` becomes the seed values-causality statement input to Step 4 here.
- Cultural-change initiatives at scale: `cld-overlay` between departments to find the cross-cutting straddle; this skill within each integrated team to sustain.
- Success here looks like: `cld-overlay` finds a straddle; this skill installs the energy practices that keep the straddle from being eroded by quarter-end pressure.

## B — Boundary ★

### Do NOT use this skill when:

- **Short-term task force or one-shot delivery team** — energy investment cost exceeds payback period. Use lighter coordination mechanisms (clear roles + working agreements + retros). The convergence-negotiation overhead is justified only when the team persists across multiple quarters.
- **Remote / distributed / asynchronous teams** — the book pre-dates 2020 hybrid work; the Nelson "shared dinners over years" pattern doesn't translate to async-first cultures. The energy-pumping metaphor assumes co-presence. The four observable proxies need async-native equivalents (asynchronous mental-model documents + scheduled-but-async value-revisitation rituals) which Sherwood does not provide.
- **Psychological safety is the actual binding constraint** — if team members fear speaking up, surfacing mental models will produce performative agreement, not genuine surfacing. Fix safety first (see Edmondson's work) before applying this skill. Step 2's voluntary-participation halt condition is the safety guard, but it does not substitute for an environment where dissent is genuinely safe.
- **Cognitive-diversity-by-design teams** (red team, devil's advocate, audit, peer-review committees) — harmony is *anti-goal* here; productive friction is the point. Imposing mental-model convergence destroys the function. This skill assumes harmony serves the team's purpose.
- **Skill applied as a substitute for hiring / firing decisions** — if the team's underperformance is driven by individual capability gaps or value misalignment that cannot be harmonized, mental-model surfacing will surface the gap clearly but cannot close it.

### Author-warned failure modes

- **Exhortation anti-pattern (c19 Coopers & Lybrand)**: a leader who gives speeches about teamwork without investing continuous energy will produce a 100-individual-excellent / 0-team-coordination outcome. Speeches are not energy throughput. Cite this case whenever a senior leader proposes "one big all-hands" or "another values workshop" instead of sustained weekly+ practice.
- **Mistaking shared logo for shared mental models**: cultural artifacts (T-shirts, mission statements, all-hands decks) are decorative; without sustained CLD-level convergence work, mental models drift independently. The four proxies are the falsifiability test.
- **Annual offsite mistaken for "continuous"**: Sherwood explicitly contrasts Nelson's years of shared dinners with one-shot pep talks. An annual two-day retreat is a one-shot input to an open system that needs continuous flow.
- **Leader self-assessment as proxy data**: a leader's belief that they "spend lots of time on team-building" is not data. Only time-logged active-listening minutes counts.
- **Passive listening pretending to be active**: letting team members talk while waiting to reply is not active listening. Active listening surfaces dissenting CLDs and reflects them back (Sherwood p32).

### Author's blind spots / period limitations

- **"Mental-model harmony = best team" contradicts post-2010 research** (BOOK_OVERVIEW Unproven Assumption #4): Amy Edmondson's psychological-safety work and the cognitive-diversity literature (Page, Hong) suggest productive friction often outperforms harmony, especially on novel and complex problems. Sherwood asserts harmony from anecdote (Nelson, Coopers & Lybrand) without engaging this counter-evidence. Apply with awareness that the "harmony beats diversity" premise is empirically contested.
- **"Energy pumping" metaphor is poetic but unfalsifiable** (as Sherwood states it): there is no operational definition of how much energy, of what kind, applied how, produces what outcome. This skill imposes the four observable proxies as the falsifiability bar; Sherwood himself does not.
- **Misapplied to remote / distributed / async teams** (period limitation, 2002 publication): the book pre-dates the 2020 hybrid-work transition. Nelson's "years of shared dinners" model assumes co-presence; the same prescription delivered as Zoom calls and Slack threads produces fundamentally different dynamics. Sherwood has no advice for async mental-model convergence.
- **Consultant-rescue narrative arc** (BOOK_OVERVIEW): every Sherwood case ends with the workshop succeeding. There are no documented failed engagements where leaders invested continuous energy and the team still failed. The base-rate of success implied by the book is likely overstated.
- **Manager-as-protagonist framing** (BOOK_OVERVIEW): the energy-pump role assumes a unitary leader with intervention authority. Flat orgs, holacracy, self-managed teams (Buurtzorg, Morning Star, Valve) operate without this role and sometimes succeed — this skill's halt condition at Step 6 acknowledges the limit.

### Easily-confused neighboring methodologies

- **Tuckman's forming-storming-norming-performing**: stage model of team development; Sherwood adds the open-system / energy-throughput dynamic but inherits Tuckman's assumptions.
- **Patrick Lencioni's Five Dysfunctions of a Team**: trust-conflict-commitment-accountability-results pyramid. Overlaps but Lencioni leads with trust; Sherwood leads with mental-model alignment.
- **Amy Edmondson's psychological safety + teaming**: post-2010 empirically-grounded; directly challenges Sherwood's "harmony" framing. If choosing between models on novel / complex / R&D work, Edmondson has stronger evidence base.
- **Senge's Fifth Discipline shared-vision practice**: Sherwood inherits from Senge; Senge's "shared vision" overlaps heavily with "mental-model harmony" but emphasizes future-state imagery over causal-belief alignment.
- **OKR / commitment cascades**: tactical alignment mechanism; assumes underlying mental-model harmony rather than producing it.

## Related skills

- **depends-on `cld-craft`** — each team member's mental model is surfaced as a CLD drawn with the 12 hygiene rules + fuzzy-variable elevation discipline. Without that craft, Step 2's surfacing produces vague affinity-mapping rather than load-bearing causal beliefs.
- **depends-on `loop-and-link-primitives`** — the team-as-open-system claim depends on recognising leadership-energy → harmony → performance → reputation → leadership-energy as a reinforcing loop. Without the R/B loop ontology, the "closed-system decay" prediction is unintelligible.
- **composes-with `cld-overlay`** — paired sibling from the same Chapter 9 source. Use `cld-overlay` first for between-group conflict (find a straddle); hand off to this skill for sustained within-team convergence on the straddle's values-causality. Post-merger and cultural-change scenarios typically need both in sequence.

## Audit metadata

> Source-unit codes (f18/p18/p19/p31/p32/ce11/ce26/c11/c17/c18/c19/g09/g30/g31) refer to Stage-1.5 verified.md entries. See `<plugin-root>/references/VERIFIED.md`.

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Source units merged**: f18, p18, p19, p31, p32, ce11, ce26, c11, c17, c18, c19, g09, g30, g31
- **Distilled at**: 2026-05-11
- **Split at**: 2026-05-12 (split from `stakeholder-and-team-thinking` v0.3.0; INWARD protocol → `team-mental-model`, OUTWARD protocol → `cld-overlay`)
- **Output language**: body — English; metadata — English
