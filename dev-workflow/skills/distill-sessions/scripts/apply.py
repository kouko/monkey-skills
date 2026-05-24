"""apply.py — approval-gated SKILL.md write-back for distill-sessions.

Per Plan Part 2 §Task 8: parses a proposal markdown file (produced by
`propose.py`) and applies the contained §"Proposed additions" + §"Proposed
modifications" to a target SKILL.md, atomically. Refuses to run without
`--approved` (brief Decision §"No silent writes") and refuses any path
under `references/` (brief Q4 — v0.1 SKILL.md only).

CLI:
    python -m apply --proposal <docs/skill-mining/<date>-<target>.md> \\
        --target-skill <path> --approved

Exit codes:
    0 = applied (or empty-proposal no-op).
    2 = approval gate not satisfied.
    3 = parse error / anchor mismatch / references/ refusal.

Stdlib only. No third-party deps.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Proposal-file format spec (apply.py-side; propose.py MUST match)
# ---------------------------------------------------------------------------
#
# # Skill mining proposals — <date> — <target-skill>
#
# ## Proposed additions
#
# ### Addition <n> [insert into §<Section Name>]
#
# ```
# <lines to insert verbatim>
# ```
#
# ## Proposed modifications
#
# ### Modification <n> [§<Section Name>]
#
# ```diff
# - old line 1
# - old line 2
# + new line 1
# + new line 2
# ```
#
# ## Marked for v0.2
#
# - <ignored by apply.py — bucketed for v0.2 reference-file proposals>
#
# Parser rules:
# - Section anchors are matched against the FIRST `## <Section Name>` heading
#   in the target SKILL.md (case-sensitive, trimmed).
# - Additions insert immediately BEFORE the next `## ` heading after the
#   anchor (or at file end if the anchor is the last section).
# - Modifications: every `- ` line in the diff block must EXACTLY match a
#   contiguous run of lines under the anchor's section (no fuzzy matching);
#   that run is replaced with the `+ ` lines, in order.
# - Empty §"Proposed additions" / §"Proposed modifications" → no-op success.
# - Any parse failure (missing anchor, mismatched `- ` lines, malformed
#   diff block) → exit 3, target untouched.


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class Addition:
    __slots__ = ("section", "lines")

    def __init__(self, section: str, lines: list[str]) -> None:
        self.section = section
        self.lines = lines


class Modification:
    __slots__ = ("section", "minus_lines", "plus_lines")

    def __init__(
        self,
        section: str,
        minus_lines: list[str],
        plus_lines: list[str],
    ) -> None:
        self.section = section
        self.minus_lines = minus_lines
        self.plus_lines = plus_lines


# ---------------------------------------------------------------------------
# Proposal parsing
# ---------------------------------------------------------------------------


_ADDITION_HEADING_RE = re.compile(
    r"^###\s+Addition\s+\d+\s+\[insert\s+into\s+§(?P<section>.+?)\]\s*$"
)
_MODIFICATION_HEADING_RE = re.compile(
    r"^###\s+Modification\s+\d+\s+\[§(?P<section>.+?)\]\s*$"
)


def _split_top_sections(text: str) -> dict[str, list[str]]:
    """Split a proposal markdown by `## ` headings into a section-name → lines
    dict. The leading H1 and any prelude are bucketed under key "" (ignored).
    """
    sections: dict[str, list[str]] = {"": []}
    current = ""
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            current = line[len("## "):].strip()
            sections[current] = []
        else:
            sections.setdefault(current, []).append(line)
    return sections


def _parse_fenced_block(lines: list[str], start_idx: int) -> tuple[list[str], int]:
    """Given lines and an index pointing at the opening ```fence (with or
    without info string), return (block_body_lines, index_after_close).
    Raises ValueError on unterminated block.
    """
    i = start_idx
    if i >= len(lines) or not lines[i].startswith("```"):
        raise ValueError(f"expected ``` fence at line {start_idx + 1}, got {lines[i] if i < len(lines) else 'EOF'!r}")
    i += 1
    body: list[str] = []
    while i < len(lines):
        if lines[i].startswith("```"):
            return body, i + 1
        body.append(lines[i])
        i += 1
    raise ValueError("unterminated fenced block")


def parse_additions(section_lines: list[str]) -> list[Addition]:
    """Parse §"Proposed additions" body lines into Addition[]."""
    additions: list[Addition] = []
    i = 0
    while i < len(section_lines):
        line = section_lines[i]
        m = _ADDITION_HEADING_RE.match(line)
        if not m:
            i += 1
            continue
        section_name = m.group("section").strip()
        # Advance to the next ``` fence.
        j = i + 1
        while j < len(section_lines) and not section_lines[j].startswith("```"):
            j += 1
        if j >= len(section_lines):
            raise ValueError(
                f"Addition for §{section_name}: no fenced block found"
            )
        body, after = _parse_fenced_block(section_lines, j)
        additions.append(Addition(section_name, body))
        i = after
    return additions


