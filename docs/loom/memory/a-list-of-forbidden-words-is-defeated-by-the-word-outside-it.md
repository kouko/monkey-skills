---
name: a-list-of-forbidden-words-is-defeated-by-the-word-outside-it
description: A check that enumerates the words a rule forbids — runner names, disclaiming phrases, imperative verbs, marker tokens — is defeated by the first word nobody listed, and extending the list buys one round before the next word arrives; the remedy is to change what the check works on (a syntactic feature, a sentence or list-item boundary, a negation bound to its own object, or a guard that makes the unsanctioned shape unwritable), and a sweep that hunts instances by inspection reports itself clean while leaving siblings the next reviewer finds
type: practice
origin: goal-create arc (2026-08-27) — the same defeat recurred seven times across four files and five review rounds: an unlisted test runner (`k6`), an unlisted Japanese phrasing (会話に貼り付ける), an unlisted imperative verb (`Spin up`), an unlisted English stop word (`Halt`), an unlisted synonym (`obligates`), and twice a negation matched to a word further along the sentence; one instance was written by the very fix commit that closed the previous one
---

Every mechanical check on that arc that named the tokens a rule forbids
was beaten by a token outside its list, usually within one review round.
The lists were not careless — each was written from the real vocabulary
in front of its author. The defeat is structural: the set of ways to say
a forbidden thing is open, and the list is closed.

Four remedies worked, all of them changing the axis rather than the
vocabulary:

- **A syntactic feature instead of a vocabulary.** "Verification quotes a
  command in backticks" survives an unknown runner; "Verification names
  one of these runners" does not.
- **A structural scope instead of a distance.** Splitting on sentences or
  list items caught an injected instruction that a ±200-character window
  let ride on unrelated nearby text — and stopped failing compliant prose
  that had merely moved.
- **A negation bound to its own object.** `\bnot\b.*\btrue\b` is
  satisfied by *"need **not** be checkable … it is fine if it is already
  **true**"*, which states the opposite of the rule it guards.
- **A guard that makes the shape unwritable.** A test reading its own
  file's source and failing on the unsanctioned pattern ends the class,
  because it fires when the next instance is written rather than when the
  next reviewer looks.

**Why:** hunting instances converges slowly and reports done early. On
that arc each manual sweep declared the file clean and each left a
sibling — the mechanical guard, added after the fourth sweep, immediately
found three more the sweeps had missed. Deletion beat bounding twice: a
masking mechanism narrowed three times, each round fixing the reported
input and opening another, and removing it ended the class outright.

**How to apply:** when a check needs a list of forbidden words, treat the
list as the defect and look for the feature, boundary, or binding the
rule actually depends on. When the class has already recurred once, stop
fixing instances and add the guard — then say plainly what the guard
cannot catch, because a guard with unstated gaps is the same trap one
level up. That guard must itself be proven by mutation: the first version
written on this arc matched nothing and looked correct, because a regex
literal's `\b` is the two characters backslash and `b`, so searching a
pattern's *source* for a word boundary never fires.

Same remedy family as
[[a-narrowing-that-leaves-a-substring-passes-every-containment-pin]] —
change the assertion's kind, not its string. Related:
[[a-dispatch-packets-own-wording-becomes-the-artifacts-defect]], because
a packet that hands a worker a vocabulary hands it the defect too.
