# Protocol: Grounding Research

**When to use**: a skill needs primary-source grounding — either
because it's new or because gap assessment in `skill-redesign.md`
phase 1 surfaced load-bearing claims without citations.

**Output**: a list of standards files to draft, each with its
authoritative primary sources identified, plus a Japanese integration
decision.

Grounds on: `../standards/grounding-principle.md`.

## Phase 1: Define Research Questions

Translate the grounding gap into concrete questions research-team can
answer. Each question should target a specific claim cluster.

Good question shapes:
- "What is the authoritative taxonomy for {domain concept}?"
- "What are the primary sources that define {framework}?"
- "How does the {global / Anglo-American} canon treat {topic}?"
- "Are there parallel Japanese community traditions for {topic}?"

Bad question shapes:
- "What are best practices for X?" — too vague, no primary source
  anchor
- "What does Claude think about X?" — you're asking for hallucination
- "What do people on Stack Overflow say?" — not primary sources

Aim for 2–5 research questions per grounding task. More than 5 and
research-team will lose focus.

## Phase 2: Launch research-team

Use the `research-team` deep research workflow:

```
### Task
Ground {team-name} in primary sources for {topic area}.
Research questions: {list from phase 1}.

### Resource Paths
(research-team's own resources — skill-team doesn't pass them)

### Input
output_language: {user's language}
```

research-team produces a research report that passes:
- Source Citation gate (MUST) — every factual claim cited
- Research Quality rubric (SHOULD) — depth and source authority

If research-team returns `NEEDS_REVISION` or `BLOCKED`, do NOT
proceed — escalate to the user.

## Phase 3: Research Note Capture

Save the research report **in-repo by default** under the skill's
optional `research/` subdirectory:

```
domain-teams/skills/{team-name}/research/grounding-v{X.Y.Z}.md
```

where `{X.Y.Z}` is the plugin version that will land the grounding
work (for example, `grounding-v4.8.0.md` for design-team's v4.8.0
refactor). See `file-conventions.md` §Directory Semantics and
§Research Subdirectory Convention for the full rules:

- One file per grounding event; no dates in filename (dates are in
  git log and frontmatter)
- ASCII-only filename; CJK content goes in the file body
- File is maintainer-facing; NOT read by worker/evaluator at runtime
- Not listed in SKILL.md Resource Manifest or launch templates
- Exempt from Diátaxis single-quadrant rule (research notes are
  fundamentally mixed-mode)

The in-repo location makes research part of the PR review, ensures
the audit trail survives session compaction and machine changes, and
lets reviewers see the "why" behind primary-source choices alongside
the grounding changes themselves.

### File content

Preserve the full research artifact: cluster-by-cluster source
verification, research questions with cited answers, claim → source
mapping tables, JP integration decision with evidence, open
questions. Mirror the structure of prior grounded team research notes
(see `qa-team/research/grounding-v4.2.0.md`,
`docs-team/research/grounding-v4.3.0.md`,
`code-team/research/grounding-v4.6.0.md` for reference shapes).

Required frontmatter:

```yaml
---
title: {team-name} 再設計研究 — {topic}
date: {YYYY-MM-DD}
team: {team-name}
refactor_version: v{X.Y.Z}
tags: [research, domain-teams, {team-name}, grounding]
---
```

### Opt-in Obsidian export (user directive only)

Obsidian vault export is **opt-in**. If — and only if — the user's
skill-team invocation contains an explicit directive, ALSO write a
copy to the user's Obsidian vault under the legacy convention path
`research/{YYYY-MM-DD} {team-name} grounding — {topic}.md`.

**Directive trigger phrases** (multilingual, accept any):

- English: `also save to Obsidian`, `also export to Obsidian`,
  `and to Obsidian`, `Obsidian copy`
- 日本語: `Obsidianにも保存`, `Obsidianにもエクスポート`,
  `Obsidianにもコピー`
- 繁體中文: `也存到 Obsidian`, `也複製到 Obsidian`,
  `也輸出到 Obsidian`
- 简体中文: `也存到 Obsidian`, `也复制到 Obsidian`

If no Obsidian directive is present, write **only** the in-repo
file. Do not prompt the user to ask — silence means repo-only.

If an Obsidian directive IS present but the Obsidian vault location
is not discoverable (no `*.obsidian` vault found in expected paths),
log a note in Phase 6's grounding plan ("Obsidian export requested
but vault not found — in-repo copy only") and continue. Do not
block the refactor on Obsidian availability.

## Phase 4: Standards Synthesis

For each cluster of related findings, plan one standards file:

```
{authoritative-name}.md
Purpose: {what claims this standard anchors}
Primary sources: {2–5 URLs / book citations}
Estimated length: {60–140 lines}
Load-bearing claims covered: {list}
```

Standards should be single-topic. If findings span two topics, split
into two standards files.

Typical output from phase 4 is a plan listing 3–6 standards to write.

## Phase 5: Japanese Integration Decision

Apply the content-density rule from `../standards/grounding-principle.md`:

| Evidence | Strategy |
|----------|----------|
| Research surfaces a named Japanese tradition with published authors and methodologies parallel to the Anglo canon | Full integration — standards file in JP + protocol phases reference JP methodologies |
| Research surfaces JP principles or philosophical framings (not full framework) | Preamble only — JP quote or principle as ground anchor in persona |
| Research surfaces no JP parallel tradition | Explicit note — add a "Note on Global Context" section declaring no JP overlay |

Document the decision AND the evidence behind it. Future reviewers
should see why this call was made.

## Phase 6: Produce the Grounding Plan

Output a structured plan:

```markdown
## Grounding Plan for {team-name}

**Research source**: `domain-teams/skills/{team-name}/research/grounding-v{X.Y.Z}.md` (in-repo, default)
**Obsidian export**: {none | path to Obsidian copy if user requested opt-in export}

**Standards to create** (for commit 1 of skill-redesign / new-skill-creation):
1. {standard-name}.md — primary sources: {list}
2. ...

**JP integration decision**: {full | preamble | none}
**JP evidence**: {one-sentence justification}

**Load-bearing claims now grounded**:
- {claim 1} → {source 1}
- {claim 2} → {source 2}
- ...
```

This plan feeds directly into `new-skill-creation.md` phase 3 or
`skill-redesign.md` phase 4.

## Rules

- If research-team can't find primary sources for a claim, that claim
  should NOT become load-bearing in the new skill. Reword it out.
- Always prefer books and published standards over blog posts, even
  authoritative blogs.
- The JP integration decision must be backed by research evidence,
  not personal preference.
- One grounding-research run ≠ one skill refactor. The same research
  may support multiple skill updates over time.

## Anti-Patterns

- ❌ Skipping research-team and inventing "primary sources" from
  training data recall
- ❌ Citing blog posts that themselves cite the primary source
- ❌ Running research-team with no specific questions ("research
  testing best practices" — too vague)
- ❌ Using the research output without reading it — you must
  understand the sources before synthesizing standards
- ❌ Forcing JP integration because "it would look balanced"
