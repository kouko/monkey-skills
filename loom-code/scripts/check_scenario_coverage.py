#!/usr/bin/env python3
"""Compare a loom-spec change-folder's `#### Scenario:` set against a
writing-plans plan's join keys, and name every dropped scenario.

Inputs (positional CLI args):

    check_scenario_coverage.py <change-folder> <plan-path>

- `<change-folder>` is a `docs/loom/<change-id>/` directory in the shape
  `loom-spec/scripts/validate_spec_output.py` validates: `specs/<capability>/
  spec.md` delta files, each containing `### Requirement:` blocks that each
  contain one or more `#### Scenario:` headers. The heading regexes here
  reuse that exact grammar (`^###\\s+Requirement:` / `^####\\s+Scenario:`),
  only adding capture groups for the name text — not a new variant.
- `<plan-path>` is a writing-plans plan (`docs/loom/plans/...`). Per
  `loom-code/skills/writing-plans/references/plan-format.md`, a task's
  `Brief item covered` field MAY be the stable join key
  `<change-id> / Requirement: <name> / Scenario: <name>` (referent kind (b)).

The script builds the full scenario-key set from the change-folder, the
covered-key set from the plan's join keys, and reports the difference:

    exit 0 — every change-folder scenario is covered (or the folder is
             vacuous — zero scenarios — in which case a note says so).
    exit 1 — one or more scenarios are dropped; each dropped key is printed
             on stderr, one per line, agent-actionable.

A malformed plan (no join keys found at all — e.g. all `Brief item covered`
values are prose referents, or the field is absent, or the plan file itself
is missing) is treated as zero coverage: every change-folder scenario is
reported dropped. Every `Brief item covered` value that does not parse as a
join key is additionally named on stderr with its task, so a mistyped key is
distinguishable from a genuinely uncited scenario; it is a warning, not an
error, because a prose referent is legal on this path.

Brief mode is the second input path, selected by `--brief`:

    check_scenario_coverage.py --brief <brief-path> <plan-path>

It takes no change-folder — a brief-only plan has none — and answers a
different question: does every task's `Brief item covered` value resolve
against a `BI-<n>` identifier the brief declares? An unresolvable value is
an ERROR (exit 1) naming the task and quoting the value, because there the
grammar is unambiguous: the brief HAS identifiers, so a value naming none of
them is a defect rather than a legal prose referent. The one exception is a
well-formed change-folder join key (referent kind (b)): `plan-format.md`
declares it legal for this same field, so it is warned about — legal here,
contributes no coverage in this mode — rather than failing a gate a
correctly authored plan must pass. The legal
no-requirement value `none — <reason>` passes through; its reason is
mandatory, so a bare `none`, an empty reason or a whitespace-only one is
itself an error naming the task. A brief declaring no
identifiers at all is a legacy brief: the quote referent stays legal, no
resolution is attempted, and the run says so on stdout rather than exiting 0
in silence. The two modes are selected, never combined.

Stdlib only, plus the sibling `adjudication_split` for its CommonMark fence
scan (`iter_lines_outside_fences`) — this file runs as a script, so the
sibling resolves off `sys.path[0]`, its own directory.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from adjudication_split import iter_lines_outside_fences

# Same underlying heading grammar as validate_spec_output.py's
# `_REQUIREMENT_HDR` (`^###\s+Requirement:`) and the pattern
# `_first_scenario_block` matches (`^####\s+Scenario:.*$`) — these add a
# capture group for the name text, they do not change the grammar.
_REQUIREMENT_HDR = re.compile(r"^###\s+Requirement:\s*(.*)$", re.MULTILINE)
_SCENARIO_HDR = re.compile(r"^####\s+Scenario:\s*(.*)$", re.MULTILINE)

# A requirement's scope ends at the next header of level 2-3 (a sibling
# `### Requirement:`, or a higher-level `##` section heading) — `####`
# stays excluded here because that is the `#### Scenario:` level itself,
# which must stay INSIDE the requirement's scope (unlike
# validate_spec_output.py's `_ANY_HEADER = re.compile(r"^#{2,4}\s")`, used
# there to slice a single scenario's own body up to its next header).
# What we DO take from that SSOT regex: single-# is excluded, so a
# `# comment` inside an example code fence in a scenario body isn't
# mistaken for a boundary. Sharing that grammar also means sharing its
# known limitation: a `##`/`###`-prefixed line inside a fenced code block
# (e.g. a markdown example) is still mistaken for a real header, same as
# upstream.
_SECTION_BOUNDARY = re.compile(r"^#{2,3}\s", re.MULTILINE)

# writing-plans' `Brief item covered` field line (bold or not, per
# plan-format.md's canonical schema uses `**Brief item covered**:` but
# real plans in this repo write the plain `- Brief item covered:` form).
_BRIEF_ITEM_LINE = re.compile(
    r"^\s*-\s*(?:\*\*)?Brief item covered(?:\*\*)?\s*:\s*(.+)$", re.MULTILINE)

# The stable join key grammar itself: `<change-id> / Requirement: <name> /
# Scenario: <name>`, tolerant of optional surrounding quote/backtick chars.
_JOIN_KEY = re.compile(
    r"^[\"'`]?\s*(?P<change_id>.+?)\s*/\s*Requirement:\s*(?P<req>.+?)\s*/\s*"
    r"Scenario:\s*(?P<scen>.+?)\s*[\"'`]?$")

# Any markdown heading — used only to name which task an unparsed
# `Brief item covered` value sits under. Same known limitation as
# `_SECTION_BOUNDARY` above, and wider: a `#`-prefixed line inside a fenced
# code block (e.g. a `# comment` in a python example, or a markdown example's
# `## heading`) is still mistaken for a real heading — and unlike that regex,
# single-# is INCLUDED here, so a plan's code fences can mis-name the task.
# Tolerable at this call site: the value is only a label in a diagnostic
# message, never a key, so a wrong label misdirects a reader but changes no
# coverage result and no exit code.
_HEADING = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

# A brief item declaration, per `loom-code/skills/brainstorming/references/
# handoff-brief-format.md` §Brief item identifiers: the identifier FIRST on
# its line (an optional list marker aside), then the item's human-readable
# text on the same line. The form is the literal `BI`, a hyphen, a decimal
# number — that section names `BI1`, `bi-1` and `B-1` as explicitly not the
# form, hence the mandatory hyphen, the case-sensitive prefix and the `\b`
# that stops `BI-1x` matching. Identifier-first is what keeps a prose
# mention ("see BI-2 above") from reading as a second declaration.
_BRIEF_ITEM_DECL = re.compile(r"^\s*(?:[-*+]\s+)?(BI-\d+)\b(?P<text>.*)$")

# A `BI-<n>` citation inside a `Brief item covered` value. Same form as
# `_BRIEF_ITEM_DECL`'s identifier, but matched ANYWHERE in the value rather
# than identifier-first: a value legally carries the id plus the item's text
# (`BI-1 — items carry an identifier`), backticks (`` `BI-2` ``), or two ids
# for a task delivering two items. Position-anchoring is a declaration-side
# rule — it keeps a prose mention from reading as a second declaration —
# and has no counterpart here, where a mention IS the citation.
_BI_CITATION = re.compile(r"\bBI-\d+\b")

# The no-requirement value `none — <reason>` (plan-format.md §`Brief item
# covered`). The whole value is matched, not just its opening word, because
# the reason is what makes the value legal: `reason` is None for a bare
# `none` and blank for an empty or whitespace-only one, and the caller
# rejects all three the same way, with one message. Capturing the reason RAW
# (the trailing `\s*` sits outside the group) is what leaves that blank test
# to the caller instead of deciding it here.
#
# The separator is a separator, not a glyph: an em-dash, an en-dash, or a
# plain hyphen all introduce the reason. The hyphen needs whitespace on BOTH
# sides, though (or nothing at all after it, which is the reason-less form
# the caller rejects by name). Spaced only in front, it is still English's
# word-joiner: `none -of-a-kind` reads as the same prose as `none-of-a-kind`,
# one stray keystroke apart, so accepting it would hand out the escape for a
# typo — the accidental opt-out the mandatory reason exists to prevent. The
# dashes are never word-joiners and need no space.
#
# The three glyphs above are the whole separator set. A dash-alike the
# format does not name — U+2212 MINUS SIGN, U+FF0D FULLWIDTH HYPHEN-MINUS
# (what a CJK IME emits for `-`) — is deliberately NOT one, so its author is
# told to retype rather than granted an opt-out on a glyph nobody ruled on.
# Fail-closed: a value that matches nothing here (that, or prose like `none
# of the brief items apply`) falls through to ordinary resolution, where it
# fails loudly as the unresolvable citation it is, with the value quoted.
_NONE_VALUE = re.compile(
    r"^[\"'`]?\s*none(?:(?P<sep>\s*[–—]|\s+-(?=\s|$))(?P<reason>.*?))?"
    r"[\"'`]?\s*$",
    re.IGNORECASE)

# The CommonMark fence scan itself is imported, not re-derived: this module
# and `adjudication_split` ask the same question of the same grammar — which
# lines are ordinary prose rather than fenced illustration — and each used to
# carry its own copy of the state machine AND of `FENCE_RE`. A differential
# test across the CommonMark edge cases (nested longer fence, `~~~` against
# backticks, a 3-space-indented fence, a 4-space-indented non-fence, an
# unterminated fence, a closing fence longer than its opener) found the two
# identical on every one, so there was no divergent-tolerance case to
# protect — only two copies to keep in step. The seam is
# `adjudication_split.iter_lines_outside_fences`, tested there.


def _requirement_scenario_pairs(text: str) -> list[tuple[str, str]]:
    """(requirement name, scenario name) pairs found in one delta file's
    text, per validate_spec_output.py's heading grammar."""
    pairs: list[tuple[str, str]] = []
    for req_match in _REQUIREMENT_HDR.finditer(text):
        req_name = req_match.group(1).strip()
        start = req_match.end()
        boundary = _SECTION_BOUNDARY.search(text, start)
        end = boundary.start() if boundary else len(text)
        body = text[start:end]
        for scen_match in _SCENARIO_HDR.finditer(body):
            pairs.append((req_name, scen_match.group(1).strip()))
    return pairs


