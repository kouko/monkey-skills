# Design brief: loom living-spec index (two-altitude + generated index + drift gate)

Status: **DESIGN CONVERGED** (5-round adversarial coherence audit; design-level issues closed,
remainder is impl wiring — see §Open questions). Ready for brainstorm→plan once the user
greenlights build. Date: 2026-06-22 (decisions); coherence-audited 2026-06-23 (5 rounds).

> **Coherence audit (2026-06-23, iterative)**: independent adversarial reviewer, two passes.
> Round 1 → HAS-CONTRADICTIONS (2 BLOCKER + 5 CONCERN + 1 NIT); resolved inline as `[audit:N]`.
> Round 2 verified all 8 genuinely closed, but found 5 NEW issues introduced by the round-1 fixes
> (2 BLOCKER F1/F3 + 2 CONCERN F2/F4 + 1 NIT F5); resolved inline as `[audit2:Fn]`.
> Round 3 → COHERENT-WITH-FIXES (0 BLOCKER; 3 CONCERN + 2 NIT, one cluster from relocating work to
> finishing); resolved inline as `[audit3:P2-n]`.
> Round 4 → HAS-CONTRADICTIONS (1 BLOCKER F-1: R3 over-corrected the gate event to post-merge
> `push:[main]` = post-hoc alarm not a blocking gate; + 1 CONCERN + 1 NIT); resolved inline as
> `[audit4:Fn]`. Design SUBSTANCE has been stable since R1; churn is confined to CI-event wiring.
> Round 5 → COHERENT-WITH-FIXES; **DESIGN CONVERGED** — F-1/F-2/F-3 closed, the 3 highest-risk
> new-contradiction probes (PR-timing, RED-phase structural inversion, writer/verifier circularity)
> all resolved in the design's favor; the only open item is 1 IMPL nit (bind the gate to a
> finishing/ready signal, not bare `not-draft`). Convergence: R1=8 → R2=5 → R3=5 → R4=3 → R5=0
> design issues. Audit loop stopped (further rounds would only churn impl wiring).

## Problem

loom- has the **GENERATE half** of an OpenSpec-style mechanism (loom-spec emits a one-shot
change-folder: proposal.md with USM/OOUX/path-matrix + `specs/<capability>/spec.md` delta with
Requirement/Scenario; validated by `validate_spec_output.py`; consumed once by `writing-plans`).
It is **missing the back half**: no persistent "current system behavior" truth that accumulates
across changes, and no lifecycle that lets the next change **build on / diff against** prior
state. The pipeline is **single-cycle** — each feature starts from a fresh seed.

Naively adopting OpenSpec's missing half (a prose `specs/` source-of-truth) is wrong for loom:

- **loom's truth is tests (TDD iron law)**; a prose truth = a **second SSOT** that drifts.
- **Pure prose truth rots** ("just more docs" — verification-is-the-bottleneck critique).
- **Pure test-as-spec also fails**: tests are point-samples → (a) too **fragmented** to form a
  systematic model, (b) carry **WHAT not WHY**. (Textbook limit of executable specs.)

So the question is neither "prose vs tests" nor "separate vs merge" — both are false binaries.

## Decision (core)

**Verification-LEADS, TWO-ALTITUDE living-spec + GENERATED index + DRIFT GATE, with the
generate→consume loop CLOSED.** Tests stay the executable truth; intent lives in prose homed by
altitude and holds ONLY what tests structurally can't; the systematic view is a build artifact.

**Precise drift claim `[audit:1]`** (the headline, stated honestly):
- The **index cannot drift from the tags** — it is a pure projection, regenerated.
- **intent↔behavior drift is detectable + CI-gated, NOT eliminated.** There is an irreducible
  residual rot surface (the prose "why"), bounded but real (see §Residual rot surface).
  We do **not** claim zero-drift; no shipped SDD tool achieves it.

**Rejects:** (1) prose `specs/` as the source of truth; (2) intent as **free-text** comments in
tests; (3) a **hand-maintained** index (a generated-then-committed index is NOT this — see
§AUTHORED vs DERIVED).

### Blueprint (closed loop)

