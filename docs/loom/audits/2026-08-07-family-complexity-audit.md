# loom family complexity audit — 2026-08-07

Read-only complexity health-check of the whole loom family (six plugins
+ glue layer), followed by a `dev-workflow:proposal-critique` triage of
every simplification candidate. No files were changed by the audit
itself. Measurements taken at main @ e610f7c4 (working tree, 2026-08-07).

Method: four parallel read-only audit arms (loom-code core chain /
loom-code support surface / four design-side plugins / glue layer), each
returning file:line-grounded findings; candidates then triaged
KEEP / KEEP-WITH-CAVEAT / DEFER / DROP via proposal-critique's
grounding × necessity matrix.

## Quantitative baseline

| Facet | Measured |
|---|---|
| Family size | 27 skills, 5 agents, 13 hook files (every file type under `loom-*/hooks/`), 111 support md files (md under `*/skills/*/` excl. SKILL.md), 191 scripts (py+sh under `loom-*/`, excl. `__pycache__`) — populations as parenthesized; all six plugins unless stated |
| SKILL.md total | 60,651 words across the six plugins (57,197 excl. loom-pipeline); loom-code alone 35,252 — 58% of the six-plugin total |
| Heaviest SKILL.md bodies | requesting-docs-review 4,428 w (72 w under the 4,500 cap); finishing-a-development-branch 4,351 w; writing-plans 4,041 w; subagent-driven-development 4,013 w |
| Mandatory happy path, simple bug fix | 6 loom-code SKILL.md (using-loom-code, brainstorming, tdd-iron-law, verification-before-completion, requesting-code-review, finishing-a-development-branch) + 1 external plugin skill (dev-workflow:git-memory) + ≥6 auxiliary scripts/protocol docs |
| Per-session fixed overhead | ~2,400 words (two SessionStart cards + 27 skill-list descriptions) — modest, mostly justified |
| Largest single duplication | docs/loom/memory/README.md `## Index`: 7,761 w, 89% of the file, hand-maintained byte-mirror of 136 entry descriptions |
| Duplication governance | 12-rule baseline + reviewer discipline: real SSOT (scripts/_baseline.md → distribute.py → verify-drift.py, CI-gated). NOT covered: state-anchor wording (7 hand-copied files), tdd-standard.md (byte-identical full-file fork ×2), router-card 5 rules (manual "edit BOTH" sync) |

## Headline finding

The complexity is real, measured, and unevenly distributed: loom-code
alone carries 58% of the family's SKILL.md words (and the largest
support/script surface), and the heaviest parts are mostly load-bearing
(backed by documented incidents). The actual pathology is not "too big"
but "patches accumulate and are never pruned back into the base flow" —
one-off incident guards stack into per-skill rules engines
(finishing-a-development-branch Step 8 carries 5 independent
"ONCE per branch" sub-checklists; requesting-docs-review's convergence
contract has 114 "round" mentions in 192 lines).

## Load-bearing — do not touch (documented incident behind each)

