"""Tests for digest_check.py — the consolidated digest self-check gate."""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SCRIPT = HERE / "digest_check.py"

GOOD = """---
title: t
---
# 每日新聞

## 🧭 總覽

```mermaid
flowchart TD
  A --> B
```

### 故事一

> [!summary] TL;DR

```mermaid
flowchart LR
  A --> B
```

內文 [[來源筆記|來源]]。

## 🧠 知識與觀點

- [[來源筆記|另一則]]

## 來源索引
"""


def make(tmp, digest_text, extra_files=("來源筆記.md",)):
    root = Path(tmp)
    (root / "news").mkdir(parents=True)
    p = root / "news" / "2026-07-01 每日新聞.md"
    p.write_text(digest_text, encoding="utf-8")
    for f in extra_files:
        (root / f).write_text("x", encoding="utf-8")
    return root, p


def run(root, digest, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), str(digest), "--skip-mermaid", *args],
        capture_output=True, text=True)


def test_clean_digest_passes():
    with tempfile.TemporaryDirectory() as tmp:
        root, p = make(tmp, GOOD)
        r = run(root, p)
        assert r.returncode == 0, r.stdout + r.stderr
        assert "ALL PASS" in r.stdout


def test_missing_cot_fails():
    bad = GOOD.replace("```mermaid\nflowchart LR\n  A --> B\n```\n\n", "")
    with tempfile.TemporaryDirectory() as tmp:
        root, p = make(tmp, bad)
        r = run(root, p)
        assert r.returncode != 0
        assert "cot" in r.stdout.lower()


def test_broken_link_fails():
    bad = GOOD.replace("[[來源筆記|來源]]", "[[不存在的筆記|來源]]")
    with tempfile.TemporaryDirectory() as tmp:
        root, p = make(tmp, bad)
        r = run(root, p)
        assert r.returncode != 0
        assert "不存在的筆記" in r.stdout


def test_knowledge_tier_cot_cannot_mask_missing_story_cot():
    # remove the story's LR diagram but add one in the knowledge tier:
    # doc-wide counting would pass (1 >= 1); news-section counting must FAIL
    bad = GOOD.replace(
        "```mermaid\nflowchart LR\n  A --> B\n```\n\n內文", "內文").replace(
        "- [[來源筆記|另一則]]",
        "- [[來源筆記|另一則]]\n\n```mermaid\nflowchart LR\n  C --> D\n```")
    with tempfile.TemporaryDirectory() as tmp:
        root, p = make(tmp, bad)
        r = run(root, p)
        assert r.returncode != 0, r.stdout
        assert "cot" in r.stdout.lower()


def test_anchor_only_links_ok():
    ok = GOOD.replace("[[來源筆記|來源]]", "[[#故事一|跳轉]] [[來源筆記|來源]]")
    with tempfile.TemporaryDirectory() as tmp:
        root, p = make(tmp, ok)
        r = run(root, p)
        assert r.returncode == 0, r.stdout


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted({k: v for k, v in globals().items()
                            if k.startswith("test_")}.items()):
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL {name}: {e}")
    sys.exit(1 if fails else 0)