def _delta_files(change_folder: Path) -> list[Path]:
    specs = change_folder / "specs"
    if not specs.is_dir():
        return []
    return sorted(specs.rglob("*.md"))


def collect_folder_scenario_keys(change_folder: Path, change_id: str) -> set[str]:
    """Every `<change-id> / Requirement: <name> / Scenario: <name>` join key
    the change-folder's specs/ delta files define.

    Duplicate (requirement, scenario) name pairs collapse into one set
    entry — the join-key grammar is fixed (per the plan), so occurrence
    indices can't be added to disambiguate. Instead, a duplicate is
    flagged with a warning on stderr naming the key, so an uncovered
    duplicate instance is at least visible rather than silently
    undetectable.
    """
    keys: set[str] = set()
    occurrences: dict[str, int] = {}
    for delta in _delta_files(change_folder):
        text = delta.read_text(encoding="utf-8")
        for req_name, scen_name in _requirement_scenario_pairs(text):
            key = f"{change_id} / Requirement: {req_name} / Scenario: {scen_name}"
            occurrences[key] = occurrences.get(key, 0) + 1
            keys.add(key)
    for key, count in occurrences.items():
        if count > 1:
            print(f"Warning: duplicate scenario key seen {count} times "
                  f"(coverage can't distinguish instances) — {key}", file=sys.stderr)
    return keys


