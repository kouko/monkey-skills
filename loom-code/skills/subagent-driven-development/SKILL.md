---
name: subagent-driven-development
description: |
  Use when a task takes >1 hour OR touches >1 module — splits work into atomic one-failing-test units, three subagents each (implementer / spec-reviewer / code-quality-reviewer).
version: 0.12.0
---

## Continuous execution

### Live-gate receipt (SDD only)

Only when all five `LOOM_LIVE_GATE_PACKET`, `LOOM_LIVE_GATE_MARKER_DIR`,
`LOOM_LIVE_GATE_NONCE`, `LOOM_LIVE_GATE_PLUGIN_ROOT`, and
`LOOM_LIVE_GATE_REPO` are supplied: after consuming the handed packet, run
exactly once (no wrapper, redirection, prefix, or suffix):
`python3 "$LOOM_LIVE_GATE_PLUGIN_ROOT/scripts/live_gate_station_receipt.py" --packet "$LOOM_LIVE_GATE_PACKET" --plugin-root "$LOOM_LIVE_GATE_PLUGIN_ROOT" --marker-dir "$LOOM_LIVE_GATE_MARKER_DIR" --repo "$LOOM_LIVE_GATE_REPO" --station SDD --nonce "$LOOM_LIVE_GATE_NONCE"`
Otherwise do nothing. Never re-run `review_context.py` in a live-gate station;
the runner-owned packet is the sole packet source.

**Do not pause to check in between tasks.** When the orchestrator (this skill) receives a plan, it dispatches the first task's three subagents, waits for their verdicts, applies the resolution rule below, and immediately dispatches the next task. The user is not in the loop on a per-task basis — that is the loop SDD exists to remove.

Pause points the user **does** see:

- The plan itself, before any task is dispatched (user approves the task list).
- A `NEEDS_CONTEXT` from any implementer that survives the step-2 triage (orchestrator surfaces the question, waits for an answer; task-scoped checkable facts are resolved and re-dispatched without pausing).
- A `BLOCKED` from any implementer that the orchestrator cannot unblock by re-dispatch (e.g. missing dependency the user must install).
- After all tasks `DONE` (or `DONE_WITH_CONCERNS` triaged), an autonomous run with a human-approved frozen entry automatically invokes [`finishing-a-development-branch`](../finishing-a-development-branch/SKILL.md). It runs review + verification + push + PR-open in one pass; `一站一站來` keeps the final summary as the user-controlled pause point. Surface peer alternatives only when the user explicitly defers close-out.

Everything else — RED-GREEN-REFACTOR cycles, reviewer rounds, re-dispatch on `NEEDS_REVISION` — runs without user intervention.

