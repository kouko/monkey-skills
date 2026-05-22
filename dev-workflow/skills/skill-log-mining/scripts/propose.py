"""propose.py — merge subagent Memory Item outputs → markdown diff renderer.

Stage 3 of skill-log-mining v0.1. Reads a JSON list of subagent results
(one per session, each containing a list of Trace2Skill Memory Items),
dedups near-identical Items via Title + content overlap heuristic, then
renders a structured markdown proposal file with three sections:

- §"Proposed additions" — kind=success items, tagged
  ``[insert into §<section-anchor>]``.
- §"Proposed modifications" — kind=failure items, rendered as fenced
  ```diff blocks with plain ``- `` / ``+ `` line pairs. Format is
  defined by apply.py's parser (apply.py:32-69 is the source of
  truth): no unified-diff headers (``--- a/`` / ``+++ b/`` / hunk
  ``@@``), only ``- `` (old line) / ``+ `` (new line) lines inside
  the fenced ``diff`` block. propose.py emits these so apply.py's
  contiguous-run matcher can locate the old lines and substitute the
  new ones in the target SKILL.md.
- §"Marked for v0.2" — any item with ``requires_new_reference_file: true``
  (per Q4 of the v0.1 brief: SKILL.md only, new-file proposals deferred).

**No write to target SKILL.md** — this module is read-only against the
target. Only writes the proposals markdown file. The apply.py module
(T8) is the one with write authority.

CLI:

    python -m propose \\
        --input <subagent_results.json> \\
        --target-skill <path/to/SKILL.md> \\
        --output <docs/skill-mining/YYYY-MM-DD-target.md>

Subagent results JSON schema (one entry per session)::

    [
        {
            "session_id": "...",
            "target_skill_path": "/path/to/SKILL.md",
            "memory_items": [
                {
                    "title": "...",
                    "description": "...",
                    "content": "...",
                    "kind": "failure" | "success",
                    "section_anchor": "Examples",          // optional
                    "requires_new_reference_file": false   // optional
                }
            ]
        }
    ]

Per Plan Part 2 §Task 7.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

# SequenceMatcher.ratio() threshold for "this title is essentially the same
# as that other title". 0.85 picked to tolerate punctuation / minor wording
# differences (Trace2Skill prompts produce slight variants across sessions)
# while still rejecting genuinely-different titles. Pair-wise on small N is
# fine — we never have more than O(20) Memory Items per run.
_TITLE_SIMILARITY_THRESHOLD = 0.85

# Secondary check: when two titles match by ratio, also require content
# overlap above this threshold before declaring a dedup. Prevents collapsing
# items that happen to share a generic title but describe different
# scenarios.
_CONTENT_SIMILARITY_THRESHOLD = 0.50

_DEFAULT_SECTION_ANCHOR = "Examples"


# ---------------------------------------------------------------------------
# Memory Item normalization.
# ---------------------------------------------------------------------------


def normalize_memory_item(raw: dict) -> dict:
    """Fill in optional Memory Item fields with safe defaults.

    Required keys: ``title``, ``description``, ``content``, ``kind``.
    Optional keys (with defaults): ``section_anchor`` (= "Examples"),
    ``requires_new_reference_file`` (= False).

    Returns a new dict; does not mutate ``raw``.
    """
    return {
        "title": str(raw.get("title", "")).strip(),
        "description": str(raw.get("description", "")).strip(),
        "content": str(raw.get("content", "")).strip(),
        "kind": str(raw.get("kind", "failure")).strip().lower(),
        "section_anchor": str(
            raw.get("section_anchor") or _DEFAULT_SECTION_ANCHOR
        ).strip(),
        "requires_new_reference_file": bool(
            raw.get("requires_new_reference_file", False)
        ),
        # Carry session context for traceability in rendered output.
        "_source_session": raw.get("_source_session", ""),
    }


def extract_memory_items(results: list[dict]) -> list[dict]:
    """Flatten subagent results into a single list of Memory Items.

    Each result entry has a ``memory_items`` array; we walk all entries and
    return one flat list with each item normalized + tagged with its source
    session id (for traceability in rendered output).
    """
    flat: list[dict] = []
    for entry in results:
        session_id = entry.get("session_id", "unknown")
        for raw_item in entry.get("memory_items", []):
            item = normalize_memory_item({**raw_item, "_source_session": session_id})
            flat.append(item)
    return flat


# ---------------------------------------------------------------------------
# Dedup — Title + content overlap heuristic.
# ---------------------------------------------------------------------------


def _similarity(a: str, b: str) -> float:
    """SequenceMatcher.ratio() on whitespace-collapsed lowercase strings."""
    a_norm = " ".join(a.lower().split())
    b_norm = " ".join(b.lower().split())
    return difflib.SequenceMatcher(a=a_norm, b=b_norm).ratio()


def _items_are_near_duplicates(item_a: dict, item_b: dict) -> bool:
    """Two items merge when Title ratio ≥ threshold AND content overlaps.

    Title-only matching would over-aggregate when the same anti-pattern
    title shows up in two genuinely-different scenarios. Content-only
    matching is too noisy because Trace2Skill items rephrase content per
    session. Requiring BOTH keys reduces both false-positive and
    false-negative dedups.
    """
    title_ratio = _similarity(item_a["title"], item_b["title"])
    if title_ratio < _TITLE_SIMILARITY_THRESHOLD:
        return False
    content_ratio = _similarity(item_a["content"], item_b["content"])
    return content_ratio >= _CONTENT_SIMILARITY_THRESHOLD


def dedup_items(items: list[dict]) -> list[dict]:
    """Collapse near-identical Memory Items via pair-wise Title + content
    similarity.

    Greedy single-pass: for each item, check whether it merges with any
    already-kept item. If yes, drop the new item (the kept one wins —
    first-seen by input order). Order-preserving.

    Two items only merge when BOTH:
    - title SequenceMatcher ratio ≥ ``_TITLE_SIMILARITY_THRESHOLD`` (0.85)
    - content SequenceMatcher ratio ≥ ``_CONTENT_SIMILARITY_THRESHOLD`` (0.50)

    Returns a new list; does not mutate input.
    """
    kept: list[dict] = []
    for item in items:
        if any(_items_are_near_duplicates(item, k) for k in kept):
            continue
        kept.append(item)
    return kept


# ---------------------------------------------------------------------------
# v0.2 partition.
# ---------------------------------------------------------------------------


def partition_by_v02_marker(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split items into (main, v02).

    Items with ``requires_new_reference_file: True`` go to v02 (per Q4 of
    the v0.1 brief — new reference files defer to v0.2).
    """
    main: list[dict] = []
    v02: list[dict] = []
    for item in items:
        if item["requires_new_reference_file"]:
            v02.append(item)
        else:
            main.append(item)
    return main, v02


