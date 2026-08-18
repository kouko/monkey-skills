"""RED test for Task 2 — dag.py load_project() + node-schema.md.

@req: BI-1
@req: BI-2
@req: BI-3
"""
from __future__ import annotations

import subprocess
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


def test_load_project_records_non_dict_or_invalid_frontmatter_as_problems_instead_of_crashing(tmp_path):
    # @req: BI-1
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
        root / "nodes" / "list_frontmatter.md",
        "- a\n- b\n",
    )
    _write(
        root / "nodes" / "bad_yaml.md",
        "key: [unclosed\n",
    )

    project = dag.load_project(root)

    assert len(project.nodes) == 1
    assert project.nodes[0].id == "goal"
    assert len(project.problems) == 2

    problems_text = "\n".join(project.problems)
    assert "list_frontmatter.md" in problems_text
    assert "bad_yaml.md" in problems_text
    assert all("frontmatter:" in p for p in project.problems)


def _build_clean_project(root: Path) -> None:
    """A structurally-clean fixture: 4 nodes, no check violations."""
    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: active\n",
    )
    _write(
        root / "nodes" / "fact1.md",
        "id: fact1\n"
        "type: FACT\n"
        "seq: 2\n"
        "summary: Users churn at 5%\n"
        "status: active\n"
        "source: internal survey\n"
        "quote: \"5% monthly churn\"\n",
    )
    _write(
        root / "nodes" / "claim1.md",
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
        "claim: Competitor X raised prices last quarter\n"
        "seq: 4\n",
    )


