---
name: a-bias-control-specified-at-the-data-level-is-not-a-control
description: A control specified as a shape in the data — two runs, two verdicts, two records — is satisfiable by an implementation in which the control does not exist, because the property that made it a control lives in the process that produced those records; a conforming implementation then pays the full cost and buys nothing, and every scenario still passes
type: gotcha
origin: 2026-08-28, independent-advisor spec expansion — the order-counterbalancing requirement had two swap runs with two verdicts and no requirement that the runs be independent
---

The `independent-advisor` spec set out to defeat position bias: a judge
comparing two proposals favours whichever it reads first, and the fix is to
show it the pair in both orders. The requirement was written as the shape that
fix leaves in the data — two `swap_run` records, each carrying a verdict,
disagreement recorded as inconclusive rather than averaged.

Every scenario was satisfiable by one judge, in one session, answering twice.

That implementation has two runs and two verdicts. It passes. It also has no
counterbalancing at all, because the second answer is conditioned on the first
— the judge remembers what it just said, and a remembered answer is not an
independent second reading. The spec bought two dispatches' worth of cost and
received one reading.

The general shape: **a control is a property of the PROCESS that produces the
records, and a spec that describes only the records has not specified the
control.** The records are the residue, not the mechanism. Anonymisation has
the same structure — stripping the label is data-level, while the register,
the length, and a leftover first person leak identity through the process that
wrote the card.

Two things this costs when it is missed:

- **It is invisible to per-requirement review.** Each scenario reads correctly
  against its requirement. The gap only appears when someone asks "could a
  fully conforming implementation still have the defect?" — a question about
  the space of conforming implementations, not about the text.
- **It fails expensively rather than loudly.** An absent control produces
  plausible output at full price. Nothing errors.

What to write instead, in the requirement itself, not in a note beside it: the
run happens in a fresh executor process with no transcript, session, or cache
carried over, and that isolation is recorded. And say explicitly which cheaper
substitute is NOT permitted — here, a prompt-level instruction telling the
judge to ignore the order, which measurement shows is weak where the structural
swap is not.

The test to apply to any control-shaped requirement, before it ships: describe
the laziest implementation that satisfies every scenario, then ask whether the
control survives in it.
