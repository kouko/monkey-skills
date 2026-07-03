"""Tests for arc_check.py — the consolidated arc postcondition gate."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SCRIPT = HERE / "arc_check.py"

STARTERS = [
    ("us-equities", "美股大盤"), ("taiwan-equities", "台股"),
    ("japan-equities", "日股"), ("ust-us-rates", "美債與美國利率"),
    ("us-inflation-data", "美國通膨與經濟數據"), ("boj-jpy", "日銀與日圓"),
    ("usd-majors", "美元與主要貨幣"), ("oil-energy", "油價與能源"),
    ("precious-metals", "貴金屬"), ("industrial-metals-commodities", "工業金屬與大宗"),
    ("fed-policy-speak", "Fed 政策與官員發言"), ("other-central-banks", "其他央行"),
    ("geopolitics-middle-east", "地緣政治：中東"),
    ("geopolitics-us-china-taiwan", "地緣政治：美中與台海"),
    ("china-macro", "中國經濟"), ("ai-semiconductors", "AI 與半導體"),
]
DATE = "2026-07-01"


def book(concept, title, kind="topic", keywords=("kw-" + "x",), milestones=()):
    kw = "\n".join(f"  - {k}" for k in keywords)
    ms = "\n".join(milestones)
    return (f"---\ntitle: {title}\ntype: news-arc\nconcept: {concept}\n"
            f"kind: {kind}\nstatus: active\nkeywords:\n{kw}\nindicators: []\n"
            f"created: {DATE}\nlast_updated: {DATE}\n---\n\n## 數字表\n\n"
            f"| 日期 |\n|---|\n\n## 里程碑\n\n{ms}\n")


def make_vault(tmp, extra_books=(), starter_milestones=None):
    root = Path(tmp)
    arcs = root / "news" / "arcs"
    arcs.mkdir(parents=True)
    (root / "news" / f"{DATE} 每日新聞.md").write_text(
        "# 每日新聞\n\n### 油價故事\n\nbody\n\n### 台股故事\n\nbody\n",
        encoding="utf-8")
    for i, (concept, title) in enumerate(STARTERS):
        ms = starter_milestones.get(concept, ()) if starter_milestones else ()
        (arcs / f"Arc - {title}.md").write_text(
            book(concept, title, keywords=(f"kw{i}a", f"kw{i}b"), milestones=ms),
            encoding="utf-8")
    for name, text in extra_books:
        (arcs / name).write_text(text, encoding="utf-8")
    return root


def run(root, *args):
    if "--expect-milestones" not in args:
        args = ("--expect-milestones", "0", *args)
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), DATE, *args],
        capture_output=True, text=True)


GOOD_MS = f"- **{DATE}** — 油價上漲（[[{DATE} 每日新聞#油價故事|當日故事]]）"


def test_clean_vault_passes():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp, starter_milestones={"oil-energy": (GOOD_MS,)})
        r = run(root, "--expect-milestones", "1")
        assert r.returncode == 0, r.stdout + r.stderr
        assert "ALL PASS" in r.stdout


def test_missing_starter_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp)
        (root / "news" / "arcs" / "Arc - 台股.md").unlink()
        r = run(root)
        assert r.returncode != 0
        assert "taiwan-equities" in r.stdout


def test_bad_anchor_fails():
    bad = f"- **{DATE}** — 發明的錨（[[{DATE} 每日新聞#Invented Anchor|當日故事]]）"
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp, starter_milestones={"oil-energy": (bad,)})
        r = run(root)
        assert r.returncode != 0
        assert "anchor" in r.stdout.lower()


def test_milestone_count_below_expect_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp)  # zero milestones
        r = run(root, "--expect-milestones", "3")
        assert r.returncode != 0
        assert "milestone" in r.stdout.lower()


def test_event_keyword_overlap_fails():
    ev = book("hbm-shortage", "HBM 短缺", kind="event",
              keywords=("kw0a", "unique-kw"))  # kw0a overlaps starter #0
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp, extra_books=[("Arc - HBM 短缺.md", ev)])
        r = run(root)
        assert r.returncode != 0
        assert "dedup" in r.stdout.lower()


def test_event_title_containing_other_keyword_fails():
    # keywords dodge overlap, but the TITLE contains another book's keyword
    ev = book("kw3a-crisis", "kw3a 危機", kind="event", keywords=("totally-new",))
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp, extra_books=[("Arc - kw3a 危機.md", ev)])
        r = run(root)
        assert r.returncode != 0
        assert "dedup" in r.stdout.lower()


def test_invented_starter_title_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp)
        p = root / "news" / "arcs" / "Arc - 美股大盤.md"
        text = p.read_text(encoding="utf-8").replace("title: 美股大盤", "title: 美股走勢")
        p.unlink()
        (root / "news" / "arcs" / "Arc - 美股走勢.md").write_text(text, encoding="utf-8")
        r = run(root)
        assert r.returncode != 0
        assert "title" in r.stdout.lower()


def test_title_check_can_be_disabled():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp)
        p = root / "news" / "arcs" / "Arc - 美股大盤.md"
        text = p.read_text(encoding="utf-8").replace("title: 美股大盤", "title: US Equities")
        p.unlink()
        (root / "news" / "arcs" / "Arc - US Equities.md").write_text(text, encoding="utf-8")
        r = run(root, "--titles", "off")
        assert r.returncode == 0, r.stdout + r.stderr


def test_empty_keywords_fails():
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp)
        p = root / "news" / "arcs" / "Arc - 台股.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "keywords:\n  - kw1a\n  - kw1b", "keywords: []"), encoding="utf-8")
        r = run(root)
        assert r.returncode != 0
        assert "keyword" in r.stdout.lower()


def test_ascii_keyword_needs_word_boundary():
    # "kw0a" embedded inside a longer token must NOT count as containment
    ev = book("standalone-topic", "workw0adays 危機", kind="event",
              keywords=("totally-new",))
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp, extra_books=[("Arc - workw0adays 危機.md", ev)])
        r = run(root)
        assert r.returncode == 0, r.stdout + r.stderr


def test_cjk_keyword_substring_still_hits():
    # CJK has no word boundaries — plain substring containment must still fire
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp)
        rare = book("rare-earth", "稀土戰", kind="topic", keywords=("稀土",))
        (root / "news" / "arcs" / "Arc - 稀土戰.md").write_text(rare, encoding="utf-8")
        ev = book("cn-jp-war", "中日稀土戰", kind="event", keywords=("關鍵金屬",))
        (root / "news" / "arcs" / "Arc - 中日稀土戰.md").write_text(ev, encoding="utf-8")
        r = run(root, "--titles", "off")
        assert r.returncode != 0
        assert "dedup" in r.stdout.lower()


def test_starter_table_matches_spec():
    import re as _re
    sys.path.insert(0, str(HERE))
    import arc_check
    spec = (HERE.parent / "references" / "arc-tracking.md").read_text(encoding="utf-8")
    rows = _re.findall(r"^\| .*?`([a-z0-9-]+)` \| ([^|]+) \|", spec, _re.M)
    table = {slug: title.strip() for slug, title in rows}
    assert table == arc_check.CANONICAL_TITLES, (
        "spec table drifted from CANONICAL_TITLES: "
        f"{set(table.items()) ^ set(arc_check.CANONICAL_TITLES.items())}")


def test_milestone_without_link_fails():
    bad = f"- **{DATE}** — 沒有連結的里程碑"
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp, starter_milestones={"oil-energy": (bad,)})
        r = run(root)
        assert r.returncode != 0
        assert "milestone-format" in r.stdout.lower()


def test_clean_event_book_passes():
    ev = book("euro-elections", "歐洲選舉", kind="event", keywords=("歐洲選舉", "EU vote"),
              milestones=(f"- **{DATE}** — 選情（[[{DATE} 每日新聞#台股故事|當日故事]]）",))
    with tempfile.TemporaryDirectory() as tmp:
        root = make_vault(tmp, extra_books=[("Arc - 歐洲選舉.md", ev)])
        r = run(root, "--expect-milestones", "1")
        assert r.returncode == 0, r.stdout + r.stderr


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
