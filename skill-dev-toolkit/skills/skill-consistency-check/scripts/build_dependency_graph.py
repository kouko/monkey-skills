#!/usr/bin/env python3
"""
Builds a dependency graph from extracted skill data.

Nodes represent:
- Rules (MUST, NEVER, ALWAYS statements)
- Phases (from workflow sections)
- Agents (subagent definitions)
- Scripts (in scripts/ directory)
- Files (referenced files)

Edges represent:
- Dependency (A must happen before B)
- before B)
- Invocation (Agent A invokes Script B)
- Reference (Phase A uses File B)
- Contradiction potential (Rule A conflicts with Rule B)
"""

import json
import sys
from collections import defaultdict
from typing import Any


class DependencyGraph:
    def __init__(self):
        self.nodes = {}  # id -> {type, data}
        self.edges = []  # [(from_id, to_id, type, data)]
        self.node_counter = 0

    def add_node(self, node_type: str, data: dict) -> str:
        """Add a node and return its ID."""
        node_id = f"{node_type}_{self.node_counter}"
        self.node_counter += 1
        self.nodes[node_id] = {
            'type': node_type,
            'data': data
        }
        return node_id

    def add_edge(self, from_id: str, to_id: str, edge_type: str, data: dict = None):
        """Add an edge between two nodes."""
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError(f"Invalid node ID: {from_id} or {to_id}")
        self.edges.append({
            'from': from_id,
            'to': to_id,
            'type': edge_type,
            'data': data or {}
        })

    def get_nodes_by_type(self, node_type: str) -> list[str]:
        """Get all node IDs of a given type."""
        return [nid for nid, node in self.nodes.items() if node['type'] == node_type]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'nodes': self.nodes,
            'edges': self.edges
        }


def build_graph(extracted_data: dict) -> DependencyGraph:
    """Build dependency graph from extracted skill data."""
    graph = DependencyGraph()

    # Add file nodes
    for file_path in extracted_data['files']:
        node_id = graph.add_node('file', {
            'path': file_path,
            'is_skill_main': (file_path == 'SKILL.md')
        })

    # Add rule nodes from extracted rules
    for rule in extracted_data['rules']:
        node_id = graph.add_node('rule', {
            'file': rule['file'],
            'line': rule['line'],
            'type': rule['type'],
            'text': rule['text']
        })
        # Link to file
        file_nodes = [nid for nid, node in graph.nodes.items()
                     if node['type'] == 'file' and node['data']['path'] == rule['file']]
        if file_nodes:
            graph.add_edge(node_id, file_nodes[0], 'defined_in')

    # Add section nodes
    for section in extracted_data['sections']:
        node_id = graph.add_node('section', {
            'file': section['file'],
            'level': section['level'],
            'title': section['title'],
            'start_line': section['start_line'],
            'end_line': section['end_line']
        })
        # Link to file
        file_nodes = [nid for nid, node in graph.nodes.items()
                     if node['type'] == 'file' and node['data']['path'] == section['file']]
        if file_nodes:
            graph.add_edge(node_id, file_nodes[0], 'defined_in')

    # Add code block nodes
    for block in extracted_data['code_blocks']:
        node_id = graph.add_node('code_block', {
            'file': block['file'],
            'language': block['language'],
            'start_line': block['start_line']
        })
        # Link to file
        file_nodes = [nid for nid, node in graph.nodes.items()
                     if node['type'] == 'file' and node['data']['path'] == block['file']]
        if file_nodes:
            graph.add_edge(node_id, file_nodes[0], 'defined_in')

    # Add reference nodes and edges
    for ref in extracted_data['references']:
        # Determine if the referenced item exists
        exists = False
        target_node_id = None

        if ref['type'] == 'script':
            # Check if script file exists
            script_path = f"scripts/{ref['name']}"
            file_nodes = [nid for nid, node in graph.nodes.items()
                         if node['type'] == 'file' and node['data']['path'] == script_path]
            if file_nodes:
                exists = True
                target_node_id = file_nodes[0]
        elif ref['type'] == 'reference':
            # Check if reference file exists
            ref_path = f"references/{ref['name']}"
            file_nodes = [nid for nid, node in graph.nodes.items()
                         if node['type'] == 'file' and node['data']['path'] == ref_path]
            if file_nodes:
                exists = True
                target_node_id = file_nodes[0]
        elif ref['type'] == 'agent':
            # Agents are defined in agents/ directory or inline
            # For now, assume they might exist
            pass
        elif ref['type'] == 'phase':
            # Phases are defined in sections
            section_nodes = graph.get_nodes_by_type('section')
            for sec_id in section_nodes:
                sec_data = graph.nodes[sec_id]['data']
                if sec_data['title'].lower() == ref['name'].lower():
                    target_node_id = sec_id
                    exists = True
                    break

        # Add reference node
        ref_node_id = graph.add_node('reference', {
            'file': ref['file'],
            'type': ref['type'],
            'name': ref['name'],
            'line': ref['line'],
            'exists': exists
        })

        # Link to source file
        file_nodes = [nid for nid, node in graph.nodes.items()
                     if node['type'] == 'file' and node['data']['path'] == ref['file']]
        if file_nodes:
            graph.add_edge(ref_node_id, file_nodes[0], 'referenced_in')

        # If target exists, link reference to target
        if target_node_id:
            graph.add_edge(ref_node_id, target_node_id, 'references')

    # Add explicit dependencies from rule text analysis
    # This would be enhanced with NLP to extract "before", "after", "depends on" etc.
    # For now, we'll look for explicit sequencing keywords in rule text
    for rule in extracted_data['rules']:
        rule_nodes = [nid for nid, node in graph.nodes.items()
                     if node['type'] == 'rule' and
                     node['data']['file'] == rule['file'] and
                     node['data']['line'] == rule['line']]
        if not rule_nodes:
            continue
        rule_node_id = rule_nodes[0]

        text = rule['text'].lower()
        # Look for sequencing indicators
        if 'before' in text or 'prior to' in text or 'must precede' in text:
            # This rule indicates it must happen before something
            # We would need to extract what it must happen before
            # For now, we'll note this as a potential dependency
            pass
        elif 'after' in text or 'following' in text or 'must follow' in text:
            # This rule indicates it must happen after something
            pass

    return graph


def main():
    if len(sys.argv) < 2:
        print("Usage: build_dependency_graph.py <extracted_json_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(data)
    json.dump(graph.to_dict(), sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()