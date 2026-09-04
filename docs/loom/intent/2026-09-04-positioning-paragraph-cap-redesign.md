# 定位段的字數帽改成防漂移用途：單位由實作前的研究決定，並補上對抗者段的三方歸屬
originator: kouko
kind: engineering
needs-design: no — 只改兩份 agent 契約檔的一段文字與釘住它的測試常數；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-04-reviewer-and-adversary-positioning/review.json, docs/loom/2026-09-04-reviewer-and-adversary-positioning/blind-run-report.md, docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-adversary.txt]
status: confirmed 2026-09-04

## Problem
`loom-code/agents/reviewer.md` 與 `agents/adversary.md` 開頭的「You own…」定位段各有一個 ≤80 英文字的硬帽（`loom-code/scripts/test_review_station_text.py` 釘住）。2026-09-04-reviewer-and-adversary-positioning 的實測：帽子設在剛好裝得下內容的位置——讀者段 79/80、對抗者段 80/80——結果第一次修正輪為了守帽把 intent 明講要放的一句（「產出是主張，靠修正輪確認」）整句刪掉，讀者判 important，多跑一輪才放回去。帽子在替「這段該講幾件事」做決定，但它量的只是長度。同一個 80 在兩份檔案裡的份量也差很多：reviewer.md 全檔 1334 字（定位段佔 6%），adversary.md 526 字（佔 15%）。另外冷讀留了一個殘留：只讀對抗者契約的 agent 能 8/8 分出「哪些是我的」，但把不是自己的兩條（報告誇大、文件遺漏）讓給了實作者而不是讀者——對抗者段沒有一句說「不是我的那些，誰的是讀者的、誰的是實作者的」，而現在 0 字餘裕也塞不進去。業界標準查過：只有句長有數字（GOV.UK／ASD-STE100 一句 ≤25 詞），沒有任何標準給「一段幾個詞」；80 對不到任何出處。

## Proposed outcome
1. 帽子的角色明確定為**防漂移**（擋住「每次修正多加一句」），不是設計工具；設在明顯高於內容需求的位置。
2. 限制的**方式**要換，但**單位**（句數×句長、放寬的詞數、佔全檔比例，或別的）不在這裡拍板——plan 站先做研究再決定，決定與依據記為 agent-decided。目前只查到：句長有業界數字（GOV.UK／ASD-STE100 一句 ≤25 詞），「一段幾個詞」沒有任何出處；LLM 讀者的注意力分配沒有直接證據。研究至少要回答：哪個單位最貼近「這段講幾件事」、對兩份長度差 2.5 倍的檔案是否一致、以及切分規則能不能寫成不靠猜的測試。
3. 用新單位帶來的餘裕在對抗者段補一句三方歸屬：不是自己的那些，對帳類（遺漏、誇大、矛盾）是讀者的、正向可執行的 RED 是實作者的。讀者段不必改，除非切句規則讓它超帽。
4. 冷讀重跑一次（同一份 8 條混合清單、單讀一份契約）：對抗者側 own/not-own 維持 8/8，三方歸屬記錄下來；三方歸屬**不當驗收條件**——要變成保證得先有多次冷讀的語料，那是另一件事。

## Acceptance
1. 兩份契約的定位段各在新單位的上限內；`test_review_station_text.py` 釘住新單位，docstring 寫明計算規則（怎麼算一句／一個詞／一個比例）與選這個單位的依據；舊的 ≤80 詞斷言移除（不是並存）。
2. 對抗者段含一句把「不是我的」再分成讀者的與實作者的；文字測試斷言存在；段落仍不引用本 repo `docs/` 下任何路徑。
3. 冷讀盲跑（同 #787 的 8 條清單、同方法）：讀者側與對抗者側 own/not-own 各 8/8；三方歸屬分數寫進盲跑報告，附三輪歷史（7/8、7/8、6/8）對照。
4. 既有畢業探針（`loom-code/scripts/test_probes_positioning*.py`）裡釘 80 詞的案例同步改成新單位；整包測試綠；loom-code 版本 bump（patch）。

## Constraints
- 不加 checker 規則、不動角色數、不動站摘要表；純契約文字＋測試常數。
- 不論最後選哪個單位，都用 Python 算（詞用 `len(str.split())`；句或比例用測試裡明寫的規則），不可用 wc。
- 新上限要明顯高於現有內容的需求（帽子是防漂移，不是剛好裝得下）。
- 修正輪那段（`fix-rounds.md`，≤60 詞）的帽子不動——它不是定位段，這次不碰。

## Out of scope
- 把三方歸屬 8/8 變成驗收條件（需要多次冷讀語料，另開 intent）。
- 其他檔案的字數帽（README 節、session-start 預算、SKILL.md token 帽）。
- 「同時讀兩份契約」的冷讀（#787 盲跑報告留的另一個未驗項）。

## Open questions
- 單位選哪一個（句數×句長／放寬的詞數／佔全檔比例／其他）——plan 站研究後決定，記為 agent-decided 並附依據。
