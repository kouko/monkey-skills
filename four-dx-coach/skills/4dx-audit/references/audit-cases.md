---
name: 4dx-audit past-application cases
description: Two composite cross-layer audit cases extracted from SKILL.md A1 — load when user situation resembles either pattern or when constructing per-layer recommendation rationale
source: McChesney et al. 2021 Ch 6 + Ch 10 industry composite
---

# 4dx-audit — A1 Past Application (full cases)

## A1 — Past Application

### Case 1: Mid-size company with OKRs + 12-metric dashboard + collapsed weekly cadence (composite case from book Ch 10 + industry pattern)

- **Problem**: A 12-person product team had: (a) annual OKR "improve user retention 15%", (b) Notion dashboard with 12 KPI metrics, (c) weekly meetings that collapsed under firefighting after 4 weeks.
- **Audit findings**:
  - L1 WIG: malformed (OKR has Y but no X baseline / no When fixed; "user retention" too abstract)
  - L2 Lead: absent (12 metrics is database, not 2-3 lead measures; none pass two-axis test for daily action)
  - L3 Scoreboard: present but failing (12 metrics violates ≤4; team doesn't look = engagement-collapsed coaches' board)
  - L4 Cadence: broken (4-week lapse = rescue territory, not normal D4)
  - L5 Substrate: capacity weak (firefighting indicates ~80%+ whirlwind without protected slot)
- **Recommendations**: (1) Reformulate WIG: "From 35% Q3 retention to 50% by Mar 31" (route → `4dx-d1-wig-formulation`); (2) Cull dashboard from 12 → 2 lead measures via two-axis test (route → `4dx-d2-lead-measures` then `4dx-d3-scoreboard`); (3) Diagnose cadence collapse before restarting (route → `4dx-sustain-momentum-rescue`); (4) Capacity audit if firefighting persistent (route → `4dx-meta-whirlwind-triage`).
- **Conclusion**: The team had artifacts in all 4 layers but only one (L3 scoreboard) was at-fault structurally; the actual collapse was at L4 (cadence) and L5 (capacity). Audit unwound the symptom from the cause.

### Case 2: Strategy doc dropped at a kickoff (composite from Ch 6 worked examples)

- **Problem**: A leader says: "Here's our 5-page strategy doc — pick our Primary WIG using 4DX." Doc lists 9 strategic priorities, 4 of them flagged "critical".
- **Audit findings**:
  - L1 WIG: candidates present but **9 is far too many**; "critical" tagging doesn't pass Battles 2×2 importance × feasibility filter; need to narrow to 1
  - L2-L5: not yet populated — this is a pre-D2 input
- **Recommendations**: (1) Run Battles 2×2 on the 9 → narrow to 2-3 → pick 1 Primary WIG (route → `4dx-d1-wig-formulation` team-select mode); (2) After WIG selected, identify 2-3 leads (route → `4dx-d2-lead-measures` team-facilitate); (3) Build team scoreboard (route → `4dx-d3-scoreboard` team-lead-design); (4) Set up cadence (route → `4dx-d4-cadence` team-leader-session).
- **Conclusion**: Even artifact-rich starts need a sequenced roadmap; the audit's value is **ordering** the work, not just identifying gaps.
