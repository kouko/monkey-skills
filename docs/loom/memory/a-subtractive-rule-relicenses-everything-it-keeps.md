---
name: a-subtractive-rule-relicenses-everything-it-keeps
description: A rule that only says what to remove makes no surviving claim safer — every sentence it exempts is re-endorsed by the exemption, and the exempted ones are exactly those that assert something about behaviour and can therefore be wrong; the code-as-spec arc shipped a false docstring inside the fix that kept it, because the rule promoted that sentence from delete to keep-as-interface and nothing then checked it
type: practice
origin: 2026-08-22 code-as-spec-writing-rule arc — round 1 restored a display-name contract as INTERFACE, round 2 found the restored sentence stated the opposite of what the code does, and both round-2 reviewers found it by calling the function while four earlier readings missed it
---

A subtractive rule — delete what the code already shows, drop the dead
config, retire the deprecated call — feels safe because its output is
smaller. It is not safe, and the reason is the exemption clause every such
rule needs.

The code-as-spec rule says prose may not restate what the code shows, then
carves out interface: what a caller needs stays, even when a reader could
recover it from the body. That carve-out is load-bearing and correct.  It
is also the mechanism by which the arc shipped a false claim. A docstring
sentence was reviewed, classified INTERFACE, and rewritten to survive the
cut — and the rewritten sentence said an entry whose `name` disagrees with
its filename stem surfaces under the stem. The code is
`frontmatter.get("name", path.stem)`: the stem appears only when the key is
absent. The sentence was backwards, in the commit that existed to fix a
finding about that same class of defect.

The generalisation: **anything a subtractive rule exempts, it re-endorses.**
Before the rule ran, that sentence was one of many nobody had looked at.
After the rule ran, it carried a reviewer's judgment that it belonged.
Nothing in the rule checked whether it was true, because a rule about what
may be present has no opinion about accuracy. And the exempted set is not
random: a rule that removes restatement keeps precisely the sentences that
assert something about behaviour — the ones with a truth value.

**How to apply.** When writing or reviewing a subtractive rule, ask what it
exempts and what then checks the exempted. If the answer is "nothing", the
rule has moved the risk rather than removed it, and it needs a second half
before it ships: for prose about behaviour, produce the outcome the sentence
names rather than reading it again — see
[[reading-code-and-running-code-fail-differently]] for why reading does not
substitute, and [[a-number-in-prose-needs-a-test-that-recomputes-it]] for the
narrower number-shaped case this generalises. The same question applies to a
lint exemption, a deprecation allowlist, or any "except when" in a policy:
the exception list is where the unexamined survivors accumulate.

Related: [[a-deletion-rule-must-say-the-remainder-still-stands-alone]] is the
other half of the same edit — that one is about whether the remaining text
still reads, this one is about whether it is still true.
