---
name: cross-plugin-guard-tests-need-foreign-carrier-trigger-paths
description: A repo-level guard test asserting invariants over files in OTHER plugins is fail-open until the running workflow's paths filter names those foreign carrier files in BOTH pull_request and push trigger blocks — an edit to a foreign carrier alone never fires the guard
type: gotcha
origin: feat-knowledge-triage-v1 (2026-07-18) — bucket-vocabulary drift guard, T5 implementer finding
---

`scripts/test_bucket_vocabulary_consistency.py` pins byte-identity of the
three-bucket pin blocks across loom-code, loom-spec, and the plan doc, and
runs in `loom-code-ci.yml` (whose pytest line covers repo-root `scripts/`).
But that workflow's `paths:` filter originally listed only `loom-code/**` +
`scripts/**` + `docs/loom/**` — so a PR editing ONLY
`loom-spec/.../domain-tag-triage.md` or
`loom-discovery/.../evidence-template.md` would merge without the drift
guard ever running (fail-open). The per-plugin workflows can't catch it
either: they run only their own plugin's `scripts/` dir.

**Why:** cross-plugin invariants live in ONE physical test inside ONE
workflow, but the files they guard change under OTHER workflows' path
scopes. Path-filtered CI turns that into a silent coverage hole exactly on
the drift the guard exists to catch.

**How to apply:** when adding a repo-level guard test that reads files
outside the hosting workflow's path scope, add each foreign carrier file's
exact path to that workflow's `paths:` filter — in BOTH the `pull_request`
and `push` trigger blocks — with a comment naming the guard that needs it.
Verify by asking: "if only the foreign file changed, which workflow runs
this test?" — the answer must not be "none".
