# Feasibility probe — can A-class defect events be extracted from the transcript corpus?

- **Date**: 2026-08-02
- **Question**: `docs/loom/backlog/2026-07-27-phase-containment-effectiveness-success-measure-for-plan-stage-fact-grou.md`
  defines the success metric for planning-origin defects and its baseline is
  uncomputable. Can the Claude Code session-transcript corpus supply the
  missing data, or not?
- **Verdict**: **yes for the docs side, no for the code side** — and the
  reason it fails on the code side is the finding that produced
  `docs/loom/specs/2026-08-02-finding-origin-attribution.md`.
- **Status**: measurement record. The numbers below are a 2026-08-02
  snapshot, not a ceiling — the corpus grows daily and the raw counts here
  are re-runnable with the script in §Method; the deduped and day-specific
  counts additionally need the manual dedupe procedure in §Appendix, which
  the script itself does not apply.

## Definition used

**A-class** = a document, plan or spec states a fact that is wrong **and
actionable**. Someone reads it, acts exactly as written, nothing fails, and
the error surfaces much later. Deliberately excluded: a spec so wrong the
reader gets stuck and asks (it self-reports), a test lacking discriminating
power, a plain code bug.

The industry term is **"Incorrect Fact"** — a standard category in
requirements-defect taxonomies traceable to Basili & Weiss (1981), and
distinct in those taxonomies from `Infeasible / Unachievable`, which is the
self-reporting half. The split was not invented here.

## Corpus

| | |
|---|---|
| projects | 54 |
| transcript files | 6,524 |
| total size | 2.0 GB |
| span | 2026-06-26 → 2026-08-02 |
| `/insights` facets | 100 entries; reports dated 2026-07-06 and 2026-07-31 |

**Note a standing rules file is stale against this.**
`~/.claude/rules/institution-maintenance.md` §5 states `/insights` has never
run on this machine and `facets/` is empty, so `dev-workflow:distill-sessions`
mines on heuristic fallback. That was true when written (2026-07-06) and is
false now. Out of this repo; recorded here because it would misdirect any
session that reads it.

**Files are the wrong sampling unit.** 95% of the monkey-skills files are
subagent transcripts and a random 200-file sample drew 8,595 lines total
(~43 lines/file) while the largest single file is 5,276 lines. Sample by
lines or by session, never by file.

## Method

Three signals, counted separately on purpose — the open question is *who*
currently catches this class, and one blended number would hide exactly that.

- **S1** — a structured reviewer verdict (`verdict:` **and** `severity:` in
  one message; both tokens required, so prose mentioning "verdict" does not
  qualify)
- **S2** — a defect dimension in the A-class subset (`incorrect-fact`,
  `inconsistency`). `omission` and `ambiguity` are excluded: a missing or
  unclear statement is not a wrong-but-actionable one.
- **S3** — a human turn correcting a stated fact (narrow, high-precision
  phrase set, zh + en). User-type lines carrying `toolUseResult` are excluded
  so this measures the human, not tool output.

Extractor: `probe_extract.py`, reproduced in §Appendix. Stdlib only; runs the
full 203,704-line monkey-skills corpus in seconds.

## Results

### Full monkey-skills corpus

| | |
|---|---|
| lines scanned | 203,704 |
| reviewer verdicts | **777** (639 PASS / 138 NEEDS_REVISION) |
| A-class findings, raw | 124 |
| A-class findings, deduped by (dimension, file) | **56** |

The 777 verdicts are a denominator for *reviewed* work — the first one this
repo has had.

### Oracle check — does it recover a day whose defects are known?

The 2026-08-02 arc is in the corpus and its A-class defects are known
independently (they were fixed during it). Scanning that day alone:

| | |
|---|---|
| files / lines | 58 / 11,039 |
| A-class findings, raw | 24 |
| deduped by (dimension, file) | **14** |

All 14 map onto defects genuinely handled that day: the store charter's false
"the body is non-contractual" claim, the plan's drifted anchors and invariant
miscount, the `BACKLOG.md:1252` dangling anchor, the two citations repointed
at entries that never carried them, and the entry description that restated
its own status. **Precision on the docs side is high.**

Noise measured: before a path-shape filter, 1 of 14 captures was Chinese prose
matched as a path (~7%).

## The limitation that matters

**Zero of the code-side A-class defects were extracted** — not the stamp regex
that missed a multi-word status, not the date-guard seam, not the
field-agreement capture boundary.

The cause is structural, not a tuning problem. The code arm and the docs arm
use **disjoint dimension vocabularies**. Code-side A-class defects land under
`correctness` and `cross-task-coherence`, buckets that mostly contain
non-A-class findings and cannot be separated post-hoc.

Stated precisely: **when a reviewer reviews a document, A-class is
extractable; when a reviewer reviews the code that document caused, it is
not** — `where:` names the code file, and the plan-origin attribution is lost
at the moment of recording. The eighth-site defect of that arc is exactly this
case.

