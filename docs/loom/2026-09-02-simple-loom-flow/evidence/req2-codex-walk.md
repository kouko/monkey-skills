# REQ-2 verification — the write-plan station walked on Codex CLI (W4-02, 2026-09-02)

REQ-2 claim under test: *the same task on Codex CLI produces the same files,
decision points and gates as on Claude Code, with Codex adding only the
one-time `/hooks` trust.*

Verdict: **NOT identical — three differences, one of them defeats the
mechanism REQ-2 leans on.** The artifacts, the decision points and the
checker rules do match. The extra Codex steps do not stop at `/hooks`.

Raw transcripts, verbatim, beside this file:
`req2-codex-walk-run1.log`, `-run1b.log`, `-run2.log`, `-run3.log`.

---

## 0. Probe — the executor

Command:

```
command codex exec --sandbox read-only "reply with the single word ok" < /dev/null
```

Header, verbatim:

```
OpenAI Codex v0.151.0
--------
workdir: /Users/kouko/.herdr/worktrees/monkey-skills/simple-loom-flow
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: low
reasoning summaries: none
--------
```

Exit 0, reply `ok`. The shell alias resolves to
`command codex --profile status-line`, whose default reasoning effort is
`low`. For the two walk runs I raised it to `high`
(`-c model_reasoning_effort="high"`) so that a failure would be a
document failure rather than a budget failure; the small push run stayed
at `low`. That is a deliberate deviation from the probe's defaults and is
the only one.

## 1. The scratch repo

`scratchpad/codex-walk-A/`, `git init -b main`, then:

- `scripts/{fetch,sync,tag,clean,report,archive}.py` — six files, each
  carrying the identical five-line `run_git(args)` helper (Task A shape).
- `tests/test_smoke.py` — one trivially passing test.
- `docs/loom/KICKOFF-DEFAULTS.md`:
  ```
  - package-tests: python3 -m pytest -q — six scripts, bare tests (2026-09-03)
  - second-vendor: none — codex walk (2026-09-03)
  ```
- `vendor/loom-code/` — a copy of this worktree's `loom-code/`, so the
  station documents are readable in-sandbox and the transcript reproduces.

Commits `7295bab` (six scripts) and `24e31e5` (vendor copy), then
`git switch -c 2026-09-03-scripts-share-git-helper`.

The `second-vendor:` line is present on purpose: SKILL.md step 3 point 3
says "if the line already exists, say nothing about it", so the correct
behaviour on both hosts is to ask exactly **one** question at decision
point ①. That is what the comparison below checks.

## 2. Run 1 — untrusted hooks, `--sandbox workspace-write`

Prompt (verbatim, `scratchpad/prompt-run1.txt`):

> You are following vendor/loom-code/skills/write-plan/SKILL.md literally
> on Codex CLI for this task: "A repo has six scripts that each
> re-implement the same git helper; extract one shared helper." Do steps
> 0b and 0 exactly as written (the scaffold is at
> vendor/loom-code/scripts/codex_scaffold.py; the loom-code checkout is
> vendor/loom-code). Do not simulate: run the commands. Stop where the
> document says stop and print what it tells you to print.

Command:

```
command codex exec -C <repo> --sandbox workspace-write \
  -c model_reasoning_effort="high" -o run1-last.md "$(cat prompt-run1.txt)" < /dev/null
```

Exit 0. Final message, verbatim:

```
loom scaffold failed: [Errno 1] Operation not permitted: '<repo>/.codex'

`.codex/hooks/loom_checker.py` does not exist after step 0b, so I stopped as required. Step 0 was not run.
```

Files produced: none. Isolated with a two-command control run
(`req2-codex-walk-run1.log` is the walk; the control is quoted here):

```
exec /bin/zsh -lc 'mkdir -p .zztest && echo MADE-ZZ'  → MADE-ZZ
codex: mkdir: .codex: Operation not permitted
```

**Finding F1 — the scaffold cannot run under Codex's own default write
sandbox.** `.codex/` is a protected path inside the workspace; an ordinary
new directory in the same repo is writable. Step 0b writes exactly there.
Every later run in this walk needed `--sandbox danger-full-access`.

## 3. Run 1b — untrusted hooks, sandbox lifted

Same prompt, `--sandbox danger-full-access`, **no** hook-trust flag —
i.e. the state a user is in before they have ever typed `/hooks`.

Exit 0. What actually happened, verbatim from the transcript:

