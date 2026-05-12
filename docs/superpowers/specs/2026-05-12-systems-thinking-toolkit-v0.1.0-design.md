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

Mean 105/B, median 108.5/A. **Note**: this score table reflects the
pre-merge 14-skill set as evaluated on 2026-05-12. Per D7 below, v0.1.0
ships a 9-skill plugin via the Profile B merge mapping in §3.5 — five
merge pairs + four standalone skills. Post-merge skill-judge scores will
be re-baselined as part of Phase 0 pilot self-judge (§6).

Across 14 evaluations, common sub-A patterns were:

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
| D7 | Profile B merge: 5 INDEX-declared `compose-with` / `depends-on` pairs merged into 5 new skills; 4 skills stay standalone (see §3.5) | User Q (merge profile) |

## 3.5 Profile B merge mapping

The 5 merges are restricted to pairs that INDEX.md already declares as
`compose-with` or that form a tight `depends-on` chain. Pairs that
contrast at the cognitive-frame level (sk05 R+B coupling vs sk06 single
B template; sk13 vs sk14 V1-weak) stay standalone.

| New skill (kebab) | Sources | INDEX relation | Rationale |
|---|---|---|---|
| `loop-and-link-primitives` | sk01 + sk02 | sk03 `depends-on` both | Always co-used: link-signing precedes loop-classification; presenting them as one primitives layer reduces router hops |
| `cld-craft` | sk03 + sk04 | `compose-with` | Stage-3 declares the pair; sk03 Rule 7 directly triggers sk04 |
| `strategy-lever-and-cascade` | sk07 + sk08 | sk08 `depends-on` sk07 | sk07 is the reframe, sk08 is its three-timescale expansion — workflow-trunk |
| `stakeholder-and-team-thinking` | sk09 + sk10 | `compose-with` | Both stakeholder-aware; INDEX explicitly pairs them |
| `simulation-modeling` | sk11 + sk12 | sk12 `depends-on` sk11 | sk11 without sk12 is half-finished translation; sk12 without sk11 is rhetoric without artifact |

| Standalone | Why kept separate |
|---|---|
| `limits-to-growth-take-the-brakes-off` (sk05) | Contrasts with sk06 (R+B coupling archetype vs single B template); merge would dilute the trigger surface |
| `variance-target-action-template` (sk06) | Same as above |
| `innovaction-martian-test` (sk13) | V1-weak per Stage 1.5; D2 defers merger/pruning to v0.2+ |
| `manager-personality-quadrant` (sk14) | Same as above |

**Total skill count**: 5 merged + 4 standalone + 1 entry/router
(`using-systems-thinking-toolkit`) = **10 skill directories**.

**Total slash commands**: 9 per-skill + 1 router = **10 commands**.

## 4. Plugin architecture (Section 1)