```
 AUTHORED = humans / loom-spec maintain      DERIVED = CI regenerates
 -----------------------------------------------------------------------

   [ persisted truth:  TOP/MID docs  +  INDEX ]
        |  (B1) read as PRIOR-STATE, point-don't-copy  [audit:2]
        v
   [ loom-spec GENERATE next change ]   <- diffs against / builds on current truth
        |  change-folder
        v
   [ TOP model doc ]   cross-cutting invariants / object state machines / out-of-scope
        v
   [ MID per-capability readme ]   intent / why / scope   (human-read, slow-change)
        ^   @req binds leaf to intent
        |
   [ LEAF tests ]   @req (+ @invariant-ref) + assertions   == verification = TRUTH ==
        |  record git-ref PER TEST-FUNCTION  [audit2:F5]
   = = =|= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  CI
        v   regenerate: extract @req --(loom-spec namespace)--> capability  [audit:3]
   [ INDEX ]   capability -> req -> test   (committed; CI asserts == fresh regen)
        |
        v
   [ DRIFT GATE ]   structural = FAIL ;  git-ref semantic = WARN
        |
        +--> the persisted truth (top of diagram) feeds the NEXT loom-spec cycle
```

| Altitude | Holds | Resolves |
|---|---|---|
| TOP model doc | cross-cutting invariants, object state machines, out-of-scope | "too fragmented / no systematic model" |
| MID per-capability readme | intent / why / scope | "no spec intent (WHY)" |
| LEAF structured tags (`@req`, `@invariant-ref`) | the binding test↔intent | the correct form of "annotate intent in tests" |
| DERIVED index | generated queryable tree | the "knowledge index" problem (build artifact) |
| DRIFT GATE | structural=FAIL, git-ref=WARN | linkage drift (hard); intent drift (soft signal) |

## Locked decisions

| # | Decision |
|---|---|
| **B1** `[audit:2]` | **Close the loop.** loom-spec's seed intake **reads the persisted TOP/MID + INDEX as prior-state context** (point-don't-copy, the #406/#442 seam contract). The next change diffs against / builds on current truth — closes BOTH halves of the gap (audit/query AND build-on), not just audit. **Well-founded base case `[audit2:F2]`**: prior-state intake is **additive and may be empty** — a net-new capability reads whatever exists (possibly nothing) and the layers are populated forward by that same cycle ("fans net-new only", the #406 semantics). No cold-start deadlock; an empty index is never treated as authoritative. |
| **B2** `[audit:3]` | **capability is DERIVED, not tagged.** Drop path-inference entirely (it had no stable mapping across arbitrary-layout repos). The test carries `@req` (+ optional `@invariant-ref`) **only**; capability is resolved by `@req → loom-spec namespace` lookup (the namespace already encodes capability→req via `specs/<capability>/`). **Single authority = loom-spec namespace**; deterministic in any repo layout. **Namespace location `[audit2:F4]`**: the `@req → capability` namespace is a **same-repo, same-commit** artifact — the change-folder's `specs/<capability>/` tree — so `@req` always resolves against the PR's own tree (no cross-plugin/cross-repo sync timing). A `@req` absent from that tree is genuinely dangling (FAIL), never "not yet synced". |
| #1 | Tag mechanism = **structured comment/docstring convention + stdlib parser**. Language-agnostic, zero-dependency (no third-party lib injected into target repos), co-located. Rejected: framework annotations (per-language + intrusive), sidecar manifest (re-introduces linkage drift). Tags at **test-function** granularity. Syntax: `# @req: REQ-OVD-1` (one per line). Validation runs at CI-build-time, not test-runtime. |
| #2 `[audit3:P2-1]` | Index = **committed `docs/loom/INDEX.md` markdown tree** + a CI "regenerate and assert committed == fresh-regen" gate (reuses `verify-drift.py` byte-identity pattern). Tree: capability → req → [linked tests + git-ref + status]. `## Orphans` section. One root file; split per-capability only when it grows. JSON sidecar = YAGNI. **Trigger `[audit4:F1]`**: the `committed == fresh-regen` assertion is a **required PR status check evaluated on the PR head AFTER finishing regenerated the index** — it runs **post-regen, pre-merge**, so it **BLOCKS** a bad merge (NOT post-merge `push:[main]`, which would only alarm after the merge already landed). Mid-branch staleness is a non-issue because finishing finalizes the PR with a fresh index (early-PR workflows gate the check behind not-draft). Exact GitHub mechanism (required check / merge queue) = impl detail. |
| #3 `[audit2:F3]` `[audit3:P2-2]` `[audit4:F1,F2]` | Drift gate (in `loom-code-ci.yml`), tiered by **when it is safe to run**, not by index-dependency. **structural = hard FAIL on EVERY push** (PR + main): dangling `@req`, malformed tag — need no index, RED-phase-safe. **merge-boundary checks** (RED-phase-**unsafe** until finishing): the `active` req with 0 passing tests = FAIL, and the index `committed==regen` assertion (#2). These run as **required PR status checks on the PR head AFTER finishing** (post-regen, pre-merge) so they **BLOCK** the merge — NOT on req emission, NOT mid-RED (a freshly-specced `active` req legitimately has 0 tests during RED; failing it then inverts the iron law), and NOT post-merge `push:[main]` (which would only alarm after a bad merge landed). [The `active`-coverage check needs `@req` resolution + test results, not the regenerated index — it is merge-pinned for the RED-phase reason, not because it reads the index.] **semantic git-ref drift = WARN**. Matches loom's block-vs-note philosophy. |
| #4 | TOP/MID cut rule: **"remove this capability — does this content get deleted?"** YES→MID (its why/scope/out-of-scope/blind-spots). NO/survives→TOP (object state machines, invariants [= `@invariant-ref` targets], full USM journey, path×edge / cross-object matrices). provenance = metadata tag on the req. |
| #5 `[audit2:F1]` | **Lifecycle = no archive ceremony.** The index is a projection → "updating" it = regenerate. **Writer: `INDEX.md` is regenerated + committed ONCE per branch by the orchestrator at `finishing-a-development-branch` — NOT per-implementer.** The index is repo-wide, so a per-implementer regen under parallel SDD waves would merge-conflict on the generated file and reflect only a partial tree; this follows loom's existing "orchestrator commits, implementers don't" rule. CI verifies (== fresh regen) as a **required PR check on the post-finishing PR head** (#2/#3 `[audit4:F1]`) — regen (at finishing) precedes the verify/coverage checks (on that same PR head, pre-merge), so they are ordered (not racing) and they **block** a bad merge rather than alarming after it. Human gate = TOP/MID intent changes go through normal PR review (they're files in the diff). REMOVED → test deleted, `@req` removed, MID updated → regen drops it; audit lineage = git history; no `archive/` dir. |
| #6 | Ownership = **split by station** (mirrors the #406/#442 authorship split). loom-spec owns the persistent intent layer (TOP/MID) + the `@req`/`@invariant` ID namespace + a validator for it. loom-code's implementer DoD gains "tag the test with its `@req`" (index regen is the orchestrator/finishing step, not per-implementer — see #5 `[audit2:F1]`). index generator + drift gate live in `loom-code/scripts` + `loom-code-ci.yml`. **Seam `[audit3:P2-3]`**: loom-spec **authors** the `specs/<capability>/` tree (the namespace); loom-code's generator **reads it in-tree at the same commit** — there is **NO synced cross-plugin registry / namespace-handoff artifact** (Open-Q3 RESOLVED). This is **consistent with the #406 authorship split** (loom-spec authors, loom-code reads) but is **NOT** the #406 *point-don't-copy* pattern — there is no boundary to point across, just same-tree file parsing. (The genuine point-don't-copy is **B1's prior-state intake**, where loom-spec points at persisted layers without copying them.) New `loom-trace` plugin = YAGNI (defer). |

