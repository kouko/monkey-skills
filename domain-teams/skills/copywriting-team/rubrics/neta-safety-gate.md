---
title: Neta Safety Gate (SHOULD)
tier: gate
---

# Neta Safety Gate Rubric (SHOULD)

## Evaluation Instructions

You are a strict auditor. Evaluate neta-injected copy across five
dimensions. For each dimension, produce a traffic-light flag:
**🔴 Red / 🟡 Yellow / 🟢 Green** with specific evidence and
reasoning.

Two dimensions are **hard legal vetoes** — any unmitigated Red on
these blocks delivery regardless of other dimensions:
- Copyright / trademark risk
- 景品表示法 ステマ risk (JP)

The other three dimensions aggregate per Verdict Rules below.

**Grounds on**:
- `../standards/neta-injection-techniques.md`
- `../standards/neta-source-taxonomy.md`
- `../standards/neta-websearch-pipeline.md`
- `../standards/persuasion-ethics.md`

## Scope

This gate applies to copy where neta injection has been applied (per
`protocols/copy-neta-injection.md` output). It does NOT apply to copy
that deliberately avoided neta injection. If the artifact contains
no cultural reference (pop culture / subculture / meme / literary
allusion / classical quotation / famous phrase / 固有名詞), return
`NOT_APPLICABLE` for every dimension and verdict `PASS`.

## Primary sources for rubric dimensions

### Copyright + trademark (hard veto)

- **17 U.S. Code § 107** — fair use four factors (purpose, nature,
  amount, market effect).
  https://www.law.cornell.edu/uscode/text/17/107
- **Campbell v. Acuff-Rose Music, 510 U.S. 569 (1994)** — SCOTUS
  parody fair use; transformative-use doctrine (Opinion by Souter).
- **Louis Vuitton Malletier S.A. v. Haute Diggity Dog, LLC, 507
  F.3d 252 (4th Cir. 2007)** — parody trademark dual-message test.
- **Japan 著作権法 32条** — 引用 (quotation) permission. Judicial
  doctrine: 主従関係 + 明瞭区別性 (モンタージュ写真事件 最高裁
  昭和55年).

### 景品表示法 ステマ告示 (hard veto, JP)

- **消費者庁** official documentation: 景表法 5条 3号 告示 +
  2023-03-28 運用基準. Enforcement from 2023-10-01.
  https://www.caa.go.jp/policies/policy/representation/fair_labeling/stealth_marketing/

### Subcultural + signaling anchors

- **Thornton, S.** (1995) *Club Cultures: Music, Media and
  Subcultural Capital*. Wesleyan UP.
- **Spence, M.** (1973) "Job Market Signaling." *QJE* 87(3),
  355–374.
- **Bourdieu, P.** (1984/1979) *Distinction*. Harvard UP.

### Meme lifecycle

- **Shifman, L.** (2014) *Memes in Digital Culture*. MIT Press.
- **Cambridge *Humor 2.0* Ch. 16** "Half-Life of a Meme" —
  lifespan data ≈4-6 months.

## Critical Attribution Corrections

- **Drift #23: "Transformative use" was NOT coined in Campbell
  1994.** The concept was articulated earlier by **Judge Pierre N.
  Leval** in (1990) "Toward a Fair Use Standard," *Harvard Law
  Review*, 103(5), 1105–1136. Campbell adopted Leval's formulation.
  Leval predates Campbell by 4 years.

- **Drift #24: 主従関係 and 明瞭区別性 are NOT in 著作権法 32条
  statutory text.** They are judicial doctrine layers developed
  through case law (anchored on モンタージュ写真事件 最高裁 昭和55年).
  Do not cite them as "32条の要件."

## Rubric Dimensions

### Dimension 1: Copyright / Trademark Risk (HARD VETO)

**What to evaluate**: Does the neta injection create copyright or
trademark infringement exposure?

**Key tests**:

1. **US fair use four factors** (17 USC § 107):
   - Purpose and character (transformative use per Campbell 1994 —
     note the doctrine precedes Campbell via Leval 1990)
   - Nature of the copyrighted work
   - Amount and substantiality used
   - Effect on the market for the original

2. **Parody trademark dual-message** (Louis Vuitton v. Haute
   Diggity Dog 2007): does the use communicate both (a) it IS the
   original reference and (b) it is NOT the original?

