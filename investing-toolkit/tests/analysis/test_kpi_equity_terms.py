"""RED-first tests for analysis-kpi/scripts/kpi_equity_terms.py — the
whole-equity primitives that BOTH `kpi_spine_view` and
`kpi_us_statement_cells` read (plan Task 7's ordered first step,
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md ## Decision
Log, "2026-07-26, Task 5 -> Task 7. THE DEPENDENCY IS ABOUT TO INVERT INTO A
CYCLE").

WHY THIS MODULE EXISTS — MEASURED, NOT ARGUED. `kpi_us_statement_cells` binds
by name to eight of `kpi_spine_view`'s primitives and reads one of them AT
IMPORT TIME (`_EQUITY_CHAIN`). Task 7 makes `kpi_spine_view` consume the
reconstruction, which closes the loop. The failure was reproduced by MUTATION
before this module was written — a scratch copy of the scripts directory with
`import kpi_us_statement_cells` added to `kpi_spine_view`:

    $ python3 -c "import kpi_spine_view"
    AttributeError: partially initialized module 'kpi_spine_view' has no
    attribute 'SPINE_FIELD_CHAINS' (most likely due to a circular import)
    $ python3 -c "import kpi_us_statement_cells"
    OK

That is the Decision Log's prediction confirmed to the letter: the breakage is
REAL and ORDER-DEPENDENT, so whichever module a future caller happens to import
first decides whether the process starts. A test that only asserted "both
modules import today" would pass in both worlds; the test below instead asserts
the STRUCTURAL property that makes the cycle unconstructible — that
`kpi_us_statement_cells` does not import `kpi_spine_view` at all.

FIXTURE PROVENANCE: none. Every value asserted here is a CONSTANT or a rule
lifted verbatim out of `kpi_spine_view`; the numbers those rules were measured
against live in test_kpi_spine_view.py and test_kpi_us_statement_cells.py, which
are the suites that keep the semantics honest. What is pinned here is that the
lift moved them WITHOUT changing them — characterization in Feathers's sense
(2004 Ch.13), which is the right shape for code that is being relocated rather
than authored.

No `@req` tags: this dispatch carries no registered loom-spec REQ-ids (the work
is tracked by named plan Task 7), so `@req` is omitted per the implementer
contract.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

import pytest
from conftest import SKILLS

SCRIPTS = SKILLS / "analysis-kpi" / "scripts"
EQUITY_TERMS_SCRIPT = SCRIPTS / "kpi_equity_terms.py"
SPINE_VIEW_SCRIPT = SCRIPTS / "kpi_spine_view.py"
CELLS_SCRIPT = SCRIPTS / "kpi_us_statement_cells.py"

# The eight bindings the Decision Log names, which must survive Task 7 by name
# AND by semantics. `SPINE_FIELD_CHAINS["total_equity"]` is the eighth and is
# checked separately below: it is the one that cannot simply move, because
# `SPINE_FIELD_CHAINS` is Task 11's subject and its prose is asserted against
# `kpi_spine_view.py`'s own source text there.
_LIFTED_NAMES = (
    "_equity_kind",
    "_minority_interest_term",
    "_identity_value",
    "_US_GAAP",
    "MEZZANINE_CHAIN",
    "MINORITY_INTEREST_CHAIN",
    "EQUITY_INCL_NCI_CONCEPT",
)


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def equity_terms():
    """Loaded under its REAL module name, deliberately: the two importers below
    resolve it by that name, so registering it here is what makes "the same
    object, not a copy" an answerable question at all. Loaded under a test-local
    alias instead, every `is` check below would compare two independently
    executed copies and fail for a reason that says nothing about the lift."""
    return _load("kpi_equity_terms", EQUITY_TERMS_SCRIPT)


@pytest.fixture(scope="module")
def spine_view(equity_terms):
    return _load("kpi_spine_view_for_equity_terms_test", SPINE_VIEW_SCRIPT)


@pytest.fixture(scope="module")
def cells(equity_terms):
    return _load("kpi_us_statement_cells_for_equity_terms_test", CELLS_SCRIPT)


def test_the_cells_module_does_not_import_the_spine_view():
    """THE CYCLE IS UNCONSTRUCTIBLE, not merely unbuilt.

    Asked in a FRESH INTERPRETER, because the answer is about module-level
    imports and this suite's other fixtures have already loaded both modules
    into `sys.modules` — asking in-process would read this test's own setup and
    answer "imported" no matter what the file says.

    This is the test that was RED before the lift: `kpi_us_statement_cells`
    imported `kpi_spine_view` at line 86. It is also the test that goes RED
    again if anyone re-adds that import, which is the only durable guard —
    the cycle does not fail loudly on its own, it fails by statement order.
    """
    probe = (
        "import sys; sys.path.insert(0, %r);"
        "import kpi_us_statement_cells;"
        "print('kpi_spine_view' in sys.modules)" % str(SCRIPTS)
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        timeout=60,
        # The plan's kickoff decision: never regenerate `__pycache__` under
        # `skills/`, which blocks the skill-folder hook. The rest of the
        # environment rides through — a stripped one breaks the interpreter
        # this suite is already running under.
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False", (
        "kpi_us_statement_cells still reaches kpi_spine_view at import time; "
        "the Task 7 cycle is one import away from being real"
    )


def test_every_lifted_binding_is_one_object_seen_from_both_sides(
    equity_terms, spine_view,
):
    """All seven names resolve from the shared module AND still resolve under
    their historical spelling on `kpi_spine_view`, and they are the SAME object
    — not a copy that can drift.

    Identity (`is`), not equality: two equal tuples in two modules is exactly
    the duplication this lift exists to remove, and `==` would not notice it.
    """
    for name in _LIFTED_NAMES:
        lifted = getattr(equity_terms, name)
        assert getattr(spine_view, name) is lifted, name


def test_the_equity_chain_has_exactly_one_source(equity_terms, spine_view, cells):
    """The eighth binding. `SPINE_FIELD_CHAINS["total_equity"]` stays in
    `kpi_spine_view` (Task 11 owns that symbol's disposition and asserts against
    that file's source text), so the shared module carries the pair and
    `kpi_spine_view`'s own import-time `_assert_equity_chain` is what keeps the
    two from drifting apart.

    ORDER IS LOAD-BEARING and is asserted as a tuple, not a set: parent-only
    FIRST is what makes `_equity_kind`'s majority branch the parent-only one
    (kpi_spine_view.py header, "THE EQUITY TERM IS WHOLE EQUITY" — 17 of 32
    checkable filers).
    """
    pair = (
        equity_terms.EQUITY_PARENT_ONLY_CONCEPT,
        equity_terms.EQUITY_INCL_NCI_CONCEPT,
    )
    assert equity_terms.EQUITY_CHAIN == pair
    assert dict(spine_view.SPINE_FIELD_CHAINS)["total_equity"] == pair
    assert cells._EQUITY_CHAIN == pair


def test_the_drift_guard_still_refuses_a_chain_that_is_not_the_pair(spine_view):
    """`_assert_equity_chain` stays where `SPINE_FIELD_CHAINS` is, and still
    trips on BOTH failure directions — a reorder (which flips which concept the
    majority of periods resolve to) and an extension (which adds a member
    `_equity_kind` cannot name, silently making every period carrying it
    uncheckable)."""
    pair = (
        spine_view.EQUITY_PARENT_ONLY_CONCEPT,
        spine_view.EQUITY_INCL_NCI_CONCEPT,
    )
    with pytest.raises(RuntimeError):
        spine_view._assert_equity_chain(tuple(reversed(pair)))
    with pytest.raises(RuntimeError):
        spine_view._assert_equity_chain(pair + ("SomeOtherEquityConcept",))
    assert spine_view._assert_equity_chain(pair) is None


def test_the_lifted_rules_answer_exactly_as_they_did_in_the_spine_view(
    equity_terms,
):
    """Characterization of the three lifted FUNCTIONS (Feathers 2004 Ch.13):
    the branches whose wrongness costs a wrong number, pinned at the new site.

      * `_equity_kind` reads the store's spelling and answers None — not a
        guess — for a concept it cannot name.
      * `_minority_interest_term` returns 0 on the incl-NCI branch (adding the
        interest again would double-count it) and None, not 0, when the filer
        asserts an NCI exists but supplies no amount (zeroing it manufactures a
        residual equal to the interest and falsely accuses the filer).
      * `_identity_value` rejects `bool`, which is an `int` in Python and would
        otherwise enter the arithmetic as 0 or 1.
    """
    us_gaap = equity_terms._US_GAAP
    kind = equity_terms._equity_kind
    assert kind({"kpi_id": us_gaap + equity_terms.EQUITY_PARENT_ONLY_CONCEPT}) == (
        "parent_only"
    )
    assert kind({"kpi_id": us_gaap + equity_terms.EQUITY_INCL_NCI_CONCEPT}) == "incl_NCI"
    assert kind({"kpi_id": us_gaap + "Assets"}) is None
    assert kind(None) is None

    term = equity_terms._minority_interest_term
    assert term("incl_NCI", None, None, nci_is_asserted=False) == 0
    assert term("parent_only", None, None, nci_is_asserted=False) == 0
    assert term("parent_only", None, None, nci_is_asserted=True) is None
    assert term(
        "parent_only",
        {"canonical_value": 1905000000},
        {"canonical_value": 1905000000},
        nci_is_asserted=False,
    ) == 1905000000

    value = equity_terms._identity_value
    assert value({"canonical_value": 1905000000}) == 1905000000
    assert value({"canonical_value": True}) is None
    assert value({"canonical_value": "1905"}) is None
    assert value(None) is None
