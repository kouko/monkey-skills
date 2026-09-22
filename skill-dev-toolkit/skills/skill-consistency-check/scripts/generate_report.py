#!/usr/bin/env python3
"""
Generates the final consistency report in JSONL and Markdown formats.
"""

import json
import sys
from pathlib import Path
from typing import Any


def generate_report(issues: list[dict], skill_path: Path, extracted_data: dict = None,
                    graph_data: dict = None, smt_result: dict = None) -> dict:
    """Generate the full report."""

    # Count by severity
    severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    for issue in issues:
        severity_counts[issue['severity']] = severity_counts.get(issue['severity'], 0) + 1

    # Build summary
    summary = {
        'skill_path': str(skill_path),
        'total_issues': len(issues),
        'severity_counts': severity_counts,
        'files_checked': len(extracted_data.get('files', [])) if extracted_data else 0,
        'rules_found': len(extracted_data.get('rules', [])) if extracted_data else 0,
        'sections_found': len(extracted_data.get('sections', [])) if extracted_data else 0,
    }

    if smt_result:
        summary['smt_verification'] = {
            'available': smt_result.get('z3_available', False),
            'satisfiable': smt_result.get('satisfiable', True)
        }

    # Build detailed issues
    detailed_issues = []
    for issue in issues:
        detailed_issue = {
            'id': f"{issue['type']}_{issue['file']}_{issue['line']}",
            'type': issue['type'],
            'severity': issue['severity'],
            'file': issue['file'],
            'line': issue['line'],
            'message': issue['message'],
            'suggested_fix': issue.get('suggested_fix', suggest_fix(issue))
        }
        # Preserve pattern-specific fields
        for field in ['pattern_id', 'pattern_name', 'category', 'confidence', 'details']:
            if field in issue:
                detailed_issue[field] = issue[field]
        if 'reference' in issue:
            detailed_issue['reference'] = issue['reference']
        if 'rules' in issue:
            detailed_issue['conflicting_rules'] = [
                {'file': r['file'], 'line': r['line'], 'type': r['type'], 'text': r['text']}
                for r in issue['rules']
            ]
        if 'cycle_nodes' in issue:
            detailed_issue['cycle_nodes'] = issue['cycle_nodes']
        detailed_issues.append(detailed_issue)

    return {
        'summary': summary,
        'issues': detailed_issues
    }


def suggest_fix(issue: dict) -> str:
    """Suggest a fix for the given issue."""
    issue_type = issue['type']

    if issue_type == 'undefined_reference':
        ref = issue.get('reference', {})
        if ref.get('type') == 'script':
            return f"Create the missing script at scripts/{ref['name']} or update the reference to point to an existing script."
        elif ref.get('type') == 'reference':
            return f"Create the missing reference file at references/{ref['name']} or update the reference."
        return "Create the missing file or update the reference to an existing file."

    elif issue_type == 'unused_file':
        ref = issue.get('reference', {})
        if ref.get('type') == 'script':
            return f"Either reference this script in your skill (e.g., in agent prompts or workflow) or remove it if no longer needed."
        return "Either reference this file in your skill or remove it if no longer needed."

    elif issue_type == 'missing_frontmatter':
        field = issue['message'].split(': ')[-1]
        return f"Add the required frontmatter field '{field}' to SKILL.md."

    elif issue_type == 'description_too_long':
        return "Shorten the description to ≤250 characters (hard cap 1024). Front-load the most important trigger words."

    elif issue_type == 'nested_subdirectory':
        path = issue['file']
        return f"Move the contents of '{path}' to a top-level subdirectory at the skill root (e.g., create a new sibling directory like '{path.split('/')[-1]}-scripts/') and update all references."

    elif issue_type == 'circular_dependency':
        nodes = issue.get('cycle_nodes', [])
        if len(nodes) == 2:
            return f"Break the cycle between {nodes[0]['data'].get('title', nodes[0]['id'])} and {nodes[1]['data'].get('title', nodes[1]['id'])} by reordering phases or introducing an intermediate step."
        return f"Break the circular dependency among {len(nodes)} nodes by reordering or restructuring the workflow."

    elif issue_type == 'direct_contradiction':
        return "Remove or reconcile the conflicting rules. Keep only one of the MUST/ALWAYS and NEVER/MUST NOT statements, or reframe them to apply in different contexts."

    elif issue_type == 'smt_unsatisfiable':
        return "Review all MUST/NEVER/ALWAYS rules for logical consistency. The rule set as a whole cannot be simultaneously satisfied."

    return "Review the issue and apply appropriate fix based on context."


