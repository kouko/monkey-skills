# 小改動車道：一個旗標的 change 二十分鐘內結束
originator: kouko
kind: engineering
needs-design: no — 改 review 站與 build 站的站文字與一條 checker 規則的計數；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-package-tests-run-in-parallel/review.json]
status: open

## Problem
第二個真實 change（整包測試加 `-n auto`＋一個依賴檔）從決策點①到 PR 花了 85 分鐘：實作 10 分、對抗＋盲跑 13 分、讀者 7 輪約 35 分、orchestrator 失誤與外部故障約 25 分。七輪裡只有第 1 輪抓到有價值的東西（README 缺 clone／venv 步驟）和對抗者抓到的一條真缺陷；其餘輪次都是「改一句話 → 兩位讀者重讀 → 再挑一個字」的迴圈：checkpoint 之後任何 commit 都要整輪重審，而一句話的事實誤差被標成 important，important 就開輪。kouko 的判準：這種 change 該在 20 分鐘內結束；review 的目的是邏輯與事實，不是把敘述修漂亮。

## Proposed outcome
1. **小改動車道**（自動判定，不問使用者）：`needs-design: no` 且 plan ≤ 2 個 task 且分支 diff ≤ 150 行（不含 docs/loom/）→ branch-end 一位 fresh reviewer＋整包測試＋對抗探針即為完整 checkpoint；盲跑只在 intent 的 Acceptance 有非機械條目（不是「跑命令、看數字」）時才派。
2. **修正輪降級**：NEEDS_REVISION 之後的修正輪只讀修正 commit（delta 從上一輪的 reviewed commit 起算，不是從上次 PASS），由原讀者複核，不重跑探針；同一 checkpoint 第三輪起自動觸發「重看設計」（既有 intent 2026-09-03-fix-round-cap-triggers-redesign）。
3. **嚴重度規則**：純措辭的事實修正（同一件事在兩處說法不一致、數字單位用語）一律 nit；nit 不開輪，累積到下一個真正的輪或 ship 前一次修完。
4. **gate／checker 類 task 先寫探針**（併入 2026-09-03-adversarial-probes-before-implementation）：plan 把 task 標成 gate 型時，build 站先派對抗者寫可執行的攻擊案例，其中一個當實作者的 RED；實作者讓它們變綠、其餘不變。
5. **第二 vendor 改成可每次決定**（併入 2026-09-03-second-vendor-per-session）：KICKOFF `second-vendor:` 多一個值 `ask`——決策點①用一句白話問「這次要不要用 Codex 當第二位讀者」，答案只管這個 change；小改動車道只有一位讀者，這題不問。既有的 `<cli>`／`none` 值行為不變。
6. 量測：下一個走小改動車道的 change，從 intent confirmed 到 `gh pr create` 的 commit 時間戳差 ≤ 20 分鐘，記在該 change 的 evidence。

## Acceptance
1. 一個符合條件的 change 走完流程，review.json 裡 branch-end 只有一位 reviewer 的 verdict、沒有 blind-run 探針（Acceptance 全機械時），`loom_checker.py push` exit 0——即 `push.verdicts-ge-2` 在小改動車道下接受 1 位（規則語意改成「車道要求的人數」，規則數不變）。
2. 一個 NEEDS_REVISION 之後的修正輪，review.json 記的 delta 起點是上一輪的 reviewed commit，且探針紀錄沒有因該輪而新增。
3. 一個只含措辭修正的 finding 記為 nit，該 checkpoint 沒有因它多開一輪（由 verdicts[] 的 round 數證明）。
4. 下一個小 change 的 confirmed→PR 時間 ≤ 20 分鐘（commit 時間戳）。
5. 一個 plan 標為 gate 型的 task，review.json 的 dispatch[] 裡對抗者的 `started` 早於該 task 實作者的 `started`，且探針檔的 commit 早於實作 commit。
6. KICKOFF 寫 `second-vendor: ask` 時，決策點①的訊息裡有那一句問題（記在 plan 的 Questions asked），該 change 的 review.json `vendors[]` 照答案記錄；`push.second-vendor-honoured` 對 `ask` 照答案而非照 KICKOFF 判。

## Constraints
- 規則數不增不減、無 waiver；改的是既有規則的計數語意與站文字。不動 `loom-code/contract/templates/**`（`second-vendor` 的文法在 manifest.yaml，不在模板）。
- 車道判定是機械的（task 數、行數、Acceptance 條目形狀），不由 agent 自由裁量、不問使用者。
- 非小改動車道的 change 一切照舊（≥2 讀者、盲跑、對抗）。

## Out of scope
- 探針重跑去重與探針畢業（另一 change：2026-09-03-push-gate-reruns-probes-per-artifact＋2026-09-03-probes-graduate-to-permanent-tests）。
- 併入本 intent 的三條（fix-round-cap-triggers-redesign、adversarial-probes-before-implementation、second-vendor-per-session）改為 `withdrawn — superseded by 2026-09-03-small-change-lane`。
- 讀者本身的行為調整（例如要求 reviewer 不翻旁邊句子）——靠嚴重度規則處理，不改 reviewer 契約。

## Open questions
- none
