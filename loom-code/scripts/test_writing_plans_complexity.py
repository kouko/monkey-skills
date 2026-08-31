"""Contract test for writing-plans' architecture complexity assessment."""

from pathlib import Path


ROOT = Path(__file__).parent.parent
SKILL = ROOT / "skills" / "writing-plans" / "SKILL.md"
FORMAT = ROOT / "skills" / "writing-plans" / "references" / "plan-format.md"
REVIEWER = ROOT / "skills" / "writing-plans" / "references" / "plan-document-reviewer-prompt.md"
LENS = ROOT / "skills" / "writing-plans" / "references" / "architecture-complexity-lens.md"


def test_non_mechanical_plan_carries_architecture_complexity():
    """Non-mechanical plans record local architecture burden before SDD."""
    skill = SKILL.read_text(encoding="utf-8")
    plan_format = FORMAT.read_text(encoding="utf-8")
    reviewer = REVIEWER.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8")
    flat_lens = " ".join(lens.split())
    low_lens = lens.lower()
    low_flat_lens = flat_lens.lower()

    assert "references/architecture-complexity-lens.md" in skill
    assert "Complexity assessment" in plan_format
    assert "boundaries, dependencies, migrations, configuration" in flat_lens
    assert "operational duties, reuse, and deletion" in flat_lens
    assert "added complexity" in low_lens
    assert "why it is worthwhile" in low_lens
    assert "removed or avoided complexity" in low_lens
    assert "downstream risk" in low_lens
    assert "mechanical edit" in low_lens and "reasoned exemption" in low_lens
    assert "upstream evidence is absent" in low_flat_lens
    assert "required end state" in low_flat_lens
    assert "Complexity assessment" in reviewer
    assert "checks_passed: <N>/<21>" in reviewer


def _fenced_plans(text: str) -> list[str]:
    """Every ```markdown fence in the file that looks like a plan instance."""
    blocks, current = [], None
    for line in text.splitlines():
        if current is None:
            if line.strip() == "```markdown":
                current = []
            continue
        if line.strip() == "```":
            blocks.append("\n".join(current))
            current = None
            continue
        current.append(line)
    return [b for b in blocks if b.lstrip().startswith("# Plan:")]


def _slot_between_open_questions_and_task_1(plan: str) -> str:
    """The text a plan carries between Open Questions and its first task."""
    lines = plan.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Open Questions")
        end = next(
            i for i, l in enumerate(lines) if i > start and l.startswith("## Task 1")
        )
    except StopIteration:
        return ""
    return "\n".join(lines[start:end])


def test_plan_templates_carry_the_complexity_slot_they_mandate():
    """Every template a plan author copies satisfies the reviewer's Check 21.

    `plan-format.md` §Complexity assessment requires the section between
    `## Open Questions` and Task 1, and the reviewer prompt gates on it. A
    template that omits the slot teaches authors to produce plans that fail
    that gate, so the skeleton and every worked example must carry either the
    section or the schema's own mechanical-edit exemption line.
    """
    skill = SKILL.read_text(encoding="utf-8")
    plan_format = FORMAT.read_text(encoding="utf-8")

    skeleton_slot = _slot_between_open_questions_and_task_1(skill)
    assert skeleton_slot, "writing-plans/SKILL.md must show a plan skeleton"
    assert "## Complexity assessment" in skeleton_slot, (
        "the SKILL.md plan skeleton must show the `## Complexity assessment` slot "
        "between `## Open Questions` and Task 1"
    )

    plans = _fenced_plans(plan_format)
    assert plans, "plan-format.md must carry at least one worked plan example"
    for plan in plans:
        title = plan.splitlines()[0].strip()
        slot = _slot_between_open_questions_and_task_1(plan)
        if not slot:
            continue
        assert "## Complexity assessment" in slot or "mechanical edit:" in slot, (
            f"worked example {title!r} must carry `## Complexity assessment` or the "
            "schema's `N/A — mechanical edit:` exemption before Task 1"
        )


