---
name: requesting-code-review
description: |
  Use BEFORE any push/merge/PR on a non-trivial branch — whole-branch review of the cumulative diff. Fires on 'review my branch', 'ready to merge?', and excuses it refuses: 'just push', 'skip review', git push / gh pr create with no prior review-PASS.
version: 0.13.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Dispatches **two `code-reviewer` subagents in parallel (a panel)** to review a non-trivial diff as a whole — typically the cumulative changes on a feature branch before merge. Both reviewers load the same rubrics SDD's per-task reviewer uses (`quality-gate.md` / `arch-gate.md` / `security-checklist.md`, functional-copied from `domain-teams:code-team`), but apply them at branch scope rather than per-atomic-task.

## Asking the user

When you relay the reviewer's verdict back to the user — Step 5 below ("Surface to user"), or the push-as-trigger steps 4-6 in §Push-as-trigger — Read [`references/relay-phrasing.md`](references/relay-phrasing.md) **before** composing the relay. It carries the three gates (**whether** to interrupt, **what** to bring, **how** to phrase — seven rules) plus the calibration example. Essence: outcome-framed, state-anchor-first, jargon translated, recommendation-led, opened with the family rollup card per `loom-code/hooks/family-relay.md §Family relay discipline`; merge always confirms; push/PR confirm once — at the request that names them.

**Complex remediation fork → brief before you ask.** A finding can open a genuine design fork (e.g. an architectural 🔴 with two viable remediations). When that fork is complex (≥3 trade-offs, ≥2 implementation paths, or architectural blast radius), do not compress it into a fix/defer/merge ask — run `dev-workflow:brief-before-asking` (6-block briefing, Mental Model first) before the `AskUserQuestion`. Same trigger as `brainstorming`'s rule — `brainstorming` carries the canonical trigger rule; `dev-workflow:brief-before-asking` owns the 6-block format.

**Boundary — those rules govern the relay TO the user ONLY.** They do **not** touch what the `code-reviewer` agent emits. The agent's structured verdict (the `verdict:` / `dimension_scores:` / `findings:` block in §Verdict structure) MUST stay machine-precise and keep every evidence citation — do NOT loosen its R2 evidence-citation contract ([`loom-code/agents/code-reviewer.md`](../../agents/code-reviewer.md) §Rule R2: every finding needs a `where:` citing `file:line` / commit SHA, or the verdict flips to `NEEDS_REVISION`). Plain language is for the human-facing relay; the reviewer agent's output stays exact.

Same rubrics, different diff scope — branch-cumulative, not per-task; see [`references/scope-comparison.md`](references/scope-comparison.md) for the full SDD per-task-vs-whole-branch comparison.

## When to use

