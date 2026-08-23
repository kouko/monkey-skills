"""Structural contract for loom-code's portable subagent dispatch profile.

The profile is a runtime instruction artifact: Claude Code and Codex both
read it immediately before their host-native spawn call.  These tests keep
the host-neutral policy, the two adapters, and every current dispatch station
bound together so a future station cannot silently revert to model inheritance
or a Codex-only TOML role configuration.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "skills" / "using-loom-code" / "references" / "dispatch-profile.md"

DISPATCH_STATIONS = (
    ROOT / "skills" / "subagent-driven-development" / "SKILL.md",
    ROOT / "skills" / "writing-plans" / "SKILL.md",
    ROOT / "skills" / "requesting-code-review" / "SKILL.md",
    ROOT / "skills" / "requesting-docs-review" / "SKILL.md",
    ROOT / "skills" / "dispatching-parallel-agents" / "SKILL.md",
    ROOT / "skills" / "finishing-a-development-branch" / "SKILL.md",
)


def _profile() -> str:
    assert PROFILE.is_file(), f"portable dispatch profile missing: {PROFILE}"
    return PROFILE.read_text(encoding="utf-8")


def test_profile_uses_semantic_tiers_and_has_no_vendor_as_its_ssot():
    text = _profile()

    assert "economy" in text
    assert "standard" in text
    assert "frontier" in text
    assert "low" in text and "medium" in text and "high" in text
    assert "never names a vendor model" in text


def test_profile_has_explicit_claude_and_codex_adapters():
    text = _profile()

    assert "## Claude Code adapter" in text
    assert "haiku" in text and "sonnet" in text and "opus" in text
    assert "effort" in text

    assert "## Codex adapter" in text
    assert "spawn_agent" in text
    assert "model" in text and "reasoning_effort" in text
    assert ".codex/agents" in text
    assert "not the loom dispatch mechanism" in text


def test_profile_fails_closed_for_frontier_and_bounds_other_fallbacks():
    text = _profile()

    assert "frontier" in text and "fail loud" in text
    assert "at most one retry" in text
    assert "must not silently downgrade" in text
    assert "unverified" in text and "halts the dispatch" in text


def test_every_dispatch_station_points_to_the_profile_before_spawning():
    expected_link = "dispatch-profile.md"

    for station in DISPATCH_STATIONS:
        text = station.read_text(encoding="utf-8")
        assert expected_link in text, (
            f"{station.relative_to(ROOT)} must link its dispatch instructions "
            "to the portable profile"
        )
        assert "Resolve the dispatch profile" in text, (
            f"{station.relative_to(ROOT)} must require profile resolution before "
            "its host-native spawn"
        )


def test_stations_do_not_keep_a_competing_host_model_policy():
    sdd = DISPATCH_STATIONS[0].read_text(encoding="utf-8")
    planning = DISPATCH_STATIONS[1].read_text(encoding="utf-8")
    code_review = DISPATCH_STATIONS[2].read_text(encoding="utf-8")
    docs_review = DISPATCH_STATIONS[3].read_text(encoding="utf-8")

    assert "Haiku / equivalent" not in sdd
    assert "Sonnet / equivalent" not in sdd
    assert "code-quality reviewer remains `frontier`" in sdd
    assert "Dispatch defaults to `model: sonnet`" not in planning
    assert "profile tier to `frontier`" in code_review
    assert "OPTIONAL `model` field to `opus`" not in code_review
    assert "legacy `OPTIONAL model`" not in docs_review
    assert "reviewer frontmatter only to supply" in docs_review


def test_codex_adapter_matches_the_current_one_child_lifecycle():
    codex_tools = (
        ROOT / "skills" / "using-loom-code" / "references" / "codex-tools.md"
    ).read_text(encoding="utf-8")

    assert "Each `spawn_agent` call creates one child" in codex_tools
    assert "wait explicitly for every result" in codex_tools
    assert "no loom procedure may require one" in codex_tools
    assert "`close_agent` when done" not in codex_tools
    assert "automatically once the spawn instruction names multiple agents" not in codex_tools


def test_profile_precedes_host_spawn_and_replaces_inheritance_evidence():
    codex_tools = (
        ROOT / "skills" / "using-loom-code" / "references" / "codex-tools.md"
    ).read_text(encoding="utf-8")
    evidence = (
        ROOT / "skills" / "requesting-code-review" / "references" / "design-evidence.md"
    ).read_text(encoding="utf-8")

    rebinding = codex_tools.index("### Re-binding loom-code's dispatch points")
    profile_resolution = codex_tools.index("resolve the portable profile first", rebinding)
    spawn = codex_tools.index("one `spawn_agent` call per role", rebinding)
    assert profile_resolution < spawn
    assert "Current dispatch\npolicy is the portable profile" in evidence
    assert "reviewers inherit the session model by design" not in evidence


def test_all_loom_agent_roles_supply_the_claude_standard_effort_baseline():
    for role in (
        "implementer.md",
        "spec-reviewer.md",
        "code-quality-reviewer.md",
        "code-reviewer.md",
        "docs-reviewer.md",
    ):
        text = (ROOT / "agents" / role).read_text(encoding="utf-8")
        assert "effort: medium" in text


def test_privacy_judges_are_frontier_high_profile_dispatches():
    closeout = DISPATCH_STATIONS[-1].read_text(encoding="utf-8")

    assert closeout.count("Resolve the dispatch profile") >= 2
    assert closeout.count("tier=frontier; effort=high") >= 2
