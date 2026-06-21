# Plan: git-memory squash-merge retrieval caveat

Source brief: docs/loom/specs/2026-05-31-git-memory-squash-retrieval-caveat.md
Total tasks: 2   ← uncapped; width is fine
Critical-path depth: 2 (≤5)   ← T1 → T2
Execution order: sequential (Task 2 after Task 1)
Plan-document-reviewer verdict: PASS (2026-05-31, 14/14; RED verified genuinely RED on live file)

## Task 1 — SKILL.md Pillar 2: squash-merge retrieval caveat
- Description: Edit `dev-workflow/skills/git-memory/SKILL.md` Pillar 2 (lines ~67-90) to add
  a **squash-merge caveat** correcting the `%(trailers)` over-claim. Add (as a note/bullet):
  in a **squash-merge repo**, per-commit trailers are concatenated into the squash commit's
  mid-body, so `%(trailers)` / `git interpret-trailers --parse` are **unreliable on the
  default branch** (they read only the footer); `git log --grep='^Decision:'` (text match)
  still works on main, so the squash-robust retrieval path is **`git log --grep` + the PR
  `## Memory` section** (GitHub-hosted). `%(trailers)` structured parse is reliable on the
  **feature branch** and in **merge-commit / rebase-merge** repos. Name two opt-in escape
  hatches for parseable-trailers-on-main: (a) set `squash_merge_commit_message = PR_BODY`
  and end the PR body with the raw trailer footer; (b) merge-commit (not squash)
  memory-worthy PRs. Lightly qualify the "Every git hosting platform preserves trailers"
  line (true for rendering / non-squash; squash relocates them mid-body). Keep the existing
  `%(trailers)` + `git log --grep` claims (now caveated, not deleted).
- Module: dev-workflow/skills/git-memory/SKILL.md
- Files touched: dev-workflow/skills/git-memory/SKILL.md
- Context paths:
  - docs/loom/specs/2026-05-31-git-memory-squash-retrieval-caveat.md
  - dev-workflow/skills/git-memory/SKILL.md
- Acceptance:
  - RED: `grep -ciE "squash[- ]merge|squash commit|%\(trailers\).{0,40}unreliab|grep.{0,40}squash" SKILL.md` returns 0 (no squash caveat present).
  - GREEN: a squash-merge caveat present in/near Pillar 2 — names that `%(trailers)` is
    unreliable on the default branch in a squash repo, that `git log --grep` + PR `## Memory`
    is the squash-robust path, and the two opt-in escape hatches (squash=PR_BODY +
    PR-footer trailers; merge-commit for memory-worthy PRs); the "every platform preserves"
    line qualified; the existing `%(trailers)` / `git log --grep` claims still present (now
    caveated, not removed); SKILL.md body within ~6,000-token budget (`wc -w`);
    validate-skill-folder hook clean.
- Dependencies: none
- Independent: false  # only one content task in this wave
- Brief item covered: Smallest End State (squash-merge caveat + grep/PR-Memory retrieval path
  + 2 escape hatches + qualify "every platform preserves") + §Decision.

## Task 2 — dev-workflow version bump 2.14.0 → 2.14.1 + CHANGELOG
- Description: Bump dev-workflow plugin.json 2.14.0 → 2.14.1 (patch — doc accuracy
  correction, no behavior change; confirm current version) and add a CHANGELOG entry
  describing the git-memory squash-merge retrieval caveat: `%(trailers)` structured parse
  is unreliable on a squash-merge default branch (trailers buried mid-body); the
  squash-robust retrieval path is `git log --grep` + PR `## Memory`; two opt-in escape
  hatches named. Note it's a doc correction of a Pillar-2 over-claim, no behavior change.
  Sync marketplace.json only if it carries the dev-workflow version (it does not). No backfill.
- Module: release metadata (dev-workflow plugin manifest + changelog)
- Files touched: dev-workflow/.claude-plugin/plugin.json, dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/.claude-plugin/plugin.json
  - dev-workflow/CHANGELOG.md
  - docs/loom/specs/2026-05-31-git-memory-squash-retrieval-caveat.md
- Acceptance:
  - RED: plugin.json version still 2.14.0; no new CHANGELOG entry.
  - GREEN: plugin.json version 2.14.1 (valid JSON via `python3 -m json.tool`); CHANGELOG
    entry naming the squash-merge caveat + grep/PR-Memory retrieval path + escape hatches +
    "doc correction, no behavior change".
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Open Question 1 (dev-workflow patch 2.14.0 → 2.14.1).

## Notes
- Target = dev-workflow (git-memory is a dev-workflow skill); version bump on dev-workflow manifest.
- 2 tasks, sequential (T2 names what T1 changed). Critical-path depth = 2.
- Doc-only skill: no pytest; acceptance = grep-diagnostic + validate-skill-folder hook +
  token budget.
- This is a doc-accuracy correction (qualify an over-claim) — same shape as code-toolkit
  PR #357 (depth-grounding correction). No behavior/config/workflow change; the escape
  hatches are documented as opt-in, not applied.
