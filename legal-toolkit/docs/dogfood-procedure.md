# Dogfood procedure — calibrate self_grade.py against hand-grading

> **Phase 1.6 (v0.3.0)** procedure. The deterministic rubric in
> `self_grade.py` is necessary but not sufficient — it catches structural
> failures but cannot judge whether `walk_away_triggered` was a true
> match or whether a citation actually supports the conclusion it backs.
> The dogfood procedure calibrates the LLM-judged semantic tier against
> a human-graded reference set.

> **Calibration is not packaged with the plugin** — corpus files (real
> contracts) are sensitive; only the procedure ships. Each owner
> calibrates locally.

---

## Goals

The ROADMAP §Phase 1.6 quality gate:

| Metric | Target | Why this gate |
|---|---|---|
| `answer_score` Pearson correlation (LLM self-eval vs hand-grading) | **≥ 0.6** | LLM must rank contracts roughly the same as a human |
| `source_score` Pearson correlation | **≥ 0.7** | Higher bar — citations are binary "real or not", more objective |
| Hallucinated citation rate (SRC-09) | **0%** | One fabricated case ⇒ hard fail; this is not a Pearson item |

If Pearson < target after 5-10 contracts:
- Examine the criterion with the worst LLM-vs-hand disagreement
- Move misfiring semantic items to advisory tier OR tighten them to a
  deterministic check
- **Never** just lower the target — that hides the gap

---

## Corpus shape

Recommended: **5-10 contracts** covering the 5 `contract_type` buckets
that Phase 1 protocols recognise.

| # | Contract type | What to look for |
|---|---|---|
| 1 | NDA | Simplest structure; tests `nda` mode + L4-L7 fast path |
| 2 | SaaS MSA (mid-deal, < USD 1M) | Mainstream; full L0a-L7 + ABAC variant matching (LoL mid-deal / Indemnification mid-deal / DPA matching) |
| 3 | SaaS MSA (large-deal, ≥ USD 1M) | Super-cap region; ABAC large-deal hits; Override likely triggered |
| 4 | 採購合約 | 民法 §247-1 定型化契約檢查 (L0b); typically advisory mode for many clauses |
| 5 | 勞動契約 | 勞基法 §9-1 / §15-1 強行規定 (L0a); advisory mode (no labour entries in fallback) |
| 6 | DPA (TW-only) | Tests DPA tw-only variant + 個資法 §27 |
| 7 | DPA (GDPR overlay) | Tests gdpr-overlay variant + SCC requirement |
| 8 | DPA (cross-border) | Tests cross-border variant + 個資法 §21 |
| 9 | 服務委任 (IP-heavy custom dev) | Tests IP-Assignment flat entry + work-product carve-outs |
| 10 | Mixed-jurisdiction (TW + US) | Edge case — non-TW jurisdiction should skip L0a/L0b/L6.5 |

---

## Per-contract workflow

```
1. Pick a real contract (or carefully redacted version) from your archive.
   Store under <project>/docs/dogfood-corpus/<NN>-<descriptor>/
   (this folder is .gitignored — never commit real contracts)

2. Run /legal-contract-review on it.

3. The pipeline emits 6 .md files + a findings.json under
   legal-outputs/<timestamp>-<name>/. Inspect the JSON.

4. Run scripts/self_grade.py for the deterministic baseline:

     uv run skills/legal-contract-review/scripts/self_grade.py \
         --input legal-outputs/<timestamp>-<name>/findings.json \
         --outputs-dir legal-outputs/<timestamp>-<name>/ \
         --format markdown

   This writes legal-outputs/<timestamp>-<name>/self-grade.md with the
   17 ANS + 5 SRC deterministic results.

5. Hand-grade the same outputs using the same rubric:
   For each ANS-XX / SRC-XX criterion, mark pass/fail according to your
   own reading of the contract + output.

   Record in:  <project>/docs/dogfood-corpus/<NN>-<descriptor>/hand-grading.yml

6. Compare LLM verdict vs hand verdict criterion-by-criterion. Tabulate.
```

---

## Hand-grading template

`<NN>-<descriptor>/hand-grading.yml`:

