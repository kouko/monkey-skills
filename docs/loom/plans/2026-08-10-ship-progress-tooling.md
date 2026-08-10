# Plan: ship the progress tooling inside the loom-code plugin

Source brief: docs/loom/specs/2026-08-10-ship-progress-tooling.md
Goal: plan_card.py 與 backlog_index.py 隨 loom-code plugin 出貨，skill 呼叫點取得雙層解析（repo-root 優先、plugin 後備），外部 repo 不再永久靜默降級
Stage: finishing
Total tasks: 5
Critical-path depth: 4 (T1 → T2 → {T3 ∥ T4} → T5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-10, round 1, 15/15)
Endpoint recording: endpoint named: yes → continuous（/goal「修復當前發現的任務進度管理相關的機制缺陷」；PR-open 為終點站，never auto-merge）

## Notes

- Kickoff decision: SSOT 遷移方向 = 搬進 plugin（brief Alternatives #1）；repo-root 留 exec shim 保住本 repo 既有呼叫。此為 brief 已裁決事項，非 SDD 中途 fork。
- Kickoff decision: reference files（plan-format.md / family-relay.md）只用散文描述 cascade，不放 `${CLAUDE_PLUGIN_ROOT}` 字面量——替換只發生在渲染的 SKILL.md body 與 hooks.json，Read 工具讀原文不展開。
- 歷史文件（已出貨 plans、memory 條目）中的 `scripts/plan_card.py` 引用一律不改——shim 讓它們照舊可執行。
- Decision Log: brainstorming→writing-plans 的可見 checkpoint 於 goal-hook 連續授權下以本 plan 記錄代替使用者逐項簽核（前弧同型先例，記錄供審計）。
- Decision Log（post-execution 記錄更正，whole-branch docs-B 🟡）: Task 2 的 Files touched 依實際出貨 commit 78efe262 更正——移除三個實際未動的檔（test_finishing_progress_card / test_review_stage_flip_duty / test_wp_extraction_pointers，其釘全數原樣存活），補上兩個實際動到的字數上限檔（test_sdd_extraction_pointers / test_rcr_extraction_pointers，T2 report 已揭露、spec 臂已裁決接受）。純記錄面更正，非規格變更；「3 行 exec shim」同步更正為「小型」（實物 9 行）。

## Task 1 — 腳本搬進 plugin + repo-root shims

- Description: `git mv` `scripts/plan_card.py`、`scripts/backlog_index.py`、`scripts/test_plan_card.py`、`scripts/test_backlog_index.py` 至 `loom-code/scripts/`；修正測試檔內以 `__file__`/相對路徑定位腳本的常數；於 `scripts/plan_card.py`、`scripts/backlog_index.py` 原位新增小型 exec shim（argv 與 exit code 透傳）；新增 `loom-code/scripts/test_progress_tooling_shipped.py` 斷言兩腳本存在於 plugin 目錄且 `--help`/無參數呼叫回傳已知輸出。
- Module: loom-code/scripts（含 repo-root scripts/ 的 shim 對）
- Files touched: loom-code/scripts/plan_card.py, loom-code/scripts/backlog_index.py, loom-code/scripts/test_plan_card.py, loom-code/scripts/test_backlog_index.py, loom-code/scripts/test_progress_tooling_shipped.py, scripts/plan_card.py, scripts/backlog_index.py
- Context paths:
  - scripts/plan_card.py
  - scripts/backlog_index.py
  - scripts/test_plan_card.py
  - scripts/test_backlog_index.py
  - docs/loom/memory/subprocess-red-tests-go-false-green-before-the-script-exists.md
- Acceptance:
  - RED: `loom-code/scripts/test_progress_tooling_shipped.py` 的存在性斷言（`loom-code/scripts/plan_card.py` / `backlog_index.py` is_file）在搬移前失敗
  - GREEN: 該測試通過；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠（搬移後的舊測試在新位置照跑；shim 經由 `python3 scripts/plan_card.py <任一 plan>` 實跑一次驗證輸出等同直呼）
