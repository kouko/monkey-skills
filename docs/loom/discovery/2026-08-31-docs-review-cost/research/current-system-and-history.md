# Research question 1 — Where does the current review cost arise?

## Goal

Identify observed cost sources in Monkey Skills without assuming that either
the writer or reviewer is solely responsible.

## Method

- Read the two dedicated convergence audits and the yellow-finding sample.
- Read the current `requesting-docs-review` convergence contract and
  `docs-reviewer` role contract.
- Inspect Git history from the standalone skill's 2026-07-30 ship commit through
  2026-08-31.
- Count the current core contract surface with `wc -l`.

## Findings

### Initial artifact quality contributed materially

The nine-round branch began with multiple real defects, including stale claims,
contradictions, incomplete population sweeps, and instructions inconsistent with
code. Six rounds also found a defect introduced by the preceding fix. This is
direct evidence that both initial prose and remediation quality created review
work (`evidence.md` C1–C2).

### Reviewer sampling contributed materially

Four fresh reviewers examining an already-passed corpus returned seven mutually
disjoint gating findings. The checked findings were grounded in actual passages,
so the observed problem was not simply fabrication; the reviewer sampled a
large residual defect pool inconsistently (`evidence.md` C3–C4).

### The current loop bounds repetition but does not measure effectiveness

The current contract permits one full round and one confirmation. This caps the
runaway-loop symptom. It does not retain comparable measures of review cost,
finding precision, defect escape, or fix-introduced defects (`evidence.md` C7,
C9).

### Maintenance surface

Commands run from the repository root:

```text
git log --since=2026-07-30 --format='%H' -- \
  loom-code/skills/requesting-docs-review \
  loom-code/agents/docs-reviewer.md | sort -u | wc -l
```

Result: `27` commits.

```text
wc -l loom-code/skills/requesting-docs-review/SKILL.md \
  loom-code/agents/docs-reviewer.md \
  loom-code/skills/requesting-docs-review/references/convergence-contract.md
```

Result: `177 + 759 + 43 = 979` lines. This is not a complexity score, but it is
a direct continuing-maintenance surface for the core reviewer contracts.

## Insight skeleton

- Need: know whether review effort removes consequential defects efficiently.
- Evidence: C1–C9.
- Current workaround: infer quality from individual review narratives and add
  rules after incidents.
- Unknown: the post-0.75.0 cost and defect-escape rate cannot be reconstructed
  from durable data.
