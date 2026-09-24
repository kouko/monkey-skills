# Contradiction detection spec

You receive an agent-skill PACKAGE: several markdown files an AI agent follows
together (SKILL.md is the entry point; the others are loaded from it). Find places where the package contradicts itself — within one file or ACROSS
files — where an
agent that obeys every instruction literally could not satisfy all of them in
some situation the document itself describes.

Read exactly the files in the list you are given (one group, or the whole
package) — no other files — and write your output to the path you are given.

## Counts as a contradiction

- Direct: one place requires an action, another forbids the same action (possibly
  reworded), with overlapping scope.
- Conditional: two rules conflict only under a shared condition, which may be
  phrased differently in each place.
- Chain: following one rule necessarily entails something another rule forbids,
  possibly over several steps. State every step.
- Numeric: two different values/limits for the same quantity in the same scope.

## Does NOT count

- Rules whose scopes do not overlap (different modes, different phases,
  different targets) — check scope before reporting.
- A general rule plus an explicitly stated exception.
- Soft preference vs hard rule where the document says which wins.
- Quoted examples of bad practice, rationale text, or headings.
- Vagueness, style issues, missing information, or things you would design
  differently. Report only conflicts that exist in the text.

Precision matters as much as recall: every report is shown to a maintainer who
must act on it. When unsure, report it with confidence `low` rather than drop it.

## Method: execution walk-through (follow this procedure)

1. Pick 3–5 concrete situations the document itself describes: the normal run,
   each fallback/degraded path it names, and any edge case it mentions.
2. For each situation, act as the agent: walk through the instructions in the
   order the document gives them, keeping a running log of what you have done,
   what you have produced (and what it contains), and what you are currently
   forbidden to do.
3. Report every point where the next instruction cannot be followed without
   breaking an earlier or later one, or where a required input cannot exist yet.
   Put the walk-through steps that lead there in `steps`.

## Output

Write a JSON file at the path you are given:

```json
{"findings": [
  {"id": "F1",
   "type": "direct|conditional|chain|numeric",
   "confidence": "high|medium|low",
   "side_a": {"file": "SKILL.md", "lines": [12], "quote": "verbatim fragment"},
   "side_b": {"file": "references/x.md", "lines": [240, 241], "quote": "verbatim fragment"},
   "steps": ["for chain: each inference step, citing file:line"],
   "why": "one or two sentences: the situation in which both cannot hold"}
]}
```

`file` is the path relative to the package root. Line numbers are 1-based,
within that file, and must be exact (use a tool that shows line
numbers). An empty `findings` list is a valid answer.
