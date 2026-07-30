# Plan: whole-branch review round ledger + bad-fix re-check

**Source brief**: docs/loom/specs/2026-07-29-review-round-ledger-and-bad-fix-recheck.md
**Total tasks**: 8
**Critical-path depth**: 5 (≤5 ✓ — longest chain Task 1 → 2 → 3 → 7 → 8)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: NEEDS_REVISION (2026-07-30, round 1, 13/14) — never re-reviewed; this plan was PARKED before its five fixes were applied. The fixes are listed in `docs/loom/BACKLOG.md`'s park entry for this slice. Do not treat this plan as review-clean if it is ever unparked.

## Task 1 — Append a review-round ledger entry on every review-pass invocation

- **Description**: Extend `loom_gate_markers.py review-pass` so that every invocation appends one entry to `<git-dir>/loom/review-rounds.json` — **including the `NEEDS_REVISION` path that currently returns exit 3 without writing anything** (`loom-code/scripts/loom_gate_markers.py:268-272`). The file is keyed by branch name only, append-only, and never reset. Each entry carries `round` (1-based, per branch), `verdict`, `findings_reported`, `finding_paths` (the `where:` values), `head_sha`, `written_at`. Preserve every existing exit code and every existing marker write unchanged. Factor the finding-block segmentation currently inlined in `_finding_problems` into a helper both the validating lane and this counting lane call, so the two cannot diverge.
- **Module**: `loom-code/scripts/loom_gate_markers.py`
- **Files touched**: `loom-code/scripts/loom_gate_markers.py`, `loom-code/scripts/test_loom_gate_markers.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_gate_markers.py`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_loom_gate_markers.py`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/requesting-code-review/references/gate-markers-spec.md`
- **Acceptance**:
  - **RED**: `test_loom_gate_markers.py::test_review_rounds_ledger_appends_on_every_verdict` — parametrized over a `NEEDS_REVISION` invocation then a `PASS` invocation; asserts `review-rounds.json` holds two entries with `round` 1 and 2, the correct `verdict` per entry, `findings_reported` matching the number of `- severity:` blocks in each verdict text, and `finding_paths` matching their `where:` values.
  - **GREEN**: the test passes; the whole `loom-code/scripts/` suite stays green, proving no existing exit code (0 / 2 / 3 / 4) or marker write changed.
- **Reuse-adequacy**: the task reuses the finding-block segmentation at `loom-code/scripts/loom_gate_markers.py:224-249` (`_FINDING_RE` block starts, `_WHERE_RE` + `_PATHLIKE_RE` value match) in a **new lane** — extracting counts and values rather than emitting validation problems. **Behaviour-match claim**: block boundaries are identical in both lanes; only the return value differs (values versus problems). **Why acceptable**: the validating lane only needs to know *whether* a path-like `where:` exists per block, while the counting lane needs the value, so the shared part must be **factored out into one helper that both lanes call** — reusing the regexes by copy would let the two lanes' block boundaries drift silently while both lanes' own tests stay green.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "`loom_gate_markers.py review-pass` appends one entry per invocation — including the NEEDS_REVISION path that currently exits 3 writing nothing — to `<git-dir>/loom/review-rounds.json`, keyed by branch name only"

## Task 2 — Print the round trajectory from round 3 onward

