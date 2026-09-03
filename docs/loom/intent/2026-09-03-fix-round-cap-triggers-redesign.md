# 修正輪超過上限時，回頭重看設計，而不是繼續逐案修
originator: kouko
kind: engineering
needs-design: no — 只改審查站文字的一個係數與交回動作；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/]
status: open

## Problem
審查站寫「NEEDS_REVISION 的修正輪不計入 checkpoint 上限」，所以沒有任何東西會說「停」。首個真實 change（2026-09-03-loom-post-merge-seams）裡：W0-04 的 after-task 審查連修四輪（無條件前提、改名、刪檔、BOM），每輪修一個不同的解析邊界，到第三輪之後才有人問「為什麼要讀內容判斷」，改成結構觸發後四類一次全擋；spec 審查跑到第 8 輪，第 5 輪之後多是揭露措辭。兩次都是 kouko 或 orchestrator 手動喊停換方向，機制本身不會。

## Proposed outcome
同一個 checkpoint 連續第 2 次 NEEDS_REVISION（或同一函式／需求連續 3 條同類 finding）時，審查站不再派修正，而是把 finding 歷史整包交給一個 fresh、不同 tier 的 agent，只回答「這個判法本身對不對，有沒有更簡單的觸發條件」，輸出是一句改 spec／plan 的建議；orchestrator 依建議改 spec 或 plan 後才回到修正。

事前版本（kouko 2026-09-03 追加）：spec 鏡頭多一個維度 `deliberate-simplification`，固定一題「這條需求的判斷方式，有沒有結構性（不讀內容、不分支）的等價寫法？」——這次 W0-04 的內容觸發設計在 spec 被審六輪都沒人被要求問這題，最後由 kouko 叫 opus 才問出「重算正本比 bytes」。程式碼鏡頭已有同名維度，這是把它前移到 spec。

## Acceptance
0. `loom-code/skills/review/references/lenses.md` 的 spec 鏡頭列出 `deliberate-simplification`，一位 fresh reviewer 拿 2026-09-03-loom-post-merge-seams 的 spec v9（內容觸發版）審，會在該維度給出「改為結構觸發或重算比對」的建議。
1. 在一個乾淨 clone 裡模擬同一 checkpoint 連續兩次 NEEDS_REVISION：審查站的下一步是「重看設計」的派工記錄（role 可辨識），不是第三個 implementer 派工。
2. 重看設計的輸出若改了 spec 的一句，該 change 的 spec 走一輪窄範圍審查（只審改動句），不重審全篇。
3. 上限值寫在 KICKOFF-DEFAULTS 可調（預設 2）；不加新 checker 規則、不加 waiver。

## Constraints
- 這是既有審查站「修正輪」的係數與交回動作，不是新機制；規則數維持 27。
- 換設計後，被設計變更關閉的舊 finding 記 `resolved: closed by redesign <spec sha>`，不刪。

## Out of scope
- spec 階段的停止條件（紅隊上限、只重派 NEEDS_REVISION 的那一臂）——歸 checkpoint 係數那條 intent。

## Open questions
- 重看設計要不要回到決策點①問使用者：傾向 engineering 不問、product 只在可見行為改變時問。
- 「同類 finding」怎麼判：先用 reviewer 給的 dimension 相同＋anchor 在同一函式，不做語意分類。
