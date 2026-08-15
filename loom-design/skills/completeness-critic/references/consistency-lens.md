# Cross-layer consistency lens — proposal.md vs spec.md

Not one of the five/six persona lenses (`## The multi-lens critic panel`) —
this is a **mandatory cross-artifact check** you run yourself at the
consolidation step (`## Consolidate the panel union before writing back`),
because that is the moment you already hold both `proposal.md` and
`specs/**/spec.md` side by side.

**Input view:** `proposal.md`'s FLAG / open-question items — especially any
`evidence_needed: domain-convention` tag (see
[`../spec-expansion/references/domain-tag-triage.md`](../spec-expansion/references/domain-tag-triage.md))
— as the SOURCE of what is still unresolved; every `### Requirement:` body +
scenario in `spec.md` as the TARGET to check against it.

**The question — omission, not inconsistency:** for each proposal-level open
question, does any requirement in `spec.md` silently RESOLVE it — state as
settled fact (a MUST/SHALL clause, a hardcoded value, a specific rule)
something the proposal itself marked unresolved? If yes, the requirement
OMITTED carrying the open question forward (or omitted phrasing itself to
hold under either answer). That is an **OMISSION finding** under this
critic's mandate — the missing piece is the disclosure, not the
requirement's existence. Inconsistency-hunting for its own sake stays out of
scope (Spec Kit's job); this lens only fires when the resolution is silent.

**Real failure this catches** (leg-1 haiku dogfood — see
`docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`
"Severity-high" bullet): `proposal.md` flagged "Which date controls monthly report bucketing?"
as an open question tagged `evidence_needed: domain-convention`, while
`spec.md`'s REQ-002 stated "The system MUST ... only aggregate settled trades into positions"
— a silent, unflagged settlement-basis answer to that exact open question,
invisible to any implementer who reads requirements and never opens the
proposal.

**Severity:** default **3 (load-bearing)** — an invented answer leaking into
the normative layer is exactly the failure class the whole knowledge-triage
mechanism exists to intercept. Downgrade only when the resolved fact is
craft or project-local (never domain-convention) and clearly low-stakes.

**Write-back:** a finding here becomes a `## Blind spots` entry naming the
contradiction AND, where concrete, a `critic-found` re-seed rephrasing the
requirement to hold under either answer with the open question tagged
inline — fed into the same consolidated, ranked set the panel produces, not
a parallel output channel.
