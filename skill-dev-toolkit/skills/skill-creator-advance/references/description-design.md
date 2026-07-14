# Description Design Reference

Deep-dive guidance for the `description` field in SKILL.md frontmatter.
Skill discovery — whether Claude loads your skill at all — hinges
almost entirely on this field. Length budget is generous (1024 chars
per the Agent Skills spec, 1536 chars in Claude Code listings before
truncation), but well-designed descriptions are typically much shorter
(~100–200 chars in production skills).

## How skill discovery actually works

Skill name + description are pre-loaded into the system prompt at
session start, wrapped inside the Skill tool's metadata. Claude
decides which skill to invoke via a **forward pass** — semantic match
against the description, not a regex / fuzzy-string / vector-embedding
filter at the runtime level. Practical implications surface in
§Six principles below (natural keywords, multilingual belt,
front-loading under the 1,536-char Claude Code listing truncation).

## The Anthropic-vs-Superpowers tension (resolved)

Two authoritative sources appear to conflict:

| Source | Rule | Status |
|---|---|---|
| Anthropic Skills docs (`code.claude.com/docs/en/skills`) | "Include both **what the skill does and when to use it**" | Three official examples (PDF / Excel / git-commit-helper) all begin with the WHAT clause |
| Anthropic best-practices (`platform.claude.com`) | Same — "should include both what and when" | Mandates third-person (Warning block) |
| Agent Skills spec (`agentskills.io/specification`) | "Should describe both what the skill does and when to use it" | Open-standard; max 1024 chars |
| Superpowers `writing-skills` | "Description = **When to use, NOT what the skill does**" | Author Jesse Vincent's defensive heuristic |

**Resolution**: the conflict is between two *different* phenomena.

- **WHAT (outcome)**: a brief end-state summary — "Generate descriptive
  commit messages from staged diffs". Anthropic-approved. Tells
  Claude what the skill produces so it knows when to reach for it.
- **WORKFLOW (steps)**: a process recap — "Write test first, watch it
  fail, write minimal code, refactor". Superpowers correctly warns
  against this — when the description summarizes the workflow,
  Claude can shortcut into following the description instead of
  reading SKILL.md's actual content. The body becomes documentation
  Claude skips.

**Rule of thumb**: include WHAT (one sentence outcome) but never
WORKFLOW (process steps). Anthropic's examples obey this distinction;
so do roughly half of superpowers' own 14 skills (e.g.
`using-git-worktrees` opens with a what-clause: "creates isolated
git worktrees…").

When to apply Superpowers' stricter "only-when, no-what" rule:

- Your skill's behavior is fully expressible in 1–2 sentences AND
  reading the description could let Claude bypass important steps
  in SKILL.md. This is rare. Most skills have side-effects that
  require following the SKILL.md body — the description summary
  cannot fake-execute them.

## Six principles

### 1. Front-load with `Use when …` (or include WHAT then `Use when`)

Both patterns work. Pure trigger:

```yaml
description: Use when implementing any feature or bugfix, before writing implementation code
```

WHAT + WHEN (Anthropic style):

```yaml
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

Avoid descriptions that only describe WHAT with no trigger ("Generate
commit messages from diffs.") — Claude has to infer when to invoke,
and inference loses to other skills with explicit triggers.

### 2. Third-person, never first/second-person

Anthropic best-practices doc has an explicit Warning block on this.
The description is injected into the system prompt; pronoun
inconsistency causes selection problems.

```
✓ Processes Excel files and generates reports
✗ I can help you process Excel files
✗ You can use this to process Excel files
```

### 3. Include "about-to-violate" symptoms

The most discoverable trigger is the moment **just before** the user
takes the action that bypasses your skill's guidance. Examples from
superpowers:

| Skill | About-to-violate symptom |
|---|---|
| test-driven-development | "before writing implementation code" |
| systematic-debugging | "before proposing fixes" |
| writing-plans | "before touching code" |
| requesting-code-review | "before merging" |
| verification-before-completion | "about to claim work is complete… before committing or creating PRs" |
| brainstorming | "before any creative work" |

The pattern is `Use when [situation], before [action]` or
`Use when about to [action]`. This catches the pre-action moment
where loading the skill is actually useful — after the action, the
skill is too late to help.

For a skill whose rule is "capture context before X happens", name X
explicitly: `before running git commit`, `before merging`,
`before deploying`, `before deleting tests`.

### 4. Use natural keywords the user would actually type

Claude's matcher favors direct lexical overlap on natural English
verbs and nouns. Prefer:

- `git commit` over `version control commit operation`
- `open a PR` over `initiate a pull request creation workflow`
- `pivot table` over `cross-tabulation analysis`

Skill authors over-formalize their description's vocabulary. The
matcher does not care about elegant phrasing; it cares about word
overlap with the user's prompt.

### 5. Length: two-tier standard (single number authority)

This section is the repo's number authority for description length.
It supersedes `docs/skill-mining/2026-06-19-skill-description-standard.md`
(see the dated note at the top of that doc).

- **Normal skills**: target ≤150 chars; 250 is a SOFT lint line (not
  a hard cap). A normal skill MAY exceed the soft lint line when a
  colocated YAML justification comment directly above `description:`
  names the retained trigger surfaces that make ≤250 unachievable
  (same comment mechanism as the router firing-evidence note below);
  unjustified >250 remains the violation.
- **Router / CONDITIONAL skills**: exception band ≤500, admission
  REQUIRES a firing-evidence note (cite a corpus run or live A/B) —
  no evidence, no exception. A NEW router/CONDITIONAL skill with no
  firing evidence yet stays within the normal band until a corpus or
  live A/B run supplies the note; only then does the ≤500 band open.

Harness facts: Agent Skills spec max 1,024 chars; Claude Code listing
truncation 1,536 chars (combined description + when_to_use).

Provenance of the old 250 figure: it descends from a Claude Code
listing cap introduced in v2.1.86 and RESCINDED in v2.1.105 (raised
to 1,536) — recorded here so the number never re-fossilizes as a
hard cap.

Industry calibration (n=88 shipped skills, measured 2026-07-14):
medians 106 (obra/superpowers) / 156 (mattpocock) / 304 (anthropics
official) / 339 (planning-with-files).

Long descriptions burn system-prompt context that competes with the
SKILL.md body itself. Over the soft lint line, audit for prose that
belongs in SKILL.md `## Overview`, not the metadata.

