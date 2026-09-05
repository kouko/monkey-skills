---
name: a-prompt-that-may-start-with-a-dash-goes-on-stdin
description: A prompt handed to a command-line tool as a positional argument is parsed by that tool's option parser first, so any prompt that can begin with `-` — every Markdown file with YAML frontmatter begins with `---` — must travel on stdin, and a unit test that fakes the subprocess never sees the rejection; only a real invocation against a real input does
type: gotcha
origin: 2026-09-04-adversary-three-way-attribution-measured — wave-end:1 blind run (2026-09-05); both readers reproduced it independently
---

The cold-read measurement script fed a contract file inline as the value
after `claude -p`. Every agent contract in this plugin opens with YAML
frontmatter, so the prompt began with `---` and the CLI's option parser
rejected it as an unknown option before any network call. The script's
unit tests monkeypatched `subprocess.run` and were green; the blind
runner's first real call against the real contract returned nothing but
`unparsed`. Two other delivery forms were tried once each: `--`
end-of-options made the CLI ignore the prompt entirely, and stdin
delivered a `---`-leading prompt intact.

**Why:** a fake subprocess reproduces the interface the caller imagined,
not the parser the real binary runs. The failure sits exactly in the gap
the fake papers over, so the whole suite can be green while the tool
cannot process its only real inputs.

**How to apply:** when a script hands free text to another program, send
it on stdin (`subprocess.run(argv, input=text, ...)`) or through a file
argument, never as a positional argv item; keep the argv free of user
content so the transcript's command line can be recorded without the
text. Pair the mocked tests with one real smoke invocation against a
real input in the blind run, and ground the invocation in a checked-in
capture of the tool's `--help` — but say what that capture does and
does not show (it does not document stdin reading; that stays an
empirical observation). Related: [[a-failed-call-is-a-non-observation-not-a-wrong-answer]].