def parse_modifications(section_lines: list[str]) -> list[Modification]:
    """Parse §"Proposed modifications" body lines into Modification[]."""
    mods: list[Modification] = []
    i = 0
    while i < len(section_lines):
        line = section_lines[i]
        m = _MODIFICATION_HEADING_RE.match(line)
        if not m:
            i += 1
            continue
        section_name = m.group("section").strip()
        j = i + 1
        while j < len(section_lines) and not section_lines[j].startswith("```"):
            j += 1
        if j >= len(section_lines):
            raise ValueError(
                f"Modification for §{section_name}: no fenced diff block found"
            )
        body, after = _parse_fenced_block(section_lines, j)
        minus: list[str] = []
        plus: list[str] = []
        for diff_line in body:
            if diff_line.startswith("- "):
                minus.append(diff_line[2:])
            elif diff_line.startswith("-\t"):
                minus.append(diff_line[1:])
            elif diff_line.startswith("+ "):
                plus.append(diff_line[2:])
            elif diff_line.startswith("+\t"):
                plus.append(diff_line[1:])
            elif diff_line.strip() == "":
                # blank diff line — ignore (matches conventional unified diff).
                continue
            else:
                raise ValueError(
                    f"Modification for §{section_name}: unrecognized diff "
                    f"line {diff_line!r} (expected '- ' or '+ ' prefix)"
                )
        if not minus:
            raise ValueError(
                f"Modification for §{section_name}: diff block has no `- ` lines"
            )
        mods.append(Modification(section_name, minus, plus))
        i = after
    return mods


def parse_proposal(text: str) -> tuple[list[Addition], list[Modification]]:
    sections = _split_top_sections(text)
    additions_body = sections.get("Proposed additions", [])
    modifications_body = sections.get("Proposed modifications", [])
    return (
        parse_additions(additions_body),
        parse_modifications(modifications_body),
    )


# ---------------------------------------------------------------------------
# Target SKILL.md mutation
# ---------------------------------------------------------------------------


def _find_section_bounds(
    skill_lines: list[str], section_name: str
) -> tuple[int, int]:
    """Return (heading_line_index, end_index) for `## <section_name>`.

    end_index is the line index of the NEXT `## ` heading, or len(skill_lines)
    if the target section is the last one. Raises ValueError if not found.
    """
    target = f"## {section_name}".strip()
    start = -1
    for idx, line in enumerate(skill_lines):
        if line.strip() == target:
            start = idx
            break
    if start < 0:
        raise _AnchorMismatch(section_name)
    end = len(skill_lines)
    for idx in range(start + 1, len(skill_lines)):
        if skill_lines[idx].startswith("## ") and not skill_lines[idx].startswith("### "):
            end = idx
            break
    return start, end


class _AnchorMismatch(Exception):
    def __init__(self, section_name: str) -> None:
        super().__init__(f"anchor mismatch: §{section_name} not found in target SKILL.md")
        self.section = section_name


class _DiffMismatch(Exception):
    pass


def _apply_modification(
    skill_lines: list[str], mod: Modification
) -> list[str]:
    """Locate mod.minus_lines as a contiguous run inside the §<section>
    block of skill_lines and replace it with mod.plus_lines. Raises
    _DiffMismatch / _AnchorMismatch.
    """
    start, end = _find_section_bounds(skill_lines, mod.section)
    # Search inside (start+1, end) for a contiguous match of minus_lines.
    window = skill_lines[start + 1 : end]
    n = len(mod.minus_lines)
    if n == 0:
        return skill_lines
    match_at = -1
    for i in range(0, len(window) - n + 1):
        if window[i : i + n] == mod.minus_lines:
            match_at = i
            break
    if match_at < 0:
        raise _DiffMismatch(
            f"Modification for §{mod.section}: `- ` lines do not match "
            f"any contiguous run inside the section (no fuzzy matching at v0.1)"
        )
    abs_match = start + 1 + match_at
    return skill_lines[:abs_match] + mod.plus_lines + skill_lines[abs_match + n :]


