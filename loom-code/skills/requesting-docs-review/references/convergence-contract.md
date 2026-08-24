# Convergence contract — requesting-docs-review

Binding contract: read this before dispatching or verifying any round — the directives below are not optional. `SKILL.md`'s `## Process` points here at the dispatch moment; the retained inline summary and the hand-the-user decision surface live there, unmodified.

**CONVERGENCE CONTRACT — binding directives. Apply them at every dispatch and verdict moment; they override any impulse to run another round.**

**1. Round 1 is the only full review.** It is whole-artifact — every changed `.md` file, read whole, never diff-scoped. There is no round 2, no round cap, and no automatic delta round triggered by round count. Two outcomes:

- **No gating findings → done.** The review is complete.
- **Gating verdict → fix, then delta confirmation** (Directive 2). Non-gating findings never gate; they are recorded as debt. Aggregation thresholds — what makes a finding gating vs. non-gating — are UNCHANGED from today; see `requesting-code-review/SKILL.md`'s §Aggregation rule for the exact thresholds. This contract does not restate the numbers.

**2. Post-fix confirmation — one portable packet, one cycle.** After fixing a
gating verdict, create one **post-fix confirmation packet**. It contains the
complete immutable context fields `target_repo`, `reviewed_sha`,
`plugin_version`, and `resources`, plus the **original gating findings**
verbatim and **delta evidence** identifying the text changed to address each
finding. The post-fix `reviewed_sha` is the only snapshot either host may
read. Both hosts receive this entire packet; delivery mechanics do not change
the evidence being judged.

- **Claude Code** delivers the packet to the SAME reviewer via `SendMessage`.
  Its confirmation is delta-scoped: it checks the original gating findings
  against the delta evidence, never a fresh whole-corpus re-sample.
- **Codex** delivers the same packet to a labelled fresh whole-artifact
  review. The fresh reviewer still receives the original gating findings and
  delta evidence, then reports an ordinary verdict under the packet's
  post-fix snapshot.

Normalize either delivery to one of two confirmation outcomes:

- **`PASS` or `PASS_WITH_NOTES` → `CONFIRMED_RESOLVED`** only when every
  original gating finding is fixed. This is a terminal state (Directive 3).
- **`NEEDS_REVISION` → `STILL_BLOCKING` + reason**. The reason identifies an
  original finding that survives or a new gating problem found while checking
  the post-fix snapshot.

**`STILL_BLOCKING` after this one fix cycle → STOP.** Surface the finding and the reviewer's reason to the user. Do not dispatch a second fix-and-confirm cycle, and do not fall back to a fresh whole-artifact round, without explicit user authorization.

**3. Terminal state is "no gating findings" — never "clean."** For an artifact carrying many small real defects, a clean round is not a reachable state: each review samples that pool, so a pass that raises nothing is not evidence the pool is empty (pool-arithmetic rationale: `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`). Report the outcome as "round 1 found no gating findings" or "the fix was confirmed resolved" — never as "the doc is clean."

**4. Session death before confirmation → one fresh single round.** If the session dies before a dispatched delta confirmation completes, do not attempt to resume or replay it. Dispatch one fresh, whole-artifact round 1 instead — there is no cross-session delta-resume machinery to reconstruct partial state from.

This replaces the previous 2-round cap and its automatic qualifying delta round in full: no round-2 gate, no `prior_findings_check`, no auto-third-round condition, no fourth-round authorization ladder. One full round, at most one delta confirmation cycle, then done or STOP.
