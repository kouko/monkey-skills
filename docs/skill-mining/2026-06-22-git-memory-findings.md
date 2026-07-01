# git-memory — execution-status findings & improvement proposals

- **Date**: 2026-06-22
- **Target skill**: `dev-workflow:git-memory`
- **Method**: distill-sessions Stage 1+2 preview (`--target-skill-pattern '*git-memory*'`) + direct git-history audit of this repo + read of the live `SKILL.md` / `protocols/` / `standards/`
- **Status**: findings only — no skill edits made yet

---

## TL;DR

git-memory's **thinking layer is alive but its durable layer leaks**: on
recent memory-worthy work the decisions landed in Claude-native
`MEMORY.md` but **not in git**. Roughly **half** of memory-worthy
squash-merges to `main` carry no trailer *and* no PR `## Memory`
section, so the decision context is absent from the durable,
tool-agnostic substrate the skill exists to populate. The leak
concentrates at the **squash/PR step**, which the SKILL.md documents but
treats as advisory prose rather than an enforced gate step.

---

## 1. Scope & data

| Source | What it tells us |
|---|---|
| Session transcripts (distill preview) | 75 sessions invoke git-memory; `confidence: high`; cross-project; `facet_summary: {}` (no `/insights` data → kind via heuristic fallback) |
| Selected trajectories | 6 (5 failure + 1 success), each 392–1204 events |
| git history (last 500 commits) | 148/500 carry ≥1 trailer (~30%); Decision 338 / Learning 167 / Gotcha 168 |
| git history (main first-parent) | 58/100 squash-merges carry a trailer |

---

## 2. Method critique — why the generic mining pipeline mis-targets this skill

distill-sessions is tuned for **work-producing** skills (brainstorming /
writing-plans / SDD), where in-session friction signals
(interrupt-after-brainstorm, NEEDS_REVISION streaks, re-dispatch
concentration) attribute to the skill that caused them.

git-memory is a **tail-gate**: it is invoked near the end of almost
every coding session, right before commit/PR. Consequences:

- "Sessions that invoked git-memory" ≈ "all coding sessions" — the 75
  matched sessions are not a git-memory-specific population.
- The friction the pipeline detects in those sessions belongs to the
  **host coding work**, not to git-memory. The 6 selected trajectories
  are large `code-toolkit` dogfood sessions (e.g. `3d998518` is a
  code-toolkit external-API-grounding brainstorm).
- Running the generic Stage 3 fan-out on them would misattribute
  code-toolkit friction to git-memory — and it is the expensive step.

**The real signal for a tail-gate skill is not session friction — it is
the durable artifact it produces (git history) plus the narrow gate
interaction itself.** This report works from those.

---

## 3. Findings

### F1 — ~50% of memory-worthy squash-merges leak (highest severity)

Recent memory-worthy PRs whose squash commit has **no footer trailer
AND no PR `## Memory` section**:

| PR | Subject | In git? | In Claude `MEMORY.md`? |
|---|---|---|---|
| #440 | rename design→code suite to loom- (BREAKING) | ❌ | ✅ (rich) |
| #442 | wire the spec→code seam | ❌ | ✅ |
| #443 | deliberate-simplification ledger | ❌ | ✅ |
| #444 | mined skill improvements | ❌ | ✅ |
| #430 | skill-dev-toolkit extraction | ❌ | ✅ |
| (multiple dbt-wiki feat PRs) | value_domain / lint gate / Phase-B | ❌ | partial |

Same era, **did** record it correctly: #426 (description standard) —
the author remembered the `## Memory` section.

