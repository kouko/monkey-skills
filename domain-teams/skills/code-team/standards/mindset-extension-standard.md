# Mindset Extension Standard

Meta-standard for extending the `mindset-*.md` library in
`code-team/standards/`. Mindsets are a distinct sub-genre within the
standards directory — *philosophical anchors* alongside the
*mechanical* standards (Clean Code naming, Pragmatic principles,
SOLID, TDD, Refactoring, OWASP, character-encoding security).
Without a clear extension bar, the library will accumulate
overlapping or weakly-grounded mindsets and lose its anchoring
function.

## Primary Sources

- **softaworks/agent-toolkit/skills/reducing-entropy/adding-reference-mindsets.md** (MIT, originally `joshuadavidthomas/agent-skills`). https://github.com/softaworks/agent-toolkit/blob/main/skills/reducing-entropy/adding-reference-mindsets.md — the upstream Quality Checklist this standard adapts. The 5-item checklist (counter over-engineering / distinct / concise / memorable / concept-named) and the "What NOT to Add" exclusion list are taken substantively from upstream.
- **`skill-team/standards/grounding-principle.md`** (this repo) — primary-source-anchored citation rules; mindset standards are bound by the same anti-laundering rules as mechanical standards.
- **`code-team/research/grounding-v5.5.0.md`** (this repo) — citation verification methodology applied to the initial 4 mindsets.

This standard sits alongside (not above) the four mindset standards;
it is *about* the library shape, not part of the philosophical
content.

## What a Mindset Is

A mindset is a 1-2 sentence quotable principle plus a body that
grounds the principle in primary sources, names the operational
question it helps answer, and supplies anti-patterns. Mindsets
differ from mechanical standards in three ways:

| | Mechanical standard | Mindset standard |
|---|---|---|
| Question it answers | "How do I do X correctly?" | "Should I do X at all?" |
| Body shape | Rules + thresholds + examples | Quoted insight + reasoning + anti-patterns |
| Triggering | Auto-load by worker / evaluator | On-demand by protocols when design judgment is needed |
| Primary source | Books, papers, ISO standards | Books, papers, talks, *and* practitioner-coined neologisms (e.g. PAGNI 2021) |

The fourth column row matters: mindsets accept practitioner-coined
neologisms (like PAGNI) as primary as long as ≥2 independent
practitioner sources adopt the term. Mechanical standards do not.

## Quality Checklist (must pass all 5)

Before adding a new mindset standard:

- [ ] **Counters over-engineering?** The mindset must help resist
  the urge to add code, abstraction, or complexity. A mindset that
  *encourages* adding (without a named exception bar like PAGNI)
  is the wrong shape. The library exists to be a deletion-side
  weight against the additive default.
- [ ] **Distinct from existing?** The new mindset must answer a
  question the existing 4 do not. Overlap with `data-over-abstractions`
  (custom types vs data), `design-is-taking-apart` (composition vs
  complection), `expensive-to-add-later` (PAGNI / YAGNI exceptions),
  or `simplicity-vs-easy` (objective vs subjective) is grounds for
  rejection in favor of strengthening the existing mindset's body.
- [ ] **Concise?** The body is ~50–250 lines, not a book chapter.
  A mindset that needs 500 lines is a mechanical standard wearing a
  philosophical disguise.
- [ ] **Memorable core insight?** The mindset has a quotable
  principle in 1-2 sentences that a reader can recite from memory
  after one read. Compare: "design is taking apart", "100 functions
  on 1 data structure", "simple is one fold". A mindset whose
  insight needs three paragraphs to state is unfit for the *anchor*
  role.
- [ ] **Named by concept, not by person or source?** Filename and
  title use the *concept* (`design-is-taking-apart`,
  `simplicity-vs-easy`), not the person (`hickey-mindset`) or the
  source (`simple-made-easy-talk`). Concept-named mindsets compose
  with each other; person-named ones become biographical.

## Primary-Source Bar

Mindset standards inherit `skill-team/standards/grounding-principle.md`
rules with one explicit easing:

- **Required**: ≥2 independent primary sources (books / papers /
  talks / well-cited practitioner essays)
- **Required**: every quoted insight cites the source by author,
  year, work, and (where applicable) chapter / timestamp
