# Brief: bring the repo's task-management documents current with the shipped loom mechanism

Date: 2026-08-10
Origin: user ask「整理一下這個 repo 的任務管理相關文件 確認都有用到最新版本 loom 機制」immediately after PR #680 (loom-code 0.71.0 / loom-pipeline 0.16.0) merged. Two read-only audits (backlog truthfulness over all 91 OPEN+PARKED entries — the actionable subset; SHIPPED/CLOSED/UPSTREAM were spot-checked separately; stale-mechanism references over every living doc surface) produced the exact finding tables this brief consumes.

## Problem

The mechanism moved twice recently — #677 tombstoned ROADMAP.md in favor of DIRECTION.md, #680 shipped plan_card.py/backlog_index.py inside the loom-code plugin — and the skill bodies were updated both times, but the surrounding LIVING documents were not swept. Result: 2 plan ledgers claim in-flight for merged arcs; 6 living surfaces teach a repo-root-only tooling path; five surfaces (nine files — two tri-language README trios, two spec headers, one AGENTS section) point readers at a tombstoned ROADMAP as the forward plan; docs/loom/README's directory map omits DIRECTION.md entirely; 3 backlog entries carry sub-asks that already shipped (PR #619/#672/#573) and 2 point at shim paths instead of the canonical scripts. This is the exact class the store entry `a-documented-fallback-can-legitimize-a-delivery-gap` and today's stale-reference incident describe: docs drifting from mechanism, each drift surviving because nothing sweeps the periphery when the center moves.

## Users

kouko + any agent (this repo's sessions, Codex mirror readers of AGENTS.md) taking instruction from these living docs.

## Smallest End State

1. Both stale plans read `Stage: finishing` (their 9/9 tasks are done; the arcs shipped as loom-code 0.65.2 and 0.66.0, within the five-arc complexity-audit series that closed at 0.68.0).
2. Every living-doc invocation of the two progress scripts states the two-tier resolution (repo-root first, else the loom-code plugin copy) or points at the charter section that does; AGENTS.md's script inventory gains one bullet each for plan_card.py and backlog_index.py; TECH-SPEC §2.1's scripts/ block lists both and drops the nonexistent scripts/README.md.
3. Every living pointer to a ROADMAP.md is relabeled historical with forward direction at docs/loom/DIRECTION.md (loom-code README ×3 languages, PRODUCT-SPEC + TECH-SPEC headers, AGENTS.md philosophers section, philosophers-toolkit README ×3 languages).
4. docs/loom/README's directory map gains a DIRECTION.md row (human Next/Later; generated Now — never hand-edit).
5. The 3 stale-sub-ask backlog entries carry appended evidence lines (PR #619 / #672 / #573) narrowing them to their surviving items; the 2 script-internals entries point at loom-code/scripts/ paths; `backlog_index --validate` exit 0 and BACKLOG.md/DIRECTION.md regenerated if descriptions changed.
6. No frozen history touched: specs/, plans/ (other than the two Stage fields, which are the live ledger the mechanism itself flips), research/, archive/, old CHANGELOG entries.

## Current State Evidence

- Forward: audit tables in this session (stale-reference sweep: 12 findings with file:line; backlog audit: 91/91 read, 3 STALE-OPEN sub-asks with PR evidence, reverse check clean).
- Reverse: generated files verified fresh before the sweep (BACKLOG.md --check ✓, DIRECTION.md in-place regen zero-diff ✓, INDEX.md ✓, memory README ✓) — the generators are healthy; only hand-written prose drifted.
- Error: none of these edits touch behavior; worst failure mode is a broken doc-pin test (duty tests pin skill bodies, not these files — verified by the suite staying green being the acceptance).
- Data: 200 plans total; 182 predate the ledger mechanism (0.60.0) and stay old-format frozen history by design; 18 have ledgers; exactly 2 are stale.
- Boundary: README trios (loom-code, philosophers-toolkit) must change in all three languages together (repo memory: skill READMEs require tri-language).

## Alternatives Considered

1. Fix-all-in-one-docs-branch (chosen) — every edit is a one-to-three-line factual correction with audit evidence; one branch, docs review gates it.
2. Backfill ledgers into all 182 old plans — rejected: frozen history, zero operational value, the mechanism treats no-Status plans as old-format by design.
3. Leave backlog entries untouched and only fix references — rejected: the charter's own status discipline says entries carry evidence lines when reality moves; leaving known-stale sub-asks breeds the exact re-discovery waste the store warns about.

## Decision

One docs branch, four batches: (T1) the two Stage flips via plan_card itself; (T2) tooling-path currency incl. AGENTS.md + TECH-SPEC; (T3) ROADMAP pointer relabels incl. both tri-language trios; (T4) backlog entry updates + regen + validate. All .md; whole-branch gate = requesting-docs-review.

We will NOT: touch frozen history, rewrite any entry's original ask (append evidence, narrow scope — never rewrite), backfill old plans, or decide any promotion/betting (user-only).

## Out of Scope

- The milestone-layer design question (its backlog entry's Start condition fired today — noted for the user's betting decision, not acted on).
- Any skill body or script change (all verified current by the sweep).
- MEMORY.md / auto-memory (per-machine, not repo docs).

## Design-side on-ramp

Negative guard: factual-drift fix to existing docs (bug-fix shaped) — upstream-artifact walk skipped silently. Backlog ready check: ran this session (the audits ARE the ready-state read); no COMMITTED-NEXT conflict (`## Now` empty).

## Open Questions

None blocking.
