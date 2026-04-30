# 4DX D3 — Member Scoreboard Reading

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Team-member スコープ — leader が設計した team scoreboard を読む。5-second test の診断、個人貢献の locate、calibration drift の発見、壊れている場合の非対立的 surface を行う。

## このスキルが起動するとき

- 「team の scoreboard をどう読む？」「自分の貢献が見えない」
- 「scoreboard を見ても勝ってるのか分からない」
- 「scoreboard の pacing line がおかしい気がする」
- 「我們 team 的 scoreboard 怎麼看」「scoreboard 看了也看不出在贏」

## 何をするか（プロトコル概要）

週次 ≤5 分の diagnostic — leader の design rubric を反転させて member の read rubric にする。再設計はしない。

1. **comprehension 関門** — scoreboard の媒体 / 視認性を確認。team に全く存在しなければ D3-team-design に戻す
2. **5-second test（member 側）** — winning / losing / can't tell? 「can't tell」はデータであり member の問題ではない
3. **per-lead 個人貢献の locate** — 自分の仕事はどこに plug in? いずれの lead にも見つからない → D2 influence-mapping gap
4. **focus lead の trend read** — 先週 vs 前週、up / flat / down、pacing line に乗っているか、自分の活動が説明できるか
5. **calibration check** — pacing / target / 定義は現実と合っているか
6. **判断: 読了か escalate か** — いずれかの flag が立てば（5-sec-fails / drift / hidden / stale）非対立的な ask を草稿
7. **read card 出力** — 媒体 / 5-sec / 貢献 / trend / calibration / flags / escalation 状況

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| scoreboard を design する場（solo / leader） | `4dx-d3-personal-scoreboard` / `4dx-d3-team-lead-scoreboard-design` |
| team に scoreboard 自体が存在しない | step 1 で halt; leader を `4dx-d3-team-lead-scoreboard-design` に誘導 |
| 週次 commitment 準備 | `4dx-d4-member-commitment-prep`（read を消費） |
| 達成できなかった commitment の debrief | `4dx-d4-member-account-debrief`（read を消費） |
| D2 影響力地図の gap（どの lead にも自分を locate できない） | 先に `4dx-d2-member-lead-measure-influence` |
| BI / KPI / executive scorecards | 4DX 範囲外 |

## 出典

⚠️ V1 partial — 第 4 章 + 第 14 章は leader-design POV。member-read は 4 つの design 基準の対称反転 + member 専用 2 ステップ（locate-contribution / escalate-if-broken）。3 つの mirror case: Younger Brothers（framer が 6 つの safety lead を読み、昨日のチェックを自分の shift action に traced back）、Towne Park valet（可視 retrieval-time board に対する per-shift 貢献監査）、Northrop Grumman / Hurricane Katrina で倒れた stadium scoreboard（member の「score が読めない」は scoreboard 側の signal、member の能力問題ではない）。Industry grounding: Tufte 1983/2001（chartjunk が trend 知覚を遅延）、Eurich 2017（95/15 self-awareness gap → step 4 の「plausibly」hedge）、Argyris 1986（step 6a の Model-II escalation script）。

member 側 coach's-as-players' substitution、status-without-trajectory、scoreboard-as-trophy（vanity curation）、member-substitution failure、reading-as-procrastination、ならびに escalation step の high-context culture + psychological safety 注意は [`SKILL.md`](SKILL.md) を参照。
