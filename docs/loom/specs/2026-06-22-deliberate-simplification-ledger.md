# Brief: deliberate-simplification ledger (LOOM-SIMPLIFY marker + harvest)

**Date**: 2026-06-22
**Topic**: deliberate-simplification-ledger
**Source**: in-chat research — "can ponytail's framework/philosophy improve loom-*?" → item ① (the one genuine, non-redundant gap).

## Problem

(Axis 1 — JTBD)

When loom-code's implementer ships a **deliberate, scope-bounded simplification** — a naive heuristic, an `O(n²)` scan, a global lock, a deferred edge-case — because the proper solution is out of scope for the current brief, that shortcut today leaves **no auditable trace of its ceiling or its upgrade path**. It becomes invisible debt: the "for now" silently becomes "forever," and a future agent/human can't tell a deliberate corner-cut from an oversight.

Job: *"When I knowingly cut a corner during implementation, record the corner's ceiling (when it breaks) + upgrade path (how to do it properly) in an auditable place, so the shortcut is a tracked, reversible decision — not silent debt."*

This is the one mechanism ponytail (`ponytail:` markers + `/ponytail-debt` ledger) has that loom-code genuinely lacks. The **philosophy** (YAGNI, "smallest end state," deletion-over-addition) is already independently present across loom-code — see the in-chat analysis. Only this accountability mechanism is missing.

## Users

(Axis 2)

The loom-code pipeline itself, three actors:
- **implementer subagent** — *leaves* the marker at the moment it takes the shortcut (the only actor that knows the corner was cut and why).
- **code-reviewer (whole-branch) + human** — *harvest* the markers before merge, so deliberate shortcuts are visible at the review gate rather than discovered months later.
- **future-me / resuming agent** — reads the in-code markers (or the on-demand harvest) to know what's safe to lean on vs what has a known ceiling.

Job story: *When I'm reviewing a branch before merge, I want to see every deliberate shortcut it ships with its ceiling + upgrade path, so I can decide whether each corner-cut is acceptable to ship rather than rubber-stamping invisible debt.*

## Smallest End State

(Axis 3 — chosen scope: **in-code marker + harvest**, per user decision 2026-06-22; plan-time-declaration and a persisted ledger file were both rejected as redundant / drift-prone.)

1. **A marker convention** — `LOOM-SIMPLIFY: <shortcut> | ceiling: <checkable condition that breaks it> | upgrade: <path to proper version> | ref: <brief/task it belongs to>` — defined as a new SDD **standard** (`deliberate-simplification.md`), modeled on the existing `external-surface-grounding.md` (a standard referenced by multiple skills, not duplicated into each). `ceiling:` must be a **checkable condition** ("when input >10k rows"), not "later" — grounded in the on-hold-SATD research. `ref:` ties the marker to its brief/task (the loom equivalent of a ticket link), per the EN+JP ownership-convention convergence.
2. **Implementer leaves it** — one rule added to `implementer.md`: when you take a deliberate scope-bounded shortcut (proper version is Out of Scope per the brief), drop a `LOOM-SIMPLIFY:` marker. **Explicitly NOT a TDD bypass** — the shortcut's current behavior is still tested at its current scope; the marker documents the *ceiling*, it does not excuse a missing test.
3. **Harvest at the review gate** — `requesting-code-review` greps `LOOM-SIMPLIFY:` across the whole-branch diff and surfaces a ledger view in the review summary; the whole-branch `code-reviewer` flags any marker missing `ceiling:` or `upgrade:`. The in-code markers are **SSOT**; the ledger is a **grep-on-demand view**, not a persisted file (no dual-SSOT, no drift).

That is the whole change. No persisted ledger doc, no plan-time field, no slash command.

## Current State Evidence

(Brownfield — touching existing loom-code skills/agents.)

