"""W1-01 — the write-plan station's SKILL.md is executable as written.

Everything asserted here is a way the file could quietly stop being
followable: a checker sub-command that does not exist, a reference path that
was never written, a paragraph used as a gate without the `<!-- gate: -->`
marker that registers it as a mechanism (concept-model §11), a deleted
concept resurrected by habit, or a body long enough that the cold reader of
REQ-9 never reaches the end.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO / "loom-code" / "skills" / "write-plan"
SKILL = SKILL_DIR / "SKILL.md"
CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
CONTRACT = REPO / "loom-code" / "contract"
MECHANISMS = REPO / "docs" / "loom" / "evidence" / "mechanisms.yaml"

WORD_CAP = 4500
DESCRIPTION_CAP = 400

SUBCOMMAND_RE = re.compile(r"loom_checker\.py\s+(--list-rules|[a-z][a-z-]*)")
GATE_RE = re.compile(r"<!--\s*gate:\s*([A-Za-z0-9._-]+)\s*-->")
REFERENCE_RE = re.compile(r"references/([A-Za-z0-9._-]+\.md)")
TEMPLATE_RE = re.compile(r"contract/templates/([A-Za-z0-9._-]+)")

# concept-model §10 deleted these outright. A station SKILL.md that still
# speaks them is teaching a flow that no longer exists.
DELETED_VOCABULARY = (
    r"\bbrief\b",
    r"\bbriefs\b",
    r"\bseed\b",
    r"\bbatch\b",
    r"\bbatches\b",
    r"\bwaiver\b",
    r"\bwaivers\b",
    r"\bon-ramp\b",
    r"kickoff briefing",
    r"Approved-by",
    r"Decision Log",
    r"Review Batch",
)


@pytest.fixture(scope="module")
def skill_text() -> str:
    assert SKILL.is_file(), f"{SKILL.relative_to(REPO)} does not exist."
    return SKILL.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def skill_body(skill_text: str) -> str:
    match = re.match(r"^---\n.*?\n---\n", skill_text, re.DOTALL)
    return skill_text[match.end() :] if match else skill_text


def skill_markdown() -> list[Path]:
    return sorted(p for p in SKILL_DIR.rglob("*.md"))


def checker_subcommands() -> set[str]:
    """The sub-command names the checker actually dispatches, read from its
    COMMANDS mapping rather than from a copy kept in this test."""
    tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "COMMANDS" in targets and isinstance(node.value, ast.Dict):
                return {
                    key.value
                    for key in node.value.keys
                    if isinstance(key, ast.Constant)
                }
    raise AssertionError("loom_checker.py declares no COMMANDS mapping.")


def test_skill_dir_is_flat():
    assert SKILL.is_file()
    nested = [
        p
        for p in SKILL_DIR.iterdir()
        if p.is_dir() and any(child.is_dir() for child in p.iterdir())
    ]
    assert not nested, f"skill sub-folders must not nest: {nested}"


def test_frontmatter_name_and_description(skill_text):
    match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    assert match, "SKILL.md has no frontmatter."
    front = yaml.safe_load(match.group(1))
    assert front["name"] == "write-plan"
    description = " ".join(str(front["description"]).split())
    assert len(description) <= DESCRIPTION_CAP, (
        f"description is {len(description)} chars; the host truncates past "
        f"{DESCRIPTION_CAP}."
    )


def test_every_checker_subcommand_exists(skill_text):
    known = checker_subcommands() | {"--list-rules"}
    used = set(SUBCOMMAND_RE.findall(skill_text))
    assert used, "SKILL.md names no loom_checker.py sub-command at all."
    unknown = sorted(used - known)
    assert not unknown, (
        f"SKILL.md tells the agent to run sub-commands the checker does not "
        f"have: {unknown}; known are {sorted(known)}."
    )


def test_referenced_paths_exist(skill_text):
    for name in sorted(set(REFERENCE_RE.findall(skill_text))):
        assert (SKILL_DIR / "references" / name).is_file(), (
            f"SKILL.md cites references/{name}, which does not exist."
        )
    for name in sorted(set(TEMPLATE_RE.findall(skill_text))):
        assert (CONTRACT / "templates" / name).is_file(), (
            f"SKILL.md cites contract/templates/{name}, which does not exist."
        )


def test_gate_markers_are_registered_mechanisms():
    registered = {
        str(entry["id"]): entry
        for entry in yaml.safe_load(MECHANISMS.read_text(encoding="utf-8"))["mechanisms"]
    }
    found = set()
    for path in skill_markdown():
        found |= set(GATE_RE.findall(path.read_text(encoding="utf-8")))
    assert found, (
        "write-plan marks no prose gate at all; the two rules it enforces in "
        "prose (no plan without a confirmed intent; a product spec needs "
        "confirmed-behavior) are gates and must be marked."
    )
    for gate_id in sorted(found):
        assert gate_id.startswith("write-plan."), (
            f"gate id {gate_id!r} must be namespaced `write-plan.<id>`."
        )
        assert gate_id in registered, (
            f"gate {gate_id!r} is not registered in "
            f"{MECHANISMS.relative_to(REPO)} — an unregistered gate raises the "
            "mechanism baseline silently (concept-model §11)."
        )
        entry = registered[gate_id]
        assert entry["class"] == "prose-gate", (
            f"gate {gate_id!r} is registered as class {entry['class']!r}."
        )
        assert str(entry.get("eval", "")).strip(), (
            f"gate {gate_id!r} carries no eval:."
        )


@pytest.mark.parametrize("pattern", DELETED_VOCABULARY)
def test_no_deleted_vocabulary(pattern):
    offenders = []
    for path in skill_markdown():
        text = path.read_text(encoding="utf-8")
        if re.search(pattern, text, re.IGNORECASE):
            offenders.append(path.relative_to(REPO).as_posix())
    assert not offenders, (
        f"{pattern} names a concept concept-model §10 deleted; found in "
        f"{offenders}."
    )


# Facts the station cannot be followed without. Each one was a cold-read
# guess or an after-task review finding before it was written down, so each
# is pinned by the substring that carries it rather than by its section.
LOAD_BEARING = [
    ("SKILL.md", "five of the seven"),                       # second-vendor number
    ("SKILL.md", "when it is done you will be able to"),     # UI flow 1 restatement
    ("SKILL.md", "Is that right?"),
    ("SKILL.md", "reads or types into"),                     # needs-design (a)
    ("SKILL.md", "multi-state or multi-object"),             # needs-design (b)
    ("SKILL.md", "intent.needs-design-recompute"),           # who has the last word on `no`
    ("SKILL.md", "Budget **2 per plan**"),                   # after-task budget
    ("SKILL.md", "at most 5 checkpoints during build"),      # the cap is on checkpoints
    ("SKILL.md", "contract.requires"),                       # step 0's rule id
    ("SKILL.md", "/hooks"),                                  # Codex first contact
    ("SKILL.md", "codex_scaffold.py --probe"),
    ("SKILL.md", "user-judgment-leak"),                      # the dimension that catches a bad question
    ("SKILL.md", "<YYYY-MM-DD>-<slug>"),                     # change-id grammar
    ("SKILL.md", "user-decided —"),                          # where answers land with no spec
    ("one-way-door.md", "(a) Hard to swap later"),
    ("one-way-door.md", "(b) Creates money or a standing obligation"),
    ("one-way-door.md", "(c) Limits what the user can do in future"),
    ("one-way-door.md", "(d) Sets the ceiling on output quality"),
    ("one-way-door.md", "(e) An irreversible action on the user's existing state"),
    ("one-way-door.md", "Check first"),
    ("one-way-door.md", "Measure first"),
    ("one-way-door.md", "Threshold"),
    ("one-way-door.md", "Merge"),
]


@pytest.mark.parametrize("filename,fact", LOAD_BEARING)
def test_load_bearing_facts_are_stated(filename, fact):
    path = SKILL if filename == "SKILL.md" else SKILL_DIR / "references" / filename
    text = path.read_text(encoding="utf-8")
    assert fact in text, (
        f"{path.relative_to(REPO)} no longer states {fact!r}; without it the "
        "cold reader has to guess (REQ-9 counts a guess as a failure)."
    )


def test_body_word_count(skill_body):
    words = len(skill_body.split())
    assert words <= WORD_CAP, f"SKILL.md body is {words} words (cap {WORD_CAP})."
