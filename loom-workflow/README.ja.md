# loom-workflow

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Claude Code と Codex 用の loom workflow plugin — 意思決定 brief、deletion-first critique gate、git-native な project memory、recap、handoff、session distill。

**Version**: 1.0.0 ・ **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) ・ **License**: MIT

## Background

Claude Code 向けの skill 開発は反復的な作業です。skill を draft してリリースしたあと、長すぎる、出力が tone 外れだといった問題を見つけて改善したくなります — ただし *どう* 改善するかは変更の種類によって変わります。**token / structure の refactor** は機械的に検証可能（変更後も output が同じはず）。**output quality の tuning** は taste-sensitive（どの variant が良いかは人間にしか判断できない）。`darwin-skill` 系のアプローチのように両者を 1 つの rubric に混ぜると、LLM-as-judge が人間の選好から離れた方向へ hill-climb してしまいます（Goodhart drift）。

`loom-workflow` は 2 つのアーキテクチャ的判断から育ちましたが、そのうち 1 つはすでに移転しています：

1. **Two Hats split for skills**（Fowler の refactor-vs-feature を skill authoring に適用）— `skill-refactor`（Phase A：behavior-preserving、auto-evaluable）と `skill-tuning`（Phase B：taste-sensitive、human-judged）の分離。この 2 つの skill は `skill-creator-advance`・`skill-judge` とともに `skill-dev-toolkit` へ移転済み。詳細は下の「Skill-evolution architecture（移転済み）」参照。
2. **critique-gate のライン** — proposal が commit になる前に介入する：`proposal-critique`（複数項目の triage）→ `complexity-critique`（単一変更の deletion-first gate）→ simplify（実装後の review、Anthropic 純正 toolkit に存在）。こちらは今も `loom-workflow` に残っています。

この plugin はさらに `git-memory`（commit trailer と PR 本文に書き込む可搬な project memory、git を読める任意のツールから復元可能）を保持しています。

運用ガバナンス：[`docs/skill-governance.md`](docs/skill-governance.md)。四半期ヘルスチェック：[`docs/quarterly-audit-runbook.md`](docs/quarterly-audit-runbook.md)。

## 収録基準（Admission rule）

ある skill が `loom-workflow` に属するのは、それが **クロスステーション（複数 station 間）かつ複数 session にまたがる調整** を行う場合です — 単に「複数の plugin から使われている」というだけでは条件を満たしません。広く使われているかどうかはテストではなく、station を横断して作業を調整するか、session をまたいで状態を運ぶかがテストです。`decision-map` がこのルールの最初の実例です：project のライフサイクルを通じて複数の station が読み書きする decision map（`MAP.md` + ticket）を永続化するもので、まさにこの plugin が存在する理由であるクロスステーション・複数 session の形をしています。このルールは **新規** の収録のみを gate します — plugin にすでにある既存の utility skill は grandfather 扱いとし、先送りになっている family-relocation arc でまとめて再評価します。

## Skills

