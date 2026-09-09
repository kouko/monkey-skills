# Claude Code hook dogfood

Date: 2026-09-09
Executor: Claude Code, Fable, high effort
Candidate base: loom-code 2.0.4

## Scope

The run attempted four read-only commands whose arguments contained literal
publication text. It was instructed to distinguish Loom PreToolUse rejection
from Claude Code permission rejection and to perform no publication action.

## Result

| Case | Expected | Observed |
|---|---|---|
| `rg` with a literal `gh pr create` pattern | execute | executed, rc 0 |
| `rg` with literal push and PR alternatives | execute | executed, rc 0 |
| Python printing `git push origin HEAD` | execute | executed, rc 0 |
| `printf` of single-quoted `$(git push origin HEAD)` | execute | executed, rc 0 |

No command was denied by the Loom hook or Claude Code permission layer. No
additional classifier defect was reproduced, so this dogfood run earns no
new production behavior or permanent test beyond the already scoped `$()`
executable-substitution regression.
