# Protocol: Recalling past decisions (pull retrieval)

Recall is **pull, not push**: fetch the few decisions relevant to the
task at hand, on demand — never pre-bake every decision into an
always-loaded file. The point is to stop a future session (you or
another agent) from silently **re-litigating a decision already made
and rejected**. Retrieval runs against the git-memory substrate via
`scripts/memory-grep.sh` (see `standards/memory-conventions.md`
§Pull retrieval for the flags).

## When to recall (triggers)

**① The user asks.** "Why did we…", "為什麼", "what was the reasoning",
or a reference to an old branch / PR / decision. Compose the topic into
a `--match` query.

**② Before non-trivial work in an area.** Before you implement a change
to a file or module, run **one** scoped `--path` recall to surface prior
decisions that touched it. This is the highest-value trigger — it is
exactly what catches "the agent quietly redid something we already
settled."

**③ When weighing an alternative.** While brainstorming or planning,
before you propose an approach, `--match` the approach to check whether
it was already decided or explicitly rejected.

**NOT: broad session-start priming.** Do not dump recent memory into
context at the start of a session "just in case." An unscoped preload is
the push anti-pattern — it bloats context and tends to degrade agent
performance (see `standards/memory-conventions.md` §Pull retrieval).
Recall is always tied to a concrete question or a concrete area.

### Discipline for proactive recalls (② and ③)

- **Always scoped** — `--path=<pathspec>` or `--match=<topic>`, never a
  bare dump.
- **Always capped** — `--top=5` (or so) to bound the context cost.
- **One-shot** — recall once for the area/topic; do not loop or broaden.
- **Empty is a normal result** — `(no memory matches …)` means there is
  no recorded decision. Proceed; do not retry, widen, or treat it as an
  error.

## How to recall

```bash
# ① / ③ — topic recall (keywords → alternation for OR)
scripts/memory-grep.sh --match='single-pass|parser' --top=5

# ② — area recall (which decisions touched this path?)
scripts/memory-grep.sh --path=src/parser --top=5

# ① — full chain including superseded ("what did we used to do, and why
#     did it change?")
scripts/memory-grep.sh --match='parser' --history
```

- **Default is live-only** — superseded decisions are hidden. Add
  `--history` *only* when you specifically want the retire-and-replace
  chain.
- Widen `--since` if you suspect the relevant decision is older than the
  default window (it also resurfaces older supersessions).

## How to use the result

- **A live decision covers the question** → cite it (`PR #N` / subject),
  don't re-derive it. If you intend to go **against** it, say so
  explicitly to the user and treat it as a candidate for a new
  `Supersedes:` (see `protocols/compose-commit.md`).
- **Only superseded decisions match** → the topic was decided *and
  reversed*. Surface both — why it changed — rather than reviving the
  old approach.
- **Empty** → no recorded memory. Proceed. Note that if you now make a
  non-obvious decision here, this is the moment to **record** it.

## Soft link to loom-code (guidance, no coupling)

If `loom-code:brainstorming` or `writing-plans` is running, trigger ③ is
the natural hook: recall each real alternative before proposing it. This
is guidance only — git-memory does **not** modify those skills, and they
do not depend on it.

## Surfacing to the user

Report recalled decisions in the user's language, **point-first** —
"當初選 X 而非 Y，因為 …（PR #N）". Do not paste raw trailer text;
translate and condense. Recall is a lookup in service of the current
task, not a transcript dump.
