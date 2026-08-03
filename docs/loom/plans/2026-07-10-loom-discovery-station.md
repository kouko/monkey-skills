# Plan: loom-discovery station (business-value + user-insights)

Source brief: docs/loom/specs/2026-07-09-loom-discovery-station.md
Total tasks: 14
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-10, 14/14 checks)

## Task 1 — loom-discovery plugin scaffold + dual manifests
- Description: Create the plugin skeleton mirroring loom-spec: `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` (name `loom-discovery`, version 0.1.0, description per brief naming round: problem-space station, business-value + user-insights), `README.md` (single-language, per loom-spec precedent), `CHANGELOG.md` (0.1.0 entry; test counts stamped at close-out per repo memory). Write the failing manifest test first.
- Module: loom-discovery/
- Files touched: loom-discovery/.claude-plugin/plugin.json, loom-discovery/.codex-plugin/plugin.json, loom-discovery/README.md, loom-discovery/CHANGELOG.md, loom-discovery/scripts/test_plugin_manifest.py
- Context paths:
  - loom-spec/.claude-plugin/plugin.json
  - loom-spec/.codex-plugin/plugin.json
  - loom-spec/scripts/test_plugin_manifest.py
  - loom-product-principles/scripts/test_plugin_manifest.py
- Acceptance:
  - RED: `pytest loom-discovery/scripts/test_plugin_manifest.py` fails (manifests do not exist)
  - GREEN: same command passes — manifests exist, valid JSON, name matches dir, parseable semver, MIT license
- Dependencies: none
- Independent: false
- Brief item covered: "Plugin `loom-discovery` (scaffold mirrors loom-spec: dual manifest … README, CHANGELOG, `scripts/test_marketplace_entry.py` + `test_plugin_manifest.py`, no hooks)"

## Task 2 — marketplace registration + entry test
- Description: Append the loom-discovery object to the root marketplace array (pattern: loom-spec entry at .claude-plugin/marketplace.json:107-111); description string must equal loom-discovery/.claude-plugin/plugin.json description verbatim. Write the failing entry test first.
- Module: .claude-plugin/marketplace.json
- Files touched: .claude-plugin/marketplace.json, loom-discovery/scripts/test_marketplace_entry.py
- Context paths:
  - loom-spec/scripts/test_marketplace_entry.py
  - scripts/check-marketplace-description-sync.py
- Acceptance:
  - RED: `pytest loom-discovery/scripts/test_marketplace_entry.py` fails (no marketplace entry)
  - GREEN: same command passes AND `python scripts/check-marketplace-description-sync.py` exits 0
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "`.claude-plugin/marketplace.json`: append loom-discovery entry … Description must equal plugin.json description"

## Task 3 — using-loom-discovery family-entry router skill
- Description: Author `skills/using-loom-discovery/SKILL.md` (intake + routing to business-value / user-insights, §Intake references the family reception on-ramp table — point, never copy rows) + `references/claude-code-tools.md` + `references/codex-tools.md` per sibling pattern. Description must survive listing eviction (≤1536 chars, entry-router pattern per repo memory). Write the failing structural test first.
- Module: loom-discovery/skills/using-loom-discovery/
- Files touched: loom-discovery/skills/using-loom-discovery/SKILL.md, loom-discovery/skills/using-loom-discovery/references/claude-code-tools.md, loom-discovery/skills/using-loom-discovery/references/codex-tools.md, loom-discovery/scripts/test_using_skill.py
- Context paths:
  - loom-spec/skills/using-loom-spec/SKILL.md
  - loom-spec/skills/using-loom-spec/references/claude-code-tools.md
  - loom-spec/skills/using-loom-spec/references/codex-tools.md
  - loom-pipeline/hooks/family-reception.md
