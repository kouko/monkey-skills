# Plan: wiki-ingest zero-prompt + oldest-first — part 1 (commit 1 scope)

**Source brief**: docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-17 20:59)

## Scope of this plan

**Commit 1 only** per brief §7. Subsequent commits 2 (config + `topic_filter` + `batching-policy.md`) and 3 (STEP 6 next-batch preview + dogfood) get their own plans (`part-2`, `part-3`) after commit 1 ships and dogfood surfaces any design adjustments needed. Brief items explicitly out of part-1 scope (config / topic_filter / preview) are listed in §Out of scope below and not mapped to part-1 tasks; their coverage will appear in part-2 / part-3.

## Dependency graph

```
T1 (pyproject.toml)    T2 (select-batch.py)
        \              /
         \            /
          ↓          ↓
         T3 (CC-01..04)
                ↓
         T4 (CC-05..08)
                ↓
         T5 (SKILL.md rewrite)
```

Parallel pair in SDD dispatch: (T1, T2). T3 → T4 sequential to avoid concurrent-edit collision on shared `test_select_batch.py` parametrize list. T5 sequential after T4.

---

## Task 1 — Create obsidian pyproject.toml with pytest config

- **Description**: Create `obsidian/pyproject.toml` declaring pytest dev dep (`[project.optional-dependencies] dev = ["pytest>=7"]`) + pytest discovery config (`[tool.pytest.ini_options] testpaths = ["tests"]`). pytest auto-discovers `obsidian/tests/` once T3 lands; no `__init__.py` / `conftest.py` needed for basic discovery. CI workflow (`.github/workflows/test-obsidian.yml`) deferred to part-2 — local pytest verification (run by implementer + reviewer) is sufficient for commit 1; CI fires from part-2 onward.
- **Module**: `obsidian/pyproject.toml`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/code-toolkit/pyproject.toml
  - /Users/kouko/GitHub/monkey-skills/obsidian/
- **Acceptance**:
  - **RED**: `ls obsidian/pyproject.toml` returns "No such file"
  - **GREEN**: `ls obsidian/pyproject.toml` resolves; `cd obsidian && python3 -m pytest --collect-only -q 2>&1 | grep -E "no tests ran|collected 0 items"` exits 0 (pytest config parses; testpaths resolved; empty tests/ is benign)
- **Dependencies**: none
- **Brief item covered**: §4 Test harness — "obsidian/pyproject.toml 新增 [project.optional-dependencies] dev = [pytest>=7]"

## Task 2 — Implement `select-batch.py` v1

