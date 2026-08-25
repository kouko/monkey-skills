---
name: requesting-code-review
description: |
  Use BEFORE any push/merge/PR on a non-trivial branch — whole-branch review of the cumulative diff. Fires on 'review my branch', 'ready to merge?', and excuses it refuses: 'just push', 'skip review', git push / gh pr create with no prior review-PASS.
version: 0.13.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## Live-gate receipt (CODE / MIXED only)

Only when all five `LOOM_LIVE_GATE_PACKET`, `LOOM_LIVE_GATE_MARKER_DIR`,
`LOOM_LIVE_GATE_NONCE`, `LOOM_LIVE_GATE_PLUGIN_ROOT`, and
`LOOM_LIVE_GATE_REPO` are supplied: after consuming the handed packet, run
exactly one matching command (no wrapper, redirection, prefix, or suffix):

- CODE: `python3 "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py" --packet "$LOOM_LIVE_GATE_PACKET" --plugin-root "$LOOM_LIVE_GATE_PLUGIN_ROOT" --marker-dir "$LOOM_LIVE_GATE_MARKER_DIR" --repo "$LOOM_LIVE_GATE_REPO" --station CODE --nonce "$LOOM_LIVE_GATE_NONCE"`
- MIXED: `python3 "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py" --packet "$LOOM_LIVE_GATE_PACKET" --plugin-root "$LOOM_LIVE_GATE_PLUGIN_ROOT" --marker-dir "$LOOM_LIVE_GATE_MARKER_DIR" --repo "$LOOM_LIVE_GATE_REPO" --station MIXED --nonce "$LOOM_LIVE_GATE_NONCE"`

Otherwise do nothing. Never re-run `review_context.py` in a live-gate station;
the runner-owned packet is the sole packet source.

## What this skill does

Dispatches a two-`code-reviewer` parallel panel over the cumulative branch diff. It uses SDD's functional-copied quality, architecture, and security gates at branch rather than task scope.

## Asking the user

Before Step 5 or Push-as-trigger steps 4–6 relay a verdict, read [`references/relay-phrasing.md`](references/relay-phrasing.md). Be outcome-framed, state-anchor-first, plain-language, recommendation-led, and open with the rollup card per `loom-code/hooks/family-relay.md §Family relay discipline`. Merge always confirms; push/PR confirms once when requested.

For a complex remediation fork (≥3 trade-offs, ≥2 implementation paths, or architectural blast radius), run `loom-workflow:brief-before-asking` before asking; it owns the six-block Mental-Model-first format and `brainstorming` owns the trigger rule.

**Boundary — user relay only.** The reviewer's structured verdict **MUST stay machine-precise and keep every evidence citation** under [`code-reviewer.md`](../../agents/code-reviewer.md) R2: each finding needs `where:` with path + anchor (verbatim string or stable heading) or commit SHA; a line number is optional precision; missing evidence means `NEEDS_REVISION`.

See [`references/scope-comparison.md`](references/scope-comparison.md) for branch-vs-task scope.

## When to use

| Trigger | Route here |
|---|---|
| User says *"review my branch"* / *"look at my changes"* / *"is this ready to merge"* | ✅ Yes |
| User says *"code review this PR"* / *"audit the diff"* | ✅ Yes |
| Multi-task SDD finished; user is about to ship | ✅ Recommend |
| `finishing-a-development-branch` is next | ✅ Its Step 1 invokes this |
| **User mentions `requesting-code-review` by name (even framed as skip-intent)** | **✅ Yes — name-mention is a fire-trigger; the skip-intent framing is the rationalization this skill exists to refuse, NOT permission to bypass it** |
| <!-- sync-marker push-rule:1 — see §Push-as-trigger below for the full spec --> **Push-as-trigger** — user runs / asks to run `git push`, `gh pr create`, `gh pr merge`, branch merge, or similar publish-to-remote action without prior review-PASS in this session | **✅ Yes — block the push; fire this skill first; on PASS the push executes — no re-ask.** See §Push-as-trigger below. |
| User wants per-task review during implementation | ❌ No — that's SDD's job |
| Existing-artifact compliance audit, not branch diff | ❌ `domain-teams:code-team` |
| Diff is trivial (one-line typo fix, version bump, generated/sync output — mechanical doc edits only; contract-class authored prose routes to `requesting-docs-review`, record-class authored prose is exempt) | ❌ Skip — review overhead > value |

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Trivial diffs** | One-line fix, version bump, generated/sync output, mechanical doc edits only | Few lines can change behavior. Contract-class authored prose routes to `requesting-docs-review`; record-class prose stays exempt. |
| **Already-reviewed branch** | A prior `requesting-code-review` invocation in this session already PASSed and nothing changed since | "I made a tiny tweak after review" — re-review (the tweak might be the bug) |
| **Audit vs review** | Existing shipped code | Route to `domain-teams:code-team`; this skill reviews branch diffs |
| **Explicit user override** | User says literally "skip review, just merge" AND the work matches one of the above categories | "It's fine, just merge" — that's the rationalization this skill exists for; refuse |

