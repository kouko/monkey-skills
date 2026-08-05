# Plan: orchestrator-tree detach hardening + round-3 retro residue

Source brief: docs/loom/specs/2026-08-05-orchestrator-tree-detach-hardening.md
Total tasks: 4
Critical-path depth: 2 (≤5)
Execution order: parallel-where-possible (Wave 1 = T1+T2+T3; T4 after)
Plan-document-reviewer verdict: SKIPPED — the reviewer dispatch was
stopped by the user mid-run (not resumable per harness); under the
user's standing 「直接做」 directive the plan executed inline with
RED-first pins per task, and the whole-branch review remains the
review gate for this arc. Not a PASS; recorded honestly.

## Task 1 — dispatch-hygiene: forbid checkout in the orchestrator's tree

- Description: Append the fourth bullet (pinned verbatim in ## Notes,
  block N1) to `## Worktree-isolated reviewer dispatch` in
  dispatch-hygiene-notes.md, after the `standards_version` bullet and
  before `## Worked example`; extend the existing pin test's
  BOLDED_PHRASES with the new bullet's bolded lead phrase and add one
  assertion that the bullet text names both `git show` and "your OWN
  worktree" (whitespace-normalized, per the file's existing helper).
- Module: loom-code/skills/subagent-driven-development
- Files touched: loom-code/skills/subagent-driven-development/references/dispatch-hygiene-notes.md, loom-code/scripts/test_dispatch_hygiene_worktree_section.py
- Context paths:
  - loom-code/scripts/test_dispatch_hygiene_worktree_section.py (existing pin shapes)
  - docs/loom/memory/absence-pin-fix-recurred-in-files-authored-after-the-fix.md (normalization rules)
- Acceptance:
  - RED: the extended `test_worktree_section_bolded_key_phrases_present`
    (fourth phrase added) fails against the unedited file.
  - GREEN: `pytest loom-code/scripts/test_dispatch_hygiene_worktree_section.py`
    passes after the bullet lands; full package suite green.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 1 ("carries a fourth bullet:
  never `git checkout` / `git switch` in the orchestrator's main working
  tree")

## Task 2 — finishing: attached-HEAD check before the close-out commit

- Description: Insert the attached-HEAD bullet (pinned verbatim in
  ## Notes, block N2) into finishing-a-development-branch/SKILL.md
  Step 8, immediately before the "Run `git status --short`" bullet;
  create `loom-code/scripts/test_finishing_attached_head_check.py`
  pinning (a) a positive-fact control (an existing Step 8 phrase),
  (b) the bullet's lead phrase, (c) the command string
  `git symbolic-ref -q HEAD`, (d) the closing absolute "never commit
  the close-out on a detached HEAD" — all whitespace-normalized
  contiguous matches per the sibling test files' convention (strip
  markup, collapse whitespace, lowercase both sides).
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_attached_head_check.py
- Context paths:
  - loom-code/scripts/test_dispatch_hygiene_worktree_section.py (sibling pin-test shape)
  - loom-code/scripts/test_finishing_step7_privacy_gate.py (sibling naming convention)
- Acceptance:
  - RED: the new test file fails against the unedited SKILL.md (control
    assertion passes, bullet assertions fail — proves non-vacuous).
  - GREEN: `pytest loom-code/scripts/test_finishing_attached_head_check.py`
    passes after the bullet lands; SKILL.md stays ≤4500 words by
    `len(text.split())` (current 3699 + ~60).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 2 ("attached-HEAD check bullet
  ... detached → STOP and reattach, never commit detached")

## Task 3 — memory store: two new entries + third variant on the existing entry

- Description: (a) Write
  `docs/loom/memory/a-brief-level-obligation-needs-a-named-deliverable-in-each-partition.md`
  and `docs/loom/memory/name-the-word-count-convention-when-citing-a-count.md`
  per the store's format fence (frontmatter name/description/type/origin;
  body fact + **Why:** + **How to apply:**), content grounded in the
  brief's Problem section; (b) append a dated third-variant paragraph to
  `reviewer-dispatch-isolated-worktree.md` (isolation ordered AND granted,
  agent still ran checkout in the main tree via the packet's absolute
  paths, close-out commit landed detached; the fix now lives in the
  dispatch-hygiene fourth bullet and finishing's attached-HEAD gate —
  cite both paths); (c) add the two index lines to
  `docs/loom/memory/README.md` §Index, descriptions byte-identical to
  frontmatter; existing entry's description unchanged (rule text still
  true).
- Module: docs/loom/memory
- Files touched: docs/loom/memory/a-brief-level-obligation-needs-a-named-deliverable-in-each-partition.md, docs/loom/memory/name-the-word-count-convention-when-citing-a-count.md, docs/loom/memory/reviewer-dispatch-isolated-worktree.md, docs/loom/memory/README.md
- Context paths:
  - docs/loom/memory/README.md (format fence + index format)
  - docs/loom/specs/2026-08-05-orchestrator-tree-detach-hardening.md (facts)
