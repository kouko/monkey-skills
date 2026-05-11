#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""build_baseline — pack `baseline-source/` into a deterministic tarball
plus a YAML manifest describing what's inside.

Inputs (resolved relative to plugin root):
  legal-toolkit/baseline-source/                # source tree (8 clauses,
                                                # 4 flat + 4 variant-folder)

Outputs (overwritten):
  legal-toolkit/skills/legal-contract-review/assets/baseline-playbooks.tar.gz
  legal-toolkit/skills/legal-contract-review/assets/seed-manifest.yml

Reproducibility — the build is deterministic:
  - file order via sorted() walks
  - tar entry mtime fixed to a constant SOURCE_DATE_EPOCH (so output bytes
    don't drift with the filesystem)
  - file mode normalised to 0o644 for files and 0o755 for dirs
  - gzip header pinned (mtime=0, no filename, no comment)

If the committed artifact and a freshly-built one ever diverge, that's a
real source change — investigate. Run `--check` to verify drift without
overwriting.

Usage:
    build_baseline.py
    build_baseline.py --check
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import re
import sys
import tarfile
from pathlib import Path

import yaml


# Resolve plugin root by walking up to a dir that contains
# .claude-plugin/plugin.json (defensive — script may be invoked
# from anywhere).
def _plugin_root() -> Path:
    p = Path(__file__).resolve()
    for ancestor in [p, *p.parents]:
        if (ancestor / ".claude-plugin" / "plugin.json").is_file():
            return ancestor
    raise SystemExit("build_baseline: could not locate plugin root")


PLUGIN_ROOT = _plugin_root()
SOURCE_DIR = PLUGIN_ROOT / "baseline-source"
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

# Fixed mtime / mode for deterministic tar entries.
FIXED_MTIME = 1700000000  # 2023-11-14 — arbitrary but stable

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def _normalise_tarinfo(ti: tarfile.TarInfo, *, is_dir: bool) -> tarfile.TarInfo:
    ti.uid = 0
    ti.gid = 0
    ti.uname = "root"
    ti.gname = "root"
    ti.mtime = FIXED_MTIME
    ti.mode = 0o755 if is_dir else 0o644
    return ti


def _enumerate_entries() -> list[dict]:
    """Walk baseline-source/ and produce a clause inventory."""
    entries: list[dict] = []
    if not SOURCE_DIR.is_dir():
        raise SystemExit(f"baseline-source directory missing: {SOURCE_DIR}")
    for child in sorted(SOURCE_DIR.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_file() and child.suffix == ".md":
            entries.append(
                {
                    "clause_id": child.stem,
                    "layout": "flat",
                    "files": [child.name],
                }
            )
        elif child.is_dir():
            if not (child / "_clause.md").is_file():
                continue
            files = []
            for vf in sorted(child.iterdir()):
                if vf.is_file() and vf.suffix == ".md":
                    files.append(f"{child.name}/{vf.name}")
            entries.append(
                {
                    "clause_id": child.name,
                    "layout": "variant-folder",
                    "files": files,
                }
            )
    return entries


def _build_tarball_bytes(entries: list[dict]) -> bytes:
    """Produce the deterministic gzipped-tar bytes for the given entries."""
    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode="w") as tar:
        for entry in entries:
            if entry["layout"] == "flat":
                rel = entry["files"][0]
                src = SOURCE_DIR / rel
                data = src.read_bytes()
                ti = tarfile.TarInfo(name=rel)
                ti.size = len(data)
                _normalise_tarinfo(ti, is_dir=False)
                tar.addfile(ti, io.BytesIO(data))
            elif entry["layout"] == "variant-folder":
                # Emit the dir entry first
                dir_name = entry["clause_id"]
                ti_dir = tarfile.TarInfo(name=dir_name)
                ti_dir.type = tarfile.DIRTYPE
                _normalise_tarinfo(ti_dir, is_dir=True)
                tar.addfile(ti_dir)
                for rel in entry["files"]:
                    src = SOURCE_DIR / rel
                    data = src.read_bytes()
                    ti = tarfile.TarInfo(name=rel)
                    ti.size = len(data)
                    _normalise_tarinfo(ti, is_dir=False)
                    tar.addfile(ti, io.BytesIO(data))
    raw_tar = inner.getvalue()
    # gzip with stable header (mtime=0)
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", mtime=0, compresslevel=9) as gz:
        gz.write(raw_tar)
    return out.getvalue()


def _build_manifest(entries: list[dict], tarball_sha256: str) -> dict:
    return {
        "version": "1.0",
        "seeded_at_target": "legal-playbook/",
        "tarball_sha256": tarball_sha256,
        "total_clauses": len(entries),
        "total_files": sum(len(e["files"]) for e in entries),
        "entries": entries,
        "build_notes": (
            "Built by scripts/build_baseline.py. Source: <plugin>/baseline-source/. "
            "Tarball entries: deterministic mtime + sorted walk; bytes are stable "
            "across builds. If you edit a baseline clause, re-run "
            "scripts/build_baseline.py to refresh the artifact, then verify "
            "tests/test_seed_baseline.py still passes."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed artifact matches a fresh build; exit 1 on drift",
    )
    args = parser.parse_args()

    entries = _enumerate_entries()
    tar_bytes = _build_tarball_bytes(entries)
    sha256 = hashlib.sha256(tar_bytes).hexdigest()
    manifest = _build_manifest(entries, sha256)
    manifest_text = yaml.safe_dump(
        manifest, allow_unicode=True, sort_keys=False, default_flow_style=False
    )

    if args.check:
        if not TARBALL_PATH.exists():
            print(f"check: missing tarball {TARBALL_PATH}", file=sys.stderr)
            return 1
        if not MANIFEST_PATH.exists():
            print(f"check: missing manifest {MANIFEST_PATH}", file=sys.stderr)
            return 1
        committed_tar = TARBALL_PATH.read_bytes()
        committed_manifest = MANIFEST_PATH.read_text(encoding="utf-8")
        ok = True
        if committed_tar != tar_bytes:
            print("check: tarball drift detected", file=sys.stderr)
            print(
                f"  committed sha256: {hashlib.sha256(committed_tar).hexdigest()}",
                file=sys.stderr,
            )
            print(f"  fresh sha256:     {sha256}", file=sys.stderr)
            ok = False
        if committed_manifest != manifest_text:
            print("check: manifest drift detected", file=sys.stderr)
            ok = False
        if not ok:
            return 1
        print("check: PASS — tarball + manifest match a fresh build")
        return 0

    TARBALL_PATH.parent.mkdir(parents=True, exist_ok=True)
    TARBALL_PATH.write_bytes(tar_bytes)
    MANIFEST_PATH.write_text(manifest_text, encoding="utf-8")
    print(f"wrote {TARBALL_PATH.relative_to(PLUGIN_ROOT)} ({len(tar_bytes)} bytes)")
    print(f"wrote {MANIFEST_PATH.relative_to(PLUGIN_ROOT)}")
    print(f"sha256: {sha256}")
    print(f"clauses: {len(entries)}, files: {sum(len(e['files']) for e in entries)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
