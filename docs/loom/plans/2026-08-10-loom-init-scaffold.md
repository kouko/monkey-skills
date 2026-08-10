# Plan: loom-init scaffold verb

Source brief: docs/loom/specs/2026-08-10-loom-init-scaffold.md
Goal: 任何 repo 一個指令長出佇列層骨架（憲章實例＋DIRECTION 骨架＋目錄），自驗於真實 validator，兩個既有觸點各提供一次性 offer——零新 skill
Stage: finishing
Total tasks: 4
Critical-path depth: 2 (T1 → T4；T2 ∥ T3 ∥ T1)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-10, round 3, 15/15)
Endpoint recording: endpoint named: yes → continuous（/goal「把 A 跟 B 都做完」；本弧 PR-open 為終點站，never auto-merge）

## Notes

- 模板語意（brief 已裁決）：**起點非同步副本**（specify init constitution 同型）——鑄出即目標 repo 自有文件、蓋 vintage 戳（loom-code 版本）、無 drift 檢查。
- 落點裁決（本 session 記錄）：動詞＋模板 loom-code（與 backlog_index/plan_card 版本連動）；loom-pipeline 只加推薦列。
- **硬依賴：T4 的 loom-code bump 0.72.0→0.73.0 假設 PR #682（弧 A）已 merge**。#682 未落地前 T4 不派工；T1-T3 檔案集與弧 A 零重疊（unverified assumption——rebase 時以 #682 檔案清單 diff 定案），可先行。
- brainstorming SKILL.md 若有字數上限釘，T2 需預算（實作時先 grep ceiling 測試；有則量餘裕、必要時依棘輪慣例帶理由調升）。
- Decision Log（rebase 改寫 SHA，ledger 刷新）: #682 merge 後本分支 rebase，T1-T3 的交付 commit 被改寫（d49208e4→d5a3d508、d85893e7+d4bed08f→30eb007b+a4f2326a、fb9a4b3c→22b8be67）；whole-branch docs 臂抓到 ledger 仍記 pre-rebase 孤兒 SHA（fresh clone 不可解析），已刷新為可達 SHA。教訓：rebase 後 ledger done() 需同步刷新。
- Decision Log（T1 第二拒絕補記）: 出貨的 loom_init 除店存在外亦拒絕「DIRECTION.md 存在而店缺」（半採納形，防覆寫人寫主題）——T1 implementer 主動加入、spec 臂裁定 in-scope 硬化，brief/plan 原文未載，以本行入記錄；whole-branch 後又補強為全碰撞點先檢後寫（見補救 commit）。
- Decision Log（T2 措辭指令被審查推翻）: T2 原令 offer 用「雙層解析措辭同段既有形」；品質臂證明第一層對 loom_init 在**所有** repo 皆為死路（bootstrap 動詞的前提=repo 尚無此層，repo-root 副本結構上不存在；T1 亦不出 shim）——裁決改為**單層 plugin 指令**（`${CLAUDE_PLUGIN_ROOT}` + load-time 註記保留），釘同步改綁單層形。雙層 cascade 保留給 repo-root 副本可能存在的工具（backlog_index/plan_card）。
- Decision Log（plan-gate 2 輪上限越權，round 3）: round 2 唯一 finding 是 round-2 新增 Reuse-adequacy 塊的 source-marker 格式（封閉詞彙 `read <path>:<line>` 結尾缺失）＋兩處引用勘誤——reviewer 自開一行處方、brief 無恙非結構問題，套用後跑 round 3；本行即審計記錄（同型先例：task-mgmt-doc-currency plan round 3）。

## Task 1 — loom_init.py + 模板 + 自驗