# ---------------------------------------------------------------------------
# Section extraction from target SKILL.md.
# ---------------------------------------------------------------------------


def _extract_section(skill_md: str, section_anchor: str) -> str:
    """Return the body of the named section from a SKILL.md string.

    Matches ``## <section_anchor>`` (any heading level) up to the next
    heading of equal-or-lower depth. Match is CASE-SENSITIVE to align
    with apply.py's `_find_section_bounds` (apply.py:240-247) which
    uses `line.strip() == target`; emitting a different-cased anchor
    here would make apply.py refuse the proposal with an anchor
    mismatch. Returns empty string when not found — modifications
    against missing sections still render but the diff body has only
    `+ ` lines (apply.py will then refuse to apply because the diff
    block has no `- ` lines — that surfaces the problem rather than
    silently no-op'ing).
    """
    lines = skill_md.splitlines()
    # Find heading line.
    heading_idx = None
    heading_depth = None
    target = section_anchor.strip()
    for i, line in enumerate(lines):
        stripped = line.lstrip("#")
        depth = len(line) - len(stripped)
        if depth == 0 or not line.startswith("#"):
            continue
        if stripped.strip() == target:
            heading_idx = i
            heading_depth = depth
            break
    if heading_idx is None or heading_depth is None:
        return ""

    # Collect body until next heading of depth ≤ heading_depth.
    body_lines: list[str] = []
    for line in lines[heading_idx + 1:]:
        if line.startswith("#"):
            stripped = line.lstrip("#")
            other_depth = len(line) - len(stripped)
            if other_depth <= heading_depth:
                break
        body_lines.append(line)
    return "\n".join(body_lines).strip("\n") + "\n"


