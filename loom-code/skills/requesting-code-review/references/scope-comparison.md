Source: `requesting-code-review/SKILL.md` §"When this is different from SDD's per-task reviewer" — serves `requesting-code-review`.

# When this is different from SDD's per-task reviewer

| Dimension | SDD `code-quality-reviewer` (per task) | `requesting-code-review` (whole branch) |
|---|---|---|
| Scope | One atomic task's output | Cumulative branch diff (all tasks combined) |
| When fires | During each SDD task triad | After all SDD work is DONE; before merge |
| Sees | One commit / one module | The full branch diff vs main |
| Catches | Per-task quality lapses | Cross-task interactions, scope creep, architectural coherence |
| Verdict aggregation | Per-task | Per-branch |

Same rubrics, different diff scope: per-task review catches "this commit has bad naming"; whole-branch review catches "tasks 1-4 each made sense individually but together they introduced a circular dependency."
