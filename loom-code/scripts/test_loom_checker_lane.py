"""Executable contract for `declared_lane()` and the `lane:`/`default-lane:`
grammar (plan W1-01).

`declared_lane` is a pure function -- no subprocess needed, unlike the
`intent`-subcommand cases below which exercise the CLI the way
`test_loom_checker_intent.py` does. Fixtures reuse that module's
`make_repo`/`run_checker`/`git`/`blocked_rules` helpers rather than
re-deriving them (loom-code convention: one helper set per shape).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import loom_checker
from test_loom_checker_intent import (  # noqa: E402
    blocked_rules,
    git,
    make_repo,
    run_checker,
)

CHECKER = Path(__file__).with_name("loom_checker.py")


def _write_intent(repo: Path, change_id: str, *, lane_lines: tuple[str, ...] = ()) -> Path:
    """A schema-complete intent (every required field/section) with zero or
    more `lane:` lines inserted after `needs-design:` -- the LAST one wins,
    per `parse_document`'s frontmatter dict (it overwrites on each match),
    so declared_lane needs no extra "last wins" logic of its own."""
    lines = [
        f"# {change_id}",
        "originator: kouko",
        "kind: engineering",
        "needs-design: no — no interface surface touched",
        *lane_lines,
        "",
        "## Problem",
        "People doing this work want less verification for a light change.",
        "",
        "## Proposed outcome",
        "A declared lane.",
        "",
        "## Acceptance",
        "1. The declared lane is honoured.",
        "",
        "## Constraints",
        "- none",
        "",
        "## Out of scope",
        "- none",
        "",
        "## Open questions",
        "- none",
        "",
    ]
    path = repo / f"docs/loom/intent/{change_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_kickoff(repo: Path, *, default_lane: str | None = None) -> None:
    lines = ["# Kickoff Defaults", ""]
    if default_lane is not None:
        lines.append(f"- default-lane: {default_lane} — a repo default (2026-09-05)")
    (repo / "docs/loom/KICKOFF-DEFAULTS.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/loom/KICKOFF-DEFAULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# =============================================================================
# declared_lane() -- pure function, no subprocess.
# =============================================================================


def test_declared_lane_plain_intent_value(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x1"
    _write_intent(
        repo, change_id, lane_lines=("lane: express — declared 2026-09-05 by kouko",),
    )
    assert loom_checker.declared_lane(repo, change_id) == ("express", "intent", None, None)


def test_declared_lane_bare_name_is_not_legal_falls_back_to_default(tmp_path: Path) -> None:
    """A bare `lane: express`, with no dated-attribution suffix at all, is
    not a legal value (wave-end:1 adversary finding 1-01) -- `declared_
    lane` re-runs `check_lane_schema` itself and fails closed to the repo
    default rather than honouring it."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x1b"
    _write_intent(repo, change_id, lane_lines=("lane: express",))
    assert loom_checker.declared_lane(repo, change_id) == ("full", "default", None, None)


