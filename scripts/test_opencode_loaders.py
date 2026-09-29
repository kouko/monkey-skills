"""Tests for OpenCode v2 plugin loaders"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent


def _setup_test_plugin(tmp_path: Path, plugin_name: str) -> Path:
    """Create a minimal isolated plugin structure in tmp_path for testing.

    Copies the loader file from the real plugin to the temp location.
    Returns the path to the temp plugin directory.
    """
    real_plugin_dir = REPO_ROOT / plugin_name
    real_loader = real_plugin_dir / ".opencode-plugin" / "index.js"

    # Create temp plugin dir structure
    temp_plugin_dir = tmp_path / plugin_name
    temp_opencode_dir = temp_plugin_dir / ".opencode-plugin"
    temp_opencode_dir.mkdir(parents=True)

    # Copy loader file
    shutil.copy2(real_loader, temp_opencode_dir / "index.js")

    return temp_plugin_dir


def _run_loader(temp_plugin_dir: Path, plugin_name: str, extra_script: str = "") -> dict:
    """Run the loader in a temp plugin directory and return parsed JSON output."""
    loader_path = temp_plugin_dir / ".opencode-plugin" / "index.js"

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
        {extra_script}
        console.log(JSON.stringify({{
            success: true,
            skillCount: ctx.registeredSkills.length,
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
        cwd=temp_plugin_dir,
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0, f"Loader failed: {result.stderr}"
    return json.loads(result.stdout.strip())


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


def test_loader_handles_missing_skills_dir(tmp_path, plugin_name):
    """Test that loader handles missing skills directory gracefully"""
    # Create isolated plugin structure with no skills directory
    temp_plugin_dir = _setup_test_plugin(tmp_path, plugin_name)
    # Don't create skills directory - leave it missing

    output = _run_loader(temp_plugin_dir, plugin_name)
    assert output["success"] is True
    assert output["skillCount"] == 0


def test_loader_skips_hidden_directories(tmp_path, plugin_name):
    """Test that loader skips hidden directories (starting with .)"""
    temp_plugin_dir = _setup_test_plugin(tmp_path, plugin_name)

    # Create skills directory with hidden subdirectory
    skills_dir = temp_plugin_dir / "skills"
    skills_dir.mkdir()
    hidden_dir = skills_dir / ".hidden-skill"
    hidden_dir.mkdir()
    (hidden_dir / "SKILL.md").write_text("---\nname: hidden-skill\n---\nHidden content")

    output = _run_loader(temp_plugin_dir, plugin_name)
    assert output["success"] is True

    # None of the skills should be from hidden directory
    skill_ids = [s["id"] for s in output["skills"]]
    hidden_skills = [sid for sid in skill_ids if ".hidden-skill" in sid]
    assert len(hidden_skills) == 0, f"Hidden skill was not skipped: {hidden_skills}"


def test_loader_handles_block_scalar_description(tmp_path, plugin_name):
    """Test that loader correctly extracts YAML block scalar (| or >) descriptions"""
    temp_plugin_dir = _setup_test_plugin(tmp_path, plugin_name)

    # Create skills directory with test skill using block scalar
    skills_dir = temp_plugin_dir / "skills"
    skills_dir.mkdir()
    test_skill_dir = skills_dir / "test-block-scalar-skill"
    test_skill_dir.mkdir()
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

    output = _run_loader(temp_plugin_dir, plugin_name)
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


# (frontmatter block after "description:", expected description per yaml.safe_load of the same block)
BLOCK_SCALAR_CASES = [
    ("|-\n  alpha\n", "alpha"),                          # literal, strip chomp
    ("|\n  alpha\n", "alpha\n"),                         # literal, clip (default)
    ("|+\n  alpha\n", "alpha\n"),                        # literal, keep (no extra blank lines)
    ("|+\n  alpha\n\n", "alpha\n\n"),                    # literal, keep with one blank line
    (">-\n  alpha\n  beta\n", "alpha beta"),             # folded, strip
    (">\n  alpha\n  beta\n", "alpha beta\n"),            # folded, clip
    (">+\n  alpha\n  beta\n", "alpha beta\n"),           # folded, keep (no extra blank lines)
    ("|\n  alpha\n\n  beta\n", "alpha\n\nbeta\n"),       # interior blank line must not terminate
    (">\n  alpha\n    indented\n  beta\n", "alpha\n  indented\nbeta\n"),  # more-indented keeps indent+newlines
]


@pytest.mark.parametrize("block,expected", BLOCK_SCALAR_CASES)
def test_loader_block_scalar_yaml_semantics(tmp_path, plugin_name, block, expected):
    """Loader block-scalar extraction must match YAML spec byte-for-byte."""
    import yaml as yaml_mod

    temp_plugin_dir = _setup_test_plugin(tmp_path, plugin_name)
    skills_dir = temp_plugin_dir / "skills"
    skills_dir.mkdir()
    test_skill_dir = skills_dir / "case-skill"
    test_skill_dir.mkdir()
    raw = f"---\nname: case-skill\ndescription: {block}---\nBody.\n"

    # Ground truth from a real YAML parser (same extraction as fidelity test)
    frontmatter = raw.split("---\n", 2)[1]
    expected_yaml = yaml_mod.safe_load(frontmatter)["description"]
    assert expected_yaml == expected, f"Test expectation stale for {block!r}: yaml gives {expected_yaml!r}"

    (test_skill_dir / "SKILL.md").write_text(raw)
    output = _run_loader(temp_plugin_dir, plugin_name)
    test_skill = next(s for s in output["skills"] if s["id"].endswith(":case-skill"))
    assert test_skill["description"] == expected_yaml, (
        f"Block-scalar {block!r}: expected {expected_yaml!r}, got {test_skill['description']!r}"
    )


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

        actual = actual_path.read_bytes()
        if actual != expected:
            mismatches.append(f"{plugin}: Loader does not match template")

    assert not mismatches, f"Loader template mismatches: {', '.join(mismatches)}"


def test_loader_fidelity_against_yaml():
    """Test that each loader's skill extraction matches yaml.safe_load for all skills in the plugin."""
    # Import yaml for comparison
    import yaml

    # Test each plugin's loader against real SKILL.md files
    mismatches = []

    for plugin_name in get_all_plugins():
        plugin_dir = REPO_ROOT / plugin_name
        skills_dir = plugin_dir / "skills"

        if not skills_dir.exists():
            continue

        # Run the loader once for the plugin to get all skills
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

        if result.returncode != 0:
            mismatches.append(f"{plugin_name}: Loader crashed: {result.stderr}")
            continue

        try:
            output = json.loads(result.stdout.strip())
            if not output.get("success", False):
                mismatches.append(f"{plugin_name}: Loader reported failure")
                continue

            # Build a map from skill ID to skill data from loader output
            loader_skills = {}
            for skill in output.get("skills", []):
                loader_skills[skill["id"]] = {
                    "name": skill.get("name"),
                    "description": skill.get("description")
                }

            # Now check each skill directory
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
                            data = yaml.safe_load(frontmatter)
                            if isinstance(data, dict):
                                expected_name = data.get('name')
                                expected_description = data.get('description')
                            else:
                                expected_name = None
                                expected_description = None
                        else:
                            expected_name = None
                            expected_description = None
                    else:
                        expected_name = None
                        expected_description = None
                except Exception:
                    expected_name = None
                    expected_description = None

                # Construct the expected skill ID as the loader would
                expected_id = f"monkey-skills-{plugin_name}:{skill_dir.name}"

                # Get actual from loader. Contract: a skill is advertised iff its
                # description is non-empty (loader skips empty/missing descriptions).
                actual = loader_skills.get(expected_id)
                if not expected_description:
                    if actual is not None:
                        mismatches.append(f"{plugin_name}:{skill_dir.name}: Empty/missing description but skill was advertised")
                    continue
                if actual is None:
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Skill not found in loader output")
                    continue

                # Compare name and description
                if expected_name is None and actual["name"] is None:
                    name_ok = True
                elif expected_name is None:
                    name_ok = False
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Expected no name, got: {repr(actual['name'])}")
                elif actual["name"] is None:
                    name_ok = False
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Expected {repr(expected_name)}, got no name")
                else:
                    name_ok = (str(expected_name) == str(actual["name"]))
                    if not name_ok:
                        mismatches.append(f"{plugin_name}:{skill_dir.name}: Name mismatch\nExpected: {repr(expected_name)}\nActual: {repr(actual['name'])}")

                if expected_description is None and actual["description"] is None:
                    desc_ok = True
                elif expected_description is None:
                    desc_ok = False
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Expected no description, got: {repr(actual['description'])}")
                elif actual["description"] is None:
                    desc_ok = False
                    mismatches.append(f"{plugin_name}:{skill_dir.name}: Expected {repr(expected_description)}, got no description")
                else:
                    desc_ok = (str(expected_description) == str(actual["description"]))
                    if not desc_ok:
                        mismatches.append(f"{plugin_name}:{skill_dir.name}: Description mismatch\nExpected: {repr(expected_description)}\nActual: {repr(actual['description'])}")

                if not (name_ok and desc_ok):
                    # Already added mismatch messages above
                    pass

        except (json.JSONDecodeError, KeyError) as e:
            mismatches.append(f"{plugin_name}: Invalid loader output: {e}")

    assert not mismatches, f"Loader fidelity mismatches: {'; '.join(mismatches[:5])}{'...' if len(mismatches) > 5 else ''}"


def test_loader_handles_missing_skills_dir_silent(tmp_path, plugin_name):
    """Test that loader doesn't log misleading 'Loader failed' when skills dir missing"""
    # Create isolated plugin structure with no skills directory
    temp_plugin_dir = _setup_test_plugin(tmp_path, plugin_name)

    loader_path = temp_plugin_dir / ".opencode-plugin" / "index.js"
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
        cwd=temp_plugin_dir,
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


if __name__ == "__main__":
    # Simple test runner for manual verification
    pytest.main([__file__, "-v"])