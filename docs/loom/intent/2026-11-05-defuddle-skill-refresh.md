# 更新 Defuddle skill 的使用指引
originator: kouko
kind: engineering
needs-design: no — skill instructions change; no declared interface surface changes
status: confirmed 2026-11-05
intent_confirmed_sha: e7091b6

## Problem
現有 Defuddle skill 著重一般網頁，沒有說明影片逐字稿、語言選擇與擷取結果的限制，使用者可能無法從 agent 得到預期的內容，或誤認回傳的語言。

## Proposed outcome
讓 skill 的觸發描述與使用指引反映新版 Defuddle 已驗證的網頁及影片擷取能力，並清楚處理結果的限制。

## Acceptance
1. 描述提到一般網頁和 YouTube 逐字稿，讓 agent 知道何時可以使用。
2. 保留安裝、網頁擷取及 Markdown 輸出，補上影片與字幕語言的使用方式。
3. 說明指定語言不保證取得該語言；取得結果後確認字幕內容，沒有字幕或擷取失敗時如實回報。
4. 執行文件中的主要指令；用一般網頁及一兩部影片確認輸出，未測到的情況如實註明。
5. 沿用現有 skill 結構；相關索引有需要時才同步更新，內容保持簡潔。

## Constraints
- 規劃以已安裝的 Defuddle 0.19.6 與本次實測證據為起點，不假定所有影片均有字幕。
- 使用者已授權實作；發布與合併仍需另行授權。
- 額外的規則登錄、完整 agent 執行軌跡與自動觸發率測試不列為本次驗收條件。

## Out of scope
- 修改 Defuddle 本身。
- 變更本機套件安裝或其他 skill 的行為。

## Open questions
- none
