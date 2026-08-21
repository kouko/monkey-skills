"""Two capability claims the oracle
(`test_gate_scripts_fail_loud_on_unreadable_input.py`) makes about itself,
promoted from two throwaway probes to standing tests so they survive past
the session that ran them.

Claim A: no mutant of a recognised filesystem-guard handler in the FAMILY
survives an oracle run — except a named, reasoned survivor set.
Claim B: every scope-attribution shape the oracle's own `leaky_scopes`
docstring names (a read inside a class method, a nested def, a lambda,
or module-level code) is caught, alongside a spread of recognised-name
import forms (bare `open()`, plain/aliased from-import, aliased module
import, `os.path` from-import).

Both claims are asserted IN-PROCESS on the oracle's own production
expression — `leaky_scopes(source) & {"main", _MODULE_SCOPE}` — imported
from the oracle module, never re-implemented and never run as a
subprocess. A subprocess run against a `tmp_path` copy cannot work here:
the oracle's ledger test resolves `docs/loom/backlog/...` relative to its
own parent directories, which a copied tree lacks, so it exits non-zero
for every input and every mutant reads as killed regardless of whether it
was detected — a test that cannot fail. See
docs/loom/memory/a-mutation-test-must-run-the-production-assertion.md and
docs/loom/memory/a-no-mutation-test-cannot-baseline-off-shared-fixture-state.md.

Source text is read once from the real file and mutated in memory. This
module writes nothing under loom-code/scripts/, not even transiently.
"""

from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
ORACLE_PATH = SCRIPTS / "test_gate_scripts_fail_loud_on_unreadable_input.py"


def _load_oracle():
    """Load the oracle module by path under a private name, so this file
    never collides with pytest's own collection of the oracle as
    `test_gate_scripts_fail_loud_on_unreadable_input` and never
    re-implements any of its symbols."""
    spec = importlib.util.spec_from_file_location(
        "_oracle_under_test_for_capability_claims", ORACLE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_oracle = _load_oracle()
leaky_scopes = _oracle.leaky_scopes
_MODULE_SCOPE = _oracle._MODULE_SCOPE
FAMILY = _oracle.FAMILY
_OSERROR_SUPERSETS = _oracle._OSERROR_SUPERSETS


# --- Claim A: mutate every recognised filesystem-guard handler ------------


def _guarded_call_desc(node: ast.Try) -> str:
    """A short, line-number-independent label for what a `try` body's first
    call expression is — used as the stable half of a case identity, since
    the sibling docstring-only tasks in this arc shift line numbers without
    changing which call a guard protects."""
    for stmt in node.body:
        for child in ast.walk(stmt):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute):
                    base = func.value.id if isinstance(func.value, ast.Name) else "?"
                    return f"{base}.{func.attr}"
                if isinstance(func, ast.Name):
                    return func.id
    return "<no call>"


def _guard_mutation_sites(source: str) -> list[tuple[int, str, str]]:
    """(lineno, superset_name, guarded_call_desc) for every OSError-superset
    name occurring in a guarding except-handler's type expression, bare or
    inside a tuple — the same recognition `_guarded_line_ranges` uses, but
    returning sites rather than ranges so each one can be mutated alone."""
    tree = ast.parse(source)
    sites: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        desc = _guarded_call_desc(node)
        for handler in node.handlers:
            if handler.type is None:
                continue
            names: list[ast.Name] = []
            if isinstance(handler.type, ast.Name):
                names = [handler.type]
            elif isinstance(handler.type, ast.Tuple):
                names = [e for e in handler.type.elts if isinstance(e, ast.Name)]
            for n in names:
                if n.id in _OSERROR_SUPERSETS:
                    sites.append((n.lineno, n.id, desc))
    return sites


def _mutate_guard(source: str, lineno: int, name: str) -> str:
    """Replace the one occurrence of `name` as a whole word on `lineno`
    with an exception type `_guarded_line_ranges` does not recognise as a
    guard — the same mutation the source probe applied via
    `except OSError` -> `except ZeroDivisionError`, generalised to also
    reach a tuple handler's individual names."""
    lines = source.splitlines(keepends=True)
    pattern = re.compile(rf"\b{re.escape(name)}\b")
    line = lines[lineno - 1]
    mutated_line, count = pattern.subn("ZeroDivisionError", line, count=1)
    assert count == 1, f"expected {name!r} on line {lineno}, found none: {line!r}"
    lines[lineno - 1] = mutated_line
    return "".join(lines)


def _all_mutation_cases() -> list[tuple[str, int, str, str]]:
    cases: list[tuple[str, int, str, str]] = []
    for script in FAMILY:
        source = (SCRIPTS / script).read_text(encoding="utf-8")
        for lineno, name, desc in _guard_mutation_sites(source):
            cases.append((script, lineno, name, desc))
    return cases


