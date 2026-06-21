# Brief — writing-plans: parallelism-aware plan ceiling + active parallel surfacing

Date: 2026-05-31 · Stage: brainstorming output → `writing-plans`
Scope locked: **core + active-prompt** (depth-based ceiling + active parallel
marking + advisory reviewer check). All changes advisory; Dependencies stays the
floor; disjoint-files ≠ independent guarded throughout.

## Problem (Axis 1 — JTBD)

When the user has a batch of genuinely-independent work (translate N files, apply
one guard to N disjoint modules, N disjoint data fetches, audit N modules), they
want code-toolkit to plan it so it **fans out in one parallel wave and asks for
confirmation once** — not chop it into N sequential mini-projects that each cost a
fan-out cap + a full confirmation round. Root cause: writing-plans bounds plan
size by **total task COUNT** (≤5), which is blind to dependency SHAPE. Three
symptoms share this one root:
1. The splitting framework never actively considers parallelism (opt-in markup,
   separate from the 4 splitting criteria).
2. The ≤5-count ceiling force-splits wide-but-shallow work into sequential briefs.
3. → which multiplies the per-brief/per-plan/per-run user confirmations ~N×.

Symptom 3 directly contradicts the confirmation-fatigue fix just shipped in
v0.13.0 ([[project_code_toolkit_asking_user_three_gate]]).

## Users (Axis 2)

- The planning **agent** (writing-plans consumer) + **kouko** (approves plans,
  receives the confirmations). kouko is cost/step-conscious and just invested in
  reducing over-confirmation — confirmation multiplication is a direct regression
  of that value.
- Pain locus = the **wide-but-shallow parallel class**: i18n/translation sweeps,
  one-change-across-N-modules, multi-source fetches, multi-module audits. The
  common case (genuinely-sequential or ≤5 work) is unaffected.

## Smallest End State (Axis 3 — chosen scope)

Three coordinated edits to `writing-plans`, all advisory / Dependencies-as-floor:

1. **Depth-based ceiling** (replaces the count-based one): bound the **critical-path
   depth** (longest dependency chain) to ≤5, NOT total task count. N independent
   tasks at the same dependency level (disjoint `Files touched`, no mutual dep)
   count as **one level**, not N. Preserve the forcing-function PURPOSE — a *deep*
   chain >5 is still a discovery failure (smallest-end-state too big); only WIDTH
   is exempted. **No hard width cap in the plan** — mark all parallel-eligible
   tasks `Independent: true` and let the dispatch/harness layer queue concurrency
   (dispatching-parallel-agents names no numeric cap; the harness queues excess).
   A very wide wave gets at most a SOFT advisory ("sanity-check independence"),
   never a hard split-trigger.
2. **Active parallel surfacing in the splitting framework**: after splitting, a
   pass — "for each pair of tasks at the same dependency level, if `Files touched`
   are disjoint AND there is no semantic dependency (data/symbol/doc-mirrors-code),
   mark both `Independent: true`." Converts parallelism from passive opt-in to
   actively-considered. **Guard: disjoint files ≠ independent** — a real semantic
   dep (doc-after-code, consumer-imports-producer) keeps tasks sequential
   regardless of file-disjointness ([[parallel_dispatch_doc_code_race]]).
3. **Advisory reviewer Check 15** (makes the reviewer symmetric): two tasks with
   disjoint `Files touched` AND no dependency edge, but NOT marked
   `Independent: true` → emit a **NOTE** ("possible missed parallel opportunity"),
   **non-fatal** (the planner may have a real semantic reason the files don't
   show). Today Check 14 only catches over-claiming (Independent + overlapping
   files → FAIL); there is no under-marking check.

## Current State Evidence

- `code-toolkit/skills/writing-plans/SKILL.md` "## Plan size ceiling — 5 atomic
  tasks": count-based (">5 atomic tasks, the brief is too big"), "split into N
  **sequential** briefs", "a 10-task plan is almost always a discovery failure" —
  the claim that conflates wide and deep.
- Same file "## The splitting framework": 4 criteria (time-box / module-scope /
  acceptance / no-hidden-coupling) — **none** about parallelism. The
  "### Parallel-dispatch markup (v0.8.0+)" block (`Independent`, `Files touched`)
  is **opt-in, default `false`**, structurally separate from the splitting walk.
