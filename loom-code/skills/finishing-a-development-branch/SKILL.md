---
name: finishing-a-development-branch
description: |
  Use when ready to close out a development branch — about to merge or open a PR. Fires on 'finish this branch', 'wrap up', 'ready to merge', 'open a PR', 'ship it'. Orchestrates review → verification → git-memory commit → git push. No auto-merge.
version: 0.10.1
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (code-reviewer / plan-document-reviewer / implementer), the parent orchestrator already invoked this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What this skill does

Orchestrates the close-branch sequence. The agent acts as conductor — invoking each step's specialist skill in order, gating progress on each step's verdict, and surfacing the final state to the user. Before executing, Read the CURRENT SKILL.md from the installed plugin — never run the flow from memory or a compacted summary. **The user retains agency for the final merge decision** (push + PR is automated; actual merge into main is not).

```
finishing-a-development-branch (this skill)
  │
  ├─→ Phase 1: requesting-code-review
  │     three-way dispatch by file type (docs-only → whole review delegates to
  │     requesting-docs-review; mixed → per-file split, code panel + docs-reviewer;
  │     code-only → code-reviewer panel, unchanged) → verdict: PASS / PASS_WITH_NOTES / NEEDS_REVISION
  │     blocks on NEEDS_REVISION (any 🔴, or 2+ 🟡); PASS_WITH_NOTES (1 🟡) auto-proceeds,
  │     carrying the 🟡 forward into the PR body + close-out report
  │
  ├─→ Phase 2: verification-before-completion
  │     runs package-level test command → exit 0 + N>0 tests → PASS
  │     blocks on test failure
  │     + ui-verification (CONDITIONAL): branch touched UI AND a
  │       ui-flows.md exists → this is the user's main acceptance stage
  │       (design SSOT: docs/loom/design/2026-07-10-designer-pm-loop-architecture.md §1 #4)
  │       (what "done" means for a UI-bearing branch) — drives the
  │       rendered app through its enumerated states; otherwise N/A
  │       (honest skip, stated)
  │
  ├─→ Phase 3: dev-workflow:git-memory (P3-D MANDATORY)
  │     decides on Decision: / Learning: / Gotcha: trailers for the close-out commit
  │     orchestrator hands the diff + recent commits; git-memory returns trailer set
  │
  ├─→ Phase 4: git commit (orchestrator runs this)
  │     uses the message + trailers from Phase 3
  │     does NOT bypass hooks; does NOT amend
  │     then verifies the carrier landed: memory-grep.sh --verify HEAD
  │     (memory-worthy + exit 4 → STOP before push; both-carrier policy)
  │
  ├─→ Phase 5: git push (orchestrator runs this)
  │     pushes the branch; if branch is local-only, sets upstream first
  │
  ├─→ Phase 6 (optional): gh pr create
  │     only if user has gh CLI configured AND has not opted out
  │     PR body uses git-memory's PR-body convention
  │
  └─→ Phase 7 (optional): git worktree cleanup
        if branch was in .worktrees/, offer (do NOT auto-execute) the worktree remove
        per using-git-worktrees §Removing a worktree

(The diagram above is the **phase overview** — which sub-skill fires in what order.
The numbered **Step** list in §Default flow below is the granular procedure; "Phase N"
and "Step N" are distinct numbering schemes.)
```

## When NOT to use

Exempt: **mid-task work** (SDD plan not yet complete), **trivial direct-to-main commits** (solo, no review, tiny doc fix), a **branch you're abandoning** (not merging — just delete, but close out first if the work was real), and **explicit user override** with a real reason (cherry-pick / known-trivial). Each has a near-miss rationalization that does NOT qualify ("I'm tired of this branch," "I trust myself"). These exemptions waive the close-out orchestration (review / verification / PR) but **NEVER waive `dev-workflow:git-memory`** — it gates every commit, even a trivial direct-to-main one. Full table in [`references/when-not-to-use.md`](references/when-not-to-use.md).

## When to use