| Trigger | Route here |
|---|---|
| User says *"review my branch"* / *"look at my changes"* / *"is this ready to merge"* | ✅ Yes |
| User says *"code review this PR"* / *"audit the diff"* | ✅ Yes |
| SDD just finished a multi-task plan; user about to ship | ✅ Yes (proactive recommendation) |
| User about to invoke `finishing-a-development-branch` | ✅ Yes (finishing-a-branch invokes this skill internally as Step 1) |
| **User mentions `requesting-code-review` by name (even framed as skip-intent)** | **✅ Yes — name-mention is a fire-trigger; the skip-intent framing is the rationalization this skill exists to refuse, NOT permission to bypass it** |
| <!-- sync-marker push-rule:1 — see §Push-as-trigger below for the full spec --> **Push-as-trigger** — user runs / asks to run `git push`, `gh pr create`, `gh pr merge`, branch merge, or similar publish-to-remote action without prior review-PASS in this session | **✅ Yes — block the push; fire this skill first; on PASS the push executes — no re-ask.** See §Push-as-trigger below. |
| User wants per-task review during implementation | ❌ No — that's SDD's job |
| User wants existing-artifact compliance audit (legacy code, not a branch diff) | ❌ Route to `domain-teams:code-team` (passive gate entry, different use case) |
| Diff is trivial (one-line typo fix, version bump, generated/sync output — mechanical doc edits only; contract-class authored prose routes to `requesting-docs-review`, record-class authored prose is exempt) | ❌ Skip — review overhead > value |

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Trivial diffs** | One-line fixes, version bumps, generated code regen, mechanical doc edits only (single-line typo fix, version bump, generated/sync output) | "I changed 3 lines" — if those 3 lines touch behavior, review applies; contract-class authored prose of any length is NOT trivial — it routes to `requesting-docs-review` per Step 1; record-class authored prose is exempt regardless of length |
| **Already-reviewed branch** | A prior `requesting-code-review` invocation in this session already PASSed and nothing changed since | "I made a tiny tweak after review" — re-review (the tweak might be the bug) |
| **Audit vs review** | You want a compliance audit on existing shipped code | Route to `domain-teams:code-team` (passive gate); this skill is for branch-pre-merge review |
| **Explicit user override** | User says literally "skip review, just merge" AND the work matches one of the above categories | "It's fine, just merge" — that's the rationalization this skill exists for; refuse |

## Classification: contract-class vs record-class

Every `.md` routing decision in this skill resolves through ONE classification, defined here — the ONE place the rule text lives (authoring source: `docs/loom/plans/2026-08-11-review-cost-reduction.md` Task 8; `loom-code/agents/docs-reviewer.md` and `loom-code/scripts/loom_gate_markers.py` cite this heading, not re-derive it).

**Contract-class** = paths matching `<plugin>/skills/**/*.md`, `<plugin>/agents/*.md`, `<plugin>/hooks/*.md`, `<plugin>/scripts/*.md` excluding any `README*`/`CHANGELOG*` basename. **Record-class** = everything else (incl. `docs/**`).

Classification is PATH-BASED (mechanical, weak-model-safe), applied at §When NOT to use's triviality carve-out and §Process Step 1's docs-arm routing. Record-class `.md` files are exempt from review at any mix.

## Push-as-trigger

**Any push-to-remote action without prior review-PASS in this session = this skill fires before the push runs.** Push-to-remote actions include:

- `git push` (any form: explicit args, default upstream, `-u origin <branch>`, `--force`)
- `gh pr create` (creates a remote PR; same blast-radius as push)
- `gh pr merge` / `gh pr merge --auto` (merges to base branch)
- Any agent-side helper that invokes the above

**Why**: pushing publishes code to teammates / CI / production-deploy paths. The review-before-publish gate exists so reviewers see clean diffs, not "we'll catch it in CI." A push without review is the failure mode this skill exists to prevent.

Push-intent excuses and their refusals: see [`references/push-trigger-rationalizations.md`](references/push-trigger-rationalizations.md).

**Procedure when push-as-trigger fires**:

