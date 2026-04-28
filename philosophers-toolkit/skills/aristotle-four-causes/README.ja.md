# Aristotle's Four Causes Skill

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

理解の 4 つの基本次元から任意の対象を分析する。

## 四原因

| Cause | 問い | Software の例 |
|-------|------|--------------|
| Material | 何でできているか？ | 言語、framework、データ構造 |
| Formal | 何がそれをそれたらしめているか？ | アーキテクチャ、インターフェース、design patterns |
| Efficient | 何が生み出したか？ | 開発者、市場の力、ユーザーニーズ |
| Final | 何のためにあるか？ | 解決するユーザー課題、ビジネス価値 |

## Method Type

Framework-driven 分析（Socratic method のような dialogue-driven ではない）。
agent はユーザーを 4 つの次元に順に導き、各次元で 1-2 個の問いを投げかけ、
最後に各 cause 間のつながりを統合する。

## SKILL.md 中の例

| 例 | Domain | 主な洞察 |
|------|--------|----------|
| IKEA | 小売 | すべての cause が同じ telos（手頃さ）に揃っている |
| Tesla | 自動車 / エネルギー | Material cause（電池供給）が final cause（大量普及）を制約 |
| Slack | Software / SaaS | Efficient cause（偶然の pivot）が launch 前に final cause を検証 |

## 追加事例

`references/business-cases.md` により多くの例：
Patagonia、Notion、GitHub、BEAR.Sunday、Compost Business。

## 適用 domain

| Domain | Material | Formal | Efficient | Final |
|--------|----------|--------|-----------|-------|
| Software | 技術 stack、データ | アーキテクチャ、API | 開発プロセス、トリガー | ユーザー課題、価値 |
| Product | 構成要素、入力 | フォーム、UX | デザイナー、市場 | JTBD、価値提案 |
| Organization | 人、資本 | 構造、文化 | 創業者、意思決定 | Mission、価値 |
| Concept | 前提、与件 | 定義、境界 | 思想家、文脈 | 説明される問題 |
