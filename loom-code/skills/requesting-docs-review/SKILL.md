---
name: requesting-docs-review
description: |
  Whole-artifact review of every changed `.md` file on a docs-heavy branch —
  five prose dimensions, instruction/evidence blocking class,
  single-round-with-confirmation contract: round 1 whole-artifact is the
  only full review; a gating verdict is fixed then confirmed through one
  host-specific packet route — Claude same-session delta check or Codex fresh
  whole-artifact review (still-blocking after one fix cycle → STOP and surface
  to the user).
  Fires BEFORE push/merge when every changed file is `.md`; also the docs
  arm of requesting-code-review's routing. Use for 'review my docs' / 'are
  these docs ready to merge?'.
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (docs-reviewer / code-reviewer / implementer / spec-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## Live-gate receipt (DOCS only)

Only when all five `LOOM_LIVE_GATE_PACKET`, `LOOM_LIVE_GATE_MARKER_DIR`,
`LOOM_LIVE_GATE_NONCE`, `LOOM_LIVE_GATE_PLUGIN_ROOT`, and
`LOOM_LIVE_GATE_REPO` are supplied: after consuming the handed packet, run
exactly once (no wrapper, redirection, prefix, or suffix):
`python3 "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py" --packet "$LOOM_LIVE_GATE_PACKET" --plugin-root "$LOOM_LIVE_GATE_PLUGIN_ROOT" --marker-dir "$LOOM_LIVE_GATE_MARKER_DIR" --repo "$LOOM_LIVE_GATE_REPO" --station DOCS --nonce "$LOOM_LIVE_GATE_NONCE"`
Otherwise do nothing. Never re-run `review_context.py` in a live-gate station;
the runner-owned packet is the sole packet source.

## What this skill does

Owns the **docs arm** of whole-branch review. Dispatches **two `docs-reviewer` subagents in parallel (a panel)** to review every changed `.md` artifact on a branch — each artifact read whole, the diff as context — across five prose defect dimensions, unions their findings, aggregates over instruction-class findings only, and, on a docs-only branch, mints the same review-pass gate marker the code arm mints (on a mixed branch it returns its verdict instead — Step 4). Documents have no tests, so prose review has no termination oracle of its own; this skill therefore also carries what the code arm never needed: a **convergence contract** — round 1 whole-artifact is the only full review; a gating verdict is fixed, then confirmed from one portable post-fix packet.

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
- **Directive 2 — Host-specific delivery, shared confirmation packet.** After a fix, bind the post-fix SHA with the complete immutable context fields plus the original gating findings and delta evidence. Claude Code sends that packet to the SAME reviewer via `SendMessage` and checks the delta; Codex gives the same packet to a labelled fresh whole-artifact review. Both map `PASS` or `PASS_WITH_NOTES` to `CONFIRMED_RESOLVED` only if every original finding is fixed, and map `NEEDS_REVISION` to `STILL_BLOCKING` + reason. `STILL_BLOCKING` after this one cycle → STOP; surface the finding and the reviewer's reason to the user — no second cycle without explicit user authorization.
- **Directive 3 — Terminal state is "no gating findings," never "clean."** For an artifact carrying many small real defects, a clean round is not a reachable state — each review samples that pool, so a pass that raises nothing is not evidence the pool is empty (pool-arithmetic rationale, measurement provenance: [`references/design-evidence.md`](references/design-evidence.md), author-facing; `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`). Report the outcome as "round 1 found no gating findings" or "the fix was confirmed resolved" — never as "the doc is clean."
- **Directive 4 — Session death before confirmation → one fresh single round.** Do not resume or replay a dispatched-but-incomplete delta confirmation; dispatch one fresh, whole-artifact round 1 instead.

**What to hand the user.** Non-gating findings are recorded as debt automatically — no user decision needed (Aggregation thresholds, unchanged, decide gating vs. non-gating). A gating verdict has exactly one path: fix, then the delta confirmation of Directive 2 — there is no "ship without re-review" or "ship as-is" option for a finding that gated. Present the gating findings, the fix, and the confirmation outcome to the user: `CONFIRMED_RESOLVED` closes the review; `STILL_BLOCKING` hands the finding and the reviewer's reason back to the user, and no further cycle runs without their explicit authorization. Render the findings per the adjudication-view protocol (verdict mode) when that protocol's own §Firing conditions are met — see [`../using-loom-code/protocols/adjudication-view.md`](../using-loom-code/protocols/adjudication-view.md).

Steps:

1. **Adopt a handed-down immutable context packet, or resolve one only when absent; then scope.** When the upstream dispatch supplies a **complete immutable context packet**, consume it verbatim — `target_repo`, `reviewed_sha`, `plugin_version`, and approved absolute `resources` paths — and **do not invoke review_context.py to re-resolve it**. This applies equally to docs-only delegation and the `.md` arm of a mixed review. Only when no complete packet was handed down, ask the **active host adapter** to resolve its installed plugin root and run that root's `scripts/review_context.py --repo <target_repo>` once for this review attempt; the adapter is the only root-resolution authority. Do not use `CLAUDE_PLUGIN_ROOT`, a cache layout, the consumer repository, working directory, or skill-relative traversal as a path source. Keep the resulting full immutable context packet unchanged. Whether the packet was adopted verbatim or freshly resolved, validate it before use. On the adopt path, first ask the active host adapter to resolve its installed plugin root (root lookup only — the packet itself stays verbatim, never re-resolved); on the fresh-resolve path, reuse the root just resolved above. On the adopt path, the executor RECONSTRUCTS the packet JSON object from the handed-down field list — the four keys `target_repo`, `reviewed_sha`, `plugin_version`, and `resources` (a name→absolute-path object). Then write the packet JSON to a file and run that root's `scripts/review_context.py --validate <packet-file>` (validation only — it never re-resolves or replaces the packet); any non-zero exit REFUSES the fan-out: do not dispatch any reviewer — fix the packet first. In a live-gate station this `--validate` invocation is SKIPPED: the runner-owned packet was already mechanically validated by `live_gate_station_receipt.py` (the same key-set + SHA checks), and the live-gate section's "Never re-run `review_context.py`" rule governs there. This station reviews contract-class `.md` only — scope per `requesting-code-review` §Classification: contract-class vs record-class (cite that heading; do not re-derive or copy the glob rule here). §Pinned pass-down contract, transcribed verbatim: "The delegating station hands the delegate the resolved scope as `resolved-scope` in the dispatch packet. The delegate resolves scope itself ONLY when no `resolved-scope` was supplied." When this dispatch's packet carries `resolved-scope` — the delegated-dispatch shape, `requesting-code-review`'s Step 1 routing already resolved it — consume that file list directly; do not call the resolver again. Otherwise (direct invocation), resolve it through the approved `resources.review_scope` (`review_scope.py`) path: `python3 <resources.review_scope> --repo <target_repo> --reviewed-sha <reviewed_sha>`. Exit 0 prints the changed-file list to stdout, one path per line; a non-zero exit is a refusal. §Pinned refusal contract, transcribed verbatim: "A stale base, or any failure to establish freshness, REFUSES. The resolver never returns a file list it cannot vouch for, and a station that receives a refusal STOPS before dispatching anything." A refusal — the resolver's own non-zero exit here, or an upstream refusal already surfaced before scope was ever handed down — STOPS this station before any dispatch: do not dispatch the docs-reviewer panel; surface the refusal reason to the user instead. On a resolved (non-refused) scope, the docs-only dispatch fires when the list is non-empty AND every file in it ends in `.md`. Any non-`.md` file in the list means this is not a docs-only branch — route through `requesting-code-review`'s four-way dispatch instead (its mixed-branch per-file split still sends the `.md` files back to this skill's contract). On direct invocation (no `resolved-scope` handed down), also evaluate `requesting-code-review` §Process Step 1's M3 upgrade triggers against the scope you just resolved, before Step 3 — same rule, same literals; cite that heading, do not re-derive it here.
2. **Citation pre-pass.** Run `python3 <resources.doc_citation_checker> <changed .md files> --repo-root <target_repo> --reviewed-sha <reviewed_sha>` (`check_doc_citations.py`) and fold its output into the dispatch packet. `resources.doc_citation_checker` and `reviewed_sha` are the unchanged packet values: never derive a plugin path or read a mutable worktree snapshot. **Exit 0** (no citation finding) and **exit 1** (citation findings) both carry usable output into the panel. **Exit 2** or an **execution failure** REFUSES this station: surface its stderr, **do not dispatch** reviewers, and **do not mint** a marker. Pre-pass findings inside fenced code blocks, blockquotes, table cells, and inline examples are advisory, not defects — documents quoting tool output or deliberately-broken examples trigger false findings.
**Dispatch-profile gate.** **Resolve the dispatch profile** in [`using-loom-code`'s portable profile](../using-loom-code/references/dispatch-profile.md) before the panel's host-native spawn; M3 contributes `frontier`, not a host model literal. The host adapter alone translates the resolved profile. Absent M3 it receives the profile's `standard` baseline; the Claude adapter inherits the main session's effort.
3. **Dispatch TWO `docs-reviewer` subagents in parallel, with byte-identical prompts** (a panel, mirroring `requesting-code-review`'s two-arm convention; agent contract at [`loom-code/agents/docs-reviewer.md`](../../agents/docs-reviewer.md); "byte-identical" means identical to each other). Open each prompt with the agent's role anchor — "You ARE the reviewer" — verbatim. The full immutable context packet from Step 1 is **copied verbatim** into both prompts: `target_repo`, `reviewed_sha`, `plugin_version`, and the approved absolute `resources` paths. No arm derives a plugin path or version from the consumer repository, working directory, or a presumed checkout. Each arm returns the packet `reviewed_sha:` and the panel verdict carries it (§Verdict structure). The dispatch packet also carries branch name, diff scope, changed artifacts, citation pre-pass, `read-context`, and the resolved `tier` plus `requested_effort` and `effective_effort`; translate them once through `dispatch-profile.md` before spawning. Round 1 is always whole-artifact. **`read-context`** is non-`.md` material the reviewers open to verify claims, never review scope; findings against it return to the code arm unscored. Each reviewer reads every changed artifact whole, the diff only as context, and asks: does any unchanged claim in this file contradict the change, or the current code? Score omission (missing obligation or referent), ambiguity (an absolute such as only/never/zero without support), inconsistency (contradiction), incorrect-fact (citation unsupported), and missing-population (number without denominator or scope). Every finding carries `class: instruction | evidence`: instruction is text a reader or executor will act on; evidence is a narrative claim. Unclear class is `instruction` (fail closed).
**Definitions retained.** Inconsistency includes changed-vs-unchanged; incorrect-fact is a citation that does not support its claim; evidence is a narrative claim about what happened or is true; unclear class is tagged `instruction`.
4. **Wait for BOTH verdicts, union the findings, re-aggregate — then mint the gate marker ONLY if this skill owns the whole review.** Union rule as in `requesting-code-review` Step 3: same path + anchor + dimension → one finding, keeping the more detailed wording and the severer severity; optional line precision is ignored for identity, and the same path + anchor under different dimensions stays distinct. Re-run §Aggregation rule on the union — per-dimension score is re-aggregated from that dimension's union findings, not either arm's own: two arms contributing DIFFERENT findings to one dimension can each score clean alone yet union to NEEDS_REVISION, which either arm's own score would miss — never adopt one arm's own verdict. **Mint ONLY when this skill owns the whole review.** If the dispatch packet carried a non-empty `read-context` (Step 3), this invocation is the `.md` half of `requesting-code-review`'s mixed-branch split: **return the verdict to that orchestrator and do NOT mint** — it mints once from the joined verdict after both arms return, and a marker minted here would satisfy `git-guard.py`'s push gate before the code arm has said anything. `read-context` is the signal because it is supplied on exactly the mixed path and is non-empty there by construction. Otherwise (docs-only branch, whether invoked directly or delegated whole) mint here: save the panel verdict text to a temp file and run `python3 <resources.gate_markers> review-pass --repo <target_repo> --verdict-file <file> --expected-head <reviewed_sha>` — `<resources.gate_markers>` is the approved absolute path for `loom_gate_markers.py review-pass` — the docs arm mints the SAME review-pass marker as the code arm (a separate docs marker would break the `git-guard.py` push gate); the approved absolute marker path, target repository, and expected SHA are from the unchanged packet, the prose dimension names are schema-valid to the marker script, and `NEEDS_REVISION` or a malformed verdict refuses to mint (exit 3/4). Dead-arm rule: an arm that errors out with no verdict is re-dispatched once; if it dies again, proceed single-arm and say so in the verdict summary and the user relay. An arm returning `verdict: MALFORMED_PACKET` is neither a scored verdict nor a dead arm: fix the packet, then re-dispatch that arm with the corrected packet; its refusal contributes no findings to the union. One packet-fix re-dispatch is the bound: a second `MALFORMED_PACKET` on a packet that passed `--validate` surfaces to the user instead of another retry.
5. **Surface to user.** Present the verdict, its `reviewed_sha:`, the instruction-class findings (these gated — Directive 2's delta confirmation follows once they are fixed), and the evidence-class findings (recorded observations, never gating). Do NOT auto-fix — remediation is the user's decision, even for a one-word nit.
6. **Host-specific terminal confirmation — only when round 1 raised a gating verdict.** Once the surviving instruction-class findings are fixed, obtain one fresh immutable context packet for the **post-fix SHA**: adopt an upstream post-fix packet verbatim when supplied, otherwise ask the active host adapter to resolve its installed plugin root and run `review_context.py`. Form the **post-fix confirmation packet** from `target_repo`, `reviewed_sha`, `plugin_version`, `resources`, the original gating findings, and delta evidence. On **Claude Code**, send that packet to the SAME reviewer instance(s) (`docs-reviewer`) via `SendMessage`; it checks the original findings against the delta evidence. On **Codex**, dispatch a **labelled fresh whole-artifact review** with the same complete post-fix confirmation packet; its ordinary verdict is normalized, not treated as a second independent gate. Map ordinary `PASS` or `PASS_WITH_NOTES` to `CONFIRMED_RESOLVED` only when every original gating finding is fixed; map `NEEDS_REVISION` to `STILL_BLOCKING` + reason. A confirmation reviewer returning `verdict: MALFORMED_PACKET` means the post-fix confirmation packet is defective: fix the packet and re-send the confirmation; it is NOT `STILL_BLOCKING` and not a quality verdict. Each route echoes the fresh packet `reviewed_sha`. `CONFIRMED_RESOLVED` is terminal evidence, but **must not mint CONFIRMED_RESOLVED directly**: the orchestrator combines the original panel verdict with the successful confirmation and emits a **schema-valid terminal wrapper** for the current packet — `standards_version: <plugin_version>`, `reviewed_sha: <reviewed_sha>`, no unresolved instruction-class findings, and the aggregation outcome. With no evidence floor this is `verdict: PASS` and five PASS `dimension_scores`. If an original panel R3 floor is `PASS_WITH_NOTES`, preserve it in the wrapper's verdict and affected dimension score: **must not upgrade** R3 evidence to `PASS`. On a docs-only review, validate that wrapper then mint only with `python3 <resources.gate_markers> review-pass --repo <target_repo> --verdict-file <wrapper-file> --expected-head <reviewed_sha>` from the fresh packet; on a mixed review, return the wrapper to the upstream joined-verdict route and do not mint here. Report "no gating findings" or "confirmed resolved," never "clean." `STILL_BLOCKING` after this one cycle STOPs the review: surface the finding and the reviewer's reason to the user; no second cycle without their explicit authorization. Render the findings per the adjudication-view protocol (verdict mode) when that protocol's own §Firing conditions are met — see [`../using-loom-code/protocols/adjudication-view.md`](../using-loom-code/protocols/adjudication-view.md).

## Aggregation rule

Thresholds are `requesting-code-review` §Aggregation rule, unchanged: any 🔴 → `NEEDS_REVISION`; any finding with empty/missing `where:` → `NEEDS_REVISION` regardless of severity; 2+ 🟡, no 🔴 → `NEEDS_REVISION`; exactly 1 🟡 → `PASS_WITH_NOTES`; only 🟢 or none → `PASS`. These thresholds are inherited unexamined from `requesting-code-review`, where they sit on top of a passing test suite (the docs arm has only grep-window pins beneath it) — no docs-specific evidence sets them. The docs arm selects what is fed into the rule, not its thresholds:

- The rule is computed over **instruction-class findings only**; evidence-class findings are carried into the verdict as recorded observations that **do not gate**.
- A finding missing `class:` counts as instruction (fail closed), consistent with a finding missing `where:` flipping the whole verdict.
- A defect noticed **inside** a `read-context` file (Step 3) is not a finding of this arm at all: it carries no severity, no dimension and no `class:`, rides in the separate `read_context_findings:` block, and never enters a dimension score. **It gates nothing, on either arm, and nobody assigns it a severity later** — the orchestrator surfaces it in the report and hands it to the code arm as context, and that arm reviews those files on this same branch under its own rubrics anyway. Deliberate: a defect the docs arm noticed incidentally, in a file it was not scoped to judge, must not decide a verdict. A defect in what a reviewed `.md` **claims about** such a file is an ordinary finding and gates normally — that is the primary case `read-context` exists to serve.
- **The same exclusion covers `out_of_scope:`** (§Verdict structure's block for a non-gating observation a confirmation declines to raise): those entries carry no severity, no dimension and no `class:`, never enter a dimension score, and the fail-closed `class:` bullet above does NOT reach them — they are not findings. A new gating problem found by either host remains an ordinary scored finding and therefore produces `NEEDS_REVISION`. Surface non-gating observations to the user with the verdict; persisted nowhere — deferral survives only if the user or orchestrator acts on it.
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

out_of_scope:                       # omit when there is no non-gating
                                     # observation outside the original
                                     # confirmation findings
  - where: <path + anchor; line optional>
    note: <a non-gating observation noticed while confirming a fix>
    # Never use for a new gating problem: emit that as an ordinary
    # instruction-class finding so it is scored. These entries are emitted,
    # never scored, and surfaced to the user with the verdict;
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
