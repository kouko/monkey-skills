---
name: a-prose-pin-must-require-an-affirmative-un-negated-sentence
description: A test that pins a contract sentence by keyword co-occurrence is satisfied by the sentence's own negation — "probes are never named test_<unit>_<state>_<expected>; docstrings are in English" passed a probe that looked for the literal plus "English"; the pin must require an affirmative verb before the literal and no negation token in that sentence, and carry synthetic positive and contradictory cases that prove it discriminates
type: practice
origin: 2026-09-05 artifact-language-policy (loom-code 1.3.0) — the same defect was raised on two different pin files in one change (the probe-name probe, then the six station-sentence pins), each time by the Codex reader
---

A pin on prose is tempting to write as "the file contains X and Y". That
predicate is true of the sentence you want and of its exact opposite: a
contract that says the rule *does not* apply contains the same tokens as
one that says it does. Two readers in one change found the same hole
twice, in two files written by two different agents.

**What holds:** split into sentences; the sentence carrying the literal
must contain an affirmative form (`is named`, `must be named`, `are in
English`, `stays in the user's language`) *before* the literal, and no
negation token — `\b(?:not|never|no)\b|n't` on word boundaries, because
`note` and `nothing` are not negations. Then add self-tests that feed the
matcher three synthetic paragraphs: the real sentence (accepted), the
negated one (rejected), the literal with no verb (rejected). The
self-tests are what make the pin reviewable — a reader can see what it
rejects instead of guessing.

**The cost side:** the contract sentences themselves must then avoid
negation words in the qualifying sentence ("rather than" instead of
"not"), which is a small rewording, and a fair one: a rule stated
affirmatively is also the one a cold reader applies correctly.

Related: [[a-narrowing-that-leaves-a-substring-passes-every-containment-pin]],
[[adversarial-fix-must-replace-semantics-not-token]].
