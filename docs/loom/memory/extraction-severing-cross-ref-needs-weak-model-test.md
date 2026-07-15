---
name: extraction-severing-cross-ref-needs-weak-model-test
description: Extracting a rule to a reference file can sever its PROXIMITY to a cross-referenced rule in the body — a strong-model equivalence gate still passes (it reconstructs the link), but a weak model loads the extracted rule and drops the connection. Weak-model cold-read is mandatory, not optional, for any extraction-based skill slim that separates a rule from a rule it depends on
type: gotcha
origin: branch slim-loom-code-brainstorm-finishing — loom-code 0.31.2 (brainstorming + finishing token slim, 2026-07-16)
---

Slimming `finishing-a-development-branch` moved its "When NOT to use"
exemption table out to `references/when-not-to-use.md`. In the inline
(baseline) skill, the "Trivial direct-to-main" exemption sat in the same
file as the Phase 3 "git-memory P3-D MANDATORY" rule and the Red-Flags
"don't bother with git-memory" row, so a reader saw both in proximity and
correctly concluded git-memory survives the exemption. After extraction,
the exemption reference said nothing about git-memory.

The **sonnet equivalence gate PASSED** this (3 test-prompts ×
baseline/candidate × 3-judge; it even rated the slimmed version *more*
correct) — a strong model reconstructs the cross-reference from the
still-present P3-D rule in the body. But a **haiku cold-read of the same
scenario FAILED**: it loaded the extracted exemption and wrongly waived
`dev-workflow:git-memory` entirely, while baseline haiku (inline) kept it
mandatory. The extraction had severed the proximity the weak model
depended on.

**Why:** a strong model treats a pointer as "load and reconcile with the
rest of the contract"; a weak model treats the file it loaded as the whole
answer. Physical adjacency of two coupled rules is load-bearing for weak
readers, and an output-equivalence gate run entirely on strong models is
structurally blind to its loss.

**How to apply:**
- Before shipping any extraction-based slim, ask: does the extracted block
  depend on, or get depended on by, a rule that stays in the body? If yes,
  it is a cross-reference-severing extraction.
- For those, run a **weak-model (haiku) cold-read** of a scenario that
  forces both rules to interact — compare candidate vs the inline baseline
  on the SAME weak tier. A strong-model equivalence gate does NOT
  substitute (it passed this one).
- Fix a severed link by carrying the cross-reference INTO the extracted
  file AND naming it in the body pointer (here: when-not-to-use.md +
  the SKILL.md pointer both state "these exemptions NEVER waive
  git-memory"). Re-verify on the weak tier.

Related: [[cold-read-and-adversarial-review-catch-different-failures]],
[[equivalence-gate-verifies-behavior-not-facts]],
[[preamble-wording-is-contract-surface]].
