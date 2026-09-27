# Iteration Automation

Utility functions for skill iteration workflow including regression detection, timing analysis, and improvement suggestions.

These are documented procedures that agents follow during evaluation — not an importable Python module. The function signatures describe the expected inputs and outputs for each analysis step.

## Regression Detection

Detects skill regressions by comparing pass rates between versions.

**Procedures:**
- **calculate_pass_rate_delta(current, baseline)** → Returns percentage point difference between current and baseline pass rates
- **is_significant_regression(delta, threshold=0.15)** → Returns True if delta < -threshold (meaningful degradation of 15% or more)
- **detect_flaky_eval(pass_rates)** → Returns True if stddev > 0.25 (high variance indicates flakiness)

**Usage in evaluation:**
When comparing iteration results, compute the pass rate delta. If `is_significant_regression(delta)` returns True, flag as regression and report to user.

## Timing Analysis

Analyzes execution time trends and identifies performance regressions.

**Procedures:**
- **analyze_timing_trend(times)** → Returns {"trend": "improving"/"degrading"/"stable", "slope": float}
- **flag_performance_regression(current_time, baseline_mean, baseline_stddev)** → True if current > baseline_mean + 2*baseline_stddev
- **identify_outlier_cases(case_timings)** → Returns list of eval IDs with timing > Q3 + 1.5*IQR

## Improvement Suggestions

Generates actionable suggestions based on benchmark analysis.

**Procedures:**
- **suggest_assertion_improvements(failed_assertions)** → Recommends how to make assertions more specific
- **suggest_doc_improvements(unclear_outputs)** → Recommends adding examples or constraints to description
- **suggest_tool_usage_changes(unexpected_tools)** → Flags tools used that aren't in allowed-tools list

## Benchmark Aggregation Helpers

**Procedures:**
- **aggregate_run_summary(runs)** → Computes mean/stddev for pass_rate, time_seconds, tokens per configuration
- **calculate_improvement_delta(with_skill, without_skill)** → Returns improvement strings like "+0.50"
- **validate_benchmark_structure(data)** → Ensures benchmark.json follows schema before viewer consumption