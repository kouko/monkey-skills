# Plan: Axis-B relocation to the DESIGN station + the tone & manner seam (Step 2)

Source brief: docs/loom/specs/2026-07-13-axis-b-relocation-and-tone-manner-seam.md
Total tasks: 9
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (round 2, 14/14 — 2026-07-13; round-1 NEEDS_REVISION fixes folded in, see Notes)

Targets: loom-product-principles 0.8.0 → 0.9.0; loom-interface-design 0.4.2 → 0.5.0
Branch: feat-axis-b-relocation (from origin/main ac478bbc)

## Recon findings (drive the split)

- **Baselines**: `loom-interface-design/scripts/` = **77 passed**;
  `loom-product-principles/scripts/` = **275 passed**; `scripts/` = **28 passed**
  (carries the codex-manifest drift oracle).
- **design-system/SKILL.md budget**: 1,218 words ≈ **1,644 tokens** against ~6,000
  → **~4,356 tokens of headroom**. The ported candidate-pick protocol goes inline;
  no reference extraction needed.
- **The move is a `git mv` + a repoint**, not a rewrite: `canon-design-surface.md`
  keeps its table shape; only its framing (forward-note out, Axis-B-in-DESIGN in)
  and its home change.
- **`validate_design_output.py` is NOT touched** (brief §Out of Scope) — the surface
  pick rides inside the existing Overview/Brand prose section. This is what keeps
  the 8-section frozen contract (3 places) out of the blast radius.

## Task 1 — design-system inherits the tone & manner anchor (2A)

- Description: Rewrite `design-system/SKILL.md` Step 2 so it reads the `## Anchors`
  section of `PRINCIPLES.md` and treats the **3-5 tone & manner adjectives as the
  GOVERNING MOOD** — inherited, NOT re-derived. This is a **READ-AND-HONOR prose
  instruction**: do NOT build a parser, a grep, or a regex over the Anchors row
  (Axis-4 research settled this — a regex over a Markdown heading couples to
  formatting and degrades silently). Also add the **loud fallback**: when no Anchors
  row exists (older PRINCIPLES.md), derive Mood as today AND **say so explicitly** —
  never silently invent while appearing to inherit.
- Module: loom-interface-design/skills/design-system/SKILL.md
- Files touched: loom-interface-design/skills/design-system/SKILL.md, loom-interface-design/scripts/test_design_system_skill.py
- Context paths:
  - loom-interface-design/skills/design-system/SKILL.md (Step 2 at ~:58-71; the visual-concept beat at ~:87-91)
  - loom-product-principles/skills/product-principles/SKILL.md (the upstream wording that emits the anchor — mirror its vocabulary: "tone & manner", "primary visual anchor")
  - docs/loom/specs/2026-07-13-axis-b-relocation-and-tone-manner-seam.md (§Decision — why READ-AND-HONOR, not a parser)
- Acceptance:
  - RED: `test_design_system_skill.py::test_step2_inherits_tone_and_manner_anchor` fails — SKILL.md never mentions the Anchors section or tone & manner.
  - GREEN: the test passes by asserting SKILL.md (a) names the `## Anchors` section of PRINCIPLES.md as a read target, (b) names "tone & manner" and states the adjectives are the GOVERNING mood, (c) states they are inherited rather than re-derived, and (d) carries the loud-fallback rule for an absent anchor. Pin FULL PHRASES (guard-precision: the #553 vacuous-guard lesson — a membership pin that cannot fail on the violated state is not a test).
- External surfaces: none (skill prose + stdlib pytest).
- Dependencies: none
- Independent: true
- Brief item covered: "design-system Step 2 reads the `## Anchors` section of PRINCIPLES.md and treats the tone & manner adjectives as the governing mood — it does NOT re-derive." + "Absent Anchors row → fall back to today's behavior and say so loudly."

## Task 2 — the derivation contract: Mood becomes inherited, not invented (2A)

- Description: Update `design-md-schema.md`'s **Derivation contract** (~:52-68 —
  Visual concept / **Mood** / Generative visual principles, feeding the `brand_voice`
  token) so **Mood is INHERITED from the PRINCIPLES.md tone & manner anchor** when one
  exists, with the same loud fallback when it does not. Today it instructs the agent to
  invent Mood from scratch — that is the duplicate Task 1 eliminates on the SKILL.md
  side; this task eliminates it on the schema side so the two agree.
