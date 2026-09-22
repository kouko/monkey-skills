#!/usr/bin/env python3
"""
Checks for mechanical consistency: file existence, reference resolution, etc.
"""

import json
import sys
from pathlib import Path
from typing import Any


def check_mechanical(skill_path: Path, extracted_data: dict) -> list[dict]:
    """Check mechanical consistency issues."""
    issues = []

    # Check that all referenced files exist
    for ref in extracted_data.get('references', []):
        if ref['type'] == 'script':
            target = skill_path / 'scripts' / ref['name']
            if not target.exists():
                issues.append({
                    'type': 'undefined_reference',
                    'severity': 'High',
                    'file': ref['file'],
                    'line': ref['line'],
                    'message': f"Referenced script '{ref['name']}' does not exist at scripts/{ref['name']}",
                    'reference': ref
                })
        elif ref['type'] == 'reference':
            target = skill_path / 'references' / ref['name']
            if not target.exists():
                issues.append({
                    'type': 'undefined_reference',
                    'severity': 'High',
                    'file': ref['file'],
                    'line': ref['line'],
                    'message': f"Referenced file '{ref['name']}' does not exist at references/{ref['name']}",
                    'reference': ref
                })

    # Check for unused files (files not referenced anywhere)
    referenced_files = set()
    for ref in extracted_data.get('references', []):
        if ref['type'] == 'script':
            referenced_files.add(f"scripts/{ref['name']}")
        elif ref['type'] == 'reference':
            referenced_files.add(f"references/{ref['name']}")

    # Get all files in scripts/ and references/ directories
    scripts_dir = skill_path / 'scripts'
    refs_dir = skill_path / 'references'

    if scripts_dir.exists():
        for script_file in scripts_dir.iterdir():
            if script_file.is_file() and script_file.suffix in ('.py', '.sh', '.js'):
                rel = f"scripts/{script_file.name}"
                if rel not in referenced_files:
                    issues.append({
                        'type': 'unused_file',
                        'severity': 'Low',
                        'file': str(rel),
                        'line': 0,
                        'message': f"Script file '{rel}' is not referenced anywhere in the skill",
                        'reference': {'type': 'script', 'name': script_file.name}
                    })

    if refs_dir.exists():
        for ref_file in refs_dir.iterdir():
            if ref_file.is_file() and ref_file.suffix == '.md':
                rel = f"references/{ref_file.name}"
                if rel not in referenced_files:
                    issues.append({
                        'type': 'unused_file',
                        'severity': 'Low',
                        'file': str(rel),
                        'line': 0,
                        'message': f"Reference file '{rel}' is not referenced anywhere in the skill",
                        'reference': {'type': 'reference', 'name': ref_file.name}
                    })

    # Check SKILL.md frontmatter
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                fm = content[3:end]
                # Check for required fields
                required = ['name', 'description']
                for req in required:
                    if f'{req}:' not in fm:
                        issues.append({
                            'type': 'missing_frontmatter',
                            'severity': 'Medium',
                            'file': 'SKILL.md',
                            'line': 0,
                            'message': f"Missing required frontmatter field: {req}"
                        })

                # Check description length
                import re
                desc_match = re.search(r'description:\s*[\'"]?(.*?)[\'"]?(?:\n|$)', fm, re.DOTALL)
                if desc_match:
                    desc = desc_match.group(1).strip()
                    if len(desc) > 250:
                        issues.append({
                            'type': 'description_too_long',
                            'severity': 'Medium',
                            'file': 'SKILL.md',
                            'line': 0,
                            'message': f"Description is {len(desc)} chars (recommended ≤250, hard cap 1024)"
                        })

    # Check for nested subdirectories (violates flat folder convention)
    # Allowed top-level directories
    allowed_dirs = ('scripts', 'references', 'assets', 'agents', 'checklists', 'protocols', 'standards', 'rubrics', 'templates')
    for item in skill_path.iterdir():
        if item.is_dir():
            # Check if this top-level directory has subdirectories
            for sub in item.iterdir():
                if sub.is_dir():
                    issues.append({
                        'type': 'nested_subdirectory',
                        'severity': 'Critical',
                        'file': f"{item.name}/{sub.name}",
                        'line': 0,
                        'message': f"Nested subdirectory '{item.name}/{sub.name}' violates flat folder convention (only single-level subdirectories allowed)"
                    })

    return issues


