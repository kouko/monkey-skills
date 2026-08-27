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

**Do not pause between tasks.** After approval, dispatch each triad, await
verdicts, apply resolution below, and continue. SDD removes the per-task user
loop.

Pause points the user **does** see:

- Plan approval, before any task dispatch.
- A `NEEDS_CONTEXT` from any implementer that survives the step-2 triage (orchestrator surfaces the question, waits for an answer; task-scoped checkable facts are resolved and re-dispatched without pausing).
- A `BLOCKED` from any implementer that the orchestrator cannot unblock by re-dispatch (e.g. missing dependency the user must install).
- After all tasks `DONE` (or `DONE_WITH_CONCERNS` triaged), an autonomous run with a human-approved frozen entry automatically invokes [`finishing-a-development-branch`](../finishing-a-development-branch/SKILL.md). It runs review + verification + push + PR-open in one pass; `一站一站來` keeps the final summary as the user-controlled pause point. Surface peer alternatives only when the user explicitly defers close-out.

Everything else — RED-GREEN-REFACTOR cycles, reviewer rounds, re-dispatch on `NEEDS_REVISION` — runs without user intervention.

Capacity errors are a user-visible pause: finish already-`DONE` work, then read
[`references/conditional-operations.md`](references/conditional-operations.md)
§Capacity-error recovery.

## Asking the user

At a pause point, decide **① whether to ask**, **② what evidence and
recommendation to bring**, and **③ how to phrase it**. Scale act-versus-ask by
the cost of being wrong (Horvitz, CHI 1999).

### ① Whether to ask — tier by reversibility × cost

