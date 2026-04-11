# Source Citation Checklist Gate

## Primary Sources

- `standards/source-quality-and-evidence.md` — primary/secondary/tertiary taxonomy + Kovach verification discipline
- `standards/confidence-and-claim-language.md` — IPCC/Kent calibrated language + 高/中/低 mapping + Fact/Analysis/Speculation taxonomy
- `standards/citation-standards.md` — citation format rules, data freshness window, per-style examples

## Mode-Aware Triggering (v4.9.1)

This checklist is a **MUST gate in deep mode only**. In quick mode,
this checklist is **NOT triggered** — the worker's SELF check applies
instead. The v4.9.1 cost-aware modes mechanism (see SKILL.md
§Research Modes) ensures quick-mode workers do not trigger this
gate: quick mode by definition runs a stripped-down single-pass
triangulation with ≥1 primary source per claim and exits at Medium
confidence, which is below the threshold this gate is calibrated
to enforce.

When deep mode runs the gate, all CHK-SRC-001 through CHK-SRC-007
items apply unchanged. Per-mode threshold tuning (for example a
relaxed claim-to-citation ratio for quick mode) is deferred to
v4.9.2 if real usage shows the binary skip is too coarse.

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific per-claim source thresholds
and the per-claim (not per-deliverable) policy.

## Evaluation Instructions

You are a strict fact-checker. Check each item below against the
research draft. You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE`
for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-SRC-001 (Citations)** [FATAL]: Every factual claim has an explicit, verifiable source citation. No unsourced assertions of fact.
- [ ] **CHK-SRC-002 (Data Freshness)** [FATAL]: All cited data is current. For fast-moving topics, sources older than 6 months are flagged with their date. No stale data presented as current.
- [ ] **CHK-SRC-003 (Confidence Levels)** [FIXABLE]: Key conclusions are tagged with confidence level (高/中/低). No unqualified certainty on contested claims.
- [ ] **CHK-SRC-004 (Fact vs Opinion)** [FIXABLE]: The text clearly distinguishes facts (cited) from analysis (reasoned) from speculation (hedged). No opinion masquerading as fact.
- [ ] **CHK-SRC-005 (Primary Source Priority)** [FATAL]: Load-bearing claims cite primary sources (official docs, filings, peer-reviewed papers, central bank releases) where available, not just secondary commentary. Per `standards/source-quality-and-evidence.md` §The Primary / Secondary / Tertiary Taxonomy: a claim grounded only in secondary sources when a primary source exists and is accessible is a fatal verification failure.
- [ ] **CHK-SRC-006 (Confidence Calibration)** [FIXABLE]: The 高/中/低 confidence tags map correctly to the IPCC 5-tier ladder per `standards/confidence-and-claim-language.md` §Mapping Research-Team 高/中/低 to IPCC 5-Tier. No speculative claims labeled 高, no well-established facts labeled 低.
- [ ] **CHK-SRC-007 (Citation Format)** [FIXABLE]: Citations follow a consistent style (APA / Chicago / IEEE) per `standards/citation-standards.md` §Citation Format Examples. URLs include an access date for web sources. Version numbers and data dates are explicit.

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` → final verdict is `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` items (no FATALs) → final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` → final verdict is `PASS`

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-SRC-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE",
      "evidence": "Specific uncited claim or verification",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```

Reference `standards/citation-standards.md` for the full citation rules.
