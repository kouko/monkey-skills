# Skill Log Mining

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 挖掘 `~/.claude/projects` JSONL transcript 與 `/insights` facet，
> surface 已 ship 的 `dev-workflow:*` 與 `loom-code:*` skill 中
> 的 trigger 遺漏 pattern，並對各對象 SKILL.md 產出 data-grounded
> 的 edit proposal。

使用者主動 invoke 的 **skill-iteration skill**：跑完一輪多 PR 的
工作後，如果想知道哪些已 ship 的 skill 正在 under-trigger、
誤觸發、或累積 friction，就 invoke 這個 skill，得到 ranked top-N
report 與每個目標 SKILL.md 的具體 diff 建議。

這份 README 是給在 GitHub 上閱讀本 skill 的人類看的。Claude 真正
load 的 operational 檔案是 [`SKILL.md`](SKILL.md)。

---

## 為什麼有這個 skill

**graduation pipeline**：MEMORY.md 會累積各 project 的 feedback
memo — 像「reviewer mis-aggregation」、「parallel dispatch 的
doc-code race」、「lint-checks.md 是 second drift surface」等。
每個 entry 都是 friction signal，通常指向某個已 ship 的 skill —
description / anti-pattern list / activation trigger 沒擋住的那種。
手動讀完 memo、再記得折回正確的 SKILL.md，就是這個 skill 想防的
失敗 mode。

skill 的作者自己很難可靠地察覺。description 是自己寫的，所以
skill *感覺起來*瞄得很準。只有跟實際的 JSONL transcript 紀錄對照 —
本來該 fire 沒 fire、或 fire 後使用者立刻 interrupt — gap 才會
浮現。

這個 skill 把那把尺的量法捕捉下來。核心 formula：

> **Shipped Skill Quality = description 宣稱的內容 × log 證明的內容**

每個已 ship 的 skill 都會用 4 個 normalized signal 來 ranking：

- **frequency_norm** — 在 friction session 出現的次數
- **time_cost_norm** — 累積的 friction 時間
- **cross_project_norm** — 出現該 pattern 的 project 數
- **recency_norm** — pattern 的新舊程度

high-confidence 對象 = 過去 30 天在多個 project 反覆 flag 的；
low-confidence 對象 = 兩個月前只在一個 project flag 過一次的。

---

## 怎麼運作

skill 跑 multi-stage pipeline：

```
~/.claude/projects/*.jsonl  +  ~/.claude/usage-data/facets
              │
              ▼  Stage 1+2: scripts/main.py
              │   - friction signal 偵測
              │   - 以 skill 為單位 aggregate
              │   - top-N ranking
              ▼
       JSON payload (stdout) + Markdown summary (stderr)
              │
              ▼  Stage 3: Claude 透過 loom-code:dispatching-parallel-agents
              │   dispatch subagent
              │   - 每個 (skill, session) 一個 Haiku-4.5 subagent
              │   - 依 friction 選 failure / success prompt
              ▼
       per-trajectory 分析 JSON
              │
              ▼  Stage 3 (續): scripts/propose.py
              ▼
       diff 檔（對 SKILL.md 的建議 edit）
              │
              ▼  人類 review（silent-writes 會 refuse）
              │
              ▼  scripts/apply.py --approved
              ▼
       edit 落入目標 SKILL.md
```

完整 step-by-step 見 [`SKILL.md`](SKILL.md) §Pipeline。

### v0.3 主要功能

- **跨技能 friction-density routing** — 當 session 呼叫多個
  目標 skill 時（例如 brainstorming + writing-plans），Memory Items
  會 route 到該 session 中 severity score 最高的 skill，而不是
  字典序最前的 skill。這確保 feedback 歸到 friction 真正來源的 skill。

- **高 friction 成功 session 的雙派遣** — 分類為
  `friction_level="high"` 且 outcome=success 的 session 會發出
  **2 個** subagent_payload entry — 一個給 failure-analysis，
  一個給 success-analysis。`--max-trajectories-per-skill` 預算
  會計入兩個派遣。

- **Stage 4 cluster + N≥2 晉升** — Memory Items 按 normalized
  (title, section_anchor) pair 進行 cluster。具有 N≥2 個supporting
  session 的 item 會升格到 §"Proposed additions" / §"Proposed
  modifications"；單一 session 的 item (N=1) 會 route 到新的
  §"Cross-session evidence pending" bucket，待累積到 2 個 session
  時自動晉升。

---

## Installation

skill 隨 `dev-workflow` plugin 一起 ship。在 Claude Code 中：

```
Skill(skill: "dev-workflow:distill-sessions")
```

若有設定 slash-command alias：

```
/distill-sessions
```

無外部依賴 — Python script 只用 stdlib，目標為 `python3.11+`。

---

## Quick start

```bash
# 從 repo root 起，不加 override，使用 Q5 default：
cd dev-workflow/skills/distill-sessions/scripts
python3 main.py
```

預期輸出示意：

```
# distill-sessions v0.1 — run summary    (stderr)

- run_id: `b3a1...`
- target_pattern: `loom-code:*`
- top_n: 5
- max_trajectories_per_skill: 5

## Top skills

- **loom-code:writing-plans**
  - session `2026-05-20-...`: friction=high, events=12
  - session `2026-05-18-...`: friction=mid,  events=7
- **loom-code:brainstorming**
  - session `2026-05-19-...`: friction=mid,  events=5
...
```

stdout 會輸出下一 stage 要消化的完整 JSON payload
（top_skills + subagent_payload）。

---

## Configuration

v0.1 內建來自 brief Q5 的 6 個 baked-in default。要 override 的話
傳 JSON config：

```bash
python3 main.py --config /path/to/my-thresholds.json
```

完整 override schema 見 [`SKILL.md`](SKILL.md) §Configuration。
常用 lever 也提供了 CLI flag：

- `--target-skill-pattern`（default `loom-code:*`）
- `--top-n`（default `5`）
- `--max-trajectories-per-skill`（default `5`）
- `--project-root`（`~/.claude/projects` override，主要給測試用）
- `--facets-root`（`~/.claude/usage-data/facets` override）

---

## Future roadmap

v0.2+ deferred 項目（完整 list 見 [`SKILL.md`](SKILL.md) §Future）：

- 跨 run proposal 衝突時的 Stage 4 SDD 整併
- override schema 改用 YAML
- 跨 run 的 fingerprint ledger 永續化
- Codex / Gemini / Cline / Cursor CLI adapter
- Layer A 的 standalone OSS surface

---

## 授權

本 skill 屬於 [monkey-skills](https://github.com/kouko/monkey-skills)
repository，採 MIT License — 詳見 repository root 的 `LICENSE`。

### 第三方歸屬

`agents/` 目錄下兩個 prompt-analyst template 為 Trace2Skill
(arxiv 2603.25158 / github.com/Qwen-Applications/Trace2Skill, Apache 2.0
License) 之直接改作。monkey-skills 的 MIT license 與 upstream 的 Apache 2.0
license 相容 — 雙方皆允許商業使用與衍生作品,且需保留 attribution。
