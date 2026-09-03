# Skill token-reduction triage — fat tail (>3,000 words)

**Date:** 2026-07-15 · **Method:** mechanical inventory of all 193 SKILL.md (wc -w) → 6 parallel read-only triage agents over the 25 open fat-tail skills (>3,000 words, excluding #559-frozen SDD/writing-plans, #571-just-slimmed skill-judge/requesting-code-review/spec-expansion, and line-pinned skill-creator-advance/daily-news-digest). Each agent grepped owning-plugin `scripts/` + repo `.claude/hooks/` for lockstep tests and checked freeze markers before verdicting.

**Bottom line:** 63% of skills (122/193) are ≤2,000 words — leave them. Real recoverable cost is ~7,900 words (conservative) / ~13,000 (optimistic) across the fat tail, PLUS two cross-family structural dedups bigger than any single slim. Every "real slim" needs a #571 equivalence gate; prioritize by ROI × risk below.

## PROCEED — low-risk, clear ≥10% reduction (16 skills)

| skill | words | recoverable | mechanism |
|---|---|---|---|
| systems-thinking:cld-craft | 5,016 | 700–780 (14–16%) | EXTRACT boundary-notes tail → references/ |
| systems-thinking:simulation-modeling | 4,340 | 650–730 (15–17%) | EXTRACT boundary tail |
| systems-thinking:strategy-lever-and-cascade | 4,113 | 650–730 (16–18%) | EXTRACT boundary tail |
| systems-thinking:cld-archetypes | 4,073 | 550–610 (13–15%) | EXTRACT boundary tail |
| systems-thinking:cld-overlay | 3,386 | 480–520 (14–15%) | EXTRACT tail + cut ~130w cld-craft restatement |
| repo-wiki:init | 4,285 | 500–900 (12–21%) | EXTRACT author-boundary table + Phase 3 (opt-in) |
| dbt-wiki:rescan | 3,680 | 800–1,500 (22–41%) | EXTRACT Step 6.4/6.5 stale-detection pseudocode |
| dbt-wiki:pack | 3,027 | 350–650 (12–21%) | EXTRACT Step 7 acceptance script → bundle-format.md |
| loom-code:finishing-a-development-branch | 3,194 | 650–900 (20–28%) | EXTRACT Red Flags table (test-grep clean) |
| loom-code:brainstorming | 3,580 | 650–850 (18–22%) | EXTRACT Red Flags + Axis-4 template → axis4-research-protocol.md |
| domain-teams:copywriting-team | 4,098 | 400–900 (10–22%) | DEDUP 6× Phase-0 rows + COMPRESS manifest |
| dev-workflow:distill-sessions | 3,620 | 450–800 (12–22%) | EXTRACT roadmap + pycache workaround |
| four-dx:4dx-meta-xps-evaluation | 3,432 | 300–450 (9–13%) | EXTRACT A1 cases (matches sibling pattern) |
| domain-teams:research-team | 3,288 | 300–600 (9–18%) | DEDUP 4 workflow tables → one template |
| systems-thinking:team-mental-model | 3,376 | 250–400 (7–12%) | DEDUP proxy-list + EXTRACT facilitation script |
| obsidian:wiki-ingest | 3,122 | 200–500 (6–16%) | EXTRACT wikilink examples → page-format.md |

## CAUTION — reduction real but risk/effort per token is high (9 skills)

| skill | words | recoverable | risk basis |
|---|---|---|---|
| research-toolkit:deep-deep-research | 5,309 | **1,800–2,600 (34–49%)** | biggest raw win; no test pins prose, BUT PREPEND order + degradation wording is load-bearing — must preserve verbatim in extracted files |
| dbt-wiki:init | 6,476 | 600–1,300 (9–20%) | siblings cite its step labels by name; dense bash contract |
| copywriting-toolkit:copywriting-voice-tone-stage | 3,265 | 400–900 (12–28%) | JSON schema shape consumed cross-phase; documents a breaking-change migration |
| investing-toolkit:analysis-kpi | 3,082 | 300–700 (10–23%) | sole prose ref for per-CLI exit-code semantics; must preserve every distinction |
| loom-spec:completeness-critic | 3,840 | 150–400 (4–10%) | test greps load-bearing keywords through nearly every section — almost no slack |
| investing-toolkit:report-equity-memo | 3,645 | 200–500 (5–14%) | **committed test pins** phase headings + filename tokens (test_cross_layer_chains.py) |
| dev-workflow:dbt-model-style | 3,573 | 150–350 (4–10%) | validate_header.py checks field names named in prose; SQL examples prescriptive |
| systems-thinking:manager-personality-quadrant | 3,228 | 150–400 (5–12%) | "non-negotiable per user override" clause binds adjacent block |
| four-dx:4dx-audit | 3,276 | 100–250 (3–8%) | already lean; remaining bulk is prescriptive worked-example output |

## Two cross-family structural dedups — bigger than any single slim

1. **domain-teams Gate-Protocol boilerplate** — the "Handle verdict" block (PASS / PASS_WITH_NOTES / NEEDS_REVISION + max-2-rounds) and worker/evaluator Behavioral Rules are byte-near-identical across ALL ~10 domain-teams skills. One shared reference saves across 10 SKILL.md at once. **Caveat:** domain-teams' knowledge layer is a byte-identical functional copy synced to loom-code via `distribute.py` — this refactor touches that contract; higher blast radius, separate careful arc.
2. **dbt-wiki resolve-dbt-dir bash** — the 5-tier project-root detection block is duplicated near-verbatim across init/rescan/query (+likely pack). One shared `assets/resolve_dbt_dir.sh` (sourced) or reference. 3–4 files, medium win.

## Recommended execution order (each tier = one equivalence-gate arc)

- **Tier 1 — systems-thinking CLD family (5 skills, ~3,000w).** All PROCEED, uniform mechanism (extract the identical boundary-notes tail), zero test coupling. Prove the pattern on cld-craft under the gate, then batch-apply the same extraction to the other 4 (de-escalation per model-dispatch §3.4). Cleanest, lowest-risk, high aggregate.
- **Tier 2 — deep-deep-research (1 skill, 1,800–2,600w).** Biggest single win by far; CAUTION → do it carefully alone with the gate, preserving PREPEND/degradation text verbatim.
- **Tier 3 — cross-family dedups.** dbt-wiki resolve-dir first (smaller blast radius), then domain-teams gate-protocol (touches the distribute.py copy contract — most care).
- **Tier 4 — misc PROCEED singles.** dbt-wiki:rescan, finishing, brainstorming, repo-wiki:init, distill-sessions, copywriting-team, research-team, 4dx-meta, team-mental-model, wiki-ingest — pick by appetite.
- **Defer — the test-pinned CAUTION set** (report-equity-memo, dbt-model-style, completeness-critic, analysis-kpi, voice-tone-stage): reduction is small and risk/effort per token is high.

## Not touched (excluded upfront)
SDD 4,152 / writing-plans 4,090 (#559 frozen) · skill-judge 4,533 / requesting-code-review 3,706 / spec-expansion 3,584 (#571 just slimmed) · skill-creator-advance 4,495 / daily-news-digest 4,495 (line-pinned) · 122 skills ≤2,000w (negative ROI).
