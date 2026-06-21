# writing-plans

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> [`brainstorming`](../brainstorming)（ブリーフ生成）と [`subagent-driven-development`](../subagent-driven-development)（サブエージェント派遣）の橋渡し。ブリーフを ≤5 個の原子的 ≤5 分タスクに分解、明示的な RED-GREEN 受入条件を付与、plan-document-reviewer で自己レビュー、BLOCKED fallback は Kent Beck (2002) §Child Test パターンに従う (ISBN 978-0321146533)。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## このスキルが位置するパイプライン

```
brainstorming → brief                            (Discovery 段階)
                  ↓
              writing-plans → plan + self-review   (本スキル — Planning 段階)
                  ↓ (PASS)
              subagent-driven-development → per-task triad
                                                    (Execution 段階)
                  ↓
              tdd-iron-law (各 implementer 内部)
```

## 二つの厳格ルール

1. **タスク 1 つ ≤5 分**。focus した implementer サブエージェントが 5 分で終わらないなら分割する (P2-B)。
2. **プランサイズ ≤5 原子タスク**。ブリーフから 6 タスク以上が出る = ブリーフが大きすぎる。brainstorming へ差し戻すか、N 個のブリーフに分割する。

5+5 ルールは意図的な forcing function：欲張りすぎなブリーフを押し返し、曖昧なタスクで複雑さを隠したプランを押し返す。

## 各タスクが持つもの

[`references/plan-format.md`](references/plan-format.md) に従い、各タスクは：

- **Description**: ≤5 分の命令形アクション
- **Module**: 1 つのパス / モジュール名（2 つではない）
- **Context paths**: implementer が読む既存コードのパス（paths-not-content）
- **Acceptance**: RED テスト名 + GREEN 観察可能条件
- **Dependencies**: `none` | `Task N completes first` | `Tasks N, M parallel`
- **Brief item covered**: ブリーフの Smallest End State / Decision からの引用 / 参照

この形式が `subagent-driven-development` がタスクごとに 3 サブエージェントを派遣する時に消費する shape。

## DONE 宣言前の自己レビュー

プラン作成後、writing-plans は [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) を evaluator サブエージェントとして派遣する。レビュアは 12 個のチェック（タスクあたり ≤5 分、ブリーフ-タスクカバレッジ map、DAG 循環なし等）を実行し、PASS / NEEDS_REVISION を返す。NEEDS_REVISION なら writing-plans がプランをパッチして再レビュー。最大 2 ラウンド；まだ通らなければユーザにエスカレーション（ブリーフ自体の再考が必要な可能性が高い）。

plan-document-reviewer は SDD の spec-reviewer / code-quality-reviewer と **別物** — 後者はコードを評価、こちらはプラン構造を評価。

## BLOCKED fallback — Beck 2002 §Child Test

SDD が implementer サブエージェントを派遣して `BLOCKED` + `unblock_step: "このタスクは更に小さく分けるべき"` が返った時、オーケストレータは **writing-plans を失敗タスクに対して再呼び出し** する。本スキルは失敗タスクを ladder up する小さな子タスクに分解 — Kent Beck の Child Test パターン（*Test-Driven Development: By Example* Part II）：

> "テストに取り組んでいて大きくなりすぎた時、大きいテストの壊れた部分を表す小さなテストを書け。小さなテストを通せ。それから大きいテストに戻れ。"

writing-plans は同じパターンをプランタスクに適用する。これがこのスキルの **主要な再帰的価値** — 初期プランニングだけでなく、SDD が実行中に原子性失敗に遭遇した時の適応的再プランニング。

## 使わない場面

[`SKILL.md`](SKILL.md) §When NOT to Use の限定列挙：

- 上流ブリーフが未生成（先に brainstorming へ）
- ブリーフの Smallest End State 自体が ≤5 分で Out of Scope が exhaustive（ブリーフがプラン）
- ユーザの明示的 override AND plan-format スキーマを満たすタスクリストが提示済み

## このスキルがしないこと

- コードを書かない。プランは将来作業のメタデータ。
- SDD サブエージェント（implementer / spec-reviewer / code-quality-reviewer）を派遣しない — SDD の仕事。
- ≤5 分以外の dev-time 推定はしない — time-box は split-trigger であって estimation exercise ではない。
- 依存グラフが要求する以上の優先度 / sequencing 判断はしない。

## 関連

- [`SKILL.md`](SKILL.md) — 運用仕様（分割フレームワーク、BLOCKED fallback フロー、Red Flags）。
- [`references/plan-format.md`](references/plan-format.md) — worked example 付きプランスキーマ。
- [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) — 自己レビュー evaluator プロンプト。
- [`../brainstorming/SKILL.md`](../brainstorming/SKILL.md) — 上流ブリーフ producer。
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — 下流プラン consumer。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — 各 implementer サブエージェント内で発火する規律。
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — ルータ；本スキルは Stage 2（Planning）。
