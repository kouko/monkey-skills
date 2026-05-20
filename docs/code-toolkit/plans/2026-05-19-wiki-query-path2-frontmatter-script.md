# Plan: wiki-query Path 2 — frontmatter script as Tier 1 entry

**Source brief**: docs/code-toolkit/specs/2026-05-19-wiki-query-path2-frontmatter-script.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-19, 14/14 checks)

## Plan-stage findings (resolved ⚠️ items from brief)

- **wiki-cross-linker** 確實 Read `wiki/index.md`（[SKILL.md:13 pre-flight + L17 STEP 1](../../../obsidian/skills/wiki-cross-linker/SKILL.md)）→ Path 2 後 index.md stale，cross-linker 會漏新 page → 必須改用 directory glob（**T5**）
- **wiki-lint L08** 實際是 *Stale pages* warning，非 frontmatter completeness。真正檢查 `summary` 必填的是 **L01**（error 級），已強制 → **無需升級**，brief ⚠️ flag resolved as no-op
- **wiki-query Pre-flight L16** check `wiki/index.md` empty → 改檢查 `wiki/scripts/query-frontmatter.py` 存在 或直接移除（**T3** 內含）

## Execution wave 圖

```
Wave 1:  T1 (script MVP)
            ↓
Wave 2:  T2 (script multilingual + edge)
            ↓
Wave 3:  T3 ∥ T4 ∥ T5   (three SKILL.md edits, disjoint files, parallel-dispatch eligible)
```

---

## Task 1 — `query-frontmatter.py` MVP（happy-path English query）

- **Description**: 建立 `query-frontmatter.py` 骨架：CLI 解析 → 走訪 `wiki/{entities,concepts,references,skills,journal,synthesis}/*.md` → 手寫 mini YAML parser 抽 `title`/`type`/`summary`/`tags` → 對 keywords 做 lowercase substring scoring（title=3 / tag=2 / summary=1）→ JSON dump top-K
- **Module**: `obsidian/skills/wiki-query/scripts/`
- **Files touched**: `obsidian/skills/wiki-query/scripts/query-frontmatter.py`, `obsidian/skills/wiki-query/tests/test_query_frontmatter.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/references/page-format.md
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/scripts/select-batch.py
- **Plan amendment (post-T1 implementation)**: Fixtures are built at pytest `tmp_path` runtime rather than persisted on disk. Reason: `.claude/hooks/validate-skill-folder-structure.sh` forbids depth-4 nesting (`tests/fixtures/vault/wiki/entities/...` violates Anthropic skill-folder convention enforced in this repo per `CLAUDE.md`). tmp_path pattern keeps fixture vault layout identical for test correctness while satisfying hook.
- **Acceptance**:
  - **RED**: `tests/test_query_frontmatter.py::test_happy_path_top_k_by_score` 失敗（`ModuleNotFoundError: query_frontmatter` 或 `FileNotFoundError`）
  - **GREEN**: 同 pytest 通過；命令列 `python3 obsidian/skills/wiki-query/scripts/query-frontmatter.py --keywords "TSMC" --top 3 --vault-root obsidian/skills/wiki-query/tests/fixtures/vault` 輸出合法 JSON array，TSMC 在 rank 1 且每筆含 `path`/`title`/`type`/`summary`/`tags`/`score` 欄位
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: Smallest End State 第 1 項「新增 `obsidian/skills/wiki-query/scripts/query-frontmatter.py` ~80 行 stdlib Python」（MVP 骨架部分）；Decision Q1（LLM 傳 keyword list）；Decision Q3 中的 lowercase substring 基底；技術選擇「純 Python stdlib only，single file」

---

## Task 2 — `query-frontmatter.py` 多語言 + 邊界

- **Description**: 在 T1 骨架上加 NFKC normalize + CJK substring + `--type` optional filter + 邊界處理（空 keywords / 0 候選 / 缺 `summary` 欄位的 page 該被跳過）；新增 `tests/conftest.py` 加入 `sys.dont_write_bytecode = True` 抑制 `__pycache__`（被 skill-folder hook 擋）
- **Module**: `obsidian/skills/wiki-query/scripts/`
- **Files touched**: `obsidian/skills/wiki-query/scripts/query-frontmatter.py`, `obsidian/skills/wiki-query/tests/test_query_frontmatter.py`, `obsidian/skills/wiki-query/tests/conftest.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-query/scripts/query-frontmatter.py
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-query/tests/test_query_frontmatter.py
- **Plan amendment (post-T1 implementation)**: T2 inherits T1's `tmp_path` fixture pattern — CJK page (台積電) + fullwidth-test page 於 pytest runtime 建構，不持久化到磁碟（same skill-folder hook constraint as T1）；同時新增 `tests/conftest.py` 抑制 `__pycache__`，讓 pytest 不需 `PYTHONDONTWRITEBYTECODE=1` env var 即可在 CI 直接跑。
- **Acceptance**:
  - **RED**: 以下 pytest 全部失敗：`test_nfkc_normalize_fullwidth`（keyword "ABC" 命中 summary 含 "ＡＢＣ"）/ `test_cjk_substring_matches`（keyword "晶圓" 命中 summary "世界最大晶圓代工廠"）/ `test_type_filter_restricts_dir`（`--type entities` 排除 references/）/ `test_missing_summary_field_skipped`（缺 `summary:` 的 page 不進候選）/ `test_empty_keywords_returns_empty_array`
  - **GREEN**: 同 5 個 pytest case 全通過；`unicodedata.normalize('NFKC', ...)` 在 score 函式內被呼叫；`--type` 為 optional CLI flag
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Decision Q2（type filter optional）；Decision Q3（`unicodedata.normalize('NFKC', s).lower()` + Python `in` substring）；Smallest End State 第 1 項剩餘的多語言 + edge case 完備性

