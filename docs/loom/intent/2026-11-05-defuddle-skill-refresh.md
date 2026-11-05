# 更新 Defuddle skill 的使用指引
originator: kouko
kind: engineering
needs-design: no — skill instructions change; no declared interface surface changes
status: confirmed 2026-11-05
intent_confirmed_sha: 9ab342f

## Problem
現有 Defuddle skill 著重一般網頁，沒有說明影片逐字稿、語言選擇與擷取結果的限制，使用者可能無法從 agent 得到預期的內容，或誤認回傳的語言。

## Proposed outcome
讓 skill 的觸發描述與使用指引反映新版 Defuddle 已驗證的網頁及影片擷取能力，並清楚處理結果的限制。

## Acceptance
1. 使用者要求讀取一般網頁或 YouTube 逐字稿時，skill 的描述與指引涵蓋對應用途。
2. 影片逐字稿的指引能辨識實際回傳的語言、逐字稿缺失及擷取錯誤，不將其他內容當作逐字稿。
3. 現有網頁擷取用途保留，相關指令和新版功能的說明與可驗證行為一致。
4. 更新後的 skill 通過適用的檢查，並以代表性請求和輸出驗證上述用途與限制。

## Constraints
- 規劃以已安裝的 Defuddle 0.19.6 與本次實測證據為起點，不假定所有影片均有字幕。
- 本次請求授權規劃；實作、發布與合併不在此授權內。

## Out of scope
- 修改 Defuddle 本身。
- 變更本機套件安裝或其他 skill 的行為。

## Open questions
- none