- Acceptance:
  - RED: `python3 scripts/check_loom_memory_integrity.py` currently
    cannot fail for the new entries (they do not exist) — the RED
    diagnostic is the checker run AFTER writing the entry files but
    BEFORE adding index lines (must exit nonzero naming the missing
    index lines).
  - GREEN: checker exits 0 with both new files indexed byte-identical.
- Dependencies: none
- Independent: true
- Review-weight: prose
- Brief item covered: Smallest End State 3 ("two new entries ... and
  `reviewer-dispatch-isolated-worktree.md` gains the third variant")

## Task 4 — bump 0.56.0 + CHANGELOG + shipping-version pin

- Description: Set `"version": "0.56.0"` in
  loom-code/.claude-plugin/plugin.json and loom-code/.codex-plugin/plugin.json;
  prepend the CHANGELOG entry pinned verbatim in ## Notes, block N3;
  rewrite `test_plugin_version_and_changelog_at_0_55_0` in
  test_docs_review_blocking_class.py to
  `test_plugin_version_and_changelog_at_0_56_0` (same shape, strings
  0.55.0 → 0.56.0 in name, docstring, both assertions and their
  messages).
- Module: loom-code (manifests + changelog)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (entry format, 0.55.0 head)
  - loom-code/scripts/test_docs_review_blocking_class.py:200-226 (current pin)
- Acceptance:
  - RED: the rewritten version-pin test fails before the manifests and
    CHANGELOG are edited.
  - GREEN: full package suite `pytest loom-code/scripts/` passes with the
    bump landed.
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Review-weight: mechanical
- Brief item covered: Smallest End State 4 ("bumps to 0.56.0 with a
  CHANGELOG entry; the shipping-version pin test moves to 0.56.0")

## Notes

Kickoff decision: no one-way doors — all edits are additive prose +
manifest bumps; below-threshold decisions log here.

Counting convention (this arc): `len(text.split())`, per brief Decisions.

**Pinned canonical texts — transcribe VERBATIM, never re-derive**
(pin-shared-wording-in-plan-copies-transcribe-from-pin):

N1 — dispatch-hygiene fourth bullet:

```markdown
- **Never `git checkout` / `git switch` in the orchestrator's main
  working tree** — the dispatch packet names absolute paths under the
  main repo, so a worktree-isolated agent can still run git there and
  detach the tree the orchestrator is about to commit on (live: a
  close-out commit landed on a detached HEAD this way). Read other
  revisions via `git show`; run anything that needs a different
  checkout inside your OWN worktree. The main tree's checkout state
  belongs to the orchestrator alone.
```

N2 — finishing Step 8 attached-HEAD bullet:

```markdown
   - Attached-HEAD check: run `git symbolic-ref -q HEAD` in the main
     working tree — it must print the branch being finished. Detached
     HEAD or a different branch means something (typically a subagent)
     moved this tree mid-flight; STOP, reattach (`git checkout <branch>`,
     fast-forwarding any commits that already landed detached), and only
     then commit — never commit the close-out on a detached HEAD.
```

N3 — CHANGELOG entry (prepend under the format header, above [0.55.0]):

```markdown
## [0.56.0] — 2026-08-05 — the orchestrator's tree is nobody else's checkout

### Added

- **Worktree dispatch guidance forbids touching the orchestrator's
  checkout.** A fourth bullet in dispatch-hygiene's worktree section:
  never `git checkout` / `git switch` in the orchestrator's main
  working tree — the dispatch packet's absolute paths reach it, and a
  reviewer arm detached it mid-arc (the 0.55.0 close-out commit landed
  on a detached HEAD). Read via `git show`, execute in your own
  worktree.
- **Finishing gains a mechanical attached-HEAD gate.** Step 8 now
  requires `git symbolic-ref -q HEAD` to resolve to the branch being
  finished before the close-out commit — the backstop that turns the
  prose rule's failure mode from a silent detached commit into a loud
  STOP. Both surfaces pin-tested.
```

## Decision Log

- 2026-08-05: T2 places the bullet before `git status --short` (brief
  Decisions); T4's CHANGELOG heading date uses today's date — both
  below-threshold, logged not asked.
- 2026-08-05 erratum (whole-branch round 1, docs arm): T2's
  parenthetical "strip markup, collapse whitespace, lowercase both
  sides" over-describes the shipped normalization — the sibling test
  files split on lowercasing, and the shipped
  test_finishing_attached_head_check.py only collapses whitespace
  (stricter than planned, RED-verified). The shipped test is the
  convention of record.
