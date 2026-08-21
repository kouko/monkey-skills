"""Mechanical oracle: no store/brief gate script may die on a traceback.

Five consecutive whole-branch review rounds on the
2026-08-21-dissolve-direction-layer arc each found a bare filesystem read
in this family — each time in the sibling the previous round's fix did
not reach. Round 3 guarded `check_queue_relation`, round 4 guarded
`check_north_star_link`, and round 5 found `check_onramp_choice` and
`backlog_index` still bare. Both round-5 reviewers independently
recommended the same remedy: stop finding these by hand.

This is that remedy, and it is deliberately BEHAVIOURAL rather than
syntactic. A grep for `read_text(` outside a `try:` block would be
cheaper, but it pins the shape of today's fix instead of the contract:
what a gate owes its operator is one actionable line and a nonzero exit,
however that is implemented. A guard placed at the CLI boundary rather
than at the read site would fail a syntactic check while satisfying the
contract perfectly.

The contract, for every case below:

    exit nonzero  AND  no "Traceback" on stderr  AND  the failure names
    the unreadable path.

The FAMILY is the four scripts that read the backlog store or a handoff
brief as their primary input. It is named explicitly rather than
derived, because no import edge selects exactly these four
(`check_onramp_choice.py` imports nothing from `backlog_index.py`).
`test_family_membership_is_complete` is the guard against that hand-list
going stale.

Stdlib only.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent

FAMILY = (
    "backlog_index.py",
    "check_onramp_choice.py",
    "check_queue_relation.py",
    "check_north_star_link.py",
)

_ENTRY = (
    "---\n"
    "name: 2026-08-01-an-entry\n"
    "description: A fixture entry.\n"
    "status: bet\n"
    "serves: the purpose\n"
    "---\n\n"
    "Body.\n"
)

_BRIEF = "## Queue relation\n\nunqueued — nothing to queue\n"


def _repo(tmp_path: Path) -> Path:
    """A minimal repo: a backlog store with one live entry, a brief, a
    PURPOSE.md and a KICKOFF-DEFAULTS.md — enough for every FAMILY script
    to reach its reads."""
    store = tmp_path / "docs" / "loom" / "backlog"
    store.mkdir(parents=True)
    (store / "2026-08-01-an-entry.md").write_text(_ENTRY, encoding="utf-8")
    (tmp_path / "docs" / "loom" / "PURPOSE.md").write_text(
        "Ship the thing.\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "loom" / "KICKOFF-DEFAULTS.md").write_text(
        "## On-ramp standing choices\n\n- none\n", encoding="utf-8"
    )
    (tmp_path / "brief.md").write_text(_BRIEF, encoding="utf-8")
    return tmp_path


# One case per read site: (script, repo-relative file to make unreadable,
# extra argv selecting the mode that reaches that read).
_ENTRY_REL = "docs/loom/backlog/2026-08-01-an-entry.md"

_CASES_BY_SCRIPT: dict[str, list[tuple[str, tuple[str, ...]]]] = {
    # Three read sites: iter_validated_entries (--validate / --ready),
    # find_violations (--validate), and the committed index (--check).
    "backlog_index.py": [
        (_ENTRY_REL, ("--validate",)),
        (_ENTRY_REL, ("--ready",)),
        ("docs/loom/BACKLOG.md", ("--check",)),
    ],
    "check_onramp_choice.py": [
        ("brief.md", ()),
        ("docs/loom/KICKOFF-DEFAULTS.md", ()),
    ],
    "check_queue_relation.py": [
        ("brief.md", ()),
        (_ENTRY_REL, ()),
    ],
    "check_north_star_link.py": [
        (_ENTRY_REL, ()),
        ("docs/loom/PURPOSE.md", ()),
    ],
}


def _argv(script: str, repo: Path, extra: tuple[str, ...]) -> list[str]:
    store = repo / "docs" / "loom" / "backlog"
    brief = repo / "brief.md"
    if script == "backlog_index.py":
        return [
            *extra,
            "--store", str(store),
            "--output", str(repo / "docs" / "loom" / "BACKLOG.md"),
        ]
    if script in ("check_onramp_choice.py", "check_queue_relation.py"):
        return [str(brief), "--repo-root", str(repo)]
    if script == "check_north_star_link.py":
        return [str(store)]
    raise AssertionError(f"no argv recipe for {script!r}")


_CASES = [
    (script, rel, extra)
    for script in FAMILY
    for rel, extra in _CASES_BY_SCRIPT[script]
]


@pytest.mark.skipif(
    os.geteuid() == 0,
    reason="root bypasses mode 000, so the unreadable case cannot be built",
)
@pytest.mark.parametrize("script,rel,extra", _CASES)
def test_unreadable_input_exits_loudly_without_a_traceback(
    script: str, rel: str, extra: tuple[str, ...], tmp_path: Path
) -> None:
    repo = _repo(tmp_path)
    target = repo / rel
    if not target.exists():
        target.write_text("stale generated content\n", encoding="utf-8")
    target.chmod(0o000)
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *_argv(script, repo, extra)],
            capture_output=True,
            text=True,
        )
    finally:
        target.chmod(0o644)

    combined = result.stdout + result.stderr
    assert result.returncode != 0, (
        f"{script} exited 0 on an unreadable {rel} — an unreadable input "
        f"must never read as an absent or clean one:\n{combined}"
    )
    assert "Traceback" not in result.stderr, (
        f"{script} died on a raw traceback instead of one actionable line "
        f"when {rel} was unreadable:\n{result.stderr}"
    )
    assert target.name in combined or str(target) in combined, (
        f"{script} failed without naming the unreadable path {target}:\n"
        f"{combined}"
    )


def test_family_membership_is_complete() -> None:
    """The hand-listed FAMILY must still be every non-test CLI script that
    reads the backlog store or a handoff brief. Derived from the source,
    so a new gate that skips this file fails here rather than shipping
    unguarded."""
    qualifying = set()
    for path in sorted(SCRIPTS.glob("*.py")):
        if path.name.startswith("test_"):
            continue
        source = path.read_text(encoding="utf-8")
        if "def main(" not in source:
            continue
        # Two structural signals, not a filename pattern: the store's own
        # module, anything that imports it (every store reader does), and
        # anything taking a handoff brief as argv.
        reads_the_store = (
            path.name == "backlog_index.py"
            or "from backlog_index import" in source
            or "import backlog_index" in source
        )
        reads_a_brief = '"brief_path"' in source
        if reads_the_store or reads_a_brief:
            qualifying.add(path.name)

    assert qualifying == set(FAMILY), (
        "FAMILY has drifted from the scripts that actually read the store or "
        f"a brief.\n  only in FAMILY: {sorted(set(FAMILY) - qualifying)}\n"
        f"  only in the source: {sorted(qualifying - set(FAMILY))}"
    )


@pytest.mark.parametrize("script", FAMILY)
def test_every_family_read_site_has_a_case(script: str) -> None:
    """Each `read_text(` call site in a FAMILY script must be covered by a
    case above. This is the leg that catches a NEW bare read: adding one
    without adding its case fails here, which is exactly how five review
    rounds each found a bare read in this family by hand."""
    source = (SCRIPTS / script).read_text(encoding="utf-8")
    read_sites = source.count(".read_text(")
    cases = len(_CASES_BY_SCRIPT[script])
    assert read_sites <= cases, (
        f"{script} has {read_sites} `.read_text(` call sites but only "
        f"{cases} unreadable-input cases in this file. Add the case for the "
        f"new read, then make it pass."
    )