_ALL_CASES = _all_mutation_cases()

# The survivor set, recomputed against the working tree rather than
# transcribed from any Decision Log (one of them is superseded — see the
# plan's Notes). Identified by (script, guarded call) rather than line
# number, because sibling docstring-only tasks in this arc reshuffle line
# numbers in these same files without moving which call a guard protects.
#
# Two are BY DESIGN: `check_onramp_choice.py` and `check_queue_relation.py`
# each guard a `subprocess.run` call, not a filesystem call, so the oracle
# has no jurisdiction over them. Two more were found by running this
# discovery, not asserted from any prior count: `check_queue_relation.py`
# guards a call to `live_bet_names`, and `check_north_star_link.py` guards
# a call to `find_bet_entries` — both top-level helpers in THEIR OWN file
# whose bodies call `live_entries`, imported from `backlog_index`.
# `leaky_scopes` analyses one file at a time; a cross-module call is
# neither in `_FS_CALLS` nor a locally tracked leaky scope, so it is
# invisible to this file's own fixpoint. This is a real gap in the
# oracle's coverage, not a by-design exemption — reported here rather than
# asserted away. Filed at
# docs/loom/backlog/2026-08-21-leaky-scopes-cannot-see-a-guard-over-a-cross-module-delegating-helper.md.
_BY_DESIGN_SURVIVORS = {
    ("check_onramp_choice.py", "subprocess.run"),
    ("check_queue_relation.py", "subprocess.run"),
}
_CROSS_MODULE_BLIND_SPOT_SURVIVORS = {
    ("check_queue_relation.py", "live_bet_names"),
    ("check_north_star_link.py", "find_bet_entries"),
}
_ALL_SURVIVOR_KEYS = _BY_DESIGN_SURVIVORS | _CROSS_MODULE_BLIND_SPOT_SURVIVORS

# `(script, desc)` is deliberately line-number-independent (see above), but
# that means it is not injective over discovered sites: `_guarded_call_desc`
# degrades to the same label for two distinct calls sharing a receiver name
# (or two distinct bare-name calls). A collision that lands OUTSIDE the
# survivor set is harmless — every matching case is still individually
# mutated below, just under a shared label. A collision that lands INSIDE
# the survivor set is not: the filter below would silently exempt every
# site sharing that key, not just the one meant to be exempted, and the
# un-exempted twin would never be mutated at all. Rather than disambiguate
# every desc with an occurrence ordinal (which would make the reasoned
# survivor tuples above harder to read as plain "(script, call)" pairs a
# human can check by eye), assert the one place aliasing is actually
# dangerous: no survivor key may match more than one discovered site.
for _survivor_key in _ALL_SURVIVOR_KEYS:
    _matching_sites = [c for c in _ALL_CASES if (c[0], c[3]) == _survivor_key]
    assert len(_matching_sites) == 1, (
        f"survivor key {_survivor_key!r} matches {len(_matching_sites)} "
        f"discovered guard sites {_matching_sites} -- this key is not "
        "unique among mutation sites, so exempting it would silently "
        "exempt every site sharing the label, not just the one reasoned "
        "about above. Disambiguate the colliding calls (or the survivor "
        "reasoning) before trusting this exemption."
    )

_KILLED_CASES = [c for c in _ALL_CASES if (c[0], c[3]) not in _ALL_SURVIVOR_KEYS]
_BY_DESIGN_CASES = [c for c in _ALL_CASES if (c[0], c[3]) in _BY_DESIGN_SURVIVORS]
_CROSS_MODULE_CASES = [
    c for c in _ALL_CASES if (c[0], c[3]) in _CROSS_MODULE_BLIND_SPOT_SURVIVORS
]


@pytest.mark.parametrize("script,lineno,name,desc", _KILLED_CASES)
def test_mutating_a_recognised_filesystem_guard_is_caught(
    script: str, lineno: int, name: str, desc: str
) -> None:
    source = (SCRIPTS / script).read_text(encoding="utf-8")
    mutated = _mutate_guard(source, lineno, name)
    leaky = leaky_scopes(mutated) & {"main", _MODULE_SCOPE}
    assert leaky, (
        f"mutating the guard at {script}:{lineno} ({name} -> "
        "ZeroDivisionError, guarding a call to "
        f"{desc}) did not make any scope leaky — this mutant survived an "
        "oracle run undetected"
    )


@pytest.mark.parametrize("script,lineno,name,desc", _BY_DESIGN_CASES)
def test_the_subprocess_only_guards_survive_by_design(
    script: str, lineno: int, name: str, desc: str
) -> None:
    """These guard a `subprocess.run` call, not a filesystem call — the
    oracle has no jurisdiction over them, so their mutants must survive;
    asserting `leaky` here would pin a false claim."""
    source = (SCRIPTS / script).read_text(encoding="utf-8")
    mutated = _mutate_guard(source, lineno, name)
    leaky = leaky_scopes(mutated) & {"main", _MODULE_SCOPE}
    assert not leaky, (
        f"{script} guard over {desc} was expected to survive as a "
        f"subprocess-only guard but the mutant was caught: {sorted(leaky)} "
        "— the survivor set has changed, update the reasoning above"
    )


