# Memory Conventions

Format spec for commit trailers, PR body `## Memory` section, and
diagram venue. This is the source of truth that protocols and scripts
reference.

## Commit trailers

### Schema (three core + one cross-reference)

| Trailer | Value shape | When to use |
|---|---|---|
| `Decision:` | Why this approach was chosen, 1-3 sentences. May mention alternatives inline. | A non-obvious design choice where the alternative was a real contender |
| `Learning:` | Something discovered during the work that a future reader would want to know. | A surprising constraint, undocumented behavior, or insight worth keeping |
| `Gotcha:` | A specific trap future self or others should avoid. | A failure mode, easy-to-miss edge case, or policy limit hit during the work |
| `Related:` | `PR #<N>` — the PR anchor used for cross-reference | When this change builds on or relates to a prior PR |

All four are **optional**. A typical commit message has none. Memory-worthy
commits (usually 20–30% of commits) add one or more.

### Format rules

- **Placement**: trailers go in the **footer** of the commit message —
  last paragraph, separated from the body by a blank line. Place them
  alongside `Co-Authored-By:`.
- **Naming**: `Hyphenated-Title-Case:` (same family as `Signed-off-by:`,
  `Co-Authored-By:`, `Reviewed-by:`). The key is case-insensitive in
  practice; use this form consistently.
- **Line length**: soft 100 chars, hard 250 chars. Values longer than
  one line use RFC 822 folding — each continuation line starts with at
  least one space:

  ```
  Decision: Chose the two-layer i18n split over a single-policy
    approach because the API surface is natively English while the
    design layer must align with user language.
  ```

- **Multiple trailers of same kind**: repeat the key on a new line.
  Order does not matter.

  ```
  Learning: gws -s is a service filter, not scope specifier.
  Learning: Google Auth Platform UI localizes to ブランディング in JP.
  ```

- **Anchors**: use `Related: PR #<N>` — do not use commit SHAs, which
  get rewritten by rebase. PR numbers are stable.

### Naming notes

- **Do not** use `X-` prefix (RFC 6648 deprecated the X- convention for
  custom headers; git trailers follow the same guidance).
- **Do not** use ALL-CAPS names like `MEMORY:` — only `BREAKING CHANGE`
  earned that exception via the Conventional Commits spec.
- **Avoid** single-word trailer names that clash with email headers
  (`Subject:`, `From:`).

### Good examples

```
refactor(slides-toolkit): i18n — EN-native tech + trilingual design

API surface is natively English, so forcing CJK into technical skills
hurts LLM readability. Design layer, in contrast, benefits from
trilingual anchors to align with the user's spoken language.

Decision: Two-layer i18n split — technical EN-native, design trilingual,
  docs kept in origin language (ZH). The alternative of single-policy
  (full-EN or full-trilingual) was rejected because the two layers have
  fundamentally different language needs.
Learning: Google Auth Platform Console (2025-01 UI refresh) localizes
  to ブランディング / 対象 / クライアント in JP — keep untranslated
  in walkthroughs so users see the same strings.
Gotcha: gws flag `-s` is a service filter, not a scope specifier;
  use `--scopes=<URL>,<URL>` for scope elevation.
Related: PR #135
Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

### Bad examples

```
# Bad: what, not why
Decision: Added new i18n policy.

# Bad: redundant with diff
Learning: Changed 25 files, 2189 insertions.

# Bad: too vague to be useful later
Gotcha: Be careful with scopes.

# Bad: ALL CAPS
MEMORY: Two-layer split adopted.

# Bad: X- prefix
X-Decision: ...
```

## PR body `## Memory` section

The PR body gains one new optional section, placed **after all
Claude Code standard sections** (`## Summary`, `## Test plan`) and
**before the `🤖 Generated with` footer**.

### Layout

