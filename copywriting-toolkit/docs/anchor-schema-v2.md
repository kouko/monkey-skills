---
title: Anchor Schema v2 — Layer 1 Purpose-Centric Spec
status: pilot
---

# Anchor Schema v2

**Status**: pilot (v1.4.0), validating via 8-anchor reformat before full migration.

**Motivation**: v1 schema (`voice-anchor-meta-core.md`) is researcher-catalog-centric, mixing 3 readers' needs (Pass 3 copywriter / Gate evaluator / Human researcher) in one bullet list. v2 splits into layers, keeps only Layer 1 inside skill, moves Layer 2/3 to `docs/voice-anchor-deep-dives/` as research artifacts.

## Design principle

Anchor file content = **what Pass 3 copywriter agent needs to rewrite a draft in this voice, and nothing else**.

Critics' qualitative read + mechanical rules + examples + anti-patterns — these four layers of guidance work together. Biographical / era / award / agency-history content does NOT help Pass 3 rewrite, therefore not in Layer 1.

## Inclusion criterion (v1.4.0)

**An entity qualifies as a voice anchor IF AND ONLY IF it is an individual creator whose sentence-level register is identifiable across a body of work.**

Qualifying types:
- Authors / novelists / essayists (向田邦子, 宮沢賢治, 張愛玲, Joan Didion, Raymond Carver)
- Screenwriters / playwrights (坂元裕二, 王家衛, Aaron Sorkin)
- Poets (谷川俊太郎)
- Named copywriters with craft-gate signature (糸井重里, 岩崎俊一, 許舜英, 李欣頻, 梅田悟司)
- Named creative directors with recognizable craft across multiple campaigns (朱家鼎 Mike Chu, 曾錦程 KC Tsang, 胡湘雲, 龔大中, 吳念真)

**Disqualifying types** (move to `format-templates/` or `register-references/`, NOT voice library):
- Magazines / newspapers / wire services with rotating authors (天声人語, 東洋経済, 日経ビジネス, Reuters, 中央社, 天下雜誌, 商業周刊, 報導者)
- Institutional platforms / SNS / IP (研之有物, 故宮粉絲團, 台灣吧, OPEN 將, 交通部)
- Brand house-style guides without a single named author (Mailchimp as institution, Innocent as brand, Patagonia as brand, Oatly as brand)
- E-commerce platforms with distributed authorship (PChome, MOMO, Shopee)
- Campaign-level entries without clear individual authorship
- Documented movements / genres (XR Declaration civic-declarative — kept as mitigation-only reference, not anchor)

### Rationale

Voice emerges from a consistent sentence-level sensibility exercised repeatedly. Institutional / brand / campaign entities have rotating authorship, producing a FORMAT / PROTOCOL / TEMPLATE, not a voice. These are valuable references but belong elsewhere — Pass 3 anchor-loading cannot distill voice from a template.

### Recast rule

If an apparently-institutional entry has a single documentable creator-author, recast:
- ✅ Mailchimp → Kate Kiefer Lee (author of original style guide)
- ✅ Innocent Drinks → Richard Reed (co-founder, voice architect)
- ✅ Duolingo 2021-2022 → Zaria Parvez (individual social lead)
- ✅ Steak-umm Twitter → Nathan Allebach (individual account operator)
- ✅ 全聯 TV-era → 龔大中 (奧美 ECD, already in craft-lineage)
- ✅ 大眾銀行 TVC → 胡湘雲 (奧美 CD)
- ✅ 保力達B → 吳念真 (口白 + 文案)
- ✅ 中興百貨 → 許舜英 (already in craft-lineage)

If no single creator can be named, move entry out of voice library.

### Boundary: what about craft-gate masters whose corpus spans multiple campaigns?

Craft-gate masters (許舜英, 李欣頻, 葉明桂, 糸井, 岩崎, 眞木, 谷山 + recast: 朱家鼎, 曾錦程, 龔大中, 胡湘雲, 吳念真, 梅田, Kate Kiefer Lee, Richard Reed, Zaria Parvez, Nathan Allebach) are IN the voice library. Their campaign work is IN the Layer 2/3 research docs as examples. The master is the anchor; the campaign is an example.

