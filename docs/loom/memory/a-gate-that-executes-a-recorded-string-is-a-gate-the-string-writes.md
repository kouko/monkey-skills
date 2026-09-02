---
name: a-gate-that-executes-a-recorded-string-is-a-gate-the-string-writes
description: A push gate that runs whatever `command` an agent recorded in review.json is not a gate over the work — it is a gate over the string; four adversarial rounds each reopened it with one token (`true`, a `# comment` naming the artifact, `; true`, a pipeline) until the checker stopped executing recorded strings and ran the artifact file / the declared test command directly, argv-style, no shell
type: practice
origin: simple-loom-flow (2026-09-02) — W1 checkpoint rounds 1–4 on loom_checker.py; the fix that held was ffd9b90a's "execute artifacts and declared commands, never recorded strings"
---

The first design let the checker re-run `probes[].command` "so the result
is observed, not claimed". Every round the reviewer found a one-token
shape that made the string's exit code say nothing about the artifact:
`command: true`; `python3 noop.py  # attack0.py` (substring match on the
artifact name); `python3 attack0.py ; true` (shell exit is the last
segment's). Each patch closed the example and reopened the class.

What held: the checker never executes the recorded string. Adversarial
probes are executed as the artifact FILE, chosen by extension, argv-style;
package tests are executed as the command KICKOFF-DEFAULTS declares. The
recorded `command` is checked for consistency with the artifact
(argv token equality after `shlex.split(…, comments=True)`) and is
otherwise a record. The residual, stated in concept-model §7, is that the
artifact's CONTENT is unconstrained — an empty attack file "passes"; that
gap belongs to the reviewer lens, and is written down as the weakest link.
