# Backlog ↔ decision-map boundary redesign (v2)

> Entry artifact (frozen brief). Ratified 2026-08-30 by kouko, item by item,
> after an independent-advisor audit (gpt-5.6-sol, effort high, single audit
> leg, 13 divergence points — all dispositioned below) plus a controller-side
> simplification pass (4 further cuts, also ratified).

## Design-side on-ramp

fired: rows 3 — user chose direct

## Queue relation

unqueued — 本弧自身就是 queue 層紀律的重設計，從 backlog 治理討論長出、非排隊中的 bet；map 側歸屬為 family-relocation 下游

## Goal

Redraw the boundary between the two task-tracking containers so each has one
commitment level, travel between them is one-way, and the backlog store
regains an exit rate. This is a semantic/contract arc: the queue layer's
physical relocation (family-relocation map, fog F-1..F-4) is deliberately
NOT touched — the boundary rules are portable to whichever home the queue
layer ends up in.

Core split (user's own framing, ratified):

- **map task ticket** = committed work under a live purpose umbrella
  (Destination); never demoted.
- **backlog entry** = opportunistic work with no umbrella (or too small to
  deserve a ticket); never promoted without closing.

## Decisions (all user-ratified)

### decision-map side (loom-workflow plugin)

| # | Decision |
|---|---|
| D1 | **schema_version 1 → 2**, single arc: bump, migrate the one live map (`family-relocation`), retire v1 (checkers exit 2 on v1 maps with a "migrate" message). Bump-must-migrate discipline written into the contract: no grandfathered old-version artifacts. |
| D2 | **Relay ban**: `type: task` no longer means "file a backlog entry". Task = decision-unblocking work (wayfinder's narrow reading: "unblocks a decision, never delivers the destination"). Resolution records the produced artifact/answer, never a backlog-entry filing. Contract surfaces to change: `map-format.md` type table (line ~157), `decision-map/SKILL.md` delegation section (line ~119), plus a grep-style test rejecting the old relay phrasings anywhere under the contract trees. The ban itself is defined at ONE point (map-format task entry); SKILL.md references it. |
| D3 | **Parts section removed**: delete the Parts table, `map_parts.py` flipper, flip protocol, and re-flip guard from the contract + command surface. Plan→map binding becomes a **plan-side declaration**: the plan's `## Notes` carries `Map part: <map-id> / Part: <name>` (line already exists), and delivery progress is **derived read-only** (a small script/`--ready`-style listing that greps plan Notes bindings + plan state; no writes to MAP.md). Rationale: Parts' Status cell was mutable state — a store inside a self-declared index; the done(<sha>) fact already lives in git and the plan. Removal cost is at its lifetime minimum (Parts shipped 3 days ago; the only live map's Parts table is empty). |
| D4 | **clear condition fixed and single-sourced**: clear = zero non-closed tickets (both `open` AND `claimed` excluded) + fog empty. Defined once in map-format; SKILL.md references. `map_store.py` hard-validates: `state: clear` with any non-closed ticket is red. (Current drift: map-format says "every ticket closed", SKILL says "zero open" — a live contradiction.) |
| D5 | **Ticket close discipline**: every closed `task` ticket must have a non-empty Resolution plus a delivery-evidence line (commit SHA / PR / artifact path); validated by `map_store.py`. (Current fixture gap: a closed task with no Resolution passes `check_map_links`.) |
| D6 | **`is_live_map` three-valued + fail-closed**: live / not-present / **broken**. Any consumer (umbrella checks, reception) treats broken as refuse-until-repaired, never as "no live map". |
| D7 | **Umbrella checks, two primitives × two moments** (user-added moments included): 查傘/check-umbrella (does a live map's clear-condition require this work?) fires at backlog-entry creation AND at pickup-before-work; 查隊/check-queue (does backlog already track similar work?) fires at map charting AND at every task-ticket creation. `map-scope-check:` evidence lines are CUT (judgment prose; will be boilerplated). Umbrella criterion is the D4 clear-condition, NOT topical overlap (no fuzzy matching — same discipline as join keys). |
| D8 | **Unique owner**: work falling under multiple live maps' Destinations → HITL adjudication; chosen map owns the ticket, other maps record one line in Out-of-scope citing the join key (machine-checkable link, existing precedent in family-relocation MAP.md). Duplicate task tickets for the same work are contract violations (greppable). |
| D9 | **Promotion is close-and-cite** (simplified from codex #7's blocked-state machinery — ratified cut): promoting a backlog entry into a ticket closes the entry with `origin: promoted to <ticket>`. NO `blocked:` state, no bidirectional standing links, no close-on-delivery step. Orphan recovery is a one-line prose rule in the map-archive flow: a map archived with unclosed tickets reopens the entries its tickets were promoted from. Reversal cost (one-line frontmatter reopen) does not justify standing machinery (same amnesty calculus as D12). |

### backlog side (loom-code plugin)

| # | Decision |
|---|---|
| D10 | **`start:` closed grammar, two prefixes**: `start: date — YYYY-MM-DD` or `start: event — <observable condition>`. `now` is CUT — work to do now is done now, not filed. Parser validates prefix + non-empty remainder + date format. |
| D11 | **Aging, mechanical**: age = 90 days from the immutable filename date; new `--review-due --as-of YYYY-MM-DD` command lists all live open entries past bound (reads wall-clock only via the explicit `--as-of`; `--validate` stays pure syntax, no clock). Re-trigger = close old (superseded) + open a newly-dated successor with `origin:` backlink (filename date resets age honestly). Wired as one line in the finishing/close-out checkpoint (prose); NO CI wiring (ratified cut — add when a real miss is observed). |
| D12 | **Amnesty sweep** (replaces codex #12's six-bucket manifest — ratified simplification): list all 134 open entries (name + description + trigger, one page) → user names the rescues → the unrescued 134−N are bulk-closed with closure reason `amnesty-2026-08-30 (bulk cleanup, not per-entry adjudicated)` → rescued entries rewritten in D10 grammar → gate on in the same PR. No per-entry subagent classification, no manifest, no coverage check (set semantics: everything closed unless rescued). Mis-closure reversal = one-line reopen. The rescue review is a **HITL halt point** inside execution. |
| D13 | **No backward compatibility** (user override of codex #3): `backlog_index.py` enforces "open entries must carry a valid `start:`" unconditionally. No opt-in marker, no grandfather clause, no branching. Breaking change is carried by the plugin version jump (marketplace publishes by version); adopting repos hit the new rule on upgrade and read the updated charter template. Rationale (user): adoption surface is currently tiny; compat cost exceeds benefit. |
| D14 | **Charter template updated** (`scripts/templates/backlog-README.md` + this repo's store README): trigger discipline, two-prefix grammar, aging rule, promotion/promotion-ban, umbrella checks. |

### Measurement note

D15: the 134/26 figure is a **live-store composition ratio**, NOT a close rate
(archived entries are excluded from the index by design). Never cite it as a
close rate; cohort rates, if ever needed, come from `--review-due` data, not
from archaeology.

## Out of scope

- The queue layer's physical relocation decision (family-relocation map fog
  F-1..F-4, feasibility ticket). This arc lands first; relocation runs after
  (user-ratified sequencing).
- CI wiring for `--review-due` (add on observed miss).
- The `now` backlog trigger type (cut, not deferred).

## Execution order (plan will sequence mechanically)

1. decision-map contract v2 (D1–D9) — one PR-sized arc; TDD on `map_store.py`
   validators (clear-with-claimed red, closed-task-without-resolution red,
   v1-map exit 2), grep tests for relay phrasings, delete `map_parts.py` +
   flip protocol + its tests, migrate family-relocation MAP.md.
2. backlog gates (D10, D13, D14) — parser grammar test first, then
   enforcement; charter template sync.
3. `--review-due` (D11) — clock stays out of `--validate`.
4. Amnesty (D12) — **HALT: user rescue review** on the one-page list, then
   bulk close + rewrite rescues in new grammar + regen index. Lands with 2/3
   in the same PR before the gate turns on (no grandfather window).
5. Version bumps: loom-workflow + loom-code (skill content changed in both;
   marketplace publishes by version).

## Versioning

map schema_version 1 → 2 (D1). loom-workflow plugin version bump (decision-map
skill + scripts). loom-code plugin version bump (backlog_index.py + templates).
Codex mirror manifests sync via the existing sync script.
