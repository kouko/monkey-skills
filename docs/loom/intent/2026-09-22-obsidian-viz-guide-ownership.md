# obsidian-viz-guide-ownership：視覺化指引只負責選呈現方式，不再和既有規則矛盾
originator: kouko
kind: engineering
needs-design: no — 只改 skill 文件、參考檔與測試；沒有使用者介面或外部依賴的檔案格式
evidence: []
status: confirmed 2026-09-22
publication: automatic — authorized 2026-09-22 by kouko

## Problem
obsidian-markdown 在 2026-09-22 加入的視覺化選擇指引，重寫了 SKILL.md §Diagrams、§Callouts 與 obsidian-mermaid-visualizer 已經負責的規則，而且內容互相矛盾：狀態機被導去自己寫流程圖、timeline／quadrant 沒有委派、「清單超過 10 項改目錄」無法執行、數字門檻沒有依據、策略表欄列方向寫反。照指引寫筆記的 agent 會產生和 skill 其他規則不一致的圖表；這三個 commit 直接進了 main，沒經過 PR 檢查，plugin 版本也沒升，使用者更新時拿不到任何修正。

## Proposed outcome
每條視覺化規則只由一個地方負責：指引只決定用圖、表、callout、清單或文字，其餘交給原本負責的段落或 skill；日後指引若又重寫這些規則，自動測試會擋下；修正以新版本發佈。

## Acceptance
1. 指引只回答「用圖、表、callout、清單還是文字」，不出現任何 Mermaid 圖種名稱，需要畫圖或選 callout 類型時連到 SKILL.md 的對應段落。
2. SKILL.md 只有一處指向指引，且措辭為建議而非強制。
3. 不看任何討論紀錄的讀者，只讀 SKILL.md 與指引，能對狀態機、數值趨勢、上下層分類、使用者指定形式、精確數值查詢等內容做出與 SKILL.md §Diagrams／§Callouts 一致的判斷。
4. obsidian 測試套件含一項檢查：指引出現 Mermaid 圖種名稱、SKILL.md 超過一處指向指引、或指引連結指不到存在的檔案或段落時，測試失敗。
5. obsidian plugin 版本升為 3.20.4（Claude 與 Codex 兩份設定一致），CHANGELOG 記錄這次變更。

## Constraints
- 不更動 obsidian-mermaid-visualizer 與 SKILL.md §Diagrams／§Callouts 的既有規則（`quadrant-chart` 拼法更正除外）。
- `docs/loom/` 是歷史紀錄：舊 intent 與舊 attestation 不改寫內容，只允許加註已被取代。

## Out of scope
- SKILL.md §Diagrams「類型不明確」的措辭改善。
- main 上既有的 wiki-setup 絕對路徑問題與 3.20.3 缺 CHANGELOG。
- 為「讀者需求不明時該用表格或時間軸」訂預設值（已決定不改）。

## Open questions
- none