- Description: 新增 `loom-code/scripts/loom_init.py`（純 stdlib、argv 收 repo 根路徑，預設 cwd）：(a) `docs/loom/backlog/` 已存在 → 一行說明 + exit 1，永不覆寫；(b) 建 `docs/loom/backlog/README.md`（憲章實例，內容自 `loom-code/scripts/templates/backlog-README.md` 模板——由本 repo 憲章泛化：工具路徑用 #680 雙層解析措辭、去除 monkey-skills 專屬引用）、`docs/loom/DIRECTION.md`（骨架：generated-Now 憲章 bullets + **佔位行種入的 `## Now`**（生成器對空佇列輸出的正是 `_(queue empty — bet at the next close-out)_` 一行，模板必須逐字同形，否則 `--direction-check` 整段比對即紅）+ 空 `## Next`/`## Later`，自 `templates/DIRECTION.md`）、`docs/loom/plans/`、`docs/loom/specs/`（空目錄各含一行 `.gitkeep` 或省略——實作者依 git 慣例擇一並說明）；(c) 每個鑄出檔首附 vintage 戳一行（`<!-- scaffolded by loom-init (loom-code <version>) -->` 形，版本讀自 plugin.json 相對路徑、讀不到則 `unknown`）；(d) 鑄後對新店實跑 `backlog_index.py --validate` 與 `--direction-check docs/loom/DIRECTION.md`（同目錄 sibling 解析），轉述兩者 exit code，任一非零則 exit 1。RED-first 測試（scratch repo）：refuses-if-exists；鑄出檔全存在含 vintage 戳；空店 `--validate` exit 0；`--direction-check` exit 0；變異探針走正式斷言（模板抽走 charter 必要段 → 自驗紅）。
- Module: loom-code/scripts（+ templates/ 單層子目錄，合規 skill-structure）
- Files touched: loom-code/scripts/loom_init.py, loom-code/scripts/templates/backlog-README.md, loom-code/scripts/templates/DIRECTION.md, loom-code/scripts/test_loom_init.py
- Context paths:
  - docs/loom/backlog/README.md
  - docs/loom/DIRECTION.md
  - loom-code/scripts/backlog_index.py
  - docs/loom/memory/a-mutation-test-must-run-the-production-assertion.md
- Acceptance:
  - RED: test_loom_init.py 的存在性斷言於腳本/模板存在前失敗
  - GREEN: 該檔全過；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠；scratch repo 實跑 init → `--validate`/`--direction-check` 皆 exit 0
- External surfaces: 無（純 stdlib；validator 為同 plugin sibling）
- Reuse-adequacy: Observed — `loom-code/scripts/backlog_index.py --direction-write` 對空佇列在 `## Now` 生成佔位行 `_(queue empty — bet at the next close-out)_`（本 repo 空佇列實例 docs/loom/DIRECTION.md:24），`--direction-check` 將 committed body 與 regen 輸出**整段 diff**、漂移即 exit 1；flagless `--validate` 複驗同一 Now-matches 不變式 — read loom-code/scripts/backlog_index.py:98-121. Intended — 模板逐字內建該佔位行為 `## Now` 初始 body，使鑄出即通過兩個 validator；本任務對此 seam 的重用即為 GREEN 判準本身，無需另闢驗證。
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #1 + #2
- Status: done(d5a3d508)
- Gloss: 一個指令把佇列層骨架鑄進任何 repo，鑄完立刻用真 validator 自證合格

## Task 2 — brainstorming Axis 0 offer 分支

- Description: `loom-code/skills/brainstorming/SKILL.md` ready-check 段（:72-80）：現行 N/A「no store … skip silently」改為三態——有店照舊跑 `--ready`；**無店 → 一次性 offer**（自成句：offer loom-init once——`python3 scripts/loom_init.py`，雙層解析措辭同段既有形；user 婉拒或無回應即照舊靜默前進，recommend-once 規則同 Axis 0 on-ramp、把選擇記入 brief 的 Design-side on-ramp 行）；`backlog_index.py` 兩副本皆缺照舊 N/A。不 splice 被釘句（先 grep 釘測試）。釘測試：offer 句存在＋雙層解析同列＋recommend-once 措辭；若 brainstorming 有字數上限釘，先量再依棘輪慣例處理。
- Module: loom-code/skills/brainstorming + 釘測試
- Files touched: loom-code/skills/brainstorming/SKILL.md, loom-code/scripts/test_brainstorming_backlog_read.py
- Context paths:
  - loom-code/skills/brainstorming/SKILL.md
  - loom-code/scripts/test_brainstorming_backlog_read.py
