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


def validate(root: Path) -> tuple[bool, list[str]]:
    """Run all checks against the output directory `root`.

    Returns (ok, problems). ok is True iff problems is empty.
    """
    root = Path(root)
    problems: list[str] = []
    if not root.is_dir():
        return False, [f"output directory does not exist: {root}"]
    for check in _SKELETON_CHECKS + _ADDITIVE_CHECKS:
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
