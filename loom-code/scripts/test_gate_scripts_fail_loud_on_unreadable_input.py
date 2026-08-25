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
    # pathlib.Path
    "read_text", "write_text", "read_bytes", "write_bytes", "open",
    "iterdir", "glob", "rglob", "mkdir", "rmdir", "touch", "unlink",
    "rename", "replace", "symlink_to", "hardlink_to", "samefile",
    "stat", "lstat", "chmod", "resolve", "readlink",
    # `is_file`/`is_dir`/`exists` are here for the same reason given above
    # the frozenset.
    "is_file", "is_dir", "exists", "is_symlink",
    # os / os.path / shutil, matched on the attribute name alone (so
    # `os.listdir`, `from os import listdir`, and an aliased import all
    # land the same way).
    "listdir", "scandir", "walk", "makedirs", "removedirs", "remove",
    "link", "readlink", "access", "getsize", "getmtime",
    "copy", "copy2", "copyfile", "copytree", "move", "rmtree",
})

# Builtins that touch the filesystem when called bare (not as an attribute).
_FS_BUILTINS = frozenset({"open"})

# Module-level code is always reachable — it runs at import.
_MODULE_SCOPE = "<module>"

_OSERROR_SUPERSETS = frozenset({
    "OSError", "IOError", "EnvironmentError", "Exception", "BaseException",
})

