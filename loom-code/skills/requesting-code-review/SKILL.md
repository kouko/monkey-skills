---
name: requesting-code-review
description: |
  Use BEFORE any push/merge/PR on a non-trivial branch — whole-branch review of the cumulative diff. Fires on 'review my branch', 'ready to merge?', and excuses it refuses: 'just push', 'skip review', git push / gh pr create with no prior review-PASS.
version: 0.12.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer / plan-document-reviewer), the parent orchestrator already invoked this skill. **Do not** re-route through it; follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Dispatches **two `code-reviewer` subagents in parallel (a panel)** to review a non-trivial diff as a whole — typically the cumulative changes on a feature branch before merge. Both reviewers load the same rubrics SDD's per-task reviewer uses (`quality-gate.md` / `arch-gate.md` / `security-checklist.md`, functional-copied from `domain-teams:code-team`), but apply them at branch scope rather than per-atomic-task.

## Asking the user

When you relay the reviewer's verdict back to the user — Step 4 below ("Surface to user / Print the verdict + findings"), or the push-as-trigger steps 4-6 in §Push-as-trigger — three gates apply: **whether** to interrupt the user at all, **what** to bring when you do, and **how** to phrase it. The reader is a warm-but-interrupted human, not the `code-reviewer` subagent.

### ① Whether to ask — tier by reversibility × cost

Every question spends the user's attention; asking on autopilot is confirmation fatigue. Before surfacing a decision, tier it:

- **Reversible and inferable from context** → just do it, mention it after. Under a standing "just finish it" authorization, do not re-confirm each step.
- **Irreversible, outward-facing, or costly** → always confirm first. The push-as-trigger actions (`git push` / `gh pr create` / `gh pr merge`) are exactly this case: they publish to teammates / CI / production, so they are never auto-run — confirm before each one.
- **Genuine taste, scope, or un-inferable** → ask, per gate ②.

### ② What to bring — a recommendation, not an open question