| Trigger phrase | Route here |
|---|---|
| *"finish this branch"* / *"wrap up the feature"* / *"ready to merge"* | ✅ Yes |
| *"open a PR for this branch"* / *"ship it"* / *"close out this branch"* | ✅ Yes |
| *"I'm done here, what's next?"* | ✅ Yes — the one endpoint-unnamed trigger: confirm the close-out intent at entry ("closing out = review → verify → commit → push → PR — proceeding?"), then never re-ask downstream. |
| SDD's task plan just completed all tasks DONE | ✅ Yes (proactive — SDD's hand-off recommendation names the close-out endpoint; accepting it carries the authorization) |
| User wants per-task review during implementation | ❌ No — that's SDD's per-task triad |
| User wants whole-branch review WITHOUT merging | ❌ Route directly to `requesting-code-review` (no close-out flow needed) |

## Cross-skill contract — heavy delegation

This skill is intentionally light on novel logic. Its value is orchestration; the work happens in delegated specialists:

| Step | Delegate | Why this skill doesn't do it directly |
|---|---|---|
| 1 | `requesting-code-review` (three-way dispatch: docs-only delegates whole to `requesting-docs-review`; mixed splits per-file; code-only unchanged) | Human-judgment quality review is its own skill with its own subagent; this orchestrator just dispatches |
| 2 | `verification-before-completion` | Package-level test invocation has its own per-stack command table; this orchestrator just invokes the gate |
| 2b | `ui-verification` (conditional) | The user's main acceptance stage for a UI-bearing branch — what "done" means to them — has its own tooling/degradation contract (browser/device automation, N/A-loud); fires only when the branch touched UI and a `ui-flows.md` exists |
| 3 | `dev-workflow:git-memory` | P3-D MANDATORY — git-memory decides whether memory trailers are warranted on this commit. Orchestrator passes the diff + recent commits; git-memory returns the trailer set (or empty, if routine) |
| 4 | git CLI | Standard `git commit -m "<msg>" -m "<body with trailers>"` |
| 5 | git CLI | `git push -u origin <branch>` if new; `git push` if upstream set |
| 6 | gh CLI | `gh pr create --title "<title>" --body "<body>"`; authorization is request-derived — it arrived with the close-out request, so Step 11 opens the PR without a re-ask (up-front opt-out honored) |
| 7 | `using-git-worktrees` | Worktree cleanup pattern lives in that skill; this orchestrator just offers to invoke its `git worktree remove` flow |

**The orchestrator does NOT**:
- Duplicate git-memory's trailer-decision logic (P3-D — would create drift)
- Decide commit messages from scratch (delegates to git-memory output)
- Force the merge — merge stays with the user, never auto-run (PR-open is different: its authorization is request-derived, arriving with the close-out request, so Step 11 opens the PR and reports loudly rather than re-asking; see §What this skill does NOT do)

## Default flow — what happens if user just says "finish this branch"