# Modules in this directory that are NOT store/brief gates. Listed with a
# reason so that classifying a new one is a decision, never an omission.
# They are exempt from the CONTRACT, not judged safe: the exact leaky count is
# leaky by this file's own metric today — see `exempt_leaks()` below, which
# computes the list rather than restating it. Widening the contract to cover them is filed
# at docs/loom/backlog/2026-08-21-fail-loud-contract-covers-only-the-four-
# store-brief-gates.md — an earlier revision of this comment claimed that
# filing before it existed, which is the same overclaim this file has now
# been caught in twice.
EXEMPT = {
    # Helper modules with no CLI at all (no `main`, no `__main__`). They
    # cannot be gates; their callers own the fail-loud contract.
    "adjudication_profiles.py": "helper module, no CLI entry point",
    "living_spec_collect.py": "helper module, no CLI entry point",
    "living_spec_drift.py": "helper module, no CLI entry point",
    "living_spec_gitref.py": "helper module, no CLI entry point",
    "living_spec_index.py": "helper module, no CLI entry point",
    "living_spec_tags.py": "helper module, no CLI entry point",
    "adjudication_lint.py": "renders a document view; reads no store or brief",
    "adjudication_render.py": "renders a document view; reads no store or brief",
    "adjudication_split.py": "renders a document view; reads no store or brief",
    "archive_change_folder.py": "writes the store but is not a gate; its own "
                                "refusal contract is pinned in its own tests",
    "check_doc_citations.py": "checks prose citations, not the store",
    "check_contract_citations.py": "checks prose citations, not the store",
    "check_field_microstructure.py": "checks field shape in a brief or plan, "
                                     "not the store",
    "check_open_questions.py": "checks a plan's Open Questions section",
    "check_scenario_coverage.py": "checks a change-folder's scenarios",
    "check_seam_coverage.py": "checks a plan's Seam field coverage against "
                              "its Dependencies edges",
    "check-living-spec-index.py": "structural scan over docs/loom/, not the store",
    "check-skill-crossrefs.py": "checks skill cross-references",
    "distribute.py": "packaging helper",
    "loom_firing_harness.py": "probes skill firing; reads no store or brief",
    "loom_gate_markers.py": "mints and verifies gate markers",
    "review_context.py": "resolves a review packet from local git and plugin files",
    "review_scope.py": "resolves a review's changed-file set from git",
    "live_gate_station_receipt.py": "writes a live-gate receipt; its own atomic "
                                    "refusal contract is pinned in its tests",
    "live_gate_adapter_probe.py": "exercises typed adapter refusals; its own "
                                  "executable contract is pinned in its tests",
    "live_host_review_gate.py": "orchestrates disposable host probes, not a "
                                "store or handoff-brief gate",
    "verify-drift.py": "compares two copies of a synced file",
    "loom_init.py": "scaffolds a new store; has no store to read yet",
    "plan_card.py": "reads plans, not the store",
    "post_pr_ci.py": "waits for GitHub PR checks, not the store or a brief",
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


def leaky_scopes(source: str) -> set[str]:
    """Every top-level scope from which an `OSError` can escape.

    A scope is leaky when it makes an unguarded filesystem call, or calls a
    leaky scope from outside a guarded `try`. Iterated to a fixpoint, so a
    guard placed anywhere up the call chain counts — which is why this is an
    AST analysis and not a grep, and why a guard at the CLI boundary is as
    good as one at the read site.

    ## What this DOES and does NOT catch

    Recognition is by CALLEE NAME (`_FS_CALLS`) plus the bare builtin
    `open`, so it sees `p.open()`, `os.listdir(...)`, `shutil.copy(...)` and
    an aliased import of any of them equally. Calls are attributed to their
    enclosing TOP-LEVEL scope, so a read inside a class method, a nested
    def, a lambda, or module-level code all count.

    It does NOT catch: a filesystem call reached through a variable holding
    a bound method (`f = p.read_text; f()`), a call whose callee name is
    none of the recognised ones (a third-party or newly-added stdlib I/O
    entry point), I/O performed by a C extension, or **I/O deferred past its
    call site** — a generator or a lazily-evaluated object constructed
    inside a guarded `try` but consumed outside it runs its body where it is
    consumed, and this leg credits the guard at construction. No FAMILY
    script contains a `yield` today, so that shape is latent rather than
    live; it is listed because a reviewer built it and the leg passed.

    It also does NOT catch a guard placed around a top-level helper whose
    body delegates the filesystem read to a symbol imported from another
    module — `leaky_scopes` parses one file at a time, so the delegate's
    leakiness never enters the caller file's AST. This shape is LIVE, not
    latent: `check_queue_relation.live_bet_names` and
    `check_north_star_link.find_bet_entries` both delegate today to
    `live_entries`, imported from `backlog_index` (filed at
    docs/loom/backlog/2026-08-21-leaky-scopes-cannot-see-a-guard-over-a-cross-module-delegating-helper.md).

    It can also FALSE-POSITIVE on an attribute call whose name collides with
    a recognised one (`obj.open()` on something that is not a path). That
    direction is safe — it demands a guard that is not needed, rather than
    missing one that is. Bare-name calls do not have this problem: a name
    this module defines itself takes priority over the recogniser set. Those remain the
    behavioural cases' job — and the honest statement of this leg's claim is
    "no RECOGNISED escape shape reaches `main`", not "no OSError can
    escape". The previous revision asserted the stronger sentence and a
    reviewer defeated it with a bare `path.open()` in one try.
    """
    tree = ast.parse(source)
    ranges = _guarded_line_ranges(tree)

    def guarded(lineno: int) -> bool:
        return any(lo <= lineno <= hi for lo, hi in ranges)

    # Local binding -> the name it was imported under, so
    # `from os import listdir as ls` makes `ls` recognised. Without this the
    # alias form escaped while the comment above claimed it did not — caught
    # by replaying a reviewer's own experiment one variant further than they
    # ran it.
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for spec in node.names:
                if spec.asname:
                    aliases[spec.asname] = spec.name.rsplit(".", 1)[-1]

    def recognised_name(identifier: str) -> bool:
        target = aliases.get(identifier, identifier)
        return target in _FS_BUILTINS or target in _FS_CALLS

    top_level = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    # Everything that is not a top-level def belongs to the module scope,
    # which is always reachable (it runs at import time).
    module_nodes = [
        node
        for node in tree.body
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    def calls_in(nodes) -> list[ast.Call]:
        found: list[ast.Call] = []
        for root in nodes:
            for node in ast.walk(root):
                if isinstance(node, ast.Call):
                    found.append(node)
        return found

    scopes: dict[str, list[ast.Call]] = {
        name: calls_in([fn]) for name, fn in top_level.items()
    }
    scopes[_MODULE_SCOPE] = calls_in(module_nodes)

    leaky: set[str] = set()
    changed = True
    while changed:
        changed = False
        for name, calls in scopes.items():
            if name in leaky:
                continue
            for node in calls:
                if guarded(node.lineno):
                    continue
                func = node.func
                escapes = (
                    (isinstance(func, ast.Attribute) and recognised_name(func.attr))
                    # A from-import (`from os import listdir`) produces an
                    # ast.Name, not an Attribute. An earlier revision tested
                    # only `_FS_BUILTINS` here and the comment above claimed
                    # from-imports and aliases "all land the same way" — a
                    # reviewer defeated it with `from os import listdir` in
                    # one try. Recognise the same name set either way, EXCEPT
                    # where the name is a function this module defines itself:
                    # `check_onramp_choice.resolve()` is a pure parser that
                    # collides with `Path.resolve`, and name-based recognition
                    # flagged it until local definitions were given priority.
                    # A locally defined name is handled by the `in leaky`
                    # branch below, which is the accurate treatment.
                    or (
                        isinstance(func, ast.Name)
                        and func.id not in top_level
                        and recognised_name(func.id)
                    )
                    or (isinstance(func, ast.Name) and func.id in leaky)
                    or (isinstance(func, ast.Attribute) and func.attr in leaky)
                )
                if escapes:
                    leaky.add(name)
                    changed = True
                    break
    return leaky


@pytest.mark.parametrize("script", FAMILY)
def test_no_recognised_oserror_escape_reaches_main(script: str) -> None:
    """The completeness leg: no RECOGNISED filesystem-call shape may reach
    the top of a gate script unguarded.

    Read `leaky_scopes`'s docstring for exactly what "recognised" covers and
    what it does not — the scope of the claim is part of the contract here,
    because two earlier revisions of this leg asserted more than they
    delivered and a reviewer defeated each in one try. This leg is a
    COMPANION to the behavioural cases above, never a replacement: it proves
    nothing recognised escapes, they prove the operator gets something
    actionable. `except OSError: pass` satisfies this leg and fails every
    one of them.
    """
    source = (SCRIPTS / script).read_text(encoding="utf-8")
    leaky = leaky_scopes(source)
    escaping = leaky & {"main", _MODULE_SCOPE}
    assert not escaping, (
        f"a recognised OSError escape reaches {script}'s "
        f"{sorted(escaping)} — the operator gets a raw traceback instead of "
        f"one actionable line. Leaky scopes: {sorted(leaky)}"
    )


def test_every_script_here_is_classified() -> None:
    """No script joins this directory silently.

    Two earlier revisions of this leg used a structural signal — first
    `import backlog_index`, then the literal `"def main("` — and a reviewer
    defeated each by writing a plausible store-reading gate that did not
    match it (the second fell to renaming the entry point from `main` to
    `run`). A signal guesses at intent. This asks instead that EVERY
    non-test module in this directory be a decision someone recorded: in
    `FAMILY` and given unreadable-input cases, or in `EXEMPT` with a stated
    reason. A new file fails here until someone answers the question.
    """
    classified = set(FAMILY) | set(EXEMPT)
    actual = {
        path.name
        for path in sorted(SCRIPTS.glob("*.py"))
        if not path.name.startswith("test_")
    }
    unclassified = actual - classified
    assert not unclassified, (
        "these modules are neither in FAMILY (gets unreadable-input cases) "
        f"nor in EXEMPT (with a stated reason): {sorted(unclassified)}. "
        "Classify each one — anything that reads a backlog store or a "
        "handoff brief belongs in FAMILY."
    )
    stale = classified - actual
    assert not stale, f"classified but no longer present: {sorted(stale)}"


# The number of EXEMPT modules that leak by this file's own metric. Pinned
# rather than written into prose, because a hand-written count is exactly
# what went stale: three shipped artifacts said "three" while the metric
# said fourteen, and no round ran the metric against the sentence quoting
# it. Anything that changes this number must also update the backlog entry
# that sizes the follow-up work.
EXEMPT_LEAK_COUNT = 16
EXEMPT_LEAK_LEDGER = (
    "docs/loom/backlog/"
    "2026-08-21-fail-loud-contract-covers-only-the-four-store-brief-gates.md"
)


def exempt_leaks() -> list[str]:
    """Every EXEMPT module from which a recognised OSError escape reaches
    `main` or module scope. Exempt means outside the CONTRACT, never
    'measured safe' — this function is what makes that distinction
    checkable instead of asserted."""
    leaking = []
    for name in sorted(EXEMPT):
        source = (SCRIPTS / name).read_text(encoding="utf-8")
        if leaky_scopes(source) & {"main", _MODULE_SCOPE}:
            leaking.append(name)
    return leaking


def test_exempt_leak_count_matches_the_filed_ledger() -> None:
    """The debt this file defers must be sized by running the metric, not
    by remembering it."""
    leaking = exempt_leaks()
    assert len(leaking) == EXEMPT_LEAK_COUNT, (
        f"{len(leaking)} EXEMPT modules leak, not {EXEMPT_LEAK_COUNT}: "
        f"{leaking}.\nUpdate EXEMPT_LEAK_COUNT and the entry at "
        f"{EXEMPT_LEAK_LEDGER}, which sizes the follow-up work against this "
        "number. Do not update one without the other."
    )
    ledger = (SCRIPTS.parents[1] / EXEMPT_LEAK_LEDGER).read_text(encoding="utf-8")
    assert str(EXEMPT_LEAK_COUNT) in ledger, (
        f"{EXEMPT_LEAK_LEDGER} does not state the measured count "
        f"{EXEMPT_LEAK_COUNT}; the ledger and the metric have drifted apart."
    )
