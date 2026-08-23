# Gate markers spec

Reference for `loom-code/scripts/loom_gate_markers.py` (the marker
writer) and `loom-code/hooks/git-guard.py` (the PreToolUse reader).
Written up per the repository's
[`docs/loom/plans/2026-07-06-gate-friction-pack.md`](https://github.com/kouko/monkey-skills/blob/main/docs/loom/plans/2026-07-06-gate-friction-pack.md)
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
  is a path plus an anchor (a verbatim string or stable heading), with
  an optional line number for precision — `where: <path + anchor; line
  optional>`. A finding without one is an opaque finding and fails
  schema.
- Every `- severity:` finding block whose `dimension:` is absent, or does
  not fall in the docs-arm set (`omission`, `ambiguity`, `inconsistency`,
  `incorrect-fact`, `missing-population`), must carry an `origin:` line
  valued `none` or `<path> :: "<verbatim quote from that file>"` — a
  missing one fails schema the same way a missing `where:` does. A
  docs-arm finding is exempt from carrying `origin:` at all.
- Whenever an `origin:` line IS present, its value is grammar-checked on
  **every** arm, docs included — the docs-arm exemption governs only
  whether `origin:` must be carried, never excuses a malformed value a
  docs-arm finding chose to write (bare path, unterminated quote, blank
  quote). A malformed `origin:` fails schema the same way a missing
  `where:` does, regardless of arm.
- A duplicate `dimension:` line fails schema (exactly one is required):
  which of two values is intended is ambiguous, and `dimension` drives
  the arm partition that decides whether `origin:` is even required.
- A duplicate `origin:` line fails schema (exactly one is required) for
  the same reason — which of two quotes is intended is ambiguous.

The quote itself is verified separately (see §Quote verification below)
and does NOT gate schema validity or the mint.

`NEEDS_REVISION` never mints a marker (exit 3) — a failed review can't
produce a pass marker. A schema-invalid verdict text never mints one
either (exit 4, every violation listed — see `validate` below).

## Quote verification

A grammar-valid `origin:` whose value is `<path> :: "<quote>"` (not
`none`) is checked against the file's content **at `head_sha`** — via
`git show <head_sha>:<path>`, never the worktree — so the ephemeral
result reflects what was actually reviewed, not a since-edited file.
Matching is two-stage: byte-exact first, then one shared normaliser
(NFC, whitespace collapse, typographic-quote/dash folding) on a miss.
A match produces an ephemeral `verified-exact` or `verified-normalised`
status for the current invocation. Normalised matches emit one aggregated
advisory; no quote result is persisted across review rounds.
`review-pass` never creates or updates `origin-ledger.json`; an existing
legacy file under `.git/loom/` is ignored.

A quote that does NOT verify is classified ephemerally, never refused — this used to
be a mint-time refusal and was demoted (0 of 24 severity-🔴 findings
measured on this repo ever reached it — a transcript tally, not a
script; population and method at
`docs/loom/plans/2026-08-02-finding-origin-attribution.md` §Re-cut after
Tasks 1-6). Five reasons are distinguished internally as
`unverified-<reason>`:
`sha-unresolvable`, `file-absent`, `not-a-file`, `undecodable-blob` (the
committed blob couldn't be read as text), and `quote-absent` (the file
read fine but never contained the quote). `origin: none` returns
`none`; a malformed `origin:` value returns `malformed`; an absent
`origin:` line returns `absent` regardless of arm — a code-arm finding
that refuses the mint for a missing `origin:` is classified the same
way as an exempt docs-arm finding's absence; a duplicate
`origin:` produces `duplicate` (also grammar-refused — see above — but
distinct from `absent`, since an `origin:` line did exist, just twice).

`validate` (below) takes no `--repo` and therefore has no `head_sha` to
verify a quote against — it says so loudly rather than skipping
silently.

## Run-command binding (`verified --run`)

`verified --run "<cmd>"` executes `<cmd>` in the repo, captures its real
exit code + a bounded output tail (4000 chars), and mints
`verified.json` ONLY on exit 0 — recording `run_cmd`, `exit_code`,
`output_tail`. A non-zero exit writes no marker (exit 4). This binds the
marker to a real run instead of a self-typed summary; the honest
residual is that `--run "true"` still mints — a bar-raise (a command
must actually run and exit 0, and is recorded for audit), not local
cryptographic unforgeability.

The legacy suite-line grammar (`N passed` with `N > 0`, no
`failed`/`error` token, word-boundary matched so `2 xfailed` passes) is
retained ONLY for the `validate --suite-line` dry-run linter below,
never for the `verified` write path.

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