- finishing-a-development-branch memory-timing check (PR #519/#520) and
  commit-carrier verify gate (#445)
- requesting-docs-review convergence contract semantics (9-round loop
  audit, docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md)
- ui-verification's premise (2026-07-03 dogfood: 28/28 green with broken UI)
- systematic-debugging anchored-thinking WebSearch gate (2026-05-27 case)
- product-principles exemption cluster; spec-expansion Phase ③ matrix
- the distribute.py SSOT machinery itself

## Triage results

KEEP (5):

| # | Item | Reason |
|---|---|---|
| A2 | Extract requesting-docs-review Directive 1–2 convergence math to references/ (block measured 1,424 w; leave ~300 w decision table inline) | Pure move; densest block in the family; restores cap headroom 72 w → ~1,200 w. Execution requires weak-model cold-read (extraction-severing precedent in docs/loom/memory/) |
| B1 | Bring the "one-line state anchor" ask-UX wording under distribute.py SSOT | Measured 7 hand-copied files, zero drift protection — worst maintenance tax found |
| B2 | Manage tdd-standard.md (1,019 w, byte-identical in tdd-iron-law/ and subagent-driven-development/) via distribute.py | Mechanism exists; near-zero cost |
| D1 | Generate docs/loom/memory/README.md `## Index` by script instead of hand-mirroring | Largest single dedup win (7,761 w); backlog_index.py proves the pattern; requires charter revision + plugin-wide contradiction sweep for "hand-edit the index" restatements |
| E1 | Add a deletion-first (YAGNI) review dimension to code-quality-reviewer + code-reviewer via the _reviewer-discipline SSOT | Minimal built-in complexity check: rides existing review rounds, adds no new station. Grounded by external research (LLM over-engineering documented; over-correction risk says keep it lean) + two in-repo occurrences (E-1 slim arc, this audit) |

KEEP-WITH-CAVEAT (5):

| # | Item | Caveat |
|---|---|---|
| A1 | Collapse finishing Step 8's five "ONCE per branch" checklists (block measured 1,123 w) into one generic regen-artifacts table | Preserve each check's semantics and per-artifact fallback wording; merge structure only |
| A3 | Downgrade writing-plans' wrong-bind reversal trigger (block measured 315 w, self-described hypothetical, no incident) to a one-line note | Re-add trigger: first real wrong-bind incident (full text recoverable from git history) |
| C2 | SSOT the brief-before-asking clause (near-verbatim ×4 across the four design-side routers: the trigger tail is byte-identical, the fork-noun varies per router) | Not purely behavior-zero — needs a parameterized carrier or a one-time wording normalization; and choose the carrier carefully — placing it in family-reception makes it per-session preload |
| D2 | Protect router-card.md's five hand-copied rules against drift | Prefer adding the pair to verify-drift.py coverage over a build-step generation — no new machinery |
| E3 | Periodic mechanism-prune pass | Minimal form only: record this audit's recipe as a runbook, human-triggered, proposal-only output. Do NOT build a new skill for it |

DEFER (5) — each filed as a PARKED backlog entry with its re-trigger in
`start:` (docs/loom/backlog/2026-08-07-*.md):

| # | Item | Re-trigger |
|---|---|---|
| A4 | Merge SDD's two review-weight exemption protocols | A third exemption shape appears, or either protocol needs a semantic edit (exemption-compression polarity-flip precedent argues against merging now) |
| C1 | Extract completeness-critic's inline 6-lens block (~600 w) | Next edit to that SKILL.md needs cap headroom (pre-existing parked decision, reaffirmed) |
| C3 | Reconcile the two critics' parallel writer≠judge prose (~500+ w, already divergent) | Next semantic change to the sanctioned co-writer pattern |
| D4 | Mechanize loom-memory prune pre-triage | First full manual prune proves impractical, or store > 200 entries |
| E2 | Plan-time complexity-budget fields (abstraction/file counts, never LOC) | E1 alone demonstrably fails: complexity findings recur across ≥2 arcs despite the new dimension |

DROP (2):

- D3 merge the 8-file pipeline driver split — shipping artifact is the
  single built file; zero session-facing benefit, medium risk.
- D5 remove triple-key JSON emission in the two session-start scripts —
  deliberate belt-and-suspenders per its own comments; verification cost
  exceeds the ~dozen-line saving.

## Expected impact of executing KEEP + KEEP-WITH-CAVEAT

- Reader burden: ~-1,900 w across the three heaviest core skills
  (rdr → ~3,300; finishing → ~3,800; wp → ~3,750). Key win is rdr's cap
  headroom (72 w → ~1,200 w) — today any net-adding edit over 72 words
  there must slim first.
- Maintenance tax: state-anchor 7→1 files; tdd-standard 2→1;
  memory-index 2 hand-edits → 1 + regen; router-card drift CI-caught.
- Behavior: only E1 (review dimension) and E3 (prune loop) change what
  the family does; everything else is behavior-neutral dedup.
- Does NOT change: the 6-skill mandatory happy path, the ~2,400 w
  session overhead, loom-code's ~58% share of SKILL.md words.
- Execution cost: 50 test files name the three slimmed skills (grep of
  `*.py` under `loom-*/scripts`, `loom-*/tests`, `scripts/` for the three
  skill names) — prose-pin updates dominate; comparable to the E-1 slim
  arc (#652).

## Recommended execution order

1. Mechanical dedup arc: B1, B2, C2, D2 (behavior-zero, existing
   machinery, light review lane)
2. E1 + E3 legislation arc (before the prose arc, so the prose arc
   dogfoods the new dimension)
3. D1 index generation arc (touches charter semantics — separate PR,
   include contradiction-sweep arm)
4. Prose slim arc: A2 first (cap pressure), then A1, A3 (weak-model
   cold-reads; 42 test-pin surface)

Tracked as OPEN backlog entry
2026-08-07-execute-complexity-audit-keep-lanes.md.