def test_declared_lane_switch_from_round(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x2"
    _write_intent(
        repo, change_id,
        lane_lines=("lane: express — switched 2026-09-05 by kouko, from round 2",),
    )
    assert loom_checker.declared_lane(repo, change_id) == ("express", "intent", 2, "round")


def test_declared_lane_switch_from_wave_has_no_round_number(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x3"
    _write_intent(
        repo, change_id,
        lane_lines=("lane: gate-only — switched 2026-09-05 by kouko, from wave 1",),
    )
    assert loom_checker.declared_lane(repo, change_id) == ("gate-only", "intent", None, "wave")


def test_declared_lane_last_line_wins(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x4"
    _write_intent(
        repo, change_id,
        lane_lines=(
            "lane: express — declared 2026-09-05 by kouko",
            "lane: gate-only — switched 2026-09-05 by kouko, from round 3",
        ),
    )
    assert loom_checker.declared_lane(repo, change_id) == ("gate-only", "intent", 3, "round")


def test_declared_lane_falls_back_to_kickoff_default(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x5"
    _write_intent(repo, change_id, lane_lines=())
    _write_kickoff(repo, default_lane="gate-only")
    assert loom_checker.declared_lane(repo, change_id) == ("gate-only", "kickoff", None, None)


def test_declared_lane_falls_back_to_full_with_nothing_declared(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-x6"
    _write_intent(repo, change_id, lane_lines=())
    assert loom_checker.declared_lane(repo, change_id) == ("full", "default", None, None)


def test_declared_lane_no_intent_file_falls_back_to_default(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    assert loom_checker.declared_lane(repo, "2026-09-05-nonexistent") == (
        "full", "default", None, None,
    )


# =============================================================================
# `intent` subcommand: schema and switch-line-verbatim-in-message rules.
# =============================================================================


def test_intent_lane_switch_missing_by_name_blocks_schema(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y1"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    lane_line = "lane: express — switched 2026-09-05, from round 2"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched\n"
        f"{lane_line}"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0
    assert "intent.schema" in blocked_rules(result)


def test_intent_lane_line_missing_from_commit_message_blocks(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y2"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write_intent(repo, change_id, lane_lines=("lane: express",))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0
    assert "intent.needs-design-reason" in blocked_rules(result)


def test_intent_lane_switch_with_by_name_and_verbatim_message_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y3"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    lane_line = "lane: express — switched 2026-09-05 by kouko, from round 2"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched\n"
        f"{lane_line}"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode == 0, result.stderr


def test_intent_no_lane_line_is_unaffected(tmp_path: Path) -> None:
    """No `lane:` line at all must never trip either new rule."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-y4"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write_intent(repo, change_id, lane_lines=())
    git(repo, "add", intent_rel)
    message = "docs(loom): add an intent\n\nneeds-design: no — no interface surface touched"
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode == 0, result.stderr


# =============================================================================
# `effective_lane_detail()` -- plan W1-02: recompute first, then the
# declared lane's own eligibility (gate-typed forces full always; a
# skill/agent-contract path forces gate-only back to full but never blocks
# express; a switch's `from_round` applies only to rounds strictly after
# it).
# =============================================================================


def _commit_all(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def test_effective_lane_recomputed_small_promoted_to_gate_only(tmp_path: Path) -> None:
    """Ratified follow-up (PRINCIPLES.md 56a4dc4c, intent 48114098):
    gate-only IS the small lane with the reader floor waived, not a
    separate, narrower thing -- a raw recompute of `small` PLUS a dated
    `lane: gate-only` declaration makes the effective lane `gate-only`
    (floor 0), not `small` (floor 1). This reverses the OLD invariant
    ("declared gate-only never matters once raw already says small") this
    test used to pin."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff1"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "loom-code/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/scripts/test_foo.py").write_text("def test_x(): pass\n", encoding="utf-8")
    reviewed_sha = _commit_all(repo, "test(loom-code): add a test file")

    assert (
        loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)[0]
        == "gate-only"
    )


def test_effective_lane_recomputed_small_stays_small_for_express(tmp_path: Path) -> None:
    """`express` is UNCHANGED by the ratification -- a raw recompute of
    `small` PLUS a declared `express` stays `small` (floor 1 either way);
    only `gate-only` gets promoted out of `small`."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff1b"
    lane_line = "lane: express — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "loom-code/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/scripts/test_foo.py").write_text("def test_x(): pass\n", encoding="utf-8")
    reviewed_sha = _commit_all(repo, "test(loom-code): add a test file")

    assert loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)[0] == "small"


def test_effective_lane_gate_typed_path_forces_full_whatever_declared(tmp_path: Path) -> None:
    """Declared `lane: express`, but the delta touches non-test code
    (`loom_checker.py` itself) -- that forces `full` whatever is declared,
    and the reason names the path."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff2"
    _write_intent(repo, change_id, lane_lines=("lane: express",))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")
    (repo / "loom-code/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/scripts/loom_checker.py").write_text("# extra\n", encoding="utf-8")
    reviewed_sha = _commit_all(repo, "feat(loom-code): touch the checker")

    lane, reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "full"
    assert "loom_checker.py" in reason


def test_effective_lane_express_needs_no_gate_path(tmp_path: Path) -> None:
    """Declared `lane: express` with a SKILL.md in the delta but no
    non-test-code/gate path -- express stays eligible; a skill path only
    matters to gate-only."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff3"
    lane_line = "lane: express — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "loom-code/skills/example").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/skills/example/SKILL.md").write_text(
        "---\nname: example\n---\nbody\n", encoding="utf-8"
    )
    reviewed_sha = _commit_all(repo, "docs(loom-code): a skill delta")

    lane, _reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "express"


def _write_standing_doc(repo: Path) -> None:
    """`docs/loom/KICKOFF-DEFAULTS.md` -- a standing document, which forces
    `change_lane_detail`'s own raw recompute to `full`. `_lane_forcing_
    paths`' own `kind == "standing"` exemption still keeps a standing-doc
    path out of its `hard` list, which is what express (unaffected by the
    ratified gate-only rule) relies on to stay eligible whenever raw is
    forced `full` by a standing document alone (adversary probe (i):
    `default-lane:` lives in this very file). Gate-only no longer reaches
    that exemption at all -- it is eligible only when the RAW recompute is
    already `small`, so ANY raw-`full` reason blocks it, standing document
    included (ratified follow-up, PRINCIPLES.md 56a4dc4c)."""
    path = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Kickoff Defaults\n", encoding="utf-8")


def test_effective_lane_gate_only_needs_raw_small_standing_doc_blocks(
    tmp_path: Path,
) -> None:
    """RETARGETED (ratified follow-up, PRINCIPLES.md 56a4dc4c): gate-only
    is eligible ONLY when the raw recompute is already `small` -- a
    standing-doc touch (`_write_standing_doc`) forces raw `full` for ANY
    reason at all, so the declared `lane: gate-only` is now ignored and
    the delta falls back to `full`, whatever the standing document itself
    is typed. The OLD invariant this test used to pin ("neither a docs
    nor a standing path is gate/skill-typed, so gate-only stays eligible")
    is exactly what the ratification reverses."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff4"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "docs/notes.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/notes.md").write_text("notes\n", encoding="utf-8")
    _write_standing_doc(repo)
    reviewed_sha = _commit_all(repo, "docs: a note")

    lane, reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "full"
    assert "small-lane delta" in reason


def test_effective_lane_gate_only_blocked_by_skill_path(tmp_path: Path) -> None:
    """Declared `lane: gate-only`, but a SKILL.md is in the delta -- a
    skill-typed path is not one of the raw recompute's small-lane types,
    so the raw recompute is already `full`, and gate-only (eligible only
    on raw `small`) falls back to `full` too, even though nothing
    non-test-code changed."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff5"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "loom-code/skills/example").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/skills/example/SKILL.md").write_text(
        "---\nname: example\n---\nbody\n", encoding="utf-8"
    )
    reviewed_sha = _commit_all(repo, "docs(loom-code): a skill delta")

    lane, reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "full"
    assert "SKILL.md" in reason


def test_effective_lane_switch_applies_only_strictly_after_from_round(tmp_path: Path) -> None:
    """A switch `from round 2` applies to round 3 (strictly after) but not
    to round 2 itself -- the pre-switch full lane still governs round 2."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff6"
    lane_line = "lane: express — switched 2026-09-05 by kouko, from round 2"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "docs/notes.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/notes.md").write_text("notes\n", encoding="utf-8")
    _write_standing_doc(repo)
    reviewed_sha = _commit_all(repo, "docs: a note")

    lane_after, _ = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 3)
    assert lane_after == "express"
    lane_at, _ = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 2)
    assert lane_at == "full"


# =============================================================================
# Provenance (wave-end:1-r3): the deciding commit for the `lane:` line must
# carry that exact line, verbatim, in its own message -- the same discipline
# `check_lane_reason` already enforces for the separate `intent` subcommand,
# now also verified by `effective_lane_detail` itself before honouring the
# declaration at push. RED at HEAD (before the fix): a declaration whose
# commit message never states the line is currently honoured anyway.
# =============================================================================


def test_effective_lane_declaration_ignored_when_commit_omits_it(tmp_path: Path) -> None:
    """A dated `lane: express` declaration whose deciding commit's message
    never states the line must be ignored -- the effective lane falls
    back to the raw recompute (a SKILL.md path forces `full`)."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff12"
    _write_intent(
        repo, change_id, lane_lines=("lane: express — declared 2026-09-05 by kouko",),
    )
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")  # omits the line
    (repo / "loom-code/skills/example").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/skills/example/SKILL.md").write_text(
        "---\nname: example\n---\nbody\n", encoding="utf-8"
    )
    reviewed_sha = _commit_all(repo, "docs(loom-code): a skill delta")

    lane, reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "full"
    assert "not stated" in reason


def test_effective_lane_declaration_honoured_when_commit_states_it(tmp_path: Path) -> None:
    """The mirror: the same declaration, but the deciding commit's message
    carries the line verbatim -- honoured, express stays eligible."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff13"
    lane_line = "lane: express — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "loom-code/skills/example").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/skills/example/SKILL.md").write_text(
        "---\nname: example\n---\nbody\n", encoding="utf-8"
    )
    reviewed_sha = _commit_all(repo, "docs(loom-code): a skill delta")

    lane, _reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "express"


def test_effective_lane_declaration_ignored_when_no_deciding_commit_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail closed: when `deciding_commit` cannot find a commit that
    changed the `lane:` line at all, the declaration is ignored the same
    way -- never trusted as if it needed no provenance."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff14"
    lane_line = "lane: express — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "loom-code/skills/example").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/skills/example/SKILL.md").write_text(
        "---\nname: example\n---\nbody\n", encoding="utf-8"
    )
    reviewed_sha = _commit_all(repo, "docs(loom-code): a skill delta")

    monkeypatch.setattr(loom_checker, "deciding_commit", lambda *a, **k: None)
    lane, reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "full"
    assert "not stated" in reason


def test_effective_lane_gateonly_declaration_ignored_when_commit_omits_it(
    tmp_path: Path,
) -> None:
    """The gate-only direction (follow-up adversary probe): an unstated
    `lane: gate-only` declaration on a raw-`small` delta must NOT be
    promoted -- provenance is unconditional, not scoped to `express`
    alone (an earlier version of this fix scoped it to express only,
    reasoning that only express widens the floor past the raw recompute;
    that missed that gate-only-from-small still drops floor 1 to 0, the
    more dangerous direction). The effective lane stays `small` (floor 1),
    not `gate-only` (floor 0)."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff15"
    _write_intent(
        repo, change_id,
        lane_lines=("lane: gate-only — declared 2026-09-05 by kouko",),
    )
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")  # omits the line
    (repo / "loom-code/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/scripts/test_foo.py").write_text("def test_x(): pass\n", encoding="utf-8")
    reviewed_sha = _commit_all(repo, "test(loom-code): add a test file")

    lane, reason = loom_checker.effective_lane_detail(repo, reviewed_sha, change_id, 1)
    assert lane == "small"
    assert "not stated" in reason


# =============================================================================
# `check_verdicts`' lane floor: full 2 / small 1 / express 1 / gate-only 0.
# =============================================================================


def _verdict(reviewer: str, round_: int, sha: str) -> dict:
    return {
        "reviewer": reviewer, "vendor": "anthropic", "model": "m", "lens": "docs",
        "verdict": "PASS", "dimension_scores": {}, "findings": [], "sha": sha,
        "round": round_, "scope": "branch-end",
    }


def test_check_verdicts_gate_only_floor_zero_passes_with_no_verdicts(tmp_path: Path) -> None:
    """A raw-small, docs-only delta (no standing-doc touch -- gate-only is
    eligible only when raw is `small`, ratified follow-up) with a dated
    `lane: gate-only` declaration waives the reader floor to 0."""
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff7"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "docs/notes.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/notes.md").write_text("notes\n", encoding="utf-8")
    reviewed_sha = _commit_all(repo, "docs: a note")

    review = {"scope": "branch-end", "verdicts": []}
    failures = loom_checker.check_verdicts(repo, review, reviewed_sha, set(), change_id)
    assert failures == []


def test_check_verdicts_express_floor_one_passes_with_one_reader(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff8"
    lane_line = "lane: express — declared 2026-09-05 by kouko"
    _write_intent(repo, change_id, lane_lines=(lane_line,))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", f"docs(loom): add the intent\n\n{lane_line}")
    (repo / "docs/notes.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/notes.md").write_text("notes\n", encoding="utf-8")
    reviewed_sha = _commit_all(repo, "docs: a note")

    review = {
        "scope": "branch-end",
        "verdicts": [_verdict("r1", 1, reviewed_sha)],
    }
    failures = loom_checker.check_verdicts(repo, review, reviewed_sha, set(), change_id)
    assert failures == []


def test_check_verdicts_full_floor_two_blocks_with_one_reader(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    change_id = "2026-09-05-eff9"
    (repo / "docs/notes.md").parent.mkdir(parents=True, exist_ok=True)
    (repo / "docs/notes.md").write_text("notes\n", encoding="utf-8")
    (repo / "loom-code/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/scripts/loom_checker.py").write_text("# extra\n", encoding="utf-8")
    reviewed_sha = _commit_all(repo, "feat(loom-code): touch the checker")

    review = {
        "scope": "branch-end",
        "verdicts": [_verdict("r1", 1, reviewed_sha)],
    }
    failures = loom_checker.check_verdicts(repo, review, reviewed_sha, set(), change_id)
    assert any(rule == "push.verdicts-ge-2" for rule, _ in failures)


def test_list_rules_verdicts_ge_2_names_four_floors() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    line = next(
        line for line in result.stdout.splitlines() if line.startswith("push.verdicts-ge-2\t")
    )
    for token in ("full", "small", "express", "gate-only"):
        assert token in line, f"push.verdicts-ge-2 description missing {token!r}: {line}"


# =============================================================================
# Rule count pin.
# =============================================================================


def test_list_rules_count_stays_thirty_one() -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 31, f"expected 31 rules, saw {len(lines)}:\n{result.stdout}"
