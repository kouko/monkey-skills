---
name: a-narrowing-that-leaves-a-substring-passes-every-containment-pin
description: When a change replaces a value with a SUBSTRING of itself — a narrowed form, a stripped prefix, a shortened token — every containment assertion written against the old value stays green, because the new value is still `in` the old text; the stale copy therefore survives review, mutation batteries, and the pin that exists to guard it, and the fix is to change the assertion KIND (exact equality against the shipped source) rather than to tighten the string
type: practice
origin: adjudication-view Japanese-support arc (2026-08-12), fix round — the protocol's ja modality table went stale against `adjudication_profiles.py` and no pin could see it; the drift pin's own first draft had the same bug and passed
---

A fix rewrote every Japanese modality form as a verb-independent suffix:
`してはならない` → `てはならない`, `することが望ましい` → `ことが望ましい`.
The protocol document carries a table transcribing those forms, and that
table is pinned. The table went stale and **every pin stayed green**:

```
shipped form   てはならない
stale table    してはならない
               ^^^^^^^^^^^^ the shipped form is a proper substring
assert form in table_text   →  True  →  green
```

The pin was not weak in the usual way — it named the right file, the
right section, and the right form. It was defeated by the *direction* of
the change: a narrowing cannot break a containment check, because
narrowing only removes characters the check never required.

The implementer's first attempt at a drift pin reproduced the identical
bug and passed. It took writing the assertion as **exact list equality
against `get_profile()`** to make either side fail when it moved alone —
mutating the profile form reddens it, and mutating the table reddens it.

**Why:** containment (`in`, `grep -q`, `assertIn`, "the doc mentions X")
is a one-directional predicate. It can only detect that something was
ADDED or is MISSING ENTIRELY. Any edit whose result is contained in the
old text — a narrowed enum, a stripped affix, a shortened flag name, a
tightened regex, a removed alternative from an `A|B` pattern — is
invisible to it by construction. Reviewers reading a diff also miss it,
because the diff shows the code side changing and the doc side not
changing, which is exactly what a correct "doc unaffected" edit looks
like.

**How to apply:** when a change NARROWS a value that some other artifact
transcribes, containment pins are not evidence — do not read their green
as coverage. Assert the transcription by equality against the shipped
source (parse both, compare structurally), so neither side can move
alone. The tell that you need this: you are about to write a pin whose
mutation test deletes a whole line to prove it fails — deleting proves
nothing about narrowing. Mutate by SHORTENING the value instead, and
watch whether the pin notices; that is the mutation this class requires
(cf. [[a-mutation-test-must-run-the-production-assertion]]).

**Contradiction check:** distinct from
[[substring-assertions-must-pin-the-phrase-their-message-names]], where
the assertion passes because its token ALSO occurs elsewhere in the
guarded text (a collision between the pin and unrelated prose). Here
there is no collision and no second occurrence — the pin matches the one
place it means to match, and is defeated because the new value is
contained in the old one. The remedies differ accordingly: that entry's
fix is to pin a phrase unique to the guarded clause; this entry's fix is
to stop using containment at all. Both are instances of
[[assertion-must-encode-the-property-it-claims]].
