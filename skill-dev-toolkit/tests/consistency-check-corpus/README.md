# Consistency-check regression corpus

Planted contradictions and answer keys from the ten-round blind experiment
behind `skill-consistency-check`. Use it to re-check the checker after any
change to its detector specs, grouping or model.

It lives outside `skills/` because the multi-file package has nested
`agents/` and `references/` folders, which the flat-skill rule forbids
inside a skill. The ~120k-token filler package from the experiment is not
included.

## Layout

| Path | What it is |
|---|---|
| `single-a/docs/doc_1..6.md` | Six single-file skills: three originals, three with planted contradictions |
| `single-a/truth.json` | Answer key: `plants` (P1–P9, flat `lines` per plant) and `genuine` (pre-existing conflicts, `docs: {doc_N: {lines}}`) |
| `single-b/docs/doc_1..6.md` | Second set of six single-file skills |
| `single-b/truth.json` | Answer key: `plants` (Q1–Q12, `sides: [{role, lines}]`) and `genuine` |
| `multi/pkg/` | One 13-file skill package (`SKILL.md`, `agents/`, `references/`) |
| `multi/truth.json` | Answer key: `plants` (X1–X6, `sides: [{role, file, lines}]`) and `genuine` |
| `multi/recorded/son.{read,sim}.s{1,2}.json` | Round-8 Sonnet findings: two read-through and two walk-through runs |
| `score.py` | Scorer (stdlib only) |
| `test_score.py` | Scorer tests |

The docs and package are byte-identical copies of the experiment inputs.
Line numbers in the answer keys refer to them, so do not edit these files.

## Running a check on a set

1. Run the checker on the target without showing it `truth.json`:
   - `multi/`: point it at `multi/pkg/` as the skill folder.
   - `single-a/` or `single-b/`: run it on one `docs/doc_N.md` at a time.
2. Save each run's findings as JSON in this shape:

   ```json
   {"findings": [{"id": "F1", "type": "direct", "confidence": "high",
     "side_a": {"file": "SKILL.md", "lines": [287], "quote": "..."},
     "side_b": {"file": "references/eval-methodology.md", "lines": [24], "quote": "..."},
     "why": "..."}]}
   ```

   Single-file sets omit `file`. Name those findings files `doc_N.<anything>.json`
   or pass `--doc doc_N`.
3. Score one or more runs together (their union is scored):

   ```sh
   python3 score.py multi multi/recorded/*.json
   python3 score.py single-a runs/doc_4.read.json runs/doc_5.read.json
   python3 score.py single-b my-run.json --doc doc_3
   ```

Tests: `python3 -m pytest skill-dev-toolkit/tests/consistency-check-corpus -q`.

## How scoring works

- **Caught plant.** A finding catches a plant when its `side_a` and `side_b`
  touch two different sides of the plant. "Touch" means any cited line is
  within 1 line of a line on that side, and the file matches when files are
  given. Single-a plants list flat lines, so the scorer splits them into sides
  wherever consecutive lines are more than 2 apart.
- **Scope.** For single-file sets only the plants of the docs you scored are
  counted. For `multi/` all six plants are counted.
- **Recall** is caught plants over counted plants, across the union of all
  findings files given.
- **unmatched_high** lists every high-confidence finding that catches no plant
  and matches no `genuine` item (a genuine item matches when both sides touch
  it). Medium and low findings are never listed.

**Unmatched does not mean false.** A machine cannot prove a finding is false.
An unmatched finding may be a real conflict that the answer key does not
record. For example, `son.sim.s2.json` F1 is unmatched here, but the round-8
triage judged it a real conflict. The experiment's TRIAGE reviews used human
and LLM judgment to classify every finding. Review each unmatched-high finding
the same way before counting it as a false positive.

The match rule is a line-overlap heuristic. It can credit a finding whose
sides land on the right lines for the wrong reason, so spot-check caught
plants too.

Output is JSON on stdout: `plants` (id, type, caught, caught_by), `recall`,
`unmatched_high`, `findings_total`, plus `docs` for single-file sets.
