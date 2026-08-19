---
name: an-inherited-external-tool-fact-is-a-claim-with-a-version-attached
description: A behavioural fact about an external tool, copied from another skill's quirks list or docs and then made load-bearing, is only true of the version it was observed on — two such facts inherited into one branch were BOTH false against the version that branch pinned, one of them enforcing a FAIL on correct content; re-probe every inherited tool fact at the moment you pin a version, and again when the pin moves
type: practice
origin: 2026-08-19 cot-explain arc (dev-workflow 2.26.0) — `number. space` kills mermaid, and mermaid-cli exits 0 on syntax errors; both inherited from obsidian-mermaid-visualizer, both falsified live on mermaid-cli 11.16.0
---

Borrowing a hard-won quirk from a sibling skill feels like the opposite of
guessing — it is someone else's live observation, written down. The problem
is what gets dropped in transit: **the version it was true of.**

Two facts came across into one branch, and both were load-bearing:

- "mermaid parses `1. ` as a markdown list and dies" — implemented as a
  `FAIL`. On the pinned parser it renders cleanly, quoted and unquoted. The
  gate was rejecting correct content: "Step 1. do this" is an ordinary
  sentence.
- "mermaid-cli writes an error image and exits 0" — the entire justification
  for a `--render` stage. A live probe saw a malformed arrow exit 1 with no
  image at all. Both behaviours are real; neither can be relied on, which is
  a different design conclusion from the one inherited.

Note the asymmetry in cost. The second was harmlessly over-cautious — the
checker already read the output rather than the exit status, so only the
prose was wrong. The first **blocked valid work**, and would have gone on
doing so, because the failure of a gate that rejects good input looks
exactly like the gate working.

**Why:** an inherited fact arrives with provenance that reads as
verification. It says "measured, not guessed", and that is true — but the
measurement has an implicit `as of version X, on platform Y` that the
sentence never carries, and pinning a dependency is precisely the moment
that qualifier becomes load-bearing. The sibling skill did nothing wrong;
the fact simply aged.

**How to apply:** when an inherited tool fact is about to become a gate, a
FAIL, or the justification for a whole stage, run it once against the
version you are pinning — a single probe, minutes of work. Record the
version and the outcome next to the rule, so the next reader knows what it
was true of. And prefer a WARN over a FAIL for any inherited behavioural
quirk you have not personally reproduced: the cost of a false warning is
noise, the cost of a false failure is correct work rejected. Related:
[[a-tool-behaviour-measured-in-one-repo-state-is-not-a-general-fact]],
[[a-control-placed-downstream-of-what-it-guards-is-not-a-control]].
