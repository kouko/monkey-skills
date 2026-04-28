# Popper's Falsifiability Skill

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

曖昧な主張を testable な hypothesis に変換し、
それを誤りと証明できる test を設計する。

## 5 つの step

| Step | 問い | 目的 |
|------|------|------|
| State the Claim | hypothesis は具体的に何か？ | 変換前に主張を捉える |
| Operationalize | どう測定するか？ | 曖昧な主張を具体的・測定可能にする |
| Design Falsification Test | 何が証拠となれば誤りと示せるか？ | test 前に pass/fail 基準を定義 |
| Evaluate Evidence | 既存データは falsify するか支持するか？ | test を既存の証拠に適用 |
| Verdict | Falsified、survived、unfalsifiable？ | 結論と推奨する次の一歩を出す |

## Method Type

Process-driven（段階的な hypothesis testing flow）。
First Principles（真理まで分解）や Dialectics（trade-off の検討）とは異なる。

## 3 つの verdict

| Verdict | 意味 | 次の行動 |
|---------|------|-----------|
| Falsified | 証拠が hypothesis と矛盾 | 修正または破棄 |
| Survived | 反証されなかった（証明されてもいない） | 慎重に進む；より厳しい test を設計 |
| Unfalsifiable | どんな証拠でも反証不能 | 再定式化、または信念・価値として認める |

## Unfalsifiability の red flag

| シグナル | 例 |
|--------|------|
| 証拠免疫 | 「どんなデータでも考えは変わらない」 |
| 無限延期 | 「あとはデータが足りないだけ」 |
| 例外免疫 | 「反例はすべて特殊例」 |
| 計測不能 | 「観測できない方法で機能している」 |

## SKILL.md 中の例

| 例 | Domain | 主張 | Verdict |
|------|--------|------|---------|
| Performance Claim | Caching | 「Redis で速くなる」 | Survived（p95 が 350ms → 180ms） |
| Architecture Assumption | Microservices | 「Microservices で出荷が速くなる」 | Unfalsifiable（交絡変数） |

## 補完する Skills

- **Assumption Mapping**（planning-team）：AM が前提を抽出、Popper がそれらを test
- **First Principles**：ground truths まで分解；Popper は具体的な主張を test
- **Socratic Method**：dialogue で思考を挑む；Popper は test を構造化

## インスピレーション

5 step の反証プロセスは Karl Popper『The Logic of Scientific Discovery』（1934）
および『Conjectures and Refutations』（1963）に基づく。
philosophers-toolkit 標準に従い guided dialogue 形式に翻案。
