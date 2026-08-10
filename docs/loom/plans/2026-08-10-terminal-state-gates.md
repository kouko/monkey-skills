# Plan: terminal-state gates

Source brief: docs/loom/specs/2026-08-10-terminal-state-gates.md
Goal: 終態翻轉成為 finishing 的義務、全清單 stale 掃描在每次收官時出聲、squash-body 流失從散文提醒升級為 post-merge 紅燈
Stage: finishing
Total tasks: 4
Critical-path depth: 3 (T1 → T2 → T4；T3 ∥ T1)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-08-10, round 1, 15/15)
Endpoint recording: endpoint named: yes → continuous（/goal「把 A 跟 B 都做完」；本弧 PR-open 為終點站，never auto-merge；B 弧另立 brief/plan）

## Notes

- 業界研究引註（本 session 雙語調查）：終態不變式業界零家有（EN 臂：spec-kit/task-master/Kiro/OpenHands 皆無）；「散文必被破」兩語圈明文（Cline memory bank 官方自認無驗證；JP hash-gate CI 一文動機句）。細節在 brief。
- stale-scan 判準以今天兩個真實受害者為 fixture 形：all tasks done + Stage ∈ {sdd:wave-N, review:round-N}（一個各佔一種）。
- Action 消費 memory-grep.sh 既有契約（exit 4 + stderr 訊息），不改該腳本。
- Decision Log（T1 偏差補記）: 出貨行為除「無 Status 行」外亦靜默跳過「有 Status 帳、無 Stage 表頭」形（T1 spec-review 🟡 修正 3b2f233f，6 份真實 plan）——task Description 未回寫，以本行為準。
- Decision Log（T3 NEEDS_CONTEXT，spec 兩處被推翻）: implementer 實測發現 (1) 原 spec 旗標 `--verify` 為二值 trailer 語意、對合法無-trailer 合併（#667）誤紅，正確為 `--verify-merged`；(2) 紅燈 workflow `memory-verify-merged.yml` 已存在且今日 #681 實紅（squash `11390166` 上的 run `31353877679` failure）無人看見。裁決＝選項 (b) 擴充既有檔（deletion-first、單一閘門），T3 真正交付物收窄為「通知半邊」（PR 留言＋permissions）。工程決策兩軸皆低，記錄不上問。

## Task 1 — plan_card.py 增 --stale-scan 動詞

- Description: `loom-code/scripts/plan_card.py` 新增 `--stale-scan <plans-dir>`：走訪目錄內每個含 Status ledger 的 plan（無 Status 行的舊格式檔靜默跳過），凡「全部任務 Status 為 `done(...)` 且 `Stage:` 非 `finishing`」列為 stale 候選，輸出「<檔名>: stage=<現值> (all N tasks done)」一行一檔；無候選時輸出單行 `stale-scan: clean`。**恆 exit 0（advisory by design——all-done+review:round-N 是並行弧的合法瞬時態，紅燈會教人無視閘門）**。RED-first 測試含：兩個 fixture plan 重現今日受害者簽名（sdd:wave-1 全 done／review:round-1 全 done）→ 各自被列出；finishing 態 plan 不列；舊格式（無 Status）不列；變異探針走正式斷言（把 fixture 的 Stage 改 finishing → 該列消失）。
- Module: loom-code/scripts
- Files touched: loom-code/scripts/plan_card.py, loom-code/scripts/test_plan_card_stale_scan.py
- Context paths:
  - loom-code/scripts/plan_card.py
  - loom-code/scripts/test_plan_card.py
  - docs/loom/memory/a-mutation-test-must-run-the-production-assertion.md
- Acceptance:
  - RED: `test_plan_card_stale_scan.py` 的 sdd:wave-1 fixture 斷言在動詞實作前失敗（未知旗標 usage error——手刻解析器，非 argparse）
  - GREEN: 該檔全過；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠；對本 repo 實跑 `--stale-scan docs/loom/plans` 輸出 `stale-scan: clean`（今日已修完兩案）
- External surfaces: 無（純 stdlib 延伸既有解析器）
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #2「plan_card.py gains a --stale-scan verb … advisory by design」
- Status: done(3b2f233f)
- Gloss: 給機制一雙眼睛——每次收官時掃出「全做完卻沒收官」的殭屍帳

## Task 2 — finishing skill 終態義務 + 掃描列

- Description: `loom-code/skills/finishing-a-development-branch/SKILL.md` 兩處：(a) close-out 檢查表（§Default flow step 8 的表格）新增 **Stage-flip 義務列**——close-out commit 前，當分支有含 progress headers 的 plan 時，以雙層解析執行 `plan_card.py <plan> --set-stage "finishing"` 並將翻轉 stage 進 close-out commit；無 plan／無 Status 行照既有卡片規則靜默跳過；(b) 同表新增 **stale-scan 列**——同時執行 `--stale-scan docs/loom/plans`（雙層解析），把輸出逐字大聲轉達；候選中屬於已 merge 弧的當場修（同型翻轉），屬於並行進行中弧的說明後放行——advisory 判準寫明。兩列均為自成句、雙層解析措辭與既有列一致（repo-root 先、plugin 後備）。更新/新增釘測試（test_finishing_progress_card.py 或新斷言檔）綁定兩列存在與其雙層解析。
- Module: loom-code/skills/finishing-a-development-branch + 釘測試
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_progress_card.py
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md
  - loom-code/scripts/test_finishing_progress_card.py
