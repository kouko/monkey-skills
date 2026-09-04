"""RED/GREEN evidence for W1-01 — review station text carries the small
change lane, the docs-lint clause, and consequence-based severity.

Three cheap string-presence assertions; they do not parse or execute the
prose, they only prove the three pieces of text this task adds actually
landed in the files the review station and its reviewer contract read.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_review_skill_md_documents_small_lane() -> None:
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    assert "small lane" in text


def test_review_skill_md_tests_only_is_name_or_location() -> None:
    """Branch-end fix: the small-lane 'tests only' class is name/location
    only (test_*.py, *_test.py, tests/ segment), never content-verified,
    and distinct from the §6 artifact-type table (which still maps a
    tests/-relocated production file to `code`)."""
    text = (REPO / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
    assert "name or location only" in text


def test_reviewer_agent_documents_docs_lint() -> None:
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    assert "docs-lint" in text


def test_lenses_severity_section_defines_act_wrongly() -> None:
    text = (REPO / "loom-code/skills/review/references/lenses.md").read_text(encoding="utf-8")
    start = text.index("## Severity and verdict")
    section = text[start:]
    assert "act wrongly" in section


def _you_own_paragraph(text: str) -> str:
    """Return the block whose first non-blank line starts `You own`."""
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [b for b in blocks if b.lstrip().startswith("You own")]
    assert hits, "no `You own` paragraph found"
    return hits[0]


def test_reviewer_agent_owns_reconciliation_paragraph_under_80_words() -> None:
    """W1-01: reviewer.md carries a `You own` positioning paragraph, <= 80
    words counted with `len(str.split())` (never `wc` — BSD/GNU disagree)."""
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert len(para.split()) <= 80


def test_adversary_agent_owns_negative_paragraph_under_80_words() -> None:
    """W1-01: adversary.md carries a `You own` positioning paragraph, <= 80
    words counted with `len(str.split())` (never `wc`)."""
    text = (REPO / "loom-code/agents/adversary.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert len(para.split()) <= 80


def test_reviewer_agent_paragraph_names_output_as_claim_fix_round_confirms() -> None:
    """Branch-end fix (branch-end-02): intent Proposed outcome 2 requires the
    reviewer positioning paragraph to say its output is a claim the fix
    round confirms, without raising the paragraph above the 80-word cap."""
    text = (REPO / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert "a claim the fix round confirms" in " ".join(para.split())
    assert len(para.split()) <= 80


def test_adversary_agent_paragraph_owns_probe_artifact_bookkeeping() -> None:
    """Branch-end fix (branch-end-01): cold-read trial 2 showed the class
    'same artifact recorded under two spellings/paths counted twice' was
    claimed by neither role. The adversary paragraph must claim a probe's
    own artifact path (spelling/count) while explicitly leaving a
    cross-document count to the reviewer, within the 80-word cap."""
    text = (REPO / "loom-code/agents/adversary.md").read_text(encoding="utf-8")
    para = _you_own_paragraph(text)
    assert "artifact path" in para
    assert "reviewer's" in para
    assert "cross-document" in para
    assert len(para.split()) <= 80


def test_fix_rounds_reader_finding_to_probe_sentence_under_60_words() -> None:
    """W1-01: fix-rounds.md gains a block naming `important`, the adversary,
    and a probe, <= 60 words counted with `len(str.split())`."""
    text = (
        REPO / "loom-code/skills/review/references/fix-rounds.md"
    ).read_text(encoding="utf-8")
    blocks = [b for b in text.split("\n\n") if b.strip()]
    hits = [
        b
        for b in blocks
        if "important" in b.lower()
        and "adversary" in b.lower()
        and "probe" in b.lower()
    ]
    assert hits, "no block naming `important` + adversary + probe found"
    assert len(hits[0].split()) <= 60


# --- W1-01: tool-preference passage in the four contracts + build ----------

_TOOL_PREFERENCE_ANCHOR = "apply_patch"
_TOOL_PREFERENCE_CONTRACTS = {
    "implementer": REPO / "loom-code/agents/implementer.md",
    "reviewer": REPO / "loom-code/agents/reviewer.md",
    "blind-runner": REPO / "loom-code/agents/blind-runner.md",
    "adversary": REPO / "loom-code/agents/adversary.md",
}
_BUILD_SKILL = REPO / "loom-code/skills/build/SKILL.md"


def _tool_preference_bullet(text: str) -> str:
    """The single list item naming `apply_patch`, continuation lines joined."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if _TOOL_PREFERENCE_ANCHOR in line and re.match(r"^\s*[-*]\s+", line):
            bullet = [line.strip()]
            j = i + 1
            while j < len(lines) and lines[j].strip() and re.match(r"^\s+\S", lines[j]):
                bullet.append(lines[j].strip())
                j += 1
            return " ".join(bullet)
    raise AssertionError(f"no list item names `{_TOOL_PREFERENCE_ANCHOR}`")


def test_four_contracts_carry_a_capped_tool_preference_passage() -> None:
    """W1-01: each of the four agent contracts names the host edit tool,
    `apply_patch`, and `sed -i`/heredoc, in <= 40 words (`len(str.split())`).
    """
    for name, path in _TOOL_PREFERENCE_CONTRACTS.items():
        bullet = _tool_preference_bullet(path.read_text(encoding="utf-8"))
        assert "sed -i" in bullet or "heredoc" in bullet, (
            f"{name}.md tool-preference passage never names sed -i/heredoc"
        )
        assert re.search(r"\bEdit\b|\bWrite\b", bullet), (
            f"{name}.md tool-preference passage never names the host edit tool"
        )
        words = len(bullet.split())
        assert words <= 40, f"{name}.md tool-preference passage is {words} words"


def test_tool_preference_passage_does_not_forbid_reading() -> None:
    """W1-01: the passage regulates writing only — no prohibition clause in
    it names a read/search tool."""
    prohibition = r"\b(?:never|not|no|don't|do not|avoid|instead of|rather than)\b"
    read_tools = (
        r"\bcat\b", r"\bgrep\b", r"\bhead\b", r"\btail\b", r"\bsed -n\b",
        r"\bripgrep\b", r"\brg\b", r"\bRead\b", r"\bGrep\b", r"\bGlob\b",
    )
    for name, path in _TOOL_PREFERENCE_CONTRACTS.items():
        bullet = _tool_preference_bullet(path.read_text(encoding="utf-8"))
        for clause in re.split(r"[;.]|--|—", bullet):
            if not re.search(prohibition, clause, re.IGNORECASE):
                continue
            for pattern in read_tools:
                assert not re.search(pattern, clause, re.IGNORECASE), (
                    f"{name}.md tool-preference passage forbids reading: "
                    f"{pattern!r} in clause {clause.strip()!r}"
                )


def test_build_tool_preference_matches_implementer_verbatim() -> None:
    """W1-01: build/SKILL.md's standing trap-guard copy of the passage is the
    same normalised string as agents/implementer.md's — two hand-maintained
    copies must not gain a third disagreement."""
    build = _tool_preference_bullet(_BUILD_SKILL.read_text(encoding="utf-8"))
    impl = _tool_preference_bullet(
        _TOOL_PREFERENCE_CONTRACTS["implementer"].read_text(encoding="utf-8")
    )
    build_norm = " ".join(re.sub(r"^[-*]\s+", "", build).split())
    impl_norm = " ".join(re.sub(r"^[-*]\s+", "", impl).split())
    assert build_norm == impl_norm, (
        "the tool-preference passage differs between build/SKILL.md and "
        f"agents/implementer.md:\n  build: {build_norm!r}\n  impl:  {impl_norm!r}"
    )