3. **JP 著作権法 32条 引用**: does the use satisfy judicial
   doctrine of **主従関係** (reference is subordinate to original
   content) and **明瞭区別性** (reference is clearly distinguished
   from original work)?

**Flag criteria**:

- 🟢 **Green**: clear fair use / parody / 32条 applicability. No
  trademark dilution. Use a widely-documented meme / public-domain
  reference / transformative interpretation.
- 🟡 **Yellow**: plausible fair use but close call. Worth legal
  review for high-stakes campaigns. For lower-stakes (social post,
  internal) may proceed with attribution.
- 🔴 **Red (HARD VETO)**: direct reproduction of copyrighted
  material without transformative purpose, OR trademark use likely
  to confuse origin. Examples: reproducing a movie scene frame with
  product inserted; using a registered trademark in a way that
  suggests endorsement; verbatim song lyrics without license.

**Veto logic**: unmitigated 🔴 on this dimension → final verdict
`NEEDS_REVISION` regardless of other dimensions.

### Dimension 2: 景品表示法 ステマ Risk (HARD VETO, JP)

**What to evaluate**: For JP-market copy, could this content be
interpreted as stealth marketing under 消費者庁 2023-10-01 告示?

**Two-prong test** (per 景表法 5条 3号 告示 + 2023-03-28 運用基準):

1. **Brand-influence test**: is the brand involved in the content's
   creation or endorsement?
2. **Identifiability test**: can a general consumer identify the
   content as brand-influenced?

**If (1) = Yes and (2) = No → ステマ violation.** Brand is the
liable party.

**Flag criteria**:

- 🟢 **Green**: brand disclosure is explicit (PR表記, ad disclosure,
  branded account, paid partnership tag). No ambiguity about
  sponsorship.
- 🟡 **Yellow**: brand disclosure exists but may be less prominent
  than consumer would expect. Recommend prominence increase.
- 🔴 **Red (HARD VETO)**: content mimics organic UGC (user-
  generated content), uses insider framing that implies peer-to-peer
  rather than brand-to-consumer communication, AND brand sponsorship
  is not clearly identifiable. Example: Technique 3 Subcultural
  Capital (tribal signal / 界隈消費) executed in a way that reads
  as authentic fan-made content without clear ad marker.

**Veto logic**: unmitigated 🔴 on this dimension (for JP-market
content) → final verdict `NEEDS_REVISION` regardless of other
dimensions. Creator's use of neta does NOT shift liability — brand
is always the liable party.

**Non-JP markets**: adapt per local regulations (e.g., FTC Endorsement
Guides in US). If copy is not JP-market, this dimension becomes
advisory rather than hard veto; but cross-reference
`persuasion-ethics.md` for FTC rules.

### Dimension 3: Cringe Index (soft)

**What to evaluate**: does the copy read as earnestly clever, or
as cringingly out-of-touch / forced / misaligned?

**Documented failure precedents** (academic / industry):
- McDonald's #McDStories (2012) — brand-hashtag hijacked
- DiGiorno #WhyIStayed (2014) — pizza tweet on domestic-violence
  hashtag; public apology
- Pepsi Kendall Jenner "Live for Now" (2017) — protest-imagery
  parody read as trivializing; pulled within 24h
- ペヤング 異物混入 SNS mishandling (2014, JP)

**Academic anchor**: Kucuk, S. U. (2019) *Brand Hate: Navigating
Consumer Negativity*, Palgrave Macmillan — taxonomy of brand
backlash.

**Source-type-specific cringe patterns** (per
`neta-source-taxonomy.md` signaling axis model):

| Source type | Cringe failure mode |
|-------------|-------------------|
| SNS/Meme | **Out-of-touch**: dead meme, format misuse, "fellow kids" |
| Classical Lit | **Pretentiousness**: talking down to reader, brand seems elitist |
| Modern Lit | Pretentiousness OR **generational mismatch** |
| Quotes | **Cliché**: overused quote with zero compression power |
| Contemporary | Spoiler / **fandom mismatch** |

Literary-specific patterns:
- **Pretentiousness**: using obscure literary references to signal
  sophistication rather than to compress meaning. Brand voice must
  earn the literary positioning (Bourdieu cultural capital).
- **Misattribution cringe**: getting the quote wrong is worse for
  classical sources because the audience that recognizes the
  reference also recognizes the error. Verify via Path A-2 sources.
