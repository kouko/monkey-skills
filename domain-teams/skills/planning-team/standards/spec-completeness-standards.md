---
title: Spec Completeness Standards
tier: 2
---

# Spec Completeness Standards

Anchor for the cross-cutting completeness standards planning-team
applies to a PRODUCT-SPEC.md deliverable: the 5W2H coverage check
(situating the spec in the multi-origin genealogy of 5W1H → TPS +2H),
the decision-rationale rule, and the Japanese 企画書 cultural
anchoring for planning-team's JP-literate users. Tier 2: LLMs know
"5W2H" as a term but routinely misattribute its origin, and the
body spells out the correct genealogy plus the concrete per-letter
checks planning-team actually applies.

## Primary Sources

- **Rudyard Kipling (1902)** "The Elephant's Child" in *Just So Stories*. Macmillan. The 5W1H origin — the six honest serving-men verse: "I keep six honest serving-men / (They taught me all I knew); / Their names are What and Why and When / And How and Where and Who." This is the poetic origin of the 5W1H pattern that later management traditions formalized.
- **大野耐一 (1978)**『トヨタ生産方式—脱規模の経営をめざして』ダイヤモンド社. Canonical TPS source. Ohno popularized 5 Why (なぜを 5 回繰り返せ) and the 5W1H question discipline in Japanese manufacturing management, which the 1960s JUSE quality movement had already extended by adding +2H.
- **Taiichi Ohno (1988)** *Toyota Production System: Beyond Large-Scale Production*. Productivity Press. The authorized English translation of 大野 (1978). This is the bridge for non-JP readers and the source Eric Ries cites in *The Lean Startup* (2011) for his "Lean" lineage.
- **今井茂雄訳 (1988)**『アイデアのつくり方』TBSブリタニカ. The Japanese translation of James Webb Young (1940) *A Technique for Producing Ideas*. The JP translation with 竹内均's commentary elevated this slim book to **canonical status in Japanese 企画 (kikaku) culture** — far beyond its status in the English-speaking world. Planning-team cites the JP translation as the authoritative edition for JP 企画 readers because that is where the book's cultural weight actually lives.

## Critical Attribution Corrections

### 5W2H is not purely "Japanese business convention"

The prior planning-team standards described 5W2H as "日本ビジネス慣習由来"
("derived from Japanese business customs"). This is **partially correct
but genealogically oversimplified**. The correct genealogy is a
multi-step composite:

1. **5W1H poetic origin** — Kipling (1902) "The Elephant's Child" in
   *Just So Stories*. Not Japanese.
2. **5W newswriting adoption** — late-19th-century US journalism
   adopted 5W1H as a reporting checklist. Not Japanese.
3. **+1H (How) in management** — early-20th-century management
   literature extended the 5W to include How. Origin diffuse; no
   single attribution.
4. **+2H (How much) in Japanese quality movement** — the 1960s
   Japanese quality management movement (JUSE, Deming's visits to
   Japan, subsequent Kaizen tradition) extended 5W1H to 5W2H by
   adding "How much". This is the Japanese contribution.
5. **Popularization via TPS** — 大野耐一 (1978)『トヨタ生産方式』
   popularized 5W1H questioning discipline and (implicitly) 5W2H
   in the broader lean management tradition.

**Correct attribution**: "5W1H poetic origin traces to Kipling (1902);
the +2H extension entered via 1960s Japanese quality management
(JUSE), and 大野 (1978) *Toyota Production System* is the
book-form canonical popularization." Do not cite 5W2H as a
single-origin Japanese framework.

### No canonical 企画書 textbook exists at framework level

