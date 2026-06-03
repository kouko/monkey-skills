# dev-workflow

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Claude Code 用の developer workflow plugin — skill 作成・採点・refactor・tuning、deletion-first な critique gate、git-native な project memory。

**Version**: 2.0.0 ・ **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) ・ **License**: MIT

## Background

Claude Code 向けの skill 開発は反復的な作業です。skill を draft してリリースしたあと、長すぎる、出力が tone 外れだといった問題を見つけて改善したくなります — ただし *どう* 改善するかは変更の種類によって変わります。**token / structure の refactor** は機械的に検証可能（変更後も output が同じはず）。**output quality の tuning** は taste-sensitive（どの variant が良いかは人間にしか判断できない）。`darwin-skill` 系のアプローチのように両者を 1 つの rubric に混ぜると、LLM-as-judge が人間の選好から離れた方向へ hill-climb してしまいます（Goodhart drift）。

`dev-workflow` は次の 2 つのアーキテクチャ的判断のもとに skill 群を提供します：

1. **Two Hats split for skills**（Fowler の refactor-vs-feature を skill authoring に適用）— `skill-refactor`（Phase A：behavior-preserving、auto-evaluable）と `skill-tuning`（Phase B：taste-sensitive、human-judged）を分離。
2. **critique-gate のライン** — proposal が commit になる前に介入する：`proposal-critique`（複数項目の triage）→ `complexity-critique`（単一変更の deletion-first gate）→ simplify（実装後の review、Anthropic 純正 toolkit に存在）。

この plugin はさらに `skill-creator-advance`（作成 + 大規模再設計）、`skill-judge`（advisory な 8 次元品質 rubric、変更を加えない）、`git-memory`（commit trailer と PR 本文に書き込む可搬な project memory、git を読める任意のツールから復元可能）を同梱しています。

