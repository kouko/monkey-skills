---
name: ascii-graph
description: |
  CJK-width-aware ASCII/Unicode diagram & table generator for plain-text channels that can't render Mermaid (terminal, Slack, PR text). Generators: table / flow / tree / bar / arch / seq, + a wcwidth alignment oracle. Pure-Python, zero binary.
---

## Purpose

Produce **CJK (中 / English / 日本語) display-width-aligned ASCII / Unicode
diagrams and tables** for plain-text channels that cannot render Mermaid —
the Claude Code terminal, Slack messages, PR descriptions, code comments —
for a semi-technical reader. Full-width characters (Chinese, Japanese
kana/kanji) occupy 2 terminal cells while ASCII occupies 1; eyeballed
padding silently breaks. This skill makes the **script the width oracle** so
columns and trunks actually line up. Pure Python — requires the `wcwidth`
package (`pip install wcwidth`); no compiled binary.

## Routing rule (core)

Pick the path by shape, then either **generate** (one-shot, guaranteed
aligned) or run the **verify-loop** (hand-drawn, script-checked).

| Shape you need | Path |
| --- | --- |
| Table | `python scripts/generate.py table` |
| Linear flow (boxes on one trunk) | `python scripts/generate.py flow` |
| Tree / hierarchy | `python scripts/generate.py tree` |
| Horizontal bar chart | `python scripts/generate.py bar` |
| Layered / n-tier architecture (boxes in stacked layer bands) | `python scripts/generate.py arch` |
| Sequence diagram (participants + ordered messages over time) | `python scripts/generate.py seq` |
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
┌──────────┐
│   驗證   │
└──────────┘
      │
      ▼
┌──────────┐
│   出貨   │
└──────────┘
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

**arch** — payload `{"layers":[{"name":...,"components":[...]}]}` (vertically-stacked
independent layer bands, each band = a centered layer name over a row of
component cells; no connector arrows — each band is self-contained):

```
echo '{"layers":[{"name":"Presentation 表示層","components":["Web App","モバイル","管理後台"]},{"name":"Application 應用層","components":["API Gateway","認証サービス"]},{"name":"Data 資料層","components":["PostgreSQL","Redis 快取"]}]}' \
  | python scripts/generate.py arch
┌───────────────────────────────┐
│      Presentation 表示層      │
├─────────┬──────────┬──────────┤
│ Web App │ モバイル │ 管理後台 │
└─────────┴──────────┴──────────┘
┌───────────────────────────────┐
│      Application 應用層       │
├──────────────┬────────────────┤
│ API Gateway  │ 認証サービス   │
└──────────────┴────────────────┘
┌───────────────────────────────┐
│          Data 資料層          │
├───────────────┬───────────────┤
│ PostgreSQL    │ Redis 快取    │
└───────────────┴───────────────┘
```

**seq** — payload `{"participants":[...],"messages":[{"from":"A","to":"B","label":"..."},...]}`
(participant boxes across the top with vertical lifelines below; each message is a
centered label row + a directional arrow row whose arrowhead lands on the target
lifeline column). Lines after the lifeline header carry trailing spaces to the
diagram's full display-width — pasted verbatim below (re-running reproduces it
byte-for-byte):

```
echo '{"participants":["顧客","API サービス","DB"],"messages":[{"from":"顧客","to":"API サービス","label":"注文を送信"},{"from":"API サービス","to":"DB","label":"在庫確認"}]}' \
  | python scripts/generate.py seq
┌──────┐   ┌──────────────┐   ┌────┐
│ 顧客 │   │ API サービス │   │ DB │
└───┬──┘   └───────┬──────┘   └──┬─┘
    │              │             │  
    │              │             │  
    │ 注文を送信   │             │  
    │──────────────►                
    │              │  在庫確認   │  
                   │─────────────►  
```

> On a message's arrow row, the lifelines *outside* that message's span are left
> blank and the row is right-padded with trailing spaces to the diagram's full
> display-width — this is **intentional** (the diagram stays rectangular), not
> misalignment.

