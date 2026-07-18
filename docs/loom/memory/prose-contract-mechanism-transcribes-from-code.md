---
name: prose-contract-mechanism-transcribes-from-code
description: When plan/protocol prose names a MECHANISM (a formula, a status value, a field) the wording must be transcribed from the shipped code's schema, not from research/industry vocabulary — industry terms drift from the machine reality and weak-model consumers execute the wording literally
type: gotcha
origin: memo quarterly-KPI wiring slice, T5/T8 review rounds (feat-memo-quarterly-kpi-wiring, 2026-07-18)
---

Industry research supplies the right POLICY vocabulary ("implied Q4 = FY
minus first three quarters", "withheld data"), but binding prose contracts
(plan task text, protocol rules, CHANGELOGs) that name a mechanism must
carry the CODE's mechanism, verified by reading the producer. In one branch
reviewers caught three instances of research vocabulary contradicting the
shipped schema: footnote formula written "FY − ΣQ1-3" where the code derives
FY − 9mo-YTD cumulative (different under restatement); a "WITHHELD feed"
handling rule for an arm whose contract is TRUSTED-or-refused with no
WITHHELD state; and a CHANGELOG claiming a gaps↔coverage_flags
"reconciliation that blocks the memo" that no code performs. The plan itself
seeded two of the three — the implementer faithfully copied an imprecision
the plan author imported from Axis-4 research prose.

**Why:** downstream consumers of these contracts are weak-model agents that
execute wording literally — a named-but-nonexistent status invites fabricated
handling paths, and a wrong formula footnote misstates provenance on real
memo numbers. Research vocabulary is calibrated to human readers; contract
prose is calibrated to executors.

**How to apply:** before a mechanism name (formula / status / field /
structure) lands in a plan task, protocol rule, or CHANGELOG entry, open the
producer code and transcribe its actual contract (field names, status
values, derivation basis, structure split) — the same discipline as
[[critic-finding-is-hypothesis-until-code-recon]] but at AUTHORING time, on
the plan/doc side. Where the feed carries its own self-describing string
(e.g. a dqc.reason), prescribe verbatim transcription of that string instead
of paraphrasing it. Grep-level acceptance for such prose should pin the
code-true tokens (e.g. "9mo-YTD" present, "ΣQ1-3" absent).