設計の全体像：[`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md)。運用ガバナンス：[`docs/skill-governance.md`](docs/skill-governance.md)。四半期ヘルスチェック：[`docs/quarterly-audit-runbook.md`](docs/quarterly-audit-runbook.md)。

## Skills

| Skill | 役割 |
|---|---|
| [`skill-creator-advance`](skills/skill-creator-advance/) | 新規 skill の作成、または既存 skill の大規模再設計（phase の追加 / 分割 / 統合、agent 分解の変更、input/output contract の変更）。description optimization を含む反復的 eval-driven development。 |
| [`skill-refactor`](skills/skill-refactor/) | 既存 skill の token / structure refactor、**output behavior を保持**。3 段階 gate：equivalence（multi-judge ensemble）+ token reduction（≥10%）+ invariant preservation。PROCEED / RESHAPE / REJECT を判定し、git ratchet で失敗時に自動 revert。 |
| [`skill-tuning`](skills/skill-tuning/) | 既存 skill の output quality A/B — variant を生成し blind で実行、人間の preference を捕捉（A / B / both / neither）。Constitution は床、taste は天井。preference log は RLHF-lite データセットとして蓄積。 |
| [`skill-judge`](skills/skill-judge/) | Advisory な 8 次元設計 rubric（Knowledge Delta・Mindset+Procedures・Anti-Pattern・Spec Compliance・Progressive Disclosure・Freedom Calibration・Pattern Recognition・Practical Usability）、0–120 点 + A–F grade。変更は加えない。 |
| [`proposal-critique`](skills/proposal-critique/) | 複数項目の proposal（list / plan / 散文の推奨）を evidence grounding と YAGNI で KEEP / DEFER / DROP に triage。 |
| [`complexity-critique`](skills/complexity-critique/) | 1 つの具体的な提案変更を 3 つの deletion-first 質問で gate：最小到達状態、before/after の LOC、何が obsolete になるか。PROCEED / PROCEED-WITH-CAVEAT / RESHAPE / REJECT。 |
| [`git-memory`](skills/git-memory/) | 決定の文脈（diff そのものではなく **why**）を commit trailer と PR 本文に書き込み、Claude Code / Cursor / Codex / aider / 人間など将来のあらゆる session が `git log` だけから project knowledge を再構成できるようにする。 |
| [`brief-before-asking`](skills/brief-before-asking/) | 複雑な engineering 決定の質問を user に投げる前（あるいは反応として）の構造化 briefing。3 モード：Mode A（agent が複雑な fork に気づいて自発 trigger）、Mode B（user が質問に「看不懂」と返す）、Mode C（user が解釈に「跟不上」と返す — Mental Model + drill menu に退く）。Mental Model First を最高優先とする 6-block 形式。 |
| [`dogfood-skill-testing`](skills/dogfood-skill-testing/) | 開発中 skill の behavioral black-box dogfood — fresh subagent で trigger と output 品質を実地検証し、修正に直結する findings レポートを出力。 |

9 つの skill はすべて **Active**。lifecycle 状態と所有権：[`docs/skill-governance.md`](docs/skill-governance.md)。

## critique のライン

3 つの skill が deletion-first な review pipeline を構成し、それぞれ異なる proposal の形に合わせて調整されています：

```
proposal-critique           complexity-critique           Anthropic simplify
─────────────────           ─────────────────────         ──────────────────
複数項目の proposal         1 つの具体的な提案変更       実装後の diff review
（list / plan / 散文）       （refactor、feature 追加、
                            debt cleanup、または
                            「そもそも作るべきか」）

triage：各項目を            gate：3 つの deletion-first   出荷後の review：
  KEEP / DEFER / DROP         questions                     reuse、品質、効率
evidence + YAGNI で判定     • 最小到達状態
                              • before/after の LOC
                              • 何が obsolete になるか

判定：KEEP / DEFER          判定：PROCEED /              （この plugin の外に
       / DROP                      PROCEED-WITH-CAVEAT     存在）
                                   / RESHAPE / REJECT
```

backlog や番号付きの plan を渡されたら `proposal-critique`。1 つの具体的変更が table の上にあるなら `complexity-critique`。変更が出荷された後は Anthropic の `simplify`。

## skill-evolution architecture

`skill-creator-advance`・`skill-refactor`・`skill-tuning`・`skill-judge` は skill のライフサイクル全体を、**変更のサイズ × 評価モード**でカバーします：

```
size →    small                medium                large                new
       ┌────────────────┐  ┌────────────────┐  ┌──────────────────────────────┐
       │ skill-tuning   │  │ skill-refactor │  │ skill-creator-advance        │
       │                │  │                │  │ (作成 + 大規模再設計)        │
       │ output quality │  │ token / struct │  │                              │
       │ A/B variants   │  │ 同一 behavior  │  │ spec-first 再設計 / 新規     │
       │                │  │                │  │                              │
       │ HUMAN judge    │  │ LLM equiv.     │  │ user 主導の iteration loop + │
       │ each iteration │  │ + git ratchet  │  │ optional な AI A/B 比較      │
       └────────────────┘  └────────────────┘  └──────────────────────────────┘

       skill-judge：advisory な 0–120 点。変更を加えず、いつでも実行可能
```

この分割は評価コストによって規定されます：機械的変更（refactor）は LLM-as-judge による binary equivalence の信頼性が高いので auto-evaluation に耐えます。taste-sensitive な変更（tuning）は style・voice・persuasive force・design feel に対する LLM-as-judge が信頼できないため、人間が必要です。どの skill を使うかは「どれくらい自動化したいか」ではなく「どんな種類の変更を行うか」の問題です。

## git-memory の 3 本柱

`git-memory` は次の 3 つの主張に基づきます：

1. **Carrier — git 成果物そのもの**。commit message と PR 本文が substrate。git を読めるツールならどれでも memory を読めます。`git clone` が memory を一緒に持ってきます。サーバーも embedding store も vendor lock-in もなし。
2. **Structure — commit trailer**。構造化された事実は git trailer に乗ります — `Co-Authored-By:` や `Signed-off-by:` と同じ仕組み。3 つの trailer で価値の ~80% をカバー：`Decision:`（なぜこのアプローチか）、`Learning:`（何を発見したか）、`Gotcha:`（未来の自分への trap）。
3. **Content — code ではなく決定の文脈**。diff は *何が* 変わったかをすでに示しています。memory は *why* を記録します。半年後に元の文脈が失われた時にもまだ価値がある entry を目指す — code そのものと冗長な entry ではなく。

`git-memory` は Claude Code 純正の `~/.claude/.../MEMORY.md` を補完します（置き換えません）。純正 memory は project 横断の user-level 選好を保持し、`git-memory` は repo 内に project 決定を保持します。

## Upstream chain

9 つの skill のうち 3 つは MIT-licensed な upstream に由来します。完全な attribution は各 skill の `NOTICE` ファイル参照。

| Skill | Upstream chain |
|---|---|
| `skill-creator-advance` | Anthropic [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) → AllanYiin（尹相志）[`skill-creator-advanced`](https://github.com/AllanYiin/Amon) → monkey-skills |
| `skill-judge` | Leonardo Flores [`skill-judge`](https://github.com/softaworks/agent-toolkit) → monkey-skills |
| `complexity-critique` | joshuadavidthomas [`reducing-entropy`](https://github.com/joshuadavidthomas/agent-skills/tree/main/skills/reducing-entropy) → softaworks fork → monkey-skills（`reducing-entropy` → `complexity-critique` にリネーム） |

`skill-refactor`・`skill-tuning`・`proposal-critique`・`git-memory` はオリジナル設計。`skill-refactor` と `skill-tuning` は autonomous-loop + git-ratchet パターンの概念的影響源として `alchaincyf/darwin-skill`（MIT）と Andrej Karpathy の `autoresearch`（MIT）に言及しますが、architecture・gate function・evaluation rubric は独立した設計です。詳細は各 skill の `NOTICE` 参照。

## Repository 構成

```
dev-workflow/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── complexity-critique.md
│   ├── skill-creator-advance.md
│   ├── skill-refactor.md
│   └── skill-tuning.md
├── docs/
│   ├── skill-evolution-architecture.md
│   ├── skill-governance.md
│   ├── quarterly-audit-runbook.md
│   └── telemetry-setup.md
├── skills/
│   ├── brief-before-asking/
│   ├── complexity-critique/
│   ├── distill-sessions/
│   ├── dogfood-skill-testing/
│   ├── git-memory/
│   ├── handoff/
│   ├── proposal-critique/
│   ├── recap-state/
│   ├── skill-creator-advance/
│   ├── skill-judge/
│   ├── skill-refactor/
│   └── skill-tuning/
├── CHANGELOG.md
├── README.md
├── README.ja.md       (このファイル)
└── README.zh-TW.md
```

## インストール

`dev-workflow` は [monkey-skills](https://github.com/kouko/monkey-skills) marketplace の一部として配布されています。marketplace を追加して plugin をインストール：

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install dev-workflow@monkey-skills
```

## 使い方

4 つの slash command が plugin に同梱されています：

```
/skill-creator-advance      # 新規作成 または 既存の大規模再設計
/skill-refactor             # token / structure refactor、equivalence 保持
/skill-tuning               # human-judged な出力 A/B
/complexity-critique        # 具体的変更に対する deletion-first gate
```

残り 4 つの skill（`skill-judge`・`proposal-critique`・`git-memory`・`brief-before-asking`）は自然言語から auto-trigger します — 例：

```
「この skill を 8 次元 rubric で採点して」               → skill-judge
「この 12 項目の plan を critique して」                 → proposal-critique
「これから commit する — trailer 書くの手伝って」       → git-memory
```

Two-Hats split（refactor vs tuning）の walk-through は [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md) §2 参照。

## Contributing

貢献は repo 全体の convention（repo ルートの [`CLAUDE.md`](../CLAUDE.md)）に従います。

- **質問**：[kouko/monkey-skills](https://github.com/kouko/monkey-skills/issues) で GitHub Discussion または issue を開いてください。
- **PR**：`main` から branch を切り、Conventional Commits に従い、push 前にローカルで convention-drift CI script（`scripts/check-shared-conventions-drift.py`）を実行。
- **skill 内部の README** は skill owner が直接、より軽い rule set に従って執筆します（[`docs/skill-governance.md`](docs/skill-governance.md) §README Authoring Discipline 参照）。plugin レベルの README（このファイルとその翻訳）は `domain-teams:docs-team` を経由します。
- **新しい shared convention** を追加する際は、同じ PR 内で [`docs/skill-governance.md`](docs/skill-governance.md) の SSOT registry を更新し、drift CI manifest にもペアを追加してください。

## License

MIT。MIT-licensed な upstream を持つ skill（`skill-creator-advance`・`skill-judge`・`complexity-critique`）は、各 skill の `LICENSE` と `NOTICE` で完全な copyright chain を保持しています。

repo ルートの umbrella license は [LICENSE](../LICENSE) 参照。
