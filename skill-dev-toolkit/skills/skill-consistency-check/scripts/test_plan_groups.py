"""Tests for plan_groups.py (task W2-01, acceptance 3 and 5)."""

import hashlib
import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "plan_groups.py"


def run(skill_dir, *extra):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(skill_dir), *extra],
        capture_output=True,
        text=True,
    )
    return proc


def plan(skill_dir, *extra):
    proc = run(skill_dir, *extra)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def tokens_of(data, path):
    return next(f["tokens"] for f in data["files"] if f["path"] == path)


def group_tokens(data, group):
    return sum(tokens_of(data, p) for p in group)


def test_T_small_package_single_group(tmp_path):
    write(tmp_path, "SKILL.md", "Read references/a.md first.\n")
    write(tmp_path, "references/a.md", "alpha " * 10)
    write(tmp_path, "references/b.md", "beta " * 10)
    data = plan(tmp_path)
    paths = ["SKILL.md", "references/a.md", "references/b.md"]
    assert [f["path"] for f in data["files"]] == paths
    assert data["grouped"] is False
    assert data["over_limit"] is False
    assert data["groups"]["read"] == [paths]
    assert data["groups"]["simulate"] == [paths]
    assert data["uncovered_pairs"] == []
    assert data["target"] == str(tmp_path.resolve())
    assert data["limit"] == 30000 and data["group_max"] == 25000


def test_T_large_package_offset_groups_core_and_uncovered_pairs(tmp_path):
    # ~4000 tokens each; 12 periphery files -> ~48k + core > 30k limit.
    write(tmp_path, "SKILL.md", "Always follow references/named.md.\n" + "x " * 1000)
    write(tmp_path, "agents/worker.md", "y " * 1000)
    write(tmp_path, "references/named.md", "z " * 1000)
    for i in range(12):
        write(tmp_path, f"references/p{i:02d}.md", "p " * 3000)
    data = plan(tmp_path)
    assert data["grouped"] is True
    assert data["over_limit"] is False
    core = sorted(f["path"] for f in data["files"] if f["core"])
    assert core == ["SKILL.md", "agents/worker.md", "references/named.md"]
    assert data["core_tokens"] == sum(tokens_of(data, p) for p in core)
    periphery = sorted(f["path"] for f in data["files"] if not f["core"])
    for method in ("read", "simulate"):
        groups = data["groups"][method]
        assert len(groups) > 1
        seen = []
        for g in groups:
            assert group_tokens(data, g) <= 25000
            assert g[: len(core)] == core
            seen.extend(g[len(core):])
        assert sorted(seen) == periphery
    read_sets = [frozenset(g) for g in data["groups"]["read"]]
    sim_sets = [frozenset(g) for g in data["groups"]["simulate"]]
    assert set(read_sets) != set(sim_sets)
    covered = set()
    for g in data["groups"]["read"] + data["groups"]["simulate"]:
        for a, b in itertools.combinations(sorted(g), 2):
            covered.add((a, b))
    expected = [
        [a, b]
        for a, b in itertools.combinations(periphery, 2)
        if (a, b) not in covered
    ]
    assert expected, "fixture should leave some pairs uncovered"
    assert data["uncovered_pairs"] == expected


def tree_hash(root):
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            p = Path(dirpath) / name
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
        for name in dirnames:
            h.update(("dir:" + str((Path(dirpath) / name).relative_to(root))).encode())
    return h.hexdigest()


def test_T_target_tree_unchanged(tmp_path):
    write(tmp_path, "SKILL.md", "Core text.\n" + "x " * 10000)
    write(tmp_path, "agents/a.md", "a " * 100)
    for i in range(10):
        write(tmp_path, f"references/r{i}.md", "r " * 5000)
    before = tree_hash(tmp_path)
    count_before = sum(len(f) for _, _, f in os.walk(tmp_path))
    plan(tmp_path)
    assert tree_hash(tmp_path) == before
    assert sum(len(f) for _, _, f in os.walk(tmp_path)) == count_before


def test_T_core_over_limit_flagged(tmp_path):
    write(tmp_path, "SKILL.md", "s " * 15000)  # ~20k tokens
    write(tmp_path, "agents/big.md", "b " * 7500)  # ~10k tokens
    for i in range(3):
        write(tmp_path, f"references/q{i}.md", "q " * 1000)
    data = plan(tmp_path)
    assert data["over_limit"] is True
    assert data["grouped"] is True
    core = ["SKILL.md", "agents/big.md"]
    for method in ("read", "simulate"):
        groups = data["groups"][method]
        assert groups
        for g in groups:
            assert g[:2] == core


def test_readme_files_excluded(tmp_path):
    write(tmp_path, "SKILL.md", "hi")
    write(tmp_path, "README.md", "readme")
    write(tmp_path, "README.ja.md", "readme")
    write(tmp_path, "sub/README.zh-TW.md", "readme")
    write(tmp_path, "sub/notes.md", "notes")
    write(tmp_path, "sub/data.txt", "not md")
    data = plan(tmp_path)
    assert [f["path"] for f in data["files"]] == ["SKILL.md", "sub/notes.md"]


def test_cjk_counted_one_token_each(tmp_path):
    # 4 kanji + 2 hiragana + 2 katakana + 2 hangul + 1 fullwidth + 1 CJK punct
    # = 12 CJK tokens, plus 3 words in the rest -> ceil(1.33 * 3) = 4.
    write(tmp_path, "SKILL.md", "漢字漢字ひらカタ한국！。 alpha beta gamma")
    data = plan(tmp_path)
    assert tokens_of(data, "SKILL.md") == 16
    write(tmp_path, "SKILL.md", "a b c d e f")  # ceil(1.33 * 6) = 8
    assert tokens_of(plan(tmp_path), "SKILL.md") == 8


VALIDATED_PKG = (
    Path(__file__).resolve().parents[3]
    / "tests" / "consistency-check-corpus" / "multi" / "pkg"
)


def test_T_validated_package_reads_whole():
    data = plan(VALIDATED_PKG)
    assert len(data["files"]) == 13
    assert 22000 <= data["total_tokens"] <= 28000
    assert data["grouped"] is False


def test_bad_path_exits_2(tmp_path):
    proc = run(tmp_path / "missing")
    assert proc.returncode == 2
    assert proc.stdout == ""
