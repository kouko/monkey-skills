"""W0-05 / REQ-8 — the SessionStart injection must shrink to at most half
the pre-change baseline (plan §0: baseline 923fb84a = 5281 words, target
<= 2640) and must carry only the orientation a session cannot derive:
the station order, the three human decision points in plain words, a
pointer to the entry station's SKILL.md for the full summary table, and
the repo's KICKOFF-DEFAULTS lines when that file exists.

The measurement command is fixed by concept-model §11:
``bash loom-code/hooks/session-start </dev/null | wc -w`` with cwd = an
empty git repo. These tests run exactly that.

Station names and decision-point numbers are asserted against
``loom-code/contract/manifest.yaml`` — the hook derives them from the
manifest rather than carrying a second hand-typed copy.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "loom-code" / "hooks" / "session-start"
MANIFEST = REPO / "loom-code" / "contract" / "manifest.yaml"

WORD_CAP = 2640


@pytest.fixture(scope="module")
def manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def empty_repo(tmp_path_factory) -> Path:
    repo = tmp_path_factory.mktemp("empty-git-repo")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    return repo


def _run(cwd: Path) -> str:
    proc = subprocess.run(
        ["bash", str(HOOK)],
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def _context(stdout: str) -> str:
    payload = json.loads(stdout)
    return payload["hookSpecificOutput"]["additionalContext"]


def test_word_count_is_within_budget(empty_repo):
    assert len(_run(empty_repo).split()) <= WORD_CAP


def test_emits_the_canonical_and_defensive_context_keys(empty_repo):
    payload = json.loads(_run(empty_repo))
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert payload["hookSpecificOutput"]["additionalContext"]
    assert set(payload) == {"hookSpecificOutput", "additional_context", "additionalContext"}


def test_names_every_station_in_manifest_order(empty_repo, manifest):
    context = _context(_run(empty_repo))
    names = [s["name"] for s in manifest["stations"]]
    positions = [context.find(n) for n in names]
    assert all(p >= 0 for p in positions), dict(zip(names, positions))
    flow = [n for n in names if n != "maintain"]
    assert " → ".join(flow) in context
    assert "maintain" in context


def test_states_the_three_decision_points_in_plain_words(empty_repo):
    context = _context(_run(empty_repo))
    for marker in ("①", "②", "③"):
        assert marker in context, marker
    # plain-language content, not mechanism names
    assert "this is what I want" in context
    assert "product" in context  # ② is product-only


def test_points_at_the_entry_station_instead_of_inlining_the_table(empty_repo):
    context = _context(_run(empty_repo))
    assert "SKILL.md" in context
    assert "capture-intent" in context and "write-plan" in context
    # the summary table itself must NOT be inlined
    assert "|---" not in context


def test_kickoff_defaults_lines_are_injected_when_the_file_exists(empty_repo, tmp_path):
    repo = tmp_path / "repo-with-defaults"
    (repo / "docs" / "loom").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "docs" / "loom" / "KICKOFF-DEFAULTS.md").write_text(
        "# KICKOFF-DEFAULTS\n\n- second-vendor: codex — user picked (2026-09-02)\n"
        "- standing-docs: waived — spike repo (2026-09-02)\n",
        encoding="utf-8",
    )
    context = _context(_run(repo))
    assert "second-vendor: codex — user picked (2026-09-02)" in context
    assert "standing-docs: waived — spike repo (2026-09-02)" in context


def test_no_kickoff_section_when_the_file_is_absent(empty_repo):
    assert "KICKOFF-DEFAULTS" not in _context(_run(empty_repo))


def test_escape_hatch_still_returns_empty_context(empty_repo):
    proc = subprocess.run(
        ["bash", str(HOOK)],
        cwd=str(empty_repo),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        env={**os.environ, "LOOM_CODE_MODE": "off"},
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"] == ""


def test_no_deleted_mechanism_is_mentioned(empty_repo):
    context = _context(_run(empty_repo))
    for gone in ("router", "reception", "relay", "on-ramp", "waiver", "batch"):
        assert gone not in context.lower(), gone


if __name__ == "__main__":  # pragma: no cover - manual measurement helper
    sys.exit(pytest.main([__file__, "-q"]))


def test_a_decision_point_with_no_match_does_not_abort_the_hook(tmp_path):
    """`set -e` kills the script when a command substitution's last command
    fails, and `grep` fails on no match -- so a manifest whose stations
    declare no decision point used to produce an empty injection instead of
    the station order. The lookup must tolerate the empty result."""
    plugin = tmp_path / "plugin"
    (plugin / "hooks").mkdir(parents=True)
    (plugin / "contract").mkdir()
    (plugin / "hooks" / "session-start").write_text(
        HOOK.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (plugin / "contract" / "manifest.yaml").write_text(
        "version: 1.0.0\n"
        "stations:\n"
        "  - {name: write-plan, owner: loom-code, produces: plan}\n"
        "  - {name: build,      owner: loom-code, produces: diff}\n"
        "  - {name: maintain,   owner: loom-code, produces: intent}\n",
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    proc = subprocess.run(
        ["bash", str(plugin / "hooks" / "session-start")],
        cwd=str(repo), stdin=subprocess.DEVNULL, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "write-plan" in _context(proc.stdout), proc.stdout
