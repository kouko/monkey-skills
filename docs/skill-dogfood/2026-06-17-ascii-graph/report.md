# Dogfood report — ascii-graph skill

- Skill under test: `ascii-graph-toolkit/skills/ascii-graph/SKILL.md` (raw working-tree, NOT installed)
- Date: 2026-06-17 · Branch: `worktree-ascii-graph-visionlyzion`
- Probes: A (real-harness triggering, claude 2.1.179) · B (executor + 2 blind auditors) · C (blind cold-reader)
- Distractor field: full installed plugin set (incl. obsidian-mermaid-visualizer / canvas-creator / excalidraw)

## Severity summary

| Severity | Count | Findings |
|---|---|---|
| 🔴 Critical | 0 | — |
| 🟠 High | 1 | F1 align.py 0-based report vs 1-based drift message |
| 🟡 Medium | 3 | F2 ¥/ambiguous-width caveat · F3 missing wcwidth dep note · F4 truncated flow example |
| 🟢 Low | 2 | F5 arrow off-center (hand-drawn) · F6 skill-root/python/jargon |

**Triggering: PASS** (TPR 6/6, TNR 5/5). **Core output quality: PASS** (all 5 artifacts ALIGNED by 2 independent blind auditors; verify-loop demonstrably catches a real CJK-width error and converges). No 🔴. The findings are polish, not breakage.

## Probe A — triggering (real harness, 2 runs each)

Should-fire 6/6 → `ascii-graph` (12/12 runs). Should-NOT 5/5 correctly did NOT fire ascii-graph (10/10 runs):

| expect | query | run1 | run2 |
|---|---|---|---|
| ✅fire | 用 ASCII 畫中文訂單流程圖貼到終端機 | ascii-graph | ascii-graph |
| ✅fire | 中日文混排表格在 terminal 對齊 | ascii-graph | ascii-graph |
| ✅fire | bar chart, Japanese labels, plain-text Slack | ascii-graph | ascii-graph |
| ✅fire | PR 純文字中文樹狀圖 | ascii-graph | ascii-graph |
| ✅fire | 我的 ASCII 流程圖中文跑版幫我對齊 | ascii-graph | ascii-graph |
| ✅fire | monospace ASCII table, 日本語 columns | ascii-graph | ascii-graph |
| 🚫abstain | 用 mermaid 畫流程圖 | NONE | NONE |
| 🚫abstain | draw an ER diagram | NONE | NONE |
| 🚫abstain | Obsidian canvas 圖 | canvas-creator | canvas-creator |
| 🚫abstain | review my Python code | NONE | NONE |
| 🚫abstain | excalidraw 系統架構圖 | NONE | NONE |

TPR = 1.00, TNR = 1.00. The cold-reader's worry that an "ER diagram" request might over-fire (because the skill claims the Mermaid-emit territory) did NOT materialize — ascii-graph abstained.

## Probe B — output quality (executor + 2 blind auditors)

Executor ran all 6 tasks end-to-end (Python 3.12, wcwidth 0.5.3). All 4 generators produced output that **passes its own oracle** (piped back through align.py → exit 0). The verify-loop worked exactly as documented: the executor's eyeballed branching-flowchart draft had a CJK-width error → align.py flagged `line N: col C` → executor fixed only that line → `✓ no drift`. Class diagram correctly emitted Mermaid source per the Honest-ceiling section. No command failed.

Two blind auditors (no production context), independently counting cells, both ruled **all 5 artifacts ALIGNED**. Their adversarial findings → F2, F5 below.

## Findings

