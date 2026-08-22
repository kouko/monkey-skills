---
name: requesting-docs-review
description: |
  Whole-artifact review of every changed `.md` file on a docs-heavy branch —
  five prose dimensions, instruction/evidence blocking class,
  single-round-with-confirmation contract: round 1 whole-artifact is the
  only full review; a gating verdict is fixed then confirmed by the SAME
  reviewer via a delta-scoped check (still-blocking after one fix cycle →
  STOP and surface to the user).
  Fires BEFORE push/merge when every changed file is `.md`; also the docs
  arm of requesting-code-review's routing. Use for 'review my docs' / 'are
  these docs ready to merge?'.
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (docs-reviewer / code-reviewer / implementer / spec-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Owns the **docs arm** of whole-branch review. Dispatches **two `docs-reviewer` subagents in parallel (a panel)** to review every changed `.md` artifact on a branch — each artifact read whole, the diff as context — across five prose defect dimensions, unions their findings, aggregates over instruction-class findings only, and, on a docs-only branch, mints the same review-pass gate marker the code arm mints (on a mixed branch it returns its verdict instead — Step 4). Documents have no tests, so prose review has no termination oracle of its own; this skill therefore also carries what the code arm never needed: a **convergence contract** — round 1 whole-artifact is the only full review; a gating verdict is fixed, then confirmed by the SAME reviewer via a delta-scoped check, never a fresh whole-corpus re-sample.

## When to use

| Trigger | Route here |
|---|---|
| `requesting-code-review` Step 1 routing found the branch diff docs-only (non-empty, all `.md`) | ✅ Yes — this skill IS that delegated dispatch |
| The `.md` files' arm of `requesting-code-review`'s mixed-branch per-file split | ✅ Yes — this skill's dispatch + aggregation contract governs the docs arm |
| User says *"review my docs"* / *"are these docs ready to merge?"* on a docs-only branch | ✅ Yes (direct invocation) |
| Code files changed and need review | ❌ `requesting-code-review` (code arm / four-way routing) |
| Per-task prose review inside SDD (`Review-weight: prose`) | ❌ SDD's per-task triad — same `docs-reviewer` agent, different orchestrator |

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Mechanical doc edits** | Typo fix, version bump, generated/sync output regen | Authored prose of any length — a 3-line instruction edit can misdirect an executor; it routes here |
| **Already-reviewed branch** | A prior invocation this session PASSed and nothing changed since | "I tweaked a paragraph after review" — re-review (review state is session-scoped: it restarts at a session boundary, so a fresh session simply reruns round 1 rather than assuming continuity). A session that dies mid-confirmation instead falls to Directive 4's fresh-single-round rule, not this row |
| **Explicit user override** | User literally says "skip docs review" AND the diff matches the mechanical category | "It's just docs" — that framing is the reason this skill exists |

## Process

**CONVERGENCE CONTRACT — read [`references/convergence-contract.md`](references/convergence-contract.md) before running any round; its four directives are binding.**

- **Directive 1 — Round 1 is the only full review.** Whole-artifact, every changed `.md` file — no round cap, no round count. No gating findings → done. A gating verdict → fix, then delta confirmation (Directive 2); non-gating findings never gate — they are recorded as debt (Aggregation thresholds unchanged).
- **Directive 2 — Delta confirmation.** After a fix, dispatch the SAME reviewer that raised the gating finding — via `SendMessage`, never a fresh `Agent` dispatch — scoped to the delta only (the findings that gated and the text that changed to address them), never a fresh whole-corpus re-sample. It returns `CONFIRMED_RESOLVED` (terminal) or `STILL_BLOCKING` + reason. `STILL_BLOCKING` after this one fix cycle → STOP; surface the finding and the reviewer's reason to the user — no second cycle, and no fallback to a fresh whole-artifact round, without explicit user authorization.
- **Directive 3 — Terminal state is "no gating findings," never "clean."** For an artifact carrying many small real defects, a clean round is not a reachable state — each review samples that pool, so a pass that raises nothing is not evidence the pool is empty (pool-arithmetic rationale, measurement provenance: [`references/design-evidence.md`](references/design-evidence.md), author-facing; `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`). Report the outcome as "round 1 found no gating findings" or "the fix was confirmed resolved" — never as "the doc is clean."
- **Directive 4 — Session death before confirmation → one fresh single round.** Do not resume or replay a dispatched-but-incomplete delta confirmation; dispatch one fresh, whole-artifact round 1 instead.

**What to hand the user.** Non-gating findings are recorded as debt automatically — no user decision needed (Aggregation thresholds, unchanged, decide gating vs. non-gating). A gating verdict has exactly one path: fix, then the delta confirmation of Directive 2 — there is no "ship without re-review" or "ship as-is" option for a finding that gated. Present the gating findings, the fix, and the confirmation outcome to the user: `CONFIRMED_RESOLVED` closes the review; `STILL_BLOCKING` hands the finding and the reviewer's reason back to the user, and no further cycle runs without their explicit authorization. Render the findings per the adjudication-view protocol (verdict mode) when that protocol's own §Firing conditions are met — see [`../using-loom-code/protocols/adjudication-view.md`](../using-loom-code/protocols/adjudication-view.md).

Steps:

1. **Resolve scope — only when none was handed down.** This station reviews contract-class `.md` only — scope per `requesting-code-review` §Classification: contract-class vs record-class (cite that heading; do not re-derive or copy the glob rule here). §Pinned pass-down contract, transcribed verbatim: "The delegating station hands the delegate the resolved scope as `resolved-scope` in the dispatch packet. The delegate resolves scope itself ONLY when no `resolved-scope` was supplied." When this dispatch's packet carries `resolved-scope` — the delegated-dispatch shape, `requesting-code-review`'s Step 1 routing already resolved it — consume that file list directly; do not call the resolver again. Otherwise (direct invocation), resolve it yourself: run `python3 <plugin-root>/scripts/review_scope.py` (resolve `<plugin-root>` as `../..` from this skill's base dir). Exit 0 prints the changed-file list to stdout, one path per line; a non-zero exit is a refusal. §Pinned refusal contract, transcribed verbatim: "A stale base, or any failure to establish freshness, REFUSES. The resolver never returns a file list it cannot vouch for, and a station that receives a refusal STOPS before dispatching anything." A refusal — the resolver's own non-zero exit here, or an upstream refusal already surfaced before scope was ever handed down — STOPS this station before any dispatch: do not dispatch the docs-reviewer panel; surface the refusal reason to the user instead. On a resolved (non-refused) scope, the docs-only dispatch fires when the list is non-empty AND every file in it ends in `.md`. Any non-`.md` file in the list means this is not a docs-only branch — route through `requesting-code-review`'s four-way dispatch instead (its mixed-branch per-file split still sends the `.md` files back to this skill's contract). On direct invocation (no `resolved-scope` handed down), also evaluate `requesting-code-review` §Process Step 1's M3 upgrade triggers against the scope you just resolved, before Step 3 — same rule, same literals; cite that heading, do not re-derive it here.
2. **Citation pre-pass.** Run `python3 <plugin-root>/scripts/check_doc_citations.py <changed .md files>` (resolve `<plugin-root>` as `../..` from this skill's base dir) and fold its output into the dispatch packet. Pre-pass findings inside fenced code blocks, blockquotes, table cells, and inline examples are advisory, not defects — documents quoting tool output or deliberately-broken examples trigger false findings.
3. **Dispatch TWO `docs-reviewer` subagents in parallel, with byte-identical prompts** (a panel, mirroring `requesting-code-review`'s two-arm convention; agent contract at [`loom-code/agents/docs-reviewer.md`](../../agents/docs-reviewer.md); "byte-identical" means identical to each other). Open each prompt with the agent's role anchor — "You ARE the reviewer" — verbatim. **State the HEAD sha this dispatch reviews** in the packet; each arm returns it as `reviewed_sha:` and the panel verdict carries it (§Verdict structure) — provenance for the delta confirmation that follows a gating verdict (Step 6). The dispatch packet carries: branch name, diff scope, the changed-artifact list, the citation pre-pass output, any `read-context` file list handed down (see below), and an OPTIONAL `model` field — set by `requesting-code-review`'s M3 upgrade rule (its §Process Step 1) when its triggers fire. When the packet carries `model`, dispatch both `docs-reviewer` subagents with that `model` override; absent, the agents' own frontmatter default governs. Round 1 is always whole-artifact — there is no round-scope variable to set and no prior-round findings to carry (Directive 1: round 1 is the only full review). **`read-context`** — supplied by `requesting-code-review`'s mixed-branch split, absent on a docs-only branch — is the branch's non-`.md` files: material each reviewer OPENS to check the artifacts' claims against, never scope it reviews. A claim a changed `.md` makes about a shipped interface (a flag, an accepted input, a path) is verified by reading the named file, not by trusting the prose; unverifiable because the file was not supplied is itself reportable. Findings against a `read-context` file are reported for the orchestrator to pass to the code arm — they do not enter this arm's dimension scores. **Whole-artifact scope**: each reviewer reads every changed artifact whole, the diff only as context, and asks explicitly: does any UNCHANGED claim in this file contradict the change, or the current code? (an unchanged line in a document is an untouched line, not a correct one — documents have no tests). Reviewers score the five prose dimensions — **omission** (an obligation or referent the text needs and lacks), **ambiguity** (an absolute — "only", "never", "zero" — without support, or a sentence with two live readings), **inconsistency** (two passages contradicting, including changed-vs-unchanged), **incorrect-fact** (a citation that does not support its claim — open the source), **missing-population** (a measured number without its denominator or scope) — and every finding carries `class: instruction | evidence`: instruction is text a reader or executor will act on (a rule, a step, a prescribed command or path); evidence is a narrative claim about what happened or is true (a measurement, an attribution). A finding whose class is unclear is tagged `instruction` (fail closed).
4. **Wait for BOTH verdicts, union the findings, re-aggregate — then mint the gate marker ONLY if this skill owns the whole review.** Union rule as in `requesting-code-review` Step 3: same path + anchor + dimension → one finding, keeping the more detailed wording and the severer severity; optional line precision is ignored for identity, and the same path + anchor under different dimensions stays distinct. Re-run §Aggregation rule on the union — per-dimension score is re-aggregated from that dimension's union findings, not either arm's own: two arms contributing DIFFERENT findings to one dimension can each score clean alone yet union to NEEDS_REVISION, which either arm's own score would miss — never adopt one arm's own verdict. **Mint ONLY when this skill owns the whole review.** If the dispatch packet carried a non-empty `read-context` (Step 3), this invocation is the `.md` half of `requesting-code-review`'s mixed-branch split: **return the verdict to that orchestrator and do NOT mint** — it mints once from the joined verdict after both arms return, and a marker minted here would satisfy `git-guard.py`'s push gate before the code arm has said anything. `read-context` is the signal because it is supplied on exactly the mixed path and is non-empty there by construction. Otherwise (docs-only branch, whether invoked directly or delegated whole) mint here: save the panel verdict text to a temp file and run `python3 <plugin-root>/scripts/loom_gate_markers.py review-pass --verdict-file <file>` — the docs arm mints the SAME review-pass marker as the code arm (a separate docs marker would break the `git-guard.py` push gate); the prose dimension names are schema-valid to the marker script, and `NEEDS_REVISION` or a malformed verdict refuses to mint (exit 3/4). Dead-arm rule: an arm that errors out with no verdict is re-dispatched once; if it dies again, proceed single-arm and say so in the verdict summary and the user relay.
5. **Surface to user.** Present the verdict, its `reviewed_sha:`, the instruction-class findings (these gated — Directive 2's delta confirmation follows once they are fixed), and the evidence-class findings (recorded observations, never gating). Do NOT auto-fix — remediation is the user's decision, even for a one-word nit.
6. **Delta confirmation — only when round 1 raised a gating verdict.** Once the surviving instruction-class findings are fixed, dispatch the SAME `docs-reviewer` subagent instance(s) that raised each one — via `SendMessage` to that same session, never a fresh `Agent` dispatch — scoped to the delta only (Directive 2) (address it by the handle its dispatch returned — see the host tool reference). Each confirms `CONFIRMED_RESOLVED` or `STILL_BLOCKING` + reason. `CONFIRMED_RESOLVED` is terminal (Directive 3) — report "no gating findings" or "confirmed resolved," never "clean." `STILL_BLOCKING` after this one cycle STOPs the review: surface the finding and the reviewer's reason to the user: no second confirmation cycle, and no fallback to a fresh round 1, without their explicit authorization. Render the findings per the adjudication-view protocol (verdict mode) when that protocol's own §Firing conditions are met — see [`../using-loom-code/protocols/adjudication-view.md`](../using-loom-code/protocols/adjudication-view.md).

## Aggregation rule

Thresholds are `requesting-code-review` §Aggregation rule, unchanged: any 🔴 → `NEEDS_REVISION`; any finding with empty/missing `where:` → `NEEDS_REVISION` regardless of severity; 2+ 🟡, no 🔴 → `NEEDS_REVISION`; exactly 1 🟡 → `PASS_WITH_NOTES`; only 🟢 or none → `PASS`. These thresholds are inherited unexamined from `requesting-code-review`, where they sit on top of a passing test suite (the docs arm has only grep-window pins beneath it) — no docs-specific evidence sets them. The docs arm selects what is fed into the rule, not its thresholds:

- The rule is computed over **instruction-class findings only**; evidence-class findings are carried into the verdict as recorded observations that **do not gate**.
- A finding missing `class:` counts as instruction (fail closed), consistent with a finding missing `where:` flipping the whole verdict.
- A defect noticed **inside** a `read-context` file (Step 3) is not a finding of this arm at all: it carries no severity, no dimension and no `class:`, rides in the separate `read_context_findings:` block, and never enters a dimension score. **It gates nothing, on either arm, and nobody assigns it a severity later** — the orchestrator surfaces it in the report and hands it to the code arm as context, and that arm reviews those files on this same branch under its own rubrics anyway. Deliberate: a defect the docs arm noticed incidentally, in a file it was not scoped to judge, must not decide a verdict. A defect in what a reviewed `.md` **claims about** such a file is an ordinary finding and gates normally — that is the primary case `read-context` exists to serve.
- **The same exclusion covers `out_of_scope:`** (§Verdict structure's block for a defect a round declines to raise): those entries carry no severity, no dimension and no `class:`, never enter a dimension score, and the fail-closed `class:` bullet above does NOT reach them — they are not findings. Without this line that bullet would sweep every suppressed observation back into the gate. Surface them to the user with the verdict; persisted nowhere — deferral survives only if the user or orchestrator acts on it.
- An evidence-class finding against narrative prose the branch left UNCHANGED (Step 3's whole-artifact question) must be superseded by an appended correction naming what it replaces, never edited in place.
- **Panel union**: each arm's own `verdict:` is advisory; the gate verdict comes from applying this rule to the union of both arms' findings.

## Verdict structure

The panel verdict text (computed over the union) mirrors the `docs-reviewer` output contract:

```
standards_version: "{X.Y.Z — value of `version` in loom-code/.claude-plugin/plugin.json}"

reviewed_sha: {the HEAD sha this round reviewed — REQUIRED; records the
              reviewed commit for provenance and as the delta-confirmation
              anchor (Directive 2) — there is no round-N handoff to track}

verdict: PASS | PASS_WITH_NOTES | NEEDS_REVISION

dimension_scores:
  omission: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  ambiguity: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  inconsistency: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  incorrect-fact: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  missing-population: PASS | PASS_WITH_NOTES | NEEDS_REVISION

findings:
  - severity: 🔴 fatal | 🟡 should-fix | 🟢 nit
    dimension: omission | ambiguity | inconsistency | incorrect-fact | missing-population
    class: instruction | evidence   # unclear → instruction (fail closed); may read `instruction (defaulted)` when the reviewer could not tell. A `(defaulted)` tag is treated exactly as `instruction` by the aggregation rule.
    where: <path + anchor; line optional>              # REQUIRED — empty/missing flips verdict to NEEDS_REVISION
    quote: <the exact current text the finding is about>
    note: <1-2 sentence finding>

read_context_findings:              # omit when empty or when no read-context was supplied
  - where: <read-context path + anchor; line optional>
    note: <a defect noticed IN a read-context file while verifying a claim>
    # No severity, no dimension, no class — never enters a dimension score.
    # The orchestrator forwards these to the code arm (§Aggregation rule).

out_of_scope:                       # omit on round 1 (unbounded -- nothing
                                     # is out of scope there); populated by
                                     # a delta confirmation (Directive 2),
                                     # which is scoped to the delta only
  - where: <path + anchor; line optional>
    note: <a defect noticed outside the delta while confirming a fix>
    # Emitted, never scored. Surfaced to the user with the verdict;
    # persisted nowhere — deferral survives only if the user or
    # orchestrator acts on it.

summary:
  - <≤5 bullet observations about the branch's artifacts as a whole>
```

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Just one more round to be safe."* | The single-round-plus-confirmation contract IS the design. What "to be safe" means here is waiting for an empty round, and for an artifact with many small real defects that state is not reachable — so it cannot be what you wait for (Directive 3). A second dispatch that is NOT the one delta confirmation Directive 2 authorizes is exactly what this row refuses. | Refuse. Round 1 is the only full review (Directive 1); a gating verdict gets exactly one fix-and-confirm cycle (Directive 2); `STILL_BLOCKING` STOPs and surfaces to the user, never a second cycle on your own authority. |
| *"The reviewer found something new — keep looping until clean."* | Prose has no termination oracle; "clean" never arrives by iteration. | Directive 3. Surface what survives; the user decides. |
| *"They re-flagged the thing we closed, so it must still be broken."* | `STILL_BLOCKING` is exactly this: the fix did not close the finding, or introduced a new gating problem. | Directive 2 — STOP after this one cycle; surface the finding and the reviewer's reason to the user, never loop again on your own authority. |
| *"Just rewrite that old paragraph in place."* | Evidence-class fix against unchanged prose — in-place rewrites destroy the record. | Appended correction naming what it replaces (§Aggregation rule). |
| *"It's just docs, skip review."* | Wrong instructions misdirect executors more cheaply than wrong code — code at least fails tests. | Only the mechanical category in §When NOT to use skips. Authored prose reviews. |
| 「もう1ラウンドだけ / 再審一輪就好」 | Same rationalization, localized. | Same refusal. |

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream routing** | `requesting-code-review` | Its Step 1 four-way dispatch delegates docs-only branches here whole, and applies this skill's contract to the `.md` arm of mixed branches; both arms of a mixed branch must pass |
| **Upstream orchestrator** | `finishing-a-development-branch` | Invokes `requesting-code-review` as its review step; a `STILL_BLOCKING` STOP from this skill surfaces to the user instead of entering the silent fix→re-review loop |
| **Dispatched agent** | [`loom-code:docs-reviewer`](../../agents/docs-reviewer.md) | Verdict-only prose reviewer; also reused by SDD's `Review-weight: prose` triad |
| **Sibling gate** | `verification-before-completion` | Code-side test-suite gate; on a docs-only branch it still runs whatever suite pins the prose (grep-window tests) |

## What this skill does NOT do

- Does **not** modify any reviewed document — reviewers are verdict-only; remediation is the user's / implementer's.
- Does **not** review code — any non-`.md` file in the diff routes through `requesting-code-review`.
- Does **not** replace the citation pre-pass with judgment — `check_doc_citations.py` runs first, mechanically.
- Does **not** run a second full round or a second delta-confirmation cycle on its own authority — `STILL_BLOCKING` after the one fix cycle STOPs and hands the decision to the user (Directive 2).

## See also

- [`loom-code/agents/docs-reviewer.md`](../../agents/docs-reviewer.md) — the dispatched reviewer's role contract, input/output contracts, and per-dispatch convergence duties.
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — the code arm + four-way routing that invokes this skill.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — branch close-out orchestrator upstream of both arms.
- `loom-code/scripts/check_doc_citations.py` — the mechanical citation pre-pass (bounds-checks `path:line` citations).
- `loom-code/scripts/loom_gate_markers.py` — mints the review-pass marker from the panel verdict text.
- `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` — the 9-round loop this skill's convergence contract ends.
