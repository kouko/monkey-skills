---
name: lexical-overlap-cannot-separate-narrating-from-sharing-a-topic
description: A gate that asks "does this text refer to that other text" cannot be built on shared vocabulary, because the two texts are related — that is why one cites the other — so they share vocabulary by construction. Measured on a real corpus, a keyword-overlap rule passed 10/10 nodes including one whose body referred to none of its three upstream nodes, while requiring an explicit identifier passed 2/10 and matched a human reading of the same corpus exactly. Stoplisting the false matches does not fix it: the class of non-discriminative words is open, and each stoplist entry buys one counterexample. Reach for an identifier the author must actually write, not for evidence that two passages are about the same subject.
type: gotcha
origin: think-orbit 0.1.4 transparency arc, T1 (2026-08-19) — `input-narration` check rule; the keyword arm was specified, built, stoplisted, and then deleted on measurement
---

The rule had to answer: does this node's body explain why it stands on its
upstream, or is the `inputs` edge machine-readable only? The first specification
accepted a shared keyword between the body and the upstream node's `summary`.

Measured against a real project — 10 nodes carrying `inputs` — that arm passed
**10/10**, including a node whose body never referred to any of its three upstream
nodes. The reason is structural, not a tuning failure: **nodes on one reasoning
chain are always about the same topic.** A node about routing shares vocabulary
with its upstream about routing whether or not it narrates it. Topic overlap and
reference are different relations, and lexical similarity only sees the first.

A 27-entry CJK function-word stoplist was added and the same zero-connection match
reproduced immediately on `他們` and `目前`, neither of which was on the list. That
is the shape of the trap: the stoplist closes exactly its named instances, and the
class of generic words is open, so every counterexample buys one more entry and
the rule never becomes discriminative.

Requiring the upstream's `id` to appear in the prose passed **2/10** — exactly the
two nodes a human checkpoint had independently marked as the ones that do narrate.
The identifier is discriminative because an author cannot write it by accident.

**Why this reads as a contradiction of BI-2 and is not:** the same arc's contract
says a body must restate its upstream in prose "rather than cited as a bare `ref`
id". Requiring the id to APPEAR is not requiring a bare citation — the two good
nodes name the id as the subject of a sentence that says what it claimed. What the
contract rejects is an id sitting alone in frontmatter with no prose around it.

**How to apply:**
1. Before building a semantic gate on text similarity, ask what makes the two
   texts similar in the negative case. If they are related documents, they are
   similar for reasons that have nothing to do with the property you want.
2. Prefer an artifact the author must deliberately produce — an id, a link, a
   declared key — over evidence inferred from wording. It is checkable without
   judgment and cannot be satisfied by coincidence.
3. When a filter needs a stoplist to work, the filter is the problem. A stoplist
   is a bet that the excluded class is finite; for natural-language function words
   it is not.
4. Measure the candidate rule against real material before shipping it, and report
   the denominator. A rule that passes everything asserts nothing, and it fails
   silently — `check` prints nothing on a false pass, so nobody notices.

Relates to [[sibling-attractor-makes-lexical-tuning-unstable]] (lexical tuning
being unstable for a different reason — a competing attractor rather than a shared
topic) and [[a-rule-stricter-than-the-corpus-best-human-work-is-miscalibrated]]
(the threshold correction that followed this one).