- **Description**: When the appended entry's `round` is ≥3, print a trajectory table to **stderr** — one line per recorded round showing `round`, `verdict`, `findings_reported` — immediately **before** the existing exit-3 `NEEDS_REVISION` message (and before returning on the mint path). Rounds 1 and 2 print nothing additional. Emit no numeric cap, no threshold, and no verdict of its own: the print is data for the orchestrator to read, not a decision.
- **Module**: `loom-code/scripts/loom_gate_markers.py`
- **Files touched**: `loom-code/scripts/loom_gate_markers.py`, `loom-code/scripts/test_loom_gate_markers.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_gate_markers.py`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_loom_gate_markers.py`
- **Acceptance**:
  - **RED**: `test_loom_gate_markers.py::test_trajectory_prints_from_round_three` — asserts invocations 1 and 2 print no trajectory table, invocation 3 prints one containing all three rounds' numbers, and the existing exit-3 message still appears after it.
  - **GREEN**: the test passes; exit codes unchanged.
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: "from round 3 the command's own stderr output prints the trajectory table before its existing exit-3 message"

## Task 3 — Record bad-fix attribution counts per entry

- **Description**: For an entry whose `round` is ≥2, additionally record `prev_findings_addressed` (how many of the **previous** entry's `finding_paths` were touched by commits between that entry's `head_sha` and current HEAD) and `prev_fix_region_findings` (how many of **this** round's `finding_paths` fall in that same set of touched files — the bad-fix attribution). Derive both mechanically from `git diff --name-only <prev head_sha>..HEAD`; never from a caller-supplied number and never from a self-report. Add both columns to the Task 2 trajectory table. When the previous `head_sha` is unreachable (history rewritten), record both fields as `null` and say so in the table rather than guessing.
- **Module**: `loom-code/scripts/loom_gate_markers.py`
- **Files touched**: `loom-code/scripts/loom_gate_markers.py`, `loom-code/scripts/test_loom_gate_markers.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_gate_markers.py`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_loom_gate_markers.py`
- **Acceptance**:
  - **RED**: `test_loom_gate_markers.py::test_bad_fix_attribution_counts_from_git` — a fixture repo where round 1 cites two files, a commit then edits one of them, and round 2 cites one file inside that edited region; asserts `prev_findings_addressed == 1` and `prev_fix_region_findings == 1`, and that an unreachable previous `head_sha` yields `null` for both.
  - **GREEN**: the test passes; the trajectory table shows both new columns.
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: "`findings_bad_fix` — of the surviving ones, how many land in the previous round's fix region" (resolving Open Question 2 mechanically; see Decision Log)

## Task 4 — Add round discipline to requesting-code-review

- **Description**: Add the round-discipline rule to `requesting-code-review/SKILL.md`, transcribed **verbatim from the pin in this plan's `## Notes`**. It must state: from round 3, run the pinned trajectory command and surface its output; classify the loop with the five-state rubric plus the editorial-versus-structural distinction; escalate to the user on that judgment; and from round 1 onward, record rather than rewrite prose-surface findings. State **no numeric round cap**. Point at the script's output rather than enumerating its columns.
- **Module**: `loom-code/skills/requesting-code-review/SKILL.md`
- **Files touched**: `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/scripts/test_review_round_discipline.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/requesting-code-review/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/test_docs_review_mode.py`
- **Acceptance**:
  - **RED**: `test_review_round_discipline.py::test_requesting_code_review_carries_round_discipline` — assertions scoped to a **measured neighbourhood window** around the pinned command string (not whole-file grep), proven RED against `git show HEAD:loom-code/skills/requesting-code-review/SKILL.md`.
  - **GREEN**: the test passes; `wc -w` on the file stays under CHK-SKL-010's 4,500-word cap (it is at 3,930 before this task).
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: "In `requesting-code-review` and `finishing-a-development-branch`: from round 3, surface the trajectory the script printed, and classify the loop using a five-state rubric … escalate to the user — on that judgment, not on a round number"

## Task 5 — Add the digest-silently exception to finishing-a-development-branch

- **Description**: Amend `finishing-a-development-branch/SKILL.md:113-115`'s "digest silently" contract with an explicit round-3 exception, transcribed **verbatim from the pin in this plan's `## Notes`**. Do not delete the digest-silently rule — it stays correct for rounds 1-2. Then grep the whole `loom-code/` plugin for restatements of the digest-silently rule (router card, agent contracts, the three-language READMEs, PRODUCT-SPEC, ROADMAP) and fix every living restatement found; leave dated archives and CHANGELOG entries untouched.
- **Module**: `loom-code/skills/finishing-a-development-branch/SKILL.md`
- **Files touched**: `loom-code/skills/finishing-a-development-branch/SKILL.md`, `loom-code/scripts/test_finishing_round_discipline.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/skills/finishing-a-development-branch/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/memory/core-rule-removal-needs-plugin-wide-sweep.md`
- **Acceptance**:
  - **RED**: `test_finishing_round_discipline.py::test_digest_silently_carries_round_three_exception` — neighbourhood-scoped assertions around the pinned wording, proven RED against `git show HEAD:loom-code/skills/finishing-a-development-branch/SKILL.md`.
  - **GREEN**: the test passes; the plugin-wide grep for digest-silently restatements returns no living stale copy; file stays under the 4,500-word cap (3,261 before this task).
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: "`finishing-a-development-branch/SKILL.md:113-115`'s unqualified 'digest silently' contract — it gains an explicit exception at round 3 rather than being deleted"

## Task 6 — Add the bad-fix re-check rule to the reviewer-discipline SSOT