```markdown
## Summary                              ← CC standard, untouched
<1-3 bullets>

## Test plan                            ← CC standard, untouched
- [ ] ...

## Memory                               ← git-memory addition, optional
### Decision
<core decision + rationale — may reference rejected alternatives inline>

### Learnings
- <surprise or insight worth keeping>

### Gotchas
- <trap future readers should avoid>

### Architecture                        ← only when arch/flow/state changes
```mermaid
flowchart LR
    ...
```

🤖 Generated with [Claude Code]...      ← CC standard, untouched
```

### Anchor rule

When inserting `## Memory`, locate the line starting with
`🤖 Generated with` and insert one blank line + the Memory section
immediately before it. If that footer is absent (user has disabled
`attribution.pr`), append `## Memory` to the end of the body.

### When to skip

Omit `## Memory` entirely for PRs where the diff is self-explanatory:
dependency bumps, typo fixes, formatting, routine tests-only PRs.
A missing `## Memory` is the correct signal that nothing was memory-worthy.

## Diagram venue

Diagrams reinforce memory of architecture, flow, and state transitions.
Choose the form based on where it will be read.

| Venue | Form | Rationale |
|---|---|---|
| Commit message body | **ASCII only** | GitHub commit view does not render Mermaid; terminal (`git log`, `gh pr view`) shows raw text. ASCII works everywhere. |
| PR body `## Memory → ### Architecture` | **Mermaid preferred** | GitHub renders Mermaid natively (since 2022-02). Fallback to ASCII for very small diagrams (< 4 nodes). |
| Repo docs (`README.md`, `TECH-SPEC.md`, ADRs) | **Mermaid** | Long-lived, rendered by GitHub; exportable to SVG/PNG for docs sites |
| Complex diagrams (class / ER / sequence / gantt / sankey) | **Mermaid only** | ASCII cannot express these cleanly |
| Non-GitHub forge (sourcehut, self-hosted Gitea) | **ASCII** | Mermaid not rendered; ASCII degrades gracefully |

### Decision tree

```
Is this a routine change (typo, bump, format)?
├─ Yes → no diagram
└─ No  → Does the change touch architecture / flow / state?
          ├─ No  → no diagram
          └─ Yes → Where will the diagram live?
                    ├─ Commit body        → ASCII
                    ├─ PR body            → Mermaid
                    └─ Repo docs          → Mermaid
```

### Rule of thumb

- Put the diagram **where its reader will see it rendered**. Commit
  message readers see raw text; PR body readers see rendered markdown.
- When unsure, ASCII is safer — it reads correctly everywhere. Mermaid
  is the specialized tool, not the default.
- Prefix any diagram with a one-sentence prose description for
  accessibility (screen readers cannot parse either form well).

## Line-length philosophy

Commit subject stays at 72 chars (Tim Pope rule). Body wraps at 72
for readability in `git log`. Trailer values can go to 100 chars
(URLs and prose sentences often exceed 72 naturally). Hard cap 250
so `git log --oneline` does not explode.

## Retrieval expectations

These conventions make retrieval cheap, but use **git's own trailer
parser** — do not invent a custom delimiter scheme on top of
`--pretty=format:'%(trailers:...)'`, because trailer values can
contain any character (pipes in shell snippets, colons in prose,
etc.) and will collide with any delimiter you choose.

```bash
# Per commit: extract all memory trailers via git's native parser
git log -1 --format='%B' "$sha" \
  | git interpret-trailers --parse --unfold \
  | grep -E '^(Decision|Learning|Gotcha|Related):'

# All PR bodies with a ## Memory section
gh pr list --state merged --limit 50 --json number,title,body \
  | jq '.[] | select(.body | contains("## Memory"))'
```

**Avoid** patterns like
`git log --pretty=format:'%h|%s|%(trailers:...)'` followed by
`IFS='|' read`, because a trailer value containing `|` (e.g.
`` Gotcha: `wc -l | tr -d ' '` matters here... ``) will split
the record incorrectly. Always round-trip through
`git interpret-trailers --parse`.

See `scripts/memory-grep.sh` for the packaged version.
