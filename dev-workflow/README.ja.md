# dev-workflow

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**：1.0.4
**Part of**：[monkey-skills](https://github.com/kouko/monkey-skills)

Skill 作成と eval workflow — 新しい Claude skill を作成するための反復的な draft → test → review → improve loop。

## Skills

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `skill-creator-advance` | `/skill-creator-advance` | 新しい skill を作成し、eval-driven loop で反復的に改善する |
| `git-memory` | — | git commit trailer + PR body `## Memory` セクション経由で、ポータブルかつツール非依存のプロジェクト記憶を実現 |
| `proposal-critique` | — | evidence grounding + YAGNI により提案（list、plan、prose）を KEEP / DEFER / DROP に振り分ける |

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
│   └── skill-creator-advance.md
└── skills/
    ├── skill-creator-advance/
    │   ├── SKILL.md
    │   ├── LICENSE               ← AllanYiin + kouko copyright
    │   ├── NOTICE                ← Upstream chain 詳細
    │   ├── agents/               ← grader / comparator / analyzer
    │   ├── scripts/              ← aggregate_benchmark / run_eval / run_loop / improve_description / package_skill / quick_validate / generate_report
    │   └── references/           ← plugin-conventions / iteration-automation / platform-adaptations / eval-methodology / schemas / mermaid-usage-guidelines
    ├── git-memory/
    │   ├── SKILL.md
    │   ├── standards/             ← memory-conventions（trailer schema、PR body、diagram venue）
    │   ├── protocols/             ← compose-commit / compose-pr
    │   └── scripts/               ← memory-grep retrieval primitive
    └── proposal-critique/
        └── SKILL.md               ← 単一ファイル gate skill（Iron Law / Gate Function / Triage Matrix）
```

## License

MIT — repository root [`LICENSE`](../LICENSE) および skill レベルの
[`LICENSE`](skills/skill-creator-advance/LICENSE) / [`NOTICE`](skills/skill-creator-advance/NOTICE) を参照。
