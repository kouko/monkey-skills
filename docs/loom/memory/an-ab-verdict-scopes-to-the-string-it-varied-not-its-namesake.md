---
name: an-ab-verdict-scopes-to-the-string-it-varied-not-its-namesake
description: A firing A/B binds only the exact string it varied, but its verdict gets written as "do not shorten X's description" and X names a plugin that owns several descriptions — so the ban reads as covering a neighbouring string no leg ever touched, and the misreading runs both ways: it blocks a safe edit, or it licenses editing the measured pin because "that experiment was overturned"
type: gotcha
origin: 2026-08-07 loom-discovery plugin-manifest diet (PR #664 shipped it; PR #666 was a duplicate closed the same day) — the reviewing session initially read the 2026-07-30 A/B as forbidding the change
---

`loom-discovery` owns at least four description strings: three SKILL
frontmatter descriptions (`user-insights`, `using-loom-discovery`,
`business-value`) and the plugin manifest description, mirrored across
`marketplace.json`, `.claude-plugin/`, and `.codex-plugin/`. They live one or
two directories apart and are all called "the description".

The 2026-07-30 firing A/B
(`docs/skill-dogfood/2026-07-30-description-diet-firing-ab/ab-results.md`)
varied exactly one of them. Its own header names the variable — "frontmatter
description at 493 rendered chars" — and its remedy enumerates the revert
scope as "frontmatter byte-identical" plus plugin.json's version and
CHANGELOG, a list that mentions plugin.json and conspicuously omits its
DESCRIPTION. Its conclusion, though, reads as a general
prohibition: "Any future attempt to diet this one description needs this same
same-day two-leg A/B against the loom-memory guard pair."

"This one description" is unambiguous to the author, standing in front of the
experiment. It is ambiguous to everyone downstream, because the surrounding
prose talks about `loom-discovery` and `loom-discovery` has several.

**Both misreadings are live, and the second is the dangerous one.**

- *Too broad*: the ban is read as covering the plugin manifest, so a
  1005-character browse blurb — 4.65x the next-longest plugin in a listing
  whose median is 97 — gets frozen by an experiment that never tested it. The
  repo had already dieted plugin manifests wholesale twice with no A/B at all
  (#437, #494); `loom-discovery` escaped both only by landing later (#523).
- *Too narrow, later*: once someone ships the manifest diet and nothing
  breaks, the A/B's authority looks falsified. The next person shortens the
  `user-insights` frontmatter on that precedent — and that string has failed
  at three separate bands (170 / 217 / 493) against
  `loom-pipeline:loom-memory`'s standing "before loom work" attractor. The
  regression is a silent routing miss, not an error.

**What distinguishes them is job, not name.** A SKILL frontmatter description
is a routing surface: the harness matches queries against it, so its wording
changes which skill fires. A plugin manifest description is a browse blurb
shown to a human choosing whether to install. No agent-runtime path reads it.
An experiment measuring firing rates cannot say anything about the second, and
did not try to.

**When recording an A/B verdict, name the artifact, not the owner.** "Do not
diet `loom-discovery:user-insights`'s SKILL.md frontmatter description without
a same-day two-leg A/B" costs six words more than "this one description" and
cannot be misread in either direction. **When reading one, find the leg
definition before accepting the conclusion** — the header that says what was
varied is load-bearing, and a conclusion written in prose will almost always
be broader than the experiment that produced it.

Anchor by quote, not line number: this file's citations are verbatim strings
so they survive edits to the A/B document, per
[[a-passage-that-describes-itself-decays-on-every-edit]] and
[[a-line-cite-fixed-before-its-file-is-edited-goes-stale-again]].
