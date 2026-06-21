# subagent-driven-development

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 1 時間超 または 複数モジュールに跨るタスクを **5 分以下の原子タスク** に分解し、各タスクに 3 つのサブエージェントを並行ディスパッチする：**implementer**（worker、TDD 鉄則下で実装） + **spec-reviewer** + **code-quality-reviewer**（いずれも evaluator）。判定は `domain-teams:code-team` の 7 standards + 2 rubrics + 2 checklists を functional copy として根拠化。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## このスキルが発火する条件

`using-loom-code` が以下のいずれかを検知した時点で自動ルーティング：

- タスクの見積もりが **1 時間超**、または
- タスクが **複数のモジュール / ファイル境界** を跨ぐ。

どちらの閾値にも届かない場合は直接 `tdd-iron-law` に行く。1 行修正に 3 つのサブエージェントを焚くのはコスト的に見合わない。

## 三役

| サブエージェント | 役割 | 出力 | 読む | 書く |
|---|---|---|---|---|
| `implementer` | worker | (status: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED) | task / spec / standards | コード・テスト・commit |
| `spec-reviewer` | evaluator | PASS / NEEDS_REVISION + gap 一覧 | artifact / spec / `checklists/spec-consistency.md` | 判定のみ |
| `code-quality-reviewer` | evaluator | PASS / PASS_WITH_NOTES / NEEDS_REVISION + 6 次元スコア + flags (🔴 / 🟡 / 🟢) | artifact / rubrics / checklist / 7 standards | 判定のみ |

各タスクは implementer 1 ラウンド + reviewer 並列 1 ラウンドで進む。レビュアの守備範囲は故意に非重複：spec-reviewer は品質を採点しない、code-quality-reviewer は spec 網羅性を採点しない。混ぜるとオーケストレータの解決アルゴリズムが壊れる。

## Phase 1 acceptance test

4 タスクの計画 → SDD は **12 サブエージェント** (4 × 3) をディスパッチし、12 判定を返す。各タスクは再ディスパッチ 3 ラウンド以内に DONE 解決。`tests/skill-triggering/prompts/` が Phase 1 でこれを検証する。

## 知識層（functional copy）

このスキル下の `standards/`、`rubrics/`、`checklists/` 全ファイルは `domain-teams/skills/code-team/{standards,rubrics,checklists}/` のバイト一致 functional copy に 5 行の SSOT ヘッダを付けたもの。規律を変更する場合：

1. `domain-teams:code-team` 側の canonical を編集。
2. 同じ commit で `python3 loom-code/scripts/distribute.py`。
3. CI で `loom-code/scripts/verify-drift.py` がバイト一致を強制。

## Reviewer 出力規律（v0.7.0+）

3 つの reviewer agent（`spec-reviewer`、`code-quality-reviewer`、`code-reviewer`）はそれぞれ **追加で** ファイル内 SSOT 注入ブロック — **reviewer-discipline-v1** — を BEGIN/END マーカーで包んで持つ。canonical テキストは `loom-code/scripts/_reviewer-discipline.md`：

- **R1** — すべての verdict に `standards_version` フィールドを付与（`plugin.json` の `version` から読む）— 後の読者が「どのバージョンの rubric で採点されたか」を判別できる。
- **R2** — すべての flag / finding / gap にエビデンス引用フィールド（`where:` / `artifact:` / `spec_ref:`）を必須記載。欠落すると verdict 全体が `NEEDS_REVISION` に反転（不透明な出力は修正不能）。

`distribute.py` が 12 ルール engineering baseline と並んで自動注入する。implementer はこのブロックを **持たない** — verdict を出さないため。`verify-drift.py` は共有の `expected_agent_text` 経由で両方のブロックをカバー。

## このスキルがしないこと

- コードを書かない — implementer をディスパッチする。
- 判定を出さない — reviewer をディスパッチする。
- SDD 適用判断をしない — `using-loom-code` がルーティングする。
- 計画を作らない — `writing-plans` (Phase 2; それまでインラインで作る) が作る。
- 最終タスク後の処理をしない — `finishing-a-development-branch` (Phase 3) がブランチを閉じ、`dev-workflow:git-memory` に委譲する。

## 関連

- [`SKILL.md`](SKILL.md) — オーケストレーション仕様。
- [`agents/implementer-prompt.md`](agents/implementer-prompt.md) / [`agents/spec-reviewer-prompt.md`](agents/spec-reviewer-prompt.md) / [`agents/code-quality-reviewer-prompt.md`](agents/code-quality-reviewer-prompt.md) — 役割プロンプト。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — implementer が従う鉄則。
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — ルーター；SDD 発火条件。
- [`../../scripts/canonical/README.md`](../../scripts/canonical/README.md) — SSOT ポインタ + ドリフトポリシー。