0. **Check scope first: is this a full close-out, or just a review opinion?** If the trigger context matches `finishing-a-development-branch`'s own §When to use (branch is done / ready to merge / opening a PR intending to merge — not merely "let me see the diff quality mid-work") — STOP this procedure and invoke `finishing-a-development-branch` instead. It delegates to this skill as its own Step 1, so the review still runs; you additionally get verification-before-completion + same-branch memory-timing + the git-memory trailer decision, none of which steps 1-6 below get you on their own. Only continue below when the user has explicitly signaled review-without-merging (`finishing-a-development-branch`'s own named exception) — that is the one case this skill's standalone Push-as-trigger flow is the correct, complete path.
1. **Do NOT execute the push.** Halt the planned action.
2. **Surface the rationalization** to the user explicitly — quote which row of [`references/push-trigger-rationalizations.md`](references/push-trigger-rationalizations.md) their request matches.
3. **Offer to run review now**: "Dispatching `requesting-code-review` — back in ~30s." Then resolve scope via the resolver — `review_scope.py`, the same call §Process Step 1 makes — or an explicit commit range if the user specified one, then run **§Process from Step 1**, not from Step 2 — the routing step is not optional here. A docs-only scope reached through this entry point must delegate exactly as Step 1 says; skipping to Steps 2-3 would dispatch the code-reviewer panel against pure prose. Once Step 1 has routed, the panel default applies as everywhere else — two reviewers, union, re-aggregate, never a single-reviewer dispatch. A refusal STOPS here, before any dispatch — see §Pinned refusal contract under §Process Step 1.
4. **After PASS**: the push WAS the request — execute it (branch-qualified form) and report loudly what was pushed. Do not re-ask. (Never a merge — step 0 routed merge-shaped triggers away.)
5. **After NEEDS_REVISION**: surface findings; do NOT push; let user remediate.
6. **After PASS_WITH_NOTES**: push, carrying every finding verbatim
   into the report (and the PR body if one follows) — consistent with
   `finishing-a-development-branch` Step 3's auto-proceed. Do NOT fix
   findings inline silently.

Any further question this flow surfaces runs the ask-vs-resolve
triage at `subagent-driven-development` §Asking the user, gate ①
(the cross-skill SSOT) before it reaches the user.

<!-- sync-marker push-rule:2 — full Push-as-trigger spec. The §When to use table row above is the 1-row summary; keep these two in sync. -->