- Acceptance:
  - RED: 新釘（ready-check 段含 loom_init offer）於編輯前失敗（現況 grep loom_init = 0）
  - GREEN: 釘過；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠
- External surfaces: `${CLAUDE_PLUGIN_ROOT}` 載入時替換（既有段落同形）
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 前半（brainstorming offer once）
- Status: done(a4f2326a)
- Gloss: 沒有佇列層的 repo 在動工前會被問一次要不要長出來，問過就不再煩

## Task 3 — family-reception 推薦列（loom-pipeline）

- Description: `loom-pipeline/hooks/family-reception.md` on-ramp criteria 表新增一列：條件「repo 無 `docs/loom/backlog/`（佇列層未採納）且工作屬 loom 家族範疇」→ 推薦「suggest running loom-init once（loom-code 出貨的 scaffold 動詞）」；遵守表格既有「Recommend ONCE, never nag」規則（表下方已有，不重複）。散文描述、無 `${CLAUDE_PLUGIN_ROOT}` 字面量（hook 檔 Read 原文）。loom-pipeline/scripts/ 釘測試（test_pipeline_reception.py 或新斷言）：新列存在＋指名 loom-init＋once 措辭。
- Module: loom-pipeline/hooks + 釘測試
- Files touched: loom-pipeline/hooks/family-reception.md, loom-pipeline/scripts/test_pipeline_reception.py
- Context paths:
  - loom-pipeline/hooks/family-reception.md
  - loom-pipeline/scripts/test_pipeline_reception.py
- Acceptance:
  - RED: 新釘於編輯前失敗（現況 grep loom-init = 0）
  - GREEN: 釘過；`python3 -m pytest loom-pipeline/scripts/ -q` 全綠
- External surfaces: 無
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3 後半（reception row）
- Status: done(22b8be67)
- Gloss: 家族接待知道向沒有佇列層的 repo 指一次路

## Task 4 — 雙 plugin 版本鏈（依賴 #682 merge）

- Description: **前置：確認 PR #682 已 merge 且本分支已 rebase/含 0.72.0 基底**（未滿足 → 本任務不動工，回報等待）。loom-code 0.72.0→0.73.0、loom-pipeline 0.16.0→0.17.0：四份 plugin.json、兩份 CHANGELOG（loom-code 條目：loom_init 動詞＋模板＋自驗＋brainstorming offer；loom-pipeline 條目：reception 推薦列）；`sync_codex_manifests.py` 兩 plugin 後 `--check --all` exit 0；版本 pin 遷移 `_0_72_0`→`_0_73_0` RED-first。
- Module: plugin manifests + CHANGELOG
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
  - loom-code/scripts/test_docs_review_blocking_class.py
- Acceptance:
  - RED: pin 翻 `_0_73_0` 後紅（缺 heading/版本）
  - GREEN: pin 綠；`--check --all` exit 0；`python3 -m pytest loom-code/scripts/ scripts/ loom-pipeline/scripts/ -q` 全綠
- External surfaces: marketplace 按版本發佈（n≥2 實證）
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Smallest End State #4
- Status: done(d5c984c5)
- Gloss: 讓 init 動詞與 offer 真的隨 plugin update 到達使用者機器

## Steps

1. 骨架動詞＋兩觸點（T1 ∥ T2 ∥ T3）
2. 出貨版本鏈（T4，等 #682 落地）
