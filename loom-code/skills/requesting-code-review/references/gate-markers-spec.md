# Gate markers spec

Reference for `loom-code/scripts/loom_gate_markers.py` (the marker
writer) and `loom-code/hooks/git-guard.py` (the PreToolUse reader).
Written up per
[`docs/loom/plans/2026-07-06-gate-friction-pack.md`](../../../../docs/loom/plans/2026-07-06-gate-friction-pack.md)
task 6 — the requirements previously lived only in code (discovered by
exit-4 retries); this file is the readable version.

All markers live under `<git-dir>/loom/`, resolved via `git rev-parse
--git-dir` from the target repo.

## Verdict-text schema (`review-pass --verdict-file`)

The reviewer's verdict text (not the marker JSON) must contain:

- `standards_version: <non-empty value>` — a bare `standards_version:`
  with nothing after it counts as missing.
- `verdict: PASS | PASS_WITH_NOTES | NEEDS_REVISION` — any other value
  is rejected outright.
- A `dimension_scores:` block (just the key needs to be present).
- Every `- severity:` finding block needs a `where:` line whose value
  is path-like (contains `/` or `.`, or is a bare 7-40 char hex commit
  SHA). A finding without one is an opaque finding and fails schema.

`NEEDS_REVISION` never mints a marker (exit 3) — a failed review can't
produce a pass marker. A schema-invalid verdict text never mints one
either (exit 4, every violation listed — see `validate` below).

## Suite-line grammar (`verified --suite-line`)

Must contain `N passed` with `N > 0`, and must NOT contain a
`failed`/`error` token (word-boundary matched, so `2 xfailed` — a
green outcome — does not trip the filter). `"0 passed"`, `"3 failed, 2
passed"`, `"no tests ran"` all reject (exit 4).

## Waiver semantics (`waiver --reason`)

One-shot bypass of both marker checks for the next push. Requires a
real justification (>= 10 chars, whitespace-trimmed). `git-guard.py`
unlinks the waiver file BEFORE honoring it (consume-then-allow) so an
undeletable waiver (e.g. read-only dir) is treated as absent and the
marker gates still apply — never a silent permanent bypass.

## Patch-id relaxation (base_sha / patch_id)

`review-pass` and `verified` additionally record `base_sha` (merge-base
with the repo's default branch — resolved via `origin/HEAD`, then local
`main`, then local `master`) and `patch_id` (`git diff base..HEAD | git
patch-id --stable`), but ONLY when every step resolves cleanly. Any
failure (no default branch found, merge-base fails, diff/patch-id
subprocess fails, empty output) omits BOTH fields — never a partial
pair.

`git-guard.py::_gate_push` accepts a marker whose `head_sha` no longer
matches current HEAD **iff** it carries a `patch_id` field AND a
freshly recomputed patch-id (current `merge-base(default-branch,
HEAD)..HEAD`) equals it. This covers:

- **Message-only amends** — `git commit --amend -m "..."` changes
  `head_sha` but not the diff.
- **Content-preserving rebases** — `git rebase main` changes both
  `head_sha` and the merge-base, but patch-id is invariant when the
  diff content itself didn't change.

A content change still blocks (the recomputed patch-id differs). Old
markers with no `patch_id` field, and any resolution/subprocess error,
fall back to strict `head_sha` equality — fail-closed, never a
weaker check than before.

## `validate` — schema dry-run (all violations at once)

```
python3 loom_gate_markers.py validate --verdict-file <path> [--suite-line "<text>"]
```

Runs the same checks `review-pass`/`verified` apply at write time, but
reports every violation in one pass instead of exiting on the first —
the writers themselves still exit-4 on the first problem (fix / rerun
/ fix was previously a ×3 retry loop for markers that fail three
separate checks). Writes nothing, needs no `--repo`. Exit 0 clean, 4
on any violation (each listed on its own line).

## Ordering rule: write markers, THEN push separately

Mint `review-pass.json` and `verified.json` as their own step, THEN run
`git push` (or `gh pr create`/`gh pr merge`) as a separate command.
Chaining them in one compound command (`... && git push`) risks the
push segment being evaluated before the marker write actually lands on
disk in some shells/tool wrappers, and makes failures harder to
attribute to the right step. `git-guard.py` gates every push-family
command independently per Bash-tool invocation regardless of ordering
inside a single compound command, but the two-step form keeps the
causal chain (verdict → marker → push) legible when something fails.

- **`base_sha` is audit metadata only** — the guard never trusts or
  dereferences the stored value; the comparison base is always a
  freshly recomputed merge-base at check time (an attacker-writable
  base would otherwise let the comparison be pinned).
