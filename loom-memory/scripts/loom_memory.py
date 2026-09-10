#!/usr/bin/env python3
"""OKF v0.2-compatible Loom memory profile: validator + `index.md` generator.

One parser serves both operations (`validate` and `regenerate-index`) so the
two never drift against each other — REQ-26 ("one validator implementation")
and the plan's own risk note ("one parser serves both").

Compatibility surface this module implements (spec.md's pinned "Normative
external baseline" paragraph, OKF v0.2 at commit 62432a095456...):

  1. every non-reserved Markdown document has parseable YAML-ish frontmatter
  2. each such frontmatter has a non-empty `type`
  3. a present reserved `index.md` (or `log.md`) follows its reserved
     structure — for `index.md` in this profile that structure is exactly
     `okf_version: "0.2"` and nothing else (clause 6)
  4. missing optional metadata, unknown types, and unknown extra keys never
     make a generic OKF bundle nonconformant (REQ-12)
  5. the Loom profile layers its own required fields on top (REQ-10):
     `type`, `name`, `description`, and >=1 `sources[].resource`; `name`
     must equal the filename stem, and `description` a non-empty single
     durable line
  6. `index.md` is progressive-disclosure and MUST be exactly what a fresh
     regeneration would produce (REQ-8, REQ-9) — drift is a validation
     failure, never a silent divergence

Frontmatter is parsed with a small hand-rolled, indentation-based mapping/
sequence reader — stdlib only, deliberately not PyYAML: this module ships
inside an installable plugin, so a third-party runtime dependency is worse
here than it was for the legacy repo-local checker it replaces
(`scripts/check_loom_memory_integrity.py`). It supports exactly the shapes
this profile needs: scalar `key: value` pairs and a `sources:` block that is
a sequence of small mappings — enough to preserve unrecognized keys and
values it doesn't specifically validate (REQ-12), without claiming to be a
general YAML parser.

Validation never mutates a store. Regeneration touches only `index.md`, and
refuses to write anything at all when the concept metadata it would render
from is itself broken (mirrors the legacy `build_entries` "raise, never
launder" contract) — see `LoomMemoryError` and `_collect_index_items_strict`.

CLI:
    python3 loom_memory.py validate <store>
    python3 loom_memory.py regenerate-index <store>

Exit codes: 0 = clean / written; 1 = at least one violation, or a structural
problem that blocks regeneration. Every violation line is printed as
`[invariant] file: detail`, and a `validate` run always reports every
offender it finds, not only the first (REQ-17).
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

RESERVED_FILENAMES = {"index.md", "log.md"}
GUIDE_TYPE = "Memory Store Guide"
# `generate_index` writes the literal text `okf_version: "0.2"` (quote
# characters included); since a scalar value is parsed byte-preserving
# (R1 — no quote-stripping at parse time), the value this dict compares
# against must carry those same quote characters, not the bare string.
INDEX_FRONTMATTER = {"okf_version": '"0.2"'}
INDEX_LINK_LINE_RE = re.compile(r"^-\s+\[[^\]]*\]\((?P<href>.*?)\)\s+—\s+")


# ---------------------------------------------------------------------------
# Minimal stdlib-only frontmatter parser
# ---------------------------------------------------------------------------


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_mapping(lines: list[str], indent: int) -> dict:
    """Parse a block of `key: value` lines all sitting at `indent`.

    A key with no inline value opens a nested block (a mapping, or a
    sequence of mappings when the first nested line starts with `- `),
    consumed recursively so unrecognized nested shapes still round-trip.
    """
    result: dict[str, object] = {}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if _indent_of(line) != indent:
            i += 1
            continue
        stripped = line[indent:]
        if ":" not in stripped:
            i += 1
            continue
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest:
            # R1: byte-preserving scalar — everything after the first `:`
            # separator, stored as-is (only the mandatory single space
            # after the colon delimiter is trimmed above). No quote
            # interpretation at parse time; REQ-8's whitespace-stripping
            # for the index copy happens at that copy site, not here.
            result[key] = rest
            i += 1
            continue

        j = i + 1
        nested: list[str] = []
        while j < n and (not lines[j].strip() or _indent_of(lines[j]) > indent):
            nested.append(lines[j])
            j += 1
        first_content = next((entry for entry in nested if entry.strip()), None)
        if first_content is None:
            result[key] = None
        else:
            sub_indent = _indent_of(first_content)
            if first_content[sub_indent:].startswith("- "):
                result[key] = _parse_sequence(nested, sub_indent)
            else:
                result[key] = _parse_mapping(nested, sub_indent)
        i = j
    return result


def _parse_sequence(lines: list[str], indent: int) -> list[dict]:
    starts = [
        idx
        for idx, entry in enumerate(lines)
        if entry.strip() and _indent_of(entry) == indent and entry[indent:].startswith("- ")
    ]
    items: list[dict] = []
    for k, start in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(lines)
        chunk = lines[start:end]
        head = chunk[0]
        item_indent = indent + 2
        item_lines = [" " * item_indent + head[indent + 2 :]] + chunk[1:]
        items.append(_parse_mapping(item_lines, item_indent))
    return items


def parse_frontmatter(text: str) -> dict | None:
    """`None` when there is no well-formed `---`-delimited block at all."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(
            i for i in range(1, len(lines)) if _indent_of(lines[i]) == 0 and lines[i].strip() == "---"
        )
    except StopIteration:
        return None
    return _parse_mapping(lines[1:end], 0)


