---
name: using-think-orbit
description: |
  Entry point for think-orbit — turn a decision discussion into a transparent chain of thought (one file per reasoning node, a regenerated DAG view), detect where the project stands, and route to decision-session or break-assumption. Fires on 我要決定 / 決策推演 / 用 think-orbit / 繼續上次的決策 / "help me decide" / "think-orbit".
source_language: en
tags: [decision-making, chain-of-thought, dag, router, part-1-draft]
---

# think-orbit — entry point

## What this is

think-orbit turns a decision discussion into a transparent chain of
thought. Each reasoning step you take with the user lands as one small
markdown file under `nodes/`, the premises a path stands on land under
`assumptions/`, and a regenerated view at `<root>/views/dag.md` is what
the user opens to see the whole graph. Three weeks later they can still
find which premise the conclusion rests on.

The family contract is **three kinds of interrupt** — you confirm the
GOAL, you ask for the assumptions each time a branch opens, and you
confirm each DECISION with the owner. Everything else is silent file
writing: no forms, no per-node confirmation, no progress narration. The
`decision-session` skill enforces this contract; state it here once and
do not re-explain it in conversation.

## Intake — once per project

Ask for the project directory `<root>` the first time, and only the
first time. It is a folder the user owns, typically inside their
Obsidian vault. Never invent a path, never create one inside the plugin,
and never guess from a previous project.

Sources are **local paths**. If the material lives in Notion, Google
Drive, or another external service, the user reaches it through their
own connectors or MCP servers — this plugin does not fetch it. Ask them
to point at a local file or paste the content.

## State detection — at every entry

Run this before you say anything substantive.

1. If `<root>/nodes/` is absent or empty → this is a **new decision**.
   Skip to routing.
2. Otherwise run the gate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py check <root>
```

On pass it prints nothing and you say nothing. On failure it prints one
line per violation — relay only the failures, in plain words, and fix
the files before continuing.

3. When `<root>/research/` exists **and** `<root>` is inside a git repo,
   also run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py claims <root> --since HEAD
```

Each output line has the shape
`<research-id>: claim changed → dependents: <node ids>`. Relay it as
"these conclusions moved, and these nodes depend on them". If the folder
is not a git repository the command says so — skip it silently, that is
not an error the user needs to hear.

## Resume opening — when nodes already exist

Open with one short paragraph, then hand over. Restate the last
DECISION (the `summary` of the DECISION node with the highest `seq`, or
"no decision yet"), then the open assumptions (`status: open`, by `id`
and `statement`), then any changed claims from the step above. Do not
narrate the whole graph, do not re-list every node, and do not ask a
question in this paragraph — the next thing the user says decides the
route.

## Routing

| The user … | Route to |
|---|---|
| starts a new decision, or wants to keep analysing an existing one | `decision-session` |
| says an assumption broke, the situation changed, 「假設破了」/「情況變了」 | `break-assumption` |
| asks for the mainline or per-branch view, a compiled proposal, or milestone git commits | Say plainly: "Part 2 — not yet." Do not improvise a substitute. |
| asks to see the graph | Tell them to open `<root>/views/dag.md`; regenerate it first with `dag.py render <root>` if nodes changed since the last render |

**You never read any file under `views/`.** It is a derived, lossy view
for the human. When you need graph structure, recompute it from the
frontmatter of `nodes/`, `assumptions/`, and `research/`.

## Files and verbs

| Path | What lives there |
|---|---|
| `<root>/nodes/` | one file per reasoning step — GOAL / FACT / CLAIM / DECISION |
| `<root>/assumptions/` | the premises a branch stands on, each with `breaks_if` |
| `<root>/research/` | standalone research notes; dependents reference the `claim` line |
| `<root>/views/` | rendered views — **human-only**, never read by you |

Every verb has the same shape:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py <verb> <root> [args]
```

| Verb | Meaning |
|---|---|
| `check <root>` | structural gate; silent on pass, one line per violation on failure |
| `break <root> <assumption-id>` | mark an assumption broken and propagate stale/weakened status downstream |
| `claims <root> --since HEAD` | research claims that changed since a git revision, with their dependents |
| `render <root>` | write `views/dag.md`, the full DAG view |
| `impact <root> <assumption-id>` | write `views/impact-<id>.md` for one assumption |

## Pointers

- `${CLAUDE_PLUGIN_ROOT}/skills/decision-session/references/node-schema.md` — field SSOT for node and assumption frontmatter
- `${CLAUDE_PLUGIN_ROOT}/skills/decision-session/references/research-rules.md` — when to verify, and how a fact enters the graph
- `${CLAUDE_PLUGIN_ROOT}/skills/decision-session/references/blind-spot-checklist.md` — offered once, when a branch opens
- Verb skills: `decision-session` (the sitting protocol) and `break-assumption` (the break and propagation flow)