Japanese business has a strong cultural attachment to 企画書
(kikakusho) as an artifact, and several practitioner handbook
series exist (高橋憲行's 企画塾 series, 『企画書の書き方』 series).
**None of these rise to framework-level canonical status** in the
way that BMC or OKR do. Planning-team treats 企画書 as a **cultural
idiom** for planning deliverables in JP contexts, not as a
methodology with a primary source. When writing in Japanese,
planning-team produces PRODUCT-SPEC.md as the actual artifact but
may describe it as a 企画書 for user-facing language. Do not cite
any single 企画書 textbook as canonical — no such canonical exists.

### James Webb Young (1940) is JP-canonical via the 1988 translation

The English-language *A Technique for Producing Ideas* (Young 1940)
is a minor trade publication in the US. The **Japanese translation
by 今井茂雄 with commentary by 竹内均**, published by TBSブリタニカ
in 1988, is **canonical in Japanese 企画 education** — deeply
embedded in the training of 商品企画, 広告制作, editorial, and
corporate planning professionals in Japan. Its 5-step idea
generation method (材料収集 → 咀嚼 → 熟成 → ひらめき → 具象化)
is part of the shared vocabulary of JP 企画 work. Planning-team
cites the **1988 Japanese translation** (not the 1940 US original)
as the load-bearing primary for this framework, because the
cultural weight lives in the JP edition.

## 5W2H — Per-Letter Checks

When planning-team applies 5W2H to a PRODUCT-SPEC.md as a final
completeness check, each letter maps to a specific spec section
and a specific question:

| Letter | Question (JP) | Question (EN) | PRODUCT-SPEC.md section |
|---|---|---|---|
| **Why（なぜ）** | この企画の目的・背景は？ | What problem / opportunity drives this? | Background & Opportunity |
| **What（何を）** | 提供する製品・サービスの内容は？ | What is the product delivering? | Core Concept / Value Proposition |
| **Who（誰が・誰に）** | ターゲットユーザーと実行者は？ | Who is the customer? Who builds it? | Target Users + Team |
| **When（いつ）** | タイムラインとマイルストーンは？ | What is the delivery timeline? | Scope & Phasing |
| **Where（どこで）** | プラットフォームと配布チャネルは？ | What platforms / channels / geographies? | UX Direction + Business Direction |
| **How（どのように）** | 技術アプローチと実現方法は？ | What is the technical approach? | Technical Direction |
| **How much（いくらで）** | コスト・リソース見積もりは？ | What resources / cost / budget? | Success Criteria / Business Direction |

A spec that fails to answer any one of the 7 is **incomplete**.
Planning-team uses 5W2H as the **final** completeness pass — after
JTBD has defined the job (Why + What + Who), after the 4 Big Risks
have surfaced assumptions, after OKRs have been set (Success
Criteria — the How much + When). 5W2H is a cross-check, not the
primary structure.

## JP 企画 genealogy — Cultural Anchoring for JP Users

For JP-literate users, planning-team carries these JP cultural
anchors in its Phase 1 Vision work:

- **ヤング 1988 日譯『アイデアのつくり方』** — the 5-step idea
  generation method (材料収集 → 咀嚼 → 熟成 → ひらめき → 具象化)
  that pre-dates JTBD but maps well to Phase 1 brainstorming.
- **大野耐一 1978『トヨタ生産方式』** — the Lean TPS origin that
  Ries 2011 inherits. Planning-team references Ohno when explaining
  Lean / MVP lineage to JP users.
- **三枝匡 1994『戦略プロフェッショナル』** — case-based JP corporate
  planning education. Useful as a cultural reference for what "good
  planning work" looks like in the JP tradition.
- **大前研一 1975『企業参謀』** — 3C 分析 origin. See
  `standards/planning-frameworks.md` §3C 分析 for the full treatment.

When a JP user requests PRODUCT-SPEC.md work, planning-team can
optionally frame the deliverable as a 企画書 (kikakusho) and draw on
these genealogies. The load-bearing methodology is still Western
primary (Christensen / Ries / Osterwalder / Cagan / Doerr); the JP
anchors appear as cultural references, not as methodology substitutes.

## Decision Rationale Rule

Every major decision in a PRODUCT-SPEC.md must include a **because**
clause — the reason for choosing X over Y. Planning-team's rule:

> For every sentence of the form "We will X", there must be a
> sentence of the form "because Y" nearby (same paragraph preferred,
> same section maximum).

Missing decision rationale is the single most common failure mode
for PRODUCT-SPEC.md work. A spec without decision rationale is not
actionable by downstream teams because they cannot tell which
decisions are load-bearing versus arbitrary. The rule applies to:

- Technical architecture choices (why this language, this framework,
  this deployment target)
- Scope decisions (why these goals, why these non-goals)
- Design decisions (why this interaction model, why this platform)
- Business decisions (why this monetization, why this channel)

CHK-PROD-005 in `checklists/product-spec-completeness.md` enforces
this rule as a FIXABLE check.

## Anti-Patterns

- Citing 5W2H as "Japanese business convention" without the
  Kipling 1902 → JUSE 1960s → Ohno 1978 genealogy.
- Treating ヤング『アイデアのつくり方』 as a minor heuristic — in
  JP 企画 culture it is canonical, and JP users will expect it to
  be recognized.
- Producing a PRODUCT-SPEC.md without 5W2H cross-check when the
  user is JP-literate — 5W2H is a cultural expectation for
  comprehensive coverage in JP business writing.
- Omitting decision rationale on load-bearing choices. "We chose
  TypeScript" without "because" is not a spec, it's a preference.
- Citing a 企画書 practitioner handbook (高橋 etc.) as if it were
  framework-level canonical — no such canonical exists; cite
  only at practitioner-tradition level.
