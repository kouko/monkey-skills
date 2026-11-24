#!/usr/bin/env python3
"""Rebuild W17 frozen replay inputs under /private/tmp/toolkit-w18-replay-20261124.

Sources:
- original/target + holdouts case-k/m targets: tracked git blobs at ref
  35a6be1446a3636450a6d94886195d37018da9b1 (skill-refactor / skill-creator-advance).
- raw detector JSON: committed case (original) + research/scope-diagnostic-20261109
  case-inputs.json (all three, byte-verified against archive preimage hashes).

Verifies every written file's SHA256 against the W17 archive input_preimages.
Read-only with respect to the repository. Exits nonzero on any hash mismatch.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/Users/kouko/GitHub/monkey-skills")
ARC_PATH = REPO / "docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/w17-scope-first-results.json"
DIAG_PATH = REPO / "docs/loom/2026-11-02-repair-skill-dev-toolkit/research/scope-diagnostic-20261109/case-inputs.json"
CASE_DIR = REPO / "skill-dev-toolkit/tests/caller-review-cases/overstated-original-claim"
TARGET_BLOBS = {
    "original": ("35a6be1446a3636450a6d94886195d37018da9b1", "skill-dev-toolkit/skills/skill-refactor", "original/target/"),
    "case-k": ("35a6be1446a3636450a6d94886195d37018da9b1", "skill-dev-toolkit/skills/skill-creator-advance", "holdouts/case-k/target/"),
    "case-m": ("cd2c2c02851f114559097f689892384332c69975", "skill-dev-toolkit/skills/skill-creator-advance", "holdouts/case-m/target/"),
}

arc = json.loads(ARC_PATH.read_text())
pre = arc["input_preimages"]
diag = json.loads(DIAG_PATH.read_text())
root = pathlib.Path("/private/tmp/toolkit-w18-replay-20261124/inputs")
root.mkdir(parents=True, exist_ok=True)

mismatches = []
written = 0


def git_show(ref: str, git_path: str) -> bytes:
    p = subprocess.run(
        ["git", "show", f"{ref}:{git_path}"],
        capture_output=True, cwd=REPO, check=True,
    )
    return p.stdout


def write_verified(rel_key: str, data: bytes, dest: pathlib.Path) -> None:
    global written
    expect = pre.get(rel_key)
    h = hashlib.sha256(data).hexdigest()
    if expect is None:
        mismatches.append((rel_key, "no-archive-hash", h))
        return
    if h != expect:
        mismatches.append((rel_key, h, expect))
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    written += 1


def case_dir_rel(case: str) -> str:
    return "original" if case == "original" else f"holdouts/{case}"


# 1. Target trees from tracked git blobs
for case, (ref, pkg, prefix) in TARGET_BLOBS.items():
    files = sorted(k[len(prefix):] for k in pre if k.startswith(prefix))
    tgt_root = root / case_dir_rel(case) / "target"
    for f in files:
        data = git_show(ref, f"{pkg}/{f}")
        write_verified(prefix + f, data, tgt_root / f)

# 2. Raw detector JSON
for case in ["original", "case-k", "case-m"]:
    base = root / case_dir_rel(case)
    for name in ["read-1.json", "simulate-1.json"]:
        if case == "original":
            data = (CASE_DIR / name).read_bytes()
            write_verified(f"{case}/{name}", data, base / name)
        else:
            raw = diag[case]["sources"][name]
            write_verified(f"holdouts/{case}/{name}", raw.encode(), base / name)

print(f"written={written} mismatches={len(mismatches)}")
for m in mismatches[:20]:
    print("  MISMATCH:", m)
sys.exit(1 if mismatches else 0)
