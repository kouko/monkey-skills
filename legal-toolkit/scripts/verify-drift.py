#!/usr/bin/env python3
"""Verify each ROUTE destination is byte-identical to its canonical source.

Exit 0 -> every routed destination exists and matches canonical.
Exit 1 -> at least one drift (mismatch, missing file, or missing canonical).

No auto-skip — every entry in ROUTE is mandatory. Update ROUTE in the same
commit that creates (or removes) a consuming skill.

CI gate: runs after every PR / push that touches legal-toolkit/.
"""
from __future__ import annotations

import filecmp
import hashlib
import re
import subprocess
import sys
from pathlib import Path

# Reuse routing from distribute.py for consistency.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from distribute import (  # type: ignore  # noqa: E402
    CANONICAL_DIR,
    ROOT,
    ROUTE,
)


def verify_drift(
    route: dict[str, list[str]] | None = None,
    root: Path | None = None,
) -> int:
    """Return 0 if every routed destination matches its canonical source; 1
    otherwise. Pure function — does not touch the real filesystem unless
    `root` defaults to ROOT.
    """
    if route is None:
        route = ROUTE
    if root is None:
        root = ROOT
    canonical_dir = root / "scripts" / "canonical"

    drifts: list[str] = []
    checked = 0
    for canonical_name, destinations in route.items():
        src = canonical_dir / canonical_name
        if not src.is_file():
            drifts.append(f"MISSING-CANONICAL  scripts/canonical/{canonical_name}")
            continue
        for rel_dst in destinations:
            dst = root / rel_dst
            if not dst.is_file():
                drifts.append(f"MISSING  {rel_dst}")
                continue
            if not filecmp.cmp(src, dst, shallow=False):
                drifts.append(
                    f"DRIFT    {rel_dst} differs from scripts/canonical/{canonical_name}"
                )
            checked += 1
    if drifts:
        for d in drifts:
            print(d)
        return 1
    print(f"OK: all {checked} functional copies byte-identical to canonical.")
    return 0


def _md5(path: Path) -> str:
    # usedforsecurity=False keeps this working on FIPS-140 systems (md5 is
    # used here as a fingerprint for the drift report, not a security primitive).
    return hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()


