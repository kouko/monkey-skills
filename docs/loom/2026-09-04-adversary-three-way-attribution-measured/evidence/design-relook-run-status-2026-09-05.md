# Design re-look — run status and scoring (wave-end:1, third round)

Dispatched per `fix-rounds.md` "Third round: stop fixing, look at the design"
after round 2 held finding wave-end:1-02 open and raised wave-end:1-09.
Reviewer: a fresh opus agent (design-relook-we1-opus), read-only, HEAD 2866b900.

## Verdict: shape-wrong

`score()` receives `list[str]` with no status channel, so a non-observation
(API/auth failure, timeout) is indistinguishable from a real observation the
model answered badly. Folding them makes an infrastructure failure read as
an attribution error: it adds 1 to `n`, adds `wrong` to every item, and can
by itself push an item over the ≥50% `systematic` threshold that decides
W2-02's arm. Fix = carry status next to the body and score only observations.

## Pinned semantics (the next fix and its probes code against this)

(a) Statuses, exactly four: `ok` (exit 0), `resumed` (existing transcript
reused, headers validated), `error` (claude exited non-zero), `timeout`
(`TimeoutExpired`). Scored = {`ok`, `resumed`}; `error`/`timeout` are
non-observations. Their transcripts are still written (audit), never scored.

(b) `score()` takes only scored bodies — signature unchanged, the caller
filters `[r["body"] for r in runs if r["status"] in ("ok", "resumed")]`.
`n` in summary.json = scored runs and is the denominator of
`own_not_own_total` / `three_way_total`. Sibling key `attempted_runs` =
`--runs`. `n` never means attempted.

(c) `failed_runs` = count of runs with status in {`error`, `timeout`} =
`attempted_runs - n`. `resumed` is never a failure (closes 09).

(d) `complete: bool` = `failed_runs == 0 and n == attempted_runs`, written
into summary.json. W2-01's probe must assert `complete is true`, `n == 10`
and `attempted_runs == 10`. `main` returns 1 when `complete` is false
(summary still written); 0 only when complete; 2 stays usage/precondition
errors — a partial baseline cannot be committed silently by a green command.

(e) Header line `# status: ok|error|timeout` written for every run. On
`--resume`, after the hash/model/N/index checks, a run file is resumable
only if its parsed status is `ok`, or the status line is absent and the body
neither starts with `# error:` nor is empty. Otherwise the file is re-run
and overwritten — an error transcript is never resumed. The absent-status
sniff is the only place status is inferred.

(f) `SYSTEMATIC_MIN_N` (3) applies to scored `n`; `wrong_rate` and
`dominant_rate` denominators are scored `n`. 10 attempted / 4 scored behaves
exactly like 4 attempted / 4 scored; state it in `score`'s docstring.

Adversary-checkable invariant: for any batch, injecting an extra failing run
leaves every number in summary.json identical except `attempted_runs`,
`failed_runs`, `complete`, `runs[]`, and the process exit code.

## Other observations

- stdin delivery is right and grounded; `run_once` returns `argv` while
  `main` rebuilds an identical `call_argv` — use the returned one.
- A resumed file with a header and no body yields `body = ""` and scores
  all-`unparsed` silently; (e)'s empty-body rule closes that.
- `n == 0` (all runs failed) must not crash: `score([])` gives zero totals
  and empty `systematic`; summary written with `complete: false`, exit 1 —
  pin it as a test.
