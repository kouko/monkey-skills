# loom-code script helper extraction (Phase 1) — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-31
> **Author**: agent (Claude), from a three-plugin script audit run this session; user (kouko) ratified plugin-level sharing and the "characterization tests first" ordering

## Design-side on-ramp

not fired — refactor of existing scripts under existing test coverage; the negative guard skips the upstream-artifact walk. Backlog ready check ran (0 bet / 8 open, none about these files). Live-map check: `family-relocation` is live (state claimed, next CTA research ticket `task-inventory-consumers`); its inventory names `loom_gate_markers` and `plan_card` as relocation candidates, so this brief carries a portability constraint (see Decision) instead of resuming the map.

## Queue relation

unqueued — no live bet entries exist (0 bet / 8 open); the arc originates from this session's script audit, not from a backlog entry.

## Problem

When a git-invocation bug is fixed in one loom-code script (as PR #769's UTF-8 argv fix was, in `batch_review_cli.py` only), I want the fix to reach every git call in the plugin, so that the other five copies of the same wrapper do not keep the bug silently. Today the wrapper is copy-pasted six times with three different failure semantics, and none of the failure paths is tested.

## Users

- loom-code maintainers (kouko + agents editing `loom-code/scripts/`) — fix a git-call defect once; must not have to grep for sibling copies.
- SDD implementers dispatched into `loom-code/scripts/` — need one documented way to run git and one documented way to load a sibling module, instead of choosing which of six/five copies to imitate.
- Adopting repos running the hooks (`language-anchor.py`, `language-stop-check.py`) — the hooks are live in `hooks.json` with zero tests; a regression there blocks every Stop event.

## Smallest End State

When this ships, all of the following hold:

- Each of the six git wrappers has a characterization test pinning its current failure behavior against the unchanged code (non-zero exit; git binary missing; timeout where the wrapper handles it).
- A single `git_exec.py` in `loom-code/scripts/` provides the wrapper body; each call site keeps its observable behavior — same return value on success, same exception type or `None` on failure, same timeout.
- Because the body is shared, the UTF-8 argv/decoding handling that only `batch_review_cli.py` has today applies to all six.
- The five sibling-module loaders in `scripts/` collapse to one helper.
- The two language hooks and `lang_detect.py` have tests covering their documented contract.
- Success criteria: all existing suites stay green (loom-code 2075 passed at baseline) and the new tests pass. Non-criteria: no line-count target; no behavior change at any call site beyond the UTF-8 handling.

- BI-1 — Characterization tests pin the failure-path behavior of the six git wrappers (`batch_review_cli._run_git`, `live_gate_station_receipt._git`, `live_host_review_gate._git`, `loom_gate_markers._git`, `review_context._git`, `review_scope._git`) and pass against the current code before any extraction.
- BI-2 — One shared module `loom-code/scripts/git_exec.py` supplies the git wrapper body; every one of the six call sites keeps its observable success and failure behavior (return value, exception type, timeout).
- BI-3 — The UTF-8 argv-as-bytes and `encoding="utf-8", errors="surrogateescape"` decoding from `batch_review_cli._run_subprocess` applies to every git call routed through `git_exec.py`, with a RED test per adopting wrapper for a non-ASCII path under a C locale.
- BI-4 — One shared sibling-loader helper in `loom-code/scripts/` replaces the five `spec_from_file_location` bodies in `scripts/` (`batch_review_cli._load`, `task_batch_replay._load`, `plan_card._review_batch_oracle`, `review_batch._review_batch_oracle`, `propose_review_batches._oracle`), preserving each site's unique module name and exception type.
- BI-5 — `hooks/language-anchor.py`, `hooks/language-stop-check.py`, and `hooks/lang_detect.py` have tests covering their documented contract: ja/zh majority → directive or block; en / None / malformed input → no output, exit 0; the stop-check `max(10, 0.05 × visible_len)` threshold at its boundary.

## Current State Evidence

- **Forward**: `loom_gate_markers._show_committed_file` and `default_branch_ref` consume `_git`'s `None` as "no such ref / not a repo" control flow (`loom-code/scripts/loom_gate_markers.py`, `"Run git in \`repo\`; return stripped stdout, or None on any failure."`); `live_host_review_gate.py` catches only the timeout (`except subprocess.TimeoutExpired as error`, line 535) and lets `CalledProcessError` propagate; `batch_review_cli._run_git` converts any non-zero exit to `PacketRefused(f"git {' '.join(args)} failed: …")`.
- **Reverse**: the six wrapper hosts are reached from every review/gate skill (`requesting-code-review`, `requesting-docs-review`, `subagent-driven-development`, `finishing-a-development-branch` cite `loom_gate_markers.py` / `review_scope.py` / `batch_review_cli.py` by filename); the test suites define their own repo-building `_git` helper (`def _git(` in `test_loom_gate_markers.py`, `test_review_scope.py`, `test_review_context.py`, `test_live_gate_station_receipt.py`) and never import the production `_git`, so the private name is free to move. `hooks/hooks.json` wires `language-anchor.py` on `PostToolUse` matcher `Skill` and `language-stop-check.py` on `Stop`.
- **Error**: three failure families today — (A) `batch_review_cli._run_git` → `PacketRefused` via `_run_subprocess` (which also maps `TimeoutExpired` → `PacketRefused`, docstring "folds what were three separate TimeoutExpired->PacketRefused copies"); (B) `live_gate_station_receipt._git` / `live_host_review_gate._git` → `check=True, timeout=20`, raise `CalledProcessError` / `TimeoutExpired`; (C) `loom_gate_markers._git` / `review_context._git` → `None` on `OSError` or non-zero exit, `review_scope._git` additionally `None` on `TimeoutExpired` with an optional `timeout`. No test exercises any of these failure branches (grep for non-git `tmp_path` / `CalledProcessError` in the six test files: 0 tests).
- **Data**: stripped stdout `str` in families B and C; unstripped stdout in A; `batch_review_cli._committed_bytes` calls `_run_subprocess(..., text=False)` and its caller requires raw `bytes` — the shared module must keep a bytes path. Loader sites register the module under a unique name (`"plan_card_review_batch_oracle"`, `"review_batch_schema_oracle"`, `"propose_review_batch_oracle"`) in `sys.modules`.
- **Boundary**: `[FRAGILE]` process locale — `_run_subprocess` docstring: `encoding="utf-8", errors="surrogateescape"` chosen because `text=True` decodes with `locale.getencoding()`; PR #769 (`24f21dbb`) applied this to `batch_review_cli.py` only (`git show --stat`: one production file). `[ASYNC]` `timeout=20` in family B, caller-supplied in `review_scope`. `[FRAGILE]` plugin isolation — `hooks/` and `scripts/` are separate import roots; a helper in `scripts/` is not importable from `hooks/` by sibling import (`loom-code/hooks/git-guard.py`, `"The check_onramp_choice module from this hook's sibling"` — a documented path-based load, not an import).
- **Evidence paths**: `loom-code/scripts/batch_review_cli.py` (`def _run_subprocess`, `def _run_git`, `def _load`); `loom-code/scripts/live_gate_station_receipt.py` (`def _git`); `loom-code/scripts/live_host_review_gate.py` (`def _git`, `except subprocess.TimeoutExpired as error`); `loom-code/scripts/loom_gate_markers.py` (`def _git`); `loom-code/scripts/review_context.py` (`def _git`); `loom-code/scripts/review_scope.py` (`def _git`); `loom-code/scripts/plan_card.py` (`def _review_batch_oracle`); `loom-code/scripts/review_batch.py` (`def _review_batch_oracle`); `loom-code/scripts/propose_review_batches.py` (`def _oracle`); `loom-code/scripts/task_batch_replay.py` (`def _load`); `loom-code/hooks/hooks.json` (`language-anchor.py`, `language-stop-check.py`); `loom-code/hooks/language-anchor.py` (module docstring); `loom-code/hooks/language-stop-check.py` (module docstring, `max(10, 0.05 × visible_len)`); `loom-code/hooks/lang_detect.py` (`def conversation_language`, `def majority_language`, `def is_harness_injection`); `loom-code/hooks/git-guard.py` (`The check_onramp_choice module from this hook's sibling`); `loom-code/scripts/heading_window.py` (module docstring on per-plugin copies); `docs/loom/maps/family-relocation/tickets/task-inventory-consumers.md`; git commit `24f21dbb`.

## Decision

We will add characterization tests first, then extract two helpers inside `loom-code/scripts/` only: `git_exec.py` (one function with a `check`-style switch mirroring stdlib `subprocess.run`, plus a bytes path) and a sibling-loader helper. Each call site keeps its exception type or `None` contract by adapting at the call site, never by changing callers. We apply the UTF-8 handling uniformly because a shared body that still differs per site would defeat the purpose.

We will NOT unify the three failure families into one, NOT package-ify `scripts/`, and NOT touch the hooks' two loader copies (different import root).

Portability constraint from the live map: `git_exec.py` and the loader helper are small, dependency-free modules that a relocated script (`loom_gate_markers`, `plan_card`) takes as its own per-plugin copy, following the `heading_window.py` precedent — no cross-plugin import is introduced.

- BI-6 — Phase 1 ships as one loom-code PR (patch version bump): characterization tests, `git_exec.py`, sibling-loader helper, hook tests; the six wrapper bodies and five loader bodies are deleted in the same PR.

## Out of Scope

- Unifying the raise / `None` failure semantics across call sites (a behavior change; callers use `None` as control flow).
- `loom-workflow` decision-map symlink-guard extraction and `claim_ticket.py` disposition (Phase 2, separate PR and plugin).
- Splitting `loom_gate_markers.py` or `batch_queue.py` (Phase 3, separate branches).
- The hooks' two `_load_lang_detect` copies (different import root from `scripts/`; 5 lines each).
- Cross-plugin sharing of any helper (`heading_window.py`, `_load_lang_detect`, `resolve_repo_root`) — user-ratified plugin independence, and official plugin docs forbid out-of-root references.
- Filename hyphen/underscore normalization.
- Any change to `batch_review_cli._run_subprocess`'s `TimeoutExpired → PacketRefused` mapping beyond routing it through the shared body.

## Alternatives Considered

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| Unify all six to raise on failure (stdlib `subprocess.run(check=True)` precedent) | Python stdlib — https://docs.python.org/3/library/subprocess.html (EN) / https://docs.python.org/ja/3/library/subprocess.html (JA); both agree | Three call sites treat `None` as "not a repo / no such ref" control flow; unifying changes behavior the characterization tests exist to preserve. The `check` switch is adopted; the unification is not. |
| Keep the six copies and add a lockstep AST test (as `loom-design`'s `mint_critic_verdict.py` does) | This repo — `loom-design/scripts/interface/test_mint_critic_verdict.py` `test_lockstep_code_matches_ssot` | The copies are legitimately different (three families); lockstep can only assert identity, and it would not deliver the UTF-8 fix to the other five. |
| Package-ify `scripts/` (`__init__.py`, relative imports) to remove the loader idiom | pytest maintainers' recommendation — https://github.com/pytest-dev/pytest/issues/8964; pytest import-mode docs https://docs.pytest.org/en/stable/explanation/pythonpath.html | Skills and `hooks.json` invoke scripts by path (`python3 scripts/x.py`); relative imports break direct execution, and pytest's own docs state `importlib` mode cannot do sibling imports, which is exactly why the loader exists. |
| Golden-master / approval snapshots instead of hand-written characterization asserts | Feathers, *Working Effectively with Legacy Code* — https://michaelfeathers.silvrback.com/characterization-testing (EN); ゴールデンマスター法 — https://comcomponent.com/knowledge/golden-master-testing/ (JA); EN/JA agree | Wrapper output is git-state dependent and noisy; what must be pinned is exception type / `None` / timeout, which explicit asserts state directly. Feathers' seam-then-pin workflow is followed; the snapshot mechanism is not. |

## What Becomes Obsolete

- BI-7 — The six inline git wrapper bodies (`_run_git` in `batch_review_cli.py`; `_git` in `live_gate_station_receipt.py`, `live_host_review_gate.py`, `loom_gate_markers.py`, `review_context.py`, `review_scope.py`) are deleted in the same PR, each replaced by a one-line delegation to `git_exec.py`.
- BI-8 — The five inline loader bodies in `scripts/` (`_load` ×2, `_review_batch_oracle` ×2, `_oracle`) are deleted in the same PR, each replaced by a call to the shared loader helper.

## Open Questions

(empty)

## Diagrams

N/A — no flow/state/architecture-shaped content: the change is six-copies-to-one and five-copies-to-one within a single directory, fully stated by the Error sub-bullet's three-family table; no control flow or state changes.
