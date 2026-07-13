---
name: equivalence-gate-verifies-behavior-not-facts
description: A behavioral-equivalence gate (judge ensemble comparing outputs) faithfully preserves inherited FACTUAL errors — a wrong citation (Beck Child Test "Part II", actually Part III) survived an equivalence-gated compression and a fresh reuse because both sides of every comparison carried the same error; factual accuracy of names/citations/numbers in skill text needs an explicit review dimension (or a fact-check pass), it is never covered by equivalence
type: gotcha
origin: feat/pocock-compression-port whole-branch review (2026-07-13), error lineage through PR #559
---

writing-plans' Beck citation said "Part II §Child Test". PR #559's
equivalence-gated compression preserved it (correctly — the gate's job is
behavior preservation, and both baseline and candidate carried the same
wrong part number). The Pocock-port branch then reused the line as a
worked example, still wrong. Only a whole-branch reviewer explicitly
checking citation accuracy against the book's real structure caught it —
Child Test lives in Part III (Testing Patterns).

**Why:** equivalence judging compares candidate vs baseline; an error
present in BOTH is invisible to it by construction. Compression moves
(especially Leading-Word Substitution, which trades prose for citations)
concentrate factual claims into fewer, higher-leverage tokens — making a
wrong fact both more prominent and less checkable by the gate.

**How to apply:** when reviewing skill text that carries citations, named
patterns, magic numbers, or version claims, verify them against the
primary source as a separate review dimension — do not treat a passing
equivalence gate as evidence the facts are right. (Related:
[[equivalence-test-prompts-must-satisfy-target-intake-contract]].)