def check_circular_dependencies(graph_data: dict) -> list[dict]:
    """Detect circular dependencies in the dependency graph using Tarjan's SCC."""
    # Build adjacency list
    adj = defaultdict(list)
    node_types = {}

    for node_id, node in graph_data['nodes'].items():
        node_types[node_id] = node['type']

    for edge in graph_data['edges']:
        adj[edge['from']].append(edge['to'])

    # Tarjan's algorithm for strongly connected components
    index = 0
    indices = {}
    lowlink = {}
    on_stack = set()
    stack = []
    sccs = []

    def strongconnect(v):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in adj.get(v, []):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in adj:
        if v not in indices:
            strongconnect(v)

    # Filter SCCs with size > 1 (or self-loop)
    issues = []
    for scc in sccs:
        if len(scc) > 1:
            # Found a cycle
            nodes_in_cycle = []
            for node_id in scc:
                node = graph_data['nodes'][node_id]
                nodes_in_cycle.append({
                    'id': node_id,
                    'type': node['type'],
                    'data': node['data']
                })
            issues.append({
                'type': 'circular_dependency',
                'severity': 'High',
                'file': nodes_in_cycle[0]['data'].get('file', 'unknown'),
                'line': nodes_in_cycle[0]['data'].get('line', 0),
                'message': f"Circular dependency detected among {len(scc)} nodes",
                'cycle_nodes': nodes_in_cycle
            })

    return issues


def check_contradictions(extracted_data: dict, smt_result: dict) -> list[dict]:
    """Check for direct contradictions in rules."""
    issues = []

    # Direct contradiction detection from rule text
    rules = extracted_data.get('rules', [])

    # Group by proposition-like text
    rule_groups = defaultdict(list)
    for rule in rules:
        # Simplified: group by normalized text
        key = re.sub(r'[^a-z0-9]+', '_', rule['text'].lower())[:64]
        rule_groups[key].append(rule)

    for key, group in rule_groups.items():
        if len(group) > 1:
            types = [r['type'] for r in group]
            has_must = any(t in ('explicit', 'always', 'must') for t in types)
            has_never = any(t in ('never', 'must_not', 'should_not') for t in types)

            if has_must and has_never:
                issues.append({
                    'type': 'direct_contradiction',
                    'severity': 'Critical',
                    'file': group[0]['file'],
                    'line': group[0]['line'],
                    'message': f"Contradiction: MUST/ALWAYS and NEVER/MUST NOT rules about the same thing",
                    'rules': group
                })

    # Add SMT contradictions if available
    if smt_result and not smt_result.get('satisfiable', True):
        issues.append({
            'type': 'smt_unsatisfiable',
            'severity': 'Critical',
            'file': 'multiple',
            'line': 0,
            'message': 'Rule set is logically unsatisfiable (SMT verification failed)',
            'details': smt_result.get('contradictions', [])
        })

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: check_consistency.py <skill_directory> [extracted_json_file] [graph_json_file] [smt_json_file]", file=sys.stderr)
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    extracted_data = {}
    graph_data = {}
    smt_result = {}

    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            extracted_data = json.load(f)

    if len(sys.argv) > 3:
        with open(sys.argv[3], 'r') as f:
            graph_data = json.load(f)

    if len(sys.argv) > 4:
        with open(sys.argv[4], 'r') as f:
            smt_result = json.load(f)

    all_issues = []
    all_issues.extend(check_mechanical(skill_path, extracted_data))

    if graph_data:
        all_issues.extend(check_circular_dependencies(graph_data))

    all_issues.extend(check_contradictions(extracted_data, smt_result))

    # Sort by severity
    severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    all_issues.sort(key=lambda x: severity_order.get(x['severity'], 4))

    json.dump(all_issues, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    import re
    from collections import defaultdict
    main()