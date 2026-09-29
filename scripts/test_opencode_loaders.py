"""Tests for OpenCode v2 plugin loaders"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture(params=[
    "investing-toolkit",
    "obsidian",
    "ascii-graph-toolkit"
])
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

    # Temporarily rename skills directory
    skills_dir = plugin_dir / "skills"
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


if __name__ == "__main__":
    # Simple test runner for manual verification
    pytest.main([__file__, "-v"])