- **Pedagogical tone**: reference reads as "look how well-read I am"
  rather than serving the product message. The reference should
  compress meaning, not lecture.

**Flag criteria**:

- 🟢 **Green**: copy reads as authentically in-tune with target
  audience. Execution is confident, not trying too hard. Reference
  fits product message naturally (not forced). For literary sources:
  brand voice credibly supports the allusion's register.
- 🟡 **Yellow**: copy is generally on-tone but has 1-2 elements that
  feel slightly off (e.g., generationally misaligned word choice,
  overused template, slight forcing of product message onto
  reference, literary reference slightly above audience's comfort
  zone).
- 🔴 **Red**: copy reads as performative, out-of-touch, or
  misaligned. For SNS/Meme: executive-written-trying-to-be-youth-
  cool. For Literary: brand-trying-to-seem-intellectual without
  earned positioning. Forced reference that doesn't map to product.
  Uses a sensitive hashtag / context inappropriately.

### Dimension 4: Audience Capital Match (soft)

**What to evaluate**: does the reference match the target audience's
recognition profile? This dimension operates on **two signaling axes**
depending on source type (per `neta-source-taxonomy.md`):

- **Thornton's subcultural capital** (1995): for SNS/Meme and
  Contemporary Culture sources — "being in the know" within a
  specific subculture. Tests in-group membership.
- **Bourdieu's cultural capital** (1984): for Classical Lit, Modern
  Lit, and Quotes sources — education, cultural literacy,
  sophistication. Tests whether the audience's reading/education
  background includes the reference.

Peterson & Kern's omnivore thesis (1996) applies: high-status
audiences consume across both axes. The two are complementary, not
contradictory, but the failure modes differ.

**Academic anchors**: Thornton 1995, Bourdieu 1984, Peterson & Kern
1996, Spence 1973 signaling.

**Flag criteria**:

- 🟢 **Green**: target audience's profile matches the reference's
  recognition requirements. For subcultural capital: brand has
  credible in-group connection (earned, not performed). For cultural
  capital: audience's education/literacy band includes the reference;
  brand voice credibly supports the allusion's register.
- 🟡 **Yellow**: audience-reference match is partial. Some segment
  of intended audience will recognize, some will not. Mitigation:
  ensure fallback readability so non-recognizers still parse surface
  meaning. For literary sources: reference may be at the edge of the
  audience's cultural literacy.
- 🔴 **Red**: For subcultural sources: reference is in-group for a
  community adjacent to (not overlapping with) target audience;
  cultural-appropriation risk. For literary sources: reference
  requires education/literacy significantly above the audience's
  profile; reads as exclusionary rather than enriching. In either
  case: brand uses cultural token without genuine connection.

### Dimension 5: Timeliness / Currency (soft)

**What to evaluate**: is the reference timely for its source type?
Timeliness criteria differ by source category (per
`neta-source-taxonomy.md`):

**Anchors**:
- Shifman 2014 meme lifecycle (for SNS/Meme)
- Cambridge *Humor 2.0* Ch. 16 half-life: ≈4-6 months (for SNS/Meme)
- Bourdieu 1984 cultural capital (for literary — recognition depends
  on education, not temporal currency)

**Source-type-aware flag criteria**:

- 🟢 **Green**:
  - *SNS/Meme*: current within meme half-life window (≤6 months)
    with 2+ independent source verification
  - *Classical Lit*: reference is canonical and within target
    audience's cultural literacy (evergreen — no expiry)
  - *Modern Lit*: reference is well-known to target generation OR
    experiencing active cultural rediscovery (adaptation, anniversary)
  - *Quotes*: reference is widely recognized AND not yet cliché
    (still carries compression power)
  - *Contemporary Culture*: within 1-5 year recognition window for
    the specific medium
- 🟡 **Yellow**:
  - *SNS/Meme*: 6-12 months old; currency requires re-verification
  - *Modern Lit*: reference is 5-10 years from last cultural moment;
    context-dependent verification needed
  - *Quotes*: quote is approaching cliché status (still parseable
    but losing compression)
  - *Contemporary*: at the tail of its recognition window