def _enclosing_heading(plan_text: str, pos: int) -> str:
    """The nearest markdown heading above `pos` — i.e. the task a
    `Brief item covered` field belongs to. Empty string when the field
    sits above every heading."""
    nearest = ""
    for hdr in _HEADING.finditer(plan_text):
        if hdr.start() >= pos:
            break
        nearest = hdr.group(1).strip()
    return nearest


def collect_plan_join_keys(plan_text: str) -> set[str]:
    """Every join key referenced by a `Brief item covered` field in the
    plan. A `Brief item covered` line whose value is prose (referent kind
    (a), not the join-key grammar) contributes nothing — that is the
    malformed-plan / zero-coverage case.

    Every such non-contributing value is named on stderr with its task and
    its verbatim text. It is reported, never an error: on this path a
    prose quote IS a legal referent kind, so an unparsed value cannot be
    told apart from a typo, and erroring would punish the legal form. What
    is being fixed is the silence — dropping the value outright made a
    mistyped citation read as 'this scenario has no task', which is a
    different repair from 'this citation did not parse'. Exit-code
    semantics are unchanged: coverage alone decides them.
    """
    keys: set[str] = set()
    unparsed: list[tuple[str, str]] = []
    for line_match in _BRIEF_ITEM_LINE.finditer(plan_text):
        value = line_match.group(1).strip()
        m = _JOIN_KEY.match(value)
        if m is None:
            unparsed.append(
                (_enclosing_heading(plan_text, line_match.start()), value))
            continue
        keys.add(f"{m.group('change_id')} / Requirement: {m.group('req')} / "
                  f"Scenario: {m.group('scen')}")
    for heading, value in unparsed:
        where = heading or "(no enclosing heading)"
        print(f"Warning: 'Brief item covered' value under '{where}' is not the "
              f"join-key grammar, so it contributes no coverage — a prose "
              f"referent is legal here, a mistyped key is not. Value: {value}",
              file=sys.stderr)
    return keys


