# Brainstorming evaluation — "auto-build harness" (go / no-go)

> **Type**: brainstorming evaluation brief (decision aid, not a build spec)
> **Date**: 2026-06-10
> **Driver**: kouko — "if I want to *auto-build an effective coding-agent harness*, based on monkey-skills, is it a plugin / a skill / or actually a new repo?" + "evaluate doing it."
> **Method**: 5-axis brainstorming framework; Axis-4 grounded in 2026-06 web research (harness anatomy, AGENTS.md auto-gen evidence, existing harness projects).

## Problem (Axis 1 — JTBD)

The **proposed solution** is "auto-build an effective harness." The **job behind it**: *make autonomous coding reliable on an arbitrary repo without manual per-repo setup.* "Build a harness" is one hypothesized means; the job is **reliability-without-manual-setup**.

Critical premise-check (from prior research): an effective harness's bottleneck is **not** the command surface. Per the harness anatomy (loop / tools / state / permissions / **evals** / certified data) and the auto-harness evidence (score 0.56→0.78 via **failure-mining + live evals**, not surface-building), the command surface is **necessary-not-sufficient**. So "auto-build harness" decomposes into three genuinely different jobs:

- **A — Repo onboarding / bootstrap (inside host).** Given a fresh repo, auto-establish what makes a *host* agent (Claude Code/Codex) effective on it: command surface + conventions + a verify loop. Semi-automatic, human-confirmed.
- **B — Standalone runtime harness (the agent itself).** Build the loop + tool execution + permission sandbox + state + eval infra — the thing that *runs* the model. This is what Claude Code already IS.
- **C — Failure-driven self-improving harness.** Mine failures, maintain live evals, gate regressions, accrete the discipline (the auto-harness / AutoHarness model). The reliability lever the evidence actually points to.

These are not the same project. The packaging answer (skill / plugin / new repo) is **determined by which job** — so this fork is the load-bearing decision.

## Users (Axis 2)

kouko — solo, building+maintaining the **monkey-skills monorepo (~21 plugins)**; hosts = Claude Code / Codex / Cursor. The "users" of this capability are kouko's own future coding sessions across many repos (and, if shipped to the marketplace, other installers). Condition today: everything kouko builds runs **inside a host agent**; values process-discipline + primary-source grounding; just shipped command-surface v1+v2 (merged `806da6b2`).

## Current State Evidence

