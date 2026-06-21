# Root-cause tracing — Phase 2 ISOLATE sub-protocols

> Companion to [`../SKILL.md`](../SKILL.md). Decision aids for picking the right bisection axis in Phase 2.

The goal of ISOLATE is to narrow *"the bug is somewhere in the system"* to *"the bug lives in {this line / this function / this dependency / this input field}."* Bisection is the workhorse — at each step you cut the surface in half by an observation that distinguishes "bug here" from "bug not here."

## Picking the bisection axis

Walk this table from top to bottom; use the FIRST axis where you can answer the trigger column with *"yes."*

| # | Axis | Trigger | Tool | Halving cost |
|---|---|---|---|---|
| 1 | **Git bisect** | "Did this work in a recent past version?" | `git bisect` | log₂(N commits) — each step is "checkout + run repro" |
| 2 | **Dependency bisect** | "Did this break after upgrading a library?" | Pin known-good in `package.json` / `requirements.txt`, then binary-search published versions | log₂(N versions) — each step is "install + run repro" |
| 3 | **Input bisect** | "Does it fail for input X but pass for input X'?" | Shrink the input: remove half the rows / characters / fields until it stops failing, then narrow further | log₂(input size) — see [`character-encoding-debug.md`](character-encoding-debug.md) for byte-level shrinking |
| 4 | **Component bisect** | "Is the bug somewhere in a multi-stage pipeline?" | Insert observation points (logging / assertions) at module boundaries; the boundary where good-input becomes bad-output is the bug locus | log₂(N stages) — each step is one new observation point |
| 5 | **Time bisect** | "Does it work most-of-the-time but fail sometimes?" | Use [`condition-based-waiting.md`](condition-based-waiting.md) to bound the timing window; then bisect within the window | depends on race granularity |
| 6 | **5-Whys** | "The cause is non-code (process, data quality, deployment, human)?" | Walk the causation chain 5 layers deep — *"why did X happen? because Y. why did Y happen? because Z..."* | qualitative; stops when the layer is actionable |

If multiple axes apply, pick the cheapest halving step. Git bisect is usually fastest when the bug is regression-shaped; input bisect is usually fastest when the bug is data-shaped.

## Git bisect — sharp tips

- **Have a script repro before starting**. `git bisect run ./bug-script.sh` automates the halving completely. Without a script, you do `bisect good` / `bisect bad` manually — slower but works.
- **Skip merge commits when the bug is build-related**. `git bisect skip` is for commits that don't compile or are mid-merge.
- **Bisect against tags / known-good releases**, not arbitrary commits. The "known good" anchor matters more than the "known bad."
- **Time budget**: log₂(N) is fast on paper but each step takes minutes (checkout, install, run). For N=1000 commits, ~10 steps × 5 min = 50 min. If the bug surfaced after a feature branch merge, just inspect the merge diff first.

## Input bisect — when the bug is data-shaped

- **Halve the input by line / row / field**. The first failing half tells you which subset matters; the second halving narrows it further.
- **For encoded inputs**, hex-dump the failing input vs the working input — see [`character-encoding-debug.md`](character-encoding-debug.md). The byte-level diff is often the smoking gun.
- **Beware shrinking**: an input small enough to debug may be small enough that the bug class doesn't trigger. Property-based testing (Hypothesis / QuickCheck / fast-check) does this halving for you with shrinking built-in.

## Component bisect — when the bug is "somewhere in the pipeline"

- **Place observation points at module boundaries**, not inside modules. The boundary where good-input-becomes-bad-output is the bug locus.
- **Use assertions, not logging**, when possible. `assert payload.valid()` at each stage is a fail-fast bisector. Logging requires you to read logs; assertions force the failure to the right stage.
- **Don't observe inside performance-critical loops** — instrumentation cost can mask timing bugs (perversely making the bug disappear).
- **For distributed pipelines**, the boundaries are network calls. Capture request/response at each hop (correlation ID essential).

## 5-Whys — when the cause is non-code

The 5-Whys protocol (Sakichi Toyoda, Toyota Production System) walks causation backwards from the symptom 5 layers:

```
1. Why did the user see <symptom>?
   → because <immediate cause>
2. Why did <immediate cause> happen?
   → because <upstream cause>
3. Why did <upstream cause> happen?
   → because <further upstream>
4. Why did <further upstream>?
   → because <process / data / human factor>
5. Why did <process / data / human factor>?
   → because <root>
```

You don't always get to 5 — 3 or 4 layers may already reach actionable root. You also don't STOP at code: many bugs ladder up to *"the spec didn't say what to do here"* (use `brainstorming` to fix the spec) or *"the deploy step was wrong"* (use `dev-workflow:git-memory` to record the deploy-fix decision).

**Anti-pattern**: stopping at *"the developer made a mistake."* That's true and useless. Walk one more layer — *why* did the developer make this mistake? Usually: missing test, ambiguous spec, no observability. Each is actionable.

## Bisection anti-patterns

- ❌ **Bisecting without a repro.** You cannot halve unless you can test each midpoint. Fix Phase 1 first.
- ❌ **Trinary search.** Cut in half, not in thirds. The whole value of binary search is the log₂ factor.
- ❌ **Mixing axes mid-bisect.** Pick one axis. If git bisect surfaces "the regression is in commit X" but the actual bug is in input Y that only triggers under commit X, switch to input bisect from Y — don't keep narrowing git.
- ❌ **Trusting "the commit that broke it" as the root cause.** That commit *exposed* the bug; the bug may be older latent code. Always verify by reading the commit before declaring root cause.
- ❌ **5-Whys producing 5 layers of speculation.** Each "why" must be answered with evidence (log, test, document, interview), not guess.

## See also

- [`../SKILL.md`](../SKILL.md) — the 4-phase framework these axes serve.
- [`condition-based-waiting.md`](condition-based-waiting.md) — for time-axis bisection (race / heisenbug).
- [`character-encoding-debug.md`](character-encoding-debug.md) — for input-axis bisection on encoded inputs.
- `dev-workflow:complexity-critique` — when ISOLATE reveals the bug lives in a too-tangled module, refactor-before-fix may be the better path.
