# Dogfood report — `obsidian-markdown` sentence-clarity rules

> Advisory record. Three rounds of blind A/B tests on the four sentence-level
> writing rules in `obsidian/skills/obsidian-markdown/references/sentence-clarity.md`.
> Raw outputs of rounds 1–2 are in this directory; round 3 used passages from a
> private vault, so only its aggregate tables are kept.

## Metadata

| Field | Value |
|---|---|
| Skill path | `obsidian/skills/obsidian-markdown/` (rules file), cited by `obsidian-research` Step 5 |
| Skill version | obsidian plugin 3.27.0 |
| Date | 2026-11-14 |
| Rules source | Clark, Martin & Mahowald (2026), arXiv:2610.29162 — measured English only, tested no mitigation |
| Writers | fresh subagents, session model `claude-fable-5-2`; round 2 adds `haiku` |
| Judges | 2 fresh `opus` subagents per round, blind to arm and to the existence of arms |
| Harness | in-session subagents (not headless `claude -p`); writers inherit the user's global instructions |

## Headline results

| Finding | Evidence |
|---|---|
| Rules v1 made Chinese prose stilted | rounds 1 and 2, 4 judges: STILTED 4/2 and 4/5 with v1, 0/0 and 0/2 without |
| Rules v2 removed that and cut flagged sentences on short essays | round 2, both judges: 2.4/3.6 flags per 100 sentences vs 8.1/8.1 without rules |
| On real vault passages the rules made no measurable difference | round 3, both judges: 12.1/9.7 with rules vs 13.0/11.2 without |
| Rewriting itself was the large effect | round 3: original passages 70.1/73.8 flags per 100 sentences |
| A fifth rule against stock phrasing had no effect | round 3: STOCK 2/1 with it, 2/1 without — dropped |

Shipped: rules v2 (four rules).

## Method

Every round: writers produce texts into files; `blind.py` shuffles them to
`S01…` labels and writes `key.json`; two judges flag sentences and rank texts
without seeing the key; `score.py` / `score3.py` unblind and tabulate.

Judge flag types — P1 lifeless subject doing a person's action · P2 words that
belong together far apart · P3 missing connective · P4 unusual wording or
unexplained term · STOCK stock phrasing · STILTED unnatural or mechanical ·
REREAD had to read twice · DIFF (round 3) fact differs from the sibling versions.

| Round | Material | Arms |
|---|---|---|
| 1 | 3 topics picked by the tester, 350–450 characters, from model knowledge | A no rules ×6 · B rules v1 ×6 |
| 2 | same 3 topics; round-1 texts re-judged alongside | A, B carried over · C rules v2 ×6 · HA haiku no rules ×3 · HC haiku rules v2 ×3 |
| 3 | 12 real vault passages (4 research notes, 4 video summaries, 4 daily-news), each rewritten from the same facts | O original ×12 · N rewrite no rules ×12 · R rewrite rules v2 + rule 5 ×12 |

Round-3 passages were picked by a fixed procedure (newest file first, first
run of ≥3 prose paragraphs of 500–900 characters), not by quality. Research
notes yielded only one such passage, so three more were taken under a relaxed
rule (≥2 paragraphs, 300–900 characters).

## Results

### Round 1 — rules v1 (judge 1 / judge 2)

| Arm | Flags per 100 sentences | Readability (1–5) | Mean rank of 4 | STILTED |
|---|---|---|---|---|
| A no rules | 12.2 / 9.5 | 4.00 / 4.33 | 2.50 / 2.50 | 0 / 0 |
| B rules v1 | 12.3 / 7.4 | 4.17 / 4.50 | 2.50 / 2.50 | 4 / 2 |

### Round 2 — rules v2, plus haiku (judge 1 / judge 2)

| Arm | Flags per 100 sentences | Readability (1–5) | Mean rank of 8 | STILTED |
|---|---|---|---|---|
| A no rules | 8.1 / 8.1 | 4.50 / 4.33 | 3.83 / 3.83 | 0 / 2 |
| B rules v1 | 7.4 / 7.4 | 4.17 / 4.33 | 4.67 / 4.33 | 4 / 5 |
| C rules v2 | 2.4 / 3.6 | 4.67 / 4.67 | 2.17 / 2.67 | 1 / 1 |
| HA haiku, no rules | 22.9 / 31.4 | 3.33 / 3.33 | 7.67 / 8.00 | 2 / 5 |
| HC haiku, rules v2 | 20.9 / 16.3 | 3.67 / 4.00 | 7.00 / 6.33 | 1 / 2 |