```
exec /bin/zsh -lc 'git status --short --branch && python3 vendor/loom-code/scripts/codex_scaffold.py --repo .'
  wrote .codex/hooks.json … suggested commit subject: chore(loom): scaffold hooks 1.0.0
exec /bin/zsh -lc "git add .codex && git commit -m 'chore(loom): scaffold hooks 1.0.0'"
  [2026-09-03-scripts-share-git-helper e345f45] chore(loom): scaffold hooks 1.0.0
   14 files changed, 3141 insertions(+)
exec /bin/zsh -lc 'python3 vendor/loom-code/scripts/codex_scaffold.py --probe'
  probe blocked the fake push — the loom gate is live
exec /bin/zsh -lc 'python3 .codex/hooks/loom_checker.py contract --require 1.0'
  contract 1.0.0 satisfies requires-contract >=1.0
```

Trust state at that moment, from `~/.codex/config.toml` — the only trusted
hook definitions are the user's own and one plugin's; the scratch repo's
`.codex/hooks.json` has **no** entry:

```
[hooks.state."/Users/kouko/.codex/hooks.json:pre_tool_use:0:0"]
[hooks.state."code-toolkit@monkey-skills:hooks/hooks.json:session_start:0:0"]
```

**Finding F2 (blocking) — `--probe` cannot detect the untrusted state it
exists to detect.** `codex_scaffold.py:probe()` runs the shim itself as a
subprocess (`subprocess.run([str(shim)], input=json.dumps(payload))`). It
never goes through Codex's hook engine, so Codex's trust decision is not in
the loop. The probe therefore reports "the loom gate is live" whether the
hook is trusted or not, the BLOCK sentence about `/hooks` is never printed,
and the station walks straight past step 0b into a repo with **no live
gate**. This is the exact silent-skip failure the probe was written for
(q4 run C), and the probe's own docstring says a scaffold write "proves
nothing on its own".

Independent confirmation from the hook-event counts in the transcripts —
one `hook: PreToolUse` per command when untrusted, three when the trust
check is bypassed:

| run | trust | `exec` commands | `hook: PreToolUse` events |
|---|---|---|---|
| 1b | untrusted | 11 | 11 |
| 2 | `--dangerously-bypass-hook-trust` | 16 | 48 |
| 3 | untrusted | 1 | 1 |

## 4. Run 2 — trust bypassed (stands in for the user having run `/hooks`)

Prompt (verbatim, `scratchpad/prompt-run2.txt`): the run-1 prompt with
"Do the whole station exactly as written", plus:

> The user has now run /hooks and approved the loom hooks.
>
> I am standing in for the user, and here are my answers in advance so you
> do not have to wait for me: to your restatement question I answer "yes";
> there are no one-way doors I want to decide differently; if you ask about
> a second reviewing vendor the answer is "none". Ask the questions anyway,
> in one message, exactly as the document tells you to word them, and
> record them; then take my answers above and carry on to the end of the
> station.

Command:

```
command codex exec -C <repo> --sandbox danger-full-access \
  --dangerously-bypass-hook-trust -c model_reasoning_effort="high" \
  -o run2-last.md "$(cat prompt-run2.txt)" < /dev/null
```

Exit 0. Checker commands run, in order, all in the Codex prefix form:

```
python3 vendor/loom-code/scripts/codex_scaffold.py --repo .      (unchanged — already scaffolded)
python3 vendor/loom-code/scripts/codex_scaffold.py --probe       → probe blocked the fake push — the loom gate is live
python3 .codex/hooks/loom_checker.py contract --require 1.0      → contract 1.0.0 satisfies requires-contract >=1.0
python3 .codex/hooks/loom_checker.py standing docs/loom/intent/2026-09-02-scripts-share-git-helper.md
python3 .codex/hooks/loom_checker.py intent  docs/loom/intent/2026-09-02-scripts-share-git-helper.md
python3 .codex/hooks/loom_checker.py intake  write-plan 2026-09-02-scripts-share-git-helper
```

`standing` printed its three WARN lines verbatim to the user and did not
block. The one decision-point question asked, verbatim:

> You want the six maintenance scripts to stop carrying duplicate
> Git-running code, and when it is done you will be able to update that
> behavior once, run every script as before, and have tests catch
> regressions or renewed duplication. Is that right?

