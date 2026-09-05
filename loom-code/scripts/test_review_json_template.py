"""W1-05 — `loom-code/contract/templates/review.json` carries a `cost` block.

Outcome 3 of intent 2026-09-05-review-sees-complexity-and-process-cost: the
review station records a per-change process-cost record (rounds, dispatches,
cap-bump count, hours from the plan commit to the PR) at every checkpoint.
The template is the worked shape every checkpoint's first write copies, so
it must show the key with the shape a freshly-created review.json starts
from -- zero rounds, zero dispatches, no cap changes yet, no PR time yet.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "loom-code" / "contract" / "templates" / "review.json"


def _template() -> dict:
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def test_template_parses_as_json() -> None:
    _template()


def test_template_carries_a_cost_block_with_the_declared_shape() -> None:
    document = _template()
    assert "cost" in document, "the template carries no `cost` key"
    assert document["cost"] == {
        "rounds": 0,
        "dispatches": 0,
        "cap_changes": [],
        "hours_plan_to_pr": None,
    }


def test_every_review_record_cost_block_has_exactly_the_declared_shape() -> None:
    """A real review.json that carries `cost` has the four declared keys and
    nothing else, with the declared value types (wave-end:1 reader finding:
    the registered eval checked only the template)."""
    import json
    for path in sorted((REPO / "docs" / "loom").glob("*/review.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if "cost" not in record:
            continue
        cost = record["cost"]
        assert set(cost) == {"rounds", "dispatches", "cap_changes", "hours_plan_to_pr"}, path
        assert isinstance(cost["rounds"], int) and isinstance(cost["dispatches"], int), path
        assert isinstance(cost["cap_changes"], list), path
        assert cost["hours_plan_to_pr"] is None or isinstance(cost["hours_plan_to_pr"], (int, float)), path