### Multi-line labels (換行)

A `\n` inside a label splits it into multiple lines (each line independently
padded and CJK-width-aligned per that shape's existing alignment — centered in
flow / arch, left-aligned in table, bare continuation lines in tree) in
**flow / tree / table / arch**.
**seq / bar reject `\n` with a `ValueError`** — multi-line is not meaningful
there (deferred), so a stray newline fails loud instead of silently corrupting
output. CRLF and a bare `\r` are handled too — treated as line breaks like `\n`
(so a label pasted from a Windows file is fine); other control characters
(e.g. `\t`) are not special-cased, so keep labels to printable text plus `\n`.
Pass the JSON as the `printf '%s'` **argument** (not `echo`, and not inside
`printf`'s format string) so the shell hands the literal two-character `\n` to
`json.loads`: `echo` expands `\n` to a real newline, which `json.loads` then
rejects with `Invalid control character`.

```
printf '%s' '{"steps":["收到訂單","驗證使用者\n身份確認（OAuth）","出貨"]}' \
  | python scripts/generate.py flow
┌───────────────────┐
│     收到訂單      │
└───────────────────┘
          │
          ▼
┌───────────────────┐
│    驗證使用者     │
│ 身份確認（OAuth） │
└───────────────────┘
          │
          ▼
┌───────────────────┐
│       出貨        │
└───────────────────┘
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
  ln  width | content
   1     6 | ┌────┐
   2     8 | │ 訂單 │
   3     6 | └────┘
line 2: col 7: '│' at display-col 7 connects to nothing vertically
```

Line numbers are **1-based** and match the drift message (here `line 2` is the
`│ 訂單 │` row — width 8 vs the box's 6, so its right `│` lands at display-col 7,
past the border). A column **greater than the box width is the drift**.

**NEVER hand-pad by eyeballing CJK width** — the script is the oracle. The
three checks it wires (vertical-seam connect, table equal-width, kink — a
connector that bends mid-seam with no junction glyph to justify it — plus
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

**Ambiguous-width caveat:** East-Asian *Ambiguous* glyphs (e.g. `·`, `§`, `°`,
`±`, `→`, `★`, Greek/Cyrillic) are counted as **1 cell** here — correct in modern
/ Western terminals (Ghostty, kitty, WezTerm, Alacritty, Windows Terminal all
default narrow). A terminal explicitly set `ambiguous=wide` (an opt-in some CJK
users enable in iTerm2 / PuTTY / mintty, or via `VTE_CJK_WIDTH`) renders them as
2 cells and can overflow a column sized at 1. No mainstream terminal defaults to
wide; it is a shrinking legacy corner.

### Alignment-column character policy (cross-terminal safe)

Width is only guaranteed identical across narrow **and** wide terminals for the
deterministic classes. When a label/cell/anchor must align, restrict it to the
**whitelist**; keep the **blacklist** out of aligned positions (use them only in
free text that is not load-bearing for a column edge or a trunk).

| | Characters | Why |
| --- | --- | --- |
| ✅ **Safe (deterministic)** | 漢字・かな・カナ・諺文 (always 2); ASCII letters/digits/`+-*/=%`; fullwidth punctuation `，。：？！（）「」` (always 2); box-drawing `─│┌┐└┘├┤┬┴┼` (special-cased 1 in ~all terminals) | width is the same under `ambiguous=1` and `=2` |
| ⚠️ **Avoid in aligned columns** | `§ ° ± · × ÷ → ← ↔ ↑ ↓ ★ ☆ ♥ ◇ ○ □` + most U+2190–U+25FF symbols, Greek `αβ…`, Cyrillic | East-Asian *Ambiguous* → 1 or 2 by terminal policy |
| ❌ **Never as anchor / column content** | emoji, ZWJ sequences, VS16 (`️`), regional indicators | width nondeterministic across fonts/terminals |

For arrows in flows, prefer the box-drawing/triangle set used by the generators
(`▼ ▲ ► ◄` are rendered 1-cell in practice alongside `│ ─`); if you need a literal
`→` in a label, keep it out of the column that sets the box width.

### Box-drawing palette — expressiveness for complex diagrams

For hand-drawn diagrams you may use the full box-drawing repertoire below — **all
of it is de-facto 1-cell in practice AND recognised by `align.py`** (the taxonomy
lives in `scripts/glyphs.py`, the SSOT the checks import). Use line style to carry
meaning; the verifier still validates seams/junctions across every style.

| Style | Glyphs | Suggested use |
| --- | --- | --- |
| Light (default) | `┌┐└┘ ├┤┬┴┼ │ ─` | normal boxes, trunks, branches/merges (`┬` split, `┴` join, `┼` cross) |
| Rounded | `╭╮╰╯` | soft / start–end nodes |
| Heavy | `┏┓┗┛ ┣┫┳┻╋ ┃ ━` | highlight a critical box or path |
| Double | `╔╗╚╝ ╠╣╦╩╬ ║ ═` | system / trust boundary, emphasis frame |
| Dashed | `┄┅┆┇` / `┈┉┊┋` | async / optional / planned (vs solid = sync/required) |
| Arrows | `▼ ▲ ► ◄` | flow direction (1-cell, align-safe) |

Junctions (`┬┴├┤┼` and their rounded/heavy/double variants) tell both the reader
and the oracle "a seam legitimately branches/ends here" — so prefer a real junction
glyph over faking a corner with a plain `│`/`─`. Mixing styles in one diagram is
fine (e.g. a double-line outer boundary with light inner boxes); the checks handle
it. Still subject to the alignment-column policy above — line glyphs are safe, but
don't put `§→★`-class symbols in width-setting columns.

## Languages

中文 / English / 日本語 all handled. Japanese kana and kanji are the same
Wide class as Chinese (2 cells), so JP tables and flows align identically.

## Honest ceiling

This v1 **reliably aligns**: tables, linear flows, trees, bar charts,
layered / n-tier architecture diagrams, and sequence diagrams (all aligned
**by construction** by their generators), plus hand-drawn flowcharts (verified
by `align.py`).

The **seq** generator's correctness is guaranteed **by construction**
(deterministic column math + its own structural tests), **not** by `align.py`
— a sequence diagram's horizontal arrows crossing vertical lifelines is a
different topology than align.py's vertical-seam model, so it does not run
through the verify-loop.

For **class / ER / state / gantt / mindmap / C4** diagrams there is **no
display-width-correct ASCII renderer available**. For those, **emit the
Mermaid source** as the faithful artifact — the reader can render it where
Mermaid is supported, or paste it into a live editor — rather than shipping
misaligned ASCII. For **very dense graphs**, prefer Mermaid source plus the
ASCII as an explicitly-labelled lossy view.

## Bundled files

| Path | Role |
| --- | --- |
| `scripts/generate.py` | Generator dispatch CLI (table / flow / tree / bar / arch / seq) |
| `scripts/align.py` | Alignment oracle CLI (verify-loop, exit 0/1) |
| `scripts/width.py` | Shared display-width primitive (wcwidth) |
| `scripts/glyphs.py` | Canonical box-drawing glyph taxonomy (single source of truth, SSOT, for the checks) |
| `scripts/gen_table.py` `scripts/gen_flow.py` `scripts/gen_tree.py` `scripts/gen_bar.py` `scripts/gen_arch.py` | Per-shape generators |
| `scripts/gen_seq.py` | Sequence-diagram generator (lifelines + message rows; correctness by construction, not via `align.py`) |
| `scripts/checks_seam.py` `scripts/checks_table.py` `scripts/checks_kink.py` | Drift checks wired by `align.py` |

## Self-check

Before sending **any** hand-drawn diagram, it MUST have passed
`python scripts/align.py -` with **exit 0** (`✓ no drift`). Generator output
is aligned by construction and needs no check.
