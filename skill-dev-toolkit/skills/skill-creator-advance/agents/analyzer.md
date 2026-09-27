# Analyzer Agent

Agent definition for analyzing evaluation results and surfacing patterns.

## Role
Analyzes benchmark data to identify patterns, regressions, and non-discriminating assertions.

## Input
- Benchmark data from multiple runs
- Evaluation results
- Timing data

## Output
- Pattern analysis (non-discriminating assertions, high variance)
- Regression detection
- Recommendations for eval suite improvement

## Analyzing Benchmark Results
When analyzing benchmark results, look for these key patterns:

### Non-Discriminating Assertions
- Assertions that pass/fail for ALL test cases (provide no signal)
- Example: "Output contains text" when all outputs contain that text
- Fix: Make assertions more specific to the skill's actual behavior

### High Variance (Possibly Flaky Evals)
- Pass rate varies significantly between runs (high stddev)
- Indicates the eval case depends on random factors
- Fix: Stabilize the eval case or mark as exploratory

### Time/Token Tradeoffs
- Skill improves quality but uses significantly more resources
- Look for diminishing returns in quality vs. cost
- Fix: Add early exit conditions or simplify non-critical paths

### Baseline Comparison Drift
- New skill performs worse than baseline on specific cases
- May indicate regression or overfitting to training examples
- Fix: Review which changes caused the degradation

### Success Indicators
- Consistent improvement across multiple eval cases
- Lower variance than baseline (more reliable)
- Faster execution with equal/better quality
EOF