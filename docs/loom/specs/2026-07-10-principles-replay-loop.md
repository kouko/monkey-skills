# Brief: principles replay quality loop — Levels 1+2 (build now) / Level 3 (design only)

- Date: 2026-07-10
- Source: conversation decision same day (post-#532) — user asked whether the
  replay material can become a quality-improvement LOOP; three-level design
  proposed and approved ("用你建議的方式做吧": build L1+L2, record L3 design).
- Inputs shipped by #531/#532: 6 seeds (1 human-grounded + 5 synthetic with
  grader-only oracles at `docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus/`),
  matrix grading procedure (`docs/loom/dogfood/2026-07-10-principles-flow-cold-operator/matrix-results.md`),
  and two proven facts: the operator's seed-walk self-report can be FALSE, and
  prose hardening for anchor drops is exhausted (5/6 probabilistic misses).

## Level 1 — regression matrix loop (BUILD)

One Workflow script that, on demand (any SKILL.md behavior change), fans out
one haiku headless replay per seed to a sandbox, then grades each artifact
MECHANICALLY (validator + the Level-2 checker; no LLM self-report anywhere in
the verdict path) and returns a pass-rate table. Eval semantics (pass-rate,
non-deterministic), never per-push CI.

## Level 2 — mechanical traceability gate (BUILD)

`check_seed_traceability.py <artifact> <oracle>`: parses the oracle's
`named_anchors:` / `deferred_items:` / `negative:` lists and verifies against
the artifact: every named anchor has a non-empty-version `## Anchors` data
row; every deferred item has an `## Open Questions` entry carrying
`— re-trigger:`; every negative string is absent. Exit 0 / exit 1 naming every
miss. The script's parser defines the oracle format contract; the 5 corpus
oracles are normalized to greppable tokens in the same change. Consumers: the
Level-1 workflow's grade stage, and any future conductor retry-on-miss loop.

Out of scope for the checker (deliberate): `stances:` carrying-principle
checks (needs semantic judgment — stays with LLM graders/humans);
`out_of_jurisdiction_bait:` (position-sensitive; same reason).

## Level 3 — autonomous improvement loop (DESIGN ONLY, BACKLOG)

Closed loop `matrix → grade → implementer proposes SKILL.md fix → review →
re-run`, gated by four guardrails proven necessary by this session:
1. **Held-out seeds** — a split of seeds never shown to the fixing agent
   (oracle-overfit guard; an oracle already got caught encoding defects as
   expectations once).
2. **One-invariant rule + word-budget brake** — fixes must reduce to a single
   invariant, and the 4,500-word SKILL.md cap is a hard stop against patch
   accumulation.
3. **Plateau detection** — a failure class surviving two consecutive fix
   rounds stops the loop (wrong-direction signal; prose ceiling was hit in
   exactly 3 rounds live) and routes to mechanical remedies or a human.
4. **No auto-merge** — the loop may propose and verify; landing on main is
   always human-reviewed.
Re-trigger: several rounds of real L1/L2 data accumulated, or a regression
suspicion the manual loop is too slow to chase. `skill-dev-toolkit:skill-tuning`
is the candidate variant-diversification engine when this builds.

## Acceptance (whole arc)

- The checker, run against the 6 committed matrix artifacts' known results,
  reproduces the graded anchor/deferred/negative verdicts (spot-validated).
- The workflow script dry-parses (meta + phases valid) and its grade stage
  invokes ONLY deterministic scripts for the verdict.
- BACKLOG harness entry points at this brief's §Level 3 instead of restating.
