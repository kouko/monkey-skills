---
name: anchor-kind-must-match-artifact-structure
description: Evidence anchors stay stable only when their form matches the cited artifact: prose headings or phrases, code declarations or literals, and configuration key paths plus value fragments
type: practice
origin: anchor-primary-line-cite-rule branch, 2026-08-22
---

An anchor is not a prose-only device. Its stable form must match the artifact
being cited: a prose heading or distinctive phrase, a code declaration or
distinctive literal, or a configuration/data key path paired with a value
fragment.

**Why:** A generic instruction to add an anchor leaves code and configuration
authors to fall back to line ranges. Those ranges drift during edits, while an
artifact-native anchor remains readable and checkable without a language
parser.

**How to apply:** Cite `path + artifact-native anchor`; add a line number only
when that anchor cannot distinguish the target by itself. Do not use a generic
description such as "the relevant code" as an anchor.
