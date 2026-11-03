#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import os
import re
import yaml
from pathlib import Path


def description_violation(description: str, skill_content: str) -> str | None:
    """Check mechanical eligibility; contextual justification still needs review."""
    if not description.strip() or "<" in description or ">" in description:
        return "description must be nonempty text without XML/angle brackets"
    if len(description) > 1024:
        return "description exceeds the platform ceiling of 1024 characters"
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", skill_content, re.DOTALL)
    if not match:
        return "description context has malformed YAML frontmatter"
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return "description context has malformed YAML frontmatter"
    if not isinstance(metadata, dict) or not isinstance(metadata.get("description"), str):
        return "description context needs a YAML description string"
    # Comments do not count toward rendered length. Only the comment block
    # directly above the parsed description field can justify a long value.
    lines = match.group(1).splitlines()
    comments = []
    for index, line in enumerate(lines):
        if line.startswith("description:"):
            for previous in reversed(lines[:index]):
                if not previous.startswith("#"):
                    break
                comments.insert(0, previous[1:].strip())
            break
    justification = " ".join(comments)
    firing_note = re.search(r"\bFiring evidence:\s*(\S.*)", justification, re.IGNORECASE)
    # Domain nouns in a KEEP explanation do not declare the skill's role.
    role_declaration = any(re.match(
        r"^(?:(?:skill\s+)?role:\s*(?:router|CONDITIONAL)\b|"
        r"(?:router|CONDITIONAL)(?:\s+skill\b|\s*[:.;]|\s*$))",
        comment, re.IGNORECASE,
    ) for comment in comments)
    declared_exception = firing_note or role_declaration or re.search(r"Firing evidence:", justification, re.IGNORECASE)
    if declared_exception and len(description) > 250:
        if not firing_note:
            return "description router/CONDITIONAL exception needs a firing-evidence note"
        if len(description) > 500:
            return "description exceeds the admitted router/CONDITIONAL bound of 500 characters"
    if len(description) > 250 and not justification:
        return "description over 250 characters needs a colocated YAML justification"
    return None


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    violation = description_violation(description, content)
    if violation:
        return False, violation

    # Validate compatibility field if present (optional)
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
