"""W1-03 — review.json has one schema, declared once in the contract package.

The review station writes the file, `loom_checker.py` reads it at push, and
`build` appends to it. Three writers, one shape: the contract manifest's
`artifacts.review.fields` is the declaration, `contract/templates/review.json`
is the worked example that ships with it, and the example inside the review
station's SKILL.md is what an orchestrator actually copies. A key that exists
in one of the three and not the others is a push rule that cannot run, or a
field nobody ever fills.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"
TEMPLATE = REPO / "loom-code" / "contract" / "templates" / "review.json"
SKILL = REPO / "loom-code" / "skills" / "review" / "SKILL.md"

# Fields the checker reads that the manifest's grammar does not name, because
# they are round bookkeeping rather than part of one verdict's content:
# `round` groups a checkpoint's verdicts, `scope` says what that round looked
# at (it is what keeps a later code round from standing in for the spec one).
BOOKKEEPING = {"round", "scope"}


@pytest.fixture(scope="module")
def manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def declared_fields(manifest) -> list[dict]:
    return manifest["artifacts"]["review"]["fields"]


@pytest.fixture(scope="module")
def template() -> dict:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def skill_example() -> dict:
    assert SKILL.is_file(), f"{SKILL.relative_to(REPO)} does not exist."
    blocks = re.findall(r"```json\n(.*?)```", SKILL.read_text(encoding="utf-8"), re.DOTALL)
    for block in blocks:
        if "reviewed_sha" in block:
            return json.loads(block)
    raise AssertionError(
        "the review station's SKILL.md shows no ```json example carrying "
        "`reviewed_sha`; the orchestrator has nothing to copy."
    )


def grammar_fields(field: dict) -> set[str] | None:
    """The inner object's key names, read off the manifest's own grammar
    string (`[{a, b, c}]`), so this test never keeps a second copy."""
    grammar = field.get("grammar")
    if not grammar or "{" not in grammar:
        return None
    inner = grammar[grammar.index("{") + 1 : grammar.rindex("}")]
    names: set[str] = set()
    for part in inner.split(","):
        key = part.split(":")[0].strip()
        if key:
            # `resolved | dismissed` is one slot with two spellings.
            names |= {alt.strip() for alt in key.split("|") if alt.strip()}
    return names


def test_template_carries_exactly_the_declared_fields(declared_fields, template):
    declared = {field["name"] for field in declared_fields}
    assert set(template) == declared, (
        "contract/templates/review.json and the manifest disagree: "
        f"template-only {sorted(set(template) - declared)}, "
        f"manifest-only {sorted(declared - set(template))}."
    )


def test_skill_example_carries_exactly_the_declared_fields(declared_fields, skill_example):
    declared = {field["name"] for field in declared_fields}
    assert set(skill_example) == declared, (
        "the review station's example and the manifest disagree: "
        f"example-only {sorted(set(skill_example) - declared)}, "
        f"manifest-only {sorted(declared - set(skill_example))}."
    )


def test_skill_example_containers_match_the_template(template, skill_example):
    for key, value in template.items():
        assert type(skill_example[key]) is type(value), (
            f"`{key}` is {type(skill_example[key]).__name__} in the station's "
            f"example but {type(value).__name__} in the template; the checker "
            "reads the template's container type."
        )


@pytest.mark.parametrize("source", ["template", "example"])
def test_array_entries_carry_the_declared_grammar(declared_fields, template, skill_example, source):
    document = template if source == "template" else skill_example
    for field in declared_fields:
        expected = grammar_fields(field)
        if expected is None:
            continue
        entries = document[field["name"]]
        assert isinstance(entries, list) and entries, (
            f"`{field['name']}` in the {source} shows no entry, so its grammar "
            "is never demonstrated."
        )
        for entry in entries:
            # `resolved` / `dismissed` are the two outcomes of one finding;
            # an entry shows either, so neither is required on its own.
            missing = expected - set(entry) - {"resolved", "dismissed"}
            assert not missing, (
                f"`{field['name']}` entry in the {source} is missing "
                f"{sorted(missing)} declared by the manifest grammar."
            )
            extra = set(entry) - expected - BOOKKEEPING
            assert not extra, (
                f"`{field['name']}` entry in the {source} carries undeclared "
                f"field(s) {sorted(extra)}; an undeclared field is a mechanism "
                "no checker recomputes."
            )
