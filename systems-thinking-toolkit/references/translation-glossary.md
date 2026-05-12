# Systems-Thinking Translation Glossary (EN / JA / ZH-TW)

This glossary is the canonical translation reference for all per-skill
READMEs in `systems-thinking-toolkit` (Phase D). All 9 README subagents
MUST consult this file. New terms encountered during translation should
be added with a brief justification.

## Core terms

| English | 日本語 | 繁體中文 |
|---|---|---|
| reinforcing loop | 強化ループ | 強化迴路 |
| balancing loop | バランスループ | 平衡迴路 |
| causal loop diagram (CLD) | 因果ループ図 | 因果迴路圖 |
| stock | ストック | 存量 |
| flow | フロー | 流量 |
| feedback | フィードバック | 回饋 |
| dangle | ダングル | 懸垂端 |
| dynamics | ダイナミクス | 動態 |
| systems thinking | システム思考 | 系統思考 |
| mental model | メンタルモデル | 心智模型 |
| variance | 変動 | 變異 |
| target | ターゲット | 目標 |
| lever | レバー | 槓桿 |
| outcome | アウトカム | 結果 |
| stakeholder | ステークホルダー | 利害關係人 |
| scenario planning | シナリオプランニング | 情境規劃 |
| archetype | アーキタイプ | 原型 |
| limits to growth | リミッツ・トゥ・グロース | 成長極限 |
| trigger | トリガー | 觸發點 |
| dimension | 観点 | 維度 |
| simulation | シミュレーション | 模擬 |
| intervention | 介入 | 介入 |
| constraint | 制約 | 約束 |
| facilitation | ファシリテーション | 引導 |
| perturbation | 摂動 | 擾動 |

## Override rules (per memory)

- `dimension` translates as 観点 / 維度, NEVER 次元 (which is mathematical sense). Per memory `feedback_dimension_translation`.
- Skill names stay as-is in body text (English slugs); only descriptions translate.
- Author proper nouns (Sherwood, Senge, Sterman, Forrester, Meadows, Goodhart, Edmondson, etc.) stay in English.
- Book titles in original language.
- Per memory `feedback_skill_readme_i18n_required`: every per-skill README must ship en/ja/zh-TW. Industry-standard A i18n discipline per PR #150 (`project_i18n_multilingual_readme`) — no Mainland calques in zh-TW (e.g. 系統 not 系统, 模擬 not 模拟).

## Open questions for translators

When uncertain, leave a `<!-- TRANS-Q: ... -->` HTML comment for controller
to resolve. Do not invent a zh-TW translation that uses Mainland calques;
refer to memory `feedback_skill_readme_i18n_required` and
`project_i18n_multilingual_readme` for the zh-TW industry-standard A
discipline.