- **Description**: Write `obsidian/skills/wiki-ingest/scripts/select-batch.py` per brief §3 contract. Inputs: stdin candidates (one vault-relative path per line), env `BATCH_ORDER` / `BATCH_CAP` / `MANIFEST_PATH` / `VAULT_ROOT`. Output: JSON `{batch, remaining, skipped_unchanged, scope_summary}`. Implements: SHA-256 hash + manifest lookup for NEW/MODIFIED/UNCHANGED bucket; 3-tier date resolution (filename `YYYY-MM-DD` → frontmatter `date|upload_date|processed_at` → mtime fallback to tail); sort by date + take cap. Python ≥ 3.10, stdlib only (no `topic_filter` arg — that's commit 2). Exit 0 normal, 2 on invalid env / unreadable manifest.
- **Module**: `obsidian/skills/wiki-ingest/scripts/select-batch.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md
  - /Users/kouko/kouko-obsidian-vault/research/2026-05-17 wiki-ingest 預設行為改造——oldest-first auto-batching 設計筆記.md
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/references/delta-tracking.md
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/scripts/scan-vault.sh
- **Acceptance**:
  - **RED**: `ls obsidian/skills/wiki-ingest/scripts/select-batch.py` returns "No such file"
  - **GREEN**: `python3 -c "import subprocess, json; r = subprocess.run(['python3', 'obsidian/skills/wiki-ingest/scripts/select-batch.py'], input='', capture_output=True, text=True, env={'BATCH_ORDER':'oldest-first','BATCH_CAP':'15','MANIFEST_PATH':'/tmp/m.json','VAULT_ROOT':'/tmp/v'}); assert r.returncode==0; assert json.loads(r.stdout).keys() >= {'batch','remaining','skipped_unchanged','scope_summary'}"` succeeds; missing env returns exit 2
- **Dependencies**: none
- **Brief item covered**: §3 select-batch.py contract — "INPUT/OUTPUT/DEPS/EXIT CODES", "Date resolution order: filename → frontmatter → mtime", "Python ≥ 3.10 stdlib only"

## Task 3 — pytest CC-01..CC-04 (filename-date cases)

- **Description**: Create `obsidian/tests/wiki_ingest/test_select_batch.py` using `@pytest.mark.parametrize` over 4 cases: CC-01 (all dated filenames → oldest-first asc), CC-02 (all undated filenames → mtime fallback asc), CC-03 (mixed: 50 dated + 10 undated → dated first by date asc, undated at tail by mtime), CC-04 (filename-prefix wins over frontmatter date). Each case = fixture dir under `obsidian/tests/wiki_ingest/fixtures/cc0N/` with `vault/` tree, `.manifest.json`, `expected.json`. Test invokes script via subprocess with appropriate env, compares stdout JSON to `expected.json`.
- **Module**: `obsidian/tests/wiki_ingest/test_select_batch.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py
  - /Users/kouko/kouko-obsidian-vault/research/2026-05-17 wiki-ingest 預設行為改造——oldest-first auto-batching 設計筆記.md
  - /Users/kouko/GitHub/monkey-skills/code-toolkit/tests/
- **Acceptance**:
  - **RED**: `pytest obsidian/tests/wiki_ingest/ -v` collects 0 items
  - **GREEN**: `pytest obsidian/tests/wiki_ingest/ -v` shows 4 PASSED: `test_select_batch[cc01]`, `test_select_batch[cc02]`, `test_select_batch[cc03]`, `test_select_batch[cc04]`
- **Dependencies**: Task 1 completes first; Task 2 completes first
- **Brief item covered**: §4 Test harness — "CC-01→CC-15 用 @pytest.mark.parametrize 一個 fixture 攤平"; §3 Date resolution order — first 4 cases validate the 3-tier resolution

## Task 4 — pytest CC-05..CC-08 (frontmatter + interaction cases)

- **Description**: Extend `test_select_batch.py` parametrize list with 4 more cases: CC-05 (frontmatter `upload_date` fallback when no filename prefix), CC-06 (NEW+MOD ≤ cap → all in batch, empty remaining), CC-07 (MOD 3 + NEW 13 = 16 with cap=15 → squeeze 1, MOD may be squeezed out), CC-08 (env `BATCH_ORDER=newest-first` → reversed dated order, undated still at tail). CC-08 documents Claude's responsibility to pass `BATCH_ORDER=newest-first` when user prompt says `latest` (SKILL.md side; verified script honors env).
- **Module**: `obsidian/tests/wiki_ingest/test_select_batch.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/tests/wiki_ingest/test_select_batch.py
  - /Users/kouko/kouko-obsidian-vault/research/2026-05-17 wiki-ingest 預設行為改造——oldest-first auto-batching 設計筆記.md
- **Acceptance**:
  - **RED**: `pytest obsidian/tests/wiki_ingest/ -v -k "cc05 or cc06 or cc07 or cc08"` collects 0 matching items
  - **GREEN**: `pytest obsidian/tests/wiki_ingest/ -v` shows 8 PASSED total (cc01..cc08)
- **Dependencies**: Task 3 completes first
- **Brief item covered**: §3 NEW vs MODIFIED interaction — "合併排序 + 合計取 cap" (CC-07); §3 Date resolution order — frontmatter fallback (CC-05); §2 Order override — "newest-first（本次 override）" (CC-08)

## Task 5 — Rewrite SKILL.md: STEP 1, strip STEP 2 Proceed? gate, insert STEP 3, renumber STEP 4-6

- **Description**: Edit `obsidian/skills/wiki-ingest/SKILL.md` per brief §1+§2 + §What Becomes Obsolete: (a) replace current STEP 1 (lines 45-65, `AskUserQuestion` three-pick) with decision table + first-line summary block per §2 format including path / single-file / time-keyword / topic-word rules; (b) **modify STEP 2 (lines 67-85)**: keep hash+bucket logic but **strip the `Proceed?` interactive gate** at line ~84 — the new STEP 3 auto-cap supersedes manual confirmation (per brief §What Becomes Obsolete bullet 2; coupling means STEP 2 `Proceed?` cannot remain when STEP 3 auto-batches); (c) insert new STEP 3 between STEP 2 and current STEP 3, describing how to invoke `select-batch.py` via stdin/env and consume JSON output (`batch`, `remaining` lists drive STEP 4 loop); (d) renumber current STEP 3/4/5 to STEP 4/5/6 (header-only changes; bodies unchanged in this commit — next-batch preview is commit 3 scope). Topic-word hint in the decision table notes `topic_filter` is `commit 2` scope; in commit 1, topic-only hints fall back to whole-vault delta with summary line annotation.
- **Module**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/docs/superpowers/specs/2026-05-17-wiki-ingest-zero-prompt-oldest-first-design.md
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/.worktrees/wiki-ingest-zero-prompt/obsidian/skills/wiki-ingest/scripts/select-batch.py
- **Acceptance**:
  - **RED**: `grep -nE '^## STEP' obsidian/skills/wiki-ingest/SKILL.md` shows only STEP 1-5; `grep -c 'AskUserQuestion' obsidian/skills/wiki-ingest/SKILL.md` ≥ 2 (default trigger still present); `grep -c 'Proceed?' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1
  - **GREEN**: `grep -nE '^## STEP' obsidian/skills/wiki-ingest/SKILL.md` shows STEP 1-6; `grep -c 'select-batch.py' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1 under STEP 3; `grep -c 'AskUserQuestion' obsidian/skills/wiki-ingest/SKILL.md` ≤ 1 (only optional-fallback mention); `grep -c 'Proceed?' obsidian/skills/wiki-ingest/SKILL.md` == 0 (gate removed); `.claude/hooks/validate-skill-folder-structure.sh` passes
- **Dependencies**: Task 2 completes first; Task 3 completes first; Task 4 completes first
- **Brief item covered**: §1 STEP structure — "STEP 1 行為換掉 / STEP 3 新增 / STEP 4-6 編號 shift"; §2 STEP 1 decision table + first-line summary; §3 — STEP 3 invokes select-batch.py via stdin+env; §What Becomes Obsolete bullet 2 — STEP 2 `Proceed?` gate removed (coupled to auto-cap behavior)

---

## Notes

- Tasks 1 + 2 are independent and can run parallel in SDD dispatch (different files / no shared state).
- Tasks 3 → 4 sequenced (not parallel) to avoid concurrent-edit collision on the shared `test_select_batch.py` parametrize list. T4 reads T3's parametrize structure then appends.
- Task 5 should wait for T3+T4 even though it only strictly needs T2, because behavior verification through the new STEP 1+3 prose benefits from tested script behind it.
- **T2 LOC budget**: select-batch.py is ~150 LOC (SHA-256 + manifest read + 3-tier date resolution + bucketing + sort+cap) — borderline for the ≤5-min implementer-task budget. Per writing-plans's BLOCKED fallback flow (Beck 2002 Child Test pattern), if the implementer subagent returns BLOCKED with decomposition signal, re-invoke writing-plans to split T2 into child tasks (likely: T2a date-resolution + T2b bucket-logic + T2c sort+cap).
- This plan ONLY covers commit 1 of the brief's 3-commit plan (§7). Brief items for commit 2 (config / topic_filter / batching-policy.md / wiki-setup template / CI workflow) and commit 3 (STEP 6 preview / CC-14..15 / dogfood) are intentionally not mapped here — they belong to `part-2` and `part-3` plans that will be written after part-1 ships.

## Out of scope (for part-2 / part-3 plans)

These brief items are explicitly NOT mapped to any task in this plan; they ship in later commits per brief §7:

| Brief item | Deferred to |
|---|---|
| `OBSIDIAN_WIKI_BATCH_ORDER` config read in SKILL.md / `select-batch.py` | part-2 |
| `topic_filter` env var + scope rule | part-2 |
| `obsidian/skills/wiki-ingest/references/batching-policy.md` | part-2 |
| `obsidian/skills/wiki-setup/SKILL.md` config template update | part-2 |
| `.github/workflows/test-obsidian.yml` (CI workflow for obsidian pytest) | part-2 (added alongside more test coverage; commit-1 uses local pytest verification only) |
| STEP 6 next-batch preview + `scope_summary` consumption | part-3 |
| CC-09..CC-15 fixtures | part-2 (CC-09..13) + part-3 (CC-14..15) |
| Dogfood on `~/kouko-obsidian-vault` | part-3 |
| PR description / changelog / version bump | finishing-a-branch phase |

## Open questions surfaced (track to part-2/3)

1. **Manifest hash re-compute avoidance** — commit 1's select-batch.py re-hashes candidates; future optimisation could pass hashes from SKILL.md STEP 2 via stdin (commit 2 candidate).
2. **CC-15 fixture boundary** — `wiki-auto-research` status interaction; mock `frontmatter.status` field directly without invoking that skill (part-3 plan to confirm).
3. **CI workflow name** — deferred to part-2 (out of part-1 scope per §Out of scope above).
