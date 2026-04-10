# Commit Split Checklist Gate

## Evaluation Instructions

You are a strict auditor. Check each item below against the git
commit history of the current branch (run `git log --stat` on the
branch vs `main`). For each item, give `PASS`, `FAIL_FIXABLE`, or
`FAIL_FATAL` with specific evidence (commit SHAs + file paths).

The failure type for each item is defined below — use the type
specified.

Grounds on: `standards/commit-convention.md`.

## Scope

This gate applies only to 3-commit-split workflows (new-skill-creation
and skill-redesign). It does NOT apply to minor single-commit fixes.
If the branch has only 1 commit, return `NOT_APPLICABLE` for every
item and verdict `PASS`.

## Checklist

- [ ] **CHK-CMT-001 (Commit 1 content)** [FATAL]: The first commit contains ONLY changes to files under `standards/` of the target team. No changes to `protocols/`, `checklists/`, `rubrics/`, `SKILL.md`, router, or `plugin.json`.

- [ ] **CHK-CMT-002 (Commit 2 content)** [FATAL]: The second commit contains ONLY changes to files under `protocols/`, `checklists/`, or `rubrics/` of the target team. No changes to `SKILL.md`, `standards/`, router, or `plugin.json`.

- [ ] **CHK-CMT-003 (Commit 3 content)** [FATAL]: The third commit contains `SKILL.md` changes AND a version bump in `.claude-plugin/plugin.json`. It may ALSO contain router updates (`using-domain-teams/SKILL.md`) and legacy file deletions. No new content files under standards / protocols / gates in this commit.

- [ ] **CHK-CMT-004 (Message format)** [FIXABLE]: Every commit message follows `<type>({scope}): <subject> (v<X.Y.Z> <N>/3)` with type in {refactor, feat, fix, chore, docs}, scope being the team name, subject in imperative lowercase without trailing period, and the version/position suffix present.

- [ ] **CHK-CMT-005 (Version bump validity)** [FIXABLE]: The version in `plugin.json` in commit 3 is greater than the version in `main` by a MINOR bump (`x.y.0 → x.(y+1).0`) for grounding refactors or brand-new teams. PATCH-only bumps are rejected for 3-commit splits. MAJOR bumps require explicit authorization in the PR description.

- [ ] **CHK-CMT-006 (No fixup / wip)** [FIXABLE]: No commit message contains the words `fixup`, `wip`, `squash`, `amend`, `typo fix`, or similar informal markers. Each commit is a clean, reviewable unit.

- [ ] **CHK-CMT-007 (Co-author)** [FIXABLE]: Every commit message ends with `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` trailer (or equivalent for the model being used).

- [ ] **CHK-CMT-008 (No --no-verify)** [FIXABLE]: No commit was created with `--no-verify`, `--no-gpg-sign`, or similar hook-skip flags. (Check by verifying pre-commit hooks would have run and passed.)

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` → final verdict is `NEEDS_REVISION` (escalate to user — 3-commit structure must be rebuilt)
- Only `FAIL_FIXABLE` items (no FATALs) → final verdict is `PASS_WITH_NOTES` (amend commit messages or re-commit cleanly)
- All items are `PASS` → final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-CMT-001",
      "status": "PASS | FAIL_FIXABLE | FAIL_FATAL | NOT_APPLICABLE",
      "evidence": "Commit SHA + file paths affected",
      "fix_instruction": "How to resolve (for failing items)"
    }
  ]
}
```
