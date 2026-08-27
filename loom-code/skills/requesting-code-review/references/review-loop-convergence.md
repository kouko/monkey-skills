# Review loop convergence contract — requesting-code-review

Binding contract: read this before dispatching round 1 or any delta
confirmation. `SKILL.md` Step 6 points here at the loop-decision moment; the
retained inline summary and the user-relay surface live there, unmodified.
This transplants `requesting-docs-review`'s experimentally-validated
ledger-driven convergence contract into the code arm, replacing the old
unconditional "fresh subagent every round" rule.

## 1. Round 1 — two named arms, one ledger

Round 1 is unchanged in scope (whole diff, byte-identical prompts, two
`code-reviewer` arms per Step 2) except for one addition: each arm is
dispatched with a stable `name:` — `code-review-arm-a` and
`code-review-arm-b` — recorded in the ledger below. This is the sanctioned
carve-out to Step 2's "must not name async teammates" clause: delta
confirmation drives an arm via `SendMessage`, which is exactly the case the
underlying rule (`environment-gotchas.md` A1) exempts — name only an arm you
intend to confirm.

A gating verdict opens **one ledger entry per gating finding**:

```
id: <stable per-finding id, e.g. F1, F2, ...>
arm: code-review-arm-a | code-review-arm-b   # which arm raised it
where: <path + anchor from the finding>
severity: 🔴 | 🟡
state: open
```

Entry states flip **individually** — `open` → `CONFIRMED_RESOLVED` or
`STILL_BLOCKING` — never as a block. An arm with any surviving `open` or
`STILL_BLOCKING` entry stays blocking. The next cycle's scope is **exactly**
the still-open entries; entries already `CONFIRMED_RESOLVED` are not
revisited.

## 2. Rounds 2+ — inherited delta confirmation

Dispatch only to **arms holding open entries**. This is an inherited delta
confirmation, not a fresh round: `SendMessage` to the SAME named reviewer
(`code-review-arm-a` and/or `code-review-arm-b`) with a post-fix packet
mirroring the docs-review packet fields — post-fix SHA, the original gating
findings for that arm's open entries verbatim, and delta evidence
identifying the text changed to address each one.

The arm replies with its ordinary three-valued `verdict:`. The orchestrator
— never the arm — maps it to a confirmation outcome:

- `PASS` or `PASS_WITH_NOTES` → **`CONFIRMED_RESOLVED`**, only when every
  original finding assigned to that arm is closed.
- `NEEDS_REVISION` → **`STILL_BLOCKING`** + reason.

Confirmation outcomes are orchestrator-owned; an agent's `verdict:` token is
never itself `CONFIRMED_RESOLVED` or `STILL_BLOCKING`.

**Anchoring guard.** The arm's default reading of any entry is blocking. An
entry closes only when the confirmation cites a
verbatim quote of the post-fix text
**and** names which clause of the original finding that quote satisfies. That
a file changed is not evidence a finding closed.

## 3. Termination and the cap

- **All entries `CONFIRMED_RESOLVED`** → converge and mint (§4).
- **Any `STILL_BLOCKING` with a cycle remaining** → run the next cycle,
  scoped to arms with open entries only.
- **Any `STILL_BLOCKING` at the cap** → quality STOP, surfaced to the user
  exactly as `requesting-docs-review` Directive 2 STOPs — never a request
  for another batch.

**Cap:** round 1 plus **at most two delta-confirmation cycles**. The
fresh-delta fallback (dead arm, quota-kill, Codex host), the dead-arm retry,
and one `MALFORMED_PACKET` repair are deliveries of the SAME cycle and
consume none of the cap; their existing Step 3 bounds are unchanged by this
loop.

A post-verdict change made with **no open ledger entries** is not a
confirmation cycle at all: it restarts at round 1 (fresh two-arm panel) and
consumes no cycle.

**Confirmation rounds are single-arm by design.** Step 3's degraded-evidence
disclosure (dead-arm rule) applies to round 1 only, never to a confirmation
delivery — a confirmation dispatched to one named arm is not a degraded
panel.

## 4. Convergence minting

On full convergence, first obtain and `--validate` a **fresh immutable
context packet at the post-fix SHA** (`review_context.py`), and re-run
Step 4's `LOOM-SIMPLIFY:` harvest against that fresh snapshot — not the
round-1 snapshot.

The orchestrator then builds a schema-valid **terminal wrapper**: current
`standards_version`, the post-fix `reviewed_sha`, all 11 `dimension_scores`,
and the aggregation result over what remains open (none, by definition of
convergence). Any R3 downgrade floor carried by either arm is preserved —
**never upgraded** — into the wrapper. Mint (`loom_gate_markers.py
review-pass`) from the wrapper. `CONFIRMED_RESOLVED` is never minted
directly; only the terminal wrapper is a mintable verdict.

## 5. Delta admissibility

A round-2+ arm may close its own entries, and may raise **new** gating
findings **only inside the fix diff**. An observation outside that
delta — however real — is not a finding and never triggers a round: the
orchestrator records it as non-gating debt by appending an `open` entry to
`docs/loom/backlog/`, using that store's own entry format (loom-scaffolded
protocol path, not a citation of this repository's development record).

## 6. Escalation valve

One fresh full two-arm round may **replace** a delta cycle, counted against
the cap, when the fix grows substantial new logic. The valve is a judgment
call, not a mechanical trigger:

- **Valve proxy (sufficient, not necessary):** the fix diff extends beyond
  every open entry's `where:`, or introduces new functions, tests, or
  behavior. Judgment may fire the valve without the proxy holding, and the
  proxy alone never forces it.
- A valve round **never closes an open ledger entry** — entries close only
  through their own arm's confirmation (§2). Any entry still open at the
  valve round's end keeps the verdict gating, exactly as before the valve
  round ran.
- The valve is **unavailable** when firing it would consume the last
  remaining cycle — at that point only an ordinary delta-confirmation cycle
  or a STOP is available.

## 7. Session death / lost handle

Session death, context compaction, or a dead handle before a confirmation
completes → **one fresh whole-diff round 1**, disclosed in the report as
"never delta-confirmed, and why" — never a ledger flip. This transplants
`requesting-docs-review` Directive 4 unchanged.

## 8. Mixed branch

The cap counts **per arm**. The docs arm keeps its own one-cycle bound
(`requesting-docs-review` Directive 2); a code-arm cycle 2 does not
re-dispatch the docs arm. The branch verdict joins the docs arm's **last**
verdict, disclosed as such in the surfaced report.

## Unchanged

The Dead-arm rule and the `MALFORMED_PACKET` one-packet-fix bound (Step 3)
are untouched by this loop — this contract governs what happens **after** a
gating verdict, not the panel-formation rules that produce it.
