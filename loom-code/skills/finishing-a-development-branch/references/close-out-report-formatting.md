# N/A consolidation — close-out report formatting

Load when the close-out report is about to list two or more N/A sub-checks from Step 8's table.

When two or more close-out sub-checks are N/A, do NOT stack ~4-5 separate "N/A — checker not present" lines before the conclusion. Each N/A stays STATEABLE (the per-check "say loudly" semantics are preserved — the check still runs and names its reason), but in the Step 13 report they consolidate inapplicable checks into ONE summary line after the plain conclusion: "N inapplicable checks skipped: <list>; details on request." Conclusion-first — the user sees the outcome before skipped-checks noise. A single N/A still emits its own one-line note; only the multi-N/A case collapses.
