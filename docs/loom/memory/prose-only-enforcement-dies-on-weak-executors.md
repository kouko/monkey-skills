---
name: prose-only-enforcement-dies-on-weak-executors
description: Weak executors preserve whatever a deterministic validator checks and lose whatever only prose demands — vocabulary survives, enforcement semantics (tier consequences, disclosure duties, provenance honesty) die; when a contract must hold on the weak tier, encode its CONSEQUENCES as validator/pre-check code, and keep prose as the explanation, not the enforcement
type: practice
origin: knowledge-triage v2.1 arc (2026-07-18) — three haiku live legs + fresh re-runs; dogfood report docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md
---

Three weak-model (Haiku 4.5) live runs of freshly-shipped skills all kept
the headline rules (flag the domain landmine, use the pinned vocabulary)
and all broke a prose-only obligation, each differently: invented enum
values once (intermittent), dropped or INVERTED the SHAPING tier's
blocking consequence (systematic — reproduced three times across spec and
design stations), and fabricated seed provenance in an Anchors table.
The natural control: within the SAME principles artifact, every dimension
the structural validator checked survived and every prose-only duty died.
After mechanizing the consequences (validator whitelist, structural
tier-label checks, --seed provenance, critic literal pre-check), a fresh
weak run either complied honestly or died loudly at validation — the
quietly-wrong state stopped existing.

**Why:** prose contracts are executed by attention, and weak-tier
attention keeps labels but drops the label's consequences. A gate whose
consequence lives only in prose trains downstream stations on silently
non-conformant artifacts.

**How to apply:** when shipping a contract that weak executors will
run (drafting skills, headless pipelines, batch workers): (1) split it
into vocabulary (names/labels) and consequences (what blocks, what must
co-occur, what needs a reason); (2) every consequence gets a
deterministic carrier — validator check, critic literal pre-check, CI
grep — with the real weak-run failure as its RED fixture; (3) grep-able
labels must be LITERAL artifact obligations (a checker cannot grep a
classification that lives in the reader's head); (4) prose keeps the
why, never the enforcement. Cold-reads and equivalence gates do NOT
substitute — they test comprehension, not execution under weak
attention. (Extends [[pipeline-enforced-gates-beat-drafter-instructions]]
from one skill's drafting obligation to the general contract-shipping
rule.)