- **Allowed exception**: practitioner-coined neologisms (PAGNI,
  Hickey's "complect") may be cited from blog posts / talks if ≥2
  independent practitioners have adopted the term and the term is
  not already in books at the time of citation
- **Forbidden**: citation laundering — fabricating chapter / topic
  numbers, attributing quotes to people who did not say them
  (e.g. the Perlis #9 epigram is *not* Hickey's; treating it as such
  is laundering even though Hickey popularized it)

The 4 initial mindsets pass this bar — see
`research/grounding-v5.5.0.md` for the verification log.

## What NOT to Add

Adapted from upstream `adding-reference-mindsets.md`:

| Anti-shape | Why it doesn't fit | Where it should live instead |
|---|---|---|
| Technology-specific advice | "React components should…", "In Rust, prefer…" — not universal; rots as the technology evolves | Project-level docs or technology-specific skill |
| Process / workflow rules | "Always run tests before…", "Use TDD when…" — these are protocols, not mindsets | `code-team/protocols/` |
| Vague platitudes | "Write clean code", "Think before you code" — no actionable insight | Nowhere; do not write |
| Context-dependent rules | "In microservices…", "When working with legacy code…" — mindsets are universal anchors, not situational rules | A mechanical standard with explicit scope, or a protocol |
| Re-statements of mechanical standards in motivational tone | "DRY is important because…" — this is mechanical-standard territory dressed up | Strengthen the existing mechanical standard's body |

## The Operational Test

A new mindset must help an agent answer **at least one** of these
design-time questions in a way the existing 4 mindsets do not:

- "Should I add this abstraction?"
- "Should I delete this?"
- "Is this complexity essential or accidental?"
- "Is this 'easy' (familiar) or 'simple' (not braided)?"
- "Is this PAGNI-grade infrastructure or YAGNI speculation?"

If the mindset doesn't directly inform one of those questions, it
likely belongs in a mechanical standard, a protocol, or nowhere.

## SSOT and Functional-Copy Policy

The 4 mindsets live in **two locations** by design:

| Location | Role | Updated by |
|---|---|---|
| `domain-teams/skills/code-team/standards/mindset-*.md` | **SSOT** — canonical version with full cross-references to mechanical standards (Pragmatic, SOLID, Refactoring, etc.). Used by code-team brainstorming / refactoring protocols. | All edits land here first. |
| `dev-workflow/skills/complexity-critique/references/mindset-*.md` | **Functional copy** — bundled with the dev-workflow skill so that `complexity-critique` runs without `domain-teams` installed (matches upstream `reducing-entropy/references/` layout). Each file carries a "Bundled functional copy" header blockquote pointing back to the SSOT. | Updated to match the SSOT in the **same PR** as the SSOT edit. |

**Why both**: the upstream `reducing-entropy` skill was zero-runtime-dependency self-contained. `complexity-critique` preserves that property by bundling. But code-team also gains real value from the mindsets being in its own standards library (they ground refactoring decisions; they fit the existing "primary-source-grounded standards" pattern). The two locations are reconciled by treating code-team as the SSOT and dev-workflow as a functional copy.

**Drift detection**: a CI sanity check (planned, not yet implemented) can diff the body text (excluding the header blockquote) and fail if they disagree. Until that exists, the same-PR rule is the discipline.

## Process for Adding a New Mindset

1. **Spike against existing 4** — write a 5-line summary of the
   proposed mindset's core insight; check overlap against
   `data-over-abstractions` / `design-is-taking-apart` /
   `expensive-to-add-later` / `simplicity-vs-easy`. If overlap
   exists, write a paragraph in the existing mindset's body
   instead.
2. **Verify primary sources** — ≥2 independent primary sources
   exist; verify by URL / ISBN / page number; record verification
   log in a research note `research/grounding-v{X.Y.Z}.md` (this
   note bundles with the mindset commit per the 3-commit standards
   split rule).
3. **Run the Quality Checklist** — all 5 items must pass; document
   "distinct from existing" by naming what design-time question the
   new mindset answers that the existing 4 do not.
4. **Add the SSOT file** at `code-team/standards/mindset-{concept}.md`
   in the same body shape as the initial 4 (no frontmatter; `# Title`
   header; `## Primary Sources` with full citations; sections;
   `## Anti-Patterns` at end).
5. **Bundle the functional copy** at
   `dev-workflow/skills/complexity-critique/references/mindset-{concept}.md`
   — copy the SSOT body verbatim and prepend the standard
   "Bundled functional copy" header blockquote (template in the
   existing 4 references files). Same PR as step 4.
6. **Wire it** in:
   - `code-team/SKILL.md` *On-demand mindsets* section
   - `dev-workflow:complexity-critique/SKILL.md` §Reference
     Mindsets table (the "Use when…" column row)
   - All 3 `complexity-critique` READMEs (en / ja / zh-TW)
     reference-mindsets bullet list and Files tree
7. **Bump versions** — `domain-teams` minor (new SSOT standard);
   `dev-workflow` patch (bundled functional copy + SKILL.md /
   READMEs reference table updates).

## Cross-References

- `mindset-data-over-abstractions.md` — initial mindset 1
- `mindset-design-is-taking-apart.md` — initial mindset 2
- `mindset-expensive-to-add-later.md` — initial mindset 3 (PAGNI
  exemption precedent for practitioner-coined neologisms)
- `mindset-simplicity-vs-easy.md` — initial mindset 4
- `research/grounding-v5.5.0.md` — initial 4 mindsets' verification
  log; template for future mindset research notes
- `dev-workflow:complexity-critique/SKILL.md` §Reference Mindsets —
  cross-plugin consumer; new mindsets must update this table

## Anti-Patterns (extension-time)

- ❌ **Person-named mindsets** — `hickey-philosophy.md`,
  `ousterhout-deep-modules.md` — concept-name them
- ❌ **Source-named mindsets** — `simple-made-easy.md`,
  `out-of-the-tar-pit.md` — these are *primary sources*, the mindset
  is the *concept they ground*
- ❌ **Adding a 5th mindset before stress-testing the existing 4**
  — most "I want to add X" cases turn out to be sub-cases of an
  existing mindset; strengthen the existing body first
- ❌ **Mindset with one primary source** — fails the 2-source bar;
  the upstream author was deliberate that mindsets are *patterns
  across multiple thinkers*, not single-author manifestos
- ❌ **Importing a mechanical rule as a mindset** — "use semantic
  versioning" is a mechanical standard, not a design-time anchor
- ❌ **Importing a corporate value as a mindset** — "move fast and
  break things", "10× engineer culture" — these are sociological
  claims, not design principles
