# requesting-code-review

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ブランチ全体 / PR 全体 レビュースキル。`subagent-driven-development` のタスク単位レビュアとは別 — こちらはブランチ作業の **終わり** に発火し、merge 前に、タスク単位レビューでは見えない **タスク間相互作用** を捕まえる。code-reviewer サブエージェントを派遣して loom-code の rubrics + checklists + standards（`domain-teams:code-team` の functional copy）をロード、重大度タグ付き構造化レビューを出力。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## タスク単位 vs ブランチ全体レビュー

| | SDD タスク単位レビュア | 本スキル（ブランチ全体） |
|---|---|---|
| スコープ | 1 原子 ≤5 分タスク | main 比 ブランチ累積変更 |
| 発火タイミング | 各 SDD タスクトライアド中 | 全 SDD 作業 DONE 後、merge 前 |
| 捕まえるもの | タスク単位の品質欠落 | タスク間相互作用、スコープクリープ、アーキテクチャー整合性 |

同じ rubrics、異なるスコープ。両層は異なる失敗モードを扱う — どちらも代替不可。

## 使う場面

- 「ブランチを review して」/ 「変更を見て」/ 「merge してよい？」
- 「コードレビューお願い」/ 「diff を audit して」/ 「機能 X 完成、見て」
- `subagent-driven-development` がマルチタスクプラン完了後に積極的に呼ぶ
- `finishing-a-development-branch` がクローズフローの Step 1 で自動呼び出し

## 使わない場面

[`SKILL.md`](SKILL.md) §When NOT to Use：
- Trivial diff（1 行 typo / doc のみ / version bump / 生成コード再生成）
- 既にレビュー済みブランチで変更なし
- 既存コードの compliance audit（`domain-teams:code-team` パッシブ gate を使う — 用途違い）
- ユーザの明示的 override AND 変更が trivial に該当

## 出力

すべての verdict は以下を含む：

- **`standards_version`** スタンプ（`plugin.json` の `version` から）— ダウンストリーム読者が「この review はどのバージョンの rubric で採点されたか」を判別できる（v0.7.0 reviewer-discipline R1）。
- 7 次元スコア（security / architecture / correctness / naming / tests / refactoring / **cross-task-coherence** — ブランチ限定）。
- 重大度タグ付き findings（🔴 fatal / 🟡 should-fix / 🟢 nit）— 各 finding は `where:`（file:line または commit SHA range）を必須記載。**`where` が欠落すると重大度に関わらず verdict は `NEEDS_REVISION` に反転**（v0.7.0 reviewer-discipline R2 — 不透明な finding は修正不能）。
- ≤5 行 summary。

集計（`rubrics/quality-gate.md` SSOT に整合）：

- 任意の 🔴 → `NEEDS_REVISION`
- 任意の finding が `where` 欠落 → `NEEDS_REVISION`（malformed）
- **🟡 が 2 個以上** → `NEEDS_REVISION`（警告の累積 = システム的懸念）
- ちょうど 1 個の 🟡、🔴 なし、全 finding が `where` 付き → `PASS_WITH_NOTES`
- 🔴 なし、🟡 なし → `PASS`

R1+R2 規律の canonical は `loom-code/scripts/_reviewer-discipline.md` にあり、`distribute.py` が 3 つの reviewer agent に自動注入する。

## Cross-skill

- **呼び出し元**：`finishing-a-development-branch`（クローズフロー Step 1）
- **任意エスカレート**：大規模 audit は `domain-teams:code-team`（>500 LOC、security 重要面、インシデント駆動レビュー）
- **rubrics ロード**：`../subagent-driven-development/{rubrics,checklists,standards}/` — タスク単位レビュアと同じ SSOT、レイヤー間ドリフトなし

## このスキルがしないこと

- コードを編集しない（evaluator のみ）。
- タスク単位 SDD レビューの代わりにはならない。
- テストを実行しない（`verification-before-completion` の役割）。
- CI を起動しない（remote push が起動する；本スキルは push 前に走る）。

## 関連

- [`SKILL.md`](SKILL.md) — 運用仕様。
- [`../../agents/code-reviewer.md`](../../agents/code-reviewer.md) — サブエージェント役割プロンプト。
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — タスク単位レビュア（異なるスコープ、同じ rubrics）。
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — 兄弟 pre-merge gate（test-suite）。
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — オーケストレータ。
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — ルータ；本スキルは Stage 6（Review）。
