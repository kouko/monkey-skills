"""Open one delivery arc of a Map as an intent, not as a delivery ticket.

Loom 1.0 deleted the delivery ticket and its Brief binding. A Map that wants
to deliver a slice writes `docs/loom/intent/<change-id>.md` carrying
`originator: map:<map-id>` and `map: <map-id>`, and lists that change-id
against the Destination acceptance criterion the slice serves. The intent's
own `status:` is the only delivery state; the Map never copies it.

Exit codes match the other decision-map readers: 0 clean, 1 operational,
2 contract violation.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import map_lock
import map_store

INTENT_DIR = "docs/loom/intent"
_CHANGE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_DA_ID = re.compile(r"DA-[0-9]+")


class StartDeliveryError(Exception):
    """A structural refusal while opening a delivery arc."""


def _intent_stub(change_id: str, map_id: str, title: str) -> str:
    """Return the intent stub every map-originated change starts from.

    Field set and section order follow loom-code's `contract/templates/
    intent.md`; that template stays the authority for what each section must
    say. This stub only guarantees a machine-checkable skeleton exists when
    loom-code is not installed beside this Map.
    """
    return (
        f"# {title}\n"
        f"originator: map:{map_id}\n"
        "kind: product | engineering\n"
        "needs-design: yes | no — <reason>\n"
        f"map: {map_id}\n"
        "status: open\n"
        "\n"
        "## Problem\n"
        "<what is wrong today and for whom, in plain words>\n"
        "\n"
        "## Proposed outcome\n"
        "<the slice this arc promises>\n"
        "\n"
        "## Acceptance\n"
        "1. <after this lands I can …; provable by a blind run>\n"
        "\n"
        "## Constraints\n"
        "- <…>\n"
        "\n"
        "## Out of scope\n"
        "- <…>\n"
        "\n"
        "## Open questions\n"
        "- <…>\n"
    )


def _acceptance_ids(doc: map_store.MapDocument) -> dict[str, str]:
    return {entry.id: entry.state for entry in doc.destination_acceptance}


def _note_line(da_id: str, intent_rel: str) -> str:
    return f"- delivery-intent: {da_id} | {intent_rel}"


_NOTE_LINE = re.compile(r"^\s*-\s*delivery-intent:\s*(DA-[0-9]+)\s*\|\s*(\S+)\s*$")


def _owning_criterion(map_text: str, intent_rel: str) -> str | None:
    """The Destination criterion this intent was already opened for, if any."""
    for line in map_text.splitlines():
        match = _NOTE_LINE.match(line)
        if match and match.group(2) == intent_rel:
            return match.group(1)
    return None


def _validate_inputs(da_id: str, change_id: str) -> None:
    if not _DA_ID.fullmatch(da_id):
        raise StartDeliveryError(f"Destination acceptance id must be DA-<n>: {da_id!r}")
    if not _CHANGE_ID.fullmatch(change_id):
        raise StartDeliveryError(
            "change-id must be lowercase letters, digits, and hyphens: "
            f"{change_id!r}"
        )


def _intent_fields(text: str) -> dict[str, str]:
    """Read an intent's header fields.

    An intent carries bare `key: value` lines under its title, with no `---`
    fence, so `map_store.parse_frontmatter` does not apply. Reading stops at
    the first `## ` section heading.
    """
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break
        key, separator, value = line.partition(":")
        if separator and key.strip() and " " not in key.strip():
            fields[key.strip()] = value.strip()
    return fields


def _existing_intent(path: Path, map_id: str) -> bool:
    """Return True when `path` already holds this Map's intent for reuse."""
    if not path.exists():
        return False
    if not path.is_file():
        raise StartDeliveryError(f"intent path is not a regular file: {path}")
    if _intent_fields(path.read_text(encoding="utf-8")).get("map") != map_id:
        raise StartDeliveryError(
            f"intent already exists and is not bound to map:{map_id}: {path}"
        )
    return True


def start_delivery(
    map_dir: Path,
    da_id: str,
    change_id: str,
    *,
    title: str | None = None,
    repo_root: Path | None = None,
) -> tuple[int, str]:
    """Write the intent for one delivery arc and list it under its DA."""
    try:
        map_dir = Path(map_dir)
        _validate_inputs(da_id, change_id)
        root = Path(
            map_store.resolve_repo_root(repo_root, map_dir)
        )
        intent_rel = f"{INTENT_DIR}/{change_id}.md"
        intent_path = root / intent_rel
        with map_lock.map_writer_lock(map_dir):
            doc = map_store.require_work_mutable(map_dir, "bind")
            map_id = doc.frontmatter.map_id
            states = _acceptance_ids(doc)
            if da_id not in states:
                raise StartDeliveryError(
                    f"{da_id} is not a Destination acceptance criterion of {map_id}"
                )
            if states[da_id] != "open":
                raise StartDeliveryError(
                    f"{da_id} is already satisfied; a satisfied criterion opens no arc"
                )
            reused = _existing_intent(intent_path, map_id)
            map_path = map_dir / "MAP.md"
            current = map_path.read_text(encoding="utf-8")
            # One intent = one delivery arc. An intent carries a single
            # `status:`, so two criteria pointing at it would be opened and
            # closed together, and the Map would report a promise as
            # delivered on another promise's evidence (W3 adversary P09).
            owner = _owning_criterion(current, intent_rel)
            if owner is not None and owner != da_id:
                raise StartDeliveryError(
                    f"{intent_rel} is already the delivery intent of {owner}; "
                    f"one intent is one delivery arc, so {da_id} needs its own "
                    "change-id (its status would otherwise close both)"
                )
            line = _note_line(da_id, intent_rel)
            if line not in current.splitlines():
                map_store._atomic_write(
                    map_path,
                    map_store._append_section_fields(current, "Notes", [line]),
                    expected=current.encode("utf-8"),
                )
            if not reused:
                intent_path.parent.mkdir(parents=True, exist_ok=True)
                map_store._atomic_write(
                    intent_path,
                    _intent_stub(change_id, map_id, title or change_id.replace("-", " ")),
                )
    except StartDeliveryError as exc:
        return 2, f"Start delivery refused: {exc}"
    except map_store.SchemaViolation as exc:
        return 2, f"Start delivery refused: {exc}"
    except (map_lock.MapLockError, map_store.MapStoreError, OSError) as exc:
        return 1, f"Start delivery failed: {exc}"
    action = "reused" if reused else "created"
    return 0, f"Start delivery {action} {intent_rel} for {da_id}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map_dir")
    parser.add_argument("da_id")
    parser.add_argument("change_id")
    parser.add_argument("--title", default=None)
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args(argv)
    code, message = start_delivery(
        Path(args.map_dir),
        args.da_id,
        args.change_id,
        title=args.title,
        repo_root=Path(args.repo_root) if args.repo_root else None,
    )
    print(message)
    return code


if __name__ == "__main__":  # pragma: no cover - CLI wiring
    sys.exit(main())
