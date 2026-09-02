---
name: maintain
description: |
  Turns a failing CI run, production alert, bug report, regression, or dogfood incident into evidence on an existing open intent, or a new intent with originator maintenance-loop, and turns the incident into a permanent eval in mechanisms.yaml.
version: 1.0.0
---

## What this skill does

`maintain` is the supply side of the admission rule (concept-model §11: "事故 → memory → eval → 才考慮 hook"). It never designs or codes a fix. It does two things only: (1) route the incident onto the intent it belongs to — an existing open one, or a fresh one it opens — and (2) make sure the incident leaves a permanent regression case behind, so the next occurrence is caught mechanically instead of by another alert.

Everything downstream — Problem/Acceptance confirmation, spec, tasks, the fix itself — belongs to `write-plan` and the stations after it. This station's own output is an `intent.md`, never a diff.

## 0. Contract check

Run once, before anything else:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py contract --require 1.0
```

(Codex form: `python3 .codex/hooks/loom_checker.py contract --require 1.0`.)

Exit 0 continue; non-zero, stop and report the contract mismatch — do not work around it.

On Codex, if `.codex/hooks/loom_checker.py` does not exist, **stop**: run
`loom-code:write-plan` step 0b (the scaffold and its trust probe) first. Do not produce any
artifact without the checker. The file existing is not proof the hook runs:
an untrusted Codex hook is skipped in silence, and step 0b's trust probe is
what tells the two apart.

## 1. Identify the incident

Write a one-line title for the incident and derive its slug (lowercase, hyphens, no punctuation — the same slugging rule `capture-intent`/`write-plan` use for `<change-id>`). Capture the incident's own identifier as `evidence`: the alert id, the CI run URL, the failing test's fully-qualified name, or the bug report's URL/path. This is the value that later dedupe checks compare against — write it down before doing anything else, it is not reconstructable from memory.

## 2. Dedupe rule (mechanical, no judgment)

<!-- gate: maintain.dedupe -->
An intent is **"the same" as this incident** iff either holds:

- the intent file's slug (its filename under `docs/loom/intent/`, minus `.md`) equals the incident slug from step 1, or
- the intent's `evidence:` frontmatter list already contains this incident's alert id (exact string match).

Search only files under `docs/loom/intent/` whose `status:` line reads `open` or `confirmed <date>` (a missing `status:` line defaults to open per §2b). Skip any intent whose `status:` reads `withdrawn — <reason>` — a withdrawn intent is closed and cannot receive new evidence.

If a match is found:

1. Append the new evidence path (e.g. `docs/loom/evidence/incidents/<date>-<slug>.md`, or the alert id itself if no file is written) to that intent's `evidence:` list.
2. Commit: `docs(loom): intent <id> evidence <alert>`.
3. Do **not** open a second intent for the same incident. Go straight to step 4.

This rule is deliberately mechanical — filename-slug or evidence-string match, nothing else — so no agent judgment call decides "is this the same problem" (concept-model §7: decisive layer recomputes, it doesn't trust a claim). If the match is genuinely ambiguous (e.g. a plausible but not exact slug), treat it as no match and open a new intent; a spurious second intent costs a merge later, a wrongly-merged one hides a real second problem.
<!-- /gate -->

## 3. Otherwise: write a new intent

Copy `${CLAUDE_PLUGIN_ROOT}/contract/templates/intent.md` to `docs/loom/intent/<slug>.md` and fill it in:

- `originator: maintenance-loop`
- `kind: engineering` unless the incident is user-visible behaviour (a broken screen, a wrong API response, a UX regression) — then `kind: product`
- `needs-design:` per concept-model §2b: `yes` when the fix touches a user-facing interface surface with no DESIGN.md/ui-flows coverage, or is multi-state/multi-object behaviour with no spec; otherwise `no — <reason>`. The reason is required either way.
- `evidence: [<paths>]` — the alert id / URL / test name from step 1, plus any incident write-up path from step 4
- `status: open`
- **Problem**: what broke and who is affected, in plain language (product intents: no file paths, code identifiers, or script filenames — the checker rejects these)
- **Proposed outcome**: the shape of "fixed", not the fix's implementation
- **Acceptance**: "the incident's reproduction no longer fails" (the failing test passes, the alert's check passes, the reported repro no longer reproduces) — state the concrete reproduction so a blind-run agent can rerun it
- **Constraints**, **Out of scope**, **Open questions**: as usual; Constraints should note anything the fix must not break (the thing the incident already broke once)

Run the checker before committing:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py intent docs/loom/intent/<slug>.md --commit-msg <path-to-commit-msg-file>
```

