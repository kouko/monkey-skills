# decision-map script cleanup (Phase 2) — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-31
> **Author**: agent (Claude), continuing the three-plugin script audit whose Phase 1 shipped as loom-code 0.108.1 (PR #771); user (kouko) ratified deleting `claim_ticket.py` after reading its evidence logic

## Design-side on-ramp

not fired — refactor and deletion under existing test coverage; the negative guard skips the upstream-artifact walk. Backlog ready check ran (0 bet / 10 open, none about these files). Live-map check: `family-relocation` is live (state active, two claimed tickets); its scope is hook relocation, not decision-map's own scripts, so this brief does not resume it.

## Queue relation

unqueued — no bet entries exist (0 bet / 10 open); the arc originates from the audit session's Phase 2 list, not from a backlog entry. The brief files new backlog entries (BI-13…BI-17) rather than consuming any.

## Problem

When a path-safety rule in decision-map's store is tightened or found wrong, I want the fix to land once, so that the three byte-identical copies of the symlink guard in `map_store.py`, `map_lock.py`, and `map_transaction.py` cannot drift apart silently. Separately, when I read `map-format.md`'s promise that a stale claim can be reclaimed, I want the store to actually do what the format says, so that a session does not act on a documented behavior that no entry point reaches and whose only success path needs a claim commit dated before the claim itself.

## Users

- loom-workflow maintainers (kouko + agents editing `loom-workflow/skills/decision-map/scripts/`) — one guard body to fix; three modules keep their own exception types.
- A single user running several worktrees against one Map — must not be offered a reclaim tool whose git evidence sees only the current checkout, so a ticket being worked in a sibling worktree can look stale.
- Future arc planners reading `docs/loom/BACKLOG.md` — need Phase 3 and the multi-worktree Map gap recorded where `backlog_index.py --ready` can surface them.

## Smallest End State

When this ships, all of the following hold:

- One guard body exists (in `map_lock.py`, the leaf module the other two already import), taking the exception class to raise; `map_store` and `map_transaction` keep their private names as one-line delegations so their external private-name callers (`map_lifecycle.py`, `migrate_map_v3.py`) and all 54 existing symlink assertions stay unchanged.
- `scripts/claim_ticket.py` and `scripts/test_claim_ticket.py` are gone; nothing else imports them.
- `references/map-format.md` and living-spec `REQ-97` say claims are not transferable and that abandonment goes through Withdrawal (`withdrawn-from: claimed`); `docs/loom/INDEX.md` is regenerated so the living-spec gate stays green.
- Four backlog entries exist and appear under `## open` in `docs/loom/BACKLOG.md`.
- Success criteria: `python3 -m pytest loom-workflow/skills/decision-map/scripts -q` stays green (254 passed at baseline, minus the 4 deleted reclaim tests, plus the new ones); loom-code's living-spec index check passes. Non-criteria: no line-count target; no change to what any guard accepts or rejects.

- BI-1 — `map_lock.py` exposes one public `assert_no_symlink_components(path, error=MapLockError)` whose raised exception class is the caller's choice; a RED test passes a custom exception class and receives it.
- BI-2 — `map_store._assert_no_symlink_components` is a one-line delegation raising `SchemaViolation`; `map_lifecycle.py` and `migrate_map_v3.py` keep calling the private name unchanged.
- BI-3 — `map_transaction._assert_no_symlink_components` is a one-line delegation raising `CloseTransactionError`.
- BI-4 — `scripts/claim_ticket.py` and `scripts/test_claim_ticket.py` are deleted; `grep -rn claim_ticket\.` over `loom-workflow/` finds only `map_transaction.claim_ticket` (the first-claim function, unrelated).
- BI-10 — `references/map-format.md` §Status and graph replaces the `Reclaim is conservative` sentence with: a claim is not transferable, and an abandoned claimed Ticket leaves `claimed` only through Withdrawal (`withdrawn-from: claimed`).
- BI-11 — Living-spec `docs/loom/outcome-map-v3/specs/outcome-map/spec.md` `REQ-97` is retitled `Claims are not transferable` with scenarios stating that a second claim on a claimed Ticket is refused and that abandonment goes through Withdrawal; the id is kept, the two reclaim scenarios are removed.
- BI-12 — `test_map_transaction.py` carries a test tagged `# @req: REQ-97` asserting `map_transaction.claim_ticket` refuses a Ticket whose status is already `claimed` and leaves its `claim:` line unchanged.
- BI-13 — Backlog entry `2026-08-31-loom-gate-markers-split` (loom-code `loom_gate_markers.py`, 1389 lines, three responsibilities: git/marker I/O, verdict parsing, CLI) with `status: open` and an `event` start trigger.
- BI-14 — Backlog entry `2026-08-31-batch-queue-split` (loom-design `batch_queue.py`, 1369 lines, six responsibilities) with `status: open` and an `event` start trigger.
- BI-15 — Backlog entry `2026-08-31-loom-design-unified-pytest-root` (per-directory CI pytest jobs in `loom-siblings-ci.yml` and siblings → one root) with `status: open` and an `event` start trigger, citing the closed entry `2026-07-30-pytest-module-name-collision-loom-code-scripts-distribute-py-vs-obsidian` as the related module-identity diagnosis.
- BI-16 — Backlog entry `2026-08-31-map-claims-collide-at-merge-not-runtime` (a Map is a committed file; `map_lock` serializes one checkout only; two worktrees' claims meet as a git conflict) with `status: open` and an `event` start trigger.
- BI-17 — `docs/loom/BACKLOG.md` is regenerated by `scripts/backlog_index.py` after the four entries exist and `scripts/backlog_index.py --validate` exits 0.
- BI-7 — loom-workflow ships as one PR with a patch version bump (3.1.0 → 3.1.1) in both plugin manifests and a CHANGELOG entry.

## Current State Evidence

- **Forward**: the guard walks each path component and raises on the first symlink (`loom-workflow/skills/decision-map/scripts/map_store.py`, `"refusing mutation through symlink component: {current}"`); `map_lock.py` and `map_transaction.py` carry the same loop with `"refusing path with symlink component: {current}"` raising `MapLockError` / `CloseTransactionError`. `claim_ticket.reclaim` refuses when the ticket's last git change date is on or after the claim date (`claim_ticket.py`, `"ticket has a post-claim or same-day ambiguous Git change"`), which every real claim commit satisfies.
- **Reverse**: import direction is `map_transaction → map_store → map_lock` (`map_transaction.py` `import map_lock` / `import map_store`; `map_store.py` `import map_lock`; `map_lock.py` imports no sibling), so `map_lock.py` is the only home that needs no new edge. External callers of the private name: `map_lifecycle.py` (`map_store._assert_no_symlink_components(brief_path)`), `migrate_map_v3.py` (two calls), `claim_ticket.py` (deleted here). `claim_ticket.py` has no caller outside `test_claim_ticket.py` (`import claim_ticket  # noqa: E402`); `SKILL.md` §Claim and `map-format.md` name `map_transaction.claim_ticket(...)`, a different function.
- **Error**: three exception types are the only difference between the copies: `SchemaViolation` (map_store), `MapLockError` (map_lock), `CloseTransactionError` (map_transaction). Tests pin those types through 54 `symlink` assertions across `test_map_store.py`, `test_map_transaction.py`, `test_delivery_binding.py`, `test_map_progress.py`, `test_start_delivery.py` — none imports the private guard name directly. `test_claim_ticket.py`'s only success case builds its repo with `commit_date="2026-07-01"` against `claim: alice, 2026-08-01` (`def _repo(`), a claim commit predating the claim by a month.
- **Data**: the guard takes a `Path`, calls `.absolute()`, and walks `parts[1:]`; no return value. Living-spec `REQ-97` (`spec.md`, `"### Requirement: REQ-97 — Stale claims have conservative recovery"`) is tagged by 4 `# @req: REQ-97` lines in `test_claim_ticket.py` and, per `docs/loom/INDEX.md` `### REQ-97`, by six `test_atomic_exchange_*` tests in `test_map_store.py`, so the requirement keeps tags after the deletion but its text no longer matches any behavior.
- **Boundary**: `[FRAGILE]` `docs/loom/INDEX.md` is CI-verified byte-for-byte against a regeneration (`loom-code/scripts/test_check_living_spec_index.py`, `"--verify-index <path>"`); deleting tagged tests without regenerating fails the gate. `[FRAGILE]` `docs/loom/BACKLOG.md` is `GENERATED by scripts/backlog_index.py — do not edit by hand`. `[ASYNC]` `map_lock.py` holds the `fcntl` writer lock per Map directory (`"Descriptor-safe Map-local serialization shared by all store writers."`) — it serializes writers on one checkout only; a Map in `docs/loom/maps/` is a committed file, so two worktrees each hold their own copy and claims meet only at merge.
- **Evidence paths**: `loom-workflow/skills/decision-map/scripts/map_store.py` (`def _assert_no_symlink_components`); `loom-workflow/skills/decision-map/scripts/map_lock.py` (`def _assert_no_symlink_components`, `class MapLockError`); `loom-workflow/skills/decision-map/scripts/map_transaction.py` (`def _assert_no_symlink_components`, `def claim_ticket`); `loom-workflow/skills/decision-map/scripts/map_lifecycle.py`, `migrate_map_v3.py` (`map_store._assert_no_symlink_components`); `loom-workflow/skills/decision-map/scripts/claim_ticket.py` (`def reclaim`, `def _git`); `loom-workflow/skills/decision-map/scripts/test_claim_ticket.py` (`def _repo(`, `# @req: REQ-97`); `loom-workflow/skills/decision-map/references/map-format.md` (`Reclaim is conservative`); `loom-workflow/skills/decision-map/SKILL.md` (`### Claim`); `docs/loom/outcome-map-v3/specs/outcome-map/spec.md` (`REQ-97`); `docs/loom/INDEX.md` (`### REQ-97`); `docs/loom/BACKLOG.md` (generated header); `docs/loom/backlog/2026-08-31-orphan-dispatch-receipt-jams-batch.md` (entry format); `loom-code/scripts/check-living-spec-index.py` (`--write-index`); `loom-workflow/.claude-plugin/plugin.json` (`"version": "3.1.0"`).

## Decision

We will move the symlink guard body into `map_lock.py` as one public function parameterized by exception class, and leave a one-line private delegation in `map_store.py` and `map_transaction.py` so every existing caller and test is untouched. We will delete `claim_ticket.py` with its test and rewrite the two prose surfaces (`map-format.md`, living-spec `REQ-97`) to say claims do not transfer, because the tool has no entry point, its evidence check cannot see sibling worktrees, and its only passing path requires a claim commit dated before the claim.

We will file Phase 3 and the multi-worktree Map gap as backlog entries in the same PR so the audit's remaining findings live in the repo, not in one session's memory.

We will NOT wire reclaim into the workflow, NOT change what any guard accepts, and NOT start any Phase 3 split here.

## Out of Scope

- Splitting `loom-code/scripts/loom_gate_markers.py` or `loom-design/scripts/pipeline/batch_queue.py` (Phase 3 — filed, not done).
- A unified pytest root for `loom-design/scripts/` (Phase 3 — filed, not done).
- Solving multi-worktree Map claim collisions (filed as a backlog gap; a design question, not a refactor).
- Any change to `map_transaction.claim_ticket` (first-claim) semantics or the Withdrawal grammar.
- Cross-plugin sharing of the guard (user-ratified plugin independence).
- Renaming `MapLockError` / `SchemaViolation` / `CloseTransactionError` or merging them.

## Alternatives Considered

My take: recommend the exception-class parameter on one body in the leaf module. Why: the three copies differ only in the raised type, so the parameter captures the whole delta without a new module. Conditional reversal: if a fourth guard variant appeared needing different walk logic, a shared body would be the wrong abstraction and lockstep copies would be preferred.

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| Keep the three copies (Rule of Three says extract at the third occurrence, which is now) | Wikipedia — https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming) (EN); understandlegacycode — https://understandlegacycode.com/blog/refactoring-rule-of-three/ (EN) | Three occurrences is exactly the extraction threshold both sources state; the copies are already byte-identical apart from the exception, so the "wrong abstraction" risk the rule guards against is absent. |
| One shared exception base class and one guard raising it, callers catch the base | Python docs on module-level exception base classes — https://docs.python.org/ja/3/library/exceptions.html (JA); Qiita 例外ベストプラクティス — https://qiita.com/hasoya/items/05d4e49d492869875cca (JA) | Would change the raised type at 54 pinned assertions and merge three modules' error taxonomies; the JA guidance to design exceptions for encapsulation argues for keeping each module's own type. EN sources say nothing against it; JA sources motivate the parameter shape — no disagreement, complementary. |
| Wire `reclaim` into SKILL.md with a CLI entry instead of deleting | This repo — `map-format.md` `Reclaim is conservative` already promises it | Its git evidence reads only the current checkout, so under the user's multi-worktree usage it can misjudge an in-progress ticket as stale; and its refusal on same-day last change means every real claim commit blocks it. Wiring would ship a tool that cannot succeed. |
| Delete `claim_ticket.py` but leave `REQ-97` and `map-format.md` untouched | — | Leaves a living-spec requirement and a reference paragraph describing behavior nothing implements; the living-spec index would still pass (other tests tag REQ-97), which is exactly how a false promise survives. |

## What Becomes Obsolete

- BI-8 — The guard bodies in `map_store.py` and `map_transaction.py` are deleted in the same PR, each replaced by a one-line delegation to `map_lock.assert_no_symlink_components`.
- BI-9 — The reclaim promise in `map-format.md` (`Reclaim is conservative: ...`) and the `REQ-97` scenarios `Claim has no usable stale evidence` / `Claim is observably stale` are replaced in the same PR.

## Open Questions

(empty)

Retired identifiers (split 2026-08-31 at plan time so each task owns one item — never reuse): BI-5 → BI-10, BI-11, BI-12; BI-6 → BI-13, BI-14, BI-15, BI-16, BI-17.

## Diagrams

N/A — no flow/state/architecture-shaped content: three-copies-to-one inside one directory plus a deletion; the Reverse sub-bullet's one-line import chain states the only structural fact.
