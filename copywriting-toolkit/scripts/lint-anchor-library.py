#!/usr/bin/env python3
"""Lint copywriting-toolkit voice anchor library.

Checks each `standards/anchor-{slug}.md` file against the v2 schema defined in
`standards/voice-anchor-meta.md §Schema (v2 — single active schema)`, plus the
machine-checkable portions of the 4-condition anchor selection rubric.

Moved from Pass 3 runtime to library-entry CI lint in v1.13.0 — Pass 3 now
trusts that any anchor in the library has already passed these checks.

Usage:
    python scripts/lint-anchor-library.py           # lint default path (anchors dir)
    python scripts/lint-anchor-library.py --strict  # exit 1 on any warning (default: only errors)
    python scripts/lint-anchor-library.py path/to/anchor-{slug}.md  # lint single file

Exit codes:
    0 — all files pass
    1 — at least one ERROR detected (blocks merge)
    2 — warnings only, strict mode (soft block)
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

DEFAULT_ANCHOR_DIR = Path(__file__).parent.parent / "skills" / "copywriting-voice-tone-stage" / "standards"
ANCHOR_FILENAME_GLOB = "anchor-*.md"

REQUIRED_FRONTMATTER_FIELDS = {
    "schema_version",
    "anchor_slug",
    "culture",
    "quadrant",
    "landmark",
    "creator_type",
}

REQUIRED_BODY_SECTIONS = [
    # (section header pattern, human-readable name)
    (r"^##\s+Voice direction\s*$", "## Voice direction"),
    (r"^##\s+Prose mechanics", "## Prose mechanics"),
    (r"^##\s+Examples", "## Examples"),
    (r"^##\s+Don't\s*/\s*Over-mimic", "## Don't / Over-mimic"),
    # Metadata check is flexible (handled by check_metadata) — some anchors use ## Metadata
    # section, others use flat ## Trigger slug: / ## Over-mimic risk: H2 headers. Either is valid.
]

VALID_CULTURES = {"jp", "zh", "zh-TW", "zh-HK", "zh-CN", "en", "kr"}
VALID_QUADRANTS = {"Q1", "Q2", "Q3", "Q4"}
VALID_EDGE_QUADRANTS = {"Q1-Q2", "Q2-Q3", "Q3-Q4", "Q1-Q4"}  # edge/transition; accepted with warn
VALID_LANDMARKS = {"center", "extreme", "toward-Q1", "toward-Q2", "toward-Q3", "toward-Q4",
                   "axis-authority", "axis-affinity", "axis-reason", "axis-emotion"}
VALID_OVER_MIMIC_RISK = {"LOW", "LOW-MEDIUM", "MEDIUM", "MEDIUM-HIGH", "HIGH", "HIGH+", "HARD"}

MITIGATION_WORD_LIMIT = 20  # ≤15 per spec + 5-word tolerance for punctuation / fillers


@dataclass
class LintResult:
    filepath: Path
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def format(self) -> str:
        lines = [f"[{'PASS' if self.passed else 'FAIL'}] {self.filepath.name}"]
        for err in self.errors:
            lines.append(f"  ERROR: {err}")
        for warn in self.warnings:
            lines.append(f"  WARN:  {warn}")
        return "\n".join(lines)


def parse_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """Extract YAML-ish frontmatter and return (frontmatter_dict, body_text).

    Returns (None, full_content) if no frontmatter detected.
    Simple parser — handles flat key: value pairs only (sufficient for v2 schema).
    """
    if not content.startswith("---"):
        return None, content
    end_match = re.search(r"^---\s*$", content[3:], re.MULTILINE)
    if not end_match:
        return None, content
    end_idx = 3 + end_match.start()
    fm_text = content[3:end_idx].strip()
    body = content[end_idx + 4:]  # skip `---\n`

    frontmatter = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip()
    return frontmatter, body


def check_frontmatter(fm: Optional[dict], result: LintResult) -> None:
    """Validate frontmatter structure."""
    if fm is None:
        result.errors.append("missing YAML frontmatter (must start with ---)")
        return

    missing = REQUIRED_FRONTMATTER_FIELDS - set(fm.keys())
    if missing:
        result.errors.append(f"frontmatter missing required fields: {sorted(missing)}")

    # Type/enum checks on present fields
    schema_version = fm.get("schema_version", "").strip("\"'")
    if schema_version and schema_version != "2.0":
        result.errors.append(f"schema_version must be 2.0 (v1 removed in v1.13.0); got: {schema_version!r}")

    culture = fm.get("culture", "").strip("\"'")
    if culture and culture.lower() not in {c.lower() for c in VALID_CULTURES}:
        result.warnings.append(f"culture {culture!r} not in expected set {sorted(VALID_CULTURES)}")

    quadrant = fm.get("quadrant", "").strip("\"'")
    if quadrant and quadrant not in VALID_QUADRANTS:
        if quadrant in VALID_EDGE_QUADRANTS:
            result.warnings.append(f"quadrant {quadrant!r} is an edge designation; primary quadrant preferred")
        else:
            result.errors.append(
                f"quadrant must be one of {sorted(VALID_QUADRANTS)} (edges allowed: {sorted(VALID_EDGE_QUADRANTS)}); got: {quadrant!r}"
            )

    landmark = fm.get("landmark", "").strip("\"'")
    if landmark and landmark not in VALID_LANDMARKS:
        result.warnings.append(f"landmark {landmark!r} not in expected set (may be custom): {sorted(VALID_LANDMARKS)}")


def check_body_sections(body: str, result: LintResult) -> None:
    """Validate required v2 body sections are present."""
    for pattern, name in REQUIRED_BODY_SECTIONS:
        if not re.search(pattern, body, re.MULTILINE):
            result.errors.append(f"missing required section: {name}")


def extract_section(body: str, section_header_pattern: str) -> Optional[str]:
    """Extract the text of a section from its H2 header until the next H2 (or EOF)."""
    match = re.search(section_header_pattern, body, re.MULTILINE)
    if not match:
        return None
    start = match.end()
    next_h2 = re.search(r"^##\s+", body[start:], re.MULTILINE)
    if next_h2:
        return body[start:start + next_h2.start()]
    return body[start:]


def count_list_items(section_text: str) -> int:
    """Count list items — accepts `- `, `* `, or `N. ` forms."""
    if not section_text:
        return 0
    count = 0
    numbered_re = re.compile(r"^\d+\.\s")
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            count += 1
        elif numbered_re.match(stripped):
            count += 1
    return count


def check_native_critical_read(body: str, result: LintResult) -> None:
    """Check that Voice direction section contains Native critical read with ≥3 entries."""
    vd_section = extract_section(body, r"^##\s+Voice direction\s*$")
    if not vd_section:
        return  # already flagged by body section check
    ncr_match = re.search(r"\*\*Native critical read\*\*", vd_section)
    if not ncr_match:
        result.errors.append("§Voice direction missing **Native critical read** block")
        return
    ncr_text = vd_section[ncr_match.end():]
    # Count bullet items until next bold header or section end
    next_bold = re.search(r"\n\*\*", ncr_text)
    ncr_body = ncr_text[:next_bold.start()] if next_bold else ncr_text
    count = count_list_items(ncr_body)
    if count < 3:
        result.errors.append(f"Native critical read has {count} entries; v2 schema requires ≥3")


def check_prose_mechanics(body: str, result: LintResult) -> None:
    """Check ≥5 actionable rules in Prose mechanics."""
    section = extract_section(body, r"^##\s+Prose mechanics")
    if section is None:
        return
    count = count_list_items(section)
    if count < 5:
        result.errors.append(f"Prose mechanics has {count} bullet items; v2 schema requires ≥5")


def check_examples(body: str, result: LintResult) -> None:
    """Check ≥5 verbatim examples (bullet items with source-like context)."""
    section = extract_section(body, r"^##\s+Examples")
    if section is None:
        return
    count = count_list_items(section)
    if count < 5:
        result.errors.append(f"Examples has {count} verbatim entries; v2 schema requires ≥5")


def check_dont_over_mimic(body: str, result: LintResult) -> None:
    """Check failure mode + ≤15-word mitigation (soft-cap 20 words for tolerance)."""
    section = extract_section(body, r"^##\s+Don't\s*/\s*Over-mimic")
    if section is None:
        return
    if not re.search(r"(?:\*\*Failure mode\*\*|Failure mode:)", section):
        result.errors.append("§Don't / Over-mimic missing **Failure mode** entry")
    mit_match = re.search(r"\*\*Mitigation\*\*(?:\s*\(.*?\))?\s*:?\s*[\"『]?([^\"『』\n]+)[\"』]?", section)
    if not mit_match:
        result.warnings.append("§Don't / Over-mimic Mitigation clause not extractable by regex (check manually)")
        return
    clause = mit_match.group(1).strip()
    # Rough word count — split on whitespace and CJK punctuation
    words = [w for w in re.split(r"[\s、，；;,]+", clause) if w]
    if len(words) > MITIGATION_WORD_LIMIT:
        result.warnings.append(
            f"Mitigation clause is {len(words)} words; v2 schema prefers ≤15 (hard cap 20): {clause!r}"
        )


def check_metadata(body: str, result: LintResult) -> None:
    """Check metadata fields exist (in ## Metadata section OR as flat ## <field>: headers).

    Two valid patterns:
    1. Grouped: `## Metadata` section containing `- Trigger slug:`, `- Over-mimic risk:`, etc.
    2. Flat: top-level H2 headers like `## Trigger slug: ...`, `## Over-mimic risk: ...`
    Either is accepted; the check scans the whole body for the field.
    """
    # Check for ## Metadata section
    metadata_section = extract_section(body, r"^##\s+Metadata")
    has_metadata_section = metadata_section is not None

    # Over-mimic risk (required)
    risk_in_section = re.search(r"Over-mimic risk\s*:\s*([A-Z+\-]+)", body)
    if not risk_in_section:
        result.errors.append("missing `Over-mimic risk:` line (looked in §Metadata section and flat H2 headers)")
    else:
        risk = risk_in_section.group(1).strip()
        if risk not in VALID_OVER_MIMIC_RISK:
            result.warnings.append(
                f"Over-mimic risk {risk!r} not in canonical set {sorted(VALID_OVER_MIMIC_RISK)}"
            )

    # Trigger slug (recommended)
    if not re.search(r"Trigger slug", body):
        result.warnings.append("missing `Trigger slug` entry (non-blocking but recommended)")

    # Pairs with form (recommended, non-blocking)
    if not re.search(r"Pairs with form", body):
        result.warnings.append("missing `Pairs with form` entry (non-blocking but recommended)")

    # Encourage grouped Metadata section for consistency
    if not has_metadata_section:
        result.warnings.append(
            "metadata uses flat H2 headers; v2 schema prefers grouped `## Metadata` section (non-blocking)"
        )


def lint_anchor_file(filepath: Path) -> LintResult:
    """Run all checks against a single anchor file."""
    result = LintResult(filepath=filepath)
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        result.errors.append(f"cannot read file: {e}")
        return result

    frontmatter, body = parse_frontmatter(content)
    check_frontmatter(frontmatter, result)
    check_body_sections(body, result)
    check_native_critical_read(body, result)
    check_prose_mechanics(body, result)
    check_examples(body, result)
    check_dont_over_mimic(body, result)
    check_metadata(body, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path, help="anchor files to lint (default: all)")
    parser.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    parser.add_argument("--anchor-dir", type=Path, default=DEFAULT_ANCHOR_DIR,
                        help=f"directory to scan (default: {DEFAULT_ANCHOR_DIR})")
    args = parser.parse_args()

    if args.paths:
        files = args.paths
    else:
        files = sorted(args.anchor_dir.glob(ANCHOR_FILENAME_GLOB))

    if not files:
        print(f"ERROR: no anchor files found (searched: {args.anchor_dir})", file=sys.stderr)
        return 1

    results = [lint_anchor_file(f) for f in files]
    n_total = len(results)
    n_failed = sum(1 for r in results if r.errors)
    n_warned = sum(1 for r in results if r.warnings and not r.errors)
    n_pass_clean = n_total - n_failed - n_warned

    # Print per-file report (only failures + warnings; clean passes summarized)
    for r in results:
        if r.errors or r.warnings:
            print(r.format())

    print()
    print(f"Summary: {n_pass_clean} clean / {n_warned} with warnings / {n_failed} failed / {n_total} total")

    if n_failed > 0:
        return 1
    if args.strict and n_warned > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