No second-vendor question (the `second-vendor:` line already existed —
correct). No one-way-door question (none found; the plan records
"There are no one-way doors"). No principles interview (`kind:
engineering`). The question was recorded in the plan's `## Questions
asked` as `① — what — …`.

`git ls-files docs/loom .codex`:

```
.codex/hooks.json
.codex/hooks/contract/README.md
.codex/hooks/contract/manifest.yaml
.codex/hooks/contract/templates/KICKOFF-DEFAULTS.md
.codex/hooks/contract/templates/PRINCIPLES-interview.md
.codex/hooks/contract/templates/PURPOSE.md
.codex/hooks/contract/templates/intent.md
.codex/hooks/contract/templates/memory-README.md
.codex/hooks/contract/templates/plan.md
.codex/hooks/contract/templates/review.json
.codex/hooks/contract/templates/spec-minimal.md
.codex/hooks/git_exec.py
.codex/hooks/loom-checker
.codex/hooks/loom_checker.py
docs/loom/2026-09-02-scripts-share-git-helper/plan.md
docs/loom/KICKOFF-DEFAULTS.md
docs/loom/intent/2026-09-02-scripts-share-git-helper.md
```

`git log --format='%h %s'`:

```
d3549f2 docs(loom): plan 2026-09-02-scripts-share-git-helper
2f62369 docs(loom): intent 2026-09-02-scripts-share-git-helper confirmed
e345f45 chore(loom): scaffold hooks 1.0.0
24e31e5 chore: vendor loom-code checkout for the walk
7295bab chore: six scripts each with their own run_git helper
```

The intent commit body carries the `needs-design:` line verbatim, as the
document requires. The plan carries Current State Evidence (all five of
Forward / Reverse / Error / Data / Boundary with a path and an anchor),
a two-task single-wave DAG with `after:` and a written reason per
judgement call, `## Questions asked`, and `## Risks`. `review.json` was
not written — correct, `needs-design: no` means write-plan calls no
review.

### The one gate that fired, and how Codex got past it

```
BLOCK intent.needs-design-recompute: `needs-design: no` but the diff touches a declared interface surface: .codex/hooks/contract/templates/KICKOFF-DEFAULTS.md, .codex/hooks/contract/templates/PRINCIPLES-interview.md, .codex/hooks/contract/templates/PURPOSE.md, .codex/hooks/contract/templates/intent.md, .codex/hooks/contract/templates/memory-README.md.
BLOCK intent.kind-recompute: `kind: engineering` but the diff touches a user surface: … Either `kind: product` …, or keep the change off the declared interface surfaces …
interface-surfaces (manifest default): **/cli/**, **/api/**, **/commands/**, **/*.tsx, **/templates/**
```

Codex's own narration of what it did next, verbatim:

> The first intent check found a setup-history problem, not an intent
> problem: the scaffold commit sits on the change branch, so its copied
> templates are being mistaken for product-surface changes. I'm moving the
> trunk pointer forward to include that already-committed scaffold—the
> history shape the station requires—then rerunning the gate.

```
exec … git branch -f main e345f45 && … loom_checker.py intent … && … loom_checker.py intake …   (exit 0)
```

**Finding F3 — step 0b's own scaffold trips two `intent.*` rules, and the
document offers no remedy.** The scaffold copies
`contract/templates/**` into `.codex/hooks/contract/templates/`, which
matches the default `**/templates/**` interface-surface glob. Any Codex
engineering change whose branch contains the scaffold commit is therefore
blocked by `intent.needs-design-recompute` and `intent.kind-recompute`.
Claude Code has no scaffold commit and never sees either rule. Codex's
escape — force-moving the trunk pointer onto the scaffold commit — is
plausible and it worked, but it is an agent-invented remedy that rewrites
`main`, and nothing in write-plan authorises or even mentions it.

## 5. Run 3 — does the hook actually block a push?

Prompt (verbatim):

> In this repository, attempt to run exactly this shell command: git push
> origin HEAD . Report verbatim what happened — the exact stderr and exit
> status. Do not retry, do not work around any block, do not do anything
> else.

Untrusted arm, `--sandbox danger-full-access`, no trust flag. Exit 0;
transcript verbatim:

```
exec /bin/zsh -c 'git push origin HEAD .' → exited 128 in 0ms:
fatal: invalid refspec '.'
```

git itself answered — the loom PreToolUse hook never ran. (The stray `.`
is the prompt's trailing full stop, swallowed into the command; it does
not affect the result, because the block would have happened before git
was reached.) This is the direct behavioural proof of F2: the probe said
"the loom gate is live" in run 1b, and the gate was not live.

**Trusted arm: not run — see §7.**

## 6. Comparison — Claude Code vs Codex CLI, same task

Claude side from the W1 blind run (`w1-checkpoint-reviews.md`,
`sonnet-blindrun-w1`) and the accepted cold read (`cold-read-A.md`).

