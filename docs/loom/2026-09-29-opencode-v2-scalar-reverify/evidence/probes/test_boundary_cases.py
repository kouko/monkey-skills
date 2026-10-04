"""Adversarial probe: boundary cases.

Tests loader behavior with:
- Missing skills directory
- Empty skills directory
- Hidden directories (starting with .)
- Malformed frontmatter
- Skills directory that is a file (not a directory)

This is an adversarial probe — it should FAIL if the loader crashes
or behaves incorrectly on these edge cases.
"""

# concern: loader may crash or behave incorrectly on boundary cases (missing skills dir, empty skills dir, hidden dirs, malformed frontmatter, skills dir as file)

import json
import subprocess
import tempfile
from pathlib import Path
import shutil


def create_fake_plugin(plugin_name: str, setup_skills_fn) -> Path:
    """Create a fake plugin directory with loader and skills setup.
    Returns the path to the fake plugin directory."""
    tmp_path = Path(tempfile.mkdtemp())
    plugin_dir = tmp_path / plugin_name
    plugin_dir.mkdir()

    # Create .opencode-plugin directory
    opencode_dir = plugin_dir / ".opencode-plugin"
    opencode_dir.mkdir()

    # Copy the loader from investing-toolkit (any plugin loader works)
    real_loader = Path(__file__).parent.parent.parent.parent.parent.parent / "investing-toolkit" / ".opencode-plugin" / "index.js"
    shutil.copy2(real_loader, opencode_dir / "index.js")

    # Let the setup function create the skills structure
    skills_dir = plugin_dir / "skills"
    setup_skills_fn(skills_dir)

    return plugin_dir


def run_loader_in_fake_plugin(plugin_dir: Path) -> dict:
    """Run the loader in the given fake plugin directory and return parsed output."""
    opencode_dir = plugin_dir / ".opencode-plugin"
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
        cwd=plugin_dir,
        capture_output=True,
        text=True,
        timeout=10
    )

    assert result.returncode == 0, f"Loader crashed: {result.stderr}"
    return json.loads(result.stdout.strip())


def test_missing_skills_dir():
    """Test that missing skills directory is handled gracefully."""
    def setup(skills_dir):
        # Do not create skills directory at all
        pass

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        assert output["skillCount"] == 0, f"Expected 0 skills for missing dir, got {output['skillCount']}"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_missing_skills_dir PASSED")


def test_empty_skills_dir():
    """Test that empty skills directory is handled gracefully."""
    def setup(skills_dir):
        skills_dir.mkdir()
        # No subdirectories

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        assert output["skillCount"] == 0, f"Expected 0 skills for empty dir, got {output['skillCount']}"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_empty_skills_dir PASSED")


def test_skills_dir_is_file():
    """Test that skills path being a file (not directory) is handled."""
    def setup(skills_dir):
        # Create a file at the skills directory path
        skills_dir.write_text("not a directory")

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        assert output["skillCount"] == 0, f"Expected 0 skills for file-as-dir, got {output['skillCount']}"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_skills_dir_is_file PASSED")


def test_hidden_directories_skipped():
    """Test that hidden directories (starting with .) are skipped."""
    def setup(skills_dir):
        skills_dir.mkdir()

        # Hidden skill directory
        hidden_dir = skills_dir / ".hidden-skill"
        hidden_dir.mkdir()
        (hidden_dir / "SKILL.md").write_text(
            "---\n"
            "name: hidden-skill\n"
            "description: should not appear\n"
            "---\n"
            "Hidden content\n"
        )

        # Visible skill directory
        visible_dir = skills_dir / "visible-skill"
        visible_dir.mkdir()
        (visible_dir / "SKILL.md").write_text(
            "---\n"
            "name: visible-skill\n"
            "description: should appear\n"
            "---\n"
            "Visible content\n"
        )

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        assert output["skillCount"] == 1, f"Expected 1 skill (hidden skipped), got {output['skillCount']}"
        assert output["skills"][0]["name"] == "visible-skill"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_hidden_directories_skipped PASSED")


def test_non_directory_entries_skipped():
    """Test that non-directory entries in skills dir are skipped."""
    def setup(skills_dir):
        skills_dir.mkdir()

        # A file in skills dir (not a directory)
        (skills_dir / "README.md").write_text("# Not a skill")

        # A valid skill directory
        skill_dir = skills_dir / "valid-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: valid-skill\n"
            "description: valid\n"
            "---\n"
            "Valid content\n"
        )

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        assert output["skillCount"] == 1, f"Expected 1 skill (file skipped), got {output['skillCount']}"
        assert output["skills"][0]["name"] == "valid-skill"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_non_directory_entries_skipped PASSED")


