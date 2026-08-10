# Brief: terminal-state gates — mandate the finishing flip, scan for stale ledgers, mechanize the squash-body check

Date: 2026-08-10
Origin: post-#681 defect review + two-language industry research (EN: spec-kit / claude-task-master / Kiro / OpenHands / Cline; JP: Fusic spec-completion hook, J-Tech disposable task files, hash-gate CI). Arc A of the user-directed two-arc goal「把 A 跟 B 都做完」.

## Problem

Two mechanism gaps keep regenerating drift the repo then has to sweep by hand:

1. **The terminal Stage flip is un-mandated.** Every intermediate stage has a
   flip duty (SDD flips waves, requesting-code-review flips review:round-N)
   but `finishing-a-development-branch` — grep "set-stage" = 0 hits — never
   instructs the flip to `finishing`. Today's doc-currency arc repaired two
   plans stranded mid-flight (all 9/9 tasks done, Stage still
   sdd:wave-1 / review:round-1, arcs merged in 0.65.2/0.66.0) — it fixed the
   data while this generator of the defect survived. Industry has NO
   "merged ⇒ terminal" mechanical invariant (research: none of spec-kit /
   task-master / Kiro / OpenHands enforce it); loom can exceed the field
   because it already owns the close-out choke point.
2. **The squash-body wipe defense is prose, n=4.** The web merge dialog
   cleared the PR body four times (#566, #641, #642, #681) past four CLI
   reminders. `memory-grep.sh --verify-merged HEAD` already DETECTS the
   loss (exit 4, "squash-shaped commit (#N) with title-only body") but
   only when a session happens to run it. (This paragraph originally
   named `--verify` — corrected after the T3 adjudication; End State #3
   records the full story.) Industry counterpart: the JP hash-gate CI
   pattern — make the divergence machine-observable and red, because
   "human attention (prose rules) gets broken".

## Users

kouko + every loom arc in this repo (the flip duty + scan), and every future
merge of this repo (the Action).

## Smallest End State

1. `finishing-a-development-branch`'s close-out sequence carries a
   **stage-flip duty**: before the close-out commit, run
   `plan_card.py <plan> --set-stage "finishing"` (two-tier resolution as
   everywhere) and stage the flip into the close-out commit; plans without
   progress headers skip loudly-silently per the existing card rules.
2. `plan_card.py` gains a **`--stale-scan <plans-dir>` verb**: lists plans
   whose tasks are ALL `done(...)` but whose `Stage:` is not `finishing`
   — the exact signature of today's two victims (one was sdd:wave-1, one
   review:round-1 — both all-done). Advisory by design (exit 0 with a
   listing; empty list prints a clean line): a plan legitimately sits
   all-done at review:round-N while its review runs, so red would
   false-positive on live parallel arcs. The finishing close-out table
   gains a row that runs the scan and relays its output loudly — stale
   ledgers surface at the NEXT close-out instead of months later.
3. The **existing post-merge workflow**
   (`.github/workflows/memory-verify-merged.yml` — discovered at
   implementation: it already runs `memory-grep.sh --verify-merged HEAD`
   on push to main and already went red on #681's wipe today, unseen)
   gains the missing half: on exit 4 it **comments on the merged PR**
   (carrier-loss fact, PR body as surviving carrier, the CLI merge
   prescription) before failing — a red light on main is not a
   notification; the PR comment is. Requires
   `permissions: pull-requests: write`. Exit 0 passes silently. (The
   originally drafted `--verify HEAD` flag was wrong — binary
   trailer-presence semantics that false-positive on legitimate
   trailer-less merges; `--verify-merged` is the wipe-shape detector,
   verified empirically on #681 vs a healthy #667.)
4. loom-code 0.71.0 → 0.72.0, codex manifest sync, version-pin migration,
   CHANGELOG.

## Current State Evidence

- Forward: finishing SKILL.md `grep -c set-stage` = 0 (live, 2026-08-10);
  rcr:85 flips review rounds; SDD §Delivery form flips waves.
- Reverse: `plan_card.py` (loom-code/scripts/, plugin-shipped since #680)
  already owns Stage parsing + `--set-stage` writes — the scan verb reads
  the same fields it already validates; no new file format.
- Error: today's victims prove the failure signature (all-done +
  non-finishing); the scan's false-positive class (live arcs at review) is
  why it is advisory, not red.
- Data: `memory-grep.sh:274-303` (`--verify-merged` section; wipe-shape
  exit-4 at :288-292) — the exact contract the workflow consumes; pure
  bash, CI-runnable.
- Boundary: finishing SKILL.md has no word-ceiling pin (checked — the
  extraction-pointer ceilings cover sdd/rcr only); Action lives at repo
  level (`.github/`), not inside a plugin, so no dev-workflow bump.

## Alternatives Considered

1. **Duty row + advisory scan + post-merge Action** (chosen) — flip duty
   kills the generator, scan catches legacy/lapsed cases at close-out,
   Action mechanizes the one prose rule with a 4-incident record.
2. Red (blocking) stale-scan in CI — rejected: all-done+review:round-N is
   a legitimate live state for a parallel arc; a red gate would teach
   people to ignore it (the false-positive → dismissed-gate spiral).
3. Fusic-style deletion of completed plan files — rejected for loom: plans
   double as the audit trail (Decision Logs, provenance); their insight
   ("a completed task file without a terminal marker is a liability")
   is satisfied by the flip duty instead.
4. Branch-protection/server-side squash-message enforcement — GitHub offers
   no hook that can block the merge dialog's body edit; post-merge
   detection + loud comment is the strongest available position (and the
   repo already sets the correct squash-message default, which the dialog
   overrides — documented in the n=4 incidents).

## Decision

Three mechanical pieces in one arc: the flip duty (skill prose + pin), the
scan verb (code + tests + close-out row), the Action (workflow + pin test).
Version chain 0.72.0.

We will NOT: make the scan red (advisory by design); touch arc-B scope
(init/scaffold verb — next arc); backfill the 182 old-format plans (no
Status ledgers → scan skips them by construction).

## Out of Scope

- Arc B (loom-init scaffolding verb + plugin-shipped charter templates).
- Any change to memory-grep.sh itself (the Action consumes its existing
  contract).
- Retrofitting Stage headers into pre-0.60.0 plans.

## Design-side on-ramp

Negative guard: mechanism hardening of existing tooling (bug-fix shaped) —
upstream-artifact walk skipped silently. Backlog ready check: read this
session (`## Now` empty; the user's two-arc goal IS the direction call).

## Open Questions

None blocking.
