# Plan: mechanical-lane suite gate + worktree-reviewer dispatch guidance

Source brief: docs/loom/specs/2026-08-04-mechanical-lane-suite-gate.md
Total tasks: 3
Critical-path depth: 2 (T1/T2 → T3)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-04, round 2, 15/15)

## Task 1 — mechanical self-check part 3: suite green

- Description: In `loom-code/skills/subagent-driven-development/SKILL.md`
  §Mechanical review-weight exemption: (a) change `a deterministic
  **self-check** with two concrete parts, both required:` to `a
  deterministic **self-check** with three concrete parts, all required:`;
  (b) after the `2. **Scope match.**` item, insert this item verbatim:
  `3. **Suite green.** Run the resolved package test command after the
  task's commit; any failure fails the self-check — a mechanical edit can
  redden a file no task touches (live case: a version bump vs the
  shipping-version pin test).`; (c) change `Both parts passing resolves
  the task` to `All three parts passing resolves the task` and `Either
  part failing (content absent, extra files touched, or any ambiguity` to
  `Any part failing (content absent, extra files touched, a red suite, or
  any ambiguity`. Add a prose-pin pytest (new file
  `loom-code/scripts/test_sdd_mechanical_suite_gate.py`) asserting, after
  whitespace-normalizing both sides: the part-3 sentence present, `all
  required:` present, `both required:` absent, AND the file's word count
  ≤ 4500 (the file is at 4435 — the insertion must stay within budget;
  trim is NOT authorized, the pinned wording above fits).
- Module: loom-code/skills/subagent-driven-development/SKILL.md
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md, loom-code/scripts/test_sdd_mechanical_suite_gate.py
- Context paths:
  - loom-code/skills/subagent-driven-development/SKILL.md (§Mechanical review-weight exemption, lines 81-88)
- Acceptance:
  - RED: the new pytest fails before the edit (pinned part-3 sentence
    absent; pair with the positive fact that `2. **Scope match.**` is
    already present so the test cannot pass vacuously on a wrong path).
  - GREEN: pytest passes; `python3 scripts/check-skill-structure.py`
    reports no CHK-SKL-010 violation for loom-code.
- Dependencies: none
- Independent: true
- Brief item covered: "The mechanical self-check gains a third required part" (Decision 1)

## Task 2 — worktree-reviewer dispatch guidance section

- Description: In
  `loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md`,
  insert a new `## Worktree-isolated reviewer dispatch` section directly
  before `## Worked example — the built-in /recap style is the target`,
  containing exactly three guidance points as a bullet list, each led by
  a bolded key phrase: (1) **The worktree may be detached at the
  default-branch tip** — when the orchestrator's working tree holds the
  branch under review, `isolation: worktree` cannot check it out again;
  the dispatch packet must tell the reviewer to address the artifact via
  `git show <branch>:<path>` / `git show <sha>` (shared object DB) and
  never assume the checked-out HEAD is the artifact. (2) **Name known
  environmental test failures in the packet** — suite runs from flat
  extracted copies or foreign checkouts produce failures the branch did
  not cause (live: `test_codex_git_guard_shim.py` needs a real `.git`);
  listing them once saves every arm independently re-proving them.
  (3) **`standards_version` comes from the REVIEWED BRANCH's manifest**
  (`git show <branch>:loom-code/.claude-plugin/plugin.json`), never the
  worktree's own checkout — a detached worktree stamps the wrong version
  otherwise (live: 0.50.0 stamped on a 0.51.0 branch). Exact prose is the
  implementer's to write from these points; the three bolded key phrases
  above are pinned verbatim. Add a prose-pin pytest (new file
  `loom-code/scripts/test_dispatch_hygiene_worktree_section.py`)
  asserting the section heading and the three bolded key phrases,
  whitespace-normalized.
- Module: loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md
- Files touched: loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md, loom-code/scripts/test_dispatch_hygiene_worktree_section.py
- Context paths:
  - loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md
  - docs/loom/specs/2026-08-04-mechanical-lane-suite-gate.md (§Problem 2 — the live evidence the prose should cite)
