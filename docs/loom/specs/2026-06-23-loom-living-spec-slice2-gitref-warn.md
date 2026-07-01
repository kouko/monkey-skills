# Brief: loom living-spec — slice 2 (D) git-ref drift WARN tier

Status: **BRAINSTORM COMPLETE** — ready for `writing-plans` once the user signs off
the Axis 1 / Smallest-End-State / Out-of-Scope checkpoint. Date: 2026-06-23.
Parent design: `docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md`
(decision #3 "semantic git-ref drift = WARN"; audit2:F5 "git-ref per test-function").
Slice plan: this is **D**, chosen to ship FIRST (independent of E/F/G) per the
between-slices triage (D / E+F / G+CI).

## Problem

(Axis 1 — JTBD) Slice 1 gave loom-code a CI gate that catches **structural** defects
in the living-spec linkage — a dangling `@req` (id not in the namespace) or a
malformed tag — and asserts the committed index is byte-identical to a fresh
regeneration. But the gate is **blind to semantic drift**: a test whose body logic
changed while its `@req` binding was never re-affirmed. The test still *claims* to
verify `REQ-X`, but the behavior it asserts may have moved away from what `REQ-X`
means, and nobody was prompted to re-check.

The job: **"when a test's logic drifts from the requirement it claims to verify,
give the maintainer a low-friction nudge to re-confirm the binding — without
blocking the merge."** WARN, not FAIL (loom's block-vs-note philosophy: hard gates
for provable defects, soft signals for judgment calls).

## Users

(Axis 2) loom-code maintainers / implementers working in a repo that has adopted
slice-1's `@req` tags and runs `loom-code-ci.yml`. They refactor tests over the life
of the codebase; a behavior change can silently decouple a test from its stated
requirement. Job story: *When I change a tagged test's logic across commits, I want
CI to flag that the test moved without its `@req` binding being re-touched, so I can
decide whether the requirement still holds — without the build going red on what may
be a benign refactor.*

## Current State Evidence

- **Forward (entry → behavior):** the gate entry is
  `check-living-spec-index.py:29 find_structural_violations(tag_records, malformed,
  namespace)` — **FAIL-only** today (dangling + malformed). Parser entry is
  `living_spec_tags.py:41 extract_tags(text)` → records `{test, reqs,
  invariant_refs}` — **carries no git-ref**.
- **Reverse (SSOT ownership):** these are plain scripts under `loom-code/scripts/`,
  not synced from any distribute/sync SSOT — D extends them **in place**. Slice-1
  deferred all real-repo wiring: `check-living-spec-index.py:74 main()` runs over
  **empty inputs and exits 0**; the pure functions are exercised only by unit tests.
- **Error (existing failure paths):** `living_spec_tags.py:77 find_malformed_tags`
  + the DANGLING branch (`check-living-spec-index.py:50`) are the **FAIL** paths. D
  adds a **WARN** path that must be reported **separately** — never conflated with,
  short-circuited by, or able to flip, a FAIL.
- **Data (contract / shapes):** record shape `{"test","reqs","invariant_refs"}`
  (`living_spec_tags.py:54`); index tree capability→req→test
  (`living_spec_index.py:48`). **Seam-test constraint** — `test_living_spec_e2e.py:57`
  asserts the *exact* dict `{"test":"test_happy","reqs":["REQ-1"],"invariant_refs":[]}`
  is `in tags`. Adding a `git_ref` key to that record would break this assertion. ⇒
  **git-ref must live in a SEPARATE structure**, not inside `extract_tags` output.
