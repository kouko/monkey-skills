"""Oracle parser for the Level-2 mechanical traceability gate (brief
§Level 2, docs/loom/specs/2026-07-10-principles-replay-loop.md).

This module's `parse_oracle` DEFINES the oracle format contract:

  - Flat `key: value` lines. Each of the three checker-scope keys —
    `named_anchors:`, `deferred_items:`, `negative:` — appears on its own
    single line: `<key>: <value>`.
  - A value is a `;`-separated list of exact-match tokens; each token is
    stripped of surrounding whitespace before being returned.
  - A token may itself be an OR-alternative group `alt1|alt2|…`: at check
    time the item matches if ANY alternative substring-matches, uniformly
    across all three checkers (an anchors/deferred item matches if any
    alternative is found; a negative item is VIOLATED if any alternative is
    present). Plain tokens (no `|`) are unaffected — a single-element
    alternative group behaves byte-identically to a bare token. An empty
    alternative (`a||b`, or a leading/trailing `|` such as `|b` or `a|`)
    raises `ValueError` at parse time — malformed `|` syntax is a parse
    error, not a matching edge case.
  - The empty sentinel `none in this seed` (optionally followed by
    trailing parenthetical commentary, e.g. "none in this seed (2-deferred
    trap lives in seed 2)") parses to an empty list `[]`. A key absent
    from the document also parses to `[]`.
  - A document carrying NONE of the three checker-scope keys raises
    `ValueError`, naming which keys are missing.
  - `stances:` and `out_of_jurisdiction_bait:` are deliberately ignored by
    this parser — they need semantic judgment and stay with LLM
    graders/humans (out of checker scope by design, brief §Level 2). Any
    other unrecognized key is likewise ignored.

`check(artifact_text, oracle_text)` verifies the artifact against the
oracle's three token lists:

  - every `named_anchors` token must appear in an `## Anchors` table data
    row (header + GFM separator row skipped) whose version/edition cell
    (second `|` cell) is non-empty;
  - every `deferred_items` token must appear in a `## Open Questions`
    ordered-list entry line that also carries the `— re-trigger:` marker
    on that same line;
  - every `negative` token must be absent from the artifact entirely.

It returns a list of miss lines, each `<class>: <token>` (class is the
oracle key name, `<token>` is the item exactly as written in the oracle,
including any `|` alternatives). This checker deliberately does NOT
validate table/list well-formedness — that is `validate_principles_output.py`'s
job; the two scripts compose (the CLI here just locates tokens).

CLI: `python check_seed_traceability.py <artifact.md> <oracle.md>` -> exit
0 with no output if every token traces; exit 1 with one miss line per
line on stderr otherwise; exit 2 with a single `error: file not found:
<path>` line on stderr if either input path is not a file.

Stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_KEYS = ("named_anchors", "deferred_items", "negative")
_EMPTY_SENTINEL = "none in this seed"


def parse_oracle(text: str) -> dict:
    """Parse an oracle document's three checker-scope keys.

    Returns a dict with all three keys always present:
    `{"named_anchors": [...], "deferred_items": [...], "negative": [...]}`.

    Raises `ValueError` if none of the three keys appear anywhere in
    `text`, naming which keys are missing.
    """
    raw_values = {}
    for key in _KEYS:
        match = re.search(rf"^{key}:[ \t]*(.*)$", text, re.MULTILINE)
        if match is not None:
            raw_values[key] = match.group(1).strip()

    if not raw_values:
        missing = ", ".join(f"{key}:" for key in _KEYS)
        raise ValueError(
            f"oracle document is missing all three checker-scope keys: {missing}"
        )

    return {key: _parse_value(raw_values.get(key, "")) for key in _KEYS}


def _parse_value(value: str) -> list:
    if not value or value.lower().startswith(_EMPTY_SENTINEL):
        return []
    tokens = [token.strip() for token in value.split(";") if token.strip()]
    for token in tokens:
        _alternatives(token)  # raises ValueError on malformed `|` syntax
    return tokens


_ALT_SEP = "|"


def _alternatives(token: str) -> list:
    """Split an oracle token into its OR-alternatives on `|`. A plain token
    (no `|`) returns `[token]` unchanged — byte-identical to today's
    single-string matching. Raises `ValueError` for an empty alternative
    (`a||b`, or a leading/trailing `|` such as `|b`/`a|`)."""
    if _ALT_SEP not in token:
        return [token]
    alternatives = [part.strip() for part in token.split(_ALT_SEP)]
    if any(not alt for alt in alternatives):
        raise ValueError(
            f"malformed alternative syntax in oracle token (empty "
            f"alternative): {token!r}"
        )
    return alternatives


# --- artifact checks ---------------------------------------------------------

_ANCHORS = "## Anchors"
_OPEN_QUESTIONS = "## Open Questions"
_RE_TRIGGER_MARKER = "— re-trigger:"
_ENTRY = re.compile(r"^\d+\.\s")
_H2 = re.compile(r"^##\s", re.MULTILINE)
_ANCHORS_SEPARATOR_RE = re.compile(r"^\|[\s:-]+\|")


def _section_body(text: str, header: str) -> str | None:
    """Body of the `## <header>` section (lines after the header line up to
    the next `## ` header or end), or None if the header is absent."""
    pat = re.compile(r"^" + re.escape(header) + r"\s*$", re.MULTILINE)
    m = pat.search(text)
    if m is None:
        return None
    nxt = _H2.search(text, m.end())
    return text[m.end():nxt.start()] if nxt else text[m.end():]


def _split_pipe_row(line: str) -> list:
    """Split a `|`-delimited table row into cells, stripping the empty
    boundary elements a leading/trailing `|` produces."""
    parts = line.strip().split("|")
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def _anchor_data_rows(text: str) -> list:
    """`## Anchors` table rows with the header + GFM separator row skipped."""
    body = _section_body(text, _ANCHORS)
    if body is None:
        return []
    pipe_lines = [
        line for line in body.splitlines()
        if line.strip().startswith("|") and not _ANCHORS_SEPARATOR_RE.match(line.strip())
    ]
    return pipe_lines[1:]  # first remaining pipe line is the header row


def _open_questions_retrigger_entries(text: str) -> list:
    """`## Open Questions` ordered-list entry lines that carry the
    `— re-trigger:` marker on the same line."""
    body = _section_body(text, _OPEN_QUESTIONS)
    if body is None:
        return []
    return [
        line for line in body.splitlines()
        if _ENTRY.match(line) and _RE_TRIGGER_MARKER in line
    ]


def check_named_anchors(artifact_text: str, tokens: list) -> list:
    """Miss lines for `named_anchors` tokens not found in an `## Anchors`
    data row whose version cell (second `|` cell) is non-empty. A `|`
    alternative-group token matches if ANY alternative is found."""
    rows = [
        row for row in _anchor_data_rows(artifact_text)
        if len(cells := _split_pipe_row(row)) > 1 and cells[1].strip()
    ]
    return [
        f"named_anchors: {token}"
        for token in tokens
        if not any(alt in row for row in rows for alt in _alternatives(token))
    ]


def check_deferred_items(artifact_text: str, tokens: list) -> list:
    """Miss lines for `deferred_items` tokens not found in a `## Open
    Questions` entry that carries `— re-trigger:` on the same line. A `|`
    alternative-group token matches if ANY alternative is found."""
    entries = _open_questions_retrigger_entries(artifact_text)
    return [
        f"deferred_items: {token}"
        for token in tokens
        if not any(alt in entry for entry in entries for alt in _alternatives(token))
    ]


def check_negative(artifact_text: str, tokens: list) -> list:
    """Miss lines for `negative` tokens that ARE present in the artifact
    (they must be absent). A `|` alternative-group token is VIOLATED if ANY
    alternative is present."""
    return [
        f"negative: {token}"
        for token in tokens
        if any(alt in artifact_text for alt in _alternatives(token))
    ]


def check(artifact_text: str, oracle_text: str) -> list:
    """Verify `artifact_text` against `oracle_text`'s three token lists.

    Returns a list of miss lines (`<class>: <token>`); empty means every
    token traces.
    """
    oracle = parse_oracle(oracle_text)
    misses = []
    misses.extend(check_named_anchors(artifact_text, oracle["named_anchors"]))
    misses.extend(check_deferred_items(artifact_text, oracle["deferred_items"]))
    misses.extend(check_negative(artifact_text, oracle["negative"]))
    return misses


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify an artifact's seed traceability against an "
                    "oracle's named_anchors/deferred_items/negative token "
                    "lists.")
    parser.add_argument("artifact_md", help="path to the artifact (e.g. PRINCIPLES.md)")
    parser.add_argument("oracle_md", help="path to the oracle document")
    parser.epilog = "Exit codes: 0 conformant, 1 miss(es) found, 2 input file not found."
    args = parser.parse_args(argv)

    for input_path in (args.artifact_md, args.oracle_md):
        if not Path(input_path).is_file():
            print(f"error: file not found: {input_path}", file=sys.stderr)
            return 2

    artifact_text = Path(args.artifact_md).read_text(encoding="utf-8")
    oracle_text = Path(args.oracle_md).read_text(encoding="utf-8")

    misses = check(artifact_text, oracle_text)
    for miss in misses:
        print(miss, file=sys.stderr)
    return 1 if misses else 0


if __name__ == "__main__":
    raise SystemExit(main())
