"""Static description-standard gate for research-toolkit's member skills.

Pins the house description standard (docs/skill-mining/
2026-06-19-skill-description-standard.md) plus this branch's two new
requirements: a `using-research-toolkit` family-entry router exists, and
`deep-deep-research`'s description carries a positive differentiation
marker vs the host's built-in `deep-research`.

Stdlib + pytest only — no PyYAML. Frontmatter is parsed by line-splitting
between the `---` fences (house precedent:
skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py),
tolerant of both `description: |` block scalars and plain one-line values.
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"

MAX_DESCRIPTION_CHARS = 250
DIFFERENTIATION_MARKERS = ("inspect", "edit", "tunab", "portab")


def _parse_frontmatter(path: Path) -> dict:
    """Return {'name': ..., 'description': ...} parsed from a SKILL.md's
    YAML frontmatter, tolerant of `description: |` block scalars."""
    assert path.is_file(), f"missing {path}"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0].strip() == "---", f"{path} missing opening frontmatter fence"

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    assert end_idx is not None, f"{path} missing closing frontmatter fence"

    fm_lines = lines[1:end_idx]
    result: dict = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        stripped = line.strip()
        if stripped.startswith("name:"):
            result["name"] = stripped[len("name:"):].strip()
            i += 1
            continue
        if stripped.startswith("description:"):
            rest = stripped[len("description:"):].strip()
            if rest and rest[0] in "|>":
                block_lines = []
                i += 1
                while i < len(fm_lines) and (
                    fm_lines[i].strip() == "" or fm_lines[i].startswith((" ", "\t"))
                ):
                    if fm_lines[i].strip() != "":
                        block_lines.append(fm_lines[i].strip())
                    i += 1
                result["description"] = " ".join(block_lines).strip()
                continue
            else:
                result["description"] = rest.strip().strip('"').strip("'")
                i += 1
                continue
        i += 1
    return result


def _all_skill_md_paths() -> list:
    assert SKILLS_DIR.is_dir(), f"missing {SKILLS_DIR}"
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


# --- (a) router skill exists with valid frontmatter -------------------------

def test_using_research_toolkit_router_exists_with_valid_frontmatter():
    router_dir = SKILLS_DIR / "using-research-toolkit"
    router_md = router_dir / "SKILL.md"
    assert router_md.is_file(), f"missing router skill at {router_md}"

    fm = _parse_frontmatter(router_md)
    assert fm.get("name") == "using-research-toolkit", (
        f"router frontmatter name must be 'using-research-toolkit', got {fm.get('name')!r}"
    )
    assert fm.get("description", "").strip(), "router frontmatter description must be non-empty"


# --- (b) every member skill's description is well-formed -------------------

def test_every_skill_description_is_nonempty_within_cap_and_tag_free():
    paths = _all_skill_md_paths()
    assert paths, f"no SKILL.md files found under {SKILLS_DIR}"

    failures = []
    for path in paths:
        fm = _parse_frontmatter(path)
        desc = fm.get("description", "")
        if not desc.strip():
            failures.append(f"{path}: description is empty")
            continue
        if len(desc) > MAX_DESCRIPTION_CHARS:
            failures.append(f"{path}: description is {len(desc)} chars (cap {MAX_DESCRIPTION_CHARS})")
        if "<" in desc:
            failures.append(f"{path}: description contains '<' (XML tag character)")

    assert not failures, "description-standard violations:\n" + "\n".join(failures)


# --- (c) deep-deep-research carries a differentiation marker ---------------

def test_deep_deep_research_has_differentiation_marker():
    path = SKILLS_DIR / "deep-deep-research" / "SKILL.md"
    fm = _parse_frontmatter(path)
    desc = fm.get("description", "").lower()
    assert any(marker in desc for marker in DIFFERENTIATION_MARKERS), (
        f"deep-deep-research description must contain one of {DIFFERENTIATION_MARKERS} "
        f"(positive differentiation vs the host's built-in deep-research); got: {desc!r}"
    )