def to_markdown(report: dict) -> str:
    """Convert report to human-readable Markdown."""
    lines = []

    # Title
    lines.append(f"# Consistency Check Report: {report['summary']['skill_path']}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(f"- **Total Issues**: {report['summary']['total_issues']}")
    lines.append(f"- **Files Checked**: {report['summary']['files_checked']}")
    lines.append(f"- **Rules Found**: {report['summary']['rules_found']}")
    lines.append(f"- **Sections Found**: {report['summary']['sections_found']}")
    for sev, count in report['summary']['severity_counts'].items():
        if count > 0:
            lines.append(f"- **{sev}**: {count}")
    if 'smt_verification' in report['summary']:
        sv = report['summary']['smt_verification']
        status = "✅ Satisfiable" if sv['satisfiable'] else "❌ Unsatisfiable"
        lines.append(f"- **SMT Verification**: {status} ({'Z3 available' if sv['available'] else 'Z3 not available'})")
    lines.append("")

    # Issues by severity
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        sev_issues = [i for i in report['issues'] if i['severity'] == severity]
        if not sev_issues:
            continue

        lines.append(f"## {severity} Issues ({len(sev_issues)})")
        lines.append("")

        for issue in sev_issues:
            lines.append(f"### {issue['type']}")
            lines.append(f"- **File**: `{issue['file']}`")
            if issue['line'] > 0:
                lines.append(f"- **Line**: {issue['line']}")
            lines.append(f"- **Message**: {issue['message']}")
            lines.append(f"- **Suggested Fix**: {issue['suggested_fix']}")

            if 'reference' in issue:
                ref = issue['reference']
                lines.append(f"- **Reference**: {ref['type']} `{ref['name']}`")

            if 'conflicting_rules' in issue:
                lines.append("- **Conflicting Rules**:")
                for r in issue['conflicting_rules']:
                    lines.append(f"  - {r['file']}:{r['line']} [{r['type']}] {r['text']}")

            if 'cycle_nodes' in issue:
                lines.append("- **Cycle Nodes**:")
                for node in issue['cycle_nodes']:
                    title = node['data'].get('title', node['id'])
                    lines.append(f"  - {node['type']}: {title}")

            lines.append("")

    return '\n'.join(lines)


def to_jsonl(report: dict) -> str:
    """Convert report to JSONL (one issue per line)."""
    lines = []
    # First line: summary
    lines.append(json.dumps({'type': 'summary', 'data': report['summary']}, ensure_ascii=False))
    # Then issues
    for issue in report['issues']:
        lines.append(json.dumps({'type': 'issue', 'data': issue}, ensure_ascii=False))
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <issues_json_file> <skill_directory> [extracted_json_file] [graph_json_file] [smt_json_file]", file=sys.stderr)
        sys.exit(1)

    issues_file = sys.argv[1]
    skill_path = Path(sys.argv[2])
    extracted_data = {}
    graph_data = {}
    smt_result = {}

    if len(sys.argv) > 3:
        with open(sys.argv[3], 'r') as f:
            extracted_data = json.load(f)

    if len(sys.argv) > 4:
        with open(sys.argv[4], 'r') as f:
            graph_data = json.load(f)

    if len(sys.argv) > 5:
        with open(sys.argv[5], 'r') as f:
            smt_result = json.load(f)

    with open(issues_file, 'r') as f:
        issues = json.load(f)

    report = generate_report(issues, skill_path, extracted_data, graph_data, smt_result)

    # Output both formats
    md_path = skill_path / 'consistency-report.md'
    jsonl_path = skill_path / 'consistency-report.jsonl'

    md_path.write_text(to_markdown(report), encoding='utf-8')
    jsonl_path.write_text(to_jsonl(report), encoding='utf-8')

    # Also output to stdout for piping
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    print(f"\n\nMarkdown report written to: {md_path}", file=sys.stderr)
    print(f"JSONL report written to: {jsonl_path}", file=sys.stderr)


if __name__ == '__main__':
    main()