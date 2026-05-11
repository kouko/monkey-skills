# systems-thinking-toolkit v0.1.0 — Design Spec

**Date**: 2026-05-12
**Branch**: `feat/systems-thinking-toolkit-v0.1.0`
**Source**: 14 SKILL.md files distilled by `tsundoku:book-distill` from Dennis
Sherwood, *Seeing the Forest for the Trees: A Manager's Guide to Applying
Systems Thinking* (2002, Nicholas Brealey), Stage-3 output at 2026-05-11.

## Status

| Section | State |
|---|---|
| Brainstorm | ✅ approved (sections 1-5) |
| Spec | drafted, awaiting user review |
| Plan | pending (`superpowers:writing-plans`) |
| Implementation | pending |

## 1. Background

A `tsundoku:book-distill` run on 2026-05-11 produced 14 RIA-TV++-formatted
SKILL.md files plus Stage-0 `BOOK_OVERVIEW.md`, Stage-1.5 `verified.md`,
and Stage-3 `INDEX.md` (17 cross-skill relations) at
`~/.tsundoku/cache/distilled/Seeing-the-Forest-for-the-Trees-A-Manager's-Guide-to-Applyin/`.

A `dev-workflow:skill-judge` evaluation across all 14 skills produced:

| Grade | Count | Slugs |
|---|---|---|
| A (108+) | 8 | sk01, sk02, sk04, sk05, sk06, sk07, sk09, sk10 |
| B (96-107) | 4 | sk03, sk08, sk11, sk12 |
| C (84-95) | 1 | sk13 (innovaction-martian-test) — V1-weak per Stage 1.5 |
| D (72-83) | 1 | sk14 (manager-personality-quadrant) — V1-weak per Stage 1.5 |

Mean 105/B, median 108.5/A. Across 14 evaluations, common
sub-A patterns were:

- **D5 progressive disclosure** ceiling at 12.5/15 — all 14 skills are
  single-file, no `references/` extraction.
- **D7 pattern recognition** ceiling at 8.9/10 — RIA-TV++ format doesn't
  cleanly fit Anthropic's five-pattern taxonomy (Mindset / Navigation /
  Philosophy / Process / Tool).
- **Frontmatter `related_skills`** unevenly filled — INDEX.md declares 17
  Stage-3 relations but most frontmatter blocks have `related_skills: []`
  or partial coverage.

## 2. Goal

Package the 14 skills as a `monkey-skills` plugin named
**`systems-thinking-toolkit`**, applying nine targeted improvements that
address the common sub-A patterns above. Target v0.1.0 grade
distribution: mean ≥ 108/A, no skill drops a single dimension after
improvement (refactor-equivalence floor).

## 3. Locked decisions (from brainstorm)

| # | Decision | Source |
|---|---|---|
| D1 | Source-of-truth: copy 14 SKILL.md into plugin (cache becomes archived snapshot) | User Q1 |
| D2 | V1-weak skills (sk13 + sk14) both retained; merger/pruning deferred to v0.2+ | User Q2 |
| D3 | Scope: "+++ Full" — all nine improvements + 14×3 tri-lang per-skill READMEs | User Q3 |
| D4 | Audit trail: `INDEX.md` + `BOOK_OVERVIEW.md` + `verified.md` all enter `references/` | User Q4 |
| D5 | Implementation strategy: Approach B (subagent-driven parallel) | User Q5 |
| D6 | Plugin name: `systems-thinking-toolkit` | User Q (plugin-name) |

## 4. Plugin architecture (Section 1)