def _scalar_literal(key: str, value: str) -> str:
    """The written form of a scalar, chosen so `parse_frontmatter` reads back
    exactly the bytes handed in.

    Since R1 the parser strips no quotes, so adding them here would make the
    round trip lossy and would accumulate a new pair on every rewrite. A colon
    needs no quoting either: the parser splits on the FIRST colon and takes the
    remainder verbatim. Two shapes have no faithful unquoted form — an empty
    value (indistinguishable from a key that opens a nested block) and one
    carrying leading or trailing whitespace (the parser strips it) — and those
    abort rather than silently changing the caller's bytes. `okf_version` gets
    no special case either: REQ-7 fixes its exact text `"0.2"`, quotes and all,
    so that text is what the constant holds and what the parser reads back —
    re-quoting it here would wrap a second pair around a value that already
    carries its own.
    """
    if value == "" or value != value.strip():
        raise ValueError(
            f"cannot serialise {key!r} byte-identically: a value that is empty "
            f"or carries leading/trailing whitespace has no unquoted form the "
            f"parser reads back unchanged (got {value!r})"
        )
    return value


def _dump_mapping(data: dict, indent: int) -> list[str]:
    pad = " " * indent
    out: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            out.append(f"{pad}{key}:")
            out.extend(_dump_mapping(value, indent + 2))
        elif isinstance(value, list):
            out.append(f"{pad}{key}:")
            out.extend(_dump_sequence(value, indent + 2))
        elif value is None:
            out.append(f"{pad}{key}:")
        else:
            out.append(f"{pad}{key}: {_scalar_literal(key, str(value))}")
    return out


def _dump_sequence(items: list[dict], indent: int) -> list[str]:
    pad = " " * indent
    out: list[str] = []
    for item in items:
        sub_lines = _dump_mapping(item, indent + 2)
        if sub_lines:
            out.append(f"{pad}- {sub_lines[0].lstrip()}")
            out.extend(sub_lines[1:])
        else:
            out.append(f"{pad}-")
    return out


