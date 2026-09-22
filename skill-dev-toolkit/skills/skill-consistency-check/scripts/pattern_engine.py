#!/usr/bin/env python3
"""
Pattern matching engine for static rule checks (Layer 1).

Detects logical contradictions and inconsistencies using patterns from
conflict-patterns.md. This is the first layer of the three-layer
verification architecture: fast pattern matching before SMT and LLM.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any
from collections import defaultdict


# ============================================================================
# PATTERN DEFINITIONS (mirroring conflict-patterns.md)
# ============================================================================

PATTERNS = [
    # CONF-DC: Direct Contradictions
    {
        'id': 'CONF-DC-001',
        'name': 'Validation Contradiction',
        'category': 'CONF-DC',
        'severity': 'Critical',
        'detect': 'validation_contradiction',
    },
    {
        'id': 'CONF-DC-002',
        'name': 'Script Modification Contradiction',
        'category': 'CONF-DC',
        'severity': 'Critical',
        'detect': 'script_modification_contradiction',
    },
    {
        'id': 'CONF-DC-003',
        'name': 'Reference vs Reality Contradiction',
        'category': 'CONF-DC',
        'severity': 'Critical',
        'detect': 'reference_reality_contradiction',
    },
    # CONF-CD: Circular Dependencies
    {
        'id': 'CONF-CD-001',
        'name': 'Phase Circular Dependency',
        'category': 'CONF-CD',
        'severity': 'Critical',
        'detect': 'phase_circular_dependency',
    },
    {
        'id': 'CONF-CD-002',
        'name': 'Agent Circular Invocation',
        'category': 'CONF-CD',
        'severity': 'High',
        'detect': 'agent_circular_invocation',
    },
    # CONF-CV: Contract Violations
    {
        'id': 'CONF-CV-001',
        'name': 'Description-Implementation Mismatch',
        'category': 'CONF-CV',
        'severity': 'High',
        'detect': 'description_implementation_mismatch',
    },
    {
        'id': 'CONF-CV-002',
        'name': 'Gate Declaration vs Reality',
        'category': 'CONF-CV',
        'severity': 'High',
        'detect': 'gate_declaration_vs_reality',
    },
    # CONF-UR: Undefined References
    {
        'id': 'CONF-UR-001',
        'name': 'Missing Reference File',
        'category': 'CONF-UR',
        'severity': 'High',
        'detect': 'missing_reference_file',
    },
    {
        'id': 'CONF-UR-002',
        'name': 'Missing Script Reference',
        'category': 'CONF-UR',
        'severity': 'High',
        'detect': 'missing_script_reference',
    },
    {
        'id': 'CONF-UR-003',
        'name': 'Missing Agent Reference',
        'category': 'CONF-UR',
        'severity': 'High',
        'detect': 'missing_agent_reference',
    },
    # CONF-MECH: Mechanical Issues
    {
        'id': 'CONF-MECH-001',
        'name': 'Nested Subdirectories',
        'category': 'CONF-MECH',
        'severity': 'Critical',
        'detect': 'nested_subdirectories',
    },
    {
        'id': 'CONF-MECH-002',
        'name': 'Overlong Description',
        'category': 'CONF-MECH',
        'severity': 'High',
        'detect': 'overlong_description',
    },
    {
        'id': 'CONF-MECH-003',
        'name': 'Missing Frontmatter Fields',
        'category': 'CONF-MECH',
        'severity': 'Critical',
        'detect': 'missing_frontmatter_fields',
    },
    # CONF-IAC: Implicit Assumption Conflicts
    {
        'id': 'CONF-IAC-001',
        'name': 'Freedom Mismatch',
        'category': 'CONF-IAC',
        'severity': 'Medium',
        'detect': 'freedom_mismatch',
    },
    {
        'id': 'CONF-IAC-002',
        'name': 'Procedure in Description',
        'category': 'CONF-IAC',
        'severity': 'Medium',
        'detect': 'procedure_in_description',
    },
]


# ============================================================================
# DETECTION FUNCTIONS
# ============================================================================

def find_rules_by_keyword(rules: list[dict], keywords: list[str]) -> list[dict]:
    """Find rules containing any of the keywords (case-insensitive)."""
    result = []
    for rule in rules:
        text = rule.get('text', '').lower()
        if any(kw.lower() in text for kw in keywords):
            result.append(rule)
    return result


def detect_validation_contradiction(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-DC-001: MUST validate vs NEVER validate."""
    issues = []
    rules = extracted_data.get('rules', [])

    validate_must = find_rules_by_keyword(rules, ['must validate', 'always validate', 'required to validate'])
    validate_never = find_rules_by_keyword(rules, ['never validate', 'must not validate', 'prohibited to validate'])

    if validate_must and validate_never:
        for m in validate_must:
            for n in validate_never:
                issues.append({
                    'pattern_id': 'CONF-DC-001',
                    'type': 'direct_contradiction',
                    'severity': 'Critical',
                    'file': m['file'],
                    'line': m['line'],
                    'message': "Contradiction: MUST/ALWAYS validate and NEVER/MUST NOT validate both present",
                    'rules': [m, n],
                    'confidence': 'high',
                    'suggested_fix': 'Remove one of the contradictory rules or clarify the validation scope'
                })
    return issues


