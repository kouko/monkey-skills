"""Validate a loom-spec INTENT LAYER root's TOP-altitude MODEL.md.

The intent layer is the persistent spec root (e.g. `docs/loom/spec/`). Its
TOP-altitude `MODEL.md` carries the cross-cutting model — the invariants,
object state machines, and out-of-scope boundary that span capabilities.

This module checks the TOP MODEL.md SKELETON only (required sections are
present, not content quality), mirroring `validate_spec_output.py`'s
structure-only behavior: extra/unknown sections are tolerated, never rejected.

`check_top_model(spec_dir) -> list[str]` grades a MODEL.md that EXISTS,
returning one problem message per MISSING required section. When MODEL.md
is ABSENT it returns [] — absence is the aggregator's concern in a later
task, not this check's.

`check_mid_readmes(spec_dir) -> list[str]` checks the MID altitude: each
IMMEDIATE sub-directory of `spec_dir` is a capability dir whose per-
capability intent doc is `README.md`. It returns one problem message per
capability dir that lacks a README.md. A spec_dir with no capability
subdirs (or a non-existent spec_dir) returns [].

Required canonical TOP sections (exact header text, whole-line match):
- ## Invariants
- ## Object state machines
- ## Out of scope

Design mirrors validate_spec_output.py: a `_section_body`-style
whole-header-line regex match (so a `## Invariants` substring in prose does
NOT count), and the `list[str]` problem-message contract (each message names
the missing section + the file path).

Stdlib only.
"""

from __future__ import annotations

import re
from pathlib import Path

# Required canonical TOP-altitude sections of MODEL.md, in declaration order.
_TOP_SECTIONS = (
    "## Invariants",
    "## Object state machines",
    "## Out of scope",
)

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


def check_top_model(spec_dir: Path) -> list[str]:
    """Grade the TOP-altitude MODEL.md at `spec_dir/MODEL.md`.

    Returns one problem message per MISSING required section. A MODEL.md with
    all required sections returns []. When MODEL.md does not exist, returns []
    (absence is the aggregator's concern, not this check's).
    """
    spec_dir = Path(spec_dir)
    model = spec_dir / "MODEL.md"
    if not model.is_file():
        return []
    text = model.read_text(encoding="utf-8")
    problems: list[str] = []
    for header in _TOP_SECTIONS:
        if _section_body(text, header) is None:
            problems.append(
                f"missing '{header}' section in {model} "
                f"(a TOP-altitude MODEL.md needs the cross-cutting "
                f"{header.lstrip('# ').lower()})")
    return problems


def check_mid_readmes(spec_dir: Path) -> list[str]:
    """Check that every MID-altitude capability dir has a README.md.

    Each IMMEDIATE sub-directory of `spec_dir` is a capability dir whose
    per-capability intent doc is `README.md`. Returns one problem message
    per capability dir that lacks one. A spec_dir with no capability subdirs,
    or a non-existent spec_dir, returns [] (absence is the aggregator's
    concern, not this check's).
    """
    spec_dir = Path(spec_dir)
    if not spec_dir.is_dir():
        return []
    problems: list[str] = []
    for cap in sorted(p for p in spec_dir.iterdir() if p.is_dir()):
        if not (cap / "README.md").is_file():
            problems.append(
                f"missing README.md in capability '{cap.name}' ({cap}) "
                f"(a MID-altitude capability dir needs a README.md intent doc)")
    return problems
