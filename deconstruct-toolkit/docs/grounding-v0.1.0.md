---
title: Grounding Research Note v0.1.0
type: grounding-note
date: 2026-05-05
status: post-v0.1.0-grounding-patch
plugin_version: 0.1.0
related_adr:
  - "[ADR-0001](adr/0001-convention-b-mixed-naming.md)"
  - "[ADR-0002](adr/0002-strict-skill-self-containment.md)"
  - "[ADR-0003](adr/0003-lens-synthesis-disclosure.md)"
---

# Grounding Research Note — v0.1.0

> **Honest research trail.** This note documents what was directly consulted vs. what was cited from training memory, what page-level claims are first-hand verified vs. inferred, and what synthesis decisions were made. It exists to let future maintainers and skill consumers distinguish "this lens reflects primary-source rigor" from "this lens reflects best-effort summarization."

## Summary table

| Lens | Primary author + work | Citation rigor | Method faithfulness | Synthesis? | Notes |
|---|---|---|---|---|---|
| `lens-semiotic` | Barthes, *S/Z* (1970) | 🟡 partial | 🟢 high | none (single source) | 5 codes confirmed via Wikipedia + multiple academic sources; specific section numbering not verified against printed edition |
| `lens-rhetoric` | Burke (1945) + Toulmin (1958) | 🟢 high | 🟢 high | ✅ synthetic combo | Both sources well-documented; pentad terms + Toulmin model verified via multiple academic sources; specific page numbers within Toulmin Ch 3 (89-134 in original assertion) not confirmed |
| `lens-frame` | Goffman (1974) + Lakoff (1980) | 🟡 partial | 🟢 high | ✅ synthetic combo | Goffman Ch 11 corrected post-publication: "Manufacture of Negative Experience" (was incorrectly stated as "frame breaks"); Lakoff 30-chapter structure verified |
| `lens-genre` | Swales (1990) + Bhatia (1993) | 🟡 partial | 🟢 high | ✅ organic combo | CARS 3-move model + Bhatia 7-move sales letter confirmed; Bhatia p 61 verified; Swales chapter location for CARS not externally confirmed |
| `lens-ux` | Norman (1988/2013) + Nielsen (1994/2020) | 🟢 high | 🟢 high | ✅ organic combo | Norman 2013 signifier addition confirmed; Nielsen 10 heuristics canonical at NN/g URL |
| `lens-persuasion` | Cialdini (2021) + Brignull (2024) | 🟢 high | 🟢 high | ✅ synthetic combo | Cialdini Unity = Ch 8 corrected post-publication (was incorrectly cited as Ch 3); Brignull deceptive.design confirmed |
| `lens-toulmin` (argument-deconstruct) | Toulmin (1958) | 🟡 partial | 🟢 high | none | "First 14 pages of Ch 3" verified via academic reception; specific page numbers in 1958 ed not confirmed |
| `lens-burke-pentad` (argument-deconstruct) | Burke (1945) | 🟡 partial | 🟢 high | none | Pentad framing question verified verbatim; specific page numbers within Introduction not confirmed |
| `lens-symptomatic-reading` (assumption-surface) | Althusser & Balibar (1965/1968) | 🟡 partial | 🟢 high | none | 1965 first ed + 1968 abridged ed distinction confirmed; central method verified; specific page numbers in 1968 abridged ed not confirmed |

**Citation rigor legend**:
- 🟢 high — author + work + chapter + key claims verified via multiple independent sources
- 🟡 partial — author + work + claims verified, but specific page numbers cited from training memory not externally confirmed
- 🔴 low — significant uncertainty or known error (NONE in this version after grounding patch)

**Method faithfulness legend**:
- 🟢 high — operationalization preserves what the original author claimed
- 🟡 partial — operationalization adapts the method significantly
- 🔴 low — operationalization conflicts with original author's claims (NONE in this version)

## Verification methodology

This grounding research, conducted 2026-05-05 as a post-v0.1.0 grounding patch, used:

1. **WebSearch** against academic citations, Wikipedia, university course materials, publisher pages, and reviews
2. **Cross-source verification** — each claim was checked against at least 2 independent sources where possible
3. **Honest gap acknowledgment** — when only training memory could confirm a page number, the citation rigor is marked 🟡

What this research did **NOT** do:

- ❌ Access the printed editions directly (no PDF / library access in this session)
- ❌ Cross-check translations against original-language editions (S/Z French, Reading Capital French)
- ❌ Verify every page number cited in lens reference files

## Errors caught during verification

The grounding patch (2026-05-05) corrected two specific errors in v0.1.0 lens reference files:

### Error 1: Goffman Ch 11 mislabeled

**Original v0.1.0 claim** (`lens-frame.md`): "fabrications Ch 4; frame breaks Ch 11"

**Verified correct**: Ch 11 is **"The Manufacture of Negative Experience"**; frame breaks / vulnerabilities of experience / frame traps are in **Ch 12 ("Vulnerabilities of Experience")**.

**Cause**: training memory conflated the chapters. **Fixed** in `lens-frame.md` source citation block + body table reference.

### Error 2: Cialdini Unity mislocated

**Original v0.1.0 claim** (`lens-persuasion.md`): "Cialdini, *Influence: The Psychology of Persuasion*, expanded ed. (Harper Business, 2021). Ch 3 pp 84–98."

