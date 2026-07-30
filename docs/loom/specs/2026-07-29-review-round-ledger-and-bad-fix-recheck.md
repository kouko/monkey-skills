# Brief: whole-branch review round ledger + bad-fix re-check (P1+P2)

- **Date**: created 2026-07-29, revised 2026-07-30 after six-agent primary-source
  research and a `dev-workflow:complexity-critique` pass.
- **Slice**: (P1+P2) of the three-slice loom-* review-mechanism plan. (P3+P4)
  shipped as loom-code 0.40.0 (PR #627); (P5+P6) not started.
- **Source audit**: `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`
  §3.2 (no convergence criterion) + §1 (the trajectory) + §5 (ship the check as a
  script).
- **Status**: brief, user-ratified on three forks — mechanical ledger over
  prose-only; delete the hard round-cap number; ship ledger and bad-fix re-check
  together.

## Problem

The job: **make a review loop's own cost and self-injection visible, so a human
can stop it on evidence instead of noticing by hand on round nine.**

Two loops in this family iterate on a NEEDS_REVISION verdict. Both other loops
in the family are capped — `subagent-driven-development/SKILL.md:148-153` caps
re-dispatch at 3 rounds then escalates, with an independent 2-round cap for
NEEDS_CONTEXT at `:103`; `writing-plans/SKILL.md:81` carries a 2-round cap
(breached once and explicitly authorised on 2026-07-27, recorded at
`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md:12`). The whole-branch
loop has nothing: `requesting-code-review/SKILL.md:109` says only "re-dispatch if
user fixed and wants re-review", and `finishing-a-development-branch/SKILL.md:113-115`
makes the absence worse by contract — NEEDS_REVISION loops "digest silently; the
user sees only the terminal verdict, never each iteration."

Both measured pathological loops happened in the uncapped one. Audit §1 records
nine rounds with no PASS and a defect count that never fell
(4 → 1 → 2 → 1 → 3 → 2 → 2 → 4 → 1), of which **six of nine rounds found a
defect introduced by the previous round's own remediation**.

### Why the primary justification is instrumentation, not braking

The obvious framing — "add a brake" — is the weaker one. Two facts moved it:

1. We cannot currently answer *why* this started happening, because round counts
   were never recorded (see §Causation, unresolved). A brake does not make that
   question answerable; a ledger does.
2. The complexity-critique pass found that trajectory surfacing plus a hard cap
   number are two controls for one job, and the number is the element with no
   evidential basis anywhere in the researched literature. Deleting it leaves one
   control — which is the deletion-biased answer, and it also removes the brake
   framing's main artefact.

So: the ledger is the instrument. The bad-fix re-check is the fix. There is no
numeric cap.

## Users

**When** an orchestrator is closing out a branch and the whole-branch reviewer
returns NEEDS_REVISION for the third time, **I want** the loop to hand me its own
trajectory and tell me how much of it is self-inflicted, **so I can** stop and
re-shape the artifact instead of paying for round four.

Specifically: the loom-code orchestrator (the strong main-loop model, running
`requesting-code-review` directly or via `finishing-a-development-branch`), and
the three reviewer subagents carrying `_reviewer-discipline.md`.

Secondary user: the person paying for the rounds, who under the current
digest-silently contract cannot see the cost until it is spent.

## Smallest End State

Three changes, in dependency order. **No hard round-cap number is shipped.**

1. **Ledger (the instrument).** `loom_gate_markers.py review-pass` appends one
   entry per invocation — **including the NEEDS_REVISION path that currently
   exits 3 writing nothing** — to `<git-dir>/loom/review-rounds.json`, keyed by
   branch name only. Each entry records:

   | Field | Why |
   |---|---|
   | `round` | the count nobody has ever had |
   | `verdict` | PASS / PASS_WITH_NOTES / NEEDS_REVISION |
   | `findings_reported` | raw union count — kept for diagnostics, **not** the signal |
   | `findings_surviving` | findings that produced a remediation action — **this is the trajectory signal** |
   | `findings_bad_fix` | of the surviving ones, how many land in the previous round's fix region |
   | `arm_overlap` | how many findings the two panel arms both reported — an independence diagnostic |
   | `head_sha` | so a human can later identify which round's artifact was best |

   No new orchestrator obligation is created: `requesting-code-review/SKILL.md:100`
   already instructs an unconditional mint call on every round, so the call site
   fires on failing rounds today and discards everything at
   `loom_gate_markers.py:268-272`.

2. **Round discipline (prose consuming the ledger).** In
   `requesting-code-review` and `finishing-a-development-branch`: from round 3,
   surface the trajectory the script printed, and classify the loop using a
   five-state rubric (fast-converging / converging / stalling / oscillating /
   diverging — borrowed as *judgment vocabulary only*, see §Alternatives), plus
   the audit's editorial-versus-structural distinction. At the point where the
   orchestrator judges the loop non-converging, **escalate to the user** — on that
   judgment, not on a round number. Prose-surface findings are **recorded, not
   rewritten**, from round 1 onward.

3. **Bad-fix re-check (reviewer contract).** A new rule in
   `loom-code/scripts/_reviewer-discipline.md`: on a re-review, verify the region
   changed by the previous round's fix **before** re-sweeping the artifact; and
   when the same defect *type* appears a second time, sweep the population rather
   than the named instance. Regenerated into the three reviewer agents via
   `distribute.py`; no new file.

**Composition constraint (from the complexity-critique pass — must reach the
plan).** The marker and the ledger are different concerns: the marker binds
*content* (`head_sha` + `patch_id`, fail-closed, read by the push guard); the
ledger binds *process* (branch-keyed, never resets). They may share the CLI entry
point — `loom_gate_markers.py` is already a multi-verb CLI — but the ledger
**must not reuse the marker's patch-id binding logic** and must write a separate
file with a separate key. Sharing the call site is composition; sharing the
binding would be complecting.

## Current State Evidence

- **Forward** — orchestrator unions both reviewer arms' findings, re-aggregates,
  writes the panel verdict to a temp file, runs
  `loom_gate_markers.py review-pass --verdict-file <file>`
  (`loom-code/skills/requesting-code-review/SKILL.md:100`); on PASS /
  PASS_WITH_NOTES it writes `.git/loom/review-pass.json` and exits 0
  (`loom-code/scripts/loom_gate_markers.py:290-292`). The union rule already
  computes arm overlap — "the same finding" = same `file:line` AND same dimension
  → one line — and then discards the overlap count.
- **Reverse (SSOT ownership — read from the distribution script, not inferred)**
  — `loom-code/scripts/_reviewer-discipline.md` is canonical; `distribute.py`
  injects its body verbatim between `BEGIN/END reviewer-discipline-v1` markers
  into the three agents listed in `AGENT_REVIEWER_DISCIPLINE_TARGETS`
  (`loom-code/scripts/distribute.py:193-209`), and `verify-drift.py` byte-diffs
  the result in CI (`loom-code/scripts/verify-drift.py:103-124`). Direction is
  `scripts/_reviewer-discipline.md` → `agents/*.md`; injected blocks are never
  edited in place. Current content is R1 (`standards_version` stamp), R2
  (evidence citation per element), R3 (unconfirmed evidence downgrades).
- **Error** — `NEEDS_REVISION` returns exit 3 and writes nothing
  (`loom-code/scripts/loom_gate_markers.py:268-272`); a schema-invalid verdict
  returns exit 4 listing every violation (`:257-266`). Neither path leaves any
  on-disk trace that a round happened, which is why round counting is currently
  impossible without conversation state — and why the causation question below
  cannot be answered retrospectively.
- **Data** — markers resolve to `<git-dir>/loom/` (`resolve_marker_dir`,
  `loom-code/scripts/loom_gate_markers.py:160-169`), are JSON carrying
  `"schema": 1`, and are written atomically through a temp file + `os.replace`
  (`_write_marker`, `:171-185`). They are runtime state under `.git/`, not
  version-controlled — so the ledger is **not** a repo file and does not breach
  the slice's "no new file" constraint.
- **Boundary** — `loom-code/hooks/git-guard.py` reads only three specific
  filenames (`review-pass.json` / `verified.json` / `waiver.json`, documented
  `git-guard.py:22-48`) and never globs the marker directory, so a fourth file is
  inert to the push gate. SKILL.md word budgets against CHK-SKL-010's 4,500-word
  hard cap: `requesting-code-review` 3,930 (≈570 words of headroom, already above
  the repo's ~3,750 soft target), `finishing-a-development-branch` 3,261.

**Evidence paths**: `loom-code/scripts/loom_gate_markers.py`,
`loom-code/scripts/distribute.py`, `loom-code/scripts/verify-drift.py`,
`loom-code/scripts/_reviewer-discipline.md`, `loom-code/hooks/git-guard.py`,
`loom-code/skills/requesting-code-review/SKILL.md`,
`loom-code/skills/requesting-code-review/references/gate-markers-spec.md`,
`loom-code/skills/finishing-a-development-branch/SKILL.md`,
`loom-code/skills/subagent-driven-development/SKILL.md`,
`loom-code/skills/writing-plans/SKILL.md`,
`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`.

## Alternatives Considered (Axis 4 — six dispatched research agents, primary sources, EN + JA, 2026-07-29/30)

Publication status is stated for every source because three of the most relevant
are unreviewed preprints.

| Alternative | Evidence | Disposition |
|---|---|---|
| **Prose-only rule in the two SKILL.md files** (this slice's original shape) | The audit records the failure at §6b — its own §4.2 practice recurred *after* being named in the audit. `docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md` requires every *consequence* to get a deterministic carrier. Independently corroborated: *When Agents Do Not Stop* (arXiv 2607.01641, **preprint, submitted 2026-07-02**) attributes real-world loop failures to bounds that developers "omit… misuse… or **place outside the actual feedback path**", and recommends bounds "enforced at the runtime scope where feedback is created". | **Rejected as sole carrier.** Kept as the explanatory layer over the ledger. The paper's diagnosis is the direct argument for putting the instrument in the script that already runs every round. Note: its mitigations are *proposed, not empirically evaluated*. |
| **Fixed hard round cap** (was: surface at 3, escalate at 5) | No source in six agents' research supports any specific number. The only concrete practitioner precedent found was a JA implementation capping an automated review→fix→re-review loop at 5 rounds [JA, Zenn]. `writing-plans` uses 2 and SDD uses 3 in this repo. | **DELETED per user decision.** Trajectory surfacing plus human judgment is one control for the job; a number would be a second control resting on nothing. |
| **LoopGain's statistical control law** (github.com/loopgain-ai/loopgain, Apache-2.0, 111 stars, **single contributor**, last push 2026-07-26) | Read from source: `classifier.py` derives `E_ratio`, `slope_log` (OLS on log10(E)), `slope_p` (t-test), `osc_std` (detrended log10 std); thresholds `DEFAULT_STALL_PATIENCE=3`, `DEFAULT_OSC_STD_THRESHOLD=0.30`, `DEFAULT_P_SIG=0.05`, `DEFAULT_DIV_MARGIN=0.10`. **Recommends a minimum of 6 iterations for trend significance**; at n≤8 the t-test needs \|t\|>3.18 and biases toward STALLING. Benchmark is a real runnable harness (`loopgain-bench`, 2,000 paired trials, $27.05→$1.94) but its README states the saving varies **78–96% by workload** — cite the range, never the single 92.8% figure. | **Statistics rejected.** Our signal is a small, often-near-zero integer count from a non-deterministic judge; log10 of such a series has near-zero variance and unstable slopes. Decisively: it needs ~6 rounds to speak, and we intend to stop around round 3. **Its five-state taxonomy is adopted as judgment vocabulary only.** |
| **Semantic / plateau early-stopping** | *Semantic Early-Stopping for Iterative LLM Agent Loops* (arXiv 2606.27009, **preprint, 2026-06-25**): halts on cosine distance between consecutive draft embeddings falling below ε. Judge-free variant cuts 38% of tokens at indistinguishable quality (ΔIS=−0.004, p=0.81) on HotpotQA, N=60. | **Rejected — wrong failure shape.** It detects a loop repeating itself. Our nine rounds each produced genuinely different content that was equally defective; the detector would never fire. The paper also self-flags that "the benchmark under-exercises iteration." |
| **Capture-recapture remaining-defect estimation** (two arms' overlap → estimate of undetected defects; classic software-inspection technique, IEEE) | Its load-bearing assumption is that the two detectors are independent. *Nine Judges, Two Effective Votes* (arXiv 2605.29800, **preprint, 2026-05-28**) measures 9 heterogeneous judges yielding only **n_eff ≈ 2.0–2.5 effective independent votes**, with panel accuracy 8–22pp short of true-independent voting. | **Rejected.** The independence premise fails on LLM panels, and a high overlap reads as "nearly exhausted" under capture-recapture but "the arms are echoing each other" under n_eff — opposite conclusions from one number. **The overlap count is retained as an independence diagnostic instead**, per that paper's own recommendation to report n_eff and treat `n_eff/k < 0.5` with caution. |
| **Cross-model-family review panel** (to break correlated error modes) | Same paper: same-family pairs φ=0.437 (OpenAI×OpenAI) and 0.435 (Meta×Meta) versus a **cross-family mean of φ=0.389** — barely different; the three most-correlated pairs are all cross-family (Claude×Gemini φ=0.603); and restricting to one judge per family **lowers** n_eff to 1.93. The widely-repeated "cross-model review finds 40–60% more issues" figure traced only to marketing pages and is **not used**. | **Rejected — no measured benefit.** Cross-family does not reliably reduce correlation and may reduce effective independence. Related peer-reviewed context, retained as caveats rather than as drivers: Panickssery et al. (**NeurIPS 2024**) establish that an evaluator recognises its own generations (GPT-4 ≈73.5%) with a causal link to self-preference, but at the level of a model recognising *its own text*, not a family-level claim; Kim et al. (**ICML 2025**, arXiv 2506.07962) find model pairs agree ~60% of the time when both are wrong (chance ≈33%) and that *more accurate* models have *more* correlated errors, with same-provider pairs only modestly higher (+0.066/+0.076). |
| **Raw reported-findings count as the trajectory signal** | **SWR-Bench** (arXiv 2509.01494, **FSE, peer-reviewed**; 1,000 real GitHub PRs across 12 Python repos, human-verified ground truth): the best LLM code-reviewer configuration reached **precision 16.65%** — roughly 83% false positives. Real-world corroboration: curl's maintainer reports the confirmed-valid rate on bug-bounty submissions falling below 5% under AI-report volume [journalistic, not peer-reviewed]. | **Rejected as the signal.** Retained as a recorded field for diagnostics. **The signal is the surviving/adjudicated count.** Note on a figure that did *not* survive checking: *Refute-or-Promote* (arXiv 2604.19049, **single-author preprint**) reports killing ~79% of 171 candidates, but the method section shows this is **deliberate over-generation followed by internal filtering, not a measured false-positive rate of a single-pass reviewer**, and it reports **no single-pass baseline**. It must not be cited as evidence about reviewer precision. |
| **Fagan-style formal re-inspection framing** | A decision already recorded in this repo: `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md:284` — "Its value is the role structure (moderator / reader / author / formal rework); loom has none of those. Borrowing the name would manufacture the impression of a control we do not have." | **Mechanism kept, name rejected.** The clause is named for bad-fix injection, not Fagan. |
| **Perspective-Based Reading role rotation between rounds** | Basili et al. [primary; replications contested — 2006, Laitenberger 69% vs 70%]. | Rejected, same grounds as the (P3+P4) brief recorded: dominant variable is likely task expertise. |
| **Append-only / supersede discipline for settled prose** | Architecture Decision Records (Nygard, 2011): an accepted ADR is never edited; revisiting it means `Superseded by NNNN` plus a new record — "the fact that you do not edit accepted ADRs is what makes the collection trustworthy." Nygard: "Large documents are never kept up to date. Small, modular documents have at least a chance at being updated." This repo's own `docs/loom/memory/` charter already works this way. | **Adopted, and moved to round 1** rather than triggering at a cap. The audit's own "record, not rewrite" terminal-round rule is this pattern arrived at independently. |
| **Diátaxis-style restructuring of the corpus** (separate tutorial / how-to / reference / explanation) | diataxis.fr (primary): "mixing types is the most common cause of confusing documentation"; boundaries are protective. The audit's §3.4 reviewer independently diagnosed narrative-adjacent-to-prescriptive text as the cause of its recurring contradictions — on round 6 of 9. | **Adopted as a judgment criterion only** (is this passage narrative or prescriptive → supersede or edit in place). Corpus restructuring is **out of scope**: Diátaxis is designed for product documentation and has no quadrant for a dated investigation record, and this repo's real gap is that its *existing* jurisdiction table (`docs/loom/memory/README.md`) is prose nothing reads — a different taxonomy would not be an enforced one. |
| **ODC-style defect classification** | Orthogonal Defect Classification (IBM, early 1990s): classify by type + trigger, analyse the distribution to prevent recurrence. | **Adopted in one clause**: same defect type appearing twice → sweep the population, not the instance. Full classification machinery out of scope. |

### The bad-fix injection baseline: honestly unmeasured

The first draft of this brief opened by comparing our measured ~67% round-level
self-injection against Capers Jones's *The Economics of Software Quality* (2011)
figures of ~7% average and up to ~25% for high-complexity unstructured code. That
comparison has been demoted to historical context, because those are **human
reviewers fixing human-written code, fifteen years ago**.

**No published study measures an LLM-era analogue of Capers Jones's
bad-fix-injection rate on a comparable population, and none compares human-era to
LLM-era rates directly — the honest baseline is "unmeasured". The nearest
fragments are structurally different metrics and cannot be cited as a like-for-like
comparison to our 67% round-level figure:**

- **ICSE 2026** (Wang, Pradel & Liu, *Are "Solved Issues" in SWE-bench Really
  Solved Correctly?*, **peer-reviewed**): "Regressive Patches" — patches that
  satisfy the issue but break unrelated functionality — at **11/77 (14.3%)** of a
  manually inspected sample of *suspicious* patches; as a fraction of all
  plausible patches this is roughly 4%, a number the paper does not state
  directly. Separately, 7.8% of plausible patches fail against all developer
  tests, extrapolating to an 11.0% incorrect rate that inflates reported
  resolution rates by 6.4 points — this is the paper's RQ4 body and its ICSE '26
  camera-ready abstract; the arXiv preprint's own abstract (v2) states 6.2
  instead. Both numbers are the paper's own across its two live versions, not a
  transcription error, so a future editor should not "correct" one to the
  other. Note that "wrong fix" and "newly injected defect" are different
  metrics; the literature routinely blurs them.
- **ASE 2026** (Huang et al., *Regression Accumulation in Multi-Turn LLM
  Programming Conversations*, **peer-reviewed**): 542 tasks × 6 models × 8 turns;
  **40–73% of tasks lose previously-correct behaviour over the conversation**;
  the best model ends at a 75.8% Regression Pass Rate by turn 8. This is the
  closest *shape* in the literature — multi-turn accumulated degradation — but the
  mechanism differs (feature-accretion turns breaking prior-turn code, not a
  repair loop whose fix is what the next round must repair).
- **Not cited**: an April 2026 preprint's ">15% of AI commits introduce ≥1 issue"
  figure is 89.3% static-analysis code smells and only 6.0% correctness — it
  blurs style with defect.

**Our 6-of-9 measurement is therefore the primary evidence for this slice, and it
is n=1 branch.** The brief must not claim industry backing for the phenomenon it
is built to address.

**My take**: ledger as instrument + prose rule that consumes it + bad-fix
re-check in the reviewer contract; no numeric cap. **Why**: the mint call site
already fires on every failing round and discards the data, so the instrument
costs no new orchestrator discipline; 2607.01641's diagnosis says bounds must
live where the feedback is created; and the prose-only alternative has a recorded
in-repo failure on this exact practice. **Conditional reversal**: if the ledger
cannot be made stable across rebase/amend without special-casing (Open Question
1), ship the bad-fix re-check alone and record the ledger as unbuilt — a wrong
round number is worse than no round number.

## Decision

Ship the round ledger in `loom_gate_markers.py`, the round-3 trajectory
surfacing plus judgment-based escalation in `requesting-code-review` and
`finishing-a-development-branch`, and a bad-fix re-check rule appended to
`_reviewer-discipline.md` regenerated through `distribute.py`.

Do **NOT** build: any numeric round cap; a new discipline file; any statistical
convergence detector; capture-recapture estimation; a cross-model-family panel;
any change to `RALLY_CAP` in `loom-pipeline` (documented intent for unattended
runs — `driver_20_runstation.js:35-40`); any new reviewer agent or review
dimension; any change to what mints a *pass* marker or to `git-guard.py`'s gate
logic; any change to SDD's per-task 3-round cap or `writing-plans`' 2-round cap.

## Complexity-critique verdict (2026-07-30)

Mindset loaded: `mindset-design-is-taking-apart` (Hickey, *Simple Made Easy*,
2011) — good design is measured by what you successfully kept separate.

- **Q1**: the marker and the ledger are separate concerns and must compose, not
  braid (constraint recorded in §Smallest End State). A smaller alternative was
  identified and considered — ship only the bad-fix re-check, ~15 lines against
  ~200 — and **rejected by the user on the instrumentation argument**: without the
  ledger, the causation question below stays unanswerable.
- **Q2**: strictly more code. ~60 lines of script, ~80 lines of tests, ~15 lines
  of reviewer-discipline text (times three generated injections), ~120 words
  across two SKILL.md files. **Nothing is deleted from the codebase.**
- **Q3**: the one deletion available was the hard round-cap number — the only
  element with no evidential basis, and a second control for a job one control
  covers. **Deleted, per user decision.**
- **Verdict: PROCEED-WITH-CAVEAT.** Named trade-off: **~200 lines and zero
  deletion, bought to obtain the first mechanical record of a loop that has twice
  run unbounded.** The justification is instrumentation, not braking.

## Causation, unresolved (load-bearing context for the plan)

Whether this failure mode is new, and whether our own mechanism changes caused
it, **cannot be determined from what this repo recorded.** Stating the candidates
matters because the plan should not encode a causal story it cannot support.

Candidates, all coinciding within three weeks of both pathological loops:

1. **Review panel became the default in loom-code 0.26.0 (2026-07-06)** — one
   `code-reviewer` became two dispatched in parallel, with the gate verdict taken
   from the *union* of both arms. Combined with SWR-Bench's 16.65% precision,
   doubling arms plausibly doubles false-positive findings, and more findings mean
   more remediation and more injection surface. Both pathological loops (07-27,
   07-28) postdate this.
2. **Two check-adding releases immediately before and between the two loops** —
   0.39.0 (plan-stage fact grounding, 07-27) and 0.40.0 (citation checking +
   docs-only review mode, 07-28).
3. **Session model changes** — 0.26.0's own entry states "Reviewers still inherit
   the session model (no pinning)", so reviewer strength tracks the session
   model. Kim et al. (ICML 2025) find *more accurate* models have *more*
   correlated errors, which would both surface more findings and reduce effective
   panel independence. **No dated record of session-model changes exists in this
   repo**, so this candidate is neither confirmable nor falsifiable here.
4. **Artifact type** — both pathological loops ran on documentation-heavy work.
   Audit §3.1's own argument turns on documents having no tests, and §7 states
   plainly that whether the loop fails the same way on code is untested.

Weak supporting probe, reported with its confound: plan files mentioning
`NEEDS_REVISION` rose from 4/26 (May) and 6/52 (June) to 18/85 (July), and
explicit round-number mentions are absent across all 52 June plan files while
common in July. **This is heavily confounded** — round-counting only became a
documentation practice in late July, and most July mentions sit inside the audits
that constitute this very investigation. Counter-datum: `writing-plans`' 2-round
cap was itself breached and explicitly authorised on 2026-07-27, so the capped
loop was straining in the same window.

**Conclusion for the plan**: treat causation as open. Do not write a causal claim
into any shipped artifact. The ledger exists partly so this question is
answerable the next time it is asked.

## Out of Scope

- The (P5+P6) slice: 0.39.0's artifact-type scope limit, the "prose naming ≠
  installing" memory entry, git-memory's compose-commit jurisdiction question,
  and the recurrence-count rider on `squash-dialog-can-drop-entire-pr-body`.
- Whole-artifact vs diff review scope (§3.1) and the docs dimension set (§3.3) —
  both shipped in 0.40.0.
- Best-so-far rollback (reverting remediation commits to the lowest-defect
  round). Highest theoretical value — *Semantic Early-Stopping*'s oracle beats
  every practical policy by +0.115 Information Score (p≈4e-11) and the paper
  reframes the open problem as "which round is best" rather than "when to stop" —
  but automating the pick is unsolved. This slice records enough to enable a
  later human or mechanism to choose; it does not choose. BACKLOG.
- Diátaxis-style corpus restructuring; deriving doc claims from code so facts are
  unwritable by hand. BACKLOG.
- A mechanical gate on rule *count* rather than file size. The only benchmark
  found is IFScale (arXiv 2507.11538, **2025-07** — a year old, pre-current model
  generation), which measures simultaneous *instruction count* (best models 68%
  accuracy at 500 instructions), not file length. This repo's `MEMORY.md` 24.4 KB
  and `rules/*.md` 6 KB soft caps therefore guard the wrong axis. BACKLOG.
- CI gates this repo lags on, found in community skill repos: a blocking
  structural-conformance check, and mechanical enforcement that a content change
  bumps the plugin version (this repo currently relies on a memory entry learned
  from PR #539 → #540). BACKLOG.
- Detecting that a rule has become *false* rather than merely long. Six agents
  found **no such mechanism anywhere** — not in Anthropic's guidance, not in
  `anthropics/skills` (which ships no CI at all), not in any community collection.
  Building one would lead the field, not close a gap. BACKLOG as an R&D bet.
- The large-doc/small-diff A/B re-test still open from the 0.40.0 close-out.
- Repairing PR #627's dropped squash body (decided against last session).

## What Becomes Obsolete

- The operator's manual round-counting that ended the nine-round loop — replaced
  by the script's trajectory print.
- Audit §3.2 changes status from PROPOSAL to shipped (the audit file stays as a
  dated observation; the resolution is recorded here and at close-out).
- `finishing-a-development-branch/SKILL.md:113-115`'s unqualified "digest
  silently" contract — it gains an explicit exception at round 3 rather than being
  deleted. **This is an edit to a load-bearing rule**: per
  `docs/loom/memory/core-rule-removal-needs-plugin-wide-sweep.md`, grep the whole
  plugin (router card, agent contracts, three-language READMEs, PRODUCT-SPEC /
  ROADMAP) for restatements of the digest-silently rule before calling it done.

## Open Questions

1. **Ledger lifetime across rebase / amend.** Existing markers bind content via
   `base_sha` + `patch_id`. Rounds are *process* history, so binding them the same
   way would reset the count on every amended fix — exactly the situation the
   counter exists to observe. Leaning: key on branch name only, record `head_sha`
   per entry for audit, never reset. Needs an explicit decision because it
   determines the test matrix, and because it is the conditional-reversal trigger
   named in §My take.
2. **How `findings_surviving` is determined.** The signal depends on it. Candidate:
   findings that produced a remediation edit before the next round's dispatch,
   counted by the orchestrator at re-dispatch time. Needs a definition that a
   weak executor cannot fudge, per
   `docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md`.
3. **Does the bad-fix re-check apply to `spec-reviewer`?** It carries
   `_reviewer-discipline.md` (all three agents are in
   `AGENT_REVIEWER_DISCIPLINE_TARGETS`) but returns a binary verdict and reviews
   against a spec rather than a prior fix. Leaning: yes, uniform — the injected
   block is verbatim by design and a carve-out would need its own mechanism.

## Design-side on-ramp

N/A — process tooling for loom-code itself; Axis 0 negative guard (incremental,
non-product-shaped) applied.
