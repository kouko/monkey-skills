# Eval Methodology

Optional reference. Read this to understand *why* the eval workflow is
designed the way it is. Each concept maps to a step or pattern in the
main SKILL.md.

---

## 1. Baseline Comparison

**Principle:** In experimental design, you can't measure the effect of a
treatment without a control group. The control shows what happens *without*
the intervention, so any difference can be attributed to the treatment.

**In skill-creator-advance:** Step 1 spawns both a with-skill run and a
baseline run (without-skill or old-skill) for every test case. Without
the baseline, you can't tell if the skill actually helped — maybe Claude
would have produced the same output on its own.

**When it matters most:** When the skill is subtle (formatting conventions,
style guidance) rather than structural (multi-step workflows). Subtle skills
might not show improvement without a baseline to compare against.

> Source: Fisher, R.A. *The Design of Experiments* (1935). Established
> the foundational principle that valid causal inference requires a
> control group.

---

## 2. Assertion-based Evaluation

**Principle:** Subjective quality judgments are unreliable across evaluators
and over time. Assertions convert subjective criteria into binary pass/fail
checks that anyone can verify — similar to unit tests in software.

**In skill-creator-advance:** Step 2 drafts assertions for each test case.
Good assertions are objectively verifiable ("output contains a summary
section") rather than subjective ("output is well-written").

**When to use assertions vs. human review:** Use assertions for structural
and factual criteria (presence of sections, correct format, data accuracy).
Use human review for subjective quality (writing style, design aesthetics,
overall usefulness). Don't force assertions onto subjective dimensions.

> Source: Beck, K. *Test-Driven Development: By Example* (2002).
> Introduced assertions as executable specifications that serve as
> both documentation and verification. Also: IEEE 829-2008, Standard
> for Software and System Test Documentation.

---

## 3. Train/Test Split

**Principle:** If you optimize against all your data, you'll find a solution
that works perfectly for that specific data but fails on new data. Holding
out a portion of data as a "test set" that you never optimize against
reveals whether your improvements generalize.

**In skill-creator-advance:** Description optimization splits trigger eval
queries into 60% train and 40% test. The optimizer proposes description
improvements based on train-set failures, then evaluates on the held-out
test set. The best description is selected by test score, not train score.

**Why 60/40 and not 80/20:** With only ~20 eval queries, an 80/20 split
leaves only 4 test queries — too few to be reliable. 60/40 balances having
enough training signal with enough test coverage.

> Source: Hastie, T., Tibshirani, R. & Friedman, J. *The Elements of
> Statistical Learning* (2nd ed., 2009), Ch. 7 "Model Assessment and
> Selection." Establishes train/test methodology and cross-validation
> as standard practice for model evaluation.

---

## 4. Overfitting & Generalization

**Principle:** A model (or skill) that performs perfectly on its training
examples but poorly on new examples has "overfit" — it memorized the
examples rather than learning the underlying pattern. The goal is
generalization: performing well on inputs it has never seen.

**In skill-creator-advance:** The improvement philosophy (point 1) warns
against overfitting: "You're iterating on a few examples, but the skill
will be used across many different prompts. Don't overfit to specific
test cases." This applies to both:
- **Skill instructions** — Don't add rules that fix test case #2 but
  would harm a different prompt
- **Description optimization** — Select by test score, not train score

**Practical signal:** If your skill passes all test cases but the user
reports it failing on real prompts, you've likely overfit.

> Source: Hastie et al. (2009), Ch. 7. Also: Vapnik, V. *The Nature
> of Statistical Learning Theory* (1995). Formalized the bias-variance
> tradeoff and the theoretical basis for generalization.

---

## 5. Regression Testing

**Principle:** When you fix one thing, you might break another. Regression
testing systematically checks whether previously passing criteria still
pass after a change. The term comes from software testing: a "regression"
is when something that used to work stops working.

**In skill-creator-advance:** Auto-regression detection (iteration 2+)
compares assertion results between iterations. A PASS → FAIL transition
is flagged as a regression. This is implemented in
`references/iteration-automation.md`.

**Why not auto-fix regressions:** Regressions are sometimes intentional
trade-offs. If you restructure a skill's output format, old assertions
about the previous format will fail — that's expected, not a bug. The
human decides whether each regression is acceptable.

> Source: Myers, G.J., Sandler, C. & Badgett, T. *The Art of Software
> Testing* (3rd ed., 2011), Ch. 8 "System Testing." Also: IEEE 610.12
> defines regression testing as "selective retesting of a system or
> component to verify that modifications have not caused unintended
> effects."

---

## 6. Blind Comparison

**Principle:** When an evaluator knows which output comes from which
version, they're susceptible to observer bias — unconsciously favoring
the version they expect to be better. Blind evaluation removes this
bias by hiding the identity of each output.

**In skill-creator-advance:** The blind comparison system (Advanced
section) gives two outputs to an independent agent without revealing
which is which. The agent judges quality purely on merit, then the
analyzer explains why the winner won.

**When to use:** When you suspect your own judgment is biased (e.g.,
you just spent hours improving the skill and want to believe it's
better). Also useful when two approaches seem equivalent and you need
a tie-breaker.

> Source: Schulz, K.F. & Grimes, D.A. "Blinding in randomised trials:
> hiding who got what." *The Lancet* 359 (2002): 696–700. Established
> evidence that unblinded assessors overestimate treatment effects by
> ~20%. Also: Karanicolas, P.J. et al. "Blinding: Who, what, when,
> why, how?" *Canadian Journal of Surgery* 53.5 (2010): 345–348.

---

## 7. Variance & Statistical Significance

**Principle:** A single measurement can be misleading due to random
variation. Running the same test multiple times and computing mean ±
standard deviation reveals how consistent the results are. High variance
means the result is unreliable — the skill might just be getting lucky
(or unlucky) on any given run.

**In skill-creator-advance:** The benchmark aggregation computes mean
and stddev for pass rates, timing, and token usage. Description
optimization runs each query 3 times for reliability.

**What to watch for:**
- **High stddev in pass rate** → The skill is flaky. Sometimes it
  follows the instructions, sometimes it doesn't. Fix the root cause
  rather than rerunning until you get a good result.
- **High stddev in timing** → Some test cases are much harder than
  others, or the skill's approach varies significantly between runs.

> Source: Walpole, R.E., Myers, R.H. et al. *Probability & Statistics
> for Engineers and Scientists* (9th ed., 2012). Standard reference for
> variance, standard deviation, and confidence intervals. Also:
> Demšar, J. "Statistical Comparisons of Classifiers over Multiple
> Data Sets." *JMLR* 7 (2006): 1–30 — on why single-run comparisons
> are unreliable in ML evaluation.

---

## 8. Non-discriminating Tests

**Principle:** A test that always passes (or always fails) regardless
of conditions provides no information. In experiment design, these are
called "non-discriminating" — they can't distinguish between a good
and bad treatment because the outcome is the same either way.

**In skill-creator-advance:** The analyst pass (Step 4) looks for
assertions that pass in both the with-skill and baseline conditions.
If an assertion passes 100% of the time for both, it tells you nothing
about whether the skill helps — Claude would have passed it anyway.

**What to do about them:**
- **Remove** if the assertion is genuinely trivial (e.g., "output is
  not empty" — Claude almost never produces empty output)
- **Tighten** if the assertion is too loose (e.g., change "output
  mentions the topic" to "output includes a structured analysis with
  at least 3 specific recommendations")
- **Keep** if the assertion guards against a real failure mode that
  just hasn't triggered yet

> Source: ISTQB Foundation Level Syllabus (v4.0, 2023), §4.3 "Test
> Techniques" — defines test effectiveness as the ratio of defects
> found to defects present; non-discriminating tests have zero
> effectiveness. Also: Hutchins, M. et al. "Experiments on the
> Effectiveness of Dataflow- and Control-flow-based Test Adequacy
> Criteria." *ICSE* (1994) — empirical evidence that test suite
> quality depends on fault detection capability, not just coverage.
