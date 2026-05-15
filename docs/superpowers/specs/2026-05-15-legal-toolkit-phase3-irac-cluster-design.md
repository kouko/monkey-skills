# legal-toolkit Phase 3 — IRAC cluster design (v0.5.0 + v0.5.2)

**Status**: Design (implementation-ready)
**Date**: 2026-05-15
**Authors**: kouko + Claude (brainstorming session, Q1–Q8)
**Predecessor**: legal-toolkit v0.4.4 (P2 polish PR #290), v0.4.3 (SP3b dogfood PR #288), v0.4.2 (SP3b PR #286)
**Target versions**: legal-toolkit v0.5.0 (SP3-a issue-spot) + v0.5.2 (SP3-b research)
**Sub-project**: Phase 3 — IRAC cluster, ROADMAP §Phase 3
**Skill scope**: 2 new skills (`legal-issue-spot` v0.5.0 + `legal-research` v0.5.2); 2 router patches (Q4-fact + Q4-law-lookup unlock); 0 canonical/ schema bumps (issue-spot + research are profile-independent); ~25-30 new tests across both skills

---

## 1. Goal

Ship Phase 3 of `legal-toolkit` ROADMAP — the **IRAC cluster** of 2 skills covering pre-incident legal consultation:

- **`legal-issue-spot`** (v0.5.0, SP3-a): take a business-language fact pattern ("我們想做 X，能不能做？") and produce an issue 矩陣 + 構成要件 涵攝 + 風險分級 + escalation 建議. Pure-LLM workflow abstraction; no external fetches.
- **`legal-research`** (v0.5.2, SP3-b): take a 法律問題 / 條文號 / 判例編號 and run plan-first iterative WebFetch + triangulation + Harvey doc-level citation. Agent abstraction; bounded by hard cap + early-stop criteria.

After Phase 3, plugin = 7 active skills (router + author + contract-review + document-draft + incident-response + issue-spot + research). Phase 4 Tracker remains v0.6.0 per ROADMAP (no shift).

## 2. Why

**Trigger** — obsidian Design SoT §3.6 + §3.7 architected the IRAC cluster as the third major skill family (after 📋 Playbook v0.3.5 + 📝 Template v0.4.0 + 🚨 Runbook v0.4.2). v0.4.x line was paused at v0.4.4 awaiting Phase 4.5 上市櫃 Compliance outreach (still in flight, user-driven). Phase 3 IRAC is **not blocked by Phase 4.5** — it serves SME 法務 daily consultation needs that are independent of 上市櫃 governance research.

**Why bundle 2 skills into Phase 3** — both are issue-driven (vs clause-driven Playbook / template-driven Template / event-driven Runbook). Both follow the IRAC mental model (Issue → Rule → Application → Conclusion). Splitting into separate phases would fragment the methodology rollout.

**Why issue-spot first, research second** — v0.4.x SP3a/3b precedent validated 2-PR split for cluster ships. issue-spot is pure-LLM (lower risk: no external dependencies); research depends on WebFetch reliability (higher risk: `.gov.tw` site availability + anti-bot). Stage risk by shipping the safer skill first; if research's WebFetch path proves unstable post-merge, issue-spot already provides standalone value.

**Why disclaimer-driven, NOT hard-exclusion** (inherited from §6.3 + §6.4 design SoT) — both skills produce 法律意見. v0 SoT proposed hard-excluding all legal-opinion output to avoid 律師法 §48 concerns; v0.4.x reversed this (律師法 §48 applies to "人" not "工具"; hard exclusion = denying skill existence). Phase 3 inherits §6.3 Mandatory Disclaimer (every output footer) + §6.4 Escalation Override (skill self-escalates when confidence threshold not met).

**Why now (2026-05-15)** — no technical debt from v0.4.x line; baseline 231 tests + drift verify both green; Phase 4.5 outreach is user-driven on parallel timeline; controller has bandwidth for 2 PRs.

## 3. Locked decisions

| # | Decision | Choice | Reasoning |
|---|---|---|---|
| 1 | Resource layer for research | **WebFetch (no scrapers)** | obsidian SoT was authored before Claude Code WebFetch maturity; scraper maintenance burden inherited 條文 reproducibility cost; legal-sources.json canonical handles 條文; research only needs hot fetch for 判決+函釋+期刊 (each-day-new content) |
| 2 | Ship cadence | **2 PR split (v0.5.0 issue-spot first → v0.5.2 research second; v0.5.1/v0.5.3 reserved for dogfood patch PRs)** | v0.4.x SP3a/3b precedent; risk staging (lower-risk skill first); router 2-stage Q4 unlock |
| 3 | Reference depth (issue-spot) | **中厚 B (element + 一行白話 + 反例 + carve-out; ~200 行/檔 × 3)** | A 薄殼 LLM hallucinates; C 厚百科 over-budget + duplicates research's job; B matches contract-review playbook density |
| 4 | issue-spot output | **2-file (`issues.md` + `business.md`); no profile.yml dependency** | Inherits v0.4.x 2-file pattern (grader reusable); profile.yml is company-identity (irrelevant for fact-pattern analysis); router Q4-fact bypasses prerequisite check |
| 5 | research interaction | **Plan-first 半互動 (plan → user Y/n confirm → autonomous loop)** | classify-path Y/n precedent (SP3b validated); plan.md is cheap reproducibility checkpoint before token spend |
| 6 | research output | **2-file (`research-memo.md` + `executive-summary.md`); citations embedded in memo + manifest section** | Symmetric with issue-spot; citation manifest in single section grep-able by grader (no need for separate citations.md file) |
| 7 | research Agent loop cap | **Hybrid: ≤ 5 rounds OR ≤ 30 fetches; early-stop if ≥ 8 sources AND ≥ 2 法源類型; ⚠️ marker on forced_stop** | Cost ceiling ~$0.5-1.5 per dispatch; 2-types is realistic floor (4-types ∩ too strict for new-domain queries); ⚠️ marker is grader safety-net signal |
| 8 | Cross-skill handoff | **Soft handoff issue-spot → research only (markdown query string in business.md "建議下一步" block); no auto-dispatch; no reverse handoff** | SP3b contract-breach precedent; user controls token budget; reverse handoff has no signal source (research input ≠ fact pattern) |

Engineering trade-offs only; legal-domain content (請求權基礎 element 列法 / dogfood case fact pattern textbook source / Harvey citation pinpoint convention) drafted by controller and marked `[draft — for 法務 review]` per `feedback_legal_toolkit_defer_legal_domain.md`. 法務 validation deferred to Phase 4.5 GC outreach.

## 4. Architecture overview

```
v0.4.4 (current main, 5 active skills)
    │
    ├─ using-legal-toolkit (router)
    ├─ legal-playbook-author (utility)
    ├─ legal-contract-review (📋 Playbook)
    ├─ legal-document-draft (📝 Template)
    └─ legal-incident-response (🚨 Runbook)

v0.5.0 PR (this design SP3-a):
    │
    ├─ legal-issue-spot (NEW, 🔍 IRAC; pure LLM; no profile dependency)
    └─ router patch: Q4-fact dispatch unlocked

v0.5.2 PR (this design SP3-b):
    │
    ├─ legal-research (NEW, 🔍 IRAC + Agent; WebFetch-driven; no profile dependency)
    └─ router patch: Q4-law-lookup dispatch unlocked

Phase 4 Tracker stays v0.6.0 (zero ROADMAP shift).

Cross-skill handoff: issue-spot business.md → research command string (user-mediated; no auto-dispatch).
```

**Inherited from v0.4.x (no change)**:

- Path A discipline (current Taiwan in-force law / 即時 not 72hr / 委託-受託 not controller-processor / 民法 §12-13 not PDPA minor age)
- §6.3 Mandatory Disclaimer footer + §6.4 Escalation Override
- `legal-outputs/<timestamp>-<skill>/` output directory pattern
- canonical SoT via `scripts/canonical/` + `distribute.py` + `verify-drift.py` CI gate
- Grader self-contained per skill; PATH_A_ANTIPATTERNS bank byte-identical (verify-drift expanded)
- Template-orphan check (v0.4.4 safety net) duplicated to new graders
- Anthropic flat-folder discipline (subfolder no nesting)
- commit type whitelist + kebab scope + marketplace.json sync CI

## 5. `legal-issue-spot` (v0.5.0 SP3-a) detailed design

### 5.1 Folder layout

```
legal-toolkit/skills/legal-issue-spot/
├── SKILL.md                              ~5,000 tokens
├── README.md / README.ja.md / README.zh-TW.md   tri-language per PR #150 convention
├── protocols/                            single-level subfolder (Anthropic flat rule)
│   ├── parse-facts.md                    LLM extracts 當事人/行為/時間/金額
│   ├── timeline.md                       時間軸 from extracted facts
│   ├── spot-issues.md                    Each fact → 構成要件 seed
│   ├── subsumption.md                    Per-element 涵攝 (該當 / 不該當 / ⚠️)
│   ├── counterfactual.md                 反事實 + carve-out + default rule
│   └── risk-grade.md                     🔴/🟡/🟢 + escalation rules
├── references/
│   ├── 請求權基礎-民法.md                 [draft — for 法務 review] ~200 行
│   ├── 構成要件-勞動.md                   [draft — for 法務 review] ~200 行
│   └── 構成要件-個資.md                   [draft — for 法務 review] ~200 行
├── assets/
│   ├── output-schema-issues.json         issues.md structural schema
│   └── output-schema-business.json       business.md structural schema
├── scripts/
│   └── grade_issue_spot.py               structural grader (self-contained)
└── tests/
    ├── test_grade_issue_spot.py          ~10 tests
    └── fixtures/
        ├── issues-pass.md, business-pass.md
        ├── issues-orphan-tbd.md          template-orphan check
        ├── business-no-handoff-on-yellow.md  ⚠️ but no handoff query → fail
        └── (5-7 negative fixtures for grader checks)
```

### 5.2 SKILL.md outline

- Frontmatter: name / description (TRIGGER bilingual + USE WHEN) / version 0.1.0
- Language Policy (instructions EN; user-facing zh-TW; mixed by design)
- Workflow mermaid (parse-facts → timeline → spot-issues → subsumption → counterfactual → risk-grade → output)
- 6 protocol pointer (1 line each + reference relative path)
- Reference pointer (3 reference files; intended consumption by subsumption + counterfactual)
- Output contract (legal-outputs/<ts>-issue-spot/{issues.md, business.md})
- §6.3 disclaimer footer requirement (boilerplate text in protocols/)
- §6.4 escalation override (when ≥ 2 構成要件 ⚠️ or risk = 🔴, business.md MUST recommend escalation to 律師)
- Cross-skill handoff: business.md trailer "建議下一步" block when ≥ 1 ⚠️ in subsumption
- Path A discipline note (current Taiwan law)
- When to use / NOT to use
- Inputs (fact pattern free-text) / Outputs (2 files)
- Reference link to PRODUCT-SPEC + ROADMAP

### 5.3 Output schemas

`assets/output-schema-issues.json` (validated by grader):

```json
{
  "required_sections": ["§事實摘要", "§時間軸", "§Issue 矩陣", "§構成要件涵攝", "§反事實", "§風險分級", "§Disclaimer"],
  "subsumption_table_columns": ["構成要件", "事實對應", "涵攝結論", "信心"],
  "subsumption_conclusion_values": ["該當", "不該當", "⚠️"],
  "risk_grade_required": ["🔴", "🟡", "🟢"],
  "min_byte_size": 800,
  "no_template_orphans": true
}
```

`assets/output-schema-business.json`:

```json
{
  "required_sections": ["§TL;DR", "§可以做的部分", "§不能做的部分", "§注意點", "§風險分級", "§Disclaimer"],
  "conditional_sections": {
    "§建議下一步": "if issues.md subsumption table contains any ⚠️"
  },
  "risk_emoji_required": ["🔴", "🟡", "🟢"],
  "handoff_query_format": "`/legal-research --query=\"<NL query>\"`",
  "min_byte_size": 400,
  "no_template_orphans": true
}
```

### 5.4 grade_issue_spot.py interface

```python
#!/usr/bin/env python3
"""Deterministic structural grader for legal-issue-spot output directories."""

