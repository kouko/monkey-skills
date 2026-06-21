# brainstorming

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> **HARD-GATE — 意図を探索する前に実装を始めるな。** 5 軸の探索フレームワーク（問題 / ユーザ / 最小終状態 / 代替案 / 何が陳腐化するか）でユーザ / エージェントを誘導し、`writing-plans` が消費する構造化ブリーフを生成する。「これは簡単」「もう何を作るか分かってる」「とりあえずコード書こう」の合理化を **拒否** する。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## HARD-GATE の意味

スキップへの圧力 —「これは簡単」「もう何を作るか分かってる」「とりあえずコード書こう」— が、まさにこのスキルが防ぐべき失敗モード。**5 分間のブレインストーミングが、間違ったものを作る 50 分間と、そこからリファクタする 500 分間を救う。**

ユーザ / エージェントが 5 軸を歩く前に実装行為（コード起草 / ファイル展開 / `tdd-iron-law` の呼び出し）に走ろうとした場合、本スキルは拒否して探索フェーズに引き戻す。

## 5 軸フレームワーク

5 つ全て歩く。§When NOT to Use の免責が適用される場合のみ省略可。

| 軸 | 問い | 根拠 |
|---|---|---|
| 1 — 問題 | ユーザがこの変更を雇う「ジョブ」は何か。**ユーザが提案した解決策ではない。** | Christensen (1997) JTBD, ISBN 978-0875845852 |
| 2 — ユーザ | 誰が、どんな条件で、どんな既存ツール・制約のもとで | Klement (2018) job-story 形式, ISBN 978-1718626751 |
| 3 — 最小終状態 | 出荷可能な最小の解決は何か | Axis 3 で `dev-workflow:complexity-critique` に委譲することが多い |
| 4 — 代替案 | この問題を他に 2-3 通り解決する方法と、なぜ却下したか | トレードオフの明示化 |
| 5 — 何が陳腐化するか | この変更で冗長になる既存コード・プロセス — **同じ PR で削除すること** | YAGNI + same-PR クリーンアップ規律 |

## Current State Evidence — recon 規律（v0.7.0+）

変更が既存コードや既存プロセスに触れる場合、ブリーフに `## Current State Evidence` セクション（5 サブブレット：Forward / Reverse / Error / Data / Boundary + Evidence paths appendix）を含める。各ブレットは `file:line` を引用。エージェントが `grep` / `Read` / `Explore` のディスパッチで自分で埋める — recon はエージェントの仕事であってユーザの仕事ではない。Greenfield 作業は `N/A — greenfield` でスキップ可。スキーマは [`references/handoff-brief-format.md`](references/handoff-brief-format.md) §Current State Evidence を参照。

## 成果物

`docs/code-toolkit/specs/YYYY-MM-DD-<topic>.md` に書き出される構造化ブリーフ。スキーマは [`references/handoff-brief-format.md`](references/handoff-brief-format.md) を参照。`writing-plans`（Phase 2）がこのブリーフを消費して原子タスクに分解する。

## 使わない場面

[`SKILL.md`](SKILL.md) §When NOT to Use で限定列挙された例外のみ：

- 1 行の既知パターン修正（typo / version bump / 動作変更を伴わない documented config 値）
- 既存テストカバレッジ下の純粋リファクタ（rename / extract-method / 既存テスト維持）
- 失敗テストが既に存在しかつ再現可能な bug fix
- ユーザの明示的 override AND 5 軸を既にカバーする spec が提示済み

このリストに該当しない作業には HARD-GATE が適用される。

## 共有スキルへの委譲

- **`dev-workflow:complexity-critique`** — 任意；Axis 3 で「変更が大きすぎる」匂いが出た時。3 問の削除優先 triage（最小終状態 / 前後 LOC / 何が陳腐化）。
- **`dev-workflow:proposal-critique`** — 任意；Axis 4 で 3 つ以上の本物の代替案が出て KEEP / DEFER / DROP triage が要る時。
- **`writing-plans`**（Phase 2）— 次段階。ブリーフを消費する。
- **`tdd-iron-law`** — `writing-plans` 終了後、SDD が implementer サブエージェントをディスパッチした時点で発火。

## このスキルがしないこと

- コードを書かない。
- ユーザの代わりに決定しない。軸を提示するだけ。決定はユーザ。
- `dev-workflow:complexity-critique` の代わりにはならない。complexity-critique は特定提案を批評；brainstorming は開かれた問題を探索。

## 関連

- [`SKILL.md`](SKILL.md) — 運用仕様。
- [`references/visual-companion.md`](references/visual-companion.md) — 図を使うべき場面（Mermaid sequence / C4 / ER 等）。
- [`references/handoff-brief-format.md`](references/handoff-brief-format.md) — `writing-plans` 消費用の出力スキーマ。
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — ルータ；本スキルは Stage 1（Discovery）。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — 探索終了後の実装フェーズで発火。
