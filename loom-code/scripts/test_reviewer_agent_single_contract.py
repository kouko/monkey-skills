"""W1-03 — one reviewer contract, and a review station that can be followed.

Four verdict contracts became one: `agents/reviewer.md` takes a `lens:` and
carries every dimension the four old agents scored, so a dimension can only
be lost by being deleted here on purpose. Alongside it the two verification
actions that are not reading get their own short contracts
(`blind-runner.md`, `adversary.md`).

The station's own file is checked the way `write-plan`'s is: a checker rule
it names must exist, a reference path it cites must exist, a paragraph it
uses as a gate must be registered as a mechanism, deleted vocabulary must
stay deleted, and the body must stay short enough that the cold reader of
REQ-9 reaches the end.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
AGENTS = REPO / "loom-code" / "agents"
SKILL_DIR = REPO / "loom-code" / "skills" / "review"
SKILL = SKILL_DIR / "SKILL.md"
CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
CONTRACT = REPO / "loom-code" / "contract"
MECHANISMS = REPO / "docs" / "loom" / "evidence" / "mechanisms.yaml"

WORD_CAP = 4500
AGENT_CAPS = {"reviewer.md": 1460, "blind-runner.md": 600, "adversary.md": 600}
DESCRIPTION_CAP = 400

GATE_RE = re.compile(r"<!--\s*gate:\s*([A-Za-z0-9._-]+)\s*-->")
REFERENCE_RE = re.compile(r"references/([A-Za-z0-9._-]+\.md)")
TEMPLATE_RE = re.compile(r"contract/templates/([A-Za-z0-9._-]+)")
AGENT_RE = re.compile(r"agents/([a-z-]+\.md)")
RULE_RE = re.compile(r"`((?:contract|intake|intent|push|standing)\.[a-z-]+)`")

# The eleven code dimensions and five docs dimensions the four superseded
# reviewer contracts scored. Names, not paraphrases: a renamed dimension is a
# lost dimension as far as an old finding is concerned.
CODE_DIMENSIONS = (
    "security",
    "architecture",
    "correctness",
    "naming",
    "tests",
    "refactoring",
    "cross-task-coherence",
    "external-surface-grounding",
    "principles-conformance",
    "deliberate-simplification",
    "deletion-first",
)
DOCS_DIMENSIONS = (
    "omission",
    "ambiguity",
    "inconsistency",
    "incorrect-fact",
    "missing-population",
)
# Added by the redesign, and the only dimensions that are new.
EXTRA_DIMENSIONS = ("spec-conformance", "design-conformance", "user-judgment-leak")

DELETED_VOCABULARY = (
    r"\bbrief\b",
    r"\bseed\b",
    r"\bbatch\b",
    r"\bbatches\b",
    r"\bwaiver\b",
    r"\bpacket\b",
    r"\breceipt\b",
    r"apply-result",
    r"\bmarker\b",
    r"\bmint\b",
    r"adjudication",
    r"CONFIRMED_RESOLVED",
    r"Approved-by",
    r"Review Batch",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def body_of(text: str) -> str:
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    return text[match.end() :] if match else text


def station_markdown() -> list[Path]:
    return sorted(SKILL_DIR.rglob("*.md")) + [
        AGENTS / name for name in AGENT_CAPS if (AGENTS / name).is_file()
    ]


@pytest.fixture(scope="module")
def skill_text() -> str:
    assert SKILL.is_file(), f"{SKILL.relative_to(REPO)} does not exist."
    return read(SKILL)


# --- the four agent contracts ---------------------------------------------


@pytest.mark.parametrize("name", ["implementer.md", "reviewer.md", "blind-runner.md", "adversary.md"])
def test_the_four_agent_contracts_exist(name):
    path = AGENTS / name
    assert path.is_file(), (
        f"loom-code/agents/{name} is missing; the four roles the dispatch "
        "record names (implementer / reviewer / blind-runner / adversary) each "
        "need exactly one contract."
    )


@pytest.mark.parametrize("name", sorted(AGENT_CAPS))
def test_agent_frontmatter_and_length(name):
    text = read(AGENTS / name)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"agents/{name} has no frontmatter."
    front = yaml.safe_load(match.group(1))
    assert front["name"] == name.removesuffix(".md")
    description = " ".join(str(front["description"]).split())
    assert description, f"agents/{name} declares an empty description."
    assert len(description) <= DESCRIPTION_CAP, (
        f"agents/{name} description is {len(description)} chars (cap {DESCRIPTION_CAP})."
    )
    words = len(body_of(text).split())
    assert words <= AGENT_CAPS[name], (
        f"agents/{name} body is {words} words (cap {AGENT_CAPS[name]})."
    )


def test_reviewer_is_one_contract_with_a_lens_parameter():
    text = read(AGENTS / "reviewer.md")
    assert "lens:" in text, (
        "agents/reviewer.md takes a `lens:` parameter — that parameter is what "
        "makes it one contract instead of four."
    )
    for lens in ("code", "docs", "spec", "design", "principles", "skill"):
        assert re.search(rf"\b{lens}\b", text), f"reviewer.md never names the {lens} lens."


@pytest.mark.parametrize("dimension", CODE_DIMENSIONS + DOCS_DIMENSIONS + EXTRA_DIMENSIONS)
def test_reviewer_names_every_dimension(dimension):
    text = read(AGENTS / "reviewer.md") + read(SKILL_DIR / "references" / "lenses.md")
    assert dimension in text, (
        f"dimension {dimension!r} is named nowhere in the reviewer contract or "
        "its lens definitions; merging four contracts into one may not drop a "
        "dimension silently."
    )


def test_verdict_vocabulary_is_the_one_schema():
    text = read(AGENTS / "reviewer.md")
    for token in ("PASS_WITH_NOTES", "NEEDS_REVISION", "dimension_scores", "findings"):
        assert token in text, f"reviewer.md never names {token}."
    for severity in ("fatal", "important", "nit"):
        assert severity in text, f"reviewer.md never defines severity {severity!r}."


def test_reviewer_does_not_modify_the_artifact():
    text = read(AGENTS / "reviewer.md")
    assert re.search(r"do not (modify|edit|change)", text, re.IGNORECASE), (
        "reviewer.md must say in words that it does not modify what it reviews."
    )


# --- the station file ------------------------------------------------------


def test_frontmatter_name_and_description(skill_text):
    match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    assert match, "SKILL.md has no frontmatter."
    front = yaml.safe_load(match.group(1))
    assert front["name"] == "review"
    description = " ".join(str(front["description"]).split())
    assert len(description) <= DESCRIPTION_CAP, (
        f"description is {len(description)} chars; the host truncates past "
        f"{DESCRIPTION_CAP}."
    )


def test_skill_dir_is_flat():
    nested = [
        p for p in SKILL_DIR.iterdir()
        if p.is_dir() and any(child.is_dir() for child in p.iterdir())
    ]
    assert not nested, f"skill sub-folders must not nest: {nested}"


def test_summary_table_is_present(skill_text):
    header = next(
        (
            line for line in skill_text.splitlines()
            if line.strip().startswith("|")
            and all(column in line.lower() for column in ("artifact", "who decides", "checker", "checkpoint"))
        ),
        None,
    )
    assert header, (
        "SKILL.md carries no station summary table; REQ-9's cold reader answers "
        "the four questions from this one file or not at all."
    )


def test_referenced_paths_exist(skill_text):
    cited = set(REFERENCE_RE.findall(skill_text))
    assert cited, "SKILL.md cites none of its own references."
    for name in sorted(cited):
        assert (SKILL_DIR / "references" / name).is_file(), (
            f"SKILL.md cites references/{name}, which does not exist."
        )
    for name in sorted(set(TEMPLATE_RE.findall(skill_text))):
        assert (CONTRACT / "templates" / name).is_file(), (
            f"SKILL.md cites contract/templates/{name}, which does not exist."
        )
    for name in sorted(set(AGENT_RE.findall(skill_text))):
        assert (AGENTS / name).is_file(), (
            f"SKILL.md cites agents/{name}, which does not exist."
        )


def checker_rule_ids() -> set[str]:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True, check=True,
    )
    return {line.split("\t", 1)[0].strip() for line in result.stdout.splitlines() if line.strip()}


def test_every_named_checker_rule_exists(skill_text):
    known = checker_rule_ids()
    named = set(RULE_RE.findall(skill_text))
    assert named, "SKILL.md names no checker rule; the station has to say what blocks it."
    unknown = sorted(named - known)
    assert not unknown, f"SKILL.md names checker rules that do not exist: {unknown}."


def test_gate_markers_are_registered_mechanisms():
    registered = {
        str(entry["id"]): entry
        for entry in yaml.safe_load(read(MECHANISMS))["mechanisms"]
    }
    found = set()
    for path in sorted(SKILL_DIR.rglob("*.md")):
        found |= set(GATE_RE.findall(read(path)))
    assert found, (
        "the review station marks no prose gate at all; two reviewers, a "
        "reviewer who did not implement, and a review-only commit are gates."
    )
    for gate_id in sorted(found):
        assert gate_id.startswith("review."), (
            f"gate id {gate_id!r} must be namespaced `review.<id>`."
        )
        assert gate_id in registered, (
            f"gate {gate_id!r} is not registered in "
            f"{MECHANISMS.relative_to(REPO)} — an unregistered gate raises the "
            "mechanism baseline silently."
        )
        assert registered[gate_id]["class"] == "prose-gate"
        assert str(registered[gate_id].get("eval", "")).strip()


@pytest.mark.parametrize("pattern", DELETED_VOCABULARY)
def test_no_deleted_vocabulary(pattern):
    offenders = [
        path.relative_to(REPO).as_posix()
        for path in station_markdown()
        if re.search(pattern, read(path), re.IGNORECASE)
    ]
    assert not offenders, (
        f"{pattern} names a concept the redesign deleted; found in {offenders}."
    )


def test_body_word_count(skill_text):
    words = len(body_of(skill_text).split())
    assert words <= WORD_CAP, f"SKILL.md body is {words} words (cap {WORD_CAP})."


# Facts the station cannot be run without: each is pinned by the substring
# that carries it rather than by the section it happens to live in.
LOAD_BEARING = [
    ("SKILL.md", "two or more fresh-context reviewers"),
    ("SKILL.md", "second-vendor:"),
    ("SKILL.md", "codex exec --sandbox read-only"),
    ("SKILL.md", "never suggests"),
    ("SKILL.md", "git diff <reviewed_sha>..HEAD"),
    ("SKILL.md", "merge-base"),
    ("SKILL.md", "HEAD^"),
    ("SKILL.md", "chore(loom): checkpoint review"),
    ("SKILL.md", "Fix rounds do not count"),
    ("SKILL.md", "no averaging"),
    ("SKILL.md", "blind-run-report.md"),
    ("blind-run-report.md", "對你既有的資料做了什麼"),
    ("blind-run-report.md", "I decided for you"),
    ("adversarial.md", "at least three"),
]


@pytest.mark.parametrize("filename,fact", LOAD_BEARING)
def test_load_bearing_facts_are_stated(filename, fact):
    path = SKILL if filename == "SKILL.md" else SKILL_DIR / "references" / filename
    assert fact in read(path), (
        f"{path.relative_to(REPO)} no longer states {fact!r}; without it the "
        "cold reader has to guess."
    )
