---
name: a-tool-behaviour-measured-in-one-repo-state-is-not-a-general-fact
description: An external tool's behaviour measured live in ONE repository state and then written down as an unconditional fact is falsified by an ordinary state change — `git cat-file -t <sha>:<gitlink>` exits 128 when the submodule's commit object is missing locally and exits 0 reporting type `commit` after a plain fetch, so a docstring that named the first outcome as "what gitlinks do" mis-stated which branch the code takes; live measurement satisfies the grounding rule and still produces a false claim unless the state it was measured in is named
type: gotcha
origin: Task 2 of the finding-origin-attribution arc (loom-code, 2026-08-02) — four consecutive review rounds, each closing a wrong-and-silent claim, three of them introduced by the edit that closed the previous one
---

Live verification is the strongest grounding source this repo recognises, and
it is what `external-surface-grounding` asks for. It is still not enough on its
own. A command run once answers *what this tool did here, now* — and the
answer can depend on state the observer never looked at.

The measured case: `_show_committed_file` classifies an `origin:` path by
running `git cat-file -t <sha>:<path>` and branching on the type. A submodule
gitlink was measured to exit **128** (`could not get object info`), and that
was written into the docstring as what gitlinks do, with the classification it
implies. A reviewer reran it after an ordinary
`git fetch <subrepo> <branch>:refs/remotes/...` — no exotic config — and got
exit **0** with type **`commit`**. The gitlink's own object had simply become
present in the superproject's object store. Both measurements are correct;
neither is a property of gitlinks. The code was safe either way (both branches
refuse), so nothing failed loudly — the defect was purely in what the prose
told the next reader the code does.

**Why it kept recurring here.** Over four rounds on one task, three
wrong-and-silent claims were introduced by the edit that fixed the previous
one: a decision whose direction contradicted its own stated rationale, a
docstring claiming a durability the mechanism lacked (a per-run marker
described as an accumulating ledger), and this one. The common shape is a
sentence written at the moment of understanding something, asserting more
scope than the observation carried. Fix-time is when this class is born, not
when it is caught.

**How to apply.** When recording an external tool's behaviour, write the state
it was measured in, or write the condition and both outcomes — never the bare
outcome. "`cat-file -t` exits 128 for a gitlink" is a defect; "exits 128 when
the linked commit object is absent from the local object store, 0 with type
`commit` when it is present" is the same measurement, stated truthfully. Then
ask of every neighbouring claim in the same file whether it holds in every
reachable state or only the one you were standing in — the audit is cheap and
it is where the siblings turn up. And when a review round closes a
wrong-claim finding, treat the replacement text as the next thing to verify,
not as the fix: on this arc it was the likeliest place for the next instance.

Same failure family, different axis:
[[evidence-measured-on-one-external-surface-does-not-transfer]] (one surface
of a library says nothing about another surface). See also
[[critic-finding-is-hypothesis-until-code-recon]] for the inverse duty on the
reading side.