```
systems-thinking-toolkit/                            ← repo root, sibling to philosophers-toolkit
├── plugin.json                                       ← SoT for plugin metadata
├── README.md / README.ja.md / README.zh-TW.md        ← plugin-level tri-lang
├── ROADMAP.md                                        ← v0.1 → v0.2+ (incl. sk13/sk14 merger discussion)
├── INDEX.md                                          ← plugin-level skill map (Stage-3 mermaid linkified)
│
├── commands/                                         ← 9 per-skill + 1 router = 10 slash commands
│   ├── stt.md                                        ← /systems-thinking-toolkit:stt = router
│   ├── link-primitives.md                            ← sk01+sk02
│   ├── cld-craft.md                                  ← sk03+sk04
│   ├── limits-to-growth.md                           ← sk05
│   ├── variance-action.md                            ← sk06
│   ├── strategy.md                                   ← sk07+sk08
│   ├── stakeholder.md                                ← sk09+sk10
│   ├── simulation.md                                 ← sk11+sk12
│   ├── martian-test.md                               ← sk13 (V1-weak)
│   └── quadrant.md                                   ← sk14 (V1-weak)
│
├── skills/                                           ← 9 + 1 entry = 10 skill dirs (see §3.5)
│   ├── using-systems-thinking-toolkit/
│   │   ├── SKILL.md                                  ← entry / router skill
│   │   └── README.md / .ja.md / .zh-TW.md
│   │
│   ├── loop-and-link-primitives/                     ← MERGE: sk01 + sk02
│   │   ├── SKILL.md
│   │   ├── README.md / .ja.md / .zh-TW.md
│   │   └── references/cases.md                       ← likely triggered (merged body > 180 lines)
│   │
│   ├── cld-craft/                                    ← MERGE: sk03 + sk04
│   │   ├── SKILL.md
│   │   ├── README.md / .ja.md / .zh-TW.md
│   │   └── references/cases.md                       ← likely triggered
│   │
│   ├── strategy-lever-and-cascade/                   ← MERGE: sk07 + sk08; largest merged body, cases.md required
│   ├── stakeholder-and-team-thinking/                ← MERGE: sk09 + sk10
│   ├── simulation-modeling/                          ← MERGE: sk11 + sk12; cases.md likely
│   ├── limits-to-growth-take-the-brakes-off/         ← STANDALONE: sk05
│   ├── variance-target-action-template/              ← STANDALONE: sk06
│   ├── innovaction-martian-test/                     ← STANDALONE: sk13 (V1-weak, per D2)
│   └── manager-personality-quadrant/                 ← STANDALONE: sk14 (V1-weak, per D2)
│       (all same structure: SKILL.md + tri-lang README + optional references/cases.md)
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

These nine improvements are applied **after** the Profile B merges (§3.5
D7) are mechanically combined. The 5 merge implementers each perform a
two-step task: (a) **combine** two source SKILL.md files into one merged
SKILL.md (deduplicate R/I/A1/A2/E/B sections, unify frontmatter,
preserve all distinct evidence), then (b) apply the nine improvements
below. The 4 standalone-skill implementers skip step (a).

Each improvement is applied per (post-merge or standalone) skill; some
are conditional, some affect all 9, two are skill-specific overrides.

### Tier 1 — applies to all 9 (post-merge)

**1. Frontmatter `related_skills` backfill.**
Cross-reference `references/INDEX.md` (the Stage-3 17-relation list,
re-mapped to the merged 9-skill graph per §3.5) and populate each
skill's frontmatter `related_skills`. The re-mapping rule: a relation
sk0X → sk0Y in the original 17-list maps to merged-skill → merged-skill
where each side is the skill or merged target that contains the source
skill. Self-loops created by intra-merge edges (e.g. sk03 ↔ sk04 both
inside `cld-craft`) are dropped.

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

**6. `loop-and-link-primitives` reverse-link backfill.**
sk01 (now merged into `loop-and-link-primitives`) is the foundational
skill on which 4+ downstream skills depend, but its pre-merge frontmatter
`related_skills: []` is empty. The merged skill's frontmatter must
populate `related_skills` with reverse links to the skills that
`depends-on` sk01 — re-mapped via §3.5 (e.g. sk05 standalone, sk06
standalone, sk10 inside `stakeholder-and-team-thinking`, and the
`cld-craft` merge).

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

**9. INDEX.md plugin-ization and re-mapping.**
Cache version of `INDEX.md` is copied to plugin root with three changes:

- Mermaid graph re-drawn from 14 → 9 nodes, with intra-merge edges
  (e.g. sk01↔sk02, sk03↔sk04) dropped and inter-merge edges re-targeted
  to the new merged-skill names.
- Node labels become markdown links pointing to `skills/<slug>/SKILL.md`.
- "Recommended learning order" numbered list re-derived from the 9-node
  topological sort, with per-item markdown links.

The original 14-node graph is preserved in `references/INDEX.md` (i.e.
the verbatim cache copy) for provenance.

### Out of scope (deferred to v0.2+)

- stock-flow numerical computation script (sk11)
- doubling-time calculator (sk12)
- sk13 / sk14 merger or removal (D2 defers)
- New TRIZ-replacement skill (D2 defers)
- Per-skill `checklists/` extraction (only `references/` used in v0.1.0)
- Score-history tracking (`dev-workflow:skill-judge` optional companion)

## 6. Orchestration (Section 3)

### Phase 0 — Pilot (controller direct, no subagent)

Controller produces ONE merged skill end-to-end as the pattern reference.
Pilot target: **`cld-craft`** (sk03 + sk04 merge). Rationale: it's the
cleanest natural merge case (Stage-3 compose-with declared; Rule 7 trigger
relationship explicit), with moderate combined body size (~300 lines
pre-improvement) — exercises both merge mechanic AND the 9 improvements
at representative scale.

Outputs:

- One atomic commit on the worktree branch.
- Reference pattern document (the `cld-craft` commit hash + its
  `references/cases.md` if triggered) for Phase A subagents.

Self-judge with `dev-workflow:skill-judge` rubric: pilot must score ≥
107 (the unmerged sk03 baseline = 107/B; pilot target ≥ that with no
dimension regression). **Halt condition: any dimension drops → re-pilot
before Phase A.** Also re-score the pre-merge sk04 baseline (110/A)
against the merged output — merged skill scoring lower than the BETTER
of its two sources triggers re-pilot.

### Phase A + A' — 8 implementers + 8 spec-reviewers (parallel)

Dispatched together in one batch (16 subagent invocations). The 8
implementers split into two task types:

- **4 merge-implementers** (one each for: `loop-and-link-primitives`,
  `strategy-lever-and-cascade`, `stakeholder-and-team-thinking`,
  `simulation-modeling`): perform mechanical merge of two source SKILL.md
  files + apply 9 improvements.
- **4 polish-implementers** (one each for: sk05, sk06, sk13, sk14
  standalone): skip the merge step; apply 9 improvements directly.

Each implementer receives:

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

Token-budget mitigation: 16-subagent batch is well within rate-limit
headroom; no wave-split anticipated.

### Phase B — Fresh-eyes cross-skill audit (1 subagent)

After all 8 implementers PASS, dispatch one fresh-eyes auditor. It
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
- 9 per-skill commands per §4 directory listing (`link-primitives.md`,
  `cld-craft.md`, `limits-to-growth.md`, `variance-action.md`,
  `strategy.md`, `stakeholder.md`, `simulation.md`, `martian-test.md`,
  `quadrant.md`)
- `README.md` (plugin-level English)

### Phase D — Per-skill READMEs (9 parallel subagents)

Each of 9 subagents owns one (post-merge or standalone) skill's three
READMEs (en / ja / zh-TW). A glossary of systems-thinking terminology is
fixed before dispatch (e.g. "reinforcing loop" → 「強化迴路」/「強化ループ」;
"causal loop diagram" → 「因果迴路圖」/「因果ループ図」).

The `cld-craft` README subagent (call it the **Phase-D anchor** — distinct
from the Phase-0 controller-pilot) is dispatched first and finishes ahead
of the others; its 3-language README triplet becomes the reference for
the other 8 README subagents. Total 27 per-skill README files.

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
| 0 (pilot — `cld-craft` merge end-to-end) | 0 | 2-3h (heavier than original — merge mechanic + 9 improvements) |
| A + A' | 16 parallel (8 impl + 8 review) | ~45 min (4 merge-impl heavier than 4 polish-impl) |
| B (fresh-eyes) | 1 | ~10 min |
| C (plugin shell) | 0 | 2-3h |
| D (READMEs) | 9 parallel | ~30-45 min |
| E (CI / PR) | 0 | ~30 min |
| **Total** | **26** | **6-8h** (excluding fresh-eyes loops; pilot heavier per-phase but fewer subagents) |

## 7. Verification (Section 4)

### C-checks (per-skill, Phase A')

| # | Check | Method |
|---|---|---|
| C1 | All applicable improvements applied | spec-reviewer diff vs spec |
| C2 | Hook does not block | `bash .claude/hooks/validate-skill-folder-structure.sh` |
| C3 | Body token ≤ 6,000 | `wc -w < SKILL.md` < ~4,500 words |
| C4 | Frontmatter YAML valid | `python3 -c "import yaml; yaml.safe_load(...)"` |
| C5 | `related_skills` ⊆ INDEX.md 17 relations, re-mapped per §3.5 to merged 9-skill graph; intra-merge edges dropped | grep cross-check |
| C6 | Shorthand sk-code first occurrence has gloss | regex |
| C7 | If body > 180 lines after improvements 1, 2, 3, 5, and applicable Tier-3 → `references/cases.md` exists + A1 MANDATORY | file + grep |
| C8 | Description first sentence preserved (except sk13/sk14, and except 5 merged skills which by definition rewrite descriptions to cover both source trigger surfaces) | diff vs cache version |
| C9 (merge-only) | Merged SKILL.md preserves ALL distinct source-unit code citations from both source skills (no provenance loss) | grep audit metadata diff |
| C10 (merge-only) | Combined body ≤ ~6000 tokens (~4500 words); if exceeded, `references/cases.md` extraction MUST trigger | `wc -w` + file existence |

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
| R9 | Per-skill README translation quality uneven across 9 subagents | Fixed terminology glossary issued pre-dispatch; `cld-craft` pilot README triplet becomes reference for the other 8 |
| R10 | Merge mechanic loses nuance from one of the two source skills (e.g. sk02's Sterman ultimate-test detail flattened into sk01's even-O/odd-O dominant frame) | C9 (Phase A') checks source-unit citation preservation; pilot self-judge re-scores merged skill vs the BETTER of two source baselines; halt on dimension regression |

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