```
systems-thinking-toolkit/                            ← repo root, sibling to philosophers-toolkit
├── plugin.json                                       ← SoT for plugin metadata
├── README.md / README.ja.md / README.zh-TW.md        ← plugin-level tri-lang
├── ROADMAP.md                                        ← v0.1 → v0.2+ (incl. sk13/sk14 merger discussion)
├── INDEX.md                                          ← plugin-level skill map (Stage-3 mermaid linkified)
│
├── commands/                                         ← 14 slash commands + 1 router
│   ├── stt.md                                        ← /systems-thinking-toolkit:stt = router
│   ├── r-loop.md
│   ├── so-link.md
│   ├── cld-rules.md
│   ├── fuzzy-var.md
│   ├── limits-to-growth.md
│   ├── variance-action.md
│   ├── lever-outcome.md
│   ├── strategic-cascade.md
│   ├── multi-cld.md
│   ├── mental-models.md
│   ├── stock-flow.md
│   ├── models-learning.md
│   ├── martian-test.md
│   └── manager-quadrant.md
│
├── skills/
│   ├── using-systems-thinking-toolkit/
│   │   ├── SKILL.md                                  ← entry / router skill
│   │   └── README.md / .ja.md / .zh-TW.md
│   │
│   ├── reinforcing-balancing-loop-diagnosis/
│   │   ├── SKILL.md                                  ← post 9-item polish
│   │   ├── README.md / .ja.md / .zh-TW.md
│   │   └── references/cases.md                       ← if body > 180 lines after polish
│   │
│   ├── s-o-link-assignment/
│   ├── cld-drawing-craft-12-rules/
│   ├── fuzzy-variable-elevation/
│   ├── limits-to-growth-take-the-brakes-off/
│   ├── variance-target-action-template/
│   ├── lever-vs-outcome-reframing/
│   ├── strategic-cascade-scenario-planning/
│   ├── multi-perspective-cld-wise-policy/
│   ├── mental-models-harmony-leadership-energy/
│   ├── stock-flow-translation/
│   ├── models-for-learning-not-answers/
│   ├── innovaction-martian-test/                     ← V1-weak, retained per D2
│   └── manager-personality-quadrant/                 ← V1-weak, retained per D2
│       (all same structure as reinforcing-balancing-loop-diagnosis above)
│
└── references/                                       ← per D4
    ├── BOOK_OVERVIEW.md                              ← Stage-0 thesis
    └── VERIFIED.md                                   ← Stage-1.5 V1/V2/V3 evidence
```

### Convention compliance

- `commands/stt.md` is the router; per-skill commands use short slugs (e.g.
  `/stt:r-loop`, `/stt:so-link`) to avoid long invocations.
- `using-systems-thinking-toolkit` matches `using-philosophers-toolkit`
  entry-skill convention.
- Each `skills/<slug>/` has at most one single-level subfolder (`references/`)
  — passes `.claude/hooks/validate-skill-folder-structure.sh`.
