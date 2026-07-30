---
name: requesting-docs-review
description: |
  Use BEFORE any push/merge/PR on a docs-heavy branch — whole-artifact review
  of every changed `.md` file across five prose dimensions, with a hard
  2-round convergence cap. Fires when `git diff main...HEAD --name-only` is
  non-empty AND every changed file ends in `.md`; invoked by
  requesting-code-review's three-way routing (the docs arm) and directly:
  'review my docs', 'are these docs ready to merge?'. Refuses 'just one more
  round' — after round 2 ends with NEEDS_REVISION it STOPs and surfaces
  surviving findings to the user.
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (docs-reviewer / code-reviewer / implementer / spec-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Owns the **docs arm** of whole-branch review. Dispatches **two `docs-reviewer` subagents in parallel (a panel)** to review every changed `.md` artifact on a branch — each artifact read whole, the diff as context — across five prose defect dimensions, unions their findings, aggregates over instruction-class findings only, and mints the same review-pass gate marker the code arm mints. Documents have no tests, so prose review has no termination oracle of its own; this skill therefore also carries what the code arm never needed: a **convergence contract** with a hard 2-round cap. The recorded pathology it exists to end is a 9-round non-converging docs-review loop in which 6 of 9 rounds shipped a defect injected by the previous round's own remediation (`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`).

## When to use

| Trigger | Route here |
|---|---|
| `requesting-code-review` Step 1 routing found the branch diff docs-only (non-empty, all `.md`) | ✅ Yes — this skill IS that delegated dispatch |
| The `.md` files' arm of `requesting-code-review`'s mixed-branch per-file split | ✅ Yes — this skill's dispatch + aggregation contract governs the docs arm |
| User says *"review my docs"* / *"are these docs ready to merge?"* on a docs-only branch | ✅ Yes (direct invocation) |
| Code files changed and need review | ❌ `requesting-code-review` (code arm / three-way routing) |
| Per-task prose review inside SDD (`Review-weight: prose`) | ❌ SDD's per-task triad — same `docs-reviewer` agent, different orchestrator |

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Mechanical doc edits** | Typo fix, version bump, generated/sync output regen | Authored prose of any length — a 3-line instruction edit can misdirect an executor; it routes here |
| **Already-reviewed branch** | A prior invocation this session PASSed and nothing changed since | "I tweaked a paragraph after review" — re-review (round accounting continues, it does not reset) |
| **Explicit user override** | User literally says "skip docs review" AND the diff matches the mechanical category | "It's just docs" — that framing is the reason this skill exists |

## Process

**CONVERGENCE CONTRACT — four binding directives. Apply them at every dispatch and verdict moment; they override any impulse to run another round.**

**1. Hard cap: 2 review rounds.** After round 2 ends with NEEDS_REVISION (PASS and PASS_WITH_NOTES are both passing verdicts and end the review) → STOP and surface the surviving findings to the user. Hand them the decision. A third round runs ONLY on explicit user authorization (the critics' user-authorized breach precedent) — never silently.

**2. Round-2 handoff.** The round-2 dispatch packet carries round 1's findings verbatim. Reviewers verify each prior finding against the quoted current text of the artifact BEFORE raising anything new. Re-raising a closed finding in new words is forbidden — that is re-litigation, not review.

**3. Oscillation stop.** A finding that resurfaces after being fix-verified ends the loop immediately → surface it to the user as an oscillation, not as a routine finding. Do not dispatch another round on an oscillation, whatever the round count.

**4. Appended corrections.** Evidence-class fixes for prose the branch left unchanged are appended corrections naming what they replace — never in-place rewrites. Rewriting settled narrative in place destroys the record the correction exists to correct.

Steps:

1. **Confirm the dispatch trigger.** Run `git diff main...HEAD --name-only` (or the user's explicit commit range). Docs-only dispatch fires when the list is non-empty AND every file in it ends in `.md`. Any non-`.md` file in the diff means this is not a docs-only branch — route through `requesting-code-review`'s three-way dispatch instead (its mixed-branch per-file split still sends the `.md` files back to this skill's contract).
2. **Citation pre-pass.** Run `python3 <plugin-root>/scripts/check_doc_citations.py <changed .md files>` (resolve `<plugin-root>` as `../..` from this skill's base dir) and fold its output into the dispatch packet. Pre-pass findings inside fenced code blocks, blockquotes, table cells, and inline examples are advisory, not defects — documents quoting tool output or deliberately-broken examples trigger false findings.
3. **Dispatch TWO `docs-reviewer` subagents in parallel, with byte-identical prompts** (a panel, mirroring `requesting-code-review`'s two-arm convention; agent contract at [`loom-code/agents/docs-reviewer.md`](../../agents/docs-reviewer.md); "byte-identical" means identical to each other). Open each prompt with the agent's role anchor — "You ARE the reviewer" — verbatim. The dispatch packet carries: branch name, diff scope, the changed-artifact list, the citation pre-pass output, and — on round 2 — the prior-round findings per Directive 2. **Whole-artifact scope**: each reviewer reads every changed artifact whole, the diff only as context, and asks explicitly: does any UNCHANGED claim in this file contradict the change, or the current code? (an unchanged line in a document is an untouched line, not a correct one — documents have no tests). Reviewers score the five prose dimensions — **omission** (an obligation or referent the text needs and lacks), **ambiguity** (an absolute — "only", "never", "zero" — without support, or a sentence with two live readings), **inconsistency** (two passages contradicting, including changed-vs-unchanged), **incorrect-fact** (a citation that does not support its claim — open the source), **missing-population** (a measured number without its denominator or scope) — and every finding carries `class: instruction | evidence`: instruction is text a reader or executor will act on (a rule, a step, a prescribed command or path); evidence is a narrative claim about what happened or is true (a measurement, an attribution). A finding whose class is unclear is tagged `instruction` (fail closed).
4. **Wait for BOTH verdicts, union the findings, re-aggregate — then mint the gate marker.** Union rule as in `requesting-code-review` Step 3: same `file:line` AND same dimension → one finding, keeping the more detailed wording and the severer severity; same location under different dimensions stays distinct. Re-run §Aggregation rule on the union (per-dimension score = the worse of the two arms' scores) — never adopt one arm's own verdict. Save the panel verdict text to a temp file and run `python3 <plugin-root>/scripts/loom_gate_markers.py review-pass --verdict-file <file>` — the docs arm mints the SAME review-pass marker as the code arm (a separate docs marker would break the `git-guard.py` push gate); the prose dimension names are schema-valid to the marker script, and `NEEDS_REVISION` or a malformed verdict refuses to mint (exit 3/4). Dead-arm rule: an arm that errors out with no verdict is re-dispatched once; if it dies again, proceed single-arm and say so in the verdict summary and the user relay.
5. **Surface to user.** Present the verdict, the instruction-class findings (these gated), and the evidence-class findings (recorded observations). Do NOT auto-fix — remediation is the user's decision, even for a one-word nit.
6. **Round 2 — only if the user fixed and wants re-review.** Fresh subagents, same panel shape, packet per Directive 2 (round-1 findings verbatim; fix-verification duty first). After round 2, Directive 1 governs: no third round without explicit user authorization.

## Aggregation rule

Thresholds are `requesting-code-review` §Aggregation rule, unchanged: any 🔴 → `NEEDS_REVISION`; any finding with empty/missing `where:` → `NEEDS_REVISION` regardless of severity; 2+ 🟡, no 🔴 → `NEEDS_REVISION`; exactly 1 🟡 → `PASS_WITH_NOTES`; only 🟢 or none → `PASS`. The docs arm selects what is fed into the rule, not its thresholds:

- The rule is computed over **instruction-class findings only**; evidence-class findings are carried into the verdict as recorded observations that **do not gate**.
- A finding missing `class:` counts as instruction (fail closed), consistent with a finding missing `where:` flipping the whole verdict.
- An evidence-class finding against narrative prose the branch left UNCHANGED (Step 3's whole-artifact question) must be superseded by an appended correction naming what it replaces, never edited in place (Directive 4).
- **Panel union**: each arm's own `verdict:` is advisory; the gate verdict comes from applying this rule to the union of both arms' findings.

## Verdict structure

The panel verdict text (computed over the union) mirrors the `docs-reviewer` output contract:

```
standards_version: "{X.Y.Z — value of `version` in loom-code/.claude-plugin/plugin.json}"

verdict: PASS | PASS_WITH_NOTES | NEEDS_REVISION

dimension_scores:
  omission: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  ambiguity: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  inconsistency: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  incorrect-fact: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  missing-population: PASS | PASS_WITH_NOTES | NEEDS_REVISION

prior_findings_check:               # round 2 only; omit on round 1
  - finding: <round-1 finding, restated verbatim>
    status: fix-verified | not-fixed | resurfaced
    quote: <the exact current text that verifies (or fails) the fix>

findings:
  - severity: 🔴 fatal | 🟡 should-fix | 🟢 nit
    dimension: omission | ambiguity | inconsistency | incorrect-fact | missing-population
    class: instruction | evidence   # unclear → instruction (fail closed)
    where: <file:line>              # REQUIRED, path-like — empty/missing flips verdict to NEEDS_REVISION
    quote: <the exact current text the finding is about>
    note: <1-2 sentence finding>

summary:
  - <≤5 bullet observations about the branch's artifacts as a whole>
```

Any `resurfaced` status in `prior_findings_check` triggers Directive 3 — the loop ends and the oscillation goes to the user.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Just one more round to be safe."* | The cap IS the design. 6 of 9 rounds in the source audit shipped a defect injected by the previous round's own remediation — extra rounds manufacture defects. | Refuse. Directive 1: STOP after round 2, surface surviving findings; a third round needs explicit user authorization. |
| *"The reviewer found something new — keep looping until clean."* | Prose has no termination oracle; "clean" never arrives by iteration. | Directive 1. Surface what survives; the user decides. |
| *"They re-flagged the thing we closed, so it must still be broken."* | Either re-litigation in new words (forbidden) or a genuine oscillation (loop-ending). | Directive 2 / Directive 3 — verify against quoted text; an oscillation goes to the user, not into another round. |
| *"Just rewrite that old paragraph in place."* | Evidence-class fix against unchanged prose — in-place rewrites destroy the record. | Directive 4: appended correction naming what it replaces. |
| *"It's just docs, skip review."* | Wrong instructions misdirect executors more cheaply than wrong code — code at least fails tests. | Only the mechanical category in §When NOT to use skips. Authored prose reviews. |
| 「もう1ラウンドだけ / 再審一輪就好」 | Same rationalization, localized. | Same refusal. |

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream routing** | `requesting-code-review` | Its Step 1 three-way dispatch delegates docs-only branches here whole, and applies this skill's contract to the `.md` arm of mixed branches; both arms of a mixed branch must pass |
| **Upstream orchestrator** | `finishing-a-development-branch` | Invokes `requesting-code-review` as its review step; a 2-round-cap STOP from this skill surfaces to the user instead of entering the silent fix→re-review loop |
| **Dispatched agent** | [`loom-code:docs-reviewer`](../../agents/docs-reviewer.md) | Verdict-only prose reviewer; also reused by SDD's `Review-weight: prose` triad |
| **Sibling gate** | `verification-before-completion` | Code-side test-suite gate; on a docs-only branch it still runs whatever suite pins the prose (grep-window tests) |

## What this skill does NOT do

- Does **not** modify any reviewed document — reviewers are verdict-only; remediation is the user's / implementer's.
- Does **not** review code — any non-`.md` file in the diff routes through `requesting-code-review`.
- Does **not** replace the citation pre-pass with judgment — `check_doc_citations.py` runs first, mechanically.
- Does **not** run round 3 on its own authority — ever (Directive 1).

## See also

- [`loom-code/agents/docs-reviewer.md`](../../agents/docs-reviewer.md) — the dispatched reviewer's role contract, input/output contracts, and per-dispatch convergence duties.
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — the code arm + three-way routing that invokes this skill.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — branch close-out orchestrator upstream of both arms.
- `loom-code/scripts/check_doc_citations.py` — the mechanical citation pre-pass (bounds-checks `path:line` citations).
- `loom-code/scripts/loom_gate_markers.py` — mints the review-pass marker from the panel verdict text.
- `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` — the 9-round loop this skill's convergence contract ends.
