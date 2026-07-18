# Knowledge triage — design-system

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

## Station mount doctrine — design-system

**Mount moment:** you are about to derive a color, type, or component
**token** whose semantic meaning is a domain convention (e.g. which color
means market "up"/"down", a sign convention for a negative value, a
period-definition-driven label) — or a TUI/CLI output convention with the
same shape — and its **correct form is NOT derivable** from `PRINCIPLES.md`
or the seed. At that exact moment, **stop and run the classification
question above FIRST** — before committing the token/convention.

## Two-tier triage — HIGH bar for SHAPING

`design-system` shares `interaction-flows`' bar: design has a downstream net
(spec's `VERIFY` gate still catches whatever design defers), so this
station's SHAPING bar is deliberately **narrower** (higher) than spec's:
only tag SHAPING when the answer would genuinely reshape the artifact, not
merely decorate it.

- **SHAPING** — the answer would alter the **flow structure**, a **state machine**, or a **semantic display convention**. Three worked examples: a **color semantic** (which color means "up" vs "down" for a market/finance feature), a **sign convention** (is a decrease shown as `-12%` or `(12%)`), or a **period definition** (fiscal vs calendar quarter). `design-system` mostly encounters the third case — flow structure and state machines are `interaction-flows`' territory — but the three-part bar stays identical across both interface-design skills so a SHAPING tag means the same thing wherever `spec-expansion` later reads it.
- **DEFERRABLE** — everything else: exact hex/spacing values, a surface
  treatment pick among equally-valid options, icon/typeface choices that
  encode no domain meaning.

**Rationale — the bar is higher than spec's.** Design can afford to defer
more because spec's gate still catches what design defers; spec's own bar is
LOW because only the expensive code-station net remains after spec. Pricing
the bar by remaining downstream nets keeps this station cheap without
losing recall.

## Routes per bucket

- **craft** or **project-local** → resolve inline (craft via the Axis 4
  research protocol reference; project-local via `PRINCIPLES.md` / this
  product's own `DESIGN.md` notes, or ask the user) — token derivation
  continues normally, no tag needed.
- **domain-convention, SHAPING-class** → do **NOT** invent a token value.
  Resolution is **routed research BEFORE `design-critic`'s verdict** — the
  orchestrator or the user routes the tagged question to research (a
  `loom-discovery` delegation, or the code-station's Axis-4-style research
  protocol). **`design-system` itself never runs WebSearch** — it is a
  closed-world drafting skill (per its Executor model) and this reference
  does not change that; its only job here is to classify and tag.
- **domain-convention, DEFERRABLE-class** → write the item into `DESIGN.md`
  as a **tagged open question** instead of a resolved token, carrying
  `evidence_needed: domain-convention` in the pin's tag format. This flows
  downstream: `loom-spec`'s spec-expansion Phase ③ intake inherits tagged
  open questions from the design seed, so a deferred item is never dropped —
  only handed to the next station.

## Cross-severing guard — critic verdict vocabulary unchanged

This reference does not add or change any verdict value. `design-critic`'s
two-valued verdict (`PASS_WITH_NOTES` / `NEEDS_REVISION`) is **unchanged** —
the `evidence_needed` tag is informational metadata on a finding or open
question, never a third verdict state.
