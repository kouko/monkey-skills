"""Structural grep-test guarding the critic-verdict-gate addition to
writing-plans/SKILL.md's §Who runs the validator (Task 19,
docs/loom/plans/2026-07-18-loop-convergence-fixes.md).

writing-plans/SKILL.md is a prompt artifact, not executable code. Its
correctness here is the PRESENCE of an additional validate requirement
layered on top of the existing validate_spec_output.py structural-clean
check: consuming a change-folder now also requires
`mint_critic_verdict.py validate --critic completeness-critic` to exit
0 before the change-folder is trusted. Structural-clean (schema-valid
spec.md) and critic-fresh-and-passed (completeness-critic actually ran,
approved, and the covered files haven't drifted since) are two
DIFFERENT gates — passing one says nothing about the other, so both
must run.

Per-exit-code routing (mirrors loom-spec/scripts/mint_critic_verdict.py's
documented exit codes 0/2/3/4):
  - 2 = no verdict file, completeness-critic never ran -> route TO
    completeness-critic.
  - 3 = a fresh verdict exists and is NEEDS_REVISION, critic blocked ->
    route BACK to the spec-expansion writer (the critic already found
    problems; writing-plans cannot fix them).
  - 4 = stale (covered files edited since mint, or a --files divergence
    from what was recorded at mint time) -> re-run completeness-critic
    so it reviews the current bytes.

These checks assert on load-bearing PHRASES (intent), tolerant of
wording variation, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "writing-plans" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _who_runs_the_validator_section(text: str) -> str:
    low = text.lower()
    start = low.index("who runs the validator")
    # Section runs to the next top-level bold-header paragraph
    # ("**Scenario -> task mapping.**"), anchored on the full heading
    # phrase (not the bare word "scenario") because the critic-verdict
    # gate's own prose legitimately mentions "#### Scenario:" inline.
    end = low.index("scenario → task mapping", start + len("who runs the validator"))
    return text[start:end]


def test_additional_critic_verdict_validate_requirement_documented():
    """Consuming a change-folder additionally requires
    mint_critic_verdict.py validate exit 0 -- structural-clean alone
    (validate_spec_output.py) is not enough."""
    section = _who_runs_the_validator_section(_text())

    assert "mint_critic_verdict.py" in section, \
        "must name mint_critic_verdict.py as an additional required check"
    assert "validate" in section.lower(), \
        "must invoke the validate subcommand"
    assert "exit 0" in section.lower(), \
        "must state the exit-0 gate on the critic-verdict validate call"


def test_structural_clean_vs_critic_fresh_distinction_stated():
    """structural-clean (validate_spec_output.py) != critic-fresh-and-passed
    (mint_critic_verdict.py validate) -- the two gates check different
    things and neither subsumes the other."""
    section = _who_runs_the_validator_section(_text())
    low = section.lower()

    assert "structural-clean" in low or "structurally clean" in low, \
        "must name the structural-clean concept"
    assert "critic-fresh" in low or "fresh" in low, \
        "must name the critic-fresh concept as distinct from structural-clean"


def test_completeness_critic_named_in_validate_invocation():
    """The --critic value must be completeness-critic -- writing-plans
    consumes loom-spec's spec-expansion output, gated by
    completeness-critic's verdict, not design-critic's."""
    section = _who_runs_the_validator_section(_text())

    assert "completeness-critic" in section, \
        "must name --critic completeness-critic in the validate invocation"


def test_exit_2_routes_to_completeness_critic():
    """Exit 2 (no verdict file, critic never ran) routes TO
    completeness-critic."""
    section = _who_runs_the_validator_section(_text())
    low = section.lower()

    assert "2" in section, "must name exit code 2"
    assert "never ran" in low or "never-ran" in low, \
        "exit 2 must be described as critic-never-ran"
    assert "completeness-critic" in low, \
        "exit 2 routing must name completeness-critic as the target"


def test_exit_3_routes_back_to_spec_expansion_writer():
    """Exit 3 (fresh NEEDS_REVISION, critic blocked) routes BACK to the
    spec-expansion writer -- writing-plans cannot resolve critic
    findings itself."""
    section = _who_runs_the_validator_section(_text())
    low = section.lower()

    assert "3" in section, "must name exit code 3"
    assert "blocked" in low or "needs_revision" in low, \
        "exit 3 must be described as critic-blocked / NEEDS_REVISION"
    assert "spec-expansion" in low, \
        "exit 3 routing must name spec-expansion as the target to route back to"


def test_exit_4_reruns_completeness_critic():
    """Exit 4 (stale hash / --files divergence) re-runs completeness-critic
    against the current bytes."""
    section = _who_runs_the_validator_section(_text())
    low = section.lower()

    assert "4" in section, "must name exit code 4"
    assert "stale" in low, "exit 4 must be described as stale"
    assert "re-run" in low or "rerun" in low, \
        "exit 4 routing must state re-running completeness-critic"


def test_three_exit_codes_have_distinct_routings():
    """The three non-zero exit codes (2/3/4) must route to three
    DIFFERENT places -- collapsing them into one generic 'fix and retry'
    instruction would lose the routing information mint_critic_verdict.py
    encodes in its exit codes."""
    section = _who_runs_the_validator_section(_text())

    for code in ("2", "3", "4"):
        assert code in section, f"must name exit code {code} distinctly"


def test_files_list_must_match_what_critic_minted():
    """The --files list passed to validate must match what
    completeness-critic minted -- mint_critic_verdict.py's own validate
    path refuses (exit 4) on a --files divergence from the recorded
    list, and that divergence deserves its own diagnostic rather than
    being silently absorbed into the generic stale case."""
    section = _who_runs_the_validator_section(_text())
    low = section.lower()

    assert "--files" in section, "must name the --files flag"
    assert "match" in low or "diverg" in low, \
        "must state the --files list must match what the critic minted"