- `references/plan-document-reviewer-prompt.md` Check 13 (Independent needs
  Files touched) + Check 14 (two Independent must be disjoint) + explicit
  "Checks 13–14 are N/A when no task declares `Independent: true`" — the
  asymmetry: catches over-claiming, never under-marking.
- `references/plan-format.md`: Dependencies semantics ("Tasks N, M parallel"),
  Independent/Files-touched as the disjointness oracle.
- `dispatching-parallel-agents/SKILL.md`: consumes `Independent: true` + disjoint
  files; **names no numeric concurrency cap** (harness runs same-message Agent
  calls concurrently, queues the rest). → the plan should NOT impose a width cap.
- Empirical: prior parallelism investigation
  ([[project_code_toolkit_parallelism_well_tuned]]) — 73% of implementer waves
  width-1 (genuine dep chains, correctly serial), but wide cases (i18n 9-wide)
  exist and the count-ceiling fragments them.

## Decision

Make the plan ceiling **dependency-shape-aware**: limit critical-path DEPTH (the
real cognitive-load + discovery-failure signal), let WIDTH fan out freely (declare
independence; harness handles concurrency). Add an active parallel-marking pass to
the splitting framework and a symmetric advisory reviewer check, so parallelism is
surfaced at plan time instead of relied on the planner remembering. Everything
advisory; Dependencies remains the execution floor; file-disjointness never
auto-implies independence. We will NOT add a DAG datastructure, a visualization,
or a hard width cap.

## Alternatives Considered (Axis 4 — research-grounded, EN + JA AGREE)

The whole industry bounds work by **depth + concurrency, never total count** —
strong EN/JA agreement:
- **Build systems** ([Bazel](https://bazel.build/versions/6.4.0/rules/performance)):
  parallelism limited by the **critical path** + a `--jobs` concurrency cap; width
  is free; idle jobs donated to critical-path bottlenecks.
- **Kanban WIP limits** ([Atlassian](https://www.atlassian.com/agile/kanban/wip-limits)
  / JA [Ryuzee](https://www.ryuzee.com/contents/blog/4134)): cap on **in-flight**
  work (cognitive load), explicitly **not** on backlog total. Conflating the two
  is the named anti-pattern.
- **Critical Path Method** (JA [Asana](https://asana.com/ja/resources/critical-path-method)
  / [Backlog](https://backlog.com/ja/blog/what-is-critical-path/)): find the
  longest chain, parallelize everything off it.

Rejected alternative: keep count-based but raise the number (e.g. ≤10) — doesn't
fix the conflation, just moves the cliff. Rejected: hard width cap — reintroduces
the count anti-pattern on the width axis. My take: depth-ceiling + free width +
advisory marking is the industry-aligned minimum.

## What Becomes Obsolete (Axis 5)

- The "≤5 atomic tasks (total)" framing and the "10-task plan is almost always a
  discovery failure" sentence → rewritten to depth-based (a 10-LEAF wide plan is
  NOT a discovery failure; a depth-10 chain is).
- The reviewer's one-directional Check 14 → balanced by advisory Check 15.
- The splitting framework's silence on parallelism → the new marking pass.
- The "split into N sequential briefs" path stays, but now fires only on genuine
  DEPTH overflow, not width.

## Out of Scope

- DAG datastructure / dependency-graph visualization (YAGNI; the Files-touched
  oracle + Dependencies field suffice).
- `dispatching-parallel-agents` and SDD changes — they already consume the markup
  + fan out correctly; the gap is in PLANNING, not dispatch.
- Hard-failing the reviewer on missed parallelism (deliberately advisory).
- Inventing a numeric concurrency/width cap (the harness owns concurrency).

## Open Questions

1. Exact wording of the "depth" definition for a doc-only prose skill — likely
   "longest chain of tasks linked by `Dependencies`" with a worked example in
   plan-format.md. Behavioral validation = dogfood + worked example (no pytest for
   skill prose).
2. Version bump target: code-toolkit `0.13.0 → 0.14.0` (writing-plans is a
   code-toolkit skill; minor, additive).
3. Should the soft "very wide wave" advisory name a number (e.g. >8) or stay
   purely qualitative? Lean qualitative to avoid a back-door count gate.