## Tag + status schema (locked)

Leaf test tags (machine-extractable by a stdlib parser; co-located comments, NOT free-text prose):

- `# @req: <REQ-id>`           — the requirement this test satisfies (resolves to a capability
  via the loom-spec namespace; **no `@capability` tag** — derived) `[audit:3]`
- `# @invariant-ref: <inv-id>` — (optional) a cross-cutting invariant (defined in a TOP model
  doc) this test guards

**git-ref granularity `[audit2:F5]`**: recorded **per test-function** (the commit that last
touched the function body), shared across that function's multiple `@req` bindings.

Requirement intent-status (set by loom-spec in the intent layer) `[audit:8]`:

- **`active`** (default) — meant to be verified now. `active` + 0 passing tests = **FAIL only as a
  post-finishing, pre-merge required PR check** (by then RED must have gone GREEN); during the TDD
  RED phase a just-specced `active` req legitimately has 0 tests and is **NOT** failed
  `[audit2:F3]` `[audit4:F2]`.
- **`deferred`** — explicitly aspirational / future. `deferred` + 0 tests = **surfaced** (shown
  in the index as "inspirational"), **not** failed.
- (Tessl mapping: a verified `active` req = *canonical*; `deferred`/unverified = *inspirational*.)

MID readme holds intent/why/scope and **MUST NOT restate behavior a test owns** (restated
behavior is the rot surface). TOP doc holds object state machines + cross-cutting invariants
(`@invariant-ref` targets) + system-level out-of-scope.

## AUTHORED vs DERIVED `[audit:5,6]`