def _apply_addition(
    skill_lines: list[str], add: Addition
) -> list[str]:
    """Insert add.lines immediately before the section's end (i.e. just
    before the next `## ` heading, or at EOF if last section). Inserts a
    leading blank line if the preceding non-blank line is not already blank.
    """
    start, end = _find_section_bounds(skill_lines, add.section)
    # `end` is the index of the next heading, or len(skill_lines).
    # Find the last non-blank line before `end` (within the section body) so we
    # know whether to prepend a separator blank line.
    insertion_at = end
    # Trim trailing blank lines off the section body so the insertion lands
    # adjacent to actual content rather than after a run of blanks.
    while insertion_at - 1 > start and skill_lines[insertion_at - 1].strip() == "":
        insertion_at -= 1
    # Build the inserted block: ensure a blank line separator before AND after.
    block: list[str] = []
    if insertion_at > start + 1 and skill_lines[insertion_at - 1].strip() != "":
        block.append("")
    block.extend(add.lines)
    # Ensure trailing blank line before the next heading.
    if insertion_at < len(skill_lines) and skill_lines[insertion_at].strip() != "":
        block.append("")
    return skill_lines[:insertion_at] + block + skill_lines[insertion_at:]


def apply_proposal_to_skill(
    skill_text: str,
    additions: Iterable[Addition],
    modifications: Iterable[Modification],
) -> str:
    """Pure function — applies modifications first (to keep `- ` line indices
    meaningful relative to the original text), then additions. Raises
    _AnchorMismatch / _DiffMismatch on any mismatch.
    """
    lines = skill_text.splitlines()
    for mod in modifications:
        lines = _apply_modification(lines, mod)
    for add in additions:
        lines = _apply_addition(lines, add)
    # Preserve trailing newline behavior of the input.
    suffix = "\n" if skill_text.endswith("\n") else ""
    return "\n".join(lines) + suffix


# ---------------------------------------------------------------------------
# Atomic write
# ---------------------------------------------------------------------------


def _atomic_write(target: Path, content: str) -> None:
    """Write `content` to a temp file in the same directory as `target`,
    fsync, then `Path.replace()` over the target (atomic on the same
    filesystem on POSIX + Windows).
    """
    target = target.resolve()
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path_str = tempfile.mkstemp(
        prefix=".apply-",
        suffix=".tmp",
        dir=str(parent),
    )
    tmp_path = Path(tmp_path_str)
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            import os
            os.fsync(f.fileno())
        tmp_path.replace(target)
    except BaseException:
        # Best-effort cleanup of the temp file on failure.
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------


def _is_under_references(path: Path) -> bool:
    """True if any path component (case-sensitive) equals 'references'.
    Per brief Q4: v0.1 writes SKILL.md only; references/* deferred to v0.2.
    """
    return "references" in path.parts


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="apply",
        description=(
            "Apply a mining proposal to a target SKILL.md "
            "(requires --approved per 'no silent writes')."
        ),
    )
    p.add_argument("--proposal", required=True, help="Path to proposal markdown file")
    p.add_argument("--target-skill", required=True, help="Path to target SKILL.md")
    p.add_argument(
        "--approved",
        action="store_true",
        help="Required acknowledgement that the proposal has been reviewed",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Gate 1: approval flag (BEFORE any file I/O — pure intent check).
    if not args.approved:
        print(
            "approval gate not satisfied — re-run with --approved after "
            "human review",
            file=sys.stderr,
        )
        return 2

    target_skill = Path(args.target_skill).resolve()
    proposal_path = Path(args.proposal).resolve()

    # Gate 2: refuse any path under references/.
    if _is_under_references(target_skill):
        print(
            f"refused write to {target_skill}: "
            "Q4: v0.1 SKILL.md only; references/*.md proposals require "
            "require_new_reference_file=true and are deferred to v0.2",
            file=sys.stderr,
        )
        return 3

    # Read inputs.
    try:
        proposal_text = proposal_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"proposal file not found: {e}", file=sys.stderr)
        return 3
    try:
        skill_text = target_skill.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"target SKILL.md not found: {e}", file=sys.stderr)
        return 3

    # Parse.
    try:
        additions, modifications = parse_proposal(proposal_text)
    except ValueError as e:
        print(f"proposal parse error: {e}", file=sys.stderr)
        return 3

    # Empty proposal → no-op success (still exit 0).
    if not additions and not modifications:
        return 0

    # Apply (pure transformation, no I/O on failure).
    try:
        new_text = apply_proposal_to_skill(skill_text, additions, modifications)
    except _AnchorMismatch as e:
        print(str(e), file=sys.stderr)
        return 3
    except _DiffMismatch as e:
        print(str(e), file=sys.stderr)
        return 3

    # No-op short circuit if pure transformation produced no change.
    if new_text == skill_text:
        return 0

    # Atomic write.
    try:
        _atomic_write(target_skill, new_text)
    except OSError as e:
        print(f"atomic write failed: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
