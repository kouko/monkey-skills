#!/usr/bin/env python3
"""
Extracts logical rules from skill text files.

Parses SKILL.md and bundled resources to extract:
- Frontmatter (name, description, etc.)
- Section headers and their content
- Rule-like statements (MUST, NEVER, ALWAYS, SHOULD, prohibited, required)
- Code blocks and their context
- Agent definitions and their prompts
- Script definitions and invocations
- Reference files and their usage

Output: JSON structure with extracted rules and metadata.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}
    end = content.find('---', 3)
    if end == -1:
        return {}
    fm_text = content[3:end].strip()
    # Simple YAML parser for our needs (no nested structures)
    result = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"\'')
            result[key] = val
    return result


def extract_rules_from_text(text: str, file_path: str) -> list[dict]:
    """Extract rule-like statements from text, excluding code blocks."""
    rules = []

    # First, remove code blocks to avoid extracting rules from examples
    # Replace code blocks with placeholder lines to preserve line numbers
    lines = text.split('\n')
    in_code_block = False
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            filtered_lines.append(' ' * len(line))  # Preserve line number, blank content
        elif in_code_block:
            filtered_lines.append(' ' * len(line))  # Preserve line number, blank content
        else:
            filtered_lines.append(line)

    filtered_text = '\n'.join(filtered_lines)

    # Patterns for rule-like statements
    patterns = [
        # **MUST**:, **NEVER**:, **ALWAYS**:, **SHOULD**: (markdown bold)
        (r'(?i)(?:^|\n)\s*[>*]?\s*\*\*(?:MUST|NEVER|ALWAYS|SHOULD)\*\*\s*[:\-]?\s*(.+)', 'explicit'),
        # MUST:, NEVER:, ALWAYS:, SHOULD: (plain)
        (r'(?i)(?:^|\n)\s*[>*]?\s*(?:MUST|NEVER|ALWAYS|SHOULD)\s*[:\-]?\s*(.+)', 'explicit'),
        # prohibited, required, forbidden
        (r'(?i)(?:^|\n)\s*[>*]?\s*(?:prohibited|required|forbidden|must not|must)\s*[:\-]?\s*(.+)', 'implicit'),
        # NEVER do X, ALWAYS do Y
        (r'(?i)(?:^|\n)\s*[>*]?\s*NEVER\s+(?:do\s+)?(.+)', 'never'),
        (r'(?i)(?:^|\n)\s*[>*]?\s*ALWAYS\s+(?:do\s+)?(.+)', 'always'),
        # MUST NOT, SHOULD NOT
        (r'(?i)(?:^|\n)\s*[>*]?\s*MUST\s+NOT\s+(.+)', 'must_not'),
        (r'(?i)(?:^|\n)\s*[>*]?\s*SHOULD\s+NOT\s+(.+)', 'should_not'),
    ]

    filtered_lines_list = filtered_text.split('\n')
    for i, line in enumerate(filtered_lines_list):
        # Skip lines that are just whitespace (were code blocks)
        if not line.strip():
            continue
        for pattern, rule_type in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                rule_text = match.group(1).strip()
                if rule_text:
                    rules.append({
                        'file': file_path,
                        'line': i + 1,
                        'type': rule_type,
                        'text': rule_text,
                        'context': lines[max(0, i-2):min(len(lines), i+3)]
                    })

    return rules


def extract_section_structure(content: str, file_path: str) -> list[dict]:
    """Extract section headers and their content boundaries."""
    sections = []
    lines = content.split('\n')
    current_section = None

    for i, line in enumerate(lines):
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            if current_section:
                current_section['end_line'] = i
            current_section = {
                'file': file_path,
                'level': level,
                'title': title,
                'start_line': i + 1,
                'end_line': len(lines)
            }
            sections.append(current_section)

    return sections


def extract_code_blocks(content: str, file_path: str) -> list[dict]:
    """Extract code blocks with their language and context."""
    blocks = []
    # Match fenced code blocks
    pattern = r'```(\w+)?\n(.*?)\n```'
    for match in re.finditer(pattern, content, re.DOTALL):
        lang = match.group(1) or 'text'
        code = match.group(2)
        # Find line number
        line_no = content[:match.start()].count('\n') + 1
        blocks.append({
            'file': file_path,
            'language': lang,
            'start_line': line_no,
            'code': code.strip()
        })
    return blocks


def extract_agent_references(content: str, file_path: str) -> list[dict]:
    """Extract references to agents, scripts, and files."""
    refs = []

    # Agent references: "Agent", "subagent", "loom-code:implementer", etc.
    # Handle formats like: "subagent: analysis-team", "Agent: validation-team"
    agent_pattern = r'(?:[Aa]gent|subagent)\s*[:]\s*([a-z0-9\-_]+)'
    for match in re.finditer(agent_pattern, content):
        refs.append({
            'file': file_path,
            'type': 'agent',
            'name': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })

    # Script references: "scripts/xxx.py", "python scripts/xxx.py"
    script_pattern = r'(?:scripts?/|python\s+scripts?/)([a-z0-9_\-]+\.py)'
    for match in re.finditer(script_pattern, content):
        refs.append({
            'file': file_path,
            'type': 'script',
            'name': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })

    # Reference file references: "references/xxx.md", "[`xxx.md`](references/xxx.md)"
    ref_pattern = r'references?/([a-z0-9_\-]+\.md)'
    for match in re.finditer(ref_pattern, content):
        refs.append({
            'file': file_path,
            'type': 'reference',
            'name': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })

    # Phase/step references: "Phase A", "Step 1", "§Workflow"
    phase_pattern = r'(?:Phase|Step|§)\s*([A-Za-z0-9]+)'
    for match in re.finditer(phase_pattern, content):
        refs.append({
            'file': file_path,
            'type': 'phase',
            'name': match.group(1),
            'line': content[:match.start()].count('\n') + 1
        })

    return refs


def process_skill_directory(skill_path: Path) -> dict:
    """Process a skill directory and extract all rules and structure."""
    result = {
        'skill_path': str(skill_path),
        'frontmatter': {},
        'rules': [],
        'sections': [],
        'code_blocks': [],
        'references': [],
        'files': []
    }

    # Find all text files in the skill directory
    text_files = list(skill_path.rglob('*.md')) + list(skill_path.rglob('*.txt')) + list(skill_path.rglob('*.py'))

    for file_path in text_files:
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
            continue

        rel_path = file_path.relative_to(skill_path)
        result['files'].append(str(rel_path))

        # Extract frontmatter from SKILL.md
        if file_path.name == 'SKILL.md':
            result['frontmatter'] = parse_frontmatter(content)

        # Extract rules
        result['rules'].extend(extract_rules_from_text(content, str(rel_path)))

        # Extract sections
        result['sections'].extend(extract_section_structure(content, str(rel_path)))

        # Extract code blocks
        result['code_blocks'].extend(extract_code_blocks(content, str(rel_path)))

        # Extract references
        result['references'].extend(extract_agent_references(content, str(rel_path)))

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_rules.py <skill_directory>", file=sys.stderr)
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    if not skill_path.exists():
        print(f"Error: Path {skill_path} does not exist", file=sys.stderr)
        sys.exit(1)

    if skill_path.is_file():
        # Single file mode
        content = skill_path.read_text(encoding='utf-8')
        result = {
            'skill_path': str(skill_path.parent),
            'frontmatter': parse_frontmatter(content),
            'rules': extract_rules_from_text(content, str(skill_path)),
            'sections': extract_section_structure(content, str(skill_path)),
            'code_blocks': extract_code_blocks(content, str(skill_path)),
            'references': extract_agent_references(content, str(skill_path)),
            'files': [str(skill_path)]
        }
    else:
        result = process_skill_directory(skill_path)

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()