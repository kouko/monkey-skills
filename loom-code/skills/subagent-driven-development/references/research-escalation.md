# Research escalation — v1 reactive mechanism

Source: `docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md`
(direct incident coverage: the 2026-07-16 fiscal-year incident spun 4
review rounds on a business-domain-convention question while treating it
as an engineering question — no research step existed between "review
failed twice" and "escalate to the user"). This file closes that gap for
subagent-driven-development.

## Pinned bucket vocabulary

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

## Mount doctrine — subagent-driven-development

**Trigger** (either one fires this protocol):

- The SAME unresolved question survives into a **2nd `NEEDS_REVISION`
  round** — a reviewer re-raises the identical gap after a re-dispatch
  already tried to close it.
- An implementer is about to return **`BLOCKED`** because a semantics or
  convention dispute — not a missing dependency, not broken test
  infra — is the actual blocker.

**Before acting on either trigger** → run the classification question
above, THEN walk exactly ONE route:

- **craft** → do not re-derive from memory. Open
  [`../../brainstorming/references/axis4-research-protocol.md`](../../brainstorming/references/axis4-research-protocol.md)
  and run it: WebSearch the shipped options (EN + JA minimum), cite
  sources, end in a recommendation.
- **domain-convention** → WebSearch the domain's own authorities,
  phrased in the domain's own language (EN + JA minimum — e.g. a
  US-filing question needs an EN query AND a JA query if the
  counterpart data vendor also publishes in Japanese). Cite the
  owning authority (the standard body, the regulator, the data vendor)
  by name. If the search returns nothing, document the empty result
  explicitly — do not fill the gap with an assumption.
- **project-local** → stay off the web. Check repo docs and
  `docs/loom/memory/` first; if neither answers it, the question goes
  to the user as-is. Never WebSearch a project-local question — there
  is nothing on the web to find.

**Evidence discipline**: the research this protocol produces rides the
NEXT re-dispatch (round 3) — attach the citations/route to the
implementer's re-dispatch prompt — or rides the user escalation if the
trigger was the BLOCKED path. Never escalate with zero research
attached when the question was classified craft or domain-convention;
that is exactly the failure this file exists to close.

## Cap unchanged — cross-reference-severing guard

This file adds a research step; it does not touch the escalation
mechanics. `subagent-driven-development/SKILL.md`'s **3-round cap** and
its **4th-retry** user escalation apply exactly as written there —
unchanged, unextended, unshortened. This protocol runs BEFORE that
4th-retry surface (at the 2nd same-question round, or at a
semantics/convention BLOCKED), never instead of it, and never adds a
round of its own.

## Reviewer-tag trigger — v2 addition

A third trigger joins the two above: a reviewer finding (per-task or
whole-branch) carrying an `evidence_needed:` tag. The tag pre-classifies
the bucket — the reviewer already named it — so this trigger's only job
is to VERIFY, not re-derive: if the tag's bucket is obviously wrong,
reclassify with the classification question above, then walk that
route; otherwise walk the tagged bucket's route as written above,
IMMEDIATELY — do not wait for a 2nd same-question round. Idempotency:
if this triage already ran for the SAME question (via any trigger),
do not re-run it — reuse the citations it produced.

Caps unchanged: this trigger runs BEFORE the 3-round cap / 4th-retry
escalation, exactly like the two triggers above — it does not add,
remove, or extend a round.
