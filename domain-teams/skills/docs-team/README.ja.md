# docs-team

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Diátaxis に基づくドキュメント skill。checkpoint 形式の quality gate と、4× コスト削減のオプトイン quick mode を備える。

**所属**: [monkey-skills](https://github.com/kouko/monkey-skills) → `domain-teams`
**slash command**: `/docs`
**grounding**: Diátaxis · Google Style · Microsoft Style · Standard README · Nygard ADR · OpenAPI 3.2.0 · Write the Docs · JTAP · *Software Engineering at Google* 第 10 章

## 目次

- [背景](#背景)
- [インストール](#インストール)
- [使い方](#使い方)
- [アーキテクチャ](#アーキテクチャ)
- [quality gates](#quality-gates)
- [コスト（full mode と quick mode）](#コストfull-mode-と-quick-mode)
- [ファイル構成](#ファイル構成)
- [貢献](#貢献)
- [ライセンス](#ライセンス)

## 背景

ドキュメントはコードよりも速く腐る。最も多い 4 つの失敗パターンは、モード混在（how-to なのに講義する、tutorial なのに全 option を列挙する）、不整合な reference、未記録の architecture decision、そして誰も信頼しない古い記述である。docs-team はそれぞれの失敗を checkpoint で防ぐ：Diátaxis 単一 quadrant の規律、OpenAPI 形式の reference、結末（consequences）必須の Nygard ADR、可視的に経年する freshness frontmatter。

skill のすべての規則は primary source に基づく。発明された規則はない — Diátaxis は Daniele Procida、style 規則は Google と Microsoft、README spec は RichardLitt、ADR template は Michael Nygard、docs-rot 対策は *Software Engineering at Google* 第 10 章を出典とする。

## インストール

docs-team は monkey-skills plugin に同梱されている。利用方法：

```bash
# monkey-skills plugin が有効化された Claude Code で：
/docs <リクエスト>
```

個別 install は不要。plugin の `domain-teams` ディレクトリに含まれる SKILL.md を Claude が自動で discover する。

## 使い方

`/docs` の後にリクエストを記述するか、`using-domain-teams` router の意図判定に任せる。

```
/docs write a README for this Go library
/docs document the payment service architecture
/docs write an ADR for our token-bucket rate limiter
/docs audit the docs/ directory for staleness
/docs draft a quick how-to for rotating API keys     ← quick mode
```

skill は artifact 種別を検出し、適切な Diátaxis quadrant または composite template を選択し、対応する gate を起動する。

### workflow

| workflow | 出力 | MUST gate | SHOULD gate |
|----------|------|-----------|-------------|
| Write Tutorial | 学習指向の walk-through | Mode Clarity | Style |
| Write How-to Guide | タスク指向のレシピ | Mode Clarity | Style |
| Write Reference | API / CLI / config reference | Mode Clarity | Style |
| Write Explanation | 設計理由 / 概念解説 | Mode Clarity | Style |
| Write README | Standard README spec | README Completeness + section 単位 Mode Clarity | Style |
| Write ADR | Architecture Decision Record | ADR Structure | Style |
| Write API Reference | OpenAPI 形式の reference | Mode Clarity | Style |
| Write Architecture | overview / component spec / data flow | Architecture Doc Completeness | Style |
| Documentation Audit | Diátaxis + freshness audit report | — | Freshness |
| Codebase Assessment | health report（code mode / doc mode）| — | — |
| Quick Write | 同 artifact、SELF check のみ | —（gate スキップ）| — |

## アーキテクチャ

```
docs-team（checkpoint オーケストレーター）
  ├── worker (sonnet)     ← protocols/ + standards/
  └── evaluator (opus)    ← checklists/ + rubrics/ + standards/
```

worker が artifact を執筆。evaluator が gate を採点。main agent が orchestrate し、verdict 規則を適用、`PASS_WITH_NOTES` の場合は最大 2 ラウンドの auto-revise を行う。

quick mode では main agent が protocol を inline で実行し、subagent dispatch を行わない — gate enforcement を犠牲にして 4× のトークン削減を得る。

## quality gates

`domain-teams:skill-team` の gate-system standard に基づく 4 階層システム。

| 階層 | 動作 | docs-team での例 |
|------|------|-----------------|
| **SELF** | すべての delivery で必ず実行。main agent が自己 audit | 全 workflow |
| **MUST** | 自動 trigger、スキップ不可 | Mode Clarity、README Completeness、ADR Structure、Architecture Doc Completeness |
| **SHOULD** | 自動 trigger、理由付きでスキップ可 | Style、Freshness |
| **MAY** | ユーザーリクエストまたは workflow 固有 | Tech Debt audit、frontmatter 未付与ドキュメントへのオプトイン Freshness |

verdict: `PASS` / `PASS_WITH_NOTES`（auto-revise）/ `NEEDS_REVISION`（ユーザーへ escalate）/ `NEEDS_METADATA`（Freshness 限定 — gate が適用不能であり、失敗ではない）。

## コスト（full mode と quick mode）

| mode | タスクあたり | 実行内容 | 用途 |
|------|------------:|----------|------|
| **Full**（既定）| 約 46K tokens | worker + evaluator × MUST/SHOULD gates + auto-revision | 本番ドキュメント、ADR、API reference、対外公開の release README |
| **Quick**（オプトイン）| 約 11K tokens | main agent inline + SELF check のみ | 下書き、個人メモ、低リスクな既存ドキュメントの調整 |

quick mode は ADR、API reference、対外公開の release README、architecture documentation について **拒否** される — これらは gate audit trail が artifact の価値そのものである。

`/docs verify <artifact>` は quick mode の出力に対して gate を後追いで実行する（約 25K）。verification の判断を後回しにできるため、最初から full mode を払う必要がない。

## ファイル構成

```
docs-team/
├── README.md                        # human 向け概要（英語、デフォルト）
├── README.ja.md                     # 日本語訳（このファイル）
├── README.zh-TW.md                  # 繁體中文訳
├── SKILL.md                         # LLM-discovery SSOT（frontmatter + workflow + gate trigger）
├── standards/                       # 安定した SSOT 規則
│   ├── diataxis-taxonomy.md            # 4 quadrant 語彙（Procida）
│   ├── style-conventions.md            # Google + Microsoft + JTAP
│   ├── docs-as-code.md                 # Write the Docs の運用哲学
│   ├── freshness-metadata.md           # frontmatter 規則（SWE@Google）
│   ├── api-reference-structure.md      # OpenAPI 3.2.0 のフィールド
│   ├── pre-writing-checklist.md        # LLM 防御的読解規則
│   └── architecture-doc-structure.md   # L0–L4 階層 + Mermaid 規則
├── protocols/                       # workflow SOP
│   ├── doc-writing-router.md           # mode + quadrant routing
│   ├── quick-write.md                  # コスト削減 inline workflow
│   ├── write-tutorial.md
│   ├── write-how-to.md
│   ├── write-reference.md
│   ├── write-explanation.md
│   ├── write-readme.md                 # Standard README composite
│   ├── write-adr.md                    # Nygard + MADR
│   ├── write-api-reference.md          # OpenAPI 特化
│   ├── write-architecture.md           # system / component / data flow
│   └── codebase-assessment.md          # code + doc 健全性 audit
├── checklists/                      # binary gate
│   ├── readme-completeness.md          # Standard README spec
│   └── tech-debt-checklist.md          # code 健全性（MAY）
├── rubrics/                         # 定性的 gate
│   ├── diataxis-mode-clarity.md
│   ├── adr-structure.md
│   ├── architecture-doc-completeness.md
│   ├── style.md
│   └── freshness.md
└── research/
    └── grounding-v4.3.0.md             # primary source の audit trail
```

## 貢献

docs-team は monkey-skills plugin の一部である。issue と PR は親 repo に提出する：<https://github.com/kouko/monkey-skills>。

変更を提案する際は：

- 新しい artifact に対して既存の gate を実行してから提出する
- 新しい規則には primary source を引用する — 自家製の taxonomy は不可
- `domain-teams:skill-team` の `file-conventions.md` の命名規則に従う（kebab-case、サブディレクトリの入れ子なし、deprecation より削除）
- `SKILL.md` を 6,000 token の hard cap 内に保つ。圧迫が続く場合は standards を分割する

## ライセンス

MIT © 2026 kouko. repo ルートの [LICENSE](../../../LICENSE) を参照。
