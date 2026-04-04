# QA Final Verification Gate

## Prerequisites

This is the LAST gate before delivery. It runs after the security
checklist and quality gate have both passed. Focus on what they
might have missed, not re-checking their scope.

## Flag Definitions

### Correctness (Final Check)
- 🔴 **Fatal**: Edge case that causes crash or data corruption
- 🔴 **Fatal**: Feature does not match the original requirements
- 🟡 **Warning**: Edge case produces incorrect but non-catastrophic result
- 🟢 **Clear**: All requirements met; edge cases handled

### Performance
- 🔴 **Fatal**: N+1 query pattern in database access
- 🔴 **Fatal**: Unnecessary I/O operation inside a loop (file read, network call)
- 🟡 **Warning**: Unnecessary memory allocation that could be avoided
- 🟡 **Warning**: Missing pagination or limit on unbounded queries
- 🟢 **Clear**: No obvious performance anti-patterns

### Maintainability
- 🟡 **Warning**: Complex logic block (>10 lines of conditionals) without explanatory comment
- 🟡 **Warning**: Naming inconsistency with surrounding codebase conventions
- 🟢 **Clear**: Code is self-documenting; follows `standards/code-conventions.md`

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: File path + line number + specific problem
3. **Fix Instruction**: How the worker should resolve this flag
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Never sugar-coat. Be direct and specific.
Include file paths and line numbers for every flag.
