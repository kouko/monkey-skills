---
name: an-assertion-scoped-wider-than-its-clause-is-about-something-else
description: A test that searches a whole file for a phrase belonging to one paragraph passes while that paragraph is deleted, because the phrase survives somewhere else in the file — the assertion is not weaker than its name, it is about a different subject; scope every assertion to the smallest text that is the claim's actual home, and prove the scope by deleting the clause rather than by reading the code
type: gotcha
sources:
  - resource: 2026-09-11, memory-timing arc — four instances in one review episode, one of them written inside the commit that fixed the previous one; each found by mutation, none by reading
---

Four times in one closing review, the same defect, each time in a test that
looked obviously correct:

1. A clause pin searched `SKILL.md` **and** its reference copy. The shipped
   contract could be rewritten end to end and the pin stayed green, because
   `references/operations.md` still carried every phrase.
2. An inertness guard selected the paragraph containing one anchor phrase.
   The passage had two paragraphs. A plugin name and a gate marker were
   added to the second with every test green.
3. An assertion pinned `"functional content"` against the whole station
   file. That phrase occurs four more times there, so the sentence the test
   was named for could be replaced outright, green. **This one was written
   in the same commit that fixed instance 1.**
4. The property of the mechanism itself was restated in six documents.
   Correcting it in two left four asserting the old thing.

**Why it is invisible.** The assertion is not vacuous — remove the phrase
from every occurrence and it fails. It is not tautological. It fails for a
real reason when it fails. What is wrong is the *subject*: the test's name
says "the passage states X" and its body says "this file contains X". Those
are different claims, and a review reads the name.

**Why writing the negative case finds it and reading does not.** Instance 1
surfaced while writing a probe meant to prove something else entirely — the
probe deleted the clause from the shipped file, expected red, and got
green. Instances 2 and 3 surfaced when a reviewer performed the mutation by
hand. In all three the positive case had been green from the start and told
nobody anything. A green assertion is evidence only about the text it
actually read.

**How to apply.**
1. Every assertion about a clause is scoped to the clause's **home** — the
   section, the paragraph, the passage — never to the file that contains it.
   Extract that scope into one helper and route every assertion through it,
   so the scope is a single decision rather than eleven.
2. Prove the scope by mutation, not by reading: delete the clause from its
   home only, leaving every other occurrence intact, and watch the test go
   red. If it stays green the test is about something else.
3. When a claim is restated in more than one document, give it one home and
   make the others describe outcomes instead. Copies do not stay correct;
   they stay until someone corrects the original.
4. Treat a second instance as a class, not a coincidence. Instance 3 was
   written by the same hand that had just fixed instance 1, in the same
   commit, because the fix was applied as a patch to one site instead of as
   a rule about scope.

Related: [[a-prose-literal-assertion-is-false-green-until-it-flattens-whitespace]]
— the mechanical prerequisite, and the same failure family: an assertion
that reads something other than what its author believed. Also
[[a-prose-pin-outlives-its-prose-only-if-it-explains-itself]] and
[[a-red-anchor-can-go-stale-from-an-earlier-tasks-own-text]], where a
sibling task's prose supplies the anchor instead of a sibling paragraph.
