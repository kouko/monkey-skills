---
name: eval-oracle-tokens-stable-fragments
description: Substring-matched eval-oracle tokens must be the shortest distinctive stable fragment (surname / product name) with |-alternatives for alias-language-case variance — full names break on translation, spacing, word order; and a miss's class (form vs genuine drop) must be re-derived per run, never carried over from an earlier run
type: practice
origin: branch feat-replay-oracle-calibration (2026-07-11) — 3 calibration rounds over 18 replay artifacts
---

Calibrating substring-matched oracle tokens against non-deterministic LLM
replay artifacts converged on two rules across 18 artifacts:

1. **Stable fragments, not full names.** Full canonical names broke on:
   translation (「Nielsen 十項可用性啟發法則」), spacing (`Hexagonal /
   Ports & Adapters`), word order (`Hexagonal Architecture / Ports &
   Adapters`), quote style (MUJI「空無」), inserted words (「預約記錄的
   法律保留期限」), and case ("cost appetite"). The shortest distinctive
   fragment (`Nielsen`, `Kenya Hara`, `SLA`) survived every observed
   variant; `alt1|alt2` alternatives absorb alias/language/case pairs.
   Trade-off: very short tokens can false-NEGATIVE by matching unrelated
   text (a `Qt` hit in another row's version cell) — that under-reports,
   never false-alarms, and is acceptable for eval semantics.

2. **Re-derive miss classes per run.** A token classified "genuine drop"
   in run 1 was silently a form-mismatch in runs 2-3 (the artifact DID
   anchor the canon, spaced differently) — carrying the earlier
   classification forward inflated the measured drop signal and was only
   caught by an independent whole-branch reviewer re-grading from disk.

**Why:** replay language/phrasing is non-deterministic, so token form
fragility and drop composition both shift run to run; a calibration
claim ("all remaining misses are genuine") is only as good as the run it
was re-verified against.

**How to apply:** when authoring or fixing oracle tokens, pick the
shortest fragment that is distinctive in its checked scope, add
`|`-alternatives for observed variants, and cite the evidencing artifact
in an adjacent note. When accepting a miss as "genuine drop", grep THAT
run's artifact for the token's stem before classifying — never reuse a
prior run's classification.
