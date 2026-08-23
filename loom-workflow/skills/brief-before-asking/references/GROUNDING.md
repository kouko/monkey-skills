# Grounding — brief-before-asking

The skill's design choices map to established communication / HCI theory.
Citations below are web-verified (author, year, venue). Where an
attribution is commonly mistaken, a **⚠ correction** flags it — use the
corrected form, not the folk version.

> Load only when you need to justify or defend a design choice, trace it
> to a primary source, or extend the skill. Not needed at runtime.

## Why the failure happens

- **Curse of Knowledge** — Camerer, C., Loewenstein, G., & Weber, M.
  (1989), "The Curse of Knowledge in Economic Settings: An Experimental
  Analysis," *Journal of Political Economy* 97(5), 1232–1254. Popularized
  by Heath, C. & Heath, D. (2007), *Made to Stick*, Random House.
  - *Claim*: once you know something you can't un-know it, which degrades
    your ability to communicate with the less-informed.
  - *Designs it grounds*: the whole skill; specifically why
    self-classification ("is this briefing-worthy?") leaks after deep
    analysis, so the contract must be unconditional, not agent-judged.

- **Cognitive Load Theory** — Sweller, J. (1988), "Cognitive Load During
  Problem Solving: Effects on Learning," *Cognitive Science* 12(2),
  257–285.
  - *Claim*: when demands exceed working memory, learning/understanding
    suffers. **Intrinsic load** = inherent difficulty (irreducible);
    **extraneous load** = avoidable, from how it's presented (reducible).
  - *Designs it grounds*: jargon is extraneous load → Plain-Language-first
    + define-terms-on-first-use reduce it; Mode C's "Mental Model only,
    then pause" caps load instead of dumping 6 blocks.
  - ⚠ *germane load* is NOT in the 1988 paper — that 3-way model is
    Sweller, van Merriënboer & Paas (1998), *Educational Psychology
    Review* 10(3). Cite 1998 if you invoke germane load.

## Stakes-first / conclusion-first

- **Pyramid Principle** — Minto, B. (1987), *The Pyramid Principle: Logic
  in Writing and Thinking* (developed at McKinsey; expanded 1996).
  - *Claim*: structure top-down — lead with the governing answer, support
    with a MECE hierarchy.
  - *Designs it grounds*: "Lead with stakes, not mechanism"; My-take's
    explicit lean before the reasoning chain.
  - ⚠ "**SCQA**" is NOT Minto's acronym. Hers is **SCQ** (Situation–
    Complication–Question); "Answer" is the pyramid apex, not a 4th letter.
    SCQA is a later third-party relabel. Attribute the *concept* to Minto;
    do not attribute the *acronym SCQA* to her.

- **BLUF (Bottom Line Up Front)** — principle codified in *Army Regulation
  25-50, Preparing and Managing Correspondence* (HQDA, 10 Oct 2020),
  para 1-38b: "putting the main point at the beginning … (bottom line up
  front)."
  - ⚠ AR 25-50 never uses the *acronym* "BLUF" and does not claim to coin
    it — it codifies existing practice. No single citable coiner. Cite it
    for the principle only. (Paragraph numbering is revision-dependent.)

## When to ask vs act

- **Mixed-Initiative User Interfaces** — Horvitz, E. (1999), "Principles
  of Mixed-Initiative User Interfaces," *Proc. CHI '99*, 159–166. ACM.
  DOI: 10.1145/302979.303030.
  - *Claim*: blend automated services with direct user control; reason
    decision-theoretically about acting vs. deferring to the user.
  - *Designs it grounds*: the "is this a fork worth asking?" gate; also
    cited by loom's SDD + requesting-code-review "Asking the user" gates.

## What to say / how to adjust

- **Jobs-to-be-Done** — Christensen, C.M., Hall, T., Dillon, K., & Duncan,
  D.S. (2016), *Competing Against Luck*, Harper Business; HBR companion
  "Know Your Customers' Jobs to Be Done" (Sept 2016).
  - *Claim*: "customers don't buy products; they hire them to do a job" —
    articulate the job before the solution.
  - *Designs it grounds*: outcome-framed options ("what the user gets"),
    not mechanism labels.
  - ⚠ NOT in *The Innovator's Dilemma* (1997, about disruption) — a common
    misattribution. Origin is also contested with Ulwick's Outcome-Driven
    Innovation (HBR, Jan 2002).

- **Grounding in communication** — Clark, H.H. & Brennan, S.E. (1991),
  "Grounding in communication," in Resnick, Levine & Teasley (Eds.),
  *Perspectives on Socially Shared Cognition*, 127–149. APA.
  - *Claim*: partners interactively build **common ground** by giving and
    seeking evidence of understanding; the form of that evidence is shaped
    by the medium.
  - *Designs it grounds*: the repeated-confusion guard (a confusion signal
    is failed grounding → repair by reframing, not by adding detail).

- **Audience Design** — Bell, A. (1984), "Language Style as Audience
  Design," *Language in Society* 13(2), 145–204. Cambridge UP.
  - *Claim*: speakers adjust style primarily in response to their audience.
  - *Designs it grounds*: "phrase it for the warm-but-interrupted user who
    reads the rendered question" — register set by the reader, not the author.

## Layering

- **Progressive Disclosure** — popularized by Nielsen, J. (NN/g,
  "Progressive Disclosure," 2006), who notes the concept is "more than 30
  years old." Antecedents: Carroll & Rosson (IBM, 1983); Woolsey (Apple,
  1985, cited in Norman & Draper, *User Centered System Design*, 1986).
  - *Claim*: show the few options most users need first; defer advanced/
    rare ones to reduce load.
  - *Designs it grounds*: Mode C's "Mental Model first, then drill menu";
    this skill's own SKILL.md-body vs references/ split.
  - ⚠ Do NOT attribute the origin to Nielsen — he popularized (2006);
    documented antecedents are early-1980s. The literal coiner of the
    phrase is not authoritatively established.

## What is NOT externally grounded (our own synthesis)

Be honest about these — they are practitioner heuristics, not citable theory:

- **Mode D (stakes didn't land) ≠ Mode C (lost in jargon)** — this split
  was induced from a real session, not from a published taxonomy.
- **"2nd consecutive confusion = hard STOP"** — the *concept* of repair
  maps to Clark & Brennan grounding, but the specific count "2" is a
  chosen threshold with no theoretical backing.
- **L1 always-on contract vs L2 opt-in skill layering** — an engineering
  decision about LLM-agent context loading, not a communication theory.

## Verification limits

Cambridge Core and ACM DL blocked live page fetches, so Bell's and
Horvitz's exact page ranges rest on multiple consistent secondary sources
rather than a live publisher page (figures agree across them). The literal
coiner of "progressive disclosure" could not be authoritatively established.
