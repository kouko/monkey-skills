# Modularize the Loom checker
originator: kouko
kind: engineering
needs-design: no — internal Python module boundaries change while the existing CLI surface and output remain unchanged
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem
`loom-code/scripts/loom_checker.py` concentrates checker rules, parsing, digests, attestation validation, probes, command handlers, and publication logic in one large file. This makes isolated rule testing difficult and raises the risk that changing one rule or command affects unrelated behavior.

## Proposed outcome
The Loom checker has explicit module boundaries for rules, shared parsing and helpers, artifact and attestation logic, and individual command handlers, while its existing entry point remains stable.

## Acceptance
1. Each checker rule can be imported and tested independently without loading unrelated command implementations.
2. Each existing subcommand is implemented in its own command module, with shared parsing and helper behavior provided by dedicated common modules.
3. `loom-code/scripts/loom_checker.py` contains only the documented CLI entry point responsibilities: the command registry, rule-list dispatch, and `main`.
4. Every existing command name, accepted argument, output format, exit code, direct script invocation, and PreToolUse hook invocation behaves exactly as before.
5. Repository consumers that import checker behavior and the mechanism-population check continue to resolve the checker rules after modularization.
6. The existing Loom checker tests and relevant integration checks pass without adding an external dependency or modifying `git_exec.py`.

## Constraints
- Use only the existing standard-library, PyYAML, and repository-owned `git_exec` dependencies.
- Preserve `loom-code/scripts/loom_checker.py` as the `__main__` and hook entry path.
- Do not change `loom-code/scripts/git_exec.py`.
- Keep edits surgical to the checker modularization and its directly affected tests or consumers.

## Out of scope
- Changing checker policy, CLI behavior, output wording, exit codes, hook behavior, or attestation semantics.
- Refactoring unrelated Loom scripts or adding new checker rules or subcommands.

## Open questions
- none
