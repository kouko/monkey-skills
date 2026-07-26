#!/usr/bin/env python3
"""kpi_us_statement_shape.py — classify one XBRL role URI as one of the three
statements (pure-compute, plan Task 2,
docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md).

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

Naming the exception, rather than writing "EVERY entry", is deliberate: this
docstring said "every" for one round while `tables` already contradicted it 32
lines below, which is the same defect the sibling module's mirroring claim and
this module's own fixture-provenance note each shipped once
(docs/loom/memory/unifying-a-normalization-has-a-scope.md). A universal claim
with a live counter-example is worse than no claim: the next reader trusts the
rule and deletes the thing the rule was never meant to cover.

NOTHING HERE INFERS MEANING FROM A LINE'S POSITION (brief §Decision): this
reads the role's NAME, which is what names are for. Which lines the role
carries, and what they mean, is decided elsewhere.

SELECTING AMONG ROLES IS NOT THIS FUNCTION'S JOB. A filing offering both a
pure income role and a combined income-and-comprehensive one must prefer the
pure one — but that is a choice BETWEEN roles and belongs to the assembly
step (plan Task 3), which is the only caller that sees a filing's whole role
set. Per-role classification stays total and order-free here.

PURE FUNCTION of the role string — stdlib only, no I/O.
"""
from __future__ import annotations

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
