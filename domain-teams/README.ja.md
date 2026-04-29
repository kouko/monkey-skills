# domain-teams

> checkpoint ベースの quality gate を備えた domain team skill 群 — planning（企画）、code、design、research、copywriting、investing ほか。

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**: 5.5.1
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

## Background

`domain-teams` は 10 個の領域特化 skill を統一された agent + gate
architecture の下に束ねる Claude Code plugin です。各 team は固有の
protocol、standards、checklist、rubric を所有し、すべて primary source
（教科書、RFC、学術論文、公式 docs）に anchor されています — LLM が
創作した heuristics ではありません。

すべての team を支える 2 つの共通 agent：

- **`worker`** — artifact（code、docs、spec、copy、research レポート）
  を生成します。dispatch 元の skill から渡された protocol と standards
  ファイルを読み、SOP を実行して deliverable を出力します。自己評価は
  しません。タスクが hallucination を要求する場合は `BLOCKED` を
  emit できます。
- **`evaluator`** — artifact を checklist（項目ごとに PASS /
  FAIL_FATAL / FAIL_FIXABLE）または rubric（🔴 / 🟡 / 🟢 フラグ）で
  judge します。`PASS`、`PASS_WITH_NOTES`（auto-revise loop）、または
  `NEEDS_REVISION`（user へ escalate）を返します。artifact 自体は
  修正しません。

この分離 — *worker は produce、evaluator は judge* — が plugin の
load-bearing な behavioral rule です。

## Architecture：4-tier quality gate

各 team は 4 つの tier にまたがる gate を定義します：

```
SELF check  （毎回の delivery、worker 自己検証）
   │
   ▼
MUST gates  （auto-trigger、skip 不可）
   │   security / architecture / completeness
   ▼
SHOULD gates  （auto-trigger、理由明示で skip 可）
   │   quality / spec consistency / mode clarity
   ▼
MAY gates  （opt-in、関連時のみ実行）
       team ごとの任意 discipline
```

Gate verdict のフロー：

```
worker artifact ──► evaluator ──► verdict
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
              PASS          PASS_WITH_NOTES         NEEDS_REVISION
           gate clear        auto-revise loop       user へ escalate
                            （最大 3 round、各 round
                              で fresh evaluator）
```

`SELF` は worker が所有します；`MUST` / `SHOULD` / `MAY` は常に明示的な
checklist または rubric ファイルとともに `evaluator` agent を launch
します。各 gate ファイルのパスは team の SKILL.md の `Quality Gates`
セクションで宣言され、verdict は evaluator 単独で emit されます —
worker が合成することはありません。

## Router skill

`using-domain-teams` は entry-point の router です。任意の領域タスクを
始める際にどの team を呼ぶべきか不明な場合に使用します。提供する内容：

- *Available Teams* テーブル（team ごとの mission + delivers）
- *Intent Routing* テーブル（具体的な user intent → team）
- *Ambiguous Cases* テーブル（複数 team の sequence、例：
  `planning-team` → `code-team` → `qa-team` → `devops-team`）

行き先が既に明確な場合は router を skip し、team skill を直接 invoke
してください。

## Teams

| Team | Slash command | 役割 | 主な grounding |
|------|---------------|------|---------------|
| `code-team` | `/code` | primary-source-grounded な quality gate で code を develop | Clean Code（Martin 2008）、Pragmatic Programmer（Hunt & Thomas 2019）、SOLID、TDD（Beck 2002）、Refactoring 第 2 版（Fowler 2018）、Working Effectively with Legacy Code（Feathers 2004）、OWASP ASVS v5.0.0、徳丸本 第 6 章 |
| `docs-team` | `/docs` | Diátaxis discipline で documentation を執筆し codebase を assess | Diátaxis taxonomy、Standard README（RichardLitt）、Google + Microsoft style、Trong-Tra `documentation-specialist`（readme + architecture L0–L4） |
| `qa-team` | `/qa` | unit を超える test を計画・検証 | 品質は工程で作り込む — built-in quality；E2E / integration / performance test 戦略 |
| `devops-team` | `/devops` | CI/CD、container、IaC で安全に code を ship | Google SRE、DORA、12-Factor App primary source |
| `research-team` | `/research` | citation 検証付きで primary-source-grounded な research を実施 | systematic-review rigor、confidence calibration、operator 視点の market analysis |
| `design-team` | `/design` | accessibility と quality review を伴う design | 行為設計（behavioral design）、感性工学、無意識の設計；UI / UX / a11y |
| `planning-team` | `/planning` | 領域横断の project planning（企画） | JTBD、Lean Startup、OKR、4 Big Risks、Business Model Canvas / Lean Canvas |
| `copywriting-team` | `/copywriting` | 説得力のある marketing copy を執筆 | 日本広告の伝統（神田昌典 PASONA / 谷山 / 糸井）+ Anglo persuasion psychology（Cialdini、Schwartz Awareness Levels、Ogilvy） |
| `investing-team` | *（slash command なし）* | primary-source framework に支えられた防御可能な投資判断 | Investment Clock（regime）、Buy/Hold/Sell verdict、台湾株式（三大法人 / 月營收 / 董監持股 / 融資融券） |
| `skill-team` | `/skill` | convention discipline で domain-team skill を構築・修正 | 4-tier gate design、primary-source grounding、3-commit split、dual-file（README + SKILL.md）、companion file pattern |
| `using-domain-teams` | *（router）* | intent を適切な team に route | — |