def collect_brief_item_ids(brief_text: str) -> dict[str, int]:
    """Every `BI-<n>` identifier the brief declares, mapped to the 1-based
    line number of the line declaring it.

    Nothing on the CLI path calls this yet — the brief-mode check that
    consumes it is wired at the gate in a later step of this change.

    Declarations are collected wherever they appear, not from a list of
    section names. `handoff-brief-format.md` §Brief item identifiers names
    `## Smallest End State`, `## What Becomes Obsolete` and `## Decision` as
    the known in-scope set, and in the same breath tells an author to extend
    that list when a brief carries another outcome-declaring section. A
    three-section allowlist would silently drop exactly the items that
    extension clause exists to admit.

    Identifiers inside a fenced code block are illustration, never
    declaration. The convention section demonstrates the form inside a
    ```markdown fence and its `## Template` nests a whole brief skeleton
    carrying example identifiers, so a brief that pastes that skeleton would
    otherwise gain items no task can deliver — and a downstream citation
    would resolve against the example instead of failing loudly.

    A brief declaring zero identifiers returns an empty mapping rather than
    raising: that is a legal legacy brief written before the convention, and
    the empty result is what puts the caller into legacy mode.

    When one identifier is declared twice (an authoring error the
    never-reused rule forbids), the first declaring line wins. The reuse is
    reported on stderr naming the identifier and both declaring lines, so
    the author can find the pair — resolving an authoring error the
    docstring calls an error, in silence, left the second declaration
    indistinguishable from a line the collector never saw.
    """
    declared: dict[str, int] = {}
    duplicates: list[tuple[str, int, int]] = []
    for offset, line in iter_lines_outside_fences(brief_text):
        decl = _BRIEF_ITEM_DECL.match(line)
        if decl is None or not decl.group("text").strip():
            continue
        # The generator reports a byte offset, but the diagnostic below is
        # read against a text editor, so the line NUMBER is what an author
        # needs. Counted here rather than tracked in the generator because
        # a declaration is rare — a handful per brief — while the scan
        # visits every line.
        lineno = brief_text.count("\n", 0, offset) + 1
        item_id = decl.group(1)
        if item_id in declared:
            duplicates.append((item_id, declared[item_id], lineno))
            continue
        declared[item_id] = lineno
    for item_id, first, repeat in duplicates:
        print(f"Warning: brief item {item_id} is declared twice — line {first} "
              f"and line {repeat}; the never-reused rule forbids reuse, so the "
              f"line {first} declaration wins.", file=sys.stderr)
    return declared


