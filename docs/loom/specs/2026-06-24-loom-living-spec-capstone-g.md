# Brief: loom living-spec index — capstone G (wire to real repo + merge gate)

Status: **BRAINSTORM — slicing decided (two thick slices), awaiting sign-off → writing-plans.**
Date: 2026-06-24. Branch: `feat/loom-living-spec-capstone-g` (cut from `origin/main` `11c44c3e`).

> **Design is CONVERGED upstream — this brief does NOT re-open it.** The 5-round adversarial
> coherence audit lives in `docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md`
> (Locked decisions B1/B2/#1–#6 + the active/deferred schema). This brief is the **implementation
> slicing** layer only: how to cut the remaining wiring into shippable PRs. All industry-alternative
> research (Serenity / Kiro / Tessl / OpenSpec) is already in the design brief — Axis 4 not re-run.

## Problem

Slices 1–4 shipped the **engine** of the living-spec index but left it **not plugged into the real
repo**. The headline design claim — *"the index cannot drift from the tags; intent↔behavior drift is
CI-gated"* — is **not yet true at runtime** because: the structural FAIL lane runs over **empty
inputs**, `generate_index()` is **never called**, no `docs/loom/INDEX.md` is **committed**, and there
is **no merge-blocking CI check**. Capstone G is the wiring job that makes the claim real, plus the
two genuinely-new authoring pieces (implementer `@req` DoD; loom-spec active/deferred status).

JTBD: *When I close a development branch, I want the living-spec index to be regenerated, committed,
and CI-gated against drift, so the index I query is provably current and an under-verified `active`
requirement cannot silently merge.*

## Users

loom-suite maintainers running loom-code's own pipeline on this repo (dogfood). Two consumers:
(a) the **finishing-a-development-branch orchestrator** (regenerates + commits the index once/branch);
(b) **CI on the PR head** (blocks merge on a stale index or an `active`-req-with-0-tests).

## Smallest End State

The smallest end state that makes the headline claim true is **PR-1 (linkage truth live)**: structural
FAIL lane reads the real repo, `docs/loom/INDEX.md` is committed + regenerated at finishing, and CI
blocks a stale index. **PR-2 (intent coverage live)** adds the intent half: loom-spec authors
active/deferred status and CI blocks an `active` req with 0 passing tests.

Smaller-than-the-full-ask was rejected for a reason: shipping the structural lane **alone** (no committed
index, no gate) is *"an invisible quick-win"* (user's own slice-2 rule) — nothing observably changes.
A thick slice that runs end-to-end (a real violation actually FAILs CI) is the minimum *demonstrable* win.

## Current State Evidence

Brownfield. All citations verified by read-only recon at `origin/main` (`11c44c3e`).

- **Forward (entry → structural lane):** `check-living-spec-index.py:main()` feeds the structural lane
  **empty inputs** — `find_structural_violations([], [], {})` at `check-living-spec-index.py:128`
  (explicit slice-1 deferral comment above it). The WARN lane on the same path **is** real-repo-wired:
  `run_drift_lane(root)` at `:106–111` collects via `collect_bindings(root)` → `resolve_binding_refs`
  → `find_gitref_drift`. **This is the pattern PR-1 mirrors for the structural lane.**
- **Reverse (index generation, SSOT direction):** `living_spec_index.py` holds `load_namespace(specs_dir)`
  (`:18–31`, parses `docs/loom/spec/<capability>/spec.md` → `{req_id: capability}`) and `generate_index()`
  — **both exist, neither is called from `main()`**. `index_is_current()` (`check-living-spec-index.py:75`)
  is the byte-identity helper to reuse for the gate. Authoring direction: loom-spec **authors** the
  `docs/loom/spec/<capability>/` namespace; loom-code's generator **reads it in-tree at the same commit**
  (design #6 seam — same-tree parse, NOT point-don't-copy).
- **Error (gate lanes):** structural = hard FAIL (need no index, RED-safe); merge-boundary checks
  (`active`+0-tests, `committed==regen`) are **RED-phase-unsafe** → must run only post-finishing,
  pre-merge (design #3). Current CI `loom-code-ci.yml:53–68` has 4 gates (pytest / verify-drift /
  codex-manifest / crossrefs); the 2 capstone gates are absent.
- **Data (status schema):** `validate_intent_layer.py:58–62` `_TOP_SECTIONS` = `## Invariants` /
  `## Object state machines` / `## Out of scope` — **zero** notion of req status. `spec.md` already
  carries `### Requirement: <id>` headings (parsed by `load_namespace`). Status attach-point is an
  open sub-decision (see Open Questions).
- **Boundary (agent contract + finishing):** `implementer.md` has **zero** `@req` / DoD / tagging
  rule (full-file recon). `finishing-a-development-branch/SKILL.md` has **zero** index-regen step;
  the natural slot is a sub-step of the close-out commit (its Phase 4), orchestrator-only (design #5:
  per-implementer regen would merge-conflict the repo-wide generated file).

Evidence paths: `loom-code/scripts/{check-living-spec-index,living_spec_index,living_spec_collect,living_spec_gitref,living_spec_drift,living_spec_tags}.py`,
`loom-code/agents/implementer.md`, `loom-code/skills/finishing-a-development-branch/SKILL.md`,
`.github/workflows/loom-code-ci.yml`, `loom-spec/scripts/validate_intent_layer.py`,
`loom-spec/skills/spec-expansion/SKILL.md`.

## Decision

Ship capstone G as **two thick single-concern slices**, each an end-to-end demonstrable win
(matches the slice-2 "thick = real-repo end-to-end" lesson; "invisible quick-win isn't a win").
Forced order: PR-1 before PR-2 (PR-2's coverage gate needs both PR-1's index machinery and PR-2's
own status authoring; it is the final integrator).

**PR-1 — "make the index real" (linkage truth live).** loom-code side. Contains:
1. **Structural FAIL lane wiring** — `check-living-spec-index.py:main()` feeds real-repo
   `tag_records` / `malformed` / `namespace` (mirror `run_drift_lane`: `collect_bindings` +
   `find_malformed_tags` + `load_namespace`) into `find_structural_violations`.
2. **INDEX.md generation + committed artifact** — call `generate_index()`; create committed
   `docs/loom/INDEX.md`.
3. **Finishing regen step** — orchestrator regenerates + stages + commits `INDEX.md` **once/branch**
   in `finishing-a-development-branch` (close-out commit sub-step; NOT per-implementer).
4. **Byte-identity CI gate** — `committed == fresh-regen` (reuse `index_is_current`) as a
   pre-merge required check on the PR head.
5. **Implementer `@req` DoD** — add to `implementer.md`: every test written under TDD carries a
   `# @req: <REQ-id>` tag (the linkage the lane + index read). Rides PR-1 because it is the linkage
   contract the rest of PR-1 consumes.

**PR-2 — "enforce intent" (intent coverage live).** loom-spec + loom-code-ci. Contains:
1. **active/deferred status authoring** — loom-spec extends the intent layer schema +
   `validate_intent_layer.py` + the spec-expansion "Authoring …" section.
2. **active-coverage CI gate** — `active` req with 0 passing tests = FAIL, as a pre-merge required
   check (RED-safe: merge-boundary only); `deferred` + 0 tests = surfaced, not failed.

**NOT building:** a JSON index sidecar; an `archive/` lifecycle; a `loom-trace` plugin; the
MID-prose-restates-behavior lint; any cross-plugin synced namespace registry. (All YAGNI / deferred
per the design brief.)

## Out of Scope

- Re-opening any locked design decision (B1/B2/#1–#6) — converged, audited, off-limits.
- Back-migrating existing one-shot change-folders into the new structure.
- The exact GitHub required-check *mechanism* (branch-protection rule vs merge-queue) — impl detail
  chosen at writing-plans/wiring time, not a design fork.
- Tagging the repo's existing tests with `@req` retroactively (the index legitimately starts near-empty;
  B1 "empty base case is valid"). PR-1's end-to-end demo uses a seeded/fixture `@req`.

## What Becomes Obsolete

- The **empty-inputs stub** at `check-living-spec-index.py:128` (+ its slice-1 deferral comment) —
  deleted in PR-1 when the real collection is wired.
- The framing that `generate_index()` / `load_namespace()` are "exercised only by unit tests" —
  they become live `main()` call-sites in PR-1.

## Open Questions (impl-level; resolved at each slice's writing-plans)

1. **active/deferred status attach-point (PR-2):** in-spec metadata (`### Requirement: <id> [status: …]`)
   vs a new TOP `## Requirement status` section vs a per-capability `status.json`. Recon surfaced all
   three; pick at PR-2 brainstorm. (Leans in-spec metadata: co-located with the `### Requirement` heading
   `load_namespace` already parses — no new file, no new parser.)
2. **Gate ready-signal binding (design Open-Q6):** bind the pre-merge checks to a finishing-emitted
   ready signal (the regen commit / ready-for-review transition), NOT bare `not-draft`, so "non-draft"
   provably implies "index regenerated." Affects both PR-1's byte-identity gate and PR-2's coverage gate.
3. **PR-1 end-to-end demo vector:** since the repo's tests carry no `@req` yet, the "real violation FAILs"
   demonstration runs through a seeded `@req` / fixture tree — confirm the demo shape at writing-plans.
