# Plan: git-memory P1+P2 — merge-gate trigger + verified substrate survival

Source brief: docs/loom/specs/2026-06-22-git-memory-merge-gate-and-verified-survival.md
Evidence: docs/skill-mining/2026-06-22-git-memory-findings.md §4b
Total tasks: 6 (width OK; 2 parallel leaves at level 1, 2 parallel leaves at the final level)
Critical-path depth: 3 (≤5) — longest chain: Task 2 → Task 3 → Task 5a/5b
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-22, round 2 — Task 5 split into 5a/5b per round-1 Check 4; 14/14 applicable checks)

## Notes

- All paths relative to repo root `/Users/kouko/.supacode/repos/monkey-skills/git-memory-r2`.
- git-memory is **not** under any sync/distribute/drift gate (brief Current State Evidence,
  Reverse) — edits are house-local, no SSOT mirror to update.
- Prose tasks (1, 3, 4) use a **RED grep diagnostic** (exact command, expected exit) rather
  than a committed test — the repo pattern for doc-convention edits. Only Task 2 (real code)
  ships a committed bash test, scoped to itself to avoid cross-task test-file coupling.
- Bash test convention: plain self-checking `bash` harness with `pass()/fail()` + exit-code
  summary, mirroring `loom-code/tests/integration/test-git-memory-delegation.sh`.
- Parallelism rationale (round-1 Check-15 advisory, not applied): Task 4 shares `SKILL.md`
  with Task 1, so Task 4 must stay `Independent: false` (marking it true would create an
  Independent-pair with overlapping `Files touched` — a Check-14 error). Task 3 and Task 4
  therefore cannot both run parallel; the serialization stands. Tasks 5a/5b ARE a valid final
  parallel pair (disjoint files, no semantic dep between them).
- `--verify` scope decision: the unit-testable core checks the **commit carrier** locally
  (grep the commit body for `^Decision:|^Learning:|^Gotcha:`, which survives squash mid-body
  under the repo's `COMMIT_MESSAGES` setting). The **PR `## Memory` carrier** check reuses the
  script's existing `gh pr` extraction and is exercised by the orchestrator at PR time, not by
  the offline unit test (network/`gh`-dependent). Dual-carrier *requirement* lives in
  compose-pr.md prose (Task 3); the deterministic *retrievability check* is `--verify` (Task 2).

## Task 1 — P1: add merge to git-memory's trigger surface

- Description: Edit `SKILL.md` so the gate's trigger surface includes `gh pr merge` (esp.
  `--squash`). Update (a) the `description:` frontmatter line and (b) the §Invocation policy
  table so merge is listed as a moment the gate must fire — it is the last checkpoint before
  memory can be lost. Keep the "always invoke, trailer outcome may be empty" framing intact.
- Module: dev-workflow/skills/git-memory/SKILL.md
- Files touched: dev-workflow/skills/git-memory/SKILL.md
- Context paths:
  - dev-workflow/skills/git-memory/SKILL.md (lines 4, 12-32 — description + §Invocation policy)
- Acceptance:
  - RED: `grep -iE 'gh pr merge|pr merge' dev-workflow/skills/git-memory/SKILL.md` → no match
    (exit 1) in the description block and §Invocation policy section today.
  - GREEN: both the `description:` line and the §Invocation policy section name `gh pr merge`
    as a gate trigger; `grep -c 'gh pr merge'` ≥ 2.
- Dependencies: none
- Independent: true
- Brief item covered: "P1 — extend the gate's trigger surface to include merge … the gate
  fires before every git commit / `gh pr create` / `gh pr merge`."

## Task 2 — P2a: add `--verify <ref>` mode to memory-grep.sh (+ committed test)

