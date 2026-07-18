"""Validate a loom-spec OUTPUT DIRECTORY against the OpenSpec change-folder
skeleton.

Spec-toolkit emits a directory in OpenSpec change-folder *shape* (plain
markdown, no OpenSpec CLI dependency):

    <output-dir>/
      proposal.md
      specs/<capability>/spec.md   # delta: ## ADDED / MODIFIED / REMOVED Requirements ...

This module checks the SKELETON only (structure, not content quality),
mirroring `openspec validate`'s structure-only behavior: extra/unknown
sections are tolerated, never rejected.

It also checks loom-spec's ADDITIVE sections in proposal.md (## USM
backbone, ## OOUX object model, ## Provenance, ## Blind spots — needs
human/field input, ## Path × edge matrix) — the differentiating richness
that OpenSpec's structure-only validate tolerates.

Design: each check is a function (root: Path) -> list[str] of problem
messages (empty == ok). `_SKELETON_CHECKS` is the skeleton registry;
`_ADDITIVE_CHECKS` is the additive registry of the same shape. `validate()`
runs both groups.

CLI: `python validate_spec_output.py <output-dir>` -> exit 0 if valid,
exit 1 with agent-actionable messages on stderr if invalid.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# RFC-2119 keyword on a requirement body line (word-boundary, case-sensitive
# per OpenSpec convention that the normative keyword is uppercase).
_RFC2119 = re.compile(r"\b(MUST|SHALL|SHOULD|MAY)\b")

# A requirements block opens with ADDED / MODIFIED / REMOVED — an OpenSpec
# change may add, modify, or remove. Accept any of the three as a valid block
# opener; gating the delta on ADDED alone walled off MODIFIED/REMOVED changes.
_REQ_BLOCK_HDR = re.compile(
    r"^##\s+(?:ADDED|MODIFIED|REMOVED)\s+Requirements\s*$", re.MULTILINE)
_REQUIREMENT_HDR = re.compile(r"^###\s+Requirement:", re.MULTILINE)

# Knowledge-triage `evidence_needed:` tag (docs/loom/BACKLOG.md §knowledge-
# triage v2.1 cut (a); doctrine in spec-expansion/references/domain-tag-
# triage.md). Pinned bucket vocabulary — any other value is a weak-executor
# invention (real failure: leg-1 haiku dogfood emitted `technical-constraint`
# / `audit-log-format`, see docs/loom/dogfood/2026-07-18-knowledge-triage-
# live-spec-leg.md).
_EVIDENCE_NEEDED = re.compile(
    r"evidence_needed:\s*([A-Za-z]+(?:-[A-Za-z]+)*)")
_EVIDENCE_WHITELIST = {"craft", "domain-convention", "project-local"}
_TIER_LABELS = ("SHAPING", "DEFERRABLE")
_DEFERRED_REASON = re.compile(r"deferred:\s*(\S[^\n]*)")

# Structural scoping for the tier-label / deferred-reason checks below
# (round 2 — replaces a fixed ±200-char window that round-1 review proved
# unsound on real acceptance data: it produced strong-leg false positives
# when the governing SHAPING lead-in sat >200 chars from a far list item,
# strong-leg false negatives when an adjacent DEFERRABLE paragraph's header
# leaked backward into range, and cross-tag compliance borrowing — a
# sibling item's tier label or `deferred:` reason satisfying THIS item's
# check purely because it happened to sit within radius).
#
# A tag's OWN SCOPE is its list item (bounded by the next top-level
# `\d+.`/`-`/`*` marker, a blank-line paragraph break, or a heading) or,
# outside lists, its paragraph (the same blank-line/heading-bounded block).
# A tag's GOVERNING HEADER is the immediately preceding block, but only
# when that block is itself a heading line or its last non-blank line ends
# with ':' (a lead-in) — i.e. the block that visibly introduces this one.
# Check (2) accepts a tier label found in OWN SCOPE *or* GOVERNING HEADER;
# check (3) requires `deferred:` in OWN SCOPE only — a governing header or a
# sibling item's `deferred:` note never satisfies it.
#
# Known accepted limitation: explanatory prose that quotes
# `evidence_needed: domain-convention` inside an OUTPUT artifact (e.g. a
# worked example in a comment) is indistinguishable from a real tag and can
# still trip check (2)/(3) — writers are expected to tag open questions,
# not quote the doctrine verbatim inside proposal.md/spec.md. This is a
# known false-positive surface, not a claim that the checks never
# false-positive.

_HEADING_LINE = re.compile(r"^#{1,6}\s")
_ITEM_MARKER = re.compile(r"^(?:\d+\.|[-*])[ \t]", re.MULTILINE)


def _blocks(text: str) -> list[tuple[int, int]]:
    """Partition `text` into (start, end) char-offset blocks: a maximal run
    of non-blank lines, with each heading line forming its own single-line
    block. Blank lines and heading lines are the boundaries that end a tag's
    OWN SCOPE and that GOVERNING HEADER lookup steps across."""
    blocks: list[tuple[int, int]] = []
    cur_start: int | None = None
    pos = 0
    for line in text.splitlines(keepends=True):
        start = pos
        pos += len(line)
        if not line.strip():
            if cur_start is not None:
                blocks.append((cur_start, start))
                cur_start = None
            continue
        if _HEADING_LINE.match(line):
            if cur_start is not None:
                blocks.append((cur_start, start))
                cur_start = None
            blocks.append((start, pos))
            continue
        if cur_start is None:
            cur_start = start
    if cur_start is not None:
        blocks.append((cur_start, pos))
    return blocks


def _item_scope_bounds(text: str, block_start: int, block_end: int,
                        pos: int) -> tuple[int, int]:
    """OWN SCOPE bounds for `pos` within the block [block_start, block_end):
    if the block contains top-level list-item markers, the item containing
    `pos` (bounded by the next marker or block_end); otherwise the whole
    block (a plain paragraph)."""
    starts = sorted(m.start() for m in
                     _ITEM_MARKER.finditer(text, block_start, block_end))
    if not starts:
        return block_start, block_end
    idx = None
    for i, s in enumerate(starts):
        if s <= pos:
            idx = i
        else:
            break
    if idx is None:
        return block_start, block_end
    end = starts[idx + 1] if idx + 1 < len(starts) else block_end
    return starts[idx], end


def _governing_header_text(text: str, blocks: list[tuple[int, int]],
                            index: int) -> str:
    """GOVERNING HEADER text for the block at `blocks[index]`: the
    immediately preceding block, if it is a heading line or its last
    non-blank line ends with ':' (a lead-in); otherwise ''."""
    if index == 0:
        return ""
    prev_start, prev_end = blocks[index - 1]
    prev_text = text[prev_start:prev_end]
    if _HEADING_LINE.match(prev_text):
        return prev_text
    lines = [ln for ln in prev_text.splitlines() if ln.strip()]
    if lines and lines[-1].rstrip().endswith(":"):
        return prev_text
    return ""


def _tag_context(text: str, pos: int) -> tuple[str, str]:
    """(own_scope, governing_header) text for a tag match starting at
    `pos`."""
    blocks = _blocks(text)
    for i, (bstart, bend) in enumerate(blocks):
        if bstart <= pos < bend:
            own_start, own_end = _item_scope_bounds(text, bstart, bend, pos)
            # Glued lead-in FIRST — the nearest governor wins: a
            # colon-terminated lead-in (or heading) written DIRECTLY above
            # its list with no blank line lives inside the SAME block, so
            # it never becomes a preceding block for
            # _governing_header_text; and when it exists it sits closer to
            # the item than any preceding block does.
            header = ""
            first_item = _ITEM_MARKER.search(text, bstart, bend)
            if (first_item and first_item.start() > bstart
                    and pos >= first_item.start()):
                lead = text[bstart:first_item.start()]
                lead_lines = [ln for ln in lead.splitlines() if ln.strip()]
                if lead_lines and (
                        lead_lines[-1].rstrip().endswith(":")
                        or _HEADING_LINE.match(lead)):
                    header = lead
            if not header:
                header = _governing_header_text(text, blocks, i)
            return text[own_start:own_end], header
    return "", ""


def _delta_files(root: Path) -> list[Path]:
    specs = root / "specs"
    if not specs.is_dir():
        return []
    return sorted(specs.rglob("*.md"))


# --- skeleton checks: each returns list[str] of problems (empty == ok) ------

def _check_proposal(root: Path) -> list[str]:
    if not (root / "proposal.md").is_file():
        return [f"missing proposal.md at {root / 'proposal.md'} "
                f"(every change folder needs a proposal.md)"]
    return []


def _check_specs_dir(root: Path) -> list[str]:
    specs = root / "specs"
    if not specs.is_dir():
        return [f"missing specs/ subdirectory at {specs} "
                f"(put delta spec files under specs/<capability>/spec.md)"]
    if not _delta_files(root):
        return [f"specs/ at {specs} contains no *.md delta files "
                f"(add at least one delta, e.g. specs/<capability>/spec.md)"]
    return []


def _check_requirements_block(root: Path) -> list[str]:
    # Note (KNOWN EDGE, out of scope): a pure '## REMOVED Requirements' delta
    # with NO scenarios still fails _check_scenario_given_when_then below — a
    # removal may legitimately have no scenario. That is a separate, deeper
    # decision; this check only makes ADDED/MODIFIED/REMOVED reachable as a
    # valid block opener.
    deltas = _delta_files(root)
    if not deltas:
        return []  # already reported by _check_specs_dir
    if any(_REQ_BLOCK_HDR.search(d.read_text(encoding="utf-8")) for d in deltas):
        return []
    return [f"no delta under {root / 'specs'} contains a "
            f"'## ADDED Requirements' / '## MODIFIED Requirements' / "
            f"'## REMOVED Requirements' header "
            f"(one of these opens the block OpenSpec parses)"]


def _check_requirement_with_rfc2119(root: Path) -> list[str]:
    deltas = _delta_files(root)
    if not deltas:
        return []
    for d in deltas:
        text = d.read_text(encoding="utf-8")
        for m in _REQUIREMENT_HDR.finditer(text):
            # Inspect the requirement's body: lines after the header up to the
            # next header (### or ####) or the next blank-line block.
            body = _slice_until_next_header(text, m.end())
            if _RFC2119.search(body):
                return []
    return [f"no '### Requirement:' under {root / 'specs'} carries an "
            f"RFC-2119 keyword (MUST / SHALL / SHOULD / MAY) on its body line "
            f"(state the normative obligation, e.g. 'The system MUST ...')"]


def _check_scenario_given_when_then(root: Path) -> list[str]:
    deltas = _delta_files(root)
    if not deltas:
        return []
    for d in deltas:
        block = _first_scenario_block(d.read_text(encoding="utf-8"))
        if block is not None:
            upper = block.upper()
            missing = [kw for kw in ("GIVEN", "WHEN", "THEN") if kw not in upper]
            if not missing:
                return []
            return [f"'#### Scenario:' in {d} is missing "
                    f"{', '.join(missing)} line(s) "
                    f"(each scenario needs GIVEN / WHEN / THEN)"]
    return [f"no '#### Scenario:' header found under {root / 'specs'} "
            f"(each requirement needs >=1 scenario with GIVEN/WHEN/THEN)"]


# --- additive checks: loom-spec's differentiating richness ---------------
# Per the brief, the OpenSpec delta under specs/ stays pure (openspec-validate
# clean); the additive sections live in proposal.md. These checks therefore
# read proposal.md. Tolerant of extra content, like the skeleton checks.

_SEC_USM_BACKBONE = "## USM backbone"
_SEC_OOUX_OBJECT_MODEL = "## OOUX object model"
_SEC_PROVENANCE = "## Provenance"
_SEC_BLIND_SPOTS = "## Blind spots — needs human/field input"
_SEC_PATH_EDGE_MATRIX = "## Path × edge matrix"
_SEC_CROSS_OBJECT_COMBINATIONS = "## Cross-object combinations"
_SEC_JOURNEY_NAVIGATION = "## Journey navigation"

_H2 = re.compile(r"^##\s", re.MULTILINE)


def _section_body(text: str, header: str) -> str | None:
    """Body of the `## <header>` section (lines after the header line up to the
    next `## ` header or end), or None if the header is absent. Match is on a
    whole header line so a substring in prose never counts."""
    pat = re.compile(r"^" + re.escape(header) + r"\s*$", re.MULTILINE)
    m = pat.search(text)
    if m is None:
        return None
    nxt = _H2.search(text, m.end())
    return text[m.end():nxt.start()] if nxt else text[m.end():]


def _check_usm_backbone_section(root: Path) -> list[str]:
    proposal = root / "proposal.md"
    if not proposal.is_file():
        return []  # already reported by _check_proposal
    if _section_body(proposal.read_text(encoding="utf-8"),
                     _SEC_USM_BACKBONE) is None:
        return [f"missing '{_SEC_USM_BACKBONE}' section in {proposal} "
                f"(Phase ① artifact — make the USM backbone visible)"]
    return []


def _check_ooux_object_model_section(root: Path) -> list[str]:
    proposal = root / "proposal.md"
    if not proposal.is_file():
        return []  # already reported by _check_proposal
    if _section_body(proposal.read_text(encoding="utf-8"),
                     _SEC_OOUX_OBJECT_MODEL) is None:
        return [f"missing '{_SEC_OOUX_OBJECT_MODEL}' section in {proposal} "
                f"(Phase ② artifact — make the OOUX object model visible)"]
    return []


def _check_provenance_section(root: Path) -> list[str]:
    proposal = root / "proposal.md"
    if not proposal.is_file():
        return []  # already reported by _check_proposal
    if _section_body(proposal.read_text(encoding="utf-8"), _SEC_PROVENANCE) is None:
        return [f"missing '{_SEC_PROVENANCE}' section in {proposal} "
                f"(tag each item seeded / inferred / critic-found)"]
    return []


def _check_blind_spots_section(root: Path) -> list[str]:
    proposal = root / "proposal.md"
    if not proposal.is_file():
        return []  # already reported by _check_proposal
    body = _section_body(proposal.read_text(encoding="utf-8"), _SEC_BLIND_SPOTS)
    if body is None:
        return [f"missing '{_SEC_BLIND_SPOTS}' section in {proposal} "
                f"(the critic's load-bearing output — list what needs "
                f"human/field input)"]
    if not any(line.strip() for line in body.splitlines()):
        return [f"'{_SEC_BLIND_SPOTS}' section in {proposal} is empty "
                f"(it MUST list >=1 blind spot; an empty section means the "
                f"critic produced nothing)"]
    return []


def _check_path_edge_matrix_section(root: Path) -> list[str]:
    proposal = root / "proposal.md"
    if not proposal.is_file():
        return []  # already reported by _check_proposal
    if _section_body(proposal.read_text(encoding="utf-8"),
                     _SEC_PATH_EDGE_MATRIX) is None:
        return [f"missing '{_SEC_PATH_EDGE_MATRIX}' section in {proposal} "
                f"(the path/edge coverage appendix)"]
    return []


def _check_cross_object_combinations_section(root: Path) -> list[str]:
    proposal = root / "proposal.md"
    if not proposal.is_file():
        return []  # already reported by _check_proposal
    if _section_body(proposal.read_text(encoding="utf-8"),
                     _SEC_CROSS_OBJECT_COMBINATIONS) is None:
        return [f"missing '{_SEC_CROSS_OBJECT_COMBINATIONS}' section in {proposal} "
                f"(L2 artifact — make cross-object combinations visible)"]
    return []


def _check_journey_navigation_section(root: Path) -> list[str]:
    proposal = root / "proposal.md"
    if not proposal.is_file():
        return []  # already reported by _check_proposal
    if _section_body(proposal.read_text(encoding="utf-8"),
                     _SEC_JOURNEY_NAVIGATION) is None:
        return [f"missing '{_SEC_JOURNEY_NAVIGATION}' section in {proposal} "
                f"(L3 artifact — make journey navigation visible)"]
    return []


# --- evidence_needed tag checks (Task 14, cut (a)) --------------------------
# Mechanize the knowledge-triage enforcement semantics that prose-only
# instructions did not survive weak execution on (the 3-leg dogfood):
# schema discipline (whitelist), tiering (SHAPING/DEFERRABLE presence), and
# the VERIFY gate rule (SHAPING requires an explicit deferred: reason).
# Runs on OUTPUT dirs only (proposal.md + specs/**/spec.md) — never on skill
# sources, so the doctrine reference file's own prose (which uses
# `evidence_needed: domain-convention` as a worked example without a nearby
# tier label) is never fed through these checks and can never false-positive.

def _target_files(root: Path) -> list[Path]:
    """proposal.md + every specs/**/*.md delta — the two artifact layers the
    knowledge-triage tag doctrine applies to."""
    files: list[Path] = []
    proposal = root / "proposal.md"
    if proposal.is_file():
        files.append(proposal)
    files.extend(_delta_files(root))
    return files


def _line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _domain_convention_matches(text: str) -> list[re.Match]:
    return [m for m in _EVIDENCE_NEEDED.finditer(text)
            if m.group(1) == "domain-convention"]


def _scan_domain_convention_tags(root: Path, predicate) -> list[str]:
    """Shared scan shell for the structural-scope checks below.
    `predicate(file, own_scope, governing_header, match, text) -> str | None`
    returns a problem message or None."""
    problems = []
    for f in _target_files(root):
        text = f.read_text(encoding="utf-8")
        for m in _domain_convention_matches(text):
            own_scope, header = _tag_context(text, m.start())
            problem = predicate(f, own_scope, header, m, text)
            if problem:
                problems.append(problem)
    return problems


def _check_evidence_needed_whitelist(root: Path) -> list[str]:
    problems = []
    for f in _target_files(root):
        text = f.read_text(encoding="utf-8")
        for m in _EVIDENCE_NEEDED.finditer(text):
            value = m.group(1)
            if value not in _EVIDENCE_WHITELIST:
                problems.append(
                    f"{f}:{_line_no(text, m.start())}: evidence_needed: "
                    f"{value} is not in the pinned bucket vocabulary "
                    f"(craft | domain-convention | project-local) — see "
                    f"spec-expansion/references/domain-tag-triage.md")
    return problems


def _check_domain_convention_tier_label(root: Path) -> list[str]:
    def predicate(f, own_scope, header, m, text):
        if any(label in own_scope or label in header for label in _TIER_LABELS):
            return None
        return (f"{f}:{_line_no(text, m.start())}: evidence_needed: "
                f"domain-convention has no SHAPING or DEFERRABLE tier "
                f"label nearby (two-tier triage required — see "
                f"domain-tag-triage.md §Two-tier triage)")
    return _scan_domain_convention_tags(root, predicate)


def _check_shaping_without_deferred(root: Path) -> list[str]:
    def predicate(f, own_scope, header, m, text):
        if "SHAPING" not in own_scope and "SHAPING" not in header:
            return None  # DEFERRABLE, or untiered (already reported above)
        dm = _DEFERRED_REASON.search(own_scope)  # OWN SCOPE only — never
        if dm and dm.group(1).strip():           # borrowed from a sibling
            return None                          # item or the header
        return (f"{f}:{_line_no(text, m.start())}: SHAPING-class "
                f"evidence_needed: domain-convention has no 'deferred: "
                f"<reason>' note — this blocks VERIFY per the "
                f"domain-tag-triage.md gate rule (spec-expansion SKILL.md "
                f"§Gate rule) unless explicitly deferred with a reason")
    return _scan_domain_convention_tags(root, predicate)


# --- text helpers -----------------------------------------------------------

_ANY_HEADER = re.compile(r"^#{2,4}\s", re.MULTILINE)


def _slice_until_next_header(text: str, start: int) -> str:
    """Body from `start` up to the next ##/###/#### header (or end)."""
    nxt = _ANY_HEADER.search(text, start)
    return text[start:nxt.start()] if nxt else text[start:]


