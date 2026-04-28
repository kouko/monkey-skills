# skill-team

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> domain-team skill を構築・refactor する meta-skill。primary source への錨定、4 階層 quality gate、3-commit Conventional Commits 規律を備える。

**所属**: [monkey-skills](https://github.com/kouko/monkey-skills) → `domain-teams`
**呼び出し**: `using-domain-teams` 経由でルーティング、または `domain-teams:skill-team` で直接呼び出し
**grounding**: Anthropic Agent Skills spec · Conventional Commits 1.0.0 · Semantic Versioning 2.0.0 · qa-team v4.2.0 / docs-team v4.3.0 / devops-team v4.4.0 の refactor 先例

## 目次

- [背景](#背景)
- [インストール](#インストール)
- [使い方](#使い方)
- [アーキテクチャ](#アーキテクチャ)
- [quality gates](#quality-gates)
- [ファイル構成](#ファイル構成)
- [Visibility convention](#visibility-convention)
- [貢献](#貢献)
- [ライセンス](#ライセンス)

## 背景

skill-team は meta-skill である。唯一の役割は **domain-team skill** の構築と refactor である — `standards/protocols/checklists/rubrics` のディレクトリレイアウトに従い、worker / evaluator agent を起動し、4 階層の quality gate を強制する skill。

skill-team が codify する規約は発明されたものではない。3 つの先行する grounded-team refactor から蒸留された：qa-team v4.2.0（ISTQB / VSTeP）、docs-team v4.3.0（Diátaxis / Google Style / JTAP）、devops-team v4.4.0（Google SRE / DORA / 12-Factor）。それらの refactor で蓄積された tribal knowledge は本 skill の 8 つの standards ファイルに集約されている。

**スコープは意図的に狭い。** 一般的な Claude skill 作成（domain-team 以外）には `superpowers:writing-skills` または Anthropic 公式の `skill-creator` を使う。Obsidian skill、philosophers-toolkit skill、plugin レベルのパッケージング、ユーティリティ script は本 skill の対象外である。

**meta-circularity 注記**: skill-team は自身が存在する前に bootstrap された。最初の構築は手動で行われた — codify する規約をまだ適用できる tool が存在しなかったためである。以降の skill 作成と refactor はすべて skill-team を通る。

## インストール

skill-team は monkey-skills plugin に同梱されている。個別 install は不要。plugin が有効化されると Claude が自動 discover する。

## 使い方

skill-team に slash command はない。間接的に呼び出される：

- `using-domain-teams` 経由（intent が一致した場合：「新しい team skill を作って」「qa-team の grounding を refactor して」など）
- Skill tool で直接：`domain-teams:skill-team`

### workflow

| workflow | 用途 |
|----------|------|
| **New Skill Creation** | 未カバーのドメインに対する新規 domain-team skill の構築（例：`security-team`、`data-team` の追加） |
| **Skill Redesign**（grounding refactor）⭐ 主要用途 | 既存 team が primary source への錨定を欠く / workflow phase が壊れている / 構造改善が必要な場合 |

両 workflow とも PR 用の 3-commit branch を出力する：

```
Commit 1: standards CREATE/MODIFY              （SSOT 規則）
Commit 2: protocols + gates CREATE/MODIFY      （workflow レシピ + verdict 基準）
Commit 3: SKILL.md + router + version bump     （配線 + ship）
```

この分割は装飾ではない。各 commit の差分は skill の 1 層に対応する — reviewer は各層を独立して audit でき、何かが壊れたときの bisect も機能する。

## アーキテクチャ

```
skill-team（checkpoint オーケストレーター）
  ├── worker (sonnet)     ← protocols/ + standards/
  └── evaluator (opus)    ← checklists/ + rubrics/ + standards/
```

worker が build / refactor protocol を実行。evaluator が gate を採点。main agent が orchestrate し、verdict 規則を適用する。

primary source の grounding research が必要な場合、skill-team は自身では実行せず `research-team` に委譲する。research artifact は対象 skill 内の `research/grounding-v{X.Y.Z}.md` に audit trail として配置される（`file-conventions.md` §research/ 規則に従う）。

## quality gates

`standards/gate-system.md` に基づく 4 階層システム。

| 階層 | 動作 | skill-team での例 |
|------|------|------------------|
| **SELF** | すべての delivery で必ず実行。main agent が自己 audit | 全 workflow |
| **MUST** | 自動 trigger、スキップ不可 | Skill Completeness、Commit Split Validity |
| **SHOULD** | 自動 trigger、理由付きでスキップ可 | Primary Source Grounding、Skill Coherence |
| **MAY** | ユーザーリクエストまたは workflow 固有 | 現状なし。将来候補：gate ファイルごとの linting、workflow 依存関係グラフ解析 |

gate verdict: `PASS` / `PASS_WITH_NOTES`（auto-revise、最大 2 ラウンド）/ `NEEDS_REVISION`（ユーザーへ escalate）。

Commit Split Validity gate は `main` に対して `git log --stat` を実行する；評価対象は単一ファイルではなく branch 全体である。

## ファイル構成

```
skill-team/
├── README.md                              # human 向け概要（英語、デフォルト）
├── README.ja.md                           # 日本語訳（このファイル）
├── README.zh-TW.md                        # 繁體中文訳
├── SKILL.md                               # LLM-discovery SSOT
├── standards/                             # 8 SSOT 規則 — codify された tribal knowledge
│   ├── skill-md-structure.md                 # SKILL.md 構造、必須セクション、token 予算
│   ├── file-conventions.md                   # 4 サブディレクトリレイアウト、top-level ファイル、path 規律
│   ├── gate-system.md                        # SELF / MUST / SHOULD / MAY 階層、verdict 意味論
│   ├── grounding-principle.md                # primary source 規則、JP 統合戦略
│   ├── agent-interface.md                    # Resource Paths 入力契約、behavioral 境界
│   ├── commit-convention.md                  # 3-commit 分割、Conventional Commits、semver
│   ├── mermaid-usage-guidelines.md           # Mermaid を使う場面と prose、syntax 規約
│   └── user-terminal-handoff.md              # TTY 拘束 command は user terminal に handoff（auth、sudo、TUI）
├── protocols/                             # workflow SOP
│   ├── skill-brainstorming.md                # 曖昧な依頼のスコープ分解
│   ├── grounding-research.md                 # primary-source research workflow（research-team に委譲）
│   ├── new-skill-creation.md                 # 新規 team の 10-phase 構築
│   └── skill-redesign.md                     # 既存 team の 6-phase refactor
├── checklists/                            # binary gate
│   ├── skill-completeness-checklist.md       # MUST — SKILL.md 構造的準拠
│   └── commit-split-checklist.md             # MUST — branch commit 履歴の妥当性
└── rubrics/                               # 定性的 gate
    ├── primary-source-grounding.md           # SHOULD — 新規 standards の citation 品質
    └── skill-coherence.md                    # SHOULD — 完成 skill の内部整合性
```

skill-team には `research/` サブディレクトリは存在しない。本 skill の規約は Anthropic Agent Skills spec と qa/docs/devops の refactor 先例に traceable で、これらは standards ファイル内で直接引用されている。skill-team が research すべき外部ドメインは存在しないため、in-repo grounding note は不要である。

## Visibility convention

skill-team v5.2.0+ は `TaskUpdate` の emission convention を定義している。すべての workflow 型 domain-team skill（research-team、code-team、docs-team、devops-team、qa-team、planning-team、investing-team、copywriting-team、design-team）が遵守する：

- **phase transition**: 各 major phase の開始と終了で emit
- **milestone**: 各 section / deliverable / sub-step 完了時に emit
- **heartbeat**: silent 期間は 60 秒を超えてはならない（extended reasoning 中であっても）

この convention は **確率的保証** を提供する — 遵守は agent 動作に依存する。非常に長時間実行される dispatch（> 5 min）で厳密な構造的保証が必要な場合、タスクをより短い sub-dispatch に分解する（phase-split アーキテクチャ）。

完全なテキストと controller narration convention は SKILL.md §Visibility Convention を参照。

## 貢献

skill-team は monkey-skills plugin の一部である。issue と PR は親 repo に提出する：<https://github.com/kouko/monkey-skills>。

変更を提案する際は：

- skill-team を skill-team 自身に適用する（dogfood）— `standards/` への変更はすべて `skill-redesign.md` の Phase 4-6（3-commit 分割）を通る
- 新規規約には primary source を引用する — `standards/grounding-principle.md` 参照。tribal-knowledge 主張については qa/docs/devops 先例が primary として認められる；それ以外は外部標準（Anthropic、Conventional Commits、semver 等）を引用
- 提出前に `checklists/skill-completeness-checklist.md` と `checklists/commit-split-checklist.md` を branch に対して実行
- `SKILL.md` を `standards/skill-md-structure.md` 定義の 6,000 token hard cap 内に保つ

## ライセンス

MIT © 2026 kouko. repo ルートの [LICENSE](../../../LICENSE) を参照。
