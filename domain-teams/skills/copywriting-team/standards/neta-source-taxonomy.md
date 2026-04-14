---
title: Neta Source Taxonomy — Source Types for Cultural-Reference Injection
tier: 3
---

# Neta Source Taxonomy

Tier 3 standard: fully self-contained. Codifies the **source types
(取材類型)** from which neta injection draws reference material. This
standard is orthogonal to `neta-injection-techniques.md`, which defines
**transformation techniques (轉化技法)** — the operations applied to
source material. The two axes are independent: any technique can operate
on any source type, with varying effectiveness documented in the
compatibility matrix below.

## Primary Sources

### Intertextuality and allusion theory

- **Kristeva, J.** (1969) *Séméiôtikè: recherches pour une sémanalyse*.
  Seuil. **Foundational.** Coins "intertextualité": "any text is
  constructed of a mosaic of quotations; any text is the absorption and
  transformation of another." Framework within which all neta injection
  operates.
- **Genette, G.** (1982) *Palimpsestes: La littérature au second degré*.
  Seuil. **Canonical.** 5 types of transtextuality. Neta injection maps
  primarily to **intertextuality** (allusion) and **hypertextuality**
  (transformation of source into new text).
- **Ben-Porat, Z.** (1976) "The Poetics of Literary Allusion." *PTL*,
  1, 105–128. **Canonical.** Formalizes allusion as: marker recognition
  → source activation → interpretive mapping. Parallels the neta
  3-condition framework (Recognition → Compression → Relevance).

### Classical Japanese literary allusion

- **藤原定家** (c. 1209)《近代秀歌》(*Kindai Shūka*). **Canonical.**
  Codifies 本歌取り (honkadori) rules: word-limit (2–3 of 5 ku),
  mandatory topic shift (心の転換), canonical source requirement.
- **Brower, R. H. & Miner, E.** (1961) *Japanese Court Poetry*.
  Stanford UP. **Canonical.** English-language definitive treatment;
  translates honkadori as **"allusive variation."**
- **佐藤信夫** (1992/1978) *『レトリック感覚』*. 講談社学術文庫.
  **Canonical JP rhetoric.** Covers 引喩 (allusion) with 本歌取り as
  canonical Japanese example.

### Cultural capital and audience signaling

- **Bourdieu, P.** (1984/1979) *Distinction*. Harvard UP. **Canonical.**
  Cultural capital (embodied / objectified / institutionalized) as the
  signaling axis for literary allusion. Already cited in
  `neta-injection-techniques.md` for Technique 3 (via Thornton 1995).
- **Peterson, R. A. & Kern, R. M.** (1996) "Changing Highbrow Taste:
  From Snob to Omnivore." *ASR*, 61(5), 900–907. **Canonical.** The
  omnivore thesis: high-status audiences consume across highbrow/lowbrow
  boundaries. Literary and meme audiences may overlap.

## Critical Attribution Corrections

- **Drift #23**: Kristeva's intertextuality is NOT limited to intentional
  allusion — it covers all text-to-text relations. Neta injection uses
  only the intentional subset (Genette's "intertextuality" + Ben-Porat's
  "allusion"). Cite Kristeva as foundational framework; cite
  Ben-Porat/Genette for allusion specifically.
- **Drift #24**: The mapping of 本歌取り to the neta injection
  3-condition framework (Recognition / Compression / Relevance) is
  **this team's interpretive synthesis**. The structural isomorphism is
  strong (see mapping table below), but cite Brower & Miner + Teika's
  rules as primary sources; flag the mapping itself as analytical
  synthesis.

## Two-Axis Design

Neta injection operates on two independent axes:

| Axis | Defined in | Content |
|------|-----------|---------|
| **Source types (取材類型)** | This standard | WHERE / WHAT the reference comes from |
| **Transformation techniques (轉化技法)** | `neta-injection-techniques.md` | HOW the reference is transformed into copy |

This separation prevents conflating "what kind of material" with "what
operation is applied." A classical-literature quote (source type) can
undergo Reversal (technique); a meme template (source type) can undergo
Substitution (technique). The source determines retrieval method and
quality criteria; the technique determines the rhetorical operation.

## Source Categories

### Category 1: SNS / Meme (existing)

**Definition**: Internet-native references — trending hashtags, viral
formats, platform-specific content, meme templates, 流行語.

**Retrieval**: WebSearch-first (Path A-1). LLM pre-training unreliable
for fast-moving content; real-time retrieval is mandatory.

**Timeliness model**: Half-life ≈4–6 months (Shifman 2014; Cambridge
*Humor 2.0* Ch. 16). References >12 months old are expired unless they
have become "classic" memes with continued recognition.

**Signaling axis**: Thornton's subcultural capital — "I am in the know."

