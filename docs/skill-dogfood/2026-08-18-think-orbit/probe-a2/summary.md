# think-orbit activation probe — 0.1.2 branch build (unmerged)

Wrapper verified: loaded SKILL.md contains both "owns intake" and "before inspecting" (0.1.2 fix text). 15 queries x 2 runs = 30 total, 0 timeouts.

| # | query (trunc) | expect | run1 | run2 | verdict |
|---|---|---|---|---|---|
| 0 | 幫我想一下…Redshift 搬到 BigQuery | using-think-orbit | using-think-orbit | using-think-orbit | TP-exact / TP-exact |
| 1 | 規劃明年上半年的產品路線圖… | using-think-orbit | NONE | NONE | FN / FN |
| 2 | help me think through…Tokyo office | using-think-orbit | using-think-orbit | using-think-orbit | TP-exact / TP-exact |
| 3 | plan the migration…billing vendor | using-think-orbit | using-think-orbit | using-think-orbit | TP-exact / TP-exact |
| 4 | help me decide…sunset dashboard | using-think-orbit | using-think-orbit | using-think-orbit | TP-exact / TP-exact |
| 5 | 繼續上次的決策，資料夾… | using-think-orbit | using-think-orbit | using-think-orbit | TP-exact / TP-exact |
| 6 | continue the decision…pricing | using-think-orbit | NONE | NONE | FN / FN |
| 7 | 来週の採用計画を…考えたい | using-think-orbit | using-think-orbit | using-think-orbit | TP-exact / TP-exact |
| 8 | 剛才主管說預算砍到100萬…假設破了 | break-assumption | using-think-orbit | using-think-orbit | TP-other / TP-other |
| 9 | 情況變了：對手降價20%… | break-assumption | using-think-orbit | using-think-orbit | TP-other / TP-other |
| 10 | one of my assumptions just broke… | break-assumption | using-think-orbit | using-think-orbit | TP-other / TP-other |
| 11 | 前提不成立了…Q4 預算不縮 | break-assumption | using-think-orbit | using-think-orbit | TP-other / TP-other |
| 12 | 我想針對這個問題做一次有結構的思考… | using-think-orbit | using-think-orbit | using-think-orbit | TP-exact / TP-exact |
| 13 | 想一下晚餐吃什麼 (should-NOT) | NONE | NONE | NONE | TN / TN |
| 14 | 幫我想個新產品的標語 (should-NOT) | NONE | NONE | NONE | TN / TN |

**Totals (30 runs):** TP-exact 14, TP-other-think-orbit 8, FN 4, TN 4, over-trigger 0, timeout 0.
Among the 13 prior-miss queries (26 runs): 22/26 now fire think-orbit (14 exact + 8 via `using-think-orbit` catching break-assumption cases before routing further); only #1 and #6 still miss (4/26 FN).

**Comparison vs previous run:** previous build fired only 1/26 on these 13 queries; 0.1.2 fires 22/26 -- routing materially improved. The 2 new should-NOT queries show 0 over-triggers.
