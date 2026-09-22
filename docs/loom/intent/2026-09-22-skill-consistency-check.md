# skill-consistency-check: complete three-layer architecture
originator: kouko
kind: engineering
needs-design: no — library-level verification tool, no UI or user-facing changes
evidence: [skills/skill-consistency-check/]
status: confirmed 2026-09-22

## Problem
The plugin lacked a systematic way to detect logical contradictions and inconsistencies within skill files. Each skill was validated manually, with no automated gate preventing contradictory rules from being merged.

## Proposed outcome
A three-layer verification architecture that can be invoked by any downstream skill (dogfood-skill-testing, skill-judge, skill-creator-advance) as a gate check:
1. Layer 1 (Pattern Engine): 14 conflict patterns detecting direct contradictions, circular dependencies, contract violations, undefined references, mechanical issues, and implicit assumption conflicts
2. Layer 2 (SMT/Z3): Formal verification using Z3 solver with auto-install
3. Layer 3 (LLM Cross-Verification): Placeholder for multi-LLM semantic consistency voting

The tool provides machine-readable exit codes (0=PASS, 1=NEEDS_REVISION, 2=ERROR) and CLI flags for flexible integration into any pipeline.

## Acceptance
1. `skill-consistency-check --help` shows all flags: `--format`, `--skip-layer`, `--quiet`, `--no-llm`, `--verbose`
2. Exit code 0 when no Critical/High issues found
3. Exit code 1 when Critical/High issues found
4. Exit code 2 on error (invalid path, missing scripts)
5. `--format=jsonl` outputs one JSON object per line for machine consumption
6. `--skip-layer=pattern|smt|llm` allows skipping specific verification layers
7. `--no-llm` is shorthand for `--skip-layer=llm`
8. Pattern engine detects all 14 patterns from conflict-patterns.md with deduplication
9. Z3 auto-install works and SMT verification returns satisfiable/unsatisfiable
10. Frontmatter check only applies to SKILL.md (not reference files)

## Constraints
- No cross-skill dependencies introduced
- The tool must be self-contained and runnable standalone
- Pattern detection must not produce duplicate reports for the same reference

## Out of scope
- Layer 3 LLM cross-verification implementation (placeholder retained for future)
- Integration into dogfood-skill-testing and skill-judge pipelines (separate task)
- Auto-fix capabilities based on suggested_fix field

## Open questions
- How should the LLM cross-verification layer be implemented when ready?
- Should `--min-severity` flag be added to filter output by minimum severity level?

## Value case
This tool provides the foundation for automated skill quality gates, enabling downstream skills to verify consistency before proceeding with their own checks.
