# 既有對抗探針畢業成永久測試
originator: kouko
kind: engineering
needs-design: no — 只新增測試檔；沒有使用者讀或輸入的介面，也沒有多狀態行為
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/probes/, docs/loom/2026-09-03-package-tests-run-in-parallel/evidence/probes/, docs/loom/2026-09-03-small-change-lane/evidence/probes/]
status: confirmed 2026-09-04

## Problem
對抗者寫的探針（可執行的攻擊案例）住在 `docs/loom/<change-id>/evidence/probes/`，是該 change 的證據，不在 repo 的整包測試命令裡；merge 後沒有東西會再跑它們。PRINCIPLES 第 2 條說每個事故要變永久 eval，但主幹上三個已 merge 的 change 共 4 個探針檔、54 個案例，全部只是歷史。原本以為 2026-09-03-loom-post-merge-seams 會在 W1-04 順手畢業自己的 21 個，實際沒做。

## Proposed outcome
把主幹上 4 個探針檔裡、既有永久測試沒蓋到的案例，搬進本 repo 的永久測試目錄（`loom-code/scripts/test_*.py`），整包命令跑得到；evidence 原檔不刪不改。搬＝複製、改檔名與 import 路徑，不重寫成別的 fixture。這是回溯一次性的搬家；「每個 change 在 ship 時自動畢業」的機制另外做（見 Out of scope）。

## Acceptance
1. 主幹上 4 個探針檔的案例出現在 `loom-code/scripts/` 的測試檔裡，整包命令（KICKOFF 的 package-tests 行）收集並跑過它們，全綠；4 個 evidence 原檔的內容與 main 上一字不差。
2. 搬進來的測試函式名沒有一個與既有 `loom-code/scripts/test_*.py` 裡的函式同名；被略過的案例在 plan 或 commit 訊息裡逐一點名，附一句「既有哪個測試已蓋到」。
3. 整包命令的 wall-clock 時間增加不超過 4 個探針檔單獨跑的 wall-clock 時間總和（兩邊都用同一台機器、同一個 `-n auto` 量）。
4. 這個 change 從 intent 確認到 push 閘乾跑通過，不超過 20 分鐘（小車道首測；時間以 commit 時間戳為準）。

## Constraints
- 只新增測試檔，不動 checker、skill、standing 文件、KICKOFF；這樣才落在小車道，Acceptance #4 才量得到小車道本身。
- 套件變慢的問題另立 intent（共用 fixture、少開子程序），不用「不畢業」來省。

## Out of scope
- ship 站 memory 步驟「每個 change 自己畢業探針」的那句話與慣例——改 skill 會把車道拉成完整，併進下一個完整車道的 change（templates-glob／stale-open-questions／squash-needs-design 那組）做。
- 本 change 自己的對抗探針不畢業（它們測的是搬家本身，不是產品行為）。

## Open questions
- 「不重疊」這次只用函式名判；斷言目標行為的重疊要不要機械判，量幾個 change 後再說。
