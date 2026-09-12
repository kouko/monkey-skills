# Fixture builders stop spending a process per commit — plan
intent: 2026-09-12-fast-test-fixtures@40f9fe14a
charter: 1.0

## Current State Evidence
- Forward: `loom-workflow/tests/test-memory-grep-perf.sh:54` `build_perf_repo` spawns one `git commit` per commit (`:96`); called with 2000 at `:181`, measured 66.31s.
- Reverse: the same builder at `:180` makes the 20-commit control repo in 0.75s, so only the large size is the cost.
- Error: `:80` picks a `Supersedes:` target out of a newline accumulator; the comment at `:101` records it once yielding 19 instead of 20.
- Data: `:186`-`:210` assert the fixture's shape through `--format=json --history` — 300 records, 20 superseded, 280 live.
- Boundary: `test_probes_memory_grep_single_pass.py:284` builds 200 commits in a module fixture (`:330`); `test_probes_memory_grep_render.py:110` builds 20 and 200 (`:160`, `:163`).

## Task DAG

**W1-01 Build the 2,000-commit shell fixture in one git process**  after: —  acceptance: 3
- Files: loom-workflow/tests/test-memory-grep-perf.sh
- Test: A3 positive: perf-12-pass-zero-fail; negative: perf-shape-assertion-fails-on-mutated-fixture.
- Risk: 20 `Supersedes:` trailers cite shas of earlier commits, so the import needs two passes; agent-decided — emit the stream with python3, already this file's dependency, adding no new file.

**W1-02 Build the two pytest fixtures in one git process**  after: —  acceptance: 4
- Files: loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_single_pass.py, loom-workflow/skills/git-memory/scripts/test_probes_memory_grep_render.py, loom-workflow/skills/git-memory/scripts/conftest.py
- Test: A4 positive: git-memory-64-passed; negative: perf-repo-shape-assertion-fails-on-mutated-fixture.
- Risk: four files in this directory keep private `_init_repo`/`_commit` copies; agent-decided — add only the bulk importer to conftest.py and leave every per-commit helper untouched.

**W2-01 Measure the whole suite and pin the diff's scope**  after: W1-01, W1-02  acceptance: 1, 2, 5
- Files: docs/loom/2026-09-12-fast-test-fixtures/evidence/suite-timing.md
- Test: A1 positive: full-suite-under-95s-twice; boundary: slowest-group-no-longer-fixture-bound. A2 positive: full-suite-pass-count-ge-baseline; negative: dropped-test-detected-by-count-compare. A5 positive: diff-lists-test-files-only; negative: non-test-path-in-diff-rejected.
- Risk: a wall-clock bound can go red from machine load rather than regression; agent-decided — record two runs plus the per-group breakdown so load stays distinguishable.

## Questions asked
① — what — 你要的是：完整測試從 145 秒降到 ≤95 秒，變快全部來自「準備測試資料」，測試檢查的東西一條都不減（通過數不變、失敗為零），那支效能測試仍餵給被測腳本同樣兩千個 commit 與同樣資料形狀，被測的程式碼一個位元組都不動。對嗎？
① — consequence — 回答「好」等於一併同意：審查與發佈檢查通過後自動推送分支並開一個 Ready 的 PR；合併仍然是你另外決定；你隨時可以在推送前叫停。

## Risks
1. The stream generation lands twice, once for the shell test and once for the pytest pair, because a shell test cannot import a pytest conftest helper. Accepted: test-only code, no shared runtime surface.
2. A fixture rewrite can quietly make an assertion vacuous — the class of bug this file's own comment at `:101` records. Every task's negative case mutates the fixture and demands the shape assertion go red.
3. CI's `check_mechanisms.py --baseline origin/main` blocks a new mechanism without a budget exception. This change adds no file and no mechanism; it rewrites three existing builders.
4. `fast-import` writes refs directly, so a fixture repo can end up with an unpopulated worktree. Each builder must leave the tracked file present, as the `--path` cases read it.
5. The version gate counts any change under a plugin's `skills/` tree as skill content, so the touched fixtures oblige a loom-workflow bump plus manifest sync. That pair rides in its own commit and owns no Acceptance line.
