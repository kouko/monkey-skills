---
name: user-insights
description: |
  The problem-space research verb of loom-design: map, with recorded evidence,
  what users need and which needs are worth serving before design or spec work.
  Two modes: opportunity-space mapping researches the world without asking the
  user for researchable facts; value commitment lets the agent recommend but
  writes only what the user ratifies. Produces user-insights.md, evidence.md,
  and per-question research reports under docs/loom/discovery/<date>-<slug>/.
  Problem-space-pure: needs and outcomes, never solutions. Heavy research goes
  to research-toolkit:deep-deep-research. Use for user needs / what do users
  need / needs research / 使用者需求 / 使用者洞察 / ユーザーインサイト. Not for
  business worth-it verdicts (business-value) or solution design (loom-design).
version: 0.1.0
---

# user-insights

Establish, with recorded evidence, what problem exists, for whom, and which
needs are worth serving, so downstream work starts from verified needs.

This skill is **problem-space-pure**: it states WHAT users need and their desired
outcomes, and never states HOW to solve them. Park mechanisms and solution ideas
in Risks & open questions for downstream design.

## Two modes

Assign modes by the nature of the work, not preference. They may run in one
session, but keep them separated because their ground truth differs.

### Mode 1 — Opportunity-space mapping (knowledge work)

Ground truth is in the world: users, competitors, prior art, and the repo.

- **Never interrogate the user for facts that are researchable** through search
  or repo reading. Research them.
- Write the Opportunity space in `user-insights.md`. Express each need as an
  evidence-linked job story — “When …, I want …, so I can …” — plus context or
  journey stage and today's workaround.
- Keep job stories outcome-only. Strip mechanism nouns such as UI elements,
  folder structures, or “automatically moved”; park them in Risks & open
  questions. A missing Solution heading does not catch mechanisms inside a
  story.
- Every asserted need cites a claim row in `evidence.md`. A need with no evidence
  is an open question, not a finding.

### Mode 2 — Value commitment (value judgment)

Ground truth is with the user. Research first, then provide “my take”:

1. Present the evidence-backed opportunity space and an explicit recommendation:
   - **Recommend** — needs to serve.
   - **Why** — supporting evidence and reasoning.
   - **Conditional reversal** — the fact that would flip the call.
2. Write the commitment only after the user ratifies it through an **explicit
   affirmative user reply** to that recommendation; no sign-off ritual is
   required. Mark `ratified by user on <date>`. If the user chooses a different
   set, write what was ratified and record the divergence.
3. **Agents never self-commit** on the user's behalf. Mapping and recommending
   belong to the agent; deciding belongs to the user.

## Research routing

- Delegate to `research-toolkit:deep-deep-research` when discovery has **more
  than 3 research questions**, or requires **primary user evidence** such as
  interviews or usage data. Pass artifact paths plus structured seed context;
  never inline the analysis. The delegate runs its pipeline and returns findings.
- Otherwise research inline. Run **EN + JA** web queries each round and cite both,
  labelled by language. Report a language's zero relevant hits as a finding.
  If live search is unavailable, delegate through the host's heavyweight route
  to `research-toolkit:deep-deep-research`; do not guess.

In both paths, place findings in `evidence.md` claim rows and per-question
`research/` reports, never as unsourced assertions.

## Artifacts and evidence chain

Use `docs/loom/discovery/<date>-<slug>/`, where date is today's `YYYY-MM-DD` and
slug is kebab-case. Reuse an existing folder for the same topic.

| Artifact | Role |
|---|---|
| `user-insights.md` | Insights and ratified commitment, following `assets/user-insights-template.md`. |
| `research/` | One auditable report per research question: goal, method, findings, insight skeleton. |
| `evidence.md` | Claims-to-evidence registry, following `assets/evidence-template.md`. |

```text
evidence.md (facts) → research/ (reports) → user-insights.md (insights + commitment)
```

**Evidence outlives any single report.** Reports may be rerun or discarded;
their underlying facts remain in `evidence.md`, keeping discovery understandable
months or years later.

Downstream, committed outcomes inform falsifiable `PRINCIPLES.md` checks, needs
and journey stages seed interaction flows, and job stories seed acceptance
criteria. State these inputs in problem-space terms; consumers translate them.

## Behavioral boundary

user-insights agents map needs and propose commitments. They **may not render
investment / worth-it verdicts**; that belongs to business-value. The skills
share no artifact or agent. Agents never self-commit.

## Workflow

1. **Frame** what the user struggles with, why now, and whose problem it is in
   `user-insights.md` §Problem framing. Include no solution.
2. **Map** Mode 1: research through the route above, record atomic claims in
   `evidence.md`, and write evidence-linked job stories.
3. **Propose** Mode 2: ask only legitimate value questions—priorities among
   mapped needs and appetite—then present Recommend / Why / Conditional reversal.
4. **Ratify**: update §Value commitment only after ratification and record its
   date and any divergence.
5. **Close** with Risks & open questions. Unsupported claims belong there, not
   in Opportunity space as settled findings.
6. **Validate, then fix** before declaring discovery done. The script is in the
   PLUGIN repo while artifacts are in the CONSUMER project; resolve the script
   to an absolute path and run from the consumer root:

   ```text
   cd <consumer-project-root>
   argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/discovery/validate_discovery_artifacts.py", "<discovery-folder>"]
   ```

   Pass the argv array directly to process execution; never through a shell.
   On non-zero, fix and rerun, **bounded at 2 attempts**. If still non-zero after
   2 fix-and-rerun cycles, stop and surface remaining problems in plain language.
   The validator accepts sanctioned greenfield/first-run states such as an
   assess-first `business-value.md` alone, but never waive a schema violation.

## References

- `assets/user-insights-template.md` — output skeleton.
- `assets/evidence-template.md` — claims-to-evidence registry.
- loom-code brainstorming `references/axis4-research-protocol.md` — Mode 2's
  research-then-my-take protocol.
- `../using-loom-design/references/discovery-claude-code-tools.md` (Codex:
  `discovery-codex-tools.md` beside it) — host-specific research invocation.
