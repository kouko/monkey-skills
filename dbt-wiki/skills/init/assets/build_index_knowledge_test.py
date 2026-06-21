# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Smoke test for build_index_knowledge.py — synthetic, offline, no specifics."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_index_knowledge import line_for, section_lines, main  # noqa: E402

CASES = []


def check(name, cond):
    CASES.append((name, cond))
    print(f"[{'OK' if cond else 'FAIL'}] {name}")


def write(p, fm):
    p.write_text("---\n" + fm + "\n---\n\nbody\n", encoding="utf-8")


with tempfile.TemporaryDirectory() as d:
    wiki = Path(d)
    for f in ("entities", "metrics", "concepts"):
        (wiki / f).mkdir()

    # 1. canonical line shape with title_local + aliases
    write(wiki / "entities" / "account.md",
          'title: Account\ntitle_local: 帳戶\nstatus: developing\n'
          'summary: A billing account.\naliases: [acct, "5010"]')
    title, line = line_for("entities", wiki / "entities" / "account.md")
    check("title_local + aliases rendered",
          line == "- [Account｜帳戶](entities/account.md) `developing` — A billing account. 〔aka: acct, 5010〕")

    # 2. no title_local, no aliases -> omitted
    write(wiki / "metrics" / "mrr.md", 'title: MRR\nstatus: mature\nsummary: Monthly recurring revenue.')
    _, line2 = line_for("metrics", wiki / "metrics" / "mrr.md")
    check("no title_local/aliases omitted",
          line2 == "- [MRR](metrics/mrr.md) `mature` — Monthly recurring revenue.")

    # 3. empty folder -> stub line
    check("empty concepts -> stub", section_lines(wiki, "concepts")[0].startswith("_(none"))

    # 4. sorted by title (case-insensitive)
    write(wiki / "entities" / "zebra.md", "title: zebra\nsummary: z")
    write(wiki / "entities" / "apple.md", "title: Apple\nsummary: a")
    rows = section_lines(wiki, "entities")
    check("sorted case-insensitive", rows[0].startswith("- [Account") and "Apple" in rows[1] and "zebra" in rows[2])

    # 5. end-to-end: stub sections + stats line replaced
    (wiki / "index.md").write_text(
        "# Index\n\n## Entities\n\n_(stub)_\n\n## Metrics\n\n_(stub)_\n\n"
        "## Concepts\n\n_(stub)_\n\n## Evidence: Models\n\n- keep me\n\n"
        "- Knowledge pages: entities 0, metrics 0, concepts 0\n", encoding="utf-8")
    rc = main(wiki)
    txt = (wiki / "index.md").read_text(encoding="utf-8")
    check("end-to-end rc 0", rc == 0)
    check("entities section populated", "[Account｜帳戶](entities/account.md)" in txt)
    check("evidence section untouched", "- keep me" in txt)
    check("stats line updated", "- Knowledge pages: entities 3, metrics 1, concepts 0" in txt)

passed = sum(1 for _, c in CASES if c)
print(f"\n{passed}/{len(CASES)} passed")
sys.exit(0 if passed == len(CASES) else 1)
