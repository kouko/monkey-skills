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

The pin above is transcribed verbatim from the plan that set the vocabulary, so it still names the pre-1.0 **Axis 4 research protocol** for the craft bucket. Under loom 1.0 that protocol is gone: route a craft question to the technology-neutral literature yourself (patterns, framework docs, EN + JA minimum) and cite what overruled you.

SHAPING never ships as non-blocking: it either resolves before this station's gate or carries `deferred: <reason>`.

Every tagged open question written into DESIGN.md must carry a literal `SHAPING` or `DEFERRABLE` label alongside its `evidence_needed:` tag.

## Station mount doctrine — design-system

**Mount moment:** you are about to derive a color, type, or component
**token** whose semantic meaning is a domain convention (e.g. which color
means market "up"/"down", a sign convention for a negative value, a
period-definition-driven label) — or a TUI/CLI output convention with the
same shape — and its **correct form is NOT derivable** from `PRINCIPLES.md`
or the user's own words in the interview. At that exact moment, **stop and
run the classification question above FIRST** — before committing the
token/convention.

## Two-tier triage — HIGH bar for SHAPING

Design has a downstream net — `write-spec`'s gate, and the review station
after it, still catch whatever design defers — so this tool's SHAPING bar is
deliberately **narrower** (higher) than spec's: only tag SHAPING when the
answer would genuinely reshape the artifact, not merely decorate it.

- **SHAPING** — the answer would alter the **flow structure**, a **state machine**, or a **semantic display convention**. Three worked examples: a **color semantic** (which color means "up" vs "down" for a market/finance feature), a **sign convention** (is a decrease shown as `-12%` or `(12%)`), or a **period definition** (fiscal vs calendar quarter). `design-system` mostly encounters the third case — flow structure and state machines belong to the spec's `## UI flows` section — but the three-part bar is stated in full here so a SHAPING tag means the same thing when `write-spec` later reads it.
- **DEFERRABLE** — everything else: exact hex/spacing values, a surface
  treatment pick among equally-valid options, icon/typeface choices that
  encode no domain meaning.

**Rationale — the bar is higher than spec's.** Design can afford to defer
more because spec's gate still catches what design defers; spec's own bar is
LOW because only the expensive code-station net remains after spec. Pricing
the bar by remaining downstream nets keeps this station cheap without
losing recall.

## Routes per bucket

- **craft** or **project-local** → resolve inline (craft against the
  technology-neutral literature, per the note under the pin; project-local
  via `PRINCIPLES.md` / this product's own `DESIGN.md` notes, or ask the
  user) — token derivation continues normally, no tag needed.
- **domain-convention, SHAPING-class** → do **NOT** invent a token value.
  Resolution is **routed research BEFORE the review station's
  design-conformance verdict** — the orchestrator or the user routes the
  tagged question to research; `design-system` never routes it itself. **`design-system` itself never runs WebSearch** — it is a
  closed-world drafting skill (per its Executor model) and this reference
  does not change that; its only job here is to classify and tag.
- **domain-convention, DEFERRABLE-class** → write the item into `DESIGN.md`
  as a **tagged open question** instead of a resolved token, carrying
  `evidence_needed: domain-convention` in the pin's tag format. This flows
  downstream: `loom-design`'s `write-spec` reads `DESIGN.md` and inherits
  the tagged open questions `DESIGN.md` itself carries, so a deferred item is
  never dropped — only handed to the next station.

## Cross-severing guard — review verdict vocabulary unchanged

This reference does not add or change any verdict value. The review station's
verdict (`PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION`) under the
design-conformance lens is **unchanged** — the `evidence_needed` tag is
informational metadata on a finding or open question, never a verdict state
of its own.