**Interpretation**: not a clean regression — **inconsistent gate
adherence**. The decisions were made and were captured (Claude-native
`MEMORY.md` proves it), but the durable git substrate ended up empty.
This is precisely the failure mode SKILL.md §"Invocation policy" warns
about ("Pre-deciding 'this commit is routine, I'll skip the skill' is
the bug") — now observed in practice, and located specifically at the
**squash/PR substrate-survival step**.

### F2 — `merge` is not in the gate's trigger surface

The description fires the gate "before every git commit / gh pr create".
**`gh pr merge --squash` is not listed** — yet squash is exactly the
step where per-commit trailers get relocated to mid-body and the PR
`## Memory` section becomes the only durable carrier. There is no
checkpoint at the moment of loss.

### F3 — squash-survival is documented but advisory

SKILL.md lines 77–98 fully describe the squash caveat and two escape
hatches (`squash_merge_commit_message = PR_BODY` + raw footer, or a
merge-commit for memory-worthy PRs). `protocols/compose-pr.md` makes
`## Memory` **additive / optional** ("If none apply, skip `## Memory`
entirely"). Nothing verifies post-merge that
`git log --grep='^Decision:' main` actually finds the memory. Advisory
prose is silently skippable, and F1 shows it gets skipped ~half the time.

### F4 — Claude-native ↔ git divergence is unmonitored

The genuine leak is "decided in session → written to `MEMORY.md` → never
written to git". SKILL.md §"Phased rollout" Phase 3 plans the *forward*
direction (git → distilled `MEMORY.md`). The *reverse* gap (session
decision never reaches git) is the one biting now and is unaddressed.
No reconciliation step asks "these decisions are in this session /
`MEMORY.md` — are they in the PR's `## Memory`?"

### F5 (minor) — no `/insights` facets

`facet_summary: {}` for all matched sessions → distill's `kind`
classification falls back to the friction heuristic. Not a git-memory
defect, but it caps any future session-based mining of this skill.

---

## 4. Improvement proposals (source-grounded, value-ranked)

### P1 — Add `merge` to the gate trigger (addresses F2)

Extend the invocation surface from "before commit / pr create" to
include "before `gh pr merge` (esp. `--squash`)". The merge step is
where memory is lost; the gate must fire there. Touches: `SKILL.md`
description + §"Invocation policy" table.

### P2 — Promote squash-survival from prose to an enforced check (F1, F3)

At PR-create / merge time for a memory-worthy PR, **require** one of the
documented escape hatches AND verify it: after writing, confirm
`git log --grep='^Decision:' <branch-or-main>` (or the PR `## Memory`
section) actually returns the trailers. Touches: `protocols/compose-pr.md`
(make `## Memory` non-optional for memory-worthy PRs), `SKILL.md`
§Pillar 2 caveat (add the verification step), possibly
`scripts/memory-grep.sh` (add a `--verify` mode).

### P3 — Pre-merge native↔git reconciliation (F4)

Before opening/merging a PR, cross-check the session's decisions (and
any new `MEMORY.md` entries from this work) against the PR `## Memory`
section; flag decisions that exist in one but not the other. Touches:
`protocols/compose-pr.md` Step 2 (add a reconciliation sub-step).

---

## 4b. Confirmation round — broadened evidence (2026-06-22)

The F1 root-cause was revised once on a single data point (#444). To avoid
anecdote, it was re-tested from three independent angles. All three agree:
**the leak is at authoring/PR time, not squash time, and the dominant
failure is the gate never firing — not firing-then-returning-empty.**

### Angle 1 — cross-repo adoption (10 of the user's repos, last ≤300 commits each)

| repo | commits | Claude-involved | trailer rate |
|---|---|---|---|
| monkey-skills (dogfood home) | 300 | 1011 | **38%** |
| redshift-comment-mcp | 129 | 66 | 22% |
| intellij-dbtree | 221 | 142 | 21% |
| iCHEF-dbt-pipeline | 300 | 249 | 18% |
| reading-list-summarize-scraper | 75 | 92 | 15% |
| dotfiles | 245 | 239 | 9% |
| youtube-summarize-scraper | 90 | 87 | 7% |
| company-context-layer | 180 | 202 | **3%** |
| meeting-emo-transcriber | 154 | 92 | **3%** |

- git-memory **is** portable — trailers appear in every Claude-active repo,
  not just the dogfood home (the portability thesis holds).
- Adoption is **highly uneven**: 38% in the dogfood repo, 3–22% elsewhere.
- Claude is the author in most commits everywhere (Co-Authored-By counts
  ≥ commit counts), so the low rate is **not** humans bypassing the gate —
  it is **Claude-authored commits skipping the substrate write**.
- Several low-rate repos use direct commits, not squash PRs → **squash is
  ruled out as the cause**; the substrate is empty even with no squash.

### Angle 2 — in-repo classification (monkey-skills main first-parent, last 80 squash merges)

| class | total | carry trailer | missing |
|---|---|---|---|
| **Memory-worthy** (feat / refactor / BREAKING) | 53 | 29 (55%) | **24 (45%)** |
| Routine (chore / docs / fix / test …) | 27 | 16 (59%) | 11 |

- **45% of memory-worthy squash merges ship with zero git-side memory** —
  a 53-PR sample, not one anecdote. The missing list includes #442, #440
  (BREAKING), #439, #430, multiple dbt-wiki / ascii-graph / code-toolkit
  feats, and the #398/#399 design-front-end MVPs — substantive work whose
  decisions exist richly in Claude-native `MEMORY.md` but not in git.
- **Nuance**: routine commits carry trailers (59%) at a rate *no lower*
  than memory-worthy ones (55%). Trailer presence does **not** correlate
  with memory-worthiness → recording is near-random w.r.t. worthiness,
  consistent with "depends on whether the agent fired the gate this
  session," not "the gate classified correctly."

### Angle 3 — gate-invocation rate (monkey-skills session transcripts, 89 sessions)

Real skill-load markers (`Launching skill: …`, not catalog text):

| skill | sessions loaded (of 89) |
|---|---|
| brainstorming | 44 |
| **git-memory** | **28 (~31%)** |
| finishing-a-development-branch (delegates git-memory) | 13 (~15%) |

- Even in the dogfood-heaviest repo, the git-memory gate fired in only
  ~31% of sessions while every session commits → the dominant failure is
  **the gate never firing at commit / PR / merge**, not firing-then-empty.
- The low-invocation (transcript) and high-missing (git, Angle 2) numbers
  **triangulate** — same leak seen from authoring side and artifact side.
- Caveat: not every session produces a memory-worthy commit, so the raw
  "~69% didn't fire" overstates the miss; the artifact-side 45% is the
  conservative, load-bearing figure.

**Implication for the fix**: P1 (extend the trigger surface so the gate
fires at more checkpoints, incl. merge) is the **primary** lever — it
attacks the dominant never-fired failure. P2 (verify) is the deterministic
backstop that catches the residual cases where it fired but recorded
nothing. The original F1 "squash leak" framing is **superseded** by this
authoring-time / never-fired framing.

## 5. Recommended next step

Route P1–P3 through loom-code (`brainstorming → writing-plans →
subagent-driven-development / tdd-iron-law`) as a focused git-memory
skill edit. **Do not** run the generic distill Stage 3 fan-out on the 6
selected trajectories — per §2 it would misattribute code-toolkit
friction to git-memory at non-trivial cost.

P1 + P2 are the high-value pair (close the leak at the exact step it
happens). P3 is the belt-and-suspenders reconciliation. F5 is
out-of-scope for git-memory itself.