- External surfaces: 無（純 stdlib、檔案系統搬移；CI lane 覆蓋已驗證 loom-code-ci.yml:115 同時跑兩目錄）
- Dependencies: none
- Independent: false
- Brief item covered: Smallest End State #1「live in loom-code/scripts/ — inside the plugin」+ #2「Repo-root … become 3-line exec shims」
- Status: done(7ffc5624)
- Gloss: 把兩支進度工具搬進 plugin 讓它們隨安裝出貨，原路徑留轉接器不破壞本 repo 既有用法

## Task 2 — skill body 呼叫點加雙層解析 cascade + 失效宣稱修正

- Description: 於 5 個 SKILL.md 的 10 個呼叫點（subagent-driven-development:55,124；writing-plans:130；requesting-code-review:85；brainstorming:73,76；finishing-a-development-branch:102,196,294-295）把 `python3 scripts/<name>.py` 改為雙層解析：repo-root `scripts/<name>.py` 存在則用之，否則 `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py"`；同步改寫 finishing:196 被 T1 falsify 的宣稱「`backlog_index.py` absent (ships in no plugin)」為新語義（絕跡情形=plugin 未裝或 cache 缺檔，N/A 訊息保留但理由改寫）；finishing:195 的 `check_loom_memory_integrity.py` 宣稱仍為真，不動。更新釘住舊指令字面的 duty 測試（test_sdd_progress_card_duty.py、test_finishing_progress_card.py、test_finishing_backlog_close.py、test_brainstorming_backlog_read.py、test_review_stage_flip_duty.py、test_wp_extraction_pointers.py 中實際釘到的斷言）至 cascade 措辭。
- Module: loom-code/skills（單一 plugin 內 5 檔）+ 其釘測試
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md, loom-code/skills/writing-plans/SKILL.md, loom-code/skills/requesting-code-review/SKILL.md, loom-code/skills/brainstorming/SKILL.md, loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_sdd_progress_card_duty.py, loom-code/scripts/test_finishing_backlog_close.py, loom-code/scripts/test_brainstorming_backlog_read.py, loom-code/scripts/test_sdd_extraction_pointers.py, loom-code/scripts/test_rcr_extraction_pointers.py
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md
  - docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md
  - docs/loom/memory/a-mutation-test-must-run-the-production-assertion.md
- Acceptance:
  - RED: 於 test_sdd_progress_card_duty.py 新增單一參數化斷言——5 個 SKILL.md 每處 `scripts/plan_card.py`/`scripts/backlog_index.py` 呼叫點的同段落內含 `${CLAUDE_PLUGIN_ROOT}/scripts/` 後備——編輯前失敗
  - GREEN: 該斷言與全部既有 duty 測試通過；`grep -c "ships in no plugin" loom-code/skills/finishing-a-development-branch/SKILL.md` 由 2 降為 1（餘者為 :195 的真宣稱）
- External surfaces: `${CLAUDE_PLUGIN_ROOT}` 載入時文字替換——已驗證先例 investing-toolkit/tsundoku SKILL.md body、loom-pipeline hooks.json（本機 live grep 2026-08-10）；非 bash env（docs/loom/memory 及 auto-memory 雙記錄）
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #3「two-step resolution cascade」+ #4「the one claim this falsifies … is rewritten」
- Status: done(78efe262)
- Gloss: 教會五個 skill 在別的 repo 找 plugin 內建副本，並修掉搬移後變成錯誤的那句說明

## Task 3 — plan-format.md 參考檔散文更新