**Verified correct**: Unity is **Ch 8** of the 2021 New and Expanded edition (originally surfaced in *Pre-Suasion*, 2016, Cialdini's earlier work). The original 6 principles each have their own chapter in the original 1984 edition; Unity was **added** as a new chapter for the 2021 expansion. Ch 3 is approximately Reciprocity territory in the original, not Unity.

**Cause**: I generated a placeholder "Ch 3 pp 84-98" without verifying. **Fixed** in `lens-persuasion.md` source citation block.

## Design decisions documented elsewhere

These decisions are recorded in formal ADRs rather than this note:

- [ADR-0001](adr/0001-convention-b-mixed-naming.md) — naming convention (Convention B mixed)
- [ADR-0002](adr/0002-strict-skill-self-containment.md) — lens cross-skill strategy (strict self-containment)
- [ADR-0003](adr/0003-lens-synthesis-disclosure.md) — lens synthesis disclosure (5 of 6 lenses combine 2+ sources)

## Real-fixture verification status

Per design-proposal §9 and §12 Q1, fixtures are real public artifacts (not synthetic) where feasible. Status as of 2026-05-05:

| Fixture | Real fetch attempted? | Outcome |
|---|---|---|
| `sample-dropbox-landing-2024.md` | ✅ yes (WebFetch) | **Updated** — real Dropbox 2026 headline, customer list, section structure captured. Annotations refreshed accordingly. |
| `sample-notion-onboarding-pack.md` | ⚠️ partial | Notion templates page returned 404 on specific template URLs; marketplace categories captured but specific personal-productivity template content not fetchable due to JS rendering. **Relabeled** as "synthetic representative — could not fetch JS-rendered content." |
| `sample-stripe-signup-flow.md` | ⚠️ partial | Stripe dashboard.stripe.com/register returns a server-side browser-compatibility gate; actual signup form is JS-rendered after auth-walled redirect. **Relabeled** as "synthetic representative — JS-rendered, not directly fetchable via WebFetch." |
| 4 other fixtures (op-ed, VC pitch, strategy memo, tweet thread) | ❌ no — synthetic by design | Already labeled "synthetic composite" in v0.1.0; no change. |

**Net**: 1 of 7 fixtures is now first-hand fetched real content; 2 are accurately labeled as JS-render-blocked synthetic representatives; 4 are accurately labeled as synthetic composites by design.

## Gaps remaining for v1.0

1. **Direct primary-source verification** — open the printed editions (or verified scans) of *S/Z*, *Frame Analysis*, *Metaphors We Live By*, *Influence*, *The Uses of Argument*, *A Grammar of Motives*, *Genre Analysis*, *Analysing Genre*, *The Design of Everyday Things*, *Reading Capital*. Goal: every page number 🟢-confirmed instead of 🟡.

2. **Original-language cross-check** — Barthes (French), Althusser (French) translations should be cross-referenced to ensure operationalization is faithful to the original, not just the English translation.

3. **JS-rendered fixture capture** — use a browser-automation tool (Playwright / Puppeteer) to capture Notion + Stripe signup flow at real-fetch fidelity, replacing the synthetic-representative labels with real content.

4. **More fixtures** — design-proposal v1.0 target is 20+ real-world eval cases. v0.1.0 ships 7. Need ~13 more across the 4 skills, with at least 50% real-public-artifact source.

5. **Independent reviewer** — fresh-eyes review by someone not involved in plugin authorship to catch citation errors a self-review (this note) would miss.

## How to update this note

When v0.2 / v0.3 / v1.0 ships, **add a new section dated to that release**, do not rewrite the v0.1.0 entries. Each version's grounding state should be recoverable for audit. This is the same pattern as `domain-teams/skills/*/research/grounding-v*.md`.

## Sources consulted (web-search trail)

A non-exhaustive list of URLs that informed the citation verification, kept for audit:

- [Wikipedia — Dramatistic pentad](https://en.wikipedia.org/wiki/Dramatistic_pentad)
- [Wikipedia — S/Z](https://en.wikipedia.org/wiki/S/Z)
- [Wikipedia — Metaphors We Live By](https://en.wikipedia.org/wiki/Metaphors_We_Live_By)
- [Wikipedia — CARS model](https://en.wikipedia.org/wiki/CARS_model)
- [Wikipedia — Frame analysis (Goffman)](https://en.wikipedia.org/wiki/Frame_analysis)
- [Wikipedia — Reading Capital (Althusser)](https://en.wikipedia.org/wiki/Reading_Capital)
- [Wikipedia — Dark pattern (Brignull)](https://en.wikipedia.org/wiki/Dark_pattern)
- [Cialdini Unity — IAW (Influence at Work)](https://www.influenceatwork.com/7-principles-of-persuasion/)
- [Cialdini Unity — Roger Dooley Medium](https://medium.com/behavior-design/unity-robert-cialdinis-new-7th-principle-of-influence-f32b97277b84)
- [Toulmin sample chapter — Cambridge Univ Press](https://catdir.loc.gov/catdir/samples/cam034/2003043502.pdf)
- [Bhatia — review by Engberg, Hermes 19 (1997)](https://pure.au.dk/ws/files/9993/H19_20.pdf)
- [Swales CARS — Emory University handout](https://writingcenter.emory.edu/documents/cars_model_handout.pdf)
- [Norman — Pitt CMPINF0010 course reading](https://www.arjun-chandrasekhar-teaching.com/courses/Pitt/CMPINF0010/course-readings/design/Norman-The-Design-of-Everyday-Things-Chapter-1.pdf)
- [Goffman frame analysis review — The Power Moves](https://thepowermoves.com/frame-analysis/)
- [deceptive.design (Brignull)](https://www.deceptive.design/)
- [Reading Capital — Marxists Internet Archive (Althusser Ch 1)](https://www.marxists.org/reference/archive/althusser/1968/reading-capital/ch01.htm)

Each source provided cross-confirmation for at least one citation in this grounding patch.