# ---------------------------------------------------------------------------
# Markdown rendering.
# ---------------------------------------------------------------------------


def _render_addition(item: dict, index: int) -> list[str]:
    """Render one kind=success item under §Proposed additions.

    Heading format MUST match apply.py's _ADDITION_HEADING_RE
    (apply.py:104-106): ``### Addition <N> [insert into §<section>]``.
    The Memory Item's freeform Title is NOT in the heading — it
    becomes a bolded first line of the fenced block body so apply.py
    inserts it verbatim into the target section.

    ``index`` is the 1-indexed counter scoped to additions in this
    proposal (Additions and Modifications counters are independent).
    """
    body_lines: list[str] = []
    if item["title"]:
        body_lines.append(f"**{item['title']}**")
        body_lines.append("")
    if item["description"]:
        body_lines.append(f"_{item['description']}_")
        body_lines.append("")
    body_lines.append(item["content"])
    if item.get("_source_session"):
        body_lines.append("")
        body_lines.append(f"_source session: `{item['_source_session']}`_")

    lines = [
        f"### Addition {index} [insert into §{item['section_anchor']}]",
        "",
        "```",
    ]
    lines.extend(body_lines)
    lines.append("```")
    lines.append("")
    return lines


def _render_modification(item: dict, index: int, skill_md: str) -> list[str]:
    """Render one kind=failure item under §Proposed modifications.

    Heading format MUST match apply.py's _MODIFICATION_HEADING_RE
    (apply.py:107-109): ``### Modification <N> [§<section>]``. Body
    is a fenced ``diff`` block containing only ``- `` (old line) and
    ``+ `` (new line) pairs — no unified-diff headers and no
    space-prefixed context lines (apply.py:191-207 only accepts
    ``- `` / ``+ `` / blank lines).

    The "old lines" are extracted from the named SKILL.md section
    (whole section body, each non-blank line). The "new lines"
    repeat the old lines, then append item.content as guidance — so
    apply.py replaces the matched contiguous run with old+new
    content, which preserves the original lines while adding the new
    guidance. When the section is empty or missing, no `- ` lines
    can be emitted; we surface that by inserting a sentinel `- `
    line based on the section anchor itself, so apply.py refuses
    with a clear DiffMismatch — better than silently no-op'ing.

    ``index`` is the 1-indexed counter scoped to modifications in
    this proposal.
    """
    current_section = _extract_section(skill_md, item["section_anchor"])
    minus_lines = [ln for ln in current_section.splitlines() if ln.strip()]

    if minus_lines:
        # Replace the section's existing non-blank lines with themselves +
        # the new guidance appended (preserves prior content, adds new
        # text below).
        plus_lines = list(minus_lines)
        plus_lines.append("")
        plus_lines.append(item["content"])
    else:
        # Section is empty or missing. Emit a single sentinel `- ` line
        # so apply.py raises DiffMismatch with a clear anchor — better
        # than a silent no-op.
        minus_lines = [f"<missing or empty section: §{item['section_anchor']}>"]
        plus_lines = [item["content"]]

    lines = [
        f"### Modification {index} [§{item['section_anchor']}]",
        "",
    ]
    if item["title"] or item["description"]:
        if item["title"]:
            lines.append(f"**{item['title']}**")
        if item["description"]:
            lines.append(f"_{item['description']}_")
        lines.append("")
    lines.append("```diff")
    for ml in minus_lines:
        lines.append(f"- {ml}")
    for pl in plus_lines:
        lines.append(f"+ {pl}")
    lines.append("```")
    if item.get("_source_session"):
        lines.append("")
        lines.append(f"_source session: `{item['_source_session']}`_")
    lines.append("")
    return lines


def _render_v02_item(item: dict) -> list[str]:
    """Render one v0.2-bucket item under §Marked for v0.2."""
    lines = [
        f"### {item['title']}",
        f"_{item['description']}_" if item["description"] else "",
        "",
        f"**Target section**: §{item['section_anchor']}",
        f"**Kind**: {item['kind']}",
        "**Deferred to v0.2**: requires new reference file (per Q4 — v0.1 is SKILL.md only).",
        "",
        item["content"],
    ]
    if item.get("_source_session"):
        lines.append("")
        lines.append(f"_source session: `{item['_source_session']}`_")
    lines.append("")
    return lines