- **Description**: Append a new rule R4 to `loom-code/scripts/_reviewer-discipline.md`: on a re-review, verify the region changed by the previous round's fix **before** re-sweeping the artifact; and when the same defect *type* appears a second time, sweep the population rather than the named instance. Write it as **labelled sub-bullets — action / consequence / boundary** — never one long run-on. Name the mechanism **bad-fix injection**; do **not** name it after Fagan (`docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md:284` records why). Then run `python3 loom-code/scripts/distribute.py` and commit the regenerated injected blocks in all three reviewer agents unmodified.
- **Module**: `loom-code/scripts/_reviewer-discipline.md`
- **Files touched**: `loom-code/scripts/_reviewer-discipline.md`, `loom-code/agents/code-reviewer.md`, `loom-code/agents/code-quality-reviewer.md`, `loom-code/agents/spec-reviewer.md`, `loom-code/scripts/test_reviewer_discipline_bad_fix.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/_reviewer-discipline.md`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/distribute.py`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/scripts/verify-drift.py`
- **Acceptance**:
  - **RED**: `test_reviewer_discipline_bad_fix.py::test_r4_present_in_all_three_reviewer_agents` — asserts R4's three labelled sub-bullets appear inside each agent's `BEGIN/END reviewer-discipline-v1` block, and that the string `Fagan` appears nowhere in the rule.
  - **GREEN**: the test passes and `python3 loom-code/scripts/verify-drift.py` exits 0 (all three injected blocks byte-match the SSOT).
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "A new rule in `loom-code/scripts/_reviewer-discipline.md`: on a re-review, verify the region changed by the previous round's fix before re-sweeping the artifact … Regenerated into the three reviewer agents via `distribute.py`; no new file"

## Task 7 — Bump loom-code to 0.41.0 with a CHANGELOG entry

- **Description**: Bump `loom-code/.claude-plugin/plugin.json` `version` from `0.40.0` to `0.41.0` and add a matching `## [0.41.0]` CHANGELOG entry describing the ledger, the round discipline, and the bad-fix re-check. State in the entry that **no numeric round cap ships** and that the bad-fix-injection phenomenon has **no published like-for-like industry measurement** (brief §"The bad-fix injection baseline: honestly unmeasured"). Do **not** write a test count into the entry — that is stamped at close-out.
- **Module**: `loom-code/.claude-plugin/plugin.json`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`, `loom-code/CHANGELOG.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/.claude-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/loom-code/CHANGELOG.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/memory/version-bump-packets-must-name-changelog-entry.md`
  - `/Users/kouko/GitHub/monkey-skills/docs/loom/memory/stamp-changelog-test-counts-at-closeout.md`
- **Acceptance**:
  - **RED**: a test asserting `plugin.json` reads `0.41.0` **and** that `CHANGELOG.md` contains a `## [0.41.0]` heading — read from the **working tree**, not from a committed blob (`docs/loom/BACKLOG.md` item 2 records that a committed-blob GREEN is unsatisfiable by an implementer, which is forbidden from committing).
  - **GREEN**: the test passes; no test count appears in the new entry.
- **Dependencies**: Tasks 3, 4, 5, 6 complete first
- **Independent**: false
- **Brief item covered**: Repo convention required by every content change to a plugin — `docs/loom/memory/version-bump-packets-must-name-changelog-entry.md`; the brief's Decision ships a loom-code behaviour change, which cannot reach the marketplace without a bump.

## Task 8 — Mirror the version bump into the Codex manifest

- **Description**: Run `python3 scripts/sync_codex_manifests.py loom-code` and commit `loom-code/.codex-plugin/plugin.json` unmodified. No hand-written edits to the script's output.
- **Module**: `loom-code/.codex-plugin/plugin.json`
- **Files touched**: `loom-code/.codex-plugin/plugin.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/loom-code/.codex-plugin/plugin.json`
  - `/Users/kouko/GitHub/monkey-skills/scripts/sync_codex_manifests.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_sync_codex_manifest.py::test_loom_code_codex_manifest_in_sync_via_shared_engine` fails — the Codex manifest still reads `0.40.0` while `plugin.json` reads `0.41.0`.
  - **GREEN**: the same test passes.
- **Dependencies**: Task 7 completes first
- **Independent**: false
- **Review-weight**: mechanical
- **Brief item covered**: Same repo convention as Task 7 — the Codex manifest mirror is the second half of a plugin version bump.

## Notes

### Pinned wording — transcribe VERBATIM, never from each other

Tasks 4 and 5 must ship the same rule in two files. Both transcribe from **this pin**, never from each other and never re-derived (`docs/loom/memory/pin-shared-wording-in-plan-copies-transcribe-from-pin.md`). Reviewers verify each copy character-level against the pin.

