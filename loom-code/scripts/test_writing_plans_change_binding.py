"""Structural grep-test guarding the layered change-folder DETECTION cascade
in writing-plans/SKILL.md's §Consuming a loom-spec change-folder.

writing-plans/SKILL.md is a prompt artifact, not executable code. Its
correctness is the PRESENCE of the detection cascade (per
docs/loom/research/2026-07-10-change-binding-and-lifecycle-research.md
§Resolved decisions, and the 2026-07-10 post-PASS plan amendment):

- Layer 0: an explicitly handed change-folder path (conductor / caller
  names it) binds immediately — detection never runs.
- Layer (i): exact branch-slug match, opportunistic only — a miss falls
  through silently to layer (ii); when it DOES decide, the binding is
  surfaced explicitly; any ambiguity skips to the ask sub-step, never
  guesses.
- Layer (ii): non-archived change-folder count — 0 -> N/A loudly,
  1 -> auto-bind and state it, >1 -> ask, sorted by recency, with a
  recommended default. Never content-similarity matching.
- Once bound (any layer), consuming the change-folder is mandatory, not
  an optional alternate input alongside a separately-authored brief.
- A wrong-bind reversal trigger note: one real wrong-bind incident
  downgrades layer (i) from opportunistic-auto to confirm-before-use.

This test also asserts the OLD "second input contract / instead of a
brief" optional framing is GONE — the task replaces it, not supplements
it.

These checks assert on load-bearing PHRASES (intent), tolerant of
wording variation, so the test guards meaning without being brittle.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "writing-plans" / "SKILL.md"
AGENTS_MD = Path(__file__).parents[2] / "AGENTS.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def test_layer_0_explicit_handoff_wins():
    """An explicitly handed change-folder path binds immediately; detection
    (layers i/ii) never runs in that case."""
    text = _text()
    low = text.lower()

    assert "layer 0" in low, "must name Layer 0 explicitly"
    assert "explicit" in low, "layer 0 must be framed as the explicit-handoff case"
    assert "detection never runs" in low or "never runs" in low, \
        "must state that detection (layers i/ii) never runs once layer 0 binds"


def test_layer_i_branch_slug_opportunistic():
    """Layer (i) is exact branch-slug match, opportunistic only: silent
    fall-through on a miss, explicit surfacing when it decides, and any
    ambiguity routes to the ask layer rather than guessing."""
    text = _text()
    low = text.lower()

    assert "branch" in low, "layer (i) must be the branch-name layer"
    assert "opportunistic" in low, "layer (i) must be marked opportunistic-only"
    assert "silent" in low or "silently" in low, \
        "a miss on the branch layer must fall through silently"
    assert "ambigu" in low, \
        "ambiguity on the branch layer must be named and routed to the ask layer"


def test_layer_ii_count_based_fallback():
    """Layer (ii) resolves by non-archived change-folder count: 0 -> N/A
    loudly, 1 -> auto-bind + state it, >1 -> ask sorted by recency with a
    recommended default. Never content-similarity."""
    text = _text()
    low = text.lower()

    assert "n/a" in low, "count 0 must resolve to a loud N/A, never a silent skip"
    assert "auto-bind" in low or "auto bind" in low or "bind to" in low, \
        "count 1 must auto-bind"
    assert "recency" in low, ">1 must sort candidates by recency"
    assert "recommended default" in low, \
        ">1 must offer a recommended default rather than a bare list"
    assert "content-similarity" in low or "content similarity" in low, \
        "must explicitly rule out content-similarity matching"
    assert "never" in low, \
        "the content-similarity rule-out must be phrased as a hard never"


def test_mandatory_when_bound():
    """Once any layer binds a change-folder, consuming it is mandatory, not
    an optional alternate input alongside a separately-authored brief."""
    text = _text()
    low = text.lower()

    assert "mandatory" in low, \
        "must state that consuming a bound change-folder is mandatory"
    assert "not optional" in low or "no longer optional" in low, \
        "must explicitly rule out treating the bound change-folder as optional"


def test_wrong_bind_reversal_trigger_present():
    """A wrong-bind incident downgrades the branch layer from
    opportunistic-auto to confirm-before-use — the reversal trigger note
    from the research grounding must survive into the skill text."""
    text = _text()
    low = text.lower()

    assert "wrong-bind" in low or "wrong bind" in low, \
        "must name the wrong-bind reversal trigger"
    assert "confirm-before-use" in low or "confirm before use" in low, \
        "must state the downgrade target: confirm-before-use"


def test_old_optional_instead_of_a_brief_framing_is_gone():
    """The OLD 'second input contract / instead of a brief' optional
    framing must be REPLACED by the detection cascade, not left standing
    alongside it."""
    text = _text()
    low = text.lower()

    assert "second input contract" not in low, \
        "the old 'second input contract' framing must be removed"
    assert "instead of a brief" not in low, \
        "the old 'instead of a brief' optional framing must be removed"


def test_coverage_script_wired_after_scenario_mapping():
    """Task 12 wiring: after producing the plan, writing-plans runs
    check_scenario_coverage.py against the bound change-folder + plan;
    exit 1 blocks the plan from PASS until every scenario maps or the
    drop is explicitly user-approved and recorded in the plan's Notes."""
    text = _text()
    low = text.lower()

    assert "check_scenario_coverage.py" in text, \
        "must name the coverage script check_scenario_coverage.py"
    assert "exit 1" in low, \
        "must state the exit-1 (dropped scenario) semantics"
    assert "block" in low, \
        "exit 1 must be stated as blocking the plan from PASS"
    assert "user-approved" in low or "user approved" in low, \
        "must name the user-approved-drop escape hatch"
    assert "notes" in low, \
        "the user-approved drop must be recorded in the plan's Notes section"


def test_agents_md_declares_coverage_script():
    """Command-surface accretion obligation (Task 12): AGENTS.md's managed
    command-surface block must declare check_scenario_coverage.py so the
    new runnable verb has a declared entry point."""
    assert AGENTS_MD.is_file(), f"AGENTS.md is absent at {AGENTS_MD}"
    text = AGENTS_MD.read_text(encoding="utf-8")
    start = text.index("BEGIN command-surface (managed)")
    end = text.index("END command-surface (managed)")
    managed_block = text[start:end]
    assert "check_scenario_coverage.py" in managed_block, \
        "AGENTS.md managed command-surface block must declare check_scenario_coverage.py"


def test_existing_change_folder_contracts_still_present():
    """Sibling contracts in the same section that the task says to PRESERVE:
    validator trust-gate, scenario->task mapping, point-don't-copy,
    verbatim carve-out, WHAT-not-WHERE, consumer read-only."""
    text = _text()
    low = text.lower()

    assert "validate_spec_output" in text, "validator trust-gate must survive"
    assert "#### Scenario:" in text, "scenario marker must survive"
    assert "point-don't-copy" in low or "point-dont-copy" in low, \
        "point-don't-copy rule must survive"
    assert "verbatim" in low, "verbatim-copy carve-out must survive"
    assert "target repo" in low or "target-repo" in low, \
        "WHAT-not-WHERE target-repo recon must survive"
    assert "read-only" in low or "read only" in low, \
        "consumer read-only rule must survive"