| Skill | 役割 |
|---|---|
| [`brief-before-asking`](skills/brief-before-asking/) | user が複雑な engineering の fork を決める前に Mental-Model-first な briefing を届ける — これがデフォルトで、任意ではない。質問・説明・利害について user が迷った時にも反応的に発火する。 |
| [`complexity-critique`](skills/complexity-critique/) | 1 つの提案変更（refactor / feature / tech-debt）を deletion-first の視点で評価：before/after の LOC、何が obsolete になるか。複数項目の proposal → `proposal-critique`。 |
| [`cot-explain`](skills/cot-explain/) | すでにある推論——指定されたファイル、あるいは直前の作業——を、CoT 図を中心に据えた自己完結型ページに描き出す。各矢印にはその手順が続く理由がラベル付けされる。 |
| [`dbt-model-style`](skills/dbt-model-style/) | dbt + Redshift モデルの style & structure contract を強制する — CTE の役割、zero-logic な final CTE、命名、YAML header、comment、syntax。 |
| [`decision-map`](skills/decision-map/) | `docs/loom/maps/<map-id>/` にある永続的な decision map を作成・推進する — 目的地、育っていく Decisions-so-far ログ、そして複数 session にわたって ticket へ卒業していく Not-yet-specified（fog）list。一発 plan ではない。 |
| [`distill-sessions`](skills/distill-sessions/) | 過去の Claude Code と Codex の session transcript ＋ `/insights` から friction pattern を掘り出し、skill ごとの改善提案 doc にまとめる。 |
| [`git-memory`](skills/git-memory/) | 決定の文脈（diff そのものではなく **why**）を commit trailer と PR 本文に書き込み、Claude Code / Cursor / Codex / aider / 人間など将来のあらゆる session が `git log` だけから project knowledge を再構成できるようにする。 |
| [`goal-create`](skills/goal-create/) | goal condition を起草する — SESSION mode は長時間実行 agent run のための 4 フィールド停止条件（Outcome / Constraints / Verification / Stop-when）、ARC mode は repository の purpose artifact（`Why` / `Done when`）。 |
| [`handoff`](skills/handoff/) | session 状態を構造化された HANDOFF ファイルに保存し、将来の agent がきれいに再開できるようにする。あるいは既存の HANDOFF を読み込み・検証する。 |
| [`independent-advisor`](skills/independent-advisor/) | 現在の plan や決定について、**別の executor**——より強い model、より高い effort、あるいは別ベンダー——から second opinion を取る。変わるのは executor であって、critique の観点ではない。 |
| [`proposal-critique`](skills/proposal-critique/) | proposal（list / plan / 散文の推奨）を evidence grounding と YAGNI で KEEP / DEFER / DROP に triage。 |
| [`recap-state`](skills/recap-state/) | session 内での再オリエンテーション — user が話の筋を見失った時、Synthesis-check で締めくくる構造化 recap を出す。 |

12 個の skill はすべて **Active**。lifecycle 状態と所有権：[`docs/skill-governance.md`](docs/skill-governance.md)。

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

## Skill-evolution architecture（移転済み）

`skill-creator-advance`・`skill-refactor`・`skill-tuning`・`skill-judge` — この節がかつて説明していた、変更のサイズ × 評価モードによるライフサイクルモデル — は `dogfood-skill-testing` とともに `skill-dev-toolkit` へ移転しました。`loom-workflow` はもうこれらを同梱していません。元の設計理由（Two Hats split、機械的変更は auto-evaluation に耐えるが taste-sensitive な変更には人間が必要という評価コストの議論）は [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md) にアーカイブされています。現在の所有権と継続中の設計は `skill-dev-toolkit` 自身の README を参照してください。

## git-memory の 3 本柱

`git-memory` は次の 3 つの主張に基づきます：

1. **Carrier — git 成果物そのもの**。commit message と PR 本文が substrate。git を読めるツールならどれでも memory を読めます。`git clone` が memory を一緒に持ってきます。サーバーも embedding store も vendor lock-in もなし。
2. **Structure — commit trailer**。構造化された事実は git trailer に乗ります — `Co-Authored-By:` や `Signed-off-by:` と同じ仕組み。3 つの trailer で価値の ~80% をカバー：`Decision:`（なぜこのアプローチか）、`Learning:`（何を発見したか）、`Gotcha:`（未来の自分への trap）。
3. **Content — code ではなく決定の文脈**。diff は *何が* 変わったかをすでに示しています。memory は *why* を記録します。半年後に元の文脈が失われた時にもまだ価値がある entry を目指す — code そのものと冗長な entry ではなく。

`git-memory` は Claude Code 純正の `~/.claude/.../MEMORY.md` を補完します（置き換えません）。純正 memory は project 横断の user-level 選好を保持し、`git-memory` は repo 内に project 決定を保持します。

## Upstream chain

12 個の skill のうち 1 つが MIT-licensed な upstream に由来します。完全な attribution はその skill の `NOTICE` ファイル参照。（`skill-creator-advance` と `skill-judge` の upstream attribution は、移転先の `skill-dev-toolkit` に一緒に移りました。）