- Description: 更新 `loom-code/skills/writing-plans/references/plan-format.md:146-147`「when `scripts/plan_card.py` exists at the repo root」為散文版 cascade 描述（repo-root 優先、否則 loom-code plugin 出貨副本；明言不得於本檔寫 `${CLAUDE_PLUGIN_ROOT}` 字面量因 Read 不展開）；對應更新 test_plan_format_progress_fields.py 中釘住該段的斷言。
- Module: loom-code/skills/writing-plans/references
- Files touched: loom-code/skills/writing-plans/references/plan-format.md, loom-code/scripts/test_plan_format_progress_fields.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md
- Acceptance:
  - RED: test_plan_format_progress_fields.py 新增斷言（該段含 plugin 後備描述）編輯前失敗
  - GREEN: 該檔全部測試通過
- External surfaces: 無
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: Smallest End State #3「Reference files … state the cascade in prose only」
- Status: done(455c4db2)
- Gloss: 參考文件跟上新解析順序，且不放不會展開的變數字面量

## Task 4 — family-relay.md 散文更新（loom-pipeline）

- Description: 更新 `loom-pipeline/hooks/family-relay.md:78`「rendered mechanically by `scripts/plan_card.py`」為指向 loom-code plugin 出貨的 plan_card.py（repo-root 副本存在時優先）；對應更新 loom-pipeline/scripts/test_family_relay.py 若有釘住該句的斷言（無則新增一條輕量存在斷言）。
- Module: loom-pipeline/hooks
- Files touched: loom-pipeline/hooks/family-relay.md, loom-pipeline/scripts/test_family_relay.py
- Context paths:
  - loom-pipeline/hooks/family-relay.md
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py 的新/改斷言（§(a2) 段含 plugin 出貨描述）編輯前失敗
  - GREEN: `python3 -m pytest loom-pipeline/scripts/ -q` 全綠
- External surfaces: 無
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: Smallest End State #3（reference-file prose 的 loom-pipeline 側）
- Status: done(e6fecb38)
- Gloss: 家族接待文件同步指向出貨副本，別的 repo 讀到的說明不再指向不存在的路徑

## Task 5 — 雙 plugin 版本 bump + codex manifest + 版本 pin 遷移

- Description: loom-code 0.70.0→0.71.0、loom-pipeline 0.15.0→0.16.0：`python3 scripts/sync_codex_manifests.py loom-code loom-pipeline`（或逐一）後 `--check --all` exit 0；兩份 CHANGELOG 新增條目（loom-code 條目載明：兩腳本入 plugin、shim、cascade、falsified 宣稱改寫；loom-pipeline 條目載明 family-relay 措辭）；版本 pin 遷移 loom-code/scripts/test_docs_review_blocking_class.py `_0_70_0`→`_0_71_0` RED-first（翻 pin→缺 heading 紅→寫條目→綠）。
- Module: plugin manifests + CHANGELOG（機械近似但含 RED-first pin 遷移，走完整 triad）
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
  - loom-code/scripts/test_docs_review_blocking_class.py
  - docs/loom/plans/2026-08-08-progress-display-hardening.md
- Acceptance:
  - RED: test_docs_review_blocking_class.py pin 翻至 `_0_71_0` 後因 CHANGELOG 缺 0.71.0 heading 而失敗
  - GREEN: 該測試綠；`python3 scripts/sync_codex_manifests.py --check --all` exit 0；`python3 -m pytest loom-code/scripts/ scripts/ loom-pipeline/scripts/ -q` 全綠
- External surfaces: marketplace 按版本發佈（不 bump 則 update 靜默 no-op——auto-memory feedback_skill_content_pr_requires_plugin_version_bump，n≥2 實證）
- Dependencies: Tasks 3, 4 complete first
- Independent: false
- Brief item covered: Smallest End State #5「0.71.0 / 0.16.0 … codex manifests synced, version-pin test migrated」
- Status: done(baf05265)
- Gloss: 讓改動真的能透過 plugin update 到達使用者機器，版本鏈與鏡射檔一致

## Steps

1. 搬家與轉接（T1）
2. 教 skill 找 plugin 副本（T2）
3. 文件同步（T3+T4 並行）
4. 出貨版本鏈（T5）