```yaml
contract: 02-saas-msa-mid-deal
contract_type: SaaS
jurisdiction: TW
deal_size: 350000

# Per-criterion hand-grade
hand:
  answer:
    ANS-01: pass
    ANS-02: pass
    # ... etc — for the 20 criteria (semantic ones the hand grader judges directly)
  source:
    SRC-01: pass
    # ...

# LLM result captured from self-grade.md
llm:
  answer:
    ANS-01: pass
    # ...
  source: { ... }

# Agreement
agreement:
  total_criteria: 30                   # 20 ANS + 10 SRC
  agreed: 28
  llm_false_positive: 1                # LLM passed, hand failed
  llm_false_negative: 1                # LLM failed, hand passed
  pearson_answer: 0.85                 # spreadsheet calc
  pearson_source: 0.92

# Disagreement notes
disagreements:
  - { criterion: ANS-18, llm: pass, hand: fail, note: "LLM accepted a finding that hallucinated a clause not in the contract" }
  - { criterion: SRC-07, llm: pass, hand: unverifiable, note: "案號 looks plausible but isn't in 司法院 database" }
```

---

## Cohort summary

After 5-10 contracts:

```
                     | Answer Pearson | Source Pearson | Hallucinated cites |
---------------------|----------------|----------------|--------------------|
contract 01 (NDA)    | 0.92           | n/a            | 0                  |
contract 02 (SaaS)   | 0.85           | 0.88           | 0                  |
contract 03 (SaaS-L) | 0.78           | 0.95           | 0                  |
contract 04 (採購)    | 0.65           | 0.72           | 1                  |
contract 05 (勞動)    | 0.62           | 0.70           | 0                  |
contract 06 (DPA-TW) | 0.71           | 0.81           | 0                  |
contract 07 (GDPR)   | 0.68           | 0.83           | 0                  |
contract 08 (X-bord) | 0.72           | 0.79           | 0                  |
---------------------|----------------|----------------|--------------------|
Cohort mean          | 0.74           | 0.81           | 0.125              |
Gate                 | ≥ 0.60         | ≥ 0.70         | = 0                |
PASS / FAIL          | PASS           | PASS           | FAIL (1 in #04)    |
```

If any contract surfaces a hallucinated citation → fix the underlying
prompt OR move SRC-09 to a stricter deterministic check (e.g. require
URL for every `case` citation). Hallucinated citations are unacceptable
even when Pearson is fine.

---

## Cohort decisions

After running the cohort, the maintainer answers:

1. **Is Pearson ≥ target on each metric?** → if yes, Phase 1.6 done; the
   semantic rubric is ready.
2. **Is hallucinated-citation rate 0?** → if yes, Phase 1.6 done.
3. **Which criteria misfire most?** → these are candidates for moving
   into the deterministic tier with tighter checks.
4. **Which contract types are weakest?** → suggests where Phase 2-3 needs
   more dedicated sub-skills (e.g. if 勞動契約 scores poorly because
   bundled fallback has no labour entries, Phase 2's `legal-document-draft`
   plus a Phase 1.5+ extension to baseline could close the gap).

---

## Privacy + governance

- **Never commit real contracts.** `<project>/docs/dogfood-corpus/` is
  `.gitignored` for legal-toolkit just as `legal-outputs/` is for users.
- **Redact when sharing externally.** If you want to share the corpus
  for skill iteration with another reviewer, run the contracts through
  a redaction pass (party names → [Counterparty], amounts → [Amount],
  individuals → [Person]) per `.legal-toolkit/config.yml`
  `global_rules.redaction_before_cloud`.
- **Don't paste real contracts into Claude.ai web** without checking
  data-handling policy.
- **Hand-grade locally; share aggregates only.** The cohort summary
  table above is shareable; the per-contract hand-grading.yml is not.

---

## Reusing the corpus across versions

When Phase 2+ adds new skills (legal-document-draft etc.):
- Reuse the same corpus to baseline new skills
- New skills get their own answer + source criteria + their own Pearson gates
- Cohort summary table grows columns, not rows (same N contracts)

This is why corpus selection in Phase 1.6 should aim for **breadth**
across contract types, not just LoL/Indemnification depth — Phase 4
contract-tracker / regulation-watch + Phase 5 governance / DD sub-skills
will all need to operate on the same contract types.

---

## Reference

- ROADMAP §Phase 1.6: <ROADMAP.md>
- TECH-SPEC §9.1: dogfood corpus shape
- self_grade.py CLI: `--help`
