# Kickoff briefing — escalation interface at plan handoff

> Companion to [`../SKILL.md`](../SKILL.md) §Self-review. Fires after
> `plan-document-reviewer` returns PASS, before handoff to
> `subagent-driven-development` (SDD).
>
> This file is the **interface SSOT** for engineering-decision escalation.
> SDD's mid-implementation ask paths point back at this same file (§f) —
> one interface, two firing points. Design SSOT for the rubric itself:
> `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md` §2
> (:64-97) + §5 (:227 merge decision — "ONE escalation interface, two
> firing points") + §6 item 1 (:232 bottom-right-cell surfacing
> decision). This file cites that rubric's operative test; it does not
> restate its rationale.

## (a) The two-axis test

An engineering decision in the plan escalates to the user only when it
clears **Axis B — reversal cost**: is it a **one-way door** (rework ≈
rewrite) or a **two-way door** (rework ≈ config change)? (Bezos,
1997/2015.) Axis A — **product consequence** (affects current experience
or future product option space) — decides *how* a decision is recorded,
not *whether* a one-way-door decision gets briefed:

| | two-way door | one-way door |
|---|---|---|
| **product consequence** | agent decides; entry in the product-language report; late-vetoable | **escalate — kickoff briefing** |
| **no product consequence** | agent decides silently; log only | agent decides + **kickoff briefing** (user decision 2026-07-10: bottom-right cell also surfaces) |

**Net collection rule**: any **one-way-door** decision briefs (both
right-column cells); every **two-way-door** decision never briefs — it
routes to the plan's `## Decision Log` instead (§e). Do not restate this
table's rationale elsewhere; cite this section by pointer.

## (b) Collection step

After `plan-document-reviewer` returns PASS on the plan — and before
handing off to SDD — sweep every task in the plan for one-way-door
engineering decisions using the test in §a. Expect **1-3 hits** per
round (design SSOT precedent). Two-way-door decisions are NOT collected
here; they route silently to the Decision Log (§e).

## (c) ONE batched briefing

Batch the round's 1-3 one-way-door hits into **ONE** briefing — never
one ask per decision. Format authority: `dev-workflow:brief-before-asking`
(pointer — load that skill's 6-block structure; do not copy it here).
Per decision inside the batch:

1. **Plain-language stakes** — what changes for the product/user if this
   choice goes one way vs the other, in non-engineer language.
2. **2-3 options**, each with its product consequence (not an abstract
   engineering trade-off).
3. **A recommendation** (a lean, not "up to you" — per brief-before-asking
   Block 5).

**Derivation-for-confirmation framing**: when `docs/loom/PRINCIPLES.md`
already locks the choice, present it as *"your principles already decide
this — declaring it writes the fact down,"* not as an open option menu
(dogfood FINDING-08, architecture doc §2). Turn-ordering rule from
brief-before-asking applies unchanged: the briefing lands as turn-final
text with the ask inline right after — never bury it under an
`AskUserQuestion` in the same turn.

## (d) Appetite read

Before briefing, grep the **target repo's** `docs/loom/PRINCIPLES.md` for
the phrase `escalation appetite`, bounded to the region between the
`## Engineering Principles` heading and the next `##` heading. Landing
shape (what the entry looks like, how it's scoped) is owned by
`loom-product-principles/skills/product-principles/references/principles-rules.md`
§Escalation appetite — landing shape — follow that scoped-grep contract
exactly; do not re-derive it here.

Read the entry **once**, apply its dial, **never re-ask** — a documented
decision beats re-asking (judgment-rubrics §3(c): "the answer is not
already recorded... a documented decision beats re-asking; cite it
verbatim instead").

**No `PRINCIPLES.md`, or no entry found** → default: brief **all**
one-way-door hits from §a/§b. Never silently suppress a briefing because
the appetite read came back empty.

## (e) Decision Log routing

Two kinds of decision land in the plan's `## Decision Log` instead of a
briefing:

1. **Delegated back** — during the batched briefing, the user says
   "you decide" on a specific item.
2. **Below-threshold** — any decision that fails the one-way-door bar in
   §a (both two-way-door cells).

Record shape is owned by
[`plan-format.md` §`Decision Log` plan section](plan-format.md) —
pointer only, do not restate the entry format here. The **SDD
orchestrator** is who actually appends entries during execution (SDD's
own Decision Log maintenance clause); this file only defines which
decisions route there.

## (f) Mid-implementation escalation — same interface, exception firing point

An engineering decision discovered **mid-implementation** (an implementer
report surfaces it, not at kickoff) is not a second protocol — it is the
**exception firing point of this SAME interface**, applying the identical
two-axis test from §a. Owned by
`subagent-driven-development/SKILL.md` §Asking the user gate ① (its
product-consequence refinement) and its Decision Log maintenance clause —
pointer only; this file does not restate SDD's mechanics.

**One interface, two firing points**: kickoff (this file — batch
collection at plan handoff, §b-§c) and mid-implementation (SDD — one
decision at a time, as discovered). Both consult §a for whether a
decision escalates.

## Worked micro-example

A 3-task plan for "add user preference sync" passes `plan-document-reviewer`.
Sweeping the tasks (§b):

- **Task 2** chooses the preference-sync backend: a third-party SSO
  provider (vendor lock-in — undoing it means re-authenticating every
  user and rewriting the auth flow: **one-way door**) vs. self-hosted
  encrypted storage (swappable via config: **two-way door**). This has
  clear product consequence (privacy promise, vendor dependency) AND is
  one-way-door → top-right cell → **collected for the kickoff briefing**.
- **Task 3** names an internal cache-key variable — no product
  consequence, trivially reversible → bottom-left cell → **agent decides
  silently; one Decision Log entry, nothing surfaced to the user** (§a's
  table: both two-way-door cells route to the Decision Log — only the two
  right-column one-way-door cells brief; the top-left
  product-consequence×two-way cell's Decision Log entry is late-vetoable,
  this bottom-left cell's is not).

Only Task 2's decision batches into ONE kickoff briefing (§c): Mental
Model in plain language ("who runs the login you'll depend on"), 2
options with product consequences, a recommendation, phrased per
`dev-workflow:brief-before-asking`. If `docs/loom/PRINCIPLES.md` already
states an engineering stance on third-party auth, present Task 2 as a
derivation-for-confirmation instead of an open menu (§c).
