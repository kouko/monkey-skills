---
title: wiki-ingest ref page — TL;DR list format + Detailed Extract — design
date: 2026-05-20
status: design-approved
target_skill: obsidian/skills/wiki-ingest (canonical owner of ref page format)
target_branch: feat/wiki-ingest-ref-page-tldr-detailed-extract
upstream_request: user complaint "## Source Excerpt / TL;DR 段落太簡單，流失很多資訊；格式不好閱讀"
brainstorming_skill: code-toolkit:brainstorming v0.9.0
predecessor: v3.13.0 (PR #319, wiki-query Path 2 Tier 1 frontmatter script)
target_version: v3.14.0
---

# wiki-ingest ref page — TL;DR list format + Detailed Extract — design

接續 v3.13.0。本次改造 **ref page body 結構**：把現行 prose 風的 `## Source Excerpt / TL;DR` 改成 bullet list 形式並重命名 `## TL;DR`；新增 `## Detailed Extract` (MAY) 接住現行 2-4 句壓縮無法承載的深資訊。Spec 從 3 必填 body section 變 3 必填 + 1 可選。

## Problem

`wiki/references/*.md` 頁的 `## Source Excerpt / TL;DR` 用 "2-4 sentence neutral description" 規範。實務上：
- **資訊嚴重流失**：把一個 30 分鐘 video / 50 頁 paper / 一本書 壓縮到 2-4 句 = ~99% 損失。Re-ingest 不 recover lost info（一擊深度決定永久深度）；source file 若被刪 / link rot → ref page 是唯一 durable 記錄。
- **格式不好讀**：當 LLM 自由心證寫成密集 prose with ad-hoc `**bold**` + `;` 分隔（如 vault 中 `_2025-09-07-little-wolf-fundednext...` 頁的 300 字密集中文），瀏覽負擔高。短頁則太薄（如 `2018-08-30-...-shinola-audio.md` 只 3 句）。
- **下游消費受限**：wiki-query Tier 2 讀整 body — TL;DR 厚度直接決定深問題答得多深；wiki-cross-linker 從 body 偵測 mentions — 薄 body 少 link opportunity。

JTBD（Klement format）：
> *When* I read a wiki ref page directly OR via wiki-query Tier 2,
> *I want* a browseable list-format quick scan + structured deep extract per source,
> *so I can* recover meaningful detail (claims / examples / quotes) without re-watching the video / re-reading the article.

## Users

kouko（vault 已 468 ref pages，混合 source types: YouTube / article / book / forum；日常 zh-TW reader）+ 其他多 source-type vault 使用者。設計目標：list 格式browseable + 結構化 deep extract 可承載差異化 source。

## Smallest End State

MVP = **2 個 spec 改造** + version bump：
- `## Source Excerpt / TL;DR` (prose 2-4 句) → `## TL;DR` (free-form 3-7 bullets, sentence-fragment style)
- 新增 `## Detailed Extract` MAY section（free-form sub-headings, source-proportional length）
- Body section order: Source → TL;DR → Detailed Extract → Key Contributions
- 既有 468 頁不動（natural drift on source modify）；`/wiki-relang` → Phase 2 future PR

## Current State Evidence

- **Forward**: `obsidian/skills/wiki-ingest/SKILL.md` STEP 4d — in-flight template for ref page generation
- **Reverse**: `obsidian/skills/wiki-ingest/references/page-format.md:45-87` — canonical spec for ref page body structure (3 sections: Source / Source Excerpt / Key Contributions)
- **Error**: 實際輸出 inconsistency — `~/kouko-obsidian-vault/wiki/references/2018-08-30-industrial-design-shinola-audio.md` (3 sentences, 太薄) vs `_2025-09-07-little-wolf-fundednext-futures-prop-firm.md` (300 字密集中文 with ad-hoc markup, 偏離 spec). LLM 自由心證 → spec 寫 "2-4 sentence" 但 implementations 變動大。
- **Data**: 8-field frontmatter (`title` / `type=wiki-reference` / `source_path` / `date` / `ingested` / `contributes_to` / `tags` / `summary`) + 3 required body sections — schema 不動。
- **Boundary**: wiki-query Tier 2 (整 body 讀；依賴 TL;DR + Detailed Extract 厚度回答深問題); wiki-cross-linker (body 偵測 mentions); wiki-lint L14 (only `## Source` wikilink format enforced; no check on `## Source Excerpt / TL;DR` heading text → rename safe).

Evidence paths appendix：
- `obsidian/skills/wiki-ingest/SKILL.md`（STEP 4d block）
- `obsidian/skills/wiki-ingest/references/page-format.md`（canonical §Reference page body structure）
- `obsidian/skills/wiki-lint/references/lint-checks.md`（L14 enforced; L01/L07/L08 unrelated）
- `~/kouko-obsidian-vault/wiki/references/`（468 existing ref pages — 2 sampled for inconsistency evidence）

## Decision

### §1 Scope (MVP)

**In**:
- Section rename: `## Source Excerpt / TL;DR` → `## TL;DR`
- Section format change: prose 2-4 sentences → free-form 3-7 bullets, sentence-fragment style
- New section: `## Detailed Extract` (MAY / advisory; LLM judges per-source whether to include)
- Section order: `## Source` → `## TL;DR` → `## Detailed Extract` (if present) → `## Key Contributions`
- Update both `wiki-ingest/SKILL.md` STEP 4d template + `wiki-ingest/references/page-format.md` §Reference page body structure (consistent across in-flight + canonical spec, per v3.12.0 pattern)
- Version bump v3.13.0 → v3.14.0

**Out** → Phase 2 future PR:
- `/wiki-relang`-style bulk re-extract command for 468 existing pages
- wiki-lint L15 enforcement on `## TL;DR` section presence / list format / sub-heading vocabulary
- Frontmatter `source_type: video|article|paper|book|forum|other` for source-type-specific template hints
- `## Detailed Extract` MUST severity upgrade (after dogfood shows MAY is too permissive)
- Density-floor lint (LLM-judges-LLM = recursive concern; revisit if dogfood demands)

**Migration**: Natural drift only — 468 existing pages stay as legacy `## Source Excerpt / TL;DR` (prose) until source modifies → re-ingest with new spec. Matches v3.10.0 / v3.11.0 / v3.12.0 migration pattern.

### §2 `## TL;DR` new format

**Length**: 3-7 bullets. Source thickness drives count:
- Thin source (3-min cat video, 1-page forum post): 3 bullets
- Medium source (10-min explainer, 5-page blog article): 4-5 bullets
- Substantive source (long video, paper, chapter): 6-7 bullets

**Bullet shape**: sentence fragments OR short sentences. Avoid full multi-clause prose. Browseable scan-friendly.

**Content per bullet**: any of {主題 / 主張 / 範例 / context / 來源頻道脈絡 / 注意事項}. LLM picks per source what's most informative.

**No nested sub-bullets** (keep TL;DR shallow; nesting goes in Detailed Extract).

**Example** (FundedNext Futures 4m21s video):
```markdown
## TL;DR

- 主題：Prop Firm (自營交易公司, Proprietary Trading Firm) 攻略入門
- 評測對象：FundedNext Futures — 期貨自營交易公司
- 涵蓋面：交易帳戶評估 / 提領限制 / 風險管理 / 客戶服務品質
- 格式：短片快速教學 (4m21s)
- 頻道脈絡：Little Wolf channel 的「Prop Firm」議題首見 (從美股技術分析向自營交易實務拓展)
```

**Example** (Shinola industrial design analysis):
```markdown
## TL;DR

- John Mauriello (CCA adjunct, Design-Theory channel) 解構 Shinola × Astro Studios Canfield headphones
- 核心主張：design is a language — 厚重 joint 結構 + 皮革金屬材質 + 拋光鉻 + 外露縫線 → encode "Detroit American craftsmanship" 定位
- 方法論：three-pass reading (silhouette/proportion → materials/contrast → manufacturing traces)
- 場景：CCA design theory 課堂 deconstruction 練習
```

### §3 `## Detailed Extract` new section

**Severity**: MAY (advisory / strongly encouraged when source has substance worth preserving).

**LLM judgment**: include when source has meaningful detail beyond what TL;DR captures (chapter-level structure, verbatim quotes, methodology, examples). Skip when source is thin (cat video, single forum post).

**Sub-heading vocabulary** (suggested, not enforced; LLM picks 2-4 per source):
- `### Key Claims` — concrete assertions made by source
- `### Examples / Cases` — illustrative case studies or worked examples
- `### Notable Quotes` — verbatim excerpts (with `^[from §X / timestamp HH:MM]` location markers when available)
- `### Cross-references` — other works / people / concepts cited by source
- `### Methodology` — how source produced claims (research method, data, analysis)
- `### Caveats / Limitations` — counter-args, limitations, acknowledged uncertainty

LLM may invent new sub-headings if source warrants (free-form).

**Length**: source-proportional, no hard cap:
- Thin source (no Detailed Extract): N/A
- Medium source: 100-400 words across 2-3 sub-sections
- Substantive source: 400-1500 words across 3-5 sub-sections
- Long paper / book: 1000+ words with comprehensive sub-sections

**Example** (substantive source — Shinola analysis with Detailed Extract):
```markdown
## Detailed Extract

### Key Claims

- Design choices ARE language — every material / proportion / surface treatment carries semantic load
- Canfield headphones specifically encode "American craftsmanship" via 4 deliberate choices: bulky joint, leather/metal materiality, polished chrome accents, exposed stitching
- Mauriello distinguishes "designer language" (intent) from "user language" (interpretation) — analysis bridges them

### Methodology

Three-pass reading protocol:
1. **Silhouette / proportion** — first impression at distance; what shape vocabulary does it borrow?
2. **Materials / contrast** — what does the material palette signal? (Plastic = mass / cheap; leather + metal = craft / weight)
3. **Manufacturing traces** — visible joints, stitches, fasteners → assembly story → labor visibility

### Notable Quotes

- "Design is a language. If you don't speak it, you'll miss the conversation." (opening)
- "Plastic would have killed this product — it would say 'mass-market', and Shinola sells the opposite story."

### Cross-references

- [[Astro-Studios]] — design firm collaborator
- Mauriello's broader "deconstruction" series methodology
```

### §4 Body section order

```markdown
---
<frontmatter — 8 fields unchanged>
---

## Source
[[<source-basename>]]

## TL;DR
- bullet 1
- bullet 2
- ...

## Detailed Extract  <!-- MAY; include when source has substance -->

### Key Claims
- ...

### Methodology
- ...

## Key Contributions
- **[[target-wiki-page-1]]** — what this source added
- **[[target-wiki-page-2]]** — what this source added
```

**Rationale for order**: TL;DR (fast scan) → Detailed Extract (deep dive) → Key Contributions (meta — which wiki pages this source fed into). Reading flow goes from quick → deep → meta.

### §5 Spec changes (touch points)

| File | Change | Scale |
|---|---|---|
| `obsidian/skills/wiki-ingest/references/page-format.md` | Rewrite §Reference page body structure (3 sections → 3 required + 1 optional; rename + reshape TL;DR; add Detailed Extract spec + sub-heading vocabulary; update examples) | ~80 lines net (add Detailed Extract spec block; rewrite TL;DR block) |
| `obsidian/skills/wiki-ingest/SKILL.md` STEP 4d | Update in-flight template + prose (mirror canonical spec change; keep `## Source` wikilink warning intact) | ~30 lines patch |
| `obsidian/.claude-plugin/plugin.json` | Version bump 3.13.0 → 3.14.0 | 1 line |

**No wiki-lint changes in MVP** — L14 (`## Source` wikilink format) unchanged; no new L15 for TL;DR / Detailed Extract enforcement (Phase 2 if dogfood shows need).

**No script changes** — select-batch.py / verify-drift.py / distribute.py unaffected. Pure markdown spec change.

### §6 Test plan (manual; no pytest)

Same reality-check as v3.11.0 part-3 ([[cc-ll-pytest-infeasibility]]): ref page format is enforced by Claude reading SKILL.md + page-format.md, not a Python script. No pytest possible for format compliance.

Manual verification:
- After commit, ack the section rename (`grep -c 'Source Excerpt' SKILL.md page-format.md` returns 0; `grep -c '## TL;DR\|## Detailed Extract' SKILL.md page-format.md` returns ≥ 2)
- Existing 24 pytest pass (no regression on script-side; ref page is doc-side only)
- verify-drift exit 0 (no impact)
- (Optional) post-merge dogfood: kouko triggers re-ingest on 1-2 substantive source notes (e.g. modify mtime to force re-ingest) → observe new ref page format

### §7 Commit split (candidate — writing-plans tightens)

Small scope, single commit likely OK. But for SDD discipline + atomic-task review:

| Task | Module | LOC est |
|---|---|---|
| T1 page-format.md rewrite (canonical) | `obsidian/skills/wiki-ingest/references/page-format.md` | ~80 |
| T2 SKILL.md STEP 4d update (in-flight template mirror) | `obsidian/skills/wiki-ingest/SKILL.md` | ~30 |
| T3 Version bump | `obsidian/.claude-plugin/plugin.json` | 1 |

Total ~111 LOC, 3 tasks, single plan. All parallel-eligible (different files, no shared state).

### §8 PR naming

- Branch: `feat/wiki-ingest-ref-page-tldr-detailed-extract` (already created)
- PR title: `wiki-ingest: ref page TL;DR list format + Detailed Extract (v3.14.0)`
- Version: v3.13.0 → v3.14.0 (minor bump — body schema change is backward compatible; old pages remain valid)

## What Becomes Obsolete

- **`## Source Excerpt / TL;DR` section name** — replaced by `## TL;DR`. Existing 468 pages keep old name via natural drift; new ingest uses new name.
- **"2-4 sentence neutral description" wording** in spec — replaced by "3-7 bullets, sentence fragments".
- **Prose convention for TL;DR** — replaced by list-format affordance.
- **Implicit "deep extraction is unspecified"** stance — replaced by explicit `## Detailed Extract` MAY section + suggested sub-heading vocabulary.

Same-PR strip / replace: all 4 above land together in the spec update.

## Alternatives Considered

### TL;DR list shape (already pinned A — free 3-7 bullets, sentence-fragment style)

- **A. Free 3-7 bullets** ✅ — flexible for diverse source types; LLM judges count + content per source
- B. Fixed 3 bullets (subject / claim / context) — rigid; short source 套不住, long source 過度壓縮
- C. Mixed (1 fixed subject bullet + 2-6 free) — middle ground but adds rule complexity for marginal value
- D. Numbered list (1./2./3.) — extraction is not inherently ordered; bullet (-) is more honest semantic

### Detailed Extract section name (orchestrator picked Detailed Extract)

- **`## Detailed Extract`** ✅ — "Extract" is standard term for structured pull-from-source; "Detailed" signals longer/structured vs short TL;DR
- `## Key Substance` — vaguer; could imply opinion vs neutral pull
- `## Source Details` — redundant with existing `## Source` section
- `## Substance` — too short; ambiguous
- `## Extract` — clean but loses "Detailed" connotation that distinguishes from TL;DR

### Detailed Extract severity (orchestrator picked MAY)

- **MAY (advisory)** ✅ — LLM judges per-source; thin sources skip cleanly
- MUST — forces every thin source to bloat with empty section; over-prescriptive
- MUST-when-source-substantive (LLM-judge condition) — requires source-type detection or length heuristic; YAGNI for MVP, Phase 2 if dogfood demands

### Sub-heading vocabulary (orchestrator picked free-form with suggested list)

- **Free-form, suggested vocabulary** ✅ — diverse source types (video / paper / forum / book) need flexibility; LLM picks 2-4 sub-sections per source from suggested list OR invents new ones
- Fixed enumeration — too rigid; video has timestamps but no "methodology", paper has methodology but no "timestamps"
- No sub-headings (flat list) — loses semantic structure that helps wiki-query Tier 2 retrieval

### Body section order (orchestrator picked TL;DR → Detailed Extract → Key Contributions)

- **Source → TL;DR → Detailed Extract → Key Contributions** ✅ — read flow goes quick → deep → meta
- Source → TL;DR → Key Contributions → Detailed Extract — Key Contributions belongs as meta-footer, not mid-body
- Source → Detailed Extract → TL;DR → Key Contributions — top-heavy; user can't skim before deep dive

### Migration scope (orchestrator picked natural drift)

- **Natural drift only** ✅ — same v3.10.0 / v3.11.0 / v3.12.0 pattern. Low risk. 468 old pages stay valid (no lint enforcement on rename).
- `/wiki-relang` bulk re-extract in MVP — +3-4 hr implementation + LLM cost for 468 page regen (substantial). Phase 2 if dogfood demand emerges.
- `OBSIDIAN_WIKI_FORCE_RELANG=true` flag — half-measure; conflicts with SHA-256 manifest idempotence.

## Out of Scope

- `/wiki-relang` migration command — Phase 2 future PR (deferred per migration alternatives)
- wiki-lint L15 enforcement on `## TL;DR` presence / format — Phase 2 if dogfood shows ingest skipping section
- Source-type-specific templates (`source_type` frontmatter field) — YAGNI for MVP; Detailed Extract free-form sub-headings handles diversity
- `## Detailed Extract` MUST upgrade — Phase 2 conditional on dogfood
- Density-floor lint (LLM judges LLM output) — recursive concern; only revisit if dogfood strongly demands
- pytest CC-style fixtures for ref page format — infeasible same as v3.11.0 ([[cc-ll-pytest-infeasibility]]); format is Claude-prose-enforced, no resolver to unit-test
- Body language policy interaction — language-policy.md (v3.11.0) already governs body language; TL;DR / Detailed Extract follow same language convention as parent body. No new interaction.

## Open Questions

1. **`## Detailed Extract` sub-heading vocabulary** — should the canonical spec include all 6 suggested sub-headings (Key Claims / Examples / Notable Quotes / Cross-references / Methodology / Caveats) OR a shorter "starter set" (3-4) to avoid template fatigue? Implementer's call during T1 (page-format.md rewrite); surface in self_review.
2. **Detailed Extract length cap** — spec says "no hard cap, source-proportional". Should there be a soft cap (e.g. "Detailed Extract MAY exceed 2000 words but consider whether wiki/synthesis page is more appropriate at that point")? Defer to dogfood — if Detailed Extracts blow past 2000 words consistently, add Phase 2 guidance.
3. **Old pages with `## Source Excerpt / TL;DR` heading** — should wiki-query Tier 2 reader prose explicitly know about both heading names (old + new)? Tier 2 reads full body so no special handling needed, but if wiki-query has any heading-specific extraction logic, it needs to handle both. Verify in implementer self_review.

## References

- Predecessor: `obsidian/skills/wiki-ingest/references/page-format.md` §Reference page body structure (v3.12.0 + later refinements)
- Current SKILL.md STEP 4d: `obsidian/skills/wiki-ingest/SKILL.md`
- Consumer: `obsidian/skills/wiki-query/references/retrieval-tiers.md` Tier 2 (full body read)
- Lint: `obsidian/skills/wiki-lint/references/lint-checks.md` L14 (Source wikilink), L01/L07/L08 (other; unrelated to this change)
- Sample ref pages: `~/kouko-obsidian-vault/wiki/references/` (468 pages; sampled `2018-08-30-...-shinola-audio.md` thin / `_2025-09-07-...-fundednext-futures-prop-firm.md` dense)
- Memory: [[cc-ll-pytest-infeasibility]] (parallel — format is Claude-prose-enforced; no pytest); [[wiki-ingest-v3-11-0]] (predecessor body-language policy used same MAY/advisory pattern + natural drift migration)
