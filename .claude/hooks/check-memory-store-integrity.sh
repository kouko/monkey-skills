#!/bin/bash
# loom memory-store integrity guard (shift-left for the CI store-integrity step).
#
# Triggered: PostToolUse on Write|Edit (configured in .claude/settings.json).
#
# Why: `docs/loom/memory/` keeps one fact per file, and its README.md §Index
# must carry one line per entry whose description is the entry's frontmatter
# `description` copied byte-identical. Writing the entry alone leaves the store
# invalid. That shipped twice before being caught by CI after push — under a job
# whose display name is "plugin version bump", which names a DIFFERENT check, so
# the failure did not point at the store and cost a diagnosis round each time.
# A third occurrence happened while this work was underway and was caught one
# step later — at branch close-out, by an orchestrator following prose. Prose
# only works when it is read; this hook fires whether or not it is.
#
# Scope: fires for any edit under a `docs/loom/memory/` tree, the store's own
# README.md included — deleting an index line breaks the invariant just as
# surely as omitting one. No-op for every other path, including the near-miss
# spellings `docs/loom/memory-archive/` and `docs/loom/memoryX/`. Note the
# checker globs the store non-recursively, so an edit at `…/memory/sub/x.md`
# triggers a check that cannot see that file — the store's charter is one flat
# file per fact, so a nested entry is itself the thing to fix.
#
# Portability: the store is portable (`loom-pipeline:loom-memory` fires in any
# repo carrying `docs/loom/memory/README.md`) but this checker ships inside no
# plugin. When it is absent, no-op — never let a "No such file" become a
# phantom store violation.
#
# Exit codes:
#   0 — store valid, not a store edit, checker unavailable, or the hook payload
#       was unreadable (no jq, malformed JSON, empty stdin → no path to check)
#   2 — invariant violated. NOTE the host contract: a PostToolUse exit 2 does
#       NOT undo the write — the file has already landed. It surfaces stderr to
#       the agent, which must then fix the store before continuing. Preventing
#       a call is PreToolUse's job (PermissionRequest can also deny one); a
#       PostToolUse hook never can. So this hook shortens the feedback loop from
#       "after push, under a misnamed CI job" to "at the edit"; it is not a
#       write barrier.

set -e

INPUT=$(cat 2>/dev/null || echo '{}')

FILE_PATH=""
if command -v jq >/dev/null 2>&1; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null || echo "")
fi

# Only relevant for edits inside a memory store. ONE pattern does both jobs:
# the strip derives the repo root, and "nothing was stripped" IS the
# not-a-store-path test. The derivation is cwd-independent because the host
# supplies an absolute `file_path`. A bare relative path strips nothing and
# no-ops (the safe direction); a `./`-prefixed one would strip to `.` and make
# the `cd` below cwd-relative — neither shape is reachable through Write/Edit,
# which pass absolute paths. An earlier draft used a separate `case` guard
# plus this strip — two patterns that can drift apart, and whole-branch review
# showed the drift was unobservable: widening only the `case` left behaviour
# identical because the stricter strip then failed and the missing checker
# fail-opened. With a single pattern, widening it changes behaviour, which is
# what makes the near-miss probes in the test suite discriminating.
REPO_ROOT="${FILE_PATH%/docs/loom/memory/*}"
# Explicit intent, deliberately untested: removing this line does not change
# observable behaviour today, because a non-store path leaves REPO_ROOT equal to
# the file path and the checker lookup then fail-opens on the missing file. It
# stays so the not-a-store-path decision is stated rather than inherited from a
# downstream accident.
[ "$REPO_ROOT" != "$FILE_PATH" ] || exit 0

CHECKER="$REPO_ROOT/scripts/check_loom_memory_integrity.py"
[ -f "$CHECKER" ] || exit 0   # portable store, non-portable checker → harmless no-op

# THREE constructs in this hook carry no test, each for a stated reason. Two are
# equivalent mutants (removing them changes nothing observable, so any test would
# be green either way); the third is observable but deliberately not pinned.
# Listing them beats shipping a green test that cannot fail.
#   1. the `[ "$REPO_ROOT" != "$FILE_PATH" ]` guard ABOVE — equivalent mutant,
#      see its own comment.
#   2. PYTHONDONTWRITEBYTECODE, immediately below — equivalent mutant.
#   3. the `2>&1` in the capture below — observable, not pinned.
#
# PYTHONDONTWRITEBYTECODE: defence-in-depth. CPython does not cache the
# `__main__` script and the checker imports stdlib only, so no `__pycache__` is
# reachable today — a test asserting its absence passes with or without this var
# (whole-branch review proved the equivalent mutant). It stays because a
# `__pycache__` under a scanned tree trips the skill-folder-structure hook, and
# the checker may grow a local import later.
# `2>&1`: folds a checker crash into $REPORT so the traceback prints under the ❌
# header instead of above it. This IS observable — a test could assert the
# header precedes the traceback — but stderr ordering on a crash path is not a
# contract worth pinning, so it is left unguarded on purpose rather than
# misfiled as untestable.
if ! REPORT=$(cd "$REPO_ROOT" && PYTHONDONTWRITEBYTECODE=1 python3 "$CHECKER" 2>&1); then
  cat >&2 <<EOF
❌ loom memory-store integrity violated

$REPORT

Fix: give every entry one line in docs/loom/memory/README.md §Index, in the
form

    [<name>](<name>.md) — <description>

where <description> is that entry's frontmatter \`description\` copied
byte-identical, and <name> matches both the filename and the frontmatter
\`name\`. Then re-run:

    python3 scripts/check_loom_memory_integrity.py
EOF
  exit 2
fi

exit 0