And that is precisely what the blocked metric needs. Its input is the share of
**planning-origin** defects caught before close-out; what is missing is
**origin attribution**, not detection. That finding is the whole reason
`docs/loom/specs/2026-08-02-finding-origin-attribution.md` exists.

## Honest limits

- **S3 (a human turn correcting a stated fact) is computed by the
  extractor and printed by `main()`, but not reported above.** §Method
  states the three signals are counted separately on purpose because the
  open question is *who* currently catches this class — S3 is the
  half of that question this record does not answer. Re-running the
  extractor against the private transcript corpus to fill it in is out
  of scope here; this bullet records the gap rather than passing over
  it silently.
- The other 53 projects (~1.2 GB) were **not scanned**. The format is
  identical so it should work, but that is unverified.
- **56 is (dimension × file) pairs, not distinct defects.** The mapping was
  verified only for the 2026-08-02 day, where 14 pairs ≈ 5-7 real defects. The
  true monkey-skills figure is likely **20-30**, not 56 — still 2-3× the
  hand-curated n=9 the existing backtest rests on.
- File `mtime` is a weak proxy for session date; no conclusion here rests on
  it.
- Precision was measured on one day only. Outside that day it is unmeasured.

## Appendix — extractor

```python
#!/usr/bin/env python3
"""Count S1/S2/S3 signals across Claude Code transcripts. Stdlib only.

S1  a reviewer verdict block   (`verdict:` + `severity:` in one message)
S2  an A-class dimension tag   (incorrect-fact | inconsistency)
S3  a human correction turn    (narrow zh/en phrase set, tool results excluded)
"""
import json, pathlib, re, sys
from collections import Counter

ROOT = pathlib.Path.home() / ".claude" / "projects"

RE_VERDICT = re.compile(r"^\s*verdict:\s*(PASS|PASS_WITH_NOTES|NEEDS_REVISION)", re.M)
RE_FINDING = re.compile(r"^\s*(?:-\s*)?severity:\s*", re.M)
RE_DIM_A   = re.compile(r"dimension:\s*(incorrect-fact|inconsistency)\b")
RE_DIM_ANY = re.compile(r"dimension:\s*([a-z-]+)")
RE_S3 = re.compile("|".join([
    r"不對", r"錯了", r"寫錯", r"搞錯", r"你確定", r"真的嗎",
    r"沒有這個", r"不存在", r"應該是",
    r"\bthat'?s wrong\b", r"\bthat'?s not (?:true|right|correct)\b",
    r"\bincorrect\b", r"\bactually,? (?:it'?s|there (?:are|is))\b",
    r"\bare you sure\b", r"\bdoesn'?t exist\b",
]), re.I)

def message_text(obj):
    """Flatten a line's message content. Unrecognised shapes yield "" rather
    than raising — a probe that dies on one malformed line measures nothing."""
    msg = obj.get("message")
    if not isinstance(msg, dict):
        return ""
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    out = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if isinstance(block.get("text"), str):
            out.append(block["text"])
        inner = block.get("content")
        if isinstance(inner, str):
            out.append(inner)
        elif isinstance(inner, list):
            out.extend(b["text"] for b in inner
                       if isinstance(b, dict) and isinstance(b.get("text"), str))
    return "\n".join(out)

def scan(path):
    res = {"lines": 0, "s1": 0, "s2": 0, "s3": 0, "dims": Counter()}
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            res["lines"] += 1
            try:
                obj = json.loads(line)
            except Exception:
                continue
            kind = obj.get("type")
            if kind not in ("user", "assistant"):
                continue
            text = message_text(obj)
            if not text:
                continue
            if kind == "assistant":
                if RE_VERDICT.search(text) and RE_FINDING.search(text):
                    res["s1"] += 1
                res["s2"] += len(RE_DIM_A.findall(text))
                for d in RE_DIM_ANY.findall(text):
                    res["dims"][d] += 1
            elif obj.get("toolUseResult") is None and RE_S3.search(text):
                # a user line carrying toolUseResult is a tool result, not a human turn
                res["s3"] += 1
    return res

def main():
    root = ROOT / sys.argv[1] if len(sys.argv) > 1 else ROOT
    agg, dims = Counter(), Counter()
    for p in root.rglob("*.jsonl"):
        r = scan(p)
        for k in ("lines", "s1", "s2", "s3"):
            agg[k] += r[k]
        dims.update(r["dims"])
    print(f"lines={agg['lines']:,} S1={agg['s1']} S2={agg['s2']} S3={agg['s3']}")
    for d, n in dims.most_common(12):
        print(f"  {n:6d}  {d}{'  <-- A' if d in ('incorrect-fact','inconsistency') else ''}")

if __name__ == "__main__":
    main()
```

To dedupe A-class findings by `(dimension, file)`, pair `dimension:` with the
nearest `where:` within the same finding block and drop captures that are not
path-shaped — the raw-to-deduped ratio was 124 → 56 corpus-wide and 24 → 14
on the oracle day.
