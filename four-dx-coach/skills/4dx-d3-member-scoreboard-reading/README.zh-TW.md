# 4DX D3 — Member Scoreboard Reading

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Team-member 範疇 — 讀 leader 設計好的 team scoreboard。診斷 5-second test、定位個人貢獻、抓 calibration drift、用非對抗的方式 surface 板子壞掉的訊號。

## 何時觸發這個 skill

- 「我們 team 的 scoreboard 怎麼看」
- 「scoreboard 有但跟我有什麼關係不知道」
- 「我們的 scoreboard 看了也看不出在贏」
- 「scoreboard 的目標線好像跟現實對不上」
- 「team の scoreboard をどう読む？」「自分の貢献が見えない」

## 它做什麼（protocol 摘要）

≤5 分鐘週次 diagnostic — 把 leader 的設計準則反向變成 member 的閱讀準則。不重新設計。

1. **comprehension 守門** — 定位 scoreboard 載體 / 是否能看；team 完全沒板 → 退回 D3-team-design
2. **5-second test（member 側）** — 在贏 / 在輸 / 看不出？「看不出」是 data，不是 member 的問題
3. **per-lead 定位個人貢獻** — 我的工作從哪卡進去？任一 lead 都無法 → D2 影響力地圖 gap
4. **focus lead trend read** — 上週 vs 前週、有沒有上 / 平 / 下、在 / 不在 pacing 線上；我的活動能合理解釋嗎？
5. **calibration check** — pacing / target / 定義 是否跟現況對得上？
6. **決定：讀完還是升報** — 任一 flag 起（5-sec 失敗 / drift / 隱藏 / 過時），起草非對抗的 ask
7. **輸出 read card** — 載體 / 5-sec / 貢獻 / trend / calibration / flags / escalation 狀態

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| 設計 scoreboard（solo / leader） | `4dx-d3-personal-scoreboard` / `4dx-d3-team-lead-scoreboard-design` |
| team 完全沒有 scoreboard | step 1 直接 halt；請 leader 跑 `4dx-d3-team-lead-scoreboard-design` |
| 準備本週 commitment | `4dx-d4-member-commitment-prep`（會消費這個 read） |
| 沒做到的 commitment debrief | `4dx-d4-member-account-debrief`（也消費這個 read） |
| D2 影響力地圖 gap（任一 lead 都定位不到自己） | 先 `4dx-d2-member-lead-measure-influence` |
| BI / KPI / executive scorecards | 不在 4DX 範圍 |

## 出處

⚠️ V1 partial — 第 4 章 + 第 14 章是 leader 設計視角，member 閱讀是把四項設計準則對稱反轉 + 兩個 member only 步驟（locate-contribution、escalate-if-broken）。三個 mirror 案例：Younger Brothers（一名 framer 看 6 個 safety lead 並把昨天某一格往自己的某個 shift action 連回去）、Towne Park valet（用可見 retrieval-time 板做每班次貢獻審計）、Northrop Grumman / Hurricane Katrina 倒下的球場記分板（member 看不出分數 = 板子的訊號，不是 member 能力問題）。Industry grounding：Tufte 1983/2001（chartjunk 拖慢 trend 感知）、Eurich 2017（95/15 自覺差距 → step 4 的「plausibly」緩衝）、Argyris 1986（step 6a 的 Model-II 升報腳本）。

member 側 coach's-as-players' 取代、status-without-trajectory、scoreboard-as-trophy 虛榮策展、member-substitution 失敗、reading-as-procrastination，以及 escalation 步驟的高 context 文化 + psychological safety 注意，見 [`SKILL.md`](SKILL.md)。