```
1. Read branch state — git status + git log main..HEAD + git diff main...HEAD
   When the branch has a plan carrying the progress headers, render the
   card once on entry (`python3 scripts/plan_card.py <plan-path>`, framed
   per `loom-pipeline/hooks/family-relay.md §(a2) Progress card`) so the
   user sees the whole arc before the gates run. Repo-root
   `scripts/plan_card.py` when it exists; otherwise the plugin-shipped
   copy: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py"
   <plan-path>` (a load-time substitution, not a run-time shell
   variable). No plan, or a plan
   with no Status lines at all (old-format) → skip silently; a plan
   whose Status VALUES the parser rejects (plan_card's "has status
   '…', outside" error) → relay that error line loudly, never skip;
   script absent (both copies) or family-relay absent → render the
   four fields inline:
   goal, task table, stage, next.
2. Verify branch has commits (else: "nothing to finish; branch matches main")
3. Dispatch requesting-code-review — route on the returned verdict, not raw severity:
   - If NEEDS_REVISION (any 🔴 fatal, or 2+ 🟡 should-fix): surface findings; STOP. Wait
     for user remediation. (Consistent with requesting-code-review: NEEDS_REVISION → do NOT push.)
   - If PASS_WITH_NOTES (exactly 1 🟡, no 🔴): auto-proceed — carry the 🟡 finding forward
     into the PR body and the final close-out report as noted debt.
   - If PASS (all 🟢): proceed silently.
   - If the docs arm (requesting-docs-review) returns its bounded-cap STOP: surface the
     surviving findings to the user now — do NOT fold this into the fix→re-review loop
     below. That skill's bounded convergence cap now runs one mechanically-conditioned
     auto-delta round on its own authority and REPORTS it in its rollup — the conditions
     live in its Directive 1 and are not restated here. A cap-STOP therefore reaches this
     step only in the shapes requesting-docs-review still stops on: a round-2
     NEEDS_REVISION shape failing the auto-round conditions (a round-2 PASS_WITH_NOTES
     auto-proceeds per the bullet above), or a round-3 verdict other than PASS or
     PASS_WITH_NOTES. Rounds beyond the bounded cap run only on explicit user
     authorization.
   - Budget/quota failure fallback: if the code-reviewer subagent fails to launch due to
     budget or quota exhaustion, perform an inline B2 self-review — Read the diff, surface
     🔴 / 🟡 / 🟢 findings with an explicit "(self-review — code-reviewer unavailable)" caveat,
     then derive the verdict by the same aggregation (any 🔴 or 2+ 🟡 → NEEDS_REVISION;
     exactly 1 🟡 → PASS_WITH_NOTES; all 🟢 → PASS) and apply the gate above. NEVER suggest
     `/ultrareview` or any external review command in AskUserQuestion options or in the PR body
     without first verifying it exists via `claude --help`.
   - Explicit contract: NEEDS_REVISION review loops — fix → re-review, whether inside
     SDD's per-task triad during development or this step's own fix-up cycle — digest
     silently; the user sees only the terminal verdict, never each iteration.
     PASS_WITH_NOTES above auto-proceeds without asking — consistent with this
     digest-silently posture, not an exception to it. The docs-arm cap-STOP above IS
     the one exception: it surfaces to the user immediately rather than looping silently.
4. Before applying any review findings from Step 3: Read each file you intend to Edit
   (Bash inspection does NOT satisfy the Edit/Write precondition) — details in
   [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §S1.
   When a finding's fix edits a prose contract, the new material goes in its OWN
   sentence or inside the placeholder it governs — never spliced into an existing
   sentence that pins or enumerations depend on (repo memory:
   splicing-into-a-pinned-sentence-creates-false-readings).
5. Dispatch verification-before-completion
   - MANDATORY even if tests were run immediately before invoking this skill. Step 3
     fix-ups may have modified files; a pre-invocation test run does NOT satisfy this gate.
   - If test failure: surface output; STOP. Route user to tdd-iron-law or systematic-debugging.
   - If 0 tests ran: surface as failure (configuration bug, not a pass).
   - If PASS: proceed silently.
5b. Dispatch ui-verification — for a UI-bearing branch, this IS the user's main
    acceptance stage: what the user judges "done" by is the rendered product,
    not test counts (CONDITIONAL — skip as N/A when the branch touched no UI
    surface or no ui-flows.md exists; state the N/A, don't silently omit)
   - NEEDS_REVISION (state mismatch, or unreachable state whose ui-flows.md row is NOT
     marked future/deferred): surface findings; STOP — route to the
     implementer, or flag the design station if the enumeration itself is wrong.
   - PASS_WITH_NOTES: proceed; carry untestable-state notes into the PR body.
6. Invoke dev-workflow:git-memory
   - Pass: diff, recent commits, branch name
   - Receive: trailer set (Decision: / Learning: / Gotcha: lines) + commit body suggestion
   - **The moment this trailer set comes back non-empty, run the Memory-timing check NOW** (see
     Step 8's Memory-timing row for the exact rule) — using the returned Decision/Learning/Gotcha
     content itself as the input: does any of it also belong in `docs/loom/memory/` as a durable,
     cross-branch-reusable practice/gotcha/process, not just this commit's local trailer? Do NOT
     defer this question to Step 8's later checklist pass — a non-empty trailer set writing rich
     "why" content is itself the trigger, and treating "trailers written" as "memory handled" is
     the exact lapse this inline check exists to prevent (documented recurrence: PR #519, PR #520).
7. Run the privacy gate on the composed commit message + trailers —
   git-memory's compose-commit protocol Step 3.5, the fail-closed
   two-layer check: layer-1 deterministic scan via
   `dev-workflow/skills/git-memory/scripts/privacy-scan.py`
   (`--text-file <path>`), then layer-2 fresh-context judge per
   `dev-workflow/skills/git-memory/protocols/privacy-judge-spec.md`
   (both live in the dev-workflow plugin — pass the judge this full
   path, not a bare filename).
   - PASS (layer-1 clean AND layer-2 PASS): proceed silently — no user ask.
   - BLOCK (any layer-1 finding, a layer-2 BLOCK, or a fail-closed
     condition — script error, judge dispatch failure, or
     non-conforming judge output): surface the findings; ASK the user
     to resolve before proceeding. This is now the ONLY user stop Step
     7 has, and it fires only on failure — the user may still edit the
     message to clear the finding.
8. git hygiene before the close-out commit:
   - Close-out sub-checks — all orchestrator-only, ONCE per branch; a parallel wave
     would race each check's target file:

     | Check | When it fires | Action | On failure or N/A |
     |---|---|---|---|
     | Living-spec index regen | The repo has a `docs/loom/` tree. | Run `python3 loom-code/scripts/check-living-spec-index.py --write-index docs/loom/INDEX.md <repo-root>` once, then stage the regenerated `docs/loom/INDEX.md` (`git add docs/loom/INDEX.md`) into THIS close-out commit. | — |
     | Archive-on-close | This branch consumed a loom-spec change-folder (bound per writing-plans' detection cascade — see `../writing-plans/SKILL.md` §Consuming a loom-spec change-folder) AND its scenarios shipped. Recover bound-ness by grepping the branch's plan (`docs/loom/plans/<date>-<topic>.md`) for change-folder join keys (the `<change-id> / Requirement: <name> / Scenario: <name>` pattern per `../writing-plans/references/plan-format.md`) — they name the bound change-id; none (or no plan) = unbound — never guess a change-id from content similarity. | Run `python3 loom-code/scripts/archive_change_folder.py <change-id> <repo-root>` (argv per the script's docstring: change-id first, root second — do NOT guess), then stage the move (`git add docs/loom/archive/<date>-<change-id>/` and the now-removed `docs/loom/<change-id>/` path) into THIS close-out commit. | No change-folder bound → say loudly, never silently skip: "archive-on-close: N/A — no change-folder bound". |
     | Memory-timing check | Asked and answered at Step 6, the moment git-memory's trailer set came back — this row only STAGEs whatever `docs/loom/memory/` file that check produced. | A durable, already-known fact (practice / gotcha / process per the jurisdiction table) goes into `docs/loom/memory/` NOW, staged into THIS close-out commit — exact rule and its one exception: `docs/loom/memory/README.md` §"When to record". | Question NOT asked at Step 6 → ask it now — late beats never — treat it as a process miss. |
     | Memory-store integrity | Fires ONLY when this branch added or edited a file under `docs/loom/memory/`; otherwise skip silently (auditable from the diff). | Run `python3 scripts/check_loom_memory_integrity.py` from the repo root before the close-out commit; exit 0 is the gate. §Index invariant (`docs/loom/memory/README.md`): one index line per memory file, description = the file's frontmatter `description`, byte-identical — index generated from frontmatter, so the memory file alone leaves the store invalid until regen. CI's catching job is named `plugin version bump`, so run it locally. Recurrence is why this check exists — the same miss shipped twice. | Checker absent (it ships in no plugin) → say `memory-store integrity: N/A — checker not present in this repo` loudly and move on — never read a "No such file" nonzero as a store violation. On nonzero: run `python3 scripts/check_loom_memory_integrity.py --write`, re-run until exit 0, then `git add` the corrected `docs/loom/memory/README.md` — do not commit on a violation; `--write` itself nonzero → fix the file it names, repeat. It validates the WORKING TREE — an unstaged index fix ships the exact defect this check prevents. |
     | Backlog-close check | The repo has `docs/loom/backlog/` AND this branch ships or supersedes a backlog entry — grep the store for the branch's topic terms and read the hits. | Flip the entry's `status:` to SHIPPED (or CLOSED — SUPERSEDED), append one body line naming the evidence (this branch/PR); if `scripts/backlog_index.py` exists at the repo root, regenerate with `python3 scripts/backlog_index.py --write` and stage both in the same close-out commit. When the repo-root copy is absent, run the plugin-shipped copy instead — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog_index.py"` with the same arguments (a load-time substitution, not a run-time shell variable) — for this and every `backlog_index.py` invocation in this row. Then, when the repo also has `docs/loom/DIRECTION.md`: run `python3 scripts/backlog_index.py --direction-write docs/loom/DIRECTION.md` and stage the refreshed file into the same close-out commit; if COMMITTED-NEXT is EMPTY, surface a betting prompt to the user — list candidates same-lane first (when the just-closed arc belongs to a theme, that theme's next arc leads the list, if one exists), then `--ready`'s output — the USER promotes (edits status to COMMITTED-NEXT) or declines; agents never auto-promote — promotion is never a silent default. If the user promotes, re-run `python3 scripts/backlog_index.py --write` and `python3 scripts/backlog_index.py --direction-write docs/loom/DIRECTION.md`, then re-stage the refreshed `BACKLOG.md` and `DIRECTION.md` before this close-out commit lands. | No hit, or no store → skip silently (auditable from the diff, like the memory-store row). `backlog_index.py` absent from both the repo root and the plugin (the loom-code plugin not installed, or its cache copy missing) → say `backlog-close: index not regenerated — backlog_index.py not present`, stage the entry flip alone, noting the regen needs a machine with the script — this N/A now also covers the direction refresh. No `docs/loom/DIRECTION.md` in this repo → skip the betting duty silently (opt-in mechanism, same posture as the store-absent case). |
   - Attached-HEAD check: run `git symbolic-ref -q HEAD` in the main
     working tree — it must print the branch being finished. Detached
     HEAD or a different branch means something (typically a subagent)
     moved this tree mid-flight; STOP, reattach (`git checkout <branch>`,
     fast-forwarding any commits that already landed detached), and only
     then commit — never commit the close-out on a detached HEAD.
   - Run `git status --short` to confirm exactly which files are staged and untracked.
   - Stage with an explicit file list (`git add <file1> <file2> …`) — avoid `git add -A <dir>`
     which sweeps unrelated untracked files into the commit.
   - Use the branch-qualified push form `git push -u origin <branch>` (or `git push origin
     <branch>` if upstream already set) — NEVER a bare `git push`, which trips the sandbox
     "do not push to main" guard on the first push of a new branch.
   - Compound `git push && gh pr create` must be two separate Bash calls, and any rebase-conflict
     resolution uses Read+Edit (not Bash `cat`+`Write`) — details in
     [environment-gotchas](../using-loom-code/references/environment-gotchas.md) §S2/§D1.
   - If any review-driven fixes were applied in Steps 3–4, re-run verification-before-completion
     here (Step 5 result is stale) before committing.
9. git commit (only after Step 7's privacy gate PASSes, or after the
   user resolves a Step-7 BLOCK)
9b. Commit-carrier verify gate — MANDATORY, runs AFTER the commit, BEFORE push:
    - Run `dev-workflow/skills/git-memory/scripts/memory-grep.sh --verify HEAD`
      (exit 0 = a Decision/Learning/Gotcha trailer is retrievable from HEAD's body;
      exit 4 = none).
    - If Phase 3 (Step 6) returned a NON-empty trailer set (the branch is
      memory-worthy) AND `--verify HEAD` exits 4: STOP. Surface "the close-out
      commit did not capture the memory trailers — fix before push." Do NOT push.
      Root cause this gate closes: a memory-worthy branch must not ship with an empty
      commit carrier — the decision would be unretrievable via `git log --grep` on
      main (the #445 leak). This is a hard STOP, consistent with finishing's other
      gates (NEEDS_REVISION review / test-failure both STOP).
    - If Phase 3 returned an EMPTY trailer set (routine branch), exit 4 is expected →
      proceed to push.
    - If `--verify HEAD` exits 0: the carrier landed → proceed to push.
9c. Gate markers at the FINAL HEAD — the `hooks/git-guard.py` PreToolUse gate blocks
    `git push` / `gh pr create` without both markers matching current HEAD:
    - Mint by running the package suite THROUGH the marker at the final HEAD:
      `python3 <plugin-root>/scripts/loom_gate_markers.py verified --run "<test command>"`
      (it executes the command and mints only on a real exit 0)
      — verification evidence must POSTDATE the close-out commit; a green run from before
      it is exactly the stale-green-light failure this gate exists to kill.
    - Mint the review marker at the final HEAD (save the Step-3 verdict text to a file,
      run `… loom_gate_markers.py review-pass --verdict-file <file>`) — allowed ONLY when
      the delta since the reviewed verdict is mechanical close-out content (living-spec
      INDEX regen, memory trailers). ANY substantive post-verdict change → re-dispatch
      requesting-code-review first: review what you ship, not what you reviewed an
      amend ago.
    - User explicitly waives review ("skip review, push now") → record it:
      `… loom_gate_markers.py waiver --reason "<user's words>"` — one-shot, consumed and
      logged by the gate on the next push. Never self-mint a waiver.
10. git push (branch-qualified form per Step 8)
11. Open the PR — no ask: the authorization arrived with the request
    (every §When to use trigger names the close-out endpoint; the one
    ambiguous row confirmed at entry). Skip only if gh CLI is
    unconfigured or the user opted out up front — then stop after
    push and say so.
    - Compose the PR body per `dev-workflow/skills/git-memory/protocols/compose-pr.md`,
      then run its Step 6 privacy gate over that composed body BEFORE `gh pr create` — the
      same two-layer gate (privacy-scan.py + the privacy-judge-spec.md judge, full
      cross-plugin paths in Step 7, fail-closed)
      that Step 7 runs on the commit carrier. Gate PASS → proceed to create; gate BLOCK
      (any layer-1 finding, layer-2 BLOCK, or a fail-closed condition) → surface findings
      and do NOT create the PR until the user resolves it. This is explicit, not transitive:
      the PR body is an outward-facing carrier and gets the identical mechanized gate as the
      commit, per the arc's mechanize-don't-rely-on-prose premise.
    - Then: gh pr create with title/body from git-memory + branch name
    - PR-carrier check (memory-worthy branch only): before declaring the PR ready,
      grep the PR body you just composed for a `## Memory` section. If Phase 3
      returned a non-empty trailer set and body has no `## Memory` section, flag
      it and add the section (both-carrier policy: commit AND PR carry memory;
      no new tooling, it's a grep on the body you're about to submit). Also
      verify the raw trailer footer carrier — the PR body's true last block
      must be a raw trailer block (one or more plain `Decision:`/`Learning:`/
      `Gotcha:` `Key: value` lines, blank-line-separated from what precedes,
      NOTHING after them — a single such line qualifies), per
      `dev-workflow/skills/git-memory/protocols/compose-pr.md` Step 4 for full
      placement rules; fix the body before submitting if missing/not last.
    - Offer BOTH merge paths in the report: the PR web URL — with a reminder
      to glance that the merge dialog's description box is prefilled before
      confirming — AND the ready-to-run `gh pr merge <N> --squash` CLI
      alternative, framed for the human to run themselves (e.g. via the `!`
      prefix). Web-dialog prefill is unreliable; see
      `docs/loom/memory/squash-dialog-can-drop-entire-pr-body.md`. The
      orchestrator prepares the command, never runs it — no auto-merge.
12. ASK user: "Branch was in .worktrees/; remove the worktree? (y/N)"
    - If yes: cd to repo root; git worktree remove .worktrees/<slug>
    - If no: leave it
13. Report final state as a product-language completion report — lead with what
    the product now does, in user terms (not with mechanism); commit SHA, push
    status, test counts, and review verdicts sink to sub-lines below that
    headline. Format authority: `loom-pipeline/hooks/family-relay.md` §(a)'s
    Close-out card (not the generic User-rollup card — the close-out
    specialization). Include: PR URL if created — same both-paths merge
    guidance as Step 11 (glance the prefilled dialog before confirming,
    plus the ready-to-run `gh pr merge <N> --squash` CLI alternative) —
    and worktree status. End the report with one line naming the top
    of the remaining COMMITTED-NEXT backlog queue ("backlog next:
    <name>" — or "COMMITTED-NEXT queue empty"), from
    `python3 scripts/backlog_index.py --ready` (repo-root copy; when
    absent, the plugin-shipped
    `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog_index.py" --ready`);
    skip the line when the repo has no backlog store or neither copy
    of `backlog_index.py`.
```

**ASK = stop and wait for user.** That guarantee is now exception-based, not blanket: close-out is autonomous on the happy path — Steps 1–10 proceed silently once each step's own gate PASSes, including Step 7's privacy gate. What remains is one OUTWARD-FACING action that always asks (Step 12 — remove the worktree, because it touches shared state), plus a Step 7 privacy-gate BLOCK, where the human returns only because the gate failed; Step 11 (open a PR) no longer asks — its authorization arrived with the request, so it reports loudly instead. For any remaining question, run the ask-vs-resolve triage at `subagent-driven-development` §Asking the user, gate ① (the cross-skill SSOT) before asking.
Every gate STOP that surfaces to the user (a NEEDS_REVISION, a privacy
BLOCK, a probe FAIL) leads with the progress card — the user sees
where the arc stopped before deciding.

## Red Flags — refuse these rationalizations

Close-out shortcuts to refuse — *"skip review just push," "tests passed yesterday skip verification," "message is obvious skip git-memory," "auto-merge after push," "force-push to clean up history," "just amend the last commit," "I already have an SDD commit message"* (and localized 「review skip / 跳過審查」). Default posture: refuse the shortcut, dispatch the gate it bypasses. Full table (rationalization → why it is one → correct response) in [`references/red-flags.md`](references/red-flags.md).

## What this skill does NOT do

Delegates rather than duplicates: review → `requesting-code-review`, tests → `verification-before-completion`, memory trailers → `dev-workflow:git-memory` (P3-D). Does **not** merge into main, force-push, amend commits (creates new per CLAUDE.md), or auto-remove worktrees — worktree removal still needs explicit user authorization, while PR-open does not re-ask: its authorization arrives with the close-out request. (Shortcut-refusal rationale for merge/force-push/amend lives in [`references/red-flags.md`](references/red-flags.md).)

## See also

- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — Phase 1 delegate.
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — Phase 2 delegate.
- [`../ui-verification/SKILL.md`](../ui-verification/SKILL.md) — Phase 2 conditional sibling (rendered-UI gate).
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — Phase 7 delegate (worktree cleanup).
- `dev-workflow:git-memory` — Phase 3 delegate (commit-trailer gate, P3-D MANDATORY).
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 8 (Branch close).
- CLAUDE.md §"Committing changes with git" — git policy (no amend, no skip hooks, no force-push without authorization) this skill inherits.
