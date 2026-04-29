#!/usr/bin/env python3
"""check-skill-structure.py — validate domain-team SKILL.md files against
skill-team's CHK-SKL-* rules from skill-completeness-checklist.md.

Usage:
    scripts/check-skill-structure.py <plugin-dir>
    scripts/check-skill-structure.py domain-teams

Discovers every `<plugin-dir>/skills/*/SKILL.md` and runs the checks
below against it. Exits 0 if every check passes for every SKILL.md;
exits 1 on any failure.

Checks (subset of skill-team v4.8.1 CHK-SKL-* rules — chosen because
they are deterministic and useful at PR time; the LLM-judgment-heavy
items like CHK-SKL-002 persona block live in the dogfood evaluator
gate, not here):

    CHK-SKL-001 (FATAL)  — frontmatter description >= 40 word tokens
                            after CJK/punctuation exclusion and
                            hyphen/slash splitting; router skills
                            (no protocols/ subdirectory, no worker
                            launch template in SKILL.md) are exempt
    CHK-SKL-005 (FATAL)  — every relative path referenced in the
                            Resource Manifest section OR in worker /
                            evaluator launch templates actually exists
                            on disk. Aspirational paths in MAY gate
                            tables and "Future candidates" prose are
                            NOT validated (those are forward-looking
                            references, not runtime dependencies)
    CHK-SKL-010 (FATAL)  — SKILL.md word count <= 4,500 words
                            (~6,000 tokens) per the token budget
                            defined in skill-md-structure.md §Token
                            Budget. Word count is used as a stable
                            proxy for token count because line count
                            varies too much with density (noted in
                            v4.19.1 line->token migration). The earlier
                            500-line cap is retired.
    CHK-SKL-011 (FATAL)  — no absolute paths (`/Users/...`) and no
                            plugin-rooted paths (`domain-teams/skills/
                            ...`) in SKILL.md. Standards / protocols /
                            checklists / rubrics files are NOT scanned
                            because they legitimately reference example
                            paths inside markdown code blocks and
                            inline backticks (path resolution examples,
                            anti-pattern documentation, primary source
                            citations to repo SSOT files outside the
                            plugin)
    CHK-SKL-012 (FATAL)  — directory layout: required subdirectories
                            `standards/`, `protocols/`, `checklists/`,
                            `rubrics/`; optional `research/`; any
                            other subdirectory is FATAL; if `research/`
                            exists, every file inside MUST match
                            `grounding-v{X.Y.Z}.md` pattern.
                            Router skills are exempt from the
                            required-subdirectory check. `.DS_Store`
                            and other dotfiles are ignored as
                            filesystem noise.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# CHK-SKL-001 — frontmatter description word count
# ---------------------------------------------------------------------------

# Per skill-md-structure.md §Frontmatter Schema:
#   - 40-word floor for non-router skills
#   - exclude YAML tokens, CJK/bilingual suffix lines, punctuation
#   - hyphenated and slash-separated compounds split into tokens
WORD_FLOOR = 40

# Punctuation that should be stripped before tokenization. Includes both
# ASCII and CJK punctuation per the standard.
STRIP_CHARS = "·—・。、「」『』`「』-/"

# Characters that signal a CJK/bilingual suffix line — if a line contains
# any of these, treat it as a non-prose suffix and exclude entirely.
CJK_RANGE = re.compile(r"[\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]")

# YAML scalar style markers to skip when reading the description.
YAML_MARKERS = {">-", ">", "|", "|-"}


@dataclass
class CheckError:
    """A single check failure with file path and human-readable detail."""

    rule: str
    skill: str
    detail: str
    path: Path | None = None

    def format(self) -> str:
        loc = f"{self.path}: " if self.path else ""
        return f"  {loc}{self.detail}"


def parse_frontmatter(skill_md: Path) -> dict[str, str] | None:
    """Return the YAML frontmatter as a {field: raw_value} dict, or None.

    Only handles the two fields `name` and `description` since those are the
    only ones the checks need. The description value is returned as the
    multi-line block joined by spaces with leading whitespace collapsed.
    """
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block = text[4:end]
    fields: dict[str, str] = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val in YAML_MARKERS:
                # Multi-line scalar — collect indented continuation lines.
                buf: list[str] = []
                i += 1
                while i < len(lines) and (
                    lines[i].startswith(" ") or lines[i].startswith("\t")
                ):
                    buf.append(lines[i].strip())
                    i += 1
                fields[key] = " ".join(buf)
                continue
            fields[key] = val
        i += 1
    return fields


def tokenize_description(description: str) -> list[str]:
    """Apply the CHK-SKL-001 tokenization rule and return Latin word tokens.

    Per skill-md-structure.md §Frontmatter Schema §Word count rule, the
    floor counts only the **English prose body** of the description.

    Steps:
    1. Collapse hyphens and slashes into spaces so `code-team` counts as
       2 tokens and `UX/UI` counts as 2 tokens.
    2. Strip ASCII + CJK punctuation listed in the standard.
    3. Split on whitespace.
    4. Drop tokens containing any CJK character — this naturally
       handles BOTH the "bilingual keyword suffix line" case (where
       every token on the line is CJK) AND mixed prose lines that
       contain occasional CJK words like 徳丸本 / 第 2 版.
    5. Drop empty / pure-punctuation residue.
    """
    text = description
    # Collapse hyphens and slashes into spaces so split tokenizes them.
    text = re.sub(r"[-/]", " ", text)
    # Strip the punctuation listed in the standard.
    for ch in STRIP_CHARS:
        text = text.replace(ch, " ")
    # Drop residual ASCII single-char punctuation.
    text = re.sub(r"[.,;:()\[\]{}\"']", " ", text)
    tokens: list[str] = []
    for raw in text.split():
        if not raw:
            continue
        if CJK_RANGE.search(raw):
            continue  # Skip CJK tokens — count only English prose.
        tokens.append(raw)
    return tokens


def is_router_skill(skill_dir: Path) -> bool:
    """Detect router skills exempt from CHK-SKL-001 word floor.

    Heuristic per skill-md-structure.md §Router-skill exemption: a router
    has no `protocols/` directory and the SKILL.md has no worker / evaluator
    launch templates. The current example is `using-domain-teams`.
    """
    if not (skill_dir / "protocols").is_dir():
        return True
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False
    text = skill_md.read_text(encoding="utf-8")
    has_worker_template = "### Task" in text and "### Resource Paths" in text
    return not has_worker_template


def check_chk_skl_001(skill_dir: Path) -> list[CheckError]:
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    fm = parse_frontmatter(skill_md)
    if fm is None or "description" not in fm:
        return [CheckError("CHK-SKL-001", name, "frontmatter or description field missing", skill_md)]
    if is_router_skill(skill_dir):
        return []
    tokens = tokenize_description(fm["description"])
    if len(tokens) < WORD_FLOOR:
        return [
            CheckError(
                "CHK-SKL-001",
                name,
                f"description has {len(tokens)} word tokens (floor: {WORD_FLOOR})",
                skill_md,
            )
        ]
    return []


# ---------------------------------------------------------------------------
# CHK-SKL-005 — Resource Manifest paths exist
# ---------------------------------------------------------------------------

# Backtick-wrapped relative path inside SKILL.md, e.g. `standards/x.md`.
BACKTICK_PATH = re.compile(r"`((?:standards|protocols|checklists|rubrics)/[A-Za-z0-9_.-]+\.md)`")
# Launch template path with {base_path} placeholder, e.g. {base_path}/standards/x.md
BASEPATH_PATH = re.compile(r"\{base_path\}/((?:standards|protocols|checklists|rubrics)/[A-Za-z0-9_.-]+\.md)")


def _extract_section(text: str, header: str) -> str:
    """Return the body of a markdown `## header` section, or empty string.

    Section ends at the next `## ` heading or end of file.
    """
    lines = text.splitlines()
    start = -1
    for i, line in enumerate(lines):
        if line.startswith(f"## {header}"):
            start = i + 1
            break
    if start == -1:
        return ""
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## ") and not lines[j].startswith("###"):
            end = j
            break
    return "\n".join(lines[start:end])


def check_chk_skl_005(skill_dir: Path) -> list[CheckError]:
    """Validate concrete launch template paths exist on disk.

    Scope: only the `## Agent Launch Protocol` section, and only the
    concrete `{base_path}/<dir>/<filename>.md` matches (placeholder
    patterns like `{base_path}/{checklists or rubrics}/{gate-file}.md`
    are not concrete paths and are correctly skipped by the regex).

    Resource Manifest list bullets are NOT validated because they are
    human-readable documentation that often lists aspirational MAY
    gates with `(MAY)` annotations. Resource-Manifest-vs-launch-
    template drift is a documentation issue, not a runtime issue, and
    is caught by the skill-coherence dogfood gate at refactor time.

    The launch templates are the runtime contract: they are exactly
    what the worker / evaluator agent will see in its launch prompt
    and what it will pass to its Read tool.
    """
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    if not skill_md.exists():
        return [CheckError("CHK-SKL-005", name, "SKILL.md missing", skill_md)]
    text = skill_md.read_text(encoding="utf-8")
    launch = _extract_section(text, "Agent Launch Protocol")
    referenced = set(BASEPATH_PATH.findall(launch))
    errors: list[CheckError] = []
    for rel in sorted(referenced):
        if not (skill_dir / rel).is_file():
            errors.append(
                CheckError(
                    "CHK-SKL-005",
                    name,
                    f"launch template references non-existent path: {rel}",
                    skill_md,
                )
            )
    return errors


# ---------------------------------------------------------------------------
# CHK-SKL-010 — SKILL.md token budget (word count proxy)
# ---------------------------------------------------------------------------

# Per skill-md-structure.md §Token Budget: hard cap ~6,000 tokens
# (~4,500 words). Word count is used as a deterministic proxy because
# token counts depend on tokenizer choice. `wc -w`-equivalent split
# matches the guidance in CHK-SKL-010.
WORD_HARD_CAP = 4500


def check_chk_skl_010(skill_dir: Path) -> list[CheckError]:
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    if not skill_md.exists():
        return []
    word_count = len(skill_md.read_text(encoding="utf-8").split())
    if word_count > WORD_HARD_CAP:
        return [
            CheckError(
                "CHK-SKL-010",
                name,
                f"SKILL.md is {word_count} words (hard cap: {WORD_HARD_CAP} words / ~6,000 tokens)",
                skill_md,
            )
        ]
    return []


# ---------------------------------------------------------------------------
# CHK-SKL-011 — no absolute / plugin-rooted paths
# ---------------------------------------------------------------------------

ABSOLUTE_PATH = re.compile(r"/Users/[A-Za-z0-9_./-]+")
PLUGIN_ROOTED_PATH = re.compile(r"\bdomain-teams/skills/[A-Za-z0-9_./-]+")

# Subdirectories whose files are read by worker/evaluator at runtime.
RUNTIME_SUBDIRS = ("standards", "protocols", "checklists", "rubrics")


def _path_check_lines(text: str, file_label: Path) -> list[CheckError]:
    errors: list[CheckError] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in ABSOLUTE_PATH.finditer(line):
            errors.append(
                CheckError(
                    "CHK-SKL-011",
                    file_label.parent.name,
                    f"absolute path at line {lineno}: {match.group(0)}",
                    file_label,
                )
            )
        for match in PLUGIN_ROOTED_PATH.finditer(line):
            errors.append(
                CheckError(
                    "CHK-SKL-011",
                    file_label.parent.parent.name,
                    f"plugin-rooted path at line {lineno}: {match.group(0)}",
                    file_label,
                )
            )
    return errors


def check_chk_skl_011(skill_dir: Path) -> list[CheckError]:
    """Check SKILL.md only (not standards/protocols/checklists/rubrics).

    Standards and other runtime files legitimately reference example
    paths inside markdown code blocks, inline backticks, anti-pattern
    documentation, and primary source citations to repo SSOT files
    outside the plugin (e.g. `/Users/kouko/GitHub/monkey-skills/CLAUDE
    .md`). Those are documentation, not runtime cross-references, and
    flagging them produces noise without preventing real drift.

    SKILL.md is the load-bearing case: any absolute path there breaks
    when the plugin is installed in a different filesystem location,
    and SKILL.md is what Claude actually reads at skill-dispatch time.
    """
    errors: list[CheckError] = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        errors.extend(_path_check_lines(skill_md.read_text(encoding="utf-8"), skill_md))
    return errors


# ---------------------------------------------------------------------------
# CHK-SKL-012 — directory structure + research/ filename pattern
# ---------------------------------------------------------------------------

REQUIRED_SUBDIRS = {"standards", "protocols", "checklists", "rubrics"}
OPTIONAL_SUBDIRS = {"research"}
RESEARCH_FILENAME = re.compile(r"^grounding-v\d+\.\d+\.\d+\.md$")


def _is_noise_file(name: str) -> bool:
    """Filesystem noise files that should be ignored.

    These are typically generated by macOS / editors / git tooling and
    are not tracked in the repo. The script targets parity with what
    GitHub Actions sees on a fresh checkout, so we skip them locally
    too to avoid spurious local-only failures.
    """
    return name == ".DS_Store" or name.startswith("._") or name == "Thumbs.db"


_README_TOP_LEVEL_RE = re.compile(r"^README(?:\.[A-Za-z]{2,3}(?:-[A-Za-z]{2,4})?)?\.md$")


def _is_allowed_top_level_file(name: str) -> bool:
    """Top-level files allowed in a skill directory.

    Per `domain-teams:skill-team/standards/file-conventions.md` §Top-Level
    Files (v5.4.0+):
      - SKILL.md — required, LLM-discovery SSOT
      - README.md — optional, human-facing GitHub-rendered overview
      - README.{lang}.md — optional BCP 47-tagged translations
        (e.g., README.ja.md, README.zh-TW.md, README.fr.md)

    Other top-level files are FATAL per CHK-SKL-012.
    """
    if name == "SKILL.md":
        return True
    if _README_TOP_LEVEL_RE.match(name):
        return True
    return False


def check_chk_skl_012(skill_dir: Path) -> list[CheckError]:
    name = skill_dir.name
    errors: list[CheckError] = []
    # Top-level files: SKILL.md (required), README.md, README.{lang}.md
    # (optional per file-conventions.md §Top-Level Files); noise files ignored.
    for entry in sorted(skill_dir.iterdir()):
        if entry.is_file() and not _is_allowed_top_level_file(entry.name) and not _is_noise_file(entry.name):
            errors.append(
                CheckError(
                    "CHK-SKL-012",
                    name,
                    f"unexpected top-level file: {entry.name}",
                    entry,
                )
            )
    # Subdirectories: required + optional only, no extras, no nesting.
    seen_subdirs: set[str] = set()
    for entry in sorted(skill_dir.iterdir()):
        if not entry.is_dir():
            continue
        seen_subdirs.add(entry.name)
        if entry.name in REQUIRED_SUBDIRS or entry.name in OPTIONAL_SUBDIRS:
            # No nested subdirectories inside any required/optional subdir.
            for child in entry.iterdir():
                if child.is_dir():
                    errors.append(
                        CheckError(
                            "CHK-SKL-012",
                            name,
                            f"nested subdirectory not allowed: {entry.name}/{child.name}",
                            child,
                        )
                    )
        else:
            errors.append(
                CheckError(
                    "CHK-SKL-012",
                    name,
                    f"unexpected subdirectory: {entry.name}/",
                    entry,
                )
            )
    # Router skill exemption: router skills (no protocols/) only need SKILL.md
    # at the top level. They are NOT required to have the four runtime
    # subdirectories.
    if is_router_skill(skill_dir):
        pass  # Skip the missing-required check for router skills.
    else:
        missing = REQUIRED_SUBDIRS - seen_subdirs
        for sub in sorted(missing):
            errors.append(
                CheckError(
                    "CHK-SKL-012",
                    name,
                    f"required subdirectory missing: {sub}/",
                    skill_dir,
                )
            )
    # research/ filename pattern check (if present). Skip noise files.
    research = skill_dir / "research"
    if research.is_dir():
        for f in sorted(research.iterdir()):
            if not f.is_file() or _is_noise_file(f.name):
                continue
            if not RESEARCH_FILENAME.match(f.name):
                errors.append(
                    CheckError(
                        "CHK-SKL-012",
                        name,
                        f"research/ filename does not match grounding-v{{X.Y.Z}}.md: {f.name}",
                        f,
                    )
                )
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


@dataclass
class Report:
    skill: str
    errors: list[CheckError] = field(default_factory=list)


def run_all_checks(skill_dir: Path) -> Report:
    name = skill_dir.name
    report = Report(skill=name)
    if not (skill_dir / "SKILL.md").exists():
        report.errors.append(
            CheckError("CHK-SKL-000", name, "SKILL.md missing in skill directory", skill_dir)
        )
        return report
    report.errors.extend(check_chk_skl_001(skill_dir))
    report.errors.extend(check_chk_skl_005(skill_dir))
    report.errors.extend(check_chk_skl_010(skill_dir))
    report.errors.extend(check_chk_skl_011(skill_dir))
    report.errors.extend(check_chk_skl_012(skill_dir))
    return report


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check-skill-structure.py <plugin-dir>", file=sys.stderr)
        return 2
    plugin_dir = Path(argv[1]).resolve()
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        print(f"error: {skills_dir} is not a directory", file=sys.stderr)
        return 2
    reports = [run_all_checks(d) for d in sorted(skills_dir.iterdir()) if d.is_dir()]
    total_errors = sum(len(r.errors) for r in reports)
    print(f"check-skill-structure: scanned {len(reports)} skills under {skills_dir}")
    for report in reports:
        if report.errors:
            print(f"FAIL  {report.skill}  ({len(report.errors)} issue(s))")
            for err in report.errors:
                print(f"  [{err.rule}] {err.format()}")
        else:
            print(f"PASS  {report.skill}")
    if total_errors:
        print(f"\n{total_errors} total issue(s) across {len(reports)} skills — FAIL")
        return 1
    print(f"\nAll {len(reports)} skills PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
