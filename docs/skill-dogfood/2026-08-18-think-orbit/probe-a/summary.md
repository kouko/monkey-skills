# Dogfood Probe A — think-orbit activation harness

TP exact-skill: 12/40 | TP wrong-think-orbit-skill: 3/40 | FN (no fire): 25/40 | TN: 14/14 | Over-trigger: 0/14

| # | query | expect | run1→routed | run2→routed | verdict |
|---|---|---|---|---|---|
| 0 | 幫我想一下下半年要不要把團隊從 Redshi | using-think-orbit | (none) | (none) | ISSUE |
| 1 | 我要決定 Q4 行銷預算怎麼分配，先幫我把思 | using-think-orbit | thinking-session | using-think-orbit | ISSUE |
| 2 | 規劃明年上半年的產品路線圖，我手上有三份會議 | using-think-orbit | (none) | (none) | ISSUE |
| 3 | 想清楚要不要接這個顧問案，來回想幾週了 | using-think-orbit | using-think-orbit | using-think-orbit | PASS |
| 4 | 整理一下我對「要不要換供應商」這件事的思路， | using-think-orbit | using-think-orbit | using-think-orbit | PASS |
| 5 | help me think through  | using-think-orbit | (none) | (none) | ISSUE |
| 6 | plan the migration to  | using-think-orbit | (none) | (none) | ISSUE |
| 7 | figure out with me whi | using-think-orbit | using-think-orbit | using-think-orbit | PASS |
| 8 | help me decide whether | using-think-orbit | (none) | using-think-orbit | ISSUE |
| 9 | 用 think-orbit 開一個新的思考： | using-think-orbit | thinking-session | using-think-orbit | ISSUE |
| 10 | 繼續上次的決策，資料夾 ./decision | using-think-orbit | (none) | (none) | ISSUE |
| 11 | continue the decision  | using-think-orbit | (none) | (none) | ISSUE |
| 12 | 決策推演：新產品定價的三個方案，幫我建立推理 | using-think-orbit | using-think-orbit | using-think-orbit | PASS |
| 13 | 来週の採用計画をじっくり考えたい。資料は . | using-think-orbit | (none) | (none) | ISSUE |
| 14 | 剛才主管說預算砍到 100 萬，我覺得我們的 | break-assumption | (none) | (none) | ISSUE |
| 15 | 情況變了：對手上週降價 20%，之前那條假設 | break-assumption | (none) | (none) | ISSUE |
| 16 | one of my assumptions  | break-assumption | (none) | (none) | ISSUE |
| 17 | 前提不成立了，那個「Q4 預算不縮」的假設要 | break-assumption | (none) | (none) | ISSUE |
| 18 | 幫我把「要不要收掉東京辦公室」這件事想透，並 | using-think-orbit | thinking-session | using-think-orbit | ISSUE |
| 19 | 我想針對這個問題做一次有結構的思考，之後可以 | using-think-orbit | (none) | (none) | ISSUE |
| 20 | 幫我加一個 CSV 匯出功能到 report | NONE | (none) | (none) | PASS(TN) |
| 21 | review my branch befor | NONE | (none) | (none) | PASS(TN) |
| 22 | critique this proposal | NONE | (none) | (none) | PASS(TN) |
| 23 | 幫我把這段對話存成 Obsidian 筆記 | NONE | (none) | obsidian-tldr | PASS(TN) |
| 24 | 畫一張心智圖整理這篇文章 | NONE | (none) | (none) | PASS(TN) |
| 25 | 這個說法對嗎：Redshift 的 SORT | NONE | fact-check | fact-check | PASS(TN) |
| 26 | brainstorm the design  | NONE | brainstorming | brainstorming | PASS(TN) |
