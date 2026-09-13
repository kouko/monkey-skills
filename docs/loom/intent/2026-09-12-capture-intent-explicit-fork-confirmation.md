# 收斂 capture-intent 的內容邊界

originator: kouko
kind: engineering
needs-design: no — 只收斂既有 intent 入口與共同文件契約，不新增使用者介面或多狀態產品行為
evidence: [docs/loom/evidence/research/2026-09-11-write-spec-complexity-control-dogfood.md, docs/loom/evidence/research/2026-09-11-write-spec-owner-group-independent-audit.md, docs/loom/evidence/research/2026-09-12-capture-intent-session-audit.md]
status: confirmed 2026-09-12
publication: automatic — authorized 2026-09-12 by kouko

## Problem
capture-intent 雖然要求填滿 Problem、Proposed outcome、Acceptance、Constraints、Value case、Out of scope 與 Open questions，卻沒有明確界定每個欄位應該寫到什麼程度。Acceptance 又同時被要求能由陌生人盲跑證明，容易讓 intent 提前寫入應由 spec 決定的情境、反應與邊界細節。另一方面，固定問題數無法證明內容完整，還可能讓沒有明確詢問過的產品岔路在整體確認後被誤標成使用者已決定。

## Proposed outcome
讓 capture-intent 只確認為什麼要改、希望取得什麼結果、為什麼值得做、哪些成果必須成立，以及範圍邊界。每個欄位明確列出可以與不可以承載的內容；問題數由尚缺的必要資訊決定。草稿完成後再移出 spec 細節與工程方法，只有會改變結果或範圍的岔路需要使用者明確回答。

## Acceptance
1. 我可以從 capture-intent 的說明分辨每個 intent 欄位應該記錄的內容，以及應留給 spec 或 plan 的內容。
2. 產品 intent 會把為何值得投入放在 Value case，把必須能證明成立的交付成果放在 Acceptance；工程 intent 不會為了填格式而重複明顯的價值理由。
3. Acceptance 的每一項都是可以由外部證據判斷成立或不成立的交付成果，但不會提前列出完整情境、畫面細節、狀態轉移或實作方法。
4. capture-intent 只詢問填滿必要欄位仍缺少的資訊，不以固定問題數判斷訪談品質；既有討論與證據足夠時可以直接整理草稿。
5. 草稿中屬於 spec 的情境與反應、屬於 plan 的工程方法，以及尚未授權的產品選擇，都不會被靜默升格成已確認的 intent 內容。
6. 會改變 Problem、Proposed outcome、Value case、Acceptance 或 scope 的未決問題會讓 intent 保持 open；純 spec 或工程問題可以明確交給後續 station。
7. 會改變使用者結果或約定範圍的岔路，只有取得明確回答後才能標成 `user-decided`；接受整體覆述不等於回答未曾詢問的岔路。
8. 安裝 loom-design 與只安裝 loom-code 時會產生相同語意的 intent，且既有 Acceptance 編號、盲跑與下游對應方式維持不變。

## Constraints
- 不新增、移除或重新命名 intent 欄位；只重新定義現有欄位的責任與內容高度。
- 同步共同 intent template、contract manifest 與 code-only fallback intake，但不修改 write-spec 或 write-plan 的規劃邏輯。
- 沿用現有 Acceptance 編號、問題記錄方式、確認點與 Closing Review 的盲跑介面。
- 先用代表性 product 與 engineering 案例驗證 intent 不會膨脹成 spec，也不會遺漏已確認的結果與限制。

## Out of scope
- 改變 Requirement、Scenario、clause、task 或 test 的粒度與對應關係。
- 設計 write-spec 的完整性檢查、Requirement group 或寫後修剪流程。
- 設計 write-plan 的產品缺口退回與 task-test 對應流程。
- 引入 Ponytail 式多 agent 決策階梯或完整 grill-me 訪談。
- 新增逐句來源 ID、問題 ID、checker rule、station、subagent 或 review 循環。
- 遷移歷史 intent，或修改研究中發現的既有歷史文件問題。

## Open questions
- none
