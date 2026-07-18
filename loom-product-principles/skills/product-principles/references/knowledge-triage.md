# Knowledge triage — product-principles

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

## Station mount doctrine — product-principles

**Mount moment:** you are about to write a principle's `— check:` clause
(Step 5, `## Product Principles` / `## Design Principles` /
`## Engineering Principles`) and making that check falsifiable requires
**guessing a fact** you have not verified — the check would assert or
depend on something no one in the room actually knows. At that exact
moment, **stop and run the classification question above FIRST** — before
writing the check clause.

- **craft** → no special handling. This bucket is already covered by the
  skill's existing completeness audit — the four `references/canon-*.md`
  lists consulted in Step 3 — because a craft fact is, by definition,
  settled by technology-neutral literature the canon lists already draw
  from. Do not restate that audit here; just run it.
- **domain-convention** → do **NOT** guess the fact to keep the check
  falsifiable. Route the question through this skill's **existing punt
  channel** — the Tripwire in the Procedure section ("route to
  `using-loom-discovery` (user-insights) for evidence-backed needs mapping
  first") — attaching the tag `evidence_needed: domain-convention` in the
  pin's tag format. The principle stays **DRAFT**: it does **not** ship
  into `PRINCIPLES.md` as a resolved entry. Record it instead as a
  `## Open Questions` entry (format per `references/principles-rules.md`
  §Optional section — `## Open Questions`: the `— re-trigger:` marker
  names when evidence is expected back), with the `evidence_needed:` tag
  appended on the same entry. Two ways it stops being DRAFT: (a) the
  routed evidence returns and the check can be written for real, or (b)
  the user explicitly accepts the guess as a stated assumption — in that
  case the principle MAY ship, but its `— check:` line MUST also carry an
  `— assumption: <reason>` marker (same em-dash/lowercase/colon idiom as
  `— check:` / `— reason:` / `— re-trigger:`) recording what was assumed
  and why, so a later reader can find and re-verify it.
- **project-local** → resolve from repo docs, `docs/loom/memory`, or by
  asking the user directly. Never WebSearch a project-local fact.

**Standing posture.** This station fires **during drafting**, every time a
`— check:` clause is about to be written — it is not gated behind a
retry/stall counter the way a reactive net is. The constitution is a
**one-way door**: an unverified domain-convention fact baked into a
`PRINCIPLES.md` check propagates as governing truth into every downstream
station (design, spec, code) before anyone would think to question it
again, so interception belongs here, at first-write, not later.

**Cross-severing guard (this file changes nothing structural).** This
reference does not add, replace, or loosen the skill's structural
validator (`scripts/validate_principles_output.py`) — the `— check:`
lexeme, entry-count, and section rules it enforces are untouched. It also
does not add an external runtime: per the Executor model, this skill has
**no** API key and **no** live research capability of its own — research
(WebSearch, domain-source lookups) happens **only** downstream, inside
`using-loom-discovery`, never inside this drafting station.