def resolve_plan_brief_citations(
    plan_text: str, declared: dict[str, int]
) -> list[str]:
    """One error message per `Brief item covered` value that resolves
    against none of the brief's `declared` identifiers.

    Called only when the brief declares at least one identifier. There the
    grammar is unambiguous — the brief HAS ids, so a value that names none
    of them is a defect, not a legal prose referent — which is why this
    path errors while `collect_plan_join_keys` only reports. That asymmetry
    is deliberate: on the change-folder path a prose quote is a legal
    referent kind and cannot be told apart from a typo, so erroring there
    would punish the legal form.

    Three shapes are not errors. A value citing only declared ids resolves,
    obviously; `none — <reason>`, the legal no-requirement value, is
    passed through untouched — a task delivering no brief outcome must not
    be forced into a false citation; and a well-formed change-folder join
    key (referent kind (b)) is warned about on stderr rather than erroring,
    because it is a legal value for this same field that simply answers a
    different question.

    That third tolerance is what keeps a legal plan shippable. `plan-format.
    md` declares kinds (a), (b) and (c) all legal for `Brief item covered`,
    and `writing-plans/SKILL.md` fires brief mode on any brief declaring
    `BI-` ids — change-folder or not — so a change carrying both a brief and
    a change-folder reaches this check with both kinds in one plan. Erroring
    there blocked a mandatory gate on a correctly authored plan, with no
    bypass: the `Notes`-approval escape covers coverage drops, not citation
    errors. Fail-closed is the right instinct against AMBIGUITY, and a value
    matching the join-key grammar is not ambiguous — it is the mirror of the
    tolerance `collect_plan_join_keys` already extends to prose referents on
    the other path, warned for the same reason: a value contributing nothing
    must say so, or a mistyped key reads as an item no task delivers.

    The tolerance is deliberately reachable only when the value cites NO
    identifier at all. A value carrying an undeclared id AND the join-key
    grammar (`BI-99 / Requirement: … / Scenario: …`) keeps erroring on the
    undeclared id, so the typo path stays fully closed — the shape this
    tolerates is the one the reviewer reproduced, not every string the
    grammar happens to accept.

    The reason is what makes that value legal, so a reason-less one is an
    error here rather than a pass-through: a bare `none`, an empty reason
    and a whitespace-only reason are the escape with its justification
    deleted, which reads as authorised to every downstream reader while
    saying nothing. That is the silent opt-out the mandatory reason exists
    to prevent, and it gets its own diagnostic — routing it through the
    cites-nothing message below would tell an author who wrote the value
    deliberately to go add an identifier they correctly decided not to
    cite.
    """
    errors: list[str] = []
    for line_match in _BRIEF_ITEM_LINE.finditer(plan_text):
        value = line_match.group(1).strip()
        where = (_enclosing_heading(plan_text, line_match.start())
                 or "(no enclosing heading)")
        none_match = _NONE_VALUE.match(value)
        if none_match is not None:
            reason = none_match.group("reason")
            if reason is not None and reason.strip():
                continue
            errors.append(
                f"Error: 'Brief item covered' under '{where}' is the "
                f"no-requirement value with no reason — the reason is what "
                f"keeps `none` from being a silent opt-out, so write "
                f"`none — <why this task delivers no brief item>`. "
                f"Value: {value}")
            continue
        cited = _BI_CITATION.findall(value)
        unknown = [item_id for item_id in cited if item_id not in declared]
        if cited and not unknown:
            continue
        if not cited:
            if _JOIN_KEY.match(value):
                print(f"Warning: 'Brief item covered' under '{where}' is a "
                      f"change-folder join key, which is a legal referent kind "
                      f"here but resolves against no brief item, so it "
                      f"contributes no coverage in brief mode — run the "
                      f"change-folder check for it. Value: {value}",
                      file=sys.stderr)
                continue
            errors.append(
                f"Error: 'Brief item covered' under '{where}' cites no BI-<n> "
                f"identifier, but the brief declares them — so this value "
                f"resolves to nothing. Value: {value}")
        else:
            errors.append(
                f"Error: 'Brief item covered' under '{where}' cites "
                f"{', '.join(unknown)}, which the brief does not declare. "
                f"Value: {value}")
    return errors


