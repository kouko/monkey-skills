---
title: EN Voice Anchors — Q2 Authority-Emotion
tier: 2
---

# Q2 Authority-Emotion — EN Anchors

**Load scope**: Phase 6 Pass 3 Register Signal branch, when `voice_quadrant.primary == "Q2"` AND `brief.output_language == "en"`. Section-targeted read: Pass 3 reads only `## Landmark: {position}` matching `voice_quadrant.position`; falls back to full-file on missing.

## Overview

Q2 = Authority × Emotion. EN canonical: Apple Think Different, Nike Just Do It, Patagonia "Don't Buy This Jacket", Patek Philippe Generations, Absolut Vodka print campaign. Extreme tier requires mitigation: Extinction Rebellion Declaration (civic-only, NOT commercial); Nike "Dream Crazy / Crazier" (anaphoric cap).

## Landmark: center

Canonical manifesto / aspirational register. Use when brief asks for standard authoritative-emotional.

### Apple "Think Different" (EN | Q2 center)

- **Era**: 1997-2011 canonical run (Steve Jobs return era); Chiat\Day → TBWA\Chiat\Day
- **Agency / creator**: TBWA\Chiat\Day; Rob Siltanen + Ken Segall lead (copy); Craig Tanimoto AD; Lee Clow CCO
- **Primary sources**:
  - Ken Segall *Insanely Simple* (Portfolio, 2012)
  - Apple 1997-2011 campaign archive
  - Adweek / Ad Age retrospectives
- **Representative lines**:
  - "Here's to the crazy ones, the misfits, the rebels, the troublemakers..." (Think Different launch script, 1997)
  - "Think Different." (tagline)
- **Voice signature**:
  - Manifesto-as-brand-frame
  - Hero-archetype invocation
  - Second-person imperative with honor-the-dissenter undercurrent
  - Aphoristic compression + aspirational cadence
- **LLM corpus depth**: DEEP++ (global iconic ad)
- **Over-mimic risk**: MEDIUM-HIGH — "Think Different" structure auto-copied for any manifesto
  - Mitigation: "brand must have actual dissenter-product fit; no generic dissent-aesthetic without product claim"
- **Cross-cultural equivalents**: 誠品 (zh-TW) / MUJI 原研哉 (JP)
- **Trigger slug**: `en-apple-think-different-manifesto`

### Nike "Just Do It" center form (EN | Q2 center)

