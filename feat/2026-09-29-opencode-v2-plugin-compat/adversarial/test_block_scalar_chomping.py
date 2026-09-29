"""Adversarial probe: YAML block scalar chomping fidelity.

Tests that the loader's extractFrontmatter handles all 6 YAML block scalar
indicators (|, |-, |+, >, >-, >+) with chomping behavior matching
yaml.safe_load exactly.

This is an adversarial probe — it should FAIL if the loader's behavior
deviates from the YAML spec.
"""

import json
import subprocess
import tempfile
from pathlib import Path
import shutil
import yaml


def run_loader_on_skill(skill_yaml: str, plugin_name: str = "investing-toolkit") -> str:
    """Run the loader against a skill with the given YAML frontmatter and return description."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_dir = tmp_path / plugin_name
        opencode_dir = plugin_dir / ".opencode-plugin"
        opencode_dir.mkdir(parents=True)

        # Copy the real loader
        real_loader = Path(__file__).parent.parent.parent.parent / plugin_name / ".opencode-plugin" / "index.js"
        shutil.copy2(real_loader, opencode_dir / "index.js")

        # Create skills dir with test skill
        skills_dir = plugin_dir / "skills"
        skills_dir.mkdir()
        test_skill_dir = skills_dir / "test-skill"
        test_skill_dir.mkdir()
        (test_skill_dir / "SKILL.md").write_text(
            f"---\n"
            f"name: test-skill\n"
            f"{skill_yaml}"
            f"---\n"
            f"Body content\n"
        )

        loader_path = opencode_dir / "index.js"
        test_script = f"""
        const ctx = {{
            registeredSkills: [],
            skill: {{
                transform: (fn) => {{
                    const draft = {{
                        add: (skill) => {{
                            ctx.registeredSkills.push(skill);
                        }}
                    }};
                    fn(draft);
                }}
            }}
        }};

        (async () => {{
            const loader = await import('file://' + {repr(str(loader_path.absolute()))});
            await loader.default.setup(ctx);
            console.log(JSON.stringify({{
                success: true,
                skills: ctx.registeredSkills.map(s => ({{
                    id: s.id,
                    description: s.description
                }}))
            }}));
        }})();
        """

        result = subprocess.run(
            ["node", "-e", test_script],
            cwd=plugin_dir,
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Loader crashed: {result.stderr}"
        output = json.loads(result.stdout.strip())
        assert output["success"] is True

        for skill in output["skills"]:
            if skill["id"].endswith(":test-skill"):
                return skill.get("description", None)

    return None


def test_block_scalar_chomping():
    """Test all 6 block scalar indicators match yaml.safe_load behavior.

    Uses the same format as real SKILL.md files: each content line ends with \n,
    including the last line. This matches the existing test_loader_block_scalar_yaml_semantics.
    """
    import yaml
    import re

    # Each case: (indicator, content_lines, test_name)
    # content_lines is a list of strings, each string is a line of content (without indentation)
    # The format matches real SKILL.md: each line ends with \n in the block scalar
    test_cases = [
        # (indicator, content_lines, test_name)
        ("|", ["line1", "line2"], "literal_clip"),  # No indicator = clip (default)
        ("|-", ["line1", "line2"], "literal_strip"),
        ("|+", ["line1", "line2"], "literal_keep"),
        (">", ["line1", "line2"], "folded_clip"),  # No indicator = clip (default)
        (">-", ["line1", "line2"], "folded_strip"),
        (">+", ["line1", "line2"], "folded_keep"),
        # With trailing blank lines (each blank line is an empty string in the list)
        ("|", ["line1", "line2", "", "", ""], "literal_clip_trailing_blanks"),
        ("|-", ["line1", "line2", "", "", ""], "literal_strip_trailing_blanks"),
        ("|+", ["line1", "line2", "", "", ""], "literal_keep_trailing_blanks"),
        (">", ["line1", "line2", "", "", ""], "folded_clip_trailing_blanks"),
        (">-", ["line1", "line2", "", "", ""], "folded_strip_trailing_blanks"),
        (">+", ["line1", "line2", "", "", ""], "folded_keep_trailing_blanks"),
        # Single line
        ("|", ["single line"], "literal_clip_single"),
        ("|-", ["single line"], "literal_strip_single"),
        ("|+", ["single line"], "literal_keep_single"),
        (">", ["single line"], "folded_clip_single"),
        (">-", ["single line"], "folded_strip_single"),
        (">+", ["single line"], "folded_keep_single"),
        # Interior blank line
        ("|", ["alpha", "", "beta"], "literal_interior_blank"),
        (">", ["alpha", "", "beta"], "folded_interior_blank"),
        # Indented continuation
        ("|", ["alpha", "  indented", "beta"], "literal_indented_continuation"),
        (">", ["alpha", "  indented", "beta"], "folded_indented_continuation"),
    ]

    failures = []

    for indicator, content_lines, test_name in test_cases:
        # Build the block string as in real SKILL.md: each content line indented by 2 spaces, each followed by \n
        indented_lines = [f"  {line}" for line in content_lines]
        # Join with \n and add final \n (each line ends with newline in SKILL.md)
        block_content = "\n".join(indented_lines) + "\n"
        block = f"{indicator}\n{block_content}"

        # Build the full SKILL.md content as in the existing test
        skill_content = f"---\nname: test-skill\ndescription: {block}---\nBody content\n"

        # Extract frontmatter by splitting on "---" (same as existing test)
        parts = skill_content.split("---\n", 2)
        if len(parts) < 3:
            failures.append(f"{test_name}: Failed to split frontmatter")
            continue
        frontmatter = parts[1]  # This is "name: test-skill\ndescription: {block}"

        # Get expected from yaml.safe_load using the same method as fidelity test
        try:
            data = yaml.safe_load(frontmatter)
            expected = data.get("description") if isinstance(data, dict) else None
        except Exception as e:
            failures.append(f"{test_name}: yaml.safe_load failed: {e}")
            continue

        # Get actual from loader - use the yaml_snippet format the loader expects
        # The loader receives frontmatter with trailing newline after last content line
        yaml_snippet = f"description: {indicator}\n{block_content}"
        try:
            actual = run_loader_on_skill(yaml_snippet)
        except Exception as e:
            failures.append(f"{test_name}: loader crashed: {e}")
            continue

        # Normalize for comparison (both should be strings or None)
        if expected is None and actual is None:
            continue
        if expected is None:
            failures.append(f"{test_name}: expected None, got {repr(actual)}")
            continue
        if actual is None:
            failures.append(f"{test_name}: expected {repr(expected)}, got None")
            continue

        if str(expected) != str(actual):
            failures.append(
                f"{test_name}: MISMATCH\n"
                f"  Indicator: {indicator!r}\n"
                f"  Content lines: {content_lines}\n"
                f"  Expected (yaml.safe_load): {repr(expected)}\n"
                f"  Actual (loader):           {repr(actual)}"
            )

    if failures:
        raise AssertionError("Block scalar chomping mismatches:\n" + "\n".join(failures))

    print("All block scalar chomping tests PASSED")


if __name__ == "__main__":
    test_block_scalar_chomping()