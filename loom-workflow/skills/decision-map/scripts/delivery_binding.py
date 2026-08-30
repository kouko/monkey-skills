#!/usr/bin/env python3
"""Read-only validation for a delivery Ticket's reciprocal Brief binding.

The public ``validate`` function follows the decision-map validators' return
contract: ``(0, message)`` is valid, ``(1, message)`` is an operational
failure, and ``(2, message)`` is a malformed binding.  It writes nothing.
"""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

import map_store


def _invalid(message: str) -> tuple[int, str]:
    return 2, f"delivery binding invalid: {message}"


def _canonical_relative(value: str, label: str) -> tuple[PurePosixPath | None, str | None]:
    """Return a lexical canonical repo-relative path, or its failure reason."""
    if not value or value != value.strip():
        return None, f"{label} path must be a non-empty canonical repository-relative path"
    if "\\" in value:
        return None, f"{label} path must use '/' separators: {value!r}"
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        return None, f"{label} path must not be absolute or traverse directories: {value!r}"
    if path.as_posix() != value:
        return None, f"{label} path is not normalized: {value!r}"
    return path, None


def _contained_regular_file(
    repo_root: Path, relative: PurePosixPath, label: str
) -> tuple[Path | None, str | None]:
    root = repo_root.resolve()
    candidate = root.joinpath(*relative.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except FileNotFoundError:
        return None, f"{label} target does not exist: {relative.as_posix()}"
    except ValueError:
        return None, f"{label} target escapes repository through a symlink: {relative.as_posix()}"
    except OSError as exc:
        return None, f"cannot resolve {label} target {relative.as_posix()}: {exc}"
    if not resolved.is_file():
        return None, f"{label} target is not a regular file: {relative.as_posix()}"
    if not os.access(resolved, os.R_OK):
        return None, f"{label} target is not readable: {relative.as_posix()}"
    return resolved, None


def _read_frontmatter(path: Path, label: str) -> tuple[dict[str, str] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"cannot read {label} {path}: {exc}"
    try:
        fields, _ = map_store.parse_frontmatter(text)
    except map_store.SchemaViolation as exc:
        return None, f"{label} {path} has invalid frontmatter: {exc}"
    return fields, None


def _duplicate_owner(
    repo_root: Path, ticket_path: Path, brief_relative: str
) -> Path | None:
    """Find another map Ticket naming this exact canonical Brief path."""
    maps_root = repo_root / "docs" / "loom" / "maps"
    if not maps_root.is_dir():
        return None
    for candidate in maps_root.rglob("*.md"):
        if candidate == ticket_path or candidate.parent.name != "tickets":
            continue
        fields, error = _read_frontmatter(candidate, "candidate ticket")
        if error is None and fields is not None and fields.get("brief") == brief_relative:
            return candidate
    return None


def validate(ticket_path: Path, repo_root: Path | None = None) -> tuple[int, str]:
    """Validate one Ticket's optional, reciprocal delivery Brief binding."""
    root = Path(repo_root) if repo_root is not None else map_store.resolve_repo_root(None, Path(ticket_path).parent)
    try:
        root = root.resolve(strict=True)
    except OSError as exc:
        return 1, f"cannot resolve repository root {root}: {exc}"
    if not root.is_dir():
        return 1, f"repository root is not a directory: {root}"

    try:
        resolved_ticket = Path(ticket_path).resolve(strict=True)
        ticket_relative = resolved_ticket.relative_to(root).as_posix()
    except FileNotFoundError:
        return 1, f"ticket does not exist: {ticket_path}"
    except ValueError:
        return _invalid(f"ticket escapes repository: {ticket_path}")
    except OSError as exc:
        return 1, f"cannot resolve ticket {ticket_path}: {exc}"
    if not resolved_ticket.is_file() or not os.access(resolved_ticket, os.R_OK):
        return 1, f"ticket is not a readable regular file: {ticket_path}"

    fields, error = _read_frontmatter(resolved_ticket, "ticket")
    if error is not None or fields is None:
        return _invalid(error or "ticket frontmatter could not be read")
    ticket_type = fields.get("type")
    has_brief = "brief" in fields
    if ticket_type != "delivery":
        if has_brief:
            return _invalid("only delivery tickets may declare a 'brief' field")
        return 0, f"{ticket_relative}: non-delivery ticket has no delivery binding"
    if not has_brief:
        return 0, f"{ticket_relative}: delivery ticket is unbriefed"

    brief_path, error = _canonical_relative(fields["brief"], "Ticket brief")
    if error is not None or brief_path is None:
        return _invalid(error or "invalid Ticket brief path")
    brief_relative = brief_path.as_posix()
    resolved_brief, error = _contained_regular_file(root, brief_path, "Brief")
    if error is not None or resolved_brief is None:
        return _invalid(error or "invalid Brief target")

    try:
        brief_text = resolved_brief.read_text(encoding="utf-8")
    except OSError as exc:
        return 1, f"cannot read Brief {brief_relative}: {exc}"
    expected = f"Outcome Map ticket: {ticket_relative}"
    reciprocal_lines = [line for line in brief_text.splitlines() if line.startswith("Outcome Map ticket:")]
    if reciprocal_lines != [expected]:
        return _invalid(
            f"Brief {brief_relative} must contain exactly {expected!r}; found {reciprocal_lines!r}"
        )

    duplicate = _duplicate_owner(root, resolved_ticket, brief_relative)
    if duplicate is not None:
        return _invalid(
            f"Brief {brief_relative} is already owned by another Ticket: "
            f"{duplicate.relative_to(root).as_posix()}"
        )
    return 0, f"{ticket_relative}: reciprocal delivery binding is valid"
