# dev-workflow

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**：1.7.0
**Part of**：[monkey-skills](https://github.com/kouko/monkey-skills)

Developer workflow skills — skill 作成、skill 品質採点、ポータブルな
git ベースのプロジェクト記憶、そして design 判断のための「critique」
ライン（コード前の提案 / 既存コードへの単一改動）。

## Skills

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `skill-creator-advance` | `/skill-creator-advance` | 新しい skill を作成し、eval-driven loop で反復的に改善する |
| `skill-judge` | — | 8 観点の品質ルーブリックで既存 skill を採点する（advisory、0-120 スケール）|
| `git-memory` | — | git commit trailer + PR body `## Memory` セクション経由で、ポータブルかつツール非依存のプロジェクト記憶を実現 |
| `proposal-critique` | — | evidence grounding + YAGNI により多項目提案（list、plan、prose）を KEEP / DEFER / DROP に振り分ける |
| `complexity-critique` | `/complexity-critique` | 既存 code に対する単一の提案改動（refactor、feature add、debt cleanup）を、実装前に 3 つの deletion-first 質問で gate する |
| `skill-refactor` | `/skill-refactor` | 既存 skill のトークン / 構造リファクタを、出力動作保持の保証付きで実行（multi-judge ensemble + git ratchet；skill-evolution アーキテクチャの Phase A）|
| `skill-tasting` | `/skill-tasting` | 既存 skill の出力品質 A/B — 異なる出力傾向の variant 生成、ブラインド実行、ユーザー選好捕捉。Constitution が床、taste が天井、preference log は RLHF-lite データセット（skill-evolution の Phase B）|

### "critique" ライン

`proposal-critique` と `complexity-critique` は姉妹である — 同じ
gate-skill の形、異なる scope とライフサイクル段階：

```
proposal-critique  →  complexity-critique  →  Anthropic simplify
（list / plan      （既存 code に対する     （post-implementation
 / prose、          単一改動、              diff review）
 まだ code がない）  実装前）
```

両者で「やる価値があるか」の判断空間の大部分を、gate ロジックを
重複させずにカバーする。

### Skill-evolution アーキテクチャ（skill-refactor + 将来の skill-tasting）

dev-workflow plugin は skill 作成・評価・進化のための 4-skill
ファミリーを段階的に展開中：

```
skill-creator-advance  →  skill-refactor  →  skill-tasting  →  skill-judge
（作成 + 再設計；spec-     （Phase A: トークン   （Phase B: 出力品質   （advisory
 first；フル eval ループ）  / 構造リファクタ；    A/B；人間 judge；    スコア；改変
                            出力保持；git ratchet）preference log）    なし）
```

- `skill-refactor`（v1.6.0）は既存 skill の*動作保持*リファクタ
  を扱う
- `skill-tasting`（このリリース、v1.7.0）は taste-sensitive な
  出力 A/B を人間判断 + preference log で扱う
- 分割は単一 rubric が抱える LLM-as-judge / Goodhart drift 問題を
  避ける — 完全な根拠は [`docs/skill-evolution-architecture.md`](docs/skill-evolution-architecture.md)

### git-memory — 3 つの柱

記憶は git artifact 自体に存在するため、git を読めるあらゆるツール
（Claude Code / Cursor / Codex / aider / 人間）が、別途ストアを
用意しなくてもプロジェクト知識を再構築できる。

1. **Carrier = git artifact 自体** — commit message と PR body
   が基盤となる。`git clone` で記憶も一緒に取得できる；別個の
   DB、embedding index、ベンダー固有ファイルは不要。
2. **Structure = commit trailer** — `Decision:` / `Learning:` /
   `Gotcha:` を `Co-Authored-By:` と並んで commit footer に
   記載する（`git-interpret-trailers(1)` の仕組み）。
   `git log --pretty='%(trailers)'` で機械可読、prose body で人間可読。
3. **Content = decision context、コードではない** — **なぜ**を
   記録し、**何を**ではない。diff がすでに「何を」を示している；
   記憶は推論過程、却下された代替案、将来の自分への注意点を記録する。

git-memory は Claude Code ネイティブの `~/.claude/.../MEMORY.md`
（user レベルの設定）を補完する。プロジェクトレベルの決定は git に、
user レベルの設定は Claude ネイティブ記憶に残す。

## Upstream Chain（MIT）

```
Anthropic skill-creator (MIT)
  → AllanYiin (尹相志) skill-creator-advanced (MIT, github.com/AllanYiin/Amon)
    → kouko dev-workflow/skill-creator-advance (MIT)
```

完全な license / attribution の詳細は skill ディレクトリの `LICENSE` と
`NOTICE` を、repo 全体のまとめは [`../ATTRIBUTION.md`](../ATTRIBUTION.md) を参照。

## 本ディストリビューションで追加した 7 つの強化

1. monkey-skills エコシステム統合ガイド
2. Description のベストプラクティス（negative trigger、多言語 keyword）
3. Eval flow の階層化（quick path vs full path）
4. 既存 skill の改善 workflow
5. Slash command 作成ガイド
6. 自己評価 pass（人間 review 前に明らかな欠陥を自動修正）
7. イテレーション間の auto-regression 検出

## Design 決定

- Eval 結果を **inline + markdown report** で提示（browser-based eval-viewer は廃止；Python web server + ブラウザ依存を除去）
- **token ベース budget**（約 6,000 token）を採用、行ベース（500 行）から変更
- Platform adaptation は reference file に切り出し（任意、必要に応じてロード）
- Eval 方法論は一次資料 citation で根拠付け（Fisher 1935、Beck 2002、Hastie et al. 2009、Myers et al. 2011、ISTQB v4.0）

## Repository 構造

```
dev-workflow/
├── .claude-plugin/plugin.json
├── CHANGELOG.md
├── commands/
│   ├── skill-creator-advance.md
│   └── complexity-critique.md
└── skills/
    ├── skill-creator-advance/
    │   ├── SKILL.md
    │   ├── LICENSE               ← AllanYiin + kouko copyright
    │   ├── NOTICE                ← Upstream chain 詳細
    │   ├── agents/               ← grader / comparator / analyzer
    │   ├── scripts/              ← aggregate_benchmark / run_eval / run_loop / improve_description / package_skill / quick_validate / generate_report
    │   └── references/           ← plugin-conventions / iteration-automation / platform-adaptations / eval-methodology / schemas / mermaid-usage-guidelines
    ├── skill-judge/
    │   ├── SKILL.md              ← 8 観点ルーブリック（E:A:R + 5-pattern + 9 failure-pattern）
    │   ├── LICENSE / NOTICE      ← upstream attribution
    │   └── README.{en,ja,zh-TW}.md
    ├── git-memory/
    │   ├── SKILL.md
    │   ├── standards/             ← memory-conventions（trailer schema、PR body、diagram venue）
    │   ├── protocols/             ← compose-commit / compose-pr
    │   └── scripts/               ← memory-grep retrieval primitive
    ├── proposal-critique/
    │   ├── SKILL.md               ← 単一ファイル gate skill（Iron Law / Gate Function / Triage Matrix）
    │   └── README.{en,ja,zh-TW}.md
    ├── complexity-critique/
    │   ├── SKILL.md               ← 単一ファイル gate skill（Iron Law / 3 Questions / Verdict）
    │   ├── LICENSE / NOTICE       ← joshuadavidthomas → softaworks → kouko MIT chain
    │   └── README.{en,ja,zh-TW}.md
    ├── skill-refactor/
    │   ├── SKILL.md               ← Phase A: トークン / 構造リファクタ、等価性保証
    │   ├── LICENSE / NOTICE       ← 独自設計；darwin-skill との設計差異を記載
    │   ├── README.{en,ja,zh-TW}.md
    │   ├── references/            ← equivalence-check / multi-judge / refactor-moves / golden-anchor / test-prompts-schema / constitution-schema（共有 convention の canonical SoT）
    │   └── scripts/               ← equivalence_check / multi_judge / golden_compare
    └── skill-tasting/
        ├── SKILL.md               ← Phase B: 出力品質 A/B、人間 judge + preference log
        ├── LICENSE / NOTICE       ← 独自設計；darwin-skill との設計差異 9 点
        ├── README.{en,ja,zh-TW}.md
        ├── references/            ← ab-harness / constitutional-judging / preference-log-schema / self-trained-judge-pipeline + 3 共有 convention の同梱 functional copy
        └── scripts/               ← ab_harness / preference_log / judge_train_stub
```

dev-workflow/ 直下に `docs/skill-evolution-architecture.md` も追加
（H1-H4 horizon プランニング doc）。

## License

MIT — repository root [`LICENSE`](../LICENSE) および skill レベルの
[`LICENSE`](skills/skill-creator-advance/LICENSE) / [`NOTICE`](skills/skill-creator-advance/NOTICE) を参照。