- **Forward** (what calls the touch points): the SDD flow dispatches `implementer.md` per task (`subagent-driven-development/SKILL.md`); `requesting-code-review` runs the whole-branch `code-reviewer.md` before any push/merge (`using-loom-code` router rule #4).
- **Reverse** (SSOT ownership): SDD's `standards/` directory owns cross-cutting implementer/reviewer rules; `external-surface-grounding.md:1+` is the canonical precedent — one standard file, referenced by `plan-format.md §External surfaces`, `implementer.md`, and reviewer D7. The new standard follows the same ownership (house additions in a new standard module, not synced SSOT).
- **Error/edge**: the marker must not become a TDD escape hatch — `tdd-iron-law/SKILL.md` (Iron Law) stays strictly stricter than ponytail's "one executable check." The standard must state the marker ≠ test waiver.
- **Data**: marker payload is free-text in three labeled fields (`shortcut` / `ceiling` / `upgrade`); harvest is `grep -rn "LOOM-SIMPLIFY:"` over the branch diff.
- **Boundary**: no existing concept overlaps — `Status` ledger (`plan-format.md:79-104`) is runtime task-state (pending/claimed/done/blocked), and brainstorming Axis 5 (`brainstorming/SKILL.md:121`) is design-time *obsolescence*, not implementation-time *shortcut*. Confirmed clean gap.

Evidence paths:
- `loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md` (precedent pattern)
- `loom-code/agents/implementer.md` (marker author)
- `loom-code/agents/code-reviewer.md` (harvest + completeness check)
- `loom-code/skills/requesting-code-review/SKILL.md` (harvest surfacing point)
- `loom-code/skills/writing-plans/references/plan-format.md` (boundary: Status ledger, not this)

## Decision

Build the **in-code marker + on-demand harvest**, housed as a new SDD standard wired into three touch points (implementer / code-reviewer / requesting-code-review). The in-code marker is SSOT; the ledger is a grep view. We will **NOT** add a plan-time `Simplification:` field (redundant with brief Out-of-Scope), a persisted ledger file (dual-SSOT drift), a slash command, or any strength dial. The marker is **not** a TDD waiver.

**Note on the original anchor**: item ① was framed as "add a convention to `writing-plans`," but the recon shows the convention's natural home is SDD standards + implementer + review — because the gap is *implementation-time emergent* shortcuts, not plan-time deferrals. `writing-plans` gets at most a one-line cross-reference. This relocation is a deliberate, surfaced deviation from the first framing.

## Out of Scope

- Plan-time declaration field in `plan-format.md` (covered by brief Out-of-Scope + Axis 5).
- A persisted ledger document or database.
- A `/loom-debt`-style slash command (loom-code has no analogous command surface; harvest rides the existing review gate).
- Strength modes (lite/full/ultra).
- Retrofitting markers onto existing loom-code shortcuts (greenfield convention; no backfill).
- Any change to `tdd-iron-law`.

## Alternatives Considered

(Axis 4 — the live alternatives were the *placement* options, triaged via the in-chat decision; external prior art is stable knowledge, cited not searched.)

- **Plan-time declaration field** (rejected): duplicates brief Out-of-Scope; misses emergent shortcuts (the actual gap).
- **Persisted ledger file** (rejected): dual-SSOT with the in-code markers → drift, the exact failure the user's "house additions in new module, not synced SSOT" memory warns against.
- **In-code marker + grep-on-demand harvest** (chosen): single SSOT, ponytail-faithful, smallest.

Prior art + empirical research (WebSearched EN+JP, 2026-06-22):

Stable conventions:
- **PEP 350 — Codetags** (TODO/FIXME/HACK/XXX/OPTIMIZE): structured in-code annotation tags. `LOOM-SIMPLIFY` is a namespaced codetag with *required structured fields* (ceiling + upgrade) most codetags lack.
- **Fowler, "Technical Debt Quadrant" (2009)**: the *deliberate + prudent* quadrant ("must ship now, will deal with consequences") — exactly the shortcut class this marker records.

Empirical findings that shaped the design:
- **Maldonado et al., ICSME 2017** (https://rabeabdalkareem.github.io/files/2-maldonado_icsme2017.pdf): ~74.4% of SATD comments are eventually removed. BUT — per **Maipradit et al. "Wait For It" (arXiv 1901.09511), crediting Zampetti et al. (2018)** — **58% of those "removals" did not actually fix the problem** (the comment was deleted with surrounding code). → A grep-count harvest is gameable across a codebase's lifetime; we sidestep this by harvesting **only at the introducing branch's review gate**, not tracking lifecycle. Reinforces in-code-marker-as-SSOT + no persisted ledger file.
- **Maipradit et al., "Wait For It" (arXiv 1901.09511) + automated identification (arXiv 2009.13113)**: ~**5.3% overall** of SATD comments are **"on-hold"** (293 of 5,529 across 15 projects) — they record a *waiting condition* (a bug fix / a library version) and are the most machine-manageable class (classifier AUC 0.83). → `ceiling:` must be a **checkable condition** ("when input >10k rows"), not "later." Our ceiling = the on-hold condition; upgrade = its resolution.
- **PromptDebt (arXiv 2509.20497) + SATD-in-LLM (arXiv 2601.06266)**: AI-generated code carries substantial LLM-specific SATD. → AI-authored shortcuts are a studied, real debt source; an agent-authored marker convention is justified.

Industry convention (EN+JP converge — a strong signal per Axis-4):
- Every debt marker should carry **ownership + a link** (ticket / expiry / author). EN: Grivner/Medium; JP: **Datadog JA rule "TODO/FIXME は所有権を持たなければならない"** (https://docs.datadoghq.com/ja/continuous_integration/static_analysis/rules/python-best-practices/comment-fixme-todo-ownership/), Sansan Tech Blog. → **adds the `ref:` field** (below) tying each marker to its brief/task — the loom equivalent of a ticket link.
- CI/ESLint gates block un-linked markers (todocheck, tickgit, leasot; JP: GitHub Actions PR-detect). → our review-gate `code-reviewer` flag is the smallest equivalent; a CI hook is a deferred option.

## What Becomes Obsolete

(Axis 5) Nothing existing is removed — this is net-additive convention. The additive-ness is itself a YAGNI flag, but it is justified: it is the one accountability mechanism the in-chat analysis found genuinely missing, and it is verification-class (makes a deliberate cut auditable), not a crutch.

## Open Questions

- **Marker tag name**: `LOOM-SIMPLIFY:` (proposed) vs `LOOM-DEBT:` vs `SIMPLIFY:`. Leaning `LOOM-SIMPLIFY:` (namespaced, greppable, not colliding with generic TODO/FIXME). Resolve at plan time.
- **Harvest home**: `requesting-code-review` (whole-branch, proposed) vs also surfacing in `finishing-a-development-branch` Phase 3. Leaning review-gate only for smallest end state; finish-branch can reference it.