- **Reversible + inferable from context** (edits, running tests, saving a memory, advancing to the next task) → just do it, mention it after. Under a standing "一路做完 / just finish it" authorization, do **not** re-confirm these per step.
- **Irreversible / outward-facing / costly** (`git push`, `gh pr create`, `gh pr merge`, deploy, delete, a paid pipeline run) → always confirm. The standing authorization does **not** cover these (`using-loom-code` router rule #4). The confirm is asked ONCE: a kickoff request that already names the endpoint ("finish the branch", "ship it", "開 PR") IS that ask — stations then report loudly instead of re-asking. `gh pr merge`, deploy, delete, and paid runs always confirm regardless.
- **Genuine taste / scope / un-inferable intent** → task-source fact: resolve it; user fact or preference: ask; researchable design fork: research, then ask with a cited recommendation. Conflicting or ambiguous sources make the fact unresolvable and legitimate to ask. This three-way triage is the cross-skill SSOT for ask-vs-resolve decisions — sibling skills point here by heading text, never copy it.
- **Implementation-discovered engineering decision** (an implementer report surfaces it mid-task, not at kickoff): apply the two-axis test — product consequence × reversal cost — from `writing-plans/references/kickoff-briefing.md` (interface SSOT; pointer, not copy). A hit escalates in the SAME briefing format as the kickoff briefing — one interface, two firing points (design SSOT: `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md` §2 / :227). Below-threshold decisions are **not** asked — they are **logged** (see §Decision Log maintenance below).

### ② What to bring — a recommendation, not an open question

Bring a scoped `(Recommended)` option and why, not a raw technical problem.
Research unfamiliar or researchable forks first under the router's research rule.

**Complex fork → brief before you ask.** The trigger threshold and stakes-first framing live in the family SSOT: [`loom-code/hooks/family-reception.md`](../../hooks/family-reception.md) §Brief before a complex fork — applies verbatim when the orchestrator surfaces a technical decision in gate ②.

### ③ How to phrase

Open with current state and stakes, describe outcomes in plain language, and
use the host's structured question tool for non-trivial choices. Read
[`references/conditional-operations.md`](references/conditional-operations.md)
§User-question delivery when a question or progress card must be rendered.
Each option says what the user gets, not which agent mechanism runs. Translate
internal verdict and wave labels, expand unfamiliar acronyms, and explain a
number's meaning before its machine token. Keep the state-and-stakes anchor in
the rendered question, not only the surrounding prose. Offer at most four
options and let the tool provide “Other”. Split unrelated decisions; combine
only jointly judgeable questions. A prose fallback must carry the same anchor
in its first line.
The reader is a warm-but-interrupted human, so never expose a bare internal
decision verb such as “next?” or ask them to invent the engineering options.
For an open design question, end with a free-form invitation; for a closed
fact, keep the response closed. Confirm that any slash command or CLI option
offered actually exists before presenting it. These presentation rules change
how an approved question is delivered, never the gate that decides whether the
question is warranted.

**Worked example — the built-in `/recap` style is the target.** Full calibration:
[`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md)
§Worked example.

**Delivery form.** The ledger actions —
`python3 scripts/plan_card.py <plan-path> --set-status "T<N>=<status>"`
and `--set-stage "<text>"` — print the full progress card after the flip. Use
the repo-root script when present, otherwise
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" …`. ANY turn
that runs one of these actions MUST relay that printed card in the live
conversation language, framed per `family-relay.md §Family relay discipline`,
progress-card variant `§(a2) Progress card` (family-relay absent, or both script
copies absent → render the four fields inline: goal, task table, stage, next).
when both copies are absent, the same relay duty binds directly at per-wave
status reports, stage transitions, and checkpoint sign-offs, with the inline
four fields. Per-wave status reports, stage transitions, and checkpoint
sign-offs flip the ledger via the script, so the card rides them by
construction. The card re-reads the plan file by construction — never compose
it from memory. Never copy the template here.

**Host todo mirror.** When the host provides task tools, mirror plan tasks and
update them with each ledger flip. This is display-only: the plan file's Status
ledger stays the SSOT and is never read back from the mirror. Hosts without
task tools → skip silently.

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

1. **Dispatch an `implementer` subagent** (role identifier `loom-code:implementer`; input contract defined in the plugin-level agent at [`loom-code/agents/implementer.md`](../../agents/implementer.md), which also carries the 12-rule engineering baseline from [`loom-code/scripts/_baseline.md`](../../scripts/_baseline.md)) with the task description + context paths + resource paths. Carry the plan task's existing `Files touched` declaration unchanged into the task packet for the later reviewer fan-out. Carry the adjacent `Seam` bullets verbatim (`plan-format.md` `#### Seam`) — its incoming bullets plus any bullet naming it `owner:` — with the owner's parser/schema path for payload-bearing seams; never the whole plan. Before dispatching, the orchestrator resolves the project's test command once via `verification-before-completion`'s declared-first rule (trust the declared surface only if it runs and emits a test count; else detect), caches it **session-scoped** (re-resolve across sessions — declarations rot), and passes it into the implementer dispatch as a **`Resolved test command`** line so the implementer runs it instead of re-detecting. Relevant `Kickoff decision:` lines from the plan's `## Notes` ride the implementer's task packet. Wait for return.
2. **Read the implementer's output.** If `status: NEEDS_CONTEXT` → do not dispatch reviewers; triage the relayed question FIRST per gate ①: a task-scoped checkable fact → resolve it yourself and re-dispatch the implementer (no user ask); a researchable design fork → research per gate ②, then surface with the cited recommendation; otherwise surface directly, phrased per [§Asking the user](#asking-the-user). A surfaced question with product stakes also applies gate ①'s two-axis framing to decide the escalation format. **NEEDS_CONTEXT re-dispatch cap:** task-scoped-fact re-dispatches on the same task are capped at 2 rounds; if the re-dispatched implementer returns NEEDS_CONTEXT a 3rd time on that task, the spec/plan is missing information, not a resolvable fact — stop re-dispatching and surface to the user per §Asking the user, mirroring the 3-round NEEDS_REVISION escalation below (a separate, independent counter — the two budgets never share rounds). If `status: BLOCKED` → apply the unblock step or surface to user.
3. **If `status: DONE` or `DONE_WITH_CONCERNS`**, resolve the installed root through the active host adapter; run `python3 "<installed-plugin-root>/scripts/review_context.py" --repo <target_repo>` **once per reviewer fan-out**. Treat its output as one unchanged immutable context packet: `target_repo`, `reviewed_sha`, `plugin_version`, and `resources`. `resources` maps approved absolute paths; never derive plugin paths from `target_repo`, the working directory, or a consumer checkout. Copy it verbatim into dispatches; retries use a fresh fan-out packet. Write the packet JSON to a file; run `python3 "<installed-plugin-root>/scripts/review_context.py" --validate <packet-file>`; any non-zero exit REFUSES the fan-out: dispatch no reviewer — fix the packet first. In a live-gate station, SKIP `--validate`: `live_gate_station_receipt.py` already validated the runner-owned packet (same key-set + SHA checks) per that section's "Never re-run `review_context.py`" rule. Require a non-empty repository-relative `Files touched` list; otherwise REFUSE the fan-out. The only reviewer artifact scope is the repository-relative file list declared in the task packet's `Files touched` field; do not derive a base or recompute a diff. For every declared `<path>`, run `git -C "<target_repo>" cat-file -e "<reviewed_sha>:<path>"` before dispatching. Any failure REFUSES the fan-out: do not dispatch any reviewer. Do not run `review_scope.py` for a per-task fan-out; whole-branch review only. Give every spec-reviewer, code-quality-reviewer, and docs-reviewer prompt the SHA-bound task scope, the same packet, and the immutable repository citation cross-read contract: `git -C "<target_repo>" show <reviewed_sha>:<path>`. Read evidence from paths at `<reviewed_sha>`, never a later mutable HEAD. Do not use mutable working-tree reads for reviewer evidence. Dispatch **`spec-reviewer`** and **`code-quality-reviewer`** **in parallel**, `loom-code:spec-reviewer` and `loom-code:code-quality-reviewer`. Wait for both. Worktree isolation: [`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md).
4. **Resolve verdicts** per the rule below.
5. **Move to the next task** unless the resolution requires re-dispatch.

**Parallel dispatch for independent tasks.** Tasks marked `Independent: true` with disjoint file sets → dispatch all their implementers in ONE fan-out step (see `dispatching-parallel-agents` §3 for the host-specific shape). When the wave completes, commit each task's `PASS` artifacts immediately — do not hold a passing task's commit while a `NEEDS_REVISION` sibling in the same wave is re-dispatched. Keeping commits atomic makes the diff bisectable.

**Mechanical review-weight exemption.** When a task's plan entry declares `Review-weight: mechanical` and the implementer returns `DONE`, the orchestrator SKIPS the step-3 `spec-reviewer` + `code-quality-reviewer` dispatch entirely and instead runs a deterministic **self-check** with three concrete parts, all required:

The checks are content match, commit-scope match, and the resolved package suite
green:

1. **Content match.** Confirm the exact literal/diff or an untampered
   deterministic sync result as detailed in the trigger-point reference below.
2. **Scope match.** `git diff --name-only` for the task commit must be a subset
   of its declared `Files touched`.
3. **Suite green.** Run the resolved package test command after the task's commit; any failure fails the self-check — a mechanical edit can redden a file no task touches (live case: a version bump vs the shipping-version pin test).

All three passing resolve `DONE` without reviewer verdicts; any failure
or ambiguity falls back to the full triad. Read
[`references/conditional-operations.md`](references/conditional-operations.md)
§Mechanical self-check when this declared lane fires. Its plan-time gate is
`plan-document-reviewer` Check 16.

**Prose review-weight substitution.** A declared `Review-weight: prose` keeps
implementer and spec-reviewer but replaces code-quality-reviewer with
`loom-code:docs-reviewer`, in parallel and with the same immutable packet. It
uses the §Verdict resolution table; the docs-reviewer's verdict substitutes
into the code-quality-reviewer column and the spec-reviewer column is unchanged.
The docs-reviewer receives the same immutable packet; its changed-artifact list and diff scope are the ones at `<reviewed_sha>`. Eligibility requires all
declared `Files touched` and actual changed files to be `.md` authored prose;
code, config, generated artifacts, or ambiguity fail closed to the full triad.
This mirrors the mechanical exemption's fail-closed rule. Unlike that
exemption, the §Verdict resolution table still applies on this path.
Read
[`references/conditional-operations.md`](references/conditional-operations.md)
§Prose and record-class routing when this lane fires, including authored-prose
eligibility and record-class narrowing. Its plan-time gate is Check 16.
The upstream validator is `plan-document-reviewer`; this uses the same trust
model as the mechanical lane and does not re-validate its plan marker. Runtime
ambiguity still fails closed rather than silently narrowing review.

**Record-class scope narrowing.** Classify the task's `Files touched` per `requesting-code-review`'s [§Classification: contract-class vs record-class](../requesting-code-review/SKILL.md) — cite the SSOT there, never re-derive its globs here. When every file is record-class, the docs-reviewer substitution is N/A: dispatch spec-reviewer only, and record "code-quality slot: N/A — record-class prose" in the task summary. Contract-class prose keeps the substitution unchanged. A mixed contract-class + record-class task routes the docs-reviewer to the contract-class subset only — consistent with `requesting-code-review`'s own mixed-branch routing. On this path the task resolves on spec-reviewer's verdict alone — its `PASS` → `DONE`, its `NEEDS_REVISION` → the table's re-dispatch row; the `code-quality-reviewer` column is N/A by construction.

**Progress ledger.** SDD writes the plan's per-task `Status` field back as it executes and resumes from it after interruption: [`references/plan-ledger-notes.md`](references/plan-ledger-notes.md) §Progress ledger. Perform every ledger flip via `python3 scripts/plan_card.py <plan-path> --set-status "T<N>=<status>"` when `scripts/plan_card.py` exists at the repo root — it validates the task, the status grammar, and refuses duplicate or missing `Status` lines; hand-edit only when the script is absent. When only the repo-root copy is missing, run the plugin-shipped copy instead — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" <plan-path> --set-status "T<N>=<status>"` — "absent" means neither copy is present.

**Decision Log maintenance.** SDD appends non-briefed, classified engineering decisions to the plan's `## Decision Log` during execution: [`references/plan-ledger-notes.md`](references/plan-ledger-notes.md) §Decision Log maintenance.

**Version / semver work in implementer tasks.** Before importing a package for
version parsing or manifest handling, the implementer must confirm it is stdlib
(`importlib.metadata`, or a plain `tuple(int(x) for x in v.split('.'))`) rather
than third-party (e.g. `packaging`). A third-party import reaching production
code with no grounding cite fails the code-quality-reviewer's
external-surface-grounding check and returns `NEEDS_REVISION`.

**Environment hygiene.** Standing rules remain at
[`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md)
§Environment hygiene. For post-review edits, command hygiene, or version metadata, read
[`references/conditional-operations.md`](references/conditional-operations.md)
§Orchestrator command hygiene at the trigger point.

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

Before surfacing a `BLOCKED` that hinges on a semantics or convention dispute,
read [`references/research-escalation.md`](references/research-escalation.md)
and run its triage FIRST. Missing dependencies and broken test infrastructure
bypass it.

Whatever the user sees at this seam — a wave sign-off, a `DONE_WITH_CONCERNS` summary — is the progress card per the **Delivery form** paragraph above (family-relay `§(a2) Progress card`), in the live conversation language; this table's states are internal routing, not user-facing copy.

## Prompt templates

Load only the role prompt being dispatched from
[`references/conditional-operations.md`](references/conditional-operations.md)
§Role prompt catalog. Roles remain separate: spec-reviewer checks coverage;
quality reviewers check artifact quality.

## Cross-skill contract

- **[`tdd-iron-law`](../tdd-iron-law/SKILL.md)** — implementer prompts must load this skill before writing code. The reviewer's `tests` dimension scores against `standards/tdd-standard.md` (functional copy of code-team SSOT).
- **`writing-plans`** — produces the task list SDD consumes.
- **`finishing-a-development-branch`** — runs after the last task is DONE; delegates to `loom-workflow:git-memory` for commit-message memory.
- **`domain-teams:code-team`** — passive gate; not invoked by SDD directly. The knowledge layer here is a functional copy of code-team's standards / rubrics / checklists, kept byte-identical by `scripts/distribute.py` + `scripts/verify-drift.py`.

## Knowledge layer

The local review knowledge is generated from code-team. Before changing it,
read [`references/conditional-operations.md`](references/conditional-operations.md)
§Role prompt catalog for the canonical edit-and-sync path.

## What this skill does NOT do

- Does **not** write code itself. It dispatches implementer subagents.
- Does **not** produce gate verdicts itself. Reviewer subagents do.
- Does **not** decide whether SDD applies. `using-loom-code` routes; this skill assumes the trigger fired.
- Does **not** edit the spec. If the implementer returns `NEEDS_CONTEXT` pointing at a spec gap, the orchestrator surfaces to the user; the user (or `writing-plans`) updates the spec.
- Does **not** produce the plan. `writing-plans` does — SDD consumes the plan.

## See also

[`tdd-iron-law`](../tdd-iron-law/SKILL.md) governs implementers;
[`using-loom-code`](../using-loom-code/SKILL.md) routes into SDD; role and
knowledge paths are in `references/conditional-operations.md`.
