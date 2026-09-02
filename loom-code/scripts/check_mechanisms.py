#!/usr/bin/env python3
"""Recompute the loom admission-rule mechanism population (concept-model
§11, spec REQ-7) and diff it against docs/loom/evidence/mechanisms.yaml.

Five classes are recomputed straight from repo state: skill, checker-rule,
hook, contract, prose-gate (see mechanisms.yaml's `counting:` field for the
prose paragraph — this module is its executable twin and must not drift
from it). A sixth class, host-hygiene, is declared but never recomputed and
never counted toward the net total.

Four red conditions:
  R1 unregistered  — a recomputed id is not in the yaml.
  R2 stale         — a yaml id (class != host-hygiene) was not recomputed.
  R3 budget        — the net count rose over --baseline and the CHANGELOG
                      entry for --version carries no
                      `budget-exception: <mechanism-id> — <reason>` line.
  R4 missing-eval   — a mechanism has no non-empty `eval:`.

Exit codes: 0 clean, 1 any red finding, 2 internal error (fail-closed).

Usage:
    check_mechanisms.py [--repo PATH] [--baseline REF] [--changelog PATH]
                         [--version X.Y.Z] [--measure]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PLUGINS = ("loom-code", "loom-design", "loom-workflow")
RECOMPUTED_CLASSES = ("skill", "checker-rule", "hook", "contract", "prose-gate")
ALL_CLASSES = RECOMPUTED_CLASSES + ("host-hygiene",)

GATE_MARKER_RE = re.compile(r"<!--\s*gate:\s*([A-Za-z0-9._-]+)\s*-->")
BUDGET_EXCEPTION_RE = re.compile(r"budget-exception:\s*(\S+)\s*—\s*(.+)")
QUOTED_TOKEN_RE = re.compile(r'"([^"]+)"|(\S+)')


# --------------------------------------------------------------------------
# Manifest / mechanisms.yaml loading
# --------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_manifest(repo: Path) -> dict:
    path = repo / "loom-code" / "contract" / "manifest.yaml"
    if not path.is_file():
        return {}
    return _load_yaml(path)


def load_mechanisms(repo: Path) -> list[dict]:
    path = repo / "docs" / "loom" / "evidence" / "mechanisms.yaml"
    if not path.is_file():
        return []
    data = _load_yaml(path)
    return list(data.get("mechanisms") or [])


def _standalone_tool_names(manifest: dict) -> set[str]:
    return {t["name"] for t in manifest.get("tools", []) if t.get("standalone")}


# --------------------------------------------------------------------------
# The five recomputable surfaces
# --------------------------------------------------------------------------

def recompute_skills(repo: Path) -> set[str]:
    manifest = load_manifest(repo)
    standalone = _standalone_tool_names(manifest)
    ids: set[str] = set()
    for plugin in PLUGINS:
        skills_dir = repo / plugin / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            name = skill_md.parent.name
            if name in standalone:
                continue
            ids.add(name)
    return ids


def recompute_checker_rules(repo: Path) -> set[str]:
    script = repo / "loom-code" / "scripts" / "loom_checker.py"
    if not script.is_file():
        return set()
    proc = subprocess.run(
        [sys.executable, str(script), "--list-rules"],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    ids: set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        ids.add(line.split("\t", 1)[0].strip())
    return ids


def _command_basename(command: str) -> str:
    tokens = [a or b for a, b in QUOTED_TOKEN_RE.findall(command)]
    path_tokens = [t for t in tokens if "/" in t]
    target = path_tokens[-1] if path_tokens else (tokens[-1] if tokens else command)
    return Path(target).name


def recompute_hooks(repo: Path) -> set[str]:
    path = repo / "loom-code" / "hooks" / "hooks.json"
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for event, entries in (data.get("hooks") or {}).items():
        for entry in entries:
            matcher = entry.get("matcher", "")
            for h in entry.get("hooks", []):
                base = _command_basename(h.get("command", ""))
                ids.add(f"{event}:{matcher}:{base}")
    return ids


def recompute_contract(repo: Path) -> set[str]:
    manifest = load_manifest(repo)
    if not manifest:
        return set()
    ids: set[str] = set()
    for s in manifest.get("stations", []):
        ids.add(f"station:{s['name']}")
    for t in manifest.get("tools", []):
        if t.get("standalone"):
            continue
        ids.add(f"tool:{t['name']}")
    for a in manifest.get("actions", []):
        ids.add(f"action:{a['name']}")
    for name in (manifest.get("artifacts") or {}):
        ids.add(f"artifact:{name}")
    return ids


def recompute_prose_gates(repo: Path) -> set[str]:
    ids: set[str] = set()
    globs = ("skills/**/*.md", "agents/*.md", "references/*.md")
    for plugin in PLUGINS:
        base = repo / plugin
        if not base.is_dir():
            continue
        for glob in globs:
            for path in base.glob(glob):
                text = path.read_text(encoding="utf-8", errors="replace")
                ids.update(GATE_MARKER_RE.findall(text))
    return ids


def recompute_all(repo: Path) -> dict[str, set[str]]:
    return {
        "skill": recompute_skills(repo),
        "checker-rule": recompute_checker_rules(repo),
        "hook": recompute_hooks(repo),
        "contract": recompute_contract(repo),
        "prose-gate": recompute_prose_gates(repo),
    }


# --------------------------------------------------------------------------
# Diff / checks
# --------------------------------------------------------------------------

@dataclass
class Finding:
    rule: str
    mechanism_id: str
    detail: str


@dataclass
class CheckResult:
    exit_code: int
    findings: list[Finding] = field(default_factory=list)
    summary: dict[str, tuple[int, int]] = field(default_factory=dict)  # class -> (recomputed, registered)
    net_total: int = 0
    baseline_total: int | None = None
    baseline_approx: bool = False


def net_count(mechanisms: list[dict]) -> int:
    return sum(1 for m in mechanisms if m.get("class") != "host-hygiene")


def _all_yaml_ids(mechanisms: list[dict]) -> set[str]:
    return {m["id"] for m in mechanisms}


def run_checks(
    repo: Path,
    *,
    baseline_ref: str | None = None,
    baseline_total_override: int | None = None,
    changelog: Path | None = None,
    version: str | None = None,
) -> CheckResult:
    mechanisms = load_mechanisms(repo)
    recomputed = recompute_all(repo)
    yaml_ids = _all_yaml_ids(mechanisms)
    recomputed_all_ids: set[str] = set().union(*recomputed.values()) if recomputed else set()

    findings: list[Finding] = []
    summary: dict[str, tuple[int, int]] = {}

    for cls in RECOMPUTED_CLASSES:
        recomputed_ids = recomputed[cls]
        registered_ids = {m["id"] for m in mechanisms if m.get("class") == cls}
        summary[cls] = (len(recomputed_ids), len(registered_ids))
        for mid in sorted(recomputed_ids - yaml_ids):
            findings.append(Finding("R1", mid, f"class {cls}: recomputed but not registered in mechanisms.yaml"))

    for m in mechanisms:
        cls = m.get("class")
        mid = m.get("id", "<missing-id>")
        if cls != "host-hygiene" and mid not in recomputed_all_ids:
            findings.append(Finding("R2", mid, f"class {cls}: registered but not found by recompute"))
        if not (m.get("eval") or "").strip():
            findings.append(Finding("R4", mid, "mechanism has no eval:"))

    net_total = net_count(mechanisms)
    baseline_total: int | None = None
    baseline_approx = False
    if baseline_total_override is not None:
        baseline_total = baseline_total_override
    elif baseline_ref is not None:
        baseline_total, baseline_approx = compute_baseline_total(repo, baseline_ref)

    if baseline_total is not None and net_total > baseline_total:
        changelog_path = changelog or _default_changelog(repo)
        version_str = version or _default_version(repo)
        if not _changelog_has_budget_exception(changelog_path, version_str):
            findings.append(Finding(
                "R3", "<net-count>",
                f"net mechanism count rose {baseline_total} -> {net_total} and "
                f"{changelog_path} has no `budget-exception:` line for version {version_str}",
            ))

    exit_code = 1 if findings else 0
    return CheckResult(
        exit_code=exit_code,
        findings=findings,
        summary=summary,
        net_total=net_total,
        baseline_total=baseline_total,
        baseline_approx=baseline_approx,
    )


# --------------------------------------------------------------------------
# Baseline computation
# --------------------------------------------------------------------------

def _git_show(repo: Path, ref: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{path}"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def _git_ls_tree(repo: Path, ref: str) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", ref],
        capture_output=True, text=True, check=True,
    )
    return proc.stdout.splitlines()


SKILL_MD_RE = re.compile(r"^(?:loom-code|loom-design|loom-workflow)/skills/[^/]+/SKILL\.md$")


def _count_hooks_json_entries(data: dict) -> int:
    total = 0
    for entries in (data.get("hooks") or {}).values():
        for entry in entries:
            total += len(entry.get("hooks", []))
    return total


def compute_baseline_total(repo: Path, ref: str) -> tuple[int, bool]:
    """Return (total, approximated). Prefers a mechanisms.yaml committed at
    `ref`; falls back to an approximation (SKILL.md count + hooks.json entry
    count at that ref) when none exists, printing that it did so."""
    text = _git_show(repo, ref, "docs/loom/evidence/mechanisms.yaml")
    if text is not None:
        data = yaml.safe_load(text) or {}
        mechs = data.get("mechanisms") or []
        return net_count(mechs), False

    files = _git_ls_tree(repo, ref)
    skill_count = sum(1 for f in files if SKILL_MD_RE.match(f))
    hook_count = 0
    hooks_text = _git_show(repo, ref, "loom-code/hooks/hooks.json")
    if hooks_text is not None:
        try:
            hook_count = _count_hooks_json_entries(json.loads(hooks_text))
        except (json.JSONDecodeError, TypeError):
            hook_count = 0
    return skill_count + hook_count, True


# --------------------------------------------------------------------------
# R3 changelog lookup
# --------------------------------------------------------------------------

def _default_changelog(repo: Path) -> Path:
    return repo / "loom-code" / "CHANGELOG.md"


def _default_version(repo: Path) -> str:
    plugin_json = repo / "loom-code" / ".claude-plugin" / "plugin.json"
    if plugin_json.is_file():
        try:
            return json.loads(plugin_json.read_text(encoding="utf-8")).get("version", "")
        except json.JSONDecodeError:
            return ""
    return ""


def _changelog_has_budget_exception(changelog: Path, version: str) -> bool:
    if not changelog.is_file():
        return False
    text = changelog.read_text(encoding="utf-8", errors="replace")
    if version:
        # scope the search to the section for `version` when the heading is
        # findable; fall back to scanning the whole file otherwise.
        heading_re = re.compile(rf"^##\s*\[{re.escape(version)}\]", re.MULTILINE)
        m = heading_re.search(text)
        if m:
            next_heading = re.compile(r"^##\s*\[", re.MULTILINE)
            nxt = next_heading.search(text, m.end())
            text = text[m.end():nxt.start() if nxt else len(text)]
    return bool(BUDGET_EXCEPTION_RE.search(text))


# --------------------------------------------------------------------------
# --measure
# --------------------------------------------------------------------------

def measure_skill_count(repo: Path) -> int:
    return len(recompute_skills(repo))


def measure_artifact_type_count(repo: Path) -> int:
    manifest = load_manifest(repo)
    return len(manifest.get("artifacts") or {})


def measure_session_start_words(repo: Path) -> int:
    script = repo / "loom-code" / "hooks" / "session-start"
    if not script.is_file():
        return -1
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True, capture_output=True)
        proc = subprocess.run(
            ["bash", str(script)],
            cwd=tmp_path, input="", capture_output=True, text=True,
        )
        return len(proc.stdout.split())


def _session_start_baseline(repo: Path) -> tuple[str, int] | None:
    path = repo / "docs" / "loom" / "KICKOFF-DEFAULTS.md"
    if not path.is_file():
        return None
    m = re.search(r"session-start-baseline:\s*(\S+)\s+(\d+)", path.read_text(encoding="utf-8"))
    if not m:
        return None
    return m.group(1), int(m.group(2))


def run_measure(repo: Path) -> int:
    skill_count = measure_skill_count(repo)
    artifact_types = measure_artifact_type_count(repo)
    words = measure_session_start_words(repo)

    print(f"skill count (counted): {skill_count}")
    print(f"artifact-type count (manifest): {artifact_types}")
    print(f"session-start word count: {words}")

    baseline = _session_start_baseline(repo)
    exit_code = 0
    if baseline is None:
        print("session-start-baseline: not recorded in KICKOFF-DEFAULTS.md (no comparison)")
    else:
        sha, baseline_words = baseline
        print(f"session-start-baseline ({sha}): {baseline_words} words")
        half = baseline_words / 2
        if words > baseline_words:
            print(f"RED: session-start word count {words} exceeds baseline {baseline_words}")
            exit_code = 1
        elif words <= half:
            print(f"info: session-start word count {words} is at or under half the baseline target ({half:.0f})")
        else:
            print(f"info: session-start word count {words} is under baseline but over half target ({half:.0f})")
    return exit_code


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_summary(result: CheckResult) -> None:
    print(f"{'class':<14} {'recomputed':>10} {'registered':>10}")
    for cls in RECOMPUTED_CLASSES:
        recomputed_n, registered_n = result.summary.get(cls, (0, 0))
        print(f"{cls:<14} {recomputed_n:>10} {registered_n:>10}")
    print(f"net mechanism count (excl. host-hygiene): {result.net_total}")
    if result.baseline_total is not None:
        approx = " (approximated)" if result.baseline_approx else ""
        print(f"baseline net count: {result.baseline_total}{approx}")
    if result.findings:
        print()
        for f in result.findings:
            print(f"RED [{f.rule}] {f.mechanism_id}: {f.detail}")
    else:
        print("all clear")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--baseline", dest="baseline_ref", default=None)
    parser.add_argument("--changelog", type=Path, default=None)
    parser.add_argument("--version", default=None)
    parser.add_argument("--measure", action="store_true")
    args = parser.parse_args(argv)

    try:
        repo = args.repo.resolve()
        if args.measure:
            return run_measure(repo)
        result = run_checks(
            repo,
            baseline_ref=args.baseline_ref,
            changelog=args.changelog,
            version=args.version,
        )
        _print_summary(result)
        return result.exit_code
    except Exception as exc:  # fail-closed: internal error -> exit 2
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