- `references/` at plugin root holds non-skill audit-trail content (INDEX.md
  lives at plugin root because it's user-facing, not audit-only).

## 5. Nine improvements per skill (Section 2)

Each improvement is applied per skill; some are conditional, some affect
all 14, two are skill-specific overrides.

### Tier 1 — applies to all 14

**1. Frontmatter `related_skills` backfill.**
Cross-reference `references/INDEX.md` (the Stage-3 17-relation list) and
populate each skill's frontmatter `related_skills`:

```yaml
related_skills:
  - slug: cld-drawing-craft-12-rules
    relation: depends-on  # or composes-with / contrasts-with
```

Implementer MUST limit entries to the 17 declared relations in INDEX.md.
No invented or inferred relations.

**2. Shorthand sk-code resolution.**
For every occurrence of `sk0[0-9]` or `sk1[0-4]` in body text, the first
occurrence in each section gets a parenthetical gloss with the slug:

```diff
- composes with (3); learn after the 12 rules
+ composes with cld-drawing-craft-12-rules (sk03); learn after the 12 rules
```

Subsequent occurrences in the same section keep the bare `sk03` form.

**3. Source-unit code provenance footer.**
Body keeps source-unit codes (`f01`, `p28`, `g10`, `ce27`, etc.) as-is.
The Audit metadata block gets one explanatory line:

```markdown
> Source-unit codes (f01/p28/g10/ce27/...) refer to Stage-1.5 verified.md
> entries. See `<plugin-root>/references/VERIFIED.md`.
```

### Tier 2 — conditional

**4. `references/cases.md` extraction.**
Trigger: SKILL.md body > 180 lines **after** all other applicable
improvements (1, 2, 3, 5, plus any Tier-3 override) have been applied.
Measure last so #4 is the final size-reduction step.

Action: A1 Past Application section moves to
`skills/<slug>/references/cases.md`. The A1 section retains a brief 1-2
line summary plus a MANDATORY load directive:

```markdown
## A1 — Past Application

The three cases that calibrate even-O/odd-O classification (UK back-office
c01, Hatfield Rail c05, Ratner Jewelry c06) are detailed in
`references/cases.md`.

**MANDATORY — READ ENTIRE FILE**: Before classifying a loop, you MUST
read [`references/cases.md`](references/cases.md) (~80 lines) for the
trigger-vs-structure distinction.
```

Expected to trigger for sk08 (~270 lines), sk12 (~256), sk13 (~249), and
possibly others after polish — exact set determined per-skill.

**5. Decision-tree ASCII visualization.**
Trigger: E (Execution) section has ≥ 6 numbered steps.

Action: A compact decision-tree diagram is inserted at the top of E
section, before step 1. Example:

```
E flow:
  closed loop? ── no → not applicable (open chain)
        │ yes
        v
  all links signed? ── no → run s-o-link-assignment first
        │ yes
        v
  count Os → R (even) or B (odd)
        │
        ├── R: name current spin + trigger
        └── B: name target + delay
```

ASCII format (not mermaid) for grep-friendliness and zero-dependency
rendering in any text-only context.

### Tier 3 — skill-specific overrides

**6. sk01 reverse-link backfill.**
sk01 is the foundational skill on which 4+ downstream skills depend, but
its current frontmatter `related_skills: []` is empty. Implementer for
sk01 explicitly populates `related_skills` with reverse links to the
skills that `depends-on` it (per INDEX.md).

**7. sk13 description framing-prefix.**
sk13's Boundary section already discloses TRIZ / morphological-analysis
prior-art overlap. The description gets a framing prefix without
destroying existing trigger keywords:

```diff
- description: |
-     Activate when a team is stuck generating ideas...
+ description: |
+     Auxiliary skill — typically reached from inside
+     strategic-cascade-scenario-planning workflow when generating
+     alternative futures. Activate when a team is stuck generating
+     ideas...
```

All other trigger keywords and the NOT-for clause stay intact.

**8. sk14 lead-with-headline-contribution.**
sk14's most novel procedural delta is E Step 3 "adapt framing not
analysis" (the 2x2 taxonomy itself is heavily overlapped by DISC / MBTI /
Hogan / Situational Leadership). Implementer for sk14 promotes the
framing-vs-analysis split to the R (Reading) section header; the 2x2
taxonomy stays in I (Interpretation) as supporting vocabulary.

### Tier 4 — plugin-level (controller-only, not subagent)

**9. INDEX.md plugin-ization.**
Cache version of `INDEX.md` is copied to plugin root with two changes:

- Mermaid node labels become markdown links pointing to `skills/<slug>/SKILL.md`.
- The "Recommended learning order" numbered list gets per-item markdown links.

No other content change to the INDEX itself.

### Out of scope (deferred to v0.2+)

- stock-flow numerical computation script (sk11)
- doubling-time calculator (sk12)
- sk13 / sk14 merger or removal (D2 defers)
- New TRIZ-replacement skill (D2 defers)
- Per-skill `checklists/` extraction (only `references/` used in v0.1.0)
- Score-history tracking (`dev-workflow:skill-judge` optional companion)

## 6. Orchestration (Section 3)

### Phase 0 — Pilot (controller direct, no subagent)

Controller applies improvements 1-3 + 6 (and 4-5 if triggered) to sk01
**reinforcing-balancing-loop-diagnosis** end-to-end. Outputs:

- One atomic commit on the worktree branch.
- Reference pattern document (the sk01 commit hash + its `references/cases.md`
  if triggered) for Phase A subagents to consume.

Self-judge with `dev-workflow:skill-judge` rubric: sk01 must score ≥ 110
(current 110/A) with no dimension regression. **Halt condition: any
dimension drops → re-pilot before Phase A.**

### Phase A + A' — 13 implementers + 13 spec-reviewers (parallel)

Dispatched together in one batch (26 subagent invocations). Each
implementer receives:

- Cache path to the original SKILL.md.
- Worktree destination path.
- Path to sk01 pilot commit (for pattern reference).
- Path to INDEX.md (for 17-relation cross-check).
- Spec document (this file).

Each implementer produces one atomic commit. Each spec-reviewer reviews
the corresponding implementer's commit against the C1-C8 checklist
(Section 7 Verification below) and emits a JSON status report.

Re-run loop: spec-reviewer FAIL → controller sends specific issue to
implementer via SendMessage → implementer fixes → spec-reviewer re-runs.
Maximum 3 rounds per skill; on round 4 failure, controller takes over
that skill directly.