### 6. Multilingual keyword belt (optional)

For repos that operate in mixed languages, a short keyword belt at
the end is low-cost insurance:

```yaml
description: Capture and recall git decision context. Use when about to commit or open a PR ... Triggers: commit / PR / 為什麼 / コミット.
```

But: zero of the 14 superpowers skills use multilingual belts.
Claude semantic-matches across languages without it. The belt's
marginal benefit is small but its cost (a few chars at the end)
is also small — include it if your repo's prompts are routinely
non-English; skip it otherwise.

## Token economy: three cutting rules

Principle 5 says HOW MUCH; these rules say HOW to cut. Framing:
model-invoked descriptions cost **context load** — every description
is re-paid in the system prompt each session, whether or not the
skill fires. User-invoked (slash-command) skills cost **cognitive
load** — the human must remember they exist; the cure for cognitive
load is a router skill, not a longer description. Decide what a
description must carry by which currency it spends.

1. **One trigger per branch.** Each distinct routing branch gets one
   trigger phrase. Piling variant phrasings onto the same branch is
   duplication — it buys no new routing, only chars.
2. **Synonyms = duplication.** An English synonym of an existing
   trigger adds cost, not recall — the matcher already covers it
   semantically. Carve-out: Principle 6's multilingual keyword belt
   (中/日 trigger words) is NOT synonym-duplication — different
   languages are distinct routing surfaces; keep them.
3. **Cut identity already in the body.** The body loads on
   activation, so the description must not restate what the skill
   IS when the body says it. Budget goes to WHEN / triggers.
   Principle 1's one-sentence WHAT is exempt — identity restatement
   means anything beyond that one-liner.

Rules ported from Matt Pocock's `mattpocock/skills` repository,
`writing-great-skills` (MIT License, © 2026 Matt Pocock).

## Length is rendered, not source

YAML's `>-` (block-folded with chomp-strip) joins newlines with
single spaces and trims trailing whitespace. The character count
that matters is the **rendered** string Claude sees in the system
prompt, not the source file's line count × line width.

```yaml
description: >-
  Line one of source.
  Line two of source.
```

renders to: `Line one of source. Line two of source.` (39 chars,
not 2 lines of ~20).

When auditing length, parse the YAML and `len(data["description"])`.

## Validation checklist

Before shipping a description, verify:

- [ ] Starts with `Use when …` OR with a one-sentence WHAT clause
      followed by `Use when …`
- [ ] Third-person (no "I", "you", "we")
- [ ] At least one "about-to-violate" symptom for skills that
      should fire pre-action (`before X`, `about to X`)
- [ ] At least one concrete natural-language trigger keyword the
      user would actually type
- [ ] Rendered length per Principle 5 two-tier standard: ≤150 target,
      250 soft lint line; router/CONDITIONAL exception ≤500 only with
      firing evidence (a NEW router with no evidence yet stays in the
      normal band; audit via YAML parse, not source lines)
- [ ] No workflow / process steps ("first do A, then B, then C")
- [ ] No English synonym pairs among triggers — one trigger per
      routing branch (multilingual belt keywords exempt)
