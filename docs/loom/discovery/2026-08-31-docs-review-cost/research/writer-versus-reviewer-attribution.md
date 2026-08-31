# Research question 2 — Is the dominant cause writing quality or review quality?

## Goal

Determine whether available evidence supports assigning the dominant cost to
the writer, the reviewer, or their interaction.

## Method

- Classify historical observations by defect origin: pre-existing prose,
  remediation-introduced prose, reviewer sampling, and review-policy behavior.
- Compare project-local observations with English and Japanese research on LLM
  evaluator consistency and bias.
- Preserve the limits of each corpus; no historical rate is generalized to the
  current version.

## Findings

### The evidence rejects a single-cause explanation

- Writer side: real defects existed before review and fixes repeatedly created
  new defects (C1–C2).
- Reviewer side: separate reviewers returned disjoint subsets on identical
  artifacts (C3), matching external evidence that LLM evaluator behavior varies
  by model, task, sample, prompt, and textual likelihood (C10–C12).
- Policy side: an unbounded “no findings means done” stop rule cannot converge
  when reviewers sample a large pool; delta scoping changes the termination
  behavior without proving the pool empty (C5, C7).

The best-supported causal model is an interaction: a sizeable prose defect pool
multiplied by a variable sampler, followed by fixes that can replenish the pool.

### “Reviewer found another issue” is not equivalent to reviewer failure

The seven-finding experiment and the historical yellow sample both indicate that
many later findings were consequential. The yellow sample is selection-biased,
so it cannot estimate the proportion of all findings that matter, but it refutes
the simple assumption that later findings are mostly cosmetic noise (C4, C6).

### “The review passed” is not equivalent to document completeness

Because reviewers disagree and sampling is incomplete, a pass only describes
the sampled run under a particular contract and model. External EN and JA
research independently supports measuring evaluator consistency rather than
assuming it (C10–C12).

## Insight skeleton

- Need: separate source defects, fix defects, reviewer variance, and policy
  effects before changing the process.
- Evidence: C1–C7, C10–C12.
- Current workaround: interpret every new finding as another repair request,
  then tune contracts after costly incidents.
- Unknown: false-positive and false-negative rates against a stable human-owned
  oracle have not been measured for the current reviewer.
