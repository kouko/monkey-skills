---
name: critic-finding-is-hypothesis-until-code-recon
description: A spec-critic finding that asserts a codebase fact is a HYPOTHESIS until code recon confirms it — spec-only lens panels can re-seed counterfactual requirements; verify the premise in code before building machinery to satisfy it
type: gotcha
origin: operational-kpi scope-B quarterly rebuild, T17 (feat-operational-kpi-quarterly, 2026-07-18)
---

A completeness-critic panel reads the SPEC and its decision docs — not the
code. A lens can therefore produce a plausible, multi-caveat finding whose
factual premise about the codebase is simply false, and the finding then
flows into the spec as a requirement for machinery that does not exist.

Real case: critic round 2's NFR lens found (sev-3) that "pre-revision cached
payloads carry the old calendar-valued `fiscal_year` and must be schema-
versioned so they never alias into the new pipeline." The re-seeded scenario
mandated versioning "the" labeled-fact cache key. At implementation, the T17
implementer's recon (whole-file grep + `git log` on the extraction function)
proved the labeled-fact layer NEVER had a cache — only schema-independent
raw-source caches exist. The scenario's GIVEN was counterfactual; satisfying
it as written would have meant BUILDING an unauthorized cache layer just to
version it.

**Why:** critic lenses are deliberately fresh-context and artifact-scoped
(spec + delta docs) to decorrelate them — the same isolation that makes them
find real omissions also cuts them off from the code. Cross-lens convergence
raises rank confidence about the SPEC's gaps, not about the CODEBASE's facts.

**How to apply:** treat every critic-found requirement that asserts a
codebase fact ("the cache", "the retry path", "the existing X") as a
hypothesis carrying an implicit recon obligation. Cheapest discharge points:
(a) at re-seed time, have the orchestrator grep the named artifact before
writing the scenario; or (b) at implementation time, sanction the implementer
to STOP with NEEDS_CONTEXT when the premise fails recon — then amend the
SPEC to reality (the true obligation is often negative: "no existing X may
do Y; any future X must Z") instead of building the missing machinery to
make the scenario literally satisfiable. The amended-scenario + poison-seed
regression pattern from T17 is the worked example. Relates to
[[cache-key-collision-across-migration]] (the real precedent the critic
over-generalized from) and
[[fiscal-year-derive-per-fact-against-filing-calendar]] (same branch's
root-cause record).
