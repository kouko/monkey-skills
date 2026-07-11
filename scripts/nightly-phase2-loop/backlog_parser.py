"""Parse the next unchecked Phase 2 backlog item from the campaign doc."""

from __future__ import annotations

import re
from dataclasses import dataclass

_PHASE2_HEADING = re.compile(r"^##\s+Phase 2\b")
_SECTION_HEADING = re.compile(r"^##\s+")
_ITEM = re.compile(r"^- \[(?P<mark>[ xX])\] (?P<id>B\d+): (?P<desc>.*)$")
_NEW_LIST_ITEM = re.compile(r"^- \[")


@dataclass(frozen=True)
class BacklogItem:
    id: str
    description: str


def parse_next_backlog_item(checklist_text: str) -> BacklogItem | None:
    """Return the first unchecked `- [ ] B<n>: ...` item in the Phase 2 section.

    Scans only the `## Phase 2` section (across its High/Medium/Low sub-groups)
    in document order and returns the first item whose checkbox is empty. A
    multi-line item description is folded into a single space-joined string.
    Returns None when every Phase 2 backlog item is checked.
    """
    lines = checklist_text.splitlines()

    start = next(
        (i + 1 for i, line in enumerate(lines) if _PHASE2_HEADING.match(line)),
        None,
    )
    if start is None:
        return None

    end = next(
        (j for j in range(start, len(lines)) if _SECTION_HEADING.match(lines[j])),
        len(lines),
    )

    i = start
    while i < end:
        match = _ITEM.match(lines[i])
        if match is None or match.group("mark").lower() == "x":
            i += 1
            continue

        description_parts = [match.group("desc").strip()]
        k = i + 1
        while k < end:
            nxt = lines[k]
            if not nxt.strip() or _NEW_LIST_ITEM.match(nxt) or not nxt[:1].isspace():
                break
            description_parts.append(nxt.strip())
            k += 1

        return BacklogItem(id=match.group("id"), description=" ".join(description_parts))

    return None