def brief_item_coverage(plan_text: str, declared: dict[str, int]) -> set[str]:
    """The declared identifiers cited by at least one task's `Brief item
    covered` value.

    Coverage is per item and BOOLEAN: one citation discharges an item, and
    the result says which items got one — never how many tasks cited them,
    nor which. The tally is therefore of items, never of citations: an item
    cited by two tasks is one covered item, which is what keeps a brief
    delivered half by one task and half by another (the shape the experiment
    behind this change found) from reading as two items' worth of progress.

    This returned a `dict[str, set[str]]` of citing task headings until a
    mutation test found the union unobservable — replacing it with
    last-write-wins left every test green, because the sole consumer asks
    only whether an item's set is empty. The heading set was computed,
    stored and never read; deleting it removes a third `_enclosing_heading`
    scan of the plan and leaves CLI output byte-identical (verified across
    the shared-item, repeated-heading, none-value, join-key and
    no-heading-at-all shapes).

    What that forecloses, recorded because it was a judgment and not an
    oversight: a future consumer asking "delivered by >= 2 DISTINCT tasks"
    would need the citing tasks back. It would need a stabler key than the
    heading anyway — two identically-titled headings are a real authoring
    case this scheme could not tell apart — so the discarded shape was not
    the one such a consumer would have reused.

    Only declared identifiers are credited. A value citing an id the brief
    does not declare resolves to nothing and is `resolve_plan_brief_
    citations`' error to raise; crediting it here would let a typo cover an
    item that has no coverage at all.
    """
    covered: set[str] = set()
    for line_match in _BRIEF_ITEM_LINE.finditer(plan_text):
        value = line_match.group(1).strip()
        covered.update(item_id for item_id in _BI_CITATION.findall(value)
                       if item_id in declared)
    return covered


