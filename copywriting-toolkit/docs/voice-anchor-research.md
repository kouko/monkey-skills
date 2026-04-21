# Voice Anchor Expansion — Research Synthesis

**Branch**: `research/copywriting-voice-anchor-expansion`
**Date**: 2026-04-21
**Status**: Research complete; awaiting scope decision from user

## Context

Current voice anchor library in `copywriting-toolkit` has two layers:

1. **Persona deep-dives** (2 files): `jp-copy-craft-lineage.md` (3 masters: 糸井 / 岩崎 / 眞木) + `zh-copy-craft-lineage.md` (3 masters: 許舜英 / 李欣頻 / 葉明桂)
2. **Brand-era entries** in `voice-quadrant-positioning.md`: Economist / Rolls-Royce / Apple / MUJI / Nike / Dove / Amazon / Uniqlo / 誠品 / 中興百貨 / 左岸咖啡館 / Patagonia / ほぼ日 (~13 entries)

**User concern (2026-04-21)**: too few personas; too Taiwan + Japan-biased; no Korean / no European / no UK-classical; contemporary SNS / DTC era absent; brand-era layer thin.

**Research question**: should we expand persona coverage, shift toward brand-era as primary anchor, or both?

## Strategic findings (6 points)

### 1. Persona vs brand-era reproducibility asymmetry

`jp-copy-craft-lineage.md` itself documents "LLM reproduction gap" per master — LLMs reproduce surface grammar but miss the cultural / strategic / craft payload. This is a structural problem with persona-as-anchor:

| Anchor type | Corpus size | LLM retrieval | Cross-cultural recognition | Era boundary clarity |
|---|---|---|---|---|
| Persona (single writer) | 10-30 pieces | thin | varies by writer fame | blurry |
| Brand-era | 100+ pieces | dense (website + press + case studies) | higher (brands are globally known) | clear (campaign start/end + agency + CD) |

**Recommendation**: brand-era as *primary* anchor for drafting pipelines; persona as *secondary* layer for craft-depth / mitigation-gate references.

### 2. Korean is the biggest single cultural gap

Zero coverage today. Adding **박웅현 (Park Woong-hyun) persona + 배달의민족 (한명수) brand-era** closes ~70% of the KR gap at low token cost. Primary sources strong (books + TBWA Korea archive + 한국일보 interviews). Korean is well-represented in LLM training corpora.

### 3. Anglo-UK slot is thinner than the English-training-corpus justifies

EN is the LLM's strongest language, but current library treats Anglo as a single block. Recommended additions that pay back immediately in Phase 5/6 voice-tuning:

- **Bernbach / DDB** persona (foundational EN, Q1↔Q3, highly reproducible pattern)
- **Hopkins** persona (foundational DR canon; *Scientific Advertising* public-domain)
- **Halbert** persona (bridges Schwartz→modern DR; free Boron Letters archive)
- **Basecamp** persona (fills B2B-SaaS Q1 gap; 4 canonical books)
- **Patek Philippe / Oatly / Absolut / BMW** brand-era (fill luxury-heritage / modern-DTC / spirits-minimalist / performance-auto sub-types)

### 4. ZH has both a big coverage gap AND 8 drift corrections

ZH research surfaced 8 misattributions that need fixing regardless of expansion scope:

1. 多喝水 ≠ 吳念真（奧美 in-house）
2. 孫大偉 agency = 台灣奧美 / 偉太（非智威湯遜）
3. 朱家鼎 agency = 堂煌 → 靈智（非東方廣告）
4. 長榮〈I SEE YOU〉旁白 = 金城武本人（非吳念真）
5. 全聯經濟美學 creative lead = 龔大中（非林敬凱；邱彥翔 為演員）
6. 意識形態廣告 = 許舜英 **+ 鄭松茂** 共同創辦（非許舜英獨資）
7. 花西子 創辦人 = 花滿天（非「梁」）
8. 曾錦程 / Calvin Choy HK JWT 身份 `[UNVERIFIED]`

### 5. JP has a cross-ref drift bug

`voice-quadrant-positioning.md` section 「Q2 author-centric deep-dives」 promises **仲畑貴志 deep-dive** exists in `jp-copy-craft-lineage.md` — it doesn't. Cross-ref drift. Fixing this alone justifies JP persona expansion.

### 6. "Visual-dominant" entries should be explicitly excluded

Across all 4 research reports, a pattern emerged: some campaigns are canonical but LLM cannot use them as voice anchors because copy alone is insufficient. Need a new standards category: **`visual-dominant-skip.md`** — documents these cases so the pipeline doesn't produce weak pseudo-Toscani headlines.

