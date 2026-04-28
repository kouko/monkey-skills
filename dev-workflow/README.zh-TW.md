# dev-workflow

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**Version**：1.0.4
**Part of**：[monkey-skills](https://github.com/kouko/monkey-skills)

Skill 建立與 eval workflow — 用於撰寫新 Claude skill 的迭代式 draft → test → review → improve loop。

## Skills

| Skill | Slash cmd | Role |
|-------|-----------|------|
| `skill-creator-advance` | `/skill-creator-advance` | 建立新 skill 並透過 eval-driven loop 持續改進 |
| `git-memory` | — | 透過 git commit trailer + PR body `## Memory` 區段提供可攜、與工具無關的專案記憶 |
| `proposal-critique` | — | 以 evidence grounding + YAGNI 將提案（list、plan 或 prose）分類為 KEEP / DEFER / DROP |

### git-memory — 三大支柱

記憶存在於 git artifact 本身，因此任何能讀取 git 的工具
（Claude Code / Cursor / Codex / aider / 人類）都能在不依賴額外儲存的情況下
重建專案知識。

1. **Carrier = git artifact 本身** — commit message 與 PR body
   就是承載介質。`git clone` 即帶來記憶；不需要獨立 DB、
   embedding index，也不需要任何特定工具的檔案。
2. **Structure = commit trailer** — `Decision:` / `Learning:` /
   `Gotcha:` 與 `Co-Authored-By:` 一起出現在 commit footer
   （`git-interpret-trailers(1)` 機制）。透過
   `git log --pretty='%(trailers)'` 可被機器讀取，prose body 則供人類閱讀。
3. **Content = decision context，不是 code** — 紀錄**為什麼**，
   不是**做了什麼**。diff 已經說明做了什麼；記憶要紀錄的是
   推論過程、被否決的替代方案，以及給未來自己的注意事項。

git-memory 補充 Claude Code 原生的 `~/.claude/.../MEMORY.md`
（user 層級的偏好設定）。專案層級的決策放在 git；
user 層級的偏好留在 Claude 原生記憶。

## Upstream Chain（MIT）

```
Anthropic skill-creator (MIT)
  → AllanYiin (尹相志) skill-creator-advanced (MIT, github.com/AllanYiin/Amon)
    → kouko dev-workflow/skill-creator-advance (MIT)
```

完整 license / attribution 細節在 skill 目錄下的 `LICENSE` 與
`NOTICE`；整 repo 摘要請見 [`../ATTRIBUTION.md`](../ATTRIBUTION.md)。

## 本發行版加入的 7 項強化

1. monkey-skills 生態系整合指引
2. Description 最佳實務（negative trigger、多語 keyword）
3. Eval flow 分級（quick path vs full path）
4. 既有 skill 改進 workflow
5. Slash command 建立指引
6. 自我評估 pass（在人工 review 前自動修補明顯缺陷）
7. 跨迭代 auto-regression 偵測

## Design 決策

- Eval 結果以 **inline + markdown report** 呈現（不再使用 browser-based eval-viewer；移除 Python web server + 瀏覽器相依）
- 採 **token-based budget**（約 6,000 token），取代行數 budget（500 行）
- 平台調整內容抽出至 reference file（選用，按需載入）
- Eval 方法論以一手來源 citation 錨定（Fisher 1935、Beck 2002、Hastie et al. 2009、Myers et al. 2011、ISTQB v4.0）

## Repository 結構

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
    │   ├── NOTICE                ← Upstream chain 細節
    │   ├── agents/               ← grader / comparator / analyzer
    │   ├── scripts/              ← aggregate_benchmark / run_eval / run_loop / improve_description / package_skill / quick_validate / generate_report
    │   └── references/           ← plugin-conventions / iteration-automation / platform-adaptations / eval-methodology / schemas / mermaid-usage-guidelines
    ├── git-memory/
    │   ├── SKILL.md
    │   ├── standards/             ← memory-conventions（trailer schema、PR body、diagram venue）
    │   ├── protocols/             ← compose-commit / compose-pr
    │   └── scripts/               ← memory-grep retrieval primitive
    └── proposal-critique/
        └── SKILL.md               ← 單檔 gate skill（Iron Law / Gate Function / Triage Matrix）
```

## License

MIT — 請見 repository root [`LICENSE`](../LICENSE) 與 skill 層級
[`LICENSE`](skills/skill-creator-advance/LICENSE) / [`NOTICE`](skills/skill-creator-advance/NOTICE)。
