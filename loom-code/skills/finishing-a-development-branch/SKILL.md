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

Orchestrates the close-branch sequence: invoke each step's specialist skill in order, gate progress on each step's verdict, surface the final state to the user. Before executing, Read the CURRENT SKILL.md from the installed plugin — never run the flow from memory or a compacted summary. **The user retains agency for the final merge decision** (push + PR is automated; actual merge into main is not).

```
finishing-a-development-branch (this skill)
  │
  ├─→ Phase 1: requesting-code-review
  │     four-way dispatch by file type (record-only / docs-only / mixed / code-only;
  │     docs-only delegates to requesting-docs-review)
  │     → verdict: PASS / PASS_WITH_NOTES / NEEDS_REVISION
  │     blocks on NEEDS_REVISION (any 🔴, or 2+ 🟡); PASS_WITH_NOTES (1 🟡) auto-proceeds
  │
  ├─→ Phase 2: verification-before-completion
  │     package-level tests → exit 0 + N>0 → PASS; blocks on failure
  │     + ui-verification (CONDITIONAL): UI-bearing branch with a ui-flows.md
  │
  ├─→ Phase 3: loom-workflow:git-memory (P3-D MANDATORY)
  │     decides Decision: / Learning: / Gotcha: trailers for the close-out commit
  │
  ├─→ Phase 4: git commit (orchestrator runs this)
  │     message + trailers from Phase 3; no hook bypass, no amend
  │     then memory-grep.sh --verify HEAD (memory-worthy + exit 4 → STOP pre-push)
  │
  ├─→ Phase 5: git push (orchestrator runs this)
  │     pushes the branch; sets upstream first if local-only
  │
  ├─→ Phase 6 (optional): gh pr create
  │     only if gh CLI configured AND not opted out; PR body per git-memory convention
  │
  ├─→ Phase 7: Post-PR CI
  │     post_pr_ci.py waits on the created PR's current head; bounded repair on fail
  │
  └─→ Phase 8 (optional): git worktree cleanup
        if branch was in .worktrees/, offer (do NOT auto-execute) the remove
        per using-git-worktrees §Removing a worktree

(Diagram = phase overview; §Default flow's numbered **Step** list is the granular
procedure — "Phase N" and "Step N" are distinct numbering schemes.)
```

## When NOT to use

Exempt: **mid-task work**, **trivial direct-to-main commits**, an **abandoned branch**, and an **explicit override** with a real reason. These waive close-out but **NEVER `loom-workflow:git-memory`**. Full table: [`references/when-not-to-use.md`](references/when-not-to-use.md).

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

This skill is light on novel logic — its value is orchestration; the work happens in delegated specialists:

| Step | Delegate | Why this skill doesn't do it directly |
|---|---|---|
| 1 | `requesting-code-review` (four-way dispatch; docs-only → `requesting-docs-review`) | Own subagent |
| 2 | `verification-before-completion` | Own per-stack command table |
| 2b | `ui-verification` (conditional) | Own tooling/degradation contract |
| 3 | `loom-workflow:git-memory` | P3-D MANDATORY |
| 4 | git CLI | Standard commit |
| 5 | git CLI | Standard push |
| 6 | gh CLI | Request-derived authorization |
| 7 | `post_pr_ci.py` + `systematic-debugging` | Post-PR CI waits on the current PR head; own bounded CI repair evidence |
| 8 | `using-git-worktrees` | Own cleanup pattern |

Boundaries: [`references/delegation-boundaries.md`](references/delegation-boundaries.md).

## Default flow — what happens if user just says "finish this branch"