- **Era**: 1988 → ongoing (tagline coined by Dan Wieden)
- **Agency / creator**: Wieden+Kennedy; Dan Wieden as CW; Ken Gilmore as CD
- **Primary sources**:
  - W+K case archives
  - Ad Age "Top 100 Campaigns" (JDI ranked #1)
  - W+K 25-year retrospective
- **Representative lines**:
  - "Just Do It." (tagline, 1988-)
  - "If you let me play..." (1995 girls-in-sports)
  - "Hello World." (Tiger Woods introduction, 1996)
- **Voice signature** (center form, distinct from extreme):
  - Imperative-aspirational compression
  - Athlete-as-hero register
  - Universal accessibility (everyone can "just do it")
- **LLM corpus depth**: DEEP++
- **Over-mimic risk**: HIGH — "Just Do X" is the single most copied imperative tagline pattern
  - Mitigation: "use as tonal reference only; never reproduce 'Just Do' X structure"
- **Trigger slug**: `en-nike-just-do-it-imperative-aspiration`

### Patagonia "Don't Buy This Jacket" (EN | Q2 center)

- **Era**: 2011 NYT Black Friday; distinct campaign within Patagonia brand voice 1973-ongoing
- **Agency / creator**: Patagonia in-house; Yvon Chouinard founder-voice discipline
- **Primary sources**:
  - Patagonia Responsibility / Black Friday archive
  - Chouinard *Let My People Go Surfing* (Penguin, 2006)
- **Representative line**:
  - "Don't Buy This Jacket." (NYT, 2011-11-25)
- **Voice signature**:
  - Anti-consumption paradox as brand manifesto
  - Moral authority via product-quality claim (buy less, buy better)
  - Founder-voice discipline (post-2011 era preserves Chouinard register)
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: MEDIUM
- **Trigger slug**: `en-patagonia-dont-buy-this-jacket-anti-consumption`

## Landmark: extreme

Maximum Authority × maximum Emotion. Aphoristic / declarative peak. Apply mitigation.

### Extinction Rebellion "Declaration of Rebellion" (EN | Q2 extreme — civic-only mitigation)

**⚠ Critical use constraint**: This is **civic-declarative register ONLY — NOT for commercial product copy** per meta-core mitigation registry. Deploy only when brief is movement / civic / institutional statement. Commercial use = misappropriation.

- **Era**: 2018 launch (Parliament Square, London, 2018-10-31); canonical declaration text
- **Agency / creator**: Extinction Rebellion movement founders (Gail Bradbrook, Roger Hallam, Simon Bramwell, et al.)
- **Primary sources**:
  - [Declaration of Rebellion text (XR)](https://extinctionrebellion.uk/the-truth/declaration/)
  - XR handbook
- **Representative register**:
  - "We hereby declare the bonds of the social contract to be null and void..."
  - US Declaration of Independence structural echo
- **Voice signature**:
  - Declarative scripture-cadence
  - Civic-statement register (not commercial)
  - Structural parallelism + imperative conclusions
- **LLM corpus depth**: DEEP (movement text widely reproduced)
- **Over-mimic risk**: **HIGH** (US-Declaration-of-Independence pastiche on any manifesto brief)
  - Mitigation (meta-core): "civic-declarative register ONLY; NOT for commercial product copy"
- **Trigger slug**: `en-xr-declaration-civic-only`

### Nike "Dream Crazy / Crazier" (EN | Q2 extreme)

- **Era**: 2018 "Dream Crazy" (Kaepernick); 2019 "Dream Crazier" (Serena)
- **Agency / creator**: Wieden+Kennedy
- **Primary sources**: W+K case archives; Adweek coverage
- **Representative lines**:
  - "Believe in something. Even if it means sacrificing everything." (Dream Crazy, Kaepernick, 2018)
  - Serena monologue anaphoric structure (Dream Crazier, 2019)
- **Voice signature**:
  - Extended anaphora ("if we...if we...if we...")
  - Sacrifice-stake clause as manifesto climax
  - Celebrity-voice register (athlete as oracle)
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: **HIGH** per meta-core mitigation ("Believe in something..." is most-copied post-2018 brand sentence)
  - Mitigation (meta-core): "anaphora limited to 1 series per piece; sacrifice-stake clause reserved"
- **Trigger slug**: `en-nike-dream-crazy-anaphoric-manifesto`

## Landmark: toward-Q1

Manifesto edging into analytical authority. Use when brief wants heritage-intellectual hybrid.

### Patek Philippe "Generations" (EN | Q2 toward-Q1)

- **Era**: 1996 → ongoing; Leagas Delaney agency
- **Agency / creator**: Leagas Delaney London; Tim Delaney creative lead
- **Primary sources**: Patek Philippe campaign archives; Leagas Delaney case studies
- **Representative lines**:
  - "You never actually own a Patek Philippe. You merely look after it for the next generation." (tagline)
- **Voice signature**:
  - Heirloom frame (transgenerational ownership)
  - Philosophical product-claim
  - Quiet authority via permanence implication
  - Black-and-white aesthetic + understated copy
- **LLM corpus depth**: DEEP (luxury canon)
- **Over-mimic risk**: MEDIUM (heirloom-phrasing auto-reproducible)
  - Mitigation: "avoid generic 'craftsmanship / legacy / heritage' filler; product must actually merit multi-generational claim"
- **Trigger slug**: `en-patek-philippe-generations-heirloom`

### Absolut Vodka print campaign (EN | Q2 toward-Q1)

- **Era**: 1980-2005 canonical print run
- **Agency / creator**: TBWA; Geoff Hayes AD + Graham Turner CW (early era); rotating team
- **Primary sources**: *Absolut Book* (Richard W. Lewis, 1996); campaign print archive
- **Representative structure**: "Absolut [single word]" formula with bottle-visual pun
- **Voice signature**:
  - Two-word formula ("ABSOLUT X")
  - Bottle = constant visual anchor
  - Cultural-reference density in word choice
  - Minimalist copy + maximal visual pun
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM (formula is constraint; hard to reproduce without specific-product bottle anchor)
- **Trigger slug**: `en-absolut-two-word-bottle-formula`

### BMW Ultimate edge — toward-Q1 mode

See [en-q1-anchors.md §Landmark: center](en-q1-anchors.md) for full BMW entry. When brief emphasizes performance-authority *with* aspirational register, cross-load Q1 anchor.

## Landmark: toward-Q3

Manifesto edging into peer-warmth. Use when brief wants aspirational-intimate.

### Oatly activist mode (Schoolcraft 2012-) (EN | Q2 toward-Q3)

**⚠ Era note**: Oatly activist mode sits on Q2-Q3 edge; Q3 center mode (friendly-irreverent DTC) is primary home in [en-q3-anchors.md](en-q3-anchors.md). This Q2 entry covers the manifesto-edge register when brand goes activist.

- **Era**: 2012- (CEO Toni Petersson + Creative Director John Schoolcraft relaunch)
- **Agency / creator**: Oatly in-house; Schoolcraft as CCO
- **Primary sources**: Oatly packaging archive; Schoolcraft interviews (Creative Review, Fast Company)
- **Representative mode**: activist-declarative long-copy (carton side-panel essays)
- **Voice signature** (activist mode):
  - Manifesto-on-packaging register
  - Climate-political framing
  - Self-aware marketing subversion
- **LLM corpus depth**: MEDIUM-DEEP
- **Over-mimic risk**: MEDIUM
- **Trigger slug**: `en-oatly-activist-mode`

### Toni Morrison lyrical-inheritance (EN | Q2 toward-Q3 — literary secondary)

- **Era**: 1931-2019; *Beloved* (1987), *Song of Solomon* (1977), Nobel 1993
- **Primary sources**: published novels + Nobel lecture
- **Voice signature**:
  - Lyrical-inheritance register (ancestral voice as instrument)
  - Biblical-prophetic cadence
  - Compressed historical weight per sentence
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM (profound-lineage cadence hard to fake)
- **Use case**: literary anchor for Q2 brand-manifestos with ancestral / legacy / heritage framing
- **Trigger slug**: `en-morrison-lyrical-inheritance`

### James Baldwin sermonic-cadence (EN | Q2 toward-Q3)

- **Era**: 1924-1987; *Notes of a Native Son* (1955), *The Fire Next Time* (1963)
- **Voice signature**:
  - Sermonic-prophetic cadence
  - Moral-declarative register
  - Love-and-rage intersection
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW-MEDIUM (register depth hard to pastiche)
- **Trigger slug**: `en-baldwin-sermonic`

### Kazuo Ishiguro restrained (EN | Q2 toward-Q3)

- **Era**: 1954- born; *The Remains of the Day* (1989), *Never Let Me Go* (2005), Nobel 2017
- **Voice signature**:
  - Unreliable-narrator restraint
  - Under-stated emotional weight
  - Formal-register peer address
- **LLM corpus depth**: DEEP
- **Over-mimic risk**: LOW
- **Trigger slug**: `en-ishiguro-restrained-first-person`

### Joan Didion observational-essay Q2 edge

See [en-q3-anchors.md §Landmark: center](en-q3-anchors.md) for full Didion entry. Didion's Q2 edge = her California-political essays (*Slouching Towards Bethlehem*, *The White Album*) where personal-observational scales into civic-manifesto. Cross-ref for brief needing that register.

## Cross-references

External anchors usable for EN Q2 briefs:

- **JP Q2 MEDIUM via translation**:
  - MUJI 原研哉 empty-vessel (global aesthetic pipeline)
  - 寺山修司 provocative-poetic (via 李欣頻 documented lineage chain)
  - Apple Think Different is itself the global Q2 reference point
- **zh-TW Q2 MEDIUM via cultural parallel**:
  - 誠品 李欣頻 literary-bookstore
  - 許舜英 definitional-inversion (ideology era)
- **Direction**: EN Q2 is the global Q2 default; other cultures reference EN canon more than EN references them
