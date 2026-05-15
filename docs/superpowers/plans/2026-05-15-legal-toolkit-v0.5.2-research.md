# legal-toolkit v0.5.2 SP3-b `legal-research` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `legal-research` skill (Phase 3 SP3-b IRAC cluster, sub-skill 2 of 2), bumping legal-toolkit to v0.5.2 and unlocking router Q4-law-lookup dispatch path. Plugin grows from 6 → 7 active skills.

**Architecture:** Agent abstraction (plan-adapt-interact). LLM-driven loop with deterministic state tracking via `state.json` checkpoint file. Plan-first 半互動: skill emits `plan.md` (search keywords + target sites + 法源 type budget) → user Y/n confirms → autonomous WebFetch loop runs to early-stop OR cap. Hybrid stop criteria: ≤ 5 rounds OR ≤ 30 fetches; early-stop on ≥ 8 sources AND ≥ 2 法源類型; forced_stop emits ⚠️ marker.

**Tech Stack:** Python 3.11 (grader + tests via pytest), JSON Schema (plan / state / output validation), Markdown (skill content + protocols + references + READMEs), WebFetch (Claude Code built-in tool; no Python scrapers), Bash (drift verify CI script).

**Spec doc:** [`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) — read §6 (research detailed design) + §7 (cross-cutting) + §8 (ship sequence) before starting any task.

---

## File Structure

**Created:**
- `legal-toolkit/skills/legal-research/SKILL.md` (~5,500 tokens)
- `legal-toolkit/skills/legal-research/README.md` / `README.ja.md` / `README.zh-TW.md`
- `legal-toolkit/skills/legal-research/protocols/plan.md` / `iterative-search.md` / `triangulate.md` / `cite.md`
- `legal-toolkit/skills/legal-research/references/webfetch-targets.md` / `citation-format.md` / `triangulation-rules.md` (all `[draft]`)
- `legal-toolkit/skills/legal-research/assets/plan-schema.json` / `state-schema.json` / `output-schema-memo.json` / `output-schema-summary.json` / `triangulation-config.json`
- `legal-toolkit/skills/legal-research/scripts/grade_research.py`
- `legal-toolkit/skills/legal-research/tests/test_grade_research.py`
- `legal-toolkit/skills/legal-research/tests/fixture-*.md` + `fixture-state-*.json` (~13 fixtures FLAT in tests/)

**Modified:**
- `legal-toolkit/skills/using-legal-toolkit/SKILL.md` (Q4-law-lookup dispatch unlock + frontmatter description sync + version bump)
- `legal-toolkit/scripts/verify-drift.py` (uncomment forward-stub for `grade_research.py` → 4-grader bank coverage)
- `legal-toolkit/.claude-plugin/plugin.json` (version 0.5.0 → 0.5.2; description += research)
- `.claude-plugin/marketplace.json` (description byte-identical sync)
- `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` (skill list 6 → 7)
- `legal-toolkit/ROADMAP.md` (Phase 3 SP3-b ✅ DONE marker)

**Parallelizable subagent dispatch:**
- Task 2 (4 protocol files) — 4 parallel implementer subagents
- Task 3 (3 reference files) — 3 parallel implementer subagents
- Task 4 (5 schemas) — single subagent (small JSON files; one shot)
- Task 8 (3 READMEs) — 3 parallel implementer subagents
- Other tasks: sequential (have dependencies)

---

## Task 1: Skill scaffold (SKILL.md + folder layout)

**Files:**
- Create: `legal-toolkit/skills/legal-research/SKILL.md`
- Create: `legal-toolkit/skills/legal-research/{protocols,references,assets,scripts,tests}/.gitkeep`

- [ ] **Step 1: Create folder structure (FLAT, single-level)**

```bash
cd /Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+legal-toolkit-v0.5.2-research
mkdir -p legal-toolkit/skills/legal-research/{protocols,references,assets,scripts,tests}
touch legal-toolkit/skills/legal-research/{protocols,references,assets,scripts,tests}/.gitkeep
```

Verify: 5 single-level subfolders + SKILL.md (no `tests/fixtures/` nested — fixtures go FLAT in `tests/` per Anthropic flat-folder rule). Confirmed by v0.5.0 precedent.

- [ ] **Step 2: Author SKILL.md frontmatter + body**

Frontmatter:

```yaml
---
name: legal-research
description: |
  IRAC legal-research skill for Taiwan in-house 法務. Takes a 法律問題 / 條文 / 判例 query, runs plan-first 半互動 Agent loop (LLM plans search → user Y/n confirms → autonomous WebFetch + triangulation + Harvey doc-level citation), and produces 2-file output (research-memo.md + executive-summary.md). Loop cap: ≤ 5 rounds OR ≤ 30 fetches; early-stop on ≥ 8 sources + ≥ 2 法源類型; forced_stop emits ⚠️ marker. No profile.yml dependency. §6.3 disclaimer footer + §6.4 escalation override inherited from v0.4.x.

  TRIGGER (中英雙語):
  - 「查 §」/「§227 是」/「判例」/「法條」/「找判決」/「research」/「lookup」
  - "law-text lookup" / "find precedent" / "research the case" / "what does §X say"
  - 條文號 + 法典名 patterns (e.g. 「民法 §184」/「個資法 §27」)

  USE WHEN: user wants literal law-text / 判例 / 函釋 lookup with structured iterative search + triangulation + citation. NOT for fact-pattern analysis (use legal-issue-spot).
version: 0.1.0
---
```

Body covers (~5,500 tokens / ~4,500 words):
1. **Language Policy** (instructions EN; user-facing zh-TW; mixed by design)
2. **Workflow mermaid** (USER query → plan.md → user Y/n → loop: state.json check → iterative-search → triangulate → cite → 2-file output)
3. **4 protocol pointers** (relative paths + 1-line purpose):
   - `protocols/plan.md` — Emit search strategy (keywords + target sites + 法源 type plan + budget)
   - `protocols/iterative-search.md` — Single-round logic (read state.json → check budget → WebFetch → write candidates → update state.json)
   - `protocols/triangulate.md` — Triangulation judgement → early-stop or continue
   - `protocols/cite.md` — Synthesize research-memo.md + executive-summary.md with doc-level citations
4. **3 reference pointers**:
   - `references/webfetch-targets.md` — Target sites (law.moj.gov.tw / judicial.gov.tw / 主管機關 RSS) + crawl etiquette + fallbacks
   - `references/citation-format.md` — Harvey doc-level citation format examples
   - `references/triangulation-rules.md` — 法源類型 classification + ∩ rules
5. **Plan-first 半互動 contract** (plan.md preview → stdout Y/n → autonomous loop)
6. **Agent loop spec** (state.json checkpoint + cap rules):
   - max_rounds = 5
   - max_fetches = 30
   - early_stop: ≥ 8 sources AND ≥ 2 法源類型 covered
   - forced_stop: cap reached AND early_stop not met → memo prepends ⚠️ "覆蓋未達 triangulation" block
7. **Output contract**: `legal-outputs/<timestamp>-research-<topic>/{plan.md, state.json, research-memo.md, executive-summary.md}`
   - `research-memo.md` sections: §問題 / §搜尋摘要 / §法源分析 / §結論 / §Citations / §Disclaimer (+ conditional ⚠️ triangulation 警告 block)
   - `executive-summary.md` sections: §問題 / §結論 (✅/⚠️/❌) / §依據 / §風險提示 / §Disclaimer (+ conditional §Escalation when forced_stop OR 涉及 高風險 法律議題)
8. **§6.3 Disclaimer footer requirement** (defer to risk-grade.md text equivalent OR own boilerplate; specify ownership)
9. **§6.4 Escalation Override** (forced_stop → §Escalation REQUIRED in summary; 刑事 / 訴訟 / 跨境 issues → §Escalation REQUIRED)
10. **Cross-skill handoff (inbound only)**: issue-spot business.md hands off via `/legal-research --query="..."` (already documented in issue-spot SKILL.md); research treats incoming query string as opaque input.
11. **Path A discipline**: Taiwan in-force law; 即時 not 72hr; 委託/受託 not controller/processor; 民法 §12-13 not PDPA minor age (inherited)
12. **WebFetch crawl etiquette**: rate-limit awareness; User-Agent declaration; fallback to Google cache / archive.org Wayback if anti-bot
13. **When to use / NOT to use**:
    - USE for: literal law-text lookup / 判例 / 函釋 / 學說 search; condition number lookup
    - NOT for: fact-pattern analysis (use legal-issue-spot); contract review (legal-contract-review); document drafting (legal-document-draft); incident response (legal-incident-response)
14. **Inputs** (query string) / **Outputs** (4 files in `legal-outputs/<ts>-research-<topic>/`)
15. **Reference links** to PRODUCT-SPEC + ROADMAP + design spec

- [ ] **Step 3: Verify token budget + flat-folder check**

```bash
wc -w legal-toolkit/skills/legal-research/SKILL.md
# Expected: ~4,000-5,000 words (~5,500 tokens)

find legal-toolkit/skills/legal-research -type d
# Expected: skill root + 5 single-level subfolders (NO tests/fixtures/)
```

- [ ] **Step 4: Commit**

```bash
git add legal-toolkit/skills/legal-research/
git commit -m "feat(legal-toolkit): legal-research skill scaffold (SKILL.md + folder)

Phase 3 SP3-b v0.5.2. Scaffolds the IRAC research Agent skill with
SKILL.md (frontmatter + workflow body + plan-first 半互動 contract +
Agent loop spec + protocol/reference/output pointers) and 5
single-level subfolders (protocols/ references/ assets/ scripts/ tests/)
per Anthropic flat-folder rule.

Skill is profile.yml-independent (input is law-text query). Plan-first
互動 contract: plan.md preview → user Y/n → autonomous loop. Loop cap
≤ 5 rounds OR ≤ 30 fetches; early_stop ≥ 8 sources + ≥ 2 法源類型.
§6.3 disclaimer + §6.4 escalation override boilerplate referenced
from protocols/cite.md (filled in Task 2). Cross-skill handoff
INBOUND only from legal-issue-spot (already in v0.5.0).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: 4 protocol files (parallelizable — 4 implementer subagents)

**Files:**
- Create: `legal-toolkit/skills/legal-research/protocols/plan.md`
- Create: `legal-toolkit/skills/legal-research/protocols/iterative-search.md`
- Create: `legal-toolkit/skills/legal-research/protocols/triangulate.md`
- Create: `legal-toolkit/skills/legal-research/protocols/cite.md`

Each ~80-150 lines markdown. Self-contained. Halt+ask fallback per protocol. Section names byte-aligned with schemas (Task 4).

- [ ] **Step 1: Dispatch 4 parallel implementer subagents — one per protocol**

**Per-protocol responsibility:**

`plan.md` — Read user query. Generate `plan.md` (search keywords ≥ 3, target sites ≥ 2, expected 法源 types subset of {條文, 判決, 函釋, 學說}, budget config {max_rounds: 5, max_fetches: 30, early_stop_min_sources: 8, early_stop_min_types: 2}). Initialize `state.json` (rounds=0, fetches=0, sources=[], types_covered={}, early_stop=false, forced_stop=false, started_at=ISO 8601, updated_at=same). Print plan.md to stdout + prompt "Plan OK 嗎? Y/n" (classify-path Y/n precedent from SP3b). Halt-and-ask on user query < 10 chars or non-legal content.

`iterative-search.md` — SINGLE-round logic. LLM reads state.json. If `rounds >= 5` OR `fetches >= 30`: set `forced_stop = true`, exit to triangulate. If `len(sources) >= 8` AND `len(types_covered) >= 2`: set `early_stop = true`, exit to triangulate. Otherwise: pick next keyword/site from plan, call WebFetch tool, parse result, append source candidates (each: url_or_cite, type, captured_at, relevance_snippet), update types_covered, increment rounds + fetches, write state.json. Loop body designed for LLM to repeat by re-reading SKILL.md workflow + this protocol.

`triangulate.md` — Read all sources from state.json. Cluster by 法源 type (條文 / 判決 / 函釋 / 學說). Verify intersection coverage matches early_stop or forced_stop criteria. If forced_stop: prepend ⚠️ "覆蓋未達 triangulation" warning block to memo (provide template). If early_stop: validate ∩ ≥ 2 types. Halt-and-ask if state.json corrupt or sources empty.

`cite.md` — Final synthesis. Generate `research-memo.md` (full legal analysis with inline citations + `## Citations` manifest section; each citation = full reference + 1-line relevance to conclusion per Harvey doc-level). Generate `executive-summary.md` (TL;DR + ✅/⚠️/❌ + 1-line 依據 + escalation note if forced_stop). Embed §6.3 Disclaimer footer in both files (canonical text). Conditional `§Escalation` in summary when forced_stop OR query involves 刑事 / 訴訟 / 跨境.

- [ ] **Step 2: Spec-reviewer subagent reviews all 4**

- Verify protocols match SKILL.md workflow stage-by-stage
- Verify halt+ask consistent (zh-TW prompts, ⚠️ marker, structured 原因+建議)
- Verify state.json contract (fields + types) matches state-schema.json (Task 4)
- Verify Path A discipline (no 72hr / no controller-processor anywhere)
- Verify §Disclaimer + §Escalation heading uses § sigil (NOT just `## Disclaimer`)
- Verify cross-skill handoff format aligned with issue-spot v0.5.0 (`/legal-research --query="..."` regex still works)

- [ ] **Step 3: Code-quality reviewer subagent**

- Markdown well-formed (header nesting, code fence balance)
- Cross-protocol section name consistency byte-exact
- Halt+ask phrasing recognizable across 4

- [ ] **Step 4: Apply fixes + commit**

```bash
git add legal-toolkit/skills/legal-research/protocols/
git commit -m "feat(legal-toolkit): legal-research 4 protocol files

Phase 3 SP3-b v0.5.2. 4 protocols implementing Agent loop pipeline:

- plan.md: emit plan.md + state.json; stdout preview + Y/n confirm
- iterative-search.md: single-round LLM-driven loop (state.json checkpoint)
- triangulate.md: 法源類型 ∩ coverage; early/forced stop dispatch
- cite.md: research-memo.md + executive-summary.md synthesis with Harvey
            doc-level citation manifest; §6.3 disclaimer + §6.4 escalation

All protocols self-contained; state.json is single deterministic
checkpoint between LLM iterations. halt+ask on ambiguous input.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: 3 reference files (parallelizable — 3 implementer subagents)

**Files:**
- Create: `legal-toolkit/skills/legal-research/references/webfetch-targets.md`
- Create: `legal-toolkit/skills/legal-research/references/citation-format.md`
- Create: `legal-toolkit/skills/legal-research/references/triangulation-rules.md`

Each ~100-200 lines. `[draft — for 法務 review]` HTML comment at top. Path A discipline.

- [ ] **Step 1: Dispatch 3 parallel implementer subagents**

**Per-reference responsibility:**

`webfetch-targets.md` — Target sites + URL patterns:
- `law.moj.gov.tw/LawClass/LawAll.aspx?pcode=<法典>` — 全國法規資料庫 (條文)
- `judicial.gov.tw/FJUD/default.aspx` — 司法院判決系統 (判決)
- `mojlaw.moj.gov.tw/LawSearch.aspx?Type=L` — 法務部主管法規 (函釋)
- `pdpc.moj.gov.tw` — 個資保護 (PDPC 籌備處 函釋; RSS where available)
- Anti-bot fallback: Google cache (`cache:URL`) + archive.org Wayback (`https://web.archive.org/web/*/URL`)
- Crawl etiquette: User-Agent declaration; rate-limit 1-2 fetches/sec; respect robots.txt; document allowed paths
- Mark `[draft — for 法務 review]` since 法務 SME should validate target prioritization + crawl-etiquette policy

`citation-format.md` — Harvey doc-level citation examples (full reference + 1-line relevance):
```
條文: 民法 §184 (中華民國民法; 全國法規資料庫 pcode B0000001; 引用日期 2026-05-15)
       → 本案 fact pattern 涉及 侵權行為 損害賠償，§184 第一項前段為核心請求權基礎。

判決: 最高法院 109 年度台上字第 1234 號民事判決 (司法院判決系統; 引用日期 2026-05-15)
       → 該判決確立「不法侵害他人權利」之 學說 通說採人格權說；本案 §184 涵攝可援引。

函釋: 個資法主管機關 PDPC (法務部) 法律字第 11012345 號函 (2026-04-15)
       → 「適當安全措施」之 解釋；本案 §27 涵攝信心提升至 該當。

學說: 王澤鑑《侵權行為法》第 3 版 (2024) §3.2 第 78 頁
       → 「相當因果關係」之 判定標準；本案 因果關係 涵攝 採通說。
```

`triangulation-rules.md` — 法源類型 classification + ∩ rules:
- 法源類型 = {條文 / 判決 / 函釋 / 學說}
- early_stop: ≥ 8 sources + ≥ 2 types covered (per Q7 design)
- forced_stop: cap reached + early_stop NOT met
- Type promotion rule: if a 判決 cites a 函釋 as binding, both count separately
- Type demotion rule: outdated 判決 (>10 years + 學說 反對) → demoted to type=未通說 (doesn't count toward ∩)
- Mark `[draft — for 法務 review]`

- [ ] **Step 2: Spec-reviewer subagent reviews all 3**

- Verify [draft] markers present
- Verify Path A discipline
- Verify Harvey doc-level citation format correctly demonstrates "full reference + 1-line relevance" pattern
- Verify triangulation rules align with state-schema.json types field

- [ ] **Step 3: Code-quality reviewer subagent**

- Markdown well-formed
- Naming consistency (法源 / 條文 / 判決 / 函釋 / 學說 — not English calques)

- [ ] **Step 4: Apply fixes + commit**

```bash
git add legal-toolkit/skills/legal-research/references/
git commit -m "feat(legal-toolkit): legal-research 3 reference files [draft]

Phase 3 SP3-b v0.5.2. 3 reference files consumed by protocols/:

- webfetch-targets.md: 4 primary sites (law.moj/judicial.gov.tw/
  PDPC/法務部 主管法規) + Google cache + archive.org fallback +
  crawl etiquette (UA declaration, 1-2 fetch/sec, robots.txt)
- citation-format.md: Harvey doc-level citation format examples for
  條文 / 判決 / 函釋 / 學說 (each with full reference + 1-line relevance)
- triangulation-rules.md: 法源類型 classification + ∩ rules (≥ 2 types
  early_stop; type promotion/demotion logic)

All marked [draft — for 法務 review; Phase 4.5 GC outreach validation].
Path A discipline maintained throughout.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: 5 schemas (plan / state / memo / summary / triangulation-config)

**Files:**
- Create: `legal-toolkit/skills/legal-research/assets/plan-schema.json`
- Create: `legal-toolkit/skills/legal-research/assets/state-schema.json`
- Create: `legal-toolkit/skills/legal-research/assets/output-schema-memo.json`
- Create: `legal-toolkit/skills/legal-research/assets/output-schema-summary.json`
- Create: `legal-toolkit/skills/legal-research/assets/triangulation-config.json`

Single subagent (one-shot JSON). All draft-07.

- [ ] **Step 1: Write all 5 schemas**

`plan-schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "legal-toolkit/skills/legal-research/assets/plan-schema.json",
  "title": "plan.md structural schema",
  "type": "object",
  "required": ["required_sections", "min_keywords", "min_target_sites", "expected_source_types", "budget_fields"],
  "properties": {
    "required_sections": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["§問題", "§關鍵字", "§目標 site", "§法源類型 plan", "§Budget"]
    },
    "min_keywords": {"type": "integer", "const": 3},
    "min_target_sites": {"type": "integer", "const": 2},
    "expected_source_types": {
      "type": "array",
      "items": {"type": "string", "enum": ["條文", "判決", "函釋", "學說"]}
    },
    "budget_fields": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["max_rounds", "max_fetches", "early_stop_min_sources", "early_stop_min_types"]
    }
  }
}
```

`state-schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "legal-toolkit/skills/legal-research/assets/state-schema.json",
  "title": "state.json structural schema",
  "type": "object",
  "required": ["rounds", "fetches", "sources", "types_covered", "early_stop", "forced_stop", "started_at", "updated_at"],
  "properties": {
    "rounds": {"type": "integer", "minimum": 0, "maximum": 5},
    "fetches": {"type": "integer", "minimum": 0, "maximum": 30},
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["url_or_cite", "type", "captured_at", "relevance_snippet"],
        "properties": {
          "url_or_cite": {"type": "string"},
          "type": {"type": "string", "enum": ["條文", "判決", "函釋", "學說"]},
          "captured_at": {"type": "string", "format": "date-time"},
          "relevance_snippet": {"type": "string"}
        }
      }
    },
    "types_covered": {
      "type": "object",
      "additionalProperties": {"type": "integer", "minimum": 0}
    },
    "early_stop": {"type": "boolean"},
    "forced_stop": {"type": "boolean"},
    "started_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"}
  }
}
```

`output-schema-memo.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "legal-toolkit/skills/legal-research/assets/output-schema-memo.json",
  "title": "research-memo.md structural schema",
  "type": "object",
  "required": ["required_sections", "conditional_sections", "citation_section", "min_citations_or_warn", "min_source_types_or_warn", "min_byte_size", "no_template_orphans"],
  "properties": {
    "required_sections": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["§問題", "§搜尋摘要", "§法源分析", "§結論", "§Citations", "§Disclaimer"]
    },
    "conditional_sections": {
      "type": "object",
      "properties": {
        "⚠️ 覆蓋未達 triangulation 警告 block": {
          "type": "string",
          "const": "REQUIRED if state.json.forced_stop == true; PREPENDED above §問題"
        }
      }
    },
    "citation_section": {"type": "string", "const": "§Citations"},
    "min_citations_or_warn": {"type": "integer", "const": 8},
    "min_source_types_or_warn": {"type": "integer", "const": 2},
    "min_byte_size": {"type": "integer", "const": 1200},
    "no_template_orphans": {"type": "boolean", "const": true}
  }
}
```

`output-schema-summary.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "legal-toolkit/skills/legal-research/assets/output-schema-summary.json",
  "title": "executive-summary.md structural schema",
  "type": "object",
  "required": ["required_sections", "conditional_sections", "conclusion_marker_required", "min_byte_size", "no_template_orphans"],
  "properties": {
    "required_sections": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["§問題", "§結論", "§依據", "§風險提示", "§Disclaimer"]
    },
    "conditional_sections": {
      "type": "object",
      "properties": {
        "§Escalation": {
          "type": "string",
          "const": "REQUIRED if state.json.forced_stop == true OR query involves 刑事 / 訴訟 / 跨境 / 重大金額"
        }
      }
    },
    "conclusion_marker_required": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["✅", "⚠️", "❌"]
    },
    "min_byte_size": {"type": "integer", "const": 400},
    "no_template_orphans": {"type": "boolean", "const": true}
  }
}
```

`triangulation-config.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "legal-toolkit/skills/legal-research/assets/triangulation-config.json",
  "title": "triangulation parameters",
  "type": "object",
  "description": "Centralized loop cap params. v0.5.3 patch room reserved for tuning.",
  "required": ["max_rounds", "max_fetches", "early_stop_min_sources", "early_stop_min_types", "valid_source_types"],
  "properties": {
    "max_rounds": {"type": "integer", "const": 5},
    "max_fetches": {"type": "integer", "const": 30},
    "early_stop_min_sources": {"type": "integer", "const": 8},
    "early_stop_min_types": {"type": "integer", "const": 2},
    "valid_source_types": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["條文", "判決", "函釋", "學說"]
    }
  }
}
```

- [ ] **Step 2: Verify all 5 schemas parse as valid JSON**

```bash
for f in legal-toolkit/skills/legal-research/assets/*.json; do
  python3 -c "import json; json.load(open('$f')); print('OK: $f')"
done
```

Expected: 5 OK lines.

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/skills/legal-research/assets/
git commit -m "feat(legal-toolkit): legal-research 5 schemas

Phase 3 SP3-b v0.5.2. JSON Schema draft-07 contracts:

- plan-schema.json: plan.md required sections + min keywords/sites/budget
- state-schema.json: state.json checkpoint contract (rounds/fetches/
  sources/types_covered/early_stop/forced_stop/started_at/updated_at)
- output-schema-memo.json: research-memo.md 6 required sections +
  conditional ⚠️ warning block + ≥ 8 citations or warn + ≥ 2 types or warn
- output-schema-summary.json: executive-summary.md 5 required sections
  + conditional §Escalation + ✅/⚠️/❌ marker
- triangulation-config.json: centralized loop cap (5 rounds / 30 fetches
  / 8 sources / 2 types early_stop floor); v0.5.3 patch room

Schemas consumed by grade_research.py in Task 5.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: grade_research.py + tests + flat fixtures (TDD)

**Files:**
- Create: `legal-toolkit/skills/legal-research/scripts/grade_research.py` (~400 lines; matches grade_issue_spot.py density + more checks)
- Create: `legal-toolkit/skills/legal-research/tests/test_grade_research.py` (~130-160 lines; 12-15 tests)
- Create: ~13 fixture files FLAT in `tests/` (naming `fixture-<name>.md` or `fixture-state-<name>.json`)

**Fixture files**:
- `fixture-plan-pass.md` — passing plan.md
- `fixture-memo-pass.md` — passing memo (≥ 8 citations + ≥ 2 types + 6 sections + canonical Disclaimer)
- `fixture-summary-pass.md` — passing summary (5 sections + ✅ marker + Disclaimer)
- `fixture-state-pass.json` — early_stop=true, rounds=3, fetches=15, 9 sources, 3 types
- `fixture-state-over-cap.json` — rounds=6 (over max_rounds=5; should fail state_within_cap)
- `fixture-state-inconsistent.json` — forced_stop=true but memo (fixture-memo-pass.md, no ⚠️) → fail state_consistency
- `fixture-memo-7-citations-no-warn.md` — 7 citations + 2 types + NO ⚠️ → fail min_citations_or_warn
- `fixture-memo-7-citations-with-warn.md` — 7 citations + 2 types + WITH ⚠️ → exit 2 (PASS_WITH_NOTES) — acceptable
- `fixture-memo-single-type-coverage.md` — 8 citations + 1 type only + NO ⚠️ → fail min_source_types
- `fixture-memo-citation-no-relevance.md` — citation manifest missing 1-line relevance per source → fail citation_has_relevance
- `fixture-memo-72hr-antipattern.md` — pass + insert "72 hours" → fail path_a
- `fixture-memo-orphan-tbd.md` — pass + insert `{{TBD_X}}` → fail template_orphan
- `fixture-summary-no-disclaimer.md` — summary pass MINUS §Disclaimer → fail disclaimer_footer
- `fixture-summary-no-conclusion-marker.md` — summary pass MINUS ✅/⚠️/❌ → fail conclusion_marker

**Grader checks (per spec §6.5)**:

```python
CHECKS = [
    ("structural_plan_md",         schema_check),
    ("structural_state_json",      jsonschema_check),
    ("state_within_cap",           lambda: rounds <= 5 AND fetches <= 30),
    ("state_consistency",          lambda: forced_stop ↔ memo has ⚠️ block),
    ("structural_memo_md",         schema_check),
    ("structural_summary_md",      schema_check),
    ("citation_section_present",   lambda: "## §Citations" in memo or "## Citations"),
    ("citation_count_or_warn",     lambda: count(citations) >= 8 OR memo has ⚠️),
    ("citation_has_relevance",     lambda: each citation has 1-line relevance),
    ("source_type_coverage",       lambda: types_count >= 2 OR memo has ⚠️),
    ("summary_conclusion_marker",  lambda: summary has one of [✅/⚠️/❌]),
    ("path_a_antipatterns",        bank_check),  # byte-identical to other 3 graders
    ("template_orphan_check",      orphan_helper),  # byte-identical
    ("disclaimer_footer",          lambda: §Disclaimer + canonical sentinel in memo AND summary),
    ("escalation_when_forced_stop", lambda: forced_stop → summary has §Escalation),
]
```

**TDD discipline** (mirrors v0.5.0 Task 5):
1. Write test → run → expect FAIL
2. Hand-craft fixture (positive/negative)
3. Implement grader check
4. Run → expect PASS
5. Move to next

**CLI interface**:

```bash
python3 grade_research.py --plan <path> --state <path> --memo <path> --summary <path>
# Exit 0 = PASS / 1 = FAIL / 2 = PASS_WITH_NOTES (forced_stop + ⚠️ acceptable)
```

**Key requirements**:
- `PATH_A_ANTIPATTERNS` bank byte-identical to grade_draft.py + grade_response.py + grade_issue_spot.py (drift-verified in Task 7)
- `_check_no_template_orphans` helper byte-identical to grade_response.py + grade_issue_spot.py (NOT grade_draft.py which uses different helper name)
- PYTHONDONTWRITEBYTECODE=1 in test ENV
- No `from __future__ import annotations`

- [ ] **Step 1: Read existing graders for byte-identical bank + helper**

```bash
grep -A 30 "PATH_A_ANTIPATTERNS = \[" legal-toolkit/skills/legal-issue-spot/scripts/grade_issue_spot.py
grep -B 1 -A 5 "_check_no_template_orphans" legal-toolkit/skills/legal-issue-spot/scripts/grade_issue_spot.py
```

Capture bank + helper verbatim.

- [ ] **Step 2: Hand-craft passing fixtures**

`fixture-plan-pass.md` — realistic plan covering 民法 §227 fact-pattern question
`fixture-memo-pass.md` — full research output with 9 citations spanning 條文/判決/函釋 (3 types), 1500+ bytes
`fixture-summary-pass.md` — executive summary with ✅ marker, ~600 bytes
`fixture-state-pass.json` — corresponding state: rounds=3, fetches=15, sources_count=9, types_covered={條文:3, 判決:4, 函釋:2}, early_stop=true, forced_stop=false

- [ ] **Step 3: Write test_passing_fixture_exits_0**

```python
"""Deterministic tests for grade_research.py."""
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GRADER = SKILL_DIR / "scripts" / "grade_research.py"
FIXTURES = Path(__file__).resolve().parent  # FLAT

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _run_grader(plan, state, memo, summary) -> int:
    result = subprocess.run(
        [sys.executable, str(GRADER), "--plan", str(plan), "--state", str(state), "--memo", str(memo), "--summary", str(summary)],
        env=ENV, capture_output=True, text=True,
    )
    return result.returncode


def test_passing_fixture_exits_0():
    rc = _run_grader(
        FIXTURES / "fixture-plan-pass.md",
        FIXTURES / "fixture-state-pass.json",
        FIXTURES / "fixture-memo-pass.md",
        FIXTURES / "fixture-summary-pass.md",
    )
    assert rc == 0
```

Run: `pytest test_grade_research.py::test_passing_fixture_exits_0 -v` → expect FAIL (grader doesn't exist).

- [ ] **Step 4: Implement minimal grade_research.py**

Skeleton with bank + helper copied byte-identical from grade_issue_spot.py. argparse for 4 file paths. Initial implementation should pass test_passing_fixture_exits_0.

Run → expect PASS.

- [ ] **Step 5: Add 12-15 negative tests + corresponding fixtures + grader checks**

Per fixture in §Files list above. Cycle: test → fixture → grader check → re-run.

Test list (matches fixture list):
1. test_passing_fixture_exits_0
2. test_missing_plan_md_exits_1
3. test_missing_state_json_exits_1
4. test_missing_memo_md_exits_1
5. test_missing_summary_md_exits_1
6. test_state_over_cap_exits_1
7. test_state_inconsistent_forced_stop_no_warn_exits_1
8. test_memo_7_citations_no_warn_exits_1
9. test_memo_7_citations_with_warn_exits_2 (PASS_WITH_NOTES)
10. test_memo_single_type_coverage_exits_1
11. test_memo_citation_no_relevance_exits_1
12. test_memo_72hr_antipattern_exits_1
13. test_memo_orphan_tbd_exits_1
14. test_summary_no_disclaimer_exits_1
15. test_summary_no_conclusion_marker_exits_1

- [ ] **Step 6: Run full plugin baseline**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q
# Expected: 244 + 15 = 259 passed (or 244 + N where N = actual test count)
```

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/skills/legal-research/scripts/ \
        legal-toolkit/skills/legal-research/tests/
git commit -m "feat(legal-toolkit): grade_research.py + tests + flat fixtures

Phase 3 SP3-b v0.5.2. Self-contained structural grader; PATH_A bank +
_check_no_template_orphans helper byte-identical to grade_issue_spot
(drift verified in Task 7).

Checks (15):
  Common:        file existence, state schema, cap, state consistency
  Memo struct:   6 required sections + ⚠️ conditional block
  Citation:      ≥ 8 sources OR ⚠️; per-citation 1-line relevance; ≥ 2 types OR ⚠️
  Summary:       5 required sections + ✅/⚠️/❌ marker + §Escalation when forced_stop
  Safety:        Path A bank, template orphans, §Disclaimer canonical

Exit codes:
  0 = PASS (early_stop met or no fault)
  1 = FAIL (missing file / schema violation / Path A / orphan / etc.)
  2 = PASS_WITH_NOTES (forced_stop + ⚠️ marker is acceptable per spec §6.6)

Fixtures FLAT in tests/. PYTHONDONTWRITEBYTECODE=1 enforced.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Router Q4-law-lookup dispatch unlock

**Files:**
- Modify: `legal-toolkit/skills/using-legal-toolkit/SKILL.md` (~30-line change)

- [ ] **Step 1: Update dispatch table**

```
| Q4 (law lookup) — research | `legal-research` | 🔍 IRAC | Phase 3 (not yet) |
```
→
```
| Q4 (law lookup) — research | `legal-research` | 🔍 IRAC | **active (v0.5.2+)** |
```

- [ ] **Step 2: Add `### Q4 (law lookup) — Research (active in v0.5.2+)` subsection**

After Q4-fact subsection (added in v0.5.0):

```markdown
### Q4 (law lookup) — Research (active in v0.5.2+)

**Keyword triggers**: 「查 §」/「§227 是」/「判例」/「法條」/「找判決」/「research」/「lookup」/「條文」/「函釋」/「what does §X say」.

**Disambiguation**: if the user's request is a fact-pattern question (能不能做 / 是否合法 / ...), route to Q4-fact (legal-issue-spot, active v0.5.0+).

→ hand off to `legal-research` skill with the query string.

**Prerequisite check**: NONE. legal-research is profile.yml-independent.

**Plan-first 半互動**: research emits `plan.md` then asks "Plan OK 嗎? Y/n" (classify-path precedent). User confirms → autonomous WebFetch loop (cap ≤ 5 rounds OR ≤ 30 fetches; early-stop ≥ 8 sources + ≥ 2 法源類型).

**Output expectation**: 4 files in `legal-outputs/<timestamp>-research-<topic>/` (`plan.md` + `state.json` + `research-memo.md` for 法務 + `executive-summary.md` for 業務). Forced_stop emits ⚠️ "覆蓋未達 triangulation" warning block.
```

- [ ] **Step 3: Update mermaid Q4 law-lookup branch**

```
Q4 -->|查法源| RS[→ legal-research<br/>🔍 IRAC — Phase 3 NOT YET]
```
→
```
Q4 -->|查法源| RS[→ legal-research<br/>🔍 IRAC — active v0.5.2+]
```

- [ ] **Step 4: Update Step 4 "not yet" path**

Remove legal-research from not-yet list (now active).

- [ ] **Step 5: Update IRAC menu line in 6-cluster menu**

Around line 197 (Q5 fallback menu); change `[Phase 3 SP3-b — v0.5.2 還沒上]` to `(✅ active v0.5.2+)`. Whole IRAC line now: `→ fact pattern 法律分析 (✅ active v0.5.0+) / 查特定法條 / 判例 (✅ active v0.5.2+)`.

- [ ] **Step 6: Update Active sub-skills list**

```markdown
  - [`legal-issue-spot`](../legal-issue-spot/SKILL.md)
  - [`legal-research`](../legal-research/SKILL.md)
```

- [ ] **Step 7: Update Cold-start onboarding (6 → 7 active skills)**

Add `legal-research` bullet + 起手路徑 entry.

- [ ] **Step 8: Update frontmatter description (paired sync)**

`6 active sub-skills (...)` → `7 active sub-skills (... + legal-research)`
`5 more sub-skills (legal-research / ...)` → `4 more sub-skills (legal-contract-tracker / ...)`

- [ ] **Step 9: Bump version 0.2.0 → 0.3.0**

- [ ] **Step 10: Run baseline + commit**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/ legal-toolkit/scripts/tests/ -q
# Expected: no regressions

git add legal-toolkit/skills/using-legal-toolkit/SKILL.md
git commit -m "feat(legal-toolkit): router Q4-law-lookup dispatch unlock

Phase 3 SP3-b v0.5.2. Activates Q4 (law-lookup) dispatch path:

- Dispatch table row: Phase 3 (not yet) → active (v0.5.2+)
- Q4-law-lookup subsection added (mirrors Q4-fact pattern)
- Mermaid Q4 law-lookup branch updated
- Step 4 not-yet path: legal-research removed from list
- 6-cluster fallback menu IRAC line updated (both sub-skills active)
- Cold-start onboarding: 6 → 7 active skill count
- Frontmatter description paired sync (legal-research moved to active list)
- Router version bump 0.2.0 → 0.3.0

Phase 3 IRAC cluster fully active. Phase 4 Tracker (v0.6.0) is next.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Drift verify uncomment forward-stub

**Files:**
- Modify: `legal-toolkit/scripts/verify-drift.py` — uncomment the forward-stub line for `grade_research.py`

- [ ] **Step 1: Locate forward-stub comment**

```bash
grep -n "grade_research" legal-toolkit/scripts/verify-drift.py
```

Expected: 1-2 lines with `# graders.append(... grade_research.py)` comment.

- [ ] **Step 2: Uncomment forward-stub**

Edit `verify-drift.py`:

FROM:
```python
# NOTE: legal-research grader added in v0.5.2; uncomment then.
# graders.append(skill_dir / "legal-research" / "scripts" / "grade_research.py")
```

TO:
```python
# legal-research grader added in v0.5.2
graders.append(skill_dir / "legal-research" / "scripts" / "grade_research.py")
```

- [ ] **Step 3: Run drift verify**

```bash
python3 legal-toolkit/scripts/verify-drift.py
```

Expected:
- `OK: all 11 functional copies byte-identical to canonical.`
- `OK: 4-grader PATH_A bank + template-orphan helper byte-identical.`
- Exit 0

If drift detected, the new grade_research.py bank/helper diverged from grade_issue_spot.py — fix by copying canonical bank/helper verbatim from grade_issue_spot.py.

- [ ] **Step 4: Run full baseline (drift test included)**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q
# Expected: all green (244 baseline + 15 grade_research + drift tests)
```

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/scripts/verify-drift.py
git commit -m "chore(legal-toolkit): drift verify activates 4-grader bank check

Phase 3 SP3-b v0.5.2. Uncomments the v0.5.0 forward-stub:

- grade_research.py added to verify_grader_bank_drift() graders list
- Now enforces PATH_A_ANTIPATTERNS + _check_no_template_orphans
  byte-identical across grade_draft + grade_response + grade_issue_spot
  + grade_research (4-grader bank)

Closes the v0.5.0 forward-stub left in commit 3bf2c47.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: 3 READMEs (parallelizable — en/ja/zh-TW)

**Files:**
- Create: `legal-toolkit/skills/legal-research/README.md` (~50-80 lines)
- Create: `legal-toolkit/skills/legal-research/README.ja.md` (~50-80 lines)
- Create: `legal-toolkit/skills/legal-research/README.zh-TW.md` (~50-80 lines)

Same structural shape as legal-issue-spot READMEs (Task 8 in v0.5.0). Per-language conventions:
- EN: tech English nouns; legal Chinese terms with gloss on first use
- JA: NO katakana for tech English nouns (skill / plugin / schema / grader / session / WebFetch / state.json) — per `docs/i18n/glossary-ja.md`
- zh-TW: 繁體; no Mainland calques (議題 / 風險 / 觀點 / not 议题 / 风险 / 次元)

Sections (mirrors v0.5.0 legal-issue-spot READMEs):
1. Skill name + version + brief
2. When to use (3 bullets — emphasize literal law-text / 判例 / 函釋 lookup)
3. When NOT to use (4 bullets — route alternatives)
4. Input format (query string)
5. Output format (4 files: plan / state / memo / summary)
6. Plan-first 半互動 explanation (Y/n confirm; plan.md preview)
7. Agent loop cap explanation (≤ 5 rounds OR ≤ 30 fetches; early-stop ≥ 8/2; forced_stop ⚠️)
8. §6.3 Disclaimer footer note
9. Links to SKILL.md + design spec

- [ ] **Step 1: Dispatch 3 parallel implementer subagents**

- [ ] **Step 2: Spec-reviewer subagent (single review pass)**

- [ ] **Step 3: Apply fixes + controller commits all 3 (avoids git index race)**

```bash
git add legal-toolkit/skills/legal-research/README.md \
        legal-toolkit/skills/legal-research/README.ja.md \
        legal-toolkit/skills/legal-research/README.zh-TW.md
git commit -m "docs(legal-toolkit): legal-research tri-language READMEs

Phase 3 SP3-b v0.5.2. en/ja/zh-TW READMEs per PR #150 i18n convention.

Per-language style notes:
- ja: preserves English tech nouns; observes glossary-ja.md
- zh-TW: no Mainland calques; 議題/風險/觀點

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Plugin docs sync + version bump (0.5.0 → 0.5.2)

**Files:**
- Modify: `legal-toolkit/.claude-plugin/plugin.json` (version 0.5.0 → 0.5.2; description += research)
- Modify: `.claude-plugin/marketplace.json` (description byte-identical sync)
- Modify: `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` (skill list 6 → 7; Q4 status both active)
- Modify: `legal-toolkit/ROADMAP.md` (Phase 3 SP3-b ✅ DONE; Phase 3 fully closed)

(Note: v0.5.1 is reserved for SP3-a dogfood patches; skipping straight to v0.5.2 per ROADMAP cadence.)

- [ ] **Step 1: Read current plugin.json + marketplace.json**

```bash
cat legal-toolkit/.claude-plugin/plugin.json | python3 -m json.tool | head -10
grep -A 5 '"name": "legal-toolkit"' .claude-plugin/marketplace.json | head -5
```

- [ ] **Step 2: Bump plugin.json**

- `version`: `"0.5.0"` → `"0.5.2"`
- `description`: append v0.5.2 SP3-b entry (preserve existing prose style; mention 4-protocol Agent loop + 5 schemas + 15-check grader + plan-first 半互動 + WebFetch budget + 4-grader bank drift activated)

- [ ] **Step 3: Sync marketplace.json byte-identical**

```bash
python3 scripts/check-marketplace-description-sync.py
# Expected: OK
```

- [ ] **Step 4: Update plugin-level READMEs (6 → 7 skills)**

For en/ja/zh-TW: skill count + add legal-research bullet + Q4 status BOTH active.

- [ ] **Step 5: Update ROADMAP.md**

- Phase 3 SP3-b marked ✅ DONE (merge date 2026-05-15 or actual)
- Phase 3 fully closed; both sub-skills active
- Timeline overview row Phase 3 fully done
- Update test count target (244 → ~259+ depending on actual)

- [ ] **Step 6: Run full CI baseline**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q
python3 scripts/check-marketplace-description-sync.py
python3 legal-toolkit/scripts/verify-drift.py
```

All expected exit 0.

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/.claude-plugin/plugin.json .claude-plugin/marketplace.json \
        legal-toolkit/README.md legal-toolkit/README.ja.md legal-toolkit/README.zh-TW.md \
        legal-toolkit/ROADMAP.md
git commit -m "chore(legal-toolkit): bump plugin to v0.5.2 + plugin docs sync

Phase 3 SP3-b v0.5.2 ship. Bumps:

- plugin.json version 0.5.0 → 0.5.2; description += research (Agent
  abstraction + plan-first + 4-protocol pipeline + 15-check grader +
  4-grader bank drift activated)
- marketplace.json description byte-identical sync
- README en/ja/zh-TW: 6 → 7 active skills; Q4 both branches active
- ROADMAP: Phase 3 SP3-b ✅ DONE; Phase 3 fully closed

Plugin grows to 7 active skills (full IRAC cluster):
  using-legal-toolkit / legal-playbook-author /
  legal-contract-review / legal-document-draft /
  legal-incident-response / legal-issue-spot / legal-research (NEW)

Skipped v0.5.1 (reserved for SP3-a dogfood patches). Phase 4 Tracker
cluster (v0.6.0) is next.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: Fresh-eyes audit + push + PR

(Mirrors v0.5.0 Task 10 structure)

- [ ] **Step 1: Dispatch fresh-eyes audit subagent**

Categories:
- Cross-task drift (mermaid ↔ protocols ↔ schemas ↔ grader; reference ↔ protocols consumption)
- Contract-vs-implementation gaps (§Disclaimer / §Escalation / cross-skill handoff format)
- §Citations heading byte-exact (`## §Citations` vs `## Citations`)
- Per-task reviewer blind spots
- CI gates (244 + new tests; drift 4-grader bank; marketplace sync; flat folder)

- [ ] **Step 2: Apply Critical/Important fixes inline**

- [ ] **Step 3: Final baseline sweep**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q
python3 legal-toolkit/scripts/verify-drift.py
python3 scripts/check-marketplace-description-sync.py
```

- [ ] **Step 4: Push + open PR**

```bash
git push -u origin feat/legal-toolkit-v0.5.2-research

gh pr create --title "feat(legal-toolkit): v0.5.2 — Phase 3 SP3-b legal-research" --body "$(cat <<'EOF'
## Summary

Ships **Phase 3 SP3-b** — the second half of the 🔍 IRAC cluster — bumping legal-toolkit to **v0.5.2** (skipping v0.5.1 reserved for SP3-a dogfood). Phase 3 IRAC fully closed.

- New skill `legal-research` (Agent abstraction; plan-first 半互動; WebFetch-driven; profile.yml-independent)
- Router Q4-law-lookup dispatch unlocked (Q4 cluster fully active)
- 4-grader bank drift verification activated (forward-stub from v0.5.0 closed)
- Plugin grows: 6 → 7 active skills

Design SoT: [`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §6 + §7. Plan: [`docs/superpowers/plans/2026-05-15-legal-toolkit-v0.5.2-research.md`](docs/superpowers/plans/2026-05-15-legal-toolkit-v0.5.2-research.md).

## What changed

- **Skill content**: SKILL.md + 4 protocols (plan → iterative-search → triangulate → cite) + 3 reference files (`[draft]`)
- **Schemas (5)**: plan / state / output-memo / output-summary / triangulation-config
- **Grader**: `grade_research.py` (15 checks; PATH_A bank + `_check_no_template_orphans` helper byte-identical w/ existing 3 graders; drift CI enforced)
- **Router**: Q4-law-lookup dispatch active; subsection + mermaid + cold-start + frontmatter description all synced
- **Drift CI**: 4-grader bank coverage (forward-stub from v0.5.0 PR #291 uncommented)
- **Plugin docs**: plugin.json + marketplace.json sync + tri-language READMEs + ROADMAP Phase 3 fully closed

## Agent loop spec

```
1. User invokes /legal-research --query="..."
2. protocols/plan.md: emit plan.md + state.json; stdout preview + "Plan OK 嗎? Y/n"
3. User Y: autonomous loop
   Loop body (LLM-driven, state.json checkpoint):
     If rounds ≥ 5 OR fetches ≥ 30: forced_stop → break
     If sources ≥ 8 AND types ≥ 2: early_stop → break
     Otherwise: pick keyword/site from plan → WebFetch → parse → append → write state.json → loop
4. protocols/triangulate.md: 法源類型 ∩ coverage check; prepend ⚠️ "覆蓋未達" block if forced_stop
5. protocols/cite.md: synthesize research-memo.md + executive-summary.md with Harvey doc-level citations
```

## Test plan

- [ ] CI: `pytest legal-toolkit/` green (244 + 15+ new tests)
- [ ] CI: `verify-drift.py` exit 0 — 4-grader bank check now active
- [ ] CI: `check-marketplace-description-sync.py` exit 0
- [ ] CI: flat-folder check + commit type whitelist + kebab scope green
- [ ] Manual: post-merge dogfood with 5 hand-curated 法律問題 (controller-driven; v0.5.3 patch PR if P0/P1 surfaces)

## Inherited conventions (Phase 3 complete)

Path A discipline; §6.3 Mandatory Disclaimer; §6.4 Escalation Override; 2-file audience-shaped output; SSOT-and-functional-copy grader bank; flat folder; SDD orchestration; PYTHONDONTWRITEBYTECODE=1.

## Open items

- 法務 SME validation of 3 reference files (webfetch-targets / citation-format / triangulation-rules) deferred to Phase 4.5 GC outreach
- Quality-gate dataset (5 hand-curated 法律問題) hand-curated post-merge for dogfood
- WebFetch reliability monitoring (if `.gov.tw` sites change layout / anti-bot → graceful forced_stop + ⚠️ marker)
- `--plan-from <file>` resume flag reserved for v0.5.x patch

## Cross-references

- Memory: `project_legal_toolkit_design.md` / `feedback_legal_toolkit_defer_legal_domain.md` / `feedback_legal_toolkit_autonomous_after_design_lock.md`
- Predecessor: PR #291 (v0.5.0 SP3-a legal-issue-spot)
- Phase 3 fully closed; Phase 4 Tracker cluster (v0.6.0) is next per ROADMAP

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 5: Monitor CI**

```bash
gh pr checks --watch
```

If green → report PR URL to user.

---

## Self-Review

**Spec coverage:**
- §6.1 folder layout → Task 1
- §6.2 SKILL.md outline + Agent loop → Task 1 Step 2
- §6.3 plan.md schema → Task 4
- §6.4 state.json schema → Task 4
- §6.5 grader interface → Task 5
- §6.6 WebFetch target sites → Task 3 (webfetch-targets.md)
- §6.7 test surface → Task 5
- §7.1 router Q4-law-lookup unlock → Task 6
- §7.3 grader self-contained + 4-grader drift → Task 5 + Task 7
- §7.4 CI surface → Tasks 5/7/9
- §8.3 commit breakdown (9 commits) → mapped 1:1 onto Tasks 1-9 + Task 10 audit

**Placeholder scan:**
- All bash commands have explicit paths
- All schemas show full JSON inline
- Reference content for `[draft]` files is intentional per design (controller drafts; Phase 4.5 validation)
- No "TBD" / "implement later" / "fill in details" anywhere in task steps

**Type consistency:**
- Section names consistent: `§問題 / §搜尋摘要 / §法源分析 / §結論 / §Citations / §Disclaimer` (memo); `§問題 / §結論 / §依據 / §風險提示 / §Disclaimer / §Escalation` (summary); `§Disclaimer` uses § sigil per v0.5.0 convention
- Function names: `_check_no_template_orphans` byte-identical with grade_response.py + grade_issue_spot.py (not grade_draft.py which uses different helper)
- State JSON field names: rounds / fetches / sources / types_covered / early_stop / forced_stop / started_at / updated_at — consistent across schema + protocols + grader

---

## Execution

Per `feedback_legal_toolkit_autonomous_after_design_lock.md`: SDD execution proceeds autonomously without per-task confirmation. Dispatching subagent-driven-development now.