# Constants byte-identical to v0.4.x graders (drift-verified):
PATH_A_ANTIPATTERNS = [...]  # GDPR phrases, 72hr, controller/processor, etc.
def _check_no_template_orphans(text): ...  # v0.4.4 safety net

CHECKS = [
    ("structural_issues_md",       lambda paths: structural_check(paths.issues_md, schema=...)),
    ("structural_business_md",     lambda paths: structural_check(paths.business_md, schema=...)),
    ("path_a_antipatterns",        lambda paths: check_no_anti(paths.both)),
    ("template_orphan_check",      lambda paths: _check_no_template_orphans(paths.both_text)),
    ("crac_section_present",       lambda paths: assert_section(paths.issues_md, "§Issue 矩陣")),
    ("subsumption_table_valid",    lambda paths: validate_subsumption_table(paths.issues_md)),
    ("risk_emoji_required",        lambda paths: assert_one_of(paths.business_md, ["🔴","🟡","🟢"])),
    ("handoff_when_yellow",        lambda paths: check_handoff_when_yellow(paths.issues_md, paths.business_md)),
    ("disclaimer_footer",          lambda paths: assert_disclaimer(paths.both)),
    ("escalation_when_red",        lambda paths: check_escalation_when_red(paths.business_md)),
]

# Exit codes: 0 = PASS / 1 = FAIL / 2 = NEEDS_REVISION (PASS_WITH_NOTES)
```

### 5.5 Reference file content (controller-drafted, deferred 法務 review)

Per `feedback_legal_toolkit_defer_legal_domain.md`, controller drafts grounded in:
- obsidian Design SoT §1.4 (Issue Spotting) + §3.6 (skill spec)
- canonical legal-sources.json (民法 184/227/767/179 條文 already in canonical SoT)
- Controller training knowledge of TW 民法 構成要件 (王澤鑑《侵權行為法》/《債法原理》framework)

Each reference file marked at top: `<!-- [draft — for 法務 review; Phase 4.5 GC outreach validation] -->`.

`請求權基礎-民法.md` covers 民法 §184 (侵權行為) / §227 (不完全給付) / §767 (物上請求權) / §179 (不當得利). Per element: 1-line 白話 + typical 反例 + typical carve-out.

`構成要件-勞動.md` covers 勞基法 §11 (合法解雇事由) + §14 (勞工終止事由) + §16 (預告期間) + 性平法 §13 (性騷擾雇主責任).

`構成要件-個資.md` covers 個資法 §5 (蒐集原則) + §8-9 (告知義務) + §27 (適當安全措施) + §29 (損害賠償).

Each ~200 lines; total ~600 lines hand-curated content commit (single commit, with `[draft]` markers throughout).

### 5.6 Test surface

10 tests in `tests/test_grade_issue_spot.py`:

1. `test_passing_fixture_exits_0` — both files schema-valid, no anti-patterns, ≥ 1 ⚠️ → has handoff query
2. `test_missing_issues_md_exits_1`
3. `test_missing_business_md_exits_1`
4. `test_path_a_antipattern_72hr_exits_1`
5. `test_path_a_antipattern_controller_processor_exits_1`
6. `test_template_orphan_in_issues_md_exits_1`
7. `test_template_orphan_in_business_md_exits_1`
8. `test_yellow_in_subsumption_no_handoff_exits_1`
9. `test_red_risk_no_escalation_exits_1`
10. `test_missing_disclaimer_exits_1`

All fixture-driven; no LLM calls. PYTHONDONTWRITEBYTECODE=1 enforced (per `feedback_pycache_hook_blocks_edits.md`).

## 6. `legal-research` (v0.5.2 SP3-b) detailed design

### 6.1 Folder layout

```
legal-toolkit/skills/legal-research/
├── SKILL.md                              ~5,500 tokens
├── README.md / README.ja.md / README.zh-TW.md
├── protocols/
│   ├── plan.md                           Generate plan.md + state.json (search strategy + budget cap)
│   ├── iterative-search.md               Single-round logic (read state.json → check budget → WebFetch → write)
│   ├── triangulate.md                    Triangulation judgement → early-stop or continue
│   └── cite.md                           Synthesize research-memo.md + executive-summary.md (Harvey citation)
├── references/
│   ├── webfetch-targets.md               [draft] Target sites + URL patterns + crawl etiquette
│   ├── citation-format.md                [draft] Harvey doc-level citation format examples
│   └── triangulation-rules.md            [draft] 法源類型 classification + ∩ rules
├── assets/
│   ├── plan-schema.json                  plan.md structural schema
│   ├── state-schema.json                 state.json structural schema (rounds/fetches/sources/法源類型/markers)
│   ├── output-schema-memo.json           research-memo.md schema
│   ├── output-schema-summary.json        executive-summary.md schema
│   └── triangulation-config.json         centralized loop cap params (≤5 rounds, ≤30 fetches, ≥8 sources, ≥2 types)
├── scripts/
│   └── grade_research.py                 structural grader (self-contained)
└── tests/
    ├── test_grade_research.py            ~12-15 tests
    └── fixtures/
        ├── plan-pass.md, memo-pass.md, summary-pass.md
        ├── memo-7-sources-no-warning.md  (fail: < 8 + no ⚠️)
        ├── memo-7-sources-with-warning.md (pass-with-notes)
        ├── state-over-cap.json           (fail: rounds=6)
        ├── state-inconsistent.json       (fail: state forced_stop=true but memo no ⚠️)
        ├── citation-no-relevance.md      (fail: bare 字號 with no relevance line)
        └── single-type-coverage.md       (fail: only 條文 type; no 判決/函釋/學說)
