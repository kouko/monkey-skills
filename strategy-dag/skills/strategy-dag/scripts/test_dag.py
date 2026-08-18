"""RED test for Task 2 — dag.py load_project() + node-schema.md.

@req: BI-1
@req: BI-2
@req: BI-3
"""
from __future__ import annotations

from pathlib import Path

import dag


NODE_FIELDS = (
    "id", "type", "seq", "inputs", "summary", "status",
    "branch", "branch_type", "source", "quote", "path",
)
ASSUMPTION_FIELDS = (
    "id", "status", "statement", "breaks_if", "source", "branch", "path",
)


def _write(path: Path, frontmatter: str, body: str = "body text\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n{body}", encoding="utf-8")


def test_load_project_parses_nodes_assumptions_and_research_claims(tmp_path):
    root = tmp_path

    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: active\n",
    )
    _write(
        root / "nodes" / "fact.md",
        "id: fact1\n"
        "type: FACT\n"
        "seq: 2\n"
        "summary: Users churn at 5%\n"
        "status: active\n"
        "source: internal survey\n"
        "quote: \"5% monthly churn\"\n",
    )
    _write(
        root / "nodes" / "claim.md",
        "id: claim1\n"
        "type: CLAIM\n"
        "seq: 3\n"
        "summary: Pricing change reduces churn\n"
        "status: active\n"
        "branch: b1\n"
        "branch_type: exclusive\n"
        "inputs:\n"
        "  - ref: goal\n"
        "    load_bearing: true\n",
    )
    _write(
        root / "assumptions" / "q4_budget_holds.md",
        "id: q4_budget_holds\n"
        "status: open\n"
        "statement: Q4 budget will not be cut\n"
        "breaks_if: Budget cut announced\n"
        "source: finance team\n"
        "branch: b1\n",
    )
    _write(
        root / "research" / "r1.md",
        "id: r1\n"
        "claim: Competitor X raised prices last quarter\n",
    )

    project = dag.load_project(root)

    assert len(project.nodes) == 4
    ids = {n.id for n in project.nodes}
    assert ids == {"goal", "fact1", "claim1", "r1"}

    by_id = {n.id for n in project.nodes}
    node_map = {n.id: n for n in project.nodes}

    goal = node_map["goal"]
    for field in NODE_FIELDS:
        assert hasattr(goal, field), f"Node missing field {field}"
    assert goal.type == "GOAL"
    assert goal.seq == 1
    assert goal.summary == "Ship v0"
    assert goal.status == "active"
    assert goal.path == root / "nodes" / "goal.md"

    fact = node_map["fact1"]
    assert fact.type == "FACT"
    assert fact.source == "internal survey"
    assert fact.quote == "5% monthly churn"

    claim = node_map["claim1"]
    assert claim.branch == "b1"
    assert claim.branch_type == "exclusive"
    assert len(claim.inputs) == 1
    assert claim.inputs[0].ref == "goal"
    assert claim.inputs[0].load_bearing is True

    research_node = node_map["r1"]
    assert research_node.type == "FACT"
    assert research_node.summary == "Competitor X raised prices last quarter"
    assert research_node.path == root / "research" / "r1.md"

    assert len(project.assumptions) == 1
    assumption = project.assumptions[0]
    for field in ASSUMPTION_FIELDS:
        assert hasattr(assumption, field), f"Assumption missing field {field}"
    assert assumption.id == "q4_budget_holds"
    assert assumption.status == "open"
    assert assumption.statement == "Q4 budget will not be cut"
    assert assumption.breaks_if == "Budget cut announced"
    assert assumption.source == "finance team"
    assert assumption.branch == "b1"
    assert assumption.path == root / "assumptions" / "q4_budget_holds.md"

    # sorted by seq then id determinism check
    node_ids_in_order = [n.id for n in project.nodes]
    assert node_ids_in_order[0] == "goal"


def test_node_schema_doc_names_every_field():
    schema_path = Path(__file__).resolve().parents[1] / "references" / "node-schema.md"
    assert schema_path.exists(), f"missing {schema_path}"
    text = schema_path.read_text(encoding="utf-8")
    for field in NODE_FIELDS + ASSUMPTION_FIELDS:
        assert field in text, f"node-schema.md missing field mention: {field}"
