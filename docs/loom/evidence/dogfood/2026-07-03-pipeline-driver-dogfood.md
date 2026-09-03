# loom pipeline driver — first end-to-end headless dogfood (2026-07-03)

> Roadmap item ① from the 2026-07-02 automation assessment (memory:
> `loom-automation-next-steps`): drive the FULL loom-* pipeline —
> idea → PRINCIPLES → design → design-critic → spec → completeness-critic →
> code(SDD) → whole-branch review — with a **Workflow script as conductor**
> reading each station's verdict / validator exit code. Deliverable: the
> **manual-intervention ledger** (what still needs a human), plus driver-layer
> requirements learned by running it. The F1–F5 requirements identified here
> are now implemented by `loom-pipeline` v0.1.0 — this doc remains the
> evidence record; the plugin is the living implementation.

## Setup

- **Toy product**: `focus-timer` — single-page pomodoro timer (one HTML file,
  vanilla JS, `node --test`able core). Rich enough in states
  (idle/running/paused/break/ending) to give the design station and critics
  real material.
- **Driver**: dynamic Workflow script, 7 sequential stations, critic gates
  consume the two-valued verdict enum (#471), generators gate on validator
  exit codes; critic loop-back ≤2 rounds; per-station retry ×2; idempotent
  adopt-if-valid on principles + design.
- **Models**: ALL stations Sonnet (user's cost directive mid-run) — including
  critic lenses and the SDD roles, which inherit their station's model. Gate
  quality at Sonnet vs Fable is an **open question** (see §Open questions).
- **Project isolation**: toy repo in session scratchpad; skills library
  (`monkey-skills` checkout) declared read-only to stations.

## Result — the pipeline ran end-to-end and its last gate fired

| # | Station | Verdict | Validator | Notes |
|---|---------|---------|-----------|-------|
| 1 | product-principles | PASS_WITH_NOTES | exit 0 | 6 falsifiable principles (idempotent adopt on re-runs) |
| 2 | design-system + interaction-flows | PASS_WITH_NOTES | exit 0 | DESIGN.md (8-section) + per-change `focus-timer-mvp/ui-flows.md` |
| 3 | design-critic | PASS_WITH_NOTES | exit 0 | 2 rounds, 15 gaps (2 sev-3) all re-seeded `critic-found`; 11 blind spots |
| 4 | spec-expansion | PASS_WITH_NOTES | exit 0 | 13 Requirements / ~24 scenarios; single-surface collapse; `pairwise.py` ran on the 6-object stage |
| 5 | completeness-critic | PASS_WITH_NOTES | exit 0 | 6 lenses, 5 gaps re-seeded, write-back committed |
| 6 | code (writing-plans + SDD) | PASS_WITH_NOTES | exit 0 | 5-task plan (deliberate cut from 13 reqs), RED→GREEN per task, **28/28 tests green**, 5 conventional commits (SDD's own) on the feature branch |
| 7 | whole-branch review | **NEEDS_REVISION** | — | 1 🔴 cross-task-coherence + 2 🟡 |

**The final 🔴 is the run's best advertisement for the pipeline's own design.**
Task 1 deferred wall-clock math to Task 3; Task 3 added `recompute()` but never
retrofitted Task 1/2's session-producing functions, and its tests hand-built
fixtures instead of composing through `start()`/`tickToZero()`. Every per-task
self-review said PASS — "each task's self-pass only ever saw its own slice —
exactly the blind spot whole-branch review exists to catch" (reviewer's own
words). The whole-branch gate caught what per-task gates structurally cannot —
**with degraded (writer=judge) per-task review upstream, see F5.**

## Getting here took 5 launches — each failure is a driver requirement

| Launch | Died at | Root cause | Driver requirement learned |
|--------|---------|-----------|---------------------------|
| 1 | design-critic | station ended with a prose verdict, no StructuredOutput (even after nudge) | **F1 — output-contract coupling**: skills define prose output contracts (round summary); an orchestration layer needs a machine contract. Dispatch prompts must pin "your LAST action is the StructuredOutput call"; longer-term, skills could define a machine-output mode. |
| 2 | design-critic | transient `Connection closed mid-response` | **F2 — per-station retry** is mandatory for long stations (added ×2 wrapper). |
| 3 | design-critic ×2 | account usage limit hit mid-pipeline | **F3 — freeze/resume is a hard requirement**: usage caps are a real ceiling for full-pipeline automation. The Workflow journal cache made resume free — completed stations replay instantly. A production driver needs checkpointing as a first-class feature, not luck. |
| 4 | (completed, but derailed) | resumed run delivered literal `"undefined"` for every `args` template slot | **F4 — the worst failure mode is a smart agent with permissive fallback instructions.** See below. |
| 5 | — | clean end-to-end | — |

### F4 — the silent-derail incident (launch 4)

With `${PROJ}`/`${SKILLS}` rendering as `undefined`, the ground rules said
"make the smallest reasonable assumption and proceed". Every station obeyed —
*intelligently and disastrously*:

- design-critic went hunting and **critiqued a completely different project**
  it found on disk (`~/pipeline-dogfood/invoice-tracker`, a leftover from an
  earlier experiment);
- spec-expansion found no seed anywhere and **synthesized its own product**
  (a CLI todo app), flagged it "ungoverned", and spec'd it;
- the code station then **built the invented todo app inside the monkey-skills
  checkout** — correctly on feature branches (loom-code discipline held: local
  `main` and `origin` untouched; branches `feat/toy-todo-cli-impl` +
  `docs/loom-spec-headless-dogfood-toy-todo-cli` kept as evidence, delete at
  leisure).

Every step was locally reasonable; the pipeline as a whole drifted onto the
wrong product **without a single failure signal**. Fixes applied and
validated in launch 5: (a) paths **baked into the script** — args plumbing is
a single point of failure across resume boundaries; (b) an **input contract
guard** in every station prompt: required inputs missing at their exact paths
→ `verdict: FAIL` immediately; no filesystem hunting, no substitute seeds, no
working in any other directory. Launch 5's stations all logged "input
contract verified" before working.

## The intervention ledger — 25 raw entries, triaged into three buckets

(The stations logged 25 raw interventions; near-duplicates across stations —
e.g. the same no-dispatch-tool gap reported by four stations — are
consolidated below, so the bucket items enumerate consolidated THEMES, not
the raw 25.)

### A. Driver/harness gaps (automatable — fix the machinery, not the human)

1. **No subagent-dispatch tool inside workflow stations** (**F5, the
   structural finding of the run**). design-critic, completeness-critic,
   spec-expansion's OOUX fan-out, and SDD's three-role triad ALL degraded to
   single-context simulation ("no Task/subagent tool exists — confirmed via
   ToolSearch"). The critics said so honestly; SDD's orchestrator played
   implementer + both reviewers itself. Cost is measurable: every per-task
   self-review passed, and the whole-branch reviewer (running later with fresh
   eyes) immediately found a 🔴 that per-task independence should have caught
   earlier. **A production driver must give stations real dispatch capability
   (workflow `agentType: 'general-purpose'` or per-lens `agent()` calls in the
   driver script itself) — writer≠judge is a capability requirement, not just
   prompt text.**
2. Output-contract pinning (F1), retry (F2), checkpoint/resume (F3), input
   guards (F4) — all now encoded in the driver script; a formal driver
   inherits them as requirements.
3. Commit-or-not conventions per station: stations improvised git behavior
   (spec-critic inferred "prior stations committed, so I will"; design-critic
   left write-back uncommitted "for whatever station owns that gate"). A
   formal driver should own an explicit per-station commit contract.
4. dcg/hook friction in headless mode (a station's `git restore` was blocked
   by a guard hook and it worked around it) — driver needs a documented
   policy for guarded-command fallbacks.

### B. Genuine human gates (keep a person here)

1. **Product decisions made inline by stations.** The spec station *resolved a
   product behavior itself* — "ending-state controls = Reset-only, no
   Pause/Start" — by chaining seeded facts. Defensible, but in a live run this
   is exactly a complex-fork briefing moment (PR #475): **spec-level product
   choices should surface to the user, not be inferred.** Similarly
   design-critic's sev-3 findings (screen-reader gaps) change scope — a human
   should triage which re-seeds are in-scope before code.
2. **Change-id minting.** The change-id must be minted once, by a human or at
   the pipeline entry — launch 2's design station self-named
   `core-timer-session` while the driver said `focus-timer-mvp`, costing a
   canonicalization step.
3. **Cost caps as policy**: 5-of-13-requirements task cut; completeness-critic
   capped at 1 round (dryness never verified); design-critic stopped at 2
   rounds although round 2 was NOT dry (its own K=2 rule would justify a round
   3) — each is a scope/rigor decision a human should set (per-run budget
   policy), not a station's judgment call.
4. **Final merge** stays human (review NEEDS_REVISION → fix or accept is a
   user decision; loom-code already encodes no-auto-merge).

### C. Capability gaps (build next)

1. **UI-verify station (roadmap ②) — now evidence-backed.** The code station's
   own ledger: "No live browser was used to verify index.html end-to-end …
   verification is static." The whole GUI half of the product (DOM wiring,
   sound, aria-live, script-failure fallback) shipped with zero behavioral
   verification. This is precisely the agent-device / chrome-devtools station
   the roadmap deferred pending this evidence. Shape suggestion from this run:
   it slots AFTER the SDD suite gate and BEFORE whole-branch review, driving
   the flows in `ui-flows.md` (which already enumerates the states to check)
   against the real rendered page.
2. **Critic loop-backs never fired** — both critics returned PASS_WITH_NOTES
   round 1 because their contract is *re-seed, not reject* (NEEDS_REVISION
   only fires when a sev-3 cannot be concretely re-seeded). The driver's
   revision loop is therefore mostly dead code at GENERATE stations; the real
   revision pressure arrives at the review station. Worth revisiting whether
   critics should escalate more (e.g. sev-3 count threshold) or whether
   review-stage-only rejection is the intended economy.

## Open questions

- **Sonnet gates vs Fable gates**: this run's critics/review all ran Sonnet
  (user cost directive). The review still caught a real 🔴. A/B the same
  artifacts under Fable critics to price the quality delta before fixing a
  production tier policy.
- Does the toy run fire the DESIGN.md-consumer re-trigger (#473)? Judged NO —
  a scratchpad toy is not "a real GUI product wiring its frontend", but this
  run produced the first end-to-end evidence the re-trigger evaluation will
  want.

## Artifacts

- Toy repo (session scratchpad, `focus-timer/`): branch `feat/focus-timer-mvp`,
  11 commits total (1 seed + 5 upstream-station commits + 5 SDD commits;
  design-critic's round-2 write-back stayed uncommitted per its evaluator
  convention — the per-station commit-contract gap of Bucket A item 3),
  28/28 tests green; `docs/loom/` carries PRINCIPLES / DESIGN /
  ui-flows / spec change-folder with both critics' provenance-tagged
  write-backs. Re-verified locally: `node --test` exit 0.
- Driver script: session workflow dir, `loom-pipeline-dogfood-*.js`
  (7 stations, ~260 lines) — the seed of a formal `using-loom-pipeline`
  driver; carries F1–F4 fixes inline.
- Derail-incident evidence: monkey-skills branches `feat/toy-todo-cli-impl`,
  `docs/loom-spec-headless-dogfood-toy-todo-cli` (safe to delete).
- Run stats (launch 5): 7 station agents, ~607k subagent tokens, 153 tool
  calls, ~33 min wall clock. Cumulative across 5 launches: ~1.6M subagent
  tokens.
