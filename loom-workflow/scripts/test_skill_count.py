"""loom-workflow ships exactly eleven skills, two of them standalone and one
outside loom-code's contract manifest entirely.

The loom 1.0 budget counts eight tools in loom-code's contract manifest.
`goal-create` and `dbt-model-style` sit outside the loom flow and are marked
`standalone: true` there, so they ship here but are not counted
(user-decided 2026-09-02). `loom-memory` joined this plugin's skill
directory when the independent `loom-memory` plugin retired into
loom-workflow (2026-09-11), but its earlier design decision — "memory was
retired from [loom-code's] contract ... owned solely by the independent
`loom-memory` plugin" (test_contract_manifest.py) — survives the move: the
manifest still does not name it, counted or standalone. This test pins all
three halves: the directory set on disk (which does include `loom-memory`),
the manifest's agreement on its own ten tools, and `loom-memory`'s deliberate
absence from that manifest — a skill added or deleted without a matching
manifest edit, or a manifest gaining a stray `loom-memory` entry, is the
drift this catches.
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
# Ships in loom-workflow/skills/ but is deliberately absent from loom-code's
# contract manifest — carried over unchanged from when `loom-memory` was its
# own independent plugin (REQ-24 of 2026-09-10-okf-compatible-loom-memory).
OUT_OF_CONTRACT = {"loom-memory"}


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


def test_eleven_skill_directories_ship():
    on_disk = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}

    assert on_disk == COUNTED | STANDALONE | OUT_OF_CONTRACT
    assert len(on_disk) == 11


def test_every_skill_has_a_skill_md():
    for directory in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        assert (directory / "SKILL.md").is_file(), directory


def test_manifest_agrees_on_the_two_standalone_skills():
    tools = _manifest_tools()

    assert set(tools) == COUNTED | STANDALONE
    assert {name for name, standalone in tools.items() if standalone} == STANDALONE
    assert len([name for name, standalone in tools.items() if not standalone]) == 8


def test_loom_memory_stays_out_of_the_contract_manifest():
    """`loom-memory` ships on disk (`test_eleven_skill_directories_ship`) but
    must not appear in loom-code's contract manifest — the relocation moved
    its files, not its relationship to loom-code's mechanism budget."""
    assert "loom-memory" not in _manifest_tools()
