#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""seed_baseline — extract bundled baseline tarball into a user's
working folder, mutating frontmatter so the seeded entries are
treated as `user_playbook` rather than `bundled_fallback`.

Flow:
  1. Read `assets/baseline-playbooks.tar.gz` (built by build_baseline.py)
  2. Verify sha256 matches `assets/seed-manifest.yml`
  3. Refuse to seed when `<target>/legal-playbook/` already has content
     unless --force or --merge passed
  4. Extract each .md file
  5. Mutate frontmatter per-file:
       - `source_type: bundled_fallback`  →  `source_type: user_playbook`
       - `last_updated:`                  →  today's ISO date
       - leave `escalate_to: "[請編輯..."` placeholder (user fills in)
       - leave `owner: "[請編輯..."` placeholder (user fills in)
  6. Write seed-history entry to `<target>/.legal-toolkit/seed-history.yml`
     recording manifest hash + seed timestamp for reproducibility

Usage:
    seed_baseline.py --target <dir>            # default: <cwd>
    seed_baseline.py --force                   # overwrite existing
    seed_baseline.py --merge                   # skip existing files, seed missing
    seed_baseline.py --dry-run                 # preview without writing
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path

import yaml


def _plugin_root() -> Path:
    p = Path(__file__).resolve()
    for ancestor in [p, *p.parents]:
        if (ancestor / ".claude-plugin" / "plugin.json").is_file():
            return ancestor
    raise SystemExit("seed_baseline: could not locate plugin root")


PLUGIN_ROOT = _plugin_root()
TARBALL_PATH = (
    PLUGIN_ROOT
    / "skills"
    / "legal-contract-review"
    / "assets"
    / "baseline-playbooks.tar.gz"
)
MANIFEST_PATH = (
    PLUGIN_ROOT
    / "skills"
    / "legal-contract-review"
    / "assets"
    / "seed-manifest.yml"
)

FRONTMATTER_SOURCE_TYPE_RE = re.compile(r"^source_type:\s*bundled_fallback\s*$", re.MULTILINE)
FRONTMATTER_LAST_UPDATED_RE = re.compile(r"^last_updated:\s*[0-9-]+\s*$", re.MULTILINE)


def _verify_tarball() -> dict:
    """Check tarball hash matches manifest; return manifest dict."""
    if not TARBALL_PATH.is_file():
        raise SystemExit(f"seed_baseline: tarball missing: {TARBALL_PATH}")
    if not MANIFEST_PATH.is_file():
        raise SystemExit(f"seed_baseline: manifest missing: {MANIFEST_PATH}")
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = manifest.get("tarball_sha256")
    actual = hashlib.sha256(TARBALL_PATH.read_bytes()).hexdigest()
    if expected != actual:
        raise SystemExit(
            f"seed_baseline: tarball hash mismatch — manifest says {expected}, "
            f"file is {actual}. Re-run build_baseline.py."
        )
    return manifest


def _mutate_frontmatter(text: str, today_iso: str) -> str:
    """Replace bundled-fallback flags so the seeded file becomes user_playbook."""
    text = FRONTMATTER_SOURCE_TYPE_RE.sub("source_type: user_playbook", text)
    text = FRONTMATTER_LAST_UPDATED_RE.sub(f"last_updated: {today_iso}", text)
    return text


def _scan_existing(target_playbook: Path) -> list[str]:
    """List relative paths under <target>/legal-playbook/ that already exist."""
    if not target_playbook.is_dir():
        return []
    return [
        str(p.relative_to(target_playbook))
        for p in sorted(target_playbook.rglob("*.md"))
    ]


def seed(
    target_root: Path,
    *,
    force: bool = False,
    merge: bool = False,
    dry_run: bool = False,
) -> dict:
    manifest = _verify_tarball()
    target_playbook = target_root / "legal-playbook"
    target_tool_internal = target_root / ".legal-toolkit"

    existing = _scan_existing(target_playbook)
    if existing and not (force or merge):
        raise SystemExit(
            f"seed_baseline: refusing — {target_playbook} already has "
            f"{len(existing)} file(s). Use --force to overwrite or --merge "
            f"to seed only the missing entries.\nExisting: {existing[:5]}..."
        )

    today_iso = _dt.date.today().isoformat()
    written: list[str] = []
    skipped: list[str] = []
    overwritten: list[str] = []

    with tarfile.open(TARBALL_PATH, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isdir():
                if not dry_run:
                    (target_playbook / member.name).mkdir(parents=True, exist_ok=True)
                continue
            if not member.name.endswith(".md"):
                continue
            f = tar.extractfile(member)
            if f is None:
                continue
            data = f.read().decode("utf-8")
            data = _mutate_frontmatter(data, today_iso)
            out_path = target_playbook / member.name
            rel = str(out_path.relative_to(target_playbook))
            if out_path.exists():
                if merge:
                    skipped.append(rel)
                    continue
                if force:
                    overwritten.append(rel)
            if not dry_run:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(data, encoding="utf-8")
            written.append(rel)

    # seed-history.yml under .legal-toolkit/
    history_entry = {
        "seeded_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "manifest_version": manifest.get("version"),
        "tarball_sha256": manifest.get("tarball_sha256"),
        "total_clauses": manifest.get("total_clauses"),
        "total_files": manifest.get("total_files"),
        "mode": "force" if force else ("merge" if merge else "fresh"),
        "files_written": written,
        "files_skipped": skipped,
        "files_overwritten": overwritten,
    }
    if not dry_run:
        target_tool_internal.mkdir(parents=True, exist_ok=True)
        history_path = target_tool_internal / "seed-history.yml"
        if history_path.exists():
            existing_history = yaml.safe_load(history_path.read_text(encoding="utf-8")) or []
            if not isinstance(existing_history, list):
                existing_history = []
        else:
            existing_history = []
        existing_history.append(history_entry)
        history_path.write_text(
            yaml.safe_dump(existing_history, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    return {
        "target_playbook": str(target_playbook),
        "tool_internal": str(target_tool_internal),
        "files_written": written,
        "files_skipped": skipped,
        "files_overwritten": overwritten,
        "dry_run": dry_run,
        "today_iso": today_iso,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", default=".", help="working folder root (default: cwd)")
    parser.add_argument("--force", action="store_true", help="overwrite existing entries")
    parser.add_argument("--merge", action="store_true", help="only seed missing entries")
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    if args.force and args.merge:
        print("seed_baseline: --force and --merge are mutually exclusive", file=sys.stderr)
        return 2

    report = seed(
        Path(args.target).resolve(),
        force=args.force,
        merge=args.merge,
        dry_run=args.dry_run,
    )

    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        prefix = "[DRY-RUN] " if args.dry_run else ""
        print(f"{prefix}Seeded baseline to: {report['target_playbook']}")
        print(f"{prefix}  files written:    {len(report['files_written'])}")
        if report["files_overwritten"]:
            print(f"{prefix}  files overwritten: {len(report['files_overwritten'])}")
        if report["files_skipped"]:
            print(f"{prefix}  files skipped:    {len(report['files_skipped'])}")
        print(f"\nNext steps:")
        print(f"  - Review each clause's '## 偏好立場' / '## Fallback 1'")
        print(f"  - Replace [請編輯…] placeholders in escalate_to / owner")
        print(f"  - Run /legal-contract-review on a real contract to dogfood")
    return 0


if __name__ == "__main__":
    sys.exit(main())