def detect_script_modification_contradiction(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-DC-002: MUST use exact script vs NEVER modify script."""
    issues = []
    rules = extracted_data.get('rules', [])

    use_exact = find_rules_by_keyword(rules, ['use exact script', 'use the exact script'])
    never_modify = find_rules_by_keyword(rules, ['never modify', 'must not modify', 'do not modify'])

    if use_exact and never_modify:
        for u in use_exact:
            for n in never_modify:
                issues.append({
                    'pattern_id': 'CONF-DC-002',
                    'type': 'direct_contradiction',
                    'severity': 'Critical',
                    'file': u['file'],
                    'line': u['line'],
                    'message': "Contradiction: MUST use exact script and NEVER modify script",
                    'rules': [u, n],
                    'confidence': 'high',
                    'suggested_fix': 'Clarify whether script modification is allowed for bug fixes vs behavior changes'
                })
    return issues


def detect_reference_reality_contradiction(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-DC-003: Claim references unused vs agent doesn't know to load."""
    issues = []
    rules = extracted_data.get('rules', [])
    frontmatter = extracted_data.get('frontmatter', {})

    references_unused = find_rules_by_keyword(rules, ['references sit unused', 'reference unused', 'unused reference'])
    agent_doesnt_know = find_rules_by_keyword(rules, ['agent does not know', "agent doesn't know", 'agent cannot find'])

    if references_unused and agent_doesnt_know:
        for r in references_unused:
            for a in agent_doesnt_know:
                issues.append({
                    'pattern_id': 'CONF-DC-003',
                    'type': 'direct_contradiction',
                    'severity': 'Critical',
                    'file': r['file'],
                    'line': r['line'],
                    'message': "Contradiction: References claimed unused but agent cannot load them",
                    'rules': [r, a],
                    'confidence': 'medium',
                    'suggested_fix': 'Add explicit reference loading instructions or auto-load mechanism'
                })
    return issues


def detect_phase_circular_dependency(skill_path: Path, extracted_data: dict, graph_data: dict) -> list[dict]:
    """CONF-CD-001: Phase A reads from Phase B, Phase B uses Phase A's plan."""
    issues = []
    # This is primarily detected by the dependency graph (check_circular_dependencies)
    # Here we add pattern-specific detection from text
    rules = extracted_data.get('rules', [])

    phase_a_reads_b = find_rules_by_keyword(rules, ['phase a', 'read.*phase b', 'output from phase b'])
    phase_b_uses_a = find_rules_by_keyword(rules, ['phase b', 'plan from phase a', 'use.*phase a'])

    if phase_a_reads_b and phase_b_uses_a:
        for a in phase_a_reads_b:
            for b in phase_b_uses_a:
                issues.append({
                    'pattern_id': 'CONF-CD-001',
                    'type': 'circular_dependency',
                    'severity': 'Critical',
                    'file': a['file'],
                    'line': a['line'],
                    'message': "Circular dependency: Phase A reads Phase B output, Phase B uses Phase A plan",
                    'rules': [a, b],
                    'confidence': 'medium',
                    'suggested_fix': 'Restructure phases to have a clear linear order or shared intermediate artifact'
                })
    return issues


def detect_agent_circular_invocation(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-CD-002: Agent A invokes B, B invokes A."""
    issues = []
    references = extracted_data.get('references', [])

    # Build agent invocation graph from references
    invocations = defaultdict(set)
    for ref in references:
        if ref['type'] == 'agent':
            # We need context - check surrounding rules for invocations
            pass

    # Check rules for invocation patterns
    rules = extracted_data.get('rules', [])
    for rule in rules:
        text = rule.get('text', '').lower()
        # Look for "invoke agent X" or "call agent X"
        invoke_match = re.search(r'(invoke|call|run|execute)\s+(?:the\s+)?(?:agent|subagent)\s+([a-z0-9\-_]+)', text)
        if invoke_match:
            # This is a heuristic - would need more context to build full graph
            pass

    return issues


def detect_description_implementation_mismatch(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-CV-001: Description promises validation, implementation has none."""
    issues = []
    frontmatter = extracted_data.get('frontmatter', {})
    description = frontmatter.get('description', '').lower()

    # Check if description claims validation
    promises_validation = any(kw in description for kw in ['validat', 'check', 'verify', 'ensure'])
    if not promises_validation:
        return issues

    # Check if any script actually does validation
    scripts_dir = skill_path / 'scripts'
    has_validation_code = False
    if scripts_dir.exists():
        for script_file in scripts_dir.glob('*.py'):
            try:
                content = script_file.read_text(encoding='utf-8')
                if any(kw in content.lower() for kw in ['validat', 'assert', 'check', 'verify']):
                    has_validation_code = True
                    break
            except Exception:
                pass

    if promises_validation and not has_validation_code:
        issues.append({
            'pattern_id': 'CONF-CV-001',
            'type': 'contract_violation',
            'severity': 'High',
            'file': 'SKILL.md',
            'line': 0,
            'message': "Description promises validation/checking but no validation code found in scripts",
            'details': {'description': frontmatter.get('description', '')},
            'confidence': 'medium',
            'suggested_fix': 'Add validation logic to scripts or update description to match implementation'
        })
    return issues


def detect_gate_declaration_vs_reality(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-CV-002: Gate declares strict pass, actually passes on partial success."""
    issues = []
    rules = extracted_data.get('rules', [])

    gate_strict = find_rules_by_keyword(rules, ['gate passes if all', 'all assertions must pass', 'require all'])
    gate_soft = find_rules_by_keyword(rules, ['soft assertion', 'partial success', 'warn but continue'])

    if gate_strict and gate_soft:
        for s in gate_strict:
            for f in gate_soft:
                issues.append({
                    'pattern_id': 'CONF-CV-002',
                    'type': 'contract_violation',
                    'severity': 'High',
                    'file': s['file'],
                    'line': s['line'],
                    'message': "Gate declares strict pass criteria but implementation allows partial success",
                    'rules': [s, f],
                    'confidence': 'medium',
                    'suggested_fix': 'Align gate implementation with declared criteria or update declaration'
                })
    return issues


def detect_missing_reference_file(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-UR-001: Reference to non-existent file in references/."""
    issues = []
    # This is also caught by check_consistency.py mechanical checks
    # Adding here for pattern-specific reporting
    references = extracted_data.get('references', [])

    # Track which missing references we've already reported to avoid duplicates
    reported_missing = set()

    for ref in references:
        if ref['type'] == 'reference':
            target = skill_path / 'references' / ref['name']
            if not target.exists():
                # Create a key for deduplication: (reference name)
                dedup_key = ref['name']
                if dedup_key in reported_missing:
                    continue
                reported_missing.add(dedup_key)

                issues.append({
                    'pattern_id': 'CONF-UR-001',
                    'type': 'undefined_reference',
                    'severity': 'High',
                    'file': ref['file'],
                    'line': ref['line'],
                    'message': f"Referenced file '{ref['name']}' does not exist at references/{ref['name']}",
                    'details': {'reference': ref},
                    'confidence': 'high',
                    'suggested_fix': f"Create references/{ref['name']} or remove the reference"
                })
    return issues


def detect_missing_script_reference(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-UR-002: Reference to non-existent script in scripts/."""
    issues = []
    references = extracted_data.get('references', [])

    # Track which missing references we've already reported to avoid duplicates
    reported_missing = set()

    for ref in references:
        if ref['type'] == 'script':
            target = skill_path / 'scripts' / ref['name']
            if not target.exists():
                # Create a key for deduplication: (reference name)
                dedup_key = ref['name']
                if dedup_key in reported_missing:
                    continue
                reported_missing.add(dedup_key)

                issues.append({
                    'pattern_id': 'CONF-UR-002',
                    'type': 'undefined_reference',
                    'severity': 'High',
                    'file': ref['file'],
                    'line': ref['line'],
                    'message': f"Referenced script '{ref['name']}' does not exist at scripts/{ref['name']}",
                    'details': {'reference': ref},
                    'confidence': 'high',
                    'suggested_fix': f"Create scripts/{ref['name']} or remove the reference"
                })
    return issues


def detect_missing_agent_reference(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-UR-003: Reference to non-existent agent."""
    issues = []
    references = extracted_data.get('references', [])
    agents_dir = skill_path / 'agents'

    agent_files = set()
    if agents_dir.exists():
        agent_files = {f.stem for f in agents_dir.glob('*.md')}

    # Track which missing references we've already reported to avoid duplicates
    reported_missing = set()

    for ref in references:
        if ref['type'] == 'agent':
            agent_name = ref['name']
            # Also check for plugin:agent format
            if ':' in agent_name:
                agent_name = agent_name.split(':', 1)[1]

            if agent_name not in agent_files:
                # Create a key for deduplication: (agent name)
                dedup_key = agent_name
                if dedup_key in reported_missing:
                    continue
                reported_missing.add(dedup_key)

                issues.append({
                    'pattern_id': 'CONF-UR-003',
                    'type': 'undefined_reference',
                    'severity': 'High',
                    'file': ref['file'],
                    'line': ref['line'],
                    'message': f"Referenced agent '{ref['name']}' not found in agents/ directory",
                    'details': {'reference': ref},
                    'confidence': 'medium',
                    'suggested_fix': f"Create agents/{agent_name}.md or use correct agent name"
                })
    return issues


def detect_nested_subdirectories(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-MECH-001: Nested subdirectories violate flat folder convention."""
    issues = []
    allowed_dirs = ('scripts', 'references', 'assets', 'agents', 'checklists', 'protocols', 'standards', 'rubrics', 'templates')

    for item in skill_path.iterdir():
        if item.is_dir() and item.name in allowed_dirs:
            for sub in item.iterdir():
                if sub.is_dir():
                    issues.append({
                        'pattern_id': 'CONF-MECH-001',
                        'type': 'nested_subdirectory',
                        'severity': 'Critical',
                        'file': f"{item.name}/{sub.name}",
                        'line': 0,
                        'message': f"Nested subdirectory '{item.name}/{sub.name}' violates flat folder convention",
                        'confidence': 'high',
                        'suggested_fix': f"Move contents of {item.name}/{sub.name} to a top-level directory or flatten structure"
                    })
    return issues


def detect_overlong_description(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-MECH-002: Description exceeds 250 chars (soft) or 1024 (hard)."""
    issues = []
    frontmatter = extracted_data.get('frontmatter', {})
    description = frontmatter.get('description', '')

    if len(description) > 1024:
        issues.append({
            'pattern_id': 'CONF-MECH-002',
            'type': 'description_too_long',
            'severity': 'High',
            'file': 'SKILL.md',
            'line': 0,
            'message': f"Description is {len(description)} chars (exceeds hard limit 1024)",
            'confidence': 'high',
            'suggested_fix': 'Shorten description to ≤250 characters (soft limit) or ≤1024 (hard limit)'
        })
    elif len(description) > 250:
        issues.append({
            'pattern_id': 'CONF-MECH-002',
            'type': 'description_too_long',
            'severity': 'Medium',
            'file': 'SKILL.md',
            'line': 0,
            'message': f"Description is {len(description)} chars (exceeds soft limit 250)",
            'confidence': 'high',
            'suggested_fix': 'Shorten description to ≤250 characters to avoid context eviction'
        })
    return issues


def detect_missing_frontmatter_fields(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-MECH-003: Missing required frontmatter fields (name, description) in SKILL.md."""
    issues = []
    # Only check SKILL.md frontmatter, not reference files
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return issues

    content = skill_md.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return issues

    end = content.find('---', 3)
    if end == -1:
        return issues

    fm_text = content[3:end].strip()
    # Simple check for required fields
    required = ['name', 'description']
    for req in required:
        if f'{req}:' not in fm_text:
            issues.append({
                'pattern_id': 'CONF-MECH-003',
                'type': 'missing_frontmatter',
                'severity': 'Critical',
                'file': 'SKILL.md',
                'line': 0,
                'message': f"Missing required frontmatter field: {req}",
                'confidence': 'high',
                'suggested_fix': f"Add {req} field to SKILL.md frontmatter"
            })
    return issues


def detect_freedom_mismatch(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-IAC-001: Claims high freedom but constrains to exact script."""
    issues = []
    frontmatter = extracted_data.get('frontmatter', {})
    description = frontmatter.get('description', '').lower()
    rules = extracted_data.get('rules', [])

    claims_freedom = any(kw in description for kw in ['high freedom', 'multiple approaches', 'flexible', 'various ways'])
    if not claims_freedom:
        return issues

    constrains_script = find_rules_by_keyword(rules, ['use exact script', 'must use script', 'only use script'])

    if claims_freedom and constrains_script:
        for c in constrains_script:
            issues.append({
                'pattern_id': 'CONF-IAC-001',
                'type': 'implicit_assumption_conflict',
                'severity': 'Medium',
                'file': c['file'],
                'line': c['line'],
                'message': "Description claims high freedom but rules constrain to exact script",
                'details': {'description': frontmatter.get('description', ''), 'rule': c},
                'confidence': 'medium',
                'suggested_fix': 'Align description with actual constraints or relax script constraints'
            })
    return issues


def detect_procedure_in_description(skill_path: Path, extracted_data: dict) -> list[dict]:
    """CONF-IAC-002: Description contains step-by-step procedure."""
    issues = []
    frontmatter = extracted_data.get('frontmatter', {})
    description = frontmatter.get('description', '')

    # Check for step-by-step patterns
    step_patterns = [
        r'step\s+\d+',
        r'first[,:]',
        r'then[,:]',
        r'next[,:]',
        r'finally[,:]',
        r'\d+\.\s',  # numbered list
    ]

    has_procedure = any(re.search(p, description, re.IGNORECASE) for p in step_patterns)

    if has_procedure:
        issues.append({
            'pattern_id': 'CONF-IAC-002',
            'type': 'procedure_in_description',
            'severity': 'Medium',
            'file': 'SKILL.md',
            'line': 0,
            'message': "Description contains step-by-step procedure (should be in body, not description)",
            'details': {'description': description},
            'confidence': 'medium',
            'suggested_fix': 'Move procedural steps to the skill body; keep description as a one-sentence summary'
        })
    return issues


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

DETECTION_FUNCTIONS = {
    'validation_contradiction': detect_validation_contradiction,
    'script_modification_contradiction': detect_script_modification_contradiction,
    'reference_reality_contradiction': detect_reference_reality_contradiction,
    'phase_circular_dependency': detect_phase_circular_dependency,
    'agent_circular_invocation': detect_agent_circular_invocation,
    'description_implementation_mismatch': detect_description_implementation_mismatch,
    'gate_declaration_vs_reality': detect_gate_declaration_vs_reality,
    'missing_reference_file': detect_missing_reference_file,
    'missing_script_reference': detect_missing_script_reference,
    'missing_agent_reference': detect_missing_agent_reference,
    'nested_subdirectories': detect_nested_subdirectories,
    'overlong_description': detect_overlong_description,
    'missing_frontmatter_fields': detect_missing_frontmatter_fields,
    'freedom_mismatch': detect_freedom_mismatch,
    'procedure_in_description': detect_procedure_in_description,
}


def run_pattern_checks(skill_path: Path, extracted_data: dict, graph_data: dict = None) -> list[dict]:
    """Run all pattern detection checks and return issues."""
    all_issues = []

    for pattern in PATTERNS:
        detect_func_name = pattern['detect']
        detect_func = DETECTION_FUNCTIONS.get(detect_func_name)

        if not detect_func:
            print(f"Warning: No detection function for {detect_func_name}", file=sys.stderr)
            continue

        try:
            if detect_func_name in ('phase_circular_dependency',):
                issues = detect_func(skill_path, extracted_data, graph_data or {})
            else:
                issues = detect_func(skill_path, extracted_data)

            # Add pattern metadata to each issue
            for issue in issues:
                issue['pattern_id'] = pattern['id']
                issue['pattern_name'] = pattern['name']
                issue['category'] = pattern['category']
                if 'severity' not in issue:
                    issue['severity'] = pattern['severity']

            all_issues.extend(issues)
        except Exception as e:
            print(f"Error in {detect_func_name}: {e}", file=sys.stderr)

    # Sort by severity
    severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    all_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'Low'), 4))

    return all_issues


def main():
    if len(sys.argv) < 2:
        print("Usage: pattern_engine.py <skill_directory> [extracted_json_file] [graph_json_file]", file=sys.stderr)
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    extracted_data = {}
    graph_data = {}

    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            extracted_data = json.load(f)

    if len(sys.argv) > 3:
        with open(sys.argv[3], 'r') as f:
            graph_data = json.load(f)

    issues = run_pattern_checks(skill_path, extracted_data, graph_data)
    json.dump(issues, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()