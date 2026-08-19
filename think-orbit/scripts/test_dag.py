"""Tests for dag.py — the think-orbit project loader, gate, break/claims and views.

Covers load_project(), the `check` rules, assumption breaking with stale
propagation, the `claims` git diff, and the mermaid render/impact views.

brief-item: BI-1
brief-item: BI-2
brief-item: BI-3
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import dag


NODE_FIELDS = (
    "id", "type", "seq", "inputs", "summary", "status",
    "branch", "branch_type", "source", "quote", "path",
)
ASSUMPTION_FIELDS = (
    "id", "status", "statement", "breaks_if", "source", "branch", "path",
)


def _write(path: Path, frontmatter: str, body: str = "Body sentence one. Body sentence two.\n") -> None:
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
        "status: current\n",
    )
    _write(
        root / "nodes" / "fact.md",
        "id: fact1\n"
        "type: FACT\n"
        "seq: 2\n"
        "summary: Users churn at 5%\n"
        "status: current\n"
        "source: internal survey\n"
        "quote: \"5% monthly churn\"\n",
    )
    _write(
        root / "nodes" / "claim.md",
        "id: claim1\n"
        "type: CLAIM\n"
        "seq: 3\n"
        "summary: Pricing change reduces churn\n"
        "status: current\n"
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
    assert goal.status == "current"
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
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "skills" / "thinking-session" / "references" / "node-schema.md"
    )
    assert schema_path.exists(), f"missing {schema_path}"
    text = schema_path.read_text(encoding="utf-8")
    for field in NODE_FIELDS + ASSUMPTION_FIELDS:
        assert field in text, f"node-schema.md missing field mention: {field}"


def test_load_project_records_non_dict_or_invalid_frontmatter_as_problems_instead_of_crashing(tmp_path):
    # brief-item: BI-1
    root = tmp_path

    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
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
        "status: current\n",
    )
    _write(
        root / "nodes" / "fact1.md",
        "id: fact1\n"
        "type: FACT\n"
        "seq: 2\n"
        "summary: Users churn at 5%\n"
        "status: current\n"
        "source: internal survey\n"
        "quote: \"5% monthly churn\"\n",
    )
    _write(
        root / "nodes" / "claim1.md",
        "id: claim1\n"
        "type: CLAIM\n"
        "seq: 3\n"
        "summary: Pricing change reduces churn\n"
        "status: current\n"
        "branch: b1\n"
        "branch_type: exclusive\n"
        "inputs:\n"
        "  - ref: goal\n"
        "    load_bearing: true\n",
        body="This claim builds on goal. It changes pricing.\n",
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
    # brief-item: BI-4
    dirty_root = tmp_path / "dirty"
    _write(
        dirty_root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
    )
    _write(
        dirty_root / "nodes" / "claim1.md",
        "id: claim1\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: Pricing change reduces churn\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: goal\n",  # missing load_bearing -> violation 1
        body="This claim builds on goal. It changes pricing.\n",
    )
    _write(
        dirty_root / "nodes" / "claim2.md",
        "id: claim2\n"
        "type: CLAIM\n"
        "seq: 3\n"
        "summary: Second claim\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: missing_id\n"  # dangling ref -> violation 2
        "    load_bearing: true\n",
        body="This claim builds on missing_id. It is dangling.\n",
    )
    _write(
        dirty_root / "nodes" / "fact1.md",
        "id: fact1\n"
        "type: FACT\n"
        "seq: 4\n"
        "summary: Users churn at 5%\n"
        "status: current\n"
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


def test_check_flags_assumption_missing_breaks_if_and_more_than_three_per_branch(tmp_path, capsys):
    # brief-item: BI-2
    root = tmp_path
    _write(
        root / "nodes" / "claim_b1.md",
        "id: claim_b1\n"
        "type: CLAIM\n"
        "seq: 1\n"
        "summary: A claim on branch b1\n"
        "status: current\n"
        "branch: b1\n",  # gives b1 a node so branch-has-node stays silent here
    )
    _write(
        root / "assumptions" / "a1.md",
        "id: a1\n"
        "status: open\n"
        "statement: First assumption\n"
        "branch: b1\n",  # missing breaks_if -> violation 1
    )
    _write(
        root / "assumptions" / "a2.md",
        "id: a2\n"
        "status: open\n"
        "statement: Second assumption\n"
        "breaks_if: x\n"
        "branch: b1\n",
    )
    _write(
        root / "assumptions" / "a3.md",
        "id: a3\n"
        "status: open\n"
        "statement: Third assumption\n"
        "breaks_if: x\n"
        "branch: b1\n",
    )
    _write(
        root / "assumptions" / "a4.md",
        "id: a4\n"
        "status: open\n"
        "statement: Fourth assumption\n"
        "breaks_if: x\n"
        "branch: b1\n",  # 4 assumptions on b1 -> violation 2 (max 3)
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 1
    assert len(lines) == 2
    assert any("a1.md" in ln and "breaks_if" in ln for ln in lines)
    assert any("branch b1 has 4 assumptions (max 3)" in ln for ln in lines)


def test_check_flags_a_branch_carried_only_by_assumptions(tmp_path, capsys):
    # brief-item: BI-4 — a branch id present on assumptions but no node is a
    # violation; a branch with at least one node is silent; a project-wide
    # assumption (no `branch` key at all) is out of scope and never flagged.
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
    )
    # b_ok: carries a node -> silent
    _write(
        root / "nodes" / "claim_ok.md",
        "id: claim_ok\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: A claim on branch b_ok\n"
        "status: current\n"
        "branch: b_ok\n",
    )
    _write(
        root / "assumptions" / "a_ok.md",
        "id: a_ok\n"
        "status: open\n"
        "statement: Assumption backing b_ok\n"
        "breaks_if: x\n"
        "branch: b_ok\n",
    )
    # b_orphan: carries only an assumption, no node -> violation
    _write(
        root / "assumptions" / "a_orphan.md",
        "id: a_orphan\n"
        "status: open\n"
        "statement: Assumption with no supporting claim\n"
        "breaks_if: x\n"
        "branch: b_orphan\n",
    )
    # project-wide assumption: no `branch` key at all -> never flagged
    _write(
        root / "assumptions" / "a_wide.md",
        "id: a_wide\n"
        "status: open\n"
        "statement: Project-wide premise\n"
        "breaks_if: x\n",
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    branch_lines = [ln for ln in lines if "branch-has-node" in ln]
    assert rc == 1
    assert len(branch_lines) == 1
    assert "b_orphan" in branch_lines[0]
    assert not any("b_ok" in ln for ln in branch_lines)
    assert not any("a_wide" in ln for ln in branch_lines)


def test_check_flags_inputs_entry_without_ref(tmp_path, capsys):
    # brief-item: BI-4
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
    )
    _write(
        root / "nodes" / "claim1.md",
        "id: claim1\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: Pricing change reduces churn\n"
        "status: current\n"
        "inputs:\n"
        "  - load_bearing: true\n",  # no ref -> violation
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 1
    assert len(lines) == 1
    assert "claim1.md" in lines[0]
    assert "inputs[0] has no ref" in lines[0]


def test_check_flags_paragraphs_outside_two_to_four_sentences(tmp_path, capsys):
    # brief-item: BI-4
    dirty_root = tmp_path / "dirty"
    _write(
        dirty_root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
        body=(
            "第一句。第二句。第三句。第四句。第五句。第六句。\n"
            "\n"
            "This is one sentence.\n"
        ),
    )

    rc = dag.main(["check", str(dirty_root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 1
    assert len(lines) == 2
    assert any("goal.md" in ln and "paragraph 1 has 6 sentences" in ln for ln in lines)
    assert any("goal.md" in ln and "paragraph 2 has 1 sentences" in ln for ln in lines)

    clean_root = tmp_path / "clean"
    _write(
        clean_root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
        body=(
            "# Heading\n"
            "\n"
            "One sentence here. Two sentence here. Three sentence here.\n"
            "\n"
            "- item one\n"
            "- item two\n"
            "\n"
            "Another para. Second sentence. Third sentence.\n"
            "\n"
            "```mermaid\n"
            "flowchart TD\n"
            "  A --> B\n"
            "```\n"
        ),
    )

    rc2 = dag.main(["check", str(clean_root)])
    out2 = capsys.readouterr().out
    assert rc2 == 0
    assert out2 == ""


def test_count_sentences_ignores_abbreviations_urls_ellipses_and_inline_code():
    # brief-item: BI-4
    assert dag._count_sentences("See docs, e.g. the README. It has details.") == 2
    assert dag._count_sentences("Visit https://example.com/a.b.c for info. It works.") == 2
    assert dag._count_sentences("This trailed off... and continued.") == 1
    assert dag._count_sentences("Run `foo!` now. Then stop.") == 2


def test_count_sentences_ignores_title_abbreviations():
    # brief-item: BI-4
    text = (
        "We talked to Dr. Chen about the migration plan. "
        "She recommended waiting until Q3. "
        "This gives the team more runway. "
        "We agreed to revisit in September."
    )
    assert dag._count_sentences(text) == 4
    assert dag._count_sentences("Bring pens, paper, etc. to the meeting.") == 1
    assert dag._count_sentences("We packed pens, paper, etc.") == 1


def test_strip_fenced_blocks_handles_tilde_and_unclosed_fences():
    # brief-item: BI-4
    assert dag._strip_fenced_blocks("before\n~~~\ncode 1\ncode 2\n~~~\nafter\n") == "before\nafter\n"
    assert dag._strip_fenced_blocks("before\n```\ncode\nno close\n") == "before"


def test_check_flags_a_node_whose_body_names_none_of_its_inputs(tmp_path, capsys):
    # brief-item: BI-3
    # Spec revised mid-task after measurement against the real project (see
    # the plan's ## Notes): the summary-keyword arm passed 10/10 nodes,
    # including ones that never refer to any of their inputs, because
    # nodes on one reasoning chain are always about the same topic. Naming
    # the id is the only discriminator that reproduced the human reading.
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
    )
    _write(
        root / "nodes" / "fact1.md",
        "id: fact1\n"
        "type: FACT\n"
        "seq: 2\n"
        "summary: \u4f7f\u7528\u8005\u6d41\u5931\u7387\u4e0a\u5347\u5230 5%\n"
        "status: current\n"
        "source: internal survey\n"
        "quote: \"5% monthly churn\"\n",
    )
    _write(
        root / "nodes" / "claim_a.md",
        "id: claim_a\n"
        "type: CLAIM\n"
        "seq: 3\n"
        "summary: Unrelated claim\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n",
        body="Nothing here explains anything. This body mentions nothing.\n",
    )
    _write(
        root / "nodes" / "claim_b.md",
        "id: claim_b\n"
        "type: CLAIM\n"
        "seq: 4\n"
        "summary: Claim naming the input by id\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n",
        body="fact1 \u986f\u793a\u6d41\u5931\u7387\u4e0a\u5347\u3002\u9019\u9ede\u503c\u5f97\u6ce8\u610f\u3002\n",
    )
    _write(
        root / "nodes" / "claim_c.md",
        "id: claim_c\n"
        "type: CLAIM\n"
        "seq: 5\n"
        "summary: Claim paraphrasing the input's topic without naming it\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n",
        body="\u8fd1\u671f\u6d41\u5931\u60c5\u6cc1\u56b4\u91cd\u3002\u9700\u8981\u512a\u5148\u8655\u7406\u3002\n",
    )
    _write(
        root / "nodes" / "claim_d.md",
        "id: claim_d\n"
        "type: CLAIM\n"
        "seq: 6\n"
        "summary: Claim with no inputs at all\n"
        "status: current\n"
        "inputs: []\n",
    )
    _write(
        root / "nodes" / "claim_e.md",
        "id: claim_e\n"
        "type: CLAIM\n"
        "seq: 7\n"
        "summary: Claim naming its load-bearing input but not its weak one\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n"
        "  - ref: goal\n"
        "    load_bearing: false\n",
        body="This claim relies on fact1. It says nothing else.\n",
    )

    _write(
        root / "nodes" / "fact2.md",
        "id: fact2\n"
        "type: FACT\n"
        "seq: 8\n"
        "summary: Second fact\n"
        "status: current\n"
        "source: internal survey\n"
        "quote: \"second figure\"\n",
    )
    _write(
        root / "nodes" / "claim_f.md",
        "id: claim_f\n"
        "type: CLAIM\n"
        "seq: 9\n"
        "summary: Claim naming only one of several load-bearing inputs\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n"
        "  - ref: fact2\n"
        "    load_bearing: true\n"
        "  - ref: goal\n"
        "    load_bearing: true\n",
        body="This claim relies on fact1. It ignores the rest.\n",
    )
    _write(
        root / "nodes" / "claim_g.md",
        "id: claim_g\n"
        "type: CLAIM\n"
        "seq: 10\n"
        "summary: Claim whose inputs are all non-load-bearing and names none\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: false\n"
        "  - ref: goal\n"
        "    load_bearing: false\n",
        body="Nothing here explains anything, again. This body mentions nothing either.\n",
    )

    _write(
        root / "nodes" / "claim_h.md",
        "id: claim_h\n"
        "type: CLAIM\n"
        "seq: 11\n"
        "summary: Claim whose inputs are all non-load-bearing and names one\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: false\n"
        "  - ref: goal\n"
        "    load_bearing: false\n",
        body="This claim mentions fact1 even though it is not load-bearing. Context matters.\n",
    )
    _write(
        root / "nodes" / "claim_i.md",
        "id: claim_i\n"
        "type: CLAIM\n"
        "seq: 12\n"
        "summary: Claim naming its non-load-bearing input but not the load-bearing one\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n"
        "  - ref: goal\n"
        "    load_bearing: false\n",
        body="This claim rests entirely on goal. Nothing else matters here.\n",
    )
    _write(
        root / "nodes" / "claim_j1.md",
        "id: claim_j1\n"
        "type: CLAIM\n"
        "seq: 13\n"
        "summary: Claim discussing a longer id that shares a prefix with its input\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n",
        body="This claim rests entirely on fact10's finding that adoption doubled. That finding stands alone.\n",
    )
    _write(
        root / "nodes" / "claim_j2.md",
        "id: claim_j2\n"
        "type: CLAIM\n"
        "seq: 14\n"
        "summary: Claim naming its input immediately before CJK text with no space\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n",
        body="fact1\u7684\u8b49\u64da\u652f\u6301\u9019\u500b\u7d50\u8ad6\u3002\u7b2c\u4e8c\u53e5\u88dc\u5145\u8aaa\u660e\u3002\n",
    )

    _write(
        root / "nodes" / "claim_k1.md",
        "id: claim_k1\n"
        "type: CLAIM\n"
        "seq: 15\n"
        "summary: Claim discussing a kebab-case sibling id instead of its input\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: goal\n"
        "    load_bearing: true\n",
        body="This claim tracks goal-v2's rollout closely. Nothing else is discussed.\n",
    )
    _write(
        root / "nodes" / "claim_k2.md",
        "id: claim_k2\n"
        "type: CLAIM\n"
        "seq: 16\n"
        "summary: Claim naming its input at the end of an English sentence\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: fact1\n"
        "    load_bearing: true\n",
        body="This claim rests entirely on fact1. Nothing more to add.\n",
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    narration_lines = [ln for ln in lines if "input-narration" in ln]
    assert rc == 1
    assert len(narration_lines) == 6
    assert any("claim_a.md" in ln for ln in narration_lines)  # (a) names none -> violation
    assert not any("claim_b.md" in ln for ln in narration_lines)  # (b) names id in a sentence -> none
    assert any("claim_c.md" in ln for ln in narration_lines)  # (c) paraphrases topic without id -> violation (inverted from old spec)
    assert not any("claim_d.md" in ln for ln in narration_lines)  # (d) inputs: [] -> none
    assert not any("claim_e.md" in ln for ln in narration_lines)  # (e) names load-bearing, not the non-load-bearing one -> none
    assert not any("claim_f.md" in ln for ln in narration_lines)  # (f) names only ONE of several load-bearing inputs -> none
    assert any("claim_g.md" in ln for ln in narration_lines)  # (g) all inputs non-load-bearing, names none -> violation
    assert not any("claim_h.md" in ln for ln in narration_lines)  # (h) all inputs non-load-bearing, names one -> none
    assert any("claim_i.md" in ln for ln in narration_lines)  # (i) names non-load-bearing, load-bearing unnamed -> violation
    assert any("claim_j1.md" in ln for ln in narration_lines)  # (j) fact1 vs fact10 boundary -> violation
    assert not any("claim_j2.md" in ln for ln in narration_lines)  # (j) fact1 immediately before CJK, no space -> none
    assert any("claim_k1.md" in ln for ln in narration_lines)  # (k) goal-v2 kebab sibling, not goal itself -> violation
    assert not any("claim_k2.md" in ln for ln in narration_lines)  # (k) fact1 at end of an English sentence -> none


def test_input_narration_message_names_load_bearing_when_a_load_bearing_input_exists(tmp_path, capsys):
    """Counter-example the whole-branch reviewer proved by execution: a body
    that names a NON-load-bearing input (`bfact`) is still told it names
    "none of its inputs" and shown only the unrelated load-bearing candidate
    -- an author who re-reads their own body sees the id they wrote and
    concludes the gate is broken. The message must say `load-bearing` and
    list only the load-bearing candidates that went unnamed."""
    root = tmp_path
    _write(
        root / "nodes" / "afact.md",
        "id: afact\ntype: FACT\nseq: 1\nsummary: A fact\nstatus: current\n"
        "source: x\nquote: \"y\"\n",
    )
    _write(
        root / "nodes" / "bfact.md",
        "id: bfact\ntype: FACT\nseq: 2\nsummary: B fact\nstatus: current\n"
        "source: x\nquote: \"y\"\n",
    )
    _write(
        root / "nodes" / "claim1.md",
        "id: claim1\ntype: CLAIM\nseq: 3\nsummary: Test claim\nstatus: current\n"
        "inputs:\n"
        "  - {ref: afact, load_bearing: true}\n"
        "  - {ref: bfact, load_bearing: false}\n",
        body="This claim narrates bfact in its body, but never mentions the other one. It stands on prior work.\n",
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    narration_line = next(ln for ln in out.splitlines() if "input-narration" in ln)

    assert rc == 1
    assert narration_line == (
        "nodes/claim1.md: input-narration: body names none of its "
        "load-bearing inputs ['afact']"
    ), narration_line


def test_input_narration_message_omits_load_bearing_when_no_input_is_load_bearing(tmp_path, capsys):
    """The all-non-load-bearing fallback arm keeps the plain wording -- there
    is no load-bearing subset to name, so calling it that would be false too."""
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\ntype: GOAL\nseq: 1\nsummary: Ship v0\nstatus: current\n",
    )
    _write(
        root / "nodes" / "fact1.md",
        "id: fact1\ntype: FACT\nseq: 2\nsummary: A fact\nstatus: current\n"
        "source: x\nquote: \"y\"\n",
    )
    _write(
        root / "nodes" / "claim1.md",
        "id: claim1\ntype: CLAIM\nseq: 3\nsummary: Test claim\nstatus: current\n"
        "inputs:\n"
        "  - {ref: goal, load_bearing: false}\n"
        "  - {ref: fact1, load_bearing: false}\n",
        body="Nothing here explains anything. This body mentions nothing either.\n",
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    narration_line = next(ln for ln in out.splitlines() if "input-narration" in ln)

    assert rc == 1
    assert narration_line == (
        "nodes/claim1.md: input-narration: body names none of its "
        "inputs ['fact1', 'goal']"
    ), narration_line
    assert "load-bearing" not in narration_line


def test_check_lead_in_sentence_followed_by_list_is_not_a_paragraph_violation(tmp_path, capsys):
    # brief-item: BI-4
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
        body=(
            "Lead sentence one. Lead sentence two.\n"
            "- item 1\n"
            "- item 2\n"
            "- item 3\n"
            "- item 4\n"
            "- item 5\n"
        ),
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 0
    assert not any("paragraph-form" in ln for ln in lines)

def test_break_marks_load_bearing_chain_stale_and_reports_weakened(tmp_path, capsys):
    # brief-item: BI-5
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
    # brief-item: BI-5
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
    # brief-item: BI-5
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


def _git_commit_all(root: Path) -> None:
    """Init a git repo at `root` and commit everything written there so far."""
    for args in (
        ("init", "-q"),
        ("config", "user.email", "test@example.com"),
        ("config", "user.name", "Test"),
        ("add", "."),
        ("commit", "-q", "-m", "initial"),
    ):
        _git(root, *args)


def test_claims_lists_dependents_only_for_research_claims_changed_since_rev(tmp_path, capsys):
    # brief-item: BI-3
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
        "status: current\n"
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
        "status: current\n"
        "inputs:\n"
        "  - ref: r2\n"
        "    load_bearing: true\n",
    )

    _git_commit_all(root)

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


def test_claims_works_when_root_is_a_symlink_to_the_real_git_worktree(tmp_path, capsys):
    # brief-item: BI-3
    real_root = tmp_path / "real"
    _write(
        real_root / "research" / "r1.md",
        "id: r1\n"
        "claim: Original claim via symlinked root\n",
    )
    _write(
        real_root / "nodes" / "n1.md",
        "id: n1\n"
        "type: CLAIM\n"
        "seq: 1\n"
        "summary: Depends on r1\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: r1\n"
        "    load_bearing: true\n",
    )
    _git_commit_all(real_root)

    link_root = tmp_path / "link"
    os.symlink(real_root, link_root)

    _write(
        link_root / "research" / "r1.md",
        "id: r1\n"
        "claim: Updated claim via symlinked root\n",
    )

    rc = dag.main(["claims", str(link_root), "--since", "HEAD"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 0
    assert lines == ["r1: claim changed → dependents: n1"]


def test_claims_tolerates_invalid_utf8_bytes_in_historic_git_show_output(tmp_path, capsys):
    # brief-item: BI-3
    root = tmp_path
    root_dir = root / "research"
    root_dir.mkdir(parents=True, exist_ok=True)
    r1_path = root_dir / "r1.md"
    r1_path.write_bytes(
        b"---\nid: r1\nclaim: Old claim with invalid bytes\n---\n"
        b"body with an invalid byte: \xff\xfe\n"
    )

    _git_commit_all(root)

    _write(
        root / "research" / "r1.md",
        "id: r1\n"
        "claim: New claim, valid utf-8 only\n",
    )

    rc = dag.main(["claims", str(root), "--since", "HEAD"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 0
    assert lines == ["r1: claim changed → dependents: (none)"]


def test_claims_rejects_invalid_since_revision(tmp_path, capsys):
    # brief-item: BI-3
    root = tmp_path
    _write(root / "research" / "r1.md", "id: r1\nclaim: A claim\n")
    _git_commit_all(root)

    rc = dag.main(["claims", str(root), "--since", "not-a-real-rev"])
    err = capsys.readouterr().err

    assert rc == 1
    assert "invalid revision: not-a-real-rev" in err


def test_claims_treats_note_added_after_valid_rev_as_unchanged_new(tmp_path, capsys):
    # brief-item: BI-3
    root = tmp_path
    _write(root / "nodes" / "goal.md", "id: goal\ntype: GOAL\nseq: 1\nsummary: Ship v0\nstatus: current\n")
    _git_commit_all(root)

    _write(root / "research" / "r_new.md", "id: r_new\nclaim: Added after the rev\n")

    rc = dag.main(["claims", str(root), "--since", "HEAD"])
    out = capsys.readouterr().out

    assert rc == 0
    assert out == ""


def test_render_writes_full_dag_mermaid_with_branches_assumptions_and_stale_class(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    _build_clean_project(root)
    _write(
        root / "nodes" / "decision1.md",
        "id: decision1\n"
        "type: DECISION\n"
        "seq: 5\n"
        "summary: Go with the pricing change\n"
        "status: stale\n"
        "inputs:\n"
        "  - ref: claim1\n"
        "    load_bearing: false\n",
    )

    rc = dag.main(["render", str(root)])
    assert rc == 0

    out_path = root / "views" / "dag.md"
    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")

    lines = text.splitlines()
    assert lines[0] == "<!-- generated by dag.py render — regenerate, never hand-edit; agent must not read -->"
    assert "```mermaid" in text
    assert "flowchart TD" in text

    for node_id in ("goal", "fact1", "claim1", "r1", "decision1"):
        assert node_id in text
    assert "q4_budget_holds" in text

    assert "subgraph br_b1" in text
    assert text.count("-.->") == 1
    assert "classDef stale" in text
    assert "class" in text and "decision1" in text.split("classDef stale", 1)[1]

    rc2 = dag.main(["render", str(root)])
    assert rc2 == 0
    text2 = out_path.read_text(encoding="utf-8")
    assert text == text2


def test_render_disambiguates_colliding_mermaid_ids_and_check_flags_them(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    _write(
        root / "nodes" / "a1.md",
        "id: a-1\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: First\n"
        "status: current\n",
    )
    _write(
        root / "nodes" / "a2.md",
        "id: a_1\n"
        "type: GOAL\n"
        "seq: 2\n"
        "summary: Second\n"
        "status: current\n",
    )

    project = dag.load_project(root)

    check_lines = dag.check(project)
    collision_lines = [ln for ln in check_lines if "id-collision" in ln]
    assert len(collision_lines) == 1
    assert "a-1" in collision_lines[0]
    assert "a_1" in collision_lines[0]
    assert "a_1" in collision_lines[0].rsplit("both render as ", 1)[1]

    text = dag.render_dag(project)
    assert 'a_1{{"a-1<br/>First"}}' in text
    assert 'a_1_2{{"a_1<br/>Second"}}' in text


def test_render_empty_project_emits_placeholder(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    (root / "nodes").mkdir(parents=True)

    rc = dag.main(["render", str(root)])
    assert rc == 0

    text = (root / "views" / "dag.md").read_text(encoding="utf-8")
    assert "```mermaid" in text
    assert "flowchart TD" in text
    assert "%% no nodes yet" in text


def test_render_branch_with_assumptions_but_no_member_nodes_uses_unknown_branch_type(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship v0\n"
        "status: current\n",
    )
    _write(
        root / "assumptions" / "lonely.md",
        "id: lonely\n"
        "status: open\n"
        "statement: Nobody else is in this branch\n"
        "breaks_if: x\n"
        "branch: b9\n",
    )

    project = dag.load_project(root)
    text = dag.render_dag(project)

    assert 'subgraph br_b9 ["b9 (?)"]' in text


def test_render_truncates_long_labels_including_cjk(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    english_summary = "This English summary is deliberately written to exceed sixty characters total."
    cjk_summary = "這是一段刻意寫得很長的中文摘要文字用來測試截斷功能是否能正確處理多位元組字元不會爛掉喔這是重複的部分再加長一點確保超過六十個字元"
    assert len(english_summary) > 60
    assert len(cjk_summary) > 60

    _write(
        root / "nodes" / "goal.md",
        f"id: goal\ntype: GOAL\nseq: 1\nsummary: {english_summary}\nstatus: current\n",
    )
    _write(
        root / "nodes" / "fact1.md",
        f"id: fact1\ntype: FACT\nseq: 2\nsummary: {cjk_summary}\nstatus: current\n",
    )

    project = dag.load_project(root)
    text = dag.render_dag(project)

    assert english_summary not in text
    assert english_summary[:60] + "…" in text
    assert cjk_summary not in text
    assert cjk_summary[:60] + "…" in text


def test_render_escapes_angle_brackets_in_labels(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: \"Ship <v0> now\"\n"
        "status: current\n",
    )

    project = dag.load_project(root)
    text = dag.render_dag(project)

    assert "Ship #lt;v0#gt; now" in text
    assert "<v0>" not in text
    assert "goal<br/>Ship" in text


def test_render_escapes_special_characters_in_ids(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: 'q\"1<x>'\n"
        "type: GOAL\n"
        "seq: 1\n"
        "summary: Ship it\n"
        "status: current\n",
    )

    project = dag.load_project(root)
    text = dag.render_dag(project)

    assert "q#quot;1#lt;x#gt;<br/>Ship it" in text
    assert 'q"1<x>' not in text
    assert "<x>" not in text

    mermaid_ids = dag._mermaid_ids(project)
    node_mermaid_id = mermaid_ids['q"1<x>']
    assert node_mermaid_id == "q_1_x_"
    assert node_mermaid_id in text


def test_break_writes_impact_view_with_stale_dependents(tmp_path, capsys):
    # brief-item: BI-5
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

    _write(root / "assumptions" / "a1.md", a1_fm)
    _write(root / "nodes" / "n1.md", n1_fm)
    _write(root / "nodes" / "n2.md", n2_fm)
    _write(root / "nodes" / "n3.md", n3_fm)
    _write(root / "nodes" / "n4.md", n4_fm)

    rc = dag.main(["break", str(root), "a1"])
    assert rc == 0

    out_path = root / "views" / "impact-a1.md"
    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")

    lines = text.splitlines()
    assert lines[0] == "<!-- generated by dag.py impact — regenerate, never hand-edit; agent must not read -->"
    assert "```mermaid" in text
    assert "flowchart LR" in text

    for node_id in ("a1", "n1", "n3", "n2"):
        assert node_id in text

    assert "classDef stale" in text
    class_section = text.split("classDef stale", 1)[1]
    assert "n1" in class_section
    assert "n3" in class_section
    assert "n2 -.->" not in class_section  # class line itself must not reuse the dashed-edge text
    assert "n1,n3 stale" in text or ("n1" in class_section and "n3" in class_section)

    assert "-.->" in text  # weakened dependent (n2) drawn with a dashed edge

    rc2 = dag.main(["impact", str(root), "a1"])
    assert rc2 == 0
    text2 = out_path.read_text(encoding="utf-8")
    assert text == text2


def test_impact_unknown_assumption_errors_without_writing(tmp_path, capsys):
    # brief-item: BI-5
    root = tmp_path
    _write(
        root / "assumptions" / "a1.md",
        "id: a1\n"
        "status: open\n"
        "statement: Q4 budget will not be cut\n"
        "breaks_if: Budget cut announced\n"
        "source: finance team\n",
    )

    rc = dag.main(["impact", str(root), "nope"])
    err = capsys.readouterr().err

    assert rc == 1
    assert "assumption nope not found" in err
    assert not (root / "views" / "impact-nope.md").exists()


def test_check_flags_unknown_node_status(tmp_path, capsys):
    # brief-item: BI-1
    root = tmp_path
    _write(
        root / "nodes" / "ok.md",
        "id: ok\ntype: GOAL\nseq: 1\nsummary: Ship v0\nstatus: current\n",
    )
    _write(
        root / "nodes" / "implicit.md",
        "id: implicit\ntype: CLAIM\nseq: 2\nsummary: No status field\n",
    )
    _write(
        root / "nodes" / "bad.md",
        "id: bad\ntype: CLAIM\nseq: 3\nsummary: Wrong status\nstatus: active\n",
    )

    rc = dag.main(["check", str(root)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln]

    assert rc == 1
    assert "nodes/bad.md: node-status: 'active' not in ['current', 'stale']" in lines
    # A missing status is allowed — it means `current`.
    assert not any(ln.startswith("nodes/implicit.md: node-status") for ln in lines)
    assert not any(ln.startswith("nodes/ok.md: node-status") for ln in lines)


def _impact_fixture(root: Path) -> None:
    _write(
        root / "assumptions" / "a1.md",
        "id: a1\nstatus: open\nstatement: Customers refer\n"
        "breaks_if: Two asks declined\nbranch: b1\n",
    )
    _write(
        root / "nodes" / "n1.md",
        "id: n1\ntype: CLAIM\nseq: 1\nsummary: Referral scales\n"
        "status: current\ninputs:\n  - {ref: a1, load_bearing: true}\n",
    )


def test_break_and_impact_print_the_written_view_path(tmp_path, capsys):
    # brief-item: BI-5
    root = tmp_path
    _impact_fixture(root)

    assert dag.main(["break", str(root), "a1"]) == 0
    break_lines = [ln for ln in capsys.readouterr().out.splitlines() if ln]
    assert "impact view: views/impact-a1.md" in break_lines

    assert dag.main(["impact", str(root), "a1"]) == 0
    impact_lines = [ln for ln in capsys.readouterr().out.splitlines() if ln]
    assert "impact view: views/impact-a1.md" in impact_lines


def test_break_prints_the_sanitized_view_path_for_an_awkward_id(tmp_path, capsys):
    # brief-item: BI-5
    root = tmp_path
    _write(
        root / "assumptions" / "a.md",
        "id: a/b c\nstatus: open\nstatement: Awkward id\n"
        "breaks_if: Something observable\nbranch: b1\n",
    )

    assert dag.main(["break", str(root), "a/b c"]) == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln]

    assert "impact view: views/impact-a_b_c.md" in lines
    assert (root / "views" / "impact-a_b_c.md").exists()


def test_break_rewrites_files_whose_delimiter_line_has_trailing_whitespace(tmp_path):
    # brief-item: BI-5
    root = tmp_path
    a1_path = root / "assumptions" / "a1.md"
    n1_path = root / "nodes" / "n1.md"
    a1_path.parent.mkdir(parents=True, exist_ok=True)
    n1_path.parent.mkdir(parents=True, exist_ok=True)

    # the loader accepts any line that strips to `---`; so must the writer
    a1_path.write_text(
        "--- \n"
        "id: a1\n"
        "status: open\n"
        "statement: Q4 budget holds\n"
        "breaks_if: Budget cut announced\n"
        "--- \n"
        "Body one. Body two.\n",
        encoding="utf-8",
    )
    n1_path.write_text(
        "---\t\n"
        "id: n1\n"
        "type: CLAIM\n"
        "seq: 1\n"
        "summary: n1\n"
        "status: current\n"
        "inputs:\n"
        "  - ref: a1\n"
        "    load_bearing: true\n"
        "---\t\n"
        "Body one. Body two.\n",
        encoding="utf-8",
    )

    rc = dag.main(["break", str(root), "a1"])

    assert rc == 0
    assert "status: broken" in a1_path.read_text(encoding="utf-8")
    assert "status: stale" in n1_path.read_text(encoding="utf-8")


def test_break_fails_loud_when_a_target_file_has_no_frontmatter(tmp_path, capsys, monkeypatch):
    # brief-item: BI-5
    root = tmp_path
    a1_path = root / "assumptions" / "a1.md"
    n1_path = root / "nodes" / "n1.md"
    _write(
        a1_path,
        "id: a1\nstatus: open\nstatement: S\nbreaks_if: B\n",
    )
    n1_path.parent.mkdir(parents=True, exist_ok=True)
    n1_path.write_text("no frontmatter at all\n", encoding="utf-8")

    a1_before = a1_path.read_text(encoding="utf-8")

    def _fake_load_project(_root):
        return dag.Project(
            root=root,
            nodes=[
                dag.Node(
                    id="n1",
                    type="CLAIM",
                    seq=1,
                    summary="n1",
                    inputs=[dag.Input(ref="a1", load_bearing=True)],
                    path=n1_path,
                )
            ],
            assumptions=[dag.Assumption(id="a1", status="open", path=a1_path)],
        )

    monkeypatch.setattr(dag, "load_project", _fake_load_project)

    rc = dag.main(["break", str(root), "a1"])
    err = capsys.readouterr().err

    assert rc == 1
    assert "cannot rewrite frontmatter: nodes/n1.md" in err
    # no partial writes: the healthy target and the impact view are untouched
    assert a1_path.read_text(encoding="utf-8") == a1_before
    assert not (root / "views").exists()


def test_render_skips_idless_nodes_instead_of_crashing(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\ntype: GOAL\nseq: 1\nsummary: Ship v0\nstatus: current\n",
    )
    _write(
        root / "nodes" / "nameless.md",
        "type: CLAIM\nseq: 2\nsummary: No id at all\nstatus: current\n",
    )

    rc = dag.main(["render", str(root)])

    assert rc == 0
    text = (root / "views" / "dag.md").read_text(encoding="utf-8")
    assert "goal" in text
    assert "No id at all" not in text


def test_dag_module_reports_missing_pyyaml_plainly(capsys):
    def _failing_importer(name):
        raise ImportError(f"No module named {name!r}")

    with pytest.raises(SystemExit) as excinfo:
        dag._require_yaml(_failing_importer)

    assert excinfo.value.code == 2
    assert capsys.readouterr().err.strip() == (
        "think-orbit: PyYAML is required — pip install pyyaml"
    )


def test_check_flags_duplicate_id_without_an_id_collision_line(tmp_path, capsys):
    # brief-item: BI-4
    root = tmp_path
    _write(
        root / "nodes" / "first.md",
        "id: dup\ntype: GOAL\nseq: 1\nsummary: First\nstatus: current\n",
    )
    _write(
        root / "nodes" / "second.md",
        "id: dup\ntype: CLAIM\nseq: 2\nsummary: Second\nstatus: current\n",
    )

    rc = dag.main(["check", str(root)])
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln]

    assert rc == 1
    assert lines == [
        "nodes/second.md: duplicate-id: dup also declared in nodes/first.md"
    ]


def test_cli_no_longer_offers_a_load_subcommand():
    with pytest.raises(SystemExit) as excinfo:
        dag.main(["load"])

    assert excinfo.value.code != 0


def test_frontmatter_span_ignores_indented_dashes_inside_block_scalars(tmp_path, capsys):
    # brief-item: BI-1
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: g\ntype: GOAL\nseq: 1\nsummary: Ship v0\nstatus: current\n",
    )
    _write(
        root / "nodes" / "claim1.md",
        "id: c1\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: Depends on g\n"
        "status: current\n"
        "statement: |\n"
        "  ---\n"
        "  more text under the rule\n"
        "inputs:\n"
        "  - ref: g\n"
        "    load_bearing: true\n",
        body="This claim builds on g. It survives the block scalar.\n",
    )

    project = dag.load_project(root)
    claim = {n.id: n for n in project.nodes}["c1"]

    assert [(i.ref, i.load_bearing) for i in claim.inputs] == [("g", True)]

    rc = dag.main(["check", str(root)])
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_render_subgraph_ids_never_collide_with_node_ids_and_titles_are_escaped(tmp_path):
    # brief-item: BI-12
    root = tmp_path
    _write(
        root / "nodes" / "collides.md",
        "id: b1\ntype: GOAL\nseq: 1\nsummary: A node whose id equals a branch id\nstatus: current\n",
    )
    _write(
        root / "nodes" / "member.md",
        "id: m1\ntype: CLAIM\nseq: 2\nsummary: Member of the branch\nstatus: current\n"
        "branch: b1\nbranch_type: 'ex\"clusive'\n",
    )

    text = dag.render_dag(dag.load_project(root))

    assert '    subgraph br_b1 ["b1 (ex#quot;clusive)"]' in text
    assert 'b1{{"b1<br/>A node whose id equals a branch id"}}' in text
    assert 'ex"clusive' not in text


def test_load_project_records_non_utf8_file_as_problem(tmp_path):
    # brief-item: BI-1
    root = tmp_path
    bad_path = root / "nodes" / "bad.md"
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_bytes(b"---\nid: x\nsummary: \xff\xfe not utf-8\n---\nbody\n")

    project = dag.load_project(root)

    assert project.nodes == []
    assert project.problems == ["nodes/bad.md: frontmatter: not utf-8"]


def test_render_impact_rejects_an_unknown_assumption_id():
    # brief-item: BI-5
    project = dag.Project(root=Path("/unused"), assumptions=[dag.Assumption(id="a1")])

    with pytest.raises(KeyError):
        dag.render_impact(project, "nope")


# --- 0.1.2 dogfood fixes ---


def test_render_prints_the_view_path(tmp_path, capsys):
    """FINDING-007 — a silent `render` leaves the agent unable to tell the view
    was written without listing the folder; it prints one line like `impact`."""
    root = tmp_path
    _write(
        root / "nodes" / "goal.md",
        "id: goal\ntype: GOAL\nseq: 1\nsummary: Ship v0\nstatus: current\n",
    )

    rc = dag.main(["render", str(root)])

    assert rc == 0
    assert capsys.readouterr().out == "dag view: views/dag.md\n"


def test_project_wide_assumption_is_gate_clean_and_outside_the_per_branch_cap(tmp_path):
    """FINDING-005 — a pivotal premise governing several branches is filed
    project-wide (no `branch`), so the ≤3 cap of one branch cannot force it in."""
    root = tmp_path
    _write(
        root / "nodes" / "claim_b1.md",
        "id: claim_b1\n"
        "type: CLAIM\n"
        "seq: 1\n"
        "summary: A claim on branch b1\n"
        "status: current\n"
        "branch: b1\n",  # gives b1 a node so branch-has-node stays silent here
    )
    _write(
        root / "assumptions" / "checkpoint_go.md",
        "id: checkpoint_go\n"
        "status: open\n"
        "statement: The mid-quarter checkpoint still happens\n"
        "breaks_if: The checkpoint is cancelled\n",
        body="",
    )
    for i in range(3):
        _write(
            root / "assumptions" / f"a{i}.md",
            f"id: a{i}\n"
            "status: open\n"
            f"statement: Branch premise {i}\n"
            "breaks_if: It is contradicted in writing\n"
            "branch: b1\n",
            body="",
        )

    assert dag.check(dag.load_project(root)) == []


def test_render_places_a_project_wide_assumption_outside_every_subgraph(tmp_path):
    """FINDING-005 — the project-wide premise is drawn at top level, not inside
    the subgraph of whichever branch happened to cite it first."""
    root = tmp_path
    _write(
        root / "assumptions" / "checkpoint_go.md",
        "id: checkpoint_go\n"
        "status: open\n"
        "statement: The mid-quarter checkpoint still happens\n"
        "breaks_if: The checkpoint is cancelled\n",
        body="",
    )
    _write(
        root / "nodes" / "claim.md",
        "id: claim1\n"
        "type: CLAIM\n"
        "seq: 2\n"
        "summary: Branch A is viable\n"
        "status: current\n"
        "branch: b1\n"
        "branch_type: exclusive\n"
        "inputs:\n"
        "  - {ref: checkpoint_go, load_bearing: true}\n",
    )

    dag.main(["render", str(root)])
    lines = (root / "views" / "dag.md").read_text(encoding="utf-8").splitlines()

    assumption_line = next(i for i, l in enumerate(lines) if "checkpoint_go(" in l)
    subgraph_line = next(i for i, l in enumerate(lines) if l.strip().startswith("subgraph "))
    assert assumption_line < subgraph_line, (
        "a branch-less assumption must be drawn before (outside) every subgraph"
    )
