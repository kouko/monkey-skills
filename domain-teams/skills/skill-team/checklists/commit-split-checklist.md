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

This gate applies to split-commit workflows (new-skill-creation and
skill-redesign). It does NOT apply to minor single-commit fixes. If
the branch has only 1 commit, return `NOT_APPLICABLE` for every item
and verdict `PASS`.

### Split-mode detection (mandatory first step)

Before evaluating CHK-CMT-001/002/003, detect which split mode applies:

```
git diff --name-only --diff-filter=A main..HEAD -- '**/standards/*.md'
```

The `--diff-filter=A` restricts the check to **added** files. Modify-only
edits to existing standards (e.g., a convention amendment that tweaks
`commit-convention.md` itself) stay in 2-commit mode — only *new*
standards files introduce new grounding and require 3-commit review
isolation.

- **Empty output** → **2-commit variant** applies (refactor adds no
  new `standards/` files). Branch must have exactly 2 commits. Apply
  CHK-CMT items per the "2-commit variant" branch below.
- **Non-empty output** → **canonical 3-commit split** applies. Branch
  must have exactly 3 commits. Apply CHK-CMT items per the "3-commit
  canonical" branch below.

See `standards/commit-convention.md` §2-Commit Variant for the
underlying convention.

## Checklist

- [ ] **CHK-CMT-001 (Commit 1 content)** [FATAL]:
    - **3-commit canonical**: The first commit contains ONLY changes to files under `standards/` of the target team AND optionally the single in-repo research note at `research/grounding-v{X.Y.Z}.md` (per skill-team v4.7.0 research-note convention — the research note is the layer-3 companion to the standards grounding and is inseparable from commit 1 by design). No changes to `protocols/`, `checklists/`, `rubrics/`, `SKILL.md`, router, or `plugin.json`.
    - **2-commit variant**: The first commit (`1/2`) contains ONLY changes to files under `protocols/`, `checklists/`, or `rubrics/` of the target team AND/OR **modifications** (not additions) to existing `standards/*.md` files AND optionally the single in-repo research note at `research/grounding-v{X.Y.Z}.md`. No **new** standards files (adding a new standards file trips detection into 3-commit mode). No `SKILL.md` changes, no router changes, no `plugin.json` changes in this commit.

- [ ] **CHK-CMT-002 (Commit 2 content)** [FATAL]:
    - **3-commit canonical**: The second commit contains ONLY changes to files under `protocols/`, `checklists/`, or `rubrics/` of the target team. No changes to `SKILL.md`, `standards/`, router, or `plugin.json`.
    - **2-commit variant**: The second commit (`2/2`) contains a version bump in `.claude-plugin/plugin.json` AND a new entry in `CHANGELOG.md`. It MUST ALSO contain `SKILL.md` changes for additive MINOR bumps where the new structure needs to be wired into the discovery surface; for modify-only PATCH bumps where wiring is not needed, `SKILL.md` changes are OPTIONAL. It may contain router updates (`using-domain-teams/SKILL.md`) and legacy file deletions. No new content files under standards / protocols / gates in this commit. (This is the equivalent of canonical Commit 3/3 under the 2-commit variant.)

- [ ] **CHK-CMT-003 (Commit 3 content)** [FATAL]:
    - **3-commit canonical**: The third commit contains a version bump in `.claude-plugin/plugin.json` AND a new entry in `CHANGELOG.md`. It MUST ALSO contain `SKILL.md` changes for additive MINOR bumps (grounding refactors, brand-new teams) where the new structure needs to be wired into the discovery surface. For modify-only PATCH bumps where convention clarifications do not require SKILL.md rewiring, `SKILL.md` changes are OPTIONAL. It may contain router updates (`using-domain-teams/SKILL.md`) and legacy file deletions. No new content files under standards / protocols / gates in this commit.
    - **2-commit variant**: Return `NOT_APPLICABLE` — there is no third commit. The content CHK-CMT-003 would check lives in Commit 2/2 and is validated by CHK-CMT-002 (2-commit variant branch) above.

- [ ] **CHK-CMT-004 (Message format)** [FIXABLE]: Every commit message follows `<type>({scope}): <subject> (v<X.Y.Z> <N>/<N>)` with type in {refactor, feat, fix, chore, docs}, scope being the team name, subject in imperative lowercase without trailing period, and the version/position suffix present. The denominator in the suffix matches the detected split mode (`3` for canonical 3-commit split, `2` for the 2-commit variant).

- [ ] **CHK-CMT-005 (Version bump validity)** [FIXABLE]: The version in `plugin.json` in commit 3 is greater than the version in `main` by one of:
    - **MINOR bump** (`x.y.z → x.(y+1).0`) — for **additive** work that introduces new grounded content or new convention infrastructure: grounding refactors, brand-new teams, new standards / protocols / gates, new research-note infrastructure, or backfilled research files. Example precedents: v4.2.0 (qa-team grounding), v4.7.0 (research-note in-repo convention + 3 backfills), v4.8.0 (design-team grounding).
    - **PATCH bump** (`x.y.z → x.y.(z+1)`) — for **modify-only** skill-team convention clarification, policy fixes, or meta-improvement work that does not introduce new files or new grounded content. The scope is "clarify or correct existing standards / checklists / rubrics / protocols". Example precedents: v4.6.1 (CHK-SKL-001 word-count rule + router exemption + tokenization), v4.7.1 (Compact+Admonitions citation policy), v4.7.2 (3-tier classification + ISBN removal).
    - **MAJOR bump** (`(x+1).0.0`) — requires explicit authorization in the PR description; never applied automatically.

    A 3-commit-split branch is valid for either MINOR or PATCH bumps as long as the bump kind matches the nature of the changes. The distinguishing rule: does this branch introduce **new files** that will be read by worker or evaluator agents at runtime? If yes → MINOR. If no (only modifies existing runtime files) → PATCH.

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
