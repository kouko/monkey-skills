# loom 五支腳本純效能優化：每次 Bash 呼叫少載一個模組、引用檢查 1.8 秒降到 0.6 秒、三處重複讀取合成一趟，輸出逐位元不變
originator: kouko
kind: engineering
needs-design: no — 只改五支腳本的內部實作與它們的測試；命令列參數、輸出格式、exit code、hook 注入的文字一個都不動；沒有使用者讀或輸入的介面改變
evidence: [loom-code/scripts/test_check_doc_citations.py, loom-code/scripts/test_session_start_words.py, loom-workflow/skills/decision-map/scripts/test_check_map_fog.py, loom-workflow/skills/decision-map/scripts/test_map_store.py]
status: closed 2026-09-07 — branch loom-script-performance

## Problem
2026-09-07 對 loom-code／loom-design／loom-workflow 三個 plugin 的全部腳本做了一輪效能審計（兩個 fresh-context agent、cProfile 與計時實測）。大多數腳本已是單趟或本來就小，但有五處是「每次都做、多數時候不需要」或「同一件事做兩遍以上」，形狀跟 2026-09-06 memory-grep 那次（逐 commit 開子行程→單趟 git，19.9 秒→0.09 秒）一樣：

1. `loom-code/scripts/loom_checker.py:39` 在模組頂層 `import yaml`。這支腳本是 PreToolUse hook，**每一次 Bash 工具呼叫**都會執行；非 push 指令走 `--hook` 快速路徑，根本不會呼叫 `load_manifest()`（唯一用到 yaml 的地方），卻每次都付 8.7 毫秒（實測 `-X importtime`）的載入成本。
2. `loom-code/scripts/check_doc_citations.py:235-266` 的 `resolve_cited_path` 與 `_is_explicit_path_citation_with_no_match` 對每條引用把全 repo 4,924 個檔案路徑做一次 `endswith` 線性掃描。本 repo 1,652 份 markdown、3,311 條引用 → 1,810 萬次 `endswith`，cProfile 下 2.99 秒裡佔 1.6 秒。
3. `loom-code/hooks/session-start:48-74` 的 `stations_block()`（awk 掃 manifest.yaml）被呼叫四次：一次取站名、`stations_for_dp` 對三個決策點各一次，四次讀同一份 343 行的檔。每次 session start／clear／compact 都付 15-30 毫秒（hook 總長 50-70 毫秒）。
4. `loom-workflow/skills/decision-map/scripts/check_map_fog.py:110-141` 的 `read_base_graduated_ids` 先 `git ls-tree` 列出 base ref 的 ticket 檔，再**對每一張 ticket 各開一次 `git show`**。每次 spawn 30 毫秒（實測），20 張 ticket 就是 600 毫秒。
5. `loom-workflow/skills/decision-map/scripts/map_store.py:1379、1536`（`_check_tickets` 與 `_check_monotonic_relations`，都由 `validate()` 呼叫）以及 `map_transaction.py:404-415`（`_update_blockers_locked`）都在同一次呼叫裡對 tickets 目錄 `glob("*.md")` 加 `read_ticket()` 各做兩趟，同一組檔讀了兩次、解析了兩次。今天 5 張 ticket 只差 0.3 毫秒，但 decision-map 是跨 session 長期成長的 store，浪費隨張數線性放大。

## Proposed outcome
1. `loom_checker.py`：`import yaml` 搬進 `load_manifest()`（lazy import）；其他八處呼叫 `load_manifest()` 的路徑行為不變。
2. `check_doc_citations.py`：從 `repo_files` 建一次「basename → 完整路徑清單」的索引，`resolve_cited_path` 與 `_is_explicit_path_citation_with_no_match` 兩處都改用它，只對同 basename 的候選做 `endswith`。zero／one／multiple 三種判斷語意完全不變（同 basename 是 suffix match 的必要條件）。**兩處必須吃同一個索引**，不可只改一處。
3. `session-start`：`stations_block` 的輸出算一次存進變數，`stations_for_dp` 改對那個字串做 sed，awk 由四次降為一次。注入的文字逐位元不變。
4. `check_map_fog.py`：`ls-tree` 改帶 blob SHA，用一次 `git cat-file --batch` 餵全部 SHA 讀出內容，取代逐張 `git show`；錯誤訊息與 `SchemaViolation` 的觸發條件不變。
5. `map_store.py` 與 `map_transaction.py`：ticket 集合讀一次、解析一次，交給兩個 check／兩個 dict 共用；validate 的 finding 順序與內容不變。
6. **看得見的行為零改變**：五支腳本的參數、輸出、exit code、hook 注入文字全部照舊。既有測試不動一字、全綠；每處各加一個等價測試或計時測試。
7. loom-code 與 loom-workflow 版本各 bump 一次，CHANGELOG 記改前改後數字與量測方法。

