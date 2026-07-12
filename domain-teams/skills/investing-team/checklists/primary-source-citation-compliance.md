---
name: primary-source-citation-compliance
description: MUST gate — every load-bearing claim traces to a cited primary source; no unsourced assertions
gate_tier: MUST
---

# Primary Source Citation Compliance

## Primary Sources

- `standards/data-sources-and-fixtures.md` — Provenance Footer format, fixture labeling, data source taxonomy
- `standards/taiwan-equity-frameworks.md` — TWSE/MOPS/FSC statutory sources for Taiwan-specific claims
- `standards/investment-memo-format.md` — memo structure requirements including Provenance Footer placement

## Evaluation Instructions

You are a strict citation auditor. Check each item below against the
investing-team output. Mark each item ✅ PASS or ❌ FAIL with
specific evidence. N/A is permitted only where the item explicitly
allows it — you must provide a justification.

## Checklist

- [ ] **CHK-CIT-001 (Valuation Numbers Sourced)**: Every EV/EBITDA, P/E, DCF assumption, or comparable metric in the output traces to a disclosed data source (SEC filing, MOPS, financial API, or user fixture). No unsupported numbers appear without a source label.

- [ ] **CHK-CIT-002 (Framework Invocation Cited)**: Every named framework invocation includes a reference to its governing standard. "Investment Clock" cites `standards/investment-macro-regime.md` or Greetham & Hartnett 2004. "Kelly criterion" cites `standards/position-sizing-and-risk.md` or Kelly 1956. Naming the standard file is sufficient — a full bibliographic citation is not required.

- [ ] **CHK-CIT-003 (No Hedged Vagueness)**: The output contains no phrases of the form "as widely known," "it is well established," "it is generally accepted," or equivalent vague hedges substituting for a citation. Every load-bearing claim either cites a source or is explicitly labeled as the author's own analytical judgment.

- [ ] **CHK-CIT-004 (No LLM-Recall Factual Assertions)**: The output makes no numeric factual assertions (e.g., "Company X's Q3 revenue was Y") relying on LLM recall alone. Each specific numeric claim either traces to a user fixture, a retrieved data source, or is explicitly flagged as an estimate with a stated basis.

- [ ] **CHK-CIT-005 (Provenance Footer Present)**: Any output containing 3 or more distinct data items includes a Provenance Footer table per `standards/data-sources-and-fixtures.md`. Outputs with 1–2 data points may use inline source attribution in lieu of the full footer table. Quick screens with a single data point are exempt — mark N/A with justification.

- [ ] **CHK-CIT-006 (Taiwan Claims Cite Statutory Source)**: Claims about 三大法人 flows, 月營收 reporting rules, 董監持股 thresholds, 融資融券 ratios, or other TWSE/FSC-governed metrics cite `standards/taiwan-equity-frameworks.md` or the underlying TWSE/MOPS/FSC statutory source. Wikipedia, analyst blog posts, and news articles do not satisfy this item.

- [ ] **CHK-CIT-007 (Upstream Warnings and Disclosures Transcribed Verbatim)**: Every `_status` block, `warnings[]` entry, and seed-context mandatory disclosure from the input data files appears in the output's Limitations (or the directly relevant section) at verbatim grade — the substance intact, no silent dropping, softening, or relabeling (e.g. re-labeling an FY-basis multiple as "TTM" is a FAIL; claiming a data section is unavailable when the input files or a provided section inventory show it present is a FAIL). The evaluator cross-checks against the input files / inventory, not against the memo's own claims.

## Verdict Rules

- ✅ All 7 items PASS (or N/A with justification) → **PASS**
- ❌ Any item FAIL → **NEEDS_REVISION** — list each failed item by ID with the specific unsourced claim

## Output Format

```json
{
  "verdict": "PASS | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-CIT-001",
      "status": "PASS | FAIL | N/A",
      "evidence": "Specific unsourced claim or confirmation of compliance",
      "fix_instruction": "How to resolve (for FAIL items only)"
    }
  ]
}
```