Fix any `BLOCK intent.*` finding, then commit. The commit message must carry the same `needs-design:` line verbatim (checker rule `intent.needs-design-reason`).

## 4. Eval: turn the incident into a permanent case

Identify which mechanism should have caught this before it reached an alert — a skill, a checker rule, a hook, a contract manifest field, or a prose gate (a `<!-- gate: … -->` paragraph). Check `docs/loom/evidence/mechanisms.yaml` for its entry.

- **A mechanism is responsible**: extend or tighten that mechanism's `eval:` with a concrete regression case — a new test if it's a checker rule or script, a new attack/edge case file under `docs/loom/evidence/` if it's a gate, or a cold-read scenario if it's a skill's prose. Create the case file when the eval is an attack case (it must be executable or replayable, not a description of one). Commit: `test(loom): eval for <mechanism> from <incident>`.
- **No mechanism is responsible** (this was a genuinely new failure mode nothing was built to catch): do not propose a new mechanism here — that decision belongs to `write-plan`/§11's admission rule, which weighs the net-count cost. Instead, record the incident under `docs/loom/evidence/incidents/<date>-<slug>.md` (what happened, how it was found, why no existing mechanism covers it) and commit: `docs(loom): incident <slug>` — leave the "should we add a mechanism" call to write-plan, which reads this file as evidence.

Either branch runs; never both, and never skip both — an incident with no eval and no incident record is a supply-side leak (concept-model §6: "目錄累積＝continuous evals").

## 5. Hand off

Point the user (or the next automated pass) at `loom-code:write-plan` with the intent's path. Decision point ① — the plain-language Problem/Acceptance restatement and the user's confirmation — runs there, not here: a `maintenance-loop`-originated intent still needs the user's "yes" before `write-plan` will pick it up (checker rule `intake.confirmed`). If step 2 only appended evidence to an existing confirmed intent, no new decision point is needed — the intent was already confirmed; `write-plan` will re-triage it with the new evidence on its next pass.

## Station summary

| station | artifact | who decides | checker | checkpoint |
|---|---|---|---|---|
| capture-intent | intent — `docs/loom/intent/<change-id>.md`; `PRINCIPLES.md` and `DESIGN.md` at the repo root are side outputs of the tools it calls | user — decision point ① | `intent.schema`, `intent.product-no-identifiers`, `intent.needs-design-reason`, `intent.needs-design-recompute` | N/A |
| write-spec | spec — `docs/loom/<change-id>/spec.md` | user — decision point ②, product only | `intake.confirmed`, `standing.product-principles-reject` | spec lens must pass before a plan exists |
| write-plan | plan — `docs/loom/<change-id>/plan.md` | agent-decided (runs ① itself when loom-design is absent) | `intake.confirmed`, `intake.confirmed-behavior`, `intake.spec-pass`, `intake.after-task-budget` | calls review with scope `spec` |
| build | diff — commits on the change branch, one `Task: <id>` trailer each | agent-decided | none during build; writes the `dispatch[]` the push rules read | wave end when the unreviewed delta exceeds 8 files or 400 lines; immediately after an `after-task` task; ≤5 checkpoints during build, NEEDS_REVISION fix rounds not counted; branch end always |
| review | review — `docs/loom/<change-id>/review.json`, and `docs/loom/<change-id>/blind-run-report.md` from the blind run | two or more fresh-context reviewers; no averaging | `push.verdicts-ge-2`, `push.reviewer-ne-implementer`, `push.dismissed-by-reviewer`, `push.open-findings-closed`, `push.second-vendor-honoured` | `branch-end` always runs |
| ship | diff / PR — the pushed change branch and its pull request | user — decision point ③, reads the blind-run report | `push.review-only-head`, `push.reviewed-sha`, `push.review-schema`, `push.probes-package-tests`, `push.probes-adversarial`, `push.dispatch-covers-tasks`, and every review rule above, re-run at push | before push; a missing `branch-end` pass sends the change back to review |
| maintain | intent — a fresh `docs/loom/intent/<change-id>.md` | agent (dedupe is mechanical) | `intent.schema`, `intent.needs-design-reason`, `intent.needs-design-recompute`, `intent.product-no-identifiers` on a new intent | before hand-off to write-plan |

