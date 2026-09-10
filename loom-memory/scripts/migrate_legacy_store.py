#!/usr/bin/env python3
"""Explicit, one-shot migration: legacy README-indexed store -> OKF v0.2-
compatible Loom memory profile (REQ-18, REQ-23, REQ-26).

This is the ONLY legacy-format reader in the codebase (REQ-23). It is never
invoked implicitly — installation, session start, recall, and every other
`loom-memory` operation refuse a legacy store and report that an explicit
migration is required, without modifying it. Only this command's own CLI
entry point reads the legacy shape (a hand-maintained `## Index` section in
`README.md`, one `[name](file) — description` line per body file, and a flat
`name`/`description`/`type`/`origin` frontmatter block on every body file).

What migration does, per concept file:
  - keeps `name`, `description`, and the lesson BODY (everything after the
    closing `---`) byte-for-byte untouched;
  - keeps an existing `type` verbatim; assigns the generic `type: Memory`
    only where legacy `type` is absent;
  - moves a legacy `origin` string, verbatim, into `sources: [{resource:
    <origin>}]`; when `origin` is absent, derives one `sources[].resource`
    naming the file's full introducing commit (`git log --diff-filter=A`);
  - preserves any other unrecognized frontmatter key untouched, in place;
  - never touches the body.

What migration does to `README.md` specifically: gives it the complete
concept metadata (`type: Memory Store Guide`, `name: README`, a standalone
`description`, one `sources[].resource` naming its own full introducing
commit) and removes the hand-maintained `## Index` section — the generated
`index.md` (via `loom_memory.regenerate_index`) is its replacement, per the
spec's "Charter location" decision (each file has one owner). Every other
line of README's charter prose is left untouched.

Frontmatter is rendered with a small local serializer, not
`loom_memory.dump_frontmatter`: the latter's generic quoting rule wraps any
scalar containing a colon in `"..."`, and several real `description` values
here both contain a colon AND end in a literal `"` character — a generic
wrap would then re-parse with a stray trailing quote. Every value migrated
here was already stored on disk, unquoted, on a single physical line, so
this serializer never quotes a scalar; only the key delimiter (the first
`:` on the line) matters to `loom_memory.parse_frontmatter`'s reader, and
that first colon is always the frontmatter key's own colon.

CLI:
    python3 migrate_legacy_store.py <store> [--repo-root PATH]

Exit codes: 0 = migrated (or nothing to do is never silent — it is always a
failure, see below); 1 = the store is not a legacy README-indexed store (
already migrated, or was never in that shape), or a concept file's legacy
frontmatter is unreadable. Either way nothing is written.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT_DEFAULT = SCRIPTS_DIR.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import loom_memory as lm  # noqa: E402

DEFAULT_TYPE = "Memory"
INDEX_HEADING = "## Index"

README_DESCRIPTION = (
    "This store's charter: one distilled loom-family lesson per file, the "
    "test for whether a fact belongs here rather than in an open intent, a "
    "commit trailer, or a one-off evidence record, and how to record, "
    "recall, and reconcile an entry; read before adding, editing, or "
    "retiring any concept in this store."
)


class MigrationError(Exception):
    """Raised instead of writing anything — the store is left untouched."""


@dataclass(frozen=True)
class MigrationResult:
    lessons: int
    guide: int


# ---------------------------------------------------------------------------
# Legacy reader (the only place in the codebase that understands this shape)
# ---------------------------------------------------------------------------


def split_legacy(text: str) -> tuple[list[str], str]:
    """`(frontmatter_lines, body)` for a `---`-delimited legacy concept file.

    `body` is reconstructed via `str.split`/`str.join`, which are exact
    inverses of each other — this is what makes the body byte-for-byte
    preservation guarantee (REQ-18) hold by construction, not by care.
    """
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise MigrationError("no '---' frontmatter opening delimiter on line 1")
    try:
        close_idx = next(i for i in range(1, len(lines)) if lines[i] == "---")
    except StopIteration as exc:
        raise MigrationError("no closing '---' frontmatter delimiter") from exc
    body = "\n".join(lines[close_idx + 1 :])
    return lines[1:close_idx], body


def parse_legacy_frontmatter(fm_lines: list[str]) -> dict[str, str]:
    """Flat `key: value` reader, first-colon partition only — the same rule
    `scripts/check_loom_memory_integrity.py` used, so a description or
    origin string containing its own colon still parses correctly."""
    frontmatter: dict[str, str] = {}
    for line in fm_lines:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def _extract_charter(readme_text: str) -> str:
    """Everything before the `## Index` heading, trailing blank lines
    dropped, with exactly one trailing newline."""
    lines = readme_text.split("\n")
    try:
        idx = next(i for i, line in enumerate(lines) if line.strip() == INDEX_HEADING)
    except StopIteration as exc:
        raise MigrationError(f"README.md has no {INDEX_HEADING!r} heading; not a legacy store") from exc
    charter_lines = lines[:idx]
    while charter_lines and charter_lines[-1].strip() == "":
        charter_lines.pop()
    return "\n".join(charter_lines) + "\n"


# ---------------------------------------------------------------------------
# Frontmatter rendering (never quotes a scalar — see module docstring)
# ---------------------------------------------------------------------------


def render_frontmatter(fm: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in fm.items():
        if key == "sources":
            lines.append("sources:")
            for source in value:  # type: ignore[union-attr]
                items = list(source.items())
                first_key, first_value = items[0]
                lines.append(f"  - {first_key}: {first_value}")
                for extra_key, extra_value in items[1:]:
                    lines.append(f"    {extra_key}: {extra_value}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Provenance (REQ-18: verbatim origin, or the full introducing commit)
# ---------------------------------------------------------------------------


def introducing_commit(repo_root: Path, rel_path: str) -> str:
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", rel_path],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    shas = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not shas:
        raise MigrationError(f"no introducing commit found for {rel_path!r}")
    return shas[-1]  # oldest entry = the true introducing commit


def _check_legacy_concept_frontmatter(legacy_fm: dict[str, str], *, filename: str) -> None:
    """Raise `MigrationError`, naming `filename`, for every field this
    concept's migration will dereference — checked BEFORE any file in the
    batch is written (R4), so a single bad file never leaves an earlier
    one half-migrated on disk."""
    if "sources" in legacy_fm:
        raise MigrationError(
            f"{filename}: already carries a 'sources' key — this file is already in the "
            "OKF profile, not a legacy concept; refusing to re-migrate it as legacy"
        )
    if "name" not in legacy_fm:
        raise MigrationError(f"{filename}: legacy frontmatter has no 'name' key")
    if "description" not in legacy_fm:
        raise MigrationError(f"{filename}: legacy frontmatter has no 'description' key")
    stem = filename[: -len(".md")] if filename.endswith(".md") else filename
    if legacy_fm["name"] != stem:
        raise MigrationError(
            f"{filename}: legacy frontmatter name {legacy_fm['name']!r} != filename stem "
            f"{stem!r}; index regeneration would refuse this store, so the batch stops "
            "here rather than after rewriting earlier files"
        )


def _migrate_concept_frontmatter(
    legacy_fm: dict[str, str], *, repo_root: Path, rel_path: str
) -> dict[str, object]:
    new_fm: dict[str, object] = {
        "name": legacy_fm["name"],
        "description": legacy_fm["description"],
        "type": legacy_fm.get("type", DEFAULT_TYPE),
    }
    if "origin" in legacy_fm:
        resource = legacy_fm["origin"]
    else:
        resource = f"introducing commit {introducing_commit(repo_root, rel_path)}"
    new_fm["sources"] = [{"resource": resource}]
    for key, value in legacy_fm.items():
        if key in ("name", "description", "type", "origin"):
            continue
        new_fm[key] = value
    return new_fm


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------


def is_legacy_store(store: Path) -> bool:
    """True only for the known legacy README-indexed shape this command
    alone reads (REQ-23): a README.md carrying a `## Index` heading and no
    `index.md` already present."""
    readme = store / "README.md"
    if not readme.is_file() or (store / "index.md").exists():
        return False
    text = readme.read_text(encoding="utf-8")
    return any(line.strip() == INDEX_HEADING for line in text.split("\n"))


def migrate(store: Path, repo_root: Path) -> MigrationResult:
    """R4: every rewrite is computed in memory first, against every legacy
    file's own required fields, before a single byte is written. A
    failure on any one file raises `MigrationError` naming it, and writes
    nothing at all — the store is left exactly as it was found."""
    if not is_legacy_store(store):
        raise MigrationError(
            f"{store} is not a legacy README-indexed store (already migrated, "
            "or was never in that shape) — explicit migration refuses to run"
        )

    readme_path = store / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    store_rel = store.relative_to(repo_root)

    lesson_paths = sorted(p for p in store.glob("*.md") if p.name not in ("README.md", "index.md"))

    # Stage every lesson rewrite first — check, then compute, never write —
    # so a problem anywhere in the batch is caught before any write happens.
    staged: list[tuple[Path, str]] = []
    for path in lesson_paths:
        text = path.read_text(encoding="utf-8")
        fm_lines, body = split_legacy(text)
        legacy_fm = parse_legacy_frontmatter(fm_lines)
        _check_legacy_concept_frontmatter(legacy_fm, filename=path.name)
        rel_path = (store_rel / path.name).as_posix()
        new_fm = _migrate_concept_frontmatter(legacy_fm, repo_root=repo_root, rel_path=rel_path)
        staged.append((path, render_frontmatter(new_fm) + body))

    charter = _extract_charter(readme_text)
    readme_rel = (store_rel / "README.md").as_posix()
    readme_sha = introducing_commit(repo_root, readme_rel)
    readme_fm: dict[str, object] = {
        "name": "README",
        "description": README_DESCRIPTION,
        "type": lm.GUIDE_TYPE,
        "sources": [{"resource": f"introducing commit {readme_sha}"}],
    }
    readme_new_text = render_frontmatter(readme_fm) + "\n" + charter

    # Every rewrite computed and validated — now write the whole batch.
    for path, new_text in staged:
        path.write_text(new_text, encoding="utf-8")
    readme_path.write_text(readme_new_text, encoding="utf-8")

    lm.regenerate_index(store)
    return MigrationResult(lessons=len(lesson_paths), guide=1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="migrate_legacy_store", description=__doc__)
    parser.add_argument("store")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args(argv)

    store = Path(args.store).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else REPO_ROOT_DEFAULT

    try:
        result = migrate(store, repo_root)
    except MigrationError as exc:
        print(f"migrate_legacy_store: FAIL — {exc}")
        return 1

    print(
        f"migrate_legacy_store: migrated {result.lessons} lesson concept(s) "
        f"+ {result.guide} guide concept; wrote {store / 'index.md'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
