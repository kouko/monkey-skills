# Aristotle's First Principles Skill

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

問題を根本的な真理まで分解し、ゼロから再構築する。類推と慣習を拒否する。

## 5 つの phase

| Phase | 問い | 目的 |
|-------|------|------|
| Problem Essence | 本当に達成したいことは何か？ | 結果と想定された解法を分離する |
| Challenge Assumptions | 何を前提にしているか、それは検証済みか？ | すべての前提を証拠で test する |
| Establish Ground Truths | 何があっても揺らがない真理は何か？ | これ以上分解できない事実を 3-5 個見つける |
| Reason Upward | これらの真理だけからの最も単純な解法は？ | 真理に裏付けされた最小解を組み立てる |
| Validate Reasoning | すべての決定を ground truth に遡れるか？ | 類推・複雑化・しがらみの罠を stress test |

## Method Type

Process-driven（段階的な分解と再構築）。
Four Causes（既存のものを分析）や Dialectics（立場を比較）とは異なる。

## 避けるべき主な罠

| Trap | 説明 | 例 |
|------|------|-----|
| Complexity | 不要な構成要素がこっそり戻ってくる | 「念のため」に cache を追加 |
| Analogy | 既存の解法を無意識にコピー | 「X 版の Uber」 |
| Legacy | 不要となった互換性を維持 | 誰も使っていない形式のサポート |

## SKILL.md 中の例

| 例 | Domain | 従来のアプローチ | First-Principles の結果 |
|------|--------|----------|----------------------|
| Authentication | 社内ツール | OAuth2 を追加 | 既存の corporate SSO を使う |
| Data Storage | イベントログ | PostgreSQL vs MongoDB | append-only log ファイル + バッチクエリ |

## インスピレーション

5 phase 構造は
[awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill)（MIT License）から着想を得た。
philosophers-toolkit 標準に従い guided dialogue 形式に書き直した。
