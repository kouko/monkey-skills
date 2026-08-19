---
name: error-message-text-is-not-the-rules-statement
description: A checker's stderr wording gets read downstream as the rule's definition — it is the first statement of the rule anyone sees, and the only one they see at the moment they care — so an error string left behind when the rule changes silently becomes a second, contradicting source of truth that no documentation check covers
type: gotcha
origin: branch plan-field-microstructure (2026-08-19) — a checker's message kept describing a ceiling the rule had already dropped
---

A rule written into a checker has two texts: the rule as stated in its contract
document, and the sentence the checker prints when it fires. Only the second is
read at the moment of violation, by someone who wants to know what they did
wrong and what is allowed instead. That makes the error string a de facto
definition, whatever its author intended it as.

So when the rule changes and the message does not, the two disagree — and the
disagreement propagates in the wrong direction. The author who hits the checker
believes the message, not the contract file they did not open, and writes their
next document to the stale wording. Nothing detects this: prose reviews read
contract documents, tests assert the checker's exit code and often match the
message only as a substring, and the message itself is code, so a docs pass
never reaches it.

**Why:** the failure mode is that the stale text is *usable*. It names a real
constraint that was true recently, so following it produces documents that pass
— they are merely shaped by a rule that no longer exists, and the reason for
their shape is unrecoverable later. This is worse than a message that is simply
wrong and gets reported.

**How to apply:** treat a checker's user-facing strings as part of the rule's
contract surface, not as implementation. Any change to what a rule permits
lists that rule's error strings among the sites to update, alongside the
contract document and its restatements. Pin at least one message whose text
states the *specific* constraint — the number, the permitted forms — so that
changing the rule and forgetting the message goes RED; a pin matching only a
stable prefix will not, and per
[[assertion-must-encode-the-property-it-claims]] that pin must fail on the
message's claim being reversed, not merely on its removal. Related:
[[prose-contract-mechanism-transcribes-from-code]] (the same two texts, kept in
sync from the other direction).
