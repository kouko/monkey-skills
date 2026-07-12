# Plan: visual anchoring realignment — tone & manner primary anchor + Axis A reframing (P2 Step 1)

Source brief: docs/loom/specs/2026-07-12-visual-anchor-realignment-tone-and-manner.md
Total tasks: 8
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (round 2, 14/14 — 2026-07-12; round-1 NEEDS_REVISION fixes + round-2 advisories folded in, see Notes)

Target: loom-product-principles 0.7.0 → 0.8.0
Branch: feat-visual-anchor-realignment (from origin/main 79fb86b6)

## Recon findings (drive the split)

- `SKILL.md` is ~2,781 words ≈ 3,754 tokens against a ~6,000-token budget —
  **~2,200 tokens of headroom**. The brief's "extract to a reference file if it
  overflows" contingency is therefore NOT triggered; flow text goes inline.
- The version-pinned `## Anchors` row machinery already exists
  (`SKILL.md:178` defines the section; `SKILL.md:310` already mandates
  "MUST land as a version-pinned `## Anchors` row"). The tone & manner anchor
  **reuses** it — no new machinery, per the brief.
- `test_canon_references.py` is `@pytest.mark.parametrize`'d over `CANON_FILES`
  and already enforces **≥14 entries, each row carrying a source URL**
  (`MIN_ENTRIES = 14`, line 43). The 15-row expansion is therefore already
  URL-guarded by an existing test — new tests pin only NEW behavior
  (adjective anchor, reframing, cultural coverage, forward-note).
- Test surface = structural grep tests over skill prose (pytest, stdlib +
  path-based). That IS the TDD surface for this repo.

## Task 1 — tone & manner primary anchor in the Design lane flow

- Description: Add the tone & manner primary-anchor step to the Design lane's
  visual flow: BEFORE any canon candidate round, derive **3-5 tone & manner
  adjectives** from the product's values/Product Principles; these adjectives
  are the **primary visual anchor** and MUST land as their own version-pinned
  `## Anchors` row (reusing the existing Anchors machinery — do NOT extend it).
  State that the canon axes are DOWNSTREAM of this anchor. Edit `SKILL.md`
  Step 3 flow text only.
- Module: loom-product-principles/skills/product-principles/SKILL.md
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md (Step 3, lines ~105-151; Anchors rules at 178, 310)
  - loom-product-principles/scripts/test_product_principles_skill.py (grep-pin style; see test_canon_audit_lists_surface_file / test_visual_lens_3_5_carveout)
