"""W1-02 — the build station's dispatch record matches the contract manifest.

`build` is the only station that writes `dispatch[]` entries for
implementers (concept-model §2e). Two things must hold for the record to be
usable by the push rules `reviewer-ne-implementer` and
`dismissed-by-reviewer`:

1. the example the SKILL.md shows an orchestrator is real JSON carrying
   exactly the fields the manifest declares — no more (an invented field is
   an unrecomputable mechanism), no fewer (a missing field is a push rule
   that cannot run);
2. Build has no automatic intermediate review trigger. Task and integration
   tests advance the DAG; one branch-end review follows the completed build.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "loom-code" / "skills" / "build" / "SKILL.md"
MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"


def manifest_dispatch_fields() -> set[str]:
    """Field names declared by the review artifact's `dispatch` grammar."""
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    grammar = next(
        field["grammar"]
        for field in data["artifacts"]["review"]["fields"]
        if field["name"] == "dispatch"
    )
    inner = grammar.strip().strip("[]").strip().strip("{}")
    return {part.split(":")[0].strip() for part in inner.split(",")}


def json_blocks(text: str) -> list[str]:
    return re.findall(r"```json\n(.*?)```", text, re.DOTALL)


def dispatch_example(text: str) -> dict:
    """The first fenced json block that is a dispatch entry."""
    for block in json_blocks(text):
        try:
            value = json.loads(block)
        except json.JSONDecodeError as error:  # a broken example is a defect
            raise AssertionError(
                f"a ```json block in {SKILL.name} does not parse: {error}\n{block}"
            ) from error
        if isinstance(value, dict) and "task" in value:
            return value
    raise AssertionError(
        f"{SKILL.name} shows no ```json object carrying a `task` key — the "
        "dispatch record example the orchestrator copies is missing."
    )


def test_skill_exists():
    assert SKILL.is_file(), f"{SKILL} has not landed."


def test_dispatch_example_carries_exactly_the_manifest_fields():
    entry = dispatch_example(SKILL.read_text(encoding="utf-8"))
    assert set(entry) == manifest_dispatch_fields(), (
        "the dispatch example in the build station must carry exactly the "
        "fields loom-code/contract/manifest.yaml declares for "
        "`artifact:review.dispatch`."
    )


def test_dispatch_example_is_an_implementer_record():
    entry = dispatch_example(SKILL.read_text(encoding="utf-8"))
    assert entry["role"] == "implementer", (
        "build writes implementer dispatch entries; reviewer / blind-runner / "
        "adversary entries are the review station's."
    )
    assert entry["fresh_context"] is True, (
        "every build dispatch is a fresh context (concept-model §6: the "
        "writer is never the verifier)."
    )


def test_build_has_no_automatic_intermediate_review_thresholds():
    text = SKILL.read_text(encoding="utf-8")
    assert not re.search(r"\b8\b\s*files", text)
    assert not re.search(r"\b400\b\s*lines", text)
    assert "at most 5 per plan" not in text


def test_only_branch_end_calls_the_review_station():
    text = SKILL.read_text(encoding="utf-8")
    task_section = text.split("## 4. After each task returns", 1)[1]
    task_section = task_section.split("## 5. Wave end", 1)[0]
    wave_section = text.split("## 5. Wave end", 1)[1]
    wave_section = wave_section.split("**Last wave of the plan.**", 1)[0]
    assert "call `loom-code:review`" not in task_section
    assert "call `loom-code:review`" not in wave_section