def dump_frontmatter(data: dict) -> str:
    """The inverse of `parse_frontmatter` — used internally so unrecognized
    keys and shapes demonstrably round-trip (REQ-12)."""
    lines = ["---", *_dump_mapping(data, 0), "---"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Violations
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Violation:
    invariant: str
    file: str
    detail: str

    def render(self) -> str:
        return f"  [{self.invariant}] {self.file}: {self.detail}"


class LoomMemoryError(Exception):
    """Raised instead of laundering broken concept metadata into output.

    Carries every offending `Violation` found (REQ-17: name every offender,
    not just the first), never only one.
    """

    def __init__(self, violations: list[Violation]):
        self.violations = violations
        super().__init__("; ".join(v.render().strip() for v in violations))


def iter_concept_files(store: Path) -> list[Path]:
    """Flat, top-level concept files only — concept identity stays flat
    (R5): a nested Markdown document is never a concept, it is reported
    separately by `iter_nested_markdown_files` as its own violation."""
    return sorted(p for p in store.glob("*.md") if p.name not in RESERVED_FILENAMES)


def iter_nested_markdown_files(store: Path) -> list[Path]:
    """Every Markdown document that lives one or more directories below the
    store root (R5 / pinned OKF clause 1: the walk must cover the whole
    bundle). The bundle is flat by profile choice, so any such document —
    parseable frontmatter or not — is itself a violation, named by its
    path relative to the store, not silently skipped by a non-recursive
    glob."""
    return sorted(p for p in store.rglob("*.md") if p.parent != store)


# ---------------------------------------------------------------------------
# Loom profile validation (REQ-6, REQ-7, REQ-10, REQ-12, REQ-17)
# ---------------------------------------------------------------------------


def _validate_concept_file(path: Path) -> list[Violation]:
    violations: list[Violation] = []
    text = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    if frontmatter is None:
        violations.append(Violation("frontmatter", path.name, "no parseable YAML frontmatter block"))
        return violations

    type_value = frontmatter.get("type")
    if not isinstance(type_value, str) or not type_value.strip():
        violations.append(Violation("type", path.name, "frontmatter missing a non-empty 'type'"))

    name = frontmatter.get("name")
    stem = path.stem
    if not isinstance(name, str) or not name.strip():
        violations.append(Violation("name", path.name, "frontmatter missing a non-empty 'name'"))
    elif name != stem:
        violations.append(
            Violation("name", path.name, f"frontmatter name {name!r} != filename stem {stem!r}")
        )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        violations.append(Violation("description", path.name, "frontmatter missing a non-empty 'description'"))

    sources = frontmatter.get("sources")
    if not isinstance(sources, list) or not sources:
        violations.append(Violation("sources", path.name, "frontmatter missing at least one 'sources' entry"))
    else:
        for idx, entry in enumerate(sources):
            resource = entry.get("resource") if isinstance(entry, dict) else None
            if not isinstance(resource, str) or not resource.strip():
                violations.append(
                    Violation("sources", path.name, f"sources[{idx}] missing a non-empty 'resource'")
                )

    return violations


def _validate_reserved_index(index_path: Path) -> list[Violation]:
    text = index_path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    if frontmatter is None:
        return [Violation("reserved-index", index_path.name, "no parseable frontmatter block")]
    if frontmatter != INDEX_FRONTMATTER:
        return [
            Violation(
                "reserved-index",
                index_path.name,
                f"frontmatter must be exactly {INDEX_FRONTMATTER!r}, got {frontmatter!r}",
            )
        ]
    return []


def _check_index_targets(store: Path, index_path: Path) -> list[Violation]:
    """Check each index ENTRY's link target — never a substring scan over
    the whole index text (R2). `index.md` is machine-generated: every real
    entry is one line of the exact shape `- [name](file) — description`
    that `generate_index` emits, so a target is only ever read from that
    anchored line shape. This keeps a link quoted inside a description
    (e.g. `... — see [the plan](plan.md) before acting`) from being read
    as a second index target, and keeps a literal `(`/`)` inside a
    concept's own filename from truncating its own href early — the
    lazy match stops at the first `) <space> — <space>` it finds, which
    is the entry's own closing delimiter, not the first `)` byte."""
    text = index_path.read_text(encoding="utf-8")
    violations: list[Violation] = []
    store_resolved = store.resolve()
    for line in text.splitlines():
        match = INDEX_LINK_LINE_RE.match(line.lstrip())
        if not match:
            continue
        href = match.group("href")
        resolved = (store / href).resolve()
        try:
            resolved.relative_to(store_resolved)
            escapes_store = False
        except ValueError:
            escapes_store = True
        if escapes_store:
            violations.append(
                Violation("broken-target", href, f"index.md links outside the store {href!r}")
            )
        elif not resolved.exists():
            violations.append(Violation("broken-target", href, f"index.md links to a missing file {href!r}"))
    return violations


def validate_bundle(store: Path) -> list[Violation]:
    """Every offender, every violated invariant — never stops at the first."""
    violations: list[Violation] = []

    # R5: an absent (or non-directory) store path is its own offender —
    # never misdiagnosed downstream as an ordinary store missing its index.
    if not store.is_dir():
        return [
            Violation(
                "store-missing", str(store), "the store path does not exist or is not a directory"
            )
        ]

    for nested in iter_nested_markdown_files(store):
        violations.append(
            Violation(
                "nested-document",
                str(nested.relative_to(store)),
                "concept files must live directly under the store root; "
                "this profile is flat and does not walk into subdirectories",
            )
        )

    concept_files = iter_concept_files(store)
    names_seen: dict[str, list[str]] = {}
    for path in concept_files:
        violations.extend(_validate_concept_file(path))
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        name = frontmatter.get("name") if frontmatter else None
        if isinstance(name, str) and name.strip():
            names_seen.setdefault(name, []).append(path.name)

    for name, files in sorted(names_seen.items()):
        if len(files) > 1:
            for file in sorted(files):
                violations.append(
                    Violation("duplicate-identity", file, f"name {name!r} is shared by {sorted(files)}")
                )

    index_path = store / "index.md"
    if index_path.exists():
        violations.extend(_validate_reserved_index(index_path))
        violations.extend(_check_index_targets(store, index_path))
        violations.extend(check_index_drift(store))
    else:
        violations.append(Violation("index-missing", "index.md", "the Loom profile requires a generated index.md"))

    log_path = store / "log.md"
    if log_path.exists():
        log_frontmatter = parse_frontmatter(log_path.read_text(encoding="utf-8"))
        if log_frontmatter is None:
            violations.append(Violation("reserved-log", "log.md", "no parseable frontmatter block"))

    return violations


# ---------------------------------------------------------------------------
# Index generation (REQ-8, REQ-9)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IndexItem:
    name: str
    file: str
    description: str
    type: str


def _collect_index_items_strict(store: Path) -> list[IndexItem]:
    """Every concept file's metadata, or a `LoomMemoryError` naming every
    offender — never a stem-fallback or a blank description (mirrors the
    legacy `build_entries` "raise, never launder" contract).

    Reuses `_validate_concept_file`'s frontmatter/name/description/type
    checks rather than restating them (a fifth required field would
    otherwise drift between the two implementations) — but a missing
    `sources` entry alone never blocks regeneration: it is a Loom-profile
    violation `validate` reports on its own, not something the index needs
    to render name/description/type.
    """
    problems: list[Violation] = []
    items: list[IndexItem] = []
    for path in iter_concept_files(store):
        blocking = [v for v in _validate_concept_file(path) if v.invariant != "sources"]
        if blocking:
            problems.extend(
                Violation(v.invariant, v.file, f"{v.detail}; refusing to regenerate") for v in blocking
            )
            continue
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        items.append(
            IndexItem(
                name=frontmatter["name"].strip(),
                file=path.name,
                description=frontmatter["description"].strip(),
                type=frontmatter["type"].strip(),
            )
        )
    if problems:
        raise LoomMemoryError(problems)
    return items


def generate_index(store: Path) -> str:
    """Deterministic `index.md` text: `okf_version` frontmatter only, lesson
    links grouped by memory `type`, the charter concept under `Guides`.
    Raises `LoomMemoryError` (without producing any text) when a concept
    file's own required metadata is broken."""
    items = _collect_index_items_strict(store)
    guides = sorted((item for item in items if item.type == GUIDE_TYPE), key=lambda item: item.name)
    groups: dict[str, list[IndexItem]] = {}
    for item in items:
        if item.type == GUIDE_TYPE:
            continue
        groups.setdefault(item.type, []).append(item)

    lines = ["---", 'okf_version: "0.2"', "---", "", "# Memory Store Index", ""]
    if guides:
        lines.append("## Guides")
        lines.append("")
        for item in guides:
            lines.append(f"- [{item.name}]({item.file}) — {item.description}")
        lines.append("")
    for type_name in sorted(groups):
        lines.append(f"## {type_name}")
        lines.append("")
        for item in sorted(groups[type_name], key=lambda entry: entry.name):
            lines.append(f"- [{item.name}]({item.file}) — {item.description}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def check_index_drift(store: Path) -> list[Violation]:
    index_path = store / "index.md"
    if not index_path.exists():
        return []
    try:
        regenerated = generate_index(store)
    except LoomMemoryError:
        # Already reported per-file under the concept-level violations above;
        # a drift comparison against unusable data would only be noise.
        return []
    # R3: the comparison is unconditionally a byte comparison (REQ-9) —
    # `read_text()` would silently fold CRLF to LF and hide real drift.
    committed_bytes = index_path.read_bytes()
    regenerated_bytes = regenerated.encode("utf-8")
    if committed_bytes == regenerated_bytes:
        return []
    diff = "\n".join(
        difflib.unified_diff(
            committed_bytes.decode("utf-8", errors="replace").splitlines(),
            regenerated.splitlines(),
            fromfile="index.md (committed)",
            tofile="index.md (regenerated)",
            lineterm="",
        )
    )
    return [Violation("index-drift", "index.md", f"committed index.md differs from a fresh regeneration:\n{diff}")]


def regenerate_index(store: Path) -> str:
    """Writes ONLY `index.md`. Raises `LoomMemoryError` — leaving the store
    untouched — before any write when concept metadata is broken."""
    text = generate_index(store)
    (store / "index.md").write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_violations(violations: list[Violation]) -> None:
    for violation in sorted(violations, key=lambda v: (v.file, v.invariant)):
        print(violation.render())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loom_memory", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate_p = sub.add_parser("validate", help="validate an OKF v0.2-compatible Loom memory store")
    validate_p.add_argument("store")

    regen_p = sub.add_parser("regenerate-index", help="deterministically rewrite index.md")
    regen_p.add_argument("store")

    args = parser.parse_args(argv)
    store = Path(args.store)

    if args.command == "validate":
        violations = validate_bundle(store)
        if not violations:
            print("loom_memory validate: OK — OKF v0.2-compatible Loom memory profile holds.")
            return 0
        print("loom_memory validate: FAIL — the following invariants are violated.\n")
        _print_violations(violations)
        return 1

    if args.command == "regenerate-index":
        try:
            regenerate_index(store)
        except LoomMemoryError as exc:
            print("loom_memory regenerate-index: FAIL — refusing to write; fix these first.\n")
            _print_violations(exc.violations)
            return 1
        print(f"loom_memory regenerate-index: wrote {store / 'index.md'}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
