# Kaizen Skill

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

構造化された 6 step cycle を通して、
既存プロセスにおける小さく継続的な改善を見出し実施する。

## 6 つの step

| Step | 日本語 | 意味 | 主な行動 |
|------|------|------|---------|
| 1 | 現状把握 | 現状を把握する | 評価せず観察する |
| 2 | 問題発見 | 問題を見つける | 摩擦と無駄を特定する |
| 3 | 根本原因 | 根本原因 | 「なぜ？」を核心に達するまで問う |
| 4 | 改善案 | 改善提案 | 最小の変更を提案する |
| 5 | 実行と検証 | 実行と検証 | 試して結果を測る |
| 6 | 標準化 | 標準化 | 新しい既定にする |

## Method Type

Process-driven（Socratic method のような dialogue-driven ではない）。
agent はユーザーを各 step へ順に導き、
改善が小さく可逆で計測可能であり続けることを担保する。

基本原則：Kaizen は継続的な小さな改善であり、
一度きりの大変革ではない。提案された変更が革命のように感じられるなら、それは大きすぎる。

## 7 つの無駄（Muda）

Toyota Production System を知識労働に翻案：

| 無駄の種類 | 日本語 | 知識労働での例 |
|-----------|------|--------------|
| Overproduction | 作りすぎ | 誰も求めていない feature の構築 |
| Waiting | 待ち | code review や承認の待ち |
| Transportation | 運搬 | ツール間のデータ移動、手動転送 |
| Over-processing | 加工 | 不要な手順、gold-plating |
| Inventory | 在庫 | 未処理の backlog、未読通知 |
| Motion | 動作 | context switching、ツールホッピング |
| Defects | 不良 | bug、手戻り、誤伝達 |

## SKILL.md 中の例

| 例 | Domain | 主な洞察 |
|------|--------|----------|
| PR review の bottleneck | 開発 workflow | 根本原因は PR のサイズ文化であり、reviewer 数ではない |
| 長い週次会議 | 会議効率 | 進捗報告を非同期化し会議時間を半減 |

## 追加事例

`references/kaizen-cases.md` により多くの例：
deployment pipeline の最適化、ドキュメントプロセス、onboarding 改善。

## 改善の原則

| 原則 | 説明 | アンチ pattern |
|------|------|-------------|
| 最小の変更 | 一度に 1 つだけ変える | 「pipeline を全部書き直そう」 |
| 可逆 | うまくいかなければ戻せる | 不可逆なインフラ変更 |
| 計測可能 | 前後を数値化できる | データなしで「良くなった気がする」 |
| 即時 | いつかではなく今週始める | 「Q3 にやろう」 |
| 循環 | 1 つの改善が次に繋がる | 「もう改善は終わった」 |

## 文化的起源

Kaizen は戦後日本の製造業に由来し、特に
大野耐一が開発した Toyota Production System で著名。
その哲学では CEO から現場作業員まで、すべての従業員が
仕事を改善する方法を継続的に探すべきとされる。W. Edwards Deming の
品質管理の原則が Kaizen 方法論の発展に大きく影響した。
