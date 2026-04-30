# 4DX D3 — Personal Scoreboard

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> D3 の中核 — 1 人用の players' scoreboard を「ぱっと見で勝敗が分かる」形に設計する（要素 ≤4、lead + lag + where-you-should-be line、5 秒テスト合格）。

## このスキルが起動するとき

- 「Notion で管理してるけど開かない」「追跡表は作ったけど見てない」
- 「fitness app が指標多すぎて何にもやる気起きない」
- 「進捗を可視化したい」「sticky note / whiteboard / アプリ、どれがいい？」
- D1 + D2 はやったが 2-4 週で momentum が落ちている（多くは scoreboard 不在で、意志力の問題ではない）
- 今ある追跡物が明らかに coach's scoreboard（multi-tab spreadsheet、Gantt、project plan）

## 何をするか（プロトコル概要）

Socratic な設計対話 — 出力は「今日中に目に入る場所に貼る scoreboard 仕様」。tracking 哲学の議論ではない:

1. **WIG + lead measure が定義済みか確認** — 両方を書面で。欠けていたら D1/D2 に差し戻す
2. **表示媒体を user の実生活に合わせて選ぶ** — 1 日 3-5 回視線が自然に落ちる場所。「アプリで確認する」は却下
3. **lead measure の可視化をデザイン** — 週次 bar / 連続日数 streak / checkbox grid / 累積カウント。30 秒以内で更新できる形
4. **lag の可視化に where-you-should-be line を必ず入れる** — pacing line / target marker / "goat"。これがないと「今どこ」しか見えず「勝っているか」が分からない
5. **5 秒テスト** — 冷静に描写し直し、user が即「分かる」と言えるか。ヘッジが入ったら要素を削る。最終 ≤4 要素
6. **表示場所と更新 cadence を確定** — 「[場所] に貼り、[lead] は毎日 / [lag] は毎週、自分で更新する」を 1 行で commitment
7. **出力: 仕様 + 今日中の物理アクション** — 印刷する、貼る、whiteboard に書く。「今週末にやる」は不可（このスキルは inertia を防ぐためにある）

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 自分が管理する team の組織横断 BI / KPI dashboard | coach's scoreboard は別問題、適切に複雑でよい |
| WIG や lead measure が未定義 | 先に `4dx-d1-personal-wig-defining` / `4dx-d2-personal-lead-measure-discovery` |
| stroke-of-pen な goal（買う / 雇う / 決めるだけ） | scoreboard 化する対象がない |
| reactive / on-call で whirlwind 自体が戦略 | phantom guilt のリスク。`4dx-meta-personal-strategy-triage` 参照 |
| 高 context 文化のチーム文脈（公開比較が face-loss になる） | 書籍の shift-vs-shift 例は JP / ZH / KR には素直に効かない |

## 出典

*The 4 Disciplines of Execution* 第 2 版 第 4 章 Discipline 3: Keep a Compelling Scoreboard + 第 14 章より蒸留。3 つの anchor case: Northrop Grumman（ハリケーンで吹き飛ばされたスタジアム scoreboard の比喩）、カナダ遠隔工場（shift 単位の可視 board のみで品質 74 → 94）、戦闘機開発（"project plan is not a scoreboard"；2 つの成果物が共存する）。

coach's-as-players' substitution（CE-08）、status-without-trajectory（CE-09）、Goodhart / vanity-metric drift、manual-update-as-feature の設計則を含む完全 RIA++ 展開は [`SKILL.md`](SKILL.md) を参照。
