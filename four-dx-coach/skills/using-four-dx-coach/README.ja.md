# using-four-dx-coach（ルーター）

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> four-dx-coach プラグインのエントリーポイント router。汎用的 / 曖昧な 4DX 質問を該当する atomic skill に振り分け、4DX が合わない場合は明確に断る。

## このスキルが起動するとき

- 「4DX を使い始めたい」「4DX の始め方」
- 「4 つの規律で目標を達成したい」「実行の 4 つの規律を導入したい」
- 「4DX で〜を達成したい」「4DX を実務で説明して」
- ユーザーがまだ特定の discipline を名指していない汎用 4DX 質問

## 何をするか（プロトコル概要）

Socratic な決定木で、ユーザーの signal を 7 つの atomic skill のいずれかに mapping する:

| # | Signal | Route 先 |
|---|---|---|
| 1 | 4DX 自体が合うか不明 | `4dx-meta-personal-strategy-triage`（6 verdict gate） |
| 2 | 「日常業務に追われて目標が進まない」 | `4dx-d1-personal-whirlwind-triage`（7 日監査、80/20 capacity） |
| 3 | 目標が曖昧 / 多優先 / activity 表現のみ | `4dx-d1-personal-wig-defining`（1 つの *From X to Y by When*） |
| 4 | WIG はあるが日々何をすべきか不明 | `4dx-d2-personal-lead-measure-discovery`（predictive + influenceable） |
| 5 | tracking が noisy / 見ない / 30 個の metric DB | `4dx-d3-personal-scoreboard`（≤4 要素、5 秒テスト） |
| 6 | D1-D3 はあるが cadence がない | `4dx-d4-personal-wig-session`（週次 Account → Review → Plan） |
| 7 | 実践が停滞 / lapse / momentum 喪失 | `4dx-sustain-personal-momentum-rescue`（破損層の診断） |

新規ユーザーの canonical な順序は 1 → 2 → 3 → 4 → 5 → 6、7 は cadence が崩れた時点（崩れる前提）で起動。順序は optional ではない — 4DX は "a matched set, not a menu"。

## 使わない場面

| 状況 | 代わりの行き先 |
|---|---|
| 特定の discipline を名指している（「WIG の書き方は？」） | 該当 atomic skill に直接、router は飛ばす |
| enterprise / 複数チーム展開（50 人以上、cascading WIGs） | 断り、書籍 6-10 章（Leader-of-Leaders）を案内 |
| ソフトウェアプロセス（agile / scrum / kanban / sprint planning） | 断る — 別の問題クラス |
| 突破型 lag のない習慣形成（毎日 meditate、毎晩フロス） | 断り、Atomic Habits を推奨 |
| 投機的 portfolio / pre-PMF | 断り、OKR / lean-startup を推奨 |
| burnout / 抑うつ / 臨床的疲弊 | 断り、臨床 / コーチングへ |

## 出典

Stage-0 BOOK_OVERVIEW と four-dx-coach プラグインの 7 つの atomic skill SKILL.md frontmatter から構成。基盤は *The 4 Disciplines of Execution*（2nd ed., 2021）。

router の決定木全体、4DX 不適合時の handoff スクリプト（enterprise / habit / OKR / agile / burnout）、明示的な非起動 signal は [`SKILL.md`](SKILL.md) を参照。