- **Boundary (external I/O):** the actual git query (`git log -L` for a function
  body / a tag line's last-touching commit) is the external boundary. Slice 1 kept
  all git / real-repo I/O **out of the pure functions**. D keeps the **comparator
  pure** (refs injected as inputs) **AND** (thick slice) adds a **thin git adapter**
  that computes those refs from a real tree, tested against a throwaway temp git
  repo — so the layering (pure core / I/O at the edge) is preserved while D still
  runs end-to-end. This adapter is the git-ref portion of what the capstone slice
  would otherwise have wired; the capstone keeps the *rest* (index regen at
  finishing, the required PR checks).

Evidence paths: `loom-code/scripts/living_spec_tags.py`,
`loom-code/scripts/living_spec_index.py`,
`loom-code/scripts/check-living-spec-index.py`,
`loom-code/scripts/test_living_spec_e2e.py` (all on `origin/main` @ `1e65a222`).

## Decision

Build a **WARN-tier git-ref drift check, model M1 (self-contained, fully derived)**,
**THICK slice** — runs end-to-end on a real repo at merge (not deferred plumbing).

- **Comparison (M1):** for each binding, compare the **test-function-body's last-
  touching commit** against the **`@req` binding-line's last-touching commit**. If
  the body was touched *after* the binding line (body-ref is newer) → the test logic
  moved without the binding being re-affirmed → emit **WARN**. Re-touching the `@req`
  line (or editing body + binding in the same commit) re-affirms it → clears.
- **Why M1:** keeps D **independent of E** (needs only slice-1's `@req` tag + git, no
  intent-doc layer) → honors the "D first" slice order; **fully derived** (no new
  authored baseline field, consistent with the parent brief's AUTHORED-vs-DERIVED:
  the drift report is DERIVED); lightest re-affirmation ceremony.
- **Shape (3 layers, inner→outer):**
  1. **Pure comparator** — `find_gitref_drift(bindings) -> list[str]`, each binding
     `{test, req, body_ref, binding_ref}` (a NEW structure, **separate from**
     `extract_tags` output → seam test untouched). Hermetic unit tests.
  2. **Binding locator** — a NEW function returning each binding's *line positions*
     (the `def test_…` body range + each `@req` line), needed to drive `git log -L`.
     Kept separate from `extract_tags` so its `{test,reqs,invariant_refs}` output
     (and the seam-test contract at `test_living_spec_e2e.py:57`) stays byte-identical.
  3. **Git adapter** — computes `body_ref` / `binding_ref` via `git log -L` over a
     real tree; tested against a throwaway temp git repo. Plus `__main__` wiring so
     the gate runs the WARN lane over the source tree at CI time.
- **Reporting:** WARN strings are reported in their own tier, distinct from
  `find_structural_violations`' FAIL list; WARN prints (e.g. stderr) and **exits 0**
  — it never flips a FAIL or fails the build.
- **What we will NOT build:** no intent-doc comparison (that is M2, couples to E); no
  stored/authored baseline or "bless" action (M3).

## Alternatives Considered (Axis 4 — research-grounded)

Industry approaches found (WebSearch EN+JP):

1. **Stored baseline ref (Kiro #9435)** — record a `gitRef` snapshot in spec
   metadata; on resume, scoped `git diff` since that ref → WARN. (= **M3**.)
   - Pros: closest shipped blueprint; explicit "reconciled at" point.
   - Cons: needs a **new authored baseline field** + a "bless/reconcile" action loom
     has no surface for; in tension with the parent brief's "git-ref is DERIVED".
   - Source: <https://github.com/kirodotdev/Kiro/issues/9435>
2. **Derived timestamp-compare, ALM-style (ReqToCode / patent)** — no stored
   baseline; compare requirement-last-modified vs last commit touching the
   referencing code. The richest semantic variant compares test-function-ref vs the
   **intent doc's** ref. (= **M2**.)
   - Pros: highest semantic precision — fires exactly when "behavior moved, the *why*
     wasn't revisited"; fully derived.
   - Cons: needs the MID intent doc, which is **slice 3 (E)** → **couples D to E**,
     forcing the order to E→D and abandoning "D first".
   - Source: <https://arxiv.org/pdf/2603.13999>
3. **WARN-only drift mode** — surface drift without auto-correcting (Helm `mode:
   warn`). Confirms the WARN-not-FAIL stance is industry-standard.
   - Source: <https://github.com/fluxcd/helm-controller/issues/643>

JP (microTRACER Git連携, テスト構成管理 traceability) confirms test↔target git
linkage is mature practice but ships no open drift-mechanism — **EN/JP gap is itself
a finding**: concrete mechanisms are EN-only; JP stays at the "traceability matters"
general level.

**My take:** Recommend **M1** (a self-contained variant of #2's derived comparison,
re-targeted from the intent-doc to the `@req` binding line). Chosen by the user.
**Conditional reversal:** if loom later wants to force a genuine "revisit the *why*"
loop and is willing to do E first, switch the comparison target to the MID intent
doc (M2) — the comparator's shape is unchanged, only the second ref's source moves.

## What Becomes Obsolete (Axis 5)

Nothing is removed — D is **additive**: a new WARN tier alongside the existing FAIL
check. It does **not** obsolete the structural FAIL path; it complements it (FAIL =
linkage broken / malformed; WARN = linkage intact but possibly stale). This is a
planned tier from a converged design, not speculative addition (so the "purely
additive ⇒ YAGNI" smell does not apply).

## Out of Scope

- The intent-doc comparison (M2) and any stored/authored baseline or "bless" flow
  (M3).
- The capstone's *other* CI wiring beyond the git-ref WARN lane — index regen at
  finishing, the required PR status checks, the active-coverage merge-boundary check
  (those stay in the G + CI slice; D ships only the git-ref WARN end-to-end).
- The intent layer itself (TOP/MID docs) — slice 3 (E).
- The index's git-ref / status columns (parent brief #2) — index-format open-Q,
  separate concern from the WARN gate.
- WARN acknowledge/suppress persistence (a durable "I've accepted this WARN" store) —
  M1 clears by re-touching the binding, so no separate suppression store is needed
  for the smallest end state.

## Open Questions (impl-level)

1. **WARN report format / wiring** — does the WARN tier return from the same
   `__main__` runner (printed to stderr, exit 0 since WARN doesn't fail), or a
   separate entry point? Resolve in `writing-plans`.
2. **Binding-line ref granularity** — `git log -L` on the exact `@req` line vs the
   line range of the comment block. (Now in scope; resolve in `writing-plans`.)
3. **Multiple `@req` on one function** — per-`@req` binding-line ref (each line
   independent) vs one shared function-level binding ref. Leaning per-line (matches
   audit2:F5 "per test-function" body-ref shared across the function's bindings, but
   each `@req` line has its own last-touch).
