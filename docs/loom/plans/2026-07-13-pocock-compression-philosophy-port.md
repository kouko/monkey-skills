# Plan: Pocock compression philosophy port into skill-dev-toolkit

Source brief: docs/loom/specs/2026-07-13-pocock-compression-philosophy-port.md
Total tasks: 4   ← uncapped
Critical-path depth: 2 (≤5)   ← longest Dependencies chain; this is the ceiling
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-13, 14/14 checks, general-purpose evaluator)

## Task 1 — Add "Leading-Word Substitution" move to refactor-moves-catalog

- Description: Add a `### Leading-Word Substitution` move under the **Medium-risk** section of the catalog (replace an in-file explanation with the name of a pre-trained concept the model already holds — e.g. "Fowler's Feature Envy", "Beck's Child Test" — so the name recruits the prior instead of the prose restating it), following the existing move format (`### Name` + prose + `**Example**` + `**Equivalence risk**`), with a MANDATORY guard line: equivalence runs for this move MUST execute on the weakest model tier that will run the target skill in production (priors vary by tier; Anthropic's Haiku-vs-Opus guidance + this repo's explicit-contract-load-bearing evidence). Include attribution line (Matt Pocock, mattpocock/skills + aihero.dev writing-great-skills, MIT). Add one row to the Summary table.
- Module: skill-dev-toolkit/skills/skill-refactor (references content)
- Files touched: skill-dev-toolkit/skills/skill-refactor/references/refactor-moves-catalog.md
- Context paths:
  - skill-dev-toolkit/skills/skill-refactor/references/refactor-moves-catalog.md
  - docs/loom/specs/2026-07-13-pocock-compression-philosophy-port.md
  - docs/skill-dogfood/2026-07-13-writing-plans-token-refactor/gate-evidence.md
- Acceptance:
  - RED: `grep -c 'Leading-Word Substitution' skill-dev-toolkit/skills/skill-refactor/references/refactor-moves-catalog.md` returns 0 (section absent)
  - GREEN: the grep finds the move BOTH as a `###` heading under the Medium-risk section AND as a Summary-table row; the move body contains the weakest-tier guard sentence and the MIT attribution; existing moves byte-unchanged
- External surfaces: (omit — pure internal content)
- Dependencies: none
- Independent: true
- Brief item covered: "skill-refactor/references/refactor-moves-catalog.md — add one Medium-risk move: Leading-word substitution … mandatory guard line: equivalence runs MUST use the weakest tier" (brief §Smallest End State item 1)

## Task 2 — Add taxonomy-guided candidate pre-pass to ablation-mode

- Description: Add a `## Taxonomy-guided candidate pre-pass` section to ablation-mode.md: BEFORE the leave-one-out runs, scan each section against Pocock's bloat taxonomy — (a) no-op sentences (assert nothing checkable), (b) sediment (leftovers from superseded revisions), (c) negative instructions ("don't think of an elephant" — naming the forbidden behavior can trigger it), (d) premature completion claims, (e) duplication with a bundled reference — and RANK sections by taxonomy-hit count so the expensive ablation runs execute in descending-suspicion order. State explicitly: the pre-pass ORDERS candidates only; every cut still passes the Q1/Q2/Q3 gate (candidate-finder-not-auto-deleter discipline unchanged). Include MIT attribution line.
- Module: skill-dev-toolkit/skills/skill-refactor (references content)
- Files touched: skill-dev-toolkit/skills/skill-refactor/references/ablation-mode.md
- Context paths:
  - skill-dev-toolkit/skills/skill-refactor/references/ablation-mode.md
  - skill-dev-toolkit/skills/skill-refactor/SKILL.md
  - docs/loom/specs/2026-07-13-pocock-compression-philosophy-port.md
- Acceptance:
  - RED: `grep -c 'pre-pass' skill-dev-toolkit/skills/skill-refactor/references/ablation-mode.md` returns 0
  - GREEN: the new section exists, names all 5 taxonomy categories, contains the "orders candidates only / gate still applies" sentence; existing sections byte-unchanged
- External surfaces: (omit — pure internal content)
- Dependencies: none
- Independent: true
- Brief item covered: "skill-refactor/references/ablation-mode.md — add a taxonomy-guided candidate pre-pass … cheaper ordering, same gate" (brief §Smallest End State item 2)

## Task 3 — New writing-lean.md authoring reference + ≤0-net-growth pointer

