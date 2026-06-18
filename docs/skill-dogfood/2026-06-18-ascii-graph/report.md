# Dogfood report — `ascii-graph` skill (v0.3.0, 6 generators + verify-loop)

Date: 2026-06-18 · Target: `ascii-graph-toolkit/skills/ascii-graph/` (working tree
== merged `main` after #415). Method: `dev-workflow:dogfood-skill-testing` —
≥3 rounds, both dimensions (triggering + output quality), blind/firewalled probes.

## Verdict summary

**The core skill is sound.** All 6 generators produce display-width-correct
(rectangular) output on mixed 中/英/日 input; the verify-loop catches and clears
hand-drawn drift end-to-end; triggering separates cleanly from sibling skills.
Findings are **documentation/polish**, not generator-correctness bugs.

| # | Severity | Category | Finding | Status |
|---|---|---|---|---|
| F1 | **High** | Cold-start / Progressive-disclosure | `seq` worked example has NO runnable command line (only output) — breaks the pattern all 5 siblings follow; payload spec `{"from","to","label"}` is malformed-JSON shorthand → seq not runnable verbatim | **Confirmed → fix ready** |
| F2 | Medium | Output-quality (UX) | `seq` sample output *reads as corrupted* to a first-timer — arrow rows blank the out-of-span lifelines + carry trailing whitespace; ironic for an alignment skill (doc warns, but it still looks broken) | Confirmed (= v2-C deferred nit) |
| F3 | Low | Jargon-leak | Undefined terms in a semi-technical-reader doc: **SSOT** (never expanded), **kink**, **oracle**, **by construction**, **seam**, **trunk**, **lifeline** | Confirmed |
| F4 | Low | Cold-start | `bar` `width` optionality + `generate.py` error/exit behavior undocumented | Confirmed |
| F5 | Low | Output-quality | `seq` unknown-participant → bare `KeyError` (not the friendly `ValueError` used for self-message); emoji is *documented* unsafe but not *rejected* by the generator | Known/accepted (v2 decision record) |
| ~~F0~~ | ~~Med~~ | — | ~~documented commands leak `__pycache__`~~ | **Investigated → REFUTED** |

## Rounds run (both dimensions)

- **Round 1 — ground-truth smoke (mechanical):** arch/seq/table on mixed 中/英/日 →
  every line equal display width (RECT). seq 11 lines all width 53.
- **Round 2 — Probe B executor (informed, end-to-end):** ran arch + seq + verify-loop
  on realistic CJK tasks. arch 15 lines = 52 cells; seq 14 lines = 65 cells with
  arrowhead landing numerically verified at lifelines 7/28/55 (incl. a **non-adjacent**
  message and a **long-CJK-label** gap-widening); verify-loop caught 2 deliberate drifts
  by line+col and converged to `✓ no drift` (exit 0) in one fix iteration.
- **Round 3 — adversarial edge-case sweep (predict-then-execute):** empty/single
  inputs don't crash; extreme width asymmetry stays RECT; self-message → `ValueError`;
  long-CJK widening RECT; ambiguous-width (→★§°) RECT under the ambiguous=1 policy;
  `bar` with 0 handled.
- **Probe A — activation (blind, synthetic-menu, `fidelity:approximate`):** 15-query
  corpus + distractor menu (mermaid-visualizer / canvas / gws-charts / deep-research /
  translation). should-fire 8/8 → ascii-graph (**TPR 1.00**); should-NOT 7/7 routed
  elsewhere (**TNR 1.00**) — incl. class-diagram→Mermaid (matches honest-ceiling) and
  "ascii art of a cat"→NONE (over-trigger trap avoided). *Single-run, approximate —
  re-run live for higher fidelity if desired.*
- **Probe C — cold-reader (zero-context):** surfaced F1–F4.

## Finding detail

### F1 (High) — `seq` worked example is not runnable verbatim
`SKILL.md` §Generators: table/flow/tree/bar/arch each show
`echo '…' | python scripts/generate.py <shape>` **then** the output, inside one code
block. The **seq** block (lines 123–133) shows **only the output** — no `echo … seq`
command — and the payload spec (line 116) `{"from","to","label"}` is shorthand, not
valid JSON. A first-timer must invent the payload. (The Probe B executor *did* invent
a correct one — proof it's guessable, but it still had to guess.)
- **Why static review missed it:** the v2-C reviewers checked "does the pasted output
  reproduce byte-for-byte" (it does), not "is the runnable command present like the
  siblings." Output-fidelity passed while runnability regressed.
- **Fix (verified):** insert this command line into the seq code block (it reproduces
  the existing output block byte-for-byte, all lines width 36):
  ```
  echo '{"participants":["顧客","API サービス","DB"],"messages":[{"from":"顧客","to":"API サービス","label":"注文を送信"},{"from":"API サービス","to":"DB","label":"在庫確認"}]}' \
    | python scripts/generate.py seq
  ```

### F2 (Medium) — `seq` sample looks corrupted on first read
On the arrow rows (lines 130, 132) the lifelines *outside* the message's span are
blanked (not kept as `│`) and the rows carry trailing spaces. The doc pre-warns about
trailing spaces, but the cold-reader still read it as "misaligned/corrupted output" —
notable for an *alignment* skill. Root = the v2-C deferred 🟢 nit (out-of-span
lifelines blanked on arrow rows). Options: (a) keep `│` on out-of-span lifelines for a
cleaner UML look, or (b) add a one-line caption under the example explaining the look
is intentional. Non-blocking.

### F3 (Low) — undefined jargon
`SSOT` is used in user-facing prose without expansion; `kink` (and `checks_kink.py`)
is never defined. Others (`oracle`, `by construction`, `seam`, `trunk`, `lifeline`)
are inferable but undefined for the stated "semi-technical" reader. Fix: expand SSOT on
first use, add a one-line gloss for `kink`/`oracle`.

### F4 (Low) — undocumented edges
`bar`'s `width` default and `generate.py`'s behavior on malformed JSON / unknown shape
/ missing key are not stated. Low impact (fails loud), but a sentence would help.

### F5 (Low, accepted) — input-robustness asymmetry
`seq` rejects self-message with a friendly `ValueError` but an unknown participant
raises a bare `KeyError`; emoji is documented unsafe but not rejected. Both are recorded
as accepted/deferred in `docs/code-toolkit/specs/2026-06-18-ascii-graph-v2-backlog-decisions.md`.

### F0 — REFUTED: "documented commands leak `__pycache__`"
Probe B reported the documented invocation creates `scripts/__pycache__`. **Clean
re-reproduction disproved it**: `python3 scripts/generate.py flow` leaks nothing — the
in-CLI `sys.dont_write_bytecode = True` guard (set before imports) works. The leak the
executor saw came from its *own* direct-module-import verification harness (`gen_*` /
`width.py` don't self-guard — only the CLIs do, by design; pytest uses
`PYTHONDONTWRITEBYTECODE=1`). Recorded for transparency; no action.

## Bottom line
Generators + verify-loop are correct and CJK-aligned across normal, edge, and
adversarial inputs; triggering is clean. The only fix worth shipping is **F1** (add
the seq command — a one-line doc fix restoring runnable-verbatim parity). F2–F4 are
optional polish.
