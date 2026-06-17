---
name: ascii-graph
description: CJK (中/英/日) display-width-aware ASCII/Unicode diagram and table generator for plain-text channels that cannot render Mermaid (Claude Code terminal, Slack, PR text). Provides deterministic generators (table / flow / tree / bar) plus a wcwidth-based verify-loop that acts as an alignment oracle so full-width characters stay aligned. Zero external binary, pure-Python.
---

## Purpose

Produce **CJK (中 / English / 日本語) display-width-aligned ASCII / Unicode
diagrams and tables** for plain-text channels that cannot render Mermaid —
the Claude Code terminal, Slack messages, PR descriptions, code comments —
for a semi-technical reader. Full-width characters (Chinese, Japanese
kana/kanji) occupy 2 terminal cells while ASCII occupies 1; eyeballed
padding silently breaks. This skill makes the **script the width oracle** so
columns and trunks actually line up. Pure Python, zero external binary.

## Routing rule (core)

Pick the path by shape, then either **generate** (one-shot, guaranteed
aligned) or run the **verify-loop** (hand-drawn, script-checked).

| Shape you need | Path |
| --- | --- |
| Table | `python scripts/generate.py table` |
| Linear / layered flow (boxes on one trunk) | `python scripts/generate.py flow` |
| Tree / hierarchy | `python scripts/generate.py tree` |
| Horizontal bar chart | `python scripts/generate.py bar` |
| **Any other box-and-arrow flowchart** you compose by hand | **VERIFY-LOOP** with `scripts/align.py` (below) |
| class / ER / state / gantt / mindmap / C4 | **Emit Mermaid source** (see Honest ceiling) |

### Generators — `python scripts/generate.py <shape>`

Reads a JSON payload on **stdin**, prints the aligned diagram, exits 0.
Run each from the skill root (`scripts/` is on the import path).

**table** — payload `{"headers":[...],"rows":[[...]],"ascii_only":false}`
(`ascii_only:true` falls back to `+ - |` for ASCII-only contexts):

```
echo '{"headers":["項目","Q1","売上"],"rows":[["茶葉","100","¥200"],["コーヒー","80","¥150"]]}' \
  | python scripts/generate.py table
┌──────────┬─────┬──────┐
│ 項目     │ Q1  │ 売上 │
├──────────┼─────┼──────┤
│ 茶葉     │ 100 │ ¥200 │
│ コーヒー │ 80  │ ¥150 │
└──────────┴─────┴──────┘
```

**flow** — payload `{"steps":[...]}` (vertically-stacked boxes on one trunk):

```
echo '{"steps":["収到訂單","驗證","出貨"]}' | python scripts/generate.py flow
┌──────────┐
│ 収到訂單 │
└──────────┘
      │
      ▼
   ... (驗證 / 出貨 follow on the same trunk)
```

**tree** — payload `{"node":{"label":...,"children":[{...}]}}`:

```
echo '{"node":{"label":"訂單系統","children":[{"label":"訂單服務"},{"label":"庫存サービス","children":[{"label":"預扣"}]}]}}' \
  | python scripts/generate.py tree
訂單系統
├─ 訂單服務
└─ 庫存サービス
   └─ 預扣
```

**bar** — payload `{"pairs":[["label",val],...],"width":20}`:

```
echo '{"pairs":[["東京",120],["台北",80],["NYC",40]],"width":20}' \
  | python scripts/generate.py bar
東京 ████████████████████ 120
台北 █████████████ 80
NYC  ███████ 40
```

### VERIFY-LOOP — `python scripts/align.py -`

For a flowchart no generator fits, you draw it by hand, but you do **not**
trust your own padding. `align.py` is the alignment oracle: it reads a
diagram from a file arg or `-` (stdin), prints a per-line display-width
report, lists drift as `line N: col C: msg`, and exits **0 clean / 1 on
drift**. Loop:

1. Draft the diagram.
2. Pipe it: `printf '...your draft...' | python scripts/align.py -`
3. If it reports drift, the message gives the **line + display-column +
   the exact width mismatch** — fix only the flagged lines.
4. Re-run until it prints `✓ no drift` (exit 0).

```
printf '┌────┐\n│ 訂單 │\n└────┘\n' | python scripts/align.py -
   0     6 | ┌────┐
   1     8 | │ 訂單 │
   2     6 | └────┘
line 2: col 7: '│' at display-col 7 connects to nothing vertically
```

**NEVER hand-pad by eyeballing CJK width** — the script is the oracle. The
three checks it wires (vertical-seam connect, table equal-width, kink +
arrowhead-landing) live in `scripts/checks_seam.py`,
`scripts/checks_table.py`, `scripts/checks_kink.py`.

## Width policy

| Class | Cells |
| --- | --- |
| Box-drawing (U+2500..257F) | 1 |
| East-Asian **Ambiguous** | 1 |
| CJK **Wide / Fullwidth** (中文・かな・漢字) | 2 |
| Control / zero-width | 0 |
| Narrow ASCII, everything else | 1 |

Measured by `scripts/width.py` (wraps `wcwidth`). **Emoji must NOT be used
as an alignment anchor or as column content** — terminal emoji width is
nondeterministic across fonts/terminals and will break alignment.

## Languages

中文 / English / 日本語 all handled. Japanese kana and kanji are the same
Wide class as Chinese (2 cells), so JP tables and flows align identically.

## Honest ceiling

This v1 **reliably aligns**: tables, linear / layered flows, trees, bar
charts, and hand-drawn flowcharts (verified by `align.py`).

For **class / ER / state / gantt / mindmap / C4** diagrams there is **no
display-width-correct ASCII renderer available**. For those, **emit the
Mermaid source** as the faithful artifact — the reader can render it where
Mermaid is supported, or paste it into a live editor — rather than shipping
misaligned ASCII. For **very dense graphs**, prefer Mermaid source plus the
ASCII as an explicitly-labelled lossy view.

## Bundled files

| Path | Role |
| --- | --- |
| `scripts/generate.py` | Generator dispatch CLI (table / flow / tree / bar) |
| `scripts/align.py` | Alignment oracle CLI (verify-loop, exit 0/1) |
| `scripts/width.py` | Shared display-width primitive (wcwidth) |
| `scripts/gen_table.py` `scripts/gen_flow.py` `scripts/gen_tree.py` `scripts/gen_bar.py` | Per-shape generators |
| `scripts/checks_seam.py` `scripts/checks_table.py` `scripts/checks_kink.py` | Drift checks wired by `align.py` |

## Self-check

Before sending **any** hand-drawn diagram, it MUST have passed
`python scripts/align.py -` with **exit 0** (`✓ no drift`). Generator output
is aligned by construction and needs no check.
