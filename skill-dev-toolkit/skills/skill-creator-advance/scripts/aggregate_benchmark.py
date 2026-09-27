# Aggregate Benchmark Script

Python module for aggregating benchmark results from multiple iterations.

## Usage
```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

## Functionality
- Collects timing.json, grading.json, and metrics.json from test cases
- Computes aggregate statistics across iterations
- Generates benchmark.json for skill comparison
- Detects performance trends and regressions