### F1 🟠 High — align.py mixes 0-based report with 1-based drift message
- pass: blind (cold-reader) + confirmed by orchestrator on live output
- category: Output-quality / Cold-start
- probe: cold-reader read SKILL.md §VERIFY-LOOP example; orchestrator reproduced on a real diagram.
- expected: the per-line width report and the drift message use the SAME line numbering, so "fix only the flagged lines" points to one unambiguous line.
- actual: the report numbers lines **0-based** (`0`,`1`,`2`…) while the drift message says **1-based** (`line 9` refers to report row `8`). A first-timer following "fix the flagged line" edits the wrong line. The SKILL.md worked example (`line 2: col 7` over a 0-based `0/1/2` report) is itself confusing, and "col 7 on a width-6 box" has no legend explaining cols can exceed the box (that's the drift).
- root cause: `align.py` `analyze()`/`main()` print loop emits `i` (0-based enumerate) for the report but the check modules return 1-based line numbers.
- why static review missed it: tests assert issue contents and exit codes, not the cross-consistency of two human-facing numbering schemes.
- location: `scripts/align.py` (report print loop) + `SKILL.md` §VERIFY-LOOP example.
- suggested fix: make the report **1-based** to match the messages (`f"{i+1:4d} …"`), and add a one-line legend (`line# | width | content`; "a col past the box width IS the drift"). Update the SKILL.md example to match.

### F2 🟡 Medium — ¥ / East-Asian "Ambiguous" width is a portability hazard, undocumented as a caveat
- pass: blind (both auditors, independently, highest-likelihood real breakage)
- category: Output-quality / domain
- expected: a reader knows the alignment assumes Ambiguous=1 and when that breaks.
- actual: the width-policy table lists "Ambiguous = 1" but gives no warning that CJK-locale terminals configured `ambiguous=wide` render `¥`, some punctuation, etc. as 2 cells → a column sized at 1-cell-per-¥ overflows. Correct in default/Western terminals; breaks in a common CJK-locale config.
- location: `SKILL.md` §Width policy.
- suggested fix: add a caveat line — "Ambiguous chars (¥, some punctuation) are counted 1 cell; in a terminal set to `ambiguous=wide` (some CJK locales) they render 2 and can break a column — avoid ambiguous-width glyphs in aligned columns, or note the assumption."

### F3 🟡 Medium — no wcwidth dependency / setup note
- pass: blind (cold-reader)
- category: Cold-start
- actual: SKILL.md says "wraps wcwidth" / "zero external binary" but never states wcwidth is a third-party PyPI package that must be installed. First run in a fresh env → `ModuleNotFoundError`, with nothing in the file to recover. ("Zero external binary" ≠ "zero dependency".)
- location: `SKILL.md` (Purpose / Bundled files).
- suggested fix: one line — "Requires the `wcwidth` package (`pip install wcwidth`); pure-Python, no binary."

### F4 🟡 Medium — flow generator example is truncated
- pass: blind (cold-reader)
- category: Progressive-disclosure
- actual: unlike table/tree/bar, the `flow` example renders only the first box then literally prints `... (驗證 / 出貨 follow on the same trunk)`, so a reader never sees a complete multi-step flow (connector glyph, equal-width boxes, trunk). The executor's run shows the real output is clean — the doc just hides it.
- location: `SKILL.md` §Generators / flow.
- suggested fix: replace the `...` with the full rendered 3-box flow (the executor's Task-2 output is a ready example).

### F5 🟢 Low — hand-drawn branch arrows land off-center under unequal-width boxes
- pass: blind (both auditors)
- actual: in a branch to two different-width boxes, the ▼ glyphs land inside the boxes but not at their centers (align.py's arrowhead check verifies "inside the box span", not centered). Cosmetic; not a width fault. Inherent to hand-drawn layout, not a generator output.
- suggested fix: none required; optionally note in SKILL.md that hand-drawn branches to unequal boxes may look off-center (align.py only guarantees the arrow lands in-box).

### F6 🟢 Low — skill-root not named, `python` vs `python3`, undefined terms
- pass: blind (cold-reader)
- actual: "run from the skill root" never names the dir; examples use `python` (vs `python3`); terms "trunk", "kink", "arrowhead-landing", "East-Asian Ambiguous" are undefined. Low impact because the skill's *operator is Claude* (not the semi-technical end-reader), and the JSON/CLI shapes are concrete.
- suggested fix: optional — name the root once ("run from `skills/ascii-graph/`"), standardize on `python3`.

## Note on the latent ？ trap (NOT a finding)
Auditor 2 noted the hand-drawn flowchart balances only because it uses ASCII `?` (1 cell); a full-width `？` (2 cells) would overflow. This is **not a defect** — it is exactly what the verify-loop catches: had the author written `？` and mis-padded, align.py would flag the overflow. It demonstrates the oracle working, and the width policy correctly classes `？` as Wide=2.

## Verdict
No 🔴/blocking defects. Triggering and core output quality are strong (TPR/TNR 1.00; 5/5 artifacts independently judged aligned; verify-loop proven). Recommend fixing **F1** (the one High — genuine UX bug in the oracle's own output) and the 3 Medium doc items (F2–F4) before wider use; F5/F6 optional. This is a *floor* check, not a pass stamp — the user is the final calibrator.