def test_malformed_frontmatter():
    """Test that malformed frontmatter doesn't crash the loader."""
    def setup(skills_dir):
        skills_dir.mkdir()

        # Skill with no frontmatter
        skill1 = skills_dir / "no-frontmatter"
        skill1.mkdir()
        (skill1 / "SKILL.md").write_text("Just body content, no frontmatter\n")

        # Skill with unclosed frontmatter
        skill2 = skills_dir / "unclosed-frontmatter"
        skill2.mkdir()
        (skill2 / "SKILL.md").write_text(
            "---\n"
            "name: unclosed\n"
            "description: no closing dashes\n"
            "Body content\n"
        )

        # Skill with invalid YAML
        skill3 = skills_dir / "invalid-yaml"
        skill3.mkdir()
        (skill3 / "SKILL.md").write_text(
            "---\n"
            "name: invalid\n"
            "description: [unclosed bracket\n"
            "---\n"
            "Body\n"
        )

        # Valid skill for comparison
        skill4 = skills_dir / "valid-skill"
        skill4.mkdir()
        (skill4 / "SKILL.md").write_text(
            "---\n"
            "name: valid-skill\n"
            "description: valid\n"
            "---\n"
            "Valid content\n"
        )

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        # Should at least register the valid skill
        skill_names = [s["name"] for s in output["skills"]]
        assert "valid-skill" in skill_names, f"Valid skill not registered: {skill_names}"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_malformed_frontmatter PASSED")


def test_skill_without_skill_md():
    """Test that skill directories without SKILL.md are skipped."""
    def setup(skills_dir):
        skills_dir.mkdir()

        # Directory without SKILL.md
        nodoc = skills_dir / "no-skill-md"
        nodoc.mkdir()

        # Valid skill
        valid = skills_dir / "valid-skill"
        valid.mkdir()
        (valid / "SKILL.md").write_text(
            "---\n"
            "name: valid-skill\n"
            "description: valid\n"
            "---\n"
            "Valid\n"
        )

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        assert output["skillCount"] == 1, f"Expected 1 skill, got {output['skillCount']}"
        assert output["skills"][0]["name"] == "valid-skill"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_skill_without_skill_md PASSED")


def test_skill_md_is_directory():
    """Test that SKILL.md being a directory doesn't crash."""
    def setup(skills_dir):
        skills_dir.mkdir()

        # SKILL.md is a directory
        skill_dir = skills_dir / "skill-md-is-dir"
        skill_dir.mkdir()
        skill_md_dir = skill_dir / "SKILL.md"
        skill_md_dir.mkdir()

        # Valid skill
        valid = skills_dir / "valid-skill"
        valid.mkdir()
        (valid / "SKILL.md").write_text(
            "---\n"
            "name: valid-skill\n"
            "description: valid\n"
            "---\n"
            "Valid\n"
        )

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        output = run_loader_in_fake_plugin(plugin_dir)
        assert output["success"] is True
        assert output["skillCount"] == 1, f"Expected 1 skill, got {output['skillCount']}"
        assert output["skills"][0]["name"] == "valid-skill"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_skill_md_is_directory PASSED")


def test_no_misleading_loader_failed_log():
    """Test that missing skills dir doesn't log misleading 'Loader failed'."""
    def setup(skills_dir):
        # No skills dir
        pass

    plugin_dir = create_fake_plugin("fake-plugin", setup)
    try:
        opencode_dir = plugin_dir / ".opencode-plugin"
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

        assert result.returncode == 0, f"Loader crashed: {result.stderr}"
        output = json.loads(result.stdout.strip())
        assert output["success"] is True
        assert output["skillCount"] == 0
        # Should not have logged "Loader failed"
        assert "Loader failed" not in result.stderr, f"Misleading error log: {result.stderr}"
    finally:
        shutil.rmtree(plugin_dir.parent)
    print("test_no_misleading_loader_failed_log PASSED")


if __name__ == "__main__":
    test_missing_skills_dir()
    test_empty_skills_dir()
    test_skills_dir_is_file()
    test_hidden_directories_skipped()
    test_non_directory_entries_skipped()
    test_malformed_frontmatter()
    test_skill_without_skill_md()
    test_skill_md_is_directory()
    test_no_misleading_loader_failed_log()
    print("\nAll boundary case tests PASSED")