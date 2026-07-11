# principles-improve-loop report — l3-run2

Rounds run: 2/3 (hard cap 3). Accepted: 0.

| Round | Invariant | Applied | Compare | Confirm | Smoke | Wordcap | Accepted | Reason |
|---|---|---|---|---|---|---|---|---|
| 1 | Every seed-named canon or tech-stack item must land as its own `## Anchors` row whose name cell reproduces the seed's exact spelling verbatim — never abbreviated, translated, or paraphrased (a gloss may be appended, never substituted). | true | 1 | n/a | n/a | n/a | false | compare: no win (exit 1) |
| 2 | The post-draft seed walk must be a mechanical verbatim-grep, not a from-memory review: every name the seed states — canon, guideline, model, framework, language, library, format, or technology — must be found by grepping the draft for the seed's exact name string (landing as a version-pinned `## Anchors` row for canons/tech choices), and every deferred/undecidable marker's own wording must be found under `## Open Questions`; any grep miss is fixed by adding the missing row before finalizing. | true | 1 | n/a | n/a | n/a | false | compare: no win (exit 1) |

## Per-seed rows (final visible baseline)

- seed1: PASS
- seed2: FAIL
- seed3: PASS
- seed4: FAIL
