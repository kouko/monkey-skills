# Ablation Mode — section-splitter + worked example

Detail behind `SKILL.md` §Ablation mode. Use this to find which sections of a
skill add words without adding behavioral capability, **without** needing a
control group (ancestor / sibling skill) to compare against.

## Section splitter (leave-one-out)

Split the target SKILL.md into top-level `## ` sections (keep the frontmatter +
any pre-header preamble in every variant). For each section, emit a variant that
is the full skill **minus that one section**. Pseudocode:

```python
# read SKILL.md → keep frontmatter (head) + split body on top-level "## " headers
# for each section i: variant_i = head + body with section i removed
# write each variant to /tmp/<skill>-abl/abl-<i>-<slug>.md
```

Run the same `test-prompts.json` (the gate's behavioral eval) through the FULL
skill and through each variant; a judge ensemble compares full-vs-ablated per
section. **Map each section to the prompt(s) that exercise its purpose** — a
section whose trigger no prompt hits will read as bloat regardless (the coverage
caveat). For navigational sections, judge by hand.

## Cost

Roughly `(1 + N_sections) × N_relevant_prompts` runs + 2 judges. Bound it: feed
each section only the prompt(s) that exercise it (not the full cross product). A
prototype with 2 prompts + 7 sections ran in ~11 subagent calls.

## Verdict mapping

| Ensemble on a section | Meaning | Action |
|---|---|---|
| Both judges: behavior unchanged | BLOAT candidate | compress or cut (then pass the Q1/Q2/Q3 gate) |
| Both judges: behavior degraded | LOAD-BEARING | keep |
| SPLIT (judges disagree) across **two related sections** | the two are REDUNDANT with each other | **merge the pair** into one tighter section — do NOT delete either alone |
| SPLIT on an isolated section | uncertain | investigate by hand / add a sharper test prompt |

## Worked example — verification-before-completion (2026-05-30 prototype)

7 sections, 2 prompts (P1 = "ran the test FILE directly, good to merge?" → correct
= refuse + demand package-level run; P2 = "bumped version + README, done without
tests?" → correct = doc/config exemption). 2-judge ensemble:

| Section removed | Verdict |
|---|---|
| When NOT to use | **LOAD-BEARING** (2/2) — removal made the agent demand `npm test` on a doc change (broke the exemption) |
| Process | BLOAT (2/2) — agent reconstructed the procedure from the HARD-GATE alone |
| Cross-skill contract | BLOAT (2/2) — integration table never fires on a direct user prompt |
| What this skill does NOT do | BLOAT (2/2) — scope prose; behavior survives |
| See also | BLOAT (2/2) — link list; zero enforcement |
| The HARD-GATE | SPLIT — bloat per judge A *because Red Flags covers it* |
| Red Flags | SPLIT — bloat per judge B *because the HARD-GATE covers it* |

**Reading:** the positive control fired (When-NOT-to-use is load-bearing, caught
by both judges). The HARD-GATE / Red-Flags SPLIT is the redundancy trap — they
overlap (both encode "refuse unverified done-claims, demand package-level run"),
so leave-one-out shows each as removable, but you can't remove both → **merge
them**. Refactor targets produced with no control group: merge HARD-GATE+Red-Flags,
compress Process (drop the detection-signals list that duplicates
`test-invocation-by-stack.md`), trim Cross-skill / What-NOT / See-also.

## Sources

- ablation studies on prompt components are non-monotonic — generic additions can
  *degrade* task accuracy; validate each component against a task eval, not intuition
  (arXiv:2601.22025, "When Better Prompts Hurt").
- context rot: surplus input tokens measurably degrade output quality, complex tasks
  worst (Chroma 2025; LongLLMLingua arXiv:2310.06839 — 4× fewer tokens, +17% accuracy).
  So a confirmed-bloat cut is often net-positive, not neutral.