```
1. Read branch state — git status + git log main..HEAD + git diff main...HEAD
   When the branch has a plan carrying the progress headers, render the
   card once on entry (`python3 scripts/plan_card.py <plan-path>`, framed
   per `loom-code/hooks/family-relay.md §(a2) Progress card`) so the
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
   - If the docs arm (requesting-docs-review) returns a STILL_BLOCKING confirmation:
     surface the finding and the reviewer's reason to the user now — do NOT fold this
     into the fix→re-review loop below. That skill runs a single-round-with-confirmation
     contract: round 1 is whole-artifact and the only full review; a gating verdict is
     fixed once, then confirmed through its host-specific convergence route
     (mechanics live in its Directive 2, not restated here). STILL_BLOCKING after
     that one fix cycle STOPs here — no second confirmation
     cycle and no fresh round 1 run without explicit user authorization.
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
     digest-silently posture, not an exception to it. The docs-arm STILL_BLOCKING
     confirmation above IS the one exception: it surfaces to the user immediately
     rather than looping silently.
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
6. Invoke loom-workflow:git-memory
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
   two-layer check: ask `loom-workflow:git-memory` to run its deterministic
   `privacy-scan.py` (`--text-file <path>`), then its fresh-context judge
   using `privacy-judge-spec.md`. The public skill owns both implementation
   details; do not resolve sibling-plugin paths.
   - **Resolve the dispatch profile** in [`using-loom-code`'s portable
     profile](../using-loom-code/references/dispatch-profile.md) before the
     fresh-context judge spawn. Privacy review is security-sensitive, so its
     packet is `tier=frontier; requested_effort=high`; the host adapter
     records its effective effort separately.
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
     | Archive-on-close | This branch consumed a loom-design change-folder (bound per writing-plans' detection cascade — see `../writing-plans/SKILL.md` §Consuming a loom-design change-folder) AND its scenarios shipped. Recover bound-ness by grepping the branch's plan (`docs/loom/plans/<date>-<topic>.md`) for change-folder join keys (the `<change-id> / Requirement: <name> / Scenario: <name>` pattern per `../writing-plans/references/plan-format.md`) — they name the bound change-id; none (or no plan) = unbound — never guess a change-id from content similarity. | Run `python3 loom-code/scripts/archive_change_folder.py <change-id> <repo-root>` (argv per the script's docstring: change-id first, root second — do NOT guess), then stage the move (`git add docs/loom/archive/<date>-<change-id>/` and the now-removed `docs/loom/<change-id>/` path) into THIS close-out commit. | No change-folder bound → say loudly, never silently skip: "archive-on-close: N/A — no change-folder bound". |
     | Memory-timing check | Asked and answered at Step 6, the moment git-memory's trailer set came back — this row only STAGEs whatever `docs/loom/memory/` file that check produced. | A durable, already-known fact (practice / gotcha / process per the jurisdiction table) goes into `docs/loom/memory/` NOW, staged into THIS close-out commit — exact rule and its one exception: `docs/loom/memory/README.md` §"When to record". | Question NOT asked at Step 6 → ask it now — late beats never — treat it as a process miss. |
     | Memory-store integrity | Fires ONLY when this branch added or edited a file under `docs/loom/memory/`; otherwise skip silently (auditable from the diff). | Run `python3 scripts/check_loom_memory_integrity.py` from the repo root before the close-out commit; exit 0 is the gate. §Index invariant (`docs/loom/memory/README.md`): one index line per memory file, description = the file's frontmatter `description`, byte-identical — index generated from frontmatter, so the memory file alone leaves the store invalid until regen. CI's catching job is named `plugin version bump`, so run it locally. Recurrence is why this check exists — the same miss shipped twice. | Checker absent (it ships in no plugin) → say `memory-store integrity: N/A — checker not present in this repo` loudly and move on — never read a "No such file" nonzero as a store violation. On nonzero: run `python3 scripts/check_loom_memory_integrity.py --write`, re-run until exit 0, then `git add` the corrected `docs/loom/memory/README.md` — do not commit on a violation; `--write` itself nonzero → fix the file it names, repeat. It validates the WORKING TREE — an unstaged index fix ships the exact defect this check prevents. |
     | Backlog-close check | The repo has `docs/loom/backlog/` AND this branch ships or supersedes a backlog entry — grep the store for the branch's topic terms and read the hits. | Flip the entry's `status:` to `closed`, append one body line naming the evidence (this branch/PR); if `scripts/backlog_index.py` exists at the repo root, regenerate with `python3 scripts/backlog_index.py --write` and stage both in the same close-out commit. When the repo-root copy is absent, run the plugin-shipped copy instead — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog_index.py"` with the same arguments (a load-time substitution, not a run-time shell variable) — for this and every `backlog_index.py` invocation in this row. Then, when the store is present AND holds zero live `bet` entries, report `bet queue empty` in the close-out card and do not ask the user to select or promote a candidate; agents never auto-promote — promotion is never a silent default, so leave the queue unchanged. | No hit, or no store → skip silently (auditable from the diff, like the memory-store row). `backlog_index.py` absent from both the repo root and the plugin (the loom-code plugin not installed, or its cache copy missing) → say `backlog-close: index not regenerated — backlog_index.py not present`, stage the entry flip alone, noting the regen needs a machine with the script. |
     | Open-questions check | The branch has a plan — reuse the path Step 1 already read to render the progress card, not a fresh discovery rule. | Run `python3 loom-code/scripts/check_open_questions.py <plan-path>` before the close-out commit; exit 0 is the gate — every `## Open Questions` entry is `[RESOLVED]`, or the section carries the well-formed N/A line. Prose orchestrator check, not hook-level — `git-guard.py` (Step 9c) is blind to plan content. | Nonzero (an `[OPEN]` entry, or section absent/malformed) → **STOP**; surface stderr verbatim (it names the unresolved `OQ-<n>`, or describes the absent/malformed section) and route back to the user or plan author — do not commit past it. No plan → skip silently, per Step 1. |
     | Stage-flip duty | The branch has a plan carrying the progress headers (the same plan Step 1 rendered). | BEFORE the close-out commit, flip the plan's terminal state: run `python3 scripts/plan_card.py <plan-path> --set-stage "finishing"` — repo-root `scripts/plan_card.py` when it exists; otherwise the plugin-shipped copy: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" <plan-path> --set-stage "finishing"` (a load-time substitution, not a run-time shell variable). Then stage the flipped plan file (`git add docs/loom/plans/<plan>.md`) into THIS close-out commit. | No plan, a plan with no Status lines at all (old-format), or a plan whose ledger predates the `Stage:` header (Status lines but no `Stage:` — `--set-stage` refuses nonzero on that shape) → skip silently, per Step 1's entry-card rules. |
     | Stale-scan relay | Every close-out where the repo has a `docs/loom/plans/` directory. | Run `python3 scripts/plan_card.py --stale-scan docs/loom/plans` — repo-root `scripts/plan_card.py` when it exists; otherwise the plugin-shipped copy: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plan_card.py" --stale-scan docs/loom/plans` (a load-time substitution, not a run-time shell variable). Relay its stdout VERBATIM and loudly to the user — including the single `stale-scan: clean` line. A candidate plan belonging to an already-merged arc gets fixed on the spot: the same `--set-stage "finishing"` flip, staged into THIS close-out commit. A candidate belonging to a live parallel arc is named and passed through untouched. The scan is advisory by design — it always exits 0, because all-done at `review:round-N` is a legitimate transient state of a live arc; never harden a candidate line into a block or a STOP. | No `docs/loom/plans/` directory → skip silently (nothing to scan, auditable from the tree). |
   - **Purpose-linked betting.** Never list or promote a bet on automatic close-out. Only AFTER the user explicitly requests choosing or promoting a bet, and before listing betting candidates, print `docs/loom/PURPOSE.md`; if absent, offer to write one — never silently skip the print. After promotion run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_north_star_link.py" <backlog-store>` (load-time substitution, not a run-time shell variable). Exit 0 means every live bet is linked. Exit 1 means an unreadable store or status vocabulary outside its closed vocabulary; fix that entry's frontmatter. Exit 2 means unresolved `PURPOSE.md` is absent, unanswered, or `serves` is malformed. STOP-and-ask: relay the printed question, wait, record it where that question asks (`PURPOSE.md` itself when applicable), then re-run. Status semantics remain in `docs/loom/backlog/README.md`.
   - **N/A consolidation (close-out report)**: when two or more close-out
     sub-checks above are N/A, do NOT stack ~4-5 separate "N/A — checker not
     present" lines before the conclusion. Each N/A stays STATEABLE (the
     per-check "say loudly" semantics are preserved — the check still runs
     and names its reason), but in the Step 13 report they consolidate inapplicable checks into
     ONE summary line after the plain conclusion: "N inapplicable checks skipped: <list>; details on request."
     Conclusion-first — the user sees the outcome before skipped-checks noise. A single N/A still emits its
     own one-line note; only the multi-N/A case collapses.
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
    - Ask `loom-workflow:git-memory` to run `memory-grep.sh --verify HEAD`
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
      INDEX regen, memory trailers, plan Stage flips incl. stale-scan fixes,
      backlog status flips with regen). ANY substantive post-verdict change → re-dispatch
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
    - Ask `loom-workflow:git-memory` to compose the PR body per its `compose-pr.md` protocol,
      then run its Step 6 privacy gate over that composed body BEFORE `gh pr create` — the
      same two-layer gate (privacy-scan.py + the privacy-judge-spec.md judge, full
      cross-plugin paths in Step 7, fail-closed)
      that Step 7 runs on the commit carrier. Gate PASS → proceed to create; gate BLOCK
      (any layer-1 finding, layer-2 BLOCK, or a fail-closed condition) → surface findings
      and do NOT create the PR until the user resolves it. This is explicit, not transitive:
      the PR body is an outward-facing carrier and gets the identical mechanized gate as the
      commit, per the arc's mechanize-don't-rely-on-prose premise.
    - PR-carrier check (memory-worthy branch only): before creating the PR,
      grep the composed body for a `## Memory` section. If Phase 3 returned a
      non-empty trailer set and the section is absent, add it. Also verify the
      true last block is the raw `Decision:`/`Learning:`/`Gotcha:` trailer
      footer required by `loom-workflow:git-memory`'s `compose-pr.md` Step 4;
      fix the body before submitting if either carrier is missing or misplaced.
    - **Resolve the dispatch profile** in [`using-loom-code`'s portable
      profile](../using-loom-code/references/dispatch-profile.md) before the
      fresh-context PR-body judge spawn. Its packet is
      `tier=frontier; requested_effort=high`; the host adapter records its
      effective effort separately.
    - Then: `PR_URL="$(gh pr create --title "$PR_TITLE" --body-file
      "$PR_BODY_FILE")"`, using the title/body composed by git-memory. The
      locally verified `gh pr create --help` documents stdout URL output and
      exposes no `--json` flag.
    - Resolve `PR_NUMBER="$(gh pr view "$PR_URL" --json number --jq .number)"`.
      Use `$PR_NUMBER` for every later `gh pr view` and helper call.
    - **Post-PR CI phase:** after `gh pr create` succeeds, resolve the created
      PR and its current head with `gh pr view "$PR_NUMBER" --json headRefOid`, then
      run `python3 <plugin-root>/scripts/post_pr_ci.py --pr "$PR_NUMBER"
      --expected-head <current-head>`. This helper owns polling and does not
      replace its algorithm with prose here.
      - On status `"pass"`, report that the PR is CI-verified and continue to
        the final report.
      - On status `"fail"`, enter one repair attempt through
        `systematic-debugging` using the remote CI evidence. After its fix,
        re-run `requesting-code-review`, then
        `verification-before-completion`, then `loom-workflow:git-memory`.
        Run the privacy gate, then `git commit` the repair. Mint fresh
        `loom_gate_markers.py` markers at that repaired head; then `git push`.
        Resolve the new HEAD with `gh pr view "$PR_NUMBER" --json headRefOid` and wait
        again with `post_pr_ci.py` against that new HEAD.
      - Permit at most two automated repair attempts. A third `"fail"` is
        budget exhaustion: STOP, surface the CI evidence, and wait for user
        direction.
      - On `cancelled`, STOP with the helper JSON and cancellation evidence;
        do not let a cancelled check fall through to repair or a pass report.
      - On `timeout`, `no_checks`, `operational_error`, or `head_drift`, STOP
        with the helper JSON and actionable evidence. The orchestrator must
        never auto-merge.
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
    headline. Format authority: `loom-code/hooks/family-relay.md` §(a)'s
    Close-out card (not the generic User-rollup card — the close-out
    specialization). Include: PR URL if created — same both-paths merge
    guidance as Step 11 (glance the prefilled dialog before confirming,
    plus the ready-to-run `gh pr merge <N> --squash` CLI alternative) —
    and worktree status. End the report with one line naming the top
    of the remaining bet queue ("next bet:
    <name>" — or "bet queue empty"), from
    `python3 scripts/backlog_index.py --ready` (repo-root copy; when
    absent, the plugin-shipped
    `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog_index.py" --ready`);
    skip the line when the repo has no backlog store or neither copy
    of `backlog_index.py`.
    Include CI evidence: the checked PR head, helper status, and any repair
    attempt count or stopping evidence.
```

**ASK = stop and wait for user.** Exception-based, not blanket: close-out is autonomous on the happy path — Steps 1–10 proceed silently once each step's gate PASSes. What asks: one outward-facing action — Step 12 (worktree removal — touches shared state) — and a Step 7 privacy-gate BLOCK (human returns only because the gate failed). Step 11 (open a PR) reports loudly instead of asking — authorization arrived with the request. For any remaining question, run the ask-vs-resolve triage at `subagent-driven-development` §Asking the user, gate ① (the cross-skill SSOT) before asking.
Every gate STOP that surfaces to the user (a NEEDS_REVISION, a privacy BLOCK, a probe FAIL) leads with the progress card — the user sees where the arc stopped before deciding.

## Red Flags — refuse these rationalizations

Close-out shortcuts to refuse — *"skip review just push," "tests passed yesterday skip verification," "message is obvious skip git-memory," "auto-merge after push," "force-push to clean up history," "just amend the last commit," "I already have an SDD commit message"* (and 「review skip / 跳過審查」). Default: refuse the shortcut, dispatch the gate it bypasses. Full table in [`references/red-flags.md`](references/red-flags.md).

## What this skill does NOT do

Never merges into main or force-pushes; see full boundary list in [`references/delegation-boundaries.md`](references/delegation-boundaries.md).

## See also

Sibling-skill delegates and the git policy this skill inherits — full list in [`references/delegation-boundaries.md`](references/delegation-boundaries.md).