Candidates for the skip list:
- Benetton / Oliviero Toscani 1984-2000 (photograph IS the message)
- 이제석광고연구소 (guerilla installation carries 80%)
- Thai Life / TrueMove H "Unsung Hero" (cinematic film, 5-word closing card)
- Apple "1984" single spot (95% directorial, 5% copy — Ridley Scott, not a voice anchor)
- Guinness "Surfer" 1999 (same — Jonathan Glazer directorial)
- Old Spice 2010 "Man Your Man" (delivery / comedic timing by Isaiah Mustafa — not a written-voice anchor)
- John Webster BMP TV work (character performance carries copy)

## Consolidated candidate list (26 entries across 4 cultures + drift)

Ranked by composite score: primary-source strength × cultural-coverage-gap-fill × LLM reproducibility × canonical window clarity.

### Tier A — HIGH priority (12 entries)

| # | Culture | Entry | Type | Quadrant | Why |
|---|---|---|---|---|---|
| A1 | KR | **박웅현 / Park Woong-hyun** | persona-deep-dive | Q2 | Fills largest single cultural gap; 『책은 도끼다』 100쇄+; TBWA Korea archive |
| A2 | KR | **배달의민족 / 한명수** | brand-era | Q3 | Unique 반말 peer-register voice; no library substitute |
| A3 | JP | **仲畑貴志** | persona-deep-dive | Q3-core/Q2-edge | Fixes cross-ref drift bug; TCC Hall 1998; completes 1947-48 "big four" |
| A4 | JP | **秋山晶** | persona-deep-dive | Q2-core | Fills Q2-core gap (existing 3 are Q3/Q2-edge); 1936 prequel generation |
| A5 | JP | **谷山雅計** | persona-deep-dive (shallow) | Q3/Q2 hybrid | Only JP master who wrote method book (ISBN 978-4883351770); bridges 1980s→2000s |
| A6 | ZH (CN) | **杜蕾斯官微 / 金鵬遠 (環時互動 2011-2017)** | brand-era + persona | Q3/Q4 | Largest CN gap (SNS 借勢); 數英 + 梅花網 archive; clear canonical era boundary |
| A7 | ZH (HK) | **朱家鼎 / 鐵達時系列 (1988-1992)** | persona-deep-dive | Q2 | HK persona #1; 金帆獎 primary archive; fills HK gap entirely |
| A8 | ZH (TW) | **龔大中 (全聯經濟美學 2015-)** | persona-deep-dive (extend existing brand entry) | Q3 | 動腦/數位時代/經理人 triple archive; completes Q3-TW |
| A9 | EN | **Bill Bernbach / DDB (VW + Avis)** | persona-deep-dive | Q1↔Q3 | Foundational EN canon; Levenson book + Ad Age #1 campaign of century |
| A10 | EN | **Claude Hopkins — Scientific Advertising** | persona-deep-dive | Q1/Q4 | Public-domain canonical book; foundational DR method |
| A11 | EN | **David Abbott / AMV BBDO (Economist era)** | persona-deep-dive | Q1/Q2 | Most-anthologized UK copywriter; extends existing Economist brand-era |
| A12 | EN | **Oatly (Schoolcraft 2012-)** | brand-era | Q3↔Q2 | Modern-DTC Q3 anchor; Marketing Society doc; highly distinctive |

### Tier B — MEDIUM priority (10 entries)

| # | Culture | Entry | Type | Quadrant | Why |
|---|---|---|---|---|---|
| B1 | JP | **梅田悟司 + ジョージア「世界は誰かの仕事でできている。」(2014)** | brand-era + shallow persona | Q3↔Q2 | Post-糸井 generation (1979 birth); fills 2000s-2010s gap |
| B2 | JP | **サントリー multi-era cluster** | brand-era cluster | Q2-Q3-Q4 | Japan's highest-density voice portfolio; demonstrates one brand traversing multiple Q |
| B3 | JP | **JR東海「そうだ 京都、行こう。」(1993-)** | brand-era + 一倉宏 note | Q2↔Q3 | Longest single-voice JP campaign; 30-year sustainability lesson |
| B4 | ZH (TW) | **吳念真 (保力達B 1990s-)** | persona-deep-dive | Q3 台語 | Fills Q3 台語軸; 中央社 primary source |
| B5 | ZH (TW) | **胡湘雲 (大眾銀行 2010-2015)** | persona-deep-dive | Q3 TVC-narrative | TW contemporary Q3 long-form anchor |
| B6 | ZH (CN) | **網易雲音樂樂評地鐵 (2017)** | brand-era canonical | Q3 | UGC-as-brand-voice methodology; 數英 project archive |
| B7 | ZH (CN) | **江小白 文案瓶 + LLM anti-pattern** | brand-era + anti-pattern reference | Q3 | Dual value: brand-era canon + negative reference for LLM over-mimic |
| B8 | EN | **Gary Halbert / Boron Letters** | persona-deep-dive | Q4/Q3 | Free canonical corpus; bridges Schwartz → modern DR |
| B9 | EN | **Basecamp / Fried+DHH** | persona-deep-dive | Q1↔Q2 | Fills B2B-SaaS gap; 4 books; negation-manifesto pattern |
| B10 | EN | **Patek Philippe "Generations" (Leagas Delaney 1996-)** | brand-era | Q2 | Heritage-luxury Q2 sub-type (complements Apple/MUJI tech/lifestyle) |