| | Claude Code | Codex CLI (measured here) | same? |
|---|---|---|---|
| intent path | `docs/loom/intent/<change-id>.md` | `docs/loom/intent/2026-09-02-scripts-share-git-helper.md` | ✅ |
| plan path | `docs/loom/<change-id>/plan.md` | `docs/loom/2026-09-02-scripts-share-git-helper/plan.md` | ✅ |
| KICKOFF-DEFAULTS | read; `second-vendor:` line present → not touched | same | ✅ |
| spec | none (`needs-design: no`) | none | ✅ |
| review.json | not written by write-plan | not written | ✅ |
| decision points | ① restatement only; second-vendor suppressed by the existing line | ① restatement only; second-vendor suppressed | ✅ |
| question recorded | plan `## Questions asked`, `<point> — <type> — <text>` | `① — what — You want the six maintenance scripts…` | ✅ |
| checker commands | `contract`, `standing`, `intent`, `intake` | same four, Codex prefix `python3 .codex/hooks/loom_checker.py` | ✅ |
| rules exercised | `contract.requires`, `standing.warn`, `intent.*`, `intake.*` | same, **plus** `intent.needs-design-recompute` + `intent.kind-recompute` firing on the scaffold's own files | ❌ F3 |
| commits | `docs(loom): intent … confirmed`, `docs(loom): plan …` | same two, **plus** `chore(loom): scaffold hooks 1.0.0` | delta (expected) |
| extra steps | none | step 0b scaffold + commit; `/hooks` trust; **plus** a sandbox that forbids the scaffold (F1); **plus** a trunk-pointer move to clear F3 | ❌ F1, F3 |
| the `/hooks` stop itself | N/A | **never reached** — the probe passes while untrusted (F2) | ❌ F2 |

## 7. What could not be tested

- **Real `/hooks` trust.** `/hooks` is an interactive TUI command; there is
  no `codex exec` equivalent and the trust hash could not be
  reverse-engineered (q4, unchanged). `--dangerously-bypass-hook-trust`
  stands in for it: it is the same "run the enabled hooks" state, reached
  by a different door. What it does *not* stand in for is the user
  experience of being asked.
- **The trusted-arm push (§5).** Two attempts to dispatch that run were
  refused by this session's own Claude Code auto-mode classifier, which
  reads a command line asking an agent to push as a push. Per the
  standing rule (a guard blocking the same intent twice means stop, not a
  third try), it was not attempted again. The claim it would have
  confirmed — a trusted repo `.codex/hooks.json` PreToolUse hook fires and
  exit 2 blocks the command, on this Codex version, with this payload
  shape — is already on record from the q4 live test, runs A, B and D. The
  gap is that it was not re-confirmed against *this* scaffolded repo.
- **Interactive approval of the `.codex/` write (F1).** Whether an
  interactive Codex session with an on-request approval mode would let the
  user approve the scaffold's write into `.codex/` was not tested;
  `--sandbox danger-full-access` was used instead. So F1 is confirmed for
  `codex exec` and unconfirmed for the interactive TUI.

## 8. Findings

- **F2 (blocking, REQ-2 fails on this point).** `codex_scaffold.py --probe`
  invokes the shim directly instead of letting Codex invoke it, so it
  cannot see Codex's trust decision. It reports the gate live while the
  gate is dead, the `/hooks` BLOCK sentence never prints, and a Codex user
  can walk the whole station — and, on the evidence of run 3, push —
  with no deterministic layer at all. REQ-2's "Codex adds only the
  one-time `/hooks` trust" is false in the other direction: as written,
  Codex adds *nothing*, because the step that would ask for the trust
  never fires. The fix has to put a real Codex tool call in the probe path
  (a nested `codex exec` that attempts the fake push, or a marker the hook
  writes that the probe then looks for), not a direct subprocess.
- **F3 (blocking for engineering changes on Codex).** The scaffold's own
  `contract/templates/**` copies sit under the default `**/templates/**`
  interface-surface glob, so `intent.needs-design-recompute` and
  `intent.kind-recompute` block every Codex engineering change whose
  branch contains the scaffold commit. Two candidate fixes: exclude
  `.codex/hooks/**` from the recompute's diff, or have step 0b say the
  scaffold commit belongs on the trunk, before the change branch.
- **F1 (blocking under `codex exec`).** `.codex/` is not writable under
  `--sandbox workspace-write`. Step 0b as written fails there, and the
  document's failure branch ("if `.codex/hooks/loom_checker.py` still does
  not exist after step 0b, stop") sends the user to a dead end with no
  diagnosis. Worth one sentence in step 0b.
- **F4 (minor, host-independent).** Both hosts derive the change-id date
  from SKILL.md's worked example (`2026-09-02`) rather than from today,
  so the plan directory and the branch name disagree
  (`2026-09-02-scripts-share-git-helper` vs the branch
  `2026-09-03-scripts-share-git-helper`). The cold read did the same. The
  worked example reads as canonical; consider dating it relatively.
- **No difference found** in artifacts, artifact paths, decision-point
  count, question wording, question recording, checker command sequence,
  or which rules are meant to run. On everything REQ-2 says about *what
  the user sees and answers*, the two hosts matched.

## 9. Verdict

REQ-2 **not verified**. The user-facing half holds — same files, one
decision point, same questions, same checkers, same rule ids. The
mechanism half does not: on Codex the safety belt is not installed
silently (F2), the station cannot write it under Codex's own default
sandbox (F1), and once written it blocks the very changes it is meant to
wave through (F3).
