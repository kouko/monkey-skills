# Market Validation Checklist Gate (MAY)

## Scope

User-requested gate (MAY tier) applied when a PRODUCT-SPEC.md makes
**market-level claims** that need lightweight validation before
handoff. This is NOT a full market analysis (that belongs to
research-team `market-analysis` protocol); it is a sanity-check that
the spec's market assumptions are not obviously wrong or unfounded.

Reference standards:
- `standards/planning-frameworks.md` — 3C 分析 (大前 1975), JTBD, 4 Big Risks
- `standards/discovery-frameworks.md` — Customer Development (Blank 2005)
- `standards/goals-and-metrics.md` — North Star Metric, AARRR

## When to Invoke

- User explicitly requests "market check" / "market validation" / "市場
  検証" / "市場チェック" for a PRODUCT-SPEC.md
- Spec makes quantitative market-size claims (TAM / SAM / SOM)
- Spec names specific competitors or positions against a named category
- Spec asserts a regulatory or policy constraint as a market gating
  factor

## Do NOT Invoke For

- Greenfield research (use `research-team` `market-analysis` protocol
  instead — that is the full deep analysis, and it is grounded in
  Porter Five Forces + Blue Ocean Strategy + Business Model Canvas
  via research-team's `strategic-frameworks.md`)
- Technical feasibility assessment (that is CHK-PROD-005 in
  `product-spec-completeness.md`)
- Full competitive analysis (use `research-team` `competitive-analysis`
  protocol)

## CHK-MKT-001: Customer Validation [FIXABLE]

- [ ] Target users are described specifically, not as "users" or
      "everyone". A Customer Segment grounded in 3C 分析 §Customer
      (大前 1975) is named.
- [ ] At least one claim about "what users currently do" is in the
      spec (per Blank 2005 Customer Development — a spec cannot
      claim demand exists without naming the existing alternative
      and explaining why it is inadequate).
- [ ] If the spec names a user pain, the pain is **specific enough
      to be falsifiable** (not "users have difficulty" but "users
      cannot do X within Y minutes without Z interruption").

## CHK-MKT-002: Competitive Landscape [FIXABLE]

- [ ] At least 2 existing alternatives named (including non-direct
      substitutes, per the 3C 分析 Competitor lens — 大前 1975)
- [ ] Each alternative has a stated strength AND a stated weakness
      (no competitor is described only positively or only negatively)
- [ ] The spec explains **why** the existing alternatives are
      inadequate, not just that they exist

## CHK-MKT-003: Market Sizing Claims [FATAL if unsourced]

- [ ] Any quantitative market-size claim (TAM / SAM / SOM,
      percentages, market growth rates, user counts) has a named
      source or is explicitly tagged `[ASSUMPTION]` with a
      validation approach
- [ ] Unsourced quantitative claims are a FATAL failure — the spec
      is claiming facts it cannot support. Either cite the source or
      rewrite as "[ASSUMPTION] — TBD validation via ..."
- [ ] If deep market analysis is needed, the spec explicitly notes
      "defer to `research-team` `market-analysis` protocol" rather
      than fabricating numbers

## CHK-MKT-004: Regulatory / Compliance Claims [FATAL if unsourced]

- [ ] Any claim that a regulation gates or enables the market must
      cite the regulation (name + jurisdiction + year or rule number)
- [ ] Unsourced regulatory claims are FATAL — they often hide
      disqualifying risks

## CHK-MKT-005: Go-To-Market Coherence [FIXABLE]

- [ ] If the spec names a distribution channel, the channel is
      consistent with the target user (you cannot reach teenagers
      via enterprise sales)
- [ ] If the spec names a monetization model, it is consistent with
      the target user's willingness to pay (not assumed)
- [ ] If AARRR funnel is referenced (`standards/goals-and-metrics.md`
      §AARRR), each stage has at least one named metric or
      hypothesis

## Verdict Rules

- Any FATAL check failed → NEEDS_REVISION
- 2+ FIXABLE checks failed → NEEDS_REVISION
- 1 FIXABLE check failed → PASS_WITH_NOTES
- All checks pass → PASS

## Note on Scope

This is a lightweight sanity-check, not a market research
deliverable. If the spec requires actual primary-source market
research with TAM/SAM/SOM breakdown, Porter Five Forces analysis, or
multi-competitor financial modeling, planning-team should **defer to
research-team** and invoke its `market-analysis` or `competitive-
analysis` protocol rather than producing market content in-place. The
division of labor: planning-team owns the PRODUCT-SPEC.md and
validates it internally via this checklist; research-team owns deep
market analysis as a separate deliverable.