- **Packaging model**: monkey-skills = monorepo of ~21 plugins; each plugin = `skills/ + agents/ + commands/ + hooks/ + scripts/`, installed via `marketplace.json`. **A skill or plugin is a host-injected EXTENSION — never a runtime.** (`ls */`, `code-toolkit/.claude-plugin/plugin.json`.)
- **No harness/onboarding/bootstrap plugin exists** — greenfield for this capability (`ls | grep -iE harness|onboard|bootstrap` → none).
- **code-toolkit boundary**: PRODUCT-SPEC §3.2 frames it as a **"write-code process-discipline toolkit"** and explicitly is NOT the "write-skill meta toolkit" (Non-Goal #95). The "builder not configurator" line lives in the *command-surface spec §7*, not PRODUCT-SPEC. Either way, **auto-onboarding a whole repo's harness is neither writing code nor a reviewer gate → outside code-toolkit's charter.**
- **Command surface already shipped**: v1 resolution + v2 accretion (merged). Detection table covers 24 stacks; vbc falls back to detection when no surface exists (so absence of a surface does NOT block the host today). Seed ④/⑤ parked.
- **Failure-driven primitives already exist in dev-workflow**: `dogfood-skill-testing`, `distill-sessions`, `skill-tuning`, `skill-judge`, `skill-creator-advance` — i.e. the C-flavoured machinery partially exists, today aimed at *skills*, not at *coding tasks*.
- **The host already provides B's runtime**: Claude Code is the loop/permissions/tools. Building B = reinventing the host.

## Smallest End State (Axis 3) — per interpretation

- **A**: finish **野心 B ④ seed-preflight** as a `code-toolkit` skill (readiness check: is there a runnable `test` verb? if not, draft a seed via detection + verify-before-declare, human-confirms). **Smallest of all — possibly 0 new top-level artifacts.** If onboarding grows past command surface (conventions, eval stub, dep install), graduate to a **new `harness-bootstrap` plugin** (NOT inside code-toolkit — charter violation).
- **B**: **not small.** [~4–12 weeks / 5–20k LOC](https://atlan.com/know/how-to-build-ai-agent-harness/). Smallest viable = **adopt** an existing harness ([OpenHarness](https://github.com/HKUDS/OpenHarness) / [AutoHarness](https://github.com/aiming-lab/AutoHarness)) rather than build.
- **C**: a loop that runs a coding task, captures failures, and turns them into regression tests/evals. **Smallest = generalize the primitives we already have** (`dogfood-skill-testing` + `distill-sessions` pattern) from skills to coding tasks — likely a new plugin (`coding-evals` / `failure-mining`), since it needs its own commands + run-store.

## Alternatives Considered (Axis 4 — researched 2026-06)

| # | Option | Maps to | Pro | Con |
|---|---|---|---|---|
| 1 | Extend code-toolkit with seed-preflight skill | A (subset) | cheapest; reuses v1/v2; no new plugin | only command surface — not a "harness" |
| 2 | New `harness-bootstrap` plugin in monkey-skills | A | semi-auto onboarding; matches proven "regenerate-data-preserve-human" + [OpenHarness dry-run readiness verdict](https://github.com/HKUDS/OpenHarness) pattern | onboarding ≠ reliability; ETH: full auto-gen HURTS unless human-curated |
| 3 | New standalone runtime repo | B | host-independent; full control | reinvents Claude Code; 5–20k LOC; surface is necessary-not-sufficient |
| 4 | **Adopt** an existing harness (OpenHarness / AutoHarness / [neosigmaai/auto-harness](https://github.com/neosigmaai/auto-harness)) | B/C | BYO-agent + failure-mining + regression gates already built; reuse not rebuild | external dep; learning curve; may not fit monkey-skills idioms |
| 5 | New failure-driven eval plugin (generalize dogfood/distill to code) | C | **highest reliability leverage per evidence** (auto-harness 0.56→0.78 via failure-mining); we already own the seeds | new plugin; eval infra is real work |

**Industry signal (EN+JA agree)**: AGENTS.md/context files **rot** and should **grow naturally** (= accretion, which v2 already does); JA practitioners independently built ["auto-grow AGENTS.md"](https://nyosegawa.com/posts/agents-md-generator/). **EN adds the caution** ([ETH study via Augment Code](https://www.augmentcode.com/guides/how-to-build-agents-md)): naive **full auto-generation reduced task success ~3% and raised cost >20%** — human-curated wins. No mainstream tool does autonomous from-zero harness build; the proven shape is **semi-auto + readiness-verdict + human review**.

## Decision / Recommendation

1. **Reject B (build a standalone runtime) unless host-independence is a hard requirement.** Evidence: reinvents Claude Code, 5–20k LOC, and the command surface (your entry point to this idea) is necessary-not-sufficient. If you ever need host-independent runs, **adopt** (Option 4), don't build.
2. **"auto-build harness" as literally stated → the honest smallest version is A**, and A's smallest is **finishing 野心 B ④ (semi-auto seed) inside code-toolkit**, graduating to a `harness-bootstrap` plugin only if onboarding scope grows beyond the command surface. Keep human-in-the-loop (ETH).
3. **But the JTBD ("reliable autonomous coding") points at C, not A/B.** The reliability lever is **failure-driven evals**, not surface-building. Highest-value reading = Option 5 (a failure-mining/eval plugin generalizing our existing `dogfood-skill-testing` + `distill-sessions` from skills to coding tasks) — or adopt auto-harness's pattern.
4. **Packaging rule of thumb** (the one-line test): *"when this runs, is the host driving it, or is it driving the model?"* Host-driven → monkey-skills (skill if narrow, plugin if multi-capability). Drives-the-model → new repo.

**Net**: "auto-build a full harness" is the wrong-sized target. Pick by goal — **less manual per-repo setup → A (seed-preflight skill → harness-bootstrap plugin)**; **more reliable autonomous coding → C (failure-driven eval plugin / adopt auto-harness)**; **host-independent runtime → adopt, don't build B.**

## What Becomes Obsolete (Axis 5)

- A: manual AGENTS.md authoring for new repos; the parked 野心 B ⑤ (subsumed by the semi-auto seed).
- C: the manual "file a dogfood note when a rationalization breaks through" loop (code-toolkit `tests/README.md`) → automated failure→regression-test.
- B: would obsolete code-toolkit's SessionStart-hook discipline model (it'd move into the runtime) — a reason NOT to do B casually.

## Out of Scope / Open Questions

- **THE decision (blocking)**: which JTBD — A (onboarding), B (runtime), or C (failure-driven reliability)? The packaging answer falls out of this:
  - A → skill in code-toolkit, then a new `harness-bootstrap` plugin if it grows.
  - B → new repo (or adopt an existing harness).
  - C → new plugin in monkey-skills (generalize dogfood/distill), or adopt auto-harness.
- Secondary: is host-independence (running without Claude Code, e.g. in CI) a requirement? If yes, it forces B/adopt regardless of A/C.

---

## Decision (2026-06-10): **C chosen — failure-driven reliability**

Job = *more reliable autonomous coding*. Packaging = **new plugin in monkey-skills** (host-driven). The full-harness build (B) and the onboarding bootstrap (A) are deprioritized; the command-surface seed (野心 B ④/⑤) stays parked — it is not the reliability lever.

### C-specific next forks (the next evaluation layer, before any build)

1. **Build vs adopt.**
   - *Build*: generalize the primitives we **already own** — `dogfood-skill-testing` (blind behavioral probes) + `distill-sessions` (mine past sessions) + the code-toolkit pressure-prompt/`tests/README` "file a dogfood note when a rationalization breaks through" loop — from **skills** to **coding tasks**. Highest fit with monkey-skills idioms; no external dep.
   - *Adopt*: [neosigmaai/auto-harness](https://github.com/neosigmaai/auto-harness) ("BYO agent + mine failures + optimize harness + gate regressions") / [AutoHarness](https://github.com/aiming-lab/AutoHarness). Faster, but external dep + idiom mismatch.
   - *Lean*: **build** (we own ~half the machinery; adoption's value is the failure-mining *pattern*, which is cheap to reimplement on our primitives).

2. **Where it lives.**
   - The failure-mining/eval primitives (`dogfood`, `distill`, `tuning`, `judge`) live in **`dev-workflow`** (the meta-toolkit). A coding-task reliability loop is arguably a `dev-workflow` skill, OR a **new `coding-evals` plugin**.
   - *Lean*: **new plugin** (`coding-evals` / `failure-mining`) — it needs its own commands + a per-run failure store + its own version line; cramming it into dev-workflow (meta-skill toolkit) blurs that plugin's "write skills" charter, just as auto-onboarding would blur code-toolkit's "write code" charter.

3. **Smallest end state (MVP).** A loop that: (a) runs a coding task under code-toolkit, (b) on a `requesting-code-review` / `verification-before-completion` **FAIL**, distills the failure into a **regression test** + a one-line "what broke through" record, (c) re-runs to confirm the gate now catches it. Smallest = a single skill that turns a *captured failure* into a *committed regression test* (the "accrete the eval" step) — the rest (scheduling, live-eval dashboards, score tracking) is later.

4. **Relationship to what shipped.** This is the natural *next beat after accretion*: v2 made the **command surface** a living artifact; C makes the **eval/test surface** a living artifact (failures accrete into regression tests). Same "living artifact" philosophy, different surface.

### Open question for the next session
Build-vs-adopt + home (new `coding-evals` plugin vs `dev-workflow` skill) + MVP scope — resolve via a focused brainstorm → plan when ready.