## Acceptance
1. **loom_checker hook 路徑**：在本 repo 執行 `python3 -X importtime loom-code/scripts/loom_checker.py push --hook` 餵一條非 push 指令（例如 `echo hi`），importtime 輸出中不再出現 `yaml`；exit code 仍為 0。餵一條 `git push` 指令時 `load_manifest()` 仍正常載入 manifest（既有 push 規則測試全綠）。
2. **check_doc_citations**：在本 repo 對全部 markdown 跑 `python3 loom-code/scripts/check_doc_citations.py`（用它現有的參數形式），改前與改後的 stdout、stderr、exit code `diff` 全空；wall time 從 ≥1.2 秒降到 ≤0.6 秒（盲跑報告寫出量測指令與兩邊秒數；原寫 ≤0.4 秒是規劃時從 profile 推估的數字——kouko 2026-09-07 於 branch-end review 後核可改為 ≤0.6 秒：實測 1.77 秒→0.57 秒、CPU 時間 0.56 秒，剩餘時間是開 3,383 個檔案與比對本身，不在本 change 的「消除白工」範圍）。沙盒裡造「同 basename 出現在兩個目錄」「引用帶 `/` 但零命中」「裸檔名零命中」三種引用，改前改後輸出逐位元相同。
3. **session-start**：`bash loom-code/hooks/session-start </dev/null` 在本 repo 與一個空 git repo 各跑一次，改前改後 stdout 逐位元相同（`diff` 全空）；`test_session_start_words.py` 的字數上限測試仍綠；腳本裡 `awk` 對 manifest 的呼叫由 4 次變 1 次（`bash -x` 計數）。
4. **check_map_fog**：本 repo 的 decision-map（或沙盒裡造一張 20 張 ticket 的地圖，其中若干張帶 `graduated-from`）跑 `read_base_graduated_ids`，改前改後回傳的集合相同；`bash -x`／`strace` 等價計數顯示 git 子行程由 1+N 次降為 2 次；base ref 缺 ticket 目錄、某張 ticket 無法解析兩種錯誤情境的 `SchemaViolation` 訊息逐字相同。
5. **map_store／map_transaction**：對同一張地圖跑 `validate()` 與 `update-blockers`，改前改後的 finding 清單（順序、文字）與寫回的檔案逐位元相同；以 monkeypatch 計數 `read_ticket()` 的呼叫次數，validate 由 2N 降為 N，`_update_blockers_locked` 由 2N 降為 N。
6. **既有測試不動**：`test_check_doc_citations.py`、`test_session_start_words.py`、`test_check_map_fog.py`、`test_map_store.py` 與 loom_checker 全部既有測試檔 diff 為零、全綠；整包測試（KICKOFF-DEFAULTS 的 package-tests 指令）全綠。
7. loom-code 與 loom-workflow `plugin.json` 各 bump 一次，兩份 CHANGELOG 各有一行寫改前改後數字與量測方法。

## Constraints
- 五處都是純效能修：不新增參數、不改輸出、不改錯誤訊息、不改 exit code；任何一處做不到逐位元等價就把那一處退回不做並在盲跑報告寫明。
- `session-start` 維持 bash 3.2 相容（macOS 預設），注入文字受 `test_session_start_words.py` 的字數上限守著。
- `check_map_fog.py` 用 `git cat-file --batch` 時要保留「某一張讀不到就整體拋 `SchemaViolation`」的語意，不可靜默跳過。
- `loom_checker.py` 同時有 `.codex/hooks/loom_checker.py` 鏡射副本，改完要跑 repo 的 sync 腳本讓兩份一致。
- 與另一個進行中的分支 `graduated-probes-survive-squash` 同檔不同段（它改 `loom_checker.py` 第 2350-2500 段），後合併者 rebase 即可。
- 走 loom 預設 full 車道，第二讀者 Codex（kouko 2026-09-07 於決策點①同意）。

## Out of scope
- 審計時判定「已是單趟或本來就小」的腳本：`loom_checker.py` 規則引擎本身、`check_mechanisms.py`、`rehearse_probes.py`、`codex_scaffold.py`、`lang_detect.py`、`language-anchor.py`、`distill-sessions/*`、`privacy-scan.py`、`cot-explain/*`、`validate_header.py`、`goal_lint.py`、`delivery_evidence.py`、loom-design 全部腳本。
- `memory-grep.sh`（2026-09-06 已做）。
- 任何功能、輸出格式或錯誤訊息的改變；加快取檔。
- 五支腳本所屬 SKILL.md 的文字。

## Open questions
- none