def test_check_prints_one_line_per_structural_violation_and_is_silent_when_clean(tmp_path, capsys):
    # @req: BI-4
    dirty_root = tmp_path / "dirty"
    _write(
        dirty_root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: active\n",
    )
    _write(
        dirty_root / "nodes" / "claim1.md",
        "id: claim1\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: Pricing change reduces churn\n"
        "status: active\n"
        "inputs:\n"
        "  - ref: goal\n",  # missing load_bearing -> violation 1
    )
    _write(
        dirty_root / "nodes" / "claim2.md",
        "id: claim2\n"
        "type: CLAIM\n"
        "seq: 3\n"
        "summary: Second claim\n"
        "status: active\n"
        "inputs:\n"
        "  - ref: missing_id\n"  # dangling ref -> violation 2
        "    load_bearing: true\n",
    )
    _write(
        dirty_root / "nodes" / "fact1.md",
        "id: fact1\n"
        "type: FACT\n"
        "seq: 4\n"
        "summary: Users churn at 5%\n"
        "status: active\n"
        "source: internal survey\n",  # missing quote -> violation 3
    )

    dirty_mtimes_before = {
        p: p.stat().st_mtime_ns for p in sorted((dirty_root / "nodes").glob("*.md"))
    }

    rc = dag.main(["check", str(dirty_root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 1
    assert len(lines) == 3
    assert any("claim1.md" in ln and "load_bearing" in ln for ln in lines)
    assert any("claim2.md" in ln and "ref" in ln for ln in lines)
    assert any("fact1.md" in ln and "fact-source" in ln for ln in lines)

    dirty_mtimes_after = {
        p: p.stat().st_mtime_ns for p in sorted((dirty_root / "nodes").glob("*.md"))
    }
    assert dirty_mtimes_before == dirty_mtimes_after

    clean_root = tmp_path / "clean"
    _build_clean_project(clean_root)
    clean_mtimes_before = {
        p: p.stat().st_mtime_ns for p in sorted((clean_root / "nodes").glob("*.md"))
    }

    project = dag.load_project(clean_root)
    assert len(project.nodes) >= 4

    rc_clean = dag.main(["check", str(clean_root)])
    out_clean = capsys.readouterr().out

    assert rc_clean == 0
    assert out_clean == ""

    clean_mtimes_after = {
        p: p.stat().st_mtime_ns for p in sorted((clean_root / "nodes").glob("*.md"))
    }
    assert clean_mtimes_before == clean_mtimes_after


def test_break_marks_load_bearing_chain_stale_and_reports_weakened(tmp_path, capsys):
    # @req: BI-5
    root = tmp_path
    a1_fm = (
        "id: a1\n"
        "status: open\n"
        "statement: Q4 budget will not be cut\n"
        "breaks_if: Budget cut announced\n"
        "source: finance team\n"
    )
    n1_fm = (
        "id: n1\n"
        "type: CLAIM\n"
        "seq: 1\n"
        "summary: n1\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: a1\n"
        "    load_bearing: true\n"
    )
    n2_fm = (
        "id: n2\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: n2\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: a1\n"
        "    load_bearing: false\n"
    )
    n3_fm = (
        "id: n3\n"
        "type: CLAIM\n"
        "seq: 3\n"
        "summary: n3\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: n1\n"
        "    load_bearing: true\n"
    )
    n4_fm = (
        "id: n4\n"
        "type: CLAIM\n"
        "seq: 4\n"
        "summary: n4\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: n2\n"
        "    load_bearing: true\n"
    )

    a1_path = root / "assumptions" / "a1.md"
    n1_path = root / "nodes" / "n1.md"
    n2_path = root / "nodes" / "n2.md"
    n3_path = root / "nodes" / "n3.md"
    n4_path = root / "nodes" / "n4.md"

    _write(a1_path, a1_fm)
    _write(n1_path, n1_fm)
    _write(n2_path, n2_fm)
    _write(n3_path, n3_fm)
    _write(n4_path, n4_fm)

    files_before = {
        path: path.read_text(encoding="utf-8")
        for path in (a1_path, n1_path, n2_path, n3_path, n4_path)
    }

    rc = dag.main(["break", str(root), "a1"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 0
    assert "stale: n1,n3" in lines
    assert "weakened: n2,n4" in lines

    project_after = dag.load_project(root)
    by_id = {n.id: n for n in project_after.nodes}
    assumptions_by_id = {a.id: a for a in project_after.assumptions}

    assert assumptions_by_id["a1"].status == "broken"
    assert by_id["n1"].status == "stale"
    assert by_id["n3"].status == "stale"
    assert by_id["n2"].status == "current"
    assert by_id["n4"].status == "current"

    for path, before_text in files_before.items():
        after_text = path.read_text(encoding="utf-8")
        fm_before, body_before = dag.split_frontmatter(before_text)
        fm_after, body_after = dag.split_frontmatter(after_text)
        assert body_after == body_before

        fm_before_no_status = "\n".join(
            ln for ln in fm_before.splitlines() if not ln.startswith("status:")
        )
        fm_after_no_status = "\n".join(
            ln for ln in fm_after.splitlines() if not ln.startswith("status:")
        )
        assert fm_after_no_status == fm_before_no_status


def test_propagate_terminates_on_cycles_and_upgrades_weakened_to_stale():
    # @req: BI-5
    project = dag.Project(
        root=Path("/unused"),
        nodes=[
            dag.Node(
                id="n1",
                inputs=[
                    dag.Input(ref="a1", load_bearing=False),
                    dag.Input(ref="n2", load_bearing=False),
                ],
            ),
            dag.Node(id="n2", inputs=[dag.Input(ref="n1", load_bearing=False)]),
            dag.Node(
                id="n3",
                inputs=[
                    dag.Input(ref="a1", load_bearing=True),
                    dag.Input(ref="n1", load_bearing=False),
                ],
            ),
        ],
        assumptions=[dag.Assumption(id="a1")],
    )

    stale, weakened = dag.propagate(project, "a1")

    assert stale == ["n3"]
    assert weakened == ["n1", "n2"]


def test_break_preserves_crlf_line_endings_and_body_bytes(tmp_path):
    # @req: BI-5
    root = tmp_path
    a1_path = root / "assumptions" / "a1.md"
    n1_path = root / "nodes" / "n1.md"
    a1_path.parent.mkdir(parents=True, exist_ok=True)
    n1_path.parent.mkdir(parents=True, exist_ok=True)

    a1_bytes = b"---\r\nid: a1\r\nstatus: open\r\n---\r\nbody line 1\r\nbody line 2\r\n"
    n1_bytes = (
        b"---\r\nid: n1\r\ntype: CLAIM\r\nseq: 1\r\nsummary: n1\r\nstatus: current\r\n"
        b"inputs:\r\n  - ref: a1\r\n    load_bearing: true\r\n---\r\nnode body\r\n"
    )
    a1_path.write_bytes(a1_bytes)
    n1_path.write_bytes(n1_bytes)

    a1_body_before = a1_bytes.split(b"---\r\n", 2)[2]
    n1_body_before = n1_bytes.split(b"---\r\n", 2)[2]

    rc = dag.main(["break", str(root), "a1"])
    assert rc == 0

    a1_after = a1_path.read_bytes()
    n1_after = n1_path.read_bytes()

    assert b"status: broken\r\n" in a1_after
    assert a1_after.endswith(a1_body_before)

    assert b"status: stale\r\n" in n1_after
    assert n1_after.endswith(n1_body_before)

    # every line ending is CRLF -- no bare \n introduced anywhere
    assert a1_after.replace(b"\r\n", b"").find(b"\n") == -1
    assert n1_after.replace(b"\r\n", b"").find(b"\n") == -1


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def test_claims_lists_dependents_only_for_research_claims_changed_since_rev(tmp_path, capsys):
    # @req: BI-3
    root = tmp_path
    _write(
        root / "research" / "r1.md",
        "id: r1\n"
        "claim: Original claim about competitor pricing\n",
    )
    _write(
        root / "research" / "r2.md",
        "id: r2\n"
        "claim: Unrelated claim that never changes\n",
    )
    _write(
        root / "nodes" / "n1.md",
        "id: n1\n"
        "type: CLAIM\n"
        "seq: 1\n"
        "summary: Depends on r1\n"
        "status: active\n"
        "inputs:\n"
        "  - ref: r1\n"
        "    load_bearing: true\n",
    )
    _write(
        root / "nodes" / "n2.md",
        "id: n2\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: Depends on r2\n"
        "status: active\n"
        "inputs:\n"
        "  - ref: r2\n"
        "    load_bearing: true\n",
    )

    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "initial")

    rc_clean = dag.main(["claims", str(root), "--since", "HEAD"])
    out_clean = capsys.readouterr().out
    assert rc_clean == 0
    assert out_clean == ""

    _write(
        root / "research" / "r1.md",
        "id: r1\n"
        "claim: Updated claim about competitor pricing\n",
    )

    rc = dag.main(["claims", str(root), "--since", "HEAD"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 0
    assert len(lines) == 1
    assert lines[0] == "r1: claim changed → dependents: n1"
    assert "r2" not in lines[0]
    assert "n2" not in lines[0]
