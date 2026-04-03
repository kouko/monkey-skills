# Code Quality Review Gate

## Prerequisites

This gate runs AFTER the security checklist passes. Do not re-evaluate
security concerns already covered by `checklists/security-checklist.md`.

## Flag Definitions

### Correctness & Logic
- 🔴 **Fatal**: Obvious logic error, infinite loop risk, or unguarded null/undefined reference
- 🔴 **Fatal**: Race condition in concurrent code without synchronization
- 🟡 **Warning**: Missing defensive programming for likely edge cases
- 🟡 **Warning**: Error handling catches too broadly (bare `catch` swallowing all errors)
- 🟢 **Clear**: Normal and exception paths are properly handled

### API & Breaking Changes
- 🔴 **Fatal**: Public API contract broken without version bump or migration path
- 🔴 **Fatal**: Database migration would cause data loss on existing records
- 🟡 **Warning**: Undocumented behavioral change in a public interface
- 🟢 **Clear**: API contracts preserved or properly versioned

### Design
- 🟡 **Warning**: Single function exceeds 100 lines
- 🟡 **Warning**: Variable names lack semantic meaning (e.g., `let a = 1`, `temp`, `data`)
- 🟡 **Warning**: Copy-paste duplication across 3+ locations
- 🟢 **Clear**: Code is clear, SOLID principles respected where appropriate

### Tests
- 🟡 **Warning**: Critical path (money, auth, data mutation) lacks test coverage
- 🟢 **Clear**: Test coverage exists for high-risk paths

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- Read the full file before flagging (don't review snippets in isolation)
- Suggest fixes, don't just point out problems
- If the code works and is clear, say "LGTM" — don't invent issues
- Max 5 flags per review (prioritize by impact)
- Reference `standards/code-conventions.md` for objective style rules

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: File path + line number + specific problem
3. **Fix Instruction**: How the worker should resolve this flag
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-fixed without human review.
Include exact file paths and line numbers.
