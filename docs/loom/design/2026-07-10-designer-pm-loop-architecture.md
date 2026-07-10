# Designer/PM-oriented loom loop — architecture direction

> **Type**: design discussion record → triaged architecture direction (pre-implementation)
> **Date**: 2026-07-10
> **Status**: paper dogfood COMPLETED 2026-07-10 (same day) — run, graded
> report, and produced artifact in
> `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/` (4 PASS + 1
> PARTIAL; instrument v0.1 applied). Remaining gates before ship: build
> order per BACKLOG + a cold-operator dogfood round (operator ≠ author)
> **Companion**: `docs/loom/research/2026-07-10-principles-canon-base-lists.md` (canon base lists, 4 sections, web-grounded)
> **Origin**: single session 2026-07-10, six discussion rounds (coupling → persona reframe → escalation rubric → templates → canon anchoring → complexity triage)

## 0. Goal and persona (the reframe that governs everything)

Target user: a **designer/PM** — professional in product & experience design,
some understanding of engineering structure, **not** an engineering professional.

Goal: a loop/harness system where the user's deep discussion happens at the
**front of the loom-* pipeline** (discovery → principles → interface-design →
spec) and the back (loom-code) is an **agent-autonomous zone**: engineering
architecture, implementation, and quality are judged and maintained by the
agent, with the user pulled in only for decisions that are genuinely theirs.

