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

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent

# Filesystem calls from which an OSError can escape. `is_file`/`is_dir`/
# `exists` are included deliberately: an unreadable PARENT makes them raise
# PermissionError, and that exact case was a finding in two separate rounds
# of this arc's review — one of them fail-OPEN, because the unhandled raise
# was the only thing keeping an unreadable store out of an exit-0 branch.
_FS_CALLS = frozenset({
    "read_text", "write_text", "read_bytes", "write_bytes",
    "iterdir", "glob", "rglob", "mkdir", "stat",
    "is_file", "is_dir", "exists",
})

_OSERROR_SUPERSETS = frozenset({
    "OSError", "IOError", "EnvironmentError", "Exception", "BaseException",
})

# CLI scripts in this directory that are NOT store/brief gates. Listed with a
# reason so that classifying a new script is a decision, never an omission.
# Widening the fail-loud contract to cover these is filed as backlog work —
# they are exempt from the CONTRACT, not judged safe.
EXEMPT = {
    "adjudication_lint.py": "renders a document view; reads no store or brief",
    "adjudication_render.py": "renders a document view; reads no store or brief",
    "adjudication_split.py": "renders a document view; reads no store or brief",
    "archive_change_folder.py": "writes the store but is not a gate; its own "
                                "refusal contract is pinned in its own tests",
    "check_doc_citations.py": "checks prose citations, not the store",
    "check_field_microstructure.py": "checks field shape in a brief or plan, "
                                     "not the store",
    "check_open_questions.py": "checks a plan's Open Questions section",
    "check_scenario_coverage.py": "checks a change-folder's scenarios",
    "check-living-spec-index.py": "structural scan over docs/loom/, not the store",
    "check-skill-crossrefs.py": "checks skill cross-references",
    "distribute.py": "packaging helper",
    "loom_firing_harness.py": "probes skill firing; reads no store or brief",
    "loom_gate_markers.py": "mints and verifies gate markers",
    "review_scope.py": "resolves a review's changed-file set from git",
    "verify-drift.py": "compares two copies of a synced file",
    "loom_init.py": "scaffolds a new store; has no store to read yet",
    "plan_card.py": "reads plans, not the store",
}

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
    # One case per guard, not per verb. Round 6 mutation-tested every
    # `except OSError` in this family and found five survivors — three of
    # them here, including the `--write` output-write guard the commit
    # message singled out as newly added while its oracle never ran it.
    "backlog_index.py": [
        (_ENTRY_REL, ("--validate",)),
        (_ENTRY_REL, ("--ready",)),
        (_ENTRY_REL, ("--write",)),
        (_ENTRY_REL, ("--check",)),
        ("docs/loom/BACKLOG.md", ("--write",)),
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


def _guarded_line_ranges(tree: ast.AST) -> list[tuple[int, int]]:
    """Body line ranges of every `try:` whose handlers catch OSError (or a
    superset of it). A call inside one of these ranges is guarded."""
    ranges: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        catches = False
        for handler in node.handlers:
            if handler.type is None:
                catches = True
                continue
            names: list[str] = []
            if isinstance(handler.type, ast.Name):
                names = [handler.type.id]
            elif isinstance(handler.type, ast.Tuple):
                names = [e.id for e in handler.type.elts if isinstance(e, ast.Name)]
            if any(n in _OSERROR_SUPERSETS for n in names):
                catches = True
        if catches:
            for stmt in node.body:
                ranges.append((stmt.lineno, getattr(stmt, "end_lineno", stmt.lineno)))
    return ranges


def leaky_functions(source: str) -> set[str]:
    """Every module-level function from which an `OSError` can escape.

    A function is leaky when it makes an unguarded filesystem call, or when
    it calls another leaky function from outside a guarded `try`. Iterated to
    a fixpoint, so a guard placed anywhere up the call chain counts — which
    is the whole reason this is an AST analysis and not a grep. The syntactic
    check this replaces (`.read_text(` occurrences vs a case count) was
    proven non-load-bearing: two round-6 reviewers each injected a genuinely
    bare read and the suite stayed green.
    """
    tree = ast.parse(source)
    ranges = _guarded_line_ranges(tree)

    def guarded(lineno: int) -> bool:
        return any(lo <= lineno <= hi for lo, hi in ranges)

    funcs = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    leaky: set[str] = set()
    changed = True
    while changed:
        changed = False
        for name, fn in funcs.items():
            if name in leaky:
                continue
            for node in ast.walk(fn):
                if not isinstance(node, ast.Call) or guarded(node.lineno):
                    continue
                func = node.func
                escapes = (
                    (isinstance(func, ast.Attribute) and func.attr in _FS_CALLS)
                    or (isinstance(func, ast.Name) and func.id == "open")
                    or (isinstance(func, ast.Name) and func.id in leaky)
                )
                if escapes:
                    leaky.add(name)
                    changed = True
                    break
    return leaky


@pytest.mark.parametrize("script", FAMILY)
def test_no_oserror_can_escape_main(script: str) -> None:
    """The load-bearing completeness leg: `OSError` must not be able to
    reach the top of any gate script.

    This replaces a leg that counted `.read_text(` occurrences against a
    case count. Both round-6 reviewers independently defeated that one by
    injecting a bare read into a script that had slack in its count — the
    headline mechanism telling the next round it could stop looking, on
    exactly the defect class it was built for. Counting occurrences was
    never going to work; reachability is the property that matters.

    Note this is a COMPANION to the behavioural cases above, not a
    replacement. This leg proves nothing escapes; the behavioural cases
    prove the operator gets something they can act on. Neither implies the
    other: a bare `except OSError: pass` would satisfy this leg and fail
    every case above.
    """
    source = (SCRIPTS / script).read_text(encoding="utf-8")
    leaky = leaky_functions(source)
    assert "main" not in leaky, (
        f"an OSError can escape {script}'s main() — the operator gets a raw "
        f"traceback instead of one actionable line. Leaky call chain reaches: "
        f"{sorted(leaky)}"
    )


def test_every_cli_script_is_classified() -> None:
    """No script joins the family silently.

    The leg this replaces derived membership from `import backlog_index` or
    an argv named `brief_path`. A round-6 reviewer defeated it by writing a
    plausible new gate that walks the store, reads entries bare, imports
    nothing and names its argv differently — 14/14 green. Structural signals
    guess at intent; this asks instead that every CLI script in this
    directory be a decision someone made. A new script fails here until it
    is either put in FAMILY (and given cases) or exempted with a reason.
    """
    classified = set(FAMILY) | set(EXEMPT)
    actual = {
        path.name
        for path in sorted(SCRIPTS.glob("*.py"))
        if not path.name.startswith("test_")
        and "def main(" in path.read_text(encoding="utf-8")
    }
    unclassified = actual - classified
    assert not unclassified, (
        "these CLI scripts are neither in FAMILY (gets unreadable-input "
        "cases) nor in EXEMPT (with a stated reason): "
        f"{sorted(unclassified)}. Classify each one — a gate that reads a "
        "store or a brief belongs in FAMILY."
    )
    stale = classified - actual - {"__none__"}
    assert not stale, f"classified but no longer present: {sorted(stale)}"