- Acceptance:
  - RED: `pytest loom-discovery/scripts/test_using_skill.py` fails (SKILL.md absent)
  - GREEN: same command passes — SKILL.md exists with frontmatter name/description, description ≤1536 chars, both references files exist, no nested subfolders
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`skills/using-loom-discovery/` — family-entry router (+ `references/` claude-code-tools.md / codex-tools.md, per sibling pattern)"

## Task 4 — business-value member skill
- Description: Author `skills/business-value/SKILL.md`: adversarial worth-it check (Shape Up betting register, NOT Cagan viability); decidable trigger enumeration finalized from brief draft — fire on ANY of (a) outcome for others / published / maintained, (b) competing ideas for one time budget, (c) meaningful resource spend; silent skip for personal tools or pre-decided GO. Re-entrant after research. Market/GTM/revenue → delegate to domain-teams:planning-team, never inline. Agent contract: business-value agents may not map needs. Artifact template `assets/business-value-template.md` (why now / why me / opportunity cost / GO / NO-GO / NEEDS-MORE-RESEARCH). Write the failing structural test first.
- Module: loom-discovery/skills/business-value/
- Files touched: loom-discovery/skills/business-value/SKILL.md, loom-discovery/skills/business-value/assets/business-value-template.md, loom-discovery/scripts/test_business_value_skill.py
- Context paths:
  - docs/loom/specs/2026-07-09-loom-discovery-station.md
  - loom-spec/skills/spec-expansion/SKILL.md
  - loom-product-principles/skills/product-principles/SKILL.md
- Acceptance:
  - RED: `pytest loom-discovery/scripts/test_business_value_skill.py` fails (SKILL.md absent)
  - GREEN: same command passes — SKILL.md + template exist, frontmatter valid, trigger/skip conditions present as enumerated list, planning-team delegation named, no nested subfolders
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`skills/business-value/` — adversarial worth-it check. Optional (trigger conditions below), re-entrant after research. Artifact: `business-value.md`"

## Task 5 — user-insights member skill
- Description: Author `skills/user-insights/SKILL.md`: the core research verb. Two modes per brief — opportunity-space mapping (knowledge; research/explore), value commitment (value judgment; research-then-"my take" proposal, user ratifies before write, agents never self-commit). Research delegation boundary (resolves brief Open Q2): delegate to research-toolkit:deep-deep-research when >3 research questions OR external/user evidence needed; inline WebSearch otherwise. Problem-space-pure (WHAT never HOW; no solution sections). Agent contract: user-insights agents may not render investment verdicts. Artifact templates: `assets/user-insights-template.md` (problem framing / opportunity space with job stories + evidence links / value commitment + appetite / risks & open questions), `assets/evidence-template.md` (claims-to-evidence registry), plus `research/` per-question report convention documented in SKILL.md. Write the failing structural test first.
- Module: loom-discovery/skills/user-insights/
- Files touched: loom-discovery/skills/user-insights/SKILL.md, loom-discovery/skills/user-insights/assets/user-insights-template.md, loom-discovery/skills/user-insights/assets/evidence-template.md, loom-discovery/scripts/test_user_insights_skill.py
- Context paths:
  - docs/loom/specs/2026-07-09-loom-discovery-station.md
  - loom-code/skills/brainstorming/references/axis4-research-protocol.md
  - research-toolkit/skills/deep-deep-research/SKILL.md
- Acceptance:
  - RED: `pytest loom-discovery/scripts/test_user_insights_skill.py` fails (SKILL.md absent)
  - GREEN: same command passes — SKILL.md + both templates exist, commitment interaction contract present verbatim ("user ratifies" phrasing), delegation boundary stated, no solution-section headings in template, no nested subfolders
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`skills/user-insights/` — the core research verb … Commitment interaction contract … Agents never self-commit on the user's behalf"

