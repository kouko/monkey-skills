---
name: skill-consistency-check
description: |
  Checks logical consistency within a skill or group of text files. Detects contradictions, circular dependencies, contract violations, and undefined references. Use for 'validate this skill' or 'check these files for internal conflicts'.
version: 0.1.0
---
# Skill Consistency Checker

This skill verifies that a skill (or a set of text files) is logically consistent internally. It checks for:

- **Direct contradictions**: e.g., `MUST do X` and `NEVER do X` in the same context.
- **Circular dependencies**: e.g., Phase A requires Phase B's output, and Phase B requires Phase A's output.
- **Contract violations**: the declared behavior (in description, agent prompts, or gates) does not match the actual implementation (scripts, agent definitions, workflow).
- **Undefined references**: references to non-existent sections, files, or variables.
- **Mechanical consistency**: all referenced files exist and are used as declared.

The skill uses a layered verification approach:
1. **Static rule engine** (fast, deterministic): extracts rules and builds dependency graphs.
2. **SMT formal verification** (strong guarantees): encodes hard constraints (MUST/NEVER/ALWAYS) into SMT-LIB and checks with Z3.
3. **LLM cross-verification** (broad coverage): uses multiple models to vote on semantic consistency and detect implicit assumption conflicts.

Input: a path to a skill directory (containing SKILL.md and bundled resources) or a list of text files.
Output: a structured report (JSONL and Markdown) listing conflicts with location, severity, and suggested fixes.

## How It Works

### Stage 1: Parse and Extract
- Reads SKILL.md and all bundled files (references/, scripts/, assets/, agents/).
- Extracts frontmatter, section headers, code blocks, and natural language statements.
- Identifies rule-like statements (MUST, NEVER, ALWAYS, SHOULD, prohibited, required).
- Builds a symbol table of all defined entities (sections, files, agents, scripts, variables).

### Stage 2: Build Dependency Graph
- Constructs a directed graph where nodes are rules, phases, agents, scripts, and files.
- Edges represent dependencies (e.g., "Phase A runs before Phase B", "Script X is invoked in Phase Y", "Rule R1 depends on Rule R2").
- Checks for circular dependencies using graph algorithms (Tarjan's SCC).

### Stage 3: Check for Conflicts
- **Layer 1 (Static Rules)**: Uses regex and tree-sitter to find known anti-patterns (nested folders, overlong description, missing MUST list).
- **Layer 2 (SMT)**: Encodes MUST/NEVER/ALWAYS statements into SMT-LIB and checks for satisfiability with Z3.
- **Layer 3 (LLM)**: Uses multiple LLMs (Sonnet, Opus, Haiku) to vote on semantic consistency and detect implicit assumption conflicts via adversarial probing.

### Stage 4: Generate Report
- Outputs a JSONL report machine-readable for other skills to consume.
- Outputs a human-readable Markdown report with severity levels (Critical/High/Medium/Low) and suggested fixes.

## Usage

Invoke this skill with a path to a skill directory:

```
/skill-consistency-check /path/to/skill
```

Or check multiple files:

```
/skill-consistency-check file1.md file2.py file3.txt
```

The skill will automatically detect if the input is a skill directory (by looking for SKILL.md) or treat it as a list of files.

## Output Format

The report includes:
- **Location**: file path and line number (or section) of the conflict.
- **Type**: contradiction, circular_dependency, contract_violation, undefined_reference, etc.
- **Severity**: Critical, High, Medium, Low (based on impact and likelihood).
- **Evidence**: the conflicting statements or context.
- **Suggested Fix**: a concrete edit to resolve the conflict.

## Examples

### Direct Contradiction
```markdown
## Workflow
**MUST**: Validate the input before processing.
**NEVER**: validate the input (it is always valid).
```
→ Report: Contradiction between MUST and NEVER on validation.

### Circular Dependency
```markdown
### Phase A: Generate Plan
Read the output from Phase B to create the plan.

### Phase B: Execute Plan
Use the plan generated in Phase A to execute.
```
→ Report: Circular dependency between Phase A and Phase B.

### Contract Violation
```markdown
description: "Validates user input and returns a clean dataset."
```
But the actual script does no validation and assumes clean input.
→ Report: Contract violation - description promises validation but implementation does not perform it.

## Notes

- This skill is **advisory** — it points out potential issues but does not automatically fix them.
- For mechanical fixes (e.g., missing files), the skill will suggest the exact path to create or correct.
- For logical fixes (e.g., removing a contradiction), the skill will suggest removing or rephrasing the conflicting statement.
- The skill is safe to run on any text file, but is most effective on skill files (SKILL.md and bundled resources).
- To skip certain checks (e.g., if you know a reference is intentionally missing), use the `--skip-mechanical` flag.

---