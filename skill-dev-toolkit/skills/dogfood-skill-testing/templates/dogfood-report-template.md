# Dogfood report — `{skill-name}`

> Fill the `{placeholders}`. This report is an **agent-actionable fix
> dossier**: its consumer is the **main agent that will FIX the skill**
> (plus the user reviewing raw outputs). Every finding localizes the
> defect, states why it broke, and names a *suggested* edit class.
>
> **Findings are ADVISORY.** Dogfood discovers + points; it does NOT
> apply edits. The main agent decides and makes the change. Auto-fix is
> out of scope. The user is the final calibrator — read the surfaced raw
> outputs (appendix), then drive the fix by talking to the main agent.

## Metadata

| Field | Value |
|---|---|
| Skill path | `{path/to/working-tree/skill-dir}` |
| Skill version | `{x.y.z from frontmatter}` |
| Date | `{YYYY-MM-DD}` |
| Passes run | `{activation · executor+auditor · cold-reader}` |
| Model pinned | `{claude model id used for activation + subagent runs — pin for reproducibility}` |
| Activation fidelity | `{real-harness sandbox | approximate (injection fallback)}` |

## Severity summary

| Severity | Count |
|---|---|
| Critical | `{n}` |
| High | `{n}` |
| Medium | `{n}` |
| Low | `{n}` |
| **Total** | `{n}` |

> Target ~5–10 well-evidenced findings over volume. Every finding cites
> an actual probe prompt + an actual subagent response (transcript
> excerpt) — no finding asserted from reading `SKILL.md` alone.

## Findings

<!-- One block per finding. Duplicate the template below. Number FINDING-001, -002, … -->

### FINDING-001: {short title}

- **Severity**: `{Critical | High | Medium | Low}`
- **Category**: `{Trigger-miss | Over-trigger | Cold-start | Workflow-drift | Gate-bypass | Jargon-leak | Convention-violation | Progressive-disclosure | Output-quality}`
- **Pass**: `{blind | informed}`
- **Probe prompt**: `{the exact query / task handed to the subagent}`
- **Expected**: `{what the skill should have done}`
- **Actual**: `{what it actually did}`
- **Transcript evidence**: `{verbatim excerpt from the subagent transcript that proves the defect — see Raw outputs appendix for the full transcript}`
- **Root cause**: `{why it happened — the mechanism, not the symptom}`
- **Why static review missed it**: `{what a structural / self-grade check (skill-judge, smoke test) sees as PASS while this is broken — the floor-not-ceiling signal}`
- **Location**: `{SKILL.md:§section | frontmatter description | references/<file> | a gate clause — the exact spot the defect traces to}`
- **Suggested fix direction** (advisory edit class): `{e.g. "add trigger token 'X' to description first line" / "§Workflow step 3 says 'verify' but not how → spell out the check" / "gate clause is a SHOULD, defect needs MUST"}`
- **Repro**: `{how to re-run this exact probe — command / which pass / which subagent context}`

### FINDING-002: {short title}

- **Severity**: `{...}`
- **Category**: `{...}`
- **Pass**: `{blind | informed}`
- **Probe prompt**: `{...}`
- **Expected**: `{...}`
- **Actual**: `{...}`
- **Transcript evidence**: `{...}`
- **Root cause**: `{...}`
- **Why static review missed it**: `{...}`
- **Location**: `{...}`
- **Suggested fix direction**: `{...}`
- **Repro**: `{...}`

<!-- … add more FINDING-### blocks as needed … -->

## Raw outputs appendix

> This appendix is the **human-in-the-loop surface**. It collects the
> RAW test outputs — not the auditor's distilled verdict — so the user
> can judge what the auditor judged, then steer the fix by talking to
> the main agent. **No embedded feedback form**: the report's job is to
> make that conversation possible (outputs visible) and productive
> (findings already localized + fix-pointed above). The user steers from
> there.

### A. Activation runs (blind pass)

> Each should-trigger / should-NOT-trigger query → fired / didn't, across
> the ≥2 runs. This is the over-trigger / trigger-miss raw evidence.

| # | Query | should_trigger | Run 1 | Run 2 | Verdict |
|---|---|---|---|---|---|
| 1 | `{query}` | `{true \| false}` | `{fired \| didn't}` | `{fired \| didn't}` | `{TP \| FN(miss) \| TN \| FP(over-trigger)}` |
| 2 | `{...}` | `{...}` | `{...}` | `{...}` | `{...}` |

- True-positive (fire when should) rate: `{n/total}`
- True-negative (silent when should-not) rate: `{n/total}`

### B. Cold-reader audit (blind pass)

> The fresh zero-context subagent's verbatim answers to the fixed
> question set (self-contained? trigger hit/miss + unsure cases?
> per-mode procedure executable? undefined terms?).

```
{cold-reader subagent transcript — verbatim}
```

### C. Executor artifacts (informed pass)

> Every artifact the executor subagent actually produced while running
> the skill end-to-end on real/realistic input (forced through the
> cold-start / fallback path). This is what the blind auditor judged.

```
{executor-produced artifact(s) — verbatim, one block per artifact}
```

### D. Executor trajectory (informed pass)

> The executor's steps, not only its final output — so a reader can see
> broken reasoning that a correct-looking output would mask.

```
{executor step-by-step transcript — verbatim}
```

### E. Auditor judgment (informed pass)

> The blind auditor's verdict against the skill's own declared contract +
> the domain-expert bar. Recorded as a DRAFT, not gospel — the user
> closes the LLM-judge blind-spot gap by reading C/D above.

```
{auditor subagent transcript — verbatim, incl. the rubric it applied}
```