This rule applies **even when this skill was not explicitly invoked** — the description (in this file's YAML frontmatter) encodes push commands and skip-rationalization phrases as trigger phrases, so the host harness's auto-discovery matches them via description-text classification. The push command's appearance in the prompt is the trigger; an explicit `Skill(loom-code:requesting-code-review)` call is not required for the skill to fire.

## Process

At the start of each review round (round 1 included), run `python3 scripts/plan_card.py <plan-path> --set-stage "review:round-N"` — the script prints the refreshed card; relay it — and commit the flip with that round's verdict or fixes; hand-edit only when the script is absent. When only the repo-root copy is missing, run the plugin-shipped copy instead — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" <plan-path> --set-stage "review:round-N"` (a load-time substitution, not a run-time shell variable) — "absent" means neither copy is present.

1. **Determine diff scope, then route by file type**. Resolve scope by running the resolver — `python3 loom-code/scripts/review_scope.py [--repo <path>]` — or, if the user specifies one, an explicit commit range (`git diff <SHA1>..<SHA2>`). Exit 0 prints the changed-file list, one path per line; a non-zero exit is a refusal, with the reason (and, on a stale base, a ready-to-run `git rebase --onto` remedy) on stderr.

   **§Pinned refusal contract** (transcribed verbatim): A stale base, or any failure to establish freshness, REFUSES. The resolver never returns a file list it cannot vouch for, and a station that receives a refusal STOPS before dispatching anything.

   A refusal STOPS this station here, before any dispatch: surface the reason (and remedy, if present) to the user per §Asking the user, and stop — never fall back to a scope computed from whatever is on disk. On a resolved (non-refused) scope, classify every `.md` file per §Classification: contract-class vs record-class, then dispatch four ways:
   - **Record-only branch** — the file list is non-empty AND every file in it is a record-class `.md` file (no contract-class `.md`, no non-`.md`) → run NO docs arm, NO code-reviewer panel; satisfy the push gate via the record-only continuity marker: `python3 <plugin-root>/scripts/loom_gate_markers.py mint --review-na-record-only` (resolve `<plugin-root>` as in Step 3); the script re-verifies the changed-file set is record-class, refusing loudly otherwise.
   - **Docs-only branch** — the file list is non-empty, every file in it ends in `.md`, AND at least one is contract-class → **delegate the review to [`requesting-docs-review`](../requesting-docs-review/SKILL.md)**: invoke that skill, handing it ONLY the contract-class subset as `resolved-scope`, plus an OPTIONAL `model` field set by M3 below, in the dispatch packet — record-class `.md` files are exempt, dropped from scope — and stop here — do not dispatch the code-reviewer panel below. It owns the docs semantics end-to-end (whole-artifact scope, the five prose dimensions, `class:` tagging, instruction-only aggregation, the citation pre-pass, its single-round-plus-delta-confirmation convergence contract (its own Directives, not restated here)) and mints the same review-pass gate marker.
   - **Mixed branch** — the list contains both `.md` and non-`.md` files → per-file split: the non-`.md` files go to the code-reviewer panel below (Steps 2-3, diff scoped to those files); the `.md` files go to the docs arm per `requesting-docs-review`'s panel contract, restricted to the contract-class subset (record-class exempt at any mix) — handing it that subset as `resolved-scope`, the non-`.md` file list as `read-context`, **and an OPTIONAL `model` field per M3** in its dispatch packet (its two-`docs-reviewer` dispatch + aggregation, run to produce a verdict — its own mint step does not fire here). No contract-class file → no docs arm dispatches; the code arm's Step 3 mint satisfies the push gate directly. **`read-context` is material the docs arm opens to verify claims against, never scope it reviews** — semantics and the recorded miss it closes are in `requesting-docs-review` Step 3, whose verdict also returns a separate unscored `read_context_findings:` block: surface it, never score it — it gates nothing. The orchestrator unions both arms' findings for the surfaced report, and the branch verdict is the WORSE of the two arm verdicts — either arm `NEEDS_REVISION` → branch `NEEDS_REVISION`. **Mint the review-pass marker once, from this joined verdict** — neither arm mints its own marker on a mixed branch: not the code arm's Step 3 mint (scoped to the code-only path below) and not `requesting-docs-review`'s own mint (scoped to the docs-only path above); the orchestrator itself runs Step 3's mint mechanics once, against the joined verdict text, after both arms return.
   - **Code-only branch** — no `.md` file in the list → the default code path below, unchanged.

   **§Pinned pass-down contract** (transcribed verbatim): The delegating station hands the delegate the resolved scope as `resolved-scope` in the dispatch packet. The delegate resolves scope itself ONLY when no `resolved-scope` was supplied.

   **M3 — mechanical upgrade rule (docs arm only).** A branch whose changed contract-class files include any `agents/*.md` sets the dispatch packet's OPTIONAL `model` field to `opus` — `requesting-docs-review`'s own dispatch step consumes it as a dispatch-time override. A branch changing 10 or more contract-class `.md` files sets the same field to `opus`. A contested 🔴 — the delta confirmation returned `STILL_BLOCKING` and the fix author maintains the finding is factually wrong — gets ONE second-opinion review of that finding, dispatched one tier above the arm's current tier; if the arm already ran at the top tier, the dispute goes to the user instead. Honesty note: catch-quality-by-tier is UNMEASURED — the upgrade rule is the hedge.
2. **Dispatch TWO `code-reviewer` subagents in parallel, with byte-identical prompts** (a panel; role identifier `loom-code:code-reviewer`; plugin-level agent at [`loom-code/agents/code-reviewer.md`](../../agents/code-reviewer.md)) to review the branch diff. Each dispatch is a one-shot, blocking call that waits for and returns its own verdict directly — see your host's tool-mapping reference under `using-loom-code/references/` (`claude-code-tools.md` / `codex-tools.md`) for the exact per-host call shape (Claude Code: issue both `Agent()` calls in **one** assistant message so they run concurrently), and [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §A1 for a Claude-Code-specific mistake to avoid (naming a dispatch call turns it into an async mailbox teammate whose output is never delivered — Codex has no equivalent pitfall). **Open each dispatch prompt with the role anchor from the agent's §Input contract — "You ARE the reviewer" — verbatim**; "review request" phrasing without it can role-confuse the dispatched agent into acting as an orchestrator ("I've dispatched the review" — to nobody). The orchestrator passes the **same** inputs to both: diff range, paths to rubrics + checklists, branch context (recent commits, related issues if known) — "byte-identical" means identical **to each other**; conditional additions (e.g. the PRINCIPLES.md path below) go to both, which preserves it. Both agents carry the 12-rule engineering baseline ([`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md)) baked into their system prompt. Do **not** pin a model on either dispatch — reviewers inherit the session model by design: that keeps the panel's tier matched to whatever the session actually runs.
   - **Principles-conformance discovery (conditional, self-derived):** each reviewer self-derives whether to score the `principles-conformance` dimension (D8 in the agent contract — does the diff violate any falsifiable `— check:` clause?) by checking the target repo for `docs/loom/PRINCIPLES.md` itself; the orchestrator does not need to pass anything for this dimension to fire. The orchestrator MAY pass a path to both reviewers as an **override**, used only when PRINCIPLES.md lives at a non-standard location — passing nothing changes nothing, since absence of an orchestrator-passed path never disables a dimension the reviewer's own self-derivation would otherwise turn on. When neither the standard path nor an override resolves, each reviewer emits `principles-conformance: N/A`. Never synthesize principles; the file is the only source.
3. **Wait for BOTH verdicts, union the findings, re-aggregate — then mint the gate marker** (on the code-only path, this mint fires directly here; on a mixed branch, this step computes only the code arm's own verdict — the single marker mint happens once against the joined verdict per Step 1's mixed bullet, not here). Each reviewer returns its own structured review with per-dimension scores, severity-tagged findings, and a verdict; wait for both before proceeding. **Union the two findings lists** — no cross-arm adjudication **layer** is needed; the mechanical merge rule: "the same finding" = same `file:line` AND same dimension → one line, keeping the more detailed wording and the **severer** severity when the arms disagree; same location but different dimensions stay distinct; a `file:line` cite vs a commit-SHA cite are treated as distinct (fail-closed — over-counting only pushes the verdict stricter). Then **re-run the §Aggregation rule on the union** — per-dimension score is re-aggregated from that dimension's union findings, not either arm's own — to produce the panel verdict; never pick one arm's own verdict. **Dead-arm rule**: if an arm errors out with no verdict, re-dispatch that arm once; if it dies again, proceed single-arm but say so in BOTH the verdict summary and the user relay (a single-arm verdict is degraded evidence — G4 measured why). Capacity-error recovery: [`dispatch-hygiene-notes.md`](../subagent-driven-development/references/dispatch-hygiene-notes.md) §Capacity-error recovery. Save the resulting panel verdict text (dimension scores + findings computed over the union) to a temp file and run `python3 <plugin-root>/scripts/loom_gate_markers.py review-pass --verdict-file <file>` (resolve `<plugin-root>` as `../..` from this skill's base dir). Marker-minting flow itself is unchanged. The script validates the §Verdict structure schema BEFORE writing `.git/loom/review-pass.json`; `NEEDS_REVISION` or a malformed verdict refuses to mint (exit 3/4) — a failed review can never produce a pass marker. Unsure whether a draft verdict text will pass? Run `loom_gate_markers.py validate --verdict-file <file>` first — it reports every schema violation in one pass (dry-run, no marker write). The marker binds the current HEAD sha (with a fail-closed patch-id fallback for message-only amends / content-preserving rebases — see [`references/gate-markers-spec.md`](references/gate-markers-spec.md)): any other later commit invalidates it, and the `hooks/git-guard.py` PreToolUse gate blocks `git push` / `gh pr create` until a fresh verdict re-mints at the new HEAD (review what you ship, not what you reviewed an amend ago).
4. **Harvest the deliberate-simplification ledger**. Before producing the review summary, grep the whole-branch diff for the `LOOM-SIMPLIFY:` markers that record deliberate, scope-bounded shortcuts the branch shipped, reusing the file list `review_scope.py` already resolved in Step 1 rather than recomputing it:

   ```
   grep -rn "LOOM-SIMPLIFY:" <files from Step 1's review_scope.py output>
   ```

   (Scope the grep to the files the branch changed — the same scope `review_scope.py` resolved in Step 1; this is the introducing-branch review gate, where each marker's `ceiling:` / `upgrade:` is freshest.) Present the hits as a **ledger view** in the verdict's `simplification_ledger` block (see §Verdict structure) so every corner-cut the branch ships is visible at the merge gate, not buried in a code comment. For each marker, confirm a checkable `ceiling:`, an `upgrade:` path, and a `ref:` are present (the standard requires all four fields); a marker missing any is itself a finding. When the grep returns nothing, the ledger is empty — say so explicitly ("no deliberate simplifications recorded on this branch"), don't omit the line. The marker convention + harvest rule are defined in [`../subagent-driven-development/standards/deliberate-simplification.md`](../subagent-driven-development/standards/deliberate-simplification.md) (§Harvest + Scope Boundary) — that standard is the SSOT; this step surfaces its grep-on-demand view at the review gate.
5. **Surface to user**. Print the verdict + findings + the simplification ledger; let user decide remediation. Do NOT auto-fix — that's user agency, even for a trivial single-line nit. Silently auto-fixing then re-reviewing removes the user's decision point and burns an extra review round. **Phrase this relay per §Asking the user** — translate `🔴/🟡/🟢` + the verdict token into plain language and open with a state anchor; the reviewer agent's structured output stays machine-precise. The ledger surfaces in plain language too: each shortcut as "what corner was cut, when it breaks, how to upgrade." Render the findings for the user per the [`adjudication-view`](../using-loom-code/protocols/adjudication-view.md) protocol (verdict mode) whenever that protocol's own §Firing conditions are met — the structured verdict block above stays machine-precise and untouched.
6. **Re-dispatch if user fixed and wants re-review** — same skill, fresh subagent (no state carry-over between rounds for clean evaluation).

Cross-skill delegation passes paths, not content — see [`references/cross-skill-map.md`](references/cross-skill-map.md) for the full directional map (upstream / downstream / lateral).

## Verdict structure

Returns:

```
standards_version: "{X.Y.Z — value of `version` in loom-code/.claude-plugin/plugin.json}"

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
    where: <file:line OR commit SHA range>     # REQUIRED — empty/missing flips verdict to NEEDS_REVISION
    source: <rubric / checklist / standard file:section that triggered this>
    note: <1-2 sentence finding>
    origin: none | <path> :: "<verbatim quote from that file>"  # REQUIRED on code-arm findings only (docs-arm exempt, per Step 1) — quote-gate rule owned by `code-reviewer.md` §Output contract — what you return `origin:` field; not restated here
    class: instruction | evidence              # docs-arm findings only (mixed branches, per Step 1) — semantics owned by requesting-docs-review; omitted for code-branch findings

simplification_ledger:                         # grep -rn "LOOM-SIMPLIFY:" over the branch diff (Step 4); [] when none
  - where: <file:line>
    shortcut: <what corner was cut>
    ceiling: <checkable condition under which it breaks>
    upgrade: <path to the proper version>
    ref: <originating brief/task>
    marker_valid: true | false                  # false when ceiling:, upgrade:, or ref: is missing (or ceiling: uncheckable) → also emit a finding

summary:
  - <≤5 bullet observations about the branch as a whole>
```

`simplification_ledger` is the gate-scoped harvest of `LOOM-SIMPLIFY:`
markers (§Process Step 4): the deliberate, scope-bounded shortcuts this
branch ships, surfaced so the merge gate sees each corner-cut and its
ceiling/upgrade. An empty list means none were recorded. A marker with
`marker_valid: false` (missing `ceiling:`, `upgrade:`, or `ref:`, or an
uncheckable `ceiling:`) is a
finding per [`../subagent-driven-development/standards/deliberate-simplification.md`](../subagent-driven-development/standards/deliberate-simplification.md) §Field Rules.

`standards_version` lets downstream readers tell whether a verdict was
scored under the rules in effect now or a prior revision — standards,
rubrics, and checklists ship together under one plugin version.

**Aggregation rule** (same as SDD's code-quality-reviewer with the added cross-task dimension; aligned with `rubrics/quality-gate.md` §Verdict Rules):

- Any 🔴 → `verdict: NEEDS_REVISION`
- Any finding with empty / missing `where` → `verdict: NEEDS_REVISION`
  regardless of severity (opaque finding = malformed verdict)
- **2 or more 🟡 warning findings, no 🔴** → `verdict: NEEDS_REVISION`
  (rubric §Verdict Rules — aggregated warnings signal systemic concern).
  **Self-check before writing the `verdict:` token**: count the 🟡 findings; if count ≥ 2 and no 🔴, the verdict is `NEEDS_REVISION`, not `PASS_WITH_NOTES`.
- Exactly 1 🟡 warning finding, no 🔴, all with `where` → `verdict: PASS_WITH_NOTES`
- No 🔴, no 🟡 (only 🟢 informational findings or no findings) → `verdict: PASS`

**Docs findings**: docs-only branches and the `.md` arm of mixed branches aggregate under [`requesting-docs-review`](../requesting-docs-review/SKILL.md) §Aggregation rule (instruction-class gating lives there, not here); the mixed-branch verdict join is Step 1's worse-of-the-two-arm-verdicts rule.

**Panel union**: each arm's own `verdict:` is advisory only — the gate verdict is produced by applying the aggregation rule above to the **union** of both arms' findings (§Process Step 3), never by picking one arm's verdict. Supporting evidence and the panel-width exit clause: [`references/design-evidence.md`](references/design-evidence.md) (author-facing; not loaded at runtime).

## Red Flags — refuse these rationalizations

Review-skip shortcuts to refuse — *"it's fine, just merge," "it's a small change, doesn't need review," "SDD already reviewed each task," "I'll re-review after CI runs," "user said skip review"* (and localized 「審查跳過 / レビューはスキップ」). Default posture: refuse the silent skip; dispatch the reviewer — a PASS costs 30 seconds, a NEEDS_REVISION saves a fix-before-prod. Full table (rationalization → reality → correct response) in [`references/red-flags.md`](references/red-flags.md).

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
- [`../subagent-driven-development/rubrics/quality-gate.md`](../subagent-driven-development/rubrics/quality-gate.md) — functional copy of code-team's quality rubric.
- [`../subagent-driven-development/rubrics/arch-gate.md`](../subagent-driven-development/rubrics/arch-gate.md) — functional copy of code-team's architecture rubric.
- [`../subagent-driven-development/checklists/security-checklist.md`](../subagent-driven-development/checklists/security-checklist.md) — functional copy of code-team's security checklist.
- [`../subagent-driven-development/standards/deliberate-simplification.md`](../subagent-driven-development/standards/deliberate-simplification.md) — the `LOOM-SIMPLIFY:` marker convention + grep-on-demand harvest rule this skill surfaces at the merge gate (§Process Step 4).
- [`references/gate-markers-spec.md`](references/gate-markers-spec.md) — verdict-text schema, the `verified --run` real-execution binding, waiver semantics, the patch-id relaxation (`base_sha`/`patch_id`), the `validate` dry-run subcommand, and the write-markers-then-push-separately ordering rule.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — sibling skill that fires alongside this one in finishing-a-branch flow.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator that invokes this skill.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 6 (Review).
- `domain-teams:code-team` — passive gate for large audits; this skill may escalate there for >500 LOC or security-sensitive reviews.
