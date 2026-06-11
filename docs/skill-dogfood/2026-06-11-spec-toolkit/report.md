# Dogfood report — spec-toolkit (activation focus)

- **Date**: 2026-06-11
- **Skills under test**: `spec-expansion`, `completeness-critic` (uninstalled, worktree `feat/spec-toolkit-mvp`)
- **Focus**: Probe A — activation/triggering (workflow output already validated by the 7-seed A/B dogfood; see `spec-toolkit/examples/AB-SUMMARY.md`)
- **Harness**: real `claude -p --max-turns 1 --allowedTools Skill --output-format stream-json --verbose` router sandbox at `/tmp/sb-spectk-v1` — 2 targets + 4 nearest-sibling distractors (brainstorming / writing-plans / systematic-debugging / complexity-critique) with their real descriptions; the live router also saw all globally-installed skills (higher fidelity for over-trigger).
- **Corpus**: 5 should-fire (3 spec-expansion, 2 completeness-critic) + 5 should-NOT (4 distractor-territory + 1 pure control), **2 runs each** (routing is non-deterministic).

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

**No findings.** Activation is precise.

## Results (both runs identical)

| Query | Expected | Run 1 | Run 2 | Verdict |
|---|---|---|---|---|
| se1 — "rough idea: export dashboard data… expand into full spec, paths/states/edges" | spec-expansion | spec-expansion | spec-expansion | ✅ |
| se2 — "fan this one-liner into objects/states/edge-case scenarios: merge two tables" | spec-expansion | spec-expansion | spec-expansion | ✅ |
| se3 — "turn a sparse feature idea into testable acceptance criteria, edges named" | spec-expansion | spec-expansion | spec-expansion | ✅ |
| cc1 — "draft spec for password reset — what omissions/blind spots? critique for gaps" | completeness-critic | completeness-critic | completeness-critic | ✅ |
| cc2 — "what aspects did this requirements doc forget? find gaps before we build" | completeness-critic | completeness-critic | completeness-critic | ✅ |
| no1 — "fix this bug: CSV exporter throws on empty rows" | NOT a target | code-toolkit:systematic-debugging | code-toolkit:systematic-debugging | ✅ no over-trigger |
| no2 — "this module is over-complicated, simplify + delete code" | NOT a target | complexity-critique | complexity-critique | ✅ no over-trigger |
| no3 — "split this approved brief into atomic tasks + dependency graph" | NOT a target | code-toolkit:writing-plans | code-toolkit:writing-plans | ✅ no over-trigger |
| no4 — "brainstorm whether we should build dark mode at all" | NOT a target | code-toolkit:brainstorming | code-toolkit:brainstorming | ✅ no over-trigger |
| no5 — "what is the capital of France?" | none | (none) | (none) | ✅ control |

- **True-positive rate** (should-fire that fired correctly): **5/5 = 100%** (both runs)
- **True-negative rate** (should-NOT that did not fire either target): **5/5 = 100%** (both runs)

## Notable

- **no4 is the key over-trigger guard**: "should we build dark mode *at all*" is intent-exploration, which belongs to `brainstorming`, not `spec-expansion` (which operates *after* intent is settled). The router correctly chose brainstorming both runs — confirming the spec-expansion description's "when starting … from a sparse idea and you want the paths/states/edges named BEFORE implementation" framing draws the right boundary against brainstorming's "explore intent/alternatives".
- The completeness-critic vs (brainstorming/writing-plans) boundary held: "critique a spec draft for gaps" fired the critic, not a planning/review sibling.

## Method caveat
n=2 runs on a 10-query corpus. Clean result; not an exhaustive activation audit. The boundary cases that matter most (spec-expansion vs brainstorming; completeness-critic vs code review) were probed and held both runs.
