"""loom-workflow ships exactly ten skills, two of them standalone.

The loom 1.0 budget counts eight tools in this plugin. `goal-create` and
`dbt-model-style` sit outside the loom flow and are marked `standalone: true`
in loom-code's contract manifest, so they ship here but are not counted
(user-decided 2026-09-02). This test pins both halves: the directory set on
disk, and the manifest's agreement with it — a skill added or deleted without
a matching manifest edit is the drift this catches.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "loom-workflow" / "skills"
MANIFEST = REPO_ROOT / "loom-code" / "contract" / "manifest.yaml"

COUNTED = {
    "cot-explain",
    "critique",
    "decision-map",
    "distill-sessions",
    "git-memory",
    "handoff",
    "independent-advisor",
    "recap-state",
}
STANDALONE = {"goal-create", "dbt-model-style"}


def _manifest_tools() -> dict[str, bool]:
    """Return {tool name: is standalone} for every loom-workflow tool.

    A three-line hand parse of the `tools:` block rather than a YAML
    dependency: the manifest's flow-mapping rows are fixed-shape, and this
    test must run in the bare CI image the other loom-workflow suites use.
    """
    tools: dict[str, bool] = {}
    in_tools = False
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.startswith("tools:"):
            in_tools = True
            continue
        if in_tools and line and not line[0].isspace():
            break
        if not in_tools or "owner: loom-workflow" not in line:
            continue
        name = line.split("name:", 1)[1].split(",", 1)[0].strip()
        tools[name] = "standalone: true" in line
    return tools


def test_ten_skill_directories_ship():
    on_disk = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}

    assert on_disk == COUNTED | STANDALONE
    assert len(on_disk) == 10


def test_every_skill_has_a_skill_md():
    for directory in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        assert (directory / "SKILL.md").is_file(), directory


def test_manifest_agrees_on_the_two_standalone_skills():
    tools = _manifest_tools()

    assert set(tools) == COUNTED | STANDALONE
    assert {name for name, standalone in tools.items() if standalone} == STANDALONE
    assert len([name for name, standalone in tools.items() if not standalone]) == 8
