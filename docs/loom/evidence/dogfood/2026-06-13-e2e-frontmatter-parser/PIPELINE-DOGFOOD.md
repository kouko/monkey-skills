# E2E pipeline dogfood — spec-toolkit GENERATE → code-toolkit VERIFY

> Date 2026-06-13. First end-to-end run of the full GENERATE→DECLARE→VERIFY pipeline on a
> real buildable target (a stdlib markdown frontmatter parser). Purpose: validate the pipeline
> actually holds AND scope what "DECLARE bridge" is genuinely needed (vs speculative). Target
> chosen small/pure/testable on purpose — the artifact is incidental; the **seam** is the deliverable.

## Verdict — the pipeline HOLDS end-to-end (manually)

```
seed (3 lines)
  → spec-expansion (executed from SKILL.md; single-surface collapse, BVA/error lenses)
      → OpenSpec change-folder  ✅ validate_spec_output.py clean
  → completeness-critic 3-lens panel (fresh-context subagents + personas + seed-only view)
      → 5 critic-found gaps re-seeded (consolidated: dedup + rank by severity×convergence)
      → change-folder still validate-clean  ✅
  → [BRIDGE — manual] 19 `#### Scenario:` → acceptance criteria
  → code-toolkit implementer (TDD iron law: 19 RED tests → GREEN)
      → frontmatter.py (71 lines, pure stdlib, 0 imports) + test_frontmatter.py
      → 19/19 pytest green  ✅ (independently re-run)
```

**The GENERATE→VERIFY joint works.** A 3-line seed became a 19-scenario validated OpenSpec
spec, which drove a TDD build to 19/19 green with no human re-specification. The
`#### Scenario:` GIVEN/WHEN/THEN items ARE the contract joint — the implementer confirmed
"the scenarios (not the requirement prose) do the load-bearing behavior-pinning," which is
exactly the acceptance-criteria-driven design intent.

## The completeness-critic added real, build-constraining value

The panel found 5 omissions the spec-expansion draft missed, and they became real tests:
- 🔴 **empty-key-after-strip → ValueError** — **3-lens convergence** (BVA + error + contract).
  The draft's "colon-less line → raise" silently allowed `: value` → `{"": ...}`. Now a test.
- 🔴 **non-str input → TypeError**, **values-stay-strings (no YAML coercion)**, **fence
  exactness**, **empty-body-at-fence** — all now scenarios that constrain the build.

Convergence-as-precision-signal worked: the highest-converged gap (empty-key, 3 lenses) was
the most load-bearing. Decorrelation levers paid off — the **seed-only** contract critic
independently surfaced the type/negative-space contract gaps a draft-anchored reader skips.

## SEAMS found (the real deliverable — what bridge is genuinely needed)

### B-1 — document-format mismatch, but a NARROW adapter, not a big router  🟡
`code-toolkit:writing-plans` ingests a **brainstorming brief** (`docs/loom/specs/<topic>.md`:
Problem / Users / Smallest-End-State / Decision…). spec-toolkit emits an **OpenSpec change-folder**
(proposal.md + `specs/<cap>/spec.md`). The two don't match at the document level — there is **no
skill that reads a change-folder and produces writing-plans input.** BUT: the `#### Scenario:`
items map **1:1 to task acceptance criteria** (each = RED/GREEN), so the manual bridge for a
single-function module was **near-zero friction** — I handed the 19 scenarios straight to the
implementer as the test spec.
**Implication:** the needed "DECLARE bridge" is a **thin adapter** (change-folder `#### Scenario:`
→ writing-plans tasks), NOT a router/discovery/persistence stack. For a single module the manual
bridge is fine; the adapter earns its keep only when the spec spans **multiple capabilities /
modules** (then you want requirements → multiple briefs with a dependency DAG, which is real work
to do by hand). **Recommendation:** do NOT build it speculatively (two-kinds-of-scaffolding /
complexity-critique); build the thin adapter the first time a multi-module spec makes the manual
bridge painful. This run did not reach that pain.

### E-1 — lens-critic dispatched as a read-only search agent REFUSED the role  🟡 (actionable on the shipped skill)
Dispatching a completeness-critic lens as the `Explore` (read-only search) agent type → it
replied *"I'm a file search specialist… this is pure reasoning, not a search task"* and refused
to produce the critique until re-dispatched as `general-purpose`. **The shipped completeness-critic
SKILL.md says "dispatch one subagent per lens" without pinning the agent type** — on a host where
the default subagent is a search/explore agent, the panel silently loses a lens. **Fix (cheap, real):
the panel-dispatch instruction should specify a general reasoning agent, not inherit whatever the
host's default (possibly search-only) subagent is.** This is a genuine portability bug the prior
panel dogfood (run by me directly, not via dispatched search-agents) could not surface.

### P-1 — proportional-rigor: full GENERATE ceremony was mostly N/A, but it DEGRADED GRACEFULLY  🟢
A one-function pure utility doesn't need OOUX multi-agent fan-out / L2 cross-object / L3 journey-nav.
And the skill **handled this correctly on its own**: USM backbone collapsed to 1 node (v0.2.1
single-surface rule), ③b self-skipped ("no interaction-dense stage"), ③c minimal ("single-stage flow").
No fiction was manufactured. So the **parked proportional-rigor tiering (No-Spec / Lite / Full) is a
real nice-to-have but NOT a blocker** — the v0.2.1 graceful-degradation rules already prevent the
worst failure (forcing a multi-stage spine where none exists). A "Lite" tier would just make the
proportionality explicit/faster, not unlock anything.

## What this says about the original "DECLARE bridge" roadmap item

The roadmap framed DECLARE as a stack (OpenSpec CLI wiring · spec-discovery · spec-persist · router
· change-folder hand-off). This run shows **most of that is speculative**: the hand-off works
manually today, the format is already OpenSpec-valid, and the only mechanical gap is a thin
scenario→task adapter that isn't worth building until a multi-module spec demands it. The
**highest-ROI, evidence-backed** next action is not the bridge at all — it's **E-1** (a 1-line fix
to the shipped completeness-critic so its panel doesn't lose a lens on search-agent hosts).

## Artifacts (kept local — dogfood evidence, not a shipped library)
- `proposal.md` + `specs/frontmatter/spec.md` — the GENERATE output (validate-clean, 19 scenarios).
- `frontmatter.py` (71 LOC, pure stdlib) + `test_frontmatter.py` (19 tests) — the VERIFY output.
- This report.