## Task 6 — discovery artifact validator
- Description: Implement `scripts/validate_discovery_artifacts.py` (stdlib-only, family pattern): validates a `docs/loom/discovery/<slug>/` folder — user-insights.md required sections, evidence.md present, business-value.md sections when present, verdict enum GO/NO-GO/NEEDS-MORE-RESEARCH. Section names asserted against the templates shipped in Tasks 4-5 (no drift). Write the failing validator test first (fixtures: one passing folder, one missing-section folder).
- Module: loom-discovery/scripts/
- Files touched: loom-discovery/scripts/validate_discovery_artifacts.py, loom-discovery/scripts/test_validate_discovery_artifacts.py
- Context paths:
  - loom-discovery/skills/business-value/assets/business-value-template.md
  - loom-discovery/skills/user-insights/assets/user-insights-template.md
  - loom-spec/scripts/validate_spec_output.py
- Acceptance:
  - RED: `pytest loom-discovery/scripts/test_validate_discovery_artifacts.py` fails (validator missing)
  - GREEN: same command passes — good fixture exits 0, missing-section fixture exits nonzero with named section
- Dependencies: Tasks 4, 5 complete first
- Independent: false
- Brief item covered: brief Open Question 4 resolved affirmative — "family pattern: stdlib structural validators per station — assume yes, scope at writing-plans"

## Task 7 — family reception: map + three doors + on-ramp row (append-only)
- Description: Update `loom-pipeline/hooks/family-reception.md`: add using-loom-discovery to the family map (:8-20), update Three doors station enumeration (:30), APPEND discovery row to the on-ramp table after the Negative guard row — do NOT renumber existing rows 1-3 (repo memory retire-numbered-checks-dont-renumber). Row condition per brief draft: "product-shaped work AND the problem/users cannot be articulated with evidence → suggest using-loom-discovery first", with explicit precedence note over the principles row when both fire (resolves brief Open Q5; wording must survive a cold read — final cold-reader dogfood happens at branch finish, not this task).
- Module: loom-pipeline/hooks/family-reception.md
- Files touched: loom-pipeline/hooks/family-reception.md
- Context paths:
  - docs/loom/specs/2026-07-09-loom-discovery-station.md
- Acceptance:
  - RED: `grep -c 'using-loom-discovery' loom-pipeline/hooks/family-reception.md` returns 0
  - GREEN: grep returns ≥3 (family map + on-ramp row + precedence note); existing row numbers 1/2/3 unchanged (diff shows pure append + map/doors edits)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "family map … Three doors … on-ramp table — **append** a discovery row, do NOT renumber"

## Task 8 — loom-pipeline enumerations + description sync
- Description: Sweep loom-pipeline's own station enumerations to include discovery: README.md:33,40-41,76,118,129; skills/using-loom-pipeline/SKILL.md:7,11,26,51,58,64,174 (v0.1 note: discovery is interactive-only, conductor does not drive it as a batch segment); session-start hook banner if it enumerates; update loom-pipeline plugin.json description (both manifests) AND its marketplace.json entry to the same string (sync gate).
- Module: loom-pipeline/
- Files touched: loom-pipeline/README.md, loom-pipeline/skills/using-loom-pipeline/SKILL.md, loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/hooks/session-start, .claude-plugin/marketplace.json
- Context paths:
  - docs/loom/specs/2026-07-09-loom-discovery-station.md
  - scripts/check-marketplace-description-sync.py
- Acceptance:
  - RED: `grep -rn 'principles → interface-design → spec → code' loom-pipeline/ | grep -v discovery` returns hits (stale four-station chain)
  - GREEN: same grep returns 0 hits AND `python scripts/check-marketplace-description-sync.py` exits 0
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "Four/five-station enumerations sweep: `loom-pipeline/README.md…` `using-loom-pipeline/SKILL.md…` marketplace description for loom-pipeline"

## Task 9 — loom-code router card count fix
- Description: In `loom-code/skills/using-loom-code/SKILL.md` line 96, change the literal string "family map (the five using-loom-* entries) + on-ramp table" to "family map (the six using-loom-* entries) + on-ramp table". No other edits.
- Review-weight: mechanical
- Module: loom-code/skills/using-loom-code/SKILL.md
- Files touched: loom-code/skills/using-loom-code/SKILL.md
- Context paths:
  - loom-code/skills/using-loom-code/SKILL.md
