---
name: leading-at-req-comment-trips-living-spec-checker
description: A test-file comment whose FIRST token is `@req` (e.g. `# @req omitted — see docstring`) is parsed by loom-code's living-spec checker as a REQ-id tag declaration and FAILS the CI structural check as a MALFORMED tag — word any "no req-id here" note without a leading @req token; the check is CI-only (check-living-spec-index.py .), not the package pytest, so a green local suite misses it
type: gotcha
origin: feat-8k-earnings-kpi-intake CI fix (loom-code living-spec gate, 2026-07-19, PR #590)
---

`loom-code/scripts/check-living-spec-index.py .` (a loom-code CI step,
distinct from the package pytest) scans every test file for `@req` tags that
bind a test to a living-spec requirement id. It reads a comment line whose
leading token is `@req` as a tag DECLARATION and validates the rest as a
req-id. A note like `# @req omitted — see module docstring` therefore parses
as a malformed declaration ("omitted — …" is not a valid req-id) and the check
exits 1 with `MALFORMED tag:` — one per such comment. Five of these failed
PR #590's `pytest + knowledge-drift + codex-manifest-drift` job while the
package pytest was fully green, because the structural check is a SEPARATE CI
step the local `pytest investing-toolkit/tests/` run never invokes.

**Why:** the checker keys on a LEADING `@req` (a `tokenize`-filter drops `@req`
inside string literals, so the same text in a docstring is fine — only real
comment lines with `@req` as the first token trip it). "I'll note that I
skipped the req tag" using the literal `@req` word reproduces exactly the token
the checker is hunting for.

**How to apply:** to say a test has no living-spec req-id, word it WITHOUT a
leading `@req` token — e.g. `# No living-spec REQ-id: this plan traces by Brief
item, not REQ-ids.` (a mid-line or spelled-out "REQ-id" is safe; only a leading
`@req` declares a tag). And run the CI-only gate locally before pushing —
`python3 loom-code/scripts/check-living-spec-index.py .` (exit 0 = clean) — a
green package pytest does NOT cover it. Same "a CI-only structural scan the
package suite never runs" class as
[[ci-skill-structure-scan-gap-obsidian]].
