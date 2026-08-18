# Node / Assumption schema

This file documents the frontmatter fields `dag.py`'s `load_project()` reads
from `nodes/`, `assumptions/`, and `research/` files, and the three schema
defaults decided at kickoff.

## Schema defaults (kickoff decisions)

1. **Extraction-driven node granularity** — a node is created per distinct
   claim/fact/goal an agent extracts from a conversation or document, not
   per paragraph or per source file. Granularity is judgment, not a fixed rule.
2. **Multi-role paragraphs** — a single body paragraph may serve more than
   one role (e.g. both explain a claim and cite a source); the schema does
   not force one paragraph = one field.
3. **User-chosen project directory** — the project root (containing
   `nodes/`, `assumptions/`, `research/`) is picked by the user (typically
   inside their own Obsidian vault), never hardcoded or auto-created deep
   inside the plugin.

## Node fields (`nodes/*.md` and `research/*.md`)

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Author-named identifier. Not derived from title or filename. |
| `type` | string | `GOAL` / `FACT` / `CLAIM` / ... A research note always loads as `type: FACT`. |
| `seq` | int | Ordering hint; nodes sort by `seq` then `id`. |
| `inputs` | list | Upstream references. Each entry is `{ref, load_bearing}` or a bare string (then `load_bearing` is `None`, flagged by `check` later). A mapping entry with `load_bearing` set but no (or an empty) `ref` is flagged by `check`'s `ref` rule as `inputs[<i>] has no ref`. |
| `summary` | string | One-line summary. For a research note this is the `claim` field's text. |
| `status` | string | `current` or `stale`. Absent means `current`; a set value outside that pair is flagged by `check`'s `node-status` rule. `break` is what writes `stale`. |
| `branch` | string | Branch id the node belongs to, if any. |
| `branch_type` | string | `exclusive` (the paths compete, one gets chosen) or `complementary` (they coexist and all get weighed). |
| `source` | string | Citation source (mainly on FACT nodes). |
| `quote` | string | Supporting quote (mainly on FACT nodes). |
| `path` | Path | Resolved filesystem path of the file. |

A research note (`research/*.md`) has its own minimal frontmatter (`id`,
`claim`, optionally `source`/`quote`) and loads as a `Node` with
`type == "FACT"` and `summary` set to the `claim` text.

`check`'s `fact-source` rule (missing `source`/`quote`) does not apply to a
research-note FACT node — the note file itself is the source and its `claim`
line is the citable content; the loader marks these nodes with `origin: "research"`
so `check` (and later renderers) can recognize the exemption.

A file whose frontmatter parses to a non-mapping (e.g. a YAML list) or fails
to parse at all (invalid YAML) is not loaded as a node/assumption — it is
recorded as a `"<relpath>: frontmatter: ..."` entry in `Project.problems`.

`check`'s `paragraph-form` rule requires every prose body paragraph of a node
file (`nodes/*.md`, excluding research notes) to contain 2–4 sentences,
matching the vault's own writing convention; the sentence-boundary heuristic
ignores inline code spans and URLs, collapses runs like `...`, and does not
split on common abbreviations (`e.g.`, `i.e.`, `vs.`) or on a small set of
title abbreviations (`Dr.`, `Mr.`, `Mrs.`, `Ms.`, `Prof.`, `St.`, `Jr.`, `Sr.`,
`No.`, `Fig.`, `vs.`, `etc.`) even when the next word is capitalized (`Dr.
Chen`) — except at end-of-text, where the end-of-text rule still ends the
sentence — while a lead-in line followed by a list (no blank line between
them) is counted from its own sentences only.

## Assumption fields (`assumptions/*.md`)

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Author-named identifier. |
| `status` | string | e.g. `open`, `broken`. |
| `statement` | string | The assumption's statement. |
| `breaks_if` | string | Condition under which the assumption breaks. |
| `source` | string | Citation source, if any. |
| `branch` | string | Branch id the assumption belongs to, if any. |
| `path` | Path | Resolved filesystem path of the file. |

`check`'s `assumption-field` rule requires every assumption file to have a
non-empty `id`, `status` (one of `open`, `broken`, `confirmed`), `statement`,
`breaks_if`, and `branch`; a missing field or an out-of-set `status` is
flagged per file. Its `assumption-max` rule caps assumptions per branch at 3
— more than three assumption files sharing one `branch` prints a single
summary line `assumptions: branch <b> has <n> assumptions (max 3)` (not a
per-file relpath, since the violation belongs to the whole branch).

## `render` and `views/dag.md`

`dag.py render <root>` writes `<root>/views/dag.md`: one Mermaid
`flowchart TD` showing every node (shaped by `type`), every assumption as a
stadium node grouped into its branch's subgraph, one edge per `inputs` entry
(dashed when `load_bearing` is false), and a grey `stale` style on nodes
whose `status` is `stale`. The file opens with a generated-marker comment —
it is regenerated from `nodes/`/`assumptions/`/`research/` on every run,
human-only, and must never be hand-edited or read back by an agent.

Author ids are sanitized to a mermaid-safe token (`[A-Za-z0-9_]` only) for
node/subgraph ids; when two different ids sanitize to the same token (e.g.
`a-1` and `a_1`), `render` still keeps them distinct by appending a `_2`,
`_3`, ... suffix to every later one (alphabetical by raw id), and `check`
reports the clash as an `id-collision` violation so it gets fixed at the
source instead of silently living only in the rendered view.

## `impact` and `views/impact-<id>.md`

`dag.py impact <root> <assumption-id>` writes
`<root>/views/impact-<assumption-id>.md` (the assumption id sanitized to
`[A-Za-z0-9_-]` for the filename): a single `flowchart LR` mermaid block
showing that one assumption's blast radius — the assumption as a stadium
node, every dependent reachable via a fully load-bearing chain (`propagate()`)
as a box with the `stale` class when its *current* `status == "stale"`, and
every dependent reachable only through a non-load-bearing hop drawn with a
dashed edge and no `stale` class. Same generated-marker-comment convention
as `render` — human-only, regenerated on every run, never hand-edited or
read back by an agent. `dag.py break <root> <assumption-id>` calls this
renderer itself after propagating stale/weakened status, so breaking an
assumption always refreshes its impact view; an unknown assumption id
prints `assumption <id> not found` to stderr and exits 1 without writing
any file (both `break` and `impact`).

## Minimal examples

### Node — `nodes/goal.md`

```markdown
---
id: goal
type: GOAL
seq: 1
summary: Ship v0
status: current
---
Longer body text explaining the goal.
```

### Assumption — `assumptions/q4_budget_holds.md`

```markdown
---
id: q4_budget_holds
status: open
statement: Q4 budget will not be cut
breaks_if: Budget cut announced
source: finance team
branch: b1
---
Optional body with more detail.
```

### Research note — `research/r1.md`

```markdown
---
id: r1
claim: Competitor X raised prices last quarter
source: press release
---
Optional body with supporting detail.
```