- Acceptance:
  - RED: `grep -n 'five using-loom' loom-code/skills/using-loom-code/SKILL.md` returns a hit
  - GREEN: that grep returns 0 AND `grep -n 'six using-loom' loom-code/skills/using-loom-code/SKILL.md` returns exactly 1 hit at the same line
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "enumerations sweep: … `loom-code/skills/using-loom-code/SKILL.md:96`"

## Task 10 — living design docs update
- Description: Update the two living docs that enumerate the family: `docs/loom/specs/2026-07-04-loom-family-connective-tissue.md` (:14,70,124,147 — four-station framing → five stations + discovery, with a dated amendment note) and `docs/loom/audits/2026-07-04-harness-engineering-audit.md:4` ("all five loom plugins" → six, dated note). Amend, do not rewrite history sections.
- Module: docs/loom/
- Files touched: docs/loom/specs/2026-07-04-loom-family-connective-tissue.md, docs/loom/audits/2026-07-04-harness-engineering-audit.md
- Context paths:
  - docs/loom/specs/2026-07-09-loom-discovery-station.md
- Acceptance:
  - RED: `grep -l 'loom-discovery' docs/loom/specs/2026-07-04-loom-family-connective-tissue.md docs/loom/audits/2026-07-04-harness-engineering-audit.md` returns no files
  - GREEN: both files contain 'loom-discovery' with a dated (2026-07-10) amendment line
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "living design docs `docs/loom/specs/2026-07-04-loom-family-connective-tissue.md:14,70,124,147`" (+ audits doc from Current State Evidence sweep list)

## Task 11 — docs/loom artifact-home declaration
- Description: Add `discovery/` row to the `docs/loom/README.md` "What's here" table (:9-17) declaring `docs/loom/discovery/<date>-<slug>/` as the discovery artifact home (business-value.md / user-insights.md / research/ / evidence.md), and register in `docs/loom/INDEX.md`.
- Module: docs/loom/
- Files touched: docs/loom/README.md, docs/loom/INDEX.md
- Context paths:
  - docs/loom/README.md
  - docs/loom/INDEX.md
- Acceptance:
  - RED: `grep -n 'discovery/' docs/loom/README.md` returns 0 hits
  - GREEN: README table has the discovery/ row and INDEX.md references it
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`docs/loom/README.md:9-17` table + `docs/loom/INDEX.md`: declare `docs/loom/discovery/` as the artifact home"

## Task 12 — product-principles tripwire + boundary amendment
- Description: Three coordinated edits in loom-product-principles: (1) SKILL.md:33-40 boundary area — add tripwire: when the user cannot answer problem/users grilling with evidence, route to loom-discovery (user-insights) instead of dead-ending; (2) using-loom-product-principles SKILL.md:16-31 — add discovery to the sibling redirect list; (3) README.md:70 — amend the deferral line: market/GTM/revenue stays planning-team turf, user/problem research is now loom-discovery turf, marked "supersedes-in-part the 2026-06-14 MVP brief Out list (2026-07-10)".
- Module: loom-product-principles/
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/skills/using-loom-product-principles/SKILL.md, loom-product-principles/README.md
- Context paths:
  - docs/loom/specs/2026-07-09-loom-discovery-station.md
  - docs/loom/specs/2026-06-14-product-principles-toolkit-mvp.md
- Acceptance:
  - RED: `grep -rc 'loom-discovery' loom-product-principles/` returns 0 total hits
  - GREEN: all three files contain the routing/amendment; README.md contains 'supersedes-in-part'
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "product-principles tripwire: … route to loom-discovery instead of dead-ending. Amend `README.md:70` boundary line"

