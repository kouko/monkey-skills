# Brief — Axis-B relocation to the DESIGN station + the tone & manner seam (Step 2)

> **Type**: brainstorming brief (loom-code Stage 1)
> **Date**: 2026-07-13
> **Origin**: BACKLOG "Axis B relocation to the DESIGN station + surface catalog
> expansion — Step 2" (docs/loom/BACKLOG.md, shipped PR #555)
> **Targets**: loom-product-principles (0.8.0 → 0.9.0), loom-interface-design
> (0.4.2 → 0.5.0)

## Problem

Two defects, one root cause — the PRINCIPLES→DESIGN seam was never wired.

**2A — #553's central promise is an IOU.** PR #553 made product-principles emit
3-5 **tone & manner adjectives** as a version-pinned `## Anchors` row, justified
as *"mechanically readable by the downstream DESIGN station"*. Nothing downstream
reads it. `design-system` reads PRINCIPLES.md as undifferentiated prose and then
**re-derives its own Mood adjectives from scratch**. The upstream anchor and the
downstream mood are unwired duplicates: the user commits to "calm, precise,
unhurried" at the principles stage, and the design stage invents its own mood
anyway.

**2B — the surface-treatment decision has no owner.** `canon-design-surface.md`
(Axis B) sits in product-principles, where industry research (#553) showed it does
not belong: surface treatments are a **stage-4 design-language sub-decision**.
Recon corroborates this structurally — `design-md-schema.md` already ships a
`surface` token ("surface tints per elevation level"), `shadows` tokens, and border
tokens. Skeuomorphism / flat / material-elevation / neumorphism / glassmorphism /
Liquid Glass **are precisely choices over shadow + surface-tint + border**. Axis B
is the generative decision sitting directly above two already-shipped token
sections, with nobody owning it.

JTBD: *When I commit a visual direction in the product constitution, I want the
design stage to actually inherit and honor it — and to make the surface-treatment
choice where the tokens for it live — so the design system is a derivation of my
constitution instead of a parallel invention.*

## Users

The agent running `loom-interface-design:design-system` for a product that has a
`PRINCIPLES.md` (the normal case — the plugin already refuses to proceed without
one), and the user who committed the tone & manner anchor upstream and expects the
design to honor it.

## Smallest End State

**2A — wire the seam (READ-AND-HONOR, not a parser).**
1. `design-system` Step 2 reads the `## Anchors` section of PRINCIPLES.md and
   treats the **tone & manner adjectives as the governing mood** — it does NOT
   re-derive its own. If an Anchors row exists, it is the input; the Mood field in
   the derivation contract becomes "inherited from the anchor", not "invented here".
2. Absent Anchors row (older PRINCIPLES.md, or an anchor was never pinned) →
   fall back to today's behavior (derive Mood) **and say so loudly** — never
   silently invent while pretending to inherit.

**2B — relocate Axis B + port the pick protocol.**
3. Move `canon-design-surface.md` → `loom-interface-design/skills/design-system/references/`
   (flat-folder rule). Delete the forward-note (it says "deferred to Step 2" — this
   IS Step 2) and **delete its self-destruct test**, don't move it.
4. `design-system` gains a **surface-treatment pick**: propose **3-5 candidates**
   from the canon (fit/tension notes, 1-2 considered-but-rejected surfaced), the
   **user decides**, and the pick is **named + rationalized in prose** in
   Overview/Brand ("Surface treatment: X — because <adjectives> + <constraint>").
   The chosen treatment then constrains the `## Elevation & Depth` + `## Shapes`
   token blocks. Anti-costume law carries over: a treatment never overrides a
   PRINCIPLES value, and its WCAG risk flag is a blocker, not a note.
5. **Expand the catalog** 6 → ~18 rows from the 12 committed candidates.
6. **Repair the two-sided edit in product-principles**: the five-file canon audit
   list and the two-round Axis-A/Axis-B paragraph both hardcode Axis B; with Axis B
   gone they must be **rewritten to a single Axis-A round** (dangling reference
   otherwise). Same in `question-sets.md`.
7. Four version bumps (both plugins' `.claude-plugin` + `.codex-plugin`), codex
   manifests synced.

## Current State Evidence

From a completed Explore recon (2026-07-13) — every claim below is a live read.

- **Forward** (`design-system/SKILL.md`): 6 steps — read schema (`:47`), read
  PRINCIPLES.md (`:58`), detect modality (`:73`), emit 8 sections (`:81`), write to
  `docs/loom/` (`:111`), run `validate_design_output.py` (`:118`). The visual-style
  decision is taken at Step 4a item 2 (`:87-91`): *"First commit the visual concept
  … one specific art-direction idea plus the 3-5 generative visual principles."*
  **One agent-authored concept, no menu, no user pick, no pin.**
- **Reverse** (the seam): `design-system/SKILL.md:58-71` reads PRINCIPLES.md as
  prose ("North Star and principles **constrain** the design"). A grep for
  `anchors|tone & manner` across ALL of `loom-interface-design/skills/` +
  `scripts/` returns **3 false positives, zero real hits**. `design-md-schema.md:52-68`
  defines the derivation contract — Visual concept / **Mood** / Generative visual
  principles — feeding the `brand_voice` token: this is the duplicate that must
  become an inheritance.
- **Data** (where the treatment lands): `design-md-schema.md:126-134`
  (`## Elevation & Depth` — ships `surface` "surface tints per elevation level" +
  `shadows`) and `:136-144` (`## Shapes` — borders). The 8 sections are frozen in
  THREE places: `design-md-schema.md:39-42`, `design-system/SKILL.md:50-53`,
  `validate_design_output.py:53-62` (order-checked).
- **Boundary** (the cross-plugin contract): interface-design reads the CONSUMER
  repo's `docs/loom/PRINCIPLES.md` — a **path-passed artifact**, never reaching into
  loom-product-principles' directory (`design-system/SKILL.md:58-71`;
  `interaction-flows/SKILL.md:27-38`; `using-loom-interface-design/SKILL.md:115`
  *"Does not author or override PRINCIPLES.md"*). So the relocated canon file must
  live INSIDE loom-interface-design, while tone & manner keeps flowing across the
  seam via the PRINCIPLES.md artifact. The boundary supports the move.
- **Error / traps**:
  - `test_surface_canon.py:132-162` is a **self-destruct test** — it asserts the
    file still says "deferred to Step 2" / "defer". Doing Step 2 must **DELETE** it.
    A mechanical copy of the test file yields a red suite.
  - `test_canon_references.py`'s `CANON_FILES` (`:34-39`) lists only FOUR canons —
    `canon-design-surface.md` is deliberately absent, so removing the file does not
    break it. But those four require `MIN_ENTRIES = 14` while the surface canon needs
    only 5 (`MIN_SURFACE_ROWS`); if the ported test mirrors `test_canon_references`'s
    shape, keep the 5-row floor.
  - `test_design_system_skill.py:180-189` enforces flat skill folders (no nested
    subfolders) — the canon must land at `skills/design-system/references/`.
  - loom-interface-design has **no canon file and no canon-guarding test** today;
    the closest pattern is `test_design_system_skill.py:98-101` (assert the SKILL.md
    cites its reference file).

## Decision

**Build**: the READ-AND-HONOR seam (2A), the Axis-B relocation with a ported
candidate-pick protocol (2B), the catalog expansion to ~18 rows, the product-
principles repair to a single Axis-A round, and four version bumps.

**Do NOT build**: a mechanical parser of the Anchors row, and a 9th DESIGN.md
section. Axis-4 research (below) shows both are contrary to industry practice AND
carry the highest cost/risk in this change (the 8-section list is frozen in three
places incl. an order-checking validator). The surface pick is **named in prose**,
which is exactly what Apple ("Liquid Glass") and Material (the paper metaphor) do.

**Why READ-AND-HONOR wins here specifically**: a regex over a Markdown heading is
the *worst* form of machine-readable — it couples to formatting and **degrades
silently** (the agent gets the wrong mood, and nothing fails) while paying every
schema cost. Our consumer is an LLM reading Markdown; prose IS our format.

## Alternatives Considered (Axis 4 — research-grounded, all URLs live-verified)

**The question**: how should a downstream design system consume an upstream
version-pinned style/brand anchor — machine-readable pin, or prose?

1. **MECHANICAL parse** (grep the adjectives out of `## Anchors`; add a 9th
   DESIGN.md section for the surface pick).
   - Pros: enforceable; a validator could fail on contradiction.
   - Cons: **no industry precedent** — the W3C DTCG token format has token types for
     *values only* (color/dimension/shadow/typography); there is **no slot** for brand
     personality, art direction, or mood. Its only metadata is `$description` (plain
     text, tools MAY use) and `$extensions` (an explicitly unvalidated vendor escape
     hatch, no standard keys). Style Dictionary passes custom attributes through but
     has no intent/provenance concept; Tokens Studio carries only value/type/description.
     Couples to Markdown formatting; fails silently on drift; touches the frozen
     8-section contract in three places.
   - Sources: [DTCG Format Module 2025.10](https://www.designtokens.org/tr/drafts/format/) (EN);
     [Style Dictionary — Design Tokens](https://styledictionary.com/info/tokens/) (EN);
     [Tokens Studio — Token Format](https://docs.tokens.studio/manage-settings/token-format) (EN);
     [Robson, "Understanding $extensions"](https://www.alwaystwisted.com/articles/understanding-extensions-in-the-design-tokens-spec) (EN).

2. **READ-AND-HONOR prose** (instruct the downstream skill to read the Anchors
   section, honor the adjectives as the governing mood, and NAME its surface pick in
   prose). ← **CHOSEN**
   - Pros: matches universal industry practice — every flagship keeps brand voice in
     **docs/prose** and tokenizes only the *derived values*. Apple **names and
     rationalizes** "Liquid Glass" in prose; Material names the paper-and-ink metaphor
     ("seams and shadows provide meaning"). Zero schema cost; nothing frozen gets
     touched; an LLM consumer reads Markdown natively.
   - Cons: not mechanically enforceable — relies on the agent honoring an instruction
     (the repo's own #545 lesson: *"read ≠ obeyed"*). Mitigated by a grep-test pinning
     the instruction, and by the fallback-loudly rule.
   - Sources: [Apple Newsroom, Liquid Glass (2025-06-09)](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/) (EN);
     [Shopify Polaris — Creating depth](https://polaris-react.shopify.com/design/depth/creating-depth) (EN — pure token guidance, NO named aesthetic: the surface decision exists only as token values);
     [Zenn 「ADR駆動開発のすすめ」](https://zenn.dev/miyan/articles/adr-driven-dev-ai-context-precision-2026) (JA — for LLM-agent consumers, keep decision records as Markdown prose; invest in content quality, not schema).

3. **Design-decision records (ADR-style)** — a named, in-repo, append-only prose
   record with Status / Superseded-by.
   - Pros: real technique ([Thoughtworks Radar, "Design system decision records",
     Assess, Vol 29](https://www.thoughtworks.com/radar/techniques/design-system-decision-records) (EN)).
     Our version-pinned Anchors row is **ahead of** practice, not contrary to it.
   - Cons: full ADR machinery is more than this change needs. **Partially adopted**:
     the finding that industry pins *status + supersession* (which is what makes
     staleness detectable) is noted as a future upgrade to the Anchors row — a bare
     version stamp buys less. Not built now.

**My take**: READ-AND-HONOR. **Conditional reversal → MECHANICAL** if any of:
(a) a **non-LLM consumer** appears (e.g. a CI lint that must fail when shadow tokens
contradict a "flat" pick); (b) **measured drift** in dogfood (the agent ignores or
hallucinates the anchors — then the validator belongs in the PIPELINE, not the
instructions, per the repo's own #545 mechanical-gate lesson); or (c) a **third
consumer** of the same anchors appears. If reversed, add a *declared named field +
a loud validator* — never a grep of adjectives out of free prose.

**EN/JA divergence (a finding, not noise)**: JA writing splits cleanly into トンマナ
(brand prose: persona, competitor scan — never touches tokens) and デザイントークン運用
(engineering: values, semver, CI snapshot tests — never touches トンマナ). The two
corpora **never bridge** — independently corroborating that mood and tokens are
separate artifacts *by construction*, not by neglect.

## What Becomes Obsolete (Axis 5 — removed in THIS change)

- `canon-design-surface.md`'s **forward-note** ("relocation deferred to Step 2") —
  Step 2 is happening; the note is spent.
- `test_surface_canon.py::test_surface_canon_carries_design_stage_forward_note` —
  **deleted, not moved** (it guards the mis-placement being recorded; the
  mis-placement is being fixed).
- product-principles' **two-round Axis-A/Axis-B paragraph** and the **five-file canon
  audit list** — rewritten to a single Axis-A round (a dangling reference otherwise).
- The **contamination-guard sentences** — the guard becomes *free* (the axes now live
  in different plugins, so their contexts cannot co-occur in one round by
  construction), but the sentences asserting it must be rewritten, not merely deleted.
- `design-md-schema.md`'s **Mood-is-invented** framing — becomes Mood-is-inherited
  (with a loud fallback when no anchor exists).

## Out of Scope

- A mechanical parser for the Anchors row; a 9th DESIGN.md section; any change to
  `validate_design_output.py`'s 8-section order check.
- Upgrading the Anchors row to full ADR shape (Status / Superseded-by) — recorded as
  a future upgrade, not built.
- Axis A (`canon-design-visual.md`) content — it stays in product-principles,
  untouched except for the single-round rewrite.
- `interaction-flows` and `design-critic` — they read PRINCIPLES.md but do not make
  the visual-style decision; not touched.
- Re-researching the 12 catalog candidates — they are committed at
  `docs/loom/research/2026-07-12-ui-surface-treatments-canon.md` §Part 2. Re-check URL
  liveness at use time; never retype from memory.

## Open Questions

None blocking. One deliberate bet recorded: READ-AND-HONOR relies on instruction
compliance, which this repo has burned on before (#545: "read ≠ obeyed"). The
mitigation is a grep-test pinning the instruction + the loud-fallback rule; the
reversal trigger (measured drift in dogfood) is written into §Alternatives above.