This skill mostly relays a verdict and asks the user to choose: fix the findings now, defer them, or merge anyway. Whichever you ask, **lead with a scoped `(Recommended)` option and one line of why** — never hand the user an open-ended punt they have to fill in themselves. Research industry practice first for design/strategy calls ([`using-loom-code`](../using-loom-code/SKILL.md) router rule #5 / `brainstorming`'s Axis-4 — point to them, do not re-implement the protocol here). *(Grounded: Horvitz, Principles of Mixed-Initiative User Interfaces, CHI 1999.)*

**Complex remediation fork → brief before you ask.** A finding can open a genuine design fork (e.g. an architectural 🔴 with two viable remediations). When that fork is complex (≥3 trade-offs, ≥2 implementation paths, or architectural blast radius), do not compress it into a fix/defer/merge ask — run `dev-workflow:brief-before-asking` (6-block briefing, Mental Model first) before the `AskUserQuestion`. Same trigger as `brainstorming`'s rule — `brainstorming` carries the canonical trigger rule; `dev-workflow:brief-before-asking` owns the 6-block format.

### ③ How to phrase

Six rules:

1. **Outcome, not mechanism.** Each finding says what it *means for the user* and what they should do ("this branch ships a circular dependency — fix before merge"), not just the rule name it tripped ("violates arch-gate D3").
2. **Translate jargon; expand acronyms on first use.** Replace or gloss internal terms (`implementer`, `spec-reviewer`, 🟡/🟢, `Wave 1 = T1+T3`). **Exception**: terms the user introduced *this session* are fine as-is.
3. **Numbers and symbols carry their meaning.** Translate `🔴/🟡/🟢`, `PASS_WITH_NOTES`, and the Beck / Martin / OWASP / 徳丸本 citations into one plain sentence ("nothing blocking, two things worth a look before merge") — don't dump the raw verdict block at the user.
4. **Open with a one-line state anchor** (一句話現況): *I reviewed the whole branch; here's what I found.* Never lead with a bare verdict token (`NEEDS_REVISION` alone is the failure) — give the reader the situation before the symbol. When you follow up with an `AskUserQuestion`, put the anchor **inside its `question` field**, not only in chat prose above the call — the user reads the rendered question, not your preamble. Always populate the `questions` array with fully-drafted question text; an empty `{}` payload causes InputValidationError at dispatch time.
5. **≤4 options** (AskUserQuestion hard cap). Never add an explicit "Other" — the tool auto-injects it. End **open** design questions with a free-form invite; for **closed** factual questions, don't.
6. **Compound asks only when sub-questions share one topic** or are jointly judgeable. Split unrelated decisions into separate rounds.

**Boundary — these rules govern the relay TO the user ONLY.** They do **not** touch what the `code-reviewer` agent emits. The agent's structured verdict (the `verdict:` / `dimension_scores:` / `findings:` block in §Verdict structure) MUST stay machine-precise and keep every evidence citation — do NOT loosen its R2 evidence-citation contract ([`loom-code/agents/code-reviewer.md`](../../agents/code-reviewer.md) §Rule R2: every finding needs a `where:` citing `file:line` / commit SHA, or the verdict flips to `NEEDS_REVISION`). Plain language is for the human-facing relay; the reviewer agent's output stays exact.

**Worked example — the built-in `/recap` style is the target:**

```
✅ Standard (outcome-framed, no jargon, plain status, term-explained-on-use):
   "I reviewed the whole branch — nothing blocks the merge, but two things are worth a look
    first: a query that could be slow on large tables, and a missing test for the empty-input
    case. Want me to fix them now, or merge and follow up?"

❌ Avoid (jargon-dense status-report style):
   "Verdict: PASS_WITH_NOTES. 🔴 0 / 🟡 2 / 🟢 8. perf D2 (Fowler), tests D5 (Beck). See findings[]. Ready to merge?"
```

This ✅ example is the calibration target for every verdict-relay and hand-off this skill surfaces.

## When this is different from SDD's per-task reviewer

| Dimension | SDD `code-quality-reviewer` (per task) | `requesting-code-review` (whole branch) |
|---|---|---|
| Scope | One atomic task's output | Cumulative branch diff (all tasks combined) |
| When fires | During each SDD task triad | After all SDD work is DONE; before merge |
| Sees | One commit / one module | The full branch diff vs main |
| Catches | Per-task quality lapses | Cross-task interactions, scope creep, architectural coherence |
| Verdict aggregation | Per-task | Per-branch |

Both use the same rubrics. The difference is **scope of the diff being reviewed**, which catches different categories of issue: per-task review catches "this commit has bad naming"; whole-branch review catches "tasks 1-4 each made sense individually but together they introduced a circular dependency."

## When to use

| Trigger | Route here |
|---|---|
| User says *"review my branch"* / *"look at my changes"* / *"is this ready to merge"* | ✅ Yes |
| User says *"code review this PR"* / *"audit the diff"* | ✅ Yes |
| SDD just finished a multi-task plan; user about to ship | ✅ Yes (proactive recommendation) |
| User about to invoke `finishing-a-development-branch` | ✅ Yes (finishing-a-branch invokes this skill internally as Step 1) |
| **User mentions `requesting-code-review` by name (even framed as skip-intent)** | **✅ Yes — name-mention is a fire-trigger; the skip-intent framing is the rationalization this skill exists to refuse, NOT permission to bypass it** |
| <!-- sync-marker push-rule:1 — see §Push-as-trigger below for the full spec --> **Push-as-trigger** — user runs / asks to run `git push`, `gh pr create`, `gh pr merge`, branch merge, or similar publish-to-remote action without prior review-PASS in this session | **✅ Yes — block the push; fire this skill first; re-evaluate push after verdict.** See §Push-as-trigger below. |
| User wants per-task review during implementation | ❌ No — that's SDD's job |
| User wants existing-artifact compliance audit (legacy code, not a branch diff) | ❌ Route to `domain-teams:code-team` (passive gate entry, different use case) |
| Diff is trivial (one-line typo, version bump, doc change) | ❌ Skip — review overhead > value |

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Trivial diffs** | One-line fixes, doc-only changes, version bumps, generated code regen | "I changed 3 lines" — if those 3 lines touch behavior, review applies |
| **Already-reviewed branch** | A prior `requesting-code-review` invocation in this session already PASSed and nothing changed since | "I made a tiny tweak after review" — re-review (the tweak might be the bug) |
| **Audit vs review** | You want a compliance audit on existing shipped code | Route to `domain-teams:code-team` (passive gate); this skill is for branch-pre-merge review |
| **Explicit user override** | User says literally "skip review, just merge" AND the work matches one of the above categories | "It's fine, just merge" — that's the rationalization this skill exists for; refuse |

## Push-as-trigger

**Any push-to-remote action without prior review-PASS in this session = this skill fires before the push runs.** Push-to-remote actions include:

- `git push` (any form: explicit args, default upstream, `-u origin <branch>`, `--force`)
- `gh pr create` (creates a remote PR; same blast-radius as push)
- `gh pr merge` / `gh pr merge --auto` (merges to base branch)
- Any agent-side helper that invokes the above

**Why**: pushing publishes code to teammates / CI / production-deploy paths. The review-before-publish gate exists so reviewers see clean diffs, not "we'll catch it in CI." A push without review is the failure mode this skill exists to prevent.

**The agent's wrong-default rationalizations to refuse**:

| Surface signal | Wrong default | Correct response |
|---|---|---|
| User's message ends with *"just push"* / *"let me push"* | Interpret as authorization to push | **Refuse**: that's a rationalization in the test taxonomy this skill refutes. Fire review first; surface verdict; let user explicitly re-authorize push AFTER reviewing the verdict. |
| User says *"SDD already reviewed each task, push"* | Skip whole-branch review because per-task PASSed | **Refuse**: per-task ≠ whole-branch (different scopes; cross-task-coherence dimension is branch-only). Fire review. |
| Agent in autonomous flow infers "this branch is done, let me push" | Treat "done" as push-authorization | **Refuse**: "done" is the trigger for finishing-a-development-branch flow, NOT for direct push. Route to finishing-a-branch (which fires this skill as Step 1). |
| User has previously authorized pushes in this session for other branches | Generalize the authorization | **Refuse**: each push is its own authorization moment. Previous authorization does not carry to new pushes. |
| Auto-mode classifier passes the `git push` invocation | Treat classifier-pass as full authorization | **Refuse**: classifier-pass means "the action itself is permitted at the harness level"; it does NOT mean "the toolkit's review-before-publish gate has been satisfied." Both must hold. |

**Procedure when push-as-trigger fires**:

1. **Do NOT execute the push.** Halt the planned action.
2. **Surface the rationalization** to the user explicitly — quote which row of the table above their request matches.
3. **Offer to run review now**: "Dispatching `requesting-code-review` — back in ~30s." Then run the §Process panel (Steps 2-3: two reviewers, union, re-aggregate) on `git diff main...HEAD` (or explicit range) — this entry point uses the same panel default, never a single-reviewer dispatch.
4. **After PASS**: ask user to explicitly re-authorize the push. "Review PASSed; want me to push now? (y/N)" Wait for user.
5. **After NEEDS_REVISION**: surface findings; do NOT push; let user remediate.
6. **After PASS_WITH_NOTES**: surface findings; ask user whether to push anyway (acceptable for non-🔴 findings) OR remediate first. Do NOT fix findings inline before asking — present them and wait for an explicit user choice (push anyway / fix now / defer).

<!-- sync-marker push-rule:2 — full Push-as-trigger spec. The §When to use table row above is the 1-row summary; keep these two in sync. -->

This rule applies **even when this skill was not explicitly invoked** — the description (in this file's YAML frontmatter) encodes push commands and skip-rationalization phrases as trigger phrases, so the host harness's auto-discovery matches them via description-text classification. The push command's appearance in the prompt is the trigger; an explicit `Skill(loom-code:requesting-code-review)` call is not required for the skill to fire.

## Process

1. **Determine diff scope**. Default: `git diff main...HEAD` (everything on this branch not on main). Override with explicit commit range if user specifies (`git diff <SHA1>..<SHA2>`).
2. **Dispatch TWO `code-reviewer` subagents in parallel, with byte-identical prompts** (a panel; role identifier `loom-code:code-reviewer`; plugin-level agent, v0.6.0 / P15-12 Phase 2, at [`loom-code/agents/code-reviewer.md`](../../agents/code-reviewer.md)) to review the branch diff. Each dispatch is a one-shot, blocking call that waits for and returns its own verdict directly — see your host's tool-mapping reference under `using-loom-code/references/` (`claude-code-tools.md` / `codex-tools.md`) for the exact per-host call shape (Claude Code: issue both `Agent()` calls in **one** assistant message so they run concurrently), and [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §A1 for a Claude-Code-specific mistake to avoid (naming a dispatch call turns it into an async mailbox teammate whose output is never delivered — Codex has no equivalent pitfall). **Open each dispatch prompt with the role anchor from the agent's §Input contract — "You ARE the reviewer" — verbatim**; "review request" phrasing without it can role-confuse the dispatched agent into acting as an orchestrator ("I've dispatched the review" — to nobody). The orchestrator passes the **same** inputs to both: diff range, paths to rubrics + checklists, branch context (recent commits, related issues if known) — "byte-identical" means identical **to each other**; conditional additions (e.g. the PRINCIPLES.md path below) go to both, which preserves it. Both agents carry the 12-rule engineering baseline ([`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md)) baked into their system prompt. Do **not** pin a model on either dispatch — reviewers inherit the session model by design. The 2×Sonnet panel is exactly the configuration G4 measured; the report's own honesty clause cautions against extrapolating across tiers or diff types, and inheriting (rather than pinning) is what keeps the panel's tier matched to whatever the session actually runs (see §Aggregation rule's "Panel union" note).
   - **Principles-conformance discovery (conditional):** before dispatching, check whether the consumer project has a `docs/loom/PRINCIPLES.md`. **If present**, pass its path to both reviewers and instruct each to score the `principles-conformance` dimension (D8 in the agent contract — does the diff violate any falsifiable `— check:` clause?). **If absent**, pass nothing — each reviewer emits `principles-conformance: N/A`. Never synthesize principles; the file is the only source.
3. **Wait for BOTH verdicts, union the findings, re-aggregate — then mint the gate marker**. Each reviewer returns its own structured review with per-dimension scores, severity-tagged findings, and a verdict; wait for both before proceeding. **Union the two findings lists** — no cross-arm adjudication LAYER is needed (zero false positives measured across G4's 4 arms, report §Scorecard, plus the two same-day panel deployments recorded in PR #503/#504); the mechanical merge rule: "the same finding" = same `file:line` AND same dimension → one line, keeping the more detailed wording and the **severer** severity when the arms disagree; same location but different dimensions stay distinct; a `file:line` cite vs a commit-SHA cite are treated as distinct (fail-closed — over-counting only pushes the verdict stricter). Then **re-run the §Aggregation rule on the union** (per-dimension score = the worse of the two arms' scores) to produce the single panel verdict — never just pick one arm's own verdict. **Dead-arm rule**: if an arm errors out with no verdict, re-dispatch that arm once; if it dies again, proceed single-arm but say so in BOTH the verdict summary and the user relay (a single-arm verdict is degraded evidence — G4 measured why). Save the resulting panel verdict text (dimension scores + findings computed over the union) to a temp file and run `python3 <plugin-root>/scripts/loom_gate_markers.py review-pass --verdict-file <file>` (resolve `<plugin-root>` as `../..` from this skill's base dir). Marker-minting flow itself is unchanged. The script validates the §Verdict structure schema BEFORE writing `.git/loom/review-pass.json`; `NEEDS_REVISION` or a malformed verdict refuses to mint (exit 3/4) — a failed review can never produce a pass marker. Unsure whether a draft verdict text will pass? Run `loom_gate_markers.py validate --verdict-file <file>` first — it reports every schema violation in one pass (dry-run, no marker write). The marker binds the current HEAD sha (with a fail-closed patch-id fallback for message-only amends / content-preserving rebases — see [`references/gate-markers-spec.md`](references/gate-markers-spec.md)): any other later commit invalidates it, and the `hooks/git-guard.py` PreToolUse gate blocks `git push` / `gh pr create` until a fresh verdict re-mints at the new HEAD (review what you ship, not what you reviewed an amend ago).
4. **Harvest the deliberate-simplification ledger**. Before producing the review summary, grep the whole-branch diff for the `LOOM-SIMPLIFY:` markers that record deliberate, scope-bounded shortcuts the branch shipped:

   ```
   grep -rn "LOOM-SIMPLIFY:" $(git diff --name-only main...HEAD)
   ```

   (Scope the grep to the files the branch changed — same diff range as Step 1; this is the introducing-branch review gate, where each marker's `ceiling:` / `upgrade:` is freshest.) Present the hits as a **ledger view** in the verdict's `simplification_ledger` block (see §Verdict structure) so every corner-cut the branch ships is visible at the merge gate, not buried in a code comment. For each marker, confirm a checkable `ceiling:`, an `upgrade:` path, and a `ref:` are present (the standard requires all four fields); a marker missing any is itself a finding. When the grep returns nothing, the ledger is empty — say so explicitly ("no deliberate simplifications recorded on this branch"), don't omit the line. The marker convention + harvest rule are defined in [`../subagent-driven-development/standards/deliberate-simplification.md`](../subagent-driven-development/standards/deliberate-simplification.md) (§Harvest + Scope Boundary) — that standard is the SSOT; this step surfaces its grep-on-demand view at the review gate.
5. **Surface to user**. Print the verdict + findings + the simplification ledger; let user decide remediation. Do NOT auto-fix — that's user agency, even for a trivial single-line nit. Silently auto-fixing then re-reviewing removes the user's decision point and burns an extra review round. **Phrase this relay per §Asking the user** — translate `🔴/🟡/🟢` + the verdict token into plain language and open with a state anchor; the reviewer agent's structured output stays machine-precise. The ledger surfaces in plain language too: each shortcut as "what corner was cut, when it breaks, how to upgrade."
6. **Re-dispatch if user fixed and wants re-review** — same skill, fresh subagent (no state carry-over between rounds for clean evaluation).

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream invocation** | `finishing-a-development-branch` | Calls this skill as Step 1 of the close-branch flow |
| **Downstream (after PASS)** | `finishing-a-development-branch` proceeds to verification-before-completion + commit + push | |
| **Downstream (after NEEDS_REVISION)** | User remediates → re-dispatch this skill, OR invoke `subagent-driven-development` to dispatch implementer fixes if scoped enough | |
| **Lateral (optional)** | `domain-teams:code-team` | For LARGE audit work (>500 LOC changed, security-sensitive surface, or production-incident-driven review). The skill itself is sized for branch-pre-merge; major audits should escalate. |
| **Lateral (rubrics SSOT)** | Rubrics / checklists loaded from `../subagent-driven-development/{rubrics,checklists}/` (functional copies of `code-team`) | Same SSOT as SDD's per-task reviewer — no drift between per-task and whole-branch review |

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

findings:
  - severity: 🔴 fatal | 🟡 should-fix | 🟢 nit
    dimension: <which of the 7 above>
    where: <file:line OR commit SHA range>     # REQUIRED — empty/missing flips verdict to NEEDS_REVISION
    source: <rubric / checklist / standard file:section that triggered this>
    note: <1-2 sentence finding>

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

**Panel union**: each arm's own `verdict:` is advisory only — the gate verdict is produced by applying the aggregation rule above to the **union** of both arms' findings (§Process Step 3), never by picking one arm's verdict. Evidence: G4 A/B — a single-Sonnet verdict missed the correct call 1-of-2 times, while union-aggregation over both arms reproduced the correct verdict with zero false positives across all 4 tested arms (`docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md`).

**Exit clause**: if false positives start accumulating, or the two arms are persistently byte-redundant (no incremental recall from the second arm), re-evaluate panel width against the G4 baseline.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"It's fine, just merge."* | Pre-merge rationalization. Branch hasn't been reviewed; skipping review = shipping without verdict. | Refuse silent skip; dispatch reviewer. If reviewer returns PASS in 30 seconds, the user lost 30 seconds; if it returns NEEDS_REVISION, the user gained a fix-before-prod. |
| *"It's a small change, doesn't need review."* | "Small" is the rationalization. 3 behavioral lines can introduce a regression. | Apply §When NOT to Use carefully: ONLY trivial diffs (one-line typo / doc-only / version bump / generated regen) skip review. "Small behavioral" does NOT qualify. |
| *"SDD already reviewed each task."* | True for per-task scope; not for cross-task interactions. Tasks 1-4 individually fine, combined introduce a circular dep — that's the gap this skill closes. | Run anyway; the cross-task-coherence dimension is the unique value. |
| *"I'll re-review after CI runs."* | CI is automated tests; this skill is human-judgment quality review. They're complementary, not substitutable. | Run this skill BEFORE pushing; let CI catch the orthogonal issues. |
| *"User said skip review."* | Valid only with explicit override AND §When NOT to Use exemption match. | Quote §When NOT to Use back; ask for explicit re-confirmation. |
| 「審查跳過 / レビューはスキップ」 | Same rationalization, localized. | Same refusal. |

## What this skill does NOT do

- Does **not** modify code. Reviewer is evaluator-only; remediation is user / implementer.
- Does **not** replace `subagent-driven-development`'s per-task reviewer. Both layers serve different scopes.
- Does **not** replace `verification-before-completion`. This skill is human-judgment review; verification-before-completion is test-suite-run gate. Both fire before `finishing-a-development-branch` commits.
- Does **not** auto-trigger CI. Pushing to remote triggers CI; this skill runs before push.

## See also

- [`loom-code/agents/code-reviewer.md`](../../agents/code-reviewer.md) — the dispatched plugin-level subagent's role contract + input/output contracts (v0.6.0+ / P15-12 Phase 2).
- [`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md) — SSOT for the 12-rule engineering baseline carried by the code-reviewer agent.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — per-task reviewer (different scope, same rubrics).
- [`../subagent-driven-development/rubrics/quality-gate.md`](../subagent-driven-development/rubrics/quality-gate.md) — functional copy of code-team's quality rubric.
- [`../subagent-driven-development/rubrics/arch-gate.md`](../subagent-driven-development/rubrics/arch-gate.md) — functional copy of code-team's architecture rubric.
- [`../subagent-driven-development/checklists/security-checklist.md`](../subagent-driven-development/checklists/security-checklist.md) — functional copy of code-team's security checklist.
- [`../subagent-driven-development/standards/deliberate-simplification.md`](../subagent-driven-development/standards/deliberate-simplification.md) — the `LOOM-SIMPLIFY:` marker convention + grep-on-demand harvest rule this skill surfaces at the merge gate (§Process Step 4).
- [`references/gate-markers-spec.md`](references/gate-markers-spec.md) — verdict-text schema, suite-line grammar, waiver semantics, the patch-id relaxation (`base_sha`/`patch_id`), the `validate` dry-run subcommand, and the write-markers-then-push-separately ordering rule.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — sibling skill that fires alongside this one in finishing-a-branch flow.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — orchestrator that invokes this skill.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 6 (Review).
- `domain-teams:code-team` — passive gate for large audits; this skill may escalate there for >500 LOC or security-sensitive reviews.