def test_skill_names_where_the_architecture_assessment_is_recorded():
    """The lens paragraph must name the section, not only the lens file.

    A plan author reading SKILL.md end to end otherwise learns to run the lens
    but not where its output belongs; the section name lives only in
    `plan-format.md`, which that paragraph did not reference.
    """
    skill = SKILL.read_text(encoding="utf-8")
    flat = " ".join(skill.split())
    marker = "architecture-complexity lens"
    assert marker in flat
    paragraph = flat[flat.index(marker) : flat.index(marker) + 500]
    assert "## Complexity assessment" in paragraph or "`## Complexity assessment`" in paragraph, (
        "the architecture-complexity paragraph must name the `## Complexity "
        "assessment` section it writes into"
    )


def test_check_21_reconciles_with_the_open_questions_hedge_scan():
    """Check 21's mandated section sits inside Check 18(b)'s scanned region.

    18(b) scans all prose outside `## Open Questions` for hedge vocabulary on a
    declared N/A, and its seed list is explicitly non-exhaustive, so a
    downstream-risk bullet phrased as an unresolved question trips it. Neither
    row said which wins; without that, an author cannot tell whether the two
    gates conflict or cooperate.
    """
    reviewer = REVIEWER.read_text(encoding="utf-8")
    flat = " ".join(reviewer.split())
    marker = "| 21 |"
    assert marker in flat
    row = flat[flat.index(marker) : flat.index(marker) + 1200]
    assert "18(b)" in row, (
        "Check 21 must say how its mandated section interacts with Check 18(b)'s "
        "hedge scan, which covers the region the section occupies"
    )
    assert "named risk" in row.lower(), (
        "Check 21 must tell the author to state downstream risk as a named risk "
        "rather than as an unresolved question"
    )


def test_complexity_exemption_is_distinguished_from_review_weight_mechanical():
    """`mechanical` names two different tests in one file; say which applies.

    §Complexity assessment exempts a plan by a trigger list (no boundary,
    dependency, migration, configuration, operational duty, or reuse), while
    `Review-weight: mechanical` may only be set for an identical or
    near-identical edit reproducible from an exact spec. The two disagree about
    the schema's own backfill example, and Check 21 fails a plan that "claims a
    mechanical exemption despite a non-mechanical task" — so the exemption must
    say which test it means.
    """
    plan_format = FORMAT.read_text(encoding="utf-8")
    flat = " ".join(plan_format.split())
    marker = "A plan consisting only of a mechanical edit may instead declare"
    assert marker in flat
    section = flat[flat.index(marker) : flat.index(marker) + 900]
    assert "Review-weight" in section, (
        "the complexity exemption must distinguish itself from the "
        "`Review-weight: mechanical` marker, which uses a stricter and "
        "differently-scoped eligibility test"
    )


def test_check_21_failure_column_is_plan_scoped_like_its_rule():
    """Check 21's two columns must judge the same thing.

    Its rule column exempts a mechanical-only *plan* by the schema's trigger
    list, while its failure column fired on a non-mechanical *task* — and the
    only definition of a mechanical task in that table is Check 16's
    identical-edit test. A reviewer grading the schema's own backfill example
    from the failure column returns a gap on a plan the rule declares legal.
    """
    reviewer = REVIEWER.read_text(encoding="utf-8")
    row = next(
        line for line in reviewer.splitlines() if line.startswith("| 21 |")
    )
    failure = row.rsplit("|", 2)[-2]
    assert "mechanical exemption" in failure, "Check 21 must still gate a false exemption"
    assert "non-mechanical task" not in failure, (
        "Check 21's failure column must not decide a plan-scoped exemption on a "
        "task-scoped reading of `mechanical` — Check 16 owns the task test"
    )
    assert "plan" in failure, "the failure column must name the plan-level test it applies"