| Skill | Upstream chain |
|---|---|
| `complexity-critique` | joshuadavidthomas [`reducing-entropy`](https://github.com/joshuadavidthomas/agent-skills/tree/main/skills/reducing-entropy) → softaworks fork → monkey-skills（`reducing-entropy` → `complexity-critique` にリネーム） |

残り 11 個の skill はオリジナル設計で、外部 upstream への attribution はありません。詳細は各 skill の `NOTICE`（存在する場合）参照。

## Repository 構成

```
loom-workflow/
├── .claude-plugin/
│   └── plugin.json
├── docs/
│   ├── skill-evolution-architecture.md
│   ├── skill-governance.md
│   ├── quarterly-audit-runbook.md
│   └── telemetry-setup.md
├── skills/
│   ├── brief-before-asking/
│   ├── complexity-critique/
│   ├── cot-explain/
│   ├── dbt-model-style/
│   ├── decision-map/
│   ├── distill-sessions/
│   ├── git-memory/
│   ├── goal-create/
│   ├── handoff/
│   ├── independent-advisor/
│   ├── proposal-critique/
│   └── recap-state/
├── CHANGELOG.md
├── README.md
├── README.ja.md       (このファイル)
└── README.zh-TW.md
```

## インストール

`loom-workflow` は [monkey-skills](https://github.com/kouko/monkey-skills) marketplace の一部として配布されています。これは `dev-workflow` を置き換える hard-cut rename です。custom skill reference は `loom-workflow:<skill>` に更新してください。marketplace を追加して plugin をインストール：

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install loom-workflow@monkey-skills
```

## 使い方

`loom-workflow` は slash command を同梱していません — 12 個の skill はすべて自然言語から auto-trigger します。例：

```
「この 12 項目の plan を critique して」                  → proposal-critique
「これは削る価値があるか」/「そもそも作るべきか」          → complexity-critique
「これから commit する — trailer 書くの手伝って」         → git-memory
「看不懂」/「跟不上」/ agent-about-to-ask-complex-fork    → brief-before-asking
「開一張決策地圖」/「デシジョンマップを開く」              → decision-map
「wrap up」/「save state」                                → handoff
「where were we」/「我跟丟了」                             → recap-state
「second opinion」/「換一個模型看看」                      → independent-advisor
```

`skill-refactor` vs `skill-tuning` の Two-Hats split（移転済み）については、上の「Skill-evolution architecture（移転済み）」参照。

## Contributing

貢献は repo 全体の convention（repo ルートの [`CLAUDE.md`](https://github.com/kouko/monkey-skills/blob/main/AGENTS.md)）に従います。

- **質問**：[kouko/monkey-skills](https://github.com/kouko/monkey-skills/issues) で GitHub Discussion または issue を開いてください。
- **PR**：`main` から branch を切り、Conventional Commits に従い、push 前にローカルで convention-drift CI script（`scripts/check-shared-conventions-drift.py`）を実行。
- **skill 内部の README** は skill owner が直接、より軽い rule set に従って執筆します（[`docs/skill-governance.md`](docs/skill-governance.md) §README Authoring Discipline 参照）。plugin レベルの README（このファイルとその翻訳）は `domain-teams:docs-team` を経由します。
- **新しい shared convention** を追加する際は、同じ PR 内で [`docs/skill-governance.md`](docs/skill-governance.md) の SSOT registry を更新し、drift CI manifest にもペアを追加してください。

## License

MIT。plugin 内で唯一 MIT-licensed な upstream を持つ `complexity-critique` は、`LICENSE` と `NOTICE` で完全な copyright chain を保持しています。（`skill-creator-advance` と `skill-judge` は `skill-dev-toolkit` へ移転し、そちらで自身の copyright chain を保持しています。）

repo ルートの umbrella license は [LICENSE](https://github.com/kouko/monkey-skills/blob/main/LICENSE) 参照。