- Acceptance:
  - RED: `test_product_principles_skill.py::test_tone_and_manner_primary_anchor` fails — SKILL.md carries no tone & manner derivation step.
  - GREEN: the test passes by asserting SKILL.md's body (a) names "tone & manner", (b) requires 3-5 adjectives derived from the product's values/principles, (c) states the adjectives land as a version-pinned `## Anchors` row, and (d) states the canon axes are downstream of / subordinate to that anchor. Anchor assertions on full phrases (not stray "3-5" — the #550 guard-imprecision lesson).
- External surfaces: none (skill prose + stdlib pytest).
- Dependencies: none
- Independent: true
- Brief item covered: "Tone & manner primary anchor (NEW, lightweight): the Design lane's visual flow first derives 3-5 tone & manner adjectives from the product's values/principles. These adjectives are the primary visual anchor."

## Task 2 — mirror the tone & manner anchor into question-sets.md

- Description: Mirror Task 1's primary-anchor step into the Design lane of
  `references/question-sets.md` so the question lane and SKILL.md agree: the
  visual lens first derives 3-5 tone & manner adjectives from the values, pins
  them as the primary `## Anchors` row, and only THEN runs the axis-typed canon
  rounds (which remain downstream inspiration). Interaction lens stays 2-3.
- Module: loom-product-principles/skills/product-principles/references/question-sets.md
- Files touched: loom-product-principles/skills/product-principles/references/question-sets.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/question-sets.md (Design lane, lines ~55-66)
  - loom-product-principles/skills/product-principles/SKILL.md (Task 1's wording — must not contradict)
- Acceptance:
  - RED: `test_product_principles_skill.py::test_question_sets_carries_tone_and_manner_anchor` fails — question-sets.md's Design lane names no tone & manner step.
  - GREEN: the test passes by asserting question-sets.md names "tone & manner", requires 3-5 adjectives from the values, and orders them BEFORE the canon rounds. Existing pins (visual 3-5, divergent, interaction stays 2-3) stay green.
- External surfaces: none.
- Dependencies: Task 1 completes first (doc-mirrors-doc: the wording must match SKILL.md's canonical phrasing — a semantic dependency despite disjoint prose files).
- Independent: false
- Brief item covered: "Flow text + derivation instruction in SKILL.md and question-sets.md; reuse the existing Anchors-row machinery, do not extend it."

## Task 3 — reframe Axis A as value-constrained mood inspiration (canon file framing)

- Description: Rewrite the framing header of `references/canon-design-visual.md`
  so Axis A is stated as **stage-3 mood / creative-direction inspiration,
  DOWNSTREAM of the tone & manner adjective anchor — never a pick-one menu**,
  and generalize the anti-costume rule into an explicit law: a movement may
  enrich candidates but NEVER overrides a PRINCIPLES value (the existing
  Memphis-vs-low-stimulus case becomes the worked example of the general law).
  Framing prose only — table rows are Task 5's job.
- Module: loom-product-principles/skills/product-principles/references/canon-design-visual.md
- Files touched: loom-product-principles/skills/product-principles/references/canon-design-visual.md, loom-product-principles/scripts/test_canon_references.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/canon-design-visual.md (framing lines 1-16)
  - loom-product-principles/scripts/test_canon_references.py (CANON_FILES parametrize + grep-pin style)
  - docs/loom/specs/2026-07-12-visual-anchor-realignment-tone-and-manner.md (§Research — the stage-3 vs stage-4 evidence)
- Acceptance:
  - RED: `test_canon_references.py::test_visual_canon_framed_as_downstream_mood_inspiration` fails — canon-design-visual.md's framing carries no downstream/anti-costume-law statement.
  - GREEN: the test passes by asserting the framing (a) names the tone & manner anchor as upstream / states Axis A is downstream of it, (b) states it is mood/creative-direction inspiration, NOT a pick-one menu, and (c) carries the general anti-costume law (a movement never overrides a PRINCIPLES value). Existing CANON_FILES contract (≥14 rows + per-row URL, "never shown raw to the user") stays green — INCLUDING `test_canon_file_has_no_doctrine_body`, which caps every non-table, non-heading line at **400 chars**: wrap the anti-costume-law paragraph across multiple physical lines, never one long line.
- External surfaces: none.
- Dependencies: none (framing prose is independent of SKILL.md's flow text; the shared vocabulary "tone & manner" is a fixed term from the brief, not a symbol Task 1 defines)
- Independent: true
- Brief item covered: "Axis A reframed as value-constrained mood inspiration: the canon-design-visual.md framing states Axis A is stage-3 mood/creative direction downstream of the adjective anchor, never a pick-one menu; strengthen the anti-costume law."

## Task 4a — mirror the Axis-A reframing into SKILL.md wording

- Description: Bring SKILL.md's Axis-A wording into agreement with Task 3's
  reframing: where the flow currently presents Axis A as a co-equal anchoring
  round, state that Axis A supplies mood/creative direction downstream of the
  tone & manner anchor and is value-constrained (anti-costume law). Do NOT
  weaken the #550 invariants: the two-axis-round split, the contamination guard
  (each round reads only its own file), the complementary-separate-Anchors-rows
  rule, the visual 3-5 carve-out, and the 1-2 divergent candidates all stay
  intact.
- Module: loom-product-principles/skills/product-principles/SKILL.md
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/canon-design-visual.md (Task 3's canonical reframing wording)
  - loom-product-principles/scripts/test_product_principles_skill.py (the #550 invariant pins that must stay green)
- Acceptance:
  - RED: `test_product_principles_skill.py::test_skill_md_axis_a_framed_as_value_constrained_mood` fails — SKILL.md still frames Axis A as a co-equal anchoring round with no downstream/value-constrained statement.
  - GREEN: the test passes by asserting SKILL.md states Axis A is mood/creative-direction inspiration downstream of the tone & manner anchor and is value-constrained; AND every pre-existing #550 invariant test (two-axis rounds, contamination guard, complementary Anchors rows, 3-5 carve-out, divergent) still passes.
- External surfaces: none.
- Dependencies: Tasks 1, 2, 3 complete first (T1 owns SKILL.md's anchor step — same file; T3 fixes the canonical reframing vocabulary this task mirrors; T2 is declared so the shared `test_product_principles_skill.py` chain T1→T2→T4a→T4b is fully encoded in the DAG, not merely asserted in Notes).
- Independent: false
- Brief item covered: "Matching wording in SKILL.md / question-sets.md." (deliverable 2's second half — SKILL.md half)

## Task 4b — mirror the Axis-A reframing into question-sets.md wording

- Description: Same reframing as Task 4a, applied to the Design lane of
  `references/question-sets.md`: Axis A supplies mood/creative direction
  downstream of the tone & manner anchor and is value-constrained. Same #550
  invariants stay intact (two axis-typed rounds, contamination guard, visual
  3-5, 1-2 divergent, interaction lens stays 2-3).
- Module: loom-product-principles/skills/product-principles/references/question-sets.md
- Files touched: loom-product-principles/skills/product-principles/references/question-sets.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/canon-design-visual.md (Task 3's canonical reframing wording)
  - loom-product-principles/skills/product-principles/SKILL.md (Task 4a's phrasing — must not contradict)
- Acceptance:
  - RED: `test_product_principles_skill.py::test_question_sets_axis_a_framed_as_value_constrained_mood` fails — question-sets.md still frames Axis A as a co-equal anchoring round.
  - GREEN: the test passes by asserting question-sets.md states Axis A is mood/creative-direction inspiration downstream of the tone & manner anchor and is value-constrained; existing Design-lane pins stay green.
- External surfaces: none.
- Dependencies: Tasks 2, 3, 4a complete first (T2 owns question-sets.md's anchor step — same file; T4a shares test_product_principles_skill.py, so serialize).
- Independent: false
- Brief item covered: "Matching wording in SKILL.md / question-sets.md." (deliverable 2's second half — question-sets.md half)

## Task 5 — Axis A cultural expansion (16 live-verified entries)

- Description: Add the brief's 16 live-verified entries to
  `canon-design-visual.md`'s table — 6 Euro-American, 4 Japan, 1 Soviet,
  5 Greater China — chronological within region, each row carrying its verified
  source URL in the existing column shape (Entry | Fits when… | Stability |
  Source). The 6 high-costume-risk rows (Cyberpunk, Vaporwave, City Pop,
  **Soviet Socialist Realism**, Cultural-Revolution poster, Guochao) carry an
  explicit per-row anti-costume caveat; the two **propaganda-origin** rows
  (Socialist Realism, Cultural-Revolution) additionally state: formal visual
  vocabulary only, never the propaganda freight.
  **Lineage wording is EVIDENCE-BOUNDED** (brief §Lineage note): the
  Cultural-Revolution row must use the source-licensed phrasing
  "descended from Soviet Socialist Realism (Chinese painters trained in Soviet
  academies, 1949-57), then diverged into its own 紅光亮 leader-cult register" —
  do NOT strengthen it to a bare "regional variant" (the sources record the
  doctrinal break; bare "variant" overstates continuity).
  Update the file's "Popularity head" note so the new entries are part of the
  completeness re-check.
  **URL handling (CRITICAL)**: copy each URL **string** verbatim from the brief
  (they are live-verified facts — a paraphrased or re-typed URL is a defect; the
  #550 fabricated-URL lesson), but wrap it in the table's existing **markdown-link
  cell shape** `[label](url)`. The existing per-row-URL assertion is
  `LINK_RE = re.compile(r"\]\(https?://[^)]+\)")` (`test_canon_references.py:44`) —
  it matches the `[label](url)` form ONLY. A bare URL pasted straight from the
  brief's list FAILS that assertion on all 15 rows.
- Module: loom-product-principles/skills/product-principles/references/canon-design-visual.md
- Files touched: loom-product-principles/skills/product-principles/references/canon-design-visual.md, loom-product-principles/scripts/test_canon_references.py
- Context paths:
  - docs/loom/specs/2026-07-12-visual-anchor-realignment-tone-and-manner.md (§Axis A expansion — the 16 entries + their verbatim URLs; §Lineage note — the evidence-bounded Soviet↔Cultural-Revolution wording)
  - loom-product-principles/skills/product-principles/references/canon-design-visual.md (existing table shape + rows)
- Acceptance:
  - RED: `test_canon_references.py::test_visual_canon_covers_culture_regions_and_flags_costume_risk` fails — the canon carries no Japan/Soviet/Greater-China cultural entries beyond the existing two, and no per-row anti-costume caveats.
  - GREEN: the test passes by asserting canon-design-visual.md (a) names a representative entry from each region researched (e.g. Pop Art / Ukiyo-e / Socialist Realism / Dunhuang), (b) carries per-row anti-costume caveats on the 6 high-risk rows (Cyberpunk, Vaporwave, City Pop, Socialist Realism, Cultural-Revolution, Guochao), and (c) BOTH propaganda-origin rows (Socialist Realism, Cultural-Revolution) state the formal-vocabulary-only / never-the-propaganda-freight caveat. Existing CANON_FILES contract (≥14 rows, every row a source URL) stays green with the larger table.
- External surfaces: the 16 source URLs are external references (already live-verified during research; implementer copies verbatim from the brief, does NOT re-derive or invent — a plausible-looking 404 was caught during research, so re-typing a URL from memory is a defect).
- Dependencies: Task 3 completes first (same file — Task 3 rewrites the framing header, Task 5 grows the table below it; sequential to avoid a same-file race).
- Independent: false
- Brief item covered: "Axis A cultural-blindspot expansion (16 entries, all URL-live-verified): grow canon-design-visual.md with the researched entries."

## Task 6a — Axis-B forward-note (DESIGN-stage home)

- Description: Add a forward-note to `canon-design-surface.md` recording that
  this axis's correct home is the design-language (DESIGN) stage — industry
  stage 4, a sub-decision of the visual design language, downstream of the
  tone & manner anchor — and that relocating it to loom-interface-design is
  deferred to Step 2. NOTE ONLY: no move, no catalog expansion, no change to
  its existing rows or its ≥5 + Currency contract.
- Module: loom-product-principles/skills/product-principles/references/canon-design-surface.md
- Files touched: loom-product-principles/skills/product-principles/references/canon-design-surface.md, loom-product-principles/scripts/test_surface_canon.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/canon-design-surface.md (existing framing + table)
  - docs/loom/specs/2026-07-12-visual-anchor-realignment-tone-and-manner.md (§Decision — the forward-note's content; §Out of Scope — what must NOT be done)
- Acceptance:
  - RED: `test_surface_canon.py::test_surface_canon_carries_design_stage_forward_note` fails — canon-design-surface.md carries no note about its DESIGN-stage home.
  - GREEN: the test passes by asserting canon-design-surface.md states this axis belongs to the design-language / DESIGN stage and that its relocation is deferred (Step 2). Existing surface-canon contract (≥5 rows + Currency column, rows unchanged) stays green.
- External surfaces: none.
- Dependencies: none (touches only the surface-canon file + its test — disjoint from every other task's files)
- Independent: true
- Brief item covered: "This step adds only a forward-note in canon-design-surface.md recording that this axis's correct home is the design-language stage — no move, no expansion."

## Task 6b — version bump 0.7.0 → 0.8.0 + codex-manifest sync

- Description: Bump `loom-product-principles/.claude-plugin/plugin.json`
  0.7.0 → 0.8.0 (skill content changed → the bump is mandatory) and run
  `python3 scripts/sync_codex_manifests.py loom-product-principles` so the codex
  manifest stays in parity. SSOT is `.claude-plugin/plugin.json`; the codex
  manifest is the generated mirror — never hand-edit it.
- Module: loom-product-principles/.claude-plugin/plugin.json
- Files touched: loom-product-principles/.claude-plugin/plugin.json, loom-product-principles/.codex-plugin/plugin.json
- Context paths:
  - scripts/sync_codex_manifests.py (the parity script — Read its CLI before running; exact invocation above)
  - scripts/test_sync_codex_manifests.py (the drift oracle, line ~368)
- Acceptance:
  - RED: `scripts/test_sync_codex_manifests.py::test_all_eligible_codex_manifests_in_sync` fails — the codex manifest has drifted from the bumped `.claude-plugin/plugin.json`.
  - GREEN: that test passes AND `loom-product-principles/.claude-plugin/plugin.json` reads `"version": "0.8.0"`.
- External surfaces: none.
- Review-weight: mechanical (deterministic sync-script category — exact invocation `python3 scripts/sync_codex_manifests.py loom-product-principles`, named SSOT `.claude-plugin/plugin.json`)
- Dependencies: none (manifest files are disjoint from every other task's files)
- Independent: true
- Brief item covered: "bump loom-product-principles plugin.json 0.7.0 → 0.8.0 + run scripts/sync_codex_manifests.py."

## Dependency graph

```
Level 1 (parallel):  T1 ──┐      T3 ──┬───┐      T6a      T6b
                          │           │   │    (indep)  (indep)
Level 2:             T2 ──┤      T4a ─┘   └─ T5
                          │      (dep T1,T3)   (dep T3)
                       (dep T1)
Level 3:             T4b (dep T2, T3, T4a)
```

Critical-path depth: **3** — the longest chains are T1 → T2 → T4b and
T1 → T4a → T4b (both length 3). Wide at level 1 (four independent leaves:
T1, T3, T6a, T6b).

## Notes

- **Same-file sequencing** (every same-file pair is serialized — verified by
  plan-document-reviewer):
  - `SKILL.md`: T1 → T4a
  - `question-sets.md`: T2 → T4b
  - `canon-design-visual.md`: T3 → T5 (framing vs table)
  - `test_product_principles_skill.py`: T1 → T2 → T4a → T4b
  - `test_canon_references.py`: T3 → T5
- **The four `Independent: true` tasks (T1, T3, T6a, T6b) have pairwise-disjoint
  `Files touched`** — safe for one parallel wave.
- **No SKILL.md extraction needed**: recon shows ~2,200 tokens of headroom
  against the ~6,000-token budget; the brief's overflow contingency does not fire.
- **URL cell shape** (T5): the existing per-row-URL assertion matches the
  markdown-link form `[label](url)` only — a bare URL fails it. Copy the URL
  string verbatim, wrap it in the existing cell shape.
- **Doctrine-body cap** (T3): non-table, non-heading lines are capped at 400
  chars by an existing test — wrap the anti-costume law across lines.
- Every task's tests are structural grep tests over skill prose (pytest,
  stdlib + path-based) — that is the TDD surface for this repo.
- **Test-file placement is BINDING, not a convention guess** (round-2 advisory):
  a `loom-product-principles/scripts/test_question_sets.py` also exists, but
  T2 / T4a / T4b MUST place their new pins in
  `loom-product-principles/scripts/test_product_principles_skill.py` — that file
  already carries the cross-file grep pins these extend (the #550 invariants), and
  the plan's `Files touched` + same-file serialization chain
  (T1→T2→T4a→T4b) depend on it. An implementer who "follows repo convention" and
  writes into `test_question_sets.py` instead breaks the declared file graph.
- **Amendment record**: revised after plan-document-reviewer round 1
  (NEEDS_REVISION) — T4 split into T4a/T4b (Check 4: one module per task), T6
  split into T6a/T6b (Check 6: the bump half had no RED test), plus the
  URL-cell-shape and doctrine-body-cap fixes. Round 2 returned **PASS (14/14)**;
  its three advisories were then folded in: T4a's `Dependencies` now includes
  Task 2 (so the shared-test-file chain is encoded in the DAG, not just asserted
  here), and the binding test-file-placement note above was added. These
  amendments are additive and schema-safe (no task added/removed, DAG edges only
  tightened, depth unchanged at 3) — re-review skipped per §Amending a PASS plan.
- **Post-PASS amendment 2 (2026-07-12)**: the user spotted that the canon held
  Russian Constructivism (1920s) and the proposed Cultural-Revolution row, but
  NOT the style between them — Soviet Socialist Realism, which displaced
  Constructivism and stands upstream of the Chinese look. A grounding research
  pass added it as entry 11 (Tate-sourced) and, importantly, **bounded the
  lineage claim to what the sources license**: descent-then-divergence, NOT
  "regional variant" (Landsberger records both the 1949-57 Soviet training AND
  the later doctrinal break into 紅光亮). T5's scope grew 15 → 16 entries; its
  RED/GREEN now covers 6 costume-risk rows and 2 propaganda-origin rows. Only
  T5's content changed — no task added/removed, no DAG edge touched, depth still
  3 — so the amendment is schema-safe; re-review skipped per §Amending a PASS
  plan. (The research also caught a plausible-looking 404 source URL, reinforcing
  T5's verbatim-copy rule.)
