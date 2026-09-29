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


def run_loader_on_skill(skill_yaml: str, plugin_name: str = "investing-toolkit") -> str:
    """Run the loader against a skill with the given YAML frontmatter and return description."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_dir = tmp_path / plugin_name
        opencode_dir = plugin_dir / ".opencode-plugin"
        opencode_dir.mkdir(parents=True)

        # Copy the real loader
        import shutil
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
            f"{skill_yaml}\n"
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
    """Test all 6 block scalar indicators match yaml.safe_load behavior."""
    import yaml

    # Each case: (yaml_indicator, expected_behavior_description)
    # We compare loader output to yaml.safe_load for exact match
    test_cases = [
        # (yaml_snippet_for_description, test_name)
        ("description: |\n  line1\n  line2\n", "literal_clip"),
        ("description: |-\n  line1\n  line2\n", "literal_strip"),
        ("description: |+\n  line1\n  line2\n", "literal_keep"),
        ("description: >\n  line1\n  line2\n", "folded_clip"),
        ("description: >-\n  line1\n  line2\n", "folded_strip"),
        ("description: >+\n  line1\n  line2\n", "folded_keep"),
        # With trailing blank lines
        ("description: |\n  line1\n  line2\n\n\n", "literal_clip_trailing_blanks"),
        ("description: |-\n  line1\n  line2\n\n\n", "literal_strip_trailing_blanks"),
        ("description: |+\n  line1\n  line2\n\n\n", "literal_keep_trailing_blanks"),
        ("description: >\n  line1\n  line2\n\n\n", "folded_clip_trailing_blanks"),
        ("description: >-\n  line1\n  line2\n\n\n", "folded_strip_trailing_blanks"),
        ("description: >+\n  line1\n  line2\n\n\n", "folded_keep_trailing_blanks"),
        # Single line
        ("description: |\n  single line\n", "literal_clip_single"),
        ("description: |-\n  single line\n", "literal_strip_single"),
        ("description: |+\n  single line\n", "literal_keep_single"),
        ("description: >\n  single line\n", "folded_clip_single"),
        ("description: >-\n  single line\n", "folded_strip_single"),
        ("description: >+\n  single line\n", "folded_keep_single"),
    ]

    failures = []

    for yaml_snippet, test_name in test_cases:
        # Get expected from yaml.safe_load
        frontmatter = f"name: test\n{yaml_snippet}"
        try:
            data = yaml.safe_load(frontmatter)
            expected = data.get("description") if isinstance(data, dict) else None
        except Exception as e:
            failures.append(f"{test_name}: yaml.safe_load failed: {e}")
            continue

        # Get actual from loader
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
                f"  Expected (yaml.safe_load): {repr(expected)}\n"
                f"  Actual (loader):           {repr(actual)}"
            )

    if failures:
        raise AssertionError("Block scalar chomping mismatches:\n" + "\n".join(failures))

    print("All block scalar chomping tests PASSED")


if __name__ == "__main__":
    test_block_scalar_chomping()