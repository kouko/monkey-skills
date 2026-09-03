# 第二家 vendor 審查改成每次決定，不再 repo 固定
originator: kouko
kind: engineering
needs-design: no — 只改站文字與一條 checker 規則讀哪個記錄；沒有使用者讀或輸入的介面，行為只有用／不用兩態
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/]
status: open

## Problem
現在要不要用第二家 vendor（Codex）做讀審，是 repo 層級一次決定、寫進 `docs/loom/KICKOFF-DEFAULTS.md` 的 `second-vendor:` 行，之後每個 change、每一輪都照做，沒有「這次先不要」的開關。kouko 在 2026-09-03 的首個真實 change（spec 審查跑到第 7 輪、每輪一臂 Codex）提出：想改成 by session／by change 決定。

## Proposed outcome
每次開始一個 change（或一個 session）時，可以說這次要不要用第二家 vendor；不說就沿用上次或 repo 預設。checker 的 `push.second-vendor-honoured` 改讀「這個 change 記錄的決定」而不是只讀 repo 的那一行，所以決定仍是重算得到、不是宣稱。

## Acceptance
1. 在一個乾淨 clone 裡，KICKOFF-DEFAULTS 寫 `second-vendor: codex` 但本次 change 記錄「不用」：審查站兩臂都跑同家、push 閘放行，不需要改 KICKOFF-DEFAULTS。
2. 反過來，本次 change 記錄「用 codex」但最後一輪沒有 Codex 裁定：push 閘照樣擋。
3. 沒有記錄本次決定時，行為與今天完全相同（沿用 KICKOFF-DEFAULTS）。

## Constraints
- 決定要留下記錄（住在 review.json 或 intent 裡，agent-decided），不能只是口頭；閘門重算、不信宣稱。
- 不動 27 條規則以外的東西；`push.second-vendor-honoured` 的語意從「讀 repo 預設」變成「讀本 change 的記錄，缺則讀 repo 預設」。

## Out of scope
- 換 vendor（gemini 等）的支援。
- 決定該由誰問、在哪個決策點問（capture-intent 的「只問一次」規則要改成什麼）——這是設計時決定。

## Open questions
- 原設計刻意不讓嚴格度變成臨場決定（concept-model §4：一個 change 內至多建議一次、答案記住）；改成每次決定會不會讓「省事就跳過」變成常態？要不要規定「不用」時必須寫理由。
- 決策點在哪：每個 change 的決策點①順便問（多一句），還是 session 開始時問一次？
