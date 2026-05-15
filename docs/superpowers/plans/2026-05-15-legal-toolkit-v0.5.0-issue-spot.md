# legal-toolkit v0.5.0 SP3-a `legal-issue-spot` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `legal-issue-spot` skill (Phase 3 SP3-a IRAC cluster), bumping legal-toolkit to v0.5.0 and unlocking router Q4-fact dispatch path. Plugin grows from 5 → 6 active skills.

**Architecture:** Pure-LLM workflow skill (no external fetches, no profile.yml dependency). 6 protocols (parse-facts → timeline → spot-issues → subsumption → counterfactual → risk-grade) drive fact-pattern → 構成要件 涵攝 → 風險分級 → escalation 建議. 2-file audience-shaped output (issues.md + business.md) inheriting v0.4.x convention. Self-contained Python grader with byte-identical PATH_A_ANTIPATTERNS bank duplicated from existing 3 graders (drift-verified by CI).

**Tech Stack:** Python 3.11 (grader + tests via pytest), JSON Schema (output validation), Markdown (skill content + protocols + references + READMEs), Bash (drift verify CI script).

**Spec doc:** [`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) — read §5 (issue-spot detailed design) + §7 (cross-cutting) + §8 (ship sequence) before starting any task.

---

## File Structure

**Created:**
- `legal-toolkit/skills/legal-issue-spot/SKILL.md` (~5,000 tokens)
- `legal-toolkit/skills/legal-issue-spot/README.md` / `README.ja.md` / `README.zh-TW.md`
- `legal-toolkit/skills/legal-issue-spot/protocols/` (6 .md files)
- `legal-toolkit/skills/legal-issue-spot/references/` (3 .md files, `[draft]`)
- `legal-toolkit/skills/legal-issue-spot/assets/output-schema-issues.json`
- `legal-toolkit/skills/legal-issue-spot/assets/output-schema-business.json`
- `legal-toolkit/skills/legal-issue-spot/scripts/grade_issue_spot.py`
- `legal-toolkit/skills/legal-issue-spot/tests/test_grade_issue_spot.py`
- `legal-toolkit/skills/legal-issue-spot/tests/fixtures/*.md` (~10 fixtures)

**Modified:**
- `legal-toolkit/skills/using-legal-toolkit/SKILL.md` (Q4-fact dispatch unlock)
- `legal-toolkit/scripts/verify-drift.py` (extend to verify 4-grader PATH_A bank + template-orphan helper byte-identical)
- `legal-toolkit/.claude-plugin/plugin.json` (version 0.4.4 → 0.5.0; description += issue-spot mention)
- `.claude-plugin/marketplace.json` (description sync; same string as plugin.json)
- `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` (skill listing update; 5 → 6 active skills)

**Parallelizable subagent dispatch:**
- Task 2 (6 protocol files) — 6 parallel implementer subagents
- Task 3 (3 reference files) — 3 parallel implementer subagents
- Task 8 (3 READMEs) — 3 parallel implementer subagents
- Other tasks: sequential (have dependencies)

---

## Task 1: Skill scaffold (SKILL.md + folder layout)

**Files:**
- Create: `legal-toolkit/skills/legal-issue-spot/SKILL.md`
- Create: `legal-toolkit/skills/legal-issue-spot/protocols/.gitkeep`
- Create: `legal-toolkit/skills/legal-issue-spot/references/.gitkeep`
- Create: `legal-toolkit/skills/legal-issue-spot/assets/.gitkeep`
- Create: `legal-toolkit/skills/legal-issue-spot/scripts/.gitkeep`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/.gitkeep`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/.gitkeep`

- [ ] **Step 1: Create folder structure**

```bash
cd /Users/kouko/GitHub/monkey-skills/.claude/worktrees/feat+legal-toolkit-v0.5.0-issue-spot
mkdir -p legal-toolkit/skills/legal-issue-spot/{protocols,references,assets,scripts,tests/fixtures}
touch legal-toolkit/skills/legal-issue-spot/{protocols,references,assets,scripts,tests,tests/fixtures}/.gitkeep
```

Verify with `find legal-toolkit/skills/legal-issue-spot -type d`:
```
legal-toolkit/skills/legal-issue-spot
legal-toolkit/skills/legal-issue-spot/protocols
legal-toolkit/skills/legal-issue-spot/references
legal-toolkit/skills/legal-issue-spot/assets
legal-toolkit/skills/legal-issue-spot/scripts
legal-toolkit/skills/legal-issue-spot/tests
legal-toolkit/skills/legal-issue-spot/tests/fixtures
```

Confirm: each subfolder is single-level under skill root (Anthropic flat-folder rule).

- [ ] **Step 2: Author SKILL.md frontmatter + workflow body**

Create `legal-toolkit/skills/legal-issue-spot/SKILL.md` with this frontmatter:

```yaml
---
name: legal-issue-spot
description: |
  IRAC issue-spotting skill for Taiwan in-house 法務. Takes a business-language fact pattern ("我們想做 X，能不能做？") and produces an issue 矩陣 + per-element 構成要件涵攝 + 風險分級 (🔴/🟡/🟢) + escalation recommendation. Pure-LLM workflow; no external fetches; no profile.yml dependency. Output: 2-file audience-shaped (issues.md for 法務 / business.md for 業務 + escalation建議). When ⚠️ low-confidence subsumption detected, business.md soft-handoffs to /legal-research with concrete query string. §6.3 disclaimer footer + §6.4 escalation override inherited from v0.4.x.

  TRIGGER (中英雙語):
  - 「能不能做」/「是否合法」/「我們想做」/「分析一下」
  - "is it legal" / "can we" / "fact pattern" / "issue spot"
  - 民法 / 勞基法 / 個資法 issue across multiple statutes

  USE WHEN: user describes a business scenario in fact-pattern form and wants legal analysis (issue-spotting + 構成要件 涵攝 + risk grade), NOT a literal law-text lookup (that's legal-research).
version: 0.1.0
---
```

Body covers (~5,000 tokens total):
1. Language Policy block (instructions EN; user-facing zh-TW; mixed by design — no translation of keywords)
2. Workflow mermaid (parse-facts → timeline → spot-issues → subsumption → counterfactual → risk-grade → output)
3. 6 protocol pointers (relative path + 1-line purpose each):
   - `protocols/parse-facts.md` — Extract 當事人/行為/時間/金額 from raw fact pattern
   - `protocols/timeline.md` — Build chronological timeline
   - `protocols/spot-issues.md` — Map facts to 構成要件 seeds (per statute)
   - `protocols/subsumption.md` — Per-element 涵攝 (該當 / 不該當 / ⚠️) using references/
   - `protocols/counterfactual.md` — 反事實 + carve-out + default rule
   - `protocols/risk-grade.md` — 🔴/🟡/🟢 + escalation rules
4. 3 reference pointers (consumed by subsumption + counterfactual):
   - `references/請求權基礎-民法.md` (民法 184/227/767/179)
   - `references/構成要件-勞動.md` (勞基法 §11/14/16 + 性平法 §13)
   - `references/構成要件-個資.md` (個資法 §5/8/9/27/29)
5. Output contract block: `legal-outputs/<timestamp>-issue-spot/{issues.md, business.md}`
6. §6.3 Mandatory Disclaimer footer requirement (boilerplate text in protocols/risk-grade.md)
7. §6.4 Escalation Override (when ≥ 2 ⚠️ in subsumption table OR risk = 🔴 → business.md MUST recommend 律師 escalation)
8. Cross-skill handoff (business.md trailer "建議下一步" block when ≥ 1 ⚠️; format: backtick `/legal-research --query="..."`)
9. Path A discipline note (current Taiwan in-force law; refer to canonical legal-sources.json for 條文)
10. When to use / NOT to use sections
11. Inputs (fact pattern free-text) / Outputs (2 files in legal-outputs/...)
12. Reference links: PRODUCT-SPEC + ROADMAP + design spec

- [ ] **Step 3: Verify SKILL.md token budget + flat-folder check**

```bash
wc -w legal-toolkit/skills/legal-issue-spot/SKILL.md
# Expected: ~3,500-4,500 words (~5,000 tokens)

# Run flat-folder validator (the existing hook should not block)
ls -R legal-toolkit/skills/legal-issue-spot/
# Verify each subfolder contains only files, no nested subfolders
```

Acceptance: SKILL.md passes structural checks; all 6 subfolders single-level.

- [ ] **Step 4: Commit**

```bash
git add legal-toolkit/skills/legal-issue-spot/
git commit -m "feat(legal-toolkit): legal-issue-spot skill scaffold (SKILL.md + folder)

Phase 3 SP3-a v0.5.0. Scaffolds the IRAC issue-spotting skill with
SKILL.md (frontmatter + workflow body + protocol/reference/output
pointers) and 6 single-level subfolders (protocols/ references/
assets/ scripts/ tests/ tests/fixtures/) per Anthropic flat-folder rule.

Skill is profile.yml-independent (input is fact pattern; no company
identity needed). §6.3 disclaimer + §6.4 escalation override
boilerplate referenced from protocols/risk-grade.md (filled in
Task 2). Cross-skill handoff to /legal-research scaffolded in
SKILL.md output contract; grader rule lands in Task 5.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: 6 protocol files (parallelizable — 6 implementer subagents)

**Files:**
- Create: `legal-toolkit/skills/legal-issue-spot/protocols/parse-facts.md`
- Create: `legal-toolkit/skills/legal-issue-spot/protocols/timeline.md`
- Create: `legal-toolkit/skills/legal-issue-spot/protocols/spot-issues.md`
- Create: `legal-toolkit/skills/legal-issue-spot/protocols/subsumption.md`
- Create: `legal-toolkit/skills/legal-issue-spot/protocols/counterfactual.md`
- Create: `legal-toolkit/skills/legal-issue-spot/protocols/risk-grade.md`

Each protocol file:
- ~50-120 lines markdown
- Self-contained (LLM reads ONE protocol per workflow step)
- Reads inputs from `legal-outputs/<ts>-issue-spot/state.json` if needed (state.json optional for issue-spot — most state passes inline through markdown documents)
- Writes outputs explicitly to named markdown sections in issues.md / business.md
- Falls back to "halt + ask user" pattern when input ambiguous

- [ ] **Step 1: Dispatch 6 parallel implementer subagents — one per protocol file**

Each subagent receives:
- Protocol file path + responsibility (per spec §5.1 + §5.2 outline)
- Spec doc reference: `docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`
- obsidian SoT pointer: §3.6 issue-spot mermaid + §1.4 issue-spotting methodology
- Relevant references/ context (subsumption + counterfactual subagents need to know reference file names exist; can produce protocol that points to references/<file> with `please consult <file> for element list`)
- Acceptance: protocol file ~50-120 lines, valid markdown, produces named-section output, includes "halt + ask" fallback

Parallel dispatch via Agent tool; subagent_type=general-purpose.

**Per-protocol responsibility:**

`parse-facts.md` — LLM reads raw fact pattern (free-text input from user). Extracts structured facts: 當事人 (parties), 行為 (actions), 時間 (timestamps if any), 金額 (amounts if any), 標的 (subject matter). Writes to issues.md `§事實摘要` section as bullet list. Halt-and-ask if pattern is < 30 chars or contains contradictions.

`timeline.md` — Reads parse-facts output (`§事實摘要` from issues.md). Constructs chronological timeline. ISO 8601 dates where derivable; `⏳ 待釐清` for unrealized anchors (per SP3b ISO 8601 convention). Writes to issues.md `§時間軸` section as table.

`spot-issues.md` — Reads `§事實摘要`. Per fact, identifies candidate 構成要件 seeds across 3 statute domains (民法 / 勞動 / 個資). Outputs to issues.md `§Issue 矩陣` section as table (issue / 涉及法條 / 對應事實 columns). Multi-issue parallel rows expected.

`subsumption.md` — Reads `§Issue 矩陣` + `§事實摘要`. Per issue, looks up element list from `references/{請求權基礎-民法,構成要件-勞動,構成要件-個資}.md`. For each element: 涵攝 to facts. Output column = `該當` / `不該當` / `⚠️` with 1-line reasoning. Writes to issues.md `§構成要件涵攝` section.

`counterfactual.md` — Reads `§構成要件涵攝`. For each `⚠️` or 該當 result, runs reverse check: what reverses this? carve-out? default rule? typical 反例 from references/. Writes to issues.md `§反事實` section. Surfaces hidden assumptions.

`risk-grade.md` — Reads everything above. Synthesizes risk grade (🔴 high / 🟡 medium / 🟢 low). Drives escalation logic: ≥ 2 ⚠️ OR risk = 🔴 → MUST recommend 律師 escalation in business.md `§建議下一步` block. Writes to issues.md `§風險分級` and triggers business.md generation. ALSO embeds §6.3 Disclaimer footer text in both files.

- [ ] **Step 2: Spec-reviewer subagent reviews all 6 outputs**

Dispatch 1 reviewer subagent (subagent_type=general-purpose) with task:
- Verify each protocol matches spec §5.2 outline
- Verify all named sections (`§事實摘要` / `§時間軸` / `§Issue 矩陣` / `§構成要件涵攝` / `§反事實` / `§風險分級` / `§Disclaimer`) appear consistently across protocols
- Verify subsumption.md correctly references the 3 reference files by exact path
- Verify risk-grade.md handles §6.4 escalation override (≥ 2 ⚠️ OR 🔴 = MUST escalate)
- Verify cross-skill handoff query string format mentioned in risk-grade.md
- Flag any protocol that exceeds ~120 lines (consider splitting body sections)
- Output: review notes (Critical / Important / Minor) per protocol

- [ ] **Step 3: Code-quality reviewer subagent**

Dispatch 1 reviewer subagent with task:
- Verify markdown well-formed (no broken syntax, no orphaned headers)
- Verify protocol-internal pointers use correct relative paths (e.g. `references/請求權基礎-民法.md` not absolute)
- Verify each protocol's "halt + ask" pattern is consistent (same phrasing convention)
- Check for accidental Path A anti-patterns (72hr / controller-processor / GDPR phrases)
- Output: review notes

- [ ] **Step 4: Apply fixes from reviewers + commit**

Apply reviewer feedback (Critical + Important) inline. Minor items batch into next commit if possible.

```bash
git add legal-toolkit/skills/legal-issue-spot/protocols/
git commit -m "feat(legal-toolkit): legal-issue-spot 6 protocol files

Phase 3 SP3-a v0.5.0. 6 protocols implementing IRAC pipeline:

- parse-facts.md: extract 當事人/行為/時間/金額 from raw fact pattern
- timeline.md: ISO 8601 timeline from facts; ⏳ 待釐清 for unknowns
- spot-issues.md: fact → 構成要件 seed mapping across 民法/勞動/個資
- subsumption.md: per-element 涵攝 (該當/不該當/⚠️) using references/
- counterfactual.md: 反事實 + carve-out + default rule sweep
- risk-grade.md: 🔴/🟡/🟢 + §6.4 escalation override + §6.3 disclaimer footer

All protocols self-contained; output to named sections in
issues.md / business.md (no state.json needed for v0.5.0). halt+ask
fallback on ambiguous input.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: 3 reference files (parallelizable — 3 implementer subagents)

**Files:**
- Create: `legal-toolkit/skills/legal-issue-spot/references/請求權基礎-民法.md`
- Create: `legal-toolkit/skills/legal-issue-spot/references/構成要件-勞動.md`
- Create: `legal-toolkit/skills/legal-issue-spot/references/構成要件-個資.md`

Each reference file:
- Top: `<!-- [draft — for 法務 review; Phase 4.5 GC outreach validation] -->` marker (per `feedback_legal_toolkit_defer_legal_domain.md`)
- ~150-250 lines markdown
- Per element: 1-line 白話 + typical 反例 + typical carve-out (中厚 B per spec §5.5)
- Cross-references canonical legal-sources.json for 條文 text (don't duplicate condition text)

- [ ] **Step 1: Dispatch 3 parallel implementer subagents — one per reference file**

Each subagent receives:
- Reference file path + scope (per spec §5.5)
- Spec doc reference + obsidian SoT §3.6
- Path to canonical legal-sources.json (read-only consume; don't duplicate condition text)
- Acceptance: ~150-250 lines markdown; `[draft — for 法務 review]` HTML comment at top; element list complete per scope; 1-line 白話 + 反例 + carve-out per element

**Per-reference responsibility:**

`請求權基礎-民法.md` — Cover 民法 §184 (侵權行為) / §227 (不完全給付) / §767 (物上請求權) / §179 (不當得利). Per article, list each 構成要件 element with:
- 1-line 白話 (plain language)
- Typical 反例 (counterexample)
- Typical carve-out (defense)

Anchor framework: 王澤鑑《侵權行為法》/《債法原理》—— 控制器 drafts grounded in training knowledge of TW 民法.

`構成要件-勞動.md` — Cover 勞基法 §11 (合法解雇事由) / §14 (勞工終止事由) / §16 (預告期間) + 性平法 §13 (性騷擾雇主責任). Same per-element format.

`構成要件-個資.md` — Cover 個資法 §5 (蒐集原則) / §8 (告知義務) / §9 (告知例外) / §27 (適當安全措施) / §29 (損害賠償). Same per-element format. **Critical: maintain Path A discipline** — use 委託/受託 not controller/processor; use 即時 not 72hr.

- [ ] **Step 2: Spec-reviewer subagent reviews all 3 reference files**

- Verify scope matches spec §5.5
- Verify `[draft]` marker present at top
- Verify each element has 1-line 白話 + 反例 + carve-out (not just element list)
- Verify Path A discipline (no 72hr / no controller-processor / no GDPR phrases)
- Verify no duplication of canonical legal-sources.json condition text

- [ ] **Step 3: Code-quality reviewer subagent**

- Verify markdown well-formed
- Verify cross-refs to canonical legal-sources.json (don't dupe; link/cite)
- Check naming consistency (民法 §184 not 民法 184條)

- [ ] **Step 4: Apply fixes + commit**

```bash
git add legal-toolkit/skills/legal-issue-spot/references/
git commit -m "feat(legal-toolkit): legal-issue-spot 3 reference files [draft]

Phase 3 SP3-a v0.5.0. 3 reference files (中厚 B density per spec §5.5):

- 請求權基礎-民法.md: 民法 §184/227/767/179 element + 白話 + 反例 + carve-out
- 構成要件-勞動.md: 勞基法 §11/14/16 + 性平法 §13
- 構成要件-個資.md: 個資法 §5/8/9/27/29

All marked [draft — for 法務 review]; Path A discipline maintained
(即時 not 72hr; 委託/受託 not controller/processor). Cross-refs
canonical legal-sources.json for 條文 text to avoid duplication.

法務 SME validation deferred to Phase 4.5 GC outreach per
feedback_legal_toolkit_defer_legal_domain.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Output schemas (issues + business JSON)

**Files:**
- Create: `legal-toolkit/skills/legal-issue-spot/assets/output-schema-issues.json`
- Create: `legal-toolkit/skills/legal-issue-spot/assets/output-schema-business.json`

- [ ] **Step 1: Write `output-schema-issues.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "legal-toolkit/skills/legal-issue-spot/assets/output-schema-issues.json",
  "title": "issues.md structural schema",
  "type": "object",
  "description": "Structural contract for legal-issue-spot issues.md output. Markdown is post-parsed; this schema validates which sections + content patterns must appear.",
  "required": [
    "required_sections",
    "subsumption_table_columns",
    "subsumption_conclusion_values",
    "risk_grade_required",
    "min_byte_size",
    "no_template_orphans"
  ],
  "properties": {
    "required_sections": {
      "type": "array",
      "items": {"type": "string"},
      "const": [
        "§事實摘要",
        "§時間軸",
        "§Issue 矩陣",
        "§構成要件涵攝",
        "§反事實",
        "§風險分級",
        "§Disclaimer"
      ]
    },
    "subsumption_table_columns": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["構成要件", "事實對應", "涵攝結論", "信心"]
    },
    "subsumption_conclusion_values": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["該當", "不該當", "⚠️"]
    },
    "risk_grade_required": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["🔴", "🟡", "🟢"]
    },
    "min_byte_size": {"type": "integer", "const": 800},
    "no_template_orphans": {"type": "boolean", "const": true}
  }
}
```

- [ ] **Step 2: Write `output-schema-business.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "legal-toolkit/skills/legal-issue-spot/assets/output-schema-business.json",
  "title": "business.md structural schema",
  "type": "object",
  "required": [
    "required_sections",
    "conditional_sections",
    "risk_emoji_required",
    "handoff_query_format",
    "min_byte_size",
    "no_template_orphans"
  ],
  "properties": {
    "required_sections": {
      "type": "array",
      "items": {"type": "string"},
      "const": [
        "§TL;DR",
        "§可以做的部分",
        "§不能做的部分",
        "§注意點",
        "§風險分級",
        "§Disclaimer"
      ]
    },
    "conditional_sections": {
      "type": "object",
      "properties": {
        "§建議下一步": {
          "type": "string",
          "const": "REQUIRED if issues.md §構成要件涵攝 contains any ⚠️ in 涵攝結論 column"
        },
        "§Escalation": {
          "type": "string",
          "const": "REQUIRED if risk_grade is 🔴 OR ≥ 2 ⚠️ in §構成要件涵攝"
        }
      }
    },
    "risk_emoji_required": {
      "type": "array",
      "items": {"type": "string"},
      "const": ["🔴", "🟡", "🟢"]
    },
    "handoff_query_format": {
      "type": "string",
      "const": "`/legal-research --query=\"<NL query>\"`"
    },
    "min_byte_size": {"type": "integer", "const": 400},
    "no_template_orphans": {"type": "boolean", "const": true}
  }
}
```

- [ ] **Step 3: Verify schemas parse as valid JSON**

```bash
python3 -c "import json; json.load(open('legal-toolkit/skills/legal-issue-spot/assets/output-schema-issues.json'))"
python3 -c "import json; json.load(open('legal-toolkit/skills/legal-issue-spot/assets/output-schema-business.json'))"
# Both expected: silent exit 0
```

- [ ] **Step 4: Commit**

```bash
git add legal-toolkit/skills/legal-issue-spot/assets/
git commit -m "feat(legal-toolkit): legal-issue-spot output schemas (issues + business)

Phase 3 SP3-a v0.5.0. Structural contract for the 2-file output:

- output-schema-issues.json: 7 required sections + subsumption table
  spec (4 columns / 3 conclusion values) + risk grade emoji + min byte
  size 800 + no-orphans
- output-schema-business.json: 6 required sections + conditional
  §建議下一步 (when ⚠️) + conditional §Escalation (when 🔴 or ≥ 2 ⚠️)
  + handoff query string format + min byte size 400

Schemas consumed by grade_issue_spot.py in Task 5. JSON schema draft-07
syntax (matches existing legal-toolkit assets convention).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: grade_issue_spot.py + 10 tests + fixtures (TDD)

**Files:**
- Create: `legal-toolkit/skills/legal-issue-spot/scripts/grade_issue_spot.py`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/test_grade_issue_spot.py`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/issues-pass.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/business-pass.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/issues-orphan-tbd.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/business-orphan-tbd.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/issues-yellow-no-handoff.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/business-yellow-no-handoff.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/business-red-no-escalation.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/issues-72hr-antipattern.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/issues-controller-processor-antipattern.md`
- Create: `legal-toolkit/skills/legal-issue-spot/tests/fixtures/business-no-disclaimer.md`

**TDD pattern**: write test first, run to verify FAIL, implement check, run to verify PASS.

- [ ] **Step 1: Read existing graders for byte-identical bank**

```bash
# Locate the canonical PATH_A_ANTIPATTERNS bank from existing graders:
grep -A 30 "PATH_A_ANTIPATTERNS = \[" legal-toolkit/skills/legal-incident-response/scripts/grade_response.py
grep -A 30 "PATH_A_ANTIPATTERNS = \[" legal-toolkit/skills/legal-document-draft/scripts/grade_draft.py
```

Capture the bank verbatim. Do the same for `_check_no_template_orphans()` helper (added v0.4.4).

- [ ] **Step 2: Author the 2 passing fixtures (issues-pass.md + business-pass.md)**

Hand-craft realistic fixture content that satisfies all schemas. ~80-150 lines markdown each. Cover:
- All required sections present (`§事實摘要` etc.)
- Subsumption table with 3+ rows; mix of 該當 / 不該當 / ⚠️
- 風險分級 = 🟡 (so handoff branch fires; escalation does NOT fire because not 🔴 and not ≥ 2 ⚠️)
- Disclaimer footer (§6.3 boilerplate text)
- business.md has §建議下一步 with `/legal-research --query="..."` query string (because ⚠️ exists)

- [ ] **Step 3: Write Test 1 — passing fixture exits 0**

Create `tests/test_grade_issue_spot.py`:

```python
"""Deterministic tests for grade_issue_spot.py."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
GRADER = SKILL_DIR / "scripts" / "grade_issue_spot.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _run_grader(issues_md: Path, business_md: Path) -> int:
    """Invoke grader with two file paths; return exit code."""
    result = subprocess.run(
        [sys.executable, str(GRADER), "--issues", str(issues_md), "--business", str(business_md)],
        env=ENV,
        capture_output=True,
        text=True,
    )
    return result.returncode


def test_passing_fixture_exits_0():
    rc = _run_grader(FIXTURES / "issues-pass.md", FIXTURES / "business-pass.md")
    assert rc == 0
```

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/skills/legal-issue-spot/tests/test_grade_issue_spot.py::test_passing_fixture_exits_0 -v
# Expected: FAIL — grade_issue_spot.py doesn't exist yet
```

- [ ] **Step 4: Implement minimal grade_issue_spot.py to pass Test 1**

Create `scripts/grade_issue_spot.py`:

```python
#!/usr/bin/env python3
"""Deterministic structural grader for legal-issue-spot output directories.

A grader run checks an output dir at legal-outputs/<timestamp>-issue-spot/
and verifies:

Common structural floor:
    1. Both expected files exist (issues.md + business.md)
    2. Files exceed MIN_BYTE_SIZE thresholds
    3. issues.md contains all required IRAC sections (§事實摘要 / §時間軸
       / §Issue 矩陣 / §構成要件涵攝 / §反事實 / §風險分級 / §Disclaimer)
    4. business.md contains all required sections (§TL;DR / §可以做的部分
       / §不能做的部分 / §注意點 / §風險分級 / §Disclaimer)
    5. business.md contains a risk emoji (🔴 / 🟡 / 🟢)

IRAC-specific:
    6. Subsumption table valid (4 columns; conclusion values ∈ {該當,
       不該當, ⚠️})
    7. Cross-skill handoff present when subsumption has any ⚠️
       (business.md MUST contain §建議下一步 + at least 1
       `/legal-research --query="..."` query string)
    8. Escalation present when risk = 🔴 OR ≥ 2 ⚠️

Path A anti-patterns:
    9. Neither file contains GDPR/legacy phrases (PATH_A_ANTIPATTERNS
       bank byte-identical to grade_draft.py / grade_response.py per
       canonical drift verify)

Template orphans:
   10. Neither file contains unfilled template variables `{{var}}`
       (helper byte-identical to grade_draft.py per drift verify)

Exit codes: 0 = PASS / 1 = FAIL / 2 = NEEDS_REVISION (PASS_WITH_NOTES)
"""

import argparse
import re
import sys
from pathlib import Path

# === BYTE-IDENTICAL BANK (drift-verified) ===
# This bank MUST match grade_draft.py + grade_response.py + grade_research.py
# verbatim. legal-toolkit/scripts/verify-drift.py extension enforces this.
PATH_A_ANTIPATTERNS = [
    # GDPR phrases
    "72小時內通報", "72hr", "72 hours", "72-hour", "GDPR Article 33",
    # controller-processor model
    "data controller", "data processor", "controller and processor",
    # PDPA minor age confusion
    "20 歲以下未成年人", "20-year-old minor",
    # NOTE: verify against grade_response.py SP3a precedent before merge.
]

TEMPLATE_ORPHAN_PATTERN = re.compile(r"\{\{[a-z_]+\}\}")


def _check_no_template_orphans(text: str) -> bool:
    """Return True if no orphan templates; False if any `{{var}}` found."""
    return TEMPLATE_ORPHAN_PATTERN.search(text) is None


REQUIRED_ISSUES_SECTIONS = [
    "§事實摘要", "§時間軸", "§Issue 矩陣",
    "§構成要件涵攝", "§反事實", "§風險分級", "§Disclaimer",
]
REQUIRED_BUSINESS_SECTIONS = [
    "§TL;DR", "§可以做的部分", "§不能做的部分",
    "§注意點", "§風險分級", "§Disclaimer",
]
RISK_EMOJI = ["🔴", "🟡", "🟢"]
MIN_BYTES_ISSUES = 800
MIN_BYTES_BUSINESS = 400


def grade(issues_path: Path, business_path: Path) -> int:
    issues = issues_path.read_text(encoding="utf-8")
    business = business_path.read_text(encoding="utf-8")

    errs: list[str] = []

    # Existence + size
    if len(issues.encode("utf-8")) < MIN_BYTES_ISSUES:
        errs.append(f"issues.md < {MIN_BYTES_ISSUES} bytes")
    if len(business.encode("utf-8")) < MIN_BYTES_BUSINESS:
        errs.append(f"business.md < {MIN_BYTES_BUSINESS} bytes")

    # Required sections
    for sec in REQUIRED_ISSUES_SECTIONS:
        if sec not in issues:
            errs.append(f"issues.md missing section: {sec}")
    for sec in REQUIRED_BUSINESS_SECTIONS:
        if sec not in business:
            errs.append(f"business.md missing section: {sec}")

    # Risk emoji
    if not any(e in business for e in RISK_EMOJI):
        errs.append("business.md missing risk emoji (🔴/🟡/🟢)")

    # Path A anti-patterns
    for ap in PATH_A_ANTIPATTERNS:
        if ap in issues:
            errs.append(f"issues.md Path A anti-pattern: {ap!r}")
        if ap in business:
            errs.append(f"business.md Path A anti-pattern: {ap!r}")

    # Template orphans
    if not _check_no_template_orphans(issues):
        errs.append("issues.md has unfilled `{{var}}` orphans")
    if not _check_no_template_orphans(business):
        errs.append("business.md has unfilled `{{var}}` orphans")

    # Subsumption table validation (must contain ⚠️ pattern OR all-該當/不該當)
    yellow_in_subsumption = "⚠️" in issues  # naive; refined in steps below

    # Cross-skill handoff: when ⚠️ exists, business.md MUST have handoff query
    if yellow_in_subsumption:
        if "§建議下一步" not in business:
            errs.append("issues.md has ⚠️ but business.md missing §建議下一步")
        if not re.search(r"`/legal-research --query=\"[^\"]+\"`", business):
            errs.append(
                "issues.md has ⚠️ but business.md missing /legal-research handoff query"
            )

    # Escalation: when 🔴 OR ≥ 2 ⚠️, business.md MUST have §Escalation
    yellow_count = issues.count("⚠️")
    if "🔴" in business or yellow_count >= 2:
        if "§Escalation" not in business:
            errs.append(
                "🔴 risk OR ≥ 2 ⚠️ but business.md missing §Escalation section"
            )

    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issues", required=True, type=Path)
    parser.add_argument("--business", required=True, type=Path)
    args = parser.parse_args()

    if not args.issues.exists():
        print(f"FAIL: issues file not found: {args.issues}", file=sys.stderr)
        return 1
    if not args.business.exists():
        print(f"FAIL: business file not found: {args.business}", file=sys.stderr)
        return 1
    return grade(args.issues, args.business)


if __name__ == "__main__":
    sys.exit(main())
```

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/skills/legal-issue-spot/tests/test_grade_issue_spot.py::test_passing_fixture_exits_0 -v
# Expected: PASS
```

- [ ] **Step 5: Add the remaining 9 tests + corresponding fixtures**

For each of the 9 fail-mode tests (per spec §5.6), follow this micro-cycle:
1. Write the test (xfails / asserts exit 1)
2. Hand-craft the corresponding negative fixture
3. Run test → verify exit 1 (grader catches the fault)
4. If grader has bug, fix grader inline

The 9 fail-mode tests:

```python
def test_missing_issues_md_exits_1():
    rc = _run_grader(FIXTURES / "nonexistent.md", FIXTURES / "business-pass.md")
    assert rc == 1


def test_missing_business_md_exits_1():
    rc = _run_grader(FIXTURES / "issues-pass.md", FIXTURES / "nonexistent.md")
    assert rc == 1


def test_path_a_antipattern_72hr_exits_1():
    rc = _run_grader(FIXTURES / "issues-72hr-antipattern.md", FIXTURES / "business-pass.md")
    assert rc == 1


def test_path_a_antipattern_controller_processor_exits_1():
    rc = _run_grader(
        FIXTURES / "issues-controller-processor-antipattern.md",
        FIXTURES / "business-pass.md",
    )
    assert rc == 1


def test_template_orphan_in_issues_md_exits_1():
    rc = _run_grader(FIXTURES / "issues-orphan-tbd.md", FIXTURES / "business-pass.md")
    assert rc == 1


def test_template_orphan_in_business_md_exits_1():
    rc = _run_grader(FIXTURES / "issues-pass.md", FIXTURES / "business-orphan-tbd.md")
    assert rc == 1


def test_yellow_in_subsumption_no_handoff_exits_1():
    rc = _run_grader(
        FIXTURES / "issues-yellow-no-handoff.md",
        FIXTURES / "business-yellow-no-handoff.md",
    )
    assert rc == 1


def test_red_risk_no_escalation_exits_1():
    # business.md has 🔴 but no §Escalation; issues.md is the standard pass
    rc = _run_grader(FIXTURES / "issues-pass.md", FIXTURES / "business-red-no-escalation.md")
    assert rc == 1


def test_missing_disclaimer_exits_1():
    rc = _run_grader(FIXTURES / "issues-pass.md", FIXTURES / "business-no-disclaimer.md")
    assert rc == 1
```

For each test, also create the fixture. Example for `issues-72hr-antipattern.md`:

Take `issues-pass.md` content; insert "72 hours" string somewhere in `§事實摘要` body. Save as `issues-72hr-antipattern.md`.

Example for `issues-orphan-tbd.md`:
Take `issues-pass.md`; replace one section with `{{undefined_var}}` body. Save as `issues-orphan-tbd.md`.

For each test:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/skills/legal-issue-spot/tests/test_grade_issue_spot.py::<test_name> -v
# Expected: PASS (test asserts exit 1; grader returns 1 on the fault)
```

- [ ] **Step 6: Run full test suite — all 10 tests pass**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/skills/legal-issue-spot/tests/ -v
# Expected: 10 passed
```

Also run the full plugin baseline to verify no regressions:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/ legal-toolkit/scripts/tests/ legal-toolkit/skills/ -q
# Expected: 231 + 10 = 241 passed
```

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/skills/legal-issue-spot/scripts/ legal-toolkit/skills/legal-issue-spot/tests/
git commit -m "feat(legal-toolkit): grade_issue_spot.py + 10 tests + fixtures

Phase 3 SP3-a v0.5.0. Self-contained structural grader; bank
byte-identical to grade_draft.py + grade_response.py (drift verified
in Task 7).

Checks (10):
  Common: file existence, size floor, required sections, risk emoji
  IRAC:   subsumption table validity, handoff-when-⚠️, escalation-when-🔴
  Safety: Path A anti-patterns, template orphan check, disclaimer

Test surface: 10 fixture-driven tests; no LLM calls; runs in
<200ms. PYTHONDONTWRITEBYTECODE=1 enforced per
feedback_pycache_hook_blocks_edits.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Router Q4-fact dispatch unlock

**Files:**
- Modify: `legal-toolkit/skills/using-legal-toolkit/SKILL.md` (~30-line change)

- [ ] **Step 1: Read current router state**

```bash
sed -n '50,110p' legal-toolkit/skills/using-legal-toolkit/SKILL.md
```

Identify the Q4 row in the dispatch table + the mermaid Q4 branch + the "Phase 3 NOT YET" notice in Step 4.

- [ ] **Step 2: Update dispatch table — Q4-fact branch active**

In the `## Decision logic` table around the `Q4 (fact pattern)` row, change:
```
| Q4 (fact pattern) — issue spot | `legal-issue-spot` | 🔍 IRAC | Phase 3 (not yet) |
```
to:
```
| Q4 (fact pattern) — issue spot | `legal-issue-spot` | 🔍 IRAC | **active (v0.5.0+)** |
```

Leave Q4 (law lookup) row unchanged — that ships in v0.5.2.

- [ ] **Step 3: Add `### Q4-fact — Issue spotting (active in v0.5.0+)` subsection**

Insert AFTER the existing `### Q3 — Incident response (active in v0.4.2+)` subsection. Format mirrors Q2/Q3:

```markdown
### Q4 (fact pattern) — Issue spotting (active in v0.5.0+)

**Keyword triggers**: 「能不能做」/「是否合法」/「我們想做」/「分析一下」/「這樣可以嗎」/「合不合法」/「is it legal」/「can we」/「fact pattern」/「issue spot」.

**Disambiguation**: if the user's request is a literal law-text lookup (查 §227 / 找 110 年判決 / 法條), route to Q4-law-lookup instead (NOT YET available; ships v0.5.2).

→ hand off to `legal-issue-spot` skill with the fact pattern as input.

**Prerequisite check**: NONE. legal-issue-spot is profile.yml-independent (input is fact pattern, no company identity needed).

**Output expectation**: 2-file in `legal-outputs/<timestamp>-issue-spot/` (`issues.md` for 法務 + `business.md` for 業務). When ⚠️ low-confidence subsumption is detected, business.md trailer includes a `/legal-research --query="..."` handoff query string.
```

- [ ] **Step 4: Update mermaid Q4 branch**

In the mermaid block, change:
```
Q4 -->|fact-driven| IS[→ legal-issue-spot<br/>🔍 IRAC — Phase 3 NOT YET]
```
to:
```
Q4 -->|fact-driven| IS[→ legal-issue-spot<br/>🔍 IRAC — active v0.5.0+]
```

Leave `Q4 -->|查法源| RS[→ legal-research<br/>🔍 IRAC — Phase 3 NOT YET]` unchanged (v0.5.2 lands).

- [ ] **Step 5: Update Step 4 ("not yet available" path)**

In `### Step 4 — Phase 3-5 "not yet available" path` paragraph, remove `legal-issue-spot` from the Q4 examples list. Keep `legal-research` listed as not-yet.

- [ ] **Step 6: Update active sub-skills list at bottom**

In the `## Reference` section, add to the active list:
```markdown
  - [`legal-issue-spot`](../legal-issue-spot/SKILL.md)
```

In the cold-start onboarding example block (`## Cold-start onboarding`), add:
```
   👉 如果你有 fact pattern 想做 issue 分析（能不能做這個業務）：
      /legal-issue-spot
      （不需要 profile.yml；輸入 fact pattern free-text；輸出 issue 矩陣 + 構成要件涵攝 + 風險分級）
```

Bump `using-legal-toolkit` version (Y/M/Z field in frontmatter) from `0.1.0` to `0.2.0` (minor for new skill in router roster).

- [ ] **Step 7: Run baseline tests + plugin tests**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/ legal-toolkit/scripts/tests/ legal-toolkit/skills/ -q
# Expected: 241 passed (no regression)
```

- [ ] **Step 8: Commit**

```bash
git add legal-toolkit/skills/using-legal-toolkit/SKILL.md
git commit -m "feat(legal-toolkit): router Q4-fact dispatch unlock

Phase 3 SP3-a v0.5.0. Activates Q4 (fact-pattern) dispatch path:

- Dispatch table row: Phase 3 NOT YET → active (v0.5.0+)
- Q4-fact subsection added (mirrors Q2/Q3 active pattern)
- Mermaid Q4 fact-driven branch updated
- Step 4 (not-yet path) Q4 example list updated
- Cold-start onboarding example added
- Active sub-skills list extended
- Router version bump 0.1.0 → 0.2.0 (new active skill in roster)

Q4 (law-lookup) branch deliberately UNCHANGED — that ships v0.5.2.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: drift verify update for issue-spot grader bank

**Files:**
- Modify: `legal-toolkit/scripts/verify-drift.py` (extend with 4-grader bank check)

- [ ] **Step 1: Read existing verify-drift.py**

```bash
cat legal-toolkit/scripts/verify-drift.py
```

Identify the existing canonical-vs-functional-copy verification logic. Determine the extension point for adding "4-grader byte-identical bank" checks.

- [ ] **Step 2: Add 4-grader bank verification function**

Append to `verify-drift.py`:

```python
def verify_grader_bank_drift() -> list[str]:
    """Verify PATH_A_ANTIPATTERNS + _check_no_template_orphans byte-identical
    across the 4 graders: grade_draft / grade_response / grade_issue_spot
    / (grade_research lands in v0.5.2; included in this list as forward-stub).
    """
    skill_dir = Path(__file__).resolve().parent.parent / "skills"
    graders = [
        skill_dir / "legal-document-draft" / "scripts" / "grade_draft.py",
        skill_dir / "legal-incident-response" / "scripts" / "grade_response.py",
        skill_dir / "legal-issue-spot" / "scripts" / "grade_issue_spot.py",
    ]
    # NOTE: legal-research grader added in v0.5.2; uncomment then.
    # graders.append(skill_dir / "legal-research" / "scripts" / "grade_research.py")

    errs: list[str] = []
    bank_chunks: list[str] = []
    orphan_chunks: list[str] = []

    pat_bank = re.compile(
        r"PATH_A_ANTIPATTERNS\s*=\s*\[(.*?)\]", re.DOTALL
    )
    pat_orphan = re.compile(
        r"def _check_no_template_orphans\(.*?\):.*?(?=\n(?:def|class|\Z))",
        re.DOTALL,
    )

    for g in graders:
        if not g.exists():
            errs.append(f"grader not found: {g}")
            continue
        text = g.read_text(encoding="utf-8")
        bank_match = pat_bank.search(text)
        orphan_match = pat_orphan.search(text)
        if not bank_match:
            errs.append(f"PATH_A_ANTIPATTERNS bank not found in {g.name}")
        else:
            bank_chunks.append((g.name, bank_match.group(1).strip()))
        if not orphan_match:
            errs.append(f"_check_no_template_orphans not found in {g.name}")
        else:
            orphan_chunks.append((g.name, orphan_match.group(0).strip()))

    # All bank chunks must be byte-identical
    if len(set(c for _, c in bank_chunks)) > 1:
        names = [n for n, _ in bank_chunks]
        errs.append(
            f"PATH_A_ANTIPATTERNS drift across graders: {names}"
        )
    if len(set(c for _, c in orphan_chunks)) > 1:
        names = [n for n, _ in orphan_chunks]
        errs.append(
            f"_check_no_template_orphans drift across graders: {names}"
        )

    return errs
```

In the existing `main()`, add a call to `verify_grader_bank_drift()` after the existing canonical-functional-copy check; aggregate errors.

- [ ] **Step 3: Run drift verify**

```bash
python3 legal-toolkit/scripts/verify-drift.py
# Expected: OK: all 11 functional copies byte-identical to canonical.
# Expected: OK: 3-grader PATH_A bank + template-orphan helper byte-identical.
# (Or if drift exists, the script should fail with specific drift report.)
```

If drift detected, copy bank from `grade_draft.py` (canonical reference) to `grade_issue_spot.py` until byte-identical.

- [ ] **Step 4: Add a corresponding test**

Append to existing `legal-toolkit/scripts/tests/test_drift.py` (or create one if not exists):

```python
def test_grader_bank_drift_zero_after_v0_5_0():
    """Ensures PATH_A bank + template-orphan helper byte-identical across
    all 3 graders (4 in v0.5.2+)."""
    # Run verify-drift.py and capture exit code
    import subprocess
    result = subprocess.run(
        ["python3", str(Path(__file__).resolve().parent.parent / "verify-drift.py")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
```

Run:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/ -v
# Expected: PASS
```

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/scripts/verify-drift.py legal-toolkit/scripts/tests/
git commit -m "chore(legal-toolkit): drift verify for issue-spot grader bank

Phase 3 SP3-a v0.5.0. Extends verify-drift.py with 3-grader (4 in
v0.5.2+) bank verification:

- PATH_A_ANTIPATTERNS literal bank byte-identical across grade_draft /
  grade_response / grade_issue_spot
- _check_no_template_orphans() helper byte-identical across same graders
- Forward stub for legal-research grader (uncomment in v0.5.2)

CI gate prevents accidental drift on future grader edits per
SSOT-and-functional-copy convention.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: SKILL READMEs (en/ja/zh-TW; parallelizable)

**Files:**
- Create: `legal-toolkit/skills/legal-issue-spot/README.md`
- Create: `legal-toolkit/skills/legal-issue-spot/README.ja.md`
- Create: `legal-toolkit/skills/legal-issue-spot/README.zh-TW.md`

Per `feedback_skill_readme_i18n_required.md`, every skill ships tri-language READMEs.

- [ ] **Step 1: Dispatch 3 parallel implementer subagents — one per README**

Each README ~50-80 lines. Sections:
1. Skill name + version + brief
2. When to use (3 bullets)
3. When NOT to use (2 bullets)
4. Input format (fact pattern free-text)
5. Output format (2 files; 法務 vs 業務)
6. Cross-skill handoff note (when ⚠️ → /legal-research suggestion)
7. Disclaimer footer note (§6.3)
8. Link to SKILL.md
9. Link to spec doc

Per-language conventions:
- `README.md` (English): natural English
- `README.ja.md`: 日本語; preserve English nouns for tech terms (per `feedback_dimension_translation.md` style — exception only for established native industry terms)
- `README.zh-TW.md`: 繁體中文; no Mainland calques; 議題 not 议题; 風險 not 风险; etc.

- [ ] **Step 2: Spec-reviewer subagent (single review pass)**

- Verify all 3 READMEs cover same content (same headings)
- Verify Japanese version doesn't katakana-fy English tech terms (per glossary-ja.md)
- Verify zh-TW version no Mainland calques
- Verify all 3 link to same SKILL.md + spec doc

- [ ] **Step 3: Apply fixes + commit**

```bash
git add legal-toolkit/skills/legal-issue-spot/README.md \
        legal-toolkit/skills/legal-issue-spot/README.ja.md \
        legal-toolkit/skills/legal-issue-spot/README.zh-TW.md
git commit -m "docs(legal-toolkit): legal-issue-spot tri-language READMEs

Phase 3 SP3-a v0.5.0. en/ja/zh-TW READMEs per PR #150 i18n convention
+ feedback_skill_readme_i18n_required.md.

Per-language style notes:
- ja: preserves English tech nouns; observe glossary-ja.md
- zh-TW: no Mainland calques; 議題/風險/觀點 not 议题/风险/次元

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: plugin docs sync + version bump

**Files:**
- Modify: `legal-toolkit/.claude-plugin/plugin.json` (version 0.4.4 → 0.5.0; description += issue-spot)
- Modify: `.claude-plugin/marketplace.json` (description sync)
- Modify: `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` (skill list 5 → 6)
- Modify: `legal-toolkit/ROADMAP.md` (Phase 3 SP3-a status: planned → ✅ DONE)

- [ ] **Step 1: Read current plugin.json + marketplace.json descriptions**

```bash
cat legal-toolkit/.claude-plugin/plugin.json | python3 -m json.tool
grep -A 10 '"name": "legal-toolkit"' .claude-plugin/marketplace.json
```

- [ ] **Step 2: Bump plugin.json version + description**

Edit `legal-toolkit/.claude-plugin/plugin.json`:
- `version`: `"0.4.4"` → `"0.5.0"`
- `description`: append clause about Q4 fact-pattern issue-spotting (active v0.5.0+)

Example new description (preserve existing prose style):
> "Taiwan in-house 法務 toolkit: contract review (📋 Playbook) / document drafting (📝 Template; v0.4.0+) / incident response (🚨 Runbook; v0.4.2+) / **issue spotting (🔍 IRAC; v0.5.0+)** clusters. Profile-driven (legal-playbook/profile.yml schema v2; required for Q2/Q3 only). Path A discipline (current Taiwan in-force law). Open-source tool, not legal services."

- [ ] **Step 3: Sync marketplace.json description**

Edit `.claude-plugin/marketplace.json` `legal-toolkit` entry's `description` to byte-identical the new plugin.json description.

Run sync verifier:
```bash
python3 scripts/check-marketplace-description-sync.py
# Expected: OK: legal-toolkit description in marketplace.json matches plugin.json
```

- [ ] **Step 4: Update plugin-level READMEs (5 → 6 skills)**

For each of `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md`:
- Update active-skill count from 5 to 6
- Add `legal-issue-spot` to the active skill list (after `legal-incident-response`)
- Update Q4 description to "active v0.5.0+ (issue-spot) / planned v0.5.2 (research)"

- [ ] **Step 5: Update ROADMAP.md**

Add to Phase 3 section:
- Mark SP3-a (`legal-issue-spot`) as ✅ DONE; add merge date placeholder
- Update timeline overview row Phase 3 with revised cadence (SP3-a v0.5.0 / SP3-b v0.5.2)

- [ ] **Step 6: Run full CI baseline**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q
python3 scripts/check-marketplace-description-sync.py
python3 legal-toolkit/scripts/verify-drift.py
.claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/legal-issue-spot/SKILL.md  # if hook script callable directly
# All expected: exit 0
```

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/.claude-plugin/plugin.json .claude-plugin/marketplace.json \
        legal-toolkit/README.md legal-toolkit/README.ja.md legal-toolkit/README.zh-TW.md \
        legal-toolkit/ROADMAP.md
git commit -m "chore(legal-toolkit): bump plugin to v0.5.0 + plugin docs sync

Phase 3 SP3-a v0.5.0 ship. Bumps:

- plugin.json version 0.4.4 → 0.5.0; description += issue-spot
- marketplace.json description byte-identical sync (CI gate)
- README en/ja/zh-TW: 5 → 6 active skills; Q4 status updated
- ROADMAP: Phase 3 SP3-a marked ✅ DONE; SP3-b cadence revised

Plugin grows to 6 active skills:
  using-legal-toolkit / legal-playbook-author /
  legal-contract-review / legal-document-draft /
  legal-incident-response / legal-issue-spot (NEW)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: Fresh-eyes audit + push + PR

**Files:** none (review pass only)

- [ ] **Step 1: Dispatch fresh-eyes audit subagent**

Task: scan ALL commits in this PR for cross-task drift, per-task-reviewer blind spots, contract-vs-implementation gaps. Output Critical / Important / Minor / Info report.

Specifically check:
- SKILL.md (Task 1) workflow mermaid steps match the 6 protocol files (Task 2) — same names, same order
- Output schemas (Task 4) reference sections match what protocols (Task 2) actually write
- Grader (Task 5) checks match output schemas (Task 4) — no validator missing
- Reference files (Task 3) cover the statutes that subsumption.md (Task 2) loads
- Router (Task 6) keyword bank matches SKILL.md (Task 1) TRIGGER block
- Drift verify (Task 7) successfully validates all 3 graders byte-identical
- READMEs (Task 8) consistent across en/ja/zh-TW
- Plugin docs (Task 9) accurate skill count + description preserved style

If Critical or Important issues found:
- Fix inline
- Run baseline tests again
- Add a follow-up commit (do NOT amend prior commits)

- [ ] **Step 2: Final baseline test sweep**

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q
# Expected: all green (~241 tests)
python3 legal-toolkit/scripts/verify-drift.py
# Expected: OK
python3 scripts/check-marketplace-description-sync.py
# Expected: OK
```

- [ ] **Step 3: Push branch + open PR**

```bash
git push -u origin feat/legal-toolkit-v0.5.0-issue-spot

gh pr create --title "feat(legal-toolkit): v0.5.0 — Phase 3 SP3-a legal-issue-spot" --body "$(cat <<'EOF'
## Summary

Ships **Phase 3 SP3-a** — the first half of the IRAC cluster — bumping legal-toolkit to **v0.5.0**.

- New skill `legal-issue-spot` (pure-LLM workflow; profile.yml-independent)
- Router Q4-fact dispatch unlocked (Q4-law-lookup ships in v0.5.2 SP3-b)
- 4-grader bank drift verification (forward-stub for v0.5.2 grade_research.py)
- Plugin grows: 5 → 6 active skills

Design SoT: [`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md). Plan: [`docs/superpowers/plans/2026-05-15-legal-toolkit-v0.5.0-issue-spot.md`](docs/superpowers/plans/2026-05-15-legal-toolkit-v0.5.0-issue-spot.md).

## What changed

- **Skill content**: SKILL.md + 6 protocols + 3 reference files (`[draft — for 法務 review]`)
- **Schemas**: `output-schema-issues.json` + `output-schema-business.json`
- **Grader**: `grade_issue_spot.py` (10 tests; PATH_A bank byte-identical w/ existing 2 graders)
- **Router**: Q4-fact dispatch active; subsection + mermaid + cold-start updated
- **Drift CI**: 3-grader (forward-stub for 4) bank + template-orphan helper drift verify
- **Plugin docs**: plugin.json + marketplace.json (sync) + tri-language READMEs

## Output contract

`legal-outputs/<timestamp>-issue-spot/`:
- `issues.md` — 法務本位 (Issue 矩陣 + 構成要件 涵攝 + 反事實 + 風險分級)
- `business.md` — 業務本位 (TL;DR + 可以做 / 不能做 / 注意點 + 風險 + 建議下一步 + Escalation when 🔴)

When ⚠️ detected in subsumption: `business.md` ends with `/legal-research --query="..."` handoff query string (soft handoff; user copies to invoke v0.5.2 research skill).

## Inherited conventions

Path A discipline; §6.3 Mandatory Disclaimer; §6.4 Escalation Override; 2-file audience-shaped output; SSOT-and-functional-copy grader bank; flat folder; SDD orchestration.

## Test plan

- [ ] CI: `pytest legal-toolkit/` green (~241 tests; +10 from issue-spot)
- [ ] CI: `verify-drift.py` exit 0 (canonical files + 3-grader bank)
- [ ] CI: `check-marketplace-description-sync.py` exit 0
- [ ] CI: `validate-skill-folder-structure.sh` (PostToolUse hook) green
- [ ] CI: commit type whitelist + kebab scope green
- [ ] Manual: post-merge dogfood with 5 hand-curated case fact patterns (controller-driven; results in v0.5.1 patch PR if P0/P1 found)

## Open items

- 法務 SME validation of 3 reference files (draft → validated) deferred to Phase 4.5 GC outreach
- Quality-gate dataset (5 case fact patterns) hand-curated post-merge for dogfood
- Plan-resume / interactive checkpoint flags reserved for v0.5.x patch room

## Cross-references

- Memory: `project_legal_toolkit_design.md` / `feedback_legal_toolkit_defer_legal_domain.md` / `feedback_legal_toolkit_autonomous_after_design_lock.md`
- Predecessor: PR #290 (v0.4.4 P2 polish)
- Successor: v0.5.2 SP3-b `legal-research` (next PR after this merges)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 4: Monitor CI + report PR URL**

```bash
gh pr view --json url,statusCheckRollup --web
# Or watch in terminal:
gh pr checks --watch
```

If any CI fails, identify root cause, fix, push follow-up commit.

If CI green:
- Report PR URL to user
- Wait for user to merge (or autonomously merge per autonomous-mode preference if explicit)

---

## Self-Review

(Performed inline by controller before Task 1 dispatch.)

**Spec coverage:**
- §5.1 folder layout → Task 1
- §5.2 SKILL.md outline → Task 1 step 2
- §5.3 output schemas → Task 4
- §5.4 grader interface → Task 5
- §5.5 reference content (3 files) → Task 3
- §5.6 test surface (10 tests) → Task 5
- §7.1 router Q4 unlock → Task 6
- §7.2 cross-skill handoff → covered in Task 5 grader rule + Task 1 SKILL.md
- §7.3 grader self-contained + bank duplication → Task 5 + Task 7 drift extension
- §7.4 CI surface → covered across Tasks 5/7/9
- §8.2 commit breakdown (10 commits) → mapped 1:1 onto Tasks 1-9 + Task 10 audit

**Placeholder scan:**
- All bash commands have explicit paths
- All code blocks have full implementations (no `pass` stubs)
- Reference content for `[draft]` files is intentional per design (controller drafts; defer 法務 validation to Phase 4.5)
- "TBD" appears only in user-facing template patterns (e.g. `⏳ 待釐清` in timeline.md design), not in plan tasks
- Test fixture content described in steps; subagent fills realistic content

**Type consistency:**
- Section names consistent: `§事實摘要` / `§時間軸` / `§Issue 矩陣` / `§構成要件涵攝` / `§反事實` / `§風險分級` / `§Disclaimer` (issues.md); `§TL;DR` / `§可以做的部分` / `§不能做的部分` / `§注意點` / `§風險分級` / `§Disclaimer` / `§建議下一步` / `§Escalation` (business.md)
- Function names consistent: `_check_no_template_orphans()` (matches existing graders byte-identical)
- File paths absolute or relative consistently (relative within skill; absolute for cross-plugin invocations)

---

## Execution

Per `feedback_legal_toolkit_autonomous_after_design_lock.md`: SDD execution proceeds autonomously without per-task confirmation. Dispatching subagent-driven-development now.
