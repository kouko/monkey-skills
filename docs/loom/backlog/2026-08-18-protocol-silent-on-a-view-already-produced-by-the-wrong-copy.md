---
name: 2026-08-18-protocol-silent-on-a-view-already-produced-by-the-wrong-copy
description: the adjudication-view delivery gate says what to do about a missing or mismatched stamp, but not about the case a cold dogfood agent actually met — being handed a finished view that a stale copy produced; it inferred the right action from the stated equivalence, which is an inference the protocol does not make
status: open
origin: 2026-08-18 stale-render arc, dogfood probe B — a cold agent given a stale-produced view correctly refused to deliver it, and reported that it had to extend the stated rule to get there
start: next touch of the adjudication-view protocol's §Invocation contract
---

# The protocol is silent on a view already produced by the wrong copy

The shipped delivery gate covers two states: no stamp, and a stamp whose
version does not match. Both resolve to "do not deliver; re-run with the
correct copy; surface if it persists".

The state a cold agent actually met in dogfood was a third one: **a finished
view, handed over by someone else, that a stale copy produced.** It carries
no stamp, so the first rule reaches it — but only if the reader treats
"handed a finished artifact" as the same situation as "just rendered one".

- **Origin**: 2026-08-18 stale-render arc, dogfood probe B — a cold agent given a stale-produced view correctly refused to deliver it, and reported that it had to extend the stated rule to get there
- **Start**: next touch of the adjudication-view protocol's §Invocation contract

## What the cold agent did

Refused, correctly, and named the reasoning as an inference rather than a
citation: it read the stated equivalence between "no stamp" and "mismatched
stamp" and extended it to "no stamp at all, on an artifact I did not
produce" as the most severe member of the same family. It also
independently diagnosed the root cause from the artifact's markup
(`<p class="rendition">`, which only the pre-0.85 template emits).

That is the right answer. The point of this entry is that it was reached by
reasoning, not by reading — and the next reader may reason differently, e.g.
that the rule governs only pages they rendered themselves in this session.

## Fix shape

One sentence in §Invocation contract's "Before delivering an HTML view"
making the gate artifact-scoped rather than session-scoped: the check
applies to any view about to be handed to the user, regardless of who or
what produced it, or when.
