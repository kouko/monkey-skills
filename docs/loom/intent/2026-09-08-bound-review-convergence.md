# 限制 Loom review 的自動修正循環
originator: kouko
kind: engineering
needs-design: yes — review 包含初審、修正、重新設計與終止等多狀態行為，目前沒有規格界定其轉換
status: closed 2026-09-08 — PR #808

## Problem
Loom 的 reviewer 在修正後可能繼續提出新的問題，agent 也可能因為追求最安全的結果而不斷增加 review round。使用者難以判斷技術問題是否值得繼續，因此常選擇再修一輪，讓原本已完成的功能陷入長時間往返。

## Proposed outcome
每個 change 使用兩輪正常 review 加一輪重新設計後的最終驗證。Agent 在既定需求內自行判斷 blocker、修正與技術設計；到達第三輪仍有 blocker 時，本輪以未收斂結束，不再把「繼續下一輪」交給使用者決定。

## Acceptance
1. 一個 change 最多執行三輪針對不同功能內容的 review，不能透過換 reviewer、模型、round 名稱或重新設計將計數歸零。
2. 第一輪完整找問題，第二輪集中驗證修正；第二輪仍有 blocker 時，agent 能在不改變需求與保證的前提下自行重新設計，第三輪驗證該最終方案。
3. 模型格式錯誤、暫時性網路失敗或相同內容上的相同驗證重跑，不計為新的 review round，並受獨立的小型重試限制。
4. 同一 finding 連續存在、修正反覆增加相似機制或沒有減少 blocker 時，agent 能提早判斷陷入循環並改變方法。
5. 第三輪仍有 blocker 時，本輪明確結束為未收斂，不提供直接進入第四輪的選項；agent 交付根因、影響與具體替代方案。
6. 只有替代方案會改變已確認的需求、使用者可見行為或保證時，才交由使用者決定；內部技術方案由 agent 自行判斷。
7. 上述限制不恢復 committed review ledger，也不讓未解決的 blocker 被視為通過。

## Constraints
- 保留 closing Review 的兩位 fresh-context reviewer、一次 package suite、一次 adversarial execution 與 content-bound attestation。
- 既有 attestation 與 publish 邊界保持有效，publication-only 變更不重開功能 review。
- 輪數限制需適用於其他 repository，不能依賴 monkey-skills 特有的 commit 形狀。
- 先以最小 contract 與行為驗證落地；只有證明無法可靠停止時，才考慮 repo 外的最小執行狀態。

## Out of scope
- 合併 finalize-review 與 publish。
- 重做 Claude Code 或其他第二 vendor 的執行器。
- 改變 privacy gate 或 publication safety。
- 重新引入 review.json、reviewed_sha 或 finding ledger。

## Open questions
- none