```

### 6.2 SKILL.md outline + Agent loop

The Agent loop is **LLM-driven, state-tracked**. Python is used only for state persistence (`state.json` is the single checkpoint file). LLM reads state.json at the start of each iteration and decides whether to continue, early-stop, or force-stop.

```
Step 0 — User invokes /legal-research --query="..."
Step 1 — Run protocols/plan.md
  → Output: plan.md (search keywords + target sites + 法源 type plan + budget config)
  → Output: state.json (rounds=0, fetches=0, sources=[], types_covered={}, early_stop=false, forced_stop=false)
  → Stdout preview plan.md + ask "Plan OK 嗎? Y/n" (classify-path precedent)

Step 2 — User confirms (Y) → enter loop
  Loop body (LLM repeats until exit condition):
    Read state.json
    if rounds >= 5 OR fetches >= 30:
        state.forced_stop = true → break to Step 3
    if len(sources) >= 8 AND len(types_covered) >= 2:
        state.early_stop = true → break to Step 3
    Run protocols/iterative-search.md:
      Pick next keyword/site combination from plan
      Call WebFetch tool
      Parse result → extract 0-N source candidates
      Append to state.sources; update state.types_covered
      Increment rounds + fetches
      Write state.json

Step 3 — Run protocols/triangulate.md
  Read state.sources; cluster by type; check ∩ coverage
  If forced_stop: prepend ⚠️ "覆蓋未達 triangulation" warning block to memo
  
