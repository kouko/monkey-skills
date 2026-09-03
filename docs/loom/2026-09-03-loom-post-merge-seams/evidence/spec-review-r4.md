# Spec review round 4 — verdicts (spec v5, blob 7e12444, HEAD bc122370)

## codex-review-spec-4 (openai) — PASS

```yaml
verdict: PASS
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: PASS
  incorrect-fact: PASS
  missing-population: PASS
  spec-conformance: PASS
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: PASS
  user-judgment-leak: PASS
findings: []
notes:
  - "spec-R8: closed — spec.md:6 says the close commit is reviewed by two fresh-context reviewers before the review-only commit, and that the user reads no diff."
  - "spec-C9: closed — spec.md:19 says: `Nobody reads the diff for quality: not the user ... and not the agent that wrote it.`"
  - "spec-C10: closed — intent.md:23 requires rejection after changing, adding, deleting, or mode-only changing a plumbing entry."
  - "spec-S7: closed — spec.md:8 adds the trunk-copy check for branches that do not carry the close commit and states the fetch-staleness residual."
  - "spec-R11: closed — spec.md:8 specifies `-G<pattern>` rendered from the status regex's closed alternative with the same whitespace tolerance."
  - "spec-R12: closed — spec.md:21 limits canonical identity to the checker invoked by the host hook and denies a canonical to a stray copy or symlink."
  - "spec-R13: closed — spec.md:21 requires the copy's stamp version to equal the running checker's version before any blob comparison."
  - "Red-team 2a is closed by the trunk-copy check and explicit fetch-staleness boundary in spec.md:8."
  - "Red-team 2c is closed by the grammar-derived, whitespace-compatible `-G` pattern in spec.md:8."
  - "Red-team 2e is closed by the hook-invoked-checker boundary and stray-copy/symlink exclusion in spec.md:21."
  - "Red-team 2f is closed by the running-version stamp comparison before blob comparison in spec.md:21."
  - "The Codex history-wording nit is closed by spec.md:8: deleting and re-adding the path does not remove it from path history; only rewritten ancestry does."
  - "All Current state evidence anchors were opened. ship/SKILL.md:326-336, loom_checker.py:389-400, :791, :825-835, :1557-1559, :2085, :2095, manifest.yaml:85, templates/intent.md:7, and test_loom_checker_intake.py:385-447 support the stated current-state claims."
  - "The verdict-sha gap is pre-existing at reviewed_sha: check_reviewed_sha binds reviewed_sha to HEAD^, while check_verdicts checks reviewer count and passing verdicts without comparing a verdict sha. The v5 spec discloses this residual and assigns it to a follow-up intent."
  - "The close-commit round conforms to PRINCIPLES.md Non-negotiables 1-2: two fresh machines review the complete one-line intent delta, the user reviews no diff, and the existing branch-end blind-run and adversarial evidence remains present, with executable probes re-pinned at the close commit."
  - "The design adds no new prose-only blocking rule; it uses the existing review station and unchanged push rules. The disclosed verdict-sha enforcement gap is not presented as a guarantee."
  - "The reopen design is sound within its stated boundary: branch ancestry catches retained close commits, the trunk copy catches pre-merge branch forks once the local trunk ref is current, and stale or absent fetched trunk state is explicitly residual."
  - "REQ-1 through REQ-6 each trace to Acceptance lines 1 through 6 respectively, and every Acceptance line has one corresponding requirement."

```

## sonnet-review-spec-4 (anthropic) — PASS_WITH_NOTES

```yaml
verdict: PASS_WITH_NOTES
lens: spec
reviewed_sha: 4e25360c
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: PASS_WITH_NOTES — spec-R13/attack 2f not fully closed (see finding)
  incorrect-fact: PASS
  missing-population: PASS
  spec-conformance: PASS
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: PASS_WITH_NOTES — see notes on the close-commit round's no-blind-run scoping and the R13 self-check residual
  user-judgment-leak: PASS
findings:
  - severity: important
    dimension: inconsistency
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:21"
    text: "Round-3 attack 2f (spec-R13) is not actually closed. v5's fix only stops the copy's stamp from disagreeing with the running checker's own version. It does not stop the running checker itself from being a deliberately superseded cached plugin: if the loaded plugin genuinely is an old version, the scaffold copy's stamp legitimately matches that old version and blob comparison succeeds against the old, weaker canonical — no freshness check ties the running checker's version to the repo's current/expected plugin version. Unlike R9 and the S7 staleness gap, this residual is not disclosed; the text asserts 'not ambiguous' as if the exploitability question were settled."
    fix: "Either add a freshness check (running checker's version vs the highest version under the local plugin cache, or plugin.json in a reachable trunk checkout) or explicitly disclose this as an accepted residual of the same shape as R9/S7 instead of the current 'not ambiguous' framing."
notes:
  - "Anchor audit: every 'Current state evidence' citation was opened and matches. check_verdicts()/scored_verdicts() (loom_checker.py:2265-2299) confirms verdicts are picked by round number only, never compared to reviewed_sha — the 'pre-existing, not widened' framing is factually accurate."
  - "The close-commit round's 'no blind run is owed for an intent-typed delta' is a reasonable non-literal reading of Non-negotiable #2 (no Acceptance content to walk in a one-line status change), but the spec never states this reasoning; a future reader could misread it as skipping the Non-negotiable rather than scoping it."
  - "The close-before-merge structure is sound against the packet's question: closed only lands on trunk via the squash merge of a branch that passed the push gate; a symlink/mode-swap of .codex/hooks/loom_checker.py is caught by Acceptance #3's new mode-only case."
```
