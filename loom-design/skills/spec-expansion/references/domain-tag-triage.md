# Domain-tag triage — v1

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

## Station mount doctrine — spec-expansion

**Mount moment:** you are about to write the expected behavior of an edge
case or acceptance criterion (a `#### Scenario:` block, or a FLAG/KEEP call
in the Phase ③ lens layer) and that behavior is **NOT derivable** from the
seed, `PRINCIPLES.md`, or `ui-flows.md`. At that exact moment, **stop and run
the classification question above FIRST** — before drafting the scenario
text.

- **project-local** or **craft** → expand the scenario normally. Craft
  questions are already covered by this skill's existing lens checklists
  (BVA, CRUD, permissions, empty/error/loading, NFR) — no special handling.
- **domain-convention** → do **NOT** invent an answer. Write the item into
  the draft as a **tagged open question** instead of a resolved scenario:
  state what is unknown, and attach the tag `evidence_needed:
  domain-convention` in the pin's tag format. The item still appears in the
  output (in `## Blind spots — needs human/field input` or inline on the
  `#### Scenario:` it blocks) — it is deferred, never dropped and never
  silently guessed.

## Two-tier triage — SHAPING vs DEFERRABLE

Every `evidence_needed: domain-convention` tag gets triaged into exactly one
of two classes before the draft can be considered gate-ready:

- **SHAPING** — the answer would alter acceptance criteria, data semantics,
  or a state machine (e.g. how a period-labeling convention changes which
  values a field may hold, or which transition a state machine permits).
- **DEFERRABLE** — the answer is presentational, or the item may be cut
  without changing the requirement's substance.

**Gate rule:** a spec draft carrying an **unresolved SHAPING-class**
`evidence_needed: domain-convention` tag must **NOT** pass `VERIFY` (the
`validate_spec_output.py` check plus loom-code's downstream gate) unless the
tag carries an explicit `deferred: <reason>` note explaining why it is safe
to proceed unresolved. A DEFERRABLE tag never blocks the gate — it flows
downstream as a recorded open question.

## Resolution stays outside this skill (closed-world restated)

`spec-expansion` is a closed-world drafting skill (see the Executor model and
Honesty-rails sections in `SKILL.md`) and this reference does **not** change
that: **spec-expansion itself never runs WebSearch.** Resolving a
SHAPING-class domain-convention tag is explicitly **not** this skill's job —
it happens **between this draft and its gate**, driven by the orchestrator or
the user, who routes the tagged question to research (a
`loom-discovery` delegation, or the code-station's Axis-4-style research
protocol). This skill's only job is to classify, tag, and — for SHAPING
tags — refuse to let the draft pass ungated; it never fetches the answer
itself.

The structural backstop this reference depends on: even if a domain-
convention question is misclassified or never tagged here, `loom-code`'s
own reactive stall trigger (the SDD review-cap / systematic-debugging
research gate) is the last net that still forces one research pass before
any user escalation — this skill is the cheap early interception, not the
only one.
