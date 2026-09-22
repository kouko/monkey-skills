# Severity Rubric for Consistency Issues

This rubric defines how to classify the severity of detected consistency issues in skill files.

## Severity Levels

### Critical (🔴)
**Definition**: Issues that make the skill fundamentally broken, impossible to execute correctly, or produce dangerously wrong outputs.

**Criteria**:
- Direct logical contradiction (MUST X ∧ NEVER X in same context)
- SMT unsatisfiability (entire rule set is contradictory)
- Circular dependency that prevents any execution order
- Missing required frontmatter (skill cannot be triggered)
- Nested subdirectory violation (breaks tooling/hooks)

**Examples**:
- `MUST validate input` + `NEVER validate input`
- Phase A requires Phase B, Phase B requires Phase A
- SKILL.md missing `name` field
- `assets/scripts/foo.py` exists (nested subdirectory)

**Impact**: Skill will fail at runtime or produce unpredictable results. Must fix before use.

**Time to Fix**: Immediate (blocker)

---

### High (🟠)
**Definition**: Issues that will likely cause failures, incorrect behavior, or significant confusion during execution.

**Criteria**:
- Undefined reference to required file/script/agent
- Contract violation (description promises X, implementation does Y)
- Missing critical gate or validation step
- Circular dependency with workaround (e.g., optional phases)
- Overlong description that evicts other skills

**Examples**:
- References `scripts/validate.py` but file doesn't exist
- Description says "validates input" but script has no validation
- `phase_a` and `phase_b` form cycle but one is optional
- Description is 400 characters (exceeds 250 soft limit)

**Impact**: High probability of runtime errors or silent incorrect behavior.

**Time to Fix**: Within 24 hours (high priority)

---

### Medium (🟡)
**Definition**: Issues that reduce clarity, maintainability, or may cause problems in edge cases.

**Criteria**:
- Unused files (scripts, references) that clutter the skill
- Ambiguous rules that could be interpreted multiple ways
- Missing soft constraints (SHOULD without MUST backing)
- Inconsistent naming conventions
- Incomplete documentation in references

**Examples**:
- `scripts/legacy-helper.py` exists but never referenced
- Rule says "handle errors appropriately" without specifics
- `SHOULD validate` but no `MUST validate` backing it
- Some scripts use `snake_case`, others `camelCase`
- Reference file lacks table of contents

**Impact**: Technical debt, increased maintenance cost, potential future bugs.

**Time to Fix**: Next sprint (planned)

---

### Low (🟢)
**Definition**: Minor issues that don't affect correctness but improve consistency and readability.

**Criteria**:
- Style inconsistencies (formatting, capitalization)
- Missing optional frontmatter fields (version, compatibility)
- Redundant but non-contradictory rules
- Minor formatting issues in code blocks
- Unused variables in scripts

**Examples**:
- Some MUST statements use "MUST:", others "MUST -"
- Frontmatter missing optional `version` field
- Two rules say the same thing in different words
- Code block missing language annotation
- Script has unused import

**Impact**: Cosmetic, no functional impact.

**Time to Fix**: When convenient (cleanup)

---

## Decision Tree

```
Is the issue a direct logical contradiction or makes the skill unrunnable?
    │
    ├─ YES → Critical
    │
    └─ NO → Does it cause a high probability of runtime failure?
              │
              ├─ YES → High
              │
              └─ NO → Does it reduce maintainability or create technical debt?
                        │
                        ├─ YES → Medium
                        │
                        └─ NO → Low
```

## Special Cases

### Multiple Issues at Same Location
If multiple issues are found at the same file/line, classify at the **highest severity** among them.

### Context-Dependent Severity
Some issues may change severity based on context:
- Unused script in `scripts/` → Medium (clutter)
- Unused script that's a security risk → High
- Overlong description in skill with 5 skills → Medium
- Overlong description in skill with 200 skills → High (eviction risk)

### Confidence Levels
When the analyzer is uncertain about an issue, add a `confidence` field:
- `high`: Clear pattern match, high confidence
- `medium`: Pattern match with some ambiguity
- `low`: Heuristic-based detection, may be false positive

Low-confidence Medium/Low issues can be downgraded; Low-confidence Critical/High should be flagged for human review.

---

## Escalation Path

| Severity | Escalation |
|----------|------------|
| Critical | Block skill usage until fixed. Auto-fail CI if present. |
| High | Require fix before merge. Auto-fail CI if present. |
| Medium | Warn in CI. Require fix within 2 sprints. |
| Low | Info in CI. Fix at maintainer's discretion. |

---

## Tool Integration

The severity classification is used by:
1. **Static rule engine (Layer 1)**: Applies pattern-based severity from conflict-patterns.md
2. **SMT verification (Layer 2)**: Unsatisfiable → Critical, Unexpected model → Medium
3. **LLM verification (Layer 3)**: LLM judges severity based on this rubric
4. **Report generator**: Sorts issues by severity, highlights Critical/High

---