Step 4 — Run protocols/cite.md
  Synthesize research-memo.md (full analysis + inline citations + ## Citations manifest section)
  Synthesize executive-summary.md (TL;DR + ✅/⚠️/❌ + 1-line basis + escalation if forced_stop)
  Each citation: source full reference + 1-line relevance to conclusion (Harvey doc-level)
```

### 6.3 plan.md structural schema

```json
{
  "required_sections": ["§問題", "§關鍵字", "§目標 site", "§法源類型 plan", "§Budget"],
  "min_keywords": 3,
  "min_target_sites": 2,
  "expected_source_types": "subset of [條文, 判決, 函釋, 學說]",
  "budget_fields": ["max_rounds", "max_fetches", "early_stop_min_sources", "early_stop_min_types"]
}
```

### 6.4 state.json schema

```json
{
  "type": "object",
  "required": ["rounds", "fetches", "sources", "types_covered", "early_stop", "forced_stop", "started_at", "updated_at"],
  "properties": {
    "rounds": {"type": "integer", "minimum": 0, "maximum": 5},
    "fetches": {"type": "integer", "minimum": 0, "maximum": 30},
    "sources": {"type": "array", "items": {"type": "object", "required": ["url_or_cite", "type", "captured_at"]}},
    "types_covered": {"type": "object", "additionalProperties": {"type": "integer"}},
    "early_stop": {"type": "boolean"},
    "forced_stop": {"type": "boolean"}
  }
}
```

### 6.5 grade_research.py interface

```python
CHECKS = [
    ("structural_plan_md",         lambda paths: structural_check(paths.plan_md, schema=plan-schema)),
    ("structural_state_json",      lambda paths: jsonschema_check(paths.state_json, schema=state-schema)),
    ("state_within_cap",           lambda paths: assert(rounds<=5 and fetches<=30)),
    ("state_consistency",          lambda paths: assert(forced_stop ↔ memo has ⚠️ block)),
    ("structural_memo_md",         lambda paths: structural_check(paths.memo_md, schema=memo-schema)),
    ("citation_section_present",   lambda paths: assert_section(paths.memo_md, "## Citations")),
    ("citation_count_or_warn",     lambda paths: count(citations) >= 8 OR memo has ⚠️),
    ("citation_has_relevance",     lambda paths: each citation has 1-line relevance text),
    ("source_type_coverage",       lambda paths: types_count >= 2 OR memo has ⚠️),
    ("structural_summary_md",      lambda paths: structural_check(paths.summary_md, schema=summary-schema)),
    ("summary_conclusion_marker",  lambda paths: summary has one of [✅,⚠️,❌]),
    ("path_a_antipatterns",        lambda paths: check_no_anti(paths.all_md)),
    ("template_orphan_check",      lambda paths: _check_no_template_orphans(paths.all_text)),
    ("disclaimer_footer",          lambda paths: assert_disclaimer(paths.memo_md, paths.summary_md)),
]
```

### 6.6 WebFetch target sites (controller-drafted, deferred 法務 review)

`references/webfetch-targets.md` lists:
- `law.moj.gov.tw/LawClass/LawAll.aspx?pcode=<法典>` — 全國法規資料庫 (條文)
- `judicial.gov.tw/FJUD/default.aspx` — 司法院法學資料檢索 (判決)
- `mojlaw.moj.gov.tw/LawSearch.aspx?Type=L` — 法務部主管法規 (函釋)
- `pdpc.moj.gov.tw` (主管機關 RSS) — 個資保護 (PDPC 籌備處 函釋)
- Fallback: Google Cache + archive.org Wayback Machine

Each entry includes URL pattern + crawl etiquette (rate limit, User-Agent declaration). If 2026 a target site is anti-bot or returns 403, plan.md should mark it as unavailable and triangulation downgrades to whatever is reachable; grader treats `forced_stop` + ⚠️ marker as PASS_WITH_NOTES (exit 2), not FAIL.

### 6.7 Test surface

12-15 tests in `tests/test_grade_research.py`. Pattern matches issue-spot — all fixture-driven, no LLM calls. PYTHONDONTWRITEBYTECODE=1.

## 7. Cross-cutting design

### 7.1 Router Q4 2-stage unlock

`using-legal-toolkit/SKILL.md` modifications across the 2 PRs:

**v0.5.0 PR**: Q4-fact branch unlocked. Keyword bank added:
- fact-pattern triggers: 「我們想做」/「能不能」/「是否合法」/「分析一下」/「is it legal」/「can we」
- `legal-issue-spot` — Phase 3 NOT YET → **active**

**v0.5.2 PR**: Q4-law-lookup branch unlocked. Keyword bank added:
- law-lookup triggers: 「查 §」/「§227 是」/「判例」/「法條」/「research」/「找判決」/「lookup」
- `legal-research` — Phase 3 NOT YET → **active**

Q4 prerequisite check: NEITHER branch checks profile.yml (Phase 3 skills are profile-independent). Router `legal-playbook/profile.yml` check stays gated to Q2/Q3 (zero v0.5.x change to existing prerequisite logic).

### 7.2 Cross-skill handoff format

issue-spot `business.md` ends with conditional "建議下一步" block when subsumption table contains ≥ 1 ⚠️:

```markdown
## 建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- §227 不完全給付的 carve-out 認定
  → `/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`

- 個資法 §27 適當安全措施的「適當」標準
  → `/legal-research --query="個資法 §27 適當安全措施 PDPC 函釋"`
```

Grader rule (`grade_issue_spot.py`):

```python
def handoff_query_string_required_when_yellow(business_md, issues_md):
    if has_yellow_warning_in_subsumption_table(issues_md):
        assert "## 建議下一步" in business_md
        assert re.search(r"`/legal-research --query=\"[^\"]+\"`", business_md)
```

`grade_research.py` does NOT parse query string content (treated as opaque parameter; no brittle alignment).

Reverse handoff (research → issue-spot) **not implemented** (Q8 locked). Router Q4 dispatch logic catches misrouted fact-pattern queries.

### 7.3 Grader self-contained + bank duplication

Per v0.4.x SSOT-and-functional-copy convention:
- Each grader is self-contained Python (no shared `grader_lib`)
- `PATH_A_ANTIPATTERNS` bank byte-identical across `grade_draft.py` (SP3a) + `grade_response.py` (SP3b) + `grade_issue_spot.py` (v0.5.0) + `grade_research.py` (v0.5.2) — 4 graders total
- `_check_no_template_orphans()` helper byte-identical across all 4
- `legal-toolkit/scripts/verify-drift.py` extended to verify these 2 byte-identical artifacts across all 4 graders (fail CI if any drift)

### 7.4 CI surface

Per `.github/workflows/legal-toolkit.yml` (existing) + new steps:
- v0.5.0 PR: add `pytest legal-toolkit/skills/legal-issue-spot/tests/`
- v0.5.2 PR: add `pytest legal-toolkit/skills/legal-research/tests/`
- v0.5.0 PR: extend `verify-drift.py` to verify 4-grader bank drift
- Both PRs: existing flat-folder check + commit type whitelist + marketplace.json sync continue to apply

## 8. Ship sequence + risks

### 8.1 Semver + PR cadence

```
v0.4.4 (current main)
  ↓
v0.5.0  Phase 3-a SP3-a — legal-issue-spot
        ~10 commits / ~25-30 SDD subagent invocations / 4-5 days
  ↓
v0.5.1  (reserved) SP3-a dogfood patches if dogfood reveals P0/P1
  ↓
v0.5.2  Phase 3-b SP3-b — legal-research
        ~10 commits / ~25-30 SDD subagent invocations / 4-5 days
  ↓
v0.5.3  (reserved) SP3-b dogfood patches
  ↓
v0.6.0  Phase 4 Tracker cluster (ROADMAP unchanged)
```

### 8.2 v0.5.0 SP3-a commit breakdown (~10 commits)

```
1. docs(legal-toolkit): Phase 3 IRAC cluster design spec
2. feat(legal-toolkit): legal-issue-spot skill scaffold (SKILL.md + folder + frontmatter)
3. feat(legal-toolkit): legal-issue-spot 6 protocol files
4. feat(legal-toolkit): legal-issue-spot 3 reference files (draft for 法務 review)
5. feat(legal-toolkit): legal-issue-spot output schemas (issues + business)
6. feat(legal-toolkit): grade_issue_spot.py + 10 tests + fixtures
7. feat(legal-toolkit): router Q4-fact dispatch unlock
8. chore(legal-toolkit): drift verify update for issue-spot grader bank (4-grader)
9. docs(legal-toolkit): SKILL READMEs (en/ja/zh-TW) + plugin docs sync
10. chore(legal-toolkit): bump plugin.json + marketplace.json to v0.5.0
```

### 8.3 v0.5.2 SP3-b commit breakdown (~10 commits)

```
1. feat(legal-toolkit): legal-research skill scaffold
2. feat(legal-toolkit): legal-research 4 protocol files (plan/search/triangulate/cite)
3. feat(legal-toolkit): legal-research 3 reference files (draft)
4. feat(legal-toolkit): legal-research schemas (plan + state + memo + summary + triangulation-config)
5. feat(legal-toolkit): grade_research.py + 12-15 tests + fixtures
6. feat(legal-toolkit): router Q4-law-lookup dispatch unlock
7. chore(legal-toolkit): drift verify update for research grader bank
8. docs(legal-toolkit): SKILL READMEs + plugin docs sync
9. chore(legal-toolkit): bump plugin.json + marketplace.json to v0.5.2
```

### 8.4 SDD orchestration (per PR)

Per task pattern (per `feedback_subagent_driven_development_validated.md`):
- **Implementer subagent**: fresh per task, produces artifact (no prior context)
- **Spec reviewer subagent**: reviews artifact against this design doc + plan
- **Code-quality reviewer subagent**: reviews style + test coverage + convention adherence
- **Controller** (this session): merges feedback, commits, moves to next task

Parallelization opportunities (per autonomous-mode preference `feedback_legal_toolkit_autonomous_after_design_lock.md`):
- 6 issue-spot protocol files = 6 parallel implementer subagents
- 3 issue-spot reference files = 3 parallel implementer subagents (legal-domain content)
- Reviewers can run in parallel against multiple committed artifacts

Final per-PR gate: **Fresh-eyes audit subagent** scans cross-task drift (per v0.4.4 P2-1 incident which validated fresh-eyes catch worth).

### 8.5 Risk + mitigation

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | `.gov.tw` site WebFetch blocked / re-layout / login wall | research unstable | references/webfetch-targets.md lists fallbacks (Google cache / archive.org / RSS feeds where available); grader accepts `forced_stop` + ⚠️ marker as PASS_WITH_NOTES (exit 2), not FAIL |
| R2 | User skips plan-first confirmation (hits Y reflexively) | 30 fetch budget burned on off-topic plan | SKILL.md mandates plan.md include 3+ keywords + 2+ target sites + expected source types; grader validates plan-schema; stdout preview shows full plan.md before Y/n |
| R3 | Triangulation early-stop params (≥ 8 sources, ≥ 2 types) too loose/strict | Loose → low-quality memo; strict → permanent forced_stop | Centralized in `assets/triangulation-config.json` (not scattered in protocols); v0.5.3 patch room reserved for adjustment |
| R4 | 3 × ~200-line reference files (~600 lines hand-curated content) | issue-spot blocked on 法務 detail | Controller drafts grounded in obsidian SoT + canonical legal-sources.json + training; marked `[draft — for 法務 review]`; deferred validation to Phase 4.5 GC outreach |
| R5 | Quality-gate datasets (5 case + 5 法律問題) absent | ROADMAP semantic gate uncrossable | CI runs structural fixtures (synthetic); ROADMAP semantic gate (70% alignment / ≥ 8 sources) marked post-merge dogfood; controller hand-curates 5 cases post-merge → audit memo (v0.4.3 dogfood pattern) |
| R6 | Cross-skill handoff query string format drift | issue-spot's query keywords misalign with research input | grader_issue_spot.py enforces regex `\`/legal-research --query="..."\``; grade_research.py treats query as opaque (no brittle alignment) |
| R7 | Plan-first interaction breaks router single-dispatch convention | User confusion / skipped plan review | classify-path Y/n precedent (SP3b validated); plan.md is disk artifact (recoverable, unlike stdout-only) |
| R8 | LLM Agent loop fails to update state.json correctly | Loop never converges / over-runs cap | `iterative-search.md` protocol contains explicit step "after WebFetch, MUST write state.json"; grader_research.py validates state-schema + state-consistency post-hoc |
| R9 | Fresh-eyes audit subagent over-scope (catches stylistic items as Critical) | False alarm halts ship | Audit prompt scopes to: cross-task drift / per-task reviewer blind spots / contract-vs-implementation gaps; stylistic = Minor (fix in next commit, not block) |

### 8.6 Quality gate definitions

**CI (every PR must pass)**:
- structural grader exit 0 across all fixtures
- drift verify exit 0 (4-grader bank byte-identical)
- flat-folder check / commit type / kebab scope / marketplace-description sync

**Post-merge dogfood (1 day after merge; patch PR triggered if P0/P1 found)**:
- v0.5.0 SP3-a: 5 hand-curated 案例 fact pattern → run issue-spot → controller self-grade vs senior 法務 hand-grade (kouko optionally connects 1 GC sample) → 70% element alignment = PASS
- v0.5.2 SP3-b: 5 法律問題 → run research → controller self-grade ≥ 8 valid sources / each source 1-line supporting relevance / ≥ 2 法源 types
- P0/P1 → trigger v0.5.1 / v0.5.3 patch PR

## 9. Open items

Items deferred (not blocking Phase 3 ship):
1. **法務 SME validation of reference files** (請求權基礎-民法 / 構成要件-勞動 / 構成要件-個資 / webfetch-targets / citation-format / triangulation-rules) — defer to Phase 4.5 GC outreach
2. **Quality-gate dataset curation** (5 fact patterns / 5 法律問題 with hand-graded ground truth) — controller hand-curates post-merge for dogfood
3. **Plan resume flag** (`/legal-research --plan-from <file>`) — v0.5.x patch room
4. **Reverse handoff** (research → issue-spot) — explicitly NOT implemented per Q8; reconsider only if dogfood signals real need
5. **research user-in-the-loop checkpoint at search round 2** — Q5-C variant; defer to v0.5.x patch if dogfood reveals plan-first alone insufficient

## 10. Lineage + cross-references

**Inherited conventions** (from v0.4.x line):
- Path A discipline → SP2 PR #273
- §6.3 Mandatory Disclaimer + §6.4 Escalation Override → SoT design ledger §11
- 2-file audience-shaped output → SP3a v0.4.0 (PR #277) + SP3b v0.4.2 (PR #286)
- Canonical SoT pattern → SP1 v0.3.6 (PR #272) + SP3b v0.4.3 (PR #288, schema v2 migration)
- Grader self-contained + bank duplication → SP3a + SP3b
- Template-orphan check → v0.4.4 (PR #290)
- SDD pattern → SP3b v0.4.2 (validated 2-stage review)
- classify-path Y/n confirm precedent → SP3b v0.4.2

**External dependencies**:
- Claude Code WebFetch tool (used by research only)
- canonical legal-sources.json (read-only consumed by issue-spot for 條文 references; no schema change)

**Memory cross-refs**:
- `project_legal_toolkit_design.md` — plugin-level SoT pointer + ship history
- `feedback_legal_toolkit_defer_legal_domain.md` — controller drives legal-domain decisions
- `feedback_legal_toolkit_autonomous_after_design_lock.md` — autonomous mode after design approval
- `feedback_subagent_driven_development_validated.md` — SDD orchestration pattern
- `feedback_pycache_hook_blocks_edits.md` — PYTHONDONTWRITEBYTECODE=1 enforcement
- `feedback_grader_structural_vs_semantic.md` — structural grader is necessary but not sufficient
- `feedback_dogfood_authoring_drift.md` — dogfood replay catches schema-doc drift

**Obsidian Design SoT**:
- `kouko-obsidian-vault/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md` §3.6 (issue-spot) + §3.7 (research) + §11 ledger

---

End of design.
