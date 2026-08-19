---
name: a-prose-literal-assertion-is-false-green-until-it-flattens-whitespace
description: Markdown prose wraps, so a multi-word phrase is usually NOT a contiguous substring of the file. A test asserting such a phrase is absent passes before any edit; one asserting it is present fails for the wrong reason. Both directions are broken, and the failure is invisible — the test is green. Hit three times in one arc (a plan's own acceptance criterion, a router assertion, then that same test's absence checks). Flatten the body with `re.sub(r"\s+", " ", text)` once and assert every literal against the flattened copy; verify each present-assertion is absent beforehand and each absent-assertion is present beforehand.
type: gotcha
origin: think-orbit 0.1.4 transparency arc (2026-08-19) — three independent occurrences across T1's plan, T4's router test, and T4's own review round
---

`silent file writing` does not appear in `using-think-orbit/SKILL.md`. The sentence
is there; it wraps as `…is silent file` / `writing: no forms…`. So the obvious test —
`assert "silent file writing" not in body` — passes on the unedited file, and would
have certified the removal of a sentence that was still sitting there.

The same class appeared three times in one arc, in three different roles:

1. **A plan's acceptance criterion.** The GREEN for a task specified exactly that
   substring check. Caught by the plan reviewer before implementation, which is the
   only reason it did not ship as a green test over unchanged prose.
2. **The implementer's test.** Avoided, because the dispatch warned about it and the
   implementer verified the pattern matched pre-edit before trusting it.
3. **That same test's ABSENCE checks.** The `silent file writing` check used a
   whitespace-tolerant pattern; the three sibling checks asserting the router does
   not restate the warrant duty used plain `in`. Caught by review, which proved it by
   reinserting the forbidden clause with one line-wrap inside it and watching the test
   stay green.

Occurrence 3 is the instructive one: the same function got it right once and wrong
three times, by the same author, minutes apart. Knowing about the trap does not
protect the assertion you were not thinking about — only a uniform rule does.

**Both directions fail, differently.** An absence-assertion silently passes, so the
guard evaporates. A presence-assertion fails, which at least announces itself — but
the fix people reach for is usually to shorten the asserted phrase until it fits on
one line, which weakens the pin instead of fixing the comparison.

**How to apply:**
1. Flatten once per test — `flat = re.sub(r"\s+", " ", body)` — and assert every
   literal, present and absent, against `flat`. Never mix flattened and raw
   comparisons in one function; that asymmetry is what occurrence 3 was.
2. Before trusting a new assertion, check its polarity against the current file: a
   present-assertion must be RED beforehand, an absent-assertion must be GREEN
   beforehand. An assertion that does not change state when you flip the prose pins
   nothing.
3. Mutation-test with the wrap in place, not just the phrase. Reinserting a forbidden
   phrase on one line proves nothing about a checker that will meet it wrapped.
4. Beware substring collisions this creates in reverse: asserting `load-bearing` is
   present matches a pre-existing `non-load-bearing`. Flattening does not fix that —
   use a bounded pattern.

Relates to [[re-multiline-whitespace-captures-across-lines]] (the mirror-image
problem: `\s*` matching newlines makes a pattern too greedy, where this makes a
literal too brittle) and [[a-reader-and-writer-over-one-file-format-must-share-one-parser]].
