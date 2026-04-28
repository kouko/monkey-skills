# Wabi-Sabi Skill

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

3 つのレンズで不完全さを評価し、
「これで十分」を判断、over-engineering と完璧主義に対抗する。

## 3 つのレンズ

| Lens | 日本語 | 中心の問い | 目的 |
|------|------|---------------|------|
| Wabi | 侘 | 本質を損なわず取り除けるものは？ | 簡素・質素 |
| Sabi | 寂 | 物語や味を加える不完全さは？ | 時の経過と使用の痕跡 |
| Incompleteness | 不完全の美 | 成長を招く未完成の要素は？ | 意図的な不完全の美 |

## Method Type

Framework-driven 分析（3 つの独立したレンズを順に適用し、
最後に「これで十分」の判断に統合する）。

## Software / Product への適用

| Lens | Over-engineering | Wabi-Sabi |
|------|-----------------|-----------|
| Wabi | 使われない 20 の feature | ユーザーが毎日使う 5 つの feature |
| Wabi | 50 個の API endpoint | 10 個の汎用 endpoint |
| Wabi | 3 層の抽象 | 必要になるまで直接実装 |
| Sabi | 汎用 500 エラー | 文脈に応じた有益なエラーメッセージ |
| Sabi | 突然の API deprecation | 移行ガイド付きの段階的 deprecation |
| Sabi | 古い UI を全面書き直し | ユーザーが慣れた UX pattern を維持 |
| Incompleteness | あらゆる将来要件を先回り | 拡張点だけ用意し実装は後で |
| Incompleteness | すべて core に内蔵 | Core + plugin アーキテクチャ |
| Incompleteness | 100 項目のテンプレート | 最小テンプレ + ユーザーのカスタム |

## 主な違い：品質 vs 過剰品質

| | 低品質（wabi-sabi ではない） | 十分な品質（wabi-sabi） | 過剰品質（これも wabi-sabi ではない） |
|--|----------------------------|-------------------------------|----------------------------------|
| 定義 | 必須機能の欠如 | 必須機能あり、非必須は削除済み | 文脈が要求する以上の磨き込み |
| 例 | 検索が壊れている | 検索は動く、autocomplete はなし | 5 ユーザーのために ML 提案つき検索 |
| 行動 | 直す | 出荷する | 削ぎ落とす |

## SKILL.md 中の例

| 例 | Domain | 主な洞察 |
|------|--------|----------|
| MVP リリース判断 | SaaS Product | 非中核 feature（Gantt、dashboard）削除、エラーメッセージ改善、状態カスタマイズ追加 |
| UI 磨き込み判断 | 社内ツール | 5 人の社内ツールに animation や theme は不要；実際の不満ひとつを直す |

## 追加事例

`references/wabi-sabi-cases.md` により多くの例：
API 設計の簡素化、技術的負債の評価、ドキュメントの scope。

## 他の Skills との関連

| Skill | 関係 |
|-------|-------|
| design-team（Kansei Engineering） | wabi-sabi は何を残さず、kansei は感情的響きのために何を残すかを示す |
| code-team（YAGNI） | Wabi（簡素）は YAGNI と整合；incompleteness は拡張点に対応 |
| hegelian-dialectics | 「出荷 vs 磨き込み」が二択になったとき dialectics が synthesis を見出し、wabi-sabi がレンズを提供 |