- [ ] No identity restatement the SKILL.md body already carries
      (Principle 1's one-sentence WHAT is exempt)
- [ ] No vague filler ("helps with documents", "does stuff with files")
- [ ] If multilingual repo: short keyword belt at end, ≤ 50 chars
- [ ] If close skills exist: explicit negative trigger ("Do NOT use
      for X — use other-skill instead")

## Worked example: git-memory v0.1.0 → v0.1.5

The `git-memory` skill went through a description rewrite that hit
several of the principles above. Useful as a concrete reference.

### Before (650 rendered chars, 0 write-path triggers)

```yaml
description: >-
  Capture and retrieve project decision context using git commit messages
  and PR body as the substrate — a portable, tool-agnostic memory layer
  that complements Claude Code's native memory. Use when the user wants
  to record why a decision was made, surface past decisions in a new
  session, or make project knowledge survive across machines and tools
  (Claude Code / Cursor / Codex / aider / human collaborators).
  Also use when the user says "why did we do this", "record this
  decision", "what did we learn", "git memory", "portable memory".
  Git コミット・メモリ。可攜式プロジェクト記憶。可攜式專案記憶。
```

Audit:

| Issue | Detail |
|---|---|
| Mechanism prose front-loaded | First 100 chars are entirely HOW ("using git commit messages and PR body as the substrate — a portable, tool-agnostic memory layer") |
| Read-path only | Triggers like "why did we do this" are recall-side; missing all write-path triggers (`commit`, `PR`, `gh pr create`) |
| 6× the median superpowers length | 650 vs ~107 |
| Bloated multilingual block | Full sentences in three languages instead of a keyword belt |

### After (287 rendered chars, both paths covered)

```yaml
description: >-
  Capture and recall git decision context. Use when about to commit or open
  a PR (before running git commit, gh pr create, or staging changes for
  merge), or when recalling why a past decision was made (user asks "why
  did we do X", references an old branch, or revisits earlier work without
  context). Triggers: commit / PR / merge / decision / 為什麼 / commit メモ / 決定記録.
```

The Before / After diff shows the audit applied: WHAT clause replaces
mechanism prose; about-to-violate symptoms front-loaded; multilingual
sentences compressed to a keyword belt; length cut 56% (650 → 287).

## Observation: diagrams as a thinking aid (n=4, indicative not authoritative)

Empirical pattern noted across the monkey-skills development sessions
that produced this reference: drafting a Mermaid flowchart for a
proposed design / workflow has, on multiple occasions, surfaced
relationships the prose form had left implicit — merge points,
feedback loops, asymmetric data flows, parallel-then-converge
patterns. Once. Then again. Then twice more.

Hypothesized mechanism (not confirmed): writing a structured DSL
forces explicit naming of every node and every edge. Implicit
relationships in prose ("...and then it joins back up with...")
become drawn lines in Mermaid. The act of writing the diagram, not
viewing the rendered output, is where the surfacing happens — which
matters because LLMs reading the source file process Mermaid as
text, not visually. The constraint is the cognitive aid, not the
picture.

This is **not a rule**. n=4 in one project's sessions is too small
to generalize. But for high-stakes design work, drafting a Mermaid
flowchart before finalizing — even if the diagram never ships — is
a cheap discipline. Re-evaluate as a stronger recommendation if the
pattern is observed across ≥3 independent projects / authors.

Until then, treat this as a developer's note: when a design feels
"almost right" but you can't articulate why, try writing it as
Mermaid before shipping prose. The act may surface what's bothering
you.

## Trigger eval query design (moved from SKILL.md body)

Used by the Description Optimization workflow — SKILL.md's Step 1 keeps
the JSON shape and the 20-query mix; this section is the query-writing
craft.

### How triggering gates on task complexity

Skills appear in Claude's `available_skills` list with their name +
description, and Claude decides whether to consult a skill based on that
description. The important thing to know is that Claude only consults
skills for tasks it can't easily handle on its own — simple, one-step
queries like "read this PDF" may not trigger a skill even if the
description matches perfectly, because Claude can handle them directly
with basic tools. Complex, multi-step, or specialized queries reliably
trigger skills when the description matches.

This means your eval queries should be substantive enough that Claude
would actually benefit from consulting a skill. Simple queries like
"read file X" are poor test cases — they won't trigger skills
regardless of description quality.

### Query realism

The queries must be realistic and something a Claude Code or Claude.ai
user would actually type. Not abstract requests, but requests that are
concrete and specific and have a good amount of detail. For instance,
file paths, personal context about the user's job or situation, column
names and values, company names, URLs. A little bit of backstory. Some
might be in lowercase or contain abbreviations or typos or casual
speech. Use a mix of different lengths, and focus on edge cases rather
than making them clear-cut (the user will get a chance to sign off on
them).

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

### Should-trigger queries (8-10): coverage

Think about coverage. You want different phrasings of the same intent —
some formal, some casual. Include cases where the user doesn't
explicitly name the skill or file type but clearly needs it. Throw in
some uncommon use cases and cases where this skill competes with
another but should win.

### Should-not-trigger queries (8-10): near-misses

The most valuable ones are the near-misses — queries that share
keywords or concepts with the skill but actually need something
different. Think adjacent domains, ambiguous phrasing where a naive
keyword match would trigger but shouldn't, and cases where the query
touches on something the skill does but in a context where another
tool is more appropriate.

The key thing to avoid: don't make should-not-trigger queries obviously
irrelevant. "Write a fibonacci function" as a negative test for a PDF
skill is too easy — it doesn't test anything. The negative cases should
be genuinely tricky.

## References

- Anthropic Skills docs: https://code.claude.com/docs/en/skills
- Anthropic best-practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Agent Skills spec: https://agentskills.io/specification
- Superpowers `writing-skills`: https://github.com/obra/superpowers