---

## Task 3 — `wiki-query/SKILL.md` STEP 2 重寫 + Pre-flight + retrieval-tiers.md

- **Description**: 拔掉 `Read wiki/index.md` 成為 Tier 1 入口的設計；改為「LLM 從使用者問題抽 keywords → 呼叫 `wiki/scripts/query-frontmatter.py` → 收 ranked JSON 含 summary → Tier 2 判斷」。同步 retrieval-tiers.md Tier 1 契約描述。Pre-flight 第 3 點改檢查 script 存在或移除
- **Module**: `obsidian/skills/wiki-query/`（prose-only edit）
- **Files touched**: `obsidian/skills/wiki-query/SKILL.md`, `obsidian/skills/wiki-query/references/retrieval-tiers.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-query/scripts/query-frontmatter.py
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-19-wiki-query-path2-frontmatter-script.md
- **Acceptance**:
  - **RED**: `grep -c 'Read \`wiki/index.md\`' obsidian/skills/wiki-query/SKILL.md` ≥ 1（編輯前現況）
  - **GREEN**: `grep -c 'Read \`wiki/index.md\`' obsidian/skills/wiki-query/SKILL.md` == 0；`grep -c 'query-frontmatter.py' obsidian/skills/wiki-query/SKILL.md` ≥ 1；`grep -c 'query-frontmatter.py\|frontmatter script' obsidian/skills/wiki-query/references/retrieval-tiers.md` ≥ 1；`grep -ci 'index.md is empty' obsidian/skills/wiki-query/SKILL.md` == 0
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State 第 2 項「改寫 `wiki-query/SKILL.md:26-37` STEP 2」+ 第 4 項「Pre-flight 第 3 點改寫」；What Becomes Obsolete「`wiki-query/SKILL.md:30` 讀 index.md 移除」+「retrieval-tiers.md Tier 1 契約同步」

---

## Task 4 — `wiki-ingest/SKILL.md` STEP 4e 改成 banner 模式

- **Description**: STEP 4e 不再 append 新 page 連結到 `wiki/index.md`；改為「確保 `wiki/index.md` 開頭有 stale banner（如不存在則 prepend 一次性）」+ 註明 LLM Tier 1 已由 `wiki-query/scripts/query-frontmatter.py` 接手，本檔僅作 Obsidian 端歷史快照
- **Module**: `obsidian/skills/wiki-ingest/`（prose-only edit）
- **Files touched**: `obsidian/skills/wiki-ingest/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-19-wiki-query-path2-frontmatter-script.md
- **Acceptance**:
  - **RED**: `grep -c 'Append the new page link' obsidian/skills/wiki-ingest/SKILL.md` == 1（編輯前現況）
  - **GREEN**: `grep -c 'Append the new page link' obsidian/skills/wiki-ingest/SKILL.md` == 0；`grep -ci 'stale banner\|stale snapshot\|historical snapshot' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1；`grep -c 'query-frontmatter.py' obsidian/skills/wiki-ingest/SKILL.md` ≥ 1
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State 第 3 項「`wiki-ingest/SKILL.md:253-255` STEP 4e 改成『加 stale banner，停止 append』」；Decision Q5「保留檔案 + 加 stale banner + wiki-ingest STEP 4e 停止 append」

---

## Task 5 — `wiki-cross-linker/SKILL.md` 改用 directory glob 取代 index.md scan

- **Description**: Pre-flight L13 check 「`wiki/index.md` is empty」改為「`wiki/` directory 是否含任何 `.md`」；STEP 1 L17「Read `wiki/index.md` and gather all page titles」改為直接 glob `wiki/{entities,concepts,references,skills,synthesis,journal}/*.md`，逐檔取 frontmatter `title` 或 filename slug 作 inventory。原因：Path 2 後 index.md 是 stale snapshot，cross-linker 倚賴它會漏新 ingest 的 page
- **Module**: `obsidian/skills/wiki-cross-linker/`（prose-only edit）
- **Files touched**: `obsidian/skills/wiki-cross-linker/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/scripts/scan-vault.sh
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-19-wiki-query-path2-frontmatter-script.md
- **Acceptance**:
  - **RED**: `grep -c 'Read \`wiki/index.md\`' obsidian/skills/wiki-cross-linker/SKILL.md` == 1；`grep -c 'wiki/index.md\` is empty' obsidian/skills/wiki-cross-linker/SKILL.md` == 1（編輯前現況）
  - **GREEN**: `grep -c 'Read \`wiki/index.md\`' obsidian/skills/wiki-cross-linker/SKILL.md` == 0；`grep -ci 'glob\|directory scan\|wiki/\*\*/\*\.md\|wiki/{entities' obsidian/skills/wiki-cross-linker/SKILL.md` ≥ 1；Pre-flight 第 2 點不再 reference index.md
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: What Becomes Obsolete「wiki-cross-linker 對 index.md 的掃描（若有）⚠️ plan 階段確認，必要時同 PR」— plan 階段確認結果：有，且需同 PR 改

---

## Notes

- Wave 3 三任務 `Independent: true` 且 `Files touched` 完全 disjoint（`wiki-query/`、`wiki-ingest/`、`wiki-cross-linker/` 三個 skill 各自獨立檔案），符合 `dispatching-parallel-agents` 觸發條件 — SDD 可在一條 assistant message 內 3 個 `Agent` calls 並行 dispatch implementer。
- Wave 1 T1 + Wave 2 T2 為 sequential（同 `query-frontmatter.py` 檔，後者擴充前者），雙雙 `Independent: false` 屬正確標註。
- Brief 中提及的 wiki-lint L08 升級項目在 plan-stage recon 後確認為 no-op（L01 已強制 `summary` 為 error 級必填），不列為 task；本決議在頂部 §Plan-stage findings 已記錄。