This reframes the original question ("should loom-code consume upstream
artifacts more strictly?") from a discipline problem into a
**division-of-labor boundary** problem.

```
 user zone (product language)   │      agent zone (engineering language)
 discovery → principles         │
   → design → spec ────────────→│ plan → build → review (auto-loop)
        ↑                       │              │
        │  escalation surface (product-stakes │
        │  language, two firing points)       │
        └───────────────────────┴─────────────┘
        acceptance surface: running product + ui-verification report
```

## 1. Four load-bearing inversions

1. **Upstream artifacts = the ONLY intent channel.** The user never reviews
   diffs; spec/design artifacts are the only path their intent reaches the
   implementation. Must-consume is not a policy preference — non-consumption
   is a severed system. Precedent for the mechanism: `ui-verification`'s
   MANDATORY-conditional + N/A-loud pattern (the family's only hard gate
   today; scan evidence in §7).
2. **Question routing is the core design problem.** Every "ask the user"
   moment classifies first: product-shaped → ask, in product language,
   possibly re-opening a design-side station; engineering-shaped → agent
   decides + records. Generalizes loom-discovery's rule: *ask whoever holds
   the ground truth* (value judgments → the user; engineering/world
   knowledge → the agent researches and decides).
3. **The upward channel is more missing than the downward one.**
   Implementation will hit spec gaps. Today the family defines only
   upstream→downstream handoffs; there is no protocol for translating an
   implementation-discovered product question back into product language.
   For a non-engineer user this absence means the agent silently guesses.
4. **The acceptance surface moves.** The user cannot judge "done" by test
   counts. Their only adjudicable surface is the product-perceivable one:
   the running app, ui-verification results, product-language completion
   reports. ui-verification is promoted from side gate to the user's main
   acceptance stage; NEEDS_REVISION review loops digest silently.

## 2. Engineering-decision escalation rubric

**Two-axis test** — an engineering decision goes to the user only when BOTH:

- **Axis A — product consequence**: affects current experience OR future
  product option space (feature possibility, cost structure, data
  availability).
- **Axis B — reversal cost**: one-way door (rework ≈ rewrite) vs two-way
  door (rework ≈ config change). (Bezos, 1997/2015 shareholder letters.)

|                       | two-way door | one-way door |
|---|---|---|
| product consequence   | agent decides; entry in product-language report; late veto possible | **escalate** (kickoff briefing) |
| no product consequence| agent decides silently; log only | agent decides + **kickoff briefing** (user decision 2026-07-10: bottom-right cell also surfaces) |

Supporting mechanisms:

- **Kickoff briefing** (開工簡報): one-way-door decisions cluster at the
  spec→plan transition; batch the round's 1-3 of them into ONE
  product-stakes briefing at plan kickoff (each option: plain-language
  stakes → 2-3 choices with product consequences → recommendation).
  Mid-implementation escalation is the exception path of the SAME
  interface, not a second protocol. Pattern (dogfood FINDING-08): when a
  one-way door is already determined by the principles, present it as a
  derivation-for-confirmation ("your principles lock this; declaring it
  writes the fact down"), not as an open option set.
- **Decision log**: every agent-decided engineering choice gets a
  product-language record ("chose X because Y; the day you want Z, this
  choice costs W"). The log is the safety net that makes delegation
  auditable and late-vetoable. Escalation is expensive; the log is cheap.
- **Per-project escalation appetite** (user decision 2026-07-10): the
  PRINCIPLES.md Engineering Principles section carries the project's
  appetite declaration; documented decisions are never re-asked
  (consistent with judgment-rubrics §3(c)).

## 3. PRINCIPLES construction flow (canon-anchored, one flow for all sections)

**Interaction model** (user decision 2026-07-10): user states their need or
direction first → agent probes and fills gaps → agent proposes **2-3 close
established theories/schools** with fit notes → user decides.

**Canon-by-default stance** (user decision 2026-07-10): anchor on
industry-established frameworks/schools rather than building bespoke,
because: anti-drift (third-party anchor survives), collaboration vocabulary,
coverage completeness (mature frameworks are stress-tested), and —
system-specific — **canon names are agent-legible contracts**: "follow HIG"
reliably activates model-internal knowledge in every downstream agent;
a bespoke ten-paragraph philosophy re-interprets (and drifts) per agent.
Machine-local auto-memory precedent (not a repo path):
`feedback_synthesized_checklist_likely_reinvents_canon`.

```
user states direction
  → agent probes (propose-then-react when stuck; menu as late as possible)
  → 2-3 canon candidates + fit/tension notes (from ≥2 distinct traditions;
    1-2 considered-but-rejected named with reasons)
  → user decides (mix allowed; bespoke sections legal — escape hatch)
  → write: base canon (version-pinned) + deviation ledger
          + product-unique trade-off principles (falsifiable)
  → read-back confirmation
```

Guardrails:

1. **Deviation ledger** — the make-or-break piece. The real risk is silent
   hybridization (pick HIG, twenty small decisions later the product is 60%
   HIG with unrecorded exceptions — the anchor is dead and nobody noticed).
   Format: base school + explicit deviation entries, each bound to a product
   principle ("we break rule X because principle Y"). Same record shape as
   the §2 decision log — ONE record format, two views (engineering decision /
   canon deviation).
2. **Fit-forcing escape hatch** — "no good canon for this aspect; this
   section is bespoke" is a legal outcome. Bespoke sections lose the
   third-party anchor and compensate with stricter falsifiability + read-back.
3. **Altitude check** — a school settles conventions and defaults; the
   product-unique trade-off tiebreakers ("onboarding speed > feature depth")
   can never come from canon. Picking a framework is *some* principles
   entries, never all of them. Guard against "picked a school = principles
   done".
4. **Version pinning** — canon drifts too (Material 2→3, HIG yearly).
   Declarations pin edition/version.

Per-section parameters (same flow, different knobs):

| section | probing depth | candidate presentation |
|---|---|---|
| Product | deepest — ground truth only in the user's head; canon frames questions, can't answer them | candidates late, after real probing |
| Design (UX/interaction + visual, two lists) | user is the expert; expect direct statement, map to canon for coverage | candidates can surface early — shared vocabulary |
| Engineering | user is non-expert; 3-5 fixed stance questions (iteration vs robustness, reversibility preference, cost posture, data/privacy posture) + tech-stack declaration slot ("delegate to agent" is a legal answer per question) | every candidate wrapped in a plain-language stakes briefing |

**Templates are menus + question sets, never pre-written principles.**
Every sentence in PRINCIPLES.md passes through user choice/statement →
agent distillation → read-back. Canned principles are unfalsifiable
boilerplate and short-circuit exactly the discussion this system exists to
host. Machine-local auto-memory precedent (not repo paths):
`feedback_frameworks_are_completeness_audits_not_generators`,
`feedback_worked_example_is_prescriptive`.

## 4. Canon base lists (agent-facing recall insurance)

User concern (2026-07-10, drove a triage revision): LLM popularity bias —
unconstrained, the agent proposes the same top-3 candidates every time and
the option space silently collapses. Resolution: ship **four base lists**
(Product / Design-interaction / Design-visual / Engineering), reframed from
the earlier DROP ("no static menus") as follows:

- Entries are **name + one-line fits-when hint + stability/version note +
  source URL** — never doctrine content (doctrine stays in the model;
  copying it re-acquires the canon-copy maintenance liability).
- **Agent-facing only**: consulted at the propose-candidates step as a
  completeness audit ("did I miss a closer tradition?"); the user still
  sees only 2-3 fitted candidates. Header says "including but not limited to".
- **Double guard against laziness**: the list buys breadth; the flow rule
  (≥2 traditions + named considered-but-rejected) buys honesty. Both ship.
- The Engineering list is consumed ONLY by the agent (autonomous decisions +
  kickoff-briefing option generation) — it does not put MVVM-tier choices
  back on the user's table.
- Lists live in `loom-product-principles/skills/product-principles/references/`
  (flat, one file per list or one combined file — decide at build time);
  research grounding in the companion research note.

## 5. Complexity triage (2026-07-10, via dev-workflow:proposal-critique)

Verdicts as recorded below: **12 KEEP + 2 KEEP-WITH-CAVEAT / 5 DEFER /
5 DROP** (the two school-menu-file DROPs — Design and Engineering — share
one line) **+ 2 merges**; one DROP (static menus) was later resurrected in
agent-facing form, see §4. Honest clause (at triage time): no item had
been dogfooded with the real persona; see Status for the same-day dogfood
outcome.

**KEEP** (one-line reasons): mid-pipeline must-consume (writing-plans ↔
change-folder; ui-verification precedent) · scenario→task coverage script
(mechanical substitute for the human code review this persona will never
do; PR#524 derivation culture) · question-routing contract (loom-discovery
ground-truth rule) · upward-flow protocol · acceptance-surface move ·
code-reviewer PRINCIPLES-existence derivation (PR#524-shaped fix) ·
two-axis test · kickoff briefing (incl. bottom-right cell) · decision log ·
per-project appetite · unified construction flow · deviation ledger +
version pin. KEEP-WITH-CAVEAT: propose-then-react probing, bespoke escape
hatch (industry intuition, n=0). Post-triage addition (user-driven,
2026-07-10): canon base lists ×4, KEEP-WITH-CAVEAT under §4 constraints.

**DEFER** (re-trigger conditions):
- Product-type question-set split (4 types) → **ship ONE generic set**;
  split when dogfood shows a type's interrogation list genuinely diverges.
- Escalation-appetite presets → extract from ≥2 real projects' authored
  appetite sections, don't invent upfront.
- Reversibility-preference principle → add when kickoff briefings routinely
  exceed 3 items/round.
- Canon version-watch trigger → first real confusion caused by a canon
  version bump.
- Per-stack agent-side convention library → when downstream agents observed
  making inconsistent same-stack choices across sessions; then per-project
  agent-authored conventions doc, NOT shipped static templates.

**DROP**: static school-menu FILES as user-facing menus (×2 — the Design
and Engineering menu files, one line here; superseded by §4's agent-facing
reframe; user-facing menus stay dead) · standalone
expert-direct-dump channel (the unified flow IS user-speaks-first) ·
expertise-probing machinery (same reason) · "gradient enforcement table" as
a standalone doc (absorbed by two-axis test + must-consume; a second doc =
second source of truth).

**Merges**: kickoff briefing + upward flow = ONE escalation interface, two
firing points. Decision log + deviation ledger = ONE record format, two views.

## 6. User decision ledger (all 2026-07-10)

1. Bottom-right cell (invisible × one-way door) also enters the kickoff
   briefing.
2. Escalation sensitivity is per-project, carried by PRINCIPLES.md
   Engineering Principles.
3. Interaction model: user states → agent probes → 2-3 canon candidates →
   user decides.
4. Canon-by-default over bespoke construction (drift anchor + collaboration
   + completeness rationale — user-articulated).
5. Ship canon base lists (4, with Design split into interaction + visual),
   as agent-facing "including but not limited to" recall insurance.
6. Document first; research notes saved for future reference; paper dogfood
   before implementation.

## 7. Current-state evidence (scan 2026-07-10)

loom-code's upstream coupling today (read-only scan): brainstorming Axis 0 =
RECOMMENDED-once (`loom-code/skills/brainstorming/SKILL.md:60-77`);
writing-plans ↔ change-folder = OPTIONAL alternate input
(`loom-code/skills/writing-plans/SKILL.md:192-208`); ui-verification =
the only MANDATORY-conditional gate; spec-reviewer binds to loom-code's own
plan doc, NOT the upstream change-folder (transitive hole: a scenario
dropped at plan-authoring time is invisible to review); code-reviewer's
principles-conformance dimension activates only if the orchestrator passes
the PRINCIPLES.md path (registration-shaped, PR#524-vulnerable).
`docs/loom/memory/` had no prior entries on this topic (clean no-hit,
recall pass 2026-07-10).

## 8. Fragile points (named, unresolved)

1. **Relevance detection for must-consume**: how does writing-plans know
   THIS change-folder corresponds to THIS task? Stale change-folders from
   past features can false-fire ambient detection; strict change-id naming
   reintroduces "user must remember". Current lean: detect + one-shot
   confirm. ui-verification never had this problem (its trigger — UI surface
   touched — is objective); the mid-pipeline signal is not.
2. **Generic question set adequacy**: the DEFER bets one Product question
   set covers 2B-tool/2C-tool/2C-consumer/platform products. Paper dogfood
   tests this first.

## 9. Next steps

1. ~~Document the architecture~~ (this file) + research notes (companion).
2. **Paper dogfood**: draft the generic question set + engineering stance
   questions; user picks a real product idea; run the §3 flow end-to-end in
   conversation. Validates: question-set adequacy, candidate breadth (does
   §4's double guard beat popularity bias), propose-then-react feel.
   (Machine-local auto-memory precedent: cheap-experiment-before-forking,
   real-dogfood-catches-semantic-bugs.)
3. Build order after dogfood: PRINCIPLES construction flow first (everything
   downstream consumes it); pipeline-hardening trio (must-consume, coverage
   script, existence derivation) is mechanical and parallelizable.