### Tier C — LOW priority / optional (4 entries)

| # | Culture | Entry | Notes |
|---|---|---|---|
| C1 | EN | **Absolut Vodka (TBWA 1981-2005)** | Strong archive, but corpus is 1,500 pun variants — less anchoring power than top tier |
| C2 | EN | **BMW "Ultimate Driving Machine"** | 50-year window is good, but complements rather than fills gap |
| C3 | EN | **Innocent Drinks** | Founder himself regrets pioneering "wackaging"; include as audit-against-drift reference only |
| C4 | ZH (CN) | **新世相 (2015-2017)** | 公眾號-era voice; narrower canonical window than 杜蕾斯 |

### Tier D — SKIP (visual-dominant / insufficient primary source)

| Entry | Reason |
|---|---|
| 이제석광고연구소 (KR) | Visual-dominant; isolated copy reads generic |
| Benetton / Toscani | Photography is the message; no copy corpus |
| Thai Life / TrueMove H | Film anchor, 5-word closing cards only |
| BETC Paris / Orangina | French phonetic register doesn't transfer; misattribution risk |
| Volkswagen "Das Auto" (German) | Internal marketing slogan, not canonical author |
| Del Campo / SCPF (LATAM) | Primary-source copy thin in English; Cannes reels visual |
| Indonesia / Philippines / Vietnam | Primary-source canon absent; LLM training data thin |
| Dan Kennedy | Insufficient independent primary-source strength |
| Bill Jayme (DM king) | Scattered archive; needs deeper research |
| Saatchi/Saatchi political era | Narrow UK-political corpus; cultural opacity |
| 김민철 (KR) | Essayistic not campaign craft; orthogonal |
| Ben & Jerry's | Distributed authorship; no single persona anchor |
| Apple "1984" single-spot / Guinness Surfer / Old Spice Man Your Man | Visual-dominant skip list category |

## Layering framework (proposed)

Restructure anchor library into 4 layers:

```
Layer 1: Brand-era corpus (PRIMARY anchor for drafting)
  → voice-quadrant-positioning.md §per-quadrant brand entries
  → expanded with era narration + agency/CD + canonical window

Layer 2: Persona deep-dives (SECONDARY for craft-depth + mitigation gates)
  → jp-copy-craft-lineage.md (existing + 3 new)
  → zh-copy-craft-lineage.md (existing + 4 new)
  → kr-copy-craft-lineage.md (NEW, parallels JP/ZH pattern)
  → en-copy-craft-lineage.md (NEW, or expanded Anglo section)

Layer 3: LLM anti-pattern references (NEGATIVE reference to catch drift)
  → NEW section (location TBD): 江小白 / 花西子 / Innocent-wackaging-imitators
  → "If your output looks like this, voice has collapsed"

Layer 4: Visual-dominant skip list (EXCLUDED from voice emulation)
  → NEW file: visual-dominant-skip.md
  → Benetton / 이제석 / Thai Life / cinematic Anglo
  → "When a brief says 'like X,' the pipeline reframes — does not emulate copy"
```

## Drift corrections (must-do regardless of expansion scope)

8 misattributions that should be fixed in current files even if no expansion happens:

**`zh-copy-craft-lineage.md`** — add Drift Corrections Z5-Z8:
- Z5: 多喝水 ≠ 吳念真
- Z6: 孫大偉 agency 正名
- Z7: 長榮〈I SEE YOU〉旁白 = 金城武
- Z8: 全聯經濟美學 creative lead = 龔大中

**`voice-quadrant-positioning.md`** — update 中興百貨 entry:
- Note 意識形態廣告 = 許舜英 **+ 鄭松茂** 共同創辦

**`jp-copy-craft-lineage.md`** — fix cross-ref bug:
- Either add 仲畑貴志 deep-dive, or remove the "see this file for 仲畑" cross-ref in `voice-quadrant-positioning.md §Q2 author cross-reference`

## Implementation constraint (Tier 1 byte-identical policy)

Per `copywriting-toolkit/CLAUDE.md §Provenance & Divergence Principle`:

