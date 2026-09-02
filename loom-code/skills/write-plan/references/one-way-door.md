# One-way doors

A one-way door is a choice that is expensive or impossible to undo later.
It is asked **because of what it is**, not because the agent judged it
hard: no judgement call decides whether to ask. A judgement-shaped fork
(three or more trade-offs where the choice changes what gets delivered) is
also put to the user — but, like every one-way door, it is merged into a
decision point that already exists, never into a new stop of its own.

## The five classes

Any one of these makes it a one-way door:

- **(a) Hard to swap later** — framework, language, database,
  authentication method, hosting platform, package manager.
- **(b) Creates money or a standing obligation** — paid services,
  third-party APIs that need an account, infrastructure someone must
  maintain.
- **(c) Limits what the user can do in future** — data formats, export
  ability, platform lock-in.
- **(d) Sets the ceiling on output quality** — recognition or generation
  model, algorithm, data source, when the candidates differ noticeably on
  an axis the user feels (accuracy, speed, cost per run, language or
  format coverage, privacy): any such axis differing by ≥ 20%, or the
  presence versus absence of money, privacy or coverage. Purely internal
  differences (memory, line count, maintainability) do not count.
- **(e) An irreversible action on the user's existing state** — rewriting
  or deleting the user's data in place, changing an existing file format
  with no backup, sending the user's data off their machine. This one is
  asked **even when there is no fork at all** and only one way to do it: a
  blind run happens in a clean environment, so it structurally never
  touches existing data, and asking is the only thing that stops the harm.

## The four gates, in order

1. **Check first.** If the intent's Acceptance or Constraints, or
   `PRINCIPLES.md`, already pins that axis — do not ask. Pick the option
   that complies and say which line pinned it.
2. **Measure first.** If the candidates can be compared quickly on the
   user's own sample, measure, then ask about the result. Ask about
   outcomes, never about assumptions.
3. **Threshold.** Apply the significance test in class (d). Below it, the
   choice is the agent's.
4. **Merge.** All the one-way doors of one change are asked **once**,
   inside a decision point that already exists — ① for engineering, ② for
   product. Never open an extra stop.

## The consequence form

Every one-way door is asked in this shape, with no mechanism vocabulary in
it:

> Option A: from then on it only runs on ___, it costs ___ per month, and
> swapping it out means rewriting ___. Option B: ___. I suggest A,
> because ___.

Where there is no fork — class (e) — the same shape states the consequence
and the safeguard:

> This will rewrite your ___ into a new format and the old program will not
> read it. I will keep a backup at ___ first. Is that OK?

The answer goes into the spec's `## Design decision`, marked
`user-decided`.

## After the decision point has closed

A door that only surfaces later does **not** reopen the conversation. Pick
a default, mark it `agent-decided — <one-line reason>`, and list it in the
blind-run report's "I decided for you" section, which is what decision
point ③ reads.

For classes **(b), (c) and (e)** that default is not free. Take the
zero-obligation, reversible option that touches no existing data, and
record `agent-decided — not authorised, took the conservative option`.
Choosing a committing option unasked is never allowed.
