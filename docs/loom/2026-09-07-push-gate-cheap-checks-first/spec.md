# Cheap checks before push executables — spec
intent: 2026-09-07-push-gate-cheap-checks-first@7d1ec6a6
pre-build-review: not-required — the change preserves every existing rule and executable check while making one precise ordering guarantee; full branch-end review still recomputes the resulting gate behaviour

## Requirements
REQ-1 — Deterministic blockers short-circuit executables
  IF any push rule that can be decided without running the package suite or an adversarial probe blocks, THEN the push checker shall report the accumulated deterministic failures and shall not start either class of executable → Acceptance #1

REQ-2 — Valid pushes retain executable coverage
  WHEN every deterministic preflight check passes, the push checker shall execute the resolved complete package-test command exactly once unless the existing explicit skip applies, then execute the existing adversarial probes, and release only after all required executables pass → Acceptance #2

REQ-3 — Executable side effects still fail closed
  IF package or adversarial execution fails, moves the selected repository's HEAD, changes its index or working tree, or changes its effective Git configuration, THEN the push checker shall preserve the existing BLOCK outcome and shall not release the push → Acceptance #3

REQ-4 — Repository-neutral ordering
  WHERE a repository adopts the Loom checker contract, the preflight boundary shall be derived from existing deterministic rule behavior rather than source paths, languages, frameworks, or filename extensions → Acceptance #4

## Design decision
- agent-decided — Compute every non-executable rule before taking the pre-execution repository snapshot, then return once if any such rule failed. This creates one explicit phase boundary and avoids scattering conditional guards around individual checks.
- agent-decided — Preserve the package-then-adversarial execution order and the single post-execution repository recompute. The intent removes wasted execution on an already-blocked push, not either executable safety check.
- agent-decided — Treat the live-HEAD check required by `--require-live-head` as deterministic preflight and place it before the early return. It reads repository state but runs no untrusted executable.
- agent-decided — Keep the existing failure texts and rule identifiers. Tests should assert both zero executable invocations on a deterministic block and unchanged positive/mutation behavior.

## Alternatives considered
- Leave late checks in place and guard only the package suite — rejected because adversarial probes would still run on a push already known to be blocked and the phase boundary would remain implicit.
- Run deterministic checks after executables but cache a successful suite — rejected because cache identity and invalidation add a new trust mechanism while the known failure was already decidable without execution.
- Stop on the first deterministic failure — rejected because the checker currently reports accumulated failures and preserving that feedback avoids creating additional fix-and-retry rounds.

## Current state evidence
- Forward: `loom-code/scripts/loom_checker.py` function `_cmd_push` validates the review shape, then snapshots the repository and invokes `check_probes_package_tests` and `check_probes_adversarial`.
- Reverse: `.codex/hooks/loom-checker` invokes `loom_checker.py push --hook` for an intercepted push, while direct checker calls reach the same `_cmd_push` function.
- Error: `loom-code/scripts/loom_checker.py` calls `parse_dispatch`, `check_verdicts`, `check_second_vendor_honoured`, `check_dispatch_covers_tasks`, `check_frozen_store_untouched`, `check_reviewer_ne_implementer`, and `check_dismissed_by_reviewer` only after package and adversarial execution.
- Data: `docs/loom/<change-id>/review.json` supplies the committed dispatch, verdict, finding, probe, and reviewed-SHA records consumed by these recomputes.
- Boundary: `loom-code/scripts/loom_checker.py` functions `check_probes_package_tests` and `check_probes_adversarial` own executable validation; their command resolution and failure semantics remain unchanged.

## UI flows
N/A — this engineering change adds no command, argument, output format, or user interface; it changes only whether existing external programs start after an existing deterministic BLOCK is already known.
