# Knowledge triage — interaction-flows

```
Three buckets — a stuck question's bucket decides where its answer
lives. Classify ONCE, walk ONE route (triage, not checklist):

- **craft** — engineering practice. The answer is the same in any
  industry; it is overruled by technology-neutral literature
  (patterns, framework docs). Route: the Axis 4 research protocol.
- **domain-convention** — the business domain's rule. The answer is
  owned by an authority OUTSIDE the code (industry standard,
  regulator, data-vendor convention). Route: search domain sources,
  phrased in the domain's own language (EN + JA minimum), cite the
  owning authority.
- **project-local** — a fact of this repo/product only. It is not on
  the web at all. Route: repo docs / `docs/loom/memory` / ask the
  user. Never WebSearch this bucket.

Classification question: "Who can overrule this fact — engineering
literature (craft), a domain authority outside the code
(domain-convention), or only this project's own docs and people
(project-local)?"

Tag format for findings and open questions:
`evidence_needed: craft | domain-convention | project-local`.

Classification is itself fallible — structural backstops (round caps,
gate rules) still apply when it errs.
```

## Station mount doctrine — interaction-flows

**Mount moment:** you are about to draft a flow, a state transition, or a
display element (dimension 2 user-flows, dimension 4 transitions, or a
render-variant / label choice touched by dimension 1 or 3) and its
**correct form is NOT derivable** from `PRINCIPLES.md` or the feature seed.
At that exact moment, **stop and run the classification question above
FIRST** — before drafting the flow/state/display text.

## Two-tier triage — HIGH bar for SHAPING

`interaction-flows` sits closer to `design-critic`'s gate than `spec-expansion`
sits to its own — design has a downstream net (spec's `VERIFY` gate still
catches whatever design defers), so this station's SHAPING bar is
deliberately **narrower** (higher) than spec's: only tag SHAPING when the
answer would genuinely reshape the artifact, not merely decorate it.

- **SHAPING** — the answer would alter the **flow structure**, a **state machine**, or a **semantic display convention**. Three worked examples: a **color semantic** (which color means "up" vs "down" for a market/finance feature), a **sign convention** (is a decrease shown as `-12%` or `(12%)`), or a **period definition** (fiscal vs calendar quarter). These reshape what the artifact says, not just how it looks.
- **DEFERRABLE** — everything else: copy wording, spacing/density choices,
  icon picks, and any convention question that does not change which
  surfaces exist, how they transition, or what a value semantically means.

**Rationale — the bar is higher than spec's.** Design can afford to defer
more because spec's gate still catches what design defers; spec's own bar is
LOW because only the expensive code-station net remains after spec. Pricing
the bar by remaining downstream nets keeps this station cheap without
losing recall.

## Routes per bucket

- **craft** or **project-local** → resolve inline (craft via the Axis 4
  research protocol reference; project-local via `PRINCIPLES.md` / this
  change's own `ui-flows.md` notes, or ask the user) — drafting continues
  normally, no tag needed.
- **domain-convention, SHAPING-class** → do **NOT** invent an answer.
  Resolution is **routed research BEFORE `design-critic`'s verdict** — the
  orchestrator or the user routes the tagged question to research (a
  `loom-discovery` delegation, or the code-station's Axis-4-style research
  protocol). **`interaction-flows` itself never runs WebSearch** — it is a
  closed-world drafting skill (per its Executor model) and this reference
  does not change that; its only job here is to classify and tag.
- **domain-convention, DEFERRABLE-class** → write the item into `ui-flows.md`
  as a **tagged open question** instead of a resolved flow/state, carrying
  `evidence_needed: domain-convention` in the pin's tag format. This flows
  downstream: `loom-spec`'s spec-expansion Phase ③ intake inherits tagged
  open questions from the design seed, so a deferred item is never dropped —
  only handed to the next station.

## Cross-severing guard — critic verdict vocabulary unchanged

This reference does not add or change any verdict value. `design-critic`'s
two-valued verdict (`PASS_WITH_NOTES` / `NEEDS_REVISION`) is **unchanged** —
the `evidence_needed` tag is informational metadata on a finding or open
question, never a third verdict state.
