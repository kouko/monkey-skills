# Control group — Anthropic "The AI-Native SDLC Playbook"
Source: https://claude.com/blog/the-ai-native-sdlc-playbook (fetched 2026-09-02)

## Artifact chain (6 artifacts)
| artifact | author | approver | lives |
|---|---|---|---|
| intent.md — problem, proposed outcome, affected users/systems, constraints, open questions; "captured once, in the originator's own words" | originator (person, ticket filer, or incident trigger) | product owner; commit triggers Design | intent/ folder in repo or dedicated repo |
| spec.md — requirements + design spec, constrained by org skills (brand/security/compliance/UX) | Claude | product owner (+ tech lead if higher risk); commit triggers Build | alongside intent.md |
| plan.md — files that change, order of work, tests that prove it, risks | Claude in plan mode, engineer iterates | engineer; deviations update plan.md in same commit | repo, committed before code |
| diff/PR — code + tests + docs | Claude Code | code owner via branch protection | PR |
| review findings — bugs / security / compliance vs spec+plan+principles; ranked; do NOT approve or block | Claude review agent | human code owner | PR thread + CI |
| CLAUDE.md — conventions, commands, architecture, mistakes ("mistake twice → goes in") | team | code owners | repo root |

## Roles (9): originator, product owner, engineer, code owner, tech lead/architect, policy owner, security lead, release manager, service owner

## Governance mechanisms — exactly three tiers
- CLAUDE.md / skills = ADVISORY (agent likely applies; nothing forces)
- hooks = DETERMINISTIC (allow / ask / block, logged with timestamp); managed hooks non-bypassable
- git = AUDIT TRAIL ("the chain of commits is also the audit trail: who asked for what, what the agent produced, who approved it")
- evals in CI: 20–50 real tasks; run on change to CLAUDE.md/skills/hooks; each incident → permanent eval
- separation of duties: writer ≠ approver (branch protection), diagnoser ≠ fixer (approval hook)

## Sign-off points (5): intent (PO) → spec (PO) → plan (engineer) → PR (code owner) → prod deploy (release manager, hook)

## Maintain loop
deterministic detection script (no model) → 1σ log / 2σ Claude diagnoses read-only / 3σ Claude proposes PR → findings written AS intent.md (Stage 1 format) → service owner triages

## What is notably ABSENT vs loom
- no plan-splitting grammar, no batch review, no packets/receipts, no gate markers
- no critic panel; review = one identical agentic pass per PR + one human
- no "brief"; intent is pre-solution and owned by a person, spec is post-design and authored by Claude
- skills are advisory by definition; enforcement only via hooks
