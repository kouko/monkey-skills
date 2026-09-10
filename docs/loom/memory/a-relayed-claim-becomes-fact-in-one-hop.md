---
name: a-relayed-claim-becomes-fact-in-one-hop
description: A claim travelling agent→orchestrator→agent loses its provenance at the first hop and arrives as fact — nine times on one branch, twice inside the fix for an earlier instance; tag every relayed claim in the dispatch packet with how it was verified, and never verify a citation by reading
type: gotcha
sources:
  - resource: feat-us-quarterly-statement-series (US quarterly three-statement series arc, 2026-07-29)
---

Across roughly fifteen implementer/review rounds on one branch, **nine** separate
findings were "a cited source does not say what was claimed about it". Zero logic
errors were found in the same period. The dominant defect of multi-agent work on
this branch was not wrong code — it was **confident, wrong provenance**.

Every one of the nine travelled the same three-hop path:

```
subagent asserts X  →  orchestrator relays X in the next dispatch  →  implementer
writes X into an artifact as established fact  →  a later reviewer opens the source
```

The load-bearing hop is the **second**. A reviewer's finding arrives as *"I checked
and X"*; the orchestrator's dispatch packet renders it as *"X"*. That single
reformatting strips the only signal a downstream agent had for deciding whether to
re-check. Nothing lies; the provenance simply evaporates.

Concrete instances, so the shape is recognisable:

- A reviewer reported that a helper used `max(...)` with an `or ""` fallback and
  therefore sorted undated rows first. The helper actually **filters undated rows
  out** and takes a plain `max`. Relayed unchecked; a comment justifying a sort
  direction was written against the false idiom.
- The orchestrator's own dispatch used the phrase *"the SEC's 2005-2008 XBRL
  Voluntary Filer Program"*. That span was never sourced — it was phrasing. It
  landed verbatim in two committed files before two reviewers disagreed about what
  the real span was, which is how anyone noticed it had no source at all.
- A reviewer said *"only one pre-2009 filing was sampled"*. Relayed; written in. The
  same docstring **seventeen lines above** listed four sampled filings. A claim can
  contradict its own file and survive, if nobody re-reads the file.

- Two reviewers independently probed the same SEC index and reported two counts —
  "3,014 index rows" and "96 prior 10-Qs". The implementer re-derived rather than
  relaying and measured **3,287** and **46**; the second reviewer's 96 was *all
  other* 10-Qs, not *prior* ones. Both reviewers had genuinely run a probe. The
  numbers still did not survive being re-run, and only one of the three parties
  re-ran anything.
- A reviewer reported "twelve of the artifact's code citations checked, twelve
  holding". A second reviewer re-audited the same twelve and found one
  mis-attributed. An orchestrator wrote "twelve holding" into a memory entry —
  **this one** — before that second audit landed.

**Twice the defect recurred inside its own fix.** A round flagged an unscoped
absence claim; the round-2 correction introduced a *different* false absence claim.
A round flagged a false precedent citation; the round-2 replacement citation named
a file that does not do the thing claimed (it documents the opposite decision in
its own docstring). A fix round is not a safe round — it is the round where the
author is most confident and least re-reading.

**Why:** an agent has no way to distinguish "the orchestrator verified this" from
"the orchestrator was told this" unless the packet says which. Absent that signal,
the rational default is to trust — the orchestrator is the authority in the
conversation. So unverified claims propagate at full confidence, and each hop makes
them harder to trace back, because the artifact cites the *source* the claim was
about, not the chain the claim actually travelled.

**How to apply:**

1. **Tag every claim you relay, mechanically, in the dispatch packet**:
   `[VERIFIED by me: <the exact command I ran>]` or
   `[RELAYED from <source>, NOT verified — check before using]`. Mechanical because
   it must not depend on remembering to be careful. Evidence it works: once tagged
   claims started shipping in packets on this branch, an implementer re-verified a
   relayed external fact against the primary source unprompted, **and** declined to
   write in a stronger result its own probe had produced, on the grounds that it
   could not ground what the underlying flag meant.
2. **When two reviewers disagree on an external fact, do not pick a side and do not
   supply a third version.** Instruct the artifact to stop depending on the disputed
   fact. A hedge almost never needs the precise date it cites; re-ground it in
   evidence the repo actually holds.
3. **Never verify a citation by reading — verify it by executing the check the claim
   describes.** All nine were caught by opening the file, running the grep, replaying
   the predicate, or building the mutant. None was caught by careful reading, and
   several survived multiple careful readings by different agents.
4. **Treat a fix round as the highest-risk round**, and re-check the replacement
   citation with the same scrutiny the original one failed.

Relates to [[departure-disguised-as-conformance-cites-wrong-precedent]] (the
single-artifact case of the same defect: verify the cited precedent actually covers
your case) and [[cross-module-field-contracts-execute-probes]] (verify the claim
against the artifact, don't take the comment's word). This entry generalises both
to the multi-agent relay path, where the orchestrator is the amplifier.