### Boundary: documented movements (XR, Nike Dream Crazy, XR Declaration)

These remain cited in meta-core over-mimic registry as mitigation references but are NOT voice anchors. They inform what NOT to copy; they don't qualify as what TO copy.

## Layer 1 schema (the only thing in skill)

Each anchor entry in `standards/{lang}-q{N}-anchors.md` uses this structure:

```markdown
### {anchor name} ({culture} | {quadrant} {landmark position})

## Voice direction
**What this register achieves**: {one-line summary of the register's intent — what emotional / rhetorical goal}

**Native critical read** (≥3, verbatim vocabulary from critics or author themselves):
- 「{term / phrase}」({source: critic name / publication / author-self-citation})
- ...

## Prose mechanics (≥5, actionable, concrete)
- {Rule 1 — specific enough to execute (what to do / avoid, mechanically)}
- {Rule 2}
- ...

## Examples (≥5 verbatim, with source work / year)
- 「{verbatim line}」({work, year, optional character / context})
- ...

## Don't / Over-mimic
- **Failure mode**: {what LLM defaults into when trying this register}
- **Mitigation** (≤15 words): "{actionable clause}"

## Trigger slug: {culture}-{kebab-name}-{style-label}
## Over-mimic risk: LOW / MEDIUM / HIGH / HIGH+
## Cross-reference-valid-for (optional): {other-lang}: STRONG / MEDIUM / WEAK
## Safe substitute for (optional, v1.10.0+): [higher-over-mimic-risk-master-name, ...]
```

### `Safe substitute for` (optional, v1.10.0+)

Lists higher-over-mimic-risk masters this anchor can be used as a **lower-risk substitute** for. Enables Pass 3 auto-selector to prefer a safer alternative when the user-specified master has HIGH over-mimic risk + this anchor delivers adjacent register at LOWER risk.