@pytest.mark.parametrize("script,lineno,name,desc", _CROSS_MODULE_CASES)
def test_a_guard_around_a_cross_module_delegating_helper_survives_undetected(
    script: str, lineno: int, name: str, desc: str
) -> None:
    """A real gap, not a by-design exemption: the guarded call is to a
    top-level helper in THIS file whose own body delegates the actual
    filesystem read to `live_entries`, imported from `backlog_index`.
    `leaky_scopes` analyses one file at a time, so this cross-module call
    is invisible to it and the mutant is not caught."""
    source = (SCRIPTS / script).read_text(encoding="utf-8")
    mutated = _mutate_guard(source, lineno, name)
    leaky = leaky_scopes(mutated) & {"main", _MODULE_SCOPE}
    assert not leaky, (
        f"{script} guard over {desc} was expected to survive as a "
        f"cross-module delegation blind spot but the mutant was caught: "
        f"{sorted(leaky)} — the oracle may have gained cross-module reach, "
        "update the reasoning above"
    )


def test_the_family_has_no_survivor_outside_the_two_named_reasons() -> None:
    """The completeness check on Claim A: every discovered mutation site
    is accounted for by exactly one of the two reasons above, or is
    caught. A new, unreasoned survivor must fail loudly here rather than
    silently widen the exempt set."""
    discovered_survivor_keys = set()
    for script, lineno, name, desc in _ALL_CASES:
        source = (SCRIPTS / script).read_text(encoding="utf-8")
        mutated = _mutate_guard(source, lineno, name)
        if not (leaky_scopes(mutated) & {"main", _MODULE_SCOPE}):
            discovered_survivor_keys.add((script, desc))
    assert discovered_survivor_keys == _ALL_SURVIVOR_KEYS, (
        f"discovered survivor set {sorted(discovered_survivor_keys)} does "
        f"not match the reasoned set {sorted(_ALL_SURVIVOR_KEYS)} — a "
        "mutant either started surviving with no recorded reason, or a "
        "reasoned survivor is now caught and its entry is stale"
    )


# --- Claim B: every known escape shape is caught ---------------------------

_ESCAPE_SHAPES: dict[str, str] = {
    "bare path.open()": """
from pathlib import Path

def _load(root: Path) -> str:
    with root.open(encoding="utf-8") as fh:
        return fh.read()

def main() -> int:
    _load(Path("."))
    return 0
""",
    "class-method read": """
from pathlib import Path

class _Reader:
    def load(self, root: Path) -> str:
        return root.read_text(encoding="utf-8")

def _load(root: Path) -> str:
    return _Reader().load(root)

def main() -> int:
    _load(Path("."))
    return 0
""",
    "plain from-import": """
from pathlib import Path
from os import listdir

def _load(root: Path) -> list:
    return listdir(root)

def main() -> int:
    _load(Path("."))
    return 0
""",
    "aliased from-import": """
from pathlib import Path
from os import listdir as ls

def _load(root: Path) -> list:
    return ls(root)

def main() -> int:
    _load(Path("."))
    return 0
""",
    "aliased module import": """
from pathlib import Path
import os as _os

def _load(root: Path) -> list:
    return _os.listdir(root)

def main() -> int:
    _load(Path("."))
    return 0
""",
    "os.path from-import": """
from pathlib import Path
from os.path import exists

def _load(root: Path) -> bool:
    return exists(root)

def main() -> int:
    _load(Path("."))
    return 0
""",
    "nested def read": """
from pathlib import Path

def _load(root: Path) -> str:
    def _inner() -> str:
        return root.read_text(encoding="utf-8")
    return _inner()

def main() -> int:
    _load(Path("."))
    return 0
""",
    "lambda read": """
from pathlib import Path

def _load(root: Path) -> str:
    fn = lambda: root.read_text(encoding="utf-8")
    return fn()

def main() -> int:
    _load(Path("."))
    return 0
""",
    "module-level read": """
from pathlib import Path

Path(".").read_text(encoding="utf-8")

def main() -> int:
    return 0
""",
}


@pytest.mark.parametrize("shape", sorted(_ESCAPE_SHAPES))
def test_every_known_escape_shape_reaches_a_top_level_scope(shape: str) -> None:
    source = _ESCAPE_SHAPES[shape]
    leaky = leaky_scopes(source) & {"main", _MODULE_SCOPE}
    assert leaky, (
        f"escape shape {shape!r} reached neither `main` nor module scope: {source}"
    )