> Tier 1 files (`skills/*/standards/*.md`) MUST match the source verbatim. No divergence allowed. Verify via `diff -q` against `domain-teams/skills/copywriting-team/`.

This means:

**Path A — expansion via domain-teams upstream first** (strict Tier 1):
1. Land edits in `domain-teams/skills/copywriting-team/skills/*/standards/*.md`
2. `cp` to `copywriting-toolkit/skills/*/standards/*.md` (byte-identical)
3. Verify `diff -q` empty

**Path B — toolkit-originated canon** (only for NEW files with no upstream precedent):
- Precedent: `zh-copy-craft-lineage.md` was "newly authored for this toolkit in v1.0.1 (no upstream source)"
- Applies to: `kr-copy-craft-lineage.md` (NEW), `en-copy-craft-lineage.md` (NEW), `visual-dominant-skip.md` (NEW)
- Must still be Tier 1 discipline (immutable canon, no per-user edits)

**Path C — hybrid**:
- New files (KR, EN, anti-pattern, visual-skip) → Path B (toolkit-originated)
- Edits to existing files (JP, ZH, voice-quadrant-positioning) → Path A (upstream first)

**Recommendation**: Path C. Avoids waiting on domain-teams updates for new cultural coverage while keeping discipline on existing files.

## Phased expansion options

### Option 1 — Minimal (drift-only)

Scope: 8 ZH drift corrections + JP cross-ref bug fix. No new entries.
Effort: ~1 day. 2 commits.
Value: fixes known bugs; does NOT close cultural gaps.
**ROI**: HIGH-value-per-effort, but does not address user's original concern.

### Option 2 — Cultural gap fill (Tier A only, 12 entries)

Scope: Drift corrections + 12 Tier A entries across KR / JP / ZH / EN.
New files: `kr-copy-craft-lineage.md`, `en-copy-craft-lineage.md`, `visual-dominant-skip.md`.
Edits: `jp-copy-craft-lineage.md` (+3 masters), `zh-copy-craft-lineage.md` (+2 masters + 4 brand entries), `voice-quadrant-positioning.md` (+ brand-era entries + drift fixes).
Effort: ~5-7 days. 4-5 commits.
Value: closes biggest gaps; establishes layering framework.
**ROI**: HIGH. Recommended default.

### Option 3 — Comprehensive (Tier A + B, 22 entries)

Scope: Option 2 + Tier B (10 more entries).
Effort: ~10-14 days. 6-8 commits.
Value: thorough coverage; includes contemporary SNS / B2B / DTC.
**ROI**: MEDIUM. Marginal value per entry drops after Tier A.

### Option 4 — Exhaustive (Tier A + B + C, 26 entries)

Scope: Option 3 + Tier C (4 optional entries).
Effort: ~14-18 days. 8-10 commits.
Value: exhaustive; but most Tier C entries are complementary, not gap-filling.
**ROI**: LOW. Not recommended unless specific Tier C entries requested.

## Open decisions (user input needed)

1. **Scope**: Option 1 (drift-only), 2 (Tier A), 3 (Tier A+B), or 4 (exhaustive)?
2. **Layering framework adoption**: accept 4-layer restructure (Layer 1-4) or keep current 2-layer?
3. **Anti-pattern layer — where?**: new file `llm-anti-pattern-references.md`? or inline sections within existing `*-lineage.md` files?
4. **Visual-dominant skip list — opt-in?**: create `visual-dominant-skip.md` as new Tier 1 file, or integrate into `voice-quadrant-positioning.md` as a new section?
5. **Tier 1 path**: Path A (domain-teams upstream first, slower) or Path C (hybrid — new files bypass upstream)?
6. **Budget**: token budget for new files? Current budget rule is ≤6K tokens per SKILL.md body; standards files don't have explicit limit but 1K-4K per lineage file is typical.

## Research deliverables (transcripts on branch)

Four parallel research agents dispatched 2026-04-21. Each delivered structured report with primary sources, verbatim copy, voice signatures, LLM reproducibility assessments.

- **EN/Anglo**: ~2,500 words; 36 tool uses; sources: Ad Age, Cannes, D&AD, Creative Hall of Fame, author books
- **JP**: ~2,000 words; 4 tool uses; sources: TCC 年鑑, 宣伝会議, AdverTimes, author books
- **ZH**: ~2,800 words; 31 tool uses; sources: 動腦/Brain, 數英, 梅花網, 時報廣告金像獎, 百度百科, 維基百科
- **Korean+European+Other**: ~2,500 words; 22 tool uses; sources: 나무위키, TBWA Korea, Campaign Asia, Cannes Lions, Creative Review

Full transcripts available at `/private/tmp/claude-501/` agent output files (session-scoped; preserve via export if needed for audit trail).