Example: `anchor-jp-yoshimoto-banana-j-bungaku.md` declares `safe_substitute_for: [村上春樹]` — when a brief requests 村上春樹 register, Pass 3 auto-selector may suggest 吉本ばなな as safer alternative (same peer-intimate cadence, without Murakami's HIGH-risk cats/jazz/wells tropes).

Must carry **frontmatter field** (not prose only) so Pass 3 can query deterministically. Pass 3 queries: `any anchor where {higher-risk-master} ∈ safe_substitute_for[]`.

Only applies when:
1. Higher-risk master is in meta-core Over-mimic mitigation registry (documented pastiche risk)
2. Substitute anchor delivers adjacent register empirically verified (native critical read or agent-run E2E evidence)
3. Substitute anchor's own over-mimic risk is LOWER than target master's

## Field definitions

### `Voice direction`

Single sentence capturing what the register is ATTEMPTING. Not biographical, not the author's life-summary. Example:

✅ "Capture everyday kitchen domesticity as silent action-chain; emotion surfaces via physical detail, never explicit statement."
❌ "Essayist + TV scriptwriter active 1960s-80s, famous for 真打ち essays."

### `Native critical read`

Verbatim phrases used natively in the anchor's own critical tradition. Must be attributable. Acceptable sources:
- Author's self-description in interviews / books
- Published critic reviews (with name / outlet)
- Academic papers (with citation)
- Industry trade-press critical vocabulary (動腦 / 宣伝会議 / 廣告 / ADM etc.)

NOT acceptable:
- Our own classification ("post-糸井 世代")
- Translated English concepts applied back ("peer-warm register")
- Wiki-only summary lines without author or critic attribution

**Minimum 3, target 4-6**. Each must have source tag.

### `Prose mechanics`

Rules actionable at the sentence / paragraph level. Must answer "if I'm writing in this voice, what do I mechanically do or avoid?"

✅ Actionable:
- "Avg sentence length < 20 chars"
- "体言止め chain 3-5 consecutive"
- "No abstract nouns (愛 / 孤独 / 希望) in headline"
- "Humor forbidden in error states"
- "Compressed concessive `不在乎 X, 只在乎 Y` sentence once per piece"

❌ Too abstract:
- "Use warm register"
- "Emotional resonance"
- "Peer-to-peer feeling"
- "Distinctive voice"

**Minimum 5, target 6-8**. If you can't get 5 actionable rules for an anchor, the anchor is thin and the gap must be flagged.

### `Examples`

Verbatim representative lines from the anchor's corpus. Source-attributed. These are what Pass 3 uses for pattern-match.

**Minimum 5, target 6-10**. Coverage should span the register's range, not cluster on one famous line.

- Verbatim only (no paraphrase)
- Source: work name + year + optional context (character / campaign)
- If a work's specific copy cannot be verbatim-verified, tag "attributed commonly, exact source TBD"

### `Don't / Over-mimic`

Two fields:
- **Failure mode** — what LLM defaults into when asked for this register (not generic "hallucination" — specific to this anchor)
- **Mitigation** — actionable clause, ≤15 words, directly injectable as Pass 3 prompt

Dimension 6 (voice-consistency-gate) reads this directly from the anchor file (v2 change — previously read from separate meta-core registry). Single source of truth.

### Metadata trailing

- `Trigger slug` — unchanged from v1
- `Over-mimic risk` — LOW / MEDIUM / HIGH / HIGH+ (HIGH+ reserves for craft-gate masters)
- `Cross-reference-valid-for` — optional, directional strength

## What's NOT in Layer 1 (moves to Layer 2/3 research docs)

- Era / birth-death years / active period
- Agency / creator career path
- Primary source URLs (beyond the critic citations in `Native critical read`)
- Awards history
- Cross-cultural equivalents
- LLM corpus depth (relocated to `docs/voice-anchor-deep-dives/{slug}.md`)
- Cultural / historical context
- Lineage documentation (who influenced whom — moves to `voice-anchor-meta-detail.md`)

**Test**: if you can't explain how a field helps Pass 3 rewrite a draft, it doesn't belong in Layer 1.

## Layer 2/3 location

`docs/voice-anchor-deep-dives/{slug}.md` holds:
- Full research notes
- Primary source citations with URL / ISBN
- Biographical / era context
- Awards / agency timeline
- Critical history and debates
- Documented lineage influences

These are audit / provenance artifacts. Pass 3 does NOT load them. Dimension 6 evaluator may optionally cite them in rationale.

## Pilot scope (v1.4.0)

8 anchors reformatted to v2 schema using existing research agent output:
- 坂元裕二 (JP Q3 center)
- 梅田悟司 (JP Q3 toward-Q2)
- 宮沢賢治 (JP Q3 extreme)
- 朱家鼎 Mike Chu (zh-HK Q2 extreme)
- 曾錦程 KC Tsang (zh-HK Q2 toward-Q1)
- 研之有物 (zh-TW Q1 center)
- 故宮粉絲團 (zh-TW Q3 extreme)
- Mailchimp (EN Q3 center)

After reformat, score each for Layer-1 coverage. Decision fork based on aggregate coverage → shape how remaining 98 anchors are migrated.

## Migration rule (post-pilot)

If pilot coverage is acceptable:
- Ship v2-schema'd pilot 8 anchors
- Meta-core over-mimic registry stays (Dimension 6 still works)
- Remaining 98 anchors keep v1 format until their turn comes
- Pass 3 SKILL.md reads both schemas (additive check)

If pilot coverage is insufficient:
- Adjust research agent prompt to explicitly target mechanics + examples over biography
- Re-run pilot anchors' research with new prompt
- Re-score before proceeding

## Validation criteria

Anchor passes Layer-1 coverage IF AND ONLY IF:
- `Voice direction` present (1 line, substantive)
- `Native critical read` has ≥3 attributed phrases
- `Prose mechanics` has ≥5 actionable rules
- `Examples` has ≥5 verbatim with source
- `Don't / Over-mimic` has both failure mode + ≤15-word mitigation

4/5 pass → acceptable. 3/5 pass → research gap, iterate. <3/5 → research pipeline inadequate.