**Quality criteria**: currency (is it still alive?), in-group fit
(does the target audience's subculture use this?), platform match.

### Category 2: Classical Literature (new)

**Definition**: Pre-modern canonical texts with centuries-scale
recognition: 万葉集, 源氏物語, 古今和歌集, 唐詩, 宋詞, 論語, 孟子,
Shakespeare, Homer, Bible, Greek/Latin classics.

**Retrieval**: Parametric-first (Path A-2). LLMs reliably know canonical
literature. WebSearch used for **attribution verification** (correct
author, correct wording, correct context) — not for discovery.

**Timeliness model**: **Evergreen.** No expiry. Recognition depends on
audience education level, not temporal currency. Quality check =
"does the target audience's cultural literacy include this?"

**Signaling axis**: Bourdieu's cultural capital — "I am educated /
cultivated." Brand positioning: premium, heritage, intellectual.

**Quality criteria**: audience recognition (education-dependent),
attribution accuracy (misquotation is worse than for memes because the
audience that recognizes the reference also recognizes errors),
authenticity (brand must earn the literary positioning).

**JP precedent**: 本歌取り (allusive variation). 藤原定家's rules map
directly to the neta 3-condition framework:

| Neta condition | 本歌取り rule | Teika's prescription |
|----------------|--------------|---------------------|
| Recognition | Source must be canonical | 三代集 era; well-known poems only |
| Compression | Borrowed elements carry full weight of original | 2–3 ku invoke entire emotional world |
| Relevance | Must map onto new meaning | 心の転換: topic MUST differ from original |

**Analytical synthesis disclaimer**: This mapping is this team's
interpretive synthesis. Cite Brower & Miner 1961 + Teika's rules as
primary sources.

### Category 3: Modern Literature (new)

**Definition**: Post-industrial canonical and popular literature with
decades-scale recognition: 夏目漱石, 太宰治, 村上春樹, 魯迅, 張愛玲,
Hemingway, Fitzgerald, Kafka.

**Retrieval**: Parametric-first (Path A-2) with WebSearch verification.

**Timeliness model**: **Long-lived** (decades-scale). Recognition
correlates with cultural literacy and generational reading patterns.
Some works gain renewed recognition through adaptations, anniversaries,
or cultural rediscovery (e.g., *Gatsby* after the 2013 film).

**Signaling axis**: Bourdieu's cultural capital, filtered by
generational reading trends. A 太宰治 reference signals differently to
a 20-year-old (recently encountered in 国語 education or anime
adaptations) vs. a 50-year-old (personal literary history).

**Quality criteria**: audience-generation fit, adaptation-driven
recognition cycles, cliché risk (some quotes are overused to the
point of losing compression power).

### Category 4: Famous Quotes / Aphorisms (new)

**Definition**: Widely attributed phrases, proverbs, 成語/四字熟語,
ことわざ — detached from their full-text source and circulating as
standalone units.

**Retrieval**: Parametric-first (Path A-2). WebSearch for **attribution
accuracy** — misattribution of quotes is extremely common (Twain,
Einstein, Churchill are chronic misattribution targets).

**Timeliness model**: **Evergreen to long-lived.** The primary risk is
not expiry but **cliché** — overused quotes lose compression power.
"Be the change" (misattributed to Gandhi) is recognized but carries
no fresh meaning.

**Signaling axis**: Mixed. Some quotes signal cultural capital
(literary/philosophical); others signal folk wisdom (proverbs,
ことわざ); others signal professional identity (industry-specific
maxims).

**Quality criteria**: attribution accuracy (misattribution cringe),
cliché index (has the quote been used so often that it compresses
nothing?), audience relevance.

**ZH-JP shared canon**: 成語 / 四字熟語 are shared neta material —
many JP 四字熟語 originate from漢典 (論語, 孟子, 史記, 漢書), giving
cross-linguistic audience recognition. 漢詩 (李白, 杜甫, 白居易) is
part of JP 国語教育 — JP audiences have baseline recognition of
classical Chinese poetry.

### Category 5: Contemporary Culture (clarified)

**Definition**: Non-platform-native pop culture — film, TV, music,
anime, manga, games. Distinct from SNS/Meme in that the reference
originates in produced media, not user-generated content.

**Retrieval**: WebSearch + parametric. Currency matters but on a
longer timescale than memes.

**Timeliness model**: 1–5 year half-life depending on medium. Film
quotes can persist longer than meme templates. Anime/manga references
have dedicated fandom that extends recognition windows.

**Signaling axis**: Mixed Bourdieu/Thornton depending on the specific
reference. A Miyazaki film reference operates on broader cultural
capital; a niche seasonal anime reference operates on subcultural
capital.

**Quality criteria**: audience recognition (fandom-dependent), spoiler
risk (for recent works), franchise longevity.

## Retrieval Path Architecture

### Path A-1: WebSearch-first (SNS/Meme, Contemporary Culture)

Current Phase A pipeline in `neta-websearch-pipeline.md`. No change.
- Discovery via site-locked WebSearch (existing domain allow-list)
- Recency filter: meme half-life ≈4–6 months
- Currency verification: 2+ independent sources

### Path A-2: Parametric-first (Classical Lit, Modern Lit, Quotes)

New retrieval path for literary/classical sources.
- **Discovery**: LLM parametric knowledge. Classical literature is
  well-represented in training data; discovery does not require
  WebSearch.
- **Verification**: WebSearch for attribution accuracy.

  **3-language verification allow-list (JP / EN / ZH)**:

  | Category | JP Sources | EN Sources | ZH Sources |
  |----------|-----------|------------|------------|
  | Classical Lit | 青空文庫 (aozora.gr.jp); 国立国会図書館デジタルコレクション (dl.ndl.go.jp); J-STAGE | Project Gutenberg (gutenberg.org); Perseus Digital Library (perseus.tufts.edu); Internet Archive (archive.org) | 中國哲學書電子化計劃 (ctext.org); 維基文庫 (zh.wikisource.org) |
  | Modern Lit | 青空文庫 (著作権切れ); 新潮社/岩波書店カタログ | Project Gutenberg; Open Library (openlibrary.org) | 維基文庫; 中國現代文學館 |
  | Quotes / Aphorisms | 故事ことわざ辞典; コトバンク (kotobank.jp) | Wikiquote (en.wikiquote.org); Oxford Dictionary of Quotations | 維基語錄 (zh.wikiquote.org); 成語典 (dict.idioms.moe.edu.tw) |
  | Shared Classical Canon | 漢文 (漢詩・論語・孟子 — JP 国語教育で共有) | — | ctext.org (原典) |

- **Audience-recognition check** replaces currency check:
  "Does the target audience's cultural literacy include this reference?"
  (Education level, generational reading patterns, cross-cultural canon
  overlap.)

### Path selection rule

Source-type routing occurs at the start of Phase A in
`copy-neta-injection.md`. When intake specifies
`neta_source_type_preference`:
- `sns-meme` → Path A-1 only
- `literary` → Path A-2 only
- `all` or `mixed` → both paths; candidate catalog merges results

## Compatibility Matrix (Source Type × Technique)

| Source Type | Reversal | Substitution | Subcultural Capital | Cross-domain Mapping |
|-------------|----------|-------------|--------------------|--------------------|
| **SNS/Meme** | natural | natural | natural | possible |
| **Classical Lit** | natural (本歌取り precedent) | possible (snowclone on canonical phrases) | narrow (literary-educated only) | natural |
| **Modern Lit** | natural | possible | narrow (generation-dependent) | natural |
| **Famous Quotes** | natural | natural (template-fill on well-known structures) | narrow | possible |
| **Contemporary Culture** | natural | natural | possible (fandom-dependent) | natural |

**Reading the matrix**:
- **natural**: technique-source combination is well-established with
  canonical precedent or strong structural fit
- **possible**: combination works with care; success depends on
  audience specifics
- **narrow**: combination works only for a narrowly defined audience
  segment; higher cringe risk for broader audiences

**Analytical synthesis disclaimer**: this compatibility matrix is this
team's practical assessment. Individual cells are informed by the
primary sources cited above but no single academic paper maps technique
× source types in this configuration.

## Signaling Axis Model

| Source Type | Primary Signaling Axis | Cringe Failure Mode |
|-------------|----------------------|-------------------|
| SNS/Meme | Thornton subcultural capital ("in the know") | Out-of-touch (dead meme, format misuse) |
| Classical Lit | Bourdieu cultural capital ("educated") | Pretentiousness (talking down to reader) |
| Modern Lit | Bourdieu + generational | Pretentiousness OR generational mismatch |
| Famous Quotes | Mixed (literary ↔ folk wisdom) | Cliché (overused, no compression left) |
| Contemporary Culture | Mixed Bourdieu/Thornton | Spoiler / fandom mismatch |

Peterson & Kern's omnivore thesis (1996): these axes are
**complementary, not contradictory**. High-status audiences consume
across the boundary. A piece of copy can combine a classical allusion
and a meme reference if the audience is omnivore-profile — but the
failure modes remain distinct.

## Anti-Patterns

- **Treating all neta sources as memes.** Classical literature has a
  fundamentally different retrieval method (parametric-first), timeliness
  model (evergreen), and signaling axis (cultural capital). Applying
  meme half-life checks to Shakespeare is category error.
- **Assuming literary references are universally recognized.** Classical
  sources are evergreen in canon status but NOT in audience reach.
  Recognition depends on education — always check audience literacy.
- **Misattributing quotes.** LLMs can misattribute quotes (e.g.,
  assigning Twain quotes to Einstein). WebSearch verification against
  the allow-list sources is mandatory for Path A-2.
- **Using literary references decoratively.** The 3-condition test
  (Recognition + Compression + Relevance) applies equally to literary
  sources. A Kafka reference that doesn't carry product meaning is
  decorative pretentiousness, not compression.
- **Conflating source type with technique.** "Subcultural Capital" is a
  transformation technique (how you use a reference), not a source type
  (where the reference comes from). A classical-literature reference
  can be used as Subcultural Capital if the target audience is a
  literary in-group — the source is classical, the technique is
  Subcultural Capital.
- **Skipping attribution verification for literary sources.** Parametric
  retrieval means the LLM "knows" the reference, but knowing ≠ correct
  attribution. Always verify author, exact wording, and context.
- **Mixing too many source types in one piece.** One source type per
  piece is generally safer than mixing. A piece that alludes to both
  Shakespeare and a TikTok meme risks tonal whiplash unless the
  omnivore audience profile explicitly supports it.