def check_brief_coverage(brief_path: Path, plan_path: Path) -> int:
    """Brief mode: resolve every task's `Brief item covered` value against
    the identifiers the brief declares. Returns the process exit code.

    A brief declaring zero identifiers is a legal legacy brief, written
    before the convention existed: the quote referent stays legal and no
    resolution is attempted. That outcome is ANNOUNCED rather than passed
    silently, because a silent exit 0 is indistinguishable from a checked
    one — a brief that merely forgot to declare identifiers would otherwise
    read as fully resolved.
    """
    if not brief_path.is_file():
        print(f"Error: brief file not found at {brief_path}.", file=sys.stderr)
        return 1
    brief_text = brief_path.read_text(encoding="utf-8")
    declared = collect_brief_item_ids(brief_text)
    if not declared:
        print(f"Legacy mode: {brief_path} declares no BI-<n> identifiers, so no "
              f"citation in {plan_path} was resolved — this run checked nothing. "
              f"Declare identifiers in the brief to enable the check.")
        return 0

    if not plan_path.is_file():
        print(f"Error: plan file not found at {plan_path}.", file=sys.stderr)
        return 1
    plan_text = plan_path.read_text(encoding="utf-8")

    errors = resolve_plan_brief_citations(plan_text, declared)
    for message in errors:
        print(message, file=sys.stderr)

    # The reverse direction, reported on both exit paths: a plan whose one
    # bad citation fails the run still owes its author the whole picture,
    # and computing it only on the way to exit 0 would hide it exactly when
    # the plan is being edited. Declaration order, so the report reads in
    # the order the brief does.
    covered = brief_item_coverage(plan_text, declared)
    uncovered = [item_id for item_id in
                 sorted(declared, key=lambda item: declared[item])
                 if item_id not in covered]
    for item_id in uncovered:
        print(f"Warning: uncovered brief item {item_id} — declared at line "
              f"{declared[item_id]} of {brief_path}, cited by no task's "
              f"'Brief item covered' value in {plan_path}.", file=sys.stderr)
    print(f"Brief item coverage: {len(declared) - len(uncovered)} of "
          f"{len(declared)} declared identifier(s) cited by at least one task "
          f"in {plan_path}.")

    if errors:
        return 1
    print(f"Every 'Brief item covered' value in {plan_path} resolves against the "
          f"{len(declared)} identifier(s) declared in {brief_path}.")
    return 0


def check_coverage(
    change_folder: Path, plan_path: Path
) -> tuple[bool, list[str], str]:
    """Returns (ok, dropped_keys_sorted, note).

    `note` is a human-facing status line for the vacuous-empty-folder case
    or the missing-plan-file case; empty string when neither applies.
    """
    change_id = change_folder.name or change_folder.resolve().name
    folder_keys = collect_folder_scenario_keys(change_folder, change_id)
    if not folder_keys:
        return True, [], (
            f"No '#### Scenario:' headers found under {change_folder} — "
            f"vacuously covered (nothing to drop)."
        )

    note = ""
    if not plan_path.is_file():
        note = f"Note: plan file not found at {plan_path} — treating as zero coverage."
        plan_text = ""
    else:
        plan_text = plan_path.read_text(encoding="utf-8")

    plan_keys = collect_plan_join_keys(plan_text)
    dropped = sorted(folder_keys - plan_keys)
    return (not dropped), dropped, note


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare a loom-spec change-folder's '#### Scenario:' "
                    "set against a writing-plans plan's join keys; exit 1 "
                    "naming every dropped scenario."
    )
    parser.add_argument("change_folder", nargs="?",
                        help="path to the loom-spec change-folder "
                             "(omit in brief mode)")
    parser.add_argument("plan_path", help="path to the writing-plans plan file")
    parser.add_argument("--brief", help="path to the source brainstorming brief; "
                                        "selects brief mode, where each task's "
                                        "'Brief item covered' value is resolved "
                                        "against the brief's declared BI-<n> ids")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan_path)

    # The two modes read different inputs and answer different questions, so
    # they are selected, never combined: passing both would silently run one
    # of the two checks the caller asked for.
    if args.brief is not None:
        if args.change_folder is not None:
            parser.error("--brief selects brief mode, which takes no "
                         "<change-folder>; run the two checks as two "
                         "invocations")
        return check_brief_coverage(Path(args.brief), plan_path)
    if args.change_folder is None:
        parser.error("a <change-folder> is required unless --brief selects "
                     "brief mode")

    change_folder = Path(args.change_folder)

    ok, dropped, note = check_coverage(change_folder, plan_path)
    if note:
        print(note)

    if ok:
        if not note:
            print(f"Full coverage: every scenario under {change_folder} is "
                  f"mapped by a task in {plan_path}.")
        return 0

    print(f"Dropped scenario(s) — not covered by any task's 'Brief item "
          f"covered' field in {plan_path}:", file=sys.stderr)
    for key in dropped:
        print(f"  - {key}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