- Acceptance:
  - RED: the new pytest fails before the edit (heading absent; pair with
    the positive fact that the `## Capacity-error recovery` heading is
    already present).
  - GREEN: pytest passes; existing `test_rcr_capacity_pointer.py` stays
    green (the file's §Capacity-error recovery heading must not move in a
    way that breaks the pointer — it doesn't, the insertion is later in
    the file).
- Dependencies: none
- Independent: true
- Brief item covered: "Worktree-reviewer guidance lives in SDD's references/dispatch-hygiene-notes.md as a new section" (Decision 2)

## Task 3 — loom-code 0.52.0 bump, four deliverables + suite

- Description: Four exact-spec edits practicing the memory entry's
  fourth-deliverable rule: (1) `loom-code/.claude-plugin/plugin.json`
  `"version"` → `"0.52.0"`. (2) `python3 scripts/sync_codex_manifests.py
  loom-code` (SSOT: the Claude manifest), then `--check` clean. (3) In
  `loom-code/scripts/test_docs_review_blocking_class.py`, rewrite the
  shipping-version pin per its own by-design contract: function name
  `test_plugin_version_and_changelog_at_0_51_0` →
  `..._at_0_52_0`, docstring version references and both assert strings
  `0.51.0` → `0.52.0` (`"version": "0.52.0"` / `## [0.52.0]`), replace
  counts asserted before writing. (4) Insert into
  `loom-code/CHANGELOG.md` directly above the `## [0.51.0]` heading, this
  entry verbatim:

  ```markdown
  ## [0.52.0] — 2026-08-04 — the mechanical lane runs the suite, and worktree reviewers get told where they are

  ### Added

  - **Mechanical self-check part 3: suite green.** `Review-weight:
    mechanical` skipped both reviewers and checked only content + scope,
    so nothing between a task's commit and the whole-branch review ran
    the package suite — the 0.51.0 bump shipped a red tip that only the
    panel caught (the shipping-version pin test lived in a file no task
    touched). The self-check now also runs the resolved package test
    command after the commit; any failure falls back to the full triad.
  - **`dispatch-hygiene-notes.md` §Worktree-isolated reviewer dispatch.**
    A worktree dispatch can land detached at the default-branch tip when
    the orchestrator's tree holds the branch; the new section tells
    packet authors to route reviewers through `git show`, to name known
    environmental test failures once instead of letting every arm
    re-prove them, and to stamp `standards_version` from the reviewed
    branch's manifest, not the worktree's.
  ```

  Then run the FULL suite (`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest
  loom-code/scripts/ scripts/ .claude/hooks/ -q`) after the commit and
  report the tail line (practicing Task 1's rule), and verify
  `python3 scripts/check_version_bump.py --base origin/main --head HEAD`
  exits 0.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (top entry for format)
  - loom-code/scripts/test_docs_review_blocking_class.py (lines 198-227)
  - docs/loom/memory/version-bump-packets-must-name-changelog-entry.md (the four-deliverable rule)
- Acceptance:
  - RED: `check_version_bump.py --base origin/main --head HEAD` fails
    while loom-code content commits exist without the bump; pin test
    still asserts 0.51.0.
  - GREEN: `check_version_bump.py` exit 0; pin test asserts 0.52.0 and
    passes; full suite green post-commit (tail line reported).
- Review-weight: mechanical
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "Plugin bump 0.51.0 → 0.52.0 with all FOUR deliverables" (Decision 3)

## Notes

- No backlog entries by Decision 4 — the fix ships in this arc.
- Tasks 1 and 2 both author a new pytest (logic work) — neither claims a
  Review-weight; the full triad runs for both. Only Task 3 (bounded
  literal substitution, quoted CHANGELOG, named sync invocation + SSOT)
  takes the mechanical lane.
- Orchestrator trap-guards ride every dispatch packet: Read before Edit;
  modified-since-read → re-Read; guard blocks twice → stop and report;
  stage only own files, pathspec-form commit if foreign staged paths;
  conventional commits with scope; the two footer lines.
