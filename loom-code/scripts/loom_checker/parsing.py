from __future__ import annotations

import re


_COMMENT = re.compile(r"\s+#\s.*$")


_FRONTMATTER_LINE = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$")


_ANNOTATION = re.compile(r"[【\[(].*$")


LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")


def parse_document(text: str) -> tuple[dict[str, str], dict[str, str]]:
    """Split a loom artifact into its `key: value` frontmatter (the lines
    between the H1 and the first H2) and its H2 sections, keyed by the
    heading with any 【annotation】 stripped."""
    front: dict[str, str] = {}
    sections: dict[str, str] = {}
    current: str | None = None
    body: list[str] = []
    if text.startswith("﻿"):
        text = text[1:]
    for line in text.splitlines():
        if line.startswith("﻿"):
            # A BOM must never make a key invisible to frontmatter parsing --
            # a commit could otherwise smuggle a `status:` change past every
            # rule that reads it (spec REQ-1, W0-04 round-3 finding).
            line = line[1:]
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(body).strip()
            current = _ANNOTATION.sub("", line[3:]).strip()
            body = []
            continue
        if current is not None:
            body.append(line)
            continue
        if line.startswith("#") or not line.strip():
            continue
        match = _FRONTMATTER_LINE.match(line)
        if match:
            front[match.group(1)] = _COMMENT.sub("", match.group(2)).strip()
    if current is not None:
        sections[current] = "\n".join(body).strip()
    return front, sections


def _squeeze(text: str) -> str:
    return " ".join(text.split())
