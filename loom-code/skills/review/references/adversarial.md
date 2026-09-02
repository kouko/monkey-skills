# Adversarial — recipes by artifact type, and how to record what ran

The adversary's job is not to find bugs the reviewers might also find. It
is to make the change fail. Everything it runs is recorded, so a later
round can re-run it as a regression.

## Code

**If the repo declares mutation or fuzz tooling** — a `mutmut`,
`cosmic-ray`, `stryker` or fuzz target in its config — run it over the
changed modules and report survivors: a surviving mutant is a test that
asserts nothing.

**If it declares none** (the common case), write **at least three**
executable abuse or boundary cases against the changed behaviour, run them,
and record each one. Three is the floor, not the target. Draw them from:

| Class | The question |
|---|---|
| Empty and absent | zero items, empty string, missing file, unset variable — does it behave, or explode? |
| Boundary | one less, one more, exactly at the limit, the limit plus one |
| Hostile input | wrong type, enormous value, path traversal, injection payload, mixed encodings and non-ASCII |
| Wrong order | the second step called first; the operation run twice; two callers at once |
| Failure of a dependency | the network call fails, the disk is full, the subprocess exits non-zero — is the failure loud, or swallowed? |

Prefer cases that live as real tests afterwards. A case that only ran in
the adversary's head is not evidence.

## Spec

Red-team it: for each `REQ-<n>`, name a behaviour the requirement permits
that the author clearly did not want. Then look for the states the spec
never mentions — the second user, the interrupted run, the empty account,
the migration from what exists today. Each one is a finding with the
requirement as its anchor.

## Skill and gate

Work the six classes in [`attack-catalogue.md`](attack-catalogue.md)
against the file, one attempt per class, and write down what the file made
you do:

- Read the instruction as an agent under time pressure — is there a reading
  that skips the expensive step and still looks compliant?
- Attempt the prose temptations verbatim ("the diff is one line, proceed?")
  and record whether the text refuses them.
- For a gate script, feed it the input it was written to catch, then the
  same input one character different.

An attempt that the file survives is recorded too — that is what makes the
catalogue an eval rather than an anecdote.

## Recording

Every run becomes a `probes[]` entry in `review.json`:

```json
{"kind": "adversarial", "command": "python3 -m pytest tests/test_abuse_empty_input.py -q",
 "sha": "<the sha it ran against>", "result": "pass", "artifact": "tests/test_abuse_empty_input.py",
 "scope": "wave-end:1"}
```

- `command` must be re-runnable by someone else in a clean tree.
- `sha` is the commit tested — for a checkpoint, `HEAD`.
- `artifact` is where the case now lives, so the next round can run it
  again. A probe with no artifact is a one-off.
- `result` is a record only; anything the adversary found that matters
  becomes a `finding` with an anchor and a fix, like any other.