def render_proposals_markdown(
    items: list[dict],
    *,
    target_skill_path: str,
    target_skill_md_content: str,
    run_date: str | None = None,
) -> str:
    """Render the full proposals markdown file as a string.

    Args:
        items: Memory Items (already normalized + deduped). Caller may pre-
            dedup; the renderer also dedups defensively to keep test
            ergonomics simple.
        target_skill_path: path to the target SKILL.md (rendered in header
            for human reviewers).
        target_skill_md_content: current SKILL.md text (used to compute
            unified-diff against for modifications).
        run_date: optional ``YYYY-MM-DD`` override; default = today UTC.

    Returns the markdown document as a single string.
    """
    if run_date is None:
        run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    deduped = dedup_items(items)
    main, v02 = partition_by_v02_marker(deduped)

    additions = [it for it in main if it["kind"] == "success"]
    modifications = [it for it in main if it["kind"] == "failure"]

    parts: list[str] = []
    parts.append(f"# skill-log-mining proposals — {run_date}")
    parts.append("")
    parts.append(f"**Target SKILL.md**: `{target_skill_path}`")
    parts.append(
        f"**Counts**: {len(additions)} addition(s), "
        f"{len(modifications)} modification(s), {len(v02)} deferred to v0.2."
    )
    parts.append("")
    parts.append(
        "> No silent writes — review the proposals below, then run "
        "`python -m apply --approved ...` to commit the diff."
    )
    parts.append("")

    parts.append("## Proposed additions")
    parts.append("")
    if additions:
        for n, item in enumerate(additions, start=1):
            parts.extend(_render_addition(item, n))
    else:
        parts.append("_(none)_")
        parts.append("")

    parts.append("## Proposed modifications")
    parts.append("")
    if modifications:
        for n, item in enumerate(modifications, start=1):
            parts.extend(_render_modification(item, n, target_skill_md_content))
    else:
        parts.append("_(none)_")
        parts.append("")

    parts.append("## Marked for v0.2")
    parts.append("")
    if v02:
        parts.append(
            "_These proposals require new reference files; per Q4 of the v0.1 "
            "brief, defer them to a future iteration._"
        )
        parts.append("")
        for item in v02:
            parts.extend(_render_v02_item(item))
    else:
        parts.append("_(none)_")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _load_subagent_results(path: Path) -> list[dict]:
    text = path.read_text()
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(
            f"expected top-level JSON list in {path}, got {type(data).__name__}"
        )
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="propose",
        description=(
            "Merge skill-log-mining subagent Memory Items into a markdown "
            "proposal file. Does NOT write to the target SKILL.md."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to subagent results JSON (list of {session_id, memory_items}).",
    )
    parser.add_argument(
        "--target-skill",
        required=True,
        type=str,
        help="Path to the target SKILL.md (read-only — rendered in proposal header).",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Where to write the proposal markdown file.",
    )
    parser.add_argument(
        "--skill-content-file",
        type=Path,
        default=None,
        help=(
            "Optional override path to read the SKILL.md text from. Defaults "
            "to --target-skill. Useful for tests / dry-runs where the target "
            "path is symbolic."
        ),
    )
    parser.add_argument(
        "--run-date",
        type=str,
        default=None,
        help="Override run date (YYYY-MM-DD); default = today UTC.",
    )
    args = parser.parse_args(argv)

    results = _load_subagent_results(args.input)
    items = extract_memory_items(results)

    # Read SKILL.md text — from --skill-content-file if provided, else from
    # --target-skill. In production --target-skill IS the path to read; the
    # override exists for tests where target is symbolic.
    content_path = args.skill_content_file or Path(args.target_skill)
    if content_path.exists():
        skill_content = content_path.read_text()
    else:
        # Target SKILL.md may not exist yet (e.g. proposing initial content).
        # Render with empty content so modifications still produce sensible
        # diffs (current side empty → all + lines).
        skill_content = ""

    output = render_proposals_markdown(
        items,
        target_skill_path=args.target_skill,
        target_skill_md_content=skill_content,
        run_date=args.run_date,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output)
    print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover  (CLI entrypoint)
    sys.exit(main())