The judges disagree on haiku: one sees flags halved, the other sees no change.

### Round 3 — real vault passages (judge 1 / judge 2)

| Arm | Flags per 100 sentences | Readability (1–5) | Ranked first of 12 | DIFF |
|---|---|---|---|---|
| O original | 70.1 / 73.8 | 2.67 / 2.83 | 0 / 0 | — |
| N rewrite, no rules | 13.0 / 11.2 | 4.33 / 4.17 | 5 / 6 | 1 / 1 |
| R rewrite, rules | 12.1 / 9.7 | 4.58 / 4.33 | 7 / 6 | 1 / 0 |

By source type the direction is inconsistent (4 passages each): daily news
favours the rules (first place 3/4 and 4/4), research notes favour no rules
(3/4 and 4/4), video summaries tie. The originals average 60–97 characters per
sentence; both rewrites average 36–62 (`r3/lengths.txt`). The dominant flag in
the originals is P2 (21 / 21), which both rewrites remove (0–1). The largest
remaining flag is P4, mostly terms that all three versions share.

## Findings

### FINDING-001 — "make the subject a person" breeds repeated generic subjects in Chinese

- **Severity**: Medium · output quality (harm introduced by the rule)
- **Evidence**: with rules v1, writers opened sentence after sentence with 「學習者」「團隊」「人」; judges flagged them as mechanical or translated (`r1/judge/`, `r2/judge/`, arm B).
- **Root cause**: rule 1 asked for a person as subject; Chinese normally drops a subject the previous sentence made clear.
- **Fix applied (v2)**: rule 1 now says it removes personification and does not ask for a person in every sentence, with a Chinese example; the after-drafting check adds a pass for translated-sounding or repetitive sentences.

### FINDING-002 — long modifier before the noun, and skipped reasoning steps

- **Severity**: Low
- **Evidence**: round 1, both arms — definitions written as one long 「…的方法」 clause; inferences compressed into one sentence.
- **Fix applied (v2)**: rule 2 names the Chinese/Japanese case and gives an example; rule 3 adds "do not skip a step".

### FINDING-003 — no measurable benefit on real material

- **Severity**: informational
- **Evidence**: round 3 table. With 12 passages the with/without difference is inside judge-to-judge variation.
- **Reading**: the session model already avoids most of these patterns; the rules do no harm (STILTED 1/1 with, 2/3 without; DIFF equal).

### FINDING-004 — rule 5 (no stock phrasing) did nothing

- **Evidence**: added after round 2 because haiku texts kept slogan-like closing lines; in round 3 STOCK counts were identical with and without it.
- **Action**: removed before shipping. Text of the dropped rule: "Every sentence tells the reader something new. Cut a sentence that only restates, announces or decorates: a slogan-like closing line, an empty summary placed before the real answer, or a 'not X but Y' contrast when no reader believed X."

## Limits

- Rounds 1–2 use three topics the tester chose, and v2 was written from the judges' comments on those same topics, so round 2 is optimistic.
- Round 3 tests rewriting an existing passage, not writing a note from sources. Its originals were written earlier, by older or smaller models inside full pipelines, so the original-vs-rewrite gap is not all due to rewriting.
- 3–12 texts per arm; judges are models, not the vault's reader.
- All texts are Traditional Chinese. Nothing here tests English or Japanese notes.

## Files

- `rules-v1.md` — the first version of the rules (the shipped file is v2).
- `blind.py`, `score.py`, `score3.py` — blinding and scoring scripts. Re-run: `python3 score.py r1 --flags`.
- `r1/`, `r2/` — raw texts, `key.json`, judge output. `r2/raw/` holds only the texts round 2 added; its A and B texts are `r1/raw/`.
- `r3/scores.txt`, `r3/lengths.txt` — aggregate tables only.
