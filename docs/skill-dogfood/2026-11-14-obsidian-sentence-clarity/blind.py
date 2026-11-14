"""Blind the raw samples of one round and print length statistics.

Usage: python3 blind.py <round-dir> <seed>
Reads <round-dir>/raw/*.md, writes shuffled copies to <round-dir>/blind/Snn.md
and the mapping to <round-dir>/key.json (judges never see the key).
"""
import json
import random
import re
import sys
from pathlib import Path

round_dir = Path(sys.argv[1])
seed = int(sys.argv[2])
raw = sorted((round_dir / "raw").glob("*.md"))
order = raw[:]
random.Random(seed).shuffle(order)

key = {}
blind_dir = round_dir / "blind"
blind_dir.mkdir(exist_ok=True)
print(f"{'sample':<10}{'chars':>6}{'sents':>6}{'chars/sent':>11}")
for i, src in enumerate(order, 1):
    label = f"S{i:02d}"
    text = src.read_text(encoding="utf-8").strip()
    (blind_dir / f"{label}.md").write_text(text + "\n", encoding="utf-8")
    key[label] = src.stem

for src in raw:
    text = src.read_text(encoding="utf-8").strip()
    chars = len(re.sub(r"\s", "", text))
    sents = len([s for s in re.split(r"[。！？!?]", text) if s.strip()])
    print(f"{src.stem:<10}{chars:>6}{sents:>6}{chars / sents:>11.1f}")

(round_dir / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
print(f"blinded {len(order)} samples")