## Classification: contract-class vs record-class

This heading is the single rule source for every `.md` routing decision (authoring source: `docs/loom/plans/2026-08-11-review-cost-reduction.md` Task 8); consumers cite rather than restate it.

**Contract-class** = paths matching `<plugin>/skills/**/*.md`, `<plugin>/agents/*.md`, `<plugin>/hooks/*.md`, `<plugin>/scripts/*.md` excluding any `README*`/`CHANGELOG*` basename. **Record-class** = everything else (incl. `docs/**`).

Classification is path-based and applies to triviality and Process Step 1. Record-class `.md` files are exempt from review at any mix.

## Push-as-trigger

**Any push-to-remote action without this session's review-PASS fires this skill before the push.** This includes:

- any `git push` form;
- `gh pr create`, `gh pr merge`, or `gh pr merge --auto`;
- any helper invoking them.

Push-intent excuses and their refusals: see [`references/push-trigger-rationalizations.md`](references/push-trigger-rationalizations.md).

**Procedure when push-as-trigger fires**:

0. **Route close-out first.** If the branch is done, ready to merge, or opening a merge-intended PR, STOP and invoke `finishing-a-development-branch`; its Step 1 still runs this review and adds verification, memory timing, and the git-memory decision. Continue here only for explicit review-without-merging.
1. **Do NOT execute the push.**
2. Quote the matching [`push-trigger-rationalizations`](references/push-trigger-rationalizations.md) row.
3. **Offer to run review now**: "Dispatching `requesting-code-review` — back in ~30s." Resolve via `review_scope.py` (or the user's explicit range), then run **§Process from Step 1** so docs routing cannot be skipped. A refusal STOPS before dispatch. Otherwise use the two-reviewer union and re-aggregation.
4. **After PASS**: the push WAS the request — execute it (branch-qualified form) and report loudly what was pushed. Do not re-ask.
5. **After NEEDS_REVISION**, surface findings and do not push.
6. **After PASS_WITH_NOTES**: push, carrying every finding verbatim into the report (and the PR body if one follows) — consistent with `finishing-a-development-branch` Step 3's auto-proceed. Do NOT fix findings inline silently.

Any further question this flow surfaces runs the ask-vs-resolve triage at `subagent-driven-development` §Asking the user, gate ① (the cross-skill SSOT) before it reaches the user.

<!-- sync-marker push-rule:2 — full Push-as-trigger spec. The §When to use table row above is the 1-row summary; keep these two in sync. -->

This rule applies without explicit invocation: frontmatter encodes push commands and skip excuses for host auto-discovery.

## Process

At the start of each review round (round 1 included), run `python3 scripts/plan_card.py <plan-path> --set-stage "review:round-N"` — the script prints the refreshed card; relay it — and commit the flip with that round's verdict or fixes; hand-edit only when the script is absent. If the repo copy is missing, run `python3 <installed-plugin-root>/scripts/plan_card.py <plan-path> --set-stage "review:round-N"`; hand-edit only when neither copy is present.

1. **Determine diff scope, then route by file type**. Use the active host's immutable review-context adapter from loaded [`claude-code-tools.md`](../using-loom-code/references/claude-code-tools.md) or [`codex-tools.md`](../using-loom-code/references/codex-tools.md) to derive `<installed-plugin-root>` and run `python3 <installed-plugin-root>/scripts/review_context.py --repo <path>` once; never derive it from the consumer repo, cwd, cache, or environment. Preserve its packet unchanged (`target_repo`, `reviewed_sha`, `plugin_version`, absolute `resources`), write it to a file, then run `python3 <installed-plugin-root>/scripts/review_context.py --validate <packet-file>`; nonzero **REFUSES the fan-out: do not dispatch any reviewer**. Skip validation only in a live-gate station, whose receipt already validated it via `live_gate_station_receipt.py` and forbids rerunning `review_context.py`. Resolve scope with `python3 <resources.review_scope> --repo <target_repo> --reviewed-sha <reviewed_sha>` (`review_scope.py`), or the user's explicit `git diff <SHA1>..<SHA2>` only when the explicit range endpoint equals `reviewed_sha`. Any nonzero result or endpoint mismatch **REFUSES before dispatch or marker minting**; surface stderr and any stale-base rebase remedy.

   **§Pinned refusal contract** (transcribed verbatim): A stale base, or any failure to establish freshness, REFUSES. The resolver never returns a file list it cannot vouch for, and a station that receives a refusal STOPS before dispatching anything.

   A refusal STOPS before dispatch; surface it per §Asking the user and never use a disk-derived fallback. Otherwise classify `.md` paths per §Classification and route four ways:
   - **Record-only branch** — the file list is non-empty AND every file in it is a record-class `.md` file (no contract-class `.md`, no non-`.md`) → run NO docs arm, NO code-reviewer panel; satisfy the push gate via the packet-approved record-only continuity marker: `python3 <resources.gate_markers> mint --repo <target_repo> --expected-head <reviewed_sha> --review-na-record-only`; the script re-verifies the changed-file set is record-class and that the packet target HEAD still equals `reviewed_sha`, refusing loudly otherwise.
   - **Docs-only branch** — the file list is non-empty, every file in it ends in `.md`, AND at least one is contract-class → **delegate the review to [`requesting-docs-review`](../requesting-docs-review/SKILL.md)**: invoke that skill, handing it ONLY the contract-class subset as `resolved-scope`, the same unchanged immutable context packet from Step 1 — `target_repo`, `reviewed_sha`, `plugin_version`, and `resources` — and the profile tier set by M3 below; record-class `.md` files are exempt, dropped from scope — and stop here — do not dispatch the code-reviewer panel below. It owns the docs semantics end-to-end (whole-artifact scope, the five prose dimensions, `class:` tagging, instruction-only aggregation, the citation pre-pass, its single-round-plus-delta-confirmation convergence contract (its own Directives, not restated here)) and mints the same review-pass gate marker.
   - **Mixed branch** — the list contains both `.md` and non-`.md` files → per-file split: the non-`.md` files go to the code-reviewer panel below (Steps 2-3, diff scoped to those files); the `.md` files go to the docs arm per `requesting-docs-review`'s panel contract, restricted to the contract-class subset (record-class exempt at any mix) — handing it that subset as `resolved-scope`, the same unchanged immutable context packet from Step 1 — `target_repo`, `reviewed_sha`, `plugin_version`, and `resources` — the non-`.md` file list as `read-context`, **and the profile tier per M3** in its dispatch packet (its two-`docs-reviewer` dispatch + aggregation, run to produce a verdict — its own mint step does not fire here). No contract-class file → no docs arm dispatches. **`read-context` is material the docs arm opens to verify claims against, never scope it reviews** — semantics and the recorded miss it closes are in `requesting-docs-review` Step 3, whose verdict also returns a separate unscored `read_context_findings:` block: surface it, never score it — it gates nothing. The orchestrator unions both arms' findings for the surfaced report, and the branch verdict is the WORSE of the two arm verdicts — either arm `NEEDS_REVISION` → branch `NEEDS_REVISION`. **Mint the review-pass marker once, from this joined verdict only through Step 4's shared ledger-and-mint mechanics** — neither arm mints its own marker on a mixed branch; the joined verdict first receives its simplification ledger, then the same Step 4 clean-marker conditions apply.
   - **Code-only branch** — no `.md` file in the list → the default code path below, unchanged.

   **§Pinned pass-down contract** (transcribed verbatim): The delegating station hands the delegate the resolved scope as `resolved-scope` in the dispatch packet. The delegate resolves scope itself ONLY when no `resolved-scope` was supplied.

   **M3 — mechanical upgrade rule (docs arm only).** A branch whose changed contract-class files include any `agents/*.md`, or changes 10 or more contract-class `.md` files, sets the dispatch packet's profile tier to `frontier`; [`dispatch-profile.md`](../using-loom-code/references/dispatch-profile.md) translates it to the host call. A contested 🔴 — the delta confirmation returned `STILL_BLOCKING` and the fix author maintains the finding is factually wrong — gets ONE second-opinion review one tier above the arm's current tier; if already `frontier`, the dispute goes to the user instead. Honesty note: catch-quality-by-tier is UNMEASURED — the upgrade rule is the hedge.
2. **Resolve the dispatch profile** in [`dispatch-profile.md`](../using-loom-code/references/dispatch-profile.md), then **dispatch TWO `code-reviewer` subagents in parallel, with byte-identical prompts** (role `loom-code:code-reviewer`; plugin-level agent at [`code-reviewer.md`](../../agents/code-reviewer.md)). Use one-shot blocking host calls; Claude issues both `Agent()` calls in one message and must not name async teammates; see [environment gotchas](../using-loom-code/references/environment-gotchas.md). Open each prompt verbatim with **"You ARE the reviewer"**. Give both the full immutable context packet, diff range, absolute rubric/checklist paths, branch context, the profile's dispatch record, and identical conditional additions. Neither arm derives plugin paths/version from `target_repo`; both carry [`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md).
   - **Principles-conformance discovery (conditional, self-derived):** each reviewer checks `docs/loom/PRINCIPLES.md`; the orchestrator may give both a non-standard-path override but omission never disables discovery. If neither resolves, emit `principles-conformance: N/A`. Never synthesize principles.
3. **Wait for BOTH verdicts, union the findings, and re-aggregate** (on a mixed branch, this step computes only the code arm's own verdict; the branch verdict joins both arms per Step 1). Each reviewer returns its own structured review with per-dimension scores, severity-tagged findings, and a verdict; wait for both before proceeding. **Union the two findings lists** — no cross-arm adjudication **layer** is needed; the mechanical merge rule: "the same finding" = same path + anchor AND dimension → one line, keeping the more detailed wording and **severer** severity; ignore optional line-number precision when matching. Same location but different dimensions stay distinct; anchor vs commit-SHA cites are distinct (fail-closed — over-counting only pushes the verdict stricter). Then **re-run the §Aggregation rule on the union** — per-dimension score is re-aggregated from that dimension's union findings, not either arm's own — to produce the panel verdict; never pick one arm's own verdict. Preserve every R3 downgrade from either arm in that verdict; do not collapse it to PASS. **Dead-arm rule**: if an arm errors out with no verdict, re-dispatch that arm once; if it dies again, proceed single-arm but say so in BOTH the verdict summary and the user relay (a single-arm verdict is degraded evidence — G4 measured why). Capacity-error recovery: [`dispatch-hygiene-notes.md`](../subagent-driven-development/references/dispatch-hygiene-notes.md) §Capacity-error recovery. An arm returning `verdict: MALFORMED_PACKET` is neither a scored verdict nor a dead arm: fix the packet, then re-dispatch that arm with the corrected packet; its refusal contributes no findings to the union. One packet-fix re-dispatch is the bound: a second `MALFORMED_PACKET` on a packet that passed `--validate` surfaces to the user instead of another retry. On the code-only path, defer marker minting to Step 4; on a mixed branch, Step 4 receives the joined verdict from Step 1. Do not mint a marker yet: Step 4 must first attach the deliberate-simplification evidence to this verdict.
4. **Harvest the deliberate-simplification ledger**. Inspect `LOOM-SIMPLIFY:` markers for scope-bounded branch shortcuts. Reuse Step 1's resolved file list; read each path from the immutable packet snapshot:

   ```
   for path in <files from Step 1's review_scope.py output>; do
     git -C <target_repo> show <reviewed_sha>:<path> | grep -n "LOOM-SIMPLIFY:"
   done
   ```

   Record hits in `simplification_ledger`; require checkable `ceiling:`, `upgrade:`, `ref:`, `marker_valid: true`, and `snapshot_read: verified`, or emit a finding. No hits is `[]`. A missing path or failed snapshot read records `marker_valid: false` / `snapshot_read: failed`, emits a finding, and uses the packet snapshot — never the mutable working tree or current HEAD. Only after those checks, if the panel verdict is `PASS` or `PASS_WITH_NOTES` with a valid simplification ledger, whether empty or nonempty, run `python3 <resources.gate_markers> review-pass --repo <target_repo> --verdict-file <file> --expected-head <reviewed_sha>`. The gate independently refuses a nonempty ledger with missing fields, `marker_valid: false`, or `snapshot_read` other than `verified`. An R3 downgrade alone does not block this marker path; a simplification finding prevents this marker path. The script validates before writing and refuses if the packet target's HEAD drifts from `reviewed_sha`, `NEEDS_REVISION`, or malformed input. `loom_gate_markers.py validate --verdict-file <file>` is dry-run. The marker binds `reviewed_sha`; any later commit needs a fresh verdict.
5. **Surface to user**. Print the verdict + findings + the simplification ledger; let user decide remediation. Do NOT auto-fix — that's user agency, even for a trivial single-line nit. Silently auto-fixing then re-reviewing removes the user's decision point and burns an extra review round. **Phrase this relay per §Asking the user** — translate `🔴/🟡/🟢` + the verdict token into plain language and open with a state anchor; the reviewer agent's structured output stays machine-precise. The ledger surfaces in plain language too: each shortcut as "what corner was cut, when it breaks, how to upgrade." Render the findings for the user per the [`adjudication-view`](../using-loom-code/protocols/adjudication-view.md) protocol (verdict mode) whenever that protocol's own §Firing conditions are met — the structured verdict block above stays machine-precise and untouched.
6. **Re-dispatch if user fixed and wants re-review** — same skill, fresh subagent (no state carry-over between rounds for clean evaluation).

Cross-skill delegation passes paths, not content — see [`references/cross-skill-map.md`](references/cross-skill-map.md) for the full directional map (upstream / downstream / lateral).

## Verdict structure

Returns:

```
standards_version: "{X.Y.Z — value of `version` in loom-code/.claude-plugin/plugin.json}"
reviewed_sha: "{packet's immutable `reviewed_sha` — echoed verbatim}"

verdict: PASS | PASS_WITH_NOTES | NEEDS_REVISION

dimension_scores:
  security: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  architecture: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  correctness: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  naming: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  tests: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  refactoring: PASS | PASS_WITH_NOTES | NEEDS_REVISION
  cross-task-coherence: PASS | PASS_WITH_NOTES | NEEDS_REVISION  # NEW at branch scope
  external-surface-grounding: PASS | PASS_WITH_NOTES | NEEDS_REVISION  # mirrors per-task D7 + cross-task surface-consistency
  principles-conformance: PASS | PASS_WITH_NOTES | NEEDS_REVISION | N/A  # vs consumer PRINCIPLES.md; N/A when absent
  deliberate-simplification: PASS | PASS_WITH_NOTES | NEEDS_REVISION  # LOOM-SIMPLIFY marker harvest + completeness check; PASS with empty ledger when no markers
  deletion-first: PASS | PASS_WITH_NOTES | NEEDS_REVISION

findings:
  - severity: 🔴 fatal | 🟡 should-fix | 🟢 nit
    dimension: <which of the dimensions scored above>
    where: <path + anchor; line optional>     # REQUIRED — empty/missing flips verdict to NEEDS_REVISION
    source: <rubric / checklist / standard file:section that triggered this>
    note: <1-2 sentence finding>
    origin: none | <path> :: "<verbatim quote from that file>"  # REQUIRED on code-arm findings only (docs-arm exempt, per Step 1) — quote-gate rule owned by `code-reviewer.md` §Output contract — what you return `origin:` field; not restated here
    class: instruction | evidence              # docs-arm findings only (mixed branches, per Step 1) — semantics owned by requesting-docs-review; omitted for code-branch findings

simplification_ledger:                         # grep -rn "LOOM-SIMPLIFY:" over the branch diff (Step 4); [] when none
  - where: <path + anchor; line optional>
    shortcut: <what corner was cut>
    ceiling: <checkable condition under which it breaks>
    upgrade: <path to the proper version>
    ref: <originating brief/task>
    marker_valid: true | false                  # false when ceiling:, upgrade:, or ref: is missing (or ceiling: uncheckable) → also emit a finding
    snapshot_read: verified | failed            # verified only when read via reviewed_sha; failed always emits a finding and blocks marker minting

summary:
  - <≤5 bullet observations about the branch as a whole>
```

`simplification_ledger` records Step 4's scope-bounded shortcuts; `[]` means none. `marker_valid: false` is a finding per
[`../subagent-driven-development/standards/deliberate-simplification.md`](../subagent-driven-development/standards/deliberate-simplification.md) §Field Rules.

`standards_version` lets downstream readers tell whether a verdict was scored under the rules in effect now or a prior revision; the standards/rubrics/checklists ship together.

**Aggregation rule** (same as SDD's code-quality-reviewer with the added cross-task dimension; aligned with `rubrics/quality-gate.md` §Verdict Rules):

- Any 🔴 → `verdict: NEEDS_REVISION`
- Any finding with empty / missing `where` → `verdict: NEEDS_REVISION`
  regardless of severity (opaque finding = malformed verdict)
- **2 or more 🟡 warning findings, no 🔴** → `verdict: NEEDS_REVISION`
  (rubric §Verdict Rules — aggregated warnings signal systemic concern).
  **Self-check before writing the `verdict:` token**: count the 🟡 findings; if count ≥ 2 and no 🔴, the verdict is `NEEDS_REVISION`, not `PASS_WITH_NOTES`.
- Exactly 1 🟡 warning finding, no 🔴, all with `where` → `verdict: PASS_WITH_NOTES`
- No 🔴, no 🟡 (only 🟢 informational findings or no findings) → `verdict: PASS`
- An R3 downgrade from either panel arm sets the panel verdict floor to at
  least `PASS_WITH_NOTES`, even when the findings union is otherwise empty.
  Apply this floor after findings aggregation; it is evidence status, not a
  finding to count toward the warning threshold.

**Docs findings**: docs-only branches and the `.md` arm of mixed branches aggregate under [`requesting-docs-review`](../requesting-docs-review/SKILL.md) §Aggregation rule (instruction-class gating lives there, not here); the mixed-branch verdict join is Step 1's worse-of-the-two-arm-verdicts rule.

**Panel union**: each arm's own `verdict:` is advisory only — the gate verdict is produced by applying the aggregation rule above to the **union** of both arms' findings (§Process Step 3), never by picking one arm's verdict. Supporting evidence and the panel-width exit clause: [`references/design-evidence.md`](references/design-evidence.md) (author-facing; not loaded at runtime).

## Red Flags — refuse these rationalizations

Refuse silent review-skip excuses, including “small change,” “SDD reviewed tasks,” “after CI,” or “user said skip” (also 審查跳過 / レビューはスキップ). See [`references/red-flags.md`](references/red-flags.md).

## What this skill does NOT do

- Does **not** modify code. Reviewer is evaluator-only; remediation is user / implementer.
- Does **not** replace `subagent-driven-development`'s per-task reviewer. Both layers serve different scopes.
- Does **not** replace `verification-before-completion`. This skill is human-judgment review; verification-before-completion is test-suite-run gate. Both fire before `finishing-a-development-branch` commits.
- Does **not** auto-trigger CI. Pushing to remote triggers CI; this skill runs before push.

## See also

- [`loom-code/agents/code-reviewer.md`](../../agents/code-reviewer.md) — the dispatched plugin-level subagent's role contract + input/output contracts.
- [`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md) — SSOT for the 12-rule engineering baseline carried by the code-reviewer agent.
- [`../requesting-docs-review/SKILL.md`](../requesting-docs-review/SKILL.md) — the docs arm Step 1 delegates to (docs-only branches whole; the `.md` arm of mixed branches).
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — per-task reviewer (different scope, same rubrics).
- [`quality-gate.md`](../subagent-driven-development/rubrics/quality-gate.md) — functional copy of code-team's quality rubric.
- [`arch-gate.md`](../subagent-driven-development/rubrics/arch-gate.md) — functional copy of code-team's architecture rubric.
- [`security-checklist.md`](../subagent-driven-development/checklists/security-checklist.md) — functional copy of code-team's security checklist.
- `loom-code/agents/docs-reviewer.md` and `loom-code/scripts/loom_gate_markers.py` — consumers of the routing and marker contracts above.
- [`../subagent-driven-development/standards/deliberate-simplification.md`](../subagent-driven-development/standards/deliberate-simplification.md) — the `LOOM-SIMPLIFY:` marker convention + grep-on-demand harvest rule this skill surfaces at the merge gate (§Process Step 4).
- [`references/gate-markers-spec.md`](references/gate-markers-spec.md) — verdict-text schema, the `verified --run` real-execution binding, waiver semantics, the patch-id relaxation (`base_sha`/`patch_id`), the `validate` dry-run subcommand, and the write-markers-then-push-separately ordering rule.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — sibling skill that fires alongside this one in finishing-a-branch flow.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator that invokes this skill.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 6 (Review).
- `domain-teams:code-team` — passive gate for large audits; this skill may escalate there for >500 LOC or security-sensitive reviews.