- **AUTHORED** (humans/loom-spec maintain): TOP model docs, MID per-capability readmes, LEAF
  tests + their `@req`/`@invariant-ref` tags.
- **DERIVED** (mechanically regenerated; hand-editing the content = defect): the `INDEX.md`
  tree, the drift-gate report.
- **Why the committed INDEX.md is not the rejected "hand-maintained index" `[audit:6]`:** its
  bytes are **generated**, not authored; the implementer's regen step is **mechanical** (run the
  generator), and CI asserts `committed == fresh regen` so a stale/edited index FAILs. The
  rejection targeted a *human-authored second copy of truth* — this is a verified projection.

## Anti-patterns to forbid `[audit:6]`

- **Free-text intent prose in test comments** — drifts AND doesn't compose. (Distinct from the
  permitted **structured binding tags** `@req`/`@invariant-ref`, which carry *binding, not
  intent*, and DO compose into the index.)
- **MID/TOP prose that restates behavior** the tests already assert (the rot surface).
- A **hand-authored** index or any second human-kept copy of behavior.

## Residual rot surface (honest limit) `[audit:1,7]`

The intent↔behavior **non-overlap rule** ("MID MUST NOT restate behavior") is enforced by
**human PR review, not by a CI gate** — the drift gate checks git-ref linkage, not whether prose
crept into restating behavior. So the jurisdiction boundary is author-discipline + review, and
the prose "why" carries an **irreducible (but small, slow-changing, human-reviewed) rot risk**.
This is the residual surface; we state it rather than claim airtight.

**Optional future hardening** (deferred): a lightweight lint flagging MID/TOP prose that contains
assertion-like / RFC-2119 behavioral MUST statements duplicating a test name.

## Industry grounding (what we borrowed)

All shipped living-documentation systems converge on multi-altitude + generated-index; none put
cross-cutting intent as free leaf comments.

- **Serenity BDD** — closest blueprint (verification-leads): capability→feature hierarchy, a
  **readme.md per container level** homes intent, leaf tests annotated, **Requirements tree
  generated**. ([living documentation](https://serenity-bdd.github.io/docs/reporting/living_documentation))
- **Kiro** — drift detection via **git-ref in spec metadata**; diff files-touched-since → warn.
  ([Kiro #9435](https://github.com/kirodotdev/Kiro/issues/9435))
- **Tessl** — "**tests become part of the spec, turning an inspirational spec into a canonical
  spec**" — authority from test-binding, not prose. ([docs.tessl.io](https://docs.tessl.io/use/spec-driven-development-with-tessl))
- **OpenSpec** — archive = strict-ordered delta apply + re-validate; borrow the ordering
  discipline if/when index merge needs it. ([DeepWiki](https://deepwiki.com/Fission-AI/OpenSpec/6.6-archive-command))
- **Concordion / Rust doctest** — the *intent-leads* alternative (not chosen; documented fallback
  if loom ever pivots to spec-as-source).

No silver bullet: even Tessl ("drift eliminated by construction") keeps a reconcile step.

## Open questions (impl-level; no longer block the design)

1. **Tag parser**: exact stdlib parser shape (regex vs light-AST) + which comment syntaxes per
   language (`#`, `//`, `--`).
2. **Index generator output**: exact markdown-tree format + the `git-ref`/status columns;
   one root file vs root+per-capability.
3. ~~Namespace persistence~~ — **RESOLVED** by B2 `[audit2:F4]`: the namespace is the change-folder's
   same-commit `specs/<capability>/` tree (no separate registry). Remaining impl detail: the exact
   on-disk query shape loom-code's generator parses.
4. **Prior-state intake (B1)**: how loom-spec's seed step references the persisted layer
   (which sections, how surfaced to the spec-expansion phases).
5. **Drift-gate WARN ergonomics**: acknowledge/re-bind flow; how a legit behavior change clears
   the WARN.
6. **Gate-fires-after-finishing binding `[audit5:Finding1]`**: bind the merge-boundary required
   checks to a **finishing-emitted ready signal** (the regen commit / ready-for-review transition),
   NOT bare `not-draft`, so "PR is non-draft" provably implies "index was regenerated" — closes the
   early-non-draft-PR escape hatch. Build-phase CI wiring; not a design change.

## Out of scope

- spec-as-source pivot (Concordion/Tessl intent-leads) — documented fallback only.
- Back-migrating existing one-shot change-folders into the new structure.
- OpenSpec CLI dependency (file-format-only, per parked v0.2 items).
- The optional MID-prose-restates-behavior lint (deferred hardening).
</content>
