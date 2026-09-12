# Separate intent, spec, and plan vocabulary — plan
intent: 2026-09-12-separate-intent-spec-plan-vocabulary@172a6239a
charter: 1.0

## Current State Evidence
- Forward: `loom-design/skills/capture-intent/SKILL.md` currently calls an unspecified early request “what they want” and defines Acceptance later in the interview.
- Reverse: `loom-design/skills/write-spec/SKILL.md` and `loom-code/skills/write-plan/SKILL.md` each repeat only the product-versus-engineering vocabulary, not their decision boundary.
- Error: dogfood case `t06` loaded capture-intent in only one of three runs when the user named a recurring problem but had not chosen concrete behaviour.
- Data: `docs/skill-dogfood/2026-09-12-capture-intent/report.md` records 8/8 correct negative routes and no executor invention of UI, state, IDs, or implementation.
- Boundary: the user explicitly rejected new IDs, checker mechanisms, stations, and review loops; this change is prose plus focused contract tests only.

## Task DAG

### Wave 0 — Define station-local boundaries

**W0-01 Add concise vocabulary and decision boundaries**  after: none  acceptance: 1,2,3
- Files: capture-intent, write-spec, write-plan SKILL.md files and focused station-text tests.
- Test: A1 positive: vague-outcome-is-valid-intake; boundary: acceptance-is-not-spec. A2 positive: outcome-to-behaviour; boundary: no-new-scope. A3 positive: behaviour-to-implementation; boundary: return-product-gap.
- Risk: agent-decided — duplicate only the station-specific boundary because a shared glossary would add cross-plugin coupling.

## Questions asked
- ① — what — 將三個 station 各自加入短詞彙與決策邊界，不改 schema、ID、checker 或流程節點，是否開始實作？（答：做吧）

## Risks
1. Repeating too much terminology could raise prompt cost or become a second specification; focused tests keep the additions short and distinct.
