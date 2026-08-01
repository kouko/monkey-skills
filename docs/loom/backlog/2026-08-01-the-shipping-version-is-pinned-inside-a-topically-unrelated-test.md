---
name: 2026-08-01-the-shipping-version-is-pinned-inside-a-topically-unrelated-test
description: The shipping version is pinned inside a topically unrelated test
status: OPEN
origin: PR #629 (docs-review standalone skill), carried forward through three subsequent bumps.
start: the next version bump that has to edit this file, if the edit is ever missed or lands in the wrong file.
---

- Start: the next version bump that has to edit this file, if the edit is ever
  missed or lands in the wrong file.
- Origin: PR #629 (docs-review standalone skill), carried forward through three
  subsequent bumps.
- What: `loom-code/scripts/test_docs_review_blocking_class.py:200` defines
  `test_plugin_version_and_changelog_at_0_42_4`, pinning `"version": "0.42.4"`
  and the matching `## [0.42.4]` CHANGELOG heading. **The pin itself is
  deliberate and correct** — its docstring states the purpose plainly: tracking
  the current shipping version is what makes a missing bump fail CI instead of
  shipping a silent marketplace no-op — the same failure
  `docs/loom/memory/version-bump-packets-must-name-changelog-entry.md` records
  from the packet side.
- The cost is **placement, not the pin**: the file is about the docs-review
  blocking class, so every bump forces an edit to a file about something else,
  and the version number is baked into the test's own name (already rewritten
  four times — the supersede chain is in its docstring). A plugin-version guard
  belongs in a file named for that job.
- Do not "fix" this by loosening the assertion to a regex — the exact-version
  pin is the mechanism. Move it; do not weaken it.
