"""Adversarial probe: await ctx.skill.transform() contract.

Tests that the loader correctly awaits ctx.skill.transform() and that
the registration happens asynchronously. If the loader doesn't await
properly, skills won't be registered.

This is an adversarial probe — it should FAIL if the await is missing
or if the transform contract is violated.
"""

# concern: loader may not properly await ctx.skill.transform() or violate transform contract

import json
import subprocess
import tempfile
from pathlib import Path
import shutil


def run_loader(plugin_name: str, extra_setup: str = "") -> dict:
    """Run the loader and return parsed output."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_dir = tmp_path / plugin_name
        opencode_dir = plugin_dir / ".opencode-plugin"
        opencode_dir.mkdir(parents=True)

        real_loader = Path(__file__).parent.parent.parent.parent.parent.parent / plugin_name / ".opencode-plugin" / "index.js"
        shutil.copy2(real_loader, opencode_dir / "index.js")

        # Create skills dir with test skill
        skills_dir = plugin_dir / "skills"
        skills_dir.mkdir()
        test_skill_dir = skills_dir / "test-skill"
        test_skill_dir.mkdir()
        (test_skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: test-skill\n"
            "description: test\n"
            "---\n"
            "Body content\n"
        )

        loader_path = opencode_dir / "index.js"
        test_script = f"""
        const ctx = {{
            registeredSkills: [],
            transformCalled: false,
            transformCompleted: false,
            skill: {{
                transform: (fn) => {{
                    ctx.transformCalled = true;
                    const draft = {{
                        add: (skill) => {{
                            ctx.registeredSkills.push(skill);
                        }}
                    }};
                    const result = fn(draft);
                    ctx.transformCompleted = true;
                    return result;
                }}
            }}
        }};

        (async () => {{
            const loader = await import('file://' + {repr(str(loader_path.absolute()))});
            await loader.default.setup(ctx);
            {extra_setup}
            console.log(JSON.stringify({{
                success: true,
                transformCalled: ctx.transformCalled,
                transformCompleted: ctx.transformCompleted,
                skillCount: ctx.registeredSkills.length,
                skills: ctx.registeredSkills.map(s => ({{
                    id: s.id,
                    name: s.name
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


def test_transform_is_awaited():
    """Test that setup() awaits ctx.skill.transform() before returning."""
    output = run_loader("investing-toolkit")

    # transform should have been called and completed
    assert output["transformCalled"] is True, "ctx.skill.transform was not called"
    assert output["transformCompleted"] is True, "ctx.skill.transform did not complete"
    assert output["skillCount"] == 1, f"Expected 1 skill, got {output['skillCount']}"

    print("test_transform_is_awaited PASSED")


def test_transform_returns_promise():
    """Test that setup() waits for a transform whose Promise resolves on a later turn.

    The fake transform resolves the registration on a setTimeout — if the loader
    does not await the returned Promise, setup() resolves before the skill lands.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_dir = tmp_path / "investing-toolkit"
        opencode_dir = plugin_dir / ".opencode-plugin"
        opencode_dir.mkdir(parents=True)

        real_loader = Path(__file__).parent.parent.parent.parent / "investing-toolkit" / ".opencode-plugin" / "index.js"
        shutil.copy2(real_loader, opencode_dir / "index.js")

        skills_dir = plugin_dir / "skills"
        skills_dir.mkdir()
        test_skill_dir = skills_dir / "test-skill"
        test_skill_dir.mkdir()
        (test_skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: test-skill\n"
            "description: test\n"
            "---\n"
            "Body content\n"
        )

        loader_path = opencode_dir / "index.js"
        test_script = f"""
        const ctx = {{
            registeredSkills: [],
            skill: {{
                transform: (fn) => {{
                    // Resolve on a later event-loop turn — a loader that does not
                    // await this Promise returns from setup() with 0 skills.
                    return new Promise((resolve) => {{
                        setTimeout(() => {{
                            const draft = {{ add: (skill) => ctx.registeredSkills.push(skill) }};
                            fn(draft);
                            resolve();
                        }}, 20);
                    }});
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
        assert output["skillCount"] == 1, (
            f"setup() returned before the delayed transform completed — await is missing "
            f"(got {output['skillCount']} skills, expected 1)"
        )

    print("test_transform_returns_promise PASSED")


def test_multiple_skills_registered():
    """Test that multiple skills are all registered through transform."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_dir = tmp_path / "investing-toolkit"
        opencode_dir = plugin_dir / ".opencode-plugin"
        opencode_dir.mkdir(parents=True)

        real_loader = Path(__file__).parent.parent.parent.parent / "investing-toolkit" / ".opencode-plugin" / "index.js"
        shutil.copy2(real_loader, opencode_dir / "index.js")

        skills_dir = plugin_dir / "skills"
        skills_dir.mkdir()

        # Create 3 skills
        for i in range(3):
            test_skill_dir = skills_dir / f"test-skill-{i}"
            test_skill_dir.mkdir()
            (test_skill_dir / "SKILL.md").write_text(
                f"---\n"
                f"name: test-skill-{i}\n"
                f"description: test {i}\n"
                f"---\n"
                f"Body content {i}\n"
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
                skillCount: ctx.registeredSkills.length,
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

        assert result.returncode == 0, f"Loader crashed: {result.stderr}"
        output = json.loads(result.stdout.strip())

        assert output["skillCount"] == 3, f"Expected 3 skills, got {output['skillCount']}"

    print("test_multiple_skills_registered PASSED")


def test_transform_error_handling():
    """Test that errors in individual skill registration don't stop others."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        plugin_dir = tmp_path / "investing-toolkit"
        opencode_dir = plugin_dir / ".opencode-plugin"
        opencode_dir.mkdir(parents=True)

        real_loader = Path(__file__).parent.parent.parent.parent / "investing-toolkit" / ".opencode-plugin" / "index.js"
        shutil.copy2(real_loader, opencode_dir / "index.js")

        skills_dir = plugin_dir / "skills"
        skills_dir.mkdir()

        # Good skill
        test_skill_dir = skills_dir / "good-skill"
        test_skill_dir.mkdir()
        (test_skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: good-skill\n"
            "description: good\n"
            "---\n"
            "Good content\n"
        )

        # Skill with missing name (will use dir name)
        test_skill_dir2 = skills_dir / "no-name-skill"
        test_skill_dir2.mkdir()
        (test_skill_dir2 / "SKILL.md").write_text(
            "---\n"
            "description: no name\n"
            "---\n"
            "No name content\n"
        )

        # Skill that will cause an error during registration
        test_skill_dir3 = skills_dir / "bad-skill"
        test_skill_dir3.mkdir()
        (test_skill_dir3 / "SKILL.md").write_text(
            "---\n"
            "name: bad-skill\n"
            "description: bad\n"
            "---\n"
            "Bad content\n"
        )

        loader_path = opencode_dir / "index.js"
        test_script = f"""
        const ctx = {{
            registeredSkills: [],
            skill: {{
                transform: (fn) => {{
                    const draft = {{
                        add: (skill) => {{
                            // Simulate a failure for one skill
                            if (skill.name === "bad-skill") {{
                                throw new Error("Simulated registration failure");
                            }}
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
                skillNames: ctx.registeredSkills.map(s => s.name)
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

        # Should have registered both skills (errors are caught per-skill)
        assert output["skillCount"] == 2, f"Expected 2 skills, got {output['skillCount']}"
        assert "good-skill" in output["skillNames"]
        assert "no-name-skill" in output["skillNames"]

    print("test_transform_error_handling PASSED")


if __name__ == "__main__":
    test_transform_is_awaited()
    test_transform_returns_promise()
    test_multiple_skills_registered()
    test_transform_error_handling()
    print("\nAll transform contract tests PASSED")