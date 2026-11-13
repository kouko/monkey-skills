"""Unblind judge files of one round and tabulate by arm.

Usage: python3 score.py <round-dir> [--flags]
Arm = second field of the raw name (T1-A-1 -> A). --flags also lists every
flag with its arm, for reading what the judges objected to.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

round_dir = Path(sys.argv[1])
show_flags = "--flags" in sys.argv
key = json.loads((round_dir / "key.json").read_text(encoding="utf-8"))
TYPES = ["P1", "P2", "P3", "P4", "STOCK", "STILTED", "REREAD"]


def arm_of(label):
    return key[label].split("-")[1]


for jf in sorted((round_dir / "judge").glob("J*.json")):
    data = json.loads(jf.read_text(encoding="utf-8"))
    sents = defaultdict(int)
    counts = defaultdict(lambda: defaultdict(int))
    read = defaultdict(list)
    rank = defaultdict(list)
    for label, s in data["samples"].items():
        arm = arm_of(label)
        sents[arm] += s["sentences"]
        read[arm].append(s["readability"])
        for f in s["flags"]:
            counts[arm][f["type"]] += 1
    for r in data["rankings"]:
        for pos, label in enumerate(r["easiest_to_hardest"], 1):
            rank[arm_of(label)].append(pos)
    print(f"== {jf.name} ==")
    print(f"{'arm':<5}{'sents':>6}" + "".join(f"{t:>8}" for t in TYPES) + f"{'total':>7}{'/100s':>7}{'read':>6}{'rank':>6}")
    for arm in sorted(sents):
        row = [counts[arm][t] for t in TYPES]
        total = sum(row)
        print(
            f"{arm:<5}{sents[arm]:>6}" + "".join(f"{c:>8}" for c in row)
            + f"{total:>7}{100 * total / sents[arm]:>7.1f}"
            + f"{sum(read[arm]) / len(read[arm]):>6.2f}{sum(rank[arm]) / len(rank[arm]):>6.2f}"
        )
    print("per sample: " + "  ".join(
        f"{key[l]}={len(s['flags'])}f/r{s['readability']}" for l, s in sorted(data["samples"].items(), key=lambda kv: key[kv[0]])
    ))
    if show_flags:
        for label, s in sorted(data["samples"].items(), key=lambda kv: key[kv[0]]):
            for f in s["flags"]:
                print(f"  {key[label]} #{f['n']} {f['type']}: {f['quote']} — {f['why']}")
    print()
