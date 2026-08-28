"""Structural contract for loom-code's portable subagent dispatch profile.

The profile is a runtime instruction artifact: Claude Code and Codex both
read it immediately before their host-native spawn call.  These tests keep
the host-neutral policy, the two adapters, and every current dispatch station
bound together so a future station cannot silently revert to model inheritance
or a Codex-only TOML role configuration.
"""
import re
from pathlib import Path

from heading_window import line_leading as _line_leading

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


def _section(text: str, heading: str) -> str:
    """Window from `heading` to the next `## ` heading (or end of file).

    Keeps mechanism/keyword pins scoped to the section that actually
    governs them, instead of matching anywhere in the whole profile --
    a whole-file match is a false green if the rule moves or is deleted
    from its governing section but the bare words survive elsewhere.
    """
    # Anchor at a line start so a same-named `###` subheading earlier in
    # the file can't retarget this window (a bare substring match would).
    start = _line_leading(text, heading)
    assert start != -1, f"expected an {heading!r} heading"
    rest = text[start + len(heading):]
    next_heading = re.search(r"\n## ", rest)
    end = start + len(heading) + (next_heading.start() if next_heading else len(rest))
    return text[start:end]


def _intro_window(text: str) -> str:
    """Window from the top of the file to the first `## ` heading."""
    first_heading = re.search(r"\n## ", text)
    return text[: first_heading.start()] if first_heading else text


def test_profile_uses_semantic_tiers_and_has_no_vendor_as_its_ssot():
    text = _profile()

    assert "economy" in text
    assert "standard" in text
    assert "frontier" in text
    assert "low" in text and "medium" in text and "high" in text
    assert "never names a vendor model" in _intro_window(text), (
        "the vendor-neutral SSOT policy must be stated in the profile's "
        "opening statement, not merely present somewhere in the file"
    )


def test_profile_has_explicit_claude_and_codex_adapters():
    text = _profile()

    assert "## Claude Code adapter" in text
    assert "haiku" in text and "sonnet" in text and "opus" in text
    assert "effort" in text

    assert "## Codex adapter" in text
    codex_section = _section(text, "## Codex adapter")
    assert "spawn_agent" in codex_section
    assert "model" in codex_section and "reasoning_effort" in codex_section
    assert ".codex/agents" in codex_section
    assert "not the loom dispatch mechanism" in codex_section, (
        "the disclaimer that a Codex TOML role is not loom's dispatch "
        "mechanism must live inside the Codex adapter section"
    )


def test_profile_fails_closed_for_frontier_and_bounds_other_fallbacks():
    text = _profile()
    fallback_section = _section(text, "## Failure and fallback policy")

    assert "frontier" in fallback_section and "fail loud" in fallback_section
    assert "at most one retry" in fallback_section, (
        "the retry bound must live inside the failure-and-fallback policy section"
    )
    assert "must not silently downgrade" in fallback_section, (
        "the no-silent-downgrade rule must live inside the failure-and-fallback "
        "policy section"
    )
    assert "unverified" in fallback_section and "halts the dispatch" in fallback_section


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
    assert "inherits the main session's effort" in docs_review
    assert "resolved `tier` plus `effort`" not in docs_review
    assert "requested_effort` and `effective_effort" in docs_review


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

    rebinding = _line_leading(codex_tools, "### Re-binding loom-code's dispatch points")
    # _line_leading returns -1 rather than raising; a silent -1 would make the
    # two searches below start from the last character and pass vacuously.
    assert rebinding != -1, "expected a '### Re-binding' heading at a line start"
    profile_resolution = codex_tools.index("resolve the portable profile first", rebinding)
    spawn = codex_tools.index("one `spawn_agent` call per role", rebinding)
    assert profile_resolution < spawn
    assert "Current dispatch\npolicy is the portable profile" in evidence
    assert "reviewers inherit the session model by design" not in evidence


def test_claude_roles_inherit_the_main_session_effort():
    for role in (
        "implementer.md",
        "spec-reviewer.md",
        "code-quality-reviewer.md",
        "code-reviewer.md",
        "docs-reviewer.md",
    ):
        text = (ROOT / "agents" / role).read_text(encoding="utf-8")
        assert "effort:" not in text

    profile = _profile()
    assert "inherits the main session's effort" in profile
    assert "must halt when high effort cannot be verified" not in profile
    assert "model-tier or runtime capability halts the dispatch" in profile
    assert "unverified effective effort halts" not in profile


def test_dispatch_record_separates_requested_and_effective_effort():
    profile = _profile()
    claude_tools = (
        ROOT / "skills" / "using-loom-code" / "references" / "claude-code-tools.md"
    ).read_text(encoding="utf-8")

    assert "requested_effort=<low|medium|high>" in profile
    assert "effective_effort: <host-applied value, inherited, or unverified>" in profile
    assert "requested_effort=<low|medium|high>; effective_effort=inherited" in claude_tools


def test_privacy_judges_request_high_effort_without_claiming_it_is_effective():
    closeout = DISPATCH_STATIONS[-1].read_text(encoding="utf-8")

    assert closeout.count("Resolve the dispatch profile") >= 2
    assert closeout.count("tier=frontier; requested_effort=high") >= 2
    assert "tier=frontier; effort=high" not in closeout
