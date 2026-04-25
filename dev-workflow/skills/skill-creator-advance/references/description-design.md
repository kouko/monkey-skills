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
filter at the runtime level. Three implications follow:

1. **Use natural language the user would actually say.** Putting
   "git commit", "open a PR", "merge", "rebase" beats abstract terms
   like "version control operations". Claude's semantic match favors
   the same words a human would speak.
2. **Multilingual keyword belts are belt-and-suspenders.** Claude is
   itself multilingual; an English description matches a 中文 / 日本語
   prompt natively via semantic equivalence. Adding a short keyword
   belt at the end is low-cost insurance, not the primary mechanism.
3. **Front-load the triggers.** Claude Code truncates the combined
   description + when-to-use text at **1,536 characters** per skill
   listing under context-budget pressure. Anything past that gets
   cut. Place the most important trigger phrases in the first ~150
   chars.

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

### 5. Length: aim for 100–250 chars, ceiling at ~500

Empirical data from 14 superpowers SKILL.md descriptions:

- Min 79, median ~107, max 234 chars
- All 14 are well under the 1,024-char Agent Skills spec ceiling
- All 14 are well under a self-imposed ~500-char heuristic the
  superpowers author uses

Long descriptions burn system-prompt context that competes with the
SKILL.md body itself. If your description is over 500 chars, audit
for prose that belongs in SKILL.md `## Overview`, not the metadata.

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
- [ ] Rendered length < 500 chars (audit via YAML parse, not source
      lines)
- [ ] No workflow / process steps ("first do A, then B, then C")
- [ ] No vague filler ("helps with documents", "does stuff with files")
- [ ] If multilingual repo: short keyword belt at end, ≤ 50 chars
- [ ] If close skills exist: explicit negative trigger ("Do NOT use
      for X — use other-skill instead")

## Anti-patterns

| Anti-pattern | Example | Why it hurts |
|---|---|---|
| Workflow recap | "Use for TDD — write test first, watch it fail, write minimal code, refactor" | Claude shortcuts into following the recap instead of reading SKILL.md's actual TDD discipline |
| Mechanism prose | "Capture and retrieve project decision context using git commit messages and PR body as the substrate — a portable, tool-agnostic memory layer that complements Claude Code's native memory" | 100+ chars of HOW that doesn't help discovery; tells Claude the implementation, not when to load |
| First-person | "I can help you process Excel files" | Pronoun inconsistency in system prompt causes selection problems (Anthropic Warning) |
| No triggers | "Generates commit messages." | Claude has to infer when; loses to skills with explicit `Use when` |
| Vague filler | "Helps with documents" / "Processes data" | Matches everything, triggers nothing |
| Trailing keyword salad without context | "git, commit, PR, merge, rebase, diff, stage, branch" | Bare keywords without grammar reduce semantic match quality |
| Bloated multilingual block | A full sentence in each of EN / 日本語 / 中文 | Triples the description length; LLM matches across languages without it |
| Length over 500 chars | A 700-char description | Eats context budget that should belong to SKILL.md body |

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

Changes:

1. WHAT in 6 words (`Capture and recall git decision context`) — outcome,
   not mechanism
2. About-to-violate symptoms front-loaded:
   `about to commit or open a PR` + `before running git commit, gh pr
   create, or staging changes for merge`
3. Read-path symptoms preserved but tightened: `references an old branch`,
   `revisits earlier work without context`
4. Multilingual block compressed from full sentences to a keyword belt
5. Length cut 56% (650 → 287)

## References

- Anthropic Skills docs: https://code.claude.com/docs/en/skills
- Anthropic best-practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Agent Skills spec: https://agentskills.io/specification
- Superpowers `writing-skills`: https://github.com/obra/superpowers
