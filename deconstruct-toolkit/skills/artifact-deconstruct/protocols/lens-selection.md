# Protocol: Lens Selection

Decide which 1–3 lenses to apply to the artifact. Single-lens tunnel
vision and all-six over-application are both anti-patterns.

## Decision tree

```
Start: artifact at hand
├─ Type: copy / advertising / landing page
│  └─ Default: lens-persuasion + lens-rhetoric
│     └─ If embeds a long argument: + lens-genre
│
├─ Type: document pack / playbook / multi-file kit
│  └─ Default: lens-genre + run all 6 dimensions explicitly
│     └─ If the kit is for executives: + lens-rhetoric (proposal genre)
│     └─ If the kit has UI screenshots: + lens-ux
│
├─ Type: single SOP / how-to / numbered steps
│  └─ Default: lens-genre (procedure genre)
│     └─ If the SOP includes UI walkthroughs: + lens-ux
│
├─ Type: presentation deck / slides
│  └─ Default: lens-rhetoric + lens-genre
│     └─ If sales-oriented: + lens-persuasion
│
├─ Type: UI screen / app flow / website / onboarding
│  └─ Default: lens-ux + lens-persuasion
│     └─ If onboarding has long copy: + lens-rhetoric
│
├─ Type: long-form article / op-ed / proposal / paper
│  └─ Default: lens-rhetoric (for argument structure)
│     └─ If suspected ideology: + lens-frame
│     └─ If academic: + lens-genre (CARS move analysis)
│
├─ Type: speech / political address / manifesto
│  └─ Default: lens-rhetoric + lens-frame
│     └─ If invoking historical narrative: + lens-semiotic (REF code)
│
├─ Type: literature / film / poem / advertising imagery
│  └─ Default: lens-semiotic + lens-frame
│     └─ If allegory: + lens-rhetoric
│
└─ Type: ambiguous / mixed
   └─ Apply lens-genre first to identify the dominant genre,
      then re-route based on genre detection
```

## Selection rules

1. **Minimum: 1 lens.** A single lens is acceptable when the artifact is purely one type and short.
2. **Sweet spot: 2 lenses.** Most artifacts benefit from a primary + secondary lens combination.
3. **Maximum: 3 lenses.** Beyond 3, the analysis loses focus and turns into summary.
4. **Six-dimension is always-on.** It runs regardless of which lenses you picked. It is *not* a 7th lens.
5. **Lens combinations are not commutative.** `lens-persuasion + lens-rhetoric` (LP) emphasizes mechanisms; `lens-rhetoric + lens-persuasion` (academic argument) emphasizes structure. State which lens leads.

## When to pick a third lens

Add a third lens only when the artifact has **unusual depth** in a
specific dimension:

- A landing page that *also* embeds a long argument (rare) → persuasion + rhetoric + genre
- An academic paper that *also* uses propaganda framing (rare) → rhetoric + frame + genre
- A document pack that *also* has interactive UI (rare) → genre + ux + 6-dim

If you cannot name *why* a third lens earns its place, do not add it.

## When to skip a default lens

Defaults are starting points, not laws. Skip if:

- The artifact has no persuasion intent → skip `lens-persuasion`
- The artifact has no UI elements → skip `lens-ux`
- The artifact has no implicit argument → skip the Toulmin half of `lens-rhetoric`

## Order of application

When applying multiple lenses:

1. **Run lens-genre first** if you picked it — genre detection shapes
   which moves the other lenses should look for
2. **Run lens-frame early** — the frame sets context for everything else
3. **Run lens-rhetoric next** — argument structure is foundational
4. **Run lens-ux / lens-persuasion / lens-semiotic last** — these are
   surface mechanism passes that benefit from prior structural insight

## Worked examples

### Example 1: Stripe pricing page

- Type detected: marketing copy + UI hybrid
- Default for marketing copy: `lens-persuasion + lens-rhetoric`
- UI elements present (interactive price slider, plan toggle): add `lens-ux`
- **Final**: `lens-persuasion + lens-rhetoric + lens-ux` (3 lenses)
- Order: rhetoric → persuasion → ux

### Example 2: Internal AI rollout playbook (Str-Team)

- Type detected: document pack
- Default: `lens-genre + 6-dim full`
- Targeted at strategy-team executives → add `lens-rhetoric` (proposal genre)
- No UI screenshots → skip `lens-ux`
- **Final**: `lens-genre + lens-rhetoric + 6-dim`
- Order: genre → rhetoric

### Example 3: Notion's "Build your second brain" landing page

- Type detected: marketing copy with embedded testimonial
- Default: `lens-persuasion + lens-rhetoric`
- Heavy "knowledge worker / second brain" framing → add `lens-frame`
- **Final**: `lens-persuasion + lens-rhetoric + lens-frame`
- Order: rhetoric → frame → persuasion