**Pinned trajectory command** (both tasks quote this exact string):

```
python3 <plugin-root>/scripts/loom_gate_markers.py review-pass --verdict-file <file>
```

**Pinned rule text**:

> From the third review round on this branch, the marker command prints a round trajectory to stderr — surface it to the user instead of digesting the round silently, and state which reading applies: **editorial** (the fixes are sound; more defects remain) or **structural** (the artifact's shape is generating them). Classify the trajectory as fast-converging, converging, stalling, oscillating, or diverging, and escalate to the user when you judge it non-converging — **there is no round-count cap; the judgment is the trigger.** From round 1 onward, a finding against settled narrative prose is **recorded, not rewritten**: append a correction that names what it supersedes rather than editing the passage in place.

### Change-folder binding

No loom-spec change-folder is bound. Branch `feat-review-round-ledger` matches no `docs/loom/<change-id>` slug (layer i miss, silent per contract); layer (ii) finds two non-archived folders — `2026-07-12-us-sec-primary-source-layer` and `2026-07-19-8k-prose-kpi-intake` — both belonging to other arcs and read-only to this work. Input is the brainstorming brief. `check_scenario_coverage.py` is therefore **N/A** (no change-folder to check against), stated rather than skipped silently.

### Dropped from v1 during planning — `arm_overlap`

The brief's ledger schema listed `arm_overlap` (the two panel arms' shared-finding count) as an independence diagnostic. **It is not derivable at the call site**: `requesting-code-review/SKILL.md:100` has the orchestrator union both arms *before* writing the verdict file, so the file the script reads contains the union only — the overlap count is computed and discarded upstream. Recording it would require either a new orchestrator obligation (a `--arm-overlap N` flag, prose-enforced, exactly the failure mode this slice exists to avoid) or a change to the verdict-text schema (wider blast radius than this slice). **Dropped from v1; BACKLOG it** together with the n_eff diagnostic it was meant to feed.

### Ordering and parallelism

- Tasks 1 and 6 are the two level-0 leaves — disjoint `Files touched`, no shared symbol — and run in parallel.
- Tasks 3, 4 and 5 all sit at one level behind Task 2 and run in parallel: Task 3 touches the script, Tasks 4 and 5 touch two different SKILL.md files, and Tasks 4/5 deliberately **point at** the script's output rather than enumerating its columns, so Task 3's column addition creates no doc-mirrors-code edge.
- Tasks 4 and 5 depend on Task 2 (not Task 3) because they reference the trajectory command's existence, which Task 2 ships.
- Task 7 joins everything; Task 8 follows Task 7 because it mirrors Task 7's number.

### Composition constraint (from the brief, must not be lost in implementation)

`review-pass.json` binds **content** (`head_sha` + `patch_id`, fail-closed, read by `git-guard.py`). `review-rounds.json` binds **process** (branch-keyed, never resets). They share the CLI entry point only. The ledger **must not reuse the marker's patch-id binding logic** (`compute_patch_id`, `loom_gate_markers.py:125-158`) and must write a separate file with a separate key. Sharing the call site is composition; sharing the binding would braid two different lifetimes together.

### Standing trap-guards for every implementer dispatch

- `git-guard.py` reads only `review-pass.json` / `verified.json` / `waiver.json` and never globs the marker directory (`git-guard.py:22-48`), so the new fourth file is inert to the push gate. Do not add it to the gate.
- Read a file before you Edit it. On a modified-since-read error, re-Read then re-Edit — never retry the same diff.
- If a guard or hook blocks the same command twice, stop and report the block message verbatim; do not try a third time.
- Clean `loom-code/scripts/__pycache__` before editing skill folders — it trips the skill-folder-structure hook.

## Decision Log

1. chose to derive the bad-fix numbers from git history rather than from the reviewer's own report because a number an agent types about its own work is not evidence — cost-of-change: the day you want a signal git cannot see (for example which findings a human dismissed as noise), this choice costs a new caller-supplied field and the prose obligation to fill it honestly
2. chose to ship no round-count cap because every number considered was a guess and the trajectory print plus human judgment already covers the job — cost-of-change: the day you want unattended runs to stop themselves with no human present, this choice costs a cap plus the evidence to defend whatever number you pick
3. chose to record the round history rather than to pick the best round automatically because published work reframes "which round is best" as the open problem while "when to stop" is the easy one — cost-of-change: the day you want automatic rollback to the best round, this choice costs the selection rule nobody has yet demonstrated
