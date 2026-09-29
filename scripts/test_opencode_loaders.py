"""Tests for OpenCode v2 plugin loaders"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent


def get_all_plugins():
    """Return list of all plugin names that should have loaders."""
    return [
        "ascii-graph-toolkit",
        "briefing-toolkit",
        "collab-toolkit",
        "copywriting-toolkit",
        "dbt-wiki",
        "deconstruct-toolkit",
        "domain-teams",
        "four-dx-coach",
        "gws-toolkit",
        "investing-toolkit",
        "legal-toolkit",
        "obsidian",
        "philosophers-toolkit",
        "repo-wiki",
        "research-toolkit",
        "salesforce-toolkit",
        "skill-dev-toolkit",
        "systems-thinking-toolkit",
        "think-orbit",
        "translation-toolkit",
        "tsundoku",
    ]


@pytest.fixture(params=get_all_plugins())
def plugin_name(request):
    return request.param


def test_loader_exists(plugin_name):
    """Test that loader files exist for a plugin"""
    plugin_dir = REPO_ROOT / plugin_name
    loader_path = plugin_dir / ".opencode-plugin" / "index.js"
    package_path = plugin_dir / "package.json"

    assert loader_path.exists(), f"Loader missing for {plugin_name}: {loader_path}"
    assert package_path.exists(), f"Package.json missing for {plugin_name}: {package_path}"

    # Validate package.json
    with open(package_path) as f:
        pkg = json.load(f)
    assert pkg["name"] == f"monkey-skills-{plugin_name}"
    assert pkg["version"] == "0.0.1"
    assert pkg["type"] == "module"
    assert pkg["exports"]["."] == "./.opencode-plugin/index.js"


def test_loader_runs_without_error(plugin_name):
    """Test that loader can be executed without throwing"""
    plugin_dir = REPO_ROOT / plugin_name
    loader_path = plugin_dir / ".opencode-plugin" / "index.js"

    # Create a minimal fake context that captures calls
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

    // Import and run the loader
    (async () => {{
        const loader = await import('file://' + {repr(str(loader_path.absolute()))});
        await loader.default.setup(ctx);

        console.log(JSON.stringify({{
            success: true,
            skillCount: ctx.registeredSkills.length,
            skills: ctx.registeredSkills.map(s => ({{
                id: s.id,
                name: s.name,
                hasDescription: !!s.description,
                path: s.path,
                contentLength: s.content.length
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

    # Should not crash
    assert result.returncode == 0, f"Loader crashed for {plugin_name}: {result.stderr}"

    # Should produce valid JSON output
    try:
        output = json.loads(result.stdout.strip())
        assert output["success"] is True
        # Should have registered some skills (varies by plugin)
        assert output["skillCount"] >= 0
    except (json.JSONDecodeError, KeyError) as e:
        pytest.fail(f"Invalid output from loader for {plugin_name}: {e}\nStdout: {result.stdout}\nStderr: {result.stderr}")


def test_loader_handles_missing_skills_dir(plugin_name):
    """Test that loader handles missing skills directory gracefully"""
    plugin_dir = REPO_ROOT / plugin_name
    loader_path = plugin_dir / ".opencode-plugin" / "index.js"
    skills_dir = plugin_dir / "skills"

    # Temporarily rename skills directory
    if skills_dir.exists():
        skills_dir.rename(skills_dir.with_suffix(".skills.bak"))

    try:
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

        // Import and run the loader
        (async () => {{
            const loader = await import('file://' + {repr(str(loader_path.absolute()))});
            await loader.default.setup(ctx);

            console.log(JSON.stringify({{
                success: true,
                skillCount: ctx.registeredSkills.length
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

        assert result.returncode == 0, f"Loader failed on missing skills dir: {result.stderr}"
        output = json.loads(result.stdout.strip())
        assert output["success"] is True
        assert output["skillCount"] == 0
    finally:
        # Restore skills directory
        if skills_dir.with_suffix(".skills.bak").exists():
            skills_dir.with_suffix(".skills.bak").rename(skills_dir)


def test_loader_skips_hidden_directories(plugin_name):
    """Test that loader skips hidden directories (starting with .)"""
    plugin_dir = REPO_ROOT / plugin_name
    loader_path = plugin_dir / ".opencode-plugin" / "index.js"
    skills_dir = plugin_dir / "skills"

    if not skills_dir.exists():
        pytest.skip(f"No skills directory for {plugin_name}")

    # Create a hidden directory
    hidden_dir = skills_dir / ".hidden-skill"
    hidden_dir.mkdir()
    (hidden_dir / "SKILL.md").write_text("---\nname: hidden-skill\n---\nHidden content")

    try:
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

        // Import and run the loader
        (async () => {{
            const loader = await import('file://' + {repr(str(loader_path.absolute()))});
            await loader.default.setup(ctx);

            console.log(JSON.stringify({{
                success: true,
                skillIds: ctx.registeredSkills.map(s => s.id)
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

        assert result.returncode == 0, f"Loader failed: {result.stderr}"
        output = json.loads(result.stdout.strip())
        assert output["success"] is True

        # None of the skills should be from hidden directory
        skill_ids = output["skillIds"]
        hidden_skills = [sid for sid in skill_ids if ".hidden-skill" in sid]
        assert len(hidden_skills) == 0, f"Hidden skill was not skipped: {hidden_skills}"
    finally:
        # Clean up
        if hidden_dir.exists():
            import shutil
            shutil.rmtree(hidden_dir)


def test_loader_handles_block_scalar_description(plugin_name):
    """Test that loader correctly extracts YAML block scalar (| or >) descriptions"""
    plugin_dir = REPO_ROOT / plugin_name
    loader_path = plugin_dir / ".opencode-plugin" / "index.js"
    skills_dir = plugin_dir / "skills"

    if not skills_dir.exists():
        pytest.skip(f"No skills directory for {plugin_name}")

    # Create a temporary skill with block-scalar description
    test_skill_dir = skills_dir / "test-block-scalar-skill"
    test_skill_dir.mkdir()
    # Use a block scalar with multiple lines
    (test_skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: test-block-scalar-skill\n"
        "description: |\n"
        "  This is a multi-line\n"
        "  YAML block scalar\n"
        "  description\n"
        "---\n"
        "Body content here.\n"
    )

    try:
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

        // Import and run the loader
        (async () => {{
            const loader = await import('file://' + {repr(str(loader_path.absolute()))});
            await loader.default.setup(ctx);

            console.log(JSON.stringify({{
                success: true,
                skills: ctx.registeredSkills.map(s => ({{
                    id: s.id,
                    name: s.name,
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

        assert result.returncode == 0, f"Loader failed: {result.stderr}"
        output = json.loads(result.stdout.strip())
        assert output["success"] is True

        # Find our test skill
        test_skill = None
        for s in output["skills"]:
            if s["id"].endswith(":test-block-scalar-skill"):
                test_skill = s
                break

        assert test_skill is not None, "Test skill was not registered"
        assert test_skill["description"] is not None, "Block-scalar description was omitted"
        assert "multi-line" in test_skill["description"], f"Description content not captured: {test_skill['description']}"
        assert "block scalar" in test_skill["description"], f"Description content not captured: {test_skill['description']}"
    finally:
        # Clean up
        if test_skill_dir.exists():
            import shutil
            shutil.rmtree(test_skill_dir)


def test_loaders_match_template():
    """Test that all loaders match the template (consistency test)"""
    # Regenerate all loaders from template in memory
    from scripts.generate_opencode_loaders import render_template, PLUGINS

    mismatches = []

    for plugin in PLUGINS:
        expected = render_template(plugin)
        plugin_dir = REPO_ROOT / plugin
        actual_path = plugin_dir / ".opencode-plugin" / "index.js"

        if not actual_path.exists():
            mismatches.append(f"{plugin}: Loader file missing")
            continue

        actual = actual_path.read_text()
        if actual != expected:
            mismatches.append(f"{plugin}: Loader does not match template")

    assert not mismatches, f"Loader template mismatches: {', '.join(mismatches)}"


def test_loader_fidelity_against_yaml():
    """Test that each loader's description extraction matches yaml.safe_load"""
    # Import yaml for comparison
    import yaml

    # Test each plugin's loader against real SKILL.md files
    mismatches = []

    for plugin_name in get_all_plugins():
        plugin_dir = REPO_ROOT / plugin_name
        skills_dir = plugin_dir / "skills"

        if not skills_dir.exists():
            continue

        # Get all skill directories
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            # Extract frontmatter using yaml.safe_load
            try:
                content = skill_file.read_text(encoding='utf-8')
                # Simple frontmatter extraction (between --- lines)
                if content.startswith('---\n'):
                    parts = content.split('---\n', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        skill_content = parts[2]
                        data = yaml.safe_load(frontmatter)
                        expected_description = data.get('description') if isinstance(data, dict) else None
                    else:
                        expected_description = None
                else:
                    expected_description = None
            except Exception:
                expected_description = None

            # Run the loader to get actual description
            loader_path = plugin_dir / ".opencode-plugin" / "index.js"
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

            // Import and run the loader
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

            if result.returncode != 0:
                mismatches.append(f"{plugin_name}:{skill_dir.name}: Loader crashed: {result.stderr}")
                continue

            try:
                output = json.loads(result.stdout.strip())
                if not output.get("success", False):
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Loader reported failure")
                    continue

                # Find our skill
                actual_description = None
                for skill in output.get("skills", []):
                    if skill["id"].endswith(f":{skill_dir.name}"):
                        actual_description = skill.get("description")
                        break

                if actual_description is None:
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Skill not found in loader output")
                    continue

                # Compare descriptions (normalize both)
                if expected_description is None and actual_description is None:
                    continue  # Both None, OK
                elif expected_description is None:
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Expected no description, got: {repr(actual_description)}")
                elif actual_description is None:
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Expected {repr(expected_description)}, got no description")
                elif str(expected_description).strip() != str(actual_description).strip():
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Description mismatch\\nExpected: {repr(expected_description)}\\nActual: {repr(actual_description)}")

            except (json.JSONDecodeError, KeyError) as e:
                mismatches.append(f"{plugin_name}:{skill_dir.name}: Invalid loader output: {e}")

    assert not mismatches, f"Loader fidelity mismatches: {'; '.join(mismatches[:5])}{'...' if len(mismatches) > 5 else ''}"


def test_loader_handles_missing_skills_dir_silent():
    """Test that loader doesn't log misleading 'Loader failed' when skills dir missing"""
    plugin_name = "investing-toolkit"  # Test with one plugin
    plugin_dir = REPO_ROOT / plugin_name
    loader_path = plugin_dir / ".opencode-plugin" / "index.js"
    skills_dir = plugin_dir / "skills"

    # Temporarily rename skills directory
    if skills_dir.exists():
        skills_dir.rename(skills_dir.with_suffix(".skills.bak"))

    try:
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

        // Import and run the loader
        (async () => {{
            const loader = await import('file://' + {repr(str(loader_path.absolute()))});
            await loader.default.setup(ctx);

            console.log(JSON.stringify({{
                success: true,
                skillCount: ctx.registeredSkills.length
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

        assert result.returncode == 0, f"Loader failed: {result.stderr}"
        output = json.loads(result.stdout.strip())
        assert output["success"] is True
        assert output["skillCount"] == 0

        # Should not have logged "Loader failed" to stderr
        assert "Loader failed" not in result.stderr, f"Loader incorrectly logged failure when skills dir missing: {result.stderr}"
    finally:
        # Restore skills directory
        if skills_dir.with_suffix(".skills.bak").exists():
            skills_dir.with_suffix(".skills.bak").rename(skills_dir)


if __name__ == "__main__":
    # Simple test runner for manual verification
    pytest.main([__file__, "-v"])