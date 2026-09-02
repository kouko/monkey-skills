# W3 checkpoint 審查紀錄 — 2026-09-03

## wave-end（5bf3d7c1 … c35020a6，＋99bc49fc requires-contract 降到 decision-map）
| reviewer | lens | verdict | 摘要 |
|---|---|---|---|
| sonnet-review-docs-w3 | docs 5 維＋conformance | PASS_WITH_NOTES | 26 規則／每欄位／17 skill／INDEX 數字逐項吻合；🔴 AGENTS.md 一句仍指新工作進 backlog（已修）；🔴 loom-workflow README 三語 Version 1.0.0（已修 4.0.0）；🟡 write-plan 兩表對自身 checkpoint 欄不一致（已修）；🟡 REQ-8 的 skill ≤18／形狀 ≤5 只量不 gate（已改為紅燈）；🟢 backlog 1 檔未索引（凍結，不動）。REQ 對映表：REQ-1/4 部分靠散文與記錄、REQ-9/10 一次性驗收、其餘機械可驗 |
| opus-review-code-w3 | code＋CI 逐步實跑（20 步 19 綠） | NEEDS_REVISION | 🔴 Conventional Commits 必經檢查：regex 不認 `!` 與 `ci`，加四個 `review(` 舊 commit，全分支 7 FAIL；🔴 PRINCIPLES.md 未進版控；🟠 27 個 cold-read eval 中 8 個在被指向的檔內無痕跡；🟠 check_doc_citations 目標不存在算 unchecked＝fail-open；🟠 loom-code README 說 loom-workflow 宣告 requires-contract（已改為 decision-map 才檢查）；🟠 `.claude/hooks/remind-memory-mirror.sh` 指向凍結的 backlog；🟠 principles-replay-matrix.js 兩個舊路徑常數；🟡 AGENTS「opens with」措辭；start_delivery docstring；KICKOFF standing-docs 行自相矛盾；plan 指定的 kickoff grammar 測試不存在；🟢 兩處孤兒字串 |
| opus-adversary-w3 | 對抗（15 探針） | PASS_WITH_NOTES | 攔下：未註冊 gate R1、錯版本段 budget-exception R3、CI path filter、interface-surfaces 不可縮、stub 佔位符雙 BLOCK。逃脫（important）：R4 只驗路徑（README.md／假 node id 皆過）；`--measure` baseline 行缺或 hook 缺＝靜默綠、baseline 數字可改大；凍結庫只有散文；同 Map 兩 DA 共用一份 intent。逃脫（note）：host-hygiene 自宣告豁免消音 R1；`map:` 自由文字；`counting:` 散文無綁定；push.* 只靠 host hook（接受） |
處置：c0f49194。

## 複審第二輪（f05a2ec2／98a583eb／九個 docs commit／CC regex／PRINCIPLES 簽署）
| opus-review-code-w23 | code＋CI | PASS_WITH_NOTES | 對抗 p02–p15 全翻 caught（p14 設計接受）；PRINCIPLES 簽署後 standing exit 0；doc citations 顯式懸空→exit 1；9 個 pending eval 是唯一紅；CC 檢查剩 review(×4（kouko 已改寫）＋docs+test×1（待改寫）；notes：nested ARCHIVED.md 豁免、縮排 code block、死常數（c3c4d478 已修） |