- Module: loom-interface-design/skills/design-system/references/design-md-schema.md
- Files touched: loom-interface-design/skills/design-system/references/design-md-schema.md, loom-interface-design/scripts/test_design_system_skill.py
- Context paths:
  - loom-interface-design/skills/design-system/references/design-md-schema.md (the derivation contract at ~:52-68; `## Elevation & Depth` at ~:126-134; `## Shapes` at ~:136-144)
  - loom-interface-design/skills/design-system/SKILL.md (Task 1's landed wording — must not contradict)
- Acceptance:
  - RED: `test_design_system_skill.py::test_schema_mood_is_inherited_from_anchor` fails — the schema's Mood field still reads as agent-invented with no anchor reference.
  - GREEN: the test passes by asserting design-md-schema.md states Mood is inherited from the PRINCIPLES.md tone & manner anchor (when present) and names the loud fallback. The existing 8-section list and its order are UNCHANGED (assert they still pass).
- External surfaces: none.
- Dependencies: Task 1 completes first (doc-mirrors-doc: the schema must use SKILL.md's canonical vocabulary; both also touch the same test file).
- Independent: false
- Brief item covered: "`design-md-schema.md`'s Mood-is-invented framing — becomes Mood-is-inherited (with a loud fallback when no anchor exists)." (brief §What Becomes Obsolete)

## Task 3 — relocate canon-design-surface.md into design-system (2B)

- Description: `git mv` the Axis-B canon file from
  `loom-product-principles/skills/product-principles/references/canon-design-surface.md`
  to `loom-interface-design/skills/design-system/references/canon-design-surface.md`
  (flat-folder rule — `references/` may not contain a subfolder). Rewrite its framing:
  **DELETE the forward-note** ("relocation deferred to Step 2" — this IS Step 2) and
  replace it with its new home statement (this canon is consulted at the DESIGN stage,
  the industry stage-4 design-language sub-decision; it is downstream of the tone &
  manner anchor). Keep the table rows, the Currency column, the WCAG risk flag, the
  "never shown raw to the user" framing, and the grounding-doc citation intact — the
  catalog expansion is Task 5's job, not this one.
- Module: loom-interface-design/skills/design-system/references/canon-design-surface.md
- Files touched: loom-interface-design/skills/design-system/references/canon-design-surface.md, loom-product-principles/skills/product-principles/references/canon-design-surface.md (deleted by the mv), loom-interface-design/scripts/test_surface_canon.py (NEW — the ported contract test), loom-product-principles/scripts/test_surface_canon.py (deleted)
- Context paths:
  - loom-product-principles/scripts/test_surface_canon.py (the source of the ported test — read all 3 tests before porting)
  - loom-interface-design/scripts/test_design_system_skill.py (the local test idiom + the flat-folder guard at ~:180-189)
- Acceptance:
  - RED: `loom-interface-design/scripts/test_surface_canon.py::test_surface_canon_file_contract` fails — the canon file is absent from its new home.
  - GREEN: that test passes at the new path, asserting the SAME contract as before (≥**5** data rows — the 5-row floor, NOT the 14 that `test_canon_references.py`'s four canons require; a Currency column; ≥1 WCAG risk flag; "never shown raw to the user"; "including but not limited to"; the grounding-doc citation; every row carrying a markdown-link source URL). Both package suites stay green.
- **THE SELF-DESTRUCT TEST**: `loom-product-principles/scripts/test_surface_canon.py::test_surface_canon_carries_design_stage_forward_note` (~:132-162) asserts the file still says "deferred to Step 2" / "defer". **DELETE it — do NOT port it.** Step 2 removes the very forward-note it guards; a mechanical copy of the test file yields a red suite. This is the trap the recon flagged.
- **`test_surface_research_doc_grounds_seed`** (~:165-186) guards the REPO-LEVEL research doc (`docs/loom/research/...`), which does NOT move. **DECIDED (not the implementer's call): PORT it** to `loom-interface-design/scripts/test_surface_canon.py`. It is REPO_ROOT-anchored, so it works from either plugin, and porting it means `loom-product-principles/scripts/test_surface_canon.py` is **deleted wholesale** — which is what `Files touched` declares. The research doc stays guarded by exactly one live test, in the plugin that now owns the canon it grounds.
- **Net test counts**: `loom-product-principles` **275 → 272** (3 tests leave: contract ported, forward-note deleted, research-doc guard ported). `loom-interface-design` **77 → 79** (contract + research-doc guard arrive; T5 adds the third later).
- **`test_canon_references.py`'s `CANON_FILES` (~:34-39) lists only FOUR canons** — `canon-design-surface.md` is deliberately absent, so removing the file does NOT break it. Confirm this by running the product-principles suite.
- External surfaces: none.
- Dependencies: none (the file move + its test are self-contained; the SKILL.md wiring that CONSUMES it is Task 4, the product-principles repair is Task 6)
- Independent: true
- Brief item covered: "MOVE canon-design-surface.md → loom-interface-design/skills/design-system/references/. Delete the forward-note." + "delete its self-destruct test, don't move it."

## Task 4 — port the candidate-pick protocol into design-system (2B — the bulk)

- Description: Give `design-system` a **surface-treatment pick** it has never had.
  Today it commits ONE agent-authored visual concept with no menu, no rejection list,
  and **no user decision**. Port the protocol from product-principles: at the
  visual-concept beat, **propose 3-5 surface-treatment candidates** drawn from
  `references/canon-design-surface.md` with **fit/tension** notes, **surface 1-2
  considered-but-rejected** candidates with reasons, and let the **USER DECIDE**
  (a "bespoke — no canon fits" escape hatch is legal). The chosen treatment is
  **NAMED and RATIONALIZED in prose** inside the existing Overview/Brand section —
  "Surface treatment: X — because \<the tone & manner adjectives\> + \<constraint\>" —
  and it then **constrains the `## Elevation & Depth` and `## Shapes` token blocks**
  (those already ship `surface`, `shadows` and border tokens; the treatment is
  precisely a choice over them). Two rules carry over from the upstream canon:
  the **anti-costume law** (a treatment may enrich candidates but NEVER overrides a
  PRINCIPLES value) and the **WCAG risk flag is a BLOCKER, not a note** (the schema
  already makes WCAG-AA a blocker; a treatment whose flag is unresolved cannot ship).
  The candidates are **downstream of the tone & manner anchor** (Task 1) — the
  adjectives constrain which treatments are even proposable.
- Module: loom-interface-design/skills/design-system/SKILL.md
- Files touched: loom-interface-design/skills/design-system/SKILL.md, loom-interface-design/scripts/test_design_system_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md (~:110-127 the candidate round + rejection guard + canon audit; ~:167-190 the 3-5 carve-out, divergent candidates, anti-costume law, "Step 4 — user decides" + bespoke escape hatch — THIS is the protocol being ported; do not re-invent it)
  - loom-interface-design/skills/design-system/references/canon-design-surface.md (the canon it proposes from — Task 3 puts it there)
  - loom-interface-design/skills/design-system/references/design-md-schema.md (Overview/Brand is where the pick is named; `## Elevation & Depth` + `## Shapes` are what it constrains)
- Acceptance:
  - RED: `test_design_system_skill.py::test_surface_treatment_candidate_pick_protocol` fails — SKILL.md has no candidate round, no user decision, and never cites the surface canon.
  - GREEN: the test passes by asserting SKILL.md (a) cites `references/canon-design-surface.md` by relative path (mirroring the existing `test_body_references_schema_by_relative_path` idiom at ~:98-101), (b) proposes **3-5** surface-treatment candidates with fit/tension, (c) surfaces **1-2 considered-but-rejected** with reasons, (d) states the **USER decides** (with the bespoke escape hatch), (e) requires the pick to be NAMED + rationalized in prose in Overview/Brand, (f) states the pick constrains the Elevation & Depth + Shapes tokens, (g) carries the anti-costume law, and (h) makes the WCAG risk flag a blocker. Pin FULL PHRASES; a bare "3-5" is a false-green risk if it appears elsewhere.
  - The 8 DESIGN.md sections and `validate_design_output.py` are UNCHANGED — assert the existing 8-section test still passes.
- External surfaces: none.
- Dependencies: Tasks 1, 2, 3 complete first (T1 owns SKILL.md's Step-2 anchor wording — same file, and the candidates must be stated as downstream of it; T3 puts the canon file at the path this task cites; **T2 is declared because T2 and T4 both write `test_design_system_skill.py`** — the T1→T2→T4 chain must be encoded in the DAG, not merely asserted in Notes, since SDD reads only `Dependencies`).
- Independent: false
- Brief item covered: "design-system gains a surface-treatment pick: propose 3-5 candidates from the canon (fit/tension notes, 1-2 considered-but-rejected surfaced), the user decides, and the pick is named + rationalized in prose in Overview/Brand … The chosen treatment then constrains the `## Elevation & Depth` + `## Shapes` token blocks. Anti-costume law carries over … WCAG risk flag is a blocker, not a note."

## Task 5 — expand the surface catalog 6 → ~18 rows (2B)

- Description: Grow `canon-design-surface.md`'s table from 6 to ~18 rows using the
  **12 committed candidates** at `docs/loom/research/2026-07-12-ui-surface-treatments-canon.md`
  **§Part 2** (Web 1.0/GeoCities, Web 2.0 gel, Frutiger Aero, long-shadow/Flat 2.0,
  dark mode, Aurora mesh-gradient, Claymorphism, Material You, neubrutalism,
  retro-terminal/CRT, anti-design, Bento grid). Each row carries the file's existing
  column shape (Entry | Fits when… | Stability | Currency | Source) — the research doc
  supplies all five plus a scope tag and a WCAG flag per entry.
  **URL RULES (both have already bitten this project)**: (1) copy each URL string
  **verbatim** from the research doc — a fabricated URL was caught in #550's review and a
  plausible-looking 404 in #553's research; **never retype from memory**; (2) wrap it in
  the **markdown-link cell shape** `[label](url)` — the per-row assertion matches that
  form ONLY, so a bare URL fails every new row. **Re-check URL liveness** before
  committing (link rot) — report any dead link instead of shipping it.
  Carry each entry's **WCAG risk flag** into its row (dark mode, Material You, Aurora,
  Claymorphism, neubrutalism and anti-design all have one). Note the two findings the
  research doc records: **neubrutalism is Axis B**, not the Axis-A cultural
  neo-brutalism already in `canon-design-visual.md` (do not merge them); and **Frutiger
  Aero's 2023- revival is a Currency-cell update, not a second row**.
  **Bento grid is tagged `layout`, not `surface`** — include it but keep the tag honest.
- Module: loom-interface-design/skills/design-system/references/canon-design-surface.md
- Files touched: loom-interface-design/skills/design-system/references/canon-design-surface.md, loom-interface-design/scripts/test_surface_canon.py
- Context paths:
  - docs/loom/research/2026-07-12-ui-surface-treatments-canon.md (§Part 2 — the 12 entries + their verbatim URLs + WCAG flags + scope tags)
  - loom-interface-design/skills/design-system/references/canon-design-surface.md (the existing 6 rows + column shape — Task 3 puts it here)
- Acceptance:
  - RED: `test_surface_canon.py::test_surface_canon_covers_the_full_era_cycle` fails — the canon carries only the 6 seed rows, missing the expansion entries.
  - GREEN: the test passes by asserting the canon (a) has **≥15 data rows**, (b) names a representative sample of the expansion entries (e.g. neubrutalism, dark mode, Frutiger Aero, claymorphism), (c) every row still carries a markdown-link source URL, and (d) the rows carrying a WCAG risk (dark mode, Material You, Aurora, claymorphism, neubrutalism, anti-design) each flag it. Existing contract (Currency column, never-shown-raw, grounding-doc citation) stays green.
- External surfaces: the 12 source URLs are external references — already live-verified during research; the implementer **copies them verbatim from the research doc** and re-checks liveness, and does NOT re-derive or invent them.
- Dependencies: Task 3 completes first (same file — T3 relocates it and rewrites its framing; T5 grows the table below).
- Independent: false
- Brief item covered: "Expand the catalog 6 → ~18 rows from the 12 committed candidates."

## Task 6 — repair product-principles to a single Axis-A round (2B)

- Description: With Axis B gone, product-principles' SKILL.md carries **dangling
  references**. Repair BOTH: (a) the **five-file canon audit list** (~:120-127) now
  names a file that is no longer in this plugin — drop `canon-design-surface.md` from
  it (leaving four); (b) the **two-round Axis-A/Axis-B paragraph** (~:139-146) must be
  **REWRITTEN to a single Axis-A round**, not merely trimmed — it currently instructs
  two axis-typed rounds, a contamination guard between them, and complementary
  separate `## Anchors` rows. The **contamination guard becomes free** (the axes now
  live in different plugins, so their contexts cannot co-occur in one round by
  construction) — but the sentences asserting it are pinned by tests, so restate the
  new truth: the visual lens runs ONE Axis-A round here, and the surface-treatment
  axis is decided downstream at the DESIGN station (`loom-interface-design`). Keep the
  visual-lens 3-5 carve-out and the 1-2 divergent candidates (they belong to Axis A).
  Update the tests that pin the old two-round wording.
- Module: loom-product-principles/skills/product-principles/SKILL.md
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md (the audit list ~:120-127; the two-round paragraph ~:139-146)
  - loom-product-principles/scripts/test_product_principles_skill.py (the #550/#553 invariant pins that reference two rounds / the contamination guard / complementary Anchors rows — these MUST be updated, not deleted wholesale: the Axis-A half of each still holds)
- Acceptance:
  - RED: `test_product_principles_skill.py::test_visual_lens_is_single_axis_a_round` fails — SKILL.md still describes two axis-typed rounds and names canon-design-surface.md.
  - GREEN: the test passes by asserting SKILL.md (a) no longer references `canon-design-surface.md` anywhere, (b) describes ONE Axis-A visual round, and (c) states the surface-treatment axis is decided downstream at the DESIGN station. The tone & manner anchor, the visual 3-5 carve-out, the 1-2 divergent candidates and the anti-costume law all still pass their existing pins.
- External surfaces: none.
- Dependencies: Task 3 completes first (the file must actually be gone from this plugin before its references are called dangling — and T3's mv is what makes the RED honest).
- Independent: false
- Brief item covered: "REPAIR the two-sided edit in product-principles: the five-file canon audit list and the two-round Axis-A/Axis-B paragraph … must be rewritten to a single Axis-A round."

## Task 7 — repair question-sets.md to a single Axis-A round (2B)

- Description: Same repair as Task 6, applied to
  `references/question-sets.md`'s Design lane, which carries the same two-round
  Axis-A/Axis-B wording and the contamination guard. Rewrite to a single Axis-A round;
  state that the surface-treatment axis is decided downstream at the DESIGN station.
  Keep the tone & manner anchor step (#553), the visual 3-5 carve-out, the 1-2
  divergent candidates, and the interaction lens staying 2-3.
- Module: loom-product-principles/skills/product-principles/references/question-sets.md
- Files touched: loom-product-principles/skills/product-principles/references/question-sets.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/question-sets.md (Design lane — the two-round wording)
  - loom-product-principles/skills/product-principles/SKILL.md (Task 6's canonical single-round phrasing — mirror it, do not paraphrase)
- Acceptance:
  - RED: `test_product_principles_skill.py::test_question_sets_visual_lens_is_single_axis_a_round` fails — the Design lane still describes two axis-typed rounds.
  - GREEN: the test passes by asserting question-sets.md no longer references canon-design-surface.md, describes ONE Axis-A round, and names the DESIGN station as the surface axis's home. Existing Design-lane pins (tone & manner anchor ordering, 3-5, divergent, interaction 2-3) stay green.
- External surfaces: none.
- Dependencies: Tasks 3, 6 complete first (T3 makes the reference dangling; T6 fixes the canonical wording this task mirrors AND shares the same test file — serialize).
- Independent: false
- Brief item covered: "Same two-round wording in references/question-sets.md."

## Task 8 — bump loom-interface-design 0.4.2 → 0.5.0 + codex sync

- Description: Bump `loom-interface-design/.claude-plugin/plugin.json` 0.4.2 → 0.5.0
  (minor — new capability: the inherited anchor + the surface-treatment pick + the
  relocated canon) and run
  `python3 scripts/sync_codex_manifests.py loom-interface-design` to regenerate the
  codex mirror. SSOT is `.claude-plugin/plugin.json`; **never hand-edit**
  `.codex-plugin/plugin.json`.
- Module: loom-interface-design/.claude-plugin/plugin.json
- Files touched: loom-interface-design/.claude-plugin/plugin.json, loom-interface-design/.codex-plugin/plugin.json
- Context paths:
  - scripts/sync_codex_manifests.py (Read its CLI before running)
  - scripts/test_sync_codex_manifests.py (the drift oracle, ~:368)
- Acceptance:
  - RED: after bumping the SSOT and BEFORE running the sync, `scripts/test_sync_codex_manifests.py::test_all_eligible_codex_manifests_in_sync` FAILS (the mirror drifted). Red-by-construction.
  - GREEN: that test passes after the sync AND `.claude-plugin/plugin.json` reads `"version": "0.5.0"`.
- External surfaces: none.
- Review-weight: mechanical (deterministic sync-script category — exact invocation `python3 scripts/sync_codex_manifests.py loom-interface-design`, named SSOT `.claude-plugin/plugin.json`)
- Dependencies: none (manifest files are disjoint from every other task's files)
- Independent: true
- Brief item covered: "Four version bumps … loom-interface-design .claude-plugin + .codex-plugin (0.4.2 → 0.5.0)."

## Task 9 — bump loom-product-principles 0.8.0 → 0.9.0 + codex sync

- Description: Bump `loom-product-principles/.claude-plugin/plugin.json` 0.8.0 → 0.9.0
  (minor — the visual lens loses the Axis-B round; the surface axis moves downstream)
  and run `python3 scripts/sync_codex_manifests.py loom-product-principles`. Never
  hand-edit the codex mirror.
- Module: loom-product-principles/.claude-plugin/plugin.json
- Files touched: loom-product-principles/.claude-plugin/plugin.json, loom-product-principles/.codex-plugin/plugin.json
- Context paths:
  - scripts/sync_codex_manifests.py (Read its CLI before running)
  - scripts/test_sync_codex_manifests.py (the drift oracle, ~:368)
- Acceptance:
  - RED: after bumping the SSOT and BEFORE the sync, `scripts/test_sync_codex_manifests.py::test_all_eligible_codex_manifests_in_sync` FAILS. Red-by-construction.
  - GREEN: that test passes after the sync AND `.claude-plugin/plugin.json` reads `"version": "0.9.0"`.
- External surfaces: none.
- Review-weight: mechanical (deterministic sync-script category — exact invocation `python3 scripts/sync_codex_manifests.py loom-product-principles`, named SSOT `.claude-plugin/plugin.json`)
- Dependencies: Task 8 completes first. **Why, despite disjoint `Files touched`**: T8 and T9 share a repo-GLOBAL test oracle — `test_all_eligible_codex_manifests_in_sync` loops EVERY eligible plugin and asserts one global `offenders == []`. Run in the same wave, each task's un-synced bump keeps the OTHER's GREEN false, so the implementer would chase a GREEN that never arrives and be tempted to "fix" the sibling task's manifest (a cross-task boundary violation). Serializing costs one level and removes the shared-state trap entirely.
- Independent: false
- Brief item covered: "Four version bumps … loom-product-principles .claude-plugin + .codex-plugin (0.8.0 → 0.9.0)."

## Dependency graph

```
Level 1 (parallel):   T1            T3                   T8
                      │             │                    │   (indep ×3)
Level 2:              T2      T5 ───┤   T6 ──┐           T9
                      │      (T3)   │  (T3)  │          (T8)
Level 3:              T4 (T1,T2,T3) ┘        T7 (T3,T6)
```

Critical-path depth: **3** — longest chains are T1 → T2 → T4 and T3 → T6 → T7 (both
length 3). Wide at level 1 (three independent leaves: T1, T3, T8).

## Notes

- **Same-file serialization** (every same-file pair is ordered by a DECLARED
  `Dependencies` edge — SDD reads only that field, never this prose):
  - `design-system/SKILL.md`: T1 → T4
  - `design-md-schema.md`: T2 only
  - `canon-design-surface.md` (new home): T3 → T5
  - `product-principles/SKILL.md`: T6 only
  - `question-sets.md`: T7 only
  - `test_design_system_skill.py`: T1 → T2 → T4 (**T4 declares dep on T2** — this was a
    round-1 review finding: the chain existed only in prose, so the DAG permitted
    T2 ‖ T4 on one file)
  - `loom-interface-design/scripts/test_surface_canon.py`: T3 → T5
  - `test_product_principles_skill.py`: T6 → T7
- **The three `Independent: true` tasks (T1, T3, T8) have pairwise-disjoint
  `Files touched`** — safe for one parallel wave.
- **T9 is NOT parallel with T8** despite disjoint files: they share a repo-GLOBAL test
  oracle (`test_all_eligible_codex_manifests_in_sync` asserts one global
  `offenders == []` across every eligible plugin), so a same-wave run leaves both
  GREENs unreachable until BOTH manifests are synced. Round-1 review finding.
- **THE SELF-DESTRUCT TEST (T3)**: `loom-product-principles/scripts/test_surface_canon.py::test_surface_canon_carries_design_stage_forward_note`
  must be **DELETED, not ported**. It asserts the file still says "deferred to Step 2";
  Step 2 removes that note. A mechanical copy of the test file yields a red suite.
- **DO NOT** add a 9th DESIGN.md section or touch `validate_design_output.py`'s
  8-section order check (brief §Out of Scope). The surface pick rides in Overview/Brand
  prose — this is what keeps the frozen 8-section contract (pinned in three places)
  out of the blast radius, and it is what the industry actually does (Apple names
  "Liquid Glass" in prose; the W3C token format has no slot for art direction).
- **DO NOT build a parser/grep of the Anchors row** (T1). Axis-4 research settled
  READ-AND-HONOR: a regex over a Markdown heading couples to formatting and degrades
  silently. The reversal trigger (measured drift in dogfood) is recorded in the brief.
- **URL discipline (T5)**: copy verbatim from the research doc, wrap in `[label](url)`,
  re-check liveness. A fabricated URL was caught in #550; a plausible 404 in #553.
- **Guard precision**: pin FULL PHRASES, and for any ORDERING/relational claim use a
  positional assertion (`index() <`), never membership — see
  `docs/loom/memory/assertion-must-encode-the-property-it-claims.md` (the #553 lesson:
  a guard whose docstring claims order but asserts membership passes on the violated
  state, and the per-task triad will not catch it).
- **Baselines**: interface-design **77**, product-principles **275**, scripts **28**.
  Expected after the branch: product-principles **272** (T3 removes 3, T6/T7 add pins),
  interface-design **79+** (T3 ports 2, then T1/T2/T4/T5 add pins).
- Every task's tests are structural grep-tests over skill prose (pytest, stdlib +
  path-based) — that is the TDD surface for this repo.
- **Amendment record**: revised after plan-document-reviewer round 1 (NEEDS_REVISION,
  11/14). Three fixes: (1) T4's `Dependencies` now includes T2 — the shared
  `test_design_system_skill.py` chain was asserted in prose but absent from the DAG;
  (2) T3's "port it or leave it — implementer's call" for
  `test_surface_research_doc_grounds_seed` was **decided in the plan** (port it), because
  an `Independent: true` task whose write-set depends on an unmade choice is not a valid
  disjointness oracle; (3) T9 serialized after T8 — they share a repo-global test oracle,
  so a same-wave run makes both GREENs unreachable. Also corrected the stale `scripts/`
  baseline (15 → 28). Depth unchanged at 3. **Round 2 returned PASS (14/14)**; its one
  actionable advisory is folded in below.
- **T5 must UPDATE, not duplicate, the row-count assertion** (round-2 advisory): T3's
  GREEN pins `≥5` canon rows and T5's GREEN raises it to `≥15` — in the SAME test file.
  T5's implementer edits the existing `MIN_SURFACE_ROWS` constant / assertion rather than
  adding a second, contradictory one.