**Subagent capacity errors (usage limit / "529 Overloaded") mid-run.** Do not silently retry in a loop — finish and commit any tasks already `DONE` in the current wave, then surface a recovery question per [§Asking the user](#asking-the-user). Full protocol (the three recovery options, and the retrospective-reviewer-dispatch step once capacity returns): [`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md) §Capacity-error recovery.

## Asking the user

When you surface one of those pause points — the final-summary pause under `一站一站來`, a `NEEDS_CONTEXT` question, a `BLOCKED`, or the 4th-retry escalation — run the decision through three gates: **① whether to ask at all**, **② what to bring when you do ask**, and **③ how to phrase it**. The reader is a warm-but-interrupted human, not the reviewer subagent. The anchor for all three gates is Horvitz, *Principles of Mixed-Initiative User Interfaces* (CHI 1999): scale the act-vs-ask threshold by the cost of being wrong, and scope each question's precision to your confidence.

### ① Whether to ask — tier by reversibility × cost

Asking has a cost. Every low-stakes confirmation teaches the user that confirmations are noise, and then the asks that actually matter lose their signal (confirmation fatigue). Tier by reversibility × cost, not by habit:

- **Reversible + inferable from context** (edits, running tests, saving a memory, advancing to the next task) → just do it, mention it after. Under a standing "一路做完 / just finish it" authorization, do **not** re-confirm these per step.
- **Irreversible / outward-facing / costly** (`git push`, `gh pr create`, `gh pr merge`, deploy, delete, a paid pipeline run) → always confirm. The standing authorization does **not** cover these (`using-loom-code` router rule #4). The confirm is asked ONCE: a kickoff request that already names the endpoint ("finish the branch", "ship it", "開 PR") IS that ask — stations then report loudly instead of re-asking. `gh pr merge`, deploy, delete, and paid runs always confirm regardless.
- **Genuine taste / scope / un-inferable intent** → run the **three-way triage** (the SSOT for this vocabulary): fact checkable within the task's own sources → look it up, never ask; user-fact, preference, or irreversible/outward-facing confirmation → ask directly, freely; researchable design fork → research first, then ask with a cited recommendation (research protocol: gate ②). A fact whose in-scope sources conflict, or whose reading is genuinely ambiguous in practice, is not "checkable" — treat it as a user-fact (a one-line clarification is legitimate). This three-way triage is the cross-skill SSOT for ask-vs-resolve decisions — sibling skills point here by heading text, never copy it.
- **Implementation-discovered engineering decision** (an implementer report surfaces it mid-task, not at kickoff): apply the two-axis test — product consequence × reversal cost — from `writing-plans/references/kickoff-briefing.md` (interface SSOT; pointer, not copy). A hit escalates in the SAME briefing format as the kickoff briefing — one interface, two firing points (design SSOT: `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md` §2 / :227). Below-threshold decisions are **not** asked — they are **logged** (see §Decision Log maintenance below).

### ② What to bring — a recommendation, not an open question

When you ask a technical decision (a bug-fix approach, a design choice, error handling), bring your judgment, not the raw problem. An open-ended "how should I fix this?" with no options makes the user think *for* you — that is forbidden. Research industry practice first (`using-loom-code` router rule #5 / `brainstorming`'s Axis-4 — point to them, do not re-implement the protocol here), then lead with a scoped `(Recommended)` option plus one line of why. The less familiar the domain, the **more** research you owe; unfamiliarity must not collapse into an open question.

**Complex fork → brief before you ask.** The trigger threshold and stakes-first framing live in the family SSOT: [`loom-code/hooks/family-reception.md`](../../hooks/family-reception.md) §Brief before a complex fork — applies verbatim when the orchestrator surfaces a technical decision in gate ②.

### ③ How to phrase

1. **Outcome, not mechanism.** Each option describes what the user *gets* ("you'll get the two skills edited and tests green"), not the internal machinery ("uses SDD triad dispatch").
2. **Translate jargon; expand acronyms on first use.** Replace or gloss internal terms (`implementer`, `spec-reviewer`, 🟡/🟢, `Wave 1 = T1+T3`). **Exception**: terms the user introduced *this session* are fine as-is.
3. **Numbers carry their meaning.** `PASS 12/12` → "all 5 tasks checked out"; let the mechanism detail (`12/12`) sink to a sub-line, not the headline.
4. **Open with a one-line state anchor + stakes** (一句話現況+利害): *we just did X; now Y needs deciding — and here is what changes by the choice.* The stakes half is what makes the ask evaluable, not just situated. Reuse recap-state's Block-1 "Situation" idea — never ask a bare decision verb with zero context (「下一步？」alone is the failure). Put the anchor **inside the `AskUserQuestion` `question` field**, not only in chat prose above the call — the user reads the rendered question, not your preamble. **Never use internal vocabulary in the anchor** — phrases like "T3+T4+T5 reviewer verdicts" or "whole-branch review passed" mean nothing to the user; translate them ("three automated checks passed" / "the full-branch quality review passed"). And never list a slash command or CLI subcommand as an option without first confirming it exists (e.g. `claude --help`).
5. **≤4 options** (AskUserQuestion hard cap). Never add an explicit "Other" — the tool auto-injects it. End **open** design questions with a free-form invite; for **closed** factual questions, don't.
6. **Compound asks only when sub-questions share one topic** or are jointly judgeable. Split unrelated decisions into separate rounds.
7. **Channel: default to the `AskUserQuestion` tool** for any non-trivial decision ask — that channel carries the ask-triage card and structured options. A prose-text ask is legitimate only when its first line is rule 4's state anchor + stakes line; a bare prose fork question（「A 還是 B？」with zero context）is the same violation as an unanchored tool ask, and it is invisible to the mechanical triage layer — which is why it defaults to the tool.

**Worked example — the built-in `/recap` style is the target.** Full ✅/❌ pair (the calibration target for every question and hand-off the orchestrator surfaces below): [`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md) §Worked example.

**Delivery form.** The ledger actions —
`python3 scripts/plan_card.py <plan-path> --set-status "T<N>=<status>"`
and `--set-stage "<text>"` — print the full progress card themselves
after the flip. Repo-root `scripts/plan_card.py` when it exists;
otherwise run the plugin-shipped copy:
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" …` (a load-time
substitution, not a run-time shell variable).
ANY turn that runs one of these actions MUST relay
that printed card in the live conversation language, framed per
`loom-code/hooks/family-relay.md §Family relay discipline` —
progress-card variant `§(a2) Progress card` (family-relay absent, or
both script copies absent → render the four fields inline: goal, task
table, stage,
next — nothing is dropped); when both copies are absent, the same
relay duty binds directly at per-wave status reports, stage
transitions, and checkpoint sign-offs, with the inline four fields.
Per-wave status reports, stage transitions, and checkpoint sign-offs
flip the ledger via the script, so the card rides them by
construction. The card re-reads the plan file by construction — never
compose it from memory. **Never copy the card template body here;
point at it.** Internal machine traffic (verdict tokens, wave labels)
stays precise below the card.

**Host todo mirror.** When the host provides built-in task tools
(TaskCreate/TaskUpdate), mirror the plan's tasks into the todo list
when SDD starts consuming the plan, and update each mirrored task's
status in the same turn as its ledger flip. This is a one-way display
projection — the plan file's Status ledger stays the SSOT; the todo
list is never read back. Hosts without task tools → skip silently.

## When to use

Auto-routed by [`using-loom-code`](../using-loom-code/SKILL.md) when **either** trigger fires:

- The user's task is estimated to take **>1 hour**.
- The task touches **>1 module / >1 file boundary**.

Flowchart of this trigger + the per-task loop below: [`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md) §SDD flow diagram.

If neither trigger fires, the user goes straight to `tdd-iron-law` for implementation. SDD's overhead is not free; do not dispatch three subagents for a one-line change.

## Process — per-task triad

Dispatch every subagent call below as a one-shot, blocking call that waits for and returns its result directly — see your host's tool-mapping reference under `using-loom-code/references/` (`claude-code-tools.md` / `codex-tools.md`) for the exact call shape, and [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §A1 for a Claude-Code-specific naming pitfall to avoid (Codex has no equivalent).

Packet context — anchoring, provenance, locate arms, reviewer independence: [`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md) §Dispatch-packet context.

For each atomic task in the plan:

1. **Dispatch an `implementer` subagent** (role identifier `loom-code:implementer`; input contract defined in the plugin-level agent at [`loom-code/agents/implementer.md`](../../agents/implementer.md), which also carries the 12-rule engineering baseline from [`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md)) with the task description + context paths + resource paths. Carry the plan task's existing `Files touched` declaration unchanged into the task packet for the later reviewer fan-out. Before dispatching, the orchestrator resolves the project's test command once via `verification-before-completion`'s declared-first rule (consult the declared surface; trust only if it runs and emits a test count; else fall back to detection), caches it **session-scoped** (re-resolve across sessions because declarations rot), and passes it into the implementer dispatch as a **`Resolved test command`** line so the implementer runs the project's real test command instead of re-detecting. Relevant `Kickoff decision:` lines from the plan's `## Notes` ride the implementer's task packet. Wait for return.
2. **Read the implementer's output.** If `status: NEEDS_CONTEXT` → do not dispatch reviewers; triage the relayed question FIRST per gate ①: a task-scoped checkable fact → resolve it yourself and re-dispatch the implementer (no user ask); a researchable design fork → research per gate ②, then surface with the cited recommendation; otherwise surface directly, phrased per [§Asking the user](#asking-the-user). A surfaced question with product stakes also applies gate ①'s two-axis framing to decide the escalation format. **NEEDS_CONTEXT re-dispatch cap:** task-scoped-fact re-dispatches on the same task are capped at 2 rounds; if the re-dispatched implementer returns NEEDS_CONTEXT a 3rd time on that task, the spec/plan is missing information, not a resolvable fact — stop re-dispatching and surface to the user per §Asking the user, mirroring the 3-round NEEDS_REVISION escalation below (a separate, independent counter — the two budgets never share rounds). If `status: BLOCKED` → apply the unblock step or surface to user.
3. **If `status: DONE` or `DONE_WITH_CONCERNS`**, resolve the installed root through the active host adapter; run `python3 "<installed-plugin-root>/scripts/review_context.py" --repo <target_repo>` **once per reviewer fan-out**. Treat its output as one unchanged immutable context packet: `target_repo`, `reviewed_sha`, `plugin_version`, and `resources`. `resources` maps approved absolute paths; never derive plugin paths from `target_repo`, the working directory, or a consumer checkout. Copy it verbatim into dispatches; retries use a fresh fan-out packet. Write the packet JSON to a file; run `python3 "<installed-plugin-root>/scripts/review_context.py" --validate <packet-file>`; any non-zero exit REFUSES the fan-out: dispatch no reviewer — fix the packet first. In a live-gate station SKIP this `--validate` invocation: `live_gate_station_receipt.py` already validated the runner-owned packet (same key-set + SHA checks); the live-gate section's "Never re-run `review_context.py`" rule governs. Require a non-empty repository-relative `Files touched` list; otherwise REFUSE the fan-out: do not dispatch any reviewer. The only reviewer artifact scope is the repository-relative file list declared in the task packet's `Files touched` field; do not derive a base or recompute a diff. For every declared `<path>`, run `git -C "<target_repo>" cat-file -e "<reviewed_sha>:<path>"` before dispatching. Any failure REFUSES the fan-out: do not dispatch any reviewer. Do not run `review_scope.py` for a per-task fan-out; whole-branch review only. Give every spec-reviewer, code-quality-reviewer, and docs-reviewer prompt the SHA-bound task scope, the same packet, and the immutable repository citation cross-read contract: `git -C "<target_repo>" show <reviewed_sha>:<path>`. Read evidence from paths at `<reviewed_sha>`, never a later mutable HEAD. Do not use mutable working-tree reads for reviewer evidence. Dispatch **`spec-reviewer`** and **`code-quality-reviewer`** **in parallel**, `loom-code:spec-reviewer` and `loom-code:code-quality-reviewer`. Wait for both. Worktree isolation: [`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md).
4. **Resolve verdicts** per the rule below.
5. **Move to the next task** unless the resolution requires re-dispatch.

**Parallel dispatch for independent tasks.** Tasks marked `Independent: true` with disjoint file sets → dispatch all their implementers in ONE fan-out step (see `dispatching-parallel-agents` §3 for the host-specific shape). When the wave completes, commit each task's `PASS` artifacts immediately — do not hold a passing task's commit while a `NEEDS_REVISION` sibling in the same wave is re-dispatched. Keeping commits atomic makes the diff bisectable.

**Mechanical review-weight exemption.** When a task's plan entry declares `Review-weight: mechanical` and the implementer returns `DONE`, the orchestrator SKIPS the step-3 `spec-reviewer` + `code-quality-reviewer` dispatch entirely and instead runs a deterministic **self-check** with three concrete parts, all required:

1. **Content match.** The task's `Description` names an exact-spec target, in one of two shapes:
   - **Literal target** — a literal string (grep it: it must be PRESENT in each file listed in `Files touched`; for a "replace X with Y" description, the grep target is Y, the post-edit state) or a literal diff block (per Check 16's "literal string/diff" co-condition — apply the same match, verbatim, via `git diff` against the stated before/after rather than a plain grep).
   - **Deterministic sync-script target** (see `plan-format.md`'s matching worked example) — the Description names a script + its SSOT instead of a literal string. **Before trusting a re-run, first confirm the script itself is untampered**: `git status --porcelain <script-path>` must be clean AND the script must not appear in the task's own `Files touched` — a script that is itself uncommitted, newly added, or edited by this task cannot be re-run as a trust anchor, since that makes the "zero diff" check tautological (the output would trivially match a script the implementer just modified). If the script isn't clean-and-untouched, this shape's Content match FAILS outright — fall back to the full triad, do not attempt the sub-checks below. Once the script is confirmed untampered: re-run it yourself and confirm the committed `Files touched` content has **zero diff** against the fresh run's output, OR — if the script ships a paired drift-detection test (as `sync-primitives.sh` / `sync_codex_manifests.py` do) — run that test and require exit 0. Either sub-check satisfies Content match for this shape; a mismatch or nonzero exit falls back to the full triad exactly like a failed literal-target match.
2. **Scope match.** `git diff --name-only` for the task's commit MUST be a subset of the task's declared `Files touched` — no additional file, and no line outside what the exact-spec target names, may appear in the diff.
3. **Suite green.** Run the resolved package test command after the task's commit; any failure fails the self-check — a mechanical edit can redden a file no task touches (live case: a version bump vs the shipping-version pin test).

All three parts passing resolves the task as `DONE` with no reviewer verdict (this exemption bypasses the §Verdict resolution table below entirely — no spec-reviewer/code-quality-reviewer verdicts exist on this path). Any part failing (content absent, extra files touched, a red suite, or any ambiguity in applying any check) falls back to the full triad — fail-closed toward review, never toward silently skipping on ambiguity. This exemption is gated upstream by `plan-document-reviewer` Check 16 (see `writing-plans/references/plan-document-reviewer-prompt.md`): a plan setting the field without satisfying Check 16 never reaches SDD, so the orchestrator trusts the marker's presence without re-validating it here.

**Prose review-weight substitution.** When a task's plan entry declares `Review-weight: prose`, the orchestrator keeps the step-1 `implementer` dispatch and the step-3 `spec-reviewer` dispatch exactly as in the full triad — spec conformance is artifact-type-agnostic — but **replaces the code-quality-reviewer arm with the docs-reviewer agent** (role identifier `loom-code:docs-reviewer`, see [`loom-code/agents/docs-reviewer.md`](../../agents/docs-reviewer.md)), dispatched in parallel with spec-reviewer in the same step-3 fan-out. The docs-reviewer receives the same immutable packet resolved for that fan-out, copied verbatim; its changed-artifact list and diff scope are the ones at `<reviewed_sha>`. Only the code-quality-reviewer arm is substituted; the spec-reviewer arm stays and is never replaced.

Eligibility is narrow: this substitution applies only when **all** files listed in the task's `Files touched` are `.md` authored prose — never code, never config, never a generated/sync artifact. Fail-closed, mirroring the mechanical exemption's fail-closed rule above: if any file in `Files touched`, or any file that actually appears in the task's diff, is not `.md` authored prose, the substitution does not apply and the orchestrator falls back to running the **full triad** (spec-reviewer + code-quality-reviewer) — never silently drop or narrow a reviewer arm on ambiguity.

This substitution is gated upstream by `plan-document-reviewer` Check 16 (see `writing-plans/references/plan-document-reviewer-prompt.md`), the same trust model as the mechanical exemption above: a plan setting `Review-weight: prose` without satisfying Check 16's eligibility test never reaches SDD, so the orchestrator trusts the marker's presence without re-validating Check 16's plan-time judgment; the runtime fail-closed check above still applies.

Unlike the mechanical exemption, this substitution does **not** bypass the §Verdict resolution table below — the table still applies on this path, with the docs-reviewer's verdict substituting into the table's `code-quality-reviewer` column (the `spec-reviewer` column is unchanged).

**Record-class scope narrowing.** Classify the task's `Files touched` per `requesting-code-review`'s [§Classification: contract-class vs record-class](../requesting-code-review/SKILL.md) — cite the SSOT there, never re-derive its globs here. When every file is record-class, the docs-reviewer substitution is N/A: dispatch spec-reviewer only, and record "code-quality slot: N/A — record-class prose" in the task summary. Contract-class prose keeps the substitution unchanged. A mixed contract-class + record-class task routes the docs-reviewer to the contract-class subset only — consistent with `requesting-code-review`'s own mixed-branch routing. On this path the task resolves on spec-reviewer's verdict alone — its `PASS` → `DONE`, its `NEEDS_REVISION` → the table's re-dispatch row; the `code-quality-reviewer` column is N/A by construction.

**Progress ledger.** SDD writes the plan's per-task `Status` field back as it executes and resumes from it after interruption: [`references/plan-ledger-notes.md`](references/plan-ledger-notes.md) §Progress ledger. Perform every ledger flip via `python3 scripts/plan_card.py <plan-path> --set-status "T<N>=<status>"` when `scripts/plan_card.py` exists at the repo root — it validates the task, the status grammar, and refuses duplicate or missing `Status` lines; hand-edit only when the script is absent. When only the repo-root copy is missing, run the plugin-shipped copy instead — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" <plan-path> --set-status "T<N>=<status>"` — "absent" means neither copy is present.

**Decision Log maintenance.** SDD appends non-briefed, classified engineering decisions to the plan's `## Decision Log` during execution: [`references/plan-ledger-notes.md`](references/plan-ledger-notes.md) §Decision Log maintenance.

**Read-before-Edit is non-negotiable for the orchestrator.** When the orchestrator applies post-review fixes, renames files, or edits files located via **any Bash inspection** — `grep` / `jq` / `sed` / `cat` / `head` / etc.: call `Read` on each target file before `Edit`. The precondition is tool-level — only the `Read` tool satisfies it, never shell stdout. grep/jq/sed/cat output and subagent-created files do NOT satisfy the Edit read-precondition. Skipping this produces cascading "File has not been read yet" errors across every subsequent edit. For the full set of harness gotchas, see [environment-gotchas](../using-loom-code/references/environment-gotchas.md).

**Environment hygiene.** Standing hygiene rules for commands the orchestrator (or its subagents) run directly: [`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md) §Environment hygiene.

**Version / semver work in implementer tasks.** Before importing a package for version parsing or manifest handling, the implementer must confirm it is stdlib (e.g. `importlib.metadata`, plain `tuple(int(x) for x in v.split('.'))`) rather than third-party (e.g. `packaging`). Third-party imports in new code fail the code-quality-reviewer's external-surface-grounding check and return `NEEDS_REVISION`.

### Verdict resolution

| spec-reviewer | code-quality-reviewer | Resolution |
|---|---|---|
| `PASS` | `PASS` | Task DONE. Next task. |
| `PASS` | `PASS_WITH_NOTES` | Task DONE. 🟡 / 🟢 findings surfaced in final summary as debt; do not block. |
| `PASS` | `NEEDS_REVISION` | Re-dispatch implementer with `findings`. Up to **3 rounds** then escalate to user. |
| `NEEDS_REVISION` | (any quality verdict) | Re-dispatch implementer with `gaps` + (if any) `findings`. Same 3-round cap. |
| `MALFORMED_PACKET` (from either reviewer) | (any) | The dispatch packet is defective: fix it and re-dispatch THAT reviewer with a fresh fan-out packet, NOT the implementer; the round is uncounted against the 3-round cap. |

A `MALFORMED_PACKET` from either reviewer overrides every quality-verdict row.

When the 2nd round's `NEEDS_REVISION` repeats the SAME unresolved question, read [`references/research-escalation.md`](references/research-escalation.md) and run its triage FIRST — before the 3rd re-dispatch — so research evidence rides that round. A reviewer finding carrying `evidence_needed:` → run this same triage IMMEDIATELY, before any re-dispatch — do not wait for the 2nd round.

A 3-round cap prevents infinite loops on ambiguous specs. On the 4th retry, surface to the user — likely the spec is wrong, not the implementer. Phrase that escalation per [§Asking the user](#asking-the-user): lead with a state anchor and say what's actually stuck in plain words, not `NEEDS_REVISION ×3`. (Continuous mode deliberately halts one round earlier than this cap — no human is pumping the loop, so the slack is handed back sooner; see [`references/continuous-mode.md`](../using-loom-code/references/continuous-mode.md) in `using-loom-code`.)

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"This is basically mechanical, I'll skip review even though the plan didn't mark it."* | The `Review-weight: mechanical` marker is `plan-document-reviewer`-validated (Check 16), never an on-the-fly implementer/orchestrator judgment call. | Refuse. Run the full triad unless the plan itself declares `Review-weight: mechanical`. |
| 「這基本上是機械式的,計畫沒標我也自己跳過審查吧 / これは機械的だからレビューを省略しよう」 | Same rationalization, localized. | Same refusal — the marker must come from the plan, not an improvised call. |

## Definition of Done — command-surface accretion

A task that adds a **new runnable capability** must have that verb **declared in the command surface and verified to run** before `DONE` — accretion, binding capability-add to surface-declare exactly as TDD binds behaviour to test: [`references/command-surface-accretion.md`](references/command-surface-accretion.md).

## Model selection

**Resolve the dispatch profile** in [`using-loom-code`'s portable profile](../using-loom-code/references/dispatch-profile.md) before every implementer or reviewer spawn. It owns the semantic tiers, effort boundary, reviewer exception, host adapters, and bounded fallback; this station does not restate host model names or invent a lower-tier fallback. In particular, the code-quality reviewer remains `frontier` when it evaluates a `frontier` architecture task.

A second, unrelated tier floor applies to `plan-document-reviewer`'s Check 17 (c2) — see [`writing-plans/references/plan-document-reviewer-prompt.md`](../writing-plans/references/plan-document-reviewer-prompt.md), Check 17 row, which is the SSOT for that floor's value.

## Status handling — implementer states

```
DONE                 → dispatch reviewers
DONE_WITH_CONCERNS   → dispatch reviewers; surface concerns to user in final summary
NEEDS_CONTEXT        → surface specific question to user; do NOT dispatch reviewers
BLOCKED              → apply unblock_step if orchestrator can; else surface to user
```

The orchestrator never silently dismisses a `BLOCKED` — even if the unblock step is trivial, log what was done so the final summary names it. A `NEEDS_CONTEXT` question with product stakes goes through the same two-axis framing (§Asking the user ①) before it reaches the user.

Before surfacing a `BLOCKED` that hinges on a semantics or convention dispute (not a missing dependency, not broken test infra) → read [`references/research-escalation.md`](references/research-escalation.md) and run its triage FIRST, same as the 2nd-round trigger above.

Whatever the user sees at this seam — a wave sign-off, a `DONE_WITH_CONCERNS` summary — is the progress card per the **Delivery form** paragraph above (family-relay `§(a2) Progress card`), in the live conversation language; this table's states are internal routing, not user-facing copy.

## Prompt templates

Three role-defined plugin-level subagents (v0.6.0 / P15-12 complete); all carry the 12-rule engineering baseline ([`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md)) baked into their system prompts. Dispatch each one as a one-shot blocking call — see your host's tool-mapping reference for the exact shape, and [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §A1 for the Claude-Code-specific naming pitfall (Codex has no equivalent).

- **implementer** — worker; produces code + tests + status. [`loom-code/agents/implementer.md`](../../agents/implementer.md). Role identifier `loom-code:implementer`. Shipped v0.5.2 / P15-12 Phase 1.
- **spec-reviewer** — evaluator; produces `PASS` / `NEEDS_REVISION` + gap list. [`loom-code/agents/spec-reviewer.md`](../../agents/spec-reviewer.md). Role identifier `loom-code:spec-reviewer`. Promoted v0.6.0 / P15-12 Phase 2.
- **code-quality-reviewer** — evaluator; produces three-valued verdict + eight-dimension scores + findings. [`loom-code/agents/code-quality-reviewer.md`](../../agents/code-quality-reviewer.md). Role identifier `loom-code:code-quality-reviewer`. Promoted v0.6.0 / P15-12 Phase 2.

Reviewer prompts intentionally constrain scope: spec-reviewer **cannot** evaluate code quality; code-quality-reviewer **cannot** evaluate spec coverage. Mixing the two collapses the signal at the orchestrator level.

## Cross-skill contract

- **[`tdd-iron-law`](../tdd-iron-law/SKILL.md)** — implementer prompts must load this skill before writing code. The reviewer's `tests` dimension scores against `standards/tdd-standard.md` (functional copy of code-team SSOT).
- **`writing-plans`** — produces the task list SDD consumes.
- **`finishing-a-development-branch`** — runs after the last task is DONE; delegates to `loom-workflow:git-memory` for commit-message memory.
- **`domain-teams:code-team`** — passive gate; not invoked by SDD directly. The knowledge layer here is a functional copy of code-team's standards / rubrics / checklists, kept byte-identical by `scripts/distribute.py` + `scripts/verify-drift.py`.

## Knowledge layer

`standards/`, `rubrics/`, `checklists/` under this skill are byte-identical functional copies (plus a 5-line SSOT header) of the canonical `code-team` knowledge layer (which lives in the sibling `domain-teams` plugin). To edit a rule:

1. Land the edit in the canonical `code-team` source.
2. In the same commit, run `python3 loom-code/scripts/distribute.py`.
3. CI's `verify-drift.py` enforces byte-identity.

See [`../../scripts/canonical/README.md`](../../scripts/canonical/README.md) for the full pointer table (canonical paths + functional-copy destinations).

## What this skill does NOT do

- Does **not** write code itself. It dispatches implementer subagents.
- Does **not** produce gate verdicts itself. Reviewer subagents do.
- Does **not** decide whether SDD applies. `using-loom-code` routes; this skill assumes the trigger fired.
- Does **not** edit the spec. If the implementer returns `NEEDS_CONTEXT` pointing at a spec gap, the orchestrator surfaces to the user; the user (or `writing-plans`) updates the spec.
- Does **not** produce the plan. `writing-plans` does — SDD consumes the plan.

## See also

- [`loom-code/agents/implementer.md`](../../agents/implementer.md) — plugin-level implementer (v0.5.2+).
- [`loom-code/agents/spec-reviewer.md`](../../agents/spec-reviewer.md) — plugin-level spec-reviewer (v0.6.0+).
- [`loom-code/agents/code-quality-reviewer.md`](../../agents/code-quality-reviewer.md) — plugin-level code-quality-reviewer (v0.6.0+).
- [`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md) — SSOT for the 12-rule engineering baseline embedded in every plugin-level agent.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md)
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md)
- [`../../TECH-SPEC.md`](../../TECH-SPEC.md) §3.3–3.4 — interface contracts.
