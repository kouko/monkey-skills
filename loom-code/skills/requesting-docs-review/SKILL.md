---
name: requesting-docs-review
description: |
  Whole-artifact review of every changed `.md` file on a docs-heavy branch —
  five prose dimensions, instruction/evidence blocking class, hard 2-round
  convergence cap (round-2 NEEDS_REVISION → STOP and surface to the user).
  Fires BEFORE push/merge when every changed file is `.md`; also the docs
  arm of requesting-code-review's routing. Use for 'review my docs' / 'are
  these docs ready to merge?'.
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (docs-reviewer / code-reviewer / implementer / spec-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Owns the **docs arm** of whole-branch review. Dispatches **two `docs-reviewer` subagents in parallel (a panel)** to review every changed `.md` artifact on a branch — each artifact read whole, the diff as context — across five prose defect dimensions, unions their findings, aggregates over instruction-class findings only, and, on a docs-only branch, mints the same review-pass gate marker the code arm mints (on a mixed branch it returns its verdict instead — Step 4). Documents have no tests, so prose review has no termination oracle of its own; this skill therefore also carries what the code arm never needed: a **convergence contract** with a hard 2-round cap. The recorded pathology it exists to end is a 9-round non-converging docs-review loop in which 6 of 9 rounds shipped a defect injected by the previous round's own remediation (`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`).

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

**What to hand the user, and what to recommend.** "Hand them the decision" means presenting a choice, not a finding list. Present these three, in this order:

- **(a) Fix, then run one delta-scoped verification round** — *the default recommendation*. It reads whole artifacts but raises only against the fixes (Directive 2), so it costs a fraction of a full round. That cost drop is what makes it the default; before scoping existed, a third round meant re-reviewing everything, and "don't authorize lightly" was the right posture.
- **(b) Fix and ship without re-review.** State the risk concretely, never as a general caution: **a fix round is where defects get written.** On the measured branch, round 1's fixes contained three gating defects that only the next round caught (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).
- **(c) Ship as-is, the findings recorded as named residuals.** Correct when the findings are real but change nothing an executor does.

**The criterion is how large the remaining fixes are, not how many rounds are left.** Every round's fixes are verified by the next round, so the LAST round's fixes always ship unverified — adding a round moves that edge, it never removes it. Do not propose a standing extra round to close it. What decides the risk is how much text the remaining fixes rewrite: on the measured branch, round 1's fixes were a broad rewrite and carried three gating defects; round 2's were four one-to-two-sentence edits and carried none. A broad rewrite → (a). One-line corrections → (b) and (c) are both defensible.

**Why a cap rather than "review until clean": for an artifact carrying many small real defects, a clean round is not a reachable state.** Each pass samples that pool, so "the reviewer found nothing" cannot serve as the termination condition — measured on one branch's twelve already-passed `.md` artifacts: four fresh arms, seven gating findings, zero overlap, each traced to its cited text and one settled by running the command that decides it; the audit's §Limits states it does not generalize a rate (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`). The corollary is operative: when a finding names a class a standing mechanism could hold, **prefer adding that mechanism over authorizing another round** — a checker, a format rule that makes the defect unwritable, or a change to what the reviewer is handed. Each fires every time; a reviewer returns a different subset each time.

**2. Round-2 handoff.** The round-2 dispatch packet carries round 1's findings verbatim. Reviewers verify each prior finding against the quoted current text of the artifact BEFORE raising anything new. Re-raising a closed finding in new words is forbidden — that is re-litigation, not review.

**From round 2 onward, what a reviewer may RAISE narrows; what it READS never does.** It still reads every artifact whole. It may raise a new finding only if that finding is (a) about text this round's delta changed, or (b) a contradiction **in either direction** between the delta and text it did NOT change — an unchanged claim the delta falsifies (Step 3's question), or a delta claim unchanged text falsifies. What is out of scope is a contradiction between two unchanged passages, neither touched by the delta. **"Did not change" spans unchanged prose, the `read-context` files, and current code**, which is what keeps Step 3's "does any UNCHANGED claim contradict the change, or the current code?" actionable under a scoped round. Clause (b) is not optional. Two instances, both named so the claim is checkable: a docs arm's `read-context` gap let a spec claiming stdin ship against a script with no stdin path, and this contract's own `read_context_findings` rule was contradicted by an unchanged §Aggregation rule that had no exclusion for it. Anything else the reviewer notices goes in its `out_of_scope:` block (agent contract), never in `findings:`.

**Why.** A review does two jobs with one dispatch, and only one of them terminates: *sampling the artifact's pre-existing defect pool* (unbounded, inexhaustible — a mint-scope conflict in this very skill survived two unbounded rounds before a third surfaced it) and *verifying this round's edits* (bounded, shrinks each round). Round 1 does the first; every later round does the second. Conflating them is the non-convergence. Measured at round 2: two delta-scoped arms re-found BOTH gating findings that two unbounded arms found, and additionally listed 13 observations as out-of-scope (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` §Does delta-scoping converge faster).

**Round 1 stays unbounded — provisionally.** It is the only pass positioned to sample the pre-existing pool, and it samples weakly (on the measured branch, 1 of its 14 findings was pre-existing-and-unrelated). It is kept unbounded only because nothing else sweeps that pool today. **When a standing sweep of pre-existing defects exists, revisit this: the right answer becomes scoping every round, including the first.** Do not read the current setting as settled design.

**An authorized extra round declares its own scope.** A round past the cap needs explicit user authorization (Directive 1); that authorization states whether the round is for convergence (delta-scoped) or for a wider sweep (unbounded). Never infer it from the round number — scope follows intent, not count. **If the authorization is silent ("ok, one more round"), it is delta-scoped** — the same rule every round past the first carries, and the reading that terminates. Ask only when the surviving findings suggest the user wanted the wider sweep; do not ask twice about the same round.

**3. Oscillation stop.** A finding that resurfaces after being fix-verified ends the loop immediately → surface it to the user as an oscillation, not as a routine finding. Do not dispatch another round on an oscillation, whatever the round count.

**4. Appended corrections.** Evidence-class fixes for prose the branch left unchanged are appended corrections naming what they replace — never in-place rewrites. Rewriting settled narrative in place destroys the record the correction exists to correct.

Steps:

1. **Resolve scope — only when none was handed down.** §Pinned pass-down contract, transcribed verbatim: "The delegating station hands the delegate the resolved scope as `resolved-scope` in the dispatch packet. The delegate resolves scope itself ONLY when no `resolved-scope` was supplied." When this dispatch's packet carries `resolved-scope` — the delegated-dispatch shape, `requesting-code-review`'s Step 1 routing already resolved it — consume that file list directly; do not call the resolver again. Otherwise (direct invocation), resolve it yourself: run `python3 <plugin-root>/scripts/review_scope.py` (resolve `<plugin-root>` as `../..` from this skill's base dir). Exit 0 prints the changed-file list to stdout, one path per line; a non-zero exit is a refusal. §Pinned refusal contract, transcribed verbatim: "A stale base, or any failure to establish freshness, REFUSES. The resolver never returns a file list it cannot vouch for, and a station that receives a refusal STOPS before dispatching anything." A refusal — the resolver's own non-zero exit here, or an upstream refusal already surfaced before scope was ever handed down — STOPS this station before any dispatch: do not dispatch the docs-reviewer panel; surface the refusal reason to the user instead. On a resolved (non-refused) scope, the docs-only dispatch fires when the list is non-empty AND every file in it ends in `.md`. Any non-`.md` file in the list means this is not a docs-only branch — route through `requesting-code-review`'s three-way dispatch instead (its mixed-branch per-file split still sends the `.md` files back to this skill's contract).
2. **Citation pre-pass.** Run `python3 <plugin-root>/scripts/check_doc_citations.py <changed .md files>` (resolve `<plugin-root>` as `../..` from this skill's base dir) and fold its output into the dispatch packet. Pre-pass findings inside fenced code blocks, blockquotes, table cells, and inline examples are advisory, not defects — documents quoting tool output or deliberately-broken examples trigger false findings.
3. **Dispatch TWO `docs-reviewer` subagents in parallel, with byte-identical prompts** (a panel, mirroring `requesting-code-review`'s two-arm convention; agent contract at [`loom-code/agents/docs-reviewer.md`](../../agents/docs-reviewer.md); "byte-identical" means identical to each other). Open each prompt with the agent's role anchor — "You ARE the reviewer" — verbatim. The dispatch packet carries: branch name, diff scope, the changed-artifact list, the citation pre-pass output, any `read-context` file list handed down (see below), the round's **`Round scope`** — copy the value Directive 2 determined for THIS round (`unbounded` or `delta-scoped: <commit range>`; the agent contract defines both), and **never re-derive it here from the round number**: a round the user authorized as a wider sweep is `unbounded` whatever its number, and — on round 2 — the prior-round findings per Directive 2. **`read-context`** — supplied by `requesting-code-review`'s mixed-branch split, absent on a docs-only branch — is the branch's non-`.md` files: material each reviewer OPENS to check the artifacts' claims against, never scope it reviews. A claim a changed `.md` makes about a shipped interface (a flag, an accepted input, a path) is verified by reading the named file, not by trusting the prose; unverifiable because the file was not supplied is itself reportable. Findings against a `read-context` file are reported for the orchestrator to pass to the code arm — they do not enter this arm's dimension scores. The recorded miss this closes: a spec stating its shipped tool accepts input via `--claim` or stdin, on a branch whose script has no stdin path, reached merge unflagged — the docs arm that reviewed the spec was never given the script to open (`docs/loom/specs/2026-08-03-claim-copy-sweep.md:82`; `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`). **Whole-artifact scope**: each reviewer reads every changed artifact whole, the diff only as context, and asks explicitly: does any UNCHANGED claim in this file contradict the change, or the current code? (an unchanged line in a document is an untouched line, not a correct one — documents have no tests). Reviewers score the five prose dimensions — **omission** (an obligation or referent the text needs and lacks), **ambiguity** (an absolute — "only", "never", "zero" — without support, or a sentence with two live readings), **inconsistency** (two passages contradicting, including changed-vs-unchanged), **incorrect-fact** (a citation that does not support its claim — open the source), **missing-population** (a measured number without its denominator or scope) — and every finding carries `class: instruction | evidence`: instruction is text a reader or executor will act on (a rule, a step, a prescribed command or path); evidence is a narrative claim about what happened or is true (a measurement, an attribution). A finding whose class is unclear is tagged `instruction` (fail closed).
4. **Wait for BOTH verdicts, union the findings, re-aggregate — then mint the gate marker ONLY if this skill owns the whole review.** Union rule as in `requesting-code-review` Step 3: same `file:line` AND same dimension → one finding, keeping the more detailed wording and the severer severity; same location under different dimensions stays distinct. Re-run §Aggregation rule on the union (per-dimension score = the worse of the two arms' scores) — never adopt one arm's own verdict. **Mint ONLY when this skill owns the whole review.** If the dispatch packet carried a non-empty `read-context` (Step 3), this invocation is the `.md` half of `requesting-code-review`'s mixed-branch split: **return the verdict to that orchestrator and do NOT mint** — it mints once from the joined verdict after both arms return, and a marker minted here would satisfy `git-guard.py`'s push gate before the code arm has said anything. `read-context` is the signal because it is supplied on exactly the mixed path and is non-empty there by construction. Otherwise (docs-only branch, whether invoked directly or delegated whole) mint here: save the panel verdict text to a temp file and run `python3 <plugin-root>/scripts/loom_gate_markers.py review-pass --verdict-file <file>` — the docs arm mints the SAME review-pass marker as the code arm (a separate docs marker would break the `git-guard.py` push gate); the prose dimension names are schema-valid to the marker script, and `NEEDS_REVISION` or a malformed verdict refuses to mint (exit 3/4). Dead-arm rule: an arm that errors out with no verdict is re-dispatched once; if it dies again, proceed single-arm and say so in the verdict summary and the user relay.
5. **Surface to user.** Present the verdict, the instruction-class findings (these gated), and the evidence-class findings (recorded observations). Do NOT auto-fix — remediation is the user's decision, even for a one-word nit.
6. **Round 2 — only if the user fixed and wants re-review.** Fresh subagents, same panel shape, packet per Directive 2 (round-1 findings verbatim; fix-verification duty first). After round 2, Directive 1 governs: no third round without explicit user authorization.

## Aggregation rule

Thresholds are `requesting-code-review` §Aggregation rule, unchanged: any 🔴 → `NEEDS_REVISION`; any finding with empty/missing `where:` → `NEEDS_REVISION` regardless of severity; 2+ 🟡, no 🔴 → `NEEDS_REVISION`; exactly 1 🟡 → `PASS_WITH_NOTES`; only 🟢 or none → `PASS`. The docs arm selects what is fed into the rule, not its thresholds:

- The rule is computed over **instruction-class findings only**; evidence-class findings are carried into the verdict as recorded observations that **do not gate**.
- A finding missing `class:` counts as instruction (fail closed), consistent with a finding missing `where:` flipping the whole verdict.
- A defect noticed **inside** a `read-context` file (Step 3) is not a finding of this arm at all: it carries no severity, no dimension and no `class:`, rides in the separate `read_context_findings:` block, and never enters a dimension score. **It gates nothing, on either arm, and nobody assigns it a severity later** — the orchestrator surfaces it in the report and hands it to the code arm as context, and that arm reviews those files on this same branch under its own rubrics anyway. Deliberate: a defect the docs arm noticed incidentally, in a file it was not scoped to judge, must not decide a verdict. A defect in what a reviewed `.md` **claims about** such a file is an ordinary finding and gates normally — that is the primary case `read-context` exists to serve.
- **The same exclusion covers `out_of_scope:`** (Directive 2's block for what a delta-scoped round declines to raise): those entries carry no severity, no dimension and no `class:`, never enter a dimension score, and the fail-closed `class:` bullet above does NOT reach them — they are not findings. Without this line that bullet would sweep every suppressed observation back into the gate and cancel the convergence Directive 2 exists to produce. Surface them to the user with the verdict so a deferred defect is deferred on the record.
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

read_context_findings:              # omit when empty or when no read-context was supplied
  - where: <read-context file:line>
    note: <a defect noticed IN a read-context file while verifying a claim>
    # No severity, no dimension, no class — never enters a dimension score.
    # The orchestrator forwards these to the code arm (§Aggregation rule).

out_of_scope:                       # omit on an unbounded round
  - where: <file:line>
    note: <a defect noticed outside this round's raise scope (Directive 2)>
    # Emitted, never scored. Surface these to the user with the verdict so a
    # suppressed defect is deferred on the record, not lost.

summary:
  - <≤5 bullet observations about the branch's artifacts as a whole>
```

Any `resurfaced` status in `prior_findings_check` triggers Directive 3 — the loop ends and the oscillation goes to the user.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Just one more round to be safe."* | The cap IS the design. What "to be safe" means here is waiting for an empty round, and for an artifact with many small real defects that state is not reachable — so it cannot be what you wait for. An authorized extra round is a different thing and is not what this row refuses: Directive 1 makes it delta-scoped by default, so it terminates; what it still cannot do is certify the artifact clean. Two mechanisms, both measured — the source audit's remediation-injected defects (6 of 9 rounds), and a large pool of genuine small defects sampled disjointly by each pass. Do NOT read this row as "extra findings are manufactured": on one branch's twelve already-passed artifacts, four fresh arms returned seven gating findings with **zero overlap**, none manufactured (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` — read its §Limits before reusing the numbers). | Refuse. Directive 1: STOP after round 2, surface surviving findings; a third round needs explicit user authorization. Round-2 findings are presumed real — decide them on severity, never discount them as round artifacts. |
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