## Task 13 — CI wiring (fold into loom-siblings-ci)
- Description: Extend `.github/workflows/loom-siblings-ci.yml` (resolves brief Open Q3: fold, matching sibling pattern) — add loom-discovery path triggers and run its `test_plugin_manifest.py` + `test_marketplace_entry.py` + `test_*_skill.py` + `test_validate_discovery_artifacts.py`. This workflow is the declared command surface for the new pytest verbs (runnable-capability note satisfied).
- Module: .github/workflows/loom-siblings-ci.yml
- Files touched: .github/workflows/loom-siblings-ci.yml
- Context paths:
  - .github/workflows/loom-siblings-ci.yml
  - .github/workflows/loom-spec-ci.yml
- External surfaces: GitHub Actions workflow syntax (on.push.paths, jobs.*.steps) — verify against existing sibling workflow, not memory
- Acceptance:
  - RED: `grep -n 'loom-discovery' .github/workflows/loom-siblings-ci.yml` returns 0 hits
  - GREEN: workflow lists loom-discovery paths + test invocations; `pytest loom-discovery/scripts/` passes locally as the workflow would run it
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "CI: extend `.github/workflows/loom-siblings-ci.yml` (or own workflow — Open Question) so the new plugin's manifest/marketplace tests run"

## Task 14 — register loom-discovery in sync_codex_manifests CODEX_ELIGIBLE
- Description: In `scripts/sync_codex_manifests.py`, add the literal string `"loom-discovery",` to the `CODEX_ELIGIBLE` tuple (alphabetical position among existing entries). No other edits.
- Review-weight: mechanical
- Module: scripts/sync_codex_manifests.py
- Files touched: scripts/sync_codex_manifests.py
- Context paths:
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: `grep -n '"loom-discovery"' scripts/sync_codex_manifests.py` returns 0 hits
  - GREEN: that grep returns exactly 1 hit inside the CODEX_ELIGIBLE tuple AND `python3 scripts/sync_codex_manifests.py --check loom-discovery` exits 0
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Plugin `loom-discovery` (scaffold mirrors loom-spec: dual manifest …)" — completes the dual-manifest sync coverage for `--all` invocations (discovered during Task 1 execution)

## Notes

- Wave structure: Task 1 root → wave 2 parallel: Tasks 3, 4, 5, 7, 9, 10, 11, 12 (all `Independent: true`, disjoint files) plus sequential Tasks 2 → 8/13 (shared `.claude-plugin/marketplace.json` forces ordering) → Task 6 after 4+5. Critical path: 1 → 2 → 8 (depth 3).
- SDD dispatch trap-guards (repo memory): implementers must Read before Edit; `.claude/hooks/validate-skill-folder-structure.sh` blocks nested subfolders inside any skill folder (assets/ etc. stay single-level); commit messages need conventional type + mandatory scope (CC CI whitelist) and git-memory trailer duty goes in every dispatch packet; guard blocking twice = stop and report.
- Marketplace description strings must be byte-identical between plugin.json and marketplace.json (two CI gates enforce).
- Out of scope per brief: discovery-critic panel, conductor batch segment, pre-grill mechanism, two-station split.
- Amendment 2026-07-10 (execution finding, Task 11 round 2): docs/loom/INDEX.md is machine-generated by loom-code/scripts/check-living-spec-index.py (--verify-index CI gate requires byte-identity with build_index()); hand-authored registration is infeasible-by-design. Task 11's "register in INDEX.md" clause is realized as README.md-only registration; INDEX.md restored to pure generator output in the round-2 fix commit.
- Amendment 2026-07-10 (post-PASS): appended Task 14 (mechanical CODEX_ELIGIBLE tuple registration, discovered during Task 1 execution — the sync script's --all allowlist is hardcoded). Additive and schema-safe: new leaf task, single file, no dependency changes to existing tasks, depth unchanged (1→14 = 2). Re-review skipped per writing-plans §Amending a PASS plan (b); Total tasks 13→14.
