# Brief: replay-oracle calibration after L1 first run (classes A+B+C; D stays)

- Date: 2026-07-11
- Source: first real `principles-replay-matrix` run (runLabel `calib-r1`, 6 seeds,
  passRate 0/6) — every miss re-verified on disk against the produced artifacts
  (misses re-derived by re-running validator + checker manually; grade.txt paths
  recorded in the run output). User approved doing A+B+C in one small branch;
  class D is deliberately NOT calibrated away.
- Context: L1/L2 shipped in PR #533; the BACKLOG harness entry carries the
  first-run calibration re-trigger this brief discharges.

## Miss classification (evidence from calib-r1 artifacts)

- **A. Token-form defects (oracle data fixes, artifact-evidenced)**: compound
  tokens where artifacts anchor separate rows (`TypeScript+React`,
  `PostgreSQL+Redis`); spacing variants (`Hexagonal/Ports & Adapters` vs
  artifact `Hexagonal / Ports & Adapters`; `Swift/SwiftUI` vs `Swift / SwiftUI`;
  `SLA/uptime 目標` vs artifact `SLA/uptime目標`); cross-cell spans (`WCAG 2.2`
  where artifact splits canon `WCAG` / version `2.2 AA`); descriptive suffixes
  (`SVG format` vs `SVG 2.0 (file format)`; `C++/Qt stack` vs a
  `Technology Stack` row whose version cell names C++ 17+ and Qt 6).
- **B. Alias / language variance**: oracle short forms vs artifact long forms
  (`JTBD` vs `Jobs-to-be-Done`; `Apple HIG` vs `Apple Human Interface
  Guidelines`); CJK deferred tokens (`可逆性`, `升級胃口`, `成本`) missing
  English artifacts ("Reversibility posture", "Upgrade appetite", "Cost
  posture") — replay artifact language is nondeterministic (seed5 produced
  Chinese, others English), so a single-substring token cannot cover both.
- **C. Negative false positives on correct behavior**: `mock server` /
  `API gateway` hit an explicit scope-OUT line; `企業版` hit a rejection
  principle (「不優化企業版多店管理」). The artifacts did the right thing;
  bare-noun negative tokens register rejection mentions as violations.
- **D. Genuine drops — the measured signal, DO NOT calibrate away**: prose-named
  stack/canon items absent from `## Anchors` entirely (seed1 Layered/N-Tier +
  Hexagonal; seed2 React Native; seed3 Rust; seed5 React/TypeScript/FastAPI/
  PostgreSQL; seed4 Kenya Hara present only in body prose, no Anchors row).
  Mechanically reproduces the #532 residual "prose-named stack/canon → Anchors
  drops 5/6". This is the baseline the improvement loop consumes.

## Build (this branch)

1. **Parser `|` alternatives (checker contract extension, TDD)**: a token may be
   written `alt1|alt2|…`; the item matches if ANY alternative matches, applied
   uniformly across the three check classes. `|` is chosen because no calib-r1
   token or artifact cell legitimately contains it. parse_oracle returns items
   as alternative-lists (or equivalent); CLI miss lines keep naming the item as
   written in the oracle. Module docstring (the format contract) updated.
2. **Oracle re-tokenization (A+C data fixes + B pairs)**: apply class-A fixes;
   write class-B items as `CJK|English` / `short|long` alternative pairs;
   re-author the three class-C negative tokens as acceptance-context phrases
   that would only appear if the bait were ACCEPTED (not merely mentioned in a
   rejection/scope-out). Update the committed-oracle regression test's exemplar
   pins to match. Grader-only prose (`stances:`, `out_of_jurisdiction_bait:`,
   `# note:` lines) untouched.

## Out of scope

- Class D remediation (that is the improvement loop's job, with this baseline).
- Workflow robustness (grade-stage StructuredOutput throw drops the row to null
  instead of a degraded failed row — recorded in BACKLOG as next-touch).
- Pinning replay artifact language (observed nondeterminism stays; `|` pairs
  absorb it at the oracle layer).

## Acceptance (whole branch)

- Checker suite green incl. new alternative-syntax tests; committed-oracle
  regression test green with updated pins.
- Re-run `principles-replay-matrix` once post-calibration: remaining misses are
  class-D only (no A/B/C-shaped miss survives).
