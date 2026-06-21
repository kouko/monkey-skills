# Plan: framework-audit blind-spots canon rewrite (2-axis, ~7) + domain-gap filing

Source brief: docs/loom/specs/2026-06-13-framework-audit-blindspots-canon-rewrite.md
Total tasks: 4
Critical-path depth: 3 (T1 → T2 → T4; T3 branches off T1 in parallel) — ≤5
Execution order: parallel-where-possible (T3 ∥ T2/T4 after T1)
Plan-document-reviewer verdict: PASS (2026-06-13, 14/14; T1 noted upper-bound size, defensible single unit)
Amendment (post-T1, additive — re-review skipped per skill amend-rule): T1's reviewers found the count "12" also appears in two prose pointers the plan missed — library L21 ("run the 12 collective blind-spots") and SKILL.md L193 ("12 collective blind-spots at the bottom of the library"). Folded into T2 (library L21) and T3 (SKILL.md L193) — no new task, no DAG/dep change, no Independent-flag change (SKILL.md is disjoint from library MD, T3 stays Independent:true). **Do NOT touch SKILL.md L99 `CANDIDATE_COUNT (12)`** — that is the VS angle-selector count, unrelated to blind-spots.

## Notes

- **English-only hard constraint**: `references/framework-audit-library.md` must stay English-only — `grep -cP '[\x{4e00}-\x{9fff}]'` on it must remain **0** (T1 [T1]-verified pre-state). All canon is in Chinese research notes; the implementer **translates into English prose**. JP concepts are **romanized + glossed**, never CJK (e.g. `shikō teishi (thought-stopping)`, `keigaika (checklist ossification)`, `Iriyama's theory-vs-framework distinction`). A single CJK character fails the existing CJK-guard test.
- **Same-file serialization**: T1, T2, T4 all edit `framework-audit-library.md` → a sequential chain (never `Independent: true` among themselves; shared git index — see `feedback_parallel_implementers_one_worktree_interleave_commits`). Only **T3** (code files) is disjoint and parallel-eligible after T1.
- **Commit discipline**: if T3 is dispatched in parallel with the library chain, the **orchestrator commits** (implementers don't), or dispatch sequentially — same lesson.
- **Verification** (Stage 7, not a plan task): after all tasks, run package-level `pytest -q` in the skill's `scripts/` (expect 74→still green at new count), sibling suites (fact-check 28 / cite-check 41 / deep-read 26), `grep -cP CJK` library = 0, and synced-primitive drift empty. `framework_audit.py` is house code (NOT a synced primitive) — safe to edit.

## Task 1 — Rewrite blind-spots section: header + anchor + 7 items (2 axes)

- Description: In `references/framework-audit-library.md`, replace the "## Collective blind-spots (12, meta-level)" section's **header + intro + numbered list** with the reshaped design. Header → `## Collective blind-spots (7, meta-level)`. Write the **section anchor** (rationale): any single framework sees only what its cells encode (Maslow law-of-instrument / Munger; multi-framing — Bolman-Deal "each frame… a product of blind spots", Morgan, Allison); after the walk, two omission classes remain regardless of domain; self-applied completeness canons = **Decision Quality six-element chain (Spetzler/SDG 2016)** + **IC analytic standards (ICD 203)**; cognitive root = **Kahneman WYSIATI**; honest notes (not itself a named canon → cite per item; items can cross axes per Cooper; KLS-2011 demoted to an Axis-B pointer); one line noting **questioning the frame / enumerating alternatives is the framework walk's own job, not repeated here**. Then the **7 numbered items**: Axis A — structural (3): A1 Time & dynamics, A2 Second-order/reflexivity, A3 Feasibility-power-reversibility (incl Bezos one-/two-way door); Axis B — cognitive (4): B1 Outside-view/base-rates (focusing-illusion folded in), B2 Disconfirming-evidence/rival-hypotheses, B3 Uncertainty & evidence-quality, B4 Unknown-unknowns. Each item carries ≥1 citation (see brief Decision for the per-item anchors). English-only.
- Module: references/framework-audit-library.md
- Files touched: research-toolkit/skills/deep-deep-research/references/framework-audit-library.md
- Context paths:
  - docs/loom/specs/2026-06-13-framework-audit-blindspots-canon-rewrite.md (Decision §, per-item anchors)
  - research-toolkit/skills/deep-deep-research/references/framework-audit-library.md (current section L212-231; framework cells for citation phrasing)
  - /Users/kouko/kouko-obsidian-vault/research/2026-06-13 完整性稽核器的盲點 canon — 第三輪（purpose-matched：DQ／ICD203／bias-as-omission）.md (canon SSOT — translate to EN)
- Acceptance:
  - RED: `grep -c "Collective blind-spots (7, meta-level)" references/framework-audit-library.md` → 0 (file currently says "(12, meta-level)").
  - GREEN: header is `## Collective blind-spots (7, meta-level)`; section has **exactly 7** numbered items under two axis subheads (3 structural + 4 cognitive); anchor prose contains `Decision Quality`, `ICD 203`, `WYSIATI`, `Bolman` (multi-framing) and frames instrument-bias as the rationale; each of the 7 items contains a citation; `grep -cP '[\x{4e00}-\x{9fff}]' references/framework-audit-library.md` = 0.
- External surfaces: none (prose).
- Dependencies: none
- Independent: false
- Brief item covered: "Build a clean-slate universal meta-list from canon, 2-axis by omission-source, RESHAPED to ~7 numbered items" + the Axis A/B item list (brief Decision §).

## Task 2 — Add demoted notes + guardrail; verify no-regression coverage

- Description: In the same section of `framework-audit-library.md` (after T1's items), add the **demoted notes** — values/normative as a *conditional* note ("for high-stakes / normative questions, add the ethical lenses + stakeholder ethics"), and a distribution/tails sub-bullet ("aggregates hide who-wins-who-loses and the tail — check distribution, esp. for risk/policy") — and the **guardrail (not numbered)**: audit-as-justification / thought-stopping (an empty gap is a legitimate honest result; don't let "ran the audit" become the goal), grounded in **RAND RR-1408** (devil's-advocacy can backfire; SAT coverage gains are preliminary; box-checking ≠ coverage) + JP romanized `shikō teishi` / `keigaika`; plus the motivation/social layer note (self-interest / affect / groupthink — Kunda; mostly out of scope, flag when the analyst has a stake). English-only, JP romanized + glossed (no CJK). Then verify **no-regression**: every old-12 concern (time-decay, subsegment/granularity, base-rates, second-order, unknown-unknowns, power/feasibility, distribution, instrument-bias, evidence-quality, normative, execution-gap, uncertainty) is represented by an item or a note.
- Module: references/framework-audit-library.md
- Files touched: research-toolkit/skills/deep-deep-research/references/framework-audit-library.md
- Context paths:
  - docs/loom/specs/2026-06-13-framework-audit-blindspots-canon-rewrite.md (Decision § "Demoted to notes" + "Guardrail" + "Coverage cross-check vs old 12")
- Acceptance:
  - RED: `grep -ci "RAND RR-1408" references/framework-audit-library.md` → 0 in the blind-spots section (guardrail absent).
  - GREEN: section contains a guardrail paragraph citing `RAND RR-1408`; a values **conditional** note mentioning `high-stakes`; a distribution/tails sub-note; the motivation/social note; old-12 coverage cross-check holds (all 12 concerns map to an item or note — reviewer-verifiable list); `grep -cP '[\x{4e00}-\x{9fff}]' references/framework-audit-library.md` = 0.
- External surfaces: none (prose).
- Dependencies: Task 1 completes first (same section of the same file — sequential edit).
- Independent: false
- Brief item covered: brief Decision § "Demoted to notes (NOT numbered slots)", "Guardrail (not numbered)", "Coverage cross-check vs old 12 (no regression…)".

## Task 3 — Code coupling: BLIND_SPOT_COUNT 12→7 + test

- Description: In `scripts/framework_audit.py` set `BLIND_SPOT_COUNT: int = 7` (was 12) and update its descriptive comment (L112-113) from "12" to "7". In `scripts/test_framework_audit.py` update the meta-check assertion `assert "12" in prompt` → `assert "7" in prompt` and the comment "(g) references the 12 collective blind-spots" → "7". (The `audit_prompt` builds its section title from `BLIND_SPOT_COUNT`, and its step-4 examples — time-decay / base rates / second-order / unknown-unknowns — all survive as items, so the prompt body needs no other change.)
- Module: scripts (framework_audit.py + its test)
- Files touched: research-toolkit/skills/deep-deep-research/scripts/framework_audit.py, research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/framework_audit.py (L107-178)
  - research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py (L145-160)
- Acceptance:
  - RED: update the test assertion to `assert "7" in prompt` first → `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q test_framework_audit.py` fails (code still emits "12" in the title).
  - GREEN: with `BLIND_SPOT_COUNT = 7`, `pytest -q` passes; full skill suite green (74 expected; confirm count unchanged); the built prompt title reads "Collective blind-spots (7, meta-level)" — matching the library header from T1.
- External surfaces: none (stdlib pytest; existing verb, no new command-surface entry).
- Dependencies: Task 1 completes first (the count `7` is pinned by the rewritten section; if T1's final granularity shifts, this value follows it).
- Independent: true   # disjoint files from T2/T4 (code vs library MD); no semantic dep beyond the brief-pinned count
- Brief item covered: brief Decision § "Count target: 7 … `BLIND_SPOT_COUNT` 12→7 … test `assert "12"`→`assert "7"`".

## Task 4 — Domain-gap filing into domain framework cells

- Description: In `framework-audit-library.md`, file the two domain-specific gaps into their **domain cells** (NOT the universal list): (1) **Talent / key-person concentration** → Economic Moat cell (L144-147: moat durability depends on retaining the architects/key talent) AND Equity Risk Taxonomy (L149-152: add key-person as a company-specific risk); (2) **Platform / external-dependency obsolescence** → Business strategy section (the entitlement/API you depend on gets cut mid-stream; attach near Wardley evolution/commoditization, routing L42). Small additive edits to existing cells. English-only. (Relative-valuation execution discipline is already in the DCF+Comparables cell — no action.)
- Module: references/framework-audit-library.md
- Files touched: research-toolkit/skills/deep-deep-research/references/framework-audit-library.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/references/framework-audit-library.md (L137-152 Investment/finance; L125 Business strategy; L42 routing)
  - docs/loom/specs/2026-06-13-framework-audit-blindspots-canon-rewrite.md (Decision § "Domain-gap filing")
- Acceptance:
  - RED: `grep -ci "key-person" references/framework-audit-library.md` → 0 (not yet filed).
  - GREEN: Economic Moat cell mentions key-person/talent retention as a durability factor; Equity Risk Taxonomy lists key-person concentration; Business strategy section mentions platform / external-dependency obsolescence; `grep -cP '[\x{4e00}-\x{9fff}]' references/framework-audit-library.md` = 0.
- External surfaces: none (prose).
- Dependencies: Task 2 completes first (same file as T1/T2 — serialize same-file edits to avoid index/edit conflict; no semantic dependency on the blind-spots content).
- Independent: false
- Brief item covered: brief Decision § "Domain-gap filing (this brief): Talent/key-person … → Economic Moat + Equity Risk; Platform/external-dependency obsolescence → Business strategy/Wardley".