- 🔴 **Red**:
  - *SNS/Meme*: >12 months old AND not classic. "Cringe by delay."
    Also red for memes that peaked and collapsed.
  - *Classical Lit*: red only if the reference's connotation has
    shifted due to recent cultural events (e.g., a quote newly
    associated with controversy) — otherwise classical sources do
    NOT receive red on timeliness
  - *Quotes*: dead cliché — overused to the point of carrying no
    compression at all ("Be the change," "Think different" in
    non-Apple context)
  - *Modern Lit*: >10 years from last cultural moment without active
    rediscovery; recognition has decayed for the target generation

## Verdict Rules

### Step 1: Check hard vetoes

If **Copyright/Trademark (Dim 1)** OR **景表法 ステマ (Dim 2,
JP-market)** is unmitigated 🔴:
→ Final verdict `NEEDS_REVISION`.
→ Mandatory fix: resolve the legal risk before any other
  consideration. Other dimensions are moot until legal vetoes clear.

### Step 2: Aggregate soft dimensions (Dim 3/4/5)

Only if hard vetoes clear (all Green or Yellow, or Red with
documented mitigation):

- All 3 soft dimensions 🟢 → `PASS`
- 1-2 soft dimensions 🟡, rest 🟢, no 🔴 → `PASS_WITH_NOTES`
- Any soft dimension 🔴 → `NEEDS_REVISION`
- 3 soft dimensions 🟡 → `NEEDS_REVISION` (too many concerns to
  ship without revision)

### Step 3: Confidence caveat

Record confidence level per dimension. For low-confidence Green
flags (e.g., "I believe this is fair use but I'm not a lawyer"),
downgrade to Yellow with the caveat noted.

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "hard_vetoes_status": "CLEAR | TRIGGERED",
  "dimensions": [
    {
      "id": "copyright_trademark",
      "flag": "🟢 | 🟡 | 🔴",
      "is_hard_veto": true,
      "evidence": "specific reasoning with source-citation to 17 USC § 107 / Campbell / Louis Vuitton / 著作権法 32条",
      "mitigation_if_applicable": "..."
    },
    {
      "id": "stema_景表法",
      "flag": "🟢 | 🟡 | 🔴 | NOT_APPLICABLE (non-JP market)",
      "is_hard_veto": true,
      "evidence": "specific reasoning against 消費者庁 2023-10-01 告示 two-prong test",
      "mitigation_if_applicable": "..."
    },
    {
      "id": "cringe_index",
      "flag": "🟢 | 🟡 | 🔴",
      "is_hard_veto": false,
      "evidence": "specific reasoning with audience profile + reference execution quality"
    },
    {
      "id": "in_group_match",
      "flag": "🟢 | 🟡 | 🔴",
      "is_hard_veto": false,
      "evidence": "audience-reference match assessment"
    },
    {
      "id": "timeliness",
      "flag": "🟢 | 🟡 | 🔴",
      "is_hard_veto": false,
      "evidence": "meme currency assessment; include WebSearch verification timestamp if applicable"
    }
  ],
  "confidence_note": "per-dimension confidence + any caveats",
  "recommended_fix": "if NEEDS_REVISION, specific next steps"
}
```

## Anti-Patterns

- **Waiving hard vetoes because soft dimensions are all Green.**
  Legal risk is non-fungible with taste risk. A 🔴 on copyright or
  ステマ blocks delivery even if cringe / in-group match (Subcultural
  Capital) / timeliness are all 🟢.
- **Skipping the two-prong ステマ test for JP-market content.**
  The brand-influence + identifiability test is mandatory for any
  JP-facing copy that references or resembles UGC.
- **Citing "transformative use" as a Campbell 1994 invention.**
  Leval 1990 *Harvard L. Rev.* predates Campbell by 4 years
  (drift #23).
- **Treating 主従関係 / 明瞭区別性 as statutory text of 著作権法
  32条.** These are judicial doctrine layers (drift #24).
- **Evaluating timeliness without WebSearch verification.**
  Currency requires empirical check; pre-training knowledge is
  insufficient.
- **Green on in-group (Subcultural Capital) match without evidence
  of earned brand-community connection.** "We THINK this is our
  audience's subculture" is not the same as "we KNOW this audience
  recognizes us as legitimate in-group." For Technique 3
  (Subcultural Capital / tribal signal / 界隈消費) especially,
  require evidence of earned position.
- **Passing a single-source currency verification.** Meme lifespan
  variance requires 2+ independent sources before confirming
  "current."
- **Returning PASS on ambiguous Yellow-heavy output.** If three
  dimensions are Yellow, that's three concerns; pass threshold
  should be tighter.
