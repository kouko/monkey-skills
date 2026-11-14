"""Round-3 scoring: unblind, tabulate by arm, overall and per source type.

Usage: python3 score3.py <round-dir> [--flags]
Raw names are M<n>-<arm>: O = original vault text, N = rewrite without the
rules, R = rewrite with the rules. M1-4 research, M5-8 video summary,
M9-12 daily news. DIFF (fact discrepancy) is reported apart from the
readability total.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

round_dir = Path(sys.argv[1])
show_flags = "--flags" in sys.argv
key = json.loads((round_dir / "key.json").read_text(encoding="utf-8"))
TYPES = ["P1", "P2", "P3", "P4", "STOCK", "STILTED", "REREAD"]


def parts(label):
    mat, arm = key[label].split("-")
    n = int(mat[1:])
    group = "research" if n <= 4 else "video" if n <= 8 else "news"
    return mat, arm, group


def table(data, only_group=None):
    sents = defaultdict(int)
    counts = defaultdict(lambda: defaultdict(int))
    read = defaultdict(list)
    rank = defaultdict(list)
    wins = defaultdict(int)
    for label, s in data["samples"].items():
        _, arm, group = parts(label)
        if only_group and group != only_group:
            continue
        sents[arm] += s["sentences"]
        read[arm].append(s["readability"])
        for f in s["flags"]:
            counts[arm][f["type"]] += 1
    for r in data["rankings"]:
        order = r["easiest_to_hardest"]
        if only_group and parts(order[0])[2] != only_group:
            continue
        wins[parts(order[0])[1]] += 1
        for pos, label in enumerate(order, 1):
            rank[parts(label)[1]].append(pos)
    print(f"{'arm':<4}{'n':>3}{'sents':>6}" + "".join(f"{t:>8}" for t in TYPES)
          + f"{'total':>7}{'/100s':>7}{'read':>6}{'rank':>6}{'1st':>5}{'DIFF':>6}")
    for arm in sorted(sents):
        row = [counts[arm][t] for t in TYPES]
        total = sum(row)
        print(f"{arm:<4}{len(read[arm]):>3}{sents[arm]:>6}" + "".join(f"{c:>8}" for c in row)
              + f"{total:>7}{100 * total / sents[arm]:>7.1f}"
              + f"{sum(read[arm]) / len(read[arm]):>6.2f}{sum(rank[arm]) / len(rank[arm]):>6.2f}"
              + f"{wins[arm]:>5}{counts[arm]['DIFF']:>6}")


for jf in sorted((round_dir / "judge").glob("J*.json")):
    data = json.loads(jf.read_text(encoding="utf-8"))
    print(f"== {jf.name} — all 12 subjects ==")
    table(data)
    for g in ("research", "video", "news"):
        print(f"-- {g} --")
        table(data, g)
    if show_flags:
        for label, s in sorted(data["samples"].items(), key=lambda kv: (int(parts(kv[0])[0][1:]), parts(kv[0])[1])):
            for f in s["flags"]:
                print(f"  {key[label]} #{f['n']} {f['type']}: {f['quote']} — {f['why']}")
    print()
