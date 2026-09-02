# A/B results — prose-edit self-sweep (implementer rule 14)

Date: 2026-09-01 · Run after `protocol.md` was registered. 16 draft
generations (4 cases × 2 arms × 2 reps, implementer sonnet, contract varying
only by rule 14) + 16 blind docs-reviewer judgings + blind cause-labelling +
the shipped `prose_selfsweep_tally.py` instrument.

## Headline

**No measurable benefit. On the primary metric the raw count went the wrong
way.** Per-arm tally (from `prose_selfsweep_tally.py`, cause-labelled blind):

| metric | Arm A (no rule 14) | Arm B (rule 14) |
|---|---|---|
| runs | 8 | 8 |
| first-round gating findings (instruction-class) | 4 | 7 |
| — of which cause A (stale-neighbour) | 3 | 6 |
| — cause E / J | 1 / 0 | 0 / 1 |
| hedge marks | 0 | 0 |
| draft tokens (mean) | 16148 | 16181 |
| review rounds (mean, proxy) | 1.2 | 1.2 |

Metrics 3 (draft tokens) and 4 (hedge) are flat null. Metric 1 (findings) is
null-to-adverse: rule 14 did not reduce first-round preventable findings.

## The result that matters more than the count

**Firing ≠ catching.** Arm B implementers confirmed behaviorally that they ran
rule 14's sweep (6 of 8 said so and described the grep) — yet those same drafts
still shipped cause-A stale-neighbour defects (case 1 both B reps left the
`替代方案`/`單向門`/`出典` bullets resting on the corrected-away cause), and one
(case 4 rep1) introduced a *new* self-contradiction its own edit created
("reclaim touches only the claim line" vs the unchanged "noting the takeover in
the ticket body"). The sweep being executed and the draft being consistent are
decoupled: a silent instruction to "grep restatements and fix each" did not, on
this evidence, make a weak model actually reconcile the neighbours.

## Confounds — why this is weak evidence, not a clean refutation

1. **Spoon-fed tasks.** All four cases are reconstructed from merged fix
   commits, so the task text already enumerates the restatements to fix ("three
   occurrences of 8.91 plus two same-claim restatements"). This mutes rule
   14(a)'s discovery advantage — the place it would bite is an *un-named*
   restatement, which only case 2 (`蓋滿正交視野` / `icon 保持正交俯視`, never
   named by the task) and case 3 (the `Aggregate verification` sibling field)
   actually contained.
2. **case 2 Arm B never fired.** Both case-2 Arm-B drafts declined to run the
   sweep, reading rule 14's trigger ("every file in your `Files touched`") as
   requiring a literal `Files touched:` plan field the dispatch did not supply
   verbatim. So the one multi-file case — the best test of 14(a) — produced no
   A/B contrast. This is both a dispatch-wording inconsistency (the case-2
   prompt said "edits THREE .md files" not "Files touched:") AND a real finding:
   rule 14's trigger is literal-string-fragile (the docs-review D1 finding,
   confirmed behaviorally).
3. **Record-class N/A.** docs-reviewer's own scope contract makes `docs/**`
   files record-class and out of jurisdiction; only case 4 is contract-class.
   15 of 16 judges reviewed anyway; 1 (run15, case 1) correctly declined as
   N/A. Judge behaviour on the wrong artifact class is inconsistent = noise, and
   run15's decline halved case 1's Arm-A scored sample.
4. **n = 2, cause-A-dominated, high variance.** 9 of 11 instruction findings are
   the same stale-neighbour class surfacing or not essentially per-draft; two
   reps cannot separate that from signal.

## Pre-registered candidate explanations (from protocol.md, chosen before data)

- **List-position attention decay** — rule 14 is rule 14 of 14; a top-to-bottom
  reader may weight it least. Consistent with "fired but didn't catch."
- **Placement-variant (e)** — move the sweep out of the numbered list into a
  standalone `## Prose-task duties` section. The registered follow-up.

## What a cleaner re-run needs (not done here)

Fix the trigger to fire on the task's actual `.md` file set (not a literal
field name); draw cases that are contract-class AND carry un-named
restatements; use first-draft-from-seed tasks, not reconstructed fixes; more
reps. Until then, "no measurable effect" stands as the honest, confounded
result — and per the brief's conditional-reversal clause, whether rule 14 ships
or is dropped is a user decision recorded in the plan's Decision Log.

## Isolation

No case drawn from the sibling baseline corpus. Reviewer prompts unmodified in
both arms. Only `implementer.md` varied. Raw drafts, blind copies, judge
verdicts, and the tally input JSON are in this session's scratchpad
(`.../scratchpad/ab/`); they are session-local and not committed.
