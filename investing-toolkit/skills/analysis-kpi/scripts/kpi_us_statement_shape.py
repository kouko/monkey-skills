#!/usr/bin/env python3
"""kpi_us_statement_shape.py — classify one XBRL role URI as one of the three
statements (plan Task 2), and assemble a filing's three statements from the
roles that classify (plan Task 3),
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md.

TWO FUNCTIONS, TWO SCOPES. `statement_kind` is a pure function of a role
string. `statements_for` reads a filing: it is a pure function of (filing,
this module's derivation) with no cache and no persistence (plan ## Notes
kickoff decision — the reconstruction is RECOMPUTED, never persisted, so it
can be wrapped in a cache later without touching a caller). Everything below
the `statement_kind` section belongs to assembly; the classification rules
above it are unchanged by Task 3.

A filing declares 14-132 presentation/calculation roles, MOST of them notes.
`statement_kind` answers, for ONE role at a time, which of the three
statements it is — or `None`.

`None` IS AN ANSWER, NOT A FAILURE. A mis-classified role is the expensive
outcome this module exists to avoid: cash-flow lines routed into the income
statement render as plausible lines with plausible labels and then silently
fail every downstream sum check (plan Task 4). A role this cannot recognise
is therefore reported as unrecognised and left out, never rounded to the
nearest kind.

THE MEASURED TRAP (observed live 2026-07-26): an earlier probe excluded any
role whose URI mentioned comprehensive income. Some filers COMBINE the income
statement and comprehensive income into ONE statement, and such a filer is
left with NO income statement at all by that exclusion — Realty Income's
`ConsolidatedStatementsOfIncomeAndComprehensiveIncome` is the observed case.
The rule here instead REMOVES the comprehensive-income wording and then asks
whether income-statement wording remains: a combined role keeps its income
wording and classifies as `income`; a comprehensive-income-ONLY role has
nothing left and classifies as `None` (that fourth statement is out of scope
for this arc — brief §Out of Scope). Combining is the MINORITY convention:
Colgate, Costco and Microsoft were each measured filing the two separately.

A statement of RETAINED EARNINGS is the same shape of problem — a statement
outside this arc's three whose title embeds a word ("earnings") the income
rule matches on — so it is removed the same way, and for the same reason it is
removed rather than rejected: `...OfIncomeAndRetainedEarnings` is a real
combined title, and rejecting the role outright would erase that filer's
income statement exactly as the comprehensive-income exclusion did.

MATCHING IS POSITIVE, NOT A DENYLIST OF OBSERVED NAMES
([[shared-classifier-over-open-dialects-needs-allowlist]]): a role is a
statement only when its URI carries wording a statement is NAMED with. Filers
vary casing and word order freely (`ConsolidatedStatementsOfOperations`,
`CONSOLIDATEDSTATEMENTSOFOPERATIONS`, `StatementBALANCESHEETS`,
`ConsolidatedResultsOfOperations` — all observed), so matching runs on the
role's last path segment with case and punctuation folded away. The one
NEGATIVE list is small and note-shaped: those are the note roles that repeat
a statement's own wording, and repeating that wording is exactly what would
fool a positive match. A note role carrying no statement wording needs no
entry — it falls through to `None` on its own.

HOW WELL EACH ENTRY IS ACTUALLY PINNED -- three tiers, not two, because
"pinned" hides a real difference:

  1. OBSERVED-PINNED — a test built on a role URI fetched from a real filing
     fails without the entry. This is the only tier that is evidence.
  2. CONSTRUCTED-PINNED — the pinning URI was written to pin the rule. The pin
     is CIRCULAR: it restates the rule as a test rather than testing it against
     the world. Five entries sit here; all five are quarantined below the fence
     in the test module and each is labelled at its own site.
  3. KEPT-UNPINNED — `tables`, and only `tables`. Deleting it breaks no test,
     yet it guards a verified wrong-kind path
     (`...ConsolidatedStatementsOfCashFlowsTables` classifies `cash_flow`
     without it). Its caveat lives at its own site below.

An entry that cannot be pinned is normally deleted rather than kept "just in
case" — an unpinned rejection is indistinguishable from padding and can only
silently discard statements. Tier 3 is the one documented exception.

Naming the tiers, rather than writing "EVERY entry is pinned", is deliberate:
this docstring said "every" for one round while `tables` already contradicted
it 37 lines below, and a reviewer showed a maintainer applying that invariant
literally would delete a load-bearing guard. It is the same defect as the
sibling module's mirroring claim and this module's own earlier
fixture-provenance note (docs/loom/memory/unifying-a-normalization-has-a-scope.md).
A universal claim with a live counter-example is worse than no claim: the next
reader trusts the rule and deletes the thing the rule never covered.

NOTHING HERE INFERS MEANING FROM A LINE'S POSITION (brief §Decision): this
reads the role's NAME, which is what names are for. Which lines the role
carries, and what they mean, is decided elsewhere.

SELECTING AMONG ROLES IS NOT `statement_kind`'S JOB. A filing offering both a
pure income role and a combined income-and-comprehensive one must prefer the
pure one — but that is a choice BETWEEN roles, so it lives in `statements_for`
below, the only caller that sees a filing's whole role set. Per-role
classification stays total and order-free.

`statement_kind` IS A PURE FUNCTION of the role string. The module as a whole
is stdlib-only, but it is no longer I/O-free: `statements_for` reads the
filing handed to it. Stated as the exception rather than dropping the claim,
because the claim is still what governs everything above the assembly section.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Sibling import, mirroring `kpi_spine_view.py`'s shim so the module resolves
# both under `uv run --script` and under importlib test loading.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import kpi_us_statement_lines as statement_lines  # noqa: E402

# Note-role wording that repeats a statement's own words. Only roles that
# would otherwise match a statement need to be here; a note with no statement
# wording is already `None`. Each entry names the observed role that pins it:
_NON_STATEMENT_MARKERS = (
    "parenthetical",     # ...BalanceSheetsParenthetical -> balance_sheet
    # SINGULAR STEM, DELIBERATELY: filers spell this suffix both ways
    # (IBM `...StatementOfCashFlowsDetails`, Microsoft
    # `...CashFlowHedgesDetail`) and `Details` contains `detail`, so the stem
    # catches both spellings while the plural catches only one. Under the
    # plural, a singular-`Detail` note quoting a statement title —
    # `...StatementOfCashFlowsDetail` in Microsoft's dialect — reached the
    # noun rule and classified as `cash_flow`: a WRONG-KIND result surviving
    # only because no observed role happened to combine those two spellings.
    "detail",            # ...ImpactOnConsolidatedStatementsOfIncomeDetails
    # NOT INDEPENDENTLY PINNED — do not delete on a mutation audit alone. The
    # only observed ...Tables role quoting a statement's wording
    # (`SupplementalIncomeStatementInformationTables`) also carries
    # `supplemental`, so tests still pass without this entry. It is kept
    # because that joint coverage is a coincidence of one filer's naming, not
    # a property of the ...Tables shape, and the direction it guards is
    # wrong-kind.
    "tables",            # ...StatementsOfCashFlowsTables -> cash_flow
    "offbalancesheet",   # OffBalanceSheetLendingRelated... -> balance_sheet
    "supplemental",      # SupplementalBalanceSheetInformation, and
                         # SupplementalIncomeStatementInformation, which are
                         # Colgate NOTE roles quoting a statement's own title.
)

# Wording for statements OUTSIDE this arc's three, removed BEFORE classifying
# because each embeds a word the three's rules match on. What survives the
# removal decides the kind — see the module docstring's TRAP note. Removal, not
# rejection: a filer may combine one of these with the income statement, and
# rejecting the role would erase that filer's income statement.
_OTHER_STATEMENT_WORDINGS = (
    "comprehensiveincome",   # ...OfComprehensiveIncome -> would be `income`
    # DEFENSIVE AGAINST AN UNOBSERVED CASE — measured absent in BOTH eras of
    # this lane's range (checked 2026-07-26): 10 filers' 2015-2020 10-Ks
    # (GIS/KMB/SWK/PPG/ADM/SO/ED/NEE/MMM/EMR) and 12 filers' earliest
    # XBRL-era 2010 10-Ks (those plus KO/PG/JNJ), 22 filer-observations, ZERO
    # roles containing this wording. An earlier note here claimed the combined
    # "Income and Retained Earnings" title was more common in the earlier
    # span; that was an inference and the 2010 sweep measured it FALSE. The
    # statement of stockholders' equity occupies this slot at both ends of the
    # range (`realtyincome.com/role/ConsolidatedStatementsOfEquity`, observed,
    # already `None` since it carries none of the three nouns). Kept because it
    # is cheap and guards the wrong-kind direction — NOT because the case was
    # found. Its fixtures are CONSTRUCTED-CONVENTIONAL by necessity: none
    # exists to observe.
    "retainedearnings",      # ...OfRetainedEarnings -> would be `income`
)

# Each kind, with the wordings that NAME that statement on their own and the
# wordings that name it only when the word "statement" stands beside them.
# "Balance sheet" and "financial position" name nothing but the statement, and
# most real balance-sheet roles carry no "statement" word at all, so they
# stand alone. "Income", "operations", "earnings" and "cash flow" each also
# name a note topic ("income taxes", "cash flow hedges"), so alone they prove
# nothing. "Results of operations" is the one multi-word title a filer uses
# with no "statement" word (Caterpillar), so it stands alone too.
_KIND_RULES = (
    ("cash_flow", (), ("cashflow",)),
    ("balance_sheet", ("balancesheet", "financialposition"), ()),
    ("income", ("resultsofoperations",), ("income", "operations", "earnings")),
)


def statement_kind(role: str) -> str | None:
    """Which statement this role URI names: `"income"`, `"balance_sheet"`,
    `"cash_flow"` — or `None` when this cannot prove it is any of them.

    `None` covers three different roles and deliberately does not distinguish
    them: a note or parenthetical role, a statement outside this arc's three
    (comprehensive income, changes in equity), and a role whose wording this
    does not recognise. All three mean the same thing to a caller — do not
    read statement lines from this role.
    """
    folded = _fold(role)
    if any(marker in folded for marker in _NON_STATEMENT_MARKERS):
        return None
    remaining = _without_other_statement_wording(folded)
    names_a_statement = "statement" in remaining
    for kind, self_naming, needs_statement_word in _KIND_RULES:
        if any(wording in remaining for wording in self_naming):
            return kind
        if names_a_statement and any(w in remaining for w in needs_statement_word):
            return kind
    return None


def _fold(role: str) -> str:
    """The role's last path segment, lowercased with every non-alphanumeric
    character dropped — so `ConsolidatedStatementsOfOperations`,
    `CONSOLIDATED_STATEMENTS_OF_OPERATIONS` and
    `Consolidated Statements of Operations` all fold to one string to match
    against. Only the last segment: the rest of the URI is the filer's domain
    and taxonomy date (`.../20180630/taxonomy/role/...`), which say nothing
    about the statement and can contribute stray matches.
    """
    return "".join(ch for ch in role.rsplit("/", 1)[-1].lower() if ch.isalnum())


def _without_other_statement_wording(folded: str) -> str:
    """`folded` with every out-of-scope statement's wording removed.

    This is the trap fix: what a role says BESIDES that other statement is
    what decides its kind. `...OfIncomeAndComprehensiveIncome` still says
    "statements of income" afterwards and is an income statement;
    `...OfComprehensiveIncome` says nothing afterwards and is not. Same for
    `...OfIncomeAndRetainedEarnings` against `...OfRetainedEarnings`.
    """
    for wording in _OTHER_STATEMENT_WORDINGS:
        folded = folded.replace(wording, "")
    return folded


# =====================================================================
# ASSEMBLY (plan Task 3) — a filing's three statements as ordered lines
# =====================================================================

# The keys that mark a `get_statement` row as a segment slice, as observed —
# NOT as a rule. The rule lives in `kpi_us_statement_lines`, which rejects any
# truthy "dim"-containing key that is not a known child descriptor, so it needs
# no such list. This one exists only so assembly can tell a key it has SEEN
# from one it has not, and report the latter (see
# `_unrecognised_dimension_keys`).
#
# OBSERVED 2026-07-26 in tests/data/fixtures/
# us_statement_reconstruction_2026-07-26.json: exactly four keys containing
# "dim" occur across 5 filings x 3 statements x 2 eras — these three plus the
# child descriptor. Its scope is that capture and nothing wider: a filer or an
# edgartools version outside it may well spell a fifth, which is the entire
# reason the unrecognised ones are counted rather than assumed absent.
_SEEN_ROW_LEVEL_DIMENSION_KEYS = frozenset({
    "is_dimension", "full_dimension_label", "dimension_metadata",
})


def normalize_balance(balance):
    """The taxonomy's `debit` / `credit` classification in ONE spelling, so a
    consumer comparing it for equality does not have to decide how.

    THE SITE THAT DECIDES IS THIS ONE, and it is a `Line`-construction-time
    normalisation rather than a rule each reader applies (`Line.__post_init__`
    calls it). The defect it closes has now appeared three times on this branch:
    a value compared for equality by several consumers diverges the moment one
    of them folds case and the others do not — `line.balance != "debit"` admits
    a `"Debit"` cost line as a revenue total (fails OPEN) while
    `str(line.balance or "").casefold() == "debit"` excludes it (fails CLOSED).
    The parent commit `ca9c9e12` fixed the same shape for an Axis/Member suffix.

    WHAT IT DOES AND, EXACTLY, WHAT IT DOES NOT. It folds case and nothing else:
    no whitespace trimming, no synonym mapping, and NO validation against
    `debit`/`credit`. A spelling this repo has not seen is folded and carried
    through unchanged, so it stays visible to whoever reads it instead of being
    rounded to one of the two known answers — the same fail-visible doctrine
    `unrecognised_dimension_keys` applies one level up. `None` survives as
    `None`, which is the majority (349 of the 455 captured rows) and means "the
    taxonomy says nothing", never "not revenue".
    """
    return None if balance is None else str(balance).casefold()


@dataclass(frozen=True)
class Line:
    """One rendered statement line, as the FILER declared it.

    `label` is the filer's own prose and is for display only — it is never a
    key (IBM moved its revenue label five times in 14 years while holding one
    concept; brief §Series identity). `weight` and `calculation_parent` are
    `None` for a line that participates in no declared sum: KO's EPS rows are
    the observed case, and that is a property of the filing, not an error —
    they are lines, and arithmetic must leave them alone.

    `decimals` is the precision the FILER claimed for each period's fact, keyed
    by period exactly as `values` is — KO states -6 (rounded to millions) on
    its revenue line and 2 (cents) on its EPS line in the same statement, so a
    single scalar would silently pick one of them. It is ADDED FOR PLAN TASK 8
    (plan Decision Log, "Task 4 -> Task 8"): without it the sum check compares
    exactly, and filers round each fact independently, so 24 of the 27
    disagreements over the committed capture are rounding residue rather than
    filer error. It is carried, never interpreted — what an interval built on
    it permits is `kpi_us_statement_check`'s judgement, not this module's.

    An EMPTY mapping means the filer declared no precision for that line, which
    a consumer must read as "compare exactly", never as "any precision". That
    is also the default, so a `Line` built by a caller that predates this field
    keeps working and keeps the strict reading.

    `balance` is the TAXONOMY's own `debit` / `credit` classification of the
    concept — not the filer's and not this module's. It is carried for plan
    Task 8, which must tell a revenue concept from a cost concept whose local
    name also carries the revenue wording (`us-gaap_CostOfRevenue`), and whose
    weight does not always separate them: a cost line rolling POSITIVELY into a
    costs subtotal is +1.0 like a revenue line.

    `None` IS THE COMMON CASE — 349 of the 455 captured rows carry no balance
    (abstract headers, per-share rows, concepts the taxonomy does not classify)
    — and means "the taxonomy says nothing", never "not revenue". A consumer
    that read `None` as a rejection would discard exactly the filer's OWN
    custom concepts this design exists to keep.

    It arrives CASE-FOLDED, whatever the upstream spelled — see
    `normalize_balance` for why that is decided here and not by each reader.
    """

    label: str
    concept: str
    level: int | None
    weight: float | None
    calculation_parent: str | None
    values: dict[str, Any]
    decimals: dict[str, Any] = field(default_factory=dict)
    balance: str | None = None

    def __post_init__(self) -> None:
        # `object.__setattr__` because the dataclass is frozen; normalising in
        # the constructor is what makes the field canonical for EVERY producer,
        # including a caller that builds a `Line` by hand, and for the JSON this
        # is serialised into (`kpi_spine_view` rehydrates from that payload).
        object.__setattr__(self, "balance", normalize_balance(self.balance))


@dataclass(frozen=True)
class Statements:
    """One filing's three statements, plus what assembly could not account for.

    `by_kind` holds only the kinds the filing actually declares a role for: a
    kind whose role is missing is ABSENT, never an empty list, so "this filer
    files no such statement" cannot be confused with "the statement is empty".

    `roles` maps each kind to EVERY role that classified as it, in the order
    preference put them; the first is the one read. A kind with more than one
    entry is therefore visible to a caller without a second reporting channel.

    `unrecognised_dimension_keys` is the counting half of the exclusion
    doctrine in docs/loom/memory/
    shared-classifier-over-open-dialects-needs-allowlist.md — exclude
    fail-closed, count visibly, promote deliberately. Empty on every captured
    filing; non-empty means the row shape has moved and a consolidated line
    may now be being deleted in silence.
    """

    by_kind: dict[str, list[Line]]
    roles: dict[str, tuple[str, ...]]
    unrecognised_dimension_keys: tuple[str, ...]


def statements_for(filing) -> Statements:
    """The filing's three statements as ordered lines, from its own structure.

    Reads the presentation linkbase for WHICH lines exist, their order, their
    level and the filer's label, and the calculation linkbase (as carried on
    each row) for `weight` and `calculation_parent`. Nothing here infers what
    a line MEANS from where it sits — presentation was measured unreliable for
    that and reliable for this (brief §Decision).

    `filing` need only answer `.xbrl()` with an object exposing
    `presentation_roles` and `get_statement(role)`; that two-call surface is
    the whole input contract, which is what lets the suite run offline against
    captured rows.
    """
    xbrl = filing.xbrl()

    candidates: dict[str, list[str]] = {}
    for role in xbrl.presentation_roles:
        role = str(role)
        kind = statement_kind(role)
        if kind is not None:
            candidates.setdefault(kind, []).append(role)

    by_kind: dict[str, list[Line]] = {}
    roles: dict[str, tuple[str, ...]] = {}
    unrecognised: set[str] = set()
    for kind, found in candidates.items():
        ordered = _roles_in_preference_order(found)
        roles[kind] = tuple(ordered)
        rows = list(xbrl.get_statement(ordered[0]))
        unrecognised |= _unrecognised_dimension_keys(rows)
        by_kind[kind] = [_line(row) for row in rows if _is_rendered_line(row)]

    return Statements(
        by_kind=by_kind,
        roles=roles,
        unrecognised_dimension_keys=tuple(sorted(unrecognised)),
    )


def _roles_in_preference_order(roles: list[str]) -> list[str]:
    """The candidate roles for one kind, best first.

    A role that ALSO names an out-of-scope statement sorts last: a combined
    income-and-comprehensive-income role carries comprehensive-income lines
    this arc does not want, so a pure income role is the better read of the
    same kind. Remaining ties break on the role URI — an arbitrary order, but
    a STABLE one, so two runs over one filing never disagree (never "whichever
    the role dict yielded first").

    Sorting is on the FOLDED role — its last path segment with case and
    punctuation dropped — because that is the only part of the URI the
    classifier reads, and a tie-break keyed on a different string than the
    rule it breaks ties for agrees with it only by coincidence of a shared
    domain prefix.

    THE MULTI-ROLE CASE IS UNOBSERVED. Across the five captured filings every
    kind had exactly ONE role, and Realty Income's ONLY income role is the
    combined one. That is asserted by
    `test_a_filing_declares_one_role_per_kind_in_the_captured_sample`, which
    RE-DERIVES it by running the live classifier over all 694 stored role URIs
    — cite the test, never a stored count. An earlier version of this sentence
    pointed at an `n_roles_per_kind` field that a later revision deleted for
    being a frozen classifier verdict; a load-bearing claim grounded on a
    pointer that can silently stop resolving is the defect this module's own
    docstring legislates against above. So this is a GUARD, not a measured
    policy: it exists to make the choice deterministic and to prefer the purer
    role IF a filing ever offers both, and it must never REJECT a combined
    role — doing so would erase the income statement of exactly the filer that
    motivated the rule. The plan states the preference as though the situation
    were observed; it was not, in this sample.
    """
    return sorted(roles, key=lambda role: (_names_another_statement(role), _fold(role)))


def _names_another_statement(role: str) -> bool:
    """True when the role's title also names a statement outside this arc's
    three — the combined `...OfIncomeAndComprehensiveIncome` shape. Derived
    from `_OTHER_STATEMENT_WORDINGS` via the same removal the classifier uses,
    so the two can never disagree about what "another statement" means."""
    folded = _fold(role)
    return _without_other_statement_wording(folded) != folded


def _is_rendered_line(row: dict[str, Any]) -> bool:
    """Is this row a line a reader would see on the statement?

    Two rejections, and the second is Task 3's own decision:

      * NOT A STATEMENT LINE — dimensional or placeholder, per
        `kpi_us_statement_lines.is_statement_line`, which is the single site
        for that judgement and is composed rather than re-implemented.
      * ABSTRACT — `us-gaap:IncomeStatementAbstract` and its kin reach here
        because the XBRL convention reserves `Abstract` for a header and the
        predicate above deliberately does not (plan Decision Log, Task 1 ->
        Task 3, item 1). They are EXCLUDED, not rendered. A header carries a
        section title but no fact, no period, no weight and no parent, so it
        would be a `Line` whose every field but `label` is empty. The
        arithmetic settles it: KO FY2017's income role is 80 rows less 49
        segment slices less 5 abstract rows (the section header plus the four
        `Table`/`Axis`/`Domain`/`LineItems` placeholders, which are abstract
        too) = the 26 the plan's acceptance counts. Rendering the header would
        make it 27.
    """
    return statement_lines.is_statement_line(row) and not row.get("is_abstract")


def _unrecognised_dimension_keys(rows: list[dict[str, Any]]) -> set[str]:
    """Dimension-ish keys these rows carry that this repo has never seen.

    A key counts only when it is TRUTHY on at least one row, because that is
    when it changes an answer: `is_statement_line` rejects a row for a truthy
    unrecognised "dim" key, so a newly-spelled CHILD descriptor (say
    `has_dimensioned_children`) would silently start deleting consolidated
    lines — the exact defect measured on KO FY2017, arriving by a new route.
    The predicate returns a bool and structurally cannot say so; assembly sees
    every row of every statement it reads, so it says so here.

    A key present but falsy everywhere is not reported: it rejected nothing,
    and a warning nobody can act on trains readers to ignore the channel.

    "Would this key reject the row?" is ASKED of the predicate rather than
    re-derived here. This function first re-implemented the comparison and got
    it subtly wrong — exact case against the predicate's `casefold()` — so a
    key spelled `Has_Dimension_Children` was exempted there and reported as
    unrecognised here: a false alarm on a channel whose entire value is being
    silent when nothing is wrong. What is left for this module to know is only
    which keys it has SEEN, which is a fact about the capture, not a rule.
    """
    seen = {key.casefold() for key in _SEEN_ROW_LEVEL_DIMENSION_KEYS}
    return {
        str(key) for row in rows for key, value in row.items()
        if value
        and statement_lines.is_row_level_dimension_signal(key)
        and str(key).casefold() not in seen
    }


def _line(row: dict[str, Any]) -> Line:
    """One row projected onto the six fields the brief asks a line to carry,
    plus the precision the filer declared (see `Line.decimals`).

    `values` and `decimals` are copied rather than aliased: the caller's `Line`
    must not change because someone downstream mutated the row it came from.
    """
    return Line(
        label=row.get("label"),
        concept=row.get("concept"),
        level=row.get("level"),
        weight=row.get("weight"),
        calculation_parent=row.get("calculation_parent"),
        values=dict(row.get("values") or {}),
        decimals=dict(row.get("decimals") or {}),
        balance=row.get("balance"),
    )
