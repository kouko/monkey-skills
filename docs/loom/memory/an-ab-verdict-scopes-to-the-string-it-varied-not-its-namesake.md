---
name: an-ab-verdict-scopes-to-the-string-it-varied-not-its-namesake
description: A firing A/B binds only the exact string it varied, but its verdict gets written as "do not shorten X's description" and X names a plugin that owns several descriptions — so the ban reads as covering a neighbouring string no leg ever touched, and the misreading runs both ways: it blocks a safe edit, or it licenses editing the measured pin because "that experiment was overturned"
type: gotcha
origin: 2026-08-07 loom-discovery plugin-manifest diet (PR #664 shipped it; PR #666 was a duplicate closed the same day) — the reviewing session initially read the 2026-07-30 A/B as forbidding the change
---

`loom-discovery` owns at least four description strings: three SKILL
frontmatter descriptions (`user-insights`, `using-loom-discovery`,
`business-value`) and the plugin manifest description, mirrored byte-identical
across `.claude-plugin/marketplace.json`, `loom-discovery/.claude-plugin/`,
and `loom-discovery/.codex-plugin/`. They live one or two directories apart
and are all called *the description*. (Double quotes in this entry's **body**
mark verbatim text — either cited from a source or proposed as replacement
wording; mentions are italicized. The frontmatter `description` above is a
compressed summary and quotes paraphrase there.)

The 2026-07-30 firing A/B
(`docs/skill-dogfood/2026-07-30-description-diet-firing-ab/ab-results.md`)
varied exactly one of them. Its `Repo state:` metadata line names the variable
— "frontmatter description at 493 rendered chars" — its cache-experiment
disclosure overlays only that string onto the deployed copy, and its remedy
enumerates the revert scope as "frontmatter byte-identical" plus plugin.json's
version and CHANGELOG, a list that names plugin.json while omitting its
description.

Its conclusion, though, generalizes: any future attempt to diet "this one
description" needs the same same-day two-leg A/B against the loom-memory guard
pair. Unambiguous to the author standing in front of the experiment.

**The source is not maximally ambiguous, and the misreading happened anyway.**
Its neighbouring lines do carry scope cues: the remedy names "frontmatter
byte-identical", and it cites "the full 899-char" description — a size no
1005-character manifest string can match. A reader who works upward from the
ban can reconstruct the scope.

The trap is that none of those cues is *in* the operative sentence, and none
of them names the skill. The sentence a reader greps to, quotes, and acts on
says only "this one description", while its own paragraph says
`loom-discovery`, which owns four of them. Sufficient context nearby does not
rescue an imperative that is ambiguous where it is read.

**Both misreadings are live; only the first is recorded.**

- *Too broad* (observed, this entry's origin): the ban is read as covering the
  plugin manifest, freezing a browse blurb the experiment never tested. At the
  time, `loom-discovery`'s manifest description was 1005 characters — 4.65x
  the next-longest of the 27 entries in `.claude-plugin/marketplace.json`
  (`loom-pipeline`, 216), against a median of 97. (Figures as of `fd2c1a4f^`,
  before #664 cut it; re-measuring today returns different numbers.) The repo
  had already dieted plugin manifests wholesale twice with no A/B at all
  (#437, #494); `loom-discovery` escaped both only by landing later (#523).
- *Too narrow, predicted*: once someone ships the manifest diet and nothing
  breaks, the A/B's authority looks falsified. The next person shortens the
  `user-insights` frontmatter on that precedent — and that string has failed
  at three separate bands (170 / 217 / 493) against `loom-pipeline:loom-memory`'s
  standing "before loom work" attractor, per
  [[sibling-attractor-makes-lexical-tuning-unstable]]. No instance recorded
  yet; the asymmetry is what makes it worth pre-empting — a routing miss is
  silent, not an error.

**What distinguishes the two strings is job, not name.** A SKILL frontmatter
description is a routing surface: the harness matches queries against it, so
its wording changes which skill fires. A plugin manifest description is a
browse blurb shown to a human choosing whether to install. Stated at the
strength the evidence supports: no probe in this repo has ever measured a
manifest description on a firing surface —
[[deploy-surface-ab-legs-run-post-merge]] enumerates the deployed probe
surfaces as "skill frontmatter descriptions, hooks, preload cards", and
manifest descriptions are absent. That is an absence of measurement, not a
proven absence of effect; it is enough to say the 2026-07-30 experiment
cannot speak to the manifest, which is the claim this entry needs.

**Why:** the store is consulted precisely when nobody wants to re-read the
experiment, so a verdict's wording is the whole interface. A ban whose scope
every later reader has to reconstruct will be reconstructed differently each
time, and one of those readings edits a string that regresses silently.

**How to apply:** when recording an A/B verdict, name the artifact, not the
component that owns it — "do not diet `loom-discovery:user-insights`'s SKILL.md
frontmatter description without a same-day two-leg A/B" costs six words more
than "this one description" and cannot be misread in either direction. When
reading one, find the leg definition (the metadata block stating what was
varied) before accepting the conclusion; a conclusion written in prose is
almost always broader than the experiment that produced it.

Citations here are anchored by short verbatim fragments rather than line
numbers, per [[a-passage-that-describes-itself-decays-on-every-edit]] and
[[a-line-cite-fixed-before-its-file-is-edited-goes-stale-again]] — **short**
being load-bearing: the A/B's conclusion sentence spans a hard line wrap, so
no grep for it as one continuous string matches, which is why it is
paraphrased above with only "this one description" quoted. See
[[verbatim-phrase-guards-break-on-hard-line-wrap]].