Token-budget mitigation: if 26-subagent batch fails on rate limits,
split into two waves (sk02-08 then sk09-14).

### Phase B — Fresh-eyes cross-skill audit (1 subagent)

After all 13 implementers PASS, dispatch one fresh-eyes auditor. It
checks X1-X5 (Section 7 Verification) — cross-skill drift only. Controller
fixes drift directly (not delegated back to implementers, because
drift is by definition cross-skill).

Loop cap: 3 rounds. Round-4 unresolved drift → accepted as known issue
in ROADMAP.md.

### Phase C — Plugin shell (controller direct)

Controller produces, in sequence:

- `plugin.json`
- `.claude-plugin/marketplace.json` entry for the new plugin
- `using-systems-thinking-toolkit/SKILL.md` (entry / router skill)
- `INDEX.md` (improvement #9 — link-ified)
- `references/BOOK_OVERVIEW.md` (copy from cache)
- `references/VERIFIED.md` (copy from cache `verified.md`, case-renamed)
- `commands/stt.md` (router slash command)
- `commands/r-loop.md`, `commands/so-link.md`, ... (14 per-skill slash commands)
- `README.md` (plugin-level English)

### Phase D — Per-skill READMEs (14 parallel subagents)

Each of 14 subagents owns one skill's three READMEs (en / ja / zh-TW). A
glossary of systems-thinking terminology is fixed before dispatch (e.g.
"reinforcing loop" → 「強化迴路」/「強化ループ」; "causal loop diagram"
→ 「因果迴路圖」/「因果ループ図」).

The pilot subagent finishes sk01 first; its READMEs become the reference
for the other 13 subagents. Total 42 README files.

`README.ja.md` and `README.zh-TW.md` at plugin root are produced by the
controller during Phase C as part of the plugin shell.

### Phase E — Integration & CI (controller direct)

- Commit-lint pass: every commit matches `<type>(<scope>): <subject>`
  format per memory `feedback_cc_type_whitelist`. Scope MUST be
  kebab-case from {`refactor`, `feat`, `fix`, `chore`, `docs`, `test`}.
- Hook full-repo scan:
  `find systems-thinking-toolkit/skills -mindepth 3 -type d`
  must return only `references/` paths (empty otherwise).
- `git push` to the feature branch.
- `gh pr create` against `main`.

No ultrareview (user-triggered; markdown-only content has low cloud-review
ROI).

### Headcount summary

| Phase | Subagents | Approx wall-clock |
|---|---|---|
| 0 (pilot) | 0 | 1-2h |
| A + A' | 26 parallel | ~30-45 min |
| B (fresh-eyes) | 1 | ~10 min |
| C (plugin shell) | 0 | 2-3h |
| D (READMEs) | 14 parallel | ~30-45 min |
| E (CI / PR) | 0 | ~30 min |
| **Total** | **41** | **5-7h** (excluding fresh-eyes loops) |

## 7. Verification (Section 4)

### C-checks (per-skill, Phase A')

| # | Check | Method |
|---|---|---|
| C1 | All applicable improvements applied | spec-reviewer diff vs spec |
| C2 | Hook does not block | `bash .claude/hooks/validate-skill-folder-structure.sh` |
| C3 | Body token ≤ 6,000 | `wc -w < SKILL.md` < ~4,500 words |
| C4 | Frontmatter YAML valid | `python3 -c "import yaml; yaml.safe_load(...)"` |
| C5 | `related_skills` ⊆ INDEX.md 17 relations | grep cross-check |
| C6 | Shorthand sk-code first occurrence has gloss | regex |
| C7 | If body > 180 lines after improvements 1, 2, 3, 5, and applicable Tier-3 → `references/cases.md` exists + A1 MANDATORY | file + grep |
| C8 | Description first sentence preserved (except sk13/sk14) | diff vs cache version |

### X-checks (cross-skill, Phase B)

| # | Check | Why |
|---|---|---|
| X1 | `related_skills` symmetry where INDEX declares both directions | Sterman-style reverse-link consistency |
| X2 | All 14 descriptions follow verb-first + trigger + NOT-for + KEYWORDS | Router-quality consistency |
| X3 | Source-unit codes don't collide across skills | Single-source provenance |
| X4 | All 17 INDEX.md relations are reflected in at least one frontmatter | Stage-3 graph integrity |
| X5 | sk13 TRIZ disclosure + sk14 DISC/MBTI disclosure still present | V1-weak transparency must survive Tier-3 edits |

### Plugin-shell checks (Phase C)

- `python3 -m json.tool plugin.json` parses OK.
- `python3 -m json.tool .claude-plugin/marketplace.json` parses OK and
  contains a `systems-thinking-toolkit` entry.
- INDEX.md markdown links resolve to actual SKILL.md files.
- Entry skill mentions all 14 skills with correct slugs.

### Plugin-level CI (Phase E)

- Commit-message format per memory `feedback_cc_type_whitelist`.
- `find systems-thinking-toolkit/skills -mindepth 3 -type d` returns empty
  (skill folders are flat or contain only `references/`).
- GHA CI passes on push.

## 8. Risks & mitigations (Section 5)

| # | Risk | Mitigation |
|---|---|---|
| R1 | Subagent pattern drift across 13 parallel implementers | Pilot sk01 commit hash + reference pattern doc consumed by every implementer; X-checks (Phase B) catch residual drift |
| R2 | Implementer invents `related_skills` beyond INDEX 17-list | Implementer prompt enforces subset rule; spec-reviewer C5 cross-checks |
| R3 | `.claude/hooks/validate-skill-folder-structure.sh` may not fire inside worktree | Worktree lives in `.claude/worktrees/` inside the repo — inherits `.claude/settings.json`; spec-reviewer C2 runs the hook script directly as a safety net |
| R4 | 26-subagent parallel dispatch hits rate limit | Each subagent receives paths, not file contents; if limited, split to two waves (sk02-08, sk09-14) |
| R5 | `references/cases.md` extraction empties A1 | A1 retains 1-2 line summary as load-rationale; sk01 pilot rehearses the pattern (or sk08/sk12 do if sk01 doesn't trigger #4) |
| R6 | sk13/sk14 description rewrite breaks router triggering | Tier-3 #7 keeps all original keywords intact; only prepends a framing prefix |
| R7 | Cache vs plugin version drift over time | D1 accepted: cache becomes archived snapshot; re-distill flows into a new plugin version (manual merge), documented in ROADMAP.md |
| R8 | 5-7h Phase B drift-fix loop blows out wall-clock | Loop cap 3 rounds; round-4 issues recorded in ROADMAP.md as known limitations |
| R9 | Per-skill README translation quality uneven across 14 subagents | Fixed terminology glossary issued pre-dispatch; sk01 README triplet becomes reference for the other 13 |

### Accepted residuals

- R8: wall-clock may stretch to 7-9h on drift-heavy Phase B.
- R9: translation quality remains LLM-draft tier per existing
  `project_i18n_multilingual_readme` precedent.
- R6: minor router-triggering precision loss for sk13/sk14, to be
  monitored against use feedback in v0.2.

## 9. Out of scope for v0.1.0

- TRIZ-replacement skill for sk13 (D2 defers).
- sk13/sk14 merger or pruning (D2 defers).
- Domain expansion beyond Sherwood 2002 source book.
- Score-history tracking via `dev-workflow:skill-judge` companion script.
- Ultrareview (user-triggered, low ROI for markdown content).

## 10. Provenance

- **Cache source**:
  `~/.tsundoku/cache/distilled/Seeing-the-Forest-for-the-Trees-A-Manager's-Guide-to-Applyin/`
- **Source book**: Dennis Sherwood, *Seeing the Forest for the Trees: A
  Manager's Guide to Applying Systems Thinking* (Nicholas Brealey, 2002).
- **Distill date**: 2026-05-11.
- **Skill-judge run**: 2026-05-12 (14 subagent evaluations, results captured
  in conversation log preceding this spec).
- **Pipeline**: `tsundoku:book-distill` RIA-TV++ (Adler → 5-parallel-extractors
  → triple-verification → RIA++ render → Zettelkasten linking → adversarial
  pressure test).

## 11. Next steps

1. User reviews this spec.
2. On approval, invoke `superpowers:writing-plans` to produce the
   commit-by-commit implementation plan.
3. Plan execution follows Phase 0 → A → A' → B → C → D → E.