- Description: Add a `--verify <ref>` flag to `scripts/memory-grep.sh`. It resolves the ref,
  greps that commit's full message body for `^(Decision|Learning|Gotcha):` (text match — works
  on squash mid-body), and exits **0** if any memory trailer is present, **4** if absent
  (new exit code: "memory-worthy check requested but no memory found"). Update the usage block
  and exit-code header comment. Add a committed self-checking bash test that creates a temp
  git repo with one trailer-bearing commit and one bare commit, and asserts `--verify` exits 0
  vs 4 respectively, plus exit 1 on missing ref arg.
- Module: dev-workflow/skills/git-memory/scripts/memory-grep.sh
- Files touched: dev-workflow/skills/git-memory/scripts/memory-grep.sh, dev-workflow/tests/test-memory-grep-verify.sh
- Context paths:
  - dev-workflow/skills/git-memory/scripts/memory-grep.sh (arg `case` block ~line 101-109,
    exit-code header ~35-39, usage ~52-74)
  - loom-code/tests/integration/test-git-memory-delegation.sh (harness style to mirror)
- Acceptance:
  - RED: `bash dev-workflow/tests/test-memory-grep-verify.sh` fails — `--verify` is an unknown
    arg today (exits 1 via the `*)` case), so the "trailer commit → exit 0" assertion fails.
  - GREEN: the test passes — `--verify <trailer-commit>` exits 0, `--verify <bare-commit>`
    exits 4, `--verify` with no ref exits 1 (usage error). `bash -n` clean; `shellcheck`
    clean if available.
- External surfaces: `git` CLI (`git log`, `git rev-parse`) — already used throughout
  memory-grep.sh; no new external dependency.
- Runnable-capability: the new test is runnable via
  `bash dev-workflow/tests/test-memory-grep-verify.sh`; declare this invocation in
  dev-workflow's command surface (AGENTS.md test section if present, else a one-line note in
  `dev-workflow/CHANGELOG.md` under the version entry) so the new test verb is not silent.
- Dependencies: none
- Independent: true
- Brief item covered: "Verify step (the key lever) … Add a verify mode to
  scripts/memory-grep.sh (e.g. --verify <ref> → non-zero exit if a memory-worthy ref/PR yields
  no memory)."

## Task 3 — P2b: compose-pr.md — `## Memory` required for memory-worthy PRs + reference verify

- Description: Edit `protocols/compose-pr.md` so that for a **memory-worthy** PR (the Step-2
  filter), the `## Memory` section is **required**, not optional — keep the "skip entirely"
  guidance only for non-memory-worthy PRs. Add a closing step pointing the orchestrator to run
  `memory-grep.sh --verify <merge-commit>` (commit carrier) and confirm the PR body carries
  `## Memory` (PR carrier) before the branch closes, treating an empty result as a flag.
- Module: dev-workflow/skills/git-memory/protocols/compose-pr.md
- Files touched: dev-workflow/skills/git-memory/protocols/compose-pr.md
- Context paths:
  - dev-workflow/skills/git-memory/protocols/compose-pr.md (Step 2 lines 24-39; "When to skip"
    lines 160-168; Step 6 lines 170-179)
- Acceptance:
  - RED: `grep -iE 'required|must' dev-workflow/skills/git-memory/protocols/compose-pr.md` near
    the memory-worthy filter → today the section is framed "optional / skip if none apply"
    (no required-for-memory-worthy statement; grep for the required-framing returns no match).
  - GREEN: compose-pr.md states `## Memory` is required for memory-worthy PRs AND references
    `memory-grep.sh --verify` as the pre-close retrievability check; both phrases grep-present.
- Dependencies: Task 2 completes first (doc references the `--verify` capability — semantic
  doc-mirrors-code dependency; must land after the flag exists).
- Independent: false
- Brief item covered: "protocols/compose-pr.md: `## Memory` becomes required for memory-worthy
  PRs … keep optional for non-memory-worthy."

## Task 4 — P2c: SKILL.md Pillar 2 — verify-required upgrade, footer-setting stays opt-in

