---
name: a-worker-that-blames-preexisting-state-is-often-naming-its-own-damage
description: A dispatched worker reporting "that failure was already there / out of my scope / a sibling did it" is making a causal claim it did not measure — four such claims in one arc were all wrong, each maskable only because the orchestrator held a pre-dispatch baseline; take the baseline before dispatching and diff against it, never accept the attribution
type: practice
origin: loom-design-merge (6 plugins → 2 consolidation, parts 1-3, 2026-08-16/17)
---

Across one migration arc, four workers reported a failure as not-mine. Every
one was wrong:

| Claim | Reality |
|---|---|
| "The remaining failures are pre-existing content gaps, out of my scope" | A systematic path-depth bug inside its own scope that it had fixed only in the files it happened to touch |
| "Blueprint row corrected, GREEN grep clean" | The same wrong claim appeared in three places; its RED/GREEN pinned one string, so two survived and now contradicted the fixed one |
| "That suite's 1 failure predates my edits" | Caused by a SIBLING task in the same wave, which had trimmed a skill description and dropped a trigger phrase a guard asserted |
| "Sibling agents are editing my files, should I skip those directories?" | Those agents had completed long before; a finished agent's name lingers in listings and holds nothing |

**Why the claim is structurally unreliable.** A subagent sees the repo only
from its own dispatch onward. It has no pre-dispatch baseline, and in a
parallel wave it cannot distinguish "was already failing" from "a sibling
broke it ten seconds ago" from "I broke it and the symptom surfaced
elsewhere." So the not-mine attribution is a guess presented as a finding —
and it is the one kind of finding that, if believed, ends the investigation.

**The cheap defense.** Measure and record the baseline BEFORE dispatching —
per-suite pass/fail counts, not a global impression. Then a worker's
"pre-existing" is checkable in one command instead of being taken on trust.
In this arc the baseline is what turned "pre-existing, unrelated" into "a
sibling deleted a Japanese trigger phrase, so Japanese user-research asks no
longer reach the router" — a real user-facing defect that would otherwise
have shipped.

**Corollary for the dispatch packet.** Ask for measurements, not
attributions: "report each suite's count before and after your edits" beats
"report any pre-existing failures." The first is verifiable; the second
invites the guess. Related:
[[a-mechanical-check-can-go-green-by-skipping]].
