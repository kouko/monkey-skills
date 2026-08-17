---
name: a-cold-template-probe-proves-slot-binding-not-pipeline-drift
description: A cold-reader dogfood that hands a fresh agent ONLY the template/reference file plus a seed proves whether a writer who reads that file follows the slot; it cannot reproduce the drift a full skill run shows — the spec-expansion baseline produced tables in the cold probe while real shipped proposals had prose matrix sections — so for pipeline-level drift the guarantee is a mechanical validator on the emitted artifact, and the probe's verdict must be reported as "slot binds" not "behavior fixed"
type: process
origin: branch loom-doc-container (loom-code 0.85.0, 2026-08-17) — docs/loom/dogfood/2026-08-17-artifact-table-routing-dogfood.md Probe 2
---

Probe 1 (brief Alternatives Considered) flipped 0/2 → 3/3 tables between
main's template and the branch's — the slot binds. Probe 2 (spec Phase ③
matrix sections) showed no delta: baseline sonnet already emitted tables
when Phase ③ was the only text in context, yet two shipped proposals from
real full-skill runs carried prose in exactly those sections. The
discriminating check for the spec side was `validate_spec_output.py`'s
table-or-N/A gate, which fails one of the two shipped folders.

**Why:** a two-file cold read has none of the context load, phase
sequencing, or reasoning residue a full run has; the word "matrix" alone
steers a cold writer to a table. The probe measures the template's pull
on a writer at zero context — real and useful — but not what the pipeline
emits at the end of a long run.

**How to apply:** use the cold template probe to certify slot binding
(cheap, discriminating for template changes) and say so in the report;
for "the pipeline no longer emits X", ship a mechanical check on the
emitted artifact and cite that as the evidence, or run the full skill.
Related: [[process-mechanism-dogfood-via-coldreader-real-commits]],
[[dogfood-evidence-anchors-shipped-commit]].