- Description: Edit `SKILL.md` Pillar 2 (the squash caveat + "two opt-in escape hatches", lines
  ~77-101) so the **verification** of a memory-worthy PR's substrate survival is a **required**
  step (cross-referencing `memory-grep.sh --verify` and compose-pr.md), while the
  `squash_merge_commit_message = PR_BODY` / merge-commit settings remain **genuinely opt-in**
  (only needed for `%(trailers)` footer-parse, which is not required — `git log --grep` text
  retrieval is the supported path). Do not delete the caveat; tighten it.
- Module: dev-workflow/skills/git-memory/SKILL.md
- Files touched: dev-workflow/skills/git-memory/SKILL.md
- Context paths:
  - dev-workflow/skills/git-memory/SKILL.md (Pillar 2 lines 77-101)
- Acceptance:
  - RED: `grep -iE 'verify|--verify' dev-workflow/skills/git-memory/SKILL.md` in Pillar 2 → no
    match today (the escape hatches are "opt-in", no required verification step).
  - GREEN: Pillar 2 names a required verification step referencing `memory-grep.sh --verify`,
    and the footer/merge-commit settings are explicitly labeled opt-in; both grep-present.
- Dependencies: Task 1 completes first (same file — serialize SKILL.md edits to avoid an index
  race; semantic: Task 4's verify prose should sit alongside Task 1's merge-trigger edit).
- Independent: false
- Brief item covered: "SKILL.md Pillar 2 (:93-98): the 'two opt-in escape hatches' prose is
  upgraded — the verification becomes a required step for memory-worthy PRs; the PR_BODY repo
  setting stays genuinely opt-in."

## Task 5a — bump dev-workflow plugin version (minor)

- Description: Increment `dev-workflow/plugin.json` version by a minor bump (new `--verify`
  behavior + trigger-surface change, per brief Open Q1). Single-field edit.
- Module: dev-workflow/plugin.json
- Files touched: dev-workflow/plugin.json
- Context paths:
  - dev-workflow/plugin.json (current `version` field)
- Acceptance:
  - RED: `plugin.json` version is unchanged from the pre-change value (grep for the intended
    new minor version string → no match).
  - GREEN: `version` field incremented by a minor; the new version string greps-present in
    `dev-workflow/plugin.json`; file remains valid JSON (`python3 -c 'import json,sys;
    json.load(open("dev-workflow/plugin.json"))'` exits 0).
- Dependencies: Tasks 1, 2, 3, 4 complete first (version reflects the shipped changes).
- Independent: true
- Brief item covered: "Plus a version bump … dev-workflow minor (new --verify behavior +
  trigger-surface change)" (brief §Open Questions Q1, Decision ships P1+P2).

## Task 5b — add dev-workflow CHANGELOG entry

- Description: Add a dated `dev-workflow/CHANGELOG.md` entry summarizing P1 (merge added to the
  git-memory trigger surface) + P2 (verified dual-carrier substrate survival via the new
  `memory-grep.sh --verify` mode + `## Memory` required for memory-worthy PRs). Must name the
  same new version string as Task 5a.
- Module: dev-workflow/CHANGELOG.md
- Files touched: dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/CHANGELOG.md (existing entry format / latest version heading)
- Acceptance:
  - RED: `dev-workflow/CHANGELOG.md` has no entry for this change (grep for the new version
    string / "git-memory" P1+P2 summary → no match).
  - GREEN: CHANGELOG.md has a dated entry under the new version naming P1 + P2; the new version
    string and a `--verify` / merge-trigger mention grep-present.
- Dependencies: Tasks 1, 2, 3, 4 complete first (entry reflects the shipped changes). May run
  parallel with Task 5a (disjoint file, no shared symbol).
- Independent: true
- Brief item covered: "Plus a version bump + CHANGELOG" (brief §Open Questions Q1, Decision
  ships P1+P2).
