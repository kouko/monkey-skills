# Skill Consistency Check

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Find rules inside a skill package that contradict each other — one
> file requires what another forbids, two limits disagree, or one rule
> forces a step another rule bans.

A user-invoked **checking skill**: point it at a skill folder and it
returns a list of contradictions, each with both sides as file:line, the
quoted text, a confidence level and a one-sentence reason, plus an
overall verdict.

This README is for humans reading the skill on GitHub. The operational
file the agent actually loads is [`SKILL.md`](SKILL.md).

---

## Why does this skill exist?

Contradictory instructions leave an agent that obeys every line with no
correct move in some situation. Authors rarely see them: the two sides
often sit in different files, are worded differently, or only collide
under one condition.

An earlier version translated rules into logic and handed them to an
SMT solver. In blind tests it found 7 of 27 planted contradictions at
about 18% precision — nearly every miss came from the translation step.
Ten rounds of blind experiments then showed that an LLM reading the text
directly does much better, and settled the method used here.

---

## How does it work?

```
skill folder ──► plan_groups.py ──► one group, or several groups
                                          │
             ┌────────────────────────────┴───────────────┐
             ▼                                            ▼
   read-through detectors                   walk-through detectors
   (read and report conflicts)              (act as the agent through
                                             3–5 situations)
             └────────────────────┬───────────────────────┘
                                  ▼
                           merge_report.py ──► verdict + report
```

- **Two detectors**, each an independent subagent: a read-through and an
  execution walk-through. Their specs are in [`references/`](references/).
- **Grouping**: packages up to 30,000 estimated tokens are read whole.
  Larger ones are split into groups of at most 25,000 tokens; every group
  carries SKILL.md, agents/ files and the files SKILL.md cites, and the
  two methods group the rest differently. The report lists file pairs
  that were never read together.
- **Verdict**: "needs revision" only when a high-confidence finding
  exists; medium and low findings are advisory.
- **Side effects**: none. Nothing is installed and nothing is written
  inside the checked folder; reports go to a run directory elsewhere.
  Findings are never auto-fixed.
- **Hosts**: the fan-out is written as "dispatch N subagents", so the
  same SKILL.md runs on Claude Code and Codex. No model is hard-coded;
  use a mid-tier or stronger model (the smallest tier stopped after 1–3
  findings in the experiments).
- **Thorough mode** (opt-in): each method runs twice.

---

## Limits

- Validated on Claude Sonnet (200k context) with packages of about
  25,000 tokens. Other models are not validated; the report says so.
- Conditional contradictions (conflict only under a shared condition)
  and multi-step contradictions (several inference hops) may be missed.
- The regression corpus with answer keys lives in the plugin's
  `tests/consistency-check-corpus/` folder; run it before relying on a
  different model.

---

## When to use

- Before shipping a new or heavily edited skill
- When an agent following a skill behaves inconsistently and you suspect
  the instructions disagree

## When NOT to use

- **Design quality scoring** — use [`skill-judge`](../skill-judge/)
- **Behavioral testing on real prompts** — use
  [`dogfood-skill-testing`](../dogfood-skill-testing/)
- **Folder layout / word-count rules** — the repo's structure checker
  covers those