`investing-team` に slash command がないのは、通常 Cross-Plugin
Delegation Contract 経由で `investing-toolkit` plugin から呼ばれる
ためです（後述）。

## Repository 構造

```
domain-teams/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata（SSOT）
├── agents/
│   ├── worker.md                # 汎用タスク executor（sonnet）
│   └── evaluator.md             # 汎用 quality evaluator（opus）
├── commands/
│   ├── code.md                  # /code → code-team
│   ├── copywriting.md           # /copywriting
│   ├── design.md                # /design
│   ├── devops.md                # /devops
│   ├── docs.md                  # /docs
│   ├── planning.md              # /planning
│   ├── qa.md                    # /qa
│   ├── research.md              # /research
│   └── skill.md                 # /skill
├── skills/
│   ├── using-domain-teams/      # router
│   ├── code-team/
│   ├── copywriting-team/
│   ├── design-team/
│   ├── devops-team/
│   ├── docs-team/
│   ├── investing-team/
│   ├── planning-team/
│   ├── qa-team/
│   ├── research-team/
│   └── skill-team/
├── CHANGELOG.md
├── README.md
├── README.ja.md
└── README.zh-TW.md
```

各 `skills/<team>/` ディレクトリは自己完結しています：

```
<team>/
├── SKILL.md          # frontmatter + 本文、~6,000 token 予算
├── protocols/        # worker が follow する SOP
├── standards/        # artifact が遵守すべき baseline rule
├── checklists/       # binary PASS/FAIL gate ファイル
├── rubrics/          # qualitative 🔴/🟡/🟢 gate ファイル
├── research/         # grounding ノート + citation 検証（一部 team のみ）
└── README.md         # 任意の skill 内部 overview（一部 team のみ）
```

`SKILL.md` 内の bundled file は相対パスで参照されます
（例：`checklists/security-checklist.md`）。絶対パスは使いません。

## Agent behavioral rule

`worker` / `evaluator` の分離は workflow convention ではなく
behavioral rule として強制されます：

- **`worker`** は artifact を produce します。gate verdict は produce
  しません。self-check のために任意の domain ファイル（rubric、
  checklist、standards）を読めますが、`PASS` / `PASS_WITH_NOTES` /
  `NEEDS_REVISION` の verdict を emit することはできません。
- **`evaluator`** は verdict を produce します。artifact は修正
  しません。worker が action 可能な feedback を返しますが、自身が
  ファイルを編集することはありません。
- 知識アクセスは open — 制約は *behavior* にかかり、*どのファイルを
  agent が読めるか* にはかかりません。
- 各 gate retry は *fresh* evaluator を launch し、累積 context は
  ありません — original requirement + 現在の artifact + feedback の
  みです。
- worker は dispatcher の launch prompt 内の `output_language` を
  honor します；technical jargon は原語のまま保持されます（強制翻訳
  しません）。

両 agent には `BLOCKED` の escape hatch があります：タスクが
hallucination を要求する場合、agent は flawed な artifact を出すかわり
に構造化された `BLOCKED` status を emit します。

## Cross-Plugin Delegation Contract

domain-teams は他の plugin が delegate する analysis + gate authority
です。最初の事例は
`investing-toolkit:investment-memo-writer` → `domain-teams:investing-team`。

Contract：

1. **Delegation = path + 構造化 seed context を渡す。** ファイル内容は
   渡しません；analysis 結果も inline しません。
2. **Delegation target は full authority を受け取る。** 受け取る
   skill は自身で standards を読み込み、自身で gate を実行し、自身で
   verdict を emit します。delegator は介入しません。
3. **Data layer は toolkit に、analysis layer は domain-teams に
   留まる。** toolkit plugin は data fetch + pipeline orchestration
   を担い、domain-teams は analysis、primary-source anchoring、gate
   enforcement を担います。
4. **Gate verdict は遡って flow する。** verdict（`PASS` /
   `PASS_WITH_NOTES` / `NEEDS_REVISION`）は orchestrating skill に
   伝播します — swallow されません。
5. **Cross-plugin の path 解決は plugin 名 + skill path** を使います
   （例：`domain-teams:investing-team`）。filesystem の絶対パスは
   使いません。

禁止事項：他の plugin 内で domain-team の gate logic を再実装する
こと（gate bypass）、domain-teams の standards を他 plugin に複製する
こと（drift）、data-fetcher agent に analysis を行わせること。

## Skill 内部 README convention

v5.5.1 で `skill-team/standards/file-conventions.md` は次を formalize
しました：**skill 内部 README（`skills/<name>/README.md` と i18n
sibling）は docs-team workflow を必要としません**。より軽い
discipline で直接執筆します：

- 上部の言語スイッチャー
- 英語名詞の保持（`docs/i18n/glossary-*.md` に従う）
- sibling の SKILL.md へのリンク
- SKILL.md と矛盾しないこと（SKILL.md が SSOT、README は overview）
- skill が derivative の場合は upstream attribution

`docs-team` workflow が必要なケース：plugin-level README、repo-level
README、公開 release README、ADR、API reference、runbook、architecture
L0–L4 ドキュメント。

## License

MIT — 詳細は repository root の [LICENSE](../LICENSE) を参照。
