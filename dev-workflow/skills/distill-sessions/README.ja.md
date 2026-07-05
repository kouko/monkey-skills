# Skill Log Mining

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> `~/.claude/projects` の JSONL transcript と `/insights` facet を
> 採掘し、ship 済みの `dev-workflow:*` と `loom-code:*` skill に
> 含まれる trigger 漏れ pattern を surface し、それぞれの SKILL.md
> に対する data-grounded な edit proposal を生成する。

ユーザーが明示的に invoke する **skill-iteration skill**：複数の PR
を回したあと、ship 済み skill のうちどれが under-trigger している
か、誤って trigger しているか、friction を蓄積しているかを知りたい
ときに、この skill を invoke して、ranked top-N report と各対象
SKILL.md に対する具体的な diff 案を得る。

この README は GitHub で skill を読む人間向け。Claude が実際に
load する operational ファイルは [`SKILL.md`](SKILL.md)。

---

## なぜこの skill が存在するのか

**graduation pipeline**：MEMORY.md には project ごとの feedback
memo が蓄積される — 「reviewer の mis-aggregation」「parallel
dispatch の doc-code race」「lint-checks.md という second drift
surface」など。各 entry は friction signal であり、たいてい特定の
ship 済み skill — description / anti-pattern list / activation
trigger が外したやつ — を指している。memo を手で読み返し、正しい
SKILL.md に折り返すことを覚えておく、というのがこの skill が防ぎたい
失敗 mode。

skill の著者自身ではこれを確実に検出できない。description を書いた
本人なので skill は *うまく狙えているように感じる*。実際の JSONL
transcript の記録 — 本来 fire すべきだったのに fire しなかった、
あるいは fire して直後にユーザーが interrupt した — と照合して
初めて gap が可視化される。

この skill がその測定を捕捉する。中核となる formula：

> **Shipped Skill Quality = description が主張する内容 × log が証明する内容**

ship 済み skill はそれぞれ正規化された 4 つの signal で ranking
される：

- **frequency_norm** — friction session に登場する回数
- **time_cost_norm** — 蓄積される friction 時間
- **cross_project_norm** — pattern が現れる project 数
- **recency_norm** — pattern の新しさ

high-confidence な対象は、過去 30 日に複数 project で繰り返し flag
されたもの。low-confidence な対象は、2 ヶ月前に 1 project で 1 回
だけ flag されたもの。

---

## どう動くのか

skill は multi-stage pipeline で動く：

```
~/.claude/projects/*.jsonl  +  ~/.claude/usage-data/facets
              │
              ▼  Stage 1+2: scripts/main.py
              │   - friction signal 検出
              │   - skill 単位の aggregation
              │   - top-N ranking
              ▼
       JSON payload (stdout) + Markdown summary (stderr)
              │
              ▼  Stage 3: orchestrator が loom-code:dispatching-parallel-agents
              │   経由で subagent を dispatch
              │   - (skill, session) ごとに Haiku-4.5 subagent 1 つ
              │   - friction に応じて failure / success prompt を選択
              ▼
       trajectory ごとの分析 JSON
              │
              ▼  Stage 3 (続き): scripts/propose.py
              ▼
       diff ファイル（SKILL.md への提案 edit）
              │
              ▼  人間 review（silent-writes は refuse）
              │
              ▼  scripts/apply.py --approved
              ▼
       edit が対象 SKILL.md に反映される
```

完全な手順は [`SKILL.md`](SKILL.md) §Pipeline を参照。

### v0.3 の主要機能

- **クロススキル friction-density routing** — session が複数の
  対象 skill を invoke した場合（e.g. brainstorming + writing-plans）、
  Memory Items はそのセッション内で最も高い severity score を持つ
  skill にルートされる — 字句的に最初の skill ではない。これにより
  feedback は friction の original owner となる skill に帰属される。

- **高-friction-success session の デュアルディスパッチ** —
  `friction_level="high"` かつ outcome=success に分類される session
  は、**2 つの** subagent_payload entry を emit する — 1 つは
  failure-analysis に、もう 1 つは success-analysis に。
  `--max-trajectories-per-skill` budget はどちらのディスパッチも
  カウントする。

- **Stage 4 cluster + N≥2 promotion** — Memory Items は normalized
  (title, section_anchor) pair でクラスタリングされる。N≥2 個の
  supporting session を持つ item は §"Proposed additions" /
  §"Proposed modifications" に promote される；single-session item
  (N=1) は新しい §"Cross-session evidence pending" bucket にルートされ、
  2 番目の session がマッチすると自動的に re-promote される。

---

## Installation

skill は `dev-workflow` plugin に同梱されている。Claude Code 上で：

```
Skill(skill: "dev-workflow:distill-sessions")
```

slash-command alias が設定されていれば：

```
/distill-sessions
```

外部依存は無し — Python script は stdlib のみで動き、
`python3.11+` を対象とする。

---

## Quick start

```bash
# repo root から、override 無しで Q5 default を使う場合：
cd dev-workflow/skills/distill-sessions/scripts
python3 main.py
```

出力イメージ：

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

stdout には次の stage が消費する完全な JSON payload
（top_skills + subagent_payload）が出る。

---

## Configuration

v0.1 は brief Q5 由来の baked-in default を 6 つ持つ。override
する場合は JSON config を渡す：

```bash
python3 main.py --config /path/to/my-thresholds.json
```

override schema の詳細は [`SKILL.md`](SKILL.md) §Configuration
を参照。よく使う lever 用に CLI flag も用意されている：

- `--target-skill-pattern`（default `loom-code:*`）
- `--top-n`（default `5`）
- `--max-trajectories-per-skill`（default `5`）
- `--project-root`（`~/.claude/projects` の override、主に test 用）
- `--facets-root`（`~/.claude/usage-data/facets` の override）

---

## Future roadmap

v0.2+ で deferred になっている項目（完全な list は
[`SKILL.md`](SKILL.md) §Future）：

- run をまたいで proposal が衝突した場合の Stage 4 SDD 統合
- override schema を YAML に切替
- run をまたぐ fingerprint ledger の永続化
- Codex / Gemini / Cline / Cursor CLI adapter
- Layer A の standalone OSS surface

---

## ライセンス

この skill は [monkey-skills](https://github.com/kouko/monkey-skills)
repository の一部で、MIT License で配布される — 詳細は repository
root の `LICENSE` を参照。

### 第三者帰属

`agents/` 配下の 2 つの prompt-analyst template は Trace2Skill
(arxiv 2603.25158 / github.com/Qwen-Applications/Trace2Skill, Apache 2.0
License) の direct adaptation である。monkey-skills の MIT license は
upstream の Apache 2.0 license と互換性があり — 両方とも商用利用 +
派生作成を attribution preservation 条件で許諾する。