def _print_unified_diff(reference: Path, drift_path: Path, max_lines: int = 50) -> None:
    """Print up to max_lines of `diff -u` output so reviewers see WHAT differs,
    not just THAT it differs. Also print md5 for both files.
    """
    print(f"    md5(canonical) = {_md5(reference)}")
    print(f"    md5(copy)      = {_md5(drift_path)}")
    try:
        out = subprocess.run(
            ["diff", "-u", str(reference), str(drift_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        text = out.stdout or out.stderr or ""
        lines = text.splitlines()
        for line in lines[:max_lines]:
            print(f"    {line}")
        if len(lines) > max_lines:
            print(f"    ... ({len(lines) - max_lines} more lines truncated)")
    except FileNotFoundError:
        print("    (diff binary unavailable)")


# --------------------------------------------------------- 4-grader bank drift
# Per spec §7.3 (docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md),
# PATH_A_ANTIPATTERNS bank + _check_no_template_orphans helper must stay
# byte-identical across SP3a/SP3b/v0.5.0/v0.5.2 graders so future legal updates
# land in one place per skill but never silently drift.
#
# Scope notes:
# - PATH_A_ANTIPATTERNS bank check: required across ALL listed graders.
# - _check_no_template_orphans helper check: only required across graders that
#   define it. grade_draft.py predates the helper (uses its own
#   `_check_no_orphans` with a different scope — single doc, broader pattern)
#   and is exempt; spec §7.3's all-4-graders directive is implemented for the
#   3 graders that have the helper today (response + issue-spot + research).

GRADERS_FOR_BANK_DRIFT_CHECK: list[Path] = [
    ROOT / "skills" / "legal-document-draft" / "scripts" / "grade_draft.py",
    ROOT / "skills" / "legal-incident-response" / "scripts" / "grade_response.py",
    ROOT / "skills" / "legal-issue-spot" / "scripts" / "grade_issue_spot.py",
    # legal-research grader (v0.5.2 SP3-b)
    ROOT / "skills" / "legal-research" / "scripts" / "grade_research.py",
]

# Bank: literal `[...]` body of `PATH_A_ANTIPATTERNS = [...]`.
_PAT_BANK = re.compile(r"PATH_A_ANTIPATTERNS\s*=\s*\[(.*?)\]", re.DOTALL)


def _extract_func_body(text: str, name: str) -> str | None:
    """Return `def <name>(...):` plus its indented body, stopping at the next
    top-level statement. Returns None if not found.

    Uses indentation rather than the spec's lookahead regex so trailing comment
    headers (`# ---- next section`) between the helper and the next `def` do
    NOT bleed into the captured chunk and produce false drift signals.
    """
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_func = False
    prefix = f"def {name}("
    for ln in lines:
        if not in_func:
            if ln.startswith(prefix):
                in_func = True
                out.append(ln)
            continue
        # Inside the function: keep indented lines + blank lines; stop on the
        # first unindented non-blank line (next top-level def / class / comment).
        if ln.strip() == "" or ln[0] in (" ", "\t"):
            out.append(ln)
            continue
        break
    if not out:
        return None
    # Trim trailing blank lines so a stray blank line below the function body
    # does not cause spurious drift.
    while out and out[-1].strip() == "":
        out.pop()
    return "".join(out)


def verify_grader_bank_drift(
    graders: list[Path] | None = None,
) -> list[str]:
    """Verify PATH_A_ANTIPATTERNS literal bank + _check_no_template_orphans
    helper byte-identical across the registered graders.

    Bank: required in every grader.
    Helper: required only across graders that define it (must agree among
    those that do). Graders without the helper are silently skipped for the
    helper check — see module comment above.

    Returns a list of error strings; empty list = no drift.
    """
    if graders is None:
        graders = GRADERS_FOR_BANK_DRIFT_CHECK

    errs: list[str] = []
    bank_chunks: list[tuple[str, str]] = []
    orphan_chunks: list[tuple[str, str]] = []

    for g in graders:
        if not g.exists():
            errs.append(f"grader not found: {g}")
            continue
        text = g.read_text(encoding="utf-8")

        bank_match = _PAT_BANK.search(text)
        if not bank_match:
            errs.append(f"PATH_A_ANTIPATTERNS bank not found in {g.name}")
        else:
            bank_chunks.append((g.name, bank_match.group(1).strip()))

        orphan_body = _extract_func_body(text, "_check_no_template_orphans")
        if orphan_body is not None:
            orphan_chunks.append((g.name, orphan_body.strip()))
        # else: helper not defined in this grader; skip per scope note above.

    if len({c for _, c in bank_chunks}) > 1:
        names = sorted(n for n, _ in bank_chunks)
        errs.append(
            f"PATH_A_ANTIPATTERNS drift across graders: {names}"
        )
    if len({c for _, c in orphan_chunks}) > 1:
        names = sorted(n for n, _ in orphan_chunks)
        errs.append(
            f"_check_no_template_orphans drift across graders: {names}"
        )

    return errs


def main() -> int:
    if not CANONICAL_DIR.is_dir():
        print(f"ERROR: canonical directory not found: {CANONICAL_DIR}", file=sys.stderr)
        return 2

    drifts: list[tuple[str, Path | None, Path | None]] = []
    checked = 0
    for canonical_name, destinations in ROUTE.items():
        src = CANONICAL_DIR / canonical_name
        if not src.is_file():
            drifts.append(
                (f"MISSING-CANONICAL  scripts/canonical/{canonical_name}", None, None)
            )
            continue
        for rel_dst in destinations:
            dst = ROOT / rel_dst
            if not dst.is_file():
                drifts.append((f"MISSING  {rel_dst}", None, None))
                continue
            if not filecmp.cmp(src, dst, shallow=False):
                drifts.append(
                    (
                        f"DRIFT    {rel_dst} differs from scripts/canonical/{canonical_name}",
                        src,
                        dst,
                    )
                )
            checked += 1

    # Both checks run before deciding exit code so reviewers see ALL drift
    # in one run, not just the first category.
    canonical_failed = bool(drifts)
    grader_errs = verify_grader_bank_drift()

    if canonical_failed:
        for label, ref, drift_path in drifts:
            print(label)
            if ref is not None and drift_path is not None:
                _print_unified_diff(ref, drift_path)
        print(f"\nFAIL: {len(drifts)} drift(s) detected (checked {checked} pairs).")
        print("Fix locally: python3 legal-toolkit/scripts/distribute.py")
    else:
        print(f"OK: all {checked} functional copies byte-identical to canonical.")

    if grader_errs:
        print()
        for e in grader_errs:
            print(f"GRADER-DRIFT  {e}")
        print(
            f"\nFAIL: {len(grader_errs)} grader-bank drift(s) detected "
            f"across {len(GRADERS_FOR_BANK_DRIFT_CHECK)} grader(s)."
        )
        print(
            "Fix locally: align PATH_A_ANTIPATTERNS bank + "
            "_check_no_template_orphans helper byte-identical across graders "
            "(see spec §7.3)."
        )
    else:
        print(
            f"OK: {len(GRADERS_FOR_BANK_DRIFT_CHECK)}-grader PATH_A bank + "
            "template-orphan helper byte-identical."
        )

    return 1 if (canonical_failed or grader_errs) else 0


if __name__ == "__main__":
    sys.exit(main())
