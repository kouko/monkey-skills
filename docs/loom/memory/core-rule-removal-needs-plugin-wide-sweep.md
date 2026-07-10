---
name: core-rule-removal-needs-plugin-wide-sweep
description: A load-bearing rule (e.g. writing-plans' task-sizing criterion) gets quoted/paraphrased across far more files than the one defining it — router cards, agent contracts, sibling READMEs in every shipped language, living design docs — grep the whole plugin, not just the defining skill file, before considering a removal complete
type: process
origin: PR #516 (writing-plans time-box removal, 2026-07-08) — two review rounds still caught residue after an initial "fix the SKILL.md" pass
---

Removing writing-plans' ≤5-min criterion started as an edit to one file
(`writing-plans/SKILL.md`). A repo-wide grep afterward turned up 14 MORE
files quoting or paraphrasing the same rule: the implementer agent's own
role contract (`agents/implementer.md` — its dispatch template and
BLOCKED-trigger wording), the router card and `using-loom-code/SKILL.md`
(rule #3's summary), `subagent-driven-development/SKILL.md` + its README,
`brainstorming/references/handoff-brief-format.md`, `requesting-code-review/
README.md`, and `writing-plans/README.{md,ja.md,zh-TW.md}` — every shipped
language.

Even after that sweep, **two rounds of whole-branch review still found
more**: a stale "all four criteria" count (leftover from the pre-removal
4-row table), an orphaned "structural-split escape hatch" still triggering
on the now-retired check (found *independently by both panel reviewers* —
strong corroborating signal it was a real gap, not reviewer noise), and
four MORE i18n files (`subagent-driven-development` + `requesting-code-review`
READMEs, ja + zh-TW each) that a first-pass i18n sweep had covered for one
skill but missed for two others. Living design docs (`PRODUCT-SPEC.md`,
`ROADMAP.md`) also still described the removed rule as current — these are
NOT point-in-time records like `docs/announcement/` or `docs/example-runs/`,
so they needed the same fix, unlike genuinely historical artifacts which
were correctly left untouched.

**Why:** a core rule's blast radius is invisible from the defining file
alone — every place that summarizes, translates, or exemplifies it drifts
independently, and drift compounds across languages (a fix applied to one
skill's English README doesn't imply its ja/zh-TW siblings, or a SIBLING
skill's own three-language READMEs, got the same fix).

**How to apply:** after editing a core rule's defining file, `grep -rl`
the literal phrase being removed across the WHOLE plugin (not just the
skill directory) before calling the change complete. Expect a first sweep
to still miss residue — budget for at least one whole-branch review round
specifically hunting for it, and don't be surprised when two independent
reviewers converge on the same miss (that's corroboration, not noise).
Distinguish living docs (fix them) from point-in-time archives/changelogs
(leave them — they're supposed to describe what was true when written).