- Description: Create skill-dev-toolkit/skills/skill-creator-advance/references/writing-lean.md — authoring-time lean-writing guidance: (1) model-already-smart doctrine (only add context the model lacks; Anthropic best-practices citation), (2) leading words (name the prior instead of re-teaching it), (3) bloat-taxonomy self-review checklist (5 categories, same list as Task 2), (4) "thin orchestrator over thick reference" as the NAMED design dimension (SKILL.md = steps/table-of-contents; knowledge lives in references loaded on demand — names the pattern Progressive Disclosure already implements), (5) weak-tier floor rule (compression has a model-tier floor; when in doubt test on the weakest production tier), (6) attribution (Pocock MIT + Anthropic). Then add a pointer to the new file inside SKILL.md §Writing Style — with NET BODY GROWTH ≤ 0 words: tighten existing §Writing Style lines to pay for the pointer (SKILL.md is already 6,085w vs the 4,500 cap; it must not grow).
- Module: skill-dev-toolkit/skills/skill-creator-advance
- Files touched: skill-dev-toolkit/skills/skill-creator-advance/references/writing-lean.md, skill-dev-toolkit/skills/skill-creator-advance/SKILL.md
- Context paths:
  - skill-dev-toolkit/skills/skill-creator-advance/SKILL.md
  - docs/loom/specs/2026-07-13-pocock-compression-philosophy-port.md
- Acceptance:
  - RED: `test -f skill-dev-toolkit/skills/skill-creator-advance/references/writing-lean.md` exits 1 (file absent)
  - GREEN: file exists containing all 6 numbered elements; SKILL.md contains a pointer to references/writing-lean.md; `wc -w` of SKILL.md ≤ 6,085 (its pre-change count — net growth ≤0)
- External surfaces: (omit — pure internal content)
- Dependencies: none
- Independent: true
- Brief item covered: "skill-creator-advance/references/writing-lean.md (NEW file) … Body of SKILL.md gets AT MOST a one-line pointer … net body growth must be ≤0" (brief §Smallest End State item 3)

## Task 4 — Version bump 0.2.0 + CHANGELOG + codex manifest sync

- Description: Bump skill-dev-toolkit/.claude-plugin/plugin.json version 0.1.0 → 0.2.0; run `python3 scripts/sync_codex_manifests.py skill-dev-toolkit` to mirror; add a CHANGELOG.md 0.2.0 entry describing the three content additions (catalog move / ablation pre-pass / writing-lean reference) with the Pocock-generates-our-gate-verifies rationale and MIT attribution note.
- Module: skill-dev-toolkit (plugin metadata)
- Files touched: skill-dev-toolkit/.claude-plugin/plugin.json, skill-dev-toolkit/.codex-plugin/plugin.json, skill-dev-toolkit/CHANGELOG.md
- Context paths:
  - skill-dev-toolkit/CHANGELOG.md
  - skill-dev-toolkit/.claude-plugin/plugin.json
- Acceptance:
  - RED: `python3 -c "import json;v=json.load(open('skill-dev-toolkit/.claude-plugin/plugin.json'))['version'];exit(0 if v=='0.2.0' else 1)"` exits 1 (version still 0.1.0)
  - GREEN: version 0.2.0 in BOTH manifests (claude + codex mirror), CHANGELOG 0.2.0 entry present, `.claude/hooks/check-codex-manifest-drift.sh`-equivalent check clean (`python3 scripts/sync_codex_manifests.py --check skill-dev-toolkit` exit 0)
- External surfaces: (omit — repo-internal metadata)
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: "Version: skill-dev-toolkit 0.1.0 → 0.2.0 (content addition) + CHANGELOG entry" (brief §Smallest End State)

## Notes

- No loom-spec change-folder bound (detection layer ii: 0 non-archived
  docs/loom/<change-id>/ folders) — brief-only input; coverage script N/A.
- Tasks 1-3 are disjoint-file, no shared symbol → one parallel wave; Task 4 is
  the sequential join (depth 2 total).
- Content tasks (prose references): TDD iron law's docs exemption applies —
  RED/GREEN here are deterministic grep/wc acceptance probes, not test-suite
  cases; package-level suite still runs at finishing per
  verification-before-completion.
- Task 3 carries the highest-risk constraint (≤0 net growth in an over-cap
  file); reviewer attention there.
