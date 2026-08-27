---
name: 2026-08-27-verification-claims-have-no-stop-in-the-ask-vs-resolve-ssot
description: loom's ask-vs-resolve SSOT tiers every pause point by reversibility and cost, so an agent asserting its own work is done or verified always lands in the just-do-it tier — the failure mode measured most consistently across six corpora is the one tier ① cannot see
status: open
origin: 2026-08-27 codex/standardize-complexity-gate — a fingerprint re-pin passed every existing stop rule (reversible, local, evidence-backed) and was still the riskiest call of the session; a six-agent survey of this repo's records and five projects' session transcripts was run before deciding whether to change the SSOT
start: the next arc that touches subagent-driven-development SKILL.md §Asking the user, or a third recorded instance of a self-graded completion claim shipping unchallenged
---

## What the gap is

`loom-code/skills/subagent-driven-development/SKILL.md` §Asking the user ①
is the cross-skill SSOT for ask-vs-resolve decisions — sibling skills point at
it by heading text and are forbidden from copying it. It tiers every pause
point by **reversibility × cost**: reversible and inferable work is done
without asking; irreversible, outward-facing, or costly actions always confirm.

An agent asserting that its own work is done, correct, or verified is
reversible, local, cheap, and looks inferable. It therefore lands in the
first tier — "just do it, mention it after" — every time. There is no entry
covering it, and this is structural rather than an oversight: the tier axis
measures *how bad is this action if it is wrong or unauthorized*, while the
failure here is *a false claim entering the record unchallenged*. The existing
axis cannot express that.

The same blind spot exists in the other three layers that carry stop rules
(this repo's `docs/loom/memory/autonomy-needs-a-small-explicit-stop-set.md`,
and the machine-local `~/.claude/rules/judgment-rubrics.md` §3 plus the user's
CLAUDE.md red lines). All four are authority-and-reversibility lists.

## Evidence

Six agents surveyed six corpora on 2026-08-27. Two read curated records (this
repo's `docs/loom/` stores and the machine's per-project memory); four read raw
Claude Code session transcripts from five projects that consume loom
(kumiko-zaiku-app-icons, kouko-obsidian-vault, meeting-emo-transcriber,
youtube-summarize-scraper, komado-Viewfinder). Each was instructed to hunt
actively for evidence contradicting the thesis, and each reported what it found.

- **The failure axis is self-graded versus independently-verified, not
  mechanical versus judgment.** Both curated-record agents converged on this
  independently. Directly disconfirmed: agent judgment also fails on purely
  factual checks, and holds on at least one measured quality trade-off.
- **Self-grading a claim as done or correct is the only category present in
  every corpus.** The other categories' distributions are project-dependent and
  do not generalize — one project's largest bucket was factual checks with zero
  trade-off errors, another's was the exact inverse.
- **A mechanical check nobody re-validates rots exactly like unchecked
  judgment.** See `docs/loom/memory/a-mechanical-check-can-go-green-by-skipping.md`
  and `docs/loom/memory/an-instrument-can-be-correct-at-every-step-and-still-not-support-its-judgment.md`.
  A transcript case shows the same shape: an agent's own validation regex had an
  escaping bug, reported "all clean", and that report was the basis for its
  completion claim.
- **Several failures were mechanically catchable but the available check was
  simply not run** — a config value outside its documented range, a cited
  contract section never grepped, a test docstring naming a test that did not
  exist.
- **Single-reviewer verdicts are unreliable and redundancy is what fixed it** —
  `docs/loom/dogfood/2026-07-06-g4-sonnet-vs-fable-ab.md` measured a 50% miss
  rate for one arm; the two-arm union caught it with no false positives.

Honest bound on the evidence: transcript mining can only surface corrections the
user actually voiced. Errors nobody noticed leave no trace, so the real rate is
worse than what was found, not better. Three of the four transcript corpora were
also thin (roughly 20-60 genuine human turns each) and their category counts are
a census of what happened, not an estimate of a rate.

## Draft rule — carve-out, not an added tier

An added tier ④ would contradict tier ①, which would still say "just do it",
and an executor would follow whichever suits it. The change has to remove these
cases from tier ① explicitly.

```
- Reversible + inferable from context → just do it, mention it after.
  EXCEPT when the step asserts your own work is done, correct, or
  verified. That is a VERIFICATION CLAIM and routes to the tier below,
  regardless of how reversible the underlying edit is.

- Verification claim → name the checker, or ask.
  A verification claim is any of: flipping a status to DONE; minting a
  gate marker; re-pinning recorded evidence (a fingerprint, baseline,
  benchmark number, or waiver); reporting a check as passed; declaring
  a task complete.

  Before making one, NAME the downstream check that would FAIL if the
  claim were false. A check qualifies only when all three hold:
    (1) it existed before this task, and this task did not author or
        modify it;
    (2) it detects the claim being false — not merely that the original
        trigger stopped recurring;
    (3) it runs without you choosing to run it.

  Can name one → proceed, and report it by name.
  Cannot → ASK. Reversibility never exempts this tier: the risk is a
  false claim entering the record unchallenged, not a hard-to-undo edit.
```

Each condition is anchored to an observed failure: (1) to the self-authored
validation script that reported a false clean; (2) to a fingerprint test whose
green proved only that two numbers matched, so recomputing and pasting the hash
passed it; (3) to the checks that existed and were never run.

## The known risk in this draft

Condition (2) still requires a judgment — deciding whether a named check
actually detects the claim being false. This repo's own record says
judgment-shaped prose fails where action-pointing prose holds. The predicted
failure is an executor naming a check that sounds right but cannot bite, which
is precisely the original defect (a fingerprint test named as its own
post-check).

## Next step, in order

1. Do NOT draft final wording first. `docs/loom/memory/a-rule-stricter-than-the-corpus-best-human-work-is-miscalibrated.md`
   records a reasoned-not-measured threshold failing 9 of 10 cases, including
   both examples the user had called good.
2. Assemble the known cases as a corpus — the fingerprint re-pin and the
   version-collision repin from `codex/standardize-complexity-gate`, the
   self-authored validation regex, and the "check existed but was not run" cases.
3. Run cold-context agents against the draft on that corpus and measure false
   positives and false negatives before fixing the wording.
4. Only then edit the SSOT. This is a runtime contract change to loom-code:
   it needs a version bump, a CHANGELOG entry, the self-declared shipping-version
   pins repinned, a contract test pinning the new wording, and whole-branch
   review — the file is contract-class and is pointed at by sibling skills, so a
   wording defect propagates.

The carrier is the SSOT itself, by explicit user instruction on 2026-08-27: this
is to be an explicit logical rule inside the loom mechanism, not a memory entry.
