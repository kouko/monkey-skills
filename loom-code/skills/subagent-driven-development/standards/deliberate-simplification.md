<!--
FUNCTIONAL COPY — DO NOT EDIT IN PLACE
SSOT: domain-teams/skills/code-team/standards/deliberate-simplification.md
Sync via: loom-code/scripts/distribute.py
-->

# Deliberate Simplification

When an implementer ships a **deliberate, scope-bounded shortcut** — a
naive heuristic, an `O(n²)` scan, a global lock, a deferred edge-case —
because the proper solution is **Out-of-Scope per the brief**, that
shortcut MUST carry an in-code `LOOM-SIMPLIFY:` marker recording its
**ceiling** (the checkable condition under which it breaks) and its
**upgrade** path (how to do it properly). The marker converts invisible
"for now" debt into a tracked, reversible decision: a future agent or
human can tell a deliberate corner-cut from an oversight, and can see at
the review gate exactly what each shortcut costs.

## Primary Sources

- **PEP 350 — Codetags.** Structured in-code annotation tags
  (TODO/FIXME/HACK/XXX/OPTIMIZE). `LOOM-SIMPLIFY` is a namespaced
  codetag with **required structured fields** (`ceiling` + `upgrade`)
  that ordinary codetags lack. https://peps.python.org/pep-0350/
- **Fowler, M. (2009) "Technical Debt Quadrant".** Names the
  *deliberate + prudent* quadrant — "we must ship now and will deal with
  the consequences" — which is exactly the shortcut class this marker
  records. https://martinfowler.com/bliki/TechnicalDebtQuadrant.html
- **Maldonado, E. da S. et al. (ICSME 2017) *An Empirical Study on the
  Removal of Self-Admitted Technical Debt*.** ~74.4% of SATD comments
  are eventually removed. This is part of why lifetime grep-tracking is
  unreliable and why we harvest only at the introducing branch's review
  gate (see Harvest + Scope Boundary).
  https://rabeabdalkareem.github.io/files/2-maldonado_icsme2017.pdf
- **Maipradit, R. et al. "Wait For It" (arXiv:1901.09511),** crediting
  Zampetti et al. (2018), reports that **58% of "removed" SATD comments
  did not actually fix the problem** — the comment was deleted along
  with surrounding code. ~5.3% overall of SATD
  comments are **"on-hold"** — they record a *waiting condition* (a bug
  fix, a library version, a threshold) and are the most
  machine-manageable debt class. The `ceiling:` field is exactly this
  on-hold condition; `upgrade:` is its resolution.
  https://arxiv.org/abs/1901.09511
- **PromptDebt (arXiv:2509.20497).** AI-generated code carries
  substantial LLM-specific self-admitted technical debt — so an
  agent-authored marker convention addresses a studied, real debt
  source rather than a hypothetical one. https://arxiv.org/abs/2509.20497

## The Rule

When you take a **deliberate, scope-bounded** shortcut whose proper
solution is Out-of-Scope per the brief, you MUST leave a `LOOM-SIMPLIFY:`
marker at the shortcut's site, in a code comment, with **exactly four
fields**:

```
LOOM-SIMPLIFY: <shortcut> | ceiling: <checkable condition> | upgrade: <proper path> | ref: <brief/task>
```

| Field      | Meaning                                                      |
| ---------- | ----------------------------------------------------------- |
| `shortcut` | What corner you cut, in one phrase.                         |
| `ceiling`  | The **checkable condition** under which the shortcut breaks.|
| `upgrade`  | The path to the proper version.                             |
| `ref`      | The brief/task this shortcut belongs to (the ticket link).  |

Concrete example:

```python
# LOOM-SIMPLIFY: linear scan of members | ceiling: O(n²) above ~5k members | upgrade: index by member_id | ref: 2026-06-22-deliberate-simplification-ledger / Task 3
for member in members:
    ...
```

## Field Rules

1. **`ceiling:` MUST be a checkable condition** — a threshold (`when
   input >10k rows`), a named event (`when we add a second tenant`), or
   a version (`until lib X ≥ 2.0 ships the batch API`). It MUST NOT be
   `later`, `someday`, or `eventually`. This is grounded in the on-hold
   SATD research (Maipradit et al.): a recorded *waiting condition* is
   the most machine-manageable debt class, because a reviewer or future
   agent can mechanically test whether the ceiling has been reached. A
   vague ceiling is uncheckable and so cannot be managed.
2. **`ref:` ties the marker to its originating brief/task** — the loom
   equivalent of a ticket link. This follows the EN+JP industry
   ownership convention (e.g. Datadog's static-analysis rule that
   TODO/FIXME must carry ownership): every debt marker should be
   traceable to the
   decision that authorized it, so the shortcut is never orphaned.
3. **The marker is left ONLY for a deliberate, scope-bounded shortcut**
   taken because the proper solution is Out-of-Scope per the brief. It
   is **not** for bugs (those get fixed), and **not** for unfinished
   work (that is a `TODO`, a different signal). A `LOOM-SIMPLIFY:` marker
   asserts: *this is correct and complete for the current scope, and
   here is the known limit and the way past it.*
4. **The marker is NOT a tdd-iron-law waiver.** This is explicit: the
   shortcut's current behavior is **still tested at its current scope**
   under the Iron Law — write the failing test, then the implementation,
   exactly as for any other code. The marker documents the *ceiling*; it
   does **not** excuse a missing test. A shortcut with a `LOOM-SIMPLIFY:`
   marker and no test is an Iron Law violation, not a sanctioned cut.

## Harvest + Scope Boundary

The in-code markers are the **single source of truth (SSOT)**. There is
**no persisted ledger file**. Harvesting is a **grep-on-demand view**:

```
grep -rn "LOOM-SIMPLIFY:" <branch-diff-or-tree>
```

The harvest is surfaced **at the introducing branch's review gate** —
the whole-branch review that runs before any push/merge — where each
marker is checked for a valid `ceiling:` and `upgrade:`, and the
reviewer/human decides whether each corner-cut is acceptable to ship.

**Why scope the harvest to the introducing branch's review gate, and
not track markers across the codebase's lifetime?** The SATD literature
finds that ~74.4% of debt comments are eventually removed (Maldonado et
al., ICSME 2017), but **58% of those removals deleted the comment along
with surrounding code without fixing the underlying problem** (Maipradit
et al. "Wait For It", arXiv:1901.09511, crediting Zampetti et al. 2018).
That makes any lifetime grep-count harvest gameable and unreliable — a
falling marker count does not mean debt was paid down. Scoping the
harvest to the merge gate of the branch that *introduces* the shortcut
sidesteps this failure mode entirely: we audit the shortcut at the one
moment its ceiling and upgrade path are freshest and a human is in the
loop, rather than pretending to track it forever. A single in-code SSOT
plus a gate-scoped grep view also avoids the dual-SSOT drift that a
persisted ledger file would introduce.

## Anti-Patterns (rationalizations to refuse)

Refuse these phrasings — they are the failure mode the rule exists to
catch:

- ❌ *"ceiling: fix later"* — `later` is not checkable; name the
  threshold, event, or version that breaks the shortcut.
- ❌ *"I'll add the marker, so I can skip the test"* — the marker is not
  a TDD waiver; the current behavior is still tested at current scope.
- ❌ *"This is just unfinished, I'll mark it LOOM-SIMPLIFY"* — unfinished
  work is a `TODO`, not a deliberate scope-bounded shortcut; do not
  launder incompleteness through this marker.
- ❌ *"I'll record it in a ledger doc instead"* — the in-code marker is
  the SSOT; a separate persisted ledger drifts and is out of scope.
