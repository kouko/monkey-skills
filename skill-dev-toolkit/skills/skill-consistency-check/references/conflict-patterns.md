# Conflict Patterns for Skill Consistency Checker

This file contains known patterns of logical contradictions and inconsistencies found in skill files, based on historical data from the monkey-skills repository and industry best practices.

## Pattern Categories

### Direct Contradictions (CONF-DC)
These occur when a skill states both a requirement and its prohibition for the same action.

#### CONF-DC-001: Validation Contradiction
- **MUST**: "Validate input before processing"
- **NEVER**: "Validate input (it is always clean)"
- **Source**: feedback_timeout_killed_suite_leaves_orphan_xdist_workers

#### CONF-DC-002: Script Modification Contradiction
- **MUST**: "Use exact script in scripts/create-doc.py"
- **NEVER**: "Modify the script"
- **Source**: feedback_implementer_distracted_no_commit_pattern

#### CONF-DC-003: Reference vs Reality Contradiction
- **MUST**: "References sit unused" (claim)
- **REALITY**: "Agent doesn't know when to load" (cause)
- **Source**: feedback_dogfood_operator_patches_mask_bugs

### Circular Dependencies (CONF-CD)
These create infinite loops in execution flow.

#### CONF-CD-001: Phase Circular Dependency
- **Phase A**: "Read output from Phase B to create plan"
- **Phase B**: "Use plan from Phase A to execute"
- **Source**: feedback_loom_git_guard_evaluates_in_shell_cwd

#### CONF-CD-002: Agent Circular Invocation
- **Agent A**: "Invoke Agent B to get data"
- **Agent B**: "Invoke Agent A to validate data"
- **Pattern**: Common in poorly designed multi-agent systems

### Contract Violations (CONF-CV)
These occur when declared behavior doesn't match implementation.

#### CONF-CV-001: Description-Implementation Mismatch
- **Description**: "Validates user input and returns clean dataset"
- **Implementation**: Script assumes input is clean, does no validation
- **Source**: feedback_dont_blindly_execute_brief_remove_when_test_encodes_design

#### CONF-CV-002: Gate Declaration vs Reality
- **Description**: "Gate passes if all assertions pass"
- **Reality**: Gate passes on partial success due to soft assertions
- **Pattern**: Common in evaluation systems

### Undefined References (CONF-UR)
References to non-existent entities.

#### CONF-UR-001: Missing Reference File
- **Reference**: `[`workflow-spec.md`](references/workflow-spec.md)`
- **Reality**: File does not exist in references/ directory
- **Source**: feedback_missing_required_store_content_ask_user_fill_now

#### CONF-UR-002: Missing Script Reference
- **Reference**: "Run scripts/validate-input.py"
- **Reality**: No such file in scripts/ directory
- **Source**: feedback_never_git_add_dash_A_in_this_repo

#### CONF-UR-003: Missing Agent Reference
- **Reference**: "Invoke subagent: analysis-team"
- **Reality**: No such agent defined in agents/ directory
- **Pattern**: Common in delegation systems

### Mechanical Issues (CONF-MECH)
Issues with file structure and mechanical correctness.

#### CONF-MECH-001: Nested Subdirectories
- **Violation**: `assets/scripts/extract_lineage.py` (assets/ contains scripts/)
- **Rule**: Skill root may contain only single-level subdirectories
- **Source**: feedback_skill_structure_name_allowlist_parked_delete_on_next_loosen

#### CONF-MECH-002: Overlong Description
- **Issue**: Description exceeds 250 characters (soft limit) or 1024 (hard limit)
- **Impact**: Evicts other skills from Claude's context budget
- **Source**: 2026-06-19-skill-description-standard.md

#### CONF-MECH-003: Missing Frontmatter Fields
- **Missing**: `name` or `description` in SKILL.md frontmatter
- **Impact**: Skill cannot be triggered or identified properly
- **Pattern**: Common in early drafts

### Implicit Assumption Conflicts (CONF-IAC)
Where natural language implies something that contradicts explicit rules.

#### CONF-IAC-001: Freedom Mismatch
- **Explicit**: "High freedom: Multiple valid approaches"
- **Implicit**: "Use exact script in scripts/create-doc.py" (low freedom)
- **Source**: feedback_gate_review_weight_on_task_kind_not_loc

#### CONF-IAC-002: Procedure in Description
- **Explicit**: "Keep step-by-step procedure out of description"
- **Implicit**: Description contains "Step 1: Open file, Step 2: Edit..."
- **Source**: 2026-06-19-skill-description-standard.md

### Usage Instructions

Each pattern can be used to:
1. Generate detection rules for the static rule engine (Layer 1)
2. Create SMT templates for formal verification (Layer 2)
3. Generate adversarial probes for LLM verification (Layer 3)

To add a new pattern:
1. Document the contradiction with clear BEFORE/AFTER examples
2. Specify the severity (Critical/High/Medium/Low)
3. Provide detection mechanisms for each layer
4. Add to this file with a unique pattern ID

---