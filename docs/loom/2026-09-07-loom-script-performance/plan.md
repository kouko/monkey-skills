# Five pure performance fixes in loom scripts — output byte-identical — plan
intent: 2026-09-07-loom-script-performance@05fe8c28
charter: 1.0

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py:39` top-level `import yaml`; `cmd_push --hook` (`:3221-3237`) returns 0 for non-push commands before `load_manifest` (`:329-330`) ever runs.
- Forward: `loom-code/scripts/check_doc_citations.py:248`, `:283`, `:514` — three `endswith` scans over the full `repo_files` list per citation; 18.1M calls on this repo (cProfile 2026-09-07).
- Forward: `loom-code/hooks/session-start:48-49` `stations_block` awk; called at `:52` and three times via `stations_for_dp` (`:55-60`, `:72-74`).
- Forward: `loom-workflow/skills/decision-map/scripts/check_map_fog.py:116-128` — one `ls-tree` then one `git show` per ticket; `map_store.py:1379`, `:1536`, `map_transaction.py:404-415` glob+`read_ticket` twice.
- Reverse: no caller reads `yaml` outside `load_manifest`; `check_doc_citations.py:729-752` already caches `repo_files` per root, so an index hangs off that cache.
- Error: `check_map_fog.py:120-131` raises `SchemaViolation` on a failed `ls-tree` or `show`; `map_store.py:1600-1605` propagates `SchemaViolation` from both ticket checks as exit 2.
- Data: `read_ticket` returns `TicketDocument` (`map_store.py`); `_check_blocked_by(graph, tickets_dir)` takes `dict[stem, blocked_by]` (`map_transaction.py:410`); `stations_block` output is the manifest `stations:` YAML block.
- Boundary: `loom-code/scripts/test_check_doc_citations.py` (54 tests), `test_session_start_words.py`, `test_codex_mirror_matches_checker.py`, `test_check_map_fog.py` (14), `test_map_store.py` (66); CI runs `check_doc_citations.py` over all md (`.github/workflows/loom-code-ci.yml:169`).

## Task DAG

Lane: full (repo default; `loom_checker.py` and `session-start` are `gate`-typed paths). Wave 1 tasks touch disjoint files in three plugins and run in parallel; wave 2 bumps versions and closes with the memory step.

### Wave 1 — the five fixes, each behind an equivalence oracle

**W1-01 Lazy `yaml` import on the checker hook path**  acceptance: 1
- Files: `loom-code/scripts/loom_checker.py`, `.codex/hooks/loom_checker.py`, `loom-code/scripts/test_loom_checker_hook_import.py` (new)
- Test: A1 positive: `hook-nonpush-no-yaml-import` — `-X importtime` on `push --hook` with `echo hi` payload shows no `yaml` line; negative: `push-command-still-loads-manifest` — a push payload reaches `load_manifest` (existing push tests green).
- Risk: another top-level symbol may depend on `yaml` indirectly; grep shows only `:330`. agent-decided: import inside `load_manifest`, mirror regenerated with `codex_scaffold.py --repo .` so `test_codex_mirror_matches_checker` stays green.

**W1-02 Basename index for citation suffix resolution**  acceptance: 2
- Files: `loom-code/scripts/check_doc_citations.py`, `loom-code/scripts/test_check_doc_citations_index.py` (new)
- Test: A2 positive: `index-equivalence-full-repo` — old and new output byte-identical over every md, wall ≤0.4 s; boundary: `same-basename-two-dirs`, `slash-path-zero-hits`, `bare-name-zero-hits` — identical verdicts.
- Risk: three call sites (`:248`, `:283`, `:514`) must share one index or zero/one/multiple semantics diverge. agent-decided: build `dict[basename, list[path]]` next to the per-root `repo_files` cache; `endswith` check kept on the pruned candidates.

**W1-03 One awk pass in session-start**  acceptance: 3
- Files: `loom-code/hooks/session-start`, `loom-code/scripts/test_session_start_awk_once.py` (new)
- Test: A3 positive: `injection-byte-identical` — stdout identical to pre-change in this repo and an empty git repo; boundary: `awk-invoked-once` — `bash -x` trace counts exactly one `awk` on the manifest.
- Risk: bash 3.2 has no `mapfile`; a multi-line variable must be quoted at every use. agent-decided: capture `stations_block` once into `stations_yaml`, `stations_for_dp` uses `printf '%s\n' "$stations_yaml" | grep …`.

**W1-04 `cat-file --batch` in fog base-history read**  acceptance: 4
- Files: `loom-workflow/skills/decision-map/scripts/check_map_fog.py`, `loom-workflow/skills/decision-map/scripts/test_check_map_fog_batch.py` (new)
- Test: A4 positive: `graduated-set-identical-20-tickets` — same set as old code, git spawn count 2 via monkeypatched `_run_git`; negative: `missing-tree-and-unparsable-ticket` — `SchemaViolation` messages verbatim-equal to old code.
- Risk: `cat-file --batch` reports a missing blob inline (`<sha> missing`) instead of a non-zero exit; the reader must map that to the same `SchemaViolation` text. agent-decided: `ls-tree -r` without `--name-only`, parse `<mode> blob <sha>\t<path>`.

**W1-05 Single ticket read in validate and update-blockers**  acceptance: 5
- Files: `loom-workflow/skills/decision-map/scripts/map_store.py`, `loom-workflow/skills/decision-map/scripts/map_transaction.py`, `loom-workflow/skills/decision-map/scripts/test_ticket_read_once.py` (new)
- Test: A5 positive: `validate-findings-identical` — same finding text and order, `read_ticket` call count N not 2N; negative: `update-blockers-files-identical` — written files byte-identical, own pass count N not 2N (nested `validate()` adds its own N; today 4N+1).
- Risk: `_check_tickets` raises on the first bad ticket before `_check_monotonic_relations` runs; a shared pre-read must not reorder which error surfaces first. agent-decided: read the sorted list once, keep both checks' iteration order and raise points unchanged.

### Wave 2 — versions, changelogs, memory

**W2-01 Version bumps and changelog lines**  after: W1-01, W1-02, W1-03, W1-04, W1-05  acceptance: 6, 7
- Files: `loom-code/.claude-plugin/plugin.json`, `loom-code/CHANGELOG.md`, `loom-workflow/.claude-plugin/plugin.json`, `loom-workflow/CHANGELOG.md`, `.codex/hooks/loom_checker.py`
- Test: A6 positive: `existing-tests-untouched` — `git diff` of the five evidence test files empty, package tests green; boundary: `package-tests-green`. A7 positive: `changelog-matches-plugin-version` — top entry equals plugin.json, names before/after numbers; negative: `codex-mirror-version-line` — mirror header carries the new version.
- Risk: `.codex` mirror header carries the loom-code version and drifts on bump. agent-decided: patch bumps (1.8.1, 4.1.1) — no surface changed; mirror regenerated after the bump so the header and the lazy import land together.

**W2-memory Memory step — graduated probes and store entries**  after: W2-01
- Files: graduated probe copies under `loom-code/scripts/` and `loom-workflow/skills/decision-map/scripts/`; `docs/loom/memory/` entries
- Test: `python3 scripts/check_loom_memory_integrity.py`; the graduated copies pass under the package-tests command and the loom-workflow CI pytest glob.
- Risk: a probe pinning a moment-fact (8.7 ms, 2.99 s) goes red elsewhere; probes assert counts and bounds, not measurements. Implementer: the orchestrator (`fresh_context: false`).

## Questions asked
1 — what — 你要的是把 loom 三個 plugin 裡五支腳本的白工修掉，但參數、輸出、錯誤訊息、exit code、hook 注入文字一個位元組都不變；做完後你可以：hook 每次少載一個模組、引用檢查 3 秒→0.4 秒、session-start 掃 manifest 一次、fog 檢查只開 2 個 git 子行程、validate 每張 ticket 只讀一次；對嗎？（答：OK）
1 — consequence — 任何一處做不到逐位元等價，那一處就退回不做並在報告寫明。（安全網，無分岔）
1 — what — 這次要不要用 Codex 當第二位讀者？（答：OK）

## Risks
1. Wall-clock bounds (A2's 0.4 s) are secondary in CI; every perf test's primary assertion is a deterministic count (spawns, calls, awk invocations). agent-decided.
2. `loom_checker.py` is also edited on branch `graduated-probes-survive-squash` (lines 2350-2500); W1-01 touches line 39 and `:329` only, so the later merge rebases cleanly.
3. Any of the five fixes that cannot reach byte-identical output is dropped, not softened; the blind-run report names it (intent Constraints).
4. Old-vs-new oracles must not `git show main:` at test time (CI clones lack `main`); each equivalence test carries its own pre-change fixture or a pinned pure-Python reference of the old scan.