def _first_scenario_block(text: str) -> str | None:
    """Return the body of the first `#### Scenario:` header up to the next
    header, or None if there is no scenario."""
    for m in re.finditer(r"^####\s+Scenario:.*$", text, re.MULTILINE):
        return _slice_until_next_header(text, m.end())
    return None


# --- check registry (Task 3 appends an additive group here) -----------------

_SKELETON_CHECKS = [
    _check_proposal,
    _check_specs_dir,
    _check_requirements_block,
    _check_requirement_with_rfc2119,
    _check_scenario_given_when_then,
]

# loom-spec's additive richness, beyond the openspec-clean skeleton.
# The three-flow artifacts (USM backbone / OOUX object model / Path × edge
# matrix) make each expansion phase visible; Provenance + Blind spots carry
# the critic's load-bearing output.
_ADDITIVE_CHECKS = [
    _check_usm_backbone_section,
    _check_ooux_object_model_section,
    _check_provenance_section,
    _check_blind_spots_section,
    _check_path_edge_matrix_section,
    _check_cross_object_combinations_section,
    _check_journey_navigation_section,
]

# Knowledge-triage `evidence_needed:` tag checks (Task 14, cut (a)).
_EVIDENCE_TAG_CHECKS = [
    _check_evidence_needed_whitelist,
    _check_domain_convention_tier_label,
    _check_shaping_without_deferred,
]


def validate(root: Path) -> tuple[bool, list[str]]:
    """Run all checks against the output directory `root`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    root = Path(root)
    problems: list[str] = []
    if not root.is_dir():
        return False, [f"output directory does not exist: {root}"]
    for check in _SKELETON_CHECKS + _ADDITIVE_CHECKS + _EVIDENCE_TAG_CHECKS:
        problems.extend(check(root))
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a loom-spec output directory against the "
                    "OpenSpec change-folder skeleton.")
    parser.add_argument("output_dir", help="path to the loom-spec output directory")
    args = parser.parse_args(argv)

    ok, problems = validate(Path(args.output_dir))
    if ok:
        print(f"OK: {args.output_dir} conforms to the OpenSpec skeleton.")
        return 0
    print(f"INVALID: {args.output_dir} does not conform to the OpenSpec skeleton.",
          file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