- Acceptance:
  - RED: 新斷言（finishing SKILL.md 含 `--set-stage "finishing"` 於 close-out 表、含 `--stale-scan`）於編輯前失敗（現況 grep=0 已驗）
  - GREEN: 斷言過；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠
- External surfaces: `${CLAUDE_PLUGIN_ROOT}` 載入時替換（#680 已驗先例，措辭照 T2/0.71.0 既有列）
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Smallest End State #1「stage-flip duty」+ #2 後半「finishing close-out table gains a row that runs the scan」
- Status: done(582048bd)
- Gloss: 終點站從此有翻牌義務，收官時順手掃殭屍——根因和存量一次管住

## Task 3 — post-merge squash-body 驗證 Action

- Description: **擴充既有** `.github/workflows/memory-verify-merged.yml`（NEEDS_CONTEXT 發現：紅燈已存在且今日 #681 已實紅、無人看見——缺的是通知）：verify 步驟改為捕捉 exit code 不即 fail；exit 4 時（`--verify-merged` 的 wipe 形）先以 `gh pr comment`（GH_TOKEN）在 squash 標題 `(#N)` 對應 PR 留言（載體流失事實＋PR body 為存活載體＋`gh pr merge --squash --body-file` 處方一行；標題無 `(#N)` 則跳過留言仍 fail），再 exit 1 維持紅燈。`permissions` 增 `pull-requests: write`（保留 `contents: read`）。既有 WHY 註解與 `--verify-merged HEAD` 呼叫保留不動。倉庫 `scripts/test_postmerge_workflow_pin.py` 新增釘測試：workflow 檔存在、invoke `--verify-merged HEAD`、exit-4 分支含 `gh pr comment` 與 fail、`permissions` 塊含 `pull-requests: write`、trigger 為 push→main（白空間正規化文字釘，存在斷言先行）。
- Module: .github/workflows + repo scripts 釘
- Files touched: .github/workflows/memory-verify-merged.yml, scripts/test_postmerge_workflow_pin.py
- Context paths:
  - dev-workflow/skills/git-memory/scripts/memory-grep.sh
  - .github/workflows/loom-code-ci.yml
- Acceptance:
  - RED: 釘測試於 comment 步驟／permissions 擴充存在前失敗（既有檔無 `gh pr comment` 字串，grep=0）
  - GREEN: 釘測試過；`python3 -m pytest loom-code/scripts/ scripts/ -q` 全綠；YAML 語法驗證留待 CI 首跑（pin 測試只驗文字性質）
- External surfaces: GitHub Actions on-push 觸發與 GH_TOKEN 的 `gh pr comment` 權限（`permissions: pull-requests: write` 需明寫）；`--verify-merged` exit 4 契約（memory-grep.sh:274-303；實證 #681=4、#667 健康合併=0——`--verify` 二值語意誤紅已由 NEEDS_CONTEXT 排除）；今日 squash `11390166` 的 run `31353877679` failure 證紅燈已在但不可見
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State #3「post-merge GitHub Action … converting the n=4 prose reminder into a red light」
- Status: done(207eb0fc)
- Gloss: 網頁合併吃掉 body 時，紅燈自己亮、PR 上自動留言——不再靠人記得檢查

## Task 4 — 版本鏈 0.72.0

- Description: loom-code 0.71.0→0.72.0：兩份 plugin.json、CHANGELOG 0.72.0 條目（載明：--stale-scan 動詞、finishing 終態義務+掃描列、post-merge Action 屬 repo 層但隨此版記錄）；`python3 scripts/sync_codex_manifests.py loom-code` 後 `--check --all` exit 0；版本 pin 遷移 `test_docs_review_blocking_class.py` `_0_71_0`→`_0_72_0` RED-first。
- Module: plugin manifests + CHANGELOG
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
  - loom-code/scripts/test_docs_review_blocking_class.py
- Acceptance:
  - RED: pin 翻 `_0_72_0` 後因 CHANGELOG 缺 heading 而紅
  - GREEN: pin 綠；`--check --all` exit 0；`python3 -m pytest loom-code/scripts/ scripts/ loom-pipeline/scripts/ -q` 全綠
- External surfaces: marketplace 按版本發佈（不 bump 則 update 靜默 no-op，n≥2 實證）
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: Smallest End State #4
- Status: done(680f8d08)
- Gloss: 讓終態義務與掃描動詞真的隨 plugin update 到達使用者機器

## Steps

1. 掃描動詞（T1）＋ Action（T3）並行
2. 終態義務入 skill（T2）
3. 出貨版本鏈（T4）
