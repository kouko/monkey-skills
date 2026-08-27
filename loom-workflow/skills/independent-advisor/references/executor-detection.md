# Static executor detection — procedure and exclusion reasons

Static detection answers two questions per candidate executor, and nothing
else: **is its binary present and runnable on this host**, and **is there a
credential file for it that can actually be read**. It runs before the user is
asked anything, it costs nothing, and it sends nothing off the machine.

Static detection never establishes that an executor works. Its only output is
a candidate record whose status is either an exclusion reason, or the label
**statically available, not yet verified**.

## The procedure

Run the checks in order and **record what it printed** for each — the printed
line, or the empty output plus the exit status. A check you did not run has no
result; do not fill it in from what you expect the host to have.

Per candidate:

1. **Is the binary on PATH?** Run the candidate's lookup command, e.g.
   `command -v codex` for Codex, or `command -v claude` for Claude Code.
   Record the printed path. Empty output → `binary-missing`.
2. **Is that path executable?** Run `test -x <the path step 1 printed>` and
   record the exit status. Non-zero → `binary-not-executable`.
3. **Does the credential file exist?** Run `ls -l <the candidate's credential
   path>` and record the printed line. For Codex the credential file lives
   under the user's Codex home — `ls -l "${CODEX_HOME:-$HOME/.codex}/auth.json"`.
   If that host uses a different location, use the location the host actually
   documents and record which path you checked. "No such file" →
   `credential-missing`.
4. **Is the credential file readable and non-empty?** Run
   `test -r <path> && test -s <path>` and record the exit status. Non-zero →
   `credential-unusable`. A file that reads but whose content cannot be parsed
   in the format the executor expects is also `credential-unusable`.

A candidate that clears all four steps is recorded as
**statically available, not yet verified**.

An executor the host runs with no credential file at all — a locally hosted
model, or one whose credentials come from the environment rather than a file —
skips steps 3 and 4. Record which steps were skipped and why; do not record a
skipped step as a pass.

## The four exclusion reasons

They stay distinguishable because they carry four different fixes. Collapsing
them into "unavailable" hands the user a dead end instead of a next action.

| Reason | What was observed | What the user does about it |
|---|---|---|
| `binary-missing` | Step 1 printed nothing | Install the executor, or add it to `PATH` |
| `binary-not-executable` | Step 1 printed a path, step 2 exited non-zero | Fix the file's permissions on that path |
| `credential-missing` | Step 3 found no file at the checked path | Log in / authenticate to create it |
| `credential-unusable` | Step 3 found the file, step 4 failed or it could not be parsed | Fix permissions on it, or re-authenticate to rewrite it |

Record the reason together with the command and its printed output, so the
refusal the user receives at the checkpoint can quote the evidence rather than
assert a conclusion.

## Worked record shape

```
executor: codex
static_status: excluded
exclusion_reason: credential-missing
evidence: 'ls -l "${CODEX_HOME:-$HOME/.codex}/auth.json"' printed
  "ls: .../auth.json: No such file or directory"
```

```
executor: claude
static_status: statically available, not yet verified
evidence: 'command -v claude' printed "/usr/local/bin/claude";
  'test -x /usr/local/bin/claude' exited 0;
  credential check exited 0
```

The second record is **not** a capability claim. Whether that executor answers
at the requested tier is settled only by the live probe, and only for an
executor the user selected at the checkpoint.

## The live probe — procedure

The probe consumes the candidate record above: the executor identifier, its
static status, and its exclusion reason if any. Probe only a candidate whose
static status is **statically available, not yet verified** AND whom the user
selected at the checkpoint.

### Invocation shape

Send one minimal prompt and read what the executor prints about itself. The
shape below is a starting point, not a settled fact: it is what was observed on
`codex-cli 0.149.1`. Flags and their names change between CLI versions, so on a
different version treat it as a hypothesis to re-check against the header, not
as something to trust:

```
codex exec --sandbox read-only --skip-git-repo-check \
  -c model_reasoning_effort=<level> "reply with the single word ok" < /dev/null
```

Each piece earns its place:

| Piece | Why it is there |
|---|---|
| `--sandbox read-only` | The probe gets no write access to this host |
| `--skip-git-repo-check` | Outside a trusted directory the run is otherwise refused |
| `< /dev/null` | A prompt passed as an argument still hangs with stdin left open |
| `-c model_reasoning_effort=<level>` | Asks for the effort you want back in the header |

Use the same three properties — read-only, runnable where you are, stdin
closed — for any other executor, in that executor's own flags.

### Read the header, not the shell

The effective model and effort are whatever the executor prints back, never
what the flags asked for. That header is the evidence, and this is what
protects the probe against flag drift: if a flag is renamed or silently
ignored on some other CLI version, the header stops carrying the value you
asked for and the probe fails, instead of quietly running at the wrong tier.

The header looks like this:

```
--------
workdir: /some/path
model: <model name as printed>
provider: <provider as printed>
reasoning effort: <effort as printed>
--------
```

Record the printed model as `verified_model` and the printed reasoning effort
as `verified_effort`. If either line is absent from the header, the probe did
not verify that executor — a zero exit status does not substitute for it.

### Traps

- **The pipeline trap.** `<probe> | tail -20` exits with `tail`'s status, so a
  failed probe reads as a success. Capture the output to a file or a variable
  and read the probe's own exit status; never judge through a pipe.
- **The hang trap.** With stdin left open the run waits even though the prompt
  was passed as an argument. Close it with `< /dev/null`.
- **The repo-check trap.** Outside a directory the executor trusts, the run is
  refused rather than answered; skip the repo check as above.
- **A run that never returns** is recorded as a probe failure, never as a pass.
