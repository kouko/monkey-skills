# Plan: loom memory hardening — O4 → O2 → O3 → O5 → O6

Source brief: docs/loom/specs/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md
Total tasks: 10
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-17T00:20+08:00, 14/14 checks; advisory notes: Tasks 2/3 and 6/7/9 parallel-eligible but conservatively sequential — shared test files / SKILL.md chain)

## Notes

- **Branch**: create `feat/loom-memory-hardening-o4-o2-o3-o5-o6` from current
  HEAD (never from `origin/main` — push-guard gotcha) before Task 1. The brief
  + this plan are committed with the first task's commit.
- **No change-folder consumed**: input was explicitly declared as the
  brainstorming brief (Layer 0 — caller named the artifact). The single
  `docs/loom/2026-07-12-us-sec-primary-source-layer/` folder is an unrelated,
  already-shipped investing-toolkit change; detection did not run and it is
  NOT bound.
- **PINNED wording** (transcribe VERBATIM wherever a task says "pinned
  hierarchy sentence" — Tasks 1, 2; source: brief §Decision):
  > Durable lessons live in the repo's committed memory store
  > (`docs/loom/memory/` here) — the authoritative carrier. Commit trailers
  > are commit-bound capture: best-effort, secondary, and never the retrieval
  > path a durable lesson depends on.
- **PINNED contradiction-check wording** (transcribe VERBATIM — Tasks 8, 9
  carry the same rule; skill text may extend it, the charter line is the
  one-liner form):
  > Before recording, grep the store for entries the new fact contradicts —
  > on a hit, update or replace that entry (git history is the archive);
  > never add a contradicting sibling.
- **CI job names are additive only** — never rename existing workflow job
  display names (branch protection pins them by exact string).
- **Exit-code contract of `memory-grep.sh` is frozen** (0/1/2/3/4, pinned by
  `dev-workflow/tests/test-memory-grep-verify.sh`) — new flags may reuse the
  existing codes but must not change existing flags' semantics.
- **Charter edits are additive** — `loom-code/scripts/test_loom_memory_timing_convention.py`
  pins `docs/loom/memory/README.md` §When to record content; Tasks 2 and 9
  must keep it green (run it in their GREEN step).
- Prose grep-tests: scope assertions to a measured neighborhood around the
  feature's anchor string and verify RED against pre-change content
  (`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md`).

## Decision Log

- Kickoff sweep (2026-07-17): zero one-way-door decisions — every task is a
  reversible text/script/CI increment; wording + option order pre-ratified by
  the merged research doc (#575) and the user's /goal directive. No briefing
  fired (appetite read: no PRINCIPLES.md entry; nothing to brief regardless).
- Kickoff decision: memory-worthiness detector for --verify-merged → the
  `## Memory` heading in the squash-commit body (deterministic under PR_BODY
  squash mode; pinned in Task 5).
- Kickoff decision: CI verify level on main → text-grep level
  (`--verify-merged`), not strict trailer parse — old merges and multi-commit
  concatenations must not false-fail; `--verify-strict` ships as a diagnostic
  tool (Task 7).

- Execution decision (2026-07-17, Task 1 verdict split): spec-reviewer PASS
  (scope-clean per Task-3-owns-the-hatch boundary), code-quality-reviewer
  NEEDS_REVISION (🔴 the untouched hatch paragraph "git log --grep … is the
  supported path", SKILL.md:135-138, contradicts the new top-of-file
  doctrine). Resolution: the flagged lines are exactly the region Task 3
  rewrites into a pointer — the finding is folded into Task 3's dispatch as a
  MUST (eliminate "is the supported path" framing + add a whole-file absence
  assertion in the raw-footer test). Task 1 committed within its declared
  scope; the contradiction cannot survive the branch because Task 3's test
  pins its absence. (Two-way door — same-PR sequencing choice, logged not
  briefed.)

- Execution decision (2026-07-17, Task 6): the post-merge verify job ships as
  a SEPARATE workflow file `.github/workflows/memory-verify-merged.yml`, not
  a second job inside dev-workflow-ci.yml as the task text literally said —
  GitHub Actions `paths:` filters gate at the `on:` level, so an in-file job
  could never fire on pushes outside dev-workflow/**, which is exactly the
  class of push it exists to catch. Spec-reviewer accepted as
  intent-conforming. (Two-way door, logged not briefed.)

## Task 1 — O4a: git-memory SKILL.md carrier-doctrine rewrite + plugin sweep

- Description: Rewrite `dev-workflow/skills/git-memory/SKILL.md`'s carrier
  doctrine to the pinned hierarchy sentence (see ## Notes): replace the
  "commit messages / PR body as the durable substrate" framing (SKILL.md:9-10,
  28-30) and the "`git log --grep` … is the supported path" recall guidance
  (SKILL.md:91-98) so the committed file store is named the authoritative
  durable-lesson carrier and trailers are commit-bound/secondary. Sweep the
  whole dev-workflow plugin for contradicting claims ("durable substrate",
  trailer-grep-as-durable-path) and fix operative survivors. Write the new
  shell test FIRST (RED against current wording).
- Module: dev-workflow/skills/git-memory
- Files touched: dev-workflow/skills/git-memory/SKILL.md, dev-workflow/tests/test-git-memory-carrier-doctrine.sh
- Context paths:
  - dev-workflow/skills/git-memory/SKILL.md
  - dev-workflow/skills/git-memory/standards/memory-conventions.md
  - docs/loom/specs/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md (§Decision pinned wording, §Current State Evidence)
  - dev-workflow/tests/test-memory-grep-verify.sh (test style to mirror)
- Acceptance:
  - RED: `bash dev-workflow/tests/test-git-memory-carrier-doctrine.sh` fails
    against current SKILL.md (asserts pinned-sentence fragment present +
    "durable substrate" absent + grep-as-supported-durable-path claim absent).
  - GREEN: that script exits 0; `grep -ri "durable substrate" dev-workflow/`
    has zero operative hits; anti-preload section (SKILL.md:193-197) untouched.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1 "O4 — carrier doctrine fix …
  SKILL.md re-states the hierarchy … Plugin-wide grep sweep"

## Task 2 — O4b: charter README carrier-hierarchy note

- Description: Add the pinned hierarchy sentence (transcribe VERBATIM from
  ## Notes) to `docs/loom/memory/README.md` as a one-line note anchored at the
  jurisdiction table (README.md:13-18), clarifying the "Decision bound to a
  commit → git-memory trailers" row is commit-bound capture, not the durable
  retrieval path. Extend the charter-pin shell test FIRST (RED).
- Module: docs/loom/memory
- Files touched: docs/loom/memory/README.md, dev-workflow/tests/test-loom-memory-charter-pins.sh
- Context paths:
  - docs/loom/memory/README.md
  - loom-code/scripts/test_loom_memory_timing_convention.py (existing pins that must stay green)
- Acceptance:
  - RED: `bash dev-workflow/tests/test-loom-memory-charter-pins.sh` (new file)
    fails against current README (asserts pinned-sentence fragment within the
    jurisdiction-table neighborhood).
  - GREEN: that script exits 0 AND
    `python3 -m pytest loom-code/scripts/test_loom_memory_timing_convention.py -q`
    passes.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #1 "The charter … jurisdiction row
  gains the same one-line hierarchy note"

## Task 3 — O2: compose-pr.md raw-trailer-footer mandate

- Description: In `dev-workflow/skills/git-memory/protocols/compose-pr.md`,
  make memory-worthy PR bodies REQUIRED to end with a blank-line-separated raw
  trailer block (`Decision:` / `Learning:` / `Gotcha:`, unbolded) as the
  ABSOLUTE LAST block — placed after even the `🤖 Generated with` footer
  (any non-trailer line after it empties `%(trailers)`; live-found in #575).
  Include a worked before/after example. Convert the opt-in hatch in
  SKILL.md:123-130 into a pointer to this mandate. Write the shell test FIRST.
- Module: dev-workflow/skills/git-memory
- Files touched: dev-workflow/skills/git-memory/protocols/compose-pr.md, dev-workflow/skills/git-memory/SKILL.md, dev-workflow/tests/test-git-memory-raw-footer-mandate.sh
- Context paths:
  - dev-workflow/skills/git-memory/protocols/compose-pr.md
  - dev-workflow/skills/git-memory/SKILL.md
  - docs/loom/specs/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md (§Smallest End State #2)
- Acceptance:
  - RED: `bash dev-workflow/tests/test-git-memory-raw-footer-mandate.sh` fails
    against current compose-pr.md (asserts the absolute-last-block mandate
    within the ## Memory placement-rule neighborhood, compose-pr.md:90-101).
  - GREEN: that script exits 0; SKILL.md hatch section points to the
    compose-pr mandate instead of framing the footer as optional.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #2 "O2 — mechanize the raw trailer
  footer (compose-pr.md)"

## Task 4 — O3a: dev-workflow CI workflow wiring the orphan shell tests

- Description: Create `.github/workflows/dev-workflow-ci.yml` firing on
  `pull_request` and `push` to `[main]`, with a job that runs every
  `dev-workflow/tests/test-*.sh` (glob or explicit list including the three
  existing memory-grep tests, currently run by NO workflow). Copy the
  checkout/runner pattern from `.github/workflows/loom-siblings-ci.yml:52-64`.
  New job names only (additive — see ## Notes).
- Module: .github/workflows/dev-workflow-ci.yml
- Files touched: .github/workflows/dev-workflow-ci.yml
- Context paths:
  - .github/workflows/loom-siblings-ci.yml
  - .github/workflows/loom-pipeline-ci.yml
  - dev-workflow/tests/ (the scripts to wire)
- Acceptance:
  - RED: `test -f .github/workflows/dev-workflow-ci.yml` fails (file absent).
  - GREEN: file exists; `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/dev-workflow-ci.yml'))"`
    exits 0; each wired script runs green locally
    (`for t in dev-workflow/tests/test-*.sh; do bash "$t"; done`); the new
    runnable verb (dev-workflow test suite in CI) is thereby declared in the
    repo's CI command surface.
- External surfaces: GitHub Actions workflow syntax + `actions/checkout` /
  `actions/setup-python` — ground on the two existing workflow files above,
  not from memory.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 "(a) PR+push job running the three
  existing dev-workflow/tests/test-memory-grep-*.sh (currently run by NO
  workflow)"

## Task 5 — O3b-i: memory-grep.sh --verify-merged flag

- Description: Add `--verify-merged <ref>` to
  `dev-workflow/skills/git-memory/scripts/memory-grep.sh`: exit 0 when the
  ref's commit body has no `## Memory` heading (not memory-worthy) OR has the
  heading and a `Decision:`/`Learning:`/`Gotcha:` verify key; exit 4 when the
  heading is present but no verify key survives (the #574 silent-drop case).
  Reuse existing exit codes; do not alter existing flags. Write the shell
  test FIRST.
- Module: dev-workflow/skills/git-memory/scripts/memory-grep.sh
- Files touched: dev-workflow/skills/git-memory/scripts/memory-grep.sh, dev-workflow/tests/test-memory-grep-verify-merged.sh
- Context paths:
  - dev-workflow/skills/git-memory/scripts/memory-grep.sh (esp. :36-42 exit codes, :62-63 key regexes, :181-187 --verify)
  - dev-workflow/tests/test-memory-grep-verify.sh (sandbox-commit test pattern)
- Acceptance:
  - RED: `bash dev-workflow/tests/test-memory-grep-verify-merged.sh` fails
    (flag not implemented; covers the three semantic cases above via sandbox
    commits).
  - GREEN: that script exits 0 AND
    `bash dev-workflow/tests/test-memory-grep-verify.sh` still exits 0
    (frozen exit-code contract).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 "(b) push-to-main job: if HEAD
  commit body contains the ## Memory heading … then memory-grep.sh --verify
  … must exit 0" (the testable predicate the CI job calls)

## Task 6 — O3b-ii: push-to-main post-merge verify job

- Description: Add a second job to `.github/workflows/dev-workflow-ci.yml`
  that runs ONLY on `push` to `main` (`if: github.event_name == 'push'`) and
  executes `bash dev-workflow/skills/git-memory/scripts/memory-grep.sh
  --verify-merged HEAD` with `fetch-depth` sufficient to read HEAD's body —
  failing the workflow when a memory-worthy squash commit landed without its
  trailer carrier.
- Module: .github/workflows/dev-workflow-ci.yml
- Files touched: .github/workflows/dev-workflow-ci.yml
- Context paths:
  - .github/workflows/dev-workflow-ci.yml (as produced by Task 4)
  - dev-workflow/skills/git-memory/scripts/memory-grep.sh
- Acceptance:
  - RED: `grep -q 'verify-merged' .github/workflows/dev-workflow-ci.yml`
    fails (job absent).
  - GREEN: grep succeeds; YAML still parses
    (`python3 -c "import yaml; yaml.safe_load(open('.github/workflows/dev-workflow-ci.yml'))"`);
    local dry-run of the job's command on current HEAD (a non-memory-worthy
    commit or one with valid trailers) exits 0.
- External surfaces: GitHub Actions event filtering (`push` to main) — ground
  on existing workflows' `on:` blocks.
- Dependencies: Tasks 4, 5 complete first
- Independent: false
- Brief item covered: Smallest End State #3 "(b) push-to-main job … else the
  workflow fails"

## Task 7 — O5: memory-grep.sh --verify-strict flag + flag docs

- Description: Add `--verify-strict <ref>` to `memory-grep.sh`: like
  `--verify` but the verify key must be yielded by
  `git interpret-trailers --parse --unfold` over the commit message (catches
  the #575 refinement: text-grep passes while `%(trailers)` parses empty
  because non-trailer lines follow the footer). Exit 0 on parse-level hit,
  exit 4 otherwise. Document `--verify-merged` and `--verify-strict` in
  git-memory SKILL.md's verify/retrieval section (one line each; retrieval
  guidance already demoted by Task 1). Write the shell test FIRST.
- Module: dev-workflow/skills/git-memory/scripts/memory-grep.sh
- Files touched: dev-workflow/skills/git-memory/scripts/memory-grep.sh, dev-workflow/tests/test-memory-grep-verify-strict.sh, dev-workflow/skills/git-memory/SKILL.md
- Context paths:
  - dev-workflow/skills/git-memory/scripts/memory-grep.sh (:253-258 existing interpret-trailers extraction)
  - dev-workflow/skills/git-memory/standards/memory-conventions.md (:299-321 parser rule)
- Acceptance:
  - RED: `bash dev-workflow/tests/test-memory-grep-verify-strict.sh` fails —
    must include the #575-shaped case: a sandbox commit whose body text-greps
    a `Decision:` line mid-body (plain `--verify` exits 0) but whose trailer
    block is followed by a non-trailer line so strict parse finds nothing
    (`--verify-strict` exits 4).
  - GREEN: that script exits 0 AND both existing verify tests plus
    test-memory-grep-verify-merged.sh still exit 0.
- Dependencies: Tasks 3, 5 complete first
- Independent: false
- Brief item covered: Smallest End State #4 "O5 — parser-strict verification +
  retrieval guidance"

## Task 8 — O6a: loom-memory record-verb contradiction check

- Description: In `loom-pipeline/skills/loom-memory/SKILL.md` §record, add a
  mandatory contradiction-check step between classify and write (extends the
  pinned contradiction-check wording in ## Notes): grep the store (index +
  bodies) for entries the new fact contradicts; on a hit, update or replace
  the old entry (delete + rewrite — charter policy: git history is the
  archive) instead of adding a contradicting sibling; note the replacement in
  the index line. Mirrors git-memory's backward-pointing `Supersedes:`
  doctrine (memory-conventions.md:23-49) without new frontmatter. Bump the
  skill frontmatter `version: 0.1.0 → 0.2.0`. Write the pytest FIRST; confirm
  loom-pipeline CI runs `loom-pipeline/scripts/` pytest (Explore finding) and
  place the test there.
- Module: loom-pipeline/skills/loom-memory
- Files touched: loom-pipeline/skills/loom-memory/SKILL.md, loom-pipeline/scripts/test_loom_memory_record_contradiction.py
- Context paths:
  - loom-pipeline/skills/loom-memory/SKILL.md
  - dev-workflow/skills/git-memory/standards/memory-conventions.md (:23-49 supersession doctrine)
  - .github/workflows/loom-pipeline-ci.yml (confirm pytest path)
  - docs/loom/specs/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md (§Smallest End State #5)
- Acceptance:
  - RED: `python3 -m pytest loom-pipeline/scripts/test_loom_memory_record_contradiction.py -q`
    fails (asserts the contradiction-check step text within the §record
    neighborhood, scoped per ## Notes grep-test rule).
  - GREEN: that pytest passes; full `python3 -m pytest loom-pipeline/scripts/ -q`
    green.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #5 "O6 … record verb gains a
  mandatory contradiction check"

## Task 9 — O6b: charter record-guidance one-liner

- Description: Add the pinned contradiction-check one-liner (transcribe
  VERBATIM from ## Notes) to `docs/loom/memory/README.md` §When to record.
  Extend `dev-workflow/tests/test-loom-memory-charter-pins.sh` FIRST (RED).
- Module: docs/loom/memory
- Files touched: docs/loom/memory/README.md, dev-workflow/tests/test-loom-memory-charter-pins.sh
- Context paths:
  - docs/loom/memory/README.md
  - loom-code/scripts/test_loom_memory_timing_convention.py (pins that must stay green)
- Acceptance:
  - RED: extended assertion in
    `bash dev-workflow/tests/test-loom-memory-charter-pins.sh` fails against
    current README §When to record.
  - GREEN: that script exits 0 AND
    `python3 -m pytest loom-code/scripts/test_loom_memory_timing_convention.py -q`
    passes.
- Dependencies: Tasks 2, 8 complete first
- Independent: false
- Brief item covered: Smallest End State #5 "Charter §record guidance gains
  the matching one-liner"

## Task 10 — Version bumps + manifest sync

- Description: Bump `dev-workflow/.claude-plugin/plugin.json` `"version":
  "2.21.0"` → `"2.22.0"` and `loom-pipeline/.claude-plugin/plugin.json`
  `"version": "0.7.1"` → `"0.7.2"` (skill content changed in both plugins —
  marketplace publishes by version; an unbumped plugin update is a silent
  no-op). Then grep `.claude-plugin/marketplace.json` and any codex-mirror
  manifests for those plugins' version strings and sync if pinned there; run
  the repo's script-sync check if one covers these plugins.
- Module: dev-workflow/.claude-plugin/plugin.json
- Files touched: dev-workflow/.claude-plugin/plugin.json, loom-pipeline/.claude-plugin/plugin.json, .claude-plugin/marketplace.json (only if versions are pinned there)
- Context paths:
  - dev-workflow/.claude-plugin/plugin.json
  - loom-pipeline/.claude-plugin/plugin.json
  - .claude-plugin/marketplace.json
- Acceptance:
  - RED: `grep -q '"version": "2.22.0"' dev-workflow/.claude-plugin/plugin.json`
    fails (still 2.21.0).
  - GREEN: both new versions grep clean; no stale old-version pin remains for
    these two plugins in `.claude-plugin/marketplace.json` or codex-mirror
    manifests; `python3 -m pytest loom-pipeline/scripts/ -q` and
    `for t in dev-workflow/tests/test-*.sh; do bash "$t"; done` green.
- Dependencies: Tasks 6, 7, 9 complete first
- Independent: false
- Brief item covered: Decision "dev-workflow plugin bumps 2.21.0 → 2.22.0
  (skill content changed); loom-pipeline bumps 0.7.1 → 0.7.